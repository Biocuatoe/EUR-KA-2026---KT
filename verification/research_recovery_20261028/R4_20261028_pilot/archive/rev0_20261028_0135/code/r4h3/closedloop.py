"""Component C: fixed-LQR closed loop with 1 ms traces (protocol v1 2.1, 4, 10.3).

`simulate_traced` is a line-for-line port of r3_lib.simulate (frozen, lines 200-244) for one run. It
calls r3_lib's unmodified rk4_step, derivatives, torque_limits and battery_current, and in addition
records every integration-step sample. tests/test_closedloop.py checks that its end state and
accumulators equal r3_lib.simulate bitwise. The controller is the R1 fixed Bryson LQR for both arms.
"""

from __future__ import annotations

import numpy as np

from r4h3 import config

L = config.L
from eureka.controllers import gain as r1_gain  # noqa: E402
from eureka.cycles import Profile  # noqa: E402
from eureka.plant import BatchParams  # noqa: E402
from rebuild.model import IX, STATES  # noqa: E402

INTEGRATOR_CHANNELS = ("E_chem", "E_pos", "E_neg", "E_fb", "E_R0", "E_R1", "E_mi", "I_over", "Ah", "dist")


def fixed_gain(p_design):
    """R1 fixed Bryson gain designed at P1 (protocol 4); the same K is used by B0 and B3."""
    return np.ravel(r1_gain(p_design, "fixed"))


def profile_from_knots(name, t, v):
    return Profile(name, np.asarray(t, float), np.asarray(v, float))


def _signals(y, u, z, bp, lim, mm, gr):
    """Instantaneous signals at state y under the held command u (all from r3_lib functions)."""
    v = np.maximum(y[:, IX["v"]], 0.0)
    T = y[:, IX["T"]]
    V1 = y[:, IX["V1"]]
    w = gr * v
    t_pos, t_neg, base = L.torque_limits(w, V1, bp, lim, mm)
    i, p_e, p_m, ok = L.battery_current(T, w, V1, bp, mm)
    dy, _ = L.derivatives(y, u, bp, lim, mm)
    t_s = T - bp.B_m * w
    p_wheel = t_s * w - dy[:, IX["E_gear"]]                    # f_w v (derivatives: E_gear rate = t_s w - f_w v)
    return dict(v_mps=y[:, IX["v"]], T_Nm=T, w_radps=w, u_cmd_Nm=u, z_int_m=z,
                t_cmd_eff_Nm=np.clip(u, -t_neg, t_pos), t_pos_Nm=t_pos, t_neg_Nm=t_neg,
                p_mech_W=p_m, p_elec_W=p_e, i_A=i, V1_V=V1, Vt_V=bp.V_oc - V1 - bp.R0 * i, SoC=y[:, IX["SoC"]],
                P_wheel_W=p_wheel, P_regen_wheel_W=np.maximum(-p_wheel, 0.0), P_fric_W=dy[:, IX["E_fb"]],
                batt_feasible=ok.astype(float), limit_active=((u > t_pos) | (u < -t_neg)).astype(float),
                **{f"int_{k}": y[:, IX[k]] for k in INTEGRATOR_CHANNELS})


