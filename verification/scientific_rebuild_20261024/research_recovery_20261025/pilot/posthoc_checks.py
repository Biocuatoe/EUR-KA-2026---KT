"""POST-HOC (not pre-registered) checks on existing pilot outputs; no new simulation.

1. RMSE attribution: did any *fixed* tuning candidate (already simulated on T1 and T2) reach the tracking that the
   tuned scheduled gain reaches at SoH 0.8, and at what energy? If yes, the scheduled branch's lower RMSE at SoH 0.8 is
   a gain-magnitude choice available to a fixed gain, not something scheduling uniquely provides.
2. Energy per actual km contrasts (the protocol's primary denominator is the reference km; both are reported).
Writes out/analysis/posthoc.json.
"""

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"


def rd(p):
    with p.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


cand = rd(OUT / "tune" / "candidates.csv")
sel = json.loads((OUT / "tune" / "selected.json").read_text(encoding="utf-8"))
res = {}

# 1. RMSE attribution on the training scenarios (S1, T1 = SoH 1.0, T2 = SoH 0.8)
by = {}
for r in cand:
    if r["branch"] in ("F0", "S0"):
        by.setdefault((r["branch"], int(r["cand"])), {})[r["scen"]] = r
s_sel = by[("S0", sel["S0"]["cand"])]
target_t2 = float(s_sel["T2"]["rmse_ms"])
f_sel = by[("F0", sel["F0"]["cand"])]
rows = []
for (br, ci), d in by.items():
    if br != "F0" or len(d) != 2:
        continue
    rows.append({"cand": ci, "sigma": float(d["T1"]["sigma"]), "c": float(d["T1"]["c"]),
                 "rmse_T1": float(d["T1"]["rmse_ms"]), "rmse_T2": float(d["T2"]["rmse_ms"]),
                 "E_T1": float(d["T1"]["Wh_per_ref_km"]), "E_T2": float(d["T2"]["Wh_per_ref_km"])})
better = [r for r in rows if r["rmse_T1"] <= target_t2 and r["rmse_T2"] <= target_t2]
res["rmse_attribution"] = {
    "scheduled_selected": {"rmse_T1_soh1.0": float(s_sel["T1"]["rmse_ms"]), "rmse_T2_soh0.8": target_t2,
                           "E_T1": float(s_sel["T1"]["Wh_per_ref_km"]), "E_T2": float(s_sel["T2"]["Wh_per_ref_km"])},
    "fixed_selected": {"rmse_T1": float(f_sel["T1"]["rmse_ms"]), "rmse_T2": float(f_sel["T2"]["rmse_ms"]),
                       "E_T1": float(f_sel["T1"]["Wh_per_ref_km"]), "E_T2": float(f_sel["T2"]["Wh_per_ref_km"])},
    "n_fixed_candidates": len(rows),
    "fixed_candidates_with_rmse_le_scheduled_soh0.8_at_both_soh": sorted(better, key=lambda r: r["E_T2"]),
    "fixed_rmse_T1_equals_T2_max_abs_diff": max(abs(r["rmse_T1"] - r["rmse_T2"]) for r in rows),
}

# 2. energy per actual km for the four contrasts on held-out cycles
ev = {(r["cycle"], r["scen"], r["branch"]): r for r in rd(OUT / "eval" / "runs.csv")}
act = []
for c in ("S2", "UDDS"):
    for s in ("E1", "E2", "E2b", "E3", "E4"):
        for name, a, b in (("S0_vs_F0", "S0", "F0"), ("S1_vs_F1", "S1", "F1"), ("F1_vs_F0", "F1", "F0"), ("S1_vs_S0", "S1", "S0")):
            A, B = ev[(c, s, a)], ev[(c, s, b)]
            act.append({"cycle": c, "scen": s, "contrast": name,
                        "dE_pct_actual_km": 100 * (float(A["Wh_per_km"]) - float(B["Wh_per_km"])) / float(B["Wh_per_km"])})
res["actual_km_contrasts_max_abs_pct"] = max(abs(a["dE_pct_actual_km"]) for a in act)
res["actual_km_contrasts"] = act
(OUT / "analysis" / "posthoc.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
ra = res["rmse_attribution"]
print(json.dumps({k: v for k, v in ra.items() if k != "fixed_candidates_with_rmse_le_scheduled_soh0.8_at_both_soh"}, indent=1))
print("fixed candidates reaching scheduled SoH-0.8 tracking at BOTH SoH:", len(ra["fixed_candidates_with_rmse_le_scheduled_soh0.8_at_both_soh"]))
for r in ra["fixed_candidates_with_rmse_le_scheduled_soh0.8_at_both_soh"][:5]:
    print(r)
print("max |dE| per actual km over held-out contrasts: %.4f %%" % res["actual_km_contrasts_max_abs_pct"])
