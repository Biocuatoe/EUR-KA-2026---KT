"""Amendment 1 (R3_protocol_v1_amendment_1.md A1.1): stop-respecting same-task band (G-B', VSI').

    python -I run_gates_a1.py [--workers 6]      -> ../outputs/gates_a1/

Identical to run_gates.band_task except that band transitions with a nonzero offset at a sample where
the baseline v_b is at rest are infeasible (stop_mask). Frozen outputs in outputs/gates/ are not touched.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r3_lib as L  # noqa: E402
import run_gates as RG  # noqa: E402

RG.OUT = L.R3 / "outputs" / "gates_a1"
AMEND = L.R3 / "R3_protocol_v1_amendment_1.md"
_band_tables = L.band_tables


def stop_mask(tab):
    E, J = tab["E"], tab["J"]
    stop = tab["centre"] <= 1e-9
    off = np.arange(E.shape[1]) != J
    for k in np.where(stop[:-1])[0]:
        E[k, off, :] = L.INF
    for k in np.where(stop[1:])[0]:
        E[k][:, off] = L.INF
    return tab


def band_tables_stop(plant, centre, h, delta, dv, chunk=64):
    return stop_mask(_band_tables(plant, centre, h, delta, dv, chunk))


L.band_tables = band_tables_stop          # used by RG.band_task (looked up at call time, also in workers)


def run_one(args):
    import traceback
    try:
        return args, RG.band_task(*args), None
    except Exception:  # noqa: BLE001
        return args, None, traceback.format_exc()


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    rec = (L.R3 / "logs" / "amendment_1_sha256.txt").read_text(encoding="utf-8").split()[0]
    if sha(AMEND) != rec:
        sys.exit("amendment hash differs from the recorded hash; refusing to run")
    (RG.OUT / "paths").mkdir(parents=True, exist_ok=False)
    man = {"start": time.strftime("%Y-%m-%dT%H:%M:%S"), "amendment_sha256": rec, "protocol_sha256": sha(RG.PROTOCOL),
           "code": {p.name: sha(p) for p in sorted((L.R3 / "code").glob("*.py"))}, "python": sys.version,
           "numpy": np.__version__}
    specs = [(c, m, lim) for c in RG.CYCLES for m in ("M0", "M1", "M2") for lim in RG.LIMS]
    specs.sort(key=lambda s: 0 if s[0] == "UDDS" else 1)
    band, vsi, errs, times = [], [], [], []
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        for i, f in enumerate(as_completed([ex.submit(run_one, s) for s in specs]), 1):
            spec, res, err = f.result()
            if err:
                errs.append(dict(kind="band_a1", args=" ".join(spec), traceback=err))
                print(f"[{i}/{len(specs)}] ERROR {spec}", flush=True)
                continue
            _, rows, v, dt = res
            band += rows
            vsi += v
            times.append(dict(kind="band_a1", args=" ".join(spec), runtime_s=dt))
            print(f"[{i}/{len(specs)}] done {spec} {dt:.0f} s", flush=True)
    RG.write("band_rows.csv", band)
    RG.write("vsi_rows.csv", vsi)
    RG.write("task_times.csv", times)
    RG.write("errors.csv", errs or [dict(kind="", args="", traceback="no errors")])
    man["end"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    man["n_tasks"], man["n_errors"] = len(specs), len(errs)
    man["outputs"] = {p.name: sha(p) for p in sorted(RG.OUT.glob("*.csv"))}
    (RG.OUT / "run_manifest.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
