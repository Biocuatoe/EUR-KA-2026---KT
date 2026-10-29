"""Independent checks (Part B): saved raw outputs and an inverse-dynamics energy reference.

Read-only: opens artifacts/raw/*/manifest.json and timeseries.npz; writes only to argv[2].
Metric formulas are re-implemented here (not eureka.metrics).
"""

import json
import math
import pathlib
import sys

import numpy as np
import yaml
from scipy.linalg import eig, expm

ROOT = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(sys.argv[2])
RAW = ROOT / "artifacts" / "raw"
ST = ["v", "T", "V1", "SoC", "E_chem", "E_rr", "E_aero", "E_fb", "E_gear", "E_visc", "E_mi",
      "E_R0", "E_R1", "dist", "Ah", "E_regen"]  # order documented in src/eureka/plant.py
I = {k: i for i, k in enumerate(ST)}
LOSS = ["E_rr", "E_aero", "E_fb", "E_gear", "E_visc", "E_mi", "E_R0", "E_R1"]
R = {}


def rec(key, **kw):
    R[key] = kw
    print(key, json.dumps(kw, default=float)[:1500])


def load(exp, batch):
    d = RAW / exp / batch
    m = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
    with np.load(d / "timeseries.npz") as z:
        a = {k: z[k] for k in z.files}
    return m, a


def metrics(m, a, j):
    p = {**m["nominal_parameters"], **m["runs"][j]["overrides"]}
    soh = m["runs"][j]["soh"]
    y0, y1 = a["y0"][j], a["y_end"][j]
    dist = y1[I["dist"]] - y0[I["dist"]]
    e = y1[I["E_chem"]] - y0[I["E_chem"]]
    v = a["v"][:, j].astype(float)
    err = v - a["v_ref"]
    meff = p["M"] + p["J_m"] * p["G"] ** 2 / p["r_w"] ** 2
    sinks = 0.5 * meff * (y1[I["v"]] ** 2 - y0[I["v"]] ** 2) + 0.5 * p["C1"] * (y1[I["V1"]] ** 2 - y0[I["V1"]] ** 2)
    sinks += sum(y1[I[k]] - y0[I[k]] for k in LOSS)
    thr = p["V_oc"] * 3600 * (y1[I["Ah"]] - y0[I["Ah"]])
    tref, tl = a["t_ref"][:, j].astype(float), a["t_lim"][:, j].astype(float)
    return {
        "run_id": m["runs"][j]["run_id"], "controller": m["runs"][j]["controller"], "soh": soh,
        "E_Wh": e / 3600, "dist_m": dist, "E_Wh_km": (e / 3600) / (dist / 1000),
        "rmse": float(np.sqrt(np.mean(err**2))), "max_abs_err": float(np.max(np.abs(err))),
        "closure_rel": float(abs(e - sinks) / thr),
        "closure_rel_if_aero_off_by_1pct": float(abs(e - (sinks + 0.01 * (y1[I["E_aero"]] - y0[I["E_aero"]]))) / thr),
        "E_fb_J": float(y1[I["E_fb"]] - y0[I["E_fb"]]),
        "sat_frac": float(np.mean(a["sat"][:, j])),
        "min_drive_headroom_Nm": float(np.min(np.where(tref > 0, tl - tref, np.inf))),
        "min_brake_headroom_Nm": float(np.min(np.where(tref < 0, tl + tref, np.inf))),
        "peak_tref_over_tlim": float(np.max(np.abs(tref) / tl)),
        "resistive_share": float((y1[I["E_R0"]] + y1[I["E_R1"]] - y0[I["E_R0"]] - y0[I["E_R1"]]) / e),
        "road_share": float((y1[I["E_rr"]] + y1[I["E_aero"]] - y0[I["E_rr"]] - y0[I["E_aero"]]) / e),
        "mi_share": float((y1[I["E_mi"]] - y0[I["E_mi"]]) / e),
        "gear_share": float((y1[I["E_gear"]] + y1[I["E_visc"]] - y0[I["E_gear"]] - y0[I["E_visc"]]) / e),
        "gain": m["runs"][j]["gain"], "min_v": float(np.min(v)),
        "nonfinite": bool(a["nonfinite"][:, j].any()), "infeasible": bool(a["infeasible"][:, j].any()),
    }


