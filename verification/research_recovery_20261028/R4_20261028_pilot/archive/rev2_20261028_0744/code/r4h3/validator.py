"""Component A: validity of a speed trajectory against the H3 reference task (protocol v1 3, 5, 6, 9a).

A trajectory is a piecewise-linear speed history given by knots (t_i, v_i). Every check is exact for
that representation (no sampling). The validator reports every failure and never repairs anything.
It takes no planner output other than the knots, so it cannot be satisfied by a planner status flag.

Decisions applied (03_protocol_v1_amendment_1_DRAFT.md; change VC-01 of 06_readiness_implementation_report.md):
  D1  "at rest" means v <= REST_EPS = 1e-9 m/s, the frozen moving/rest rule of protocol 5.1
      (r3_lib.segments); no other near-zero threshold is used. A rest knot strictly between a segment's
      departure and its arrival is an extra stop and invalidates the trajectory.
  D3  departure must equal the reference departure ks*h exactly; arrival must not be later than the
      reference arrival ke*h; the vehicle must be at rest from its arrival to the end of the segment
      window (waiting at the prescribed stop). Time comparisons are exact: no timing tolerance.
"""

from __future__ import annotations

import numpy as np

from r4h3 import config
from r4h3.task import REST_EPS, Task

TOL_SEG_D = 1e-9      # m per segment: protocol 9(b)
TOL_A = 1e-9          # m/s^2: the admissibility tolerance of the frozen planner (r3_lib.eco_segment_tables)


def _integral(t, v, a, b):
    """Exact integral of the piecewise-linear v(t) over [a, b]."""
    if b <= a:
        return 0.0
    inner = (t > a) & (t < b)
    tt = np.concatenate([[a], t[inner], [b]])
    vv = np.concatenate([[np.interp(a, t, v)], v[inner], [np.interp(b, t, v)]])
    return float(np.sum(0.5 * (vv[1:] + vv[:-1]) * np.diff(tt)))


def _max_on(t, v, a, b):
    """Exact maximum of the piecewise-linear v(t) over [a, b] (attained at a, b or a knot inside)."""
    inner = (t >= a) & (t <= b)
    vals = [np.interp(a, t, v), np.interp(b, t, v)] + list(v[inner])
    return float(np.max(vals))


