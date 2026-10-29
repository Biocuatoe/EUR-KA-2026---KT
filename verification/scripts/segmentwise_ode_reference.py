"""Adjudicating third calculation of the ideal-tracking energy (specification section 7).

Integrates the SAME inverse-model equations as the Modelica InverseTracking model and the fixed-step reference,
but with SciPy DOP853 at rtol 1e-13 and a restart exactly at every profile knot, so no knot is ever straddled.
It is neither the fixed-step scheme of the saved reference nor DASSL. Used only to say on which side an unexplained
gap between those two lies. Run with the project's locked .venv (SciPy is installed there); imports nothing from eureka.
Writes verification/references/ideal_reference_segmentwise_dop853.json
"""
import json
import math
import pathlib
import sys

import numpy as np
import yaml
from scipy.integrate import solve_ivp

root = pathlib.Path(sys.argv[1])
cfg = yaml.safe_load((root / "configs/parameters.yaml").read_text(encoding="utf-8"))
V = {f"{g}.{k}": s["value"] for g, it in cfg.items() if isinstance(it, dict) for k, s in it.items()}
M, Af, Cd, Crr = V["vehicle.mass"], V["vehicle.frontal_area"], V["vehicle.drag_coefficient"], V["vehicle.rolling_resistance"]
rw, rho, g = V["vehicle.wheel_radius"], V["vehicle.air_density"], V["vehicle.gravity"]
G, eg, Jm, Bm, emi = V["drivetrain.gear_ratio"], V["drivetrain.gear_efficiency"], V["drivetrain.motor_inertia"], V["drivetrain.motor_viscous_friction"], V["drivetrain.motor_inverter_efficiency"]
Voc, R0n, R1n, C1 = V["battery.open_circuit_voltage"], V["battery.r0_new"], V["battery.r1_new"], V["battery.c1"]
kr0, kr1, veps = V["battery.k_r0"], V["battery.k_r1"], V["simulation.speed_smoothing"]
Meff = M + Jm * G**2 / rw**2
gr = G / rw
prof_cfg = yaml.safe_load((root / "configs/cycles/profiles.yaml").read_text(encoding="utf-8"))


def knots(segs):
    t, v = [0.0], [0.0]
    for s in segs:
        if "idle" in s or "cruise" in s:
            t.append(t[-1] + float(s.get("idle", s.get("cruise"))))
            v.append(v[-1])
        else:
            tgt = s["to_kmh"] / 3.6
            t.append(t[-1] + (tgt - v[-1]) / s["accel"])
            v.append(tgt)
    return t, v


def run(name, soh):
    tk, vk = knots(prof_cfg[name]["segments"])
    r0, r1 = R0n * (1 + kr0 * (1 - soh)), R1n * (1 + kr1 * (1 - soh))
    y = np.array([0.0, 0.0, 0.0])  # V1, E_chem, dist

    for i in range(len(tk) - 1):
        a = (vk[i + 1] - vk[i]) / (tk[i + 1] - tk[i])
        t0, v0 = tk[i], vk[i]

        def rhs(t, y, a=a, t0=t0, v0=v0):
            v = v0 + a * (t - t0)
            w = gr * v
            F = Meff * a + Crr * M * g * math.tanh(v / veps) + 0.5 * rho * Cd * Af * v * abs(v)
            ts = F / (gr * eg) if F >= 0 else F * eg / gr
            T = ts + Bm * w
            pm = T * w
            pe = pm / emi if pm >= 0 else pm * emi
            vo = Voc - y[0]
            i_ = (vo - math.sqrt(vo * vo - 4 * r0 * pe)) / (2 * r0)
            return [-y[0] / (r1 * C1) + i_ / C1, Voc * i_, v]

        sol = solve_ivp(rhs, (tk[i], tk[i + 1]), y, method="DOP853", rtol=1e-13, atol=[1e-12, 1e-7, 1e-10], max_step=0.01)  # max_step: the rolling-resistance knee at standstill is only ~0.07 s wide; a free step skips it (found in this audit)
        assert sol.success
        y = sol.y[:, -1]
    return {"E_Wh_per_km": float(y[1] / 3600 / (y[2] / 1000)), "E_J": float(y[1]), "dist_m": float(y[2])}


out = {f"{n}_soh{s}": run(n, s) for n, s in (("S1", 1.0), ("S1", 0.8), ("S2", 1.0), ("S2", 0.8))}
for k, v in out.items():
    print(k, v)
(root / "verification/references/ideal_reference_segmentwise_dop853.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
