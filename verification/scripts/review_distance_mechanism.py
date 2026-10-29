"""Integrity review phase 2 (saved records only): test the empirical relation  d4_k = dist_Mod(k) - dist_Py(k) ~ -sum_{j<k} v_j * delta_j,
delta_j = j*Ts - (time of the j-th controller update event), and the analogue for the chemical energy with P_j = V_oc*I_j.
Uses the Modelica result CSVs (event times, v, I) and the Python 1e-4 series. No simulation. usage: python review_distance_mechanism.py <root>"""
import json, pathlib, sys
import numpy as np, pandas as pd
root = pathlib.Path(sys.argv[1]); sys.path.insert(0, str(root / "verification/scripts"))
import controller_series as cs
TS = 0.01; out = {}
for p, n in (("S1", 32491), ("S2", 21328)):
    for soh in (1.0, 0.9, 0.8, 0.7):
        for kind in ("fixed", "scheduled"):
            case = f"A_{p}_{kind}_soh{round(soh*100):03d}"; f = root / f"verification/modelica-build/cases_ctl/{case}/{case}_res.csv"
            s, _ = cs.load_modelica(f, n)
            py = np.load(root / f"verification/controller-crosscheck-runs/python_reference/{p}_{kind}_soh{soh:.2f}_dt0.0001.npz")
            df = pd.read_csv(f, usecols=["time", "ctrl.k_ctrl"]); kc = df["ctrl.k_ctrl"].to_numpy(); up = np.searchsorted(kc, np.arange(1, int(kc[-1]) + 1)); te = df["time"].to_numpy()[up]
            delta = np.arange(len(te)) * TS - te
            d4 = s["dist"] - py["dist_t"]; e4 = s["E_chem"] - py["E_chem_t"]
            predd = -np.concatenate([[0], np.cumsum(s["v"][:n] * delta[:n])])
            prede = -np.concatenate([[0], np.cumsum(48.0 * s["I"][:n] * delta[:n])])
            out[case] = {"d4_end": float(d4[-1]), "pred_end": float(predd[-1]), "ratio_end": float(d4[-1] / predd[-1]) if predd[-1] else None,
                         "max_abs_resid_m": float(np.abs(d4 - predd).max()), "max_abs_d4_m": float(np.abs(d4).max()), "corr": float(np.corrcoef(d4, predd)[0, 1]),
                         "E_end": float(e4[-1]), "E_pred_end": float(prede[-1]), "E_ratio_end": float(e4[-1] / prede[-1]) if prede[-1] else None, "E_max_abs_resid_J": float(np.abs(e4 - prede).max()), "E_max_abs_J": float(np.abs(e4).max()),
                         "delta_min_s": float(delta.min()), "delta_max_s": float(delta.max())}
            o = out[case]; print(f"{case:22s} d4 end {o['d4_end']:+.2e} pred {o['pred_end']:+.2e} ratio {o['ratio_end']:.3f} resid max {o['max_abs_resid_m']:.1e} (of {o['max_abs_d4_m']:.1e}) corr {o['corr']:.4f} | E end {o['E_end']:+.1e} pred {o['E_pred_end']:+.1e} ratio {o['E_ratio_end']:.3f} resid {o['E_max_abs_resid_J']:.1e} | delta [{o['delta_min_s']:.1e},{o['delta_max_s']:.1e}]")
json.dump(out, open(root / "verification/controller-crosscheck-runs/review_distance_mechanism.json", "w"), indent=1)