# ---------------- IC-10 primary recomputation ----------------
prim = {}
traj_same = {}
for prof in ("S1", "S2"):
    m, a = load("primary", prof)
    rows = [metrics(m, a, j) for j in range(len(m["runs"]))]
    prim[prof] = rows
    f = {r["soh"]: (j, r) for j, r in enumerate(rows) if r["controller"] == "fixed"}
    # mechanical trajectory of the FIXED controller should not depend on SoH (SoH acts only on R0, R1)
    j1, j7 = f[1.0][0], f[0.7][0]
    traj_same[prof] = float(np.max(np.abs(a["v"][:, j1] - a["v"][:, j7])))
pairs = []
csv = (ROOT / "artifacts" / "tables" / "primary_pairs.csv").read_text(encoding="utf-8").splitlines()
hdr = csv[0].split(",")
saved = {(r.split(",")[hdr.index("profile")], float(r.split(",")[hdr.index("soh")])): r.split(",") for r in csv[1:]}
for prof, rows in prim.items():
    for soh in (1.0, 0.9, 0.8, 0.7):
        fx = next(r for r in rows if r["controller"] == "fixed" and r["soh"] == soh)
        sc = next(r for r in rows if r["controller"] == "scheduled" and r["soh"] == soh)
        dE = (sc["E_Wh_km"] - fx["E_Wh_km"]) / fx["E_Wh_km"] * 100
        dE_wh = (sc["E_Wh"] - fx["E_Wh"]) / fx["E_Wh"] * 100
        s = saved[(prof, soh)]
        pairs.append({"profile": prof, "soh": soh, "E_fixed": fx["E_Wh_km"], "E_sched": sc["E_Wh_km"],
                      "dE_pct": dE, "dE_pct_total_Wh_basis": dE_wh, "rmse_ratio": sc["rmse"] / fx["rmse"],
                      "saved_dE_pct": float(s[hdr.index("dE_pct")]), "saved_rmse_ratio": float(s[hdr.index("rmse_ratio")]),
                      "dist_diff_m": sc["dist_m"] - fx["dist_m"]})
allrows = [r for rows in prim.values() for r in rows]
rec("IC-10", pairs=pairs,
    max_abs_dE_diff_vs_saved=max(abs(p["dE_pct"] - p["saved_dE_pct"]) for p in pairs),
    max_closure_rel=max(r["closure_rel"] for r in allrows),
    NEGATIVE_CONTROL_min_closure_with_1pct_aero_error=min(r["closure_rel_if_aero_off_by_1pct"] for r in allrows),
    max_sat_frac=max(r["sat_frac"] for r in allrows), total_E_fb_J=sum(r["E_fb_J"] for r in allrows),
    min_drive_headroom_Nm=min(r["min_drive_headroom_Nm"] for r in allrows),
    min_brake_headroom_Nm=min(r["min_brake_headroom_Nm"] for r in allrows),
    max_peak_tref_over_tlim=max(r["peak_tref_over_tlim"] for r in allrows),
    resistive_share_range=[min(r["resistive_share"] for r in allrows), max(r["resistive_share"] for r in allrows)],
    S1_soh08_fixed_shares={k: next(r for r in prim["S1"] if r["controller"] == "fixed" and r["soh"] == 0.8)[k]
                           for k in ("road_share", "mi_share", "gear_share", "resistive_share")},
    fixed_v_traj_maxdiff_soh1_vs_soh07=traj_same,
    any_nonfinite=any(r["nonfinite"] for r in allrows), any_infeasible=any(r["infeasible"] for r in allrows),
    min_v=min(r["min_v"] for r in allrows),
    sanity_soh1_bit_identical={p["profile"]: (p["dE_pct"] == 0.0 and p["rmse_ratio"] == 1.0) for p in pairs if p["soh"] == 1.0},
    gains_in_manifest={r["run_id"]: [round(x, 4) for x in r["gain"]] for r in prim["S1"]})

