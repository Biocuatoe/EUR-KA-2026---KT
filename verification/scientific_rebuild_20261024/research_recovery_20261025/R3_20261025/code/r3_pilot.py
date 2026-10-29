"""R3 pilots (R3_protocol_v1.md section 5; amendment 1 A1.3-A1.4). Writes under ../outputs/pilot_B and pilot_C.

    python -I r3_pilot.py precheck          # port == R2 sim.py under M0 (A1.3 item 1); must pass before B
    python -I r3_pilot.py B <M0|M1|M2>      # R3-B: tune (192 runs), eval (60 runs), conv (UDDS E3, dt 0.5 ms)
    python -I r3_pilot.py C <M0|M1|M2>      # R3-C: fixed LQR tracks baseline / eco A=0 / eco A=5 % (+ dt 0.5 ms)

Never overwrites an output directory. The closed loop for R3-B is R2's ../pilot/sim.py logic with the
motor model as an argument (functions from r3_lib); R3-C uses r3_lib.simulate as frozen.
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r3_lib as L  # noqa: E402
from eureka.cycles import Profile  # noqa: E402
from eureka.controllers import design_model, dlqr, gain as r1_gain, scheduled_weights, zoh  # noqa: E402
from eureka.params import load_params  # noqa: E402
from eureka.plant import BatchParams  # noqa: E402
from rebuild.model import IX, STATES, BatteryLimits  # noqa: E402
from rebuild.run import load_cycle  # noqa: E402

OUTB = L.R3 / "outputs" / "pilot_B"
OUTC = L.R3 / "outputs" / "pilot_C"
GATES = L.R3 / "outputs" / "gates"
SEED = 20261025
N_CAND = 24
WIN = dict(v_min_ratio=0.78125, v_max_ratio=1.140625)
LIM = {"L-R1": BatteryLimits(c_dis=3.0, c_ch=1.0, **WIN), "L-EVE": BatteryLimits(c_dis=2.0, c_ch=1.0, **WIN),
       "L-EVE-s": BatteryLimits(c_dis=2.0, c_ch=1.0, soh_scaled=True, **WIN)}
SCEN = {"T1": (1.0, 0.5, "L-R1"), "T2": (0.8, 3.5, "L-R1"), "E1": (1.0, 0.5, "L-R1"), "E2": (0.8, 3.5, "L-R1"),
        "E2b": (0.8, 0.5, "L-R1"), "E3": (0.8, 3.5, "L-EVE"), "E4": (0.8, 3.5, "L-EVE-s")}
BRANCHES = {"F0": ("fixed", False), "S0": ("scheduled", False), "F1": ("fixed", True), "S1": ("scheduled", True)}
REQ = dict(shortfall=1.0, rmse=0.10, max_e=1.0)


# --------------------------------------------------------------------------- closed loop (port of R2 sim.py)
def simulate_layer(profile, params, gains, soh, limits, aware, governor, mm, dt=None, d_ref=None):
    n = len(params)
    ts = params[0].Ts
    dt = params[0].dt if dt is None else dt
    sub = round(ts / dt)
    if abs(sub * dt - ts) > 1e-12:
        raise ValueError("Ts must be an integer multiple of dt")
    steps = round(profile.duration / ts)
    gains = np.asarray(gains, dtype=float).reshape(n, 3)
    soh = np.asarray(soh, dtype=float)
    aware = np.asarray(aware, dtype=bool)
    governor = np.asarray(governor, dtype=bool)
    groups = {}
    for j, lim in enumerate(limits):
        groups.setdefault(lim, []).append(j)
    groups = {k: np.array(v) for k, v in groups.items()}
    bps = {k: BatchParams.from_params([params[j] for j in idx], soh[idx]) for k, idx in groups.items()}
    bp = BatchParams.from_params(params, soh)
    gr = bp.G / bp.r_w
    y = np.zeros((n, len(STATES)))
    y[:, IX["SoC"]] = 0.8
    y0 = y.copy()
    z = np.zeros(n)
    rg = np.zeros(n)
    acc = {k: np.zeros(n) for k in ("se2", "max_e", "max_over", "sat_batt", "gov_active", "i2", "max_i", "steps")}
    acc["max_over"][:] = -np.inf
    feasible_all = np.ones(n, dtype=bool)
    nonfinite = np.zeros(n, dtype=bool)
    for k in range(steps + 1):
        v_ref = float(profile.sample(np.array([k * ts]))[0])
        v = y[:, IX["v"]]
        t_pos = np.empty(n)
        base = np.empty(n)
        for lim, idx in groups.items():
            tp, _, b = L.torque_limits(gr[idx] * v[idx], y[idx, IX["V1"]], bps[lim], lim, mm)
            t_pos[idx], base[idx] = tp, b
        if k == 0:
            rg[:] = v_ref
        else:
            w = gr * v
            f_avail = gr * (t_pos - bp.B_m * w) * bp.eta_g
            f_res = bp.Crr * bp.M * bp.g * np.tanh(v / bp.v_eps) + 0.5 * bp.rho * bp.Cd * bp.A_f * v * v
            a_av = (f_avail - f_res) / bp.M_eff
            up = np.minimum(v_ref, rg + np.maximum(a_av, 0.0) * ts)
            rg_new = np.where(v_ref > rg, up, v_ref)
            rg = np.where(governor, rg_new, v_ref)
        e = v - v_ref
        e_c = v - rg
        u = -(gains[:, 0] * e_c + gains[:, 1] * y[:, IX["T"]] + gains[:, 2] * z)
        env = np.where(aware, t_pos, base)
        sat = u > env
        i, _, _, _ = L.battery_current(y[:, IX["T"]], gr * v, y[:, IX["V1"]], bp, mm)
        acc["se2"] += e * e
        acc["max_e"] = np.maximum(acc["max_e"], np.abs(e))
        acc["max_over"] = np.maximum(acc["max_over"], e)
        acc["sat_batt"] += (u > t_pos) & (t_pos < base - 1e-9)
        acc["gov_active"] += rg < v_ref - 1e-9
        acc["i2"] += i * i
        acc["max_i"] = np.maximum(acc["max_i"], np.abs(i))
        acc["steps"] += 1
        nonfinite |= ~np.all(np.isfinite(y), axis=1)
        if k == steps:
            break
        z = np.where(sat & (e_c < 0), z, z + ts * e_c)
        for lim, idx in groups.items():
            yy = y[idx]
            for _ in range(sub):
                yy, feas = L.rk4_step(yy, u[idx], bps[lim], lim, mm, dt)
                feasible_all[idx] &= feas
            y[idx] = yy
    closure, _ = L.energy_closure(y, y0, bp)
    return {"y0": y0, "y_end": y, "acc": acc, "closure_J": closure, "feasible": feasible_all, "nonfinite": nonfinite,
            "ref_distance_m": float(profile.stats()["distance_m"]) if d_ref is None else d_ref, "dt": dt,
            "duration_s": profile.duration}


def metrics(out, j, p):
    y0, y1, a = out["y0"][j], out["y_end"][j], out["acc"]
    m = L.sim_metrics(out, j, p)
    dref = out["ref_distance_m"] / 1000.0
    pos, neg, chem = ((y1[IX[k]] - y0[IX[k]]) for k in ("E_pos", "E_neg", "E_chem"))
    m.update(Wh_per_ref_km=m["E_net_Wh"] / dref, trip_time_s=out["duration_s"],
             max_overshoot_ms=float(a["max_over"][j]) if "max_over" in a else None,
             governor_active_frac=float(a["gov_active"][j] / a["steps"][j]) if "gov_active" in a else None,
             friction_brake_Wh=float((y1[IX["E_fb"]] - y0[IX["E_fb"]]) / 3600.0),
             regen_terminal_Wh=float(-(y1[IX["E_regen"]] - y0[IX["E_regen"]]) / 3600.0),
             I2_A2s=float(a["i2"][j] * p.Ts),                     # sum over control samples x Ts
             recompute_rel=float(abs(pos + neg - chem) / max(abs(pos), 1e-9)))
    return m


# --------------------------------------------------------------------------- gains and candidates
def gain(p, kind, sigma, c, soh, gv=0.0, gu=0.0, qT=1.0):
    Ad, Bd = zoh(*design_model(p), p.Ts)
    Q = np.diag([1 / (p.e_max * sigma) ** 2, qT / p.T_bryson ** 2, 1 / p.z_max ** 2])
    R = np.array([[c / p.T_bryson ** 2]])
    if kind == "scheduled":
        Q, R = scheduled_weights(Q, R, soh, gv, gu)
    K, _, eig = dlqr(Ad, Bd, Q, R)
    return None if np.max(np.abs(eig)) >= 1.0 else K.ravel()


def lhs(kind):
    d = 3 if kind == "fixed" else 4
    x = qmc.LatinHypercube(d=d, rng=np.random.default_rng(SEED)).random(N_CAND)
    out = []
    for r in x:
        if kind == "fixed":                                         # widened box (v1 section 5.1)
            out.append(dict(sigma=10 ** (-0.6 + 0.9 * r[0]), c=10 ** (-2 + 3.48 * r[1]), qT=10 ** (-0.48 * r[2]), gv=0.0, gu=0.0))
        else:                                                       # R2's box
            out.append(dict(sigma=10 ** (-0.6 + 0.9 * r[0]), c=10 ** (-2 + 3 * r[1]), qT=1.0, gv=10 * r[2], gu=10 * r[3]))
    return out


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write_csv(path, rows):
    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with Path(path).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def manifest(outdir, stage, extra):
    m = {"stage": stage, "time": time.strftime("%Y-%m-%dT%H:%M:%S"), "python": sys.version, "numpy": np.__version__,
         "protocol_sha256": sha(L.R3 / "R3_protocol_v1.md"), "amendment_1_sha256": sha(L.R3 / "R3_protocol_v1_amendment_1.md"),
         "code": {p.name: sha(p) for p in sorted((L.R3 / "code").glob("*.py"))},
         "data": {p.name: sha(p) for p in sorted((L.R3 / "data").glob("*")) if p.is_file()}, **extra}
    (Path(outdir) / "manifest.json").write_text(json.dumps(m, indent=1, default=str), encoding="utf-8")


def run_batch(cycle, specs, mm, dt=None):
    prof = load_cycle(cycle)
    out = simulate_layer(prof, [s["p"] for s in specs], np.array([s["K"] for s in specs]), [s["soh"] for s in specs],
                         [s["lim"] for s in specs], [s["aware"] for s in specs], [s["gov"] for s in specs], mm, dt=dt)
    rows = []
    for j, s in enumerate(specs):
        rows.append({**{k: v for k, v in s.items() if k not in ("p", "lim", "K")}, "K": json.dumps([float(x) for x in s["K"]]),
                     "cycle": cycle, "dt_s": out["dt"], **metrics(out, j, s["p"])})
    return rows


# --------------------------------------------------------------------------- precheck (A1.3 item 1)
def precheck():
    sys.path.insert(0, str(L.RR / "pilot"))
    import sim as R2  # noqa: E402  (R2's simulator, read-only)
    outdir = OUTB / "precheck"
    outdir.mkdir(parents=True, exist_ok=False)
    p = load_params().with_overrides(k_r0=3.5)
    Kf = gain(p, "fixed", 1.0, 1.0, 0.8)
    Ks = gain(p, "scheduled", 1.0, 1.0, 0.8, 5.0, 5.0)
    specs = [(K, lay, lk) for K in (Kf, Ks) for lay in (False, True) for lk in ("L-R1", "L-EVE")]
    prof = load_cycle("S2")
    args = ([p] * 8, np.array([s[0] for s in specs]), np.full(8, 0.8), [LIM[s[2]] for s in specs],
            [s[1] for s in specs], [s[1] for s in specs])
    a = R2.simulate(prof, *args)
    b = simulate_layer(prof, *args, L.motor_models()["M0"])
    rows, worst = [], 0.0
    for j in range(8):
        ma, mb = R2.metrics(a, j, p), metrics(b, j, p)
        dE = abs(ma["E_net_Wh"] - mb["E_net_Wh"]) / abs(ma["E_net_Wh"])
        dd = abs(ma["distance_km"] - mb["distance_km"]) / ma["distance_km"]
        worst = max(worst, dE, dd)
        rows.append(dict(run=j, layer=specs[j][1], limits=specs[j][2], E_R2_Wh=ma["E_net_Wh"], E_port_Wh=mb["E_net_Wh"],
                         rel_dE=dE, rel_dd=dd, rmse_R2=ma["rmse_ms"], rmse_port=mb["rmse_ms"]))
    write_csv(outdir / "precheck.csv", rows)
    ok = worst <= 1e-9
    manifest(outdir, "precheck", dict(worst_rel=worst, passed=ok, r2_sim_sha256=sha(L.RR / "pilot" / "sim.py")))
    print("worst relative difference", worst, "PASS" if ok else "FAIL")
    return ok


# --------------------------------------------------------------------------- R3-B
def stage_B(mk):
    if not json.loads((OUTB / "precheck" / "manifest.json").read_text(encoding="utf-8"))["passed"]:
        sys.exit("precheck did not pass; R3-B not run")
    mm = L.motor_models()[mk]
    root = OUTB / mk
    root.mkdir(parents=True, exist_ok=False)
    base = load_params()
    # tune -----------------------------------------------------------------
    t0 = time.time()
    specs, unstable = [], []
    for br, (kind, layer) in BRANCHES.items():
        for ci, c in enumerate(lhs(kind)):
            for sc in ("T1", "T2"):
                soh, kr, lk = SCEN[sc]
                p = base.with_overrides(k_r0=kr)
                K = gain(p, kind, c["sigma"], c["c"], soh, c["gv"], c["gu"], c["qT"])
                if K is None:
                    unstable.append(dict(branch=br, cand=ci, scen=sc, **c))
                    continue
                specs.append(dict(branch=br, cand=ci, scen=sc, soh=soh, k_r0=kr, limits=lk, aware=layer, gov=layer,
                                  p=p, lim=LIM[lk], K=K, **c))
    rows = run_batch("S1", specs, mm)
    write_csv(root / "tune_candidates.csv", rows)
    write_csv(root / "tune_unstable.csv", unstable or [dict(branch="none")])
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
        feas = [s for s in scored if not s[0]]
        if feas:
            emin = min(s[1] for s in feas)
            best = min([s for s in feas if (s[1] - emin) / emin < 1e-6], key=lambda s: s[2])
            rule = "min mean Wh/ref-km among feasible"
        else:
            best = min(scored, key=lambda s: s[2])
            rule = "NO FEASIBLE CANDIDATE: min mean RMSE"
        r0 = best[4][0]
        sel[br] = dict(cand=best[3], sigma=r0["sigma"], c=r0["c"], qT=r0["qT"], gv=r0["gv"], gu=r0["gu"],
                       mean_Wh_ref_km=float(best[1]), mean_rmse=float(best[2]), n_feasible=len(feas), n_evaluated=len(scored), rule=rule)
    (root / "tune_selected.json").write_text(json.dumps(sel, indent=1), encoding="utf-8")
    t_tune = time.time() - t0
    print(mk, "tuned", round(t_tune), "s", json.dumps({b: (s["cand"], s["n_feasible"]) for b, s in sel.items()}), flush=True)
    # eval -----------------------------------------------------------------
    t0 = time.time()

    def eval_specs():
        out = []
        for sc in ("E1", "E2", "E2b", "E3", "E4"):
            soh, kr, lk = SCEN[sc]
            p = base.with_overrides(k_r0=kr)
            for br, (kind, layer) in BRANCHES.items():
                c = sel[br]
                K = gain(p, kind, c["sigma"], c["c"], soh, c["gv"], c["gu"], c["qT"])
                out.append(dict(branch=br, scen=sc, soh=soh, k_r0=kr, limits=lk, aware=layer, gov=layer, p=p, lim=LIM[lk], K=K,
                                **{k: c[k] for k in ("sigma", "c", "qT", "gv", "gu")}))
        return out

    ev = []
    for cyc in ("S1", "S2", "UDDS"):
        ev += run_batch(cyc, eval_specs(), mm)
    write_csv(root / "eval_runs.csv", ev)
    t_eval = time.time() - t0
    print(mk, "evaluated", round(t_eval), "s", flush=True)
    # conv -----------------------------------------------------------------
    t0 = time.time()
    cv = run_batch("UDDS", [s for s in eval_specs() if s["scen"] == "E3"], mm, dt=0.0005)
    write_csv(root / "conv_dt0.5ms.csv", cv)
    sched_chk = max(float(np.max(np.abs(gain(base, "scheduled", c["sigma"], c["c"], 1.0, c["gv"], c["gu"])
                                        - gain(base, "fixed", c["sigma"], c["c"], 1.0)))) for b, c in sel.items() if b.startswith("S"))
    manifest(root, "B", dict(motor=mk, n_tune=len(rows), n_unstable=len(unstable), n_eval=len(ev), n_conv=len(cv),
                             runtime_s=dict(tune=t_tune, eval=t_eval, conv=time.time() - t0),
                             sched_equals_fixed_at_soh1_maxabs=sched_chk,
                             n_invalid=sum(not r["valid"] for r in rows + ev + cv)))
    print(mk, "done", flush=True)


# --------------------------------------------------------------------------- R3-C
def _gate_rows(name):
    with (GATES / name).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def stage_C(mk):
    mm = L.motor_models()[mk]
    root = OUTC / mk
    root.mkdir(parents=True, exist_ok=False)
    p = load_params().with_overrides(k_r0=0.5)                      # P1
    K = r1_gain(p, "fixed")
    band = _gate_rows("band_rows.csv")
    eco = _gate_rows("eco_rows.csv")
    rows = []
    t0 = time.time()
    for cyc in ("S2", "UDDS"):
        for lk in ("L-R1", "L-EVE"):
            zb = np.load(GATES / "paths" / f"band_{cyc}_{mk}_{lk}.npz")
            ze = np.load(GATES / "paths" / f"eco_{cyc}_{mk}_{lk}.npz")
            d_ref = float(np.sum(0.5 * (zb["v_ref"][1:] + zb["v_ref"][:-1])))
            brow = next(r for r in band if (r["cycle"], r["motor"], r["limits"], r["pstate"], r["delta"]) == (cyc, mk, lk, "P1", "0.05"))
            profs = {"baseline": (zb["t"], zb["P1_baseline"], float(brow["E_b_Wh"]), None)}
            for A, tag in ((0.0, "eco_A0"), (0.05, "eco_A5")):
                er = next(r for r in eco if (r["cycle"], r["motor"], r["limits"], r["pstate"], float(r["allowance"])) == (cyc, mk, lk, "P1", A))
                kt, kv = f"P1_A{A:.3f}_t", f"P1_A{A:.3f}_v"
                profs[tag] = (ze[kt], ze[kv], float(er["E_eco_Wh"]), float(er["S_found_pct"])) if kt in ze else None
            for tag, pr in profs.items():
                base_row = dict(cycle=cyc, motor=mk, limits=lk, pstate="P1", profile=tag)
                if pr is None:
                    rows.append(dict(base_row, status="profile unavailable (eco time budget infeasible)"))
                    continue
                kt, kv, e_qs, s_dp = pr
                prof = Profile(f"{cyc}_{tag}", np.asarray(kt, float), np.asarray(kv, float))
                for dt in ((None, 0.0005) if lk == "L-EVE" else (None,)):
                    s0 = time.time()
                    out = L.simulate(prof, [p], np.array([K]), np.array([1.0]), LIM[lk], mm, dt=dt)
                    out["ref_distance_m"], out["duration_s"] = d_ref, prof.duration
                    m = metrics(out, 0, p)
                    rows.append(dict(base_row, status="ok", dt_s=out["dt"], QS_E_Wh=e_qs, DP_saving_pct=s_dp,
                                     QS_vs_dyn_pct=100 * (m["E_net_Wh"] - e_qs) / e_qs,
                                     complete=m["shortfall_pct"] <= 1.0, tracking_ok=m["rmse_ms"] <= 0.10,
                                     runtime_s=time.time() - s0, **m))
                    print(mk, cyc, lk, tag, "dt", out["dt"], round(time.time() - s0), "s", flush=True)
    write_csv(root / "runs.csv", rows)
    # fixed 2026-10-25 18:40: K is 1 x 3; the first runs crashed here after runs.csv was written (logs/pilot_C_*.err.txt)
    manifest(root, "C", dict(motor=mk, n_runs=len(rows), runtime_s=time.time() - t0, gain=[float(x) for x in np.ravel(K)]))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    cmd = sys.argv[1]
    if cmd == "precheck":
        sys.exit(0 if precheck() else 1)
    {"B": stage_B, "C": stage_C}[cmd](sys.argv[2])
