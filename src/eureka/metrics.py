"""Run validation and metrics, computed only from saved raw outputs (artifacts/raw)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from eureka.params import Params
from eureka.plant import IX, BatchParams, energy_closure

CLOSURE_TOL = 1e-3  # preregistration section 10: 0.1 % of energy throughput


def load_batch(batch_dir: Path) -> tuple[dict, dict]:
    manifest = json.loads((batch_dir / "manifest.json").read_text(encoding="utf-8"))
    with np.load(batch_dir / "timeseries.npz") as z:
        arrays = {k: z[k] for k in z.files}
    return manifest, arrays


def run_params(manifest: dict, j: int) -> Params:
    return Params(**manifest["nominal_parameters"]).with_overrides(
        **manifest["runs"][j]["overrides"]
    )


def validate(manifest: dict, arr: dict, j: int) -> dict:
    p = run_params(manifest, j)
    soh = np.array([manifest["runs"][j]["soh"]])
    bp = BatchParams.from_params([p], soh)
    c = energy_closure(arr["y_end"][j : j + 1], arr["y0"][j : j + 1], bp)
    throughput = p.V_oc * 3600.0 * (arr["y_end"][j, IX["Ah"]] - arr["y0"][j, IX["Ah"]])
    rel = float(abs(c["abs_J"][0]) / throughput) if throughput > 0 else float("inf")
    reasons = []
    if arr["nonfinite"][:, j].any() or not np.all(np.isfinite(arr["y_end"][j])):
        reasons.append("non-finite state")
    if arr["infeasible"][:, j].any():
        reasons.append("battery power infeasible")
    if rel > CLOSURE_TOL:
        reasons.append(f"energy closure {rel:.2e} > {CLOSURE_TOL}")
    if float(np.min(arr["v"][:, j])) < -1e-6:
        reasons.append("negative velocity")
    return {"valid": not reasons, "reasons": "; ".join(reasons), "closure_rel": rel}


def run_metrics(manifest: dict, arr: dict, j: int) -> dict:
    ts = manifest["nominal_parameters"]["Ts"]
    y0, y1 = arr["y0"][j], arr["y_end"][j]
    v = arr["v"][:, j].astype(float)
    e = v - arr["v_ref"]
    dist_km = (y1[IX["dist"]] - y0[IX["dist"]]) / 1000.0
    e_wh = (y1[IX["E_chem"]] - y0[IX["E_chem"]]) / 3600.0
    i = arr["i"][:, j].astype(float)
    acc = np.diff(v) / ts
    jerk = np.diff(acc) / ts
    rmse = float(np.sqrt(np.mean(e**2)))
    max_e = float(np.max(np.abs(e)))
    return {
        "distance_km": float(dist_km),
        "energy_Wh": float(e_wh),
        "energy_Wh_per_km": float(e_wh / dist_km),
        "rmse_ms": rmse,
        "max_abs_err_ms": max_e,
        "rms_current_A": float(np.sqrt(np.mean(i**2))),
        "peak_current_A": float(np.max(np.abs(i))),
        "ah_throughput": float(y1[IX["Ah"]] - y0[IX["Ah"]]),
        "resistive_loss_Wh": float(
            (y1[IX["E_R0"]] + y1[IX["E_R1"]] - y0[IX["E_R0"]] - y0[IX["E_R1"]]) / 3600.0
        ),
        "friction_brake_Wh": float((y1[IX["E_fb"]] - y0[IX["E_fb"]]) / 3600.0),
        "regen_recovered_Wh": float(-(y1[IX["E_regen"]] - y0[IX["E_regen"]]) / 3600.0),
        "traction_limited_frac": float(np.mean(arr["sat"][:, j])),
        "rms_jerk_ms3": float(np.sqrt(np.mean(jerk**2))),
        "rms_torque_cmd_Nm": float(np.sqrt(np.mean(arr["t_ref"][:, j].astype(float) ** 2))),
        "tracking_failure": bool(rmse > 1.5 or max_e > 3.0),
    }


def batch_table(batch_dir: Path) -> list[dict]:
    manifest, arr = load_batch(batch_dir)
    rows = []
    for j, run in enumerate(manifest["runs"]):
        row = {
            k: run[k]
            for k in (
                "run_id",
                "experiment",
                "profile",
                "controller",
                "soh",
                "gamma_v",
                "gamma_u",
                "r_scale",
                "draw",
                "seed",
            )
        }
        row.update(batch=manifest["batch"], commit=manifest["context"]["git"]["commit"])
        row.update(validate(manifest, arr, j))
        row.update(run_metrics(manifest, arr, j))
        rows.append(row)
    return rows
