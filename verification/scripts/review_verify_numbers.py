"""Integrity review phase 4: re-derive the headline numbers directly from the preserved files with code written separately from controller_metrics.py / controller_eval.py.
Modelica: the gzip archives in verification/controller-crosscheck-runs/raw (sha256 of the decompressed bytes checked against evaluation_summary.json), E from the last row,
distance from the last row, e_k from the controller-update rows (first row where ctrl.k_ctrl reaches k+1). Python: artifacts/raw/primary/*/timeseries.npz and the 1e-4 refinement npz.
Definitions restated from src/eureka/metrics.py and scripts/analyze.py. usage: python review_verify_numbers.py <root>"""
import gzip, hashlib, io, json, pathlib, sys
import numpy as np, pandas as pd
root = pathlib.Path(sys.argv[1]); R = root / "verification/controller-crosscheck-runs"
summ = json.loads((R / "evaluation_summary.json").read_text(encoding="utf-8")); shas = summ["raw_csv_sha256_uncompressed"]
IX = {"v": 0, "E_chem": 4, "dist": 13}
def modelica(case):
    raw = gzip.open(R / f"raw/{case}.csv.gz", "rb").read(); assert hashlib.sha256(raw).hexdigest() == shas[case], case
    df = pd.read_csv(io.BytesIO(raw), usecols=["time", "E_chem", "dist", "ctrl.k_ctrl", "ctrl.e_k"])
    kc = df["ctrl.k_ctrl"].to_numpy(); up = np.searchsorted(kc, np.arange(1, int(kc[-1]) + 1))
    e = df["ctrl.e_k"].to_numpy()[up]
    return {"E_Wh_km": df["E_chem"].iloc[-1] / 3600 / (df["dist"].iloc[-1] / 1000), "rmse": float(np.sqrt(np.mean(e ** 2))), "n": len(e)}
def python_saved(prof, kind, soh):
    man = json.loads((root / f"artifacts/raw/primary/{prof}/manifest.json").read_text(encoding="utf-8"))
    j = next(i for i, r in enumerate(man["runs"]) if r["controller"] == kind and abs(r["soh"] - soh) < 1e-9)
    with np.load(root / f"artifacts/raw/primary/{prof}/timeseries.npz") as z:
        e = z["v"][:, j].astype(float) - z["v_ref"]; y = z["y_end"][j]
    return {"E_Wh_km": y[IX["E_chem"]] / 3600 / (y[IX["dist"]] / 1000), "rmse": float(np.sqrt(np.mean(e ** 2))), "n": len(e)}
def python_refined(prof, kind, soh):
    z = np.load(R / f"python_reference/{prof}_{kind}_soh{soh:.2f}_dt0.0001.npz"); e = z["v"] - z["v_ref"]
    return {"E_Wh_km": float(z["E_chem"]) / 3600 / (float(z["dist"]) / 1000), "rmse": float(np.sqrt(np.mean(e ** 2))), "n": len(e)}
def pair(f, s): return (s["E_Wh_km"] - f["E_Wh_km"]) / f["E_Wh_km"] * 100, s["rmse"] / f["rmse"]
out = {}
for prof in ("S1", "S2"):
    for soh in (1.0, 0.9, 0.8, 0.7):
        row = {}
        for lab, fn in (("modelica", lambda k: modelica(f"A_{prof}_{k}_soh{round(soh*100):03d}")), ("python_saved_1e-3", lambda k: python_saved(prof, k, soh)), ("python_1e-4", lambda k: python_refined(prof, k, soh))):
            f, s = fn("fixed"), fn("scheduled"); dE, ratio = pair(f, s)
            row[lab] = {"E_fixed": f["E_Wh_km"], "E_sched": s["E_Wh_km"], "rmse_fixed": f["rmse"], "rmse_sched": s["rmse"], "dE_pct": dE, "rmse_ratio": ratio, "samples": f["n"]}
        out[f"{prof}_soh{soh}"] = row
# saved table values (the project's own computation)
tab = {}
import csv
for r in csv.DictReader(open(root / "artifacts/tables/primary_pairs.csv", encoding="utf-8")): tab[f"{r['profile']}_soh{float(r['soh'])}"] = {"dE_pct": float(r["dE_pct"]), "rmse_ratio": float(r["rmse_ratio"]), "E_fixed": float(r["E_fixed_Wh_km"]), "E_sched": float(r["E_sched_Wh_km"])}
res = json.loads((root / "artifacts/reports/primary_results.json").read_text(encoding="utf-8"))["result"]
out["_saved_table_vs_my_recomputation_max_abs"] = {k: max(abs(out[k]["python_saved_1e-3"]["dE_pct"] - v["dE_pct"]), abs(out[k]["python_saved_1e-3"]["rmse_ratio"] - v["rmse_ratio"]), abs(out[k]["python_saved_1e-3"]["E_fixed"] - v["E_fixed"])) for k, v in tab.items()}
out["_primary_results_json"] = {"dE_pct": res["dE_pct"], "rmse_ratio": res["rmse_ratio"], "E_fixed": res["E_fixed_Wh_km"], "E_sched": res["E_sched_Wh_km"]}
json.dump(out, open(R / "review_verified_numbers.json", "w"), indent=1)
for k, row in out.items():
    if k.startswith("_"): continue
    m, p3, p4 = row["modelica"], row["python_saved_1e-3"], row["python_1e-4"]
    print(f"{k:10s} dE%: mod {m['dE_pct']:.9f} py1e-3 {p3['dE_pct']:.9f} py1e-4 {p4['dE_pct']:.9f} | ratio: {m['rmse_ratio']:.9f} {p3['rmse_ratio']:.9f} {p4['rmse_ratio']:.9f} | |mod-py1e-4| dE {abs(m['dE_pct']-p4['dE_pct']):.1e} ratio {abs(m['rmse_ratio']-p4['rmse_ratio']):.1e}")
print("saved table vs recomputation:", {k: f"{v:.1e}" for k, v in out["_saved_table_vs_my_recomputation_max_abs"].items()})
print("primary_results.json:", out["_primary_results_json"])
print("S1_soh0.8 energies:", {l: (out['S1_soh0.8'][l]['E_fixed'], out['S1_soh0.8'][l]['E_sched']) for l in out['S1_soh0.8']})
