"""Component B: the baseline task v_b and the S-eco planner with stops fixed in time (protocol v1 3.3, 4, 5).

The planner only produces speed trajectories. It never touches the controller and contains no SoH
logic: it is always designed on the plant it is given (P1 for B3, protocol 4). Energies here are the
planner's quasi-static objective values; the reported energy metric comes from the dynamic run and the
independent evaluator (Component E), never from these numbers.
"""

from __future__ import annotations

import numpy as np

from r4h3 import config
from r4h3.task import Task

L = config.L


def baseline_task(plant, task: Task):
    """v_b: closest feasible trajectory to the sampled reference (R3 v1 3.3, protocol 4)."""
    path = None
    for W in config.TRACK_W:
        path, sse, hit = L.track_dp(plant, task.v_ref, task.h, W, config.TRACK_DV)
        if path is not None and not hit:
            return {"v_b": path, "sse": sse, "W": W, "hit_boundary": False,
                    "equals_reference": bool(np.array_equal(path, task.v_ref)),
                    "max_dev_from_ref_ms": float(np.max(np.abs(path - task.v_ref)))}
    return {"v_b": path, "sse": float("inf") if path is None else sse, "W": W, "hit_boundary": True,
            "equals_reference": False, "max_dev_from_ref_ms": float("nan")}


def solve_segment(tab, T_k, lam_log10=config.LAMBDA_LOG10, iters=config.LAMBDA_ITERS):
    """Smallest lambda with t <= T_k (protocol 5.2), and the Lagrangian bound over every evaluated lambda."""
    evals = []

    def run(lg):
        sol = L.eco_segment_solve(tab, 10.0 ** lg)
        evals.append((lg, sol))
        return sol

    lo, hi = lam_log10
    s_hi = run(hi)
    if s_hi is None or s_hi["t"] > T_k:
        status = "time-infeasible" if s_hi is not None else "no feasible path"
        return {"status": status, "sol": None, "lam": None, "lb_J": float("nan"), "n_evals": len(evals)}
    s_lo = run(lo)
    if s_lo is not None and s_lo["t"] <= T_k:
        best, lg_best = s_lo, lo
    else:
        best, lg_best = s_hi, hi
        for _ in range(iters):
            mid = 0.5 * (lo + hi)
            s = run(mid)
            if s is not None and s["t"] <= T_k:
                hi, best, lg_best = mid, s, mid
            else:
                lo = mid
    lb = max(s["E"] + 10.0 ** lg * (s["t"] - T_k) for lg, s in evals if s is not None)
    return {"status": "ok", "sol": best, "lam": 10.0 ** lg_best, "lb_J": float(lb), "n_evals": len(evals)}


def seco_profile(task: Task, sols, tabs):
    """Time-domain knots: segment k departs at ks_k h, follows the DP speeds, then rests (protocol 5.3)."""
    t, v = [0.0], [0.0]
    for (ks, ke), sol, tab in zip(task.segs, sols, tabs):
        dep = ks * task.h
        if dep > t[-1]:
            t.append(dep)
            v.append(0.0)
        vs = sol["v"]
        dts = 2.0 * tab["ds"] / (vs[:-1] + vs[1:])
        tk = dep + np.cumsum(dts)
        t.extend(tk.tolist())
        v.extend(vs[1:].tolist())
    if task.T_ref > t[-1]:
        t.append(task.T_ref)
        v.append(0.0)
    return np.array(t), np.array(v)


def plan_seco(plant, task: Task, ds=config.ECO_DS, dv=config.ECO_DV):
    """S-eco planner on the given plant. Returns profile knots or status 'unavailable' (never replaced)."""
    rows, sols, tabs = [], [], []
    status = "ok"
    for k, ((ks, ke), Dk, Tk, vl) in enumerate(zip(task.segs, task.D, task.T_seg, task.v_lim)):
        tab = L.eco_segment_tables(plant, Dk, vl, task.a_lo, task.a_hi, ds, dv)
        r = solve_segment(tab, Tk)
        sol = r["sol"]
        rows.append(dict(segment=k, ks=ks, ke=ke, D_k_m=Dk, T_k_s=Tk, t_k_s=sol["t"] if sol else float("nan"),
                         E_k_J=sol["E"] if sol else float("nan"), LB_k_J=r["lb_J"], lambda_k=r["lam"],
                         N_k=tab["N"], ds_m=tab["ds"], v_lim_k_ms=vl, n_speed_grid=len(tab["v"]),
                         n_lambda_evals=r["n_evals"], status=r["status"]))
        if sol is None:
            status = "unavailable"
        sols.append(sol)
        tabs.append(tab)
    if status != "ok":
        return {"status": status, "rows": rows, "t": None, "v": None}
    t, v = seco_profile(task, sols, tabs)
    return {"status": "ok", "rows": rows, "t": t, "v": v,
            "E_seco_J": float(sum(s["E"] for s in sols)), "LB_total_J": float(sum(r["LB_k_J"] for r in rows))}
