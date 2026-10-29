"""Independent analytic checks (Part A). Read-only with respect to the project.

Parameter VALUES are read directly from configs/parameters.yaml with PyYAML (not through
eureka.params). Physics, linearisation, DARE and margins are re-implemented here with
different algorithms; eureka is imported only to compare against.
"""

import json
import math
import pathlib
import sys

import numpy as np
import pint
import sympy as sp
import yaml
from scipy.linalg import eig, expm

ROOT = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(sys.argv[2])
cfg = yaml.safe_load((ROOT / "configs" / "parameters.yaml").read_text(encoding="utf-8"))
V = {f"{g}.{k}": s["value"] for g, it in cfg.items() if isinstance(it, dict) for k, s in it.items()}

M, Af, Cd, Crr = V["vehicle.mass"], V["vehicle.frontal_area"], V["vehicle.drag_coefficient"], V["vehicle.rolling_resistance"]
rw, rho, g = V["vehicle.wheel_radius"], V["vehicle.air_density"], V["vehicle.gravity"]
G, eg, Jm, Bm = V["drivetrain.gear_ratio"], V["drivetrain.gear_efficiency"], V["drivetrain.motor_inertia"], V["drivetrain.motor_viscous_friction"]
emi, Tmax, Pmax, tau = V["drivetrain.motor_inverter_efficiency"], V["drivetrain.torque_max"], V["drivetrain.power_max"], V["drivetrain.torque_time_constant"]
Voc, R0n, R1n, C1 = V["battery.open_circuit_voltage"], V["battery.r0_new"], V["battery.r1_new"], V["battery.c1"]
kr0, kr1 = V["battery.k_r0"], V["battery.k_r1"]
Ts, v0 = V["controller.sample_time"], V["controller.linearisation_speed"]
emax, Tb, zmax = V["controller.bryson_velocity_error_max"], V["controller.bryson_torque_max"], V["controller.bryson_integral_error_max"]
veps = V["simulation.speed_smoothing"]

R = {}


def rec(key, **kw):
    R[key] = kw
    print(key, json.dumps(kw, default=float))


# ---------------- IC-01 operating points (hand formulas) ----------------
Meff = M + Jm * G**2 / rw**2
w_base = Pmax / Tmax
v_base = w_base * rw / G


def tlim(w):
    return min(Tmax, Pmax / max(w, 1e-9))


def loads(v):
    return Crr * M * g * math.tanh(v / veps) + 0.5 * rho * Cd * Af * v * abs(v)


def t_steady(v):
    w = G * v / rw
    return loads(v) * rw / (G * eg) + Bm * w


def f_trac_max(v):
    w = G * v / rw
    return G * eg * (tlim(w) - Bm * w) / rw


ops = {}
for kmh in (20, 30, 50):
    v = kmh / 3.6
    ops[kmh] = {"F_rr_N": Crr * M * g * math.tanh(v / veps), "F_aero_N": 0.5 * rho * Cd * Af * v * v,
                "T_steady_Nm": t_steady(v), "T_lim_Nm": tlim(G * v / rw), "P_road_W": loads(v) * v}
# cross-check against the project plant derivative at the hand-computed equilibrium
from eureka.params import load_params  # noqa: E402
from eureka.plant import IX, BatchParams, derivatives, initial_state  # noqa: E402

P = load_params()
bp = BatchParams.from_params([P], np.array([1.0]))
eq_resid = {}
for kmh in (20, 30, 50):
    v = kmh / 3.6
    y = initial_state(1)
    y[0, IX["v"]], y[0, IX["T"]] = v, t_steady(v)
    dy, _ = derivatives(y, np.array([t_steady(v)]), bp)
    eq_resid[kmh] = float(dy[0, IX["v"]])
rec("IC-01", M_eff=Meff, w_base=w_base, v_base_ms=v_base, v_base_kmh=v_base * 3.6,
    project_M_eff=P.M_eff, ops=ops, plant_dv_at_hand_equilibrium=eq_resid)


# ---------------- IC-02 actuator headroom along the S1/S2 REFERENCE ----------------
def build(segs):
    t, v = [0.0], [0.0]
    for s in segs:
        if "idle" in s or "cruise" in s:
            t.append(t[-1] + float(s.get("idle", s.get("cruise")))); v.append(v[-1])
        else:
            tgt = s["to_kmh"] / 3.6
            t.append(t[-1] + (tgt - v[-1]) / s["accel"]); v.append(tgt)
    return np.array(t), np.array(v)


