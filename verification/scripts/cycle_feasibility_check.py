"""Indicative check: can the project's hypothetical vehicle (configs/parameters.yaml) follow the EPA schedules?

Uses constant efficiencies and the same force/torque limits as docs/model.md. Reads project files only.
Required traction force = M_eff * a + road loads, with a from np.gradient on the 1 Hz speed trace
(a crude acceleration estimate), compared with the available force G*eta_g*(T_lim - B_m*w)/r_w.
This is a feasibility screen on the reference trajectories, not a controller simulation.
"""
import sys

import numpy as np
import pandas as pd
import yaml

root = sys.argv[1]
cfg = yaml.safe_load(open(f"{root}/configs/parameters.yaml", encoding="utf-8"))
V = {f"{g}.{k}": s["value"] for g, it in cfg.items() if isinstance(it, dict) for k, s in it.items()}
M, Af, Cd, Crr, rw, rho, g = (V[k] for k in ("vehicle.mass", "vehicle.frontal_area", "vehicle.drag_coefficient", "vehicle.rolling_resistance", "vehicle.wheel_radius", "vehicle.air_density", "vehicle.gravity"))
G, eg, Jm, Bm, Tmax, Pmax, wmax = (V[k] for k in ("drivetrain.gear_ratio", "drivetrain.gear_efficiency", "drivetrain.motor_inertia", "drivetrain.motor_viscous_friction", "drivetrain.torque_max", "drivetrain.power_max", "drivetrain.speed_max"))
Meff = M + Jm * G**2 / rw**2
vmax = wmax * rw / G
Fmax_low = G * eg * Tmax / rw
print(f"M_eff={Meff:.1f} kg | motor-speed-limited vehicle speed = {vmax:.2f} m/s = {vmax*3.6:.1f} km/h = {vmax/0.44704:.1f} mph")
print(f"max traction force at low speed = {Fmax_low:.0f} N -> max accel before road loads = {Fmax_low/Meff:.2f} m/s^2")
for name in ("udds", "hwfet", "us06"):
    d = pd.read_csv(f"{root}/data/processed/drive_cycles/epa/epa_{name}_1hz.csv")
    v, t = d.speed_m_per_s.to_numpy(), d.time_s.to_numpy()
    a = np.gradient(v, t)
    F_req = Meff * a + Crr * M * g + 0.5 * rho * Cd * Af * v * v
    w = G * v / rw
    T_lim = np.minimum(Tmax, Pmax / np.maximum(w, 1e-6))
    F_av = G * eg * (T_lim - Bm * w) / rw
    short = F_req > F_av + 1e-9
    P_shaft = np.maximum(F_req, 0) * v / eg
    print(f"{name:6s} vmax={v.max():5.2f} m/s ({v.max()*3.6:5.1f} km/h) amax={a.max():.2f} m/s^2 | "
          f"samples with required force > available: {short.sum()} of {len(v)} ({100*short.mean():.1f} %) | "
          f"peak required shaft power ~{P_shaft.max()/1000:.1f} kW (limit {Pmax/1000:.0f} kW)")
print("project profiles for comparison: S1 vmax = 50 km/h (13.9 m/s), S2 vmax = 25 km/h")
