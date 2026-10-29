"""Integrity audit, evidence-class tables and mechanism attribution for R1 (read-only on runs/).

Writes results/analysis_*.csv and results/analysis_tables.md. Every number comes from
runs/*/metrics.csv, runs/*/series.npz or runs/*/manifest.json. A batch is used only if its
manifest says 'completed'; anything else is reported as pending/failed.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from eureka import REPO_DIR
from eureka.controllers import gain
from eureka.params import load_params
from rebuild.analyze import read, write
from rebuild.model import IX
from rebuild.run import CFG, HERE

CLASSES = {"A": ["B0"], "B": ["BV", "BV-k2", "BCN"], "C": ["BCS", "BCS-k2", "BCS2"]}
CLASS_LABEL = {
    "A": "legacy plant, battery window disabled",
    "B": "battery window whose limits do not shrink with SoH (voltage window; fixed current limits)",
    "C": "EXPLORATORY: current limits proportional to SoH (assumed BMS law, no empirical source)",
}


def planned():
    grid = {f"R1_{c}": len(CFG["cases"]) * len(CFG["soh"]) * len(CFG["controllers"]) for c in CFG["cycles"]}
    cc = CFG["convergence"]
    conv = {f"CONV_{c}_dt{dt * 1e3:g}ms": len(cc["controllers"]) for c in cc["cycles"] for dt in cc["dt"]}
    return grid, conv


def audit():
    grid, conv = planned()
    rows, ok_batches = [], []
    base = load_params()
    for tag, n_plan in {**grid, **conv}.items():
        d = HERE / "runs" / tag
        row = {"batch": tag, "planned_runs": n_plan, "status": "missing", "completed_runs": 0, "invalid_runs": 0,
               "duplicate_ids": 0, "metrics_rows": 0, "series_columns": 0, "hash_mismatches": "",
               "gain_mismatches": 0, "energy_recompute_max_rel": "", "usable": False}
        if d.exists():
            man = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
            row["status"] = man["status"]
            row["runtime_s"] = man.get("runtime_s")
            if man["status"] == "completed":
                ids = [r["run_id"] for r in man["runs"]]
                row["completed_runs"] = len(ids)
                row["duplicate_ids"] = len(ids) - len(set(ids))
                row["invalid_runs"] = man.get("n_invalid")
                met = read(d / "metrics.csv")
                row["metrics_rows"] = len(met)
                with np.load(d / "series.npz") as z:
                    y_end = z["y_end"]
                    row["series_columns"] = int(z["v"].shape[1])
                mism = [f for f, h in man["file_sha256"].items() if not (REPO_DIR / f).exists()
                        or hashlib.sha256((REPO_DIR / f).read_bytes()).hexdigest() != h]
                row["hash_mismatches"] = ";".join(mism)
                gm = 0
                for r in man["runs"]:
                    p = base.with_overrides(k_r0=r["k_r0"])
                    cc = CFG["controllers"][r["controller"]]
                    K = (gain(p, "fixed", r_scale=cc["r_scale"]) if cc["kind"] == "fixed"
                         else gain(p, "scheduled", soh=r["soh"], gamma_v=cc["gamma_v"], gamma_u=cc["gamma_u"]))
                    gm += int(not np.array_equal(K.ravel(), np.array(r["gains"])))
                row["gain_mismatches"] = gm
                rel = [abs(((y_end[j, IX["E_chem"]]) / 3600.0) - m["E_net_Wh"]) / abs(m["E_net_Wh"])
                       for j, m in enumerate(met)]
                row["energy_recompute_max_rel"] = float(max(rel))
                row["usable"] = (len(ids) == n_plan == len(met) == row["series_columns"] and not row["duplicate_ids"]
                                 and not mism and gm == 0 and [m["run_id"] for m in met] == ids)
                if row["usable"]:
                    ok_batches.append(tag)
        rows.append(row)
    write("analysis_run_accounting.csv", rows)
    return rows, ok_batches


def class_tables(runs):
    key = {(r["cycle"], r["case"], r["soh"], r["controller"]): r for r in runs}
    out = []
    for cls, cases in CLASSES.items():
        for c in CFG["cycles"]:
            for cs in cases:
                for soh in CFG["soh"]:
                    if not all((c, cs, soh, k) in key for k in ("F", "S")):
                        continue
                    f, s = key[(c, cs, soh, "F")], key[(c, cs, soh, "S")]
                    dEk = s["Wh_per_km"] - f["Wh_per_km"]
                    out.append({
                        "class": cls, "cycle": c, "case": cs, "soh": soh,
                        "E_F_Wh_km": f["Wh_per_km"], "E_S_Wh_km": s["Wh_per_km"], "dE_Wh_km": dEk,
                        "dE_pct_of_F": 100 * dEk / f["Wh_per_km"],
                        "Enet_F_Wh": f["E_net_Wh"], "Enet_S_Wh": s["E_net_Wh"], "dEnet_Wh": s["E_net_Wh"] - f["E_net_Wh"],
                        "dE_ref_km_pct_of_F": 100 * (s["Wh_per_ref_km"] - f["Wh_per_ref_km"]) / f["Wh_per_ref_km"],
                        "rmse_F": f["rmse_ms"], "rmse_S": s["rmse_ms"], "d_rmse": s["rmse_ms"] - f["rmse_ms"],
                        "rmse_ratio_S_over_F": s["rmse_ms"] / f["rmse_ms"],
                        "maxerr_F": f["max_abs_err_ms"], "maxerr_S": s["max_abs_err_ms"],
                        "shortfall_F_pct": f["shortfall_pct"], "shortfall_S_pct": s["shortfall_pct"],
                        "sat_F": f["sat_frac"], "sat_S": s["sat_frac"], "sat_batt_F": f["sat_batt_frac"], "sat_batt_S": s["sat_batt_frac"],
                        "fb_F_Wh": f["friction_brake_Wh"], "fb_S_Wh": s["friction_brake_Wh"],
                        "Iover_F_As": f["I_over_As"], "Iover_S_As": s["I_over_As"],
                        "peakI_F": f["peak_current_A"], "peakI_S": s["peak_current_A"],
                        "vtmin_F": f["vt_min_V"], "vtmin_S": s["vt_min_V"],
                        "fail_F": f["tracking_failure"], "fail_S": s["tracking_failure"],
                        "valid_both": f["valid"] and s["valid"],
                    })
    write("analysis_class_pairs.csv", out)
    return out


def mechanism(runs):
    """Matched contrasts that isolate each pathway, for controller F and for the S-F difference."""
    key = {(r["cycle"], r["case"], r["soh"], r["controller"]): r for r in runs}
    rows = []
    contrasts = [
        ("SoH via R0/R1 losses only (B0: SoH 0.7 vs 1.0)", ("B0", 0.7), ("B0", 1.0)),
        ("voltage window (BV vs B0, SoH 0.7)", ("BV", 0.7), ("B0", 0.7)),
        ("extra resistance growth k_r0 2.0 vs 0.5 (BV-k2 vs BV, SoH 0.7)", ("BV-k2", 0.7), ("BV", 0.7)),
        ("fixed current limits (BCN vs BV, SoH 0.7)", ("BCN", 0.7), ("BV", 0.7)),
        ("SoH scaling of current limits (BCS vs BCN, SoH 0.7)", ("BCS", 0.7), ("BCN", 0.7)),
        ("stricter C-rates (BCS2 vs BCS, SoH 0.7)", ("BCS2", 0.7), ("BCS", 0.7)),
        ("ageing with SoH-scaled limits (BCS: SoH 0.7 vs 1.0)", ("BCS", 0.7), ("BCS", 1.0)),
    ]
    for c in CFG["cycles"]:
        for name, (ca, sa), (cb, sb) in contrasts:
            if not all((c, x, y, "F") in key for x, y in ((ca, sa), (cb, sb))):
                continue
            a, b = key[(c, ca, sa, "F")], key[(c, cb, sb, "F")]
            rows.append({"cycle": c, "contrast": name, "controller": "F",
                         "dE_Wh_km": a["Wh_per_km"] - b["Wh_per_km"], "dE_pct": 100 * (a["Wh_per_km"] / b["Wh_per_km"] - 1),
                         "d_rmse": a["rmse_ms"] - b["rmse_ms"], "d_rmse_pct": 100 * (a["rmse_ms"] / b["rmse_ms"] - 1),
                         "d_fb_Wh": a["friction_brake_Wh"] - b["friction_brake_Wh"],
                         "d_Eneg_Wh": a["E_neg_Wh"] - b["E_neg_Wh"], "d_Epos_Wh": a["E_pos_Wh"] - b["E_pos_Wh"],
                         "d_resistive_Wh": a["resistive_loss_Wh"] - b["resistive_loss_Wh"],
                         "d_sat_batt": a["sat_batt_frac"] - b["sat_batt_frac"],
                         "d_shortfall_pp": a["shortfall_pct"] - b["shortfall_pct"]})
        for cs in CFG["cases"]:
            if all((c, cs, s, k) in key for s in (0.7, 1.0) for k in ("F", "S")):
                f, s = key[(c, cs, 0.7, "F")], key[(c, cs, 0.7, "S")]
                rows.append({"cycle": c, "contrast": f"gain scheduling (S vs F, {cs}, SoH 0.7)", "controller": "S-F",
                             "dE_Wh_km": s["Wh_per_km"] - f["Wh_per_km"], "dE_pct": 100 * (s["Wh_per_km"] / f["Wh_per_km"] - 1),
                             "d_rmse": s["rmse_ms"] - f["rmse_ms"], "d_rmse_pct": 100 * (s["rmse_ms"] / f["rmse_ms"] - 1),
                             "d_fb_Wh": s["friction_brake_Wh"] - f["friction_brake_Wh"],
                             "d_Eneg_Wh": s["E_neg_Wh"] - f["E_neg_Wh"], "d_Epos_Wh": s["E_pos_Wh"] - f["E_pos_Wh"],
                             "d_resistive_Wh": s["resistive_loss_Wh"] - f["resistive_loss_Wh"],
                             "d_sat_batt": s["sat_batt_frac"] - f["sat_batt_frac"],
                             "d_shortfall_pp": s["shortfall_pct"] - f["shortfall_pct"]})
            if all((c, cs, 0.7, k) in key for k in ("F", "F01")):
                f, g = key[(c, cs, 0.7, "F")], key[(c, cs, 0.7, "F01")]
                rows.append({"cycle": c, "contrast": f"tuning (F01 vs F, {cs}, SoH 0.7)", "controller": "F01-F",
                             "dE_Wh_km": g["Wh_per_km"] - f["Wh_per_km"], "dE_pct": 100 * (g["Wh_per_km"] / f["Wh_per_km"] - 1),
                             "d_rmse": g["rmse_ms"] - f["rmse_ms"], "d_rmse_pct": 100 * (g["rmse_ms"] / f["rmse_ms"] - 1),
                             "d_fb_Wh": g["friction_brake_Wh"] - f["friction_brake_Wh"],
                             "d_Eneg_Wh": g["E_neg_Wh"] - f["E_neg_Wh"], "d_Epos_Wh": g["E_pos_Wh"] - f["E_pos_Wh"],
                             "d_resistive_Wh": g["resistive_loss_Wh"] - f["resistive_loss_Wh"],
                             "d_sat_batt": g["sat_batt_frac"] - f["sat_batt_frac"],
                             "d_shortfall_pp": g["shortfall_pct"] - f["shortfall_pct"]})
    write("analysis_mechanism.csv", rows)
    return rows


def md_table(rows, cols, fmt=".4g"):
    def f(v):
        return f"{v:{fmt}}" if isinstance(v, float) else str(v)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(f(r[c]) for c in cols) + " |" for r in rows]
    return "\n".join(lines)


def main():
    acc, ok = audit()
    runs = [r for tag in ok if tag.startswith("R1_") for r in read(HERE / "runs" / tag / "metrics.csv")]
    pairs = class_tables(runs) if runs else []
    mech = mechanism(runs) if runs else []
    out = ["# Generated tables (rebuild.report_tables)", "", "## Run accounting", "",
           md_table(acc, ["batch", "planned_runs", "status", "completed_runs", "invalid_runs", "duplicate_ids",
                          "metrics_rows", "series_columns", "gain_mismatches", "energy_recompute_max_rel", "usable"])]
    for cls in CLASSES:
        sub = [p for p in pairs if p["class"] == cls]
        if sub:
            out += ["", f"## Class {cls}: {CLASS_LABEL[cls]} (S vs F; denominators = F)", "",
                    md_table(sub, ["cycle", "case", "soh", "E_F_Wh_km", "E_S_Wh_km", "dE_Wh_km", "dE_pct_of_F",
                                   "dEnet_Wh", "rmse_F", "rmse_S", "rmse_ratio_S_over_F", "shortfall_F_pct", "shortfall_S_pct",
                                   "sat_batt_F", "sat_batt_S", "fb_F_Wh", "fb_S_Wh", "Iover_F_As", "Iover_S_As"])]
    if mech:
        out += ["", "## Mechanism contrasts (controller F unless stated)", "",
                md_table(mech, ["cycle", "contrast", "dE_Wh_km", "dE_pct", "d_rmse", "d_rmse_pct", "d_fb_Wh",
                                "d_Eneg_Wh", "d_resistive_Wh", "d_sat_batt", "d_shortfall_pp"])]
    (HERE / "results" / "analysis_tables.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("usable batches:", ok)


if __name__ == "__main__":
    main()