prof_cfg = yaml.safe_load((ROOT / "configs" / "cycles" / "profiles.yaml").read_text(encoding="utf-8"))
PROF = {k: build(v["segments"]) for k, v in prof_cfg.items()}
head = {}
for name in ("S1", "S2"):
    kt, kv = PROF[name]
    worst_drive, worst_brake = 1e9, 1e9
    for i in range(len(kt) - 1):
        dt_ = kt[i + 1] - kt[i]
        a = (kv[i + 1] - kv[i]) / dt_ if dt_ > 0 else 0.0
        for v in np.linspace(kv[i], kv[i + 1], 200):
            F = Meff * a + loads(v)
            w = G * v / rw
            if F >= 0:
                T = F * rw / (G * eg) + Bm * w
                worst_drive = min(worst_drive, tlim(w) - T)
            elif v > 0.1:
                T = F * rw * eg / G + Bm * w
                worst_brake = min(worst_brake, tlim(w) + T)  # >0: regen alone suffices
    head[name] = {"min_drive_torque_headroom_Nm": worst_drive, "min_regen_torque_headroom_Nm": worst_brake,
                  "duration_s": float(kt[-1]),
                  "distance_m": float(np.sum(np.diff(kt) * (kv[1:] + kv[:-1]) / 2))}
rec("IC-02", **head)

# ---------------- IC-03 dimensional analysis (independent Pint expressions) ----------------
u = pint.UnitRegistry()
q = {"M": 850 * u.kg, "rw": 0.28 * u.m, "G": 6.5 * u.dimensionless, "eta": 0.97 * u.dimensionless,
     "T": 10 * u.N * u.m, "v": 8.0 * u.m / u.s, "w": 100 * u.rad / u.s, "i": 100 * u.A,
     "rho": 1.225 * u.kg / u.m**3, "Cd": 0.35 * u.dimensionless, "Af": 2.2 * u.m**2,
     "Bm": 0.001 * u.N * u.m * u.s / u.rad, "Jm": 0.05 * u.kg * u.m**2, "R": 0.005 * u.ohm,
     "P": 1000 * u.W, "Vo": 48 * u.V, "L": 0.008 * u.H, "Ke": 0.1 * u.V * u.s / u.rad,
     "Kt": 0.1 * u.N * u.m / u.A, "tau": 0.02 * u.s}
acc = u.m / u.s**2


def ok(expr, target):
    try:
        expr.to(target)
        return True
    except pint.DimensionalityError:
        return False


coefG = q["G"] * q["eta"] / (q["M"] * q["rw"])
dims = {
    "project F_w = G eta T / r_w [N]": ok(q["G"] * q["eta"] * q["T"] / q["rw"], u.N),
    "project F_aero [N]": ok(0.5 * q["rho"] * q["Cd"] * q["Af"] * q["v"] ** 2, u.N),
    "project B_m*w [N m]": ok(q["Bm"] * q["w"], u.N * u.m),
    "project a drag term [1/s]": ok(q["rho"] * q["Cd"] * q["Af"] * q["v"] / q["M"], 1 / u.s),
    "project a friction term [1/s]": ok(q["Bm"] * q["G"] ** 2 / q["rw"] ** 2 * q["eta"] / q["M"] / u.rad, 1 / u.s),
    "project b * T [m/s^2]": ok(coefG * q["T"], acc),
    "project battery current [A]": ok((q["Vo"] - ((q["Vo"] ** 2 - 4 * q["R"] * q["P"]) ** 0.5)) / (2 * q["R"]), u.A),
    "thesis Eq4.3 G*eta/(M r_w) * v": ok(coefG * q["v"], acc),
    "thesis Eq4.3 G*eta/(M r_w) * i_batt": ok(coefG * q["i"], acc),
    "thesis Eq4.3 G*eta/(M r_w) * omega_m": ok(coefG * q["w"], acc),
    "thesis Eq4.3 R/L * i [A/s]": ok(q["R"] / q["L"] * q["i"], u.A / u.s),
    "thesis Eq4.3 Ke/L * omega [A/s]": ok(q["Ke"] / q["L"] * q["w"], u.A / u.s),
    "thesis Eq4.3 Kt/Jm * i [rad/s^2]": ok(q["Kt"] / q["Jm"] * q["i"], u.rad / u.s**2),
    "thesis Eq4.3 Bm/Jm * omega [rad/s^2]": ok(q["Bm"] / q["Jm"] * q["w"], u.rad / u.s**2),
    "thesis Eq4.13 x_i += (v_ref - v) has units of [m]": ok(q["v"], u.m),
    "NEGATIVE CONTROL: F_aero declared as [W] must fail": ok(0.5 * q["rho"] * q["Cd"] * q["Af"] * q["v"] ** 2, u.W),
}
rec("IC-03", **dims)

