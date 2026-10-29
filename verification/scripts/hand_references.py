"""Hand-calculated analytic references for the Modelica plant checks.

Plain `math` only. Reads parameter VALUES from configs/parameters.yaml and speed profiles from
configs/cycles/profiles.yaml. Does not import eureka, numpy-based plant code or any Modelica output.
Writes verification/references/hand_references.json.

Every quantity is derived from the equations in verification/modelica-plant-specification.md.
"""
import json
import math
import pathlib
import sys

import yaml

root = pathlib.Path(sys.argv[1])
cfg = yaml.safe_load((root / "configs/parameters.yaml").read_text(encoding="utf-8"))
V = {f"{g}.{k}": s["value"] for g, it in cfg.items() if isinstance(it, dict) for k, s in it.items()}
M, Af, Cd, Crr = V["vehicle.mass"], V["vehicle.frontal_area"], V["vehicle.drag_coefficient"], V["vehicle.rolling_resistance"]
rw, rho, g = V["vehicle.wheel_radius"], V["vehicle.air_density"], V["vehicle.gravity"]
G, eg, Jm, Bm, emi = V["drivetrain.gear_ratio"], V["drivetrain.gear_efficiency"], V["drivetrain.motor_inertia"], V["drivetrain.motor_viscous_friction"], V["drivetrain.motor_inverter_efficiency"]
Tmax, Pmax, tau = V["drivetrain.torque_max"], V["drivetrain.power_max"], V["drivetrain.torque_time_constant"]
Voc, R0n, R1n, C1 = V["battery.open_circuit_voltage"], V["battery.r0_new"], V["battery.r1_new"], V["battery.c1"]
kr0, kr1, veps = V["battery.k_r0"], V["battery.k_r1"], V["simulation.speed_smoothing"]

Meff = M + Jm * G**2 / rw**2          # [kg]
gr = G / rw                            # [rad/m]
k_aero = 0.5 * rho * Cd * Af           # [kg/m]
F_rr0 = Crr * M * g                    # [N] rolling resistance for tanh = 1
out = {"parameters_from": "configs/parameters.yaml", "M_eff_kg": Meff, "gr_rad_per_m": gr, "k_aero_kg_per_m": k_aero, "F_rr0_N": F_rr0,
       "w_base_rad_s": Pmax / Tmax, "v_base_m_s": Pmax / Tmax / gr}


def road_loads(v):
    return F_rr0 * math.tanh(v / veps) + k_aero * v * abs(v)


# --- B. equilibrium torque: F_w = F_rr + F_aero, motoring branch F_w = gr*eta_g*(T - B_m*w), w = gr*v
eq = {}
for kmh in (20, 30, 50):
    v = kmh / 3.6
    w = gr * v
    F = road_loads(v)
    T = F / (gr * eg) + Bm * w
    pm = T * w
    pe = pm / emi
    vo = Voc
    i = (vo - math.sqrt(vo * vo - 4 * R0n * pe)) / (2 * R0n)   # V1 = 0, SoH = 1
    eq[f"{kmh}kmh"] = {"v_m_s": v, "omega_rad_s": w, "F_rr_N": F_rr0 * math.tanh(v / veps), "F_aero_N": k_aero * v * v, "F_total_N": F,
                       "T_eq_Nm": T, "P_mech_W": pm, "P_elec_W": pe, "I_A_at_V1_0_SoH_1": i,
                       "T_lim_Nm": min(Tmax, Pmax / w)}
out["equilibrium"] = eq