# ---------------- IC-11 inverse-dynamics energy reference (ideal tracking) ----------------
cfg = yaml.safe_load((ROOT / "configs" / "parameters.yaml").read_text(encoding="utf-8"))
V = {f"{g}.{k}": s["value"] for g, it in cfg.items() if isinstance(it, dict) for k, s in it.items()}
M, Af, Cd, Crr = V["vehicle.mass"], V["vehicle.frontal_area"], V["vehicle.drag_coefficient"], V["vehicle.rolling_resistance"]
rw, rho, g = V["vehicle.wheel_radius"], V["vehicle.air_density"], V["vehicle.gravity"]
G, eg, Jm, Bm = V["drivetrain.gear_ratio"], V["drivetrain.gear_efficiency"], V["drivetrain.motor_inertia"], V["drivetrain.motor_viscous_friction"]
emi, Tmax, Pmax = V["drivetrain.motor_inverter_efficiency"], V["drivetrain.torque_max"], V["drivetrain.power_max"]
Voc, R0n, R1n, C1 = V["battery.open_circuit_voltage"], V["battery.r0_new"], V["battery.r1_new"], V["battery.c1"]
kr0, kr1, veps = V["battery.k_r0"], V["battery.k_r1"], V["simulation.speed_smoothing"]
Meff = M + Jm * G**2 / rw**2


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


def inverse_energy(name, soh, h=1e-3):
    kt, kv = build(prof_cfg[name]["segments"])
    r0, r1 = R0n * (1 + kr0 * (1 - soh)), R1n * (1 + kr1 * (1 - soh))
    tc = math.exp(-h / (r1 * C1))
    V1 = E = dist = Erd = Emi = Er = 0.0
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
        Er += (r0 * i * i + V1 * V1 / r1) * h
        Erd += (Crr * M * g * math.tanh(v / veps) + 0.5 * rho * Cd * Af * v * v) * v * h
        Emi += (pe - pm) * h
        dist += v * h
        V1 = V1 * tc + r1 * (1 - tc) * i
    return {"E_Wh_km": E / 3600 / (dist / 1000), "dist_m": dist, "resistive_share": Er / E, "road_share": Erd / E,
            "mi_share": Emi / E}


inv = {}
for name in ("S1", "S2"):
    for soh in (1.0, 0.8):
        ref = inverse_energy(name, soh)
        sim = {c: next(r for r in prim[name] if r["controller"] == c and r["soh"] == soh)["E_Wh_km"] for c in ("fixed", "scheduled")}
        inv[f"{name}_soh{soh}"] = {**ref, "sim_fixed": sim["fixed"], "sim_sched": sim["scheduled"],
                                   "fixed_minus_ideal_pct": (sim["fixed"] - ref["E_Wh_km"]) / ref["E_Wh_km"] * 100}
rec("IC-11", **inv)

# ---------------- IC-12 S-C (H_C) recomputation ----------------
m, a = load("fixed_family", "S1")
fam_rows = [metrics(m, a, j) | {"r_scale": m["runs"][j]["r_scale"]} for j in range(len(m["runs"]))]
sched = [r for r in prim["S1"] if r["controller"] == "scheduled"]
sE, sR = np.mean([r["E_Wh_km"] for r in sched]), np.mean([r["rmse"] for r in sched])
fam = {}
for r in fam_rows:
    fam.setdefault(r["r_scale"], []).append(r)