# ---------------- IC-04 symbolic linearisation (SymPy) ----------------
vs, Ts_, = sp.symbols("v T", real=True)
Gs, es, rws, Bms, Ms, Mes, Crs, gs, rhos, Cds, Afs, ves = sp.symbols(
    "G eta r_w B_m M M_eff C_rr g rho C_d A_f v_eps", positive=True)
w_s = Gs * vs / rws
drive = (Gs * es * (Ts_ - Bms * w_s) / rws - Crs * Ms * gs * sp.tanh(vs / ves) - sp.Rational(1, 2) * rhos * Cds * Afs * vs**2) / Mes
regen = (Gs / es * (Ts_ - Bms * w_s) / rws - Crs * Ms * gs * sp.tanh(vs / ves) - sp.Rational(1, 2) * rhos * Cds * Afs * vs**2) / Mes
subs = {Gs: G, es: eg, rws: rw, Bms: Bm, Ms: M, Mes: Meff, Crs: Crr, gs: g, rhos: rho, Cds: Cd, Afs: Af, ves: veps, vs: v0}
lin = {}
for nm, f in (("motoring", drive), ("regen", regen)):
    dfdv = sp.diff(f, vs)
    dfdT = sp.diff(f, Ts_)
    tanh_part = sp.diff(-Crs * Ms * gs * sp.tanh(vs / ves) / Mes, vs)
    lin[nm] = {"dfdv_at_v0": float(dfdv.subs(subs)), "dfdT": float(dfdT.subs(subs)),
               "rr_tanh_contribution_at_v0": float(tanh_part.subs(subs)),
               "rr_tanh_contribution_at_0.05ms": float(tanh_part.subs({**subs, vs: 0.05}))}
from eureka.controllers import design_model, gain, zoh  # noqa: E402

A_p, B_p = design_model(P)
rec("IC-04", sympy=lin, project_A00=float(A_p[0, 0]), project_A01=float(A_p[0, 1]),
    rel_err_a=abs(lin["motoring"]["dfdv_at_v0"] - A_p[0, 0]) / abs(A_p[0, 0]),
    rel_err_b=abs(lin["motoring"]["dfdT"] - A_p[0, 1]) / abs(A_p[0, 1]),
    regen_to_motoring_b_ratio=lin["regen"]["dfdT"] / lin["motoring"]["dfdT"])

# ---------------- IC-05 controllability (closed form + PBH) ----------------
a_s, b_s, t_s = sp.symbols("a b tau", positive=True)
Asym = sp.Matrix([[-a_s, b_s, 0], [0, -1 / t_s, 0], [1, 0, 0]])
Bsym = sp.Matrix([0, 1 / t_s, 0])
Csym = sp.Matrix.hstack(Bsym, Asym * Bsym, Asym**2 * Bsym)
det = sp.simplify(Csym.det())


def model(a, b):
    A = np.array([[-a, b, 0.0], [0.0, -1 / tau, 0.0], [1.0, 0.0, 0.0]])
    B = np.array([[0.0], [1 / tau], [0.0]])
    return A, B


def c2d(A, B, h):  # Van Loan block exponential, written independently
    n = A.shape[0]
    Mx = np.zeros((n + 1, n + 1)); Mx[:n, :n] = A; Mx[:n, n:] = B
    E = expm(Mx * h)
    return E[:n, :n], E[:n, n:]


