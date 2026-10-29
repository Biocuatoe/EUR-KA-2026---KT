"""Derivation checks for verification/modelica-plant-specification.md.

(1) SymPy: the coast-down closed form solves  v' = -(alpha + beta v + gamma v^2),  v(0) = v0.
(2) Pint: every equation term in the specification has the intended dimension, using the UNIT
    strings declared in configs/parameters.yaml. Includes negative controls that must fail.
Run with the project's locked .venv (sympy and pint are installed there). Imports nothing from eureka.
"""
import pathlib
import sys

import pint
import sympy as sp
import yaml

root = pathlib.Path(sys.argv[1])
lines = []


def say(s=""):
    lines.append(s)
    print(s)


# ---------------------------------------------------------------- (1) coast-down closed form
t = sp.symbols("t", real=True)
al, be, ga, v0 = sp.symbols("alpha beta gamma v0", positive=True)
s = sp.sqrt(4 * al * ga - be**2)
theta0 = sp.atan((2 * ga * v0 + be) / s)
v = (s * sp.tan(theta0 - s * t / 2) - be) / (2 * ga)
residual = sp.simplify(sp.diff(v, t) + (al + be * v + ga * v**2))
init = sp.simplify(v.subs(t, 0) - v0)
say("(1) coast-down closed form  v(t) = (s tan(atan((2 g v0 + b)/s) - s t/2) - b)/(2 g),  s = sqrt(4 a g - b^2)")
say(f"    symbolic residual  dv/dt + (alpha + beta v + gamma v^2)  simplifies to: {residual}")
say(f"    symbolic initial condition v(0) - v0 simplifies to: {init}")
assert residual == 0 and init == 0
vals = {al: 0.07606861132322461, be: 0.0006333983799738293, ga: 0.0005378044434747828, v0: 13.0}
r_num = (sp.diff(v, t) + (al + be * v + ga * v**2)).subs(vals).subs(t, 7.3).evalf(30)
say(f"    numeric residual at the project's coast-down coefficients, t = 7.3 s: {r_num}")
negative = sp.simplify(sp.diff(v, t) + (al + be * v + 1.01 * ga * v**2))
say("    negative control: residual with gamma changed by 1 % in the ODE only is non-zero: " + str(negative != 0))
assert negative != 0

# ---------------------------------------------------------------- (2) dimensional check
cfg = yaml.safe_load((root / "configs/parameters.yaml").read_text(encoding="utf-8"))
u = pint.UnitRegistry()
Q = {}
for grp, items in cfg.items():
    if isinstance(items, dict):
        for k, sp_ in items.items():
            Q[f"{grp}.{k}"] = u.Quantity(sp_["value"], sp_["unit"])
M, Af, Cd, Crr, rw = (Q[k] for k in ("vehicle.mass", "vehicle.frontal_area", "vehicle.drag_coefficient", "vehicle.rolling_resistance", "vehicle.wheel_radius"))
rho, g = Q["vehicle.air_density"], Q["vehicle.gravity"]
G, eg, Jm, Bm, emi = (Q[k] for k in ("drivetrain.gear_ratio", "drivetrain.gear_efficiency", "drivetrain.motor_inertia", "drivetrain.motor_viscous_friction", "drivetrain.motor_inverter_efficiency"))
Tmax, Pmax, tau = Q["drivetrain.torque_max"], Q["drivetrain.power_max"], Q["drivetrain.torque_time_constant"]
Voc, Qah, R0, R1, C1 = (Q[k] for k in ("battery.open_circuit_voltage", "battery.capacity", "battery.r0_new", "battery.r1_new", "battery.c1"))
veps = Q["simulation.speed_smoothing"]
vv = 8.0 * u.m / u.s
TT = 10.0 * u.N * u.m
Vtwo = 1.0 * u.V
Ii = 50.0 * u.A
sec_per_h = 3600 * u.s / u.hour


def has(expr, unit):
    try:
        expr.to(unit)
        return True
    except pint.DimensionalityError:
        return False


