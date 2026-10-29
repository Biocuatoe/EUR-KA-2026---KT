"""Spread of battery stress indicators (Ah throughput, RMS and peak current) across controllers F, S, F01.

Reads ../runs/R1_*/metrics.csv only; writes stress_spread.csv and prints the maxima. No fade model is applied.
"""

import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
R1 = HERE.parent
rows = []
for tag in ("R1_S1", "R1_S2", "R1_UDDS", "R1_US06"):
    with (R1 / "runs" / tag / "metrics.csv").open(encoding="utf-8") as f:
        rows += list(csv.DictReader(f))
g: dict[tuple, list[dict]] = {}
for r in rows:
    g.setdefault((r["cycle"], r["case"], r["soh"]), []).append(r)
out = []
for (cyc, case, soh), rs in g.items():
    d = {"cycle": cyc, "case": case, "soh": soh}
    for k in ("Ah", "rms_current_A", "peak_current_A"):
        v = [float(r[k]) for r in rs]
        d[f"{k}_spread_pct"] = 100 * (max(v) - min(v)) / v[[r["controller"] for r in rs].index("F")]
    d["tracking_failure_any"] = any(r["tracking_failure"] == "True" for r in rs)
    out.append(d)
with (HERE / "stress_spread.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)
for k in ("Ah_spread_pct", "rms_current_A_spread_pct", "peak_current_A_spread_pct"):
    for label, sel in (("all", out), ("complete+tracking-ok", [o for o in out if not o["tracking_failure_any"]])):
        m = max(sel, key=lambda o: o[k])
        print(f"{k:28s} {label:22s} max {m[k]:.3f} %  at {m['cycle']}/{m['case']}/SoH {m['soh']}  (n={len(sel)})")
