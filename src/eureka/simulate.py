"""Closed-loop simulation: 10 ms ZOH controller, 1 ms RK4 plant, batched over runs."""

from __future__ import annotations

import numpy as np

from eureka.cycles import Profile
from eureka.params import Params
from eureka.plant import IX, STATES, BatchParams, initial_state, rk4_step, torque_limit


def simulate(
    profile: Profile,
    params: list[Params],
    gains: np.ndarray,
    soh: np.ndarray,
    noise: np.ndarray | None = None,
    record_every: int = 1,
) -> dict[str, np.ndarray]:
    """Run len(params) closed loops in lockstep on the same reference profile.

    gains: (n, 3) rows K = [K_e, K_T, K_z]; u = -(K_e e + K_T T + K_z z).
    noise: optional (n, steps) additive velocity-measurement noise [m/s].
    Returns time series sampled every `record_every` control steps (index 0 = t0).
    """
    n = len(params)
    ts, dt = params[0].Ts, params[0].dt
    if any(p.Ts != ts or p.dt != dt for p in params):
        raise ValueError("all runs in a batch must share Ts and dt")
    sub = round(ts / dt)
    if abs(sub * dt - ts) > 1e-12:
        raise ValueError("Ts must be an integer multiple of dt")
    steps = round(profile.duration / ts)
    gains = np.asarray(gains, dtype=float).reshape(n, 3)
    bp = BatchParams.from_params(params, soh)

    y = initial_state(n)
    y0 = y.copy()
    z = np.zeros(n)
    rec_idx = list(range(0, steps + 1, record_every))
    if rec_idx[-1] != steps:
        rec_idx.append(steps)
    nr = len(rec_idx)
    out = {name: np.empty((nr, n)) for name in STATES}
    for name in ("t", "v_ref", "z", "t_ref", "t_lim", "sat", "i", "nonfinite", "infeasible"):
        out[name] = np.zeros((nr, n))
    infeasible = np.zeros(n, dtype=bool)
    r = 0

    for k in range(steps + 1):
        t = k * ts
        v_ref = profile.sample(np.array([t]))[0]
        v = y[:, IX["v"]]
        v_meas = v + (noise[:, k] if noise is not None and k < noise.shape[1] else 0.0)
        e = v_meas - v_ref
        u = -(gains[:, 0] * e + gains[:, 1] * y[:, IX["T"]] + gains[:, 2] * z)
        w = bp.G / bp.r_w * v
        t_lim = torque_limit(w, bp)
        sat = u > t_lim  # positive traction limit; braking excess goes to the friction brake

        if r < nr and k == rec_idx[r]:
            for name in STATES:
                out[name][r] = y[:, IX[name]]
            out["t"][r], out["v_ref"][r], out["z"][r] = t, v_ref, z
            out["t_ref"][r], out["t_lim"][r], out["sat"][r] = u, t_lim, sat
            vo = bp.V_oc - y[:, IX["V1"]]
            p_m = y[:, IX["T"]] * w
            p_e = np.where(p_m >= 0, p_m / bp.eta_mi, p_m * bp.eta_mi)
            out["i"][r] = (vo - np.sqrt(np.maximum(vo * vo - 4 * bp.R0 * p_e, 0))) / (2 * bp.R0)
            out["nonfinite"][r] = ~np.all(np.isfinite(y), axis=1)
            out["infeasible"][r] = infeasible
            r += 1
        if k == steps:
            break

        # conditional integration (anti-windup on the traction limit only)
        z = np.where(sat & (e < 0), z, z + ts * e)
        for _ in range(sub):
            y, feasible = rk4_step(y, u, bp, dt)
            infeasible |= ~feasible

    out["y0"] = y0
    out["y_end"] = y
    out["soh"] = np.asarray(soh, dtype=float)
    out["gains"] = gains
    return out
