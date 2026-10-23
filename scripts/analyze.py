"""Validate saved runs, compute metrics and the pre-registered analyses.

    python scripts/analyze.py primary
    python scripts/analyze.py gamma_sweep
    python scripts/analyze.py fixed_family        # needs primary
    python scripts/analyze.py robustness --pilot  # writes the sample-size decision
    python scripts/analyze.py robustness

Reads only artifacts/raw/<experiment>/*/{manifest.json,timeseries.npz}. Writes
data/processed/<experiment>/runs.csv (validated per-run metrics),
artifacts/tables/<experiment>_*.csv and artifacts/reports/<experiment>_results.json.
"""

import argparse
import json
import math
import sys

import numpy as np
import pandas as pd

from eureka import ROOT_DIR
from eureka.experiment import RAW_DIR, load_experiments
from eureka.lineage import run_context
from eureka.metrics import batch_table

TABLES = ROOT_DIR / "artifacts" / "tables"
REPORTS = ROOT_DIR / "artifacts" / "reports"
MARGIN_PCT, RMSE_RATIO_MAX = 1.0, 1.10  # preregistration section 9


def load_runs(name: str) -> pd.DataFrame:
    batches = sorted(p for p in (RAW_DIR / name).iterdir() if (p / "manifest.json").exists())
    if not batches:
        raise SystemExit(f"no raw outputs for {name}")
    df = pd.DataFrame([r for b in batches for r in batch_table(b)])
    out = ROOT_DIR / "data" / "processed" / name
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "runs.csv", index=False)
    return df


def run_counts(df: pd.DataFrame) -> dict:
    return {
        "attempted": len(df),
        "valid": int(df["valid"].sum()),
        "invalid": int((~df["valid"]).sum()),
        "invalid_reasons": df.loc[~df["valid"], ["run_id", "reasons"]].to_dict("records"),
    }


def decide(d_e: float, ratio: float) -> str:
    if d_e <= -MARGIN_PCT:
        return "IMPROVES" if ratio <= RMSE_RATIO_MAX else "TRADE-OFF"
    if d_e >= MARGIN_PCT:
        return "WORSE"
    return "NO PRACTICAL DIFFERENCE"