def validate_trajectory(task: Task, t, v, plant=None, label: str = "") -> dict:
    t = np.asarray(t, float)
    v = np.asarray(v, float)
    fail = []
    out = {"label": label, "n_knots": int(len(t)), "rest_eps_ms": REST_EPS}

    if t.shape != v.shape or t.ndim != 1 or len(t) < 2:
        return {**out, "valid": False, "failures": ["malformed knot arrays"]}
    if not (np.all(np.isfinite(t)) and np.all(np.isfinite(v))):
        return {**out, "valid": False, "failures": ["non-finite knots"]}
    if np.any(np.diff(t) <= 0):
        fail.append("knot times not strictly increasing")
    # duration and end conditions (exact)
    out["duration_s"] = float(t[-1] - t[0])
    if t[0] != 0.0:
        fail.append(f"does not start at t = 0 (t0 = {t[0]!r})")
    if t[-1] != task.T_ref:
        fail.append(f"duration {t[-1]!r} s != task T_ref {task.T_ref!r} s")
    if v[0] > REST_EPS or v[-1] > REST_EPS:
        fail.append("does not start and end at rest")
    if v.min() < 0.0:
        fail.append(f"negative speed {v.min()}")
    # distance: the sum of the per-segment allowances of protocol 9(b)
    d = _integral(t, v, t[0], t[-1])
    out["distance_m"] = d
    out["distance_err_m"] = d - task.d_ref
    if abs(d - task.d_ref) > TOL_SEG_D * len(task.segs):
        fail.append(f"distance {d:.9f} m != d_ref {task.d_ref:.9f} m")
    # rest intervals of the task: at rest throughout (protocol 5.3, 9a)
    rest_viol = [(a, b, _max_on(t, v, a, b)) for a, b in task.rest if _max_on(t, v, a, b) > REST_EPS]
    out["n_rest_intervals"] = len(task.rest)
    out["n_rest_violations"] = len(rest_viol)
    if rest_viol:
        fail.append(f"moving during {len(rest_viol)} reference rest interval(s), first {rest_viol[0]}")
    # per segment: departure, arrival, waiting, distance, extra stops, speed envelope
    seg_rows = []
    for k, ((ks, ke), Dk, Tk, vl) in enumerate(zip(task.segs, task.D, task.T_seg, task.v_lim)):
        a, b = ks * task.h, ke * task.h
        dk = _integral(t, v, a, b)
        inside = (t > a) & (t < b)
        # departure = the rest knot just before the first moving knot of the window [a, b]; arrival = the rest
        # knot just after the last moving knot. Motion already under way at a, or still under way at b, is caught.
        pos = np.flatnonzero((t >= a) & (t <= b) & (v > REST_EPS))
        moving_at_a = np.interp(a, t, v) > REST_EPS
        moving_at_b = np.interp(b, t, v) > REST_EPS
        if len(pos) and not moving_at_a and pos[0] > 0:
            t_dep = float(t[pos[0] - 1])
        else:
            t_dep = float("nan") if not len(pos) else -np.inf
        t_arr = float(t[pos[-1] + 1]) if len(pos) and pos[-1] + 1 < len(t) and not moving_at_b else float("nan")
        n_extra = int(np.sum(v[pos[0]:pos[-1] + 1] <= REST_EPS)) if len(pos) else 0
        wait_max = _max_on(t, v, t_arr, b) if np.isfinite(t_arr) and t_arr <= b else float("nan")
        vmax = float(v[inside].max()) if inside.any() else 0.0
        row = dict(segment=k, ks=ks, ke=ke, D_ref_m=Dk, D_traj_m=dk, T_ref_s=Tk, t_dep_s=t_dep, t_arr_s=t_arr,
                   early_arrival_s=b - t_arr if np.isfinite(t_arr) else float("nan"), wait_max_speed_ms=wait_max,
                   n_extra_stops=n_extra, v_lim_ms=vl, v_max_ms=vmax)
        seg_rows.append(row)
        if abs(dk - Dk) > TOL_SEG_D:
            fail.append(f"segment {k}: distance {dk:.9f} m != D_k {Dk:.9f} m")
        if not np.isfinite(t_dep) or t_dep != a:
            fail.append(f"segment {k}: departure {t_dep!r} s != reference departure {a!r} s")
        if not np.isfinite(t_arr) or t_arr > b:
            fail.append(f"segment {k}: arrival {t_arr!r} s later than reference arrival {b!r} s")
        elif not wait_max <= REST_EPS:
            fail.append(f"segment {k}: not at rest while waiting from arrival {t_arr!r} s to {b!r} s")
        if n_extra:
            fail.append(f"segment {k}: {n_extra} extra stop knot(s) inside the segment (D1)")
        if vmax > vl:
            fail.append(f"segment {k}: speed {vmax:.6f} m/s above segment reference maximum {vl:.6f} m/s")
    out["segments"] = seg_rows
    # global speed domain and acceleration
    out["max_speed_ms"] = float(v.max())
    if v.max() > config.SPEED_DOMAIN_MAX:
        fail.append(f"speed {v.max():.6f} m/s above the 50 km/h domain")
    dt = np.diff(t)
    acc = np.divide(np.diff(v), dt, out=np.zeros_like(dt), where=dt > 0)
    out["acc_min"], out["acc_max"] = float(acc.min()), float(acc.max())
    if acc.min() < task.a_lo - TOL_A or acc.max() > task.a_hi + TOL_A:
        fail.append(f"acceleration [{acc.min():.6f}, {acc.max():.6f}] outside task bounds "
                    f"[{task.a_lo:.6f}, {task.a_hi:.6f}]")
    # QS feasibility of every constant-acceleration piece (protocol 5.2) on the plant given
    if plant is not None:
        ok = plant.step(v[:-1], v[1:], np.where(dt > 0, dt, 1.0))[-1]
        out["n_infeasible_pieces"] = int(np.sum(~ok))
        if not ok.all():
            fail.append(f"{int(np.sum(~ok))} QS-infeasible piece(s) on the scenario plant")
    out["failures"] = fail
    out["valid"] = not fail
    return out