def simulate_traced(profile, p, K, soh, lim, mm, dt=None, record=True):
    """r3_lib.simulate for n = 1, plus per-step traces. Returns (out, traces or None)."""
    params = [p]
    n = 1
    ts = params[0].Ts
    dt = params[0].dt if dt is None else dt
    sub = round(ts / dt)
    if abs(sub * dt - ts) > 1e-12:
        raise ValueError("Ts must be an integer multiple of dt")
    steps = round(profile.duration / ts)
    gains = np.asarray(K, dtype=float).reshape(n, 3)
    bp = BatchParams.from_params(params, np.asarray([soh], dtype=float))
    gr = bp.G / bp.r_w
    y = np.zeros((n, len(STATES)))
    y[:, IX["SoC"]] = 0.8
    y0 = y.copy()
    z = np.zeros(n)
    acc = {k: np.zeros(n) for k in ("se2", "max_e", "i2", "max_i", "sat_batt", "steps")}
    feasible = np.ones(n, dtype=bool)
    nonfinite = np.zeros(n, dtype=bool)
    nrec = steps * sub + 1
    tr = None
    idx = 0

    def rec(u_now, z_now, v_tracked):
        nonlocal tr, idx
        s = _signals(y, u_now, z_now, bp, lim, mm, gr)
        if tr is None:
            tr = {k: np.empty(nrec) for k in s}
            tr["t_s"] = np.empty(nrec)
            tr["v_tracked_mps"] = np.empty(nrec)
        for k_, val in s.items():
            tr[k_][idx] = val[0]
        tr["t_s"][idx] = idx * dt
        tr["v_tracked_mps"][idx] = v_tracked
        idx += 1

    for k in range(steps + 1):
        v_ref = float(profile.sample(np.array([k * ts]))[0])
        v = y[:, IX["v"]]
        e = v - v_ref
        u = -(gains[:, 0] * e + gains[:, 1] * y[:, IX["T"]] + gains[:, 2] * z)
        t_pos, _, base = L.torque_limits(gr * v, y[:, IX["V1"]], bp, lim, mm)
        sat = u > t_pos
        i, _, _, _ = L.battery_current(y[:, IX["T"]], gr * v, y[:, IX["V1"]], bp, mm)
        acc["se2"] += e * e
        acc["max_e"] = np.maximum(acc["max_e"], np.abs(e))
        acc["i2"] += i * i
        acc["max_i"] = np.maximum(acc["max_i"], np.abs(i))
        acc["sat_batt"] += sat & (t_pos < base - 1e-9)
        acc["steps"] += 1
        nonfinite |= ~np.all(np.isfinite(y), axis=1)
        if k == steps:
            if record:
                rec(u, z, v_ref)
            break
        z_used = z.copy()
        z = np.where(sat & (e < 0), z, z + ts * e)
        for j in range(sub):
            if record:
                rec(u, z_used, float(profile.sample(np.array([k * ts + j * dt]))[0]))
            y, f = L.rk4_step(y, u, bp, lim, mm, dt)
            feasible &= f
    closure, supplied = L.energy_closure(y, y0, bp)
    out = {"y0": y0, "y_end": y, "acc": acc, "closure_J": closure, "feasible": feasible, "nonfinite": nonfinite,
           "ref_distance_m": float(profile.stats()["distance_m"]), "dt": dt}
    if record and idx != nrec:
        raise RuntimeError(f"trace length {idx} != expected {nrec}")
    return out, tr


def run_metrics(out, p, soh, d_ref, duration, Ts):
    """Simulator-side metrics from integrator states and accumulators (compared later with the evaluator)."""
    m = L.sim_metrics(out, 0, p)
    y0, y1 = out["y0"][0], out["y_end"][0]
    bp = BatchParams.from_params([p], np.asarray([soh], dtype=float))
    dlt = {k: float(y1[IX[k]] - y0[IX[k]]) for k in ("E_chem", "E_R0", "E_R1", "E_pos", "E_neg", "E_fb", "dist")}
    dE_C1 = 0.5 * float(bp.C1[0]) * float(y1[IX["V1"]] ** 2 - y0[IX["V1"]] ** 2)
    m.update(
        d_ref_m=d_ref, trip_time_s=duration, Wh_per_ref_km=m["E_net_Wh"] / (d_ref / 1000.0),
        shortfall_vs_dref_pct=100.0 * (d_ref - dlt["dist"]) / d_ref,
        E_DC_Wh=(dlt["E_chem"] - dlt["E_R0"] - dlt["E_R1"] - dE_C1) / 3600.0,   # V_t i = V_oc i - R0 i^2 - V1 i
        E_pos_Wh=dlt["E_pos"] / 3600.0, E_neg_Wh=dlt["E_neg"] / 3600.0, friction_brake_Wh=dlt["E_fb"] / 3600.0,
        I2_A2s_control_samples=float(out["acc"]["i2"][0] * Ts),
        recompute_pos_neg_rel=abs(dlt["E_pos"] + dlt["E_neg"] - dlt["E_chem"]) / max(abs(dlt["E_pos"]), 1e-9))
    return m
