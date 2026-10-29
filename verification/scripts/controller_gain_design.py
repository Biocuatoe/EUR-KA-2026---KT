"""Independent design of the fixed-gain and SoH-scheduled LQR gains (controller cross-check, verification/controller-port-design.md).

Reads ONLY configs/parameters.yaml (data) and the design equations of docs/model.md section 2 and preregistration section 5.
Imports nothing from eureka and does not read the saved gains while designing. Three routes to every gain:
  (1) 50-digit mpmath: exact ZOH (series of the augmented matrix exponential) and the structured doubling algorithm (SDA);
  (2) the same SDA in float64 (numpy);
  (3) scipy expm + scipy.linalg.solve_discrete_are (same library family as the project, listed for the record).
The FROZEN gain is route (1) rounded to the nearest float64 (the "exact" LQR gain of the specified design).
Only after that, the gains saved by the Python experiment (artifacts/raw/primary/*/manifest.json) are read and compared.
Writes verification/references/controller_gains.json   (usage: python controller_gain_design.py <project root>)
"""
import hashlib
import json
import pathlib
import platform
import sys

import mpmath as mp
import numpy as np
import scipy
import scipy.linalg as sl
import yaml

mp.mp.dps = 50
root = pathlib.Path(sys.argv[1])
cfg = yaml.safe_load((root / "configs/parameters.yaml").read_text(encoding="utf-8"))
V = {f"{g}.{k}": s["value"] for g, it in cfg.items() if isinstance(it, dict) for k, s in it.items()}
sha = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

M, Cd, Af, rho = V["vehicle.mass"], V["vehicle.drag_coefficient"], V["vehicle.frontal_area"], V["vehicle.air_density"]
rw, G, eg, Jm, Bm = V["vehicle.wheel_radius"], V["drivetrain.gear_ratio"], V["drivetrain.gear_efficiency"], V["drivetrain.motor_inertia"], V["drivetrain.motor_viscous_friction"]
tau, Ts, v0 = V["drivetrain.torque_time_constant"], V["controller.sample_time"], V["controller.linearisation_speed"]
emax, Tb, zmax = V["controller.bryson_velocity_error_max"], V["controller.bryson_torque_max"], V["controller.bryson_integral_error_max"]
gv, gu = V["controller.gamma_v"], V["controller.gamma_u"]


def design(mpf):
    """Return (Ad, Bd, Q0, R0) as mp matrices from the specification, in precision `mpf`."""
    Meff = mpf(M) + mpf(Jm) * mpf(G) ** 2 / mpf(rw) ** 2
    a = (mpf(rho) * mpf(Cd) * mpf(Af) * mpf(v0) + mpf(Bm) * mpf(G) ** 2 / mpf(rw) ** 2 * mpf(eg)) / Meff
    b = mpf(G) * mpf(eg) / (mpf(rw) * Meff)
    A = mp.matrix([[-a, b, 0], [0, -1 / mpf(tau), 0], [1, 0, 0]])
    B = mp.matrix([[0], [1 / mpf(tau)], [0]])
    blk = mp.zeros(4, 4)
    for i in range(3):
        for j in range(3):
            blk[i, j] = A[i, j] * mpf(Ts)
        blk[i, 3] = B[i, 0] * mpf(Ts)
    E = mp.expm(blk)  # exact ZOH of the augmented matrix at 50 digits
    Ad = E[:3, :3]
    Bd = E[:3, 3]
    Q0 = mp.diag([1 / mpf(emax) ** 2, 1 / mpf(Tb) ** 2, 1 / mpf(zmax) ** 2])
    R0 = mp.matrix([[1 / mpf(Tb) ** 2]])
    return Ad, Bd, Q0, R0, a, b, Meff


