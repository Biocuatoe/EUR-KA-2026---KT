"""Run experiment R1 (grid) or its convergence check. Writes only under the rebuild directory.

    python -m rebuild.run grid          # 336 runs, one batch per cycle
    python -m rebuild.run convergence   # dt halving check (protocol section 8)
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
import time
import traceback
from pathlib import Path

import numpy as np
import yaml

from eureka import REPO_DIR
from eureka.controllers import gain
from eureka.cycles import Profile, load_profiles
from eureka.lineage import run_context
from eureka.params import load_params
from rebuild.model import IX, BatteryLimits, simulate

HERE = Path(__file__).resolve().parents[2]  # verification/scientific_rebuild_20261024
CFG = yaml.safe_load((HERE / "configs" / "R1.yaml").read_text(encoding="utf-8"))
HASHED = [
    HERE / "experimental_protocol.md",
    HERE / "configs" / "R1.yaml",
    *sorted((HERE / "src" / "rebuild").glob("*.py")),
    *sorted((REPO_DIR / "src" / "eureka").glob("*.py")),
    REPO_DIR / "configs" / "parameters.yaml",
    REPO_DIR / "configs" / "cycles" / "profiles.yaml",
]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_cycle(name: str) -> Profile:
    spec = CFG["cycles"][name]
    if spec["source"] == "eureka":
        return load_profiles()[name]
    rows = list(csv.DictReader((REPO_DIR / spec["path"]).open(encoding="utf-8")))
    t = np.array([float(r["time_s"]) for r in rows])
    v = np.array([float(r["speed_m_per_s"]) for r in rows])
    return Profile(name, t, v)


def run_specs(cycle: str):
    base = load_params()
    specs = []
    for case, cs in CFG["cases"].items():
        lim = BatteryLimits(**cs["limits"])
        p = base.with_overrides(k_r0=cs["k_r0"])
        for soh in CFG["soh"]:
            for ctrl, cc in CFG["controllers"].items():
                if cc["kind"] == "fixed":
                    K = gain(p, "fixed", r_scale=cc["r_scale"])
                else:
                    K = gain(p, "scheduled", soh=soh, gamma_v=cc["gamma_v"], gamma_u=cc["gamma_u"])
                specs.append(dict(cycle=cycle, case=case, soh=soh, controller=ctrl, k_r0=cs["k_r0"],
                                  limits=cs["limits"], gains=K.ravel().tolist(), params=p, lim=lim))
    return specs


def metrics(out: dict, j: int, p) -> dict:
    y0, y1, a = out["y0"][j], out["y_end"][j], out["acc"]
    d = (y1[IX["dist"]] - y0[IX["dist"]]) / 1000.0
    dref = out["ref_distance_m"] / 1000.0
    E = (y1[IX["E_chem"]] - y0[IX["E_chem"]]) / 3600.0
    ah = y1[IX["Ah"]] - y0[IX["Ah"]]
    throughput = p.V_oc * 3600.0 * ah
    clos = float(abs(out["closure_J"][j]) / throughput) if throughput > 0 else float("inf")
    steps = a["steps"][j]
    rmse = float(np.sqrt(a["se2"][j] / steps))
    reasons = []
    if out["nonfinite"][j] or not np.all(np.isfinite(y1)):
        reasons.append("non-finite state")
    if not out["feasible"][j]:
        reasons.append("battery solution infeasible")
    if clos > 1e-3:
        reasons.append(f"closure {clos:.2e}")
    return {
        "distance_km": d, "ref_distance_km": dref, "shortfall_pct": 100 * (dref - d) / dref,
        "rmse_ms": rmse, "max_abs_err_ms": float(a["max_e"][j]),
        "E_net_Wh": E, "E_pos_Wh": (y1[IX["E_pos"]] - y0[IX["E_pos"]]) / 3600.0,
        "E_neg_Wh": (y1[IX["E_neg"]] - y0[IX["E_neg"]]) / 3600.0,
        "Wh_per_km": E / d if d > 0 else float("nan"), "Wh_per_ref_km": E / dref,
        "sat_frac": float(a["sat"][j] / steps), "sat_batt_frac": float(a["sat_batt"][j] / steps),
        "friction_brake_Wh": (y1[IX["E_fb"]] - y0[IX["E_fb"]]) / 3600.0,
        "regen_terminal_Wh": -(y1[IX["E_regen"]] - y0[IX["E_regen"]]) / 3600.0,
        "peak_current_A": float(a["max_i"][j]), "rms_current_A": float(np.sqrt(a["i2"][j] / steps)),
        "vt_min_V": float(a["vt_min"][j]), "vt_max_V": float(a["vt_max"][j]),
        "I_over_As": float(y1[IX["I_over"]] - y0[IX["I_over"]]), "Ah": float(ah),
        "resistive_loss_Wh": float((y1[IX["E_R0"]] + y1[IX["E_R1"]] - y0[IX["E_R0"]] - y0[IX["E_R1"]]) / 3600.0),
        "closure_rel": clos, "tracking_failure": bool(rmse > 1.5 or a["max_e"][j] > 3.0),
        "valid": not reasons, "invalid_reasons": "; ".join(reasons),
    }


def run_batch(tag: str, cycle: str, specs: list[dict], dt: float | None = None) -> list[dict]:
    outdir = HERE / "runs" / tag
    outdir.mkdir(parents=True, exist_ok=False)  # never overwrite an earlier batch
    log = (outdir / "log.txt").open("w", encoding="utf-8")
    manifest = {"tag": tag, "cycle": cycle, "label": CFG["cycles"][cycle]["label"], "dt": dt,
                "context": run_context(), "file_sha256": {str(f.relative_to(REPO_DIR)): sha(f) for f in HASHED},
                "status": "started", "runs": []}
    (outdir / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    t0 = time.time()
    try:
        prof = load_cycle(cycle)
        out = simulate(prof, [s["params"] for s in specs], np.array([s["gains"] for s in specs]),
                       np.array([s["soh"] for s in specs]), [s["lim"] for s in specs], dt=dt)
        rows = []
        for j, s in enumerate(specs):
            m = metrics(out, j, s["params"])
            row = {"run_id": f"{tag}-{s['case']}-soh{s['soh']:.2f}-{s['controller']}", "cycle": cycle,
                   "case": s["case"], "soh": s["soh"], "controller": s["controller"], "k_r0": s["k_r0"],
                   "dt_s": out["dt"], **m}
            rows.append(row)
            manifest["runs"].append({**{k: s[k] for k in ("case", "soh", "controller", "k_r0", "limits", "gains")},
                                     "run_id": row["run_id"], "valid": m["valid"]})
        np.savez_compressed(outdir / "series.npz", **out["series"], y0=out["y0"], y_end=out["y_end"])
        manifest.update(status="completed", runtime_s=round(time.time() - t0, 1), n_runs=len(rows),
                        n_invalid=sum(not r["valid"] for r in rows))
        with (outdir / "metrics.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        log.write(f"completed {len(rows)} runs in {time.time() - t0:.1f} s\n")
        return rows
    except Exception:
        manifest.update(status="failed", runtime_s=round(time.time() - t0, 1))
        log.write(traceback.format_exc())
        raise
    finally:
        (outdir / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
        log.close()


def main(mode: str) -> None:
    if mode == "grid":
        for cycle in CFG["cycles"]:
            rows = run_batch(f"R1_{cycle}", cycle, run_specs(cycle))
            print(cycle, len(rows), "runs;", sum(not r["valid"] for r in rows), "invalid", flush=True)
    elif mode == "convergence":
        c = CFG["convergence"]
        for cycle in c["cycles"]:
            specs = [s for s in run_specs(cycle) if s["case"] == c["case"] and s["soh"] == c["soh"]
                     and s["controller"] in c["controllers"]]
            for dt in c["dt"]:
                run_batch(f"CONV_{cycle}_dt{dt * 1e3:g}ms", cycle, specs, dt=dt)
                print(cycle, dt, "done", flush=True)
    else:
        raise SystemExit(f"unknown mode {mode}")


if __name__ == "__main__":
    main(sys.argv[1])
