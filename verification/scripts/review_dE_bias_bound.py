"""Integrity review phase 2: bound on the effect of the accumulator bias on Wh/km and dE%. The relative bias of Wh/km in one run is rE - rd
(relative end-state differences Modelica - Python(dt 1e-4) of E_chem and dist); the dE% bias is (r_sched - r_fixed)*100. Saved records only.
usage: python review_dE_bias_bound.py <root>"""
import json, pathlib, sys
root = pathlib.Path(sys.argv[1]); d = json.loads((root / "verification/controller-crosscheck-runs/review_distance_diagnostics.json").read_text(encoding="utf-8")); out = {}
for p in ("S1", "S2"):
    for soh in (1.0, 0.9, 0.8, 0.7):
        r = {k: d[f"A_{p}_{k}_soh{round(soh*100):03d}"]["rel_E"] - d[f"A_{p}_{k}_soh{round(soh*100):03d}"]["rel_dist"] for k in ("fixed", "scheduled")}
        out[f"{p}_soh{soh}"] = {"WhPerKm_rel_bias_fixed": r["fixed"], "WhPerKm_rel_bias_scheduled": r["scheduled"], "dE_pct_bias_pp": (r["scheduled"] - r["fixed"]) * 100}
        print(p, soh, f"Wh/km rel bias fixed {r['fixed']:.2e} sched {r['scheduled']:.2e} -> dE% bias {(r['scheduled']-r['fixed'])*100:.2e} pp")
json.dump(out, open(root / "verification/controller-crosscheck-runs/review_dE_bias_bound.json", "w"), indent=1)
