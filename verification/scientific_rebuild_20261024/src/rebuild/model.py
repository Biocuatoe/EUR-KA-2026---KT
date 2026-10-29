"""Documented EV plant (eureka.plant) plus a battery operating window that bounds motor torque.

With every limit disabled, `derivatives` reproduces `eureka.plant.derivatives` exactly (tested).
Equations: ../../model_equations.md. Nothing in src/eureka is modified.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from eureka.cycles import Profile
from eureka.params import Params
from eureka.plant import STATES as BASE_STATES
from eureka.plant import BatchParams

STATES = BASE_STATES + ("E_pos", "E_neg", "I_over")
IX = {name: i for i, name in enumerate(STATES)}
LOSS_TERMS = ("E_rr", "E_aero", "E_fb", "E_gear", "E_visc", "E_mi", "E_R0", "E_R1")
INF = np.inf


@dataclass(frozen=True)
class BatteryLimits:
    """Battery operating window. Currents in C-rate of nominal capacity (A per Ah)."""

    c_dis: float = INF
    c_ch: float = INF
    soh_scaled: bool = False
    v_min_ratio: float = 0.0  # V_min / V_oc; 0 disables the lower voltage limit
    v_max_ratio: float = INF  # V_max / V_oc; inf disables the upper voltage limit

    @property
    def active(self) -> bool:
        return bool(
            np.isfinite(self.c_dis)
            or np.isfinite(self.c_ch)
            or self.v_min_ratio > 0
            or np.isfinite(self.v_max_ratio)
        )


def battery_limits(V1: np.ndarray, bp: BatchParams, lim: BatteryLimits):
    """Max discharge/charge current magnitudes [A] and electrical powers [W] at the terminals.

    Discharge (I > 0): V_t = Vo - R0 I >= V_min, I <= I_dis, and I <= Vo/(2 R0) (max-power point).
    Charge (I < 0, magnitude Ic): V_t = Vo + R0 Ic <= V_max, Ic <= I_ch.
    """
    vo = bp.V_oc - V1
    s = bp.soh if lim.soh_scaled else 1.0
    i_dis = lim.c_dis * bp.Q_Ah * s
    i_ch = lim.c_ch * bp.Q_Ah * s
    v_min = lim.v_min_ratio * bp.V_oc
    v_max = lim.v_max_ratio * bp.V_oc
    i_v = np.maximum((vo - v_min) / bp.R0, 0.0)
    i_d = np.minimum(np.minimum(i_dis, i_v), vo / (2.0 * bp.R0))
    p_d = (vo - bp.R0 * i_d) * i_d
    i_cv = np.where(np.isfinite(v_max), np.maximum((v_max - vo) / bp.R0, 0.0), INF)
    i_c = np.minimum(i_ch, i_cv)
    p_c = np.where(np.isfinite(i_c), (vo + bp.R0 * np.where(np.isfinite(i_c), i_c, 0.0)) * i_c, INF)
    return i_d, i_c, p_d, p_c


def torque_limits(w: np.ndarray, V1: np.ndarray, bp: BatchParams, lim: BatteryLimits):
    """(drive limit, regen limit, motor-only limit, i_d, i_c), all >= 0."""
    w_pos = np.maximum(w, 1e-6)
    base = np.minimum(bp.T_max, bp.P_max / w_pos)
    if not lim.active:
        inf = np.full_like(base, INF)
        return base, base, base, inf, inf
    i_d, i_c, p_d, p_c = battery_limits(V1, bp, lim)
    t_pos = np.minimum(base, bp.eta_mi * p_d / w_pos)
    t_neg = np.minimum(base, p_c / (bp.eta_mi * w_pos))
    return t_pos, t_neg, base, i_d, i_c


def battery_current(T, w, V1, bp):
    p_m = T * w
    p_e = np.where(p_m >= 0, p_m / bp.eta_mi, p_m * bp.eta_mi)
    vo = bp.V_oc - V1
    disc = vo * vo - 4.0 * bp.R0 * p_e
    i = (vo - np.sqrt(np.maximum(disc, 0.0))) / (2.0 * bp.R0)
    return i, p_e, p_m, disc >= 0


def derivatives(y, t_ref, bp: BatchParams, lim: BatteryLimits):
    v_raw = y[:, IX["v"]]
    v = np.maximum(v_raw, 0.0)
    T = y[:, IX["T"]]
    V1 = y[:, IX["V1"]]
    gr = bp.G / bp.r_w
    w = gr * v
    t_pos, t_neg, _, i_d, i_c = torque_limits(w, V1, bp, lim)
    t_cmd = np.clip(t_ref, -t_neg, t_pos)

    t_s = T - bp.B_m * w
    f_w = np.where(t_s >= 0, gr * t_s * bp.eta_g, gr * t_s / bp.eta_g)
    s = np.tanh(v / bp.v_eps)
    f_rr = bp.Crr * bp.M * bp.g * s
    f_aero = 0.5 * bp.rho * bp.Cd * bp.A_f * v * v
    f_fb = gr * np.maximum(0.0, -t_neg - t_ref) * s
    dv = (f_w - f_rr - f_aero - f_fb) / bp.M_eff
    dv = np.where((v_raw <= 0.0) & (dv < 0.0), 0.0, dv)

    i, p_e, p_m, feasible = battery_current(T, w, V1, bp)

    dy = np.empty_like(y)
    dy[:, IX["v"]] = dv
    dy[:, IX["T"]] = (t_cmd - T) / bp.tau_T
    dy[:, IX["V1"]] = -V1 / (bp.R1 * bp.C1) + i / bp.C1
    dy[:, IX["SoC"]] = -i / (3600.0 * bp.Q_Ah * bp.soh)
    dy[:, IX["E_chem"]] = bp.V_oc * i
    dy[:, IX["E_rr"]] = f_rr * v
    dy[:, IX["E_aero"]] = f_aero * v
    dy[:, IX["E_fb"]] = f_fb * v
    dy[:, IX["E_gear"]] = t_s * w - f_w * v
    dy[:, IX["E_visc"]] = bp.B_m * w * w
    dy[:, IX["E_mi"]] = p_e - p_m
    dy[:, IX["E_R0"]] = bp.R0 * i * i
    dy[:, IX["E_R1"]] = V1 * V1 / bp.R1
    dy[:, IX["dist"]] = v
    dy[:, IX["Ah"]] = np.abs(i) / 3600.0
    dy[:, IX["E_regen"]] = np.minimum(p_e, 0.0)
    dy[:, IX["E_pos"]] = np.maximum(bp.V_oc * i, 0.0)
    dy[:, IX["E_neg"]] = np.minimum(bp.V_oc * i, 0.0)
    if lim.active:
        over = np.maximum(i - i_d, 0.0) + np.maximum(-i - i_c, 0.0)
        dy[:, IX["I_over"]] = np.where(np.isfinite(over), over, 0.0)
    else:
        dy[:, IX["I_over"]] = 0.0
    return dy, feasible


def rk4_step(y, t_ref, bp, lim, h):
    k1, f1 = derivatives(y, t_ref, bp, lim)
    k2, f2 = derivatives(y + 0.5 * h * k1, t_ref, bp, lim)
    k3, f3 = derivatives(y + 0.5 * h * k2, t_ref, bp, lim)
    k4, f4 = derivatives(y + h * k3, t_ref, bp, lim)
    out = y + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
    out[:, IX["v"]] = np.maximum(out[:, IX["v"]], 0.0)
    return out, f1 & f2 & f3 & f4


def energy_closure(y_end, y0, bp):
    ke = 0.5 * bp.M_eff * (y_end[:, IX["v"]] ** 2 - y0[:, IX["v"]] ** 2)
    ec1 = 0.5 * bp.C1 * (y_end[:, IX["V1"]] ** 2 - y0[:, IX["V1"]] ** 2)
    sinks = ke + ec1 + sum(y_end[:, IX[k]] - y0[:, IX[k]] for k in LOSS_TERMS)
    supplied = y_end[:, IX["E_chem"]] - y0[:, IX["E_chem"]]
    return supplied - sinks, supplied


def simulate(
    profile: Profile,
    params: list[Params],
    gains: np.ndarray,
    soh: np.ndarray,
    limits: list[BatteryLimits],
    record_every: int = 100,
    dt: float | None = None,
) -> dict:
    """Closed loop as eureka.simulate (10 ms ZOH, RK4 substeps), with per-run battery limits.

    Metrics are accumulated at every control step (same sampling as eureka.metrics on runs
    recorded at every step); time series are stored every `record_every` control steps.
    Runs are grouped by identical BatteryLimits so each group shares one derivative call.
    """
    n = len(params)
    ts = params[0].Ts
    dt = params[0].dt if dt is None else dt
    sub = round(ts / dt)
    if abs(sub * dt - ts) > 1e-12:
        raise ValueError("Ts must be an integer multiple of dt")
    steps = round(profile.duration / ts)
    gains = np.asarray(gains, dtype=float).reshape(n, 3)
    soh = np.asarray(soh, dtype=float)
    groups: dict[BatteryLimits, np.ndarray] = {}
    for j, lim in enumerate(limits):
        groups.setdefault(lim, []).append(j)
    groups = {k: np.array(v) for k, v in groups.items()}
    bps = {k: BatchParams.from_params([params[j] for j in idx], soh[idx]) for k, idx in groups.items()}
    bp_all = BatchParams.from_params(params, soh)

    y = np.zeros((n, len(STATES)))
    y[:, IX["SoC"]] = 0.8
    y0 = y.copy()
    z = np.zeros(n)
    acc = {k: np.zeros(n) for k in ("se2", "max_e", "sat", "sat_batt", "i2", "max_i", "vt_min", "vt_max", "steps")}
    acc["vt_min"][:] = INF
    acc["vt_max"][:] = -INF
    feasible_all = np.ones(n, dtype=bool)
    nonfinite = np.zeros(n, dtype=bool)
    rec = {k: [] for k in ("t", "v_ref", "v", "T", "u", "t_pos", "t_neg", "i", "v_t", "i_d", "SoC", "dist", "E_chem", "E_fb")}

    for k in range(steps + 1):
        t = k * ts
        v_ref = float(profile.sample(np.array([t]))[0])
        v = y[:, IX["v"]]
        e = v - v_ref
        u = -(gains[:, 0] * e + gains[:, 1] * y[:, IX["T"]] + gains[:, 2] * z)
        t_pos = np.empty(n)
        t_neg = np.empty(n)
        base = np.empty(n)
        i_d = np.empty(n)
        for lim, idx in groups.items():
            bp = bps[lim]
            w_g = bp.G / bp.r_w * y[idx, IX["v"]]
            tp, tn, b, idd, _ = torque_limits(w_g, y[idx, IX["V1"]], bp, lim)
            t_pos[idx], t_neg[idx], base[idx], i_d[idx] = tp, tn, b, idd
        sat = u > t_pos
        w = bp_all.G / bp_all.r_w * v
        i, _, _, _ = battery_current(y[:, IX["T"]], w, y[:, IX["V1"]], bp_all)
        v_t = bp_all.V_oc - y[:, IX["V1"]] - bp_all.R0 * i

        acc["se2"] += e * e
        acc["max_e"] = np.maximum(acc["max_e"], np.abs(e))
        acc["sat"] += sat
        acc["sat_batt"] += sat & (t_pos < base - 1e-9)
        acc["i2"] += i * i
        acc["max_i"] = np.maximum(acc["max_i"], np.abs(i))
        acc["vt_min"] = np.minimum(acc["vt_min"], v_t)
        acc["vt_max"] = np.maximum(acc["vt_max"], v_t)
        acc["steps"] += 1
        nonfinite |= ~np.all(np.isfinite(y), axis=1)
        if k % record_every == 0 or k == steps:
            for name, val in (("t", np.full(n, t)), ("v_ref", np.full(n, v_ref)), ("v", v), ("T", y[:, IX["T"]]),
                              ("u", u), ("t_pos", t_pos), ("t_neg", t_neg), ("i", i), ("v_t", v_t), ("i_d", i_d),
                              ("SoC", y[:, IX["SoC"]]), ("dist", y[:, IX["dist"]]), ("E_chem", y[:, IX["E_chem"]]),
                              ("E_fb", y[:, IX["E_fb"]])):
                rec[name].append(np.array(val, dtype=float))
        if k == steps:
            break
        z = np.where(sat & (e < 0), z, z + ts * e)
        for lim, idx in groups.items():
            yy = y[idx]
            for _ in range(sub):
                yy, feas = rk4_step(yy, u[idx], bps[lim], lim, dt)
                feasible_all[idx] &= feas
            y[idx] = yy

    closure, supplied = energy_closure(y, y0, bp_all)
    return {
        "y0": y0,
        "y_end": y,
        "acc": acc,
        "closure_J": closure,
        "supplied_J": supplied,
        "feasible": feasible_all,
        "nonfinite": nonfinite,
        "series": {k: np.array(v, dtype=np.float32) for k, v in rec.items()},
        "ref_distance_m": float(profile.stats()["distance_m"]),
        "steps": steps,
        "dt": dt,
    }
