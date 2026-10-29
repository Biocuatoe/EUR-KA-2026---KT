"""Integrity review phase 2 (saved records): window consistency residual  d(dist) - Simpson(v)  for tolerance variants, other controller/SoH, and S2. usage: python review_distance_variants.py <root>"""
import sys, numpy as np, json, pathlib
root = pathlib.Path(sys.argv[1]); sys.path.insert(0, str(root / "verification/scripts"))
import controller_series as cs
TS = 0.01
def simpson(y, a, b): return TS / 3 * (y[a] + y[b] + 4 * y[a + 1:b:2].sum() + 2 * y[a + 2:b - 1:2].sum())
out = {}
for n in ("A_S1_fixed_soh080", "N_S1_fixed_soh080_dassl_tol1e-10", "N_S1_fixed_soh080_dassl_tol1e-08", "A_S1_scheduled_soh080", "A_S1_fixed_soh070", "A_S2_fixed_soh080"):
    p = 32491 if "S1" in n else 21328
    s, _ = cs.load_modelica(root / f"verification/modelica-build/cases_ctl/{n}/{n}_res.csv", p)
    a, b = (16000, 19500) if "S1" in n else (15800, 16800)
    r = float(s["dist"][b] - s["dist"][a] - simpson(s["v"], a, b)); out[n] = {"window_s": [a * TS, b * TS], "ddist_minus_simpson_v_m": r}
    print(f"{n:38s} window {a*TS:.0f}-{b*TS:.0f} s: d(dist) - Simpson(v) = {r:.3e} m")
json.dump(out, open(root / "verification/controller-crosscheck-runs/review_distance_consistency_variants.json", "w"), indent=1)