a0 = -lin["motoring"]["dfdv_at_v0"]
b0 = lin["motoring"]["dfdT"]
Ad, Bd = c2d(*model(a0, b0), Ts)
pbh = [int(np.linalg.matrix_rank(np.hstack([lam * np.eye(3) - Ad, Bd]))) for lam in np.linalg.eigvals(Ad)]
ctrb = np.hstack([Bd, Ad @ Bd, Ad @ Ad @ Bd])
rec("IC-05", symbolic_det=str(det), PBH_ranks=pbh, ctrb_cond=float(np.linalg.cond(ctrb)),
    continuous_eigs=[-a0, -1 / tau, 0.0], zoh_matches_project=bool(np.allclose(Ad, zoh(A_p, B_p, Ts)[0], rtol=1e-10)))


# ---------------- IC-06 DARE by the symplectic-pencil method ----------------
def dare_pencil(A, B, Q, Rm):
    n = A.shape[0]
    Gm = B @ np.linalg.solve(Rm, B.T)
    L = np.block([[A, np.zeros((n, n))], [-Q, np.eye(n)]])
    Mm = np.block([[np.eye(n), Gm], [np.zeros((n, n)), A.T]])
    w, Vv = eig(L, Mm)
    idx = np.where(np.abs(w) < 1)[0]
    assert len(idx) == n, w
    X1, X2 = Vv[:n, idx], Vv[n:, idx]
    Pm = np.real(X2 @ np.linalg.inv(X1))
    Pm = (Pm + Pm.T) / 2
    K = np.linalg.solve(Rm + B.T @ Pm @ B, B.T @ Pm @ A)
    resid = A.T @ Pm @ A - Pm - A.T @ Pm @ B @ np.linalg.solve(Rm + B.T @ Pm @ B, B.T @ Pm @ A) + Q
    return K, Pm, float(np.max(np.abs(resid)) / np.max(np.abs(Pm)))


Q0 = np.diag([1 / emax**2, 1 / Tb**2, 1 / zmax**2])
Rr0 = np.array([[1 / Tb**2]])


def sched_QR(soh, gv=1.0, gu=1.0):
    al = 1 / (1 + gv * (1 - soh))
    return Q0 @ np.diag([1, al, 1]), Rr0 * (1 + gu * (1 - soh))


gains = {}
for soh in (1.0, 0.9, 0.8, 0.7):
    Qs, Rs = sched_QR(soh)
    K, Pm, res = dare_pencil(Ad, Bd, Qs, Rs)
    Kp = gain(P, "scheduled", soh=soh)
    gains[soh] = {"K_pencil": K.ravel().tolist(), "K_project": Kp.ravel().tolist(),
                  "max_rel_diff": float(np.max(np.abs(K - Kp) / np.abs(Kp))), "riccati_rel_residual": res,
                  "P_min_eig": float(np.min(np.linalg.eigvalsh(Pm)))}
rec("IC-06", **{str(k): v for k, v in gains.items()})

# ---------------- IC-07 frozen-speed / both-branch stability and margins ----------------
K_fixed = np.array(gains[1.0]["K_pencil"]).reshape(1, 3)
cands = {"fixed": K_fixed}
for soh in (0.9, 0.8, 0.7):
    cands[f"sched_{soh}"] = np.array(gains[soh]["K_pencil"]).reshape(1, 3)
for c in (0.1, 10.0):
    cands[f"fixed_r{c}"] = dare_pencil(Ad, Bd, Q0, Rr0 * c)[0]


def a_b(v, branch):
    e = eg if branch == "motoring" else 1 / eg
    a = (rho * Cd * Af * abs(v) + Crr * M * g / veps / math.cosh(v / veps) ** 2 + Bm * G**2 * e / rw**2) / Meff
    return a, G * e / (rw * Meff)


vgrid = [0.0, 0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 4, 6, 8.333, 10, 12, 13.89, 16]
sweep = {}
for nm, K in cands.items():
    worst = 0.0
    for v in vgrid:
        for br in ("motoring", "regen"):
            Ai, Bi = c2d(*model(*a_b(v, br)), Ts)
            worst = max(worst, float(np.max(np.abs(np.linalg.eigvals(Ai - Bi @ K)))))
    sweep[nm] = worst


def margins(K, A, B):
    ws = np.logspace(-4, np.log10(math.pi / Ts), 20000)
    Lw = np.array([(K @ np.linalg.solve(np.exp(1j * w * Ts) * np.eye(3) - A, B))[0, 0] for w in ws])
    rd = float(np.min(np.abs(1 + Lw)))
    ph = np.unwrap(np.angle(Lw))
    mag = np.abs(Lw)
    i_c = np.where(np.diff(np.sign(mag - 1)))[0]
    pm = [float((np.degrees(np.angle(Lw[i])) + 360) % 360 - 180) for i in i_c]  # 180 + angle, wrapped
    return rd, pm


