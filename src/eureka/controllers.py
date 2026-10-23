"""Fixed-gain and SoH-scheduled discrete LQR (preregistration section 5)."""

from __future__ import annotations

import numpy as np
from scipy.linalg import expm, solve_discrete_are

from eureka.params import Params


def design_model(p: Params) -> tuple[np.ndarray, np.ndarray]:
    """Continuous linear model, x = [e, T, z], u = T_ref (docs/model.md section 2)."""
    a = (p.rho * p.Cd * p.A_f * p.v0 + p.B_m * p.G**2 / p.r_w**2 * p.eta_g) / p.M_eff
    b = p.G * p.eta_g / (p.r_w * p.M_eff)
    A = np.array([[-a, b, 0.0], [0.0, -1.0 / p.tau_T, 0.0], [1.0, 0.0, 0.0]])
    B = np.array([[0.0], [1.0 / p.tau_T], [0.0]])
    return A, B


def zoh(A: np.ndarray, B: np.ndarray, Ts: float) -> tuple[np.ndarray, np.ndarray]:
    n, m = B.shape
    blk = np.zeros((n + m, n + m))
    blk[:n, :n], blk[:n, n:] = A, B
    e = expm(blk * Ts)
    return e[:n, :n], e[:n, n:]


def bryson_weights(p: Params) -> tuple[np.ndarray, np.ndarray]:
    Q = np.diag([1 / p.e_max**2, 1 / p.T_bryson**2, 1 / p.z_max**2])
    R = np.array([[1 / p.T_bryson**2]])
    return Q, R


def scheduled_weights(
    Q0: np.ndarray, R0: np.ndarray, soh: float, gamma_v: float, gamma_u: float
) -> tuple[np.ndarray, np.ndarray]:
    """Report Eqs. 4.39-4.41 with alpha_v applied to the torque state (mapping (a))."""
    alpha_v = 1.0 / (1.0 + gamma_v * (1.0 - soh))
    Q = Q0 @ np.diag([1.0, alpha_v, 1.0])
    R = R0 * (1.0 + gamma_u * (1.0 - soh))
    return Q, R


def dlqr(Ad: np.ndarray, Bd: np.ndarray, Q: np.ndarray, R: np.ndarray):
    P = solve_discrete_are(Ad, Bd, Q, R)
    K = np.linalg.solve(R + Bd.T @ P @ Bd, Bd.T @ P @ Ad)
    eig = np.linalg.eigvals(Ad - Bd @ K)
    return K, P, eig


def gain(
    p: Params,
    kind: str,
    soh: float = 1.0,
    r_scale: float = 1.0,
    gamma_v: float | None = None,
    gamma_u: float | None = None,
) -> np.ndarray:
    """Return K (1 x 3) for 'fixed' or 'scheduled'; r_scale multiplies R (fixed family S-C)."""
    Ad, Bd = zoh(*design_model(p), p.Ts)
    Q0, R0 = bryson_weights(p)
    if kind == "fixed":
        Q, R = Q0, R0 * r_scale
    elif kind == "scheduled":
        gv = p.gamma_v if gamma_v is None else gamma_v
        gu = p.gamma_u if gamma_u is None else gamma_u
        Q, R = scheduled_weights(Q0, R0, soh, gv, gu)
    else:
        raise ValueError(kind)
    K, _, eig = dlqr(Ad, Bd, Q, R)
    if np.max(np.abs(eig)) >= 1.0:
        raise RuntimeError(f"unstable design: {eig}")
    return K
