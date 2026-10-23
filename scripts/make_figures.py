"""Regenerate every evaluation figure from saved results.

    python scripts/make_figures.py

Inputs: artifacts/tables/{primary_pairs,fixed_family,robustness_pairs}.csv,
data/processed/primary/runs.csv and artifacts/raw/primary/S1 (time series).
Outputs: artifacts/figures/evaluation/*.png. No number is typed in by hand.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from eureka import ROOT_DIR  # noqa: E402
from eureka.experiment import RAW_DIR  # noqa: E402
from eureka.metrics import load_batch  # noqa: E402

TABLES = ROOT_DIR / "artifacts" / "tables"
OUT = ROOT_DIR / "artifacts" / "figures" / "evaluation"
SURFACE, INK, INK2, GRID, BAND = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#efeeea"
FIXED, SCHED = "#2a78d6", "#eb6834"  # categorical slots 1-2 (validated, light mode)


def style(ax, title=None):
    ax.set_facecolor(SURFACE)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.tick_params(colors=INK2, labelsize=8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    if title:
        ax.set_title(title, color=INK, fontsize=9, loc="left")


def fig_primary():
    t = pd.read_csv(TABLES / "primary_pairs.csv")
    fig, axes = plt.subplots(2, 2, figsize=(9, 5.4), dpi=150, facecolor=SURFACE, sharex=True)
    for col, prof in enumerate(["S1", "S2"]):
        d = t[t.profile == prof].sort_values("soh")
        ax = axes[0, col]
        ax.axhspan(-1, 1, color=BAND, zorder=0)
        ax.plot(d.soh * 100, d.dE_pct, color=INK2, linewidth=2, marker="o", markersize=5)
        ax.axhline(0, color=INK2, linewidth=0.8)
        ax.set_ylim(-1.5, 1.5)
        ax.text(
            70.5, 1.05, "±1 % pre-registered no-practical-difference band", color=INK2, fontsize=7
        )
        ax.text(
            70.5,
            -1.38,
            "report claim −12.5 % ± 2.1 % is far below this axis",
            color=INK2,
            fontsize=7,
        )
        style(ax, f"{prof}: energy difference, scheduled − fixed (%)")
        ax = axes[1, col]
        ax.axhline(1.10, color=INK2, linewidth=0.8, linestyle="--")
        ax.text(70.5, 1.105, "RMSE-ratio limit 1.10", color=INK2, fontsize=7)
        ax.plot(d.soh * 100, d.rmse_ratio, color=INK2, linewidth=2, marker="o", markersize=5)
        ax.set_ylim(0.95, 1.15)
        ax.set_xlabel("State of health (%)", color=INK2, fontsize=8)
        style(ax, f"{prof}: tracking RMSE ratio, scheduled / fixed")
    fig.tight_layout()
    fig.savefig(OUT / "primary_dE_rmse_vs_soh.png", facecolor=SURFACE)
    plt.close(fig)


def fig_family():
    fam = pd.read_csv(TABLES / "fixed_family.csv")
    prim = pd.read_csv(ROOT_DIR / "data" / "processed" / "primary" / "runs.csv")
    s = prim[(prim.profile == "S1") & (prim.controller == "scheduled")]
    fig, ax = plt.subplots(figsize=(6.6, 4.2), dpi=150, facecolor=SURFACE)
    ax.plot(
        fam.rmse_mean,
        fam.E_mean,
        color=FIXED,
        linewidth=2,
        marker="o",
        markersize=3,
        label="fixed gain, R scaled 0.1× to 10×",
    )
    nom = fam.iloc[(fam.r_scale - 1).abs().argmin()]
    ax.plot(
        nom.rmse_mean,
        nom.E_mean,
        "o",
        color=FIXED,
        markersize=8,
        markeredgecolor=SURFACE,
        markeredgewidth=2,
    )
    ax.annotate(
        "fixed, R × 1 (pre-registered)",
        (nom.rmse_mean, nom.E_mean),
        xytext=(14, -22),
        textcoords="offset points",
        color=INK2,
        fontsize=7,
        arrowprops={"arrowstyle": "-", "color": INK2, "linewidth": 0.6},
    )
    for (_, r), off in zip(fam.iloc[[0, -1]].iterrows(), [(12, -4), (-38, 6)], strict=True):
        ax.annotate(
            f"R × {r.r_scale:g}",
            (r.rmse_mean, r.E_mean),
            xytext=off,
            textcoords="offset points",
            color=INK2,
            fontsize=7,
        )
    ax.plot(
        s.rmse_ms.mean(),
        s.energy_Wh_per_km.mean(),
        "D",
        color=SCHED,
        markersize=9,
        markeredgecolor=SURFACE,
        markeredgewidth=2,
        label="SoH-scheduled (γ = 1)",
    )
    ax.annotate(
        "scheduled: on the fixed-gain curve",
        (s.rmse_ms.mean(), s.energy_Wh_per_km.mean()),
        xytext=(-95, 45),
        textcoords="offset points",
        color=INK2,
        fontsize=7,
        arrowprops={"arrowstyle": "-", "color": INK2, "linewidth": 0.6},
    )
    ax.set_xlabel("Tracking RMSE, mean over SoH 100/90/80/70 % (m/s)", color=INK2, fontsize=8)
    ax.set_ylabel("Energy, mean over SoH (Wh/km)", color=INK2, fontsize=8)
    ax.legend(frameon=False, fontsize=7, labelcolor=INK2, loc="upper left")
    style(ax, "S1: SoH-averaged energy vs tracking (lower-left is better)")
    fig.tight_layout()
    fig.savefig(OUT / "fixed_family_vs_scheduled.png", facecolor=SURFACE)
    plt.close(fig)


def fig_tracking():
    m, arr = load_batch(RAW_DIR / "primary" / "S1")
    col = {(r["controller"], r["soh"]): r["column"] for r in m["runs"]}
    t = arr["t"]
    fig, (a1, a2) = plt.subplots(
        2,
        1,
        figsize=(9, 4.8),
        dpi=150,
        facecolor=SURFACE,
        sharex=True,
        gridspec_kw={"height_ratios": [1, 1.3]},
    )
    a1.plot(t, arr["v_ref"] * 3.6, color=INK2, linewidth=1.5)
    a1.set_ylabel("km/h", color=INK2, fontsize=8)
    style(a1, "S1 synthetic reference speed")
    err = {}
    for ctl, color, lw in (("fixed", FIXED, 3.0), ("scheduled", SCHED, 1.0)):
        j = col[(ctl, 0.8)]
        err[ctl] = arr["v"][:, j] - arr["v_ref"]
        a2.plot(t, err[ctl], color=color, linewidth=lw, label=ctl)
    gap = float(np.max(np.abs(err["scheduled"] - err["fixed"])))
    a2.axhline(0, color=INK2, linewidth=0.8)
    a2.set_ylabel("v − v_ref (m/s)", color=INK2, fontsize=8)
    a2.set_xlabel("Time (s)", color=INK2, fontsize=8)
    a2.legend(frameon=False, fontsize=7, labelcolor=INK2, loc="upper right", ncol=2)
    style(a2, f"Tracking error at SoH 80 % (traces overlap; max difference {gap:.4f} m/s)")
    fig.tight_layout()
    fig.savefig(OUT / "tracking_error_S1_soh80.png", facecolor=SURFACE)
    plt.close(fig)


def fig_robustness():
    p = pd.read_csv(TABLES / "robustness_pairs.csv")
    p = p[p.valid_pair]
    fig, ax = plt.subplots(figsize=(6.6, 3.6), dpi=150, facecolor=SURFACE)
    bins = np.linspace(p.dE_pct.min() - 0.005, p.dE_pct.max() + 0.005, 16)
    ax.hist(p.dE_pct, bins=bins, color=INK2, edgecolor=SURFACE, linewidth=2)
    ax.axvline(0, color=INK, linewidth=0.8)
    ax.set_xlabel("Paired energy difference, scheduled − fixed (%)", color=INK2, fontsize=8)
    ax.set_ylabel("Parameter draws", color=INK2, fontsize=8)
    ax.text(
        0.02,
        0.92,
        f"N = {len(p)} paired draws; ±1 % band lies outside this axis",
        transform=ax.transAxes,
        color=INK2,
        fontsize=7,
    )
    style(ax, "S-D: S1, SoH 80 %, assumed parameter ranges + velocity noise")
    fig.tight_layout()
    fig.savefig(OUT / "robustness_paired_dE_hist.png", facecolor=SURFACE)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for f in (fig_primary, fig_family, fig_tracking, fig_robustness):
        f()
    for p in sorted(OUT.glob("*.png")):
        print(f"wrote {p}")


if __name__ == "__main__":
    main()
