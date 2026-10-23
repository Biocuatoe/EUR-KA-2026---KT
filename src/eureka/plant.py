"""Nonlinear longitudinal EV plant (docs/model.md), vectorised over a batch of runs."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from eureka.params import Params

STATES = (
    "v",
    "T",
    "V1",
    "SoC",
    "E_chem",
    "E_rr",
    "E_aero",
    "E_fb",
    "E_gear",
    "E_visc",
    "E_mi",
    "E_R0",
    "E_R1",
    "dist",
    "Ah",
    "E_regen",
)
IX = {name: i for i, name in enumerate(STATES)}
LOSS_TERMS = ("E_rr", "E_aero", "E_fb", "E_gear", "E_visc", "E_mi", "E_R0", "E_R1")


@dataclass
class BatchParams:
    """Per-run parameter arrays (shape (n,)) used inside the derivative."""

    M: np.ndarray
    M_eff: np.ndarray
    A_f: np.ndarray
    Cd: np.ndarray
    Crr: np.ndarray
    r_w: np.ndarray
    rho: np.ndarray
    g: np.ndarray
    G: np.ndarray
    eta_g: np.ndarray
    B_m: np.ndarray
    eta_mi: np.ndarray
    T_max: np.ndarray
    P_max: np.ndarray
    tau_T: np.ndarray
    V_oc: np.ndarray
    Q_Ah: np.ndarray
    R0: np.ndarray
    R1: np.ndarray
    C1: np.ndarray
    soh: np.ndarray
    v_eps: np.ndarray

    @classmethod
    def from_params(cls, params: list[Params], soh: np.ndarray) -> BatchParams:
        def arr(name: str) -> np.ndarray:
            return np.array([getattr(p, name) for p in params], dtype=float)

        soh = np.asarray(soh, dtype=float)
        return cls(
            M=arr("M"),
            M_eff=np.array([p.M_eff for p in params]),
            A_f=arr("A_f"),
            Cd=arr("Cd"),
            Crr=arr("Crr"),
            r_w=arr("r_w"),
            rho=arr("rho"),
            g=arr("g"),
            G=arr("G"),
            eta_g=arr("eta_g"),
            B_m=arr("B_m"),
            eta_mi=arr("eta_mi"),
            T_max=arr("T_max"),
            P_max=arr("P_max"),
            tau_T=arr("tau_T"),
            V_oc=arr("V_oc"),
            Q_Ah=arr("Q_Ah"),
            R0=arr("R0_new") * (1 + arr("k_r0") * (1 - soh)),
            R1=arr("R1_new") * (1 + arr("k_r1") * (1 - soh)),
            C1=arr("C1"),
            soh=soh,
            v_eps=arr("v_eps"),
        )


def torque_limit(w: np.ndarray, bp: BatchParams) -> np.ndarray:
    return np.minimum(bp.T_max, bp.P_max / np.maximum(w, 1e-6))


def derivatives(y: np.ndarray, t_ref: np.ndarray, bp: BatchParams) -> tuple[np.ndarray, dict]:
    """dy/dt for state matrix y (n, 16) under held torque request t_ref (n,)."""
    v_raw = y[:, IX["v"]]
    v = np.maximum(v_raw, 0.0)
    T = y[:, IX["T"]]
    V1 = y[:, IX["V1"]]
    gr = bp.G / bp.r_w
    w = gr * v
    t_lim = torque_limit(w, bp)
    t_cmd = np.clip(t_ref, -t_lim, t_lim)

    t_s = T - bp.B_m * w
    f_w = np.where(t_s >= 0, gr * t_s * bp.eta_g, gr * t_s / bp.eta_g)
    s = np.tanh(v / bp.v_eps)
    f_rr = bp.Crr * bp.M * bp.g * s
    f_aero = 0.5 * bp.rho * bp.Cd * bp.A_f * v * v
    f_fb = gr * np.maximum(0.0, -t_lim - t_ref) * s
    dv = (f_w - f_rr - f_aero - f_fb) / bp.M_eff
    dv = np.where((v_raw <= 0.0) & (dv < 0.0), 0.0, dv)  # holding brake: no reversing

    p_m = T * w
    p_e = np.where(p_m >= 0, p_m / bp.eta_mi, p_m * bp.eta_mi)
    vo = bp.V_oc - V1
    disc = vo * vo - 4.0 * bp.R0 * p_e
    feasible = disc >= 0
    i = (vo - np.sqrt(np.maximum(disc, 0.0))) / (2.0 * bp.R0)

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
    return dy, {"i": i, "t_lim": t_lim, "feasible": feasible, "f_fb": f_fb}


def rk4_step(
    y: np.ndarray, t_ref: np.ndarray, bp: BatchParams, h: float
) -> tuple[np.ndarray, np.ndarray]:
    """One RK4 step; also returns whether every stage had a real battery-current solution."""
    k1, a1 = derivatives(y, t_ref, bp)
    k2, a2 = derivatives(y + 0.5 * h * k1, t_ref, bp)
    k3, a3 = derivatives(y + 0.5 * h * k2, t_ref, bp)
    k4, a4 = derivatives(y + h * k3, t_ref, bp)
    out = y + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
    out[:, IX["v"]] = np.maximum(out[:, IX["v"]], 0.0)
    feasible = a1["feasible"] & a2["feasible"] & a3["feasible"] & a4["feasible"]
    return out, feasible


def initial_state(n: int, soc0: float = 0.8) -> np.ndarray:
    y = np.zeros((n, len(STATES)))
    y[:, IX["SoC"]] = soc0
    return y


def energy_closure(y_end: np.ndarray, y0: np.ndarray, bp: BatchParams) -> dict[str, np.ndarray]:
    """Supplied chemical energy minus all sinks; returns absolute and relative error."""
    ke = 0.5 * bp.M_eff * (y_end[:, IX["v"]] ** 2 - y0[:, IX["v"]] ** 2)
    ec1 = 0.5 * bp.C1 * (y_end[:, IX["V1"]] ** 2 - y0[:, IX["V1"]] ** 2)
    sinks = ke + ec1 + sum(y_end[:, IX[k]] - y0[:, IX[k]] for k in LOSS_TERMS)
    supplied = y_end[:, IX["E_chem"]] - y0[:, IX["E_chem"]]
    err = supplied - sinks
    return {"abs_J": err, "supplied_J": supplied, "sinks_J": sinks}
