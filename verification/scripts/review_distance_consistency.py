"""Integrity review, phase 2 (saved records only): is each implementation's accumulated distance / chemical energy consistent with its own
speed / current series?  In the smooth 50 km/h cruise (t = 160..195 s of S1) Simpson's rule on the 10 ms samples integrates v and V_oc*I to far better
than 1e-9 m / 1e-6 J (fourth difference of an exponentially decaying v is negligible), so  Delta(dist) - Simpson(v)  measures the state's own inconsistency.
usage: python review_distance_consistency.py <root>"""
import json, pathlib, sys
import numpy as np
root = pathlib.Path(sys.argv[1]); sys.path.insert(0, str(root / "verification/scripts"))
import controller_series as cs
TS = 0.01
def simpson(y, a, b):                      # samples a..b inclusive, (b-a) even
    return TS / 3 * (y[a] + y[b] + 4 * y[a + 1:b:2].sum() + 2 * y[a + 2:b - 1:2].sum())
res = {}
n = "A_S1_fixed_soh080"
s, _ = cs.load_modelica(root / f"verification/modelica-build/cases_ctl/{n}/{n}_res.csv", 32491)
srcs = {"modelica_dassl1e-12": (s["v"], s["dist"], s["I"], s["E_chem"]) }
for lab, f in (("python_dt1e-3", "S1_fixed_soh0.80_dt0.001.npz"), ("python_dt1e-4", "S1_fixed_soh0.80_dt0.0001.npz"), ("python_dt2e-5", "DIAG_S1_fixed_soh0.80_dt2e-05.npz")):
    z = np.load(root / "verification/controller-crosscheck-runs/python_reference" / f)
    srcs[lab] = (z["v"], z["dist_t"], z["i"], z["E_chem_t"])
for (a, b, name) in ((16000, 19500, "cruise 160-195 s (smooth)"), (6500, 9300, "cruise 65-93 s (35 km/h)"), (1800, 2800, "cruise 18-28 s (20 km/h)")):
    res[name] = {}
    for lab, (v, d, i, e) in srcs.items():
        res[name][lab] = {"dist_change_minus_simpson_v_m": float(d[b] - d[a] - simpson(v, a, b)), "E_change_minus_simpson_VocI_J": float(e[b] - e[a] - 48.0 * simpson(i, a, b)),
                          "relative_dist": float((d[b] - d[a] - simpson(v, a, b)) / (d[b] - d[a])), "relative_E": float((e[b] - e[a] - 48.0 * simpson(i, a, b)) / (e[b] - e[a]))}
# effect on the headline metrics for this case: Wh/km from the end states
m = srcs["modelica_dassl1e-12"]; p5 = srcs["python_dt2e-5"]; p4 = srcs["python_dt1e-4"]
wh = lambda d, e: e / 3600.0 / (d / 1000.0)
res["Wh_per_km_end_states"] = {"modelica": wh(m[1][-1], m[3][-1]), "python_dt1e-4": wh(p4[1][-1], p4[3][-1]), "python_dt2e-5": wh(p5[1][-1], p5[3][-1])}
res["Wh_per_km_end_states"]["modelica_minus_python2e-5"] = res["Wh_per_km_end_states"]["modelica"] - res["Wh_per_km_end_states"]["python_dt2e-5"]
res["relative_bias_end_dist"] = float((m[1][-1] - p5[1][-1]) / p5[1][-1]); res["relative_bias_end_E"] = float((m[3][-1] - p5[3][-1]) / p5[3][-1])
json.dump(res, open(root / "verification/controller-crosscheck-runs/review_distance_consistency.json", "w"), indent=1)
print(json.dumps(res, indent=1))