def weights(Q0, R0, soh, kind):
    if kind == "fixed":
        return Q0, R0
    alpha = 1 / (1 + mp.mpf(gv) * (1 - mp.mpf(soh)))
    Q = Q0 * mp.diag([1, alpha, 1])
    R = R0 * (1 + mp.mpf(gu) * (1 - mp.mpf(soh)))
    return Q, R


def sda_mp(Ad, Bd, Q, R, tol=mp.mpf(10) ** -40, itmax=80):
    n = Ad.rows
    I = mp.eye(n)
    A_, G_, H_ = Ad, Bd * mp.inverse(R) * Bd.T, Q
    for it in range(itmax):
        W = mp.inverse(I + G_ * H_)
        A2 = A_ * W * A_
        G2 = G_ + A_ * W * G_ * A_.T
        H2 = H_ + A_.T * H_ * W * A_
        d = mp.norm(H2 - H_, 1) / mp.norm(H2, 1)
        A_, G_, H_ = A2, G2, H2
        if d < tol:
            break
    else:
        raise RuntimeError("SDA (mp) did not converge")
    P = H_
    K = mp.inverse(R + Bd.T * P * Bd) * (Bd.T * P * Ad)
    return K, P, it + 1


def sda_np(Ad, Bd, Q, R, tol=1e-15, itmax=80):
    n = Ad.shape[0]
    I = np.eye(n)
    A_, G_, H_ = Ad.copy(), Bd @ np.linalg.solve(R, Bd.T), Q.copy()
    for it in range(itmax):
        W = np.linalg.inv(I + G_ @ H_)
        A2 = A_ @ W @ A_
        G2 = G_ + A_ @ W @ G_ @ A_.T
        H2 = H_ + A_.T @ H_ @ W @ A_
        d = np.max(np.abs(H2 - H_)) / np.max(np.abs(H2))
        A_, G_, H_ = A2, G2, H2
        if d < tol:
            break
    else:
        raise RuntimeError("SDA (np) did not converge")
    K = np.linalg.solve(R + Bd.T @ H_ @ Bd, Bd.T @ H_ @ Ad)
    return K, H_, it + 1


def to_np(m):
    return np.array([[float(m[i, j]) for j in range(m.cols)] for i in range(m.rows)])


Ad_mp, Bd_mp, Q0_mp, R0_mp, a_mp, b_mp, Meff_mp = design(mp.mpf)
Ad, Bd, Q0, R0 = to_np(Ad_mp), to_np(Bd_mp), to_np(Q0_mp), to_np(R0_mp)

# route (3): scipy
a_f = (rho * Cd * Af * v0 + Bm * G**2 / rw**2 * eg) / (M + Jm * G**2 / rw**2)
b_f = G * eg / (rw * (M + Jm * G**2 / rw**2))
A_f = np.array([[-a_f, b_f, 0.0], [0.0, -1.0 / tau, 0.0], [1.0, 0.0, 0.0]])
B_f = np.array([[0.0], [1.0 / tau], [0.0]])
blk = np.zeros((4, 4))
blk[:3, :3], blk[:3, 3:] = A_f * Ts, B_f * Ts
Eb = sl.expm(blk)
Ad_sp, Bd_sp = Eb[:3, :3], Eb[:3, 3:]


def dare_residual(Ad_, Bd_, Q, R, P):
    S = np.linalg.solve(R + Bd_.T @ P @ Bd_, Bd_.T @ P @ Ad_)
    return np.max(np.abs(Ad_.T @ P @ Ad_ - P - Ad_.T @ P @ Bd_ @ S + Q)) / np.max(np.abs(P))


