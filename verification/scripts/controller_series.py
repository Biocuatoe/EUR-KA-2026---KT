"""Reading simulation outputs onto the control-sample grid (shared by the controller cross-check evaluators).

Modelica CSV -> series dict (same keys as controller_metrics.metrics expects) plus the extra fields used for comparison.
OpenModelica writes extra rows at event instants, so the rows at each grid time t_k = k*Ts are located explicitly:
  - continuous quantities (v, T, I, accumulators, ...) are continuous across the event -> the FIRST row within 1e-9 s of t_k is used
    (OpenModelica's sample() times drift from k*Ts by up to ~1e-11 s over a long run, so rows are matched with a window, not exactly);
  - discrete controller quantities (u, z, z_used, e_k, T_lim_k, sat_k) are read from the controller-update row itself: the first row in which
    ctrl.k_ctrl equals k+1 (post-event values of sample k).
If the controller event at the final instant steps*Ts was not written, the discrete quantities of the final sample are NaN and are
reconstructed by the caller from the saved series with the control law (never taken from the Python results).
"""
import glob
import hashlib
import json
import pathlib
import re

import numpy as np
import pandas as pd

TS = 0.01
CONT = ["v", "v_ref", "T", "T_lim", "T_cmd", "a", "F_fb", "F_net", "I", "P_batt", "P_e", "P_m", "SoC", "V1", "E_chem", "E_rr", "E_aero", "E_fb",
        "E_gear", "E_visc", "E_mi", "E_R0", "E_R1", "E_regen", "dist", "Ah", "closure"]
DISC = ["ctrl.u", "ctrl.z", "ctrl.z_used", "ctrl.e_k", "ctrl.T_lim_k", "ctrl.sat_k", "ctrl.k_ctrl", "ctrl.se2"]


def sha256(p) -> str:
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def sim_status(root: pathlib.Path, case: str) -> str:
    """omc exits 0 even when a simulation fails: read the simulation record of the case from the launcher logs."""
    logs = glob.glob(str(root / "verification/modelica-build/logs/*.out.txt"))
    verdict = "no record found"
    for lp in sorted(logs):
        txt = open(lp, encoding="utf-8", errors="replace").read()
        for blk in re.split(r"(?m)^record SimulationResult", txt)[1:]:
            if f"fileNamePrefix = '{case}'" in blk:
                verdict = "finished successfully" if "The simulation finished successfully" in blk else "FAILED (see log)"
    return verdict


def load_modelica(path, steps: int, ts: float = TS):
    """Return (series dict on k = 0..steps, info dict). Raises if a grid time is missing."""
    df = pd.read_csv(path)
    t = df["time"].to_numpy()
    kk = np.rint(t / ts).astype(np.int64)
    on_grid = np.abs(t - kk * ts) < 1e-9
    info = {"rows": int(len(df)), "rows_on_grid": int(on_grid.sum()), "nan_cells": int(df.isna().sum().sum()), "t_end": float(t[-1])}
    idx = np.nonzero(on_grid)[0]
    kg = kk[idx]
    first = {}
    last = {}
    # first and last row index per k
    order = np.argsort(kg, kind="stable")
    kg_s, idx_s = kg[order], idx[order]
    uk, start = np.unique(kg_s, return_index=True)
    stop = np.append(start[1:], len(kg_s)) - 1
    present = np.zeros(steps + 1, bool)
    sel = (uk >= 0) & (uk <= steps)
    present[uk[sel]] = True
    if not present.all():
        missing = np.nonzero(~present)[0]
        raise ValueError(f"{path}: {len(missing)} grid samples missing, first {missing[:5]}")
    first_idx = np.empty(steps + 1, np.int64)
    last_idx = np.empty(steps + 1, np.int64)
    first_idx[uk[sel]] = idx_s[start[sel]]
    last_idx[uk[sel]] = idx_s[stop[sel]]
    s = {}
    for c in CONT:
        if c in df:
            s[c] = df[c].to_numpy()[first_idx]
    kc = df["ctrl.k_ctrl"].to_numpy()
    n_upd = int(kc[-1])
    upd_idx = np.searchsorted(kc, np.arange(1, n_upd + 1), side="left")  # k_ctrl is non-decreasing: row of the m-th update = sample k = m-1
    for c in DISC:
        if c in df:
            col = df[c].to_numpy()
            arr = np.full(steps + 1, np.nan)
            arr[: min(n_upd, steps + 1)] = col[upd_idx[: steps + 1]]
            s[c.replace("ctrl.", "")] = arr
    for c in ("v", "T", "v_ref"):  # plant states / reference exactly as the controller saw them at its update event (rows of the update itself)
        arr = np.full(steps + 1, np.nan)
        arr[: min(n_upd, steps + 1)] = df[c].to_numpy()[upd_idx[: steps + 1]]
        s[c + "_upd"] = arr
    info["updates"] = n_upd
    info["final_update_present"] = bool(n_upd >= steps + 1)
    info["update_row_time_max_dev_from_kTs"] = float(np.max(np.abs(t[upd_idx[: steps + 1]] - np.arange(min(n_upd, steps + 1)) * ts)))
    info["n_event_rows_per_grid_time_max"] = int((stop - start + 1)[sel].max())
    return s, info
