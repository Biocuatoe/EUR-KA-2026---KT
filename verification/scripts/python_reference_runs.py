"""Python-only preparatory runs for the controller cross-check (protocol: verification/controller-crosscheck-protocol.md).

Uses the project's own eureka.simulate / eureka.controllers in the locked .venv, writes ONLY under verification/.
Never writes to artifacts/. Steps:
  1. Reproduce the saved primary Python series (S1, S2; fixed/scheduled; SoH 1.0 and 0.8) at the saved dt = 1e-3 and
     compare them with artifacts/raw/primary (max |difference| of v, T, t_ref, z, E_chem, dist) and the saved metrics table.
  2. Refine the integration step (dt = 5e-4, 2.5e-4, 1e-4) to measure the Python scheme's own discretisation error
     for every comparison quantity, on S1, S2 and the tuning profile P-TUNE.
Series are stored in verification/controller-crosscheck-runs/python_reference/*.npz (float64, control-sample grid).
Summary: verification/references/python_dt_study.json
usage: python python_reference_runs.py <project root>
"""
import json
import pathlib
import sys
import time

import numpy as np

root = pathlib.Path(sys.argv[1])
sys.path.insert(0, str(root / "verification/scripts"))
import controller_metrics as cm  # noqa: E402
from eureka.controllers import gain  # noqa: E402
from eureka.cycles import load_profiles  # noqa: E402
from eureka.params import load_params  # noqa: E402
from eureka.plant import IX  # noqa: E402
from eureka.simulate import simulate  # noqa: E402

out_dir = root / "verification/controller-crosscheck-runs/python_reference"
out_dir.mkdir(parents=True, exist_ok=True)
P = load_params()
profiles = load_profiles()
DTS = [1e-3, 5e-4, 2.5e-4, 1e-4]
CASES = {"S1": [("fixed", 1.0), ("scheduled", 1.0), ("fixed", 0.8), ("scheduled", 0.8)],
         "S2": [("fixed", 1.0), ("scheduled", 1.0), ("fixed", 0.8), ("scheduled", 0.8)],
         "P-TUNE": [("fixed", 0.8), ("scheduled", 0.8)]}


def series(out, j):
    y0, y1 = out["y0"][j], out["y_end"][j]
    s = {"v": out["v"][:, j], "v_ref": out["v_ref"][:, j], "T": out["T"][:, j], "u": out["t_ref"][:, j], "t_lim": out["t_lim"][:, j],
         "sat": out["sat"][:, j], "z": out["z"][:, j], "i": out["i"][:, j], "E_chem_t": out["E_chem"][:, j], "dist_t": out["dist"][:, j]}
    for nm, ky in (("E_chem", "E_chem"), ("dist", "dist"), ("E_fb", "E_fb"), ("E_regen", "E_regen"), ("E_R0", "E_R0"), ("E_R1", "E_R1"), ("Ah", "Ah")):
        s[nm] = float(y1[IX[ky]] - y0[IX[ky]])
    return s


summary = {"dts": DTS, "runs": {}}
for prof, cases in CASES.items():
    prof_obj = profiles[prof]
    for dt in DTS:
        p = P.with_overrides(dt=dt)
        plants = [p] * len(cases)
        gains = np.vstack([gain(P, k, s) for k, s in cases])  # designed on nominal parameters, as in the experiment
        t0 = time.time()
        out = simulate(prof_obj, plants, gains, np.array([s for _, s in cases]))
        rt = time.time() - t0
        for j, (kind, soh) in enumerate(cases):
            s = series(out, j)
            key = f"{prof}|{kind}|{soh:.2f}|dt{dt:g}"
            if prof != "P-TUNE" or dt in (1e-3, 1e-4):
                np.savez_compressed(out_dir / f"{prof}_{kind}_soh{soh:.2f}_dt{dt:g}.npz", t=out["t"][:, j], gains=out["gains"][j],
                                    **{k: np.asarray(x) for k, x in s.items()})
            summary["runs"][key] = {"metrics": cm.metrics(s), "runtime_batch_s": round(rt, 1),
                                    "end_v": float(s["v"][-1]), "end_E_chem": s["E_chem"], "end_dist": s["dist"]}
        print(prof, dt, f"{rt:.0f}s", flush=True)

# 1. reproduction of the saved series at dt = 1e-3
repro = {}
for prof in ("S1", "S2"):
    man = json.loads((root / f"artifacts/raw/primary/{prof}/manifest.json").read_text(encoding="utf-8"))
    with np.load(root / f"artifacts/raw/primary/{prof}/timeseries.npz") as z:
        arr = {k: z[k] for k in z.files}
    for j, r in enumerate(man["runs"]):
        kind, soh = r["controller"], r["soh"]
        if (kind, soh) not in CASES[prof]:
            continue
        mine = np.load(out_dir / f"{prof}_{kind}_soh{soh:.2f}_dt0.001.npz")
        d = {}
        for k_saved, k_mine in (("v", "v"), ("T", "T"), ("t_ref", "u"), ("z", "z"), ("t_lim", "t_lim"), ("i", "i")):
            d[k_saved] = float(np.max(np.abs(arr[k_saved][:, j] - mine[k_mine])))
        d["sat_mismatches"] = int(np.sum(arr["sat"][:, j].astype(bool) != mine["sat"].astype(bool)))
        yend = arr["y_end"][j]
        d["E_chem_end_abs"] = float(abs(yend[IX["E_chem"]] - mine["E_chem"]))
        d["dist_end_abs"] = float(abs(yend[IX["dist"]] - mine["dist"]))
        d["gain_max_abs_diff"] = float(np.max(np.abs(np.array(r["gain"]) - mine["gains"])))
        repro[f"{prof}|{kind}|{soh:.2f}"] = d
summary["reproduction_of_saved_series"] = repro

# metric-function check against the saved metrics table
import csv  # noqa: E402

rows = list(csv.DictReader(open(root / "artifacts/tables/primary_metrics.csv", encoding="utf-8")))
chk = {}
for r in rows:
    key = f"{r['profile']}|{r['controller']}|{float(r['soh']):.2f}|dt0.001"
    if key not in summary["runs"]:
        continue
    m = summary["runs"][key]["metrics"]
    worst = 0.0
    for name in ("distance_km", "energy_Wh", "energy_Wh_per_km", "rmse_ms", "max_abs_err_ms", "rms_current_A", "peak_current_A", "ah_throughput",
                 "resistive_loss_Wh", "friction_brake_Wh", "regen_recovered_Wh", "traction_limited_frac", "rms_jerk_ms3", "rms_torque_cmd_Nm"):
        worst = max(worst, abs(m[name] - float(r[name])) / max(abs(float(r[name])), 1e-300) if float(r[name]) != 0 else abs(m[name]))
    chk[key] = worst
summary["metric_functions_vs_saved_table_max_rel_diff"] = chk
(root / "verification/references/python_dt_study.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
print("reproduction max over runs:", {k: max(v for v in d.values()) for k, d in repro.items()})
print("metric check:", max(chk.values()))
