"""Summary tables for R3_gate_results.md from the raw gate CSVs (frozen and amendment 1). Read-only.

    python -I summarise_gates.py      -> ../outputs/gates/summary_tables.txt
"""

import csv
import sys
from pathlib import Path

R3 = Path(__file__).resolve().parent.parent
G0, G1 = R3 / "outputs" / "gates", R3 / "outputs" / "gates_a1"


def rd(p):
    with p.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def f(x, n=2):
    try:
        return f"{float(x):.{n}f}"
    except (TypeError, ValueError):
        return "—"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    out = []
    P = out.append
    b0 = {(r["cycle"], r["motor"], r["limits"], r["pstate"], r["delta"]): r for r in rd(G0 / "band_rows.csv")}
    b1 = {(r["cycle"], r["motor"], r["limits"], r["pstate"], r["delta"]): r for r in rd(G1 / "band_rows.csv")}
    P("## Baselines (P1)\n\n| Cycle | Motor | Limits | E_b Wh/ref-km | shortfall % | RMS dev. from v_ref m/s | max dev. m/s | friction Wh | qualifies |\n|---|---|---|---|---|---|---|---|---|")
    for cyc in ("S1", "S2", "UDDS"):
        for m in ("M0", "M1", "M2"):
            for lim in ("L-R1", "L-EVE"):
                r = b0[(cyc, m, lim, "P1", "0.25")]
                q = cyc != "S1" and float(r["base_shortfall_pct"]) <= 1.0 and r["track_hit_boundary"] == "False"
                P(f"| {cyc} | {m} | {lim} | {f(r['E_b_Wh_per_refkm'])} | {f(r['base_shortfall_pct'])} | {f(r['base_rmse_vs_ref'],3)} | {f(r['base_max_dev_vs_ref'])} | {f(r['base_fric_Wh'])} | {'yes' if q else ('in-sample' if cyc == 'S1' else 'no')} |")
    P("\n## Same-task band, delta = 0.25 m/s: H_found % (H_max %), frozen definition vs stop-respecting (A1.1)\n\n| Cycle | Motor | Limits | P1 frozen | P1 stop | P2 stop | P3 stop |\n|---|---|---|---|---|---|---|")
    for cyc in ("S2", "UDDS", "S1"):
        for m in ("M0", "M1", "M2"):
            for lim in ("L-R1", "L-EVE"):
                c = [b0[(cyc, m, lim, "P1", "0.25")]] + [b1[(cyc, m, lim, pk, "0.25")] for pk in ("P1", "P2", "P3")]
                P(f"| {cyc} | {m} | {lim} | " + " | ".join(f"{f(r.get('H_found_pct'))} ({f(r.get('H_max_pct'))})" for r in c) + " |")
    P("\n## Stop-respecting H_found % by band (P1, L-R1)\n\n| Cycle | Motor | 0.05 | 0.10 | 0.25 | 0.50 |\n|---|---|---|---|---|---|")
    for cyc in ("S2", "UDDS", "S1"):
        for m in ("M0", "M1", "M2"):
            P(f"| {cyc} | {m} | " + " | ".join(f(b1[(cyc, m, 'L-R1', 'P1', d)]['H_found_pct']) for d in ("0.05", "0.1", "0.25", "0.5")) + " |")
    for name, G in (("frozen", G0), ("stop-respecting", G1)):
        v = rd(G / "vsi_rows.csv")
        P(f"\n## VSI ({name}): max over scenarios, % (found / max)\n\n| Motor | held-out, L-R1/L-EVE | held-out incl. L-EVE-s (exploratory) | in-sample S1 | not computable |\n|---|---|---|---|---|")
        for m in ("M0", "M1", "M2"):
            def mx(sel, k):
                xs = [float(r[k]) for r in v if r["motor"] == m and sel(r) and r.get(k) not in (None, "")]
                return max(xs) if xs else None
            qual = lambda r: r["cycle"] in ("S2", "UDDS") and r["limits"] in ("L-R1", "L-EVE")
            allh = lambda r: r["cycle"] in ("S2", "UDDS")
            ins = lambda r: r["cycle"] == "S1"
            nc = sum(1 for r in v if r["motor"] == m and r["status"] != "ok")
            P(f"| {m} | {f(mx(qual,'VSI_found_pct'),3)} / {f(mx(qual,'VSI_max_pct'),3)} | {f(mx(allh,'VSI_found_pct'),3)} / {f(mx(allh,'VSI_max_pct'),3)} | {f(mx(ins,'VSI_found_pct'),3)} / {f(mx(ins,'VSI_max_pct'),3)} | {nc} (P1 design infeasible on aged plant) |")
    e = rd(G0 / "eco_rows.csv")
    P("\n## Eco DP (P1): S_found % [S_max %], trip-time change %, RMS deviation from v_ref m/s\n\n| Cycle | Motor | Limits | A = 0 | A = 2.5 % | A = 5 % | A = 10 % |\n|---|---|---|---|---|---|---|")
    for cyc in ("S2", "UDDS", "S1"):
        for m in ("M0", "M1", "M2"):
            for lim in ("L-R1", "L-EVE"):
                cells = []
                for A in ("0.0", "0.025", "0.05", "0.1"):
                    r = next(r for r in e if (r["cycle"], r["motor"], r["limits"], r["pstate"], r["allowance"]) == (cyc, m, lim, "P1", A))
                    cells.append("infeasible (t_min " + f(100 * (float(r['t_min_eco_s']) / float(r['T_ref_s']) - 1), 1) + " %)" if r["status"] != "ok"
                                 else f"{f(r['S_found_pct'])} [{f(r['S_max_pct'])}], {f(r['time_change_pct'],1)}, {f(r['rms_dev_vs_ref_ms'])}")
                P(f"| {cyc} | {m} | {lim} | " + " | ".join(cells) + " |")
    ev = rd(G0 / "eco_vsi_rows.csv")
    P("\n## Eco VSI at A = 0 (P3)\n")
    for r in ev:
        P(f"- {r['cycle']} {r['motor']} {r['limits']}: {r['status']}; VSI_eco_found {f(r.get('VSI_eco_found_pct'),3)} %")
    cv = rd(G0 / "conv_rows.csv")
    P("\n## Discretisation checks\n")
    for r in cv:
        P("- " + ", ".join(f"{k}={r[k]}" for k in r if r[k] not in ("", None)))
    (G0 / "summary_tables.txt").write_text("\n".join(out), encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
