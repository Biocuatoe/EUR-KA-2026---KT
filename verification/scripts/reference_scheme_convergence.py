"""Convergence study of the ideal-tracking REFERENCE scheme (not of the Modelica model).

`inverse_energy` below is a faithful copy of the algorithm in audit/technical-verification/ind_checks_b.py
(IC-11): midpoint sampling of the piecewise-linear speed on a fixed step h, required force from the force
balance, exact exponential update of the RC voltage for piecewise-constant current. It is copied, not imported,
so the preserved script stays untouched. At h = 1e-3 it must reproduce the saved reference values; at smaller h it
shows how far those values are from the converged answer of the same equations.
Plain math + PyYAML + numpy (searchsorted only). Writes verification/references/ideal_reference_convergence.json
"""
import json
import math
import pathlib
import sys
import time

import numpy as np
import yaml

root = pathlib.Path(sys.argv[1])
cfg = yaml.safe_load((root / "configs/parameters.yaml").read_text(encoding="utf-8"))
V = {f"{g}.{k}": s["value"] for g, it in cfg.items() if isinstance(it, dict) for k, s in it.items()}
M, Af, Cd, Crr = V["vehicle.mass"], V["vehicle.frontal_area"], V["vehicle.drag_coefficient"], V["vehicle.rolling_resistance"]
rw, rho, g = V["vehicle.wheel_radius"], V["vehicle.air_density"], V["vehicle.gravity"]
G, eg, Jm, Bm, emi = V["drivetrain.gear_ratio"], V["drivetrain.gear_efficiency"], V["drivetrain.motor_inertia"], V["drivetrain.motor_viscous_friction"], V["drivetrain.motor_inverter_efficiency"]
Voc, R0n, R1n, C1 = V["battery.open_circuit_voltage"], V["battery.r0_new"], V["battery.r1_new"], V["battery.c1"]
kr0, kr1, veps = V["battery.k_r0"], V["battery.k_r1"], V["simulation.speed_smoothing"]
Meff = M + Jm * G**2 / rw**2
prof_cfg = yaml.safe_load((root / "configs/cycles/profiles.yaml").read_text(encoding="utf-8"))


def build(segs):
    t, v = [0.0], [0.0]
    for s in segs:
        if "idle" in s or "cruise" in s:
            t.append(t[-1] + float(s.get("idle", s.get("cruise"))))
            v.append(v[-1])
        else:
            tgt = s["to_kmh"] / 3.6
            t.append(t[-1] + (tgt - v[-1]) / s["accel"])
            v.append(tgt)
    return np.array(t), np.array(v)


def inverse_energy(name, soh, h):
    kt, kv = build(prof_cfg[name]["segments"])
    r0, r1 = R0n * (1 + kr0 * (1 - soh)), R1n * (1 + kr1 * (1 - soh))
    tc = math.exp(-h / (r1 * C1))
    V1 = E = dist = 0.0
    n = int(round(kt[-1] / h))
    seg = np.searchsorted(kt, (np.arange(n) + 0.5) * h, side="right") - 1
    acc_seg = np.diff(kv) / np.diff(kt)
    for k in range(n):
        t = (k + 0.5) * h
        s = seg[k]
        a = acc_seg[s]
        v = kv[s] + a * (t - kt[s])
        F = Meff * a + Crr * M * g * math.tanh(v / veps) + 0.5 * rho * Cd * Af * v * v
        if v <= 1e-9 and F <= 0:
            F = 0.0
        w = G * v / rw
        ts = F * rw / (G * eg) if F >= 0 else F * rw * eg / G
        T = ts + Bm * w
        pm = T * w
        pe = pm / emi if pm >= 0 else pm * emi
        vo = Voc - V1
        i = (vo - math.sqrt(vo * vo - 4 * r0 * pe)) / (2 * r0)
        E += Voc * i * h
        dist += v * h
        V1 = V1 * tc + r1 * (1 - tc) * i
    return {"E_Wh_per_km": E / 3600 / (dist / 1000), "E_J": E, "dist_m": dist}


plan = [("S1", 1.0, [1e-3, 5e-4, 2.5e-4, 1e-4]), ("S1", 0.8, [1e-3, 2.5e-4, 1e-4]), ("S2", 1.0, [1e-3, 2.5e-4, 1e-4]), ("S2", 0.8, [1e-3, 2.5e-4, 1e-4])]
out = {}
for name, soh, hs in plan:
    res = {}
    for h in hs:
        t0 = time.time()
        r = inverse_energy(name, soh, h)
        r["seconds"] = round(time.time() - t0, 1)
        res[f"h={h:g}"] = r
        print(name, soh, f"h={h:g}", r["E_Wh_per_km"], r["seconds"], "s", flush=True)
    out[f"{name}_soh{soh}"] = res
(root / "verification/references/ideal_reference_convergence.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print("written")
