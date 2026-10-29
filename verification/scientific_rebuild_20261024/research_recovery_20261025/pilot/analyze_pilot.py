"""Apply pilot_protocol.md section 6 to out/eval/runs.csv (+ out/conv). Writes out/analysis/*.csv and
out/analysis/pilot_tables.md. Read-only on the run outputs."""

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
AN = OUT / "analysis"
AN.mkdir(exist_ok=True)
R1 = HERE.parents[1]


def rd(p):
    with p.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fl(r, k):
    return float(r[k])


runs = rd(OUT / "eval" / "runs.csv")
key = {(r["cycle"], r["scen"], r["branch"]): r for r in runs}
CYC, SCN, BR = ("S1", "S2", "UDDS"), ("E1", "E2", "E2b", "E3", "E4"), ("F0", "S0", "F1", "S1")
held = {"S2", "UDDS"}


def dE(a, b):  # per reference km, protocol section 6
    return 100 * (fl(a, "Wh_per_ref_km") - fl(b, "Wh_per_ref_km")) / fl(b, "Wh_per_ref_km")


def complete(*rs):
    return all(fl(r, "shortfall_pct") <= 1.0 for r in rs)


def verdict(a, b):
    d, ratio = dE(a, b), fl(a, "rmse_ms") / fl(b, "rmse_ms")
    if d <= -1:
        v = "IMPROVES" if ratio <= 1.10 else "TRADE-OFF"
    elif d >= 1:
        v = "WORSE"
    else:
        v = "NO PRACTICAL DIFFERENCE"
    return v + ("" if complete(a, b) else " / INCOMPLETE-CYCLE")


rows, pairs = [], []
for c in CYC:
    for s in SCN:
        g = {b: key[(c, s, b)] for b in BR}
        for b in BR:
            r = g[b]
            rows.append({"cycle": c, "scen": s, "branch": b, "held_out": c in held,
                         **{k: r[k] for k in ("Wh_per_ref_km", "Wh_per_km", "shortfall_pct", "rmse_ms", "max_abs_err_ms",
                                              "max_overshoot_ms", "batt_limited_frac", "governor_active_frac",
                                              "friction_brake_Wh", "regen_terminal_Wh", "I_over_As", "Ah", "peak_current_A",
                                              "closure_rel", "valid")}})
        for name, a, b in (("S0_vs_F0", "S0", "F0"), ("S1_vs_F1", "S1", "F1"), ("F1_vs_F0", "F1", "F0"), ("S1_vs_S0", "S1", "S0")):
            A, B = g[a], g[b]
            pairs.append({"cycle": c, "scen": s, "held_out": c in held, "contrast": name, "dE_pct_ref_km": dE(A, B),
                          "rmse_ratio": fl(A, "rmse_ms") / fl(B, "rmse_ms"),
                          "max_err_ratio": fl(A, "max_abs_err_ms") / fl(B, "max_abs_err_ms"),
                          "d_overshoot_ms": fl(A, "max_overshoot_ms") - fl(B, "max_overshoot_ms"),
                          "d_shortfall_pp": fl(A, "shortfall_pct") - fl(B, "shortfall_pct"),
                          "both_complete": complete(A, B), "batt_limited_frac_b": fl(B, "batt_limited_frac"),
                          "verdict": verdict(A, B)})
        pairs.append({"cycle": c, "scen": s, "held_out": c in held, "contrast": "interaction (S1-F1)-(S0-F0)",
                      "dE_pct_ref_km": dE(g["S1"], g["F1"]) - dE(g["S0"], g["F0"]),
                      "rmse_ratio": (fl(g["S1"], "rmse_ms") - fl(g["F1"], "rmse_ms")) - (fl(g["S0"], "rmse_ms") - fl(g["F0"], "rmse_ms")),
                      "both_complete": complete(*g.values()), "verdict": "interaction in pp (dE) and m/s (rmse_ratio column = RMSE difference of differences)"})


def write(p, rr):
    keys = []
    for r in rr:
        keys += [k for k in r if k not in keys]
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rr)


write(AN / "branch_runs.csv", rows)
write(AN / "contrasts.csv", pairs)

