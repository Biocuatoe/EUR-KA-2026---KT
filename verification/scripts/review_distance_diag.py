"""Integrity review, phase 2: bounded diagnostic calculations on SAVED records only (no simulation is run).
For every primary case: where does dist_Mod - dist_Py(1e-4) accumulate, and how does it relate to speed, time, sample-time drift, energy?
Writes verification/controller-crosscheck-runs/review_distance_diagnostics.json. usage: python review_distance_diag.py <root>"""
import json, pathlib, sys
import numpy as np, pandas as pd
root = pathlib.Path(sys.argv[1]); sys.path.insert(0, str(root / "verification/scripts"))
import controller_series as cs
TS = 0.01
STEPS = {"S1": 32491, "S2": 21328}
import yaml
prof = yaml.safe_load((root / "configs/cycles/profiles.yaml").read_text(encoding="utf-8"))
def knots(name):
    t, v = [0.0], [0.0]
    for s in prof[name]["segments"]:
        if "idle" in s or "cruise" in s: t.append(t[-1] + float(s.get("idle", s.get("cruise")))); v.append(v[-1])
        else:
            tg = s["to_kmh"] / 3.6; t.append(t[-1] + (tg - v[-1]) / s["accel"]); v.append(tg)
    return np.array(t), np.array(v)
out = {}
for p in ("S1", "S2"):
    tk, vk = knots(p); n = STEPS[p]
    for soh in (1.0, 0.9, 0.8, 0.7):
        for kind in ("fixed", "scheduled"):
            case = f"A_{p}_{kind}_soh{round(soh*100):03d}"
            f = root / f"verification/modelica-build/cases_ctl/{case}/{case}_res.csv"
            s, info = cs.load_modelica(f, n)
            py = np.load(root / f"verification/controller-crosscheck-runs/python_reference/{p}_{kind}_soh{soh:.2f}_dt0.0001.npz")
            d4 = s["dist"] - py["dist_t"]
            e4 = s["E_chem"] - py["E_chem_t"]
            g = np.diff(d4)
            # per-segment accumulation
            seg = []
            for i in range(len(tk) - 1):
                a, b = int(round(tk[i] / TS)), min(int(round(tk[i + 1] / TS)), n)
                if b > a: seg.append({"seg": i + 1, "t0": float(tk[i]), "t1": float(tk[i + 1]), "v0_kmh": float(vk[i] * 3.6), "v1_kmh": float(vk[i + 1] * 3.6), "d4_change_m": float(d4[b] - d4[a]), "E_change_J": float(e4[b] - e4[a])})
            # update-row time offsets
            df = pd.read_csv(f, usecols=["time", "ctrl.k_ctrl"]); kc = df["ctrl.k_ctrl"].to_numpy(); up = np.searchsorted(kc, np.arange(1, int(kc[-1]) + 1), side="left"); te = df["time"].to_numpy()[up]
            delta = np.arange(len(te)) * TS - te      # positive = event earlier than k*Ts
            vv = 0.5 * (s["v"][:-1] + s["v"][1:])
            m = vv > 1.0
            out[case] = {
                "d4_end_m": float(d4[-1]), "d4_max_abs_m": float(np.abs(d4).max()), "E_end_diff_J": float(e4[-1]), "dist_end_m": float(s["dist"][-1]),
                "rel_dist": float(d4[-1] / s["dist"][-1]), "rel_E": float(e4[-1] / s["E_chem"][-1]),
                "delta_event_earlier_max_s": float(delta.max()), "delta_event_at_end_s": float(delta[-1]),
                "frac_of_total_in_cruise_samples_v>1": float(g[m].sum() / g.sum()) if g.sum() != 0 else None,
                "corr_increment_vs_v_times_delta": float(np.corrcoef(g[m], -(vv[m] * delta[:-1][m]))[0, 1]) if len(g[m]) > 10 else None,
                "increments_over_v_delta_median": float(np.median(g[m] / (-(vv[m] * delta[:-1][m] + 1e-300)))),
                "segments": seg,
            }
json.dump(out, open(root / "verification/controller-crosscheck-runs/review_distance_diagnostics.json", "w"), indent=1)
for c, o in out.items():
    big = sorted(o["segments"], key=lambda x: -abs(x["d4_change_m"]))[:3]
    print(c, f"d4_end {o['d4_end_m']:.2e} rel {o['rel_dist']:.1e} E_end {o['E_end_diff_J']:.1e} relE {o['rel_E']:.1e} delta_max {o['delta_event_earlier_max_s']:.1e}", "top segs:", [(b['seg'], f"{b['v0_kmh']:.0f}->{b['v1_kmh']:.0f}kmh", f"{b['t0']:.0f}-{b['t1']:.0f}s", f"{b['d4_change_m']:.2e}") for b in big], f"corr {o['corr_increment_vs_v_times_delta']}")
