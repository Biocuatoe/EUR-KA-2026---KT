"""R3 attainable-improvement gates (R3_protocol_v1.md sections 3-4 and 8). Run only after the freeze.

    python -I run_gates.py [--workers 6]      -> ../outputs/gates/

Writes (raw, never edited afterwards):
    band_rows.csv     baseline task and same-task band DP per (cycle, motor, limits, P-state, delta)
    vsi_rows.csv      value of SoH information on the same task (delta = 0.25)
    eco_rows.csv      eco-driving DP per (cycle, motor, limits, P-state, allowance)
    eco_vsi_rows.csv  value of SoH information for eco at A = 0
    conv_rows.csv     discretisation checks
    errors.csv        every task that raised (traceback kept)
    paths/*.npz       baseline, band and eco trajectories (inputs of the pilot)
    run_manifest.json hashes of code, protocol and inputs; versions; start/end time
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r3_lib as L  # noqa: E402
from eureka.params import load_params  # noqa: E402
from rebuild.model import BatteryLimits  # noqa: E402
from rebuild.run import load_cycle  # noqa: E402

OUT = L.R3 / "outputs" / "gates"
PROTOCOL = L.R3 / "R3_protocol_v1.md"
WIN = dict(v_min_ratio=0.78125, v_max_ratio=1.140625)
LIMS = {"L-R1": BatteryLimits(c_dis=3.0, c_ch=1.0, **WIN), "L-EVE": BatteryLimits(c_dis=2.0, c_ch=1.0, **WIN),
        "L-EVE-s": BatteryLimits(c_dis=2.0, c_ch=1.0, soh_scaled=True, **WIN)}
PSTATES = {"P1": (1.0, 0.5), "P2": (0.8, 0.5), "P3": (0.8, 3.5)}
CYCLES = ("S1", "S2", "UDDS")
H = 1.0
DV_BAND = 0.01
DELTAS = (0.05, 0.10, 0.25, 0.50)
GATE_DELTA = 0.25
TRACK_W = (3.0, 6.0, 12.0)
DV_TRACK = 0.05
ALLOW = (0.0, 0.025, 0.05, 0.10)
DS_ECO, DV_ECO = 2.0, 0.1
J2WH = 1.0 / 3600.0


def plant(motor, lim, pk):
    soh, kr = PSTATES[pk]
    return L.QSPlant(load_params().with_overrides(k_r0=kr), soh, LIMS[lim], L.motor_models()[motor])


def reference(cyc, h=H):
    prof = load_cycle(cyc)
    t = np.arange(0.0, prof.duration + 1e-9, h)
    return t, prof.sample(t)


def baseline(pl, v_ref, h=H):
    """Closest feasible trajectory (protocol 3.3): exact reference where feasible."""
    for W in TRACK_W:
        path, sse, hit = L.track_dp(pl, v_ref, h, W, DV_TRACK)
        if path is not None and not hit:
            return path, sse, W, False
    return path, sse, W, True


def _ev(pl, v, h):
    r = L.evaluate(pl, v, h)
    return r


# --------------------------------------------------------------------------- same-task band DP and VSI
def band_task(cyc, motor, lim):
    t0 = time.time()
    t, v_ref = reference(cyc)
    d_ref = float(np.sum(0.5 * (v_ref[1:] + v_ref[:-1])) * H)
    rows, vsi, paths = [], [], {}
    pks = ("P1", "P2", "P3") if lim != "L-EVE-s" else ("P1", "P2", "P3")
    base = {}
    best25 = {}
    for pk in pks:
        pl = plant(motor, lim, pk)
        vb, sse, W, hit = baseline(pl, v_ref)
        if vb is None:
            rows.append(dict(cycle=cyc, motor=motor, limits=lim, pstate=pk, delta=None, status="baseline infeasible",
                             track_W=W))
            continue
        eb = _ev(pl, vb, H)
        base[pk] = (vb, eb)
        paths[f"{pk}_baseline"] = vb
        common = dict(cycle=cyc, motor=motor, limits=lim, pstate=pk, d_ref_m=d_ref, track_W=W, track_hit_boundary=hit,
                      track_sse=sse, base_rmse_vs_ref=float(np.sqrt(np.mean((vb - v_ref) ** 2))),
                      base_max_dev_vs_ref=float(np.max(np.abs(vb - v_ref))),
                      base_shortfall_pct=100 * (d_ref - eb["dist_m"]) / d_ref, base_feasible=eb["feasible"],
                      E_b_Wh=eb["E_J"] * J2WH, d_b_m=eb["dist_m"], E_b_Wh_per_refkm=eb["E_J"] * J2WH / (d_ref / 1000),
                      base_fric_Wh=eb["fric_J"] * J2WH, base_Ah=eb["Ah"], base_I2_A2s=eb["I2_A2s"])
        for d in DELTAS:
            s0 = time.time()
            tab = L.band_tables(pl, vb, H, d, DV_BAND)
            r = L.band_min_energy_tab(pl, tab, eb["dist_m"])
            del tab
            if r is None:
                rows.append(dict(common, delta=d, status="band infeasible"))
                continue
            e = r["eval"]
            if d == GATE_DELTA:
                best25[pk] = r
            paths[f"{pk}_band{d:.2f}"] = r["path"]
            rows.append(dict(common, delta=d, status="ok", E_star_Wh=r["E_J"] * J2WH, d_star_m=r["dist_m"],
                             lb_Wh=r["lb_J"] * J2WH, H_found_pct=100 * (1 - r["E_J"] / eb["E_J"]),
                             H_max_pct=100 * (1 - r["lb_J"] / eb["E_J"]),
                             H_found_actualkm_pct=100 * (1 - (r["E_J"] / r["dist_m"]) / (eb["E_J"] / eb["dist_m"])),
                             star_feasible=e["feasible"], star_max_dev_vs_base=float(np.max(np.abs(r["path"] - vb))),
                             star_max_dev_vs_ref=float(np.max(np.abs(r["path"] - v_ref))),
                             star_fric_Wh=e["fric_J"] * J2WH, star_Ah=e["Ah"], star_I2_A2s=e["I2_A2s"],
                             mu=r["mu"], n_dp=r["n_dp"], runtime_s=time.time() - s0))
    # value of SoH information: same task (band around the aged state's baseline), SoH-1.0 design evaluated on the aged plant
    for pk in ("P2", "P3"):
        if pk not in base or pk not in best25:
            vsi.append(dict(cycle=cyc, motor=motor, limits=lim, pstate=pk, status="aged band unavailable"))
            continue
        vb, eb = base[pk]
        p1 = plant(motor, lim, "P1")
        tab = L.band_tables(p1, vb, H, GATE_DELTA, DV_BAND)
        r1 = L.band_min_energy_tab(p1, tab, eb["dist_m"])
        del tab
        pl = plant(motor, lim, pk)
        rs = best25[pk]
        if r1 is None:
            vsi.append(dict(cycle=cyc, motor=motor, limits=lim, pstate=pk, status="P1 design infeasible on P1 band"))
            continue
        e1 = _ev(pl, r1["path"], H)
        ok1 = e1["feasible"] and e1["dist_m"] >= eb["dist_m"] - 1e-9
        paths[f"{pk}_vsi_P1design"] = r1["path"]
        row = dict(cycle=cyc, motor=motor, limits=lim, pstate=pk, status="ok" if ok1 else "P1 design infeasible on aged plant",
                   E_aged_of_P1design_Wh=e1["E_J"] * J2WH, P1design_feasible_on_aged=e1["feasible"],
                   E_aged_star_Wh=rs["E_J"] * J2WH, lb_aged_Wh=rs["lb_J"] * J2WH)
        if ok1:
            e_star = min(rs["E_J"], e1["E_J"])
            row.update(VSI_found_pct=100 * (1 - e_star / e1["E_J"]), VSI_max_pct=100 * (1 - rs["lb_J"] / e1["E_J"]))
        vsi.append(row)
    np.savez_compressed(OUT / "paths" / f"band_{cyc}_{motor}_{lim}.npz", t=t, v_ref=v_ref, **paths)
    return "band", rows, vsi, time.time() - t0


# --------------------------------------------------------------------------- eco DP
def eco_setup(pl, v_ref, h=H, ds=DS_ECO, dv=DV_ECO):
    segs = L.segments(v_ref, h)
    acc = np.diff(v_ref) / h
    a_lo, a_hi = float(acc.min()), float(acc.max())
    tables, moving = [], 0.0
    for ks, ke in segs:
        seg = v_ref[ks:ke + 1]
        D = float(np.sum(0.5 * (seg[1:] + seg[:-1])) * h)
        tables.append(L.eco_segment_tables(pl, D, float(seg.max()), a_lo, a_hi, ds, dv))
        moving += (ke - ks) * h
    T_ref = (len(v_ref) - 1) * h
    return tables, T_ref - moving, T_ref, (a_lo, a_hi)


def _eco_on_other(sol_trip, tables_other):
    """Energy of a trip's speed sequences on another plant's tables (same grids)."""
    E, ok = 0.0, True
    for s, tab in zip(sol_trip["sols"], tables_other):
        idx = np.rint(s["v"] / (tab["v"][1] - tab["v"][0])).astype(int)
        e = tab["E"][idx[:-1], idx[1:]]
        ok &= bool(np.all(np.isfinite(e)))
        E += float(np.sum(e))
    return E, ok


def eco_task(cyc, motor, lim):
    t0 = time.time()
    t, v_ref = reference(cyc)
    d_ref = float(np.sum(0.5 * (v_ref[1:] + v_ref[:-1])) * H)
    rows, vsi, paths = [], [], {}
    trips0 = {}
    tabs = {}
    for pk in ("P1", "P3"):
        pl = plant(motor, lim, pk)
        vb, sse, W, hit = baseline(pl, v_ref)
        eb = _ev(pl, vb, H)
        tables, idle, T_ref, (a_lo, a_hi) = eco_setup(pl, v_ref)
        tabs[pk] = tables
        solver = L.EcoSolver(tables, idle)
        for A in ALLOW:
            s0 = time.time()
            T_target = (1 + A) * T_ref
            best, lam, lb, t_min = solver.for_time(T_target)
            common = dict(cycle=cyc, motor=motor, limits=lim, pstate=pk, allowance=A, d_ref_m=d_ref, T_ref_s=T_ref,
                          T_target_s=T_target, idle_s=idle, a_lo=a_lo, a_hi=a_hi, n_segments=len(tables),
                          t_min_eco_s=t_min, E_b_Wh=eb["E_J"] * J2WH, base_shortfall_pct=100 * (d_ref - eb["dist_m"]) / d_ref)
            if best is None:
                rows.append(dict(common, status="time budget infeasible"))
                continue
            if A == 0.0:
                trips0[pk] = best
            tk, vk = L.eco_profile(best, tables, v_ref, H)
            paths[f"{pk}_A{A:.3f}_t"], paths[f"{pk}_A{A:.3f}_v"] = tk, vk
            ve = np.interp(t, tk, vk)
            rows.append(dict(common, status="ok", E_eco_Wh=best["E"] * J2WH, lb_Wh=lb * J2WH, T_eco_s=best["T_total"],
                             time_change_pct=100 * (best["T_total"] / T_ref - 1), lam_W=lam,
                             S_found_pct=100 * (1 - best["E"] / eb["E_J"]), S_max_pct=100 * (1 - lb / eb["E_J"]),
                             eco_fric_Wh=best["Fb"] * J2WH, eco_Ah=best["Ah"], eco_I2_A2s=best["I2"],
                             base_fric_Wh=eb["fric_J"] * J2WH, base_Ah=eb["Ah"], base_I2_A2s=eb["I2_A2s"],
                             rms_dev_vs_ref_ms=float(np.sqrt(np.mean((ve - v_ref) ** 2))),
                             max_dev_vs_ref_ms=float(np.max(np.abs(ve - v_ref))), max_speed_ms=float(vk.max()),
                             n_lambda_evals=len(solver.cache), runtime_s=time.time() - s0))
    if "P1" in trips0 and "P3" in trips0:
        E13, ok = _eco_on_other(trips0["P1"], tabs["P3"])
        row = dict(cycle=cyc, motor=motor, limits=lim, pstate="P3", allowance=0.0,
                   status="ok" if ok else "P1 eco trip infeasible on P3", E_P3_of_P1trip_Wh=E13 * J2WH,
                   E_P3_star_Wh=trips0["P3"]["E"] * J2WH)
        if ok:
            row["VSI_eco_found_pct"] = 100 * (1 - min(trips0["P3"]["E"], E13) / E13)
        vsi.append(row)
    else:
        vsi.append(dict(cycle=cyc, motor=motor, limits=lim, pstate="P3", allowance=0.0, status="A=0 unavailable"))
    np.savez_compressed(OUT / "paths" / f"eco_{cyc}_{motor}_{lim}.npz", t=t, v_ref=v_ref, **paths)
    return "eco", rows, vsi, time.time() - t0


# --------------------------------------------------------------------------- discretisation checks (protocol 8)
def conv_band():
    t0 = time.time()
    rows = []
    for h, dv in ((1.0, 0.01), (0.5, 0.005)):
        _, v_ref = reference("S1", h)
        pl = plant("M2", "L-EVE", "P3")
        vb, *_ = baseline(pl, v_ref, h)
        eb = L.evaluate(pl, vb, h)
        tab = L.band_tables(pl, vb, h, GATE_DELTA, dv)
        r = L.band_min_energy_tab(pl, tab, eb["dist_m"])
        rows.append(dict(check="band", cycle="S1", motor="M2", limits="L-EVE", pstate="P3", h=h, dv=dv,
                         E_b_Wh=eb["E_J"] * J2WH, E_star_Wh=r["E_J"] * J2WH,
                         H_found_pct=100 * (1 - r["E_J"] / eb["E_J"]), H_max_pct=100 * (1 - r["lb_J"] / eb["E_J"])))
    return "conv", rows, [], time.time() - t0


def conv_eco():
    t0 = time.time()
    rows = []
    _, v_ref = reference("S1")
    pl = plant("M2", "L-EVE", "P1")
    vb, *_ = baseline(pl, v_ref)
    eb = L.evaluate(pl, vb, H)
    for ds, dv in ((DS_ECO, DV_ECO), (1.0, 0.05)):
        tables, idle, T_ref, _ = eco_setup(pl, v_ref, H, ds, dv)
        solver = L.EcoSolver(tables, idle)
        for A in (0.0, 0.05):
            best, lam, lb, t_min = solver.for_time((1 + A) * T_ref)
            rows.append(dict(check="eco", cycle="S1", motor="M2", limits="L-EVE", pstate="P1", ds=ds, dv=dv, allowance=A,
                             status="ok" if best else "infeasible",
                             S_found_pct=100 * (1 - best["E"] / eb["E_J"]) if best else None,
                             S_max_pct=100 * (1 - lb / eb["E_J"]) if best else None))
    return "conv", rows, [], time.time() - t0


def run_one(spec):
    kind, args = spec
    try:
        fn = {"band": band_task, "eco": eco_task, "conv_band": conv_band, "conv_eco": conv_eco}[kind]
        return spec, fn(*args), None
    except Exception:  # noqa: BLE001
        return spec, None, traceback.format_exc()


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(name, rows):
    if not rows:
        return
    keys = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with (OUT / name).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    (OUT / "paths").mkdir(parents=True, exist_ok=True)
    frozen = (L.R3 / "logs" / "protocol_v1_sha256_at_freeze.txt").read_text(encoding="utf-8").split()[0]
    if sha(PROTOCOL) != frozen:
        sys.exit("protocol hash differs from the frozen hash; refusing to run")
    man = {"start": time.strftime("%Y-%m-%dT%H:%M:%S"), "protocol": PROTOCOL.name, "protocol_sha256": sha(PROTOCOL),
           "code": {p.name: sha(p) for p in sorted((L.R3 / "code").glob("*.py"))},
           "data": {p.name: sha(p) for p in sorted((L.R3 / "data").glob("*")) if p.is_file()},
           "python": sys.version, "numpy": np.__version__, "platform": platform.platform(), "workers": a.workers}
    specs = [("band", (c, m, lim)) for c in CYCLES for m in ("M0", "M1", "M2") for lim in LIMS]
    specs += [("eco", (c, m, lim)) for c in CYCLES for m in ("M0", "M1", "M2") for lim in ("L-R1", "L-EVE")]
    specs += [("conv_band", ()), ("conv_eco", ())]
    specs.sort(key=lambda s: 0 if s[0] != "band" and s[0] != "eco" else (1 if "UDDS" in s[1] else 2))
    band, vsi, eco, evsi, conv, errs, times = [], [], [], [], [], [], []
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(run_one, s) for s in specs]
        for i, f in enumerate(as_completed(futs), 1):
            spec, res, err = f.result()
            if err:
                errs.append(dict(kind=spec[0], args=" ".join(spec[1]), traceback=err))
                print(f"[{i}/{len(specs)}] ERROR {spec}", flush=True)
                continue
            kind, rows, v, dt = res
            times.append(dict(kind=spec[0], args=" ".join(spec[1]), runtime_s=dt))
            {"band": band, "eco": eco, "conv": conv}[kind].extend(rows)
            (vsi if kind == "band" else evsi).extend(v)
            print(f"[{i}/{len(specs)}] done {spec} {dt:.0f} s", flush=True)
    write("band_rows.csv", band)
    write("vsi_rows.csv", vsi)
    write("eco_rows.csv", eco)
    write("eco_vsi_rows.csv", evsi)
    write("conv_rows.csv", conv)
    write("task_times.csv", times)
    write("errors.csv", errs or [dict(kind="", args="", traceback="no errors")])
    man["end"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    man["n_tasks"], man["n_errors"] = len(specs), len(errs)
    man["outputs"] = {p.name: sha(p) for p in sorted(OUT.glob("*.csv"))}
    (OUT / "run_manifest.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
    print("errors:", len(errs))
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