agg = {c: (np.mean([x["E_Wh_km"] for x in rs]), np.mean([x["rmse"] for x in rs]), len(rs)) for c, rs in fam.items()}
feas = {c: v for c, v in agg.items() if v[1] <= sR}
best = min(feas, key=lambda c: feas[c][0])
rmse_soh_spread = max(np.ptp([x["rmse"] for x in rs]) for rs in fam.values())
Es = [v[0] for v in agg.values()]
rec("IC-12", sched_avg_E=sE, sched_avg_rmse=sR, n_members=len(agg), n_feasible=len(feas),
    best_r_scale=best, best_E=feas[best][0], best_rmse=feas[best][1],
    H_C_holds_rel_0p1pct=bool(feas[best][0] <= sE * 1.001), H_C_holds_abs_0p1pp=bool(feas[best][0] <= sE + 0.001 * sE),
    best_at_range_edge=bool(best == min(agg)), family_energy_span_pct=(max(Es) - min(Es)) / min(Es) * 100,
    max_rmse_spread_across_soh_within_member=float(rmse_soh_spread),
    max_closure=max(r["closure_rel"] for r in fam_rows),
    E_and_rmse_monotone_in_r=bool(all(np.diff([agg[c][0] for c in sorted(agg)]) >= -1e-9) and all(np.diff([agg[c][1] for c in sorted(agg)]) >= -1e-9)))

# ---------------- IC-13 gamma sweep ----------------
m, a = load("gamma_sweep", "S1")
gs_rows = [metrics(m, a, j) | {"gu": m["runs"][j]["gamma_u"], "gv": m["runs"][j]["gamma_v"]} for j in range(len(m["runs"]))]
ref = next(r for r in gs_rows if r["controller"] == "fixed")
dEs = [(r["E_Wh_km"] - ref["E_Wh_km"]) / ref["E_Wh_km"] * 100 for r in gs_rows if r["controller"] == "scheduled"]
rr = [r["rmse"] / ref["rmse"] for r in gs_rows if r["controller"] == "scheduled"]
corr = float(np.corrcoef(dEs, rr)[0, 1])
rec("IC-13", n=len(dEs), dE_min=min(dEs), dE_max=max(dEs), rmse_ratio_min=min(rr), rmse_ratio_max=max(rr),
    corr_dE_vs_rmse_ratio=corr, max_closure=max(r["closure_rel"] for r in gs_rows))

# ---------------- IC-14 S-D recomputation ----------------
m, a = load("robustness", "draws-0000-0049")
rows = [metrics(m, a, j) | {"draw": m["runs"][j]["draw"], "seed": m["runs"][j]["seed"], "ov": m["runs"][j]["overrides"]} for j in range(len(m["runs"]))]
by = {}
for j, r in enumerate(rows):
    by.setdefault(r["draw"], {})[r["controller"]] = (j, r)
d, ratios, share_ok, noise_ok, in_range = [], [], True, True, True
rng_cfg = {k: (s["uncertainty"]["low"], s["uncertainty"]["high"]) for g_, it in cfg.items() if isinstance(it, dict)
           for k, s in it.items() if s.get("uncertainty")}
fieldmap = {"mass": "M", "frontal_area": "A_f", "drag_coefficient": "Cd", "rolling_resistance": "Crr",
            "wheel_radius": "r_w", "motor_inverter_efficiency": "eta_mi", "r0_new": "R0_new"}
lim = {fieldmap[k]: v for k, v in rng_cfg.items() if k in fieldmap}
for dr, pr in sorted(by.items()):
    (jf, f), (js, s) = pr["fixed"], pr["scheduled"]
    d.append((s["E_Wh_km"] - f["E_Wh_km"]) / f["E_Wh_km"] * 100)
    ratios.append(s["rmse"] / f["rmse"])
    share_ok &= f["ov"] == s["ov"] and f["seed"] == s["seed"]
    noise_ok &= bool(np.array_equal(a["noise"][jf], a["noise"][js]))
    in_range &= all(lim[k][0] <= v <= lim[k][1] for k, v in f["ov"].items())
