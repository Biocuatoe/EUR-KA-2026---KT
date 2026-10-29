"""POST-GATE DESCRIPTION (not a new outcome): where does the same-task band DP save energy?

    python -I describe_band_paths.py      -> ../outputs/checks/band_path_description.csv

Reads the saved paths in outputs/gates/paths/ and describes, for each held-out scenario and delta:
distance and time spent moving while the baseline v_b is at standstill, change in the sum of
positive speed increments (kinetic-energy throughput proxy), and peak speed change.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_gates as RG  # noqa: E402

OUT = RG.L.R3 / "outputs" / "checks"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for cyc in ("S2", "UDDS", "S1"):
        for m in ("M0", "M1", "M2"):
            for lim in ("L-R1", "L-EVE"):
                z = np.load(RG.OUT / "paths" / f"band_{cyc}_{m}_{lim}.npz")
                for pk in ("P1",):
                    vb = z[f"{pk}_baseline"]
                    stop = vb <= 1e-9
                    stop_step = stop[:-1] & stop[1:]
                    d_b = float(np.sum(0.5 * (vb[1:] + vb[:-1])))
                    ke_b = float(np.sum(np.maximum(np.diff(vb ** 2), 0)))
                    for d in RG.DELTAS:
                        key = f"{pk}_band{d:.2f}"
                        if key not in z:
                            continue
                        v = z[key]
                        s = 0.5 * (v[1:] + v[:-1])
                        rows.append(dict(cycle=cyc, motor=m, limits=lim, pstate=pk, delta=d,
                                         n_steps_baseline_stopped=int(stop_step.sum()),
                                         dist_while_baseline_stopped_m=float(np.sum(s[stop_step])),
                                         dist_while_baseline_stopped_pct=100 * float(np.sum(s[stop_step])) / d_b,
                                         samples_moving_while_baseline_stopped=int(np.sum((v > 1e-9) & stop)),
                                         ke_throughput_change_pct=100 * (float(np.sum(np.maximum(np.diff(v ** 2), 0))) / ke_b - 1),
                                         peak_speed_change_ms=float(v.max() - vb.max()),
                                         mean_offset_moving_ms=float(np.mean((v - vb)[~stop]))))
    with (OUT / "band_path_description.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        if r["limits"] == "L-R1":
            print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})


if __name__ == "__main__":
    main()
