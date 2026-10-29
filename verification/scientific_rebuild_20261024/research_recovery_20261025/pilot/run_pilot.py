"""P2-pilot driver (pilot_protocol.md). Writes only under ./out/<stage>/ and never overwrites a stage.

    python run_pilot.py tune     # 4 branches x 24 LHS candidates x {T1, T2} on S1  (192 runs)
    python run_pilot.py eval     # tuned branches x {E1, E2, E2b, E3, E4} x {S1, S2, UDDS} (+1 sanity run)
    python run_pilot.py conv     # UDDS E3, 4 branches, dt = 0.5 ms
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.stats import qmc

HERE = Path(__file__).resolve().parent
RR = HERE.parent                       # research_recovery_20261025
R1 = RR.parent                         # scientific_rebuild_20261024
REPO = R1.parents[1]
sys.path[:0] = [str(REPO / "src"), str(R1 / "src"), str(HERE)]

from eureka.controllers import design_model, dlqr, scheduled_weights, zoh  # noqa: E402
from eureka.lineage import run_context  # noqa: E402
from eureka.params import load_params  # noqa: E402
from rebuild.model import BatteryLimits  # noqa: E402
from rebuild.run import load_cycle  # noqa: E402
from sim import metrics, simulate  # noqa: E402

SEED = 20261025
N_CAND = 24
WIN = dict(v_min_ratio=0.78125, v_max_ratio=1.140625)
SCEN = {  # pilot_protocol.md section 3
    "T1": dict(soh=1.0, k_r0=3.5, lim=BatteryLimits(c_dis=3.0, c_ch=1.0, **WIN)),
    "T2": dict(soh=0.8, k_r0=3.5, lim=BatteryLimits(c_dis=3.0, c_ch=1.0, **WIN)),
    "E1": dict(soh=1.0, k_r0=3.5, lim=BatteryLimits(c_dis=3.0, c_ch=1.0, **WIN)),
    "E2": dict(soh=0.8, k_r0=3.5, lim=BatteryLimits(c_dis=3.0, c_ch=1.0, **WIN)),
    "E2b": dict(soh=0.8, k_r0=0.5, lim=BatteryLimits(c_dis=3.0, c_ch=1.0, **WIN)),
    "E3": dict(soh=0.8, k_r0=3.5, lim=BatteryLimits(c_dis=2.0, c_ch=0.5, **WIN)),
    "E4": dict(soh=0.8, k_r0=3.5, lim=BatteryLimits(c_dis=2.0, c_ch=0.5, soh_scaled=True, **WIN)),
}
BRANCHES = {"F0": ("fixed", False), "S0": ("scheduled", False), "F1": ("fixed", True), "S1": ("scheduled", True)}
REQ = dict(shortfall=1.0, rmse=0.10, max_e=1.0)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def gain(p, kind, sigma, c, soh, gv=0.0, gu=0.0):
    Ad, Bd = zoh(*design_model(p), p.Ts)
    Q = np.diag([1 / (p.e_max * sigma) ** 2, 1 / p.T_bryson**2, 1 / p.z_max**2])
    R = np.array([[c / p.T_bryson**2]])
    if kind == "scheduled":
        Q, R = scheduled_weights(Q, R, soh, gv, gu)
    K, _, eig = dlqr(Ad, Bd, Q, R)
    return None if np.max(np.abs(eig)) >= 1.0 else K.ravel()


def lhs(kind):
    d = 2 if kind == "fixed" else 4
    try:
        eng = qmc.LatinHypercube(d=d, rng=np.random.default_rng(SEED))
    except TypeError:
        eng = qmc.LatinHypercube(d=d, seed=SEED)
    x = eng.random(N_CAND)
    cands = []
    for r in x:
        c = dict(sigma=10 ** (-0.6 + 0.9 * r[0]), c=10 ** (-2 + 3 * r[1]), gv=0.0, gu=0.0)
        if kind == "scheduled":
            c.update(gv=10 * r[2], gu=10 * r[3])
        cands.append(c)
    return cands


def manifest(outdir: Path, stage: str, extra: dict) -> None:
    files = [RR / "pilot_protocol.md", HERE / "sim.py", HERE / "run_pilot.py",
             *sorted((R1 / "src" / "rebuild").glob("*.py")), *sorted((REPO / "src" / "eureka").glob("*.py")),
             REPO / "configs" / "parameters.yaml"]
    m = {"stage": stage, "context": run_context(), "seed": SEED, "n_candidates": N_CAND,
         "protocol_sha256": sha(RR / "pilot_protocol.md"),
         "protocol_sha256_at_freeze": (HERE / "protocol_sha256_at_freeze.txt").read_text().split()[0],
         "file_sha256": {str(f.relative_to(REPO)): sha(f) for f in files}, **extra}
    (outdir / "manifest.json").write_text(json.dumps(m, indent=1, default=str), encoding="utf-8")


def write_csv(path: Path, rows: list[dict]) -> None:
    keys: list[str] = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def run_batch(cycle, specs, dt=None):
    prof = load_cycle(cycle)
    out = simulate(prof, [s["p"] for s in specs], np.array([s["K"] for s in specs]), np.array([s["soh"] for s in specs]),
                   [s["lim"] for s in specs], [s["aware"] for s in specs], [s["gov"] for s in specs], dt=dt)
    rows = []
    for j, s in enumerate(specs):
        rows.append({**{k: v for k, v in s.items() if k not in ("p", "lim", "K")}, "K": json.dumps([float(x) for x in s["K"]]),
                     "cycle": cycle, "dt_s": out["dt"], **metrics(out, j, s["p"])})
    return rows


def stage_tune():
    outdir = HERE / "out" / "tune"
    outdir.mkdir(parents=True, exist_ok=False)
    base = load_params()
    specs, infeasible = [], []
    for br, (kind, layer) in BRANCHES.items():
        for ci, c in enumerate(lhs(kind)):
            for sc in ("T1", "T2"):
                S = SCEN[sc]
                p = base.with_overrides(k_r0=S["k_r0"])
                K = gain(p, kind, c["sigma"], c["c"], S["soh"], c["gv"], c["gu"])
                if K is None:
                    infeasible.append(dict(branch=br, cand=ci, scen=sc, **c))
                    continue
                specs.append(dict(branch=br, cand=ci, scen=sc, soh=S["soh"], k_r0=S["k_r0"], aware=layer, gov=layer,
                                  p=p, lim=S["lim"], K=K, **c))
    t0 = time.time()
    rows = run_batch("S1", specs)
    write_csv(outdir / "candidates.csv", rows)
    # selection (protocol section 4)
    sel = {}
    for br in BRANCHES:
        by = {}
        for r in rows:
            if r["branch"] == br:
                by.setdefault(r["cand"], []).append(r)
        scored = []
        for ci, rs in by.items():
            if len(rs) != 2 or not all(r["valid"] for r in rs):
                continue
            ok = all(r["shortfall_pct"] <= REQ["shortfall"] and r["rmse_ms"] <= REQ["rmse"] and r["max_abs_err_ms"] <= REQ["max_e"] for r in rs)
            scored.append((not ok, np.mean([r["Wh_per_ref_km"] for r in rs]), np.mean([r["rmse_ms"] for r in rs]), ci, rs))
        n_ok = sum(not s[0] for s in scored)
        feas = [s for s in scored if not s[0]]
        if feas:
            emin = min(s[1] for s in feas)
            tied = [s for s in feas if (s[1] - emin) / emin < 1e-6]
            best = min(tied, key=lambda s: s[2])
            rule = "min mean Wh/ref-km among feasible"
        else:
            best = min(scored, key=lambda s: s[2])
            rule = "NO FEASIBLE CANDIDATE: min mean RMSE"
        r0 = best[4][0]
        sel[br] = dict(cand=best[3], sigma=r0["sigma"], c=r0["c"], gv=r0["gv"], gu=r0["gu"], mean_Wh_ref_km=best[1],
                       mean_rmse=best[2], n_feasible=n_ok, n_evaluated=len(scored), rule=rule)
    (outdir / "selected.json").write_text(json.dumps(sel, indent=1), encoding="utf-8")
    write_csv(outdir / "unstable.csv", infeasible or [dict(branch="none")])
    manifest(outdir, "tune", dict(n_runs=len(rows), n_unstable=len(infeasible), runtime_s=round(time.time() - t0, 1),
                                  n_invalid=sum(not r["valid"] for r in rows)))
    print(json.dumps(sel, indent=1))


def eval_specs(sel):
    base = load_params()
    specs = []
    for sc in ("E1", "E2", "E2b", "E3", "E4"):
        S = SCEN[sc]
        p = base.with_overrides(k_r0=S["k_r0"])
        for br, (kind, layer) in BRANCHES.items():
            c = sel[br]
            K = gain(p, kind, c["sigma"], c["c"], S["soh"], c["gv"], c["gu"])
            specs.append(dict(branch=br, scen=sc, soh=S["soh"], k_r0=S["k_r0"], aware=layer, gov=layer, p=p, lim=S["lim"], K=K,
                              sigma=c["sigma"], c=c["c"], gv=c["gv"], gu=c["gu"]))
    return specs


def stage_eval():
    outdir = HERE / "out" / "eval"
    outdir.mkdir(parents=True, exist_ok=False)
    sel = json.loads((HERE / "out" / "tune" / "selected.json").read_text(encoding="utf-8"))
    # sanity: a scheduled gain at SoH 1.0 equals its base fixed gain
    p = load_params()
    chk = max(float(np.max(np.abs(gain(p, "scheduled", c["sigma"], c["c"], 1.0, c["gv"], c["gu"]) - gain(p, "fixed", c["sigma"], c["c"], 1.0))))
              for c in sel.values())
    t0 = time.time()
    rows = []
    for cyc in ("S1", "S2", "UDDS"):
        specs = eval_specs(sel)
        if cyc == "S2":  # R1 reproduction spot check: R1 gain F, BCN, SoH 1.0, k_r0 0.5, layer off
            pr = load_params().with_overrides(k_r0=0.5)
            specs.append(dict(branch="SANITY_R1_F", scen="R1_BCN_soh1", soh=1.0, k_r0=0.5, aware=False, gov=False, p=pr,
                              lim=BatteryLimits(c_dis=3.0, c_ch=1.0, **WIN), K=gain(pr, "fixed", 1.0, 1.0, 1.0),
                              sigma=1.0, c=1.0, gv=0.0, gu=0.0))
        rows += run_batch(cyc, specs)
        print(cyc, "done", round(time.time() - t0), "s", flush=True)
    write_csv(outdir / "runs.csv", rows)
    manifest(outdir, "eval", dict(n_runs=len(rows), runtime_s=round(time.time() - t0, 1), sched_equals_fixed_at_soh1_maxabs=chk,
                                  n_invalid=sum(not r["valid"] for r in rows)))


def stage_conv():
    outdir = HERE / "out" / "conv"
    outdir.mkdir(parents=True, exist_ok=False)
    sel = json.loads((HERE / "out" / "tune" / "selected.json").read_text(encoding="utf-8"))
    specs = [s for s in eval_specs(sel) if s["scen"] == "E3"]
    t0 = time.time()
    rows = run_batch("UDDS", specs, dt=0.0005)
    write_csv(outdir / "runs_dt0.5ms.csv", rows)
    manifest(outdir, "conv", dict(n_runs=len(rows), runtime_s=round(time.time() - t0, 1), dt=0.0005))


if __name__ == "__main__":
    {"tune": stage_tune, "eval": stage_eval, "conv": stage_conv}[sys.argv[1]]()