d = np.array(d)
sd, mean = float(np.std(d, ddof=1)), float(np.mean(d))
h = max(0.1, 0.1 * abs(mean))
N = min(1000, max(50, math.ceil((1.96 * sd / h) ** 2)))
rng = np.random.default_rng(987654321)  # deliberately NOT the project's seed
bm = d[rng.integers(0, len(d), size=(10000, len(d)))].mean(axis=1)
rec("IC-14", n_pairs=len(d), mean_dE=mean, sd_dE=sd, N_rule=N, bootstrap95_independent_seed=[float(np.quantile(bm, .025)), float(np.quantile(bm, .975))],
    frac_sched_lower=float(np.mean(d < 0)), max_abs_dE=float(np.max(np.abs(d))), median_rmse_ratio=float(np.median(ratios)),
    pairs_share_params_and_seed=bool(share_ok), pairs_share_identical_noise=bool(noise_ok), overrides_within_assumed_ranges=bool(in_range),
    max_closure=max(r["closure_rel"] for r in rows), tracking_failures=sum(r["rmse"] > 1.5 or r["max_abs_err"] > 3 for r in rows),
    max_sat_frac=max(r["sat_frac"] for r in rows), total_E_fb_J=sum(r["E_fb_J"] for r in rows))

# ---------------- IC-15 common quadratic Lyapunov function across all frozen SoH gains ----------------
sys.path.insert(0, str(pathlib.Path(__file__).parent))
pa = json.loads((pathlib.Path(sys.argv[2]).parent / "ic_a.json").read_text(encoding="utf-8"))
a0 = -pa["IC-04"]["sympy"]["motoring"]["dfdv_at_v0"]; b0 = pa["IC-04"]["sympy"]["motoring"]["dfdT"]
tau, Ts = V["drivetrain.torque_time_constant"], V["controller.sample_time"]
A = np.array([[-a0, b0, 0], [0, -1 / tau, 0], [1, 0, 0]]); B = np.array([[0], [1 / tau], [0]])
Mx = np.zeros((4, 4)); Mx[:3, :3] = A; Mx[:3, 3:] = B
E_ = expm(Mx * Ts); Ad, Bd = E_[:3, :3], E_[:3, 3:]
emax, Tb, zmax = V["controller.bryson_velocity_error_max"], V["controller.bryson_torque_max"], V["controller.bryson_integral_error_max"]
Q0 = np.diag([1 / emax**2, 1 / Tb**2, 1 / zmax**2]); Rr0 = np.array([[1 / Tb**2]])


def dare(Q, Rm):
    n = 3
    Gm = Bd @ np.linalg.solve(Rm, Bd.T)
    w, Vv = eig(np.block([[Ad, np.zeros((n, n))], [-Q, np.eye(n)]]), np.block([[np.eye(n), Gm], [np.zeros((n, n)), Ad.T]]))
    idx = np.where(np.abs(w) < 1)[0]
    Pm = np.real(Vv[n:, idx] @ np.linalg.inv(Vv[:n, idx])); Pm = (Pm + Pm.T) / 2
    return np.linalg.solve(Rm + Bd.T @ Pm @ Bd, Bd.T @ Pm @ Ad), Pm


cql = {}
Ks = {}
for s in np.linspace(0.5, 1.0, 101):
    al = 1 / (1 + (1 - s)); Ks[s] = dare(Q0 @ np.diag([1, al, 1]), Rr0 * (1 + (1 - s)))[0]
for s_ref in (1.0, 0.75, 0.5):
    _, Pc = dare(Q0 @ np.diag([1, 1 / (1 + (1 - s_ref)), 1]), Rr0 * (1 + (1 - s_ref)))
    worst = max(float(np.max(np.linalg.eigvalsh((Ad - Bd @ K).T @ Pc @ (Ad - Bd @ K) - Pc))) for K in Ks.values())
    cql[f"P_from_soh_{s_ref}"] = worst  # < 0 for every K => common Lyapunov function
# negative control: a candidate that must fail (identity matrix)
cql["NEGATIVE_CONTROL_identity_candidate"] = max(float(np.max(np.linalg.eigvalsh((Ad - Bd @ K).T @ (Ad - Bd @ K) - np.eye(3)))) for K in Ks.values())
rec("IC-15", max_eig_of_AclT_P_Acl_minus_P=cql, n_soh_points=len(Ks))

OUT.write_text(json.dumps(R, indent=2, default=float), encoding="utf-8")
