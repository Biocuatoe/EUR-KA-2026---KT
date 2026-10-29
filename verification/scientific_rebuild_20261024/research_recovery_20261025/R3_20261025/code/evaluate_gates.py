"""Apply the frozen gate rules (R3_protocol_v1.md section 4) to the raw gate outputs.

    python -I evaluate_gates.py      -> ../outputs/gates/gate_decisions.json, ../outputs/gates/summary_*.csv

Reads only outputs/gates/*.csv written by run_gates.py; never edits them.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

G = Path(__file__).resolve().parent.parent / "outputs" / "gates"
HELD = {"S2", "UDDS"}
QUAL_LIMS = {"L-R1", "L-EVE"}
THR = 1.0


if len(sys.argv) > 1:                      # e.g. ../outputs/gates_a1 (amendment 1; band and VSI only)
    G = Path(sys.argv[1]).resolve()


def rd(name):
    if not (G / name).exists():
        return []
    with (G / name).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def qualifies(r, base_lookup=None):
    if r["cycle"] not in HELD or r["limits"] not in QUAL_LIMS or r.get("status") != "ok":
        return False
    if base_lookup is not None:
        b = base_lookup.get((r["cycle"], r["motor"], r["limits"], r["pstate"]))
        if b is None or b["hit"] or b["short"] > 1.0:
            return False
    return True


def classify(rows, found, mx):
    """PASS if any found >= 1 %; FAIL-certified-on-grid if every max < 1 %; else INDETERMINATE."""
    if not rows:
        return "NO QUALIFYING SCENARIO", None, None
    f = [fnum(r[found]) for r in rows]
    m = [fnum(r[mx]) if mx else None for r in rows]
    best_f = max(x for x in f if x is not None)
    if best_f >= THR:
        return "PASS", best_f, max((x for x in m if x is not None), default=None)
    if mx and all(x is not None and x < THR for x in m):
        return "FAIL-certified-on-grid", best_f, max(m)
    return "INDETERMINATE", best_f, max((x for x in m if x is not None), default=None)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    band, vsi, eco, evsi = rd("band_rows.csv"), rd("vsi_rows.csv"), rd("eco_rows.csv"), rd("eco_vsi_rows.csv")
    base = {}
    for r in band:
        if r.get("track_W"):
            base[(r["cycle"], r["motor"], r["limits"], r["pstate"])] = dict(
                hit=r.get("track_hit_boundary") == "True", short=fnum(r.get("base_shortfall_pct")) or 0.0)
    out = {"inputs": {n: hashlib.sha256((G / n).read_bytes()).hexdigest() for n in
                      ("band_rows.csv", "vsi_rows.csv", "eco_rows.csv", "eco_vsi_rows.csv", "conv_rows.csv")
                      if (G / n).exists()},
           "gates": {}, "robustness_triggers": []}
    for m in ("M0", "M1", "M2"):
        gb = [r for r in band if r["motor"] == m and fnum(r["delta"]) == 0.25 and qualifies(r, base)]
        ga = [r for r in vsi if r["motor"] == m and qualifies(r, base)]
        gc = [r for r in eco if r["motor"] == m and fnum(r["allowance"]) in (0.0, 0.05) and qualifies(r, base)]
        res = {}
        for gate, rows, fk, mk in (("G-A", ga, "VSI_found_pct", "VSI_max_pct"), ("G-B", gb, "H_found_pct", "H_max_pct"),
                                   ("G-C", gc, "S_found_pct", "S_max_pct")):
            cls, bf, bm = classify(rows, fk, mk)
            res[gate] = dict(decision=cls, n_qualifying=len(rows), best_found_pct=bf, best_max_pct=bm)
            if bf is not None and 0.5 <= bf <= 2.0:
                top = max(rows, key=lambda r: fnum(r[fk]))
                out["robustness_triggers"].append(dict(motor=m, gate=gate, **{k: top[k] for k in
                                                       ("cycle", "limits", "pstate")}, found=bf))
        # H-C falsification: S_max(0.05) < 1 % on every qualifying held-out scenario
        hc = [r for r in eco if r["motor"] == m and fnum(r["allowance"]) == 0.05 and qualifies(r, base)]
        res["H-C S_max(5%) all < 1 %"] = bool(hc) and all(fnum(r["S_max_pct"]) < THR for r in hc)
        out["gates"][m] = res
    (G / "gate_decisions.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out["gates"], indent=1))
    print("robustness triggers:", out["robustness_triggers"])


if __name__ == "__main__":
    main()
