"""Re-derive the R1, R2 and R3-B SoH-scheduling headline ranges from their retained result tables
(R4 preflight, Phase 0). Arithmetic on saved outputs only; no simulation.

  R1:   results/pairs.csv, pair == "S vs F": range of dE_pct over all rows, and count
  R2:   research_recovery_20261025/pilot/out/analysis/contrasts.csv: held-out scheduling contrasts
  R3-B: R3_20261025/outputs/pilot_B/<M>/eval_runs.csv: S0-F0 and S1-F1 in Wh per reference km,
        held-out cycles, complete runs, paired on (cycle, scen)

    python -I recheck_soh_headlines.py <scientific_rebuild dir>
"""
import csv
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")


def rows(p):
    with open(p, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main():
    sr = Path(sys.argv[1])
    r1 = [float(r["dE_pct"]) for r in rows(sr / "results" / "pairs.csv") if r["pair"] == "S vs F"]
    print(f"R1 S vs F: n={len(r1)} dE% min={min(r1):.4f} max={max(r1):.4f}")

    c = rows(sr / "research_recovery_20261025" / "pilot" / "out" / "analysis" / "contrasts.csv")
    sch = [r for r in c if r["held_out"] == "True" and r["contrast"] in ("S0_vs_F0", "S1_vs_F1")]
    v = [abs(float(r["dE_pct_ref_km"])) for r in sch]
    print(f"R2 held-out scheduling contrasts: n={len(v)} max|dE%|={max(v):.4f} verdicts={sorted(set(r['verdict'] for r in sch))}")

    for m in ("M0", "M1", "M2"):
        ev = rows(sr / "research_recovery_20261025" / "R3_20261025" / "outputs" / "pilot_B" / m / "eval_runs.csv")
        ev = [r for r in ev if r["cycle"] in ("S2", "UDDS") and r["dt_s"] == "0.001"]
        key = {(r["branch"], r["cycle"], r["scen"]): r for r in ev}
        out = []
        for (b, cyc, sc), r in key.items():
            if b not in ("S0", "S1"):
                continue
            f = key.get(("F" + b[1], cyc, sc))
            if f is None:
                continue
            complete = float(r["shortfall_pct"]) <= 1.0 and float(f["shortfall_pct"]) <= 1.0
            d = 100 * (float(r["Wh_per_ref_km"]) - float(f["Wh_per_ref_km"])) / float(f["Wh_per_ref_km"])
            out.append((cyc, sc, b, complete, d))
        comp = [d for *_, ok, d in out if ok]
        inc = [d for *_, ok, d in out if not ok]
        print(f"R3-B {m}: complete held-out S-F n={len(comp)} range [{min(comp):+.4f}, {max(comp):+.4f}] %; "
              f"incomplete n={len(inc)} range [{min(inc):+.3f}, {max(inc):+.3f}] %")


if __name__ == "__main__":
    main()
