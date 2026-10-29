"""Additional port check (beyond amendment 1 A1.3 item 1): the R2 layer logic where limits bind.

    python -I pilot_precheck2.py      -> ../outputs/pilot_B/precheck/precheck2.csv

The A1.3 precheck used S2, where no limit binds, so the governor and the aware anti-windup were not
exercised. This repeats the comparison with R2's sim.py on S1 under L-EVE and L-EVE-s (SoH 0.8,
k_r0 3.5), layer off and on, with M0. Pass: relative energy and distance difference <= 1e-9 and the
governor active in at least one run.
"""

import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r3_pilot as P  # noqa: E402

sys.path.insert(0, str(P.L.RR / "pilot"))
import sim as R2  # noqa: E402


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    p = P.load_params().with_overrides(k_r0=3.5)
    K = P.gain(p, "fixed", 1.0, 1.0, 0.8)
    specs = [(lay, lk) for lay in (False, True) for lk in ("L-EVE", "L-EVE-s")]
    prof = P.load_cycle("S1")
    args = ([p] * 4, np.array([K] * 4), np.full(4, 0.8), [P.LIM[s[1]] for s in specs], [s[0] for s in specs], [s[0] for s in specs])
    a = R2.simulate(prof, *args)
    b = P.simulate_layer(prof, *args, P.L.motor_models()["M0"])
    rows, worst = [], 0.0
    for j, (lay, lk) in enumerate(specs):
        ma, mb = R2.metrics(a, j, p), P.metrics(b, j, p)
        d = max(abs(ma["E_net_Wh"] - mb["E_net_Wh"]) / abs(ma["E_net_Wh"]), abs(ma["distance_km"] - mb["distance_km"]) / ma["distance_km"])
        worst = max(worst, d)
        rows.append(dict(layer=lay, limits=lk, E_R2_Wh=ma["E_net_Wh"], E_port_Wh=mb["E_net_Wh"], rel_diff=d,
                         gov_active_R2=ma["governor_active_frac"], gov_active_port=mb["governor_active_frac"],
                         batt_limited_R2=ma["batt_limited_frac"], batt_limited_port=mb["batt_limited_frac"],
                         rmse_R2=ma["rmse_ms"], rmse_port=mb["rmse_ms"]))
    out = P.OUTB / "precheck" / "precheck2.csv"
    P.write_csv(out, rows)
    ok = worst <= 1e-9 and any(r["gov_active_port"] > 0 for r in rows)
    for r in rows:
        print(r)
    print("worst", worst, "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
