"""Vertical slice: one scenario, one B0/B3 trajectory pair (implementation smoke test, not a result).

    python -I -B code/run_slice.py --cycle S1 --motor M0 --limits L-R1 --pstate P1

Stops (writing a status record, never a result) if: frozen hashes differ; the pre-run gate record is
missing, its code hashes differ from the code on disk, or its test run had failures; either trajectory
is invalid; the trace cannot be written or read back; the evaluator disagrees with the simulator.
It never computes an energy difference between the arms.
"""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import sys
import time
import traceback
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

from r4h3 import SCHEMA_VERSION, frozen

PILOT = frozen.PILOT
GATE_FILE = PILOT / "logs" / "pre_run_hashes.txt"


# --------------------------------------------------------------------------- pre-run gate (protocol 10.1)
def code_files():
    files = sorted((PILOT / "code").rglob("*.py")) + [PILOT / "code" / "pytest.ini"]
    files += sorted((PILOT / "config").glob("*.json"))
    return [f for f in files if "__pycache__" not in f.parts]


def code_hashes():
    return {f.relative_to(PILOT).as_posix(): frozen.sha256(f) for f in code_files()}


def junit_summary(path):
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    return {k: sum(int(s.get(k, 0)) for s in suites) for k in ("tests", "failures", "errors", "skipped")}


def check_gate():
    if not GATE_FILE.is_file():
        raise RuntimeError("pre-run gate record logs/pre_run_hashes.txt is missing")
    rec = json.loads(GATE_FILE.read_text(encoding="utf-8"))
    if rec["protocol_sha256"] != frozen.FROZEN_SHA256[frozen.PROTOCOL]:
        raise RuntimeError("gate record protocol hash differs from the frozen value")
    now = code_hashes()
    if now != rec["code_sha256"]:
        diff = sorted(set(now.items()) ^ set(rec["code_sha256"].items()))
        raise RuntimeError(f"code or config changed since the gate record: {diff[:4]}")
    j = PILOT / rec["junit_xml"]
    if frozen.sha256(j) != rec["junit_sha256"]:
        raise RuntimeError("junit record changed since the gate record")
    s = junit_summary(j)
    if s["tests"] == 0 or s["failures"] or s["errors"]:
        raise RuntimeError(f"test run not clean: {s}")
    return rec, s


# --------------------------------------------------------------------------- helpers
def write_csv(path, rows):
    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def sim_stop_ok(tr, rest, rules):
    """Simulator-side stop check from the integrated position state (evaluator uses trapz of v)."""
    t, v, x = tr["t_s"], tr["v_mps"], tr["int_dist"]
    ok = True
    for t_a, t_d in rest:
        if t_d - t_a < rules["stop_min_duration_s"] - 1e-9:
            continue
        sel = np.flatnonzero((t >= t_a + rules["stop_settle_s"] - 1e-12) & (t <= t_d + 1e-12))
        ok &= bool(np.max(np.abs(v[sel])) <= rules["stop_speed_max_ms"]
                   and x[sel[-1]] - x[sel[0]] <= rules["stop_distance_max_m"])
    return ok


def eval_spec(cfg, p, soh, lim, sid, task, dt, Ts):
    from r4h3 import evaluator
    return {
        "battery": dict(V_oc=p.V_oc, R0=p.R0_new * (1 + p.k_r0 * (1 - soh)), Q_Ah=p.Q_Ah, c_dis=lim.c_dis,
                        c_ch=lim.c_ch, v_min_ratio=lim.v_min_ratio, v_max_ratio=lim.v_max_ratio),
        "motor": evaluator.motor_spec_from_protocol(sid, frozen.M1_CURVE),
        "G": p.G, "r_w": p.r_w, "v_eps": p.v_eps, "T_max": p.T_max, "P_max": p.P_max, "B_m": p.B_m, "eta_g": p.eta_g,
        "M_eff": p.M_eff, "C1": p.C1, "Ts_s": Ts, "dt_s": dt, "d_ref_m": task.d_ref,
        "rest_intervals": [list(r) for r in task.rest],
    }


