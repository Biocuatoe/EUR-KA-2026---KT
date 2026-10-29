"""P2-pilot closed loop (pilot_protocol.md section 2).

The plant is R1's (`rebuild.model`, imported and unmodified). Added here, per run:
  aware    -> conditional anti-windup uses the battery-aware drive envelope T_pos (R1 rule);
              otherwise only the motor envelope min(T_max, P_max/w) (controller unaware of the BMS limit)
  governor -> the controller tracks r_g, the reference rate-limited to the acceleration the battery-aware
              envelope can deliver; braking is never altered.
Tracking metrics are always taken against the original reference.
"""

from __future__ import annotations

import numpy as np

from eureka.plant import BatchParams
from rebuild.model import IX, STATES, BatteryLimits, battery_current, energy_closure, rk4_step, torque_limits


def simulate(profile, params, gains, soh, limits: list[BatteryLimits], aware, governor, dt=None) -> dict:
    n = len(params)
    ts = params[0].Ts
    dt = params[0].dt if dt is None else dt
    sub = round(ts / dt)
    if abs(sub * dt - ts) > 1e-12:
        raise ValueError("Ts must be an integer multiple of dt")
    steps = round(profile.duration / ts)
    gains = np.asarray(gains, dtype=float).reshape(n, 3)
    soh = np.asarray(soh, dtype=float)
    aware = np.asarray(aware, dtype=bool)
    governor = np.asarray(governor, dtype=bool)
    groups: dict[BatteryLimits, list[int]] = {}
    for j, lim in enumerate(limits):
        groups.setdefault(lim, []).append(j)
    groups = {k: np.array(v) for k, v in groups.items()}
    bps = {k: BatchParams.from_params([params[j] for j in idx], soh[idx]) for k, idx in groups.items()}
    bp = BatchParams.from_params(params, soh)
    gr = bp.G / bp.r_w

    y = np.zeros((n, len(STATES)))
    y[:, IX["SoC"]] = 0.8
    y0 = y.copy()
    z = np.zeros(n)
    rg = np.zeros(n)
    acc = {k: np.zeros(n) for k in ("se2", "max_e", "max_over", "sat_batt", "gov_active", "i2", "max_i", "steps")}
    acc["max_over"][:] = -np.inf
    feasible_all = np.ones(n, dtype=bool)
    nonfinite = np.zeros(n, dtype=bool)

    for k in range(steps + 1):
        v_ref = float(profile.sample(np.array([k * ts]))[0])
        v = y[:, IX["v"]]
        t_pos = np.empty(n)
        base = np.empty(n)
        for lim, idx in groups.items():
            w_g = gr[idx] * v[idx]
            tp, _, b, _, _ = torque_limits(w_g, y[idx, IX["V1"]], bps[lim], lim)
            t_pos[idx], base[idx] = tp, b
        if k == 0:
            rg[:] = v_ref
        else:
            w = gr * v
            f_avail = gr * (t_pos - bp.B_m * w) * bp.eta_g
            f_res = bp.Crr * bp.M * bp.g * np.tanh(v / bp.v_eps) + 0.5 * bp.rho * bp.Cd * bp.A_f * v * v
            a_av = (f_avail - f_res) / bp.M_eff
            up = np.minimum(v_ref, rg + np.maximum(a_av, 0.0) * ts)
            rg_new = np.where(v_ref > rg, up, v_ref)
            rg = np.where(governor, rg_new, v_ref)
        e = v - v_ref
        e_c = v - rg
        u = -(gains[:, 0] * e_c + gains[:, 1] * y[:, IX["T"]] + gains[:, 2] * z)
        env = np.where(aware, t_pos, base)
        sat = u > env
        i, _, _, _ = battery_current(y[:, IX["T"]], gr * v, y[:, IX["V1"]], bp)

        acc["se2"] += e * e
        acc["max_e"] = np.maximum(acc["max_e"], np.abs(e))
        acc["max_over"] = np.maximum(acc["max_over"], e)
        acc["sat_batt"] += (u > t_pos) & (t_pos < base - 1e-9)
        acc["gov_active"] += rg < v_ref - 1e-9
        acc["i2"] += i * i
        acc["max_i"] = np.maximum(acc["max_i"], np.abs(i))
        acc["steps"] += 1
        nonfinite |= ~np.all(np.isfinite(y), axis=1)
        if k == steps:
            break
        z = np.where(sat & (e_c < 0), z, z + ts * e_c)
        for lim, idx in groups.items():
            yy = y[idx]
            for _ in range(sub):
                yy, feas = rk4_step(yy, u[idx], bps[lim], lim, dt)
                feasible_all[idx] &= feas
            y[idx] = yy

    closure, supplied = energy_closure(y, y0, bp)
    return {"y0": y0, "y_end": y, "acc": acc, "closure_J": closure, "feasible": feasible_all,
            "nonfinite": nonfinite, "ref_distance_m": float(profile.stats()["distance_m"]), "dt": dt}


def metrics(out: dict, j: int, p) -> dict:
    y0, y1, a = out["y0"][j], out["y_end"][j], out["acc"]
    d = (y1[IX["dist"]] - y0[IX["dist"]]) / 1000.0
    dref = out["ref_distance_m"] / 1000.0
    E = (y1[IX["E_chem"]] - y0[IX["E_chem"]]) / 3600.0
    ah = y1[IX["Ah"]] - y0[IX["Ah"]]
    thr = p.V_oc * 3600.0 * ah
    clos = float(abs(out["closure_J"][j]) / thr) if thr > 0 else float("inf")
    st = a["steps"][j]
    reasons = []
    if out["nonfinite"][j] or not np.all(np.isfinite(y1)):
        reasons.append("non-finite state")
    if not out["feasible"][j]:
        reasons.append("battery solution infeasible")
    if clos > 1e-3:
        reasons.append(f"closure {clos:.2e}")
    rmse = float(np.sqrt(a["se2"][j] / st))
    return {
        "distance_km": d, "shortfall_pct": 100 * (dref - d) / dref, "rmse_ms": rmse,
        "max_abs_err_ms": float(a["max_e"][j]), "max_overshoot_ms": float(a["max_over"][j]),
        "E_net_Wh": E, "Wh_per_km": E / d if d > 0 else float("nan"), "Wh_per_ref_km": E / dref,
        "batt_limited_frac": float(a["sat_batt"][j] / st), "governor_active_frac": float(a["gov_active"][j] / st),
        "friction_brake_Wh": (y1[IX["E_fb"]] - y0[IX["E_fb"]]) / 3600.0,
        "regen_terminal_Wh": -(y1[IX["E_regen"]] - y0[IX["E_regen"]]) / 3600.0,
        "resistive_loss_Wh": float((y1[IX["E_R0"]] + y1[IX["E_R1"]] - y0[IX["E_R0"]] - y0[IX["E_R1"]]) / 3600.0),
        "I_over_As": float(y1[IX["I_over"]] - y0[IX["I_over"]]), "Ah": float(ah),
        "peak_current_A": float(a["max_i"][j]), "rms_current_A": float(np.sqrt(a["i2"][j] / st)),
        "closure_rel": clos, "valid": not reasons, "invalid_reasons": "; ".join(reasons),
    }
