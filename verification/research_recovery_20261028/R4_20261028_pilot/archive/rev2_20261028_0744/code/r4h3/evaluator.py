"""Component E: independent energy and validity evaluation from a retained trace (protocol v1 7, 8.2, 9).

Separate from the simulator and planner: this module imports neither r3_lib, rebuild, eureka nor the planner,
and code/recompute_from_traces.py runs it in its own process on the saved traces and per-run spec files only.
It re-writes the declared model's motor-loss, battery-current, battery-limit and friction laws (protocol 2;
R1-R3 model basis; the protocol text itself gives no equations), recomputes the battery current from the
traced torque, speed and V1, and integrates every quantity by the trapezoid rule over the 1 ms samples.
What this independence does and does not cover is listed in 04_independent_code_review.md (CR-A6): it checks
bookkeeping, integration and the metric definitions, not the plant dynamics, which come from the trace.

Sign convention: battery current i > 0 on discharge. Energy at the primary boundary (protocol 7.1) is
E_chem = integral of V_oc i dt: propulsion energy enters positive, regenerated energy negative, and the
net value is reported. Auxiliary load is 0 W (not modelled). Regenerative-braking efficiency
(protocol 7.3) is reported separately and never mixed with Wh/km.

Changes after the smoke test (06_readiness_implementation_report.md): VC-03 checks the trace sample step and
adds the R1-R3 battery-limited fraction and max |e| against the task reference; VC-04 separates the
protocol-9 recomputation checks (which decide crediting) from implementation diagnostics; VC-05 compares the
deciding C-rate I_over and the constraint flag with simulator-side values and adds diagnostics for the tracked
profile, the wheel braking power and the energy closure.
VC-09 computes the drive and regeneration torque limits itself (battery power limits inverted through the loss
law: closed forms for M0/M2, bisection for M1) and uses them for friction and the battery-limited fraction; the
traced limits are only compared, as diagnostics. Shared with the simulator: the model equations and parameters.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def _trapz(y, t):
    y = np.asarray(y, float)
    return float(np.sum(0.5 * (y[1:] + y[:-1]) * np.diff(t)))


# --------------------------------------------------------------------------- formulas from the protocol text
def motor_loss(spec: dict, p_m, T):
    """Combined motor + inverter loss L >= 0 (protocol 2.3): M0 const eta, M1 eta(|P_m|/P_rated), M2 k_c T^2."""
    kind = spec["kind"]
    if kind == "copper":
        return spec["k_c"] * T * T
    if kind == "const":
        eta = np.full_like(np.asarray(p_m, float), spec["eta"])
    elif kind == "curve":
        eta = np.interp(np.abs(p_m) / spec["p_rated"], spec["frac"], spec["eff"])
    else:
        raise ValueError(f"unknown motor kind {kind!r}")
    return np.where(p_m >= 0, p_m * (1.0 / eta - 1.0), -p_m * (1.0 - eta))


def motor_spec_from_protocol(sid: str, m1_curve_path: Path) -> dict:
    """The three scenarios written from protocol 2.3 (not taken from r3_lib)."""
    if sid == "M0":
        return {"sid": "M0", "kind": "const", "eta": 0.874}
    if sid == "M1":
        m1 = json.loads(Path(m1_curve_path).read_text(encoding="utf-8"))
        return {"sid": "M1", "kind": "curve", "frac": list(m1["frac"]), "eff": list(m1["eff"]),
                "p_rated": float(m1["p_rated_W"])}
    if sid == "M2":
        # ledger MOT-07 derivation; protocol 2.3 prints it rounded as 0.3592 (AMB-07)
        return {"sid": "M2", "kind": "copper", "k_c": 18000.0 * (1 / 0.874 - 1) / 85.0 ** 2}
    raise ValueError(f"unknown motor scenario {sid!r}")


def battery_current(T, w, V1, b: dict, motor: dict):
    p_m = T * w
    p_e = p_m + motor_loss(motor, p_m, T)
    vo = b["V_oc"] - V1
    disc = vo * vo - 4.0 * b["R0"] * p_e
    i = (vo - np.sqrt(np.maximum(disc, 0.0))) / (2.0 * b["R0"])
    return i, p_e, disc >= 0


def window_limits(V1, b: dict):
    """Discharge/charge current magnitudes allowed by C-rate, voltage window and max-power point."""
    vo = b["V_oc"] - V1
    i_v = np.maximum((vo - b["v_min_ratio"] * b["V_oc"]) / b["R0"], 0.0)
    i_d = np.minimum(np.minimum(b["c_dis"] * b["Q_Ah"], i_v), vo / (2.0 * b["R0"]))
    i_c = np.minimum(b["c_ch"] * b["Q_Ah"], np.maximum((b["v_max_ratio"] * b["V_oc"] - vo) / b["R0"], 0.0))
    return i_d, i_c


# --------------------------------------------------------------------------- independent torque limits (VC-09)
W_FLOOR = 1e-6          # rad/s: speed floor of the declared model (R1/R3 torque limits divide by max(w, 1e-6))
INV_ITERS = 64          # bisection steps for the M1 inverse: 1.5 p_rated / 2^64 < 1e-15 W
# Diagnostic tolerance on |own - traced| torque limits [N m], by loss kind. const/copper: both sides use closed
# forms (float rounding <= 2e-13 N m measured over 240 000 operating points). curve (M1): r3_lib inverts the curve
# through a 3001-point table, ours by bisection; the table's interpolation error was <= 9.7e-7 N m on the same
# points, so 1e-5 N m is a 10x margin. Diagnostic only: never decides crediting (06_ / 10_ reports).
TORQUE_LIMIT_TOL = {"const": 1e-9, "copper": 1e-9, "curve": 1e-5}


def battery_power_limits(V1, b: dict):
    """Terminal power at the largest allowed discharge and charge currents (declared model): p_d = (vo - R0 i_d) i_d,
    p_c = (vo + R0 i_c) i_c, with i_d, i_c from window_limits (C-rate of nominal Q, voltage window, max-power point)."""
    vo = b["V_oc"] - V1
    i_d, i_c = window_limits(V1, b)
    return (vo - b["R0"] * i_d) * i_d, (vo + b["R0"] * i_c) * i_c


def _bisect_increasing(f, target, hi):
    """Largest x in [0, hi] with f(x) <= target for a non-decreasing f (vectorised); inf where target > f(hi)."""
    lo_ = np.zeros_like(target, dtype=float)
    hi_ = np.full_like(target, hi, dtype=float)
    for _ in range(INV_ITERS):
        mid = 0.5 * (lo_ + hi_)
        ok = f(mid) <= target
        lo_ = np.where(ok, mid, lo_)
        hi_ = np.where(ok, hi_, mid)
    return np.where(target > f(np.full_like(target, hi, dtype=float)), np.inf, lo_)


def mech_power_limits(p_d, p_c, w_pos, motor: dict):
    """Largest mechanical drive power whose electrical demand is <= p_d, and largest mechanical braking power whose
    electrical return is <= p_c, from the loss law motor_loss (P_e = P_m + L). Closed forms for const and copper;
    bisection on the forward law for the curve (the curve is not inverted through a table)."""
    kind = motor["kind"]
    if kind == "const":
        return motor["eta"] * p_d, p_c / motor["eta"]
    if kind == "copper":                                   # P_e = P_m + k_c (P_m / w)^2, returned = P_b - k_c (P_b / w)^2
        a = motor["k_c"] / w_pos ** 2
        pd = 2.0 * p_d / (1.0 + np.sqrt(1.0 + 4.0 * a * p_d))
        disc = 1.0 - 4.0 * a * p_c
        pc = np.where(disc >= 0, 2.0 * p_c / (1.0 + np.sqrt(np.maximum(disc, 0.0))), np.inf)
        return pd, pc
    hi = 1.5 * motor["p_rated"]                            # the curve's declared domain (shared with r3_lib)
    zero = np.zeros(1)
    drive = lambda pm: pm + motor_loss(motor, pm, zero)                 # noqa: E731
    regen = lambda pb: pb - motor_loss(motor, -pb, zero)                # noqa: E731
    return _bisect_increasing(drive, p_d, hi), _bisect_increasing(regen, p_c, hi)


def torque_limits(w, V1, b: dict, motor: dict, T_max: float, P_max: float):
    """Drive limit, regeneration limit (magnitude) and motor-only limit [N m] from the declared model:
    base = min(T_max, P_max / w), t_pos = min(base, P_m,drive / w), t_neg = min(base, P_m,brake / w), w >= W_FLOOR.
    Written from the model basis, not from r3_lib; the limit sets are always active in H3 (nominal Q)."""
    w_pos = np.maximum(w, W_FLOOR)
    base = np.minimum(T_max, P_max / w_pos)
    p_d, p_c = battery_power_limits(V1, b)
    pd, pc = mech_power_limits(p_d, p_c, w_pos, motor)
    return np.minimum(base, pd / w_pos), np.minimum(base, pc / w_pos), base


# --------------------------------------------------------------------------- evaluation
def evaluate_trace(a: dict, spec: dict, rules: dict) -> dict:
    """All protocol 7 metrics and 8.2 flags from the trace channels `a` and the run specification."""
    b, motor = spec["battery"], spec["motor"]
    t = a["t_s"]
    # spec["dt_s"] is the trace sample step (1 ms for every run, protocol 10.3); refuse any other spacing so that
    # the control instants k Ts used for RMSE are the right samples (change VC-03)
    steps_t = np.diff(t)
    if np.max(np.abs(steps_t - spec["dt_s"])) > 1e-9:
        raise ValueError(f"trace sample step {steps_t.min()}..{steps_t.max()} s != declared {spec['dt_s']} s")
    sub = int(round(spec["Ts_s"] / spec["dt_s"]))
    if abs(sub * spec["dt_s"] - spec["Ts_s"]) > 1e-12 or (len(t) - 1) % sub:
        raise ValueError("control period is not a whole number of trace samples")
    v = np.maximum(a["v_mps"], 0.0)
    w = spec["G"] / spec["r_w"] * v
    i, p_e, feas = battery_current(a["T_Nm"], w, a["V1_V"], b, motor)
    vt = b["V_oc"] - a["V1_V"] - b["R0"] * i
    ctrl = np.arange(0, len(t), sub)
    e = a["v_mps"][ctrl] - a["v_tracked_mps"][ctrl]
    e_ref = a["v_mps"][ctrl] - a["v_ref_task_mps"][ctrl]
    # torque limits computed here from the battery state and the loss law (VC-09), not taken from the trace
    t_pos, t_neg, base_all = torque_limits(w, a["V1_V"], b, motor, spec["T_max"], spec["P_max"])
    dpos = float(np.max(np.abs(t_pos - a["t_pos_Nm"])))
    dneg = float(np.max(np.abs(t_neg - a["t_neg_Nm"])))
    # battery-limited control instants as R1-R3 define them: command above the drive limit, and that limit below
    # the motor's own torque/power limit min(T_max, P_max / w)
    u_c, tp_c, base = a["u_cmd_Nm"][ctrl], t_pos[ctrl], base_all[ctrl]
    batt_lim = (u_c > tp_c) & (tp_c < base - 1e-9)
    # instants whose classification could flip within the measured limit difference (diagnostic tolerance)
    n_ambiguous = int(np.sum((np.abs(u_c - tp_c) <= dpos) | (np.abs(tp_c - (base - 1e-9)) <= dpos)))
    d = _trapz(v, t)
    E = _trapz(b["V_oc"] * i, t)
    # Friction power depends on the zero-order-hold command u, which jumps at control instants. Each interval
    # is therefore integrated with the u held over it: both ends computed here from (u_start, t_neg, v) with the
    # model's friction law gr max(0, -t_neg - u) tanh(v/v_eps) v and the independently computed t_neg.
    gr = spec["G"] / spec["r_w"]

    def fric(u, tn, vv):
        return gr * np.maximum(0.0, -tn - u) * np.tanh(vv / spec["v_eps"]) * vv

    p_fric_start = fric(a["u_cmd_Nm"], t_neg, v)
    p_fric_end = fric(a["u_cmd_Nm"][:-1], t_neg[1:], v[1:])
    fric_J = float(np.sum(0.5 * (p_fric_start[:-1] + p_fric_end) * np.diff(t)))
    p_fric_law_traced = fric(a["u_cmd_Nm"], a["t_neg_Nm"], v)        # the law applied to the traced limit
    # motor-braking power at the wheel, recomputed from (T, w, v) with the declared gear law (VC-05): the wheel force
    # f_w = gr t_s eta_g (t_s >= 0) or gr t_s / eta_g, t_s = T - B_m w; braking power max(-f_w v, 0) (protocol 7.3)
    t_s = a["T_Nm"] - spec["B_m"] * w
    f_w = np.where(t_s >= 0, gr * t_s * spec["eta_g"], gr * t_s / spec["eta_g"])
    p_regen_wheel = np.maximum(-f_w * v, 0.0)
    W_brake = _trapz(p_regen_wheel, t) + fric_J
    kn = spec.get("tracked_knots")
    tracked_diff = (float(np.max(np.abs(np.interp(t, kn[0], kn[1]) - a["v_tracked_mps"]))) if kn is not None
                    else float("nan"))
    if all(f"int_{k}" in a for k in ("E_chem", "Ah") + CLOSURE_LOSSES):
        dlt = {k: a[f"int_{k}"][-1] - a[f"int_{k}"][0] for k in ("E_chem", "Ah") + CLOSURE_LOSSES}
        sinks = (0.5 * spec["M_eff"] * (a["v_mps"][-1] ** 2 - a["v_mps"][0] ** 2)
                 + 0.5 * spec["C1"] * (a["V1_V"][-1] ** 2 - a["V1_V"][0] ** 2) + sum(dlt[k] for k in CLOSURE_LOSSES))
        thr = b["V_oc"] * 3600.0 * dlt["Ah"]
        closure_rel = float(abs(dlt["E_chem"] - sinks) / thr) if thr > 0 else float("inf")
    else:
        closure_rel = float("nan")                                   # schema v1 trace: closure integrators absent
    E_regen = abs(_trapz(np.minimum(b["V_oc"] * i, 0.0), t))
    i_lim_over = np.maximum(i - b["c_dis"] * b["Q_Ah"], 0.0) + np.maximum(-i - b["c_ch"] * b["Q_Ah"], 0.0)
    i_d, i_c = window_limits(a["V1_V"], b)
    win_over = np.maximum(i - i_d, 0.0) + np.maximum(-i - i_c, 0.0)
    m = {
        "current_max_abs_diff_A": float(np.max(np.abs(i - a["i_A"]))),
        "speed_map_max_abs_diff": float(np.max(np.abs(w - a["w_radps"]))),
        "E_chem_Wh": E / 3600.0,
        "E_pos_Wh": _trapz(np.maximum(b["V_oc"] * i, 0.0), t) / 3600.0,
        "E_neg_Wh": _trapz(np.minimum(b["V_oc"] * i, 0.0), t) / 3600.0,
        "E_DC_Wh": _trapz(vt * i, t) / 3600.0,
        "distance_m": d,
        "trip_time_s": float(t[-1] - t[0]),
        "Wh_per_ref_km": (E / 3600.0) / (spec["d_ref_m"] / 1000.0),
        "Wh_per_actual_km": (E / 3600.0) / (d / 1000.0) if d > 0 else float("nan"),
        "shortfall_pct": 100.0 * (spec["d_ref_m"] - d) / spec["d_ref_m"],
        "rmse_ms": float(np.sqrt(np.mean(e * e))),
        "max_abs_err_ms": float(np.max(np.abs(e))),
        "rmse_vs_task_ref_ms": float(np.sqrt(np.mean(e_ref * e_ref))),
        "max_abs_err_vs_task_ref_ms": float(np.max(np.abs(e_ref))),
        "friction_power_max_abs_diff_W": float(np.max(np.abs(p_fric_law_traced - a["P_fric_W"]))),
        "friction_power_own_limits_max_abs_diff_W": float(np.max(np.abs(p_fric_start - a["P_fric_W"]))),
        "torque_limit_pos_max_abs_diff_Nm": dpos,
        "torque_limit_neg_max_abs_diff_Nm": dneg,
        "torque_limit_tol_Nm": TORQUE_LIMIT_TOL[motor["kind"]],
        "friction_tol_Wh": 1e-6 + gr * dneg * d / 3600.0,
        "batt_limited_ambiguous_frac": n_ambiguous / len(ctrl),
        "v_max_ms": float(np.max(v)),
        "gr_rad_per_m": gr,
        "regen_wheel_power_max_abs_diff_W": float(np.max(np.abs(p_regen_wheel - a["P_regen_wheel_W"]))),
        "tracked_profile_max_abs_diff_ms": tracked_diff,
        "closure_rel_from_trace": closure_rel,
        "friction_brake_Wh": fric_J / 3600.0,
        "regen_returned_chem_Wh": E_regen / 3600.0,
        "braking_work_wheel_Wh": W_brake / 3600.0,
        "eta_regen": E_regen / W_brake if W_brake > 0 else float("nan"),
        "Ah": _trapz(np.abs(i), t) / 3600.0,
        "I2_A2s": _trapz(i * i, t),
        "peak_abs_current_A": float(np.max(np.abs(i))),
        "rms_current_A": float(np.sqrt(_trapz(i * i, t) / (t[-1] - t[0]))),
        "I_over_protocol_As": _trapz(i_lim_over, t),
        "I_over_window_As": _trapz(win_over, t),
        "min_Vt_V": float(np.min(vt)),
        "V_min_V": b["v_min_ratio"] * b["V_oc"],
        "battery_feasible_all": bool(np.all(feas)),
        "batt_limited_frac": float(np.mean(batt_lim)),
        "limit_active_sample_frac": float(np.mean(a["limit_active"])),   # command outside any torque limit
    }
    stops = stop_compliance(t, a["v_mps"], spec["rest_intervals"], rules)
    m["stop_rows"] = stops
    m["n_stops_tested"] = sum(1 for s in stops if s["tested"])
    m["stop_ok"] = all(s["ok"] for s in stops if s["tested"])
    m["complete"] = m["shortfall_pct"] <= rules["shortfall_max_pct"]
    m["tracking_ok"] = m["rmse_ms"] <= rules["rmse_max_ms"] and m["max_abs_err_ms"] <= rules["max_abs_err_ms"]
    m["constraint_ok"] = (m["I_over_protocol_As"] <= rules["i_over_max_As"]
                          and m["min_Vt_V"] >= m["V_min_V"] - rules["v_min_tol_V"])
    m["finite_ok"] = bool(all(np.all(np.isfinite(a[k])) for k in a)) and m["battery_feasible_all"]
    return m


def stop_compliance(t, v, rest_intervals, rules):
    """Protocol 8.2: for each rest interval of >= 2 s, |v| <= 0.05 m/s and distance <= 0.10 m on [t_a + 1, t_d]."""
    rows = []
    for t_a, t_d in rest_intervals:
        tested = (t_d - t_a) >= rules["stop_min_duration_s"] - 1e-9
        row = dict(t_a=t_a, t_d=t_d, tested=tested, max_abs_v=float("nan"), distance_m=float("nan"), ok=True)
        if tested:
            sel = (t >= t_a + rules["stop_settle_s"] - 1e-12) & (t <= t_d + 1e-12)
            vv = np.maximum(v[sel], 0.0)
            row["max_abs_v"] = float(np.max(np.abs(v[sel])))
            row["distance_m"] = _trapz(vv, t[sel])
            row["ok"] = row["max_abs_v"] <= rules["stop_speed_max_ms"] and row["distance_m"] <= rules["stop_distance_max_m"]
        rows.append(row)
    return rows


def compare_with_simulator(ev: dict, sim: dict, rules: dict) -> dict:
    """Protocol 9 'independent recomputation': evaluator vs simulator-side values.

    Protocol group (decides crediting): E_chem and E_DC within 1e-4 relative, distance within 1e-6 relative
    (protocol 9), trip time, the deciding C-rate I_over and RMSE within PROTOCOL_TOLERANCES (the three values protocol
    9 does not state; justified in 10_tolerance_approval_register.md, amendment A1-12), and identical stop, completion,
    tracking and constraint flags. Diagnostic group: reported and flagged, never an exclusion rule (VC-04). A
    diagnostic whose value is NaN (input absent) is omitted."""
    def rel(x, y):
        return abs(x - y) / max(abs(y), 1e-12)

    sim_complete = sim["shortfall_vs_dref_pct"] <= rules["shortfall_max_pct"]
    sim_tracking = sim["rmse_ms"] <= rules["rmse_max_ms"] and sim["max_abs_err_ms"] <= rules["max_abs_err_ms"]
    checks = {
        "E_chem_rel": (rel(ev["E_chem_Wh"], sim["E_net_Wh"]), rules["recompute_energy_rel"]),
        "E_DC_rel": (rel(ev["E_DC_Wh"], sim["E_DC_Wh"]), rules["recompute_energy_rel"]),
        "distance_rel": (rel(ev["distance_m"], sim["distance_km"] * 1000.0), rules["recompute_distance_rel"]),
        "trip_time_abs_s": (abs(ev["trip_time_s"] - sim["trip_time_s"]), PROTOCOL_TOLERANCES["trip_time_abs_s"]),
        "I_over_protocol_abs_As": (abs(ev["I_over_protocol_As"] - sim["I_over_protocol_As"]),
                                   PROTOCOL_TOLERANCES["I_over_protocol_abs_As"]),
        "rmse_rel": (rel(ev["rmse_ms"], sim["rmse_ms"]), PROTOCOL_TOLERANCES["rmse_rel"]),
        # diagnostics
        "E_pos_rel": (rel(ev["E_pos_Wh"], sim["E_pos_Wh"]), rules["recompute_energy_rel"]),
        "friction_abs_Wh": (abs(ev["friction_brake_Wh"] - sim["friction_brake_Wh"]), ev["friction_tol_Wh"]),
        "max_err_rel": (rel(ev["max_abs_err_ms"], sim["max_abs_err_ms"]), 1e-9),
        "I_over_window_abs_As": (abs(ev["I_over_window_As"] - sim["I_over_As"]), 1e-4),
        "min_Vt_abs_V": (abs(ev["min_Vt_V"] - sim["min_Vt_V"]), 1e-6),
        "batt_limited_frac_abs": (abs(ev["batt_limited_frac"] - sim["batt_limited_frac"]),
                                  ev["batt_limited_ambiguous_frac"] + 1e-12),
        "torque_limit_pos_abs_Nm": (ev["torque_limit_pos_max_abs_diff_Nm"], ev["torque_limit_tol_Nm"]),
        "torque_limit_neg_abs_Nm": (ev["torque_limit_neg_max_abs_diff_Nm"], ev["torque_limit_tol_Nm"]),
        "friction_power_own_limits_abs_W": (ev["friction_power_own_limits_max_abs_diff_W"],
                                            1e-9 + gr_v_max(ev) * ev["torque_limit_neg_max_abs_diff_Nm"]),
        "current_recompute_abs_A": (ev["current_max_abs_diff_A"], 1e-9),
        "friction_power_recompute_abs_W": (ev["friction_power_max_abs_diff_W"], 1e-9),
        "regen_wheel_power_recompute_abs_W": (ev["regen_wheel_power_max_abs_diff_W"], 1e-9),
        "tracked_profile_abs_ms": (ev["tracked_profile_max_abs_diff_ms"], 1e-9),
        "closure_rel_abs": (abs(ev["closure_rel_from_trace"] - sim["closure_rel"]), 1e-9),
    }
    flags = {"stop_ok_equal": ev["stop_ok"] == sim["stop_ok_sim"],
             "complete_equal": ev["complete"] == sim_complete,
             "tracking_ok_equal": ev["tracking_ok"] == sim_tracking,
             "constraint_ok_equal": ev["constraint_ok"] == sim["constraint_ok_sim"]}
    res = {k: dict(value=float(x), tol=tol, ok=bool(x <= tol)) for k, (x, tol) in checks.items()
           if k in PROTOCOL_CHECKS or np.isfinite(x)}
    res.update({k: dict(value=v, tol=None, ok=bool(v)) for k, v in flags.items()})
    for k in res:
        res[k]["group"] = "protocol" if k in PROTOCOL_CHECKS else "diagnostic"
    # protocol 9 lists the quantities whose agreement decides crediting; the others are diagnostics that are
    # reported and flagged but add no exclusion rule the protocol does not have (change VC-04)
    res["protocol_ok"] = all(r["ok"] for k, r in res.items() if k in PROTOCOL_CHECKS)
    res["diagnostics_ok"] = all(r["ok"] for k, r in res.items() if isinstance(r, dict) and r["group"] == "diagnostic")
    res["all_ok"] = res["protocol_ok"] and res["diagnostics_ok"]
    return res


# protocol 9 'independent recomputation': E_chem, E_DC, distance, trip time, stop compliance, I_over and RMSE agree;
# flags identical. I_over is the 8.2 (C-rate) quantity that decides constraint compliance (VC-05).
PROTOCOL_CHECKS = ("E_chem_rel", "E_DC_rel", "distance_rel", "trip_time_abs_s", "I_over_protocol_abs_As", "rmse_rel",
                   "stop_ok_equal", "complete_equal", "tracking_ok_equal", "constraint_ok_equal")
# the three protocol-9 quantities without a stated tolerance (amendment A1-12; 10_tolerance_approval_register.md)
PROTOCOL_TOLERANCES = {"trip_time_abs_s": 1e-9, "I_over_protocol_abs_As": 1e-6, "rmse_rel": 1e-9}


def gr_v_max(ev):
    """Upper bound factor for friction-power differences caused by a torque-limit difference: gr v_max [rad/s]."""
    return ev["gr_rad_per_m"] * ev["v_max_ms"]


# energy-closure sinks of the declared model (rebuild.model.LOSS_TERMS)
CLOSURE_LOSSES = ("E_rr", "E_aero", "E_fb", "E_gear", "E_visc", "E_mi", "E_R0", "E_R1")


def refuse_pooling(rows):
    """Results are never pooled across motor scenarios, cycles, limit sets or plant states (protocol 7.1)."""
    keys = {(r["motor_scenario"], r["cycle"], r["limits"], r["pstate"]) for r in rows}
    if len(keys) > 1:
        raise ValueError(f"refusing to pool across conditions: {sorted(keys)}")
    return keys.pop()