# --------------------------------------------------------------------------- slice
def run(cycle, motor, limits, pstate, dt=None, name=None):
    t_start = time.time()
    tag = name or f"slice_{cycle}_{motor}_{limits}_{pstate}"
    outdir = PILOT / "outputs" / tag
    outdir.mkdir(parents=True, exist_ok=False)
    log = open(outdir / "execution_log.txt", "w", encoding="utf-8")
    manifest = {"kind": "H3 vertical slice (implementation smoke test; not a result)", "tag": tag,
                "start": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "status": "started", "errors": [], "stops": []}

    def say(*msg):
        s = " ".join(str(m) for m in msg)
        print(s, flush=True)
        log.write(s + "\n")
        log.flush()

    def stop(reason):
        manifest["status"] = "STOPPED"
        manifest["stops"].append(reason)
        say("STOP:", reason)

    try:
        manifest["frozen_inputs"] = frozen.verify_frozen()
        say("frozen inputs verified:", json.dumps(manifest["frozen_inputs"], indent=0))
        gate, junit = check_gate()
        manifest["gate"] = {"record": str(GATE_FILE.relative_to(PILOT)), "record_sha256": frozen.sha256(GATE_FILE),
                            "junit": junit}
        say("pre-run gate ok:", junit)

        from r4h3 import config, evaluator, planner, task as taskmod, traces, validator
        from r4h3.closedloop import (TRACE_DT, fixed_gain, profile_from_knots, run_metrics, simulate_traced,
                                     trace_constraint_metrics)
        L = config.L
        tk = taskmod.load_task(cycle)
        p = config.params_for(pstate)
        soh = config.PSTATES[pstate]["soh"]
        lim = config.LIMITS[limits]
        mm = config.motor_model(motor)
        plant = L.QSPlant(p, soh, lim, mm)
        design = L.QSPlant(config.params_for("P1"), config.PSTATES["P1"]["soh"], lim, mm)   # B3 designed on P1
        dt = p.dt if dt is None else dt
        say(f"task {cycle}: d_ref {tk.d_ref:.6f} m, T_ref {tk.T_ref} s, {len(tk.rest)} rest intervals, "
            f"{len(tk.segs)} segments; cycle definition {tk.profile_duration:.6f} s / {tk.profile_distance:.6f} m (AMB-01)")
        config.write_scenario_record(outdir / "scenario_config.json")

        # ---------------------------------------------------------------- trajectories
        vb = planner.baseline_task(plant, tk)
        val_b = validator.validate_trajectory(tk, tk.t, vb["v_b"], plant, "B0 v_b")
        say("baseline task: equals reference", vb["equals_reference"], "W", vb["W"], "| valid", val_b["valid"],
            val_b["failures"])
        eco = planner.plan_seco(design, tk)
        write_csv(outdir / "planner_rows.csv", eco["rows"])
        if eco["status"] != "ok":
            stop(f"S-eco profile unavailable: {eco['status']}")
            return manifest
        np.savez_compressed(outdir / "profiles.npz", t_task=tk.t, v_ref=tk.v_ref, v_b=vb["v_b"], t_seco=eco["t"],
                            v_seco=eco["v"])
        val_e = validator.validate_trajectory(tk, eco["t"], eco["v"], plant, "B3 S-eco")
        say("S-eco: valid", val_e["valid"], val_e["failures"], "| extra-stop knots",
            sum(s["n_extra_stops"] for s in val_e["segments"]))
        (outdir / "trajectory_validation.json").write_text(json.dumps({"B0": val_b, "B3": val_e}, indent=1, default=float),
                                                           encoding="utf-8")
        if not (val_b["valid"] and val_e["valid"]):
            stop("trajectory validation failed; no dynamic run")
            return manifest

        # ---------------------------------------------------------------- closed loop, traces, evaluation
        K = fixed_gain(config.params_for("P1"))
        spec = eval_spec(config, p, soh, lim, motor, tk, TRACE_DT, p.Ts)      # trace step, not dt (CR-A1)
        run_cfg = dict(cycle=cycle, motor_scenario=motor, limits=limits, pstate=pstate, soh=soh, dt_s=dt, Ts_s=p.Ts,
                       gain=[float(x) for x in K], params=p.as_dict(), rules=config.RULES, eval_spec=spec,
                       schema=SCHEMA_VERSION)
        cfg_json = json.dumps(run_cfg, sort_keys=True, default=float)
        cfg_sha = hashlib.sha256(cfg_json.encode()).hexdigest()
        (outdir / "run_config.json").write_text(cfg_json, encoding="utf-8")
        sim_rows, ev_rows, stop_rows, cmp_all, run_files = [], [], [], {}, {}
        for branch, (kt, kv) in (("B0", (tk.t, vb["v_b"])), ("B3", (eco["t"], eco["v"]))):
            run_id = f"H3-slice-{cycle}-{motor}-{limits}-{pstate}-{branch}-dt{dt * 1e3:g}ms"
            prof = profile_from_knots(run_id, kt, kv)
            s0 = time.time()
            out, tr = simulate_traced(prof, p, K, soh, lim, mm, dt=dt)
            sim = run_metrics(out, p, soh, tk.d_ref, prof.duration, p.Ts)
            tr["v_ref_task_mps"] = np.interp(tr["t_s"], tk.t, tk.v_ref)
            tr["stop_ref_flag"] = np.zeros_like(tr["t_s"])
            for t_a, t_d in tk.rest:
                tr["stop_ref_flag"][(tr["t_s"] >= t_a - 1e-12) & (tr["t_s"] <= t_d + 1e-12)] = 1.0
            sim["stop_ok_sim"] = sim_stop_ok(tr, tk.rest, config.RULES)
            sim.update(trace_constraint_metrics(tr, p, lim, config.RULES))
            sim.update(run_id=run_id, branch=branch, cycle=cycle, motor_scenario=motor, limits=limits, pstate=pstate,
                       dt_s=dt, runtime_s=time.time() - s0, n_samples=len(tr["t_s"]))
            meta = dict(run_id=run_id, schema_version=SCHEMA_VERSION, branch=branch, cycle=cycle, motor_scenario=motor,
                        limits=limits, pstate=pstate, soh=soh, dt_s=dt, trace_dt_s=out["trace_dt"], Ts_s=p.Ts,
                        initial_conditions=dict(v=0.0, T=0.0, V1=0.0, SoC=0.8, z=0.0), config_sha256=cfg_sha,
                        gain=[float(x) for x in K], d_ref_m=tk.d_ref, T_ref_s=tk.T_ref, seed=None,
                        tracked_profile="v_b (baseline task)" if branch == "B0" else "S-eco (protocol 5)")
            tpath = outdir / f"trace_{run_id}.npz"
            tsha = traces.write_trace(tpath, tr, meta)
            a, meta_back, _ = traces.read_trace(tpath)                       # evaluate what was retained
            ev = evaluator.evaluate_trace(a, spec, config.RULES)
            cmp = evaluator.compare_with_simulator(ev, sim, config.RULES)
            sim_valid = bool(sim["valid"])
            comparable = sim_valid and ev["complete"] and ev["tracking_ok"] and ev["stop_ok"] and ev["constraint_ok"] \
                and ev["finite_ok"]
            for r in ev.pop("stop_rows"):
                stop_rows.append(dict(run_id=run_id, **r))
            ev_rows.append(dict(run_id=run_id, branch=branch, motor_scenario=motor, cycle=cycle, limits=limits,
                                pstate=pstate, sim_valid=sim_valid, comparable=comparable,
                                recompute_all_ok=cmp["all_ok"], **ev))
            sim_rows.append(sim)
            cmp_all[run_id] = cmp
            run_files[run_id] = {"trace": tpath.name, "trace_sha256": tsha, "n_samples": len(a["t_s"])}
            say(f"{run_id}: {sim['runtime_s']:.0f} s, sim valid {sim_valid} ({sim['invalid_reasons']}), complete "
                f"{ev['complete']}, tracking {ev['tracking_ok']}, stops {ev['stop_ok']} ({ev['n_stops_tested']} tested), "
                f"constraints {ev['constraint_ok']}, recomputation {cmp['all_ok']}")
            for k_, c_ in cmp.items():
                if k_ != "all_ok":
                    say(f"    {k_}: {c_['value']} (tol {c_['tol']}) {'ok' if c_['ok'] else 'FAIL'}")
        evaluator.refuse_pooling(ev_rows)
        write_csv(outdir / "runs.csv", sim_rows)
        write_csv(outdir / "evaluation.csv", ev_rows)
        write_csv(outdir / "stop_compliance.csv", stop_rows)
        (outdir / "recomputation.json").write_text(json.dumps(cmp_all, indent=1), encoding="utf-8")
        ok = all(r["comparable"] and r["recompute_all_ok"] for r in ev_rows)
        manifest.update(status="PASS" if ok else "FAILED-CHECKS", runs=run_files, config_sha256=cfg_sha,
                        checks={r["run_id"]: {k: r[k] for k in ("sim_valid", "complete", "tracking_ok", "stop_ok",
                                                                 "constraint_ok", "finite_ok", "recompute_all_ok",
                                                                 "comparable")} for r in ev_rows})
        if not ok:
            stop("at least one run failed a validity or recomputation check (diagnose; nothing is relaxed)")
        say("no energy difference between the arms is computed (smoke test)")
    except Exception as e:  # noqa: BLE001
        manifest["status"] = "ERROR"
        manifest["errors"].append(traceback.format_exc())
        say("ERROR:", repr(e))
        say(traceback.format_exc())
    finally:
        manifest.update(end=time.strftime("%Y-%m-%dT%H:%M:%S%z"), wall_s=time.time() - t_start,
                        python=sys.version, executable=sys.executable, numpy=np.__version__, machine=platform.node(),
                        inputs={"profiles_yaml": str(frozen.PROFILES_YAML), "profiles_yaml_sha256": frozen.sha256(frozen.PROFILES_YAML),
                                "m1_curve": str(frozen.M1_CURVE), "r3_lib": str(frozen.R3_LIB), "protocol": str(frozen.PROTOCOL)},
                        seed=None, args=dict(cycle=cycle, motor=motor, limits=limits, pstate=pstate, dt=dt))
        try:
            import scipy
            manifest["scipy"] = scipy.__version__
        except Exception:  # noqa: BLE001
            pass
        log.close()
        manifest["outputs"] = {f.name: frozen.sha256(f) for f in sorted(outdir.iterdir()) if f.is_file()}
        (outdir / "manifest.json").write_text(json.dumps(manifest, indent=1, default=str), encoding="utf-8")
    return manifest
