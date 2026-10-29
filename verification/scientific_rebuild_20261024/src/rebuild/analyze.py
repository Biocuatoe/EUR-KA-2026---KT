"""Tables and figures for R1, computed only from runs/*/metrics.csv and runs/*/series.npz."""

from __future__ import annotations

import csv
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from eureka import REPO_DIR  # noqa: E402
from rebuild.run import CFG, HERE  # noqa: E402

RES, FIG = HERE / "results", HERE / "figures"


def read(path):
    with path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k, v in r.items():
            try:
                r[k] = float(v)
            except ValueError:
                r[k] = {"True": True, "False": False}.get(v, v)
    return rows


def write(name, rows):
    if not rows:
        return
    fields = list(dict.fromkeys(k for r in rows for k in r))  # union of keys, first-seen order
    with (RES / name).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def decision(dE, ratio):
    if dE <= -1.0:
        return "IMPROVES" if ratio <= 1.10 else "TRADE-OFF"
    if dE >= 1.0:
        return "WORSE"
    return "NO PRACTICAL DIFFERENCE"


def main():
    runs = [r for c in CFG["cycles"] for r in read(HERE / "runs" / f"R1_{c}" / "metrics.csv")]
    write("runs.csv", runs)
    key = {(r["cycle"], r["case"], r["soh"], r["controller"]): r for r in runs}
    cycles, cases, sohs = list(CFG["cycles"]), list(CFG["cases"]), CFG["soh"]

    # sanity controls (protocol section 6)
    san = []
    for c in cycles:
        for cs in cases:
            f, s = key[(c, cs, 1.0, "F")], key[(c, cs, 1.0, "S")]
            san.append({"check": "S == F at SoH 1.0", "cycle": c, "case": cs,
                        "value": f["E_net_Wh"] - s["E_net_Wh"], "pass": f["E_net_Wh"] == s["E_net_Wh"]})
        for ctrl in CFG["controllers"]:
            a, b = key[(c, "BCS", 1.0, ctrl)], key[(c, "BCN", 1.0, ctrl)]
            san.append({"check": f"BCS == BCN at SoH 1.0 ({ctrl})", "cycle": c, "case": "BCS/BCN",
                        "value": a["E_net_Wh"] - b["E_net_Wh"], "pass": a["E_net_Wh"] == b["E_net_Wh"]})
    prim = read(REPO_DIR / "artifacts" / "tables" / "primary_pairs.csv")
    for p in prim:
        for ctrl, col in (("F", "E_fixed_Wh_km"), ("S", "E_sched_Wh_km")):
            r = key[(p["profile"], "B0", p["soh"], ctrl)]
            rel = abs(r["Wh_per_km"] - p[col]) / p[col]
            san.append({"check": f"B0 reproduces saved primary ({ctrl})", "cycle": p["profile"],
                        "case": f"B0 soh {p['soh']}", "value": rel, "pass": rel <= 1e-9})
    write("sanity_checks.csv", san)

    # Q2 pairs and secondary pairs
    pairs = []
    for c in cycles:
        for cs in cases:
            for soh in sohs:
                for a, b in (("S", "F"), ("F01", "F"), ("S", "F01")):
                    ra, rb = key[(c, cs, soh, a)], key[(c, cs, soh, b)]
                    dE = 100 * (ra["Wh_per_km"] - rb["Wh_per_km"]) / rb["Wh_per_km"]
                    dEr = 100 * (ra["Wh_per_ref_km"] - rb["Wh_per_ref_km"]) / rb["Wh_per_ref_km"]
                    ratio = ra["rmse_ms"] / rb["rmse_ms"]
                    incomplete = max(ra["shortfall_pct"], rb["shortfall_pct"]) > 1.0
                    pairs.append({"cycle": c, "case": cs, "soh": soh, "pair": f"{a} vs {b}",
                                  "E_a_Wh_km": ra["Wh_per_km"], "E_b_Wh_km": rb["Wh_per_km"],
                                  "dE_abs_Wh_km": ra["Wh_per_km"] - rb["Wh_per_km"], "dE_pct": dE,
                                  "dE_ref_km_pct": dEr, "rmse_a": ra["rmse_ms"], "rmse_b": rb["rmse_ms"],
                                  "rmse_ratio": ratio, "maxerr_a": ra["max_abs_err_ms"], "maxerr_b": rb["max_abs_err_ms"],
                                  "shortfall_a_pct": ra["shortfall_pct"], "shortfall_b_pct": rb["shortfall_pct"],
                                  "decision": decision(dE, ratio) + (" / INCOMPLETE-CYCLE" if incomplete else "")})
    write("pairs.csv", pairs)

    # Q1: does SoH change the behaviour of each controller?
    q1 = []
    for c in cycles:
        for cs in cases:
            for ctrl in CFG["controllers"]:
                r1, r7 = key[(c, cs, 1.0, ctrl)], key[(c, cs, 0.7, ctrl)]
                drm = 100 * (r7["rmse_ms"] / r1["rmse_ms"] - 1)
                dEn = 100 * (r7["Wh_per_km"] / r1["Wh_per_km"] - 1)
                q1.append({"cycle": c, "case": cs, "controller": ctrl, "rmse_soh1": r1["rmse_ms"],
                           "rmse_soh07": r7["rmse_ms"], "rmse_change_pct": drm, "E_soh1": r1["Wh_per_km"],
                           "E_soh07": r7["Wh_per_km"], "E_change_pct": dEn,
                           "sat_batt_frac_soh1": r1["sat_batt_frac"], "sat_batt_frac_soh07": r7["sat_batt_frac"],
                           "fb_Wh_soh1": r1["friction_brake_Wh"], "fb_Wh_soh07": r7["friction_brake_Wh"],
                           "soh_matters": abs(drm) > 5 or abs(dEn) > 1})
    write("soh_effect.csv", q1)

    # Q3
    q3 = []
    for c in cycles:
        for cs in cases:
            eS = np.mean([key[(c, cs, s, "S")]["Wh_per_km"] for s in sohs])
            eF = np.mean([key[(c, cs, s, "F01")]["Wh_per_km"] for s in sohs])
            rS = np.mean([key[(c, cs, s, "S")]["rmse_ms"] for s in sohs])
            rF = np.mean([key[(c, cs, s, "F01")]["rmse_ms"] for s in sohs])
            q3.append({"cycle": c, "case": cs, "E_S_avg": eS, "E_F01_avg": eF, "rmse_S_avg": rS,
                       "rmse_F01_avg": rF, "H_C_holds": bool(eF <= eS * 1.001 and rF <= rS)})
    write("q3_fixed_vs_scheduled.csv", q3)

    # convergence
    conv = []
    cc = CFG["convergence"]
    for c in cc["cycles"]:
        prev = None
        for dt in cc["dt"]:
            d = HERE / "runs" / f"CONV_{c}_dt{dt * 1e3:g}ms" / "metrics.csv"
            if not d.exists():
                continue
            rr = {r["controller"]: r for r in read(d)}
            dE = 100 * (rr["S"]["Wh_per_km"] - rr["F"]["Wh_per_km"]) / rr["F"]["Wh_per_km"]
            row = {"cycle": c, "dt_ms": dt * 1e3, "E_F": rr["F"]["Wh_per_km"], "E_S": rr["S"]["Wh_per_km"],
                   "dE_pct": dE, "rmse_F": rr["F"]["rmse_ms"], "rmse_S": rr["S"]["rmse_ms"]}
            if prev:
                row["dE_change_pp"] = dE - prev["dE_pct"]
                row["E_F_rel_change"] = abs(row["E_F"] / prev["E_F"] - 1)
                row["E_S_rel_change"] = abs(row["E_S"] / prev["E_S"] - 1)
                row["pass"] = abs(row["dE_change_pp"]) < 0.01 and max(row["E_F_rel_change"], row["E_S_rel_change"]) < 1e-4
            conv.append(row)
            prev = row
    write("convergence.csv", conv)

    # figures
    FIG.mkdir(exist_ok=True)
    fig, axs = plt.subplots(1, len(cycles), figsize=(4 * len(cycles), 3.4), sharey=False)
    for ax, c in zip(axs, cycles):
        for cs in cases:
            ax.plot(sohs, [next(p["dE_pct"] for p in pairs if p["cycle"] == c and p["case"] == cs and p["soh"] == s
                                and p["pair"] == "S vs F") for s in sohs], marker="o", label=cs)
        ax.axhspan(-1, 1, color="0.9")
        ax.set_title(c)
        ax.set_xlabel("SoH")
        ax.invert_xaxis()
    axs[0].set_ylabel("ΔE, scheduled vs fixed [%] (Wh per actual km)")
    axs[-1].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "dE_sched_vs_fixed.png", dpi=130)
    plt.close(fig)

    fig, axs = plt.subplots(1, len(cycles), figsize=(4 * len(cycles), 3.4))
    for ax, c in zip(axs, cycles):
        for ctrl, ls in (("F", "-"), ("S", "--"), ("F01", ":")):
            for cs, col in (("B0", "k"), ("BCS", "C1"), ("BCS2", "C3")):
                ax.plot(sohs, [key[(c, cs, s, ctrl)]["rmse_ms"] for s in sohs], ls, color=col, marker=".",
                        label=f"{ctrl} {cs}")
        ax.set_title(c)
        ax.set_xlabel("SoH")
        ax.invert_xaxis()
    axs[0].set_ylabel("tracking RMSE [m/s]")
    axs[-1].legend(fontsize=6, ncol=2)
    fig.tight_layout()
    fig.savefig(FIG / "rmse_vs_soh.png", dpi=130)
    plt.close(fig)

    man = json.loads((HERE / "runs" / "R1_UDDS" / "manifest.json").read_text(encoding="utf-8"))
    ids = [r["run_id"] for r in man["runs"]]
    with np.load(HERE / "runs" / "R1_UDDS" / "series.npz") as z:
        s = {k: z[k] for k in z.files}
    fig, axs = plt.subplots(2, 1, figsize=(9, 5.5), sharex=True)
    for ctrl, col in (("F", "C0"), ("S", "C1")):
        j = ids.index(f"R1_UDDS-BCS-soh0.70-{ctrl}")
        axs[0].plot(s["t"][:, j], s["v"][:, j] * 3.6, color=col, lw=0.8, label=f"{ctrl} (BCS, SoH 0.7)")
        axs[1].plot(s["t"][:, j], s["i"][:, j], color=col, lw=0.8)
    axs[0].plot(s["t"][:, 0], s["v_ref"][:, 0] * 3.6, "k:", lw=0.8, label="reference (EPA UDDS)")
    j = ids.index("R1_UDDS-BCS-soh0.70-F")
    axs[1].plot(s["t"][:, j], s["i_d"][:, j], "k:", lw=0.8, label="discharge limit")
    axs[0].set_ylabel("speed [km/h]")
    axs[1].set_ylabel("battery current [A]")
    axs[1].set_xlabel("time [s] (samples every 1 s)")
    axs[0].legend(fontsize=7)
    axs[1].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "udds_bcs_soh07_timeseries.png", dpi=130)
    plt.close(fig)
    print("tables and figures written")


if __name__ == "__main__":
    main()