Meff = M + Jm * G**2 / rw**2
gr = G / rw
w = gr * vv                        # rad/s: radian is dimensionless in pint, so this is 1/s
ts = TT - Bm * w
checks = [
    ("M_eff = M + J_m G^2 / r_w^2  [kg]", Meff, "kg"),
    ("omega = G v / r_w  [1/s]", w, "1/s"),
    ("t_s = T - B_m omega  [N m]", ts, "N*m"),
    ("F_w = G t_s eta_g / r_w  [N]", G * ts * eg / rw, "N"),
    ("F_w (regeneration) = G t_s / (eta_g r_w)  [N]", G * ts / eg / rw, "N"),
    ("F_rr = C_rr M g  [N]", Crr * M * g, "N"),
    ("tanh argument v / v_eps  [1]", vv / veps, "dimensionless"),
    ("F_aero = 1/2 rho C_d A_f v^2  [N]", 0.5 * rho * Cd * Af * vv**2, "N"),
    ("F_fb = G max(0, -T_lim - T_ref) / r_w  [N]", G * TT / rw, "N"),
    ("T_lim = P_max / omega  [N m]", Pmax / w, "N*m"),
    ("dv/dt = F / M_eff  [m/s^2]", (G * ts * eg / rw) / Meff, "m/s^2"),
    ("dT/dt = (T_cmd - T) / tau_T  [N m / s]", TT / tau, "N*m/s"),
    ("P_m = T omega  [W]", TT * w, "W"),
    ("P_e = P_m / eta_mi  [W]", TT * w / emi, "W"),
    ("I = (V - sqrt(V^2 - 4 R0 P_e)) / (2 R0)  [A]; V^2 vs R0*P_e", (Vtwo**2 - 4 * R0 * (TT * w) ) , "V**2"),
    ("I -> V/R0  [A]", Vtwo / R0, "A"),
    ("dV1/dt = -V1/(R1 C1) + I/C1  [V/s]  (term 1)", Vtwo / (R1 * C1), "V/s"),
    ("dV1/dt  (term 2)", Ii / C1, "V/s"),
    ("dSoC/dt = -I / (3600 Q SoH)  [1/s]", Ii / (sec_per_h * Qah), "1/s"),
    ("dE_chem/dt = V_oc I  [W]", Voc * Ii, "W"),
    ("dE_rr/dt = F_rr v  [W]", Crr * M * g * vv, "W"),
    ("dE_gear/dt = t_s omega - F_w v  [W]", ts * w - G * ts * eg / rw * vv, "W"),
    ("dE_visc/dt = B_m omega^2  [W]", Bm * w**2, "W"),
    ("dE_R0/dt = R0 I^2  [W]", R0 * Ii**2, "W"),
    ("dE_R1/dt = V1^2 / R1  [W]", Vtwo**2 / R1, "W"),
    ("E_C1 = 1/2 C1 V1^2  [J]", 0.5 * C1 * Vtwo**2, "J"),
    ("E_kin = 1/2 M_eff v^2  [J]", 0.5 * Meff * vv**2, "J"),
    ("shaft friction reflected c = B_m G^2/(eta_g r_w^2)  [N s/m]", Bm * G**2 / (eg * rw**2), "N*s/m"),
]
say("")
say("(2) dimensional check of every specification term (units taken from configs/parameters.yaml)")
bad = 0
for label, expr, unit in checks:
    ok = has(expr, unit)
    bad += (not ok)
    say(f"    {'OK ' if ok else 'FAIL'}  {label}")
say("")
say("    negative controls (each must be detected as dimensionally wrong):")
neg = [
    ("F_w = G t_s eta_g * r_w   (wrong: multiply by wheel radius)", G * ts * eg * rw, "N"),
    ("F_aero with v instead of v^2", 0.5 * rho * Cd * Af * vv, "N"),
    ("P_m = T * v   (wheel speed in place of motor speed)", TT * vv, "W"),
    ("dv/dt = F / M  with F in W", (Pmax) / Meff, "m/s^2"),
]
neg_detected = 0
for label, expr, unit in neg:
    ok = has(expr, unit)
    neg_detected += (not ok)
    say(f"    {'detected' if not ok else 'NOT DETECTED'}  {label}")
say("")
say(f"    positive checks failed: {bad} of {len(checks)};  negative controls detected: {neg_detected} of {len(neg)}")
assert bad == 0 and neg_detected == len(neg)
out = root / "verification/references/spec_derivation_checks.txt"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("written:", out)