cases = {}
spec = [("fixed", 1.0)] + [("scheduled", s) for s in (1.0, 0.9, 0.8, 0.7)]
for kind, soh in spec:
    Qm, Rm = weights(Q0_mp, R0_mp, soh, kind)
    Kmp, Pmp, itmp = sda_mp(Ad_mp, Bd_mp, Qm, Rm)
    K_exact = [float(Kmp[0, j]) for j in range(3)]  # nearest float64 to the 50-digit gain
    Q, R = to_np(Qm), to_np(Rm)
    Knp, Pnp, itnp = sda_np(Ad, Bd, Q, R)
    Psp = sl.solve_discrete_are(Ad_sp, Bd_sp, Q, R)
    Ksp = np.linalg.solve(R + Bd_sp.T @ Psp @ Bd_sp, Bd_sp.T @ Psp @ Ad_sp)[0]
    eig = np.linalg.eigvals(Ad - Bd @ np.array([K_exact]))
    key = f"{kind}_soh{soh:.2f}"
    rel = lambda x: float(np.max(np.abs((np.asarray(x).ravel() - np.array(K_exact)) / np.array(K_exact))))
    cases[key] = {
        "kind": kind, "soh": soh, "K": K_exact, "K_hex": [float.hex(x) for x in K_exact],
        "K_mp_50digits": [mp.nstr(Kmp[0, j], 40) for j in range(3)],
        "Q_diag": [float(Qm[i, i]) for i in range(3)], "R": float(Rm[0, 0]),
        "sda_mp_iterations": itmp, "sda_np_iterations": itnp,
        "rel_diff_sda_float64_vs_exact": rel(Knp), "rel_diff_scipy_vs_exact": rel(Ksp),
        "dare_residual_rel_float64_sda": dare_residual(Ad, Bd, Q, R, Pnp),
        "dare_residual_rel_scipy": dare_residual(Ad_sp, Bd_sp, Q, R, Psp),
        "closed_loop_max_abs_eig": float(np.max(np.abs(eig))),
    }

# comparison with what the Python experiment saved (read only now, after the frozen gains exist)
saved = {}
for prof in ("S1", "S2"):
    m = json.loads((root / f"artifacts/raw/primary/{prof}/manifest.json").read_text(encoding="utf-8"))
    for r in m["runs"]:
        saved[(prof, r["controller"], round(r["soh"], 2))] = r["gain"]
cmp = {}
for (prof, kind, soh), g in sorted(saved.items()):
    key = f"{kind}_soh{soh:.2f}" if kind == "scheduled" else "fixed_soh1.00"
    ex = np.array(cases[key]["K"])
    cmp[f"{prof}_{kind}_soh{soh:.2f}"] = {"saved": g, "frozen_key": key, "max_rel_diff": float(np.max(np.abs((np.array(g) - ex) / ex)))}

out = {
    "purpose": "frozen gains for the Modelica controller cross-check",
    "inputs": {"parameters_yaml_sha256": sha(root / "configs/parameters.yaml"),
               "values": {"M_eff": float(Meff_mp), "a": float(a_mp), "b": float(b_mp), "Ts": Ts, "v0": v0, "tau_T": tau,
                          "e_max": emax, "T_bryson": Tb, "z_max": zmax, "gamma_v": gv, "gamma_u": gu}},
    "design_model_Ad": Ad.tolist(), "design_model_Bd": Bd.ravel().tolist(),
    "zoh_scipy_vs_mp_max_abs_diff": float(max(np.max(np.abs(Ad_sp - Ad)), np.max(np.abs(Bd_sp.ravel() - Bd.ravel())))),
    "software": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__, "mpmath": mp.__version__, "mp_dps": mp.mp.dps},
    "gains": cases,
    "comparison_with_saved_python_gains": cmp,
}
(root / "verification/references/controller_gains.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
for k, c in cases.items():
    print(f"{k:22s} K={c['K']}  sda64/scipy rel {c['rel_diff_sda_float64_vs_exact']:.1e}/{c['rel_diff_scipy_vs_exact']:.1e}  |eig|max={c['closed_loop_max_abs_eig']:.6f}")
print("ZOH scipy vs mp:", out["zoh_scipy_vs_mp_max_abs_diff"])
for k, c in cmp.items():
    print(k, f"{c['max_rel_diff']:.2e}")
