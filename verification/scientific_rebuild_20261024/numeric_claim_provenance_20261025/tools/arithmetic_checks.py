"""Arithmetic checks on numbers as printed in the thesis, in its figures and in Tawfik et al. 2024.

    python -I tools/arithmetic_checks.py   -> outputs/arithmetic_checks.csv

No model is run and no parameter is chosen. Each row recomputes a ratio from printed inputs, or
asks what input a printed claim would have required. "para" refers to outputs/thesis_paragraphs.tsv;
"fig11"/"fig9" values come from outputs/figure_geometry_summary.json (figure geometry, not data).
Tawfik values are from the open-access full text (Table 5, p. 13; SHA-256 of the PDF in the report).
"""

import csv
import json
from math import sqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "outputs"


def main():
    geo = json.loads((OUT / "figure_geometry_summary.json").read_text(encoding="utf-8"))
    f11 = geo["figure11"]["readout"]
    rows = []

    def add(cid, claim, formula, inputs, value, compare, note):
        rows.append({"check_id": cid, "claim": claim, "formula": formula, "inputs_and_sources": inputs,
                     "result": value if isinstance(value, str) else f"{value:.4g}", "compared_with": compare,
                     "note": note})

    # --- energy -------------------------------------------------------------------------------
    add("E1", "12.5 % energy (abstract, para 5)", "(95 - 85.3) / 95 * 100",
        "95 Wh/km fixed LQR (para 5973, 7181); 85.3 Wh/km adaptive (para 5975, 7183; Tables 16/18/36 mean)",
        (95 - 85.3) / 95 * 100, "12.5 % (abstract); '9.7 %' (para 5977, 7185)",
        "The only fixed-vs-adaptive energy pair printed in the thesis gives 10.2 %; '9.7 %' is the Wh/km difference relabelled as a percentage")
    add("E2", "12.5 % energy", "85.3 / (1 - 0.125)", "85.3 Wh/km adaptive", 85.3 / 0.875,
        "no fixed-LQR value of 97.5 Wh/km appears anywhere in the thesis",
        "Baseline that 12.5 % would need if 85.3 Wh/km is the adaptive value")
    add("E3", "12.5 % energy", "95 * (1 - 0.125)", "95 Wh/km fixed LQR", 95 * 0.875,
        "no adaptive value of 83.1 Wh/km appears anywhere in the thesis",
        "Adaptive value that 12.5 % would need if 95 Wh/km is the baseline")
    add("E4", "± 2.1 % on the energy claim", "not computable",
        "needs per-sample paired energy for both controllers; the thesis prints only adaptive-LQR summaries (Tables 16, 18, 36: SD 4.2 Wh/km) and no fixed-LQR energy distribution",
        "not computable", "± 2.1 %", "Statistic (SD, SE, CI) not named; no independent samples exist in the project")
    add("E5", "Cohen's d = 0.89 for energy (para 7277)", "d * s_pooled, with s_pooled taken as 4.2 Wh/km",
        "d = 0.89 (para 7277); SD 4.2 Wh/km (Table 18 para 5315; Table 36) - assumption: fixed-LQR SD similar",
        0.89 * 4.2, "9.7 Wh/km difference (para 5977)",
        "Under that assumption d = 0.89 implies a ~3.7 Wh/km (~3.9 %) gap; a 9.7 Wh/km gap would give d = 2.3. Consistency check only; the fixed-LQR SD is not printed")
    add("E6", "Monte Carlo sample count", "compare printed counts",
        "abstract para 10 and Contribution 4 para 524: 100 trials per configuration; Table 11 para 4323: 100; para 4363: 6 controllers x 4 cycles x 100 = 2400; Tables 16/18 paras 5121/5296: N = 1000",
        "inconsistent", "one stated design", "N behind the ± values cannot be identified")

    # --- fade ---------------------------------------------------------------------------------
    add("F1", "15.3 % fade (abstract, para 5)", "(16.5 - 14.2) / 16.5 * 100",
        "16.5 %/1000 cycles fixed (para 5980, 7188); 14.2 %/1000 cycles adaptive (para 5982, 7190; Table 18 mean)",
        (16.5 - 14.2) / 16.5 * 100, "15.3 % (abstract); '14 %' (para 5984, 7192)",
        "The only printed fade pair gives 13.9 %, which the body rounds to 14 %, not 15.3 %")
    add("F2", "15.3 % fade", "14.2 / (1 - 0.153)", "14.2 %/1000 cycles adaptive", 14.2 / 0.847,
        "16.5 %/1000 cycles printed", "Baseline fade that 15.3 % would need: 16.77, not printed anywhere")
    r1000 = f11["fade_pp_at_1000_cycles"]
    add("F3", "15.3 % fade over 1000 cycles", "1 - fade_adaptive(1000) / fade_fixed(1000), read from Figure 11 geometry",
        f"Figure 11 curves: fixed {r1000['Fixed Controller']:.3f} pp, adaptive {r1000['Adaptive LQR']:.3f} pp at 1000 cycles",
        r1000["relative_reduction_adaptive_vs_fixed_pct"], "15.3 % (abstract); 14 % (Ch. 6)",
        f"The drawn curves give 16.7 % at 1000 cycles; 15.3 % only near {geo['figure11']['cycles_where_reduction_equals_15.3pct']:.0f} cycles")
    add("F4", "absolute fade level", "fixed-LQR fade at 1000 cycles: Figure 11 vs Chapter 6",
        f"Figure 11: {r1000['Fixed Controller']:.2f} pp; para 5980: 16.5 %/1000 cycles",
        16.5 / r1000["Fixed Controller"], "1.0 if consistent",
        "Figure 11 and Chapter 6 differ by a factor of 5.5 in absolute fade")
    add("F5", "Pareto knee 14.0 %/1000 cycles at 122 Wh/km (para 3638)", "compare with Figure 9 geometry",
        "Figure 9 front spans 1.8-4.2 %/1000 cycles over 120-175 Wh/km; y axis 1-5",
        "outside plotted range", "14.0 %/1000 cycles", "The knee value lies outside the axis of the figure it describes")
    add("F6", "fade model shape", "least-squares fit of Figure 11 curves",
        "fits in figure_geometry_summary.json: a*N + b*N^2 residual <= 2e-5 pp; a*sqrt(N) + b*N needs a < 0",
        "convex quadratic", "Eq. 4.22: f_c = alpha*sqrt(Ah) + beta*Ah with alpha, beta > 0 (concave)",
        "With constant throughput per cycle Eq. 4.22 cannot produce the drawn convex curves")
    add("F7", "± 2.8 % on the fade claim", "not computable",
        "needs per-sample fade for both controllers over 1000 cycles; Table 18 prints adaptive-only SD 1.5 %/1000 cycles",
        "not computable", "± 2.8 %", "No independent fade samples exist in the project")

    # --- literature lead ----------------------------------------------------------------------
    add("T1", "Tawfik 2024 Table 5 capacity loss", "(0.012 - 0.0101) / 0.012 * 100",
        "normal 0.012 %, optimized 0.0101 % after one daily trip (Table 5, p. 13)", (0.012 - 0.0101) / 0.012 * 100,
        "15.8 % (Tawfik)", "Internally consistent")
    add("T2", "Tawfik 2024 Table 5 energy", "(171.3 - 149.2) / 171.3 * 100",
        "171.3 vs 149.2 Wh/km (Table 5, p. 13)", (171.3 - 149.2) / 171.3 * 100, "13 % (Tawfik)",
        "Internally consistent (12.9 % rounded)")
    add("T3", "numerical proximity", "thesis value - Tawfik value",
        "12.5 vs 13 (energy); 15.3 vs 15.8 (degradation)", "-0.5 pp and -0.5 pp", "",
        "Both thesis headline numbers sit exactly 0.5 pp below Tawfik's; an observation, not evidence of transcription")

    with open(OUT / "arithmetic_checks.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(f"{r['check_id']:3s} {r['result']:>22s}  {r['claim']}")


if __name__ == "__main__":
    main()