# --- B2. non-equilibrium instantaneous acceleration with delivered torque T held as a STATE value
pts = {}
for name, v, T in (("motoring_v10_T10", 10.0, 10.0), ("motoring_v3_T60", 3.0, 60.0), ("regen_v10_Tm20", 10.0, -20.0), ("regen_v20_Tm40", 20.0, -40.0)):
    w = gr * v
    ts = T - Bm * w
    fw = gr * ts * eg if ts >= 0 else gr * ts / eg
    frr, fa = F_rr0 * math.tanh(v / veps), k_aero * v * v
    # friction brake (spec equation 9) with the torque request held equal to T: active only when T_ref < -T_lim.
    # (The first version of this script omitted this term; it was found when the Modelica run disagreed at
    # v = 20 m/s, T = -40 N m where -40 is beyond -T_lim = -38.77. See independent-model-report.md.)
    tlim = min(Tmax, Pmax / w)
    ffb = gr * max(0.0, -tlim - T) * math.tanh(v / veps)
    net = fw - frr - fa - ffb
    pm = T * w
    pe = pm / emi if pm >= 0 else pm * emi
    i = (Voc - math.sqrt(Voc * Voc - 4 * R0n * pe)) / (2 * R0n)
    pts[name] = {"v": v, "T": T, "omega": w, "t_s": ts, "F_w": fw, "F_rr": frr, "F_aero": fa, "F_fb": ffb, "T_lim": tlim, "net_force_N": net, "accel_m_s2": net / Meff,
                 "P_mech_W": pm, "P_elec_W": pe, "I_A": i, "dE_chem_dt_W": Voc * i}
out["instantaneous_points"] = pts

# --- actuator limit corner
for v in (2.0, 13.0):
    w = gr * v
    out[f"T_lim_at_v{v:g}_Nm"] = min(Tmax, Pmax / w)
out["dT_dt_at_v13_T0_Tref1000_Nm_s"] = min(Tmax, Pmax / (gr * 13.0)) / tau

# --- C. project coast-down (T_ref = 0, T = 0): t_s = -B_m*w < 0 -> regeneration branch: F_w = gr*t_s/eta_g
c = Bm * G**2 / (eg * rw**2)           # [N s / m] shaft friction reflected through the gearbox
al, be, ga = F_rr0 / Meff, c / Meff, k_aero / Meff
s = math.sqrt(4 * al * ga - be**2)
out["coastdown"] = {"c_reflected_N_s_per_m": c, "alpha": al, "beta": be, "gamma": ga, "s": s, "v0": 13.0, "t_end": 20.0,
                    "v_end_closed_form": (s * math.tan(math.atan((2 * ga * 13.0 + be) / s) - s * 20.0 / 2) - be) / (2 * ga),
                    "note": "valid while tanh(v/v_eps) = 1, i.e. v above about 1 m/s; v(20) is well above that"}

# --- profiles: exact segment arithmetic
prof = yaml.safe_load((root / "configs/cycles/profiles.yaml").read_text(encoding="utf-8"))


def profile_exact(segs):
    t = dist = e_aero = 0.0
    v = 0.0
    start_stop_corr = 0.0
    for sg in segs:
        if "idle" in sg or "cruise" in sg:
            d = float(sg.get("idle", sg.get("cruise")))
            dist += v * d
            e_aero += k_aero * v**3 * d
            t += d
        else:
            a, tgt = float(sg["accel"]), sg["to_kmh"] / 3.6
            d = (tgt - v) / a
            dist += (v + tgt) / 2 * d
            e_aero += k_aero * (tgt**4 - v**4) / (4 * a)       # integral of k v^3 dt for v linear in t
            if v == 0.0:
                start_stop_corr += (veps**2 * math.pi**2 / 24) / abs(a)   # leaving rest: integral v (1 - tanh(v/eps)) dt = eps^2 pi^2/(24 a)
            if tgt == 0.0:
                start_stop_corr += (veps**2 * math.pi**2 / 24) / abs(a)   # arriving at rest: same by symmetry
            t += d
            v = tgt
    e_rr = F_rr0 * dist - F_rr0 * start_stop_corr
    return {"duration_s": t, "distance_m": dist, "E_aero_J_analytic": e_aero, "E_rr_J_analytic": e_rr,
            "rr_smoothing_correction_J": F_rr0 * start_stop_corr, "E_road_J_analytic": e_aero + e_rr,
            "E_road_Wh_per_km_analytic": (e_aero + e_rr) / 3600 / (dist / 1000)}


out["profiles"] = {nm: profile_exact(prof[nm]["segments"]) for nm in ("S1", "S2")}
dst = root / "verification/references"
dst.mkdir(parents=True, exist_ok=True)
(dst / "hand_references.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print(json.dumps(out, indent=2))
