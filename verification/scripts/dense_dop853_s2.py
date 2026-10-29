"""Diagnostic: dense DOP853 trajectory (V1, E_chem, dist) of ideal tracking for S2 / SoH 1.0 on a 0.02 s grid, to localise
where the Modelica E_chem departs from the segment-wise DOP853 reference. Same equations as segmentwise_ode_reference.py."""
import math, pathlib, sys
import numpy as np, yaml
from scipy.integrate import solve_ivp
root = pathlib.Path(sys.argv[1]); prof = sys.argv[2]; soh = float(sys.argv[3])
cfg = yaml.safe_load((root / "configs/parameters.yaml").read_text(encoding="utf-8"))
V = {f"{g}.{k}": s["value"] for g, it in cfg.items() if isinstance(it, dict) for k, s in it.items()}
M, Af, Cd, Crr, rw, rho, g = (V[k] for k in ("vehicle.mass","vehicle.frontal_area","vehicle.drag_coefficient","vehicle.rolling_resistance","vehicle.wheel_radius","vehicle.air_density","vehicle.gravity"))
G, eg, Jm, Bm, emi = (V[k] for k in ("drivetrain.gear_ratio","drivetrain.gear_efficiency","drivetrain.motor_inertia","drivetrain.motor_viscous_friction","drivetrain.motor_inverter_efficiency"))
Voc, R0n, R1n, C1 = (V[k] for k in ("battery.open_circuit_voltage","battery.r0_new","battery.r1_new","battery.c1"))
kr0, kr1, veps = V["battery.k_r0"], V["battery.k_r1"], V["simulation.speed_smoothing"]
Meff = M + Jm*G**2/rw**2; gr = G/rw
segs = yaml.safe_load((root / "configs/cycles/profiles.yaml").read_text(encoding="utf-8"))[prof]["segments"]
tk, vk = [0.0], [0.0]
for s in segs:
    if "idle" in s or "cruise" in s: tk.append(tk[-1] + float(s.get("idle", s.get("cruise")))); vk.append(vk[-1])
    else: tgt = s["to_kmh"]/3.6; tk.append(tk[-1] + (tgt - vk[-1])/s["accel"]); vk.append(tgt)
r0, r1 = R0n*(1+kr0*(1-soh)), R1n*(1+kr1*(1-soh))
y = np.array([0.0, 0.0, 0.0]); rows = []
import pandas as _pd
grid = np.unique(_pd.read_csv(sys.argv[4])["time"].to_numpy())   # evaluate at exactly the Modelica output times
for i in range(len(tk)-1):
    a = (vk[i+1]-vk[i])/(tk[i+1]-tk[i]); t0, v0 = tk[i], vk[i]
    def rhs(t, y):
        v = v0 + a*(t-t0); w = gr*v
        F = Meff*a + Crr*M*g*math.tanh(v/veps) + 0.5*rho*Cd*Af*v*abs(v)
        ts = F/(gr*eg) if F >= 0 else F*eg/gr; T = ts + Bm*w; pm = T*w; pe = pm/emi if pm >= 0 else pm*emi
        vo = Voc - y[0]; i_ = (vo - math.sqrt(vo*vo - 4*r0*pe))/(2*r0)
        return [-y[0]/(r1*C1) + i_/C1, Voc*i_, v]
    te = grid[(grid >= tk[i]) & (grid < tk[i+1])]
    sol = solve_ivp(rhs, (tk[i], tk[i+1]), y, method="DOP853", rtol=1e-13, atol=[1e-12,1e-7,1e-10], t_eval=te)
    for tt, yy in zip(sol.t, sol.y.T): rows.append((tt, yy[0], yy[1], yy[2]))
    y = solve_ivp(rhs, (tk[i], tk[i+1]), y, method="DOP853", rtol=1e-13, atol=[1e-12,1e-7,1e-10]).y[:, -1]
rows.append((tk[-1], y[0], y[1], y[2]))
out = root / f"verification/modelica-build/dop853_{prof}_soh{soh}_dense.csv"
np.savetxt(out, np.array(rows), delimiter=",", header="time,V1,E_chem,dist", comments="", fmt="%.17g")
print("rows", len(rows), "->", out)