def pair_table(df: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    f = df[df.controller == "fixed"].set_index(keys)
    s = df[df.controller == "scheduled"].set_index(keys)
    t = pd.DataFrame(
        {
            "E_fixed_Wh_km": f["energy_Wh_per_km"],
            "E_sched_Wh_km": s["energy_Wh_per_km"],
            "rmse_fixed": f["rmse_ms"],
            "rmse_sched": s["rmse_ms"],
            "peak_I_fixed": f["peak_current_A"],
            "peak_I_sched": s["peak_current_A"],
            "loss_R_fixed_Wh": f["resistive_loss_Wh"],
            "loss_R_sched_Wh": s["resistive_loss_Wh"],
            "valid_pair": f["valid"] & s["valid"],
        }
    )
    t["dE_pct"] = (t.E_sched_Wh_km - t.E_fixed_Wh_km) / t.E_fixed_Wh_km * 100
    t["rmse_ratio"] = t.rmse_sched / t.rmse_fixed
    return t.reset_index()


def analyze_primary(df):
    pairs = pair_table(df, ["profile", "soh"])
    pairs["decision"] = [decide(a, b) for a, b in zip(pairs.dE_pct, pairs.rmse_ratio, strict=True)]
    pairs.to_csv(TABLES / "primary_pairs.csv", index=False)
    df.to_csv(TABLES / "primary_metrics.csv", index=False)
    prim = pairs[(pairs.profile == "S1") & (np.isclose(pairs.soh, 0.8))].iloc[0]
    sanity = pairs[np.isclose(pairs.soh, 1.0)]
    sanity_ok = bool((sanity.dE_pct == 0).all() and (sanity.rmse_ratio == 1).all())
    valid = bool(df["valid"].all())
    return {
        "primary_condition": "S1, SoH 0.80, gamma_v = gamma_u = 1",
        "primary_valid": valid and bool(prim.valid_pair),
        "sanity_soh1_identical": sanity_ok,
        "dE_pct": float(prim.dE_pct),
        "rmse_ratio": float(prim.rmse_ratio),
        "E_fixed_Wh_km": float(prim.E_fixed_Wh_km),
        "E_sched_Wh_km": float(prim.E_sched_Wh_km),
        "decision_H1": decide(prim.dE_pct, prim.rmse_ratio) if valid and sanity_ok else "INVALID",
        "pairs": pairs.to_dict("records"),
    }


def analyze_gamma(df):
    ref = df[df.controller == "fixed"].iloc[0]
    s = df[df.controller == "scheduled"].copy()
    s["dE_pct"] = (s.energy_Wh_per_km - ref.energy_Wh_per_km) / ref.energy_Wh_per_km * 100
    s["rmse_ratio"] = s.rmse_ms / ref.rmse_ms
    s["decision"] = [decide(a, b) for a, b in zip(s.dE_pct, s.rmse_ratio, strict=True)]
    cols = [
        "gamma_u",
        "gamma_v",
        "energy_Wh_per_km",
        "dE_pct",
        "rmse_ms",
        "rmse_ratio",
        "peak_current_A",
        "decision",
        "valid",
    ]
    s[cols].to_csv(TABLES / "gamma_sweep.csv", index=False)
    return {
        "reference_fixed_Wh_km": float(ref.energy_Wh_per_km),
        "reference_fixed_rmse": float(ref.rmse_ms),
        "rows": s[cols].to_dict("records"),
        "decision_counts": s.decision.value_counts().to_dict(),
    }


def analyze_family(df):
    prim_path = ROOT_DIR / "data" / "processed" / "primary" / "runs.csv"
    prim_res = json.loads((REPORTS / "primary_results.json").read_text(encoding="utf-8"))
    if not prim_res["result"]["primary_valid"]:
        raise SystemExit("primary analysis invalid: S-C depends on it and is not run")
    prim = pd.read_csv(prim_path)
    sched = prim[(prim.profile == "S1") & (prim.controller == "scheduled")]
    sched_E, sched_rmse = sched.energy_Wh_per_km.mean(), sched.rmse_ms.mean()
    fam = (
        df.groupby("r_scale")
        .agg(
            E_mean=("energy_Wh_per_km", "mean"),
            rmse_mean=("rmse_ms", "mean"),
            valid=("valid", "all"),
            n_soh=("soh", "nunique"),
        )
        .reset_index()
    )
    fam.to_csv(TABLES / "fixed_family.csv", index=False)
    feasible = fam[(fam.rmse_mean <= sched_rmse) & fam.valid]
    best = feasible.loc[feasible.E_mean.idxmin()] if len(feasible) else None
    hc = bool(best is not None and best.E_mean <= sched_E * 1.001)
    return {
        "scheduled_soh_avg_E_Wh_km": float(sched_E),
        "scheduled_soh_avg_rmse": float(sched_rmse),
        "n_family_members": int(len(fam)),
        "n_feasible": int(len(feasible)),
        "best_fixed_r_scale": None if best is None else float(best.r_scale),
        "best_fixed_E_Wh_km": None if best is None else float(best.E_mean),
        "best_fixed_rmse": None if best is None else float(best.rmse_mean),
        "H_C_holds": hc,
    }


def bootstrap_ci(x: np.ndarray, rng: np.random.Generator, n: int = 10_000) -> list[float]:
    idx = rng.integers(0, len(x), size=(n, len(x)))
    means = x[idx].mean(axis=1)
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def analyze_robustness(df, pilot: bool):
    c = load_experiments()["robustness"]
    pairs = pair_table(df, ["draw"])
    pairs.to_csv(
        TABLES / ("robustness_pilot_pairs.csv" if pilot else "robustness_pairs.csv"), index=False
    )
    v = pairs[pairs.valid_pair]
    d = v.dE_pct.to_numpy()
    sd, mean = float(np.std(d, ddof=1)), float(np.mean(d))
    if pilot:
        h = max(0.1, 0.1 * abs(mean))
        n = min(c["max_draws"], max(c["min_draws"], math.ceil((1.96 * sd / h) ** 2)))
        decision = {
            "pilot_draws": len(d),
            "pilot_mean_dE_pct": mean,
            "pilot_sd_dE_pct": sd,
            "target_half_width_pp": h,
            "N": int(n),
            "rule": "N = min(1000, max(50, ceil((1.96 sd / h)^2))), h = max(0.1 pp, 0.1 |mean|)",
        }
        (REPORTS / "robustness-sample-size.json").write_text(
            json.dumps(decision, indent=2), encoding="utf-8"
        )
        return decision
    rng = np.random.default_rng(c["base_seed"])
    return {
        "draws_valid_pairs": len(d),
        "mean_dE_pct": mean,
        "sd_dE_pct": sd,
        "bootstrap95_mean_dE_pct": bootstrap_ci(d, rng),
        "frac_draws_sched_lower_energy": float(np.mean(d < 0)),
        "median_rmse_ratio": float(v.rmse_ratio.median()),
        "frac_draws_rmse_ratio_gt_1_10": float(np.mean(v.rmse_ratio > RMSE_RATIO_MAX)),
        "decision_counts": pd.Series(
            [decide(a, b) for a, b in zip(v.dE_pct, v.rmse_ratio, strict=True)]
        )
        .value_counts()
        .to_dict(),
        "tracking_failures": int(df.tracking_failure.sum()),
        "interpretation_limit": "Interval = Monte Carlo uncertainty of the mean over an ASSUMED "
        "uniform parameter distribution; not an inference about vehicles.",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("experiment", choices=["primary", "gamma_sweep", "fixed_family", "robustness"])
    ap.add_argument("--pilot", action="store_true")
    a = ap.parse_args()
    df = load_runs(a.experiment)
    if a.experiment == "robustness" and a.pilot:
        df = df[df.draw < load_experiments()["robustness"]["pilot_draws"]]
    fn = {
        "primary": analyze_primary,
        "gamma_sweep": analyze_gamma,
        "fixed_family": analyze_family,
    }.get(a.experiment)
    res = fn(df) if fn else analyze_robustness(df, a.pilot)
    report = {
        "context": run_context(),
        "experiment": a.experiment,
        "runs": run_counts(df),
        "source_commits": sorted(df.commit.unique().tolist()),
        "result": res,
    }
    name = f"{a.experiment}{'_pilot' if a.pilot else ''}_results.json"
    (REPORTS / name).write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(
        json.dumps(
            {
                "runs": report["runs"] | {"invalid_reasons": "..."},
                "result": {k: v for k, v in res.items() if k not in ("pairs", "rows")},
            },
            indent=2,
            default=str,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
