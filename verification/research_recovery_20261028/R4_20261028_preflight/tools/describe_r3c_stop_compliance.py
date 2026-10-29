"""Descriptive stop-compliance check of the saved R3 eco and baseline trajectories (R4 preflight, Phase 1).

Reads the R3 gate paths (outputs/gates/paths/*.npz) read-only and reports, for every saved eco profile and
every saved baseline v_b:
  - stop events (maximal runs of zero speed) in the reference and in the trajectory, and whether they pair up;
  - stop location error: cumulative distance at each stop, trajectory minus reference;
  - dwell error: stop duration, trajectory minus reference;
  - arrival-time shift at each stop: trajectory minus reference;
  - motion while the reference is at rest (baseline only, sampled on the reference grid);
  - total distance and trip time versus the reference.
No optimisation, simulation or energy computation is run. Nothing is written except the two output files.

    python -I describe_r3c_stop_compliance.py <R3 dir> <out_eco.csv> <out_baseline.csv>
"""
import csv
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
EPS = 1e-9


def stop_events(t, v):
    """List of (t_arrive, t_depart, k_first, k_last) for maximal runs of |v| <= EPS on knots t, v."""
    z = np.abs(v) <= EPS
    ev, k, n = [], 0, len(v)
    while k < n:
        if z[k]:
            k0 = k
            while k < n and z[k]:
                k += 1
            ev.append((t[k0], t[k - 1], k0, k - 1))
        else:
            k += 1
    return ev


def cumdist(t, v):
    """Cumulative distance at each knot of a piecewise-linear-in-time speed history (exact trapezoid)."""
    return np.concatenate([[0.0], np.cumsum(0.5 * (v[1:] + v[:-1]) * np.diff(t))])


def compare(t_ref, v_ref, t, v):
    er, et = stop_events(t_ref, v_ref), stop_events(t, v)
    sr, st = cumdist(t_ref, v_ref), cumdist(t, v)
    out = {"n_stops_ref": len(er), "n_stops_traj": len(et), "stops_pair": len(er) == len(et),
           "d_ref_m": sr[-1], "d_traj_m": st[-1], "T_ref_s": t_ref[-1], "T_traj_s": t[-1]}
    if len(er) == len(et):
        loc = np.array([st[b[2]] - sr[a[2]] for a, b in zip(er, et)])
        dwell = np.array([(b[1] - b[0]) - (a[1] - a[0]) for a, b in zip(er, et)])
        arr = np.array([b[0] - a[0] for a, b in zip(er, et)])
        out.update(max_abs_stop_location_err_m=np.max(np.abs(loc)), max_abs_dwell_err_s=np.max(np.abs(dwell)),
                   max_abs_arrival_shift_s=np.max(np.abs(arr)), mean_abs_arrival_shift_s=np.mean(np.abs(arr)),
                   max_late_arrival_s=np.max(arr), max_early_arrival_s=-np.min(arr))
    return out


def main():
    r3, out_eco, out_base = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
    pdir = r3 / "outputs" / "gates" / "paths"
    eco_rows, base_rows = [], []
    for f in sorted(pdir.glob("eco_*.npz")):
        _, cyc, motor, lim = f.stem.split("_", 3)
        z = np.load(f, allow_pickle=False)
        t_ref, v_ref = z["t"], z["v_ref"]
        for key in sorted(k for k in z.files if k.endswith("_t")):
            stem = key[:-2]
            ps, a = stem.split("_A")
            r = {"cycle": cyc, "motor": motor, "limits": lim, "pstate": ps, "allowance": float(a)}
            r.update(compare(t_ref, v_ref, z[key], z[stem + "_v"]))
            # A1.1's criterion applied in time: eco speed on the reference's 1 s grid where the reference is at rest
            rest = np.abs(v_ref) <= EPS
            ve = np.interp(t_ref, z[key], z[stem + "_v"], right=0.0)
            r.update(samples_ref_at_rest=int(rest.sum()), samples_moving_while_ref_at_rest=int(np.sum(rest & (ve > EPS))),
                     max_speed_while_ref_at_rest_ms=float(np.max(np.where(rest, ve, 0.0))))
            eco_rows.append(r)
    for f in sorted(pdir.glob("band_*.npz")):
        _, cyc, motor, lim = f.stem.split("_", 3)
        z = np.load(f, allow_pickle=False)
        t_ref, v_ref = z["t"], z["v_ref"]
        rest = np.abs(v_ref) <= EPS
        for key in sorted(k for k in z.files if k.endswith("_baseline")):
            vb = z[key]
            r = {"cycle": cyc, "motor": motor, "limits": lim, "pstate": key.split("_")[0],
                 "samples_ref_at_rest": int(rest.sum()),
                 "samples_moving_while_ref_at_rest": int(np.sum(rest & (vb > EPS))),
                 "samples_at_rest_while_ref_moving": int(np.sum(~rest & (vb <= EPS))),
                 "max_speed_while_ref_at_rest_ms": float(np.max(np.where(rest, vb, 0.0)))}
            r.update(compare(t_ref, v_ref, t_ref, vb))
            base_rows.append(r)
    for path, rows in ((out_eco, eco_rows), (out_base, base_rows)):
        keys = list(dict.fromkeys(k for r in rows for k in r))
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=keys)
            w.writeheader()
            w.writerows(rows)
        print(path, len(rows), "rows")


if __name__ == "__main__":
    main()