def gain_margin_bisect(K, A, B):
    rho_ = lambda k: np.max(np.abs(np.linalg.eigvals(A - B @ (k * K))))
    lo, hi = 1.0, 1.0
    while rho_(hi) < 1 and hi < 1e4:
        hi *= 2
    up = None
    if hi < 1e4:
        l, h = hi / 2, hi
        for _ in range(60):
            m = (l + h) / 2
            l, h = (m, h) if rho_(m) < 1 else (l, m)
        up = l
    l, h = 0.0, 1.0
    for _ in range(60):
        m = (l + h) / 2
        l, h = (l, m) if rho_(m) < 1 else (m, h)
    return up, h, rho_


marg = {}
for nm in ("fixed", "sched_0.7", "fixed_r0.1"):
    K = cands[nm]
    rd, pm = margins(K, Ad, Bd)
    up, low, rho_ = gain_margin_bisect(K, Ad, Bd)
    marg[nm] = {"min_return_difference": rd,
                "guaranteed_gain_interval": [1 / (1 + rd), (1 / (1 - rd)) if rd < 1 else None],
                "guaranteed_phase_margin_deg": float(np.degrees(2 * np.arcsin(min(rd, 2) / 2))),
                "phase_margins_at_crossover_deg": pm,
                "upper_gain_margin_bisection": up, "lower_gain_limit_bisection": low,
                "spectral_radius_nominal": float(rho_(1.0)),
                "NEGATIVE_CONTROL_rho_at_1.05x_upper_GM": float(rho_(1.05 * up)) if up else None}
rec("IC-07", worst_spectral_radius_over_speed_and_branch=sweep, margins=marg)


# ---------------- IC-08 discrete slow-variation bound for the scheduled gain ----------------
def PK(soh):
    Qs, Rs = sched_QR(soh)
    K, Pm, _ = dare_pencil(Ad, Bd, Qs, Rs)
    return Qs, Rs, K, Pm


sgrid = np.linspace(0.5, 1.0, 51)
worst_allow, lyap_resid = 1e9, 0.0
for s in sgrid:
    Qs, Rs, K, Pm = PK(s)
    Acl = Ad - Bd @ K
    Mm = Qs + K.T @ Rs @ K
    lyap_resid = max(lyap_resid, float(np.max(np.abs(Acl.T @ Pm @ Acl - Pm + Mm)) / np.max(np.abs(Pm))))
    h = 1e-5
    dP = (PK(min(s + h, 1.0))[3] - PK(max(s - h, 0.5))[3]) / (min(s + h, 1.0) - max(s - h, 0.5))
    allow = np.min(np.linalg.eigvalsh(Mm)) / (np.linalg.norm(dP, 2) * np.linalg.norm(Acl, 2) ** 2)
    worst_allow = min(worst_allow, float(allow))
fast_drift = 0.2 / (365 * 86400 / Ts)  # 20 % SoH loss in one year, per 10 ms step
dK = np.abs(np.array(gains[0.7]["K_pencil"]) - np.array(gains[1.0]["K_pencil"]))
rec("IC-08", lyapunov_form_of_DARE_rel_residual=lyap_resid,
    max_allowed_abs_dSoH_per_step=worst_allow, fast_realistic_drift_per_step=fast_drift,
    safety_factor=worst_allow / fast_drift,
    allowed_jump_in_one_step_pct=100 * worst_allow,
    K_change_soh1_to_0p7=dK.tolist())

# ---------------- IC-09 thesis arithmetic ----------------
rec("IC-09", eta_dt_product_inv_motor_gear_bearing=0.95 * 0.92 * 0.98 * 0.99, eta_dt_table8=0.88,
    eta_gear_bearing=0.98 * 0.99, r_from_13in_diameter_m=13 * 0.0254 / 2, r_table=0.28,
    nyquist_Ts_for_10Hz_bandwidth_ms=1000 * math.pi / (2 * math.pi * 10),
    thesis_nyquist_ms=1000 * math.pi / 100,
    bryson_R1_implies_umax_Nm=1.0, ZOH_poles_tau_over_Ts=tau / Ts)

OUT.write_text(json.dumps(R, indent=2, default=float), encoding="utf-8")
