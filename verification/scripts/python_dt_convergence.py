"""Convergence analysis of the Python step-size study (reads verification/references/python_dt_study.json and the stored series).
Writes verification/references/python_dt_convergence.json. usage: python python_dt_convergence.py <root>"""
import json, pathlib, sys
import numpy as np
root = pathlib.Path(sys.argv[1])
d = json.loads((root / "verification/references/python_dt_study.json").read_text(encoding="utf-8"))
DTS = [1e-3, 5e-4, 2.5e-4, 1e-4]
out = {}
names = ["energy_Wh_per_km", "rmse_ms", "max_abs_err_ms", "distance_km", "peak_current_A", "traction_limited_frac", "friction_brake_Wh", "regen_recovered_Wh", "rms_jerk_ms3"]
cases = sorted({k.rsplit("|dt", 1)[0] for k in d["runs"]})
for c in cases:
    row = {}
    for n in names:
        v = [d["runs"][f"{c}|dt{dt:g}"]["metrics"][n] for dt in DTS]
        diffs = [abs(v[i] - v[i + 1]) for i in range(3)]          # successive differences 1e-3->5e-4, 5e-4->2.5e-4, 2.5e-4->1e-4
        row[n] = {"values": v, "abs_diff_to_1e-4": [abs(x - v[3]) for x in v[:3]], "successive_diffs": diffs,
                  "rel_diff_1e-3_vs_1e-4": abs(v[0] - v[3]) / abs(v[3]) if v[3] else None}
    out[c] = row
# trace differences 1e-3 vs 1e-4 (stored series)
tr = {}
P = root / "verification/controller-crosscheck-runs/python_reference"
for c in cases:
    prof, kind, soh = c.split("|")
    a = np.load(P / f"{prof}_{kind}_soh{soh}_dt0.001.npz"); b = np.load(P / f"{prof}_{kind}_soh{soh}_dt0.0001.npz")
    tr[c] = {k: float(np.max(np.abs(a[k] - b[k]))) for k in ("v", "T", "u", "z", "i", "E_chem_t", "dist_t")}
    tr[c]["sat_flag_mismatches"] = int(np.sum(a["sat"].astype(bool) != b["sat"].astype(bool)))
    tr[c]["E_chem_end_abs"] = abs(float(a["E_chem"]) - float(b["E_chem"]))
out["_traces_1e-3_vs_1e-4"] = tr
# pair quantities per dt
import sys as _s; _s.path.insert(0, str(root / "verification/scripts")); import controller_metrics as cm
pairs = {}
for prof in ("S1", "S2", "P-TUNE"):
    for soh in ("1.00", "0.80"):
        if f"{prof}|fixed|{soh}|dt0.001" not in d["runs"]: continue
        pairs[f"{prof}|{soh}"] = {}
        for dt in DTS:
            f, s = d["runs"][f"{prof}|fixed|{soh}|dt{dt:g}"]["metrics"], d["runs"][f"{prof}|scheduled|{soh}|dt{dt:g}"]["metrics"]
            pairs[f"{prof}|{soh}"][f"{dt:g}"] = cm.pair(f, s)
out["_pairs"] = pairs
(root / "verification/references/python_dt_convergence.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
for c in cases:
    r = out[c]["energy_Wh_per_km"]; q = out[c]["rmse_ms"]
    print(f"{c:22s} E  succ.diffs {r['successive_diffs'][0]:.2e} {r['successive_diffs'][1]:.2e} {r['successive_diffs'][2]:.2e} | rmse succ {q['successive_diffs'][0]:.2e} {q['successive_diffs'][1]:.2e} {q['successive_diffs'][2]:.2e}")
for k, v in pairs.items():
    print(k, {dt: (round(p["dE_pct"], 9), round(p["rmse_ratio"], 9)) for dt, p in v.items()})
for c, t in tr.items(): print(c, {k: f"{x:.2e}" for k, x in t.items()})
