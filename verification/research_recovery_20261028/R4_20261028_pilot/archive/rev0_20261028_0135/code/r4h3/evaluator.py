"""Component E: independent energy and validity evaluation from a retained trace (protocol v1 7, 8.2, 9).

Deliberately independent of the simulator and planner: this module imports neither r3_lib nor the
planner. It re-implements the motor-loss, battery-current and battery-limit formulas from the protocol
text, recomputes the battery current from the traced torque, speed and V1, and integrates every
quantity by the trapezoid rule over the 1 ms samples.

Sign convention: battery current i > 0 on discharge. Energy at the primary boundary (protocol 7.1) is
E_chem = integral of V_oc i dt: propulsion energy enters positive, regenerated energy negative, and the
net value is reported. Auxiliary load is 0 W (not modelled). Regenerative-braking efficiency
(protocol 7.3) is reported separately and never mixed with Wh/km.
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


# --------------------------------------------------------------------------- evaluation
def evaluate_trace(a: dict, spec: dict, rules: dict) -> dict:
    """All protocol 7 metrics and 8.2 flags from the trace channels `a` and the run specification."""
    b, motor = spec["battery"], spec["motor"]
    t = a["t_s"]
    v = np.maximum(a["v_mps"], 0.0)
    w = spec["G"] / spec["r_w"] * v
    i, p_e, feas = battery_current(a["T_Nm"], w, a["V1_V"], b, motor)
    vt = b["V_oc"] - a["V1_V"] - b["R0"] * i
    sub = int(round(spec["Ts_s"] / spec["dt_s"]))
    ctrl = np.arange(0, len(t), sub)
    e = a["v_mps"][ctrl] - a["v_tracked_mps"][ctrl]
    d = _trapz(v, t)
    E = _trapz(b["V_oc"] * i, t)
    # Friction power depends on the zero-order-hold command u, which jumps at control instants. Each interval
    # is therefore integrated with the u held over it: start value from the trace, end value recomputed here
    # from (u_start, t_neg_end, v_end) with the protocol's friction law gr max(0, -t_neg - u) tanh(v/v_eps) v.
    gr = spec["G"] / spec["r_w"]

    def fric(u, t_neg, vv):
        return gr * np.maximum(0.0, -t_neg - u) * np.tanh(vv / spec["v_eps"]) * vv

    p_fric_start_re = fric(a["u_cmd_Nm"], a["t_neg_Nm"], v)
    p_fric_end = fric(a["u_cmd_Nm"][:-1], a["t_neg_Nm"][1:], v[1:])
    fric_J = float(np.sum(0.5 * (a["P_fric_W"][:-1] + p_fric_end) * np.diff(t)))
    W_brake = _trapz(a["P_regen_wheel_W"], t) + fric_J
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
        "rmse_vs_task_ref_ms": float(np.sqrt(np.mean((a["v_mps"][ctrl] - a["v_ref_task_mps"][ctrl]) ** 2))),
        "friction_power_max_abs_diff_W": float(np.max(np.abs(p_fric_start_re - a["P_fric_W"]))),
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
        "batt_limited_time_frac": float(np.mean(a["limit_active"])),
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
    """Protocol 9 'independent recomputation': evaluator vs simulator-side values."""
    def rel(x, y):
        return abs(x - y) / max(abs(y), 1e-12)

    checks = {
        "E_chem_rel": (rel(ev["E_chem_Wh"], sim["E_net_Wh"]), rules["recompute_energy_rel"]),
        "E_DC_rel": (rel(ev["E_DC_Wh"], sim["E_DC_Wh"]), rules["recompute_energy_rel"]),
        "E_pos_rel": (rel(ev["E_pos_Wh"], sim["E_pos_Wh"]), rules["recompute_energy_rel"]),
        "friction_abs_Wh": (abs(ev["friction_brake_Wh"] - sim["friction_brake_Wh"]), 1e-6),
        "distance_rel": (rel(ev["distance_m"], sim["distance_km"] * 1000.0), rules["recompute_distance_rel"]),
        "trip_time_abs_s": (abs(ev["trip_time_s"] - sim["trip_time_s"]), 1e-9),
        "rmse_rel": (rel(ev["rmse_ms"], sim["rmse_ms"]), 1e-9),
        "max_err_rel": (rel(ev["max_abs_err_ms"], sim["max_abs_err_ms"]), 1e-9),
        "I_over_window_abs_As": (abs(ev["I_over_window_As"] - sim["I_over_As"]), 1e-4),
        "current_recompute_abs_A": (ev["current_max_abs_diff_A"], 1e-9),
        "friction_power_recompute_abs_W": (ev["friction_power_max_abs_diff_W"], 1e-9),
    }
    flags = {"stop_ok_equal": ev["stop_ok"] == sim["stop_ok_sim"]}
    res = {k: dict(value=float(x), tol=tol, ok=bool(x <= tol)) for k, (x, tol) in checks.items()}
    res.update({k: dict(value=v, tol=None, ok=bool(v)) for k, v in flags.items()})
    res["all_ok"] = all(r["ok"] for r in res.values())
    return res


def refuse_pooling(rows):
    """Results are never pooled across motor scenarios, cycles, limit sets or plant states (protocol 7.1)."""
    keys = {(r["motor_scenario"], r["cycle"], r["limits"], r["pstate"]) for r in rows}
    if len(keys) > 1:
        raise ValueError(f"refusing to pool across conditions: {sorted(keys)}")
    return keys.pop()
