"""Recompute the R3-C quantities reported in R3_gate_results.md section 5 and R3_pilot_results.md section 2
from the retained raw rows (R4 preflight, Phase 1). Arithmetic on saved outputs only; no simulation.

  QS (gate) rows:   S_found = 100 (1 - E_eco / E_b), from outputs/gates/eco_rows.csv
  dynamic (pilot):  dE = 100 (E_eco - E_base) / E_base in Wh per reference km, from outputs/pilot_C/<M>/runs.csv,
                    paired by (cycle, limits, dt) with the baseline-profile run

    python -I recompute_r3c.py <R3 dir> <out_qs.csv> <out_dyn.csv>
"""
import csv
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return float("nan")


def main():
    r3, out_qs, out_dyn = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
    qs = []
    with open(r3 / "outputs" / "gates" / "eco_rows.csv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            s = 100 * (1 - f(r["E_eco_Wh"]) / f(r["E_b_Wh"])) if r["status"] == "ok" else float("nan")
            qs.append({"cycle": r["cycle"], "motor": r["motor"], "limits": r["limits"], "pstate": r["pstate"],
                       "allowance": r["allowance"], "status": r["status"], "S_found_pct_recorded": r["S_found_pct"],
                       "S_found_pct_recomputed": s, "abs_diff_pp": abs(s - f(r["S_found_pct"])),
                       "base_shortfall_pct": r["base_shortfall_pct"], "T_ref_s": r["T_ref_s"], "T_eco_s": r["T_eco_s"],
                       "time_change_pct": r["time_change_pct"], "eco_fric_Wh": r["eco_fric_Wh"], "base_fric_Wh": r["base_fric_Wh"],
                       "rms_dev_vs_ref_ms": r["rms_dev_vs_ref_ms"]})
    dyn = []
    for mdir in sorted((r3 / "outputs" / "pilot_C").glob("M*")):
        with open(mdir / "runs.csv", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        base = {(r["cycle"], r["limits"], r["dt_s"]): r for r in rows if r["profile"] == "baseline"}
        for r in rows:
            b = base.get((r["cycle"], r["limits"], r["dt_s"]))
            ok = r["status"] == "ok" and b is not None
            d = 100 * (f(r["Wh_per_ref_km"]) - f(b["Wh_per_ref_km"])) / f(b["Wh_per_ref_km"]) if ok and r is not b else float("nan")
            dyn.append({"motor": mdir.name, "cycle": r["cycle"], "limits": r["limits"], "profile": r["profile"], "dt_s": r["dt_s"],
                        "status": r["status"], "valid": r["valid"], "complete": r["complete"], "tracking_ok": r["tracking_ok"],
                        "shortfall_pct": r["shortfall_pct"], "rmse_ms": r["rmse_ms"], "trip_time_s": r["trip_time_s"],
                        "Wh_per_ref_km": r["Wh_per_ref_km"], "Wh_per_km_actual": r["Wh_per_km"],
                        "baseline_Wh_per_ref_km": b["Wh_per_ref_km"] if b else "",
                        "baseline_complete": b["complete"] if b else "", "baseline_shortfall_pct": b["shortfall_pct"] if b else "",
                        "dE_pct_vs_baseline_recomputed": d, "DP_saving_pct_recorded": r["DP_saving_pct"],
                        "QS_vs_dyn_pct": r["QS_vs_dyn_pct"], "friction_brake_Wh": r["friction_brake_Wh"],
                        "I_over_As": r["I_over_As"], "Ah": r["Ah"], "I2_A2s": r["I2_A2s"], "recompute_rel": r["recompute_rel"]})
    for path, rows in ((out_qs, qs), (out_dyn, dyn)):
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    print("QS rows", len(qs), "max |recomputed - recorded| pp:",
          max(r["abs_diff_pp"] for r in qs if r["status"] == "ok"))
    print("motor cycle limits profile dt | dE% | DP% | t_s | rmse | complete | base_complete base_short | QSvsDyn")
    for r in dyn:
        if r["profile"] != "baseline":
            print(r["motor"], r["cycle"], r["limits"], r["profile"], r["dt_s"], "|", round(r["dE_pct_vs_baseline_recomputed"], 3),
                  "|", r["DP_saving_pct_recorded"][:6], "|", r["trip_time_s"][:7], "|", r["rmse_ms"][:6], "|", r["complete"],
                  "|", r["baseline_complete"], r["baseline_shortfall_pct"][:5], "|", r["QS_vs_dyn_pct"][:6])
        else:
            print(r["motor"], r["cycle"], r["limits"], "baseline", r["dt_s"], "| complete", r["complete"], "short",
                  r["shortfall_pct"][:6], "| status", r["status"], "| QSvsDyn", r["QS_vs_dyn_pct"][:6])


if __name__ == "__main__":
    main()
