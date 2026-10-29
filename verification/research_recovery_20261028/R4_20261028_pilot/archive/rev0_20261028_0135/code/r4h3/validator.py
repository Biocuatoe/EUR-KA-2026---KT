"""Component A: validity of a speed trajectory against the H3 reference task (protocol v1 3, 5, 6, 9a).

A trajectory is a piecewise-linear speed history given by knots (t_i, v_i). Every check is exact for
that representation (no sampling). The validator reports every failure and never repairs anything.
Open ambiguities are applied in their strictest reading (02_protocol_ambiguity_register.md):
  AMB-02  an extra stop inside a segment (v = 0 between departure and arrival) is a failure.
"""

from __future__ import annotations

import numpy as np

from r4h3 import config
from r4h3.task import Task

TOL_T = 1e-9          # s
TOL_V = 1e-12         # m/s, "at rest"
TOL_SEG_D = 1e-9      # m per segment (protocol 9b)
TOL_A = 1e-9          # m/s^2


def _integral(t, v, a, b):
    """Exact integral of the piecewise-linear v(t) over [a, b]."""
    if b <= a:
        return 0.0
    inner = (t > a) & (t < b)
    tt = np.concatenate([[a], t[inner], [b]])
    vv = np.concatenate([[np.interp(a, t, v)], v[inner], [np.interp(b, t, v)]])
    return float(np.sum(0.5 * (vv[1:] + vv[:-1]) * np.diff(tt)))


def _max_on(t, v, a, b):
    inner = (t >= a) & (t <= b)
    vals = [np.interp(a, t, v), np.interp(b, t, v)] + list(v[inner])
    return float(np.max(vals))


def validate_trajectory(task: Task, t, v, plant=None, label: str = "") -> dict:
    t = np.asarray(t, float)
    v = np.asarray(v, float)
    fail = []
    out = {"label": label, "n_knots": int(len(t))}

    if t.shape != v.shape or t.ndim != 1 or len(t) < 2:
        return {**out, "valid": False, "failures": ["malformed knot arrays"]}
    if not (np.all(np.isfinite(t)) and np.all(np.isfinite(v))):
        return {**out, "valid": False, "failures": ["non-finite knots"]}
    if np.any(np.diff(t) <= 0):
        fail.append("knot times not strictly increasing")
    # duration and end conditions
    out["duration_s"] = float(t[-1] - t[0])
    if abs(t[0]) > TOL_T:
        fail.append(f"does not start at t = 0 (t0 = {t[0]})")
    if abs(t[-1] - task.T_ref) > TOL_T:
        fail.append(f"duration {t[-1]:.9f} s != task T_ref {task.T_ref} s")
    if abs(v[0]) > TOL_V or abs(v[-1]) > TOL_V:
        fail.append("does not start and end at rest")
    if v.min() < -TOL_V:
        fail.append(f"negative speed {v.min()}")
    # distance
    d = _integral(t, v, t[0], t[-1])
    out["distance_m"] = d
    out["distance_err_m"] = d - task.d_ref
    if abs(d - task.d_ref) > TOL_SEG_D * (len(task.segs) + 1):
        fail.append(f"distance {d:.9f} m != d_ref {task.d_ref:.9f} m")
    # rest intervals of the task: at rest throughout (protocol 5.3, 9a)
    rest_viol = [(a, b, _max_on(t, v, a, b)) for a, b in task.rest if _max_on(t, v, a, b) > TOL_V]
    out["n_rest_intervals"] = len(task.rest)
    out["n_rest_violations"] = len(rest_viol)
    if rest_viol:
        fail.append(f"moving during {len(rest_viol)} reference rest interval(s), first {rest_viol[0]}")
    # per segment: departure, arrival, distance, extra stops, speed envelope
    seg_rows = []
    for k, ((ks, ke), Dk, Tk, vl) in enumerate(zip(task.segs, task.D, task.T_seg, task.v_lim)):
        a, b = ks * task.h, ke * task.h
        dk = _integral(t, v, a, b)
        inside = (t > a + TOL_T) & (t < b - TOL_T)
        # departure = last zero knot before the first moving knot of the window; arrival = first zero knot after
        # the last moving knot. Motion already under way at a, or still under way at b, is caught explicitly.
        pos = np.flatnonzero((t >= a - TOL_T) & (t <= b + TOL_T) & (v > TOL_V))
        moving_at_a = np.interp(a, t, v) > TOL_V
        moving_at_b = np.interp(b, t, v) > TOL_V
        if len(pos) and not moving_at_a and pos[0] > 0:
            t_dep = float(t[pos[0] - 1])
        else:
            t_dep = float("nan") if not len(pos) else -np.inf
        t_arr = float(t[pos[-1] + 1]) if len(pos) and pos[-1] + 1 < len(t) and not moving_at_b else float("nan")
        n_extra = int(np.sum(v[pos[0]:pos[-1] + 1] <= TOL_V)) if len(pos) else 0
        vmax = float(v[inside].max()) if inside.any() else 0.0
        row = dict(segment=k, ks=ks, ke=ke, D_ref_m=Dk, D_traj_m=dk, T_ref_s=Tk, t_dep_s=t_dep, t_arr_s=t_arr,
                   early_arrival_s=b - t_arr if np.isfinite(t_arr) else float("nan"), n_extra_stops=n_extra,
                   v_lim_ms=vl, v_max_ms=vmax)
        seg_rows.append(row)
        if abs(dk - Dk) > TOL_SEG_D:
            fail.append(f"segment {k}: distance {dk:.9f} m != D_k {Dk:.9f} m")
        if not np.isfinite(t_dep) or abs(t_dep - a) > TOL_T:
            fail.append(f"segment {k}: departure {t_dep} s != reference departure {a} s")
        if not np.isfinite(t_arr) or t_arr > b + TOL_T:
            fail.append(f"segment {k}: arrival {t_arr} s later than reference arrival {b} s")
        if n_extra:
            fail.append(f"segment {k}: {n_extra} extra stop knot(s) inside the segment (AMB-02, strict)")
        if vmax > vl + TOL_V:
            fail.append(f"segment {k}: speed {vmax:.6f} m/s above segment reference maximum {vl:.6f} m/s")
    out["segments"] = seg_rows
    # global speed domain and acceleration
    out["max_speed_ms"] = float(v.max())
    if v.max() > config.SPEED_DOMAIN_MAX + TOL_V:
        fail.append(f"speed {v.max():.6f} m/s above the 50 km/h domain")
    dt = np.diff(t)
    acc = np.divide(np.diff(v), dt, out=np.zeros_like(dt), where=dt > 0)
    out["acc_min"], out["acc_max"] = float(acc.min()), float(acc.max())
    if acc.min() < task.a_lo - TOL_A or acc.max() > task.a_hi + TOL_A:
        fail.append(f"acceleration [{acc.min():.6f}, {acc.max():.6f}] outside task bounds "
                    f"[{task.a_lo:.6f}, {task.a_hi:.6f}]")
    # QS feasibility of every constant-acceleration piece (protocol 5.2)
    if plant is not None:
        ok = plant.step(v[:-1], v[1:], np.where(dt > 0, dt, 1.0))[-1]
        out["n_infeasible_pieces"] = int(np.sum(~ok))
        if not ok.all():
            fail.append(f"{int(np.sum(~ok))} QS-infeasible piece(s) on the scenario plant")
    out["failures"] = fail
    out["valid"] = not fail
    return out
