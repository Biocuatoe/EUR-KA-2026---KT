"""Pre-freeze scenario property: is exact tracking of each reference feasible on each R3 plant?

    python -I precheck_feasibility.py   -> ../outputs/precheck_feasibility.csv

Counts quasi-static steps whose drive demand exceeds the motor/battery envelope. No energy is
computed or written; the result only decides how the protocol defines the baseline (R3_protocol_v1.md section 3.3).
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r3_lib as L  # noqa: E402
from eureka.params import load_params  # noqa: E402
from rebuild.model import BatteryLimits  # noqa: E402
from rebuild.run import load_cycle  # noqa: E402

WIN = dict(v_min_ratio=0.78125, v_max_ratio=1.140625)
LIMS = {"L-R1": BatteryLimits(c_dis=3.0, c_ch=1.0, **WIN), "L-EVE": BatteryLimits(c_dis=2.0, c_ch=1.0, **WIN),
        "L-EVE-s": BatteryLimits(c_dis=2.0, c_ch=1.0, soh_scaled=True, **WIN), "none": BatteryLimits()}
PSTATES = {"P1": (1.0, 0.5), "P2": (0.8, 0.5), "P3": (0.8, 3.5)}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    out = L.R3 / "outputs"
    out.mkdir(exist_ok=True)
    rows = []
    for cyc in ("S1", "S2", "UDDS"):
        prof = load_cycle(cyc)
        for h in (1.0, 0.1):
            v = prof.sample(np.arange(0.0, prof.duration + 1e-9, h))
            for mk, mm in L.motor_models().items():
                for lk, lim in LIMS.items():
                    for pk, (soh, kr) in PSTATES.items():
                        pl = L.QSPlant(load_params().with_overrides(k_r0=kr), soh, lim, mm)
                        *_, ok = pl.step(v[:-1], v[1:], h)
                        rows.append(dict(cycle=cyc, h_s=h, motor=mk, limits=lk, pstate=pk, n_steps=len(ok),
                                         n_infeasible=int((~ok).sum()), frac_time_infeasible=float((~ok).mean())))
    path = out / "precheck_feasibility.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        if r["h_s"] == 1.0 and r["pstate"] in ("P1", "P3"):
            print(r["cycle"], r["motor"], r["limits"], r["pstate"], r["n_infeasible"], "/", r["n_steps"])


if __name__ == "__main__":
    main()