# predictions P1-P5 (held-out conditions)
H = [p for p in pairs if p["held_out"]]
p1_fals = [p for p in H if p["contrast"] == "S1_vs_F1" and p["verdict"].startswith("IMPROVES") and p["both_complete"]]
p2_fals = [p for p in H if p["contrast"] in ("F1_vs_F0", "S1_vs_S0") and p["both_complete"] and abs(p["dE_pct_ref_km"]) >= 1]
p3_cand = [p for p in H if p["contrast"] in ("F1_vs_F0", "S1_vs_S0") and p["batt_limited_frac_b"] > 0.01]
p3_fals = [p for p in p3_cand if p["max_err_ratio"] > 1.10]
p4_fals = [p for p in H if p["contrast"].startswith("interaction") and abs(p["dE_pct_ref_km"]) >= 0.5]
p5_fals = [p for p in H if not p["contrast"].startswith("interaction") and p["both_complete"] and abs(p["dE_pct_ref_km"]) >= 1]
pred = {
    "P1 S1 vs F1 no practical difference (held-out)": {"falsified": bool(p1_fals), "n_falsifying": len(p1_fals)},
    "P2 layer changes energy < 1 % (complete, held-out)": {"falsified": bool(p2_fals), "n_falsifying": len(p2_fals)},
    "P3 layer does not raise max|e| > 10 % where battery-limited > 1 %": {"falsified": bool(p3_fals), "n_tested": len(p3_cand),
                                                                           "n_falsifying": len(p3_fals)},
    "P4 |interaction| < 0.5 pp": {"falsified": bool(p4_fals), "n_falsifying": len(p4_fals)},
    "P5 all branch differences < 1 % on complete runs": {"falsified": bool(p5_fals), "n_falsifying": len(p5_fals)},
}
san = [r for r in runs if r["branch"] == "SANITY_R1_F"][0]
r1 = next(r for r in rd(R1 / "runs" / "R1_S2" / "metrics.csv") if r["run_id"] == "R1_S2-BCN-soh1.00-F")
sanity = {"R1_reproduction_rel_diff_Wh_km": abs(fl(san, "Wh_per_km") - fl(r1, "Wh_per_km")) / fl(r1, "Wh_per_km"),
          "sched_equals_fixed_at_soh1_maxabs": json.loads((OUT / "eval" / "manifest.json").read_text())["sched_equals_fixed_at_soh1_maxabs"],
          "n_invalid": sum(r["valid"] != "True" for r in runs), "max_closure_rel": max(fl(r, "closure_rel") for r in runs)}

conv = {}
cp = OUT / "conv" / "runs_dt0.5ms.csv"
if cp.exists():
    c05 = {r["branch"]: r for r in rd(cp)}
    c10 = {b: key[("UDDS", "E3", b)] for b in BR}
    for name, a, b in (("S0_vs_F0", "S0", "F0"), ("S1_vs_F1", "S1", "F1"), ("F1_vs_F0", "F1", "F0"), ("S1_vs_S0", "S1", "S0")):
        d1, d05 = dE(c10[a], c10[b]), dE(c05[a], c05[b])
        conv[name] = {"dE_1ms": d1, "dE_0.5ms": d05, "change_pp": d05 - d1, "pass": abs(d05 - d1) < 0.01}
(AN / "decisions.json").write_text(json.dumps({"predictions": pred, "sanity": sanity, "convergence": conv}, indent=1), encoding="utf-8")

# markdown tables
L = ["# Pilot tables (generated by analyze_pilot.py)\n", "## Branch results\n",
     "| Cycle | Scen | Branch | Wh/ref-km | Wh/km | Shortfall % | RMSE m/s | max\\|e\\| m/s | max overshoot m/s | batt-limited % | gov active % | friction Wh | regen Wh | I_over A·s |",
     "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    L.append(f"| {r['cycle']}{'' if r['held_out'] else ' (in-sample)'} | {r['scen']} | {r['branch']} | {fl(r,'Wh_per_ref_km'):.3f} | {fl(r,'Wh_per_km'):.3f} | "
             f"{fl(r,'shortfall_pct'):.3f} | {fl(r,'rmse_ms'):.4f} | {fl(r,'max_abs_err_ms'):.3f} | {fl(r,'max_overshoot_ms'):.3f} | "
             f"{100*fl(r,'batt_limited_frac'):.2f} | {100*fl(r,'governor_active_frac'):.2f} | {fl(r,'friction_brake_Wh'):.2f} | {fl(r,'regen_terminal_Wh'):.2f} | {fl(r,'I_over_As'):.2f} |")
L += ["\n## Contrasts (ΔE per reference km, a vs b)\n", "| Cycle | Scen | Contrast | ΔE % | RMSE ratio | max\\|e\\| ratio | Δ overshoot m/s | complete | verdict |",
      "|---|---|---|---|---|---|---|---|---|"]
for p in pairs:
    if p["contrast"].startswith("interaction"):
        L.append(f"| {p['cycle']} | {p['scen']} | interaction | {p['dE_pct_ref_km']:+.4f} pp | ΔRMSE {p['rmse_ratio']:+.5f} m/s | | | {p['both_complete']} | |")
    else:
        L.append(f"| {p['cycle']} | {p['scen']} | {p['contrast']} | {p['dE_pct_ref_km']:+.4f} | {p['rmse_ratio']:.3f} | {p['max_err_ratio']:.3f} | "
                 f"{p['d_overshoot_ms']:+.3f} | {p['both_complete']} | {p['verdict']} |")
L += ["\n## Decisions\n", "```json", json.dumps({"predictions": pred, "sanity": sanity, "convergence": conv}, indent=1), "```"]
(AN / "pilot_tables.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print(json.dumps({"predictions": pred, "sanity": sanity, "convergence": conv}, indent=1))
