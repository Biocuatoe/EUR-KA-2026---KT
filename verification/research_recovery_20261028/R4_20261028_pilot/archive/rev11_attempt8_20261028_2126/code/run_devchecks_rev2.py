"""Rev2 development checks and tolerance evidence (S1 and synthetic only; NOT campaign runs).

    python -I -B code/run_devchecks_rev2.py

Writes outputs/dev_rev2_<timestamp>/ (never overwritten); reads, never modifies, earlier outputs:
  R2-1  re-evaluate the DEV-4 trace (S1, M0, L-R1, 0.5 ms) with the rev2 evaluator (independent torque limits) in a
        separate process (recompute_from_traces.py --out)
  R2-2  one S1 run, B0 tracking v_b, M1, L-EVE, P1, 1 ms: the case where r3_lib's table inverse and the evaluator's
        bisection differ; recomputed in-process and in a separate process
  R2-3  tolerance evidence for amendment A1-12: floating-point bounds and the smallest structural errors for trip
        time, the protocol 8.2 I_over and RMSE (10_tolerance_approval_register.md)
No energy difference between arms, no S_found and no saving is computed. S2 is not used.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.stdout.reconfigure(encoding="utf-8")

import numpy as np  # noqa: E402

from r4h3 import campaign, config, evaluator, frozen, inputs, traces  # noqa: E402
from r4h3 import task as taskmod  # noqa: E402
from r4h3.closedloop import fixed_gain, profile_from_knots, run_metrics, simulate_traced, trace_constraint_metrics  # noqa: E402

DEV4 = frozen.PILOT / "outputs" / "dev_readiness_20261028_061453"


def recompute(src: Path, dest: Path):
    r = subprocess.run([sys.executable, "-I", "-B", str(HERE / "recompute_from_traces.py"), str(src), "--out", str(dest)],
                       capture_output=True, text=True, timeout=3600)
    return dict(exit=r.returncode, stdout=r.stdout.strip(), stderr=r.stderr.strip()[-2000:])


def main() -> int:
    gate = json.loads(campaign.READINESS_GATE.read_text(encoding="utf-8"))
    from r4h3.slice import code_hashes
    if gate["code_sha256"] != code_hashes():
        raise SystemExit("STOP: code differs from the readiness gate record")
    out = frozen.PILOT / "outputs" / f"dev_rev2_{time.strftime('%Y%m%d_%H%M%S')}"
    out.mkdir(parents=True, exist_ok=False)
    rec = {"kind": "rev2 development checks and tolerance evidence (S1/synthetic; not campaign runs)",
           "start": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "readiness_gate_sha256": frozen.sha256(campaign.READINESS_GATE),
           "frozen": frozen.verify_frozen({**frozen.FROZEN_SHA256, **frozen.UPSTREAM_SHA256}),
           "canonical_cycle_inputs": inputs.verify_all(), "env": campaign.env_record()}

    # R2-1 -------------------------------------------------------------------
    rec["R2-1_dev4_reevaluated"] = recompute(DEV4, out / "R2-1_dev4_recompute")
    print("R2-1", rec["R2-1_dev4_reevaluated"]["exit"], rec["R2-1_dev4_reevaluated"]["stdout"])

    # R2-2 -------------------------------------------------------------------
    tk = taskmod.load_task("S1")
    p1, lim, mm = config.params_for("P1"), config.LIMITS["L-EVE"], config.motor_model("M1")
    plant = config.L.QSPlant(p1, 1.0, lim, mm)
    from r4h3 import planner
    vb = planner.baseline_task(plant, tk)
    run_dir = out / "R2-2_S1_M1_LEVE"
    run_dir.mkdir()
    rid = "DEV-S1-M1-LEVE-P1-B0-dt1ms"
    s0 = time.time()
    sim, ev, stops, cmp = campaign.run_arm(rid, "B0", tk, (tk.t, vb["v_b"]), p1, 1.0, lim, mm,
                                           evaluator.motor_spec_from_protocol("M1", frozen.M1_CURVE), fixed_gain(p1), 1e-3,
                                           run_dir, dict(cycle="S1", motor_scenario="M1", limits="L-EVE", pstate="P1",
                                                         design_pstate="P1", draw=None, tracked_profile="v_b"))
    sim["executed"] = True
    (run_dir / "runs.csv").write_text(campaign.csv_text([sim]), encoding="utf-8", newline="\n")
    (run_dir / "evaluation.csv").write_text(campaign.csv_text([ev]), encoding="utf-8", newline="\n")
    (run_dir / "recomputation.json").write_text(json.dumps({rid: cmp}, indent=1, default=float), encoding="utf-8")
    keys = ("torque_limit_pos_max_abs_diff_Nm", "torque_limit_neg_max_abs_diff_Nm", "torque_limit_tol_Nm",
            "friction_tol_Wh", "batt_limited_ambiguous_frac")
    rec["R2-2_S1_M1_LEVE"] = dict(run_id=rid, wall_s=time.time() - s0, v_b_equals_reference=vb["equals_reference"],
                                  protocol_ok=cmp["protocol_ok"], diagnostics_ok=cmp["diagnostics_ok"],
                                  failed=[k for k, v in cmp.items() if isinstance(v, dict) and not v["ok"]],
                                  checks={k: v["value"] for k, v in cmp.items() if isinstance(v, dict)},
                                  **{k: ev[k] for k in keys},
                                  separate_process=recompute(run_dir, out / "R2-2_recompute"))
    print("R2-2", {k: rec["R2-2_S1_M1_LEVE"][k] for k in ("protocol_ok", "diagnostics_ok", "failed")})

    # R2-3 -------------------------------------------------------------------
    ev3 = {}
    # trip time: float bound of step * dt against T_ref; smallest structural error is one trace sample (1 ms)
    ev3["trip_time"] = dict(
        float_error_s={f"T={T:g},dt={dt:g}": abs(round(T / 0.01) * round(0.01 / dt) * dt - T)
                       for T in (213.0, 324.0) for dt in (1e-3, 5e-4)},
        smallest_structural_error_s=1e-3)
    # I_over: forced over-current cases (synthetic 6 s ramp on a 15 Ah pack); smallest structural error is one 1 ms
    # sample of exceedance x A (1e-3 x A s)
    rows = []
    prof = profile_from_knots("hard", [0, 0.2, 3.0, 4.0, 6.0], [0, 0, 6.0, 6.0, 0])
    for sid in ("M0", "M1", "M2"):
        for lk in ("L-R1", "L-EVE"):
            p = p1.with_overrides(Q_Ah=15.0)
            o, tr = simulate_traced(prof, p, fixed_gain(p1), 1.0, config.LIMITS[lk], config.motor_model(sid))
            sm = run_metrics(o, p, 1.0, float(prof.stats()["distance_m"]), prof.duration, p.Ts)
            sm.update(trace_constraint_metrics(tr, p, config.LIMITS[lk], config.RULES))
            tr["v_ref_task_mps"] = tr["v_tracked_mps"]
            tr["stop_ref_flag"] = np.zeros_like(tr["t_s"])
            from r4h3.task import task_from_samples
            spec = campaign.eval_spec(p, 1.0, config.LIMITS[lk], evaluator.motor_spec_from_protocol(sid, frozen.M1_CURVE),
                                      task_from_samples("X", np.array([0.0, 1.0]), np.zeros(2)))
            spec.update(d_ref_m=float(prof.stats()["distance_m"]), rest_intervals=[])
            e = evaluator.evaluate_trace(tr, spec, config.RULES)
            over = np.maximum(tr["i_A"] - config.LIMITS[lk].c_dis * 15.0, 0.0)
            rows.append(dict(motor=sid, limits=lk, I_over_sim_As=sm["I_over_protocol_As"],
                             I_over_eval_As=e["I_over_protocol_As"],
                             abs_diff_As=abs(e["I_over_protocol_As"] - sm["I_over_protocol_As"]),
                             current_max_abs_diff_A=e["current_max_abs_diff_A"],
                             bound_T_maxdi_As=prof.duration * e["current_max_abs_diff_A"],
                             smallest_nonzero_sample_exceedance_A=float(np.min(over[over > 0])) if np.any(over > 0) else None))
    ev3["I_over"] = dict(forced_cases=rows, decision_threshold_As=config.RULES["i_over_max_As"])
    # RMSE: summation-order bound and the structural sensitivity on a real S1 trace (DEV-4)
    a, meta, _ = traces.read_trace(DEV4 / "traces" / "DEV-S1-M0-LR1-P1-B0-dt0.5ms.npz")
    ctrl = np.arange(0, len(a["t_s"]), 10)
    e = a["v_mps"][ctrl] - a["v_tracked_mps"][ctrl]
    seq = 0.0
    for x in e:
        seq += x * x
    r_seq, r_np = float(np.sqrt(seq / len(e))), float(np.sqrt(np.mean(e * e)))
    drop = float(np.sqrt(np.mean(e[:-1] ** 2)))
    shift = a["v_mps"][ctrl[1:] - 1] - a["v_tracked_mps"][ctrl[1:]]                  # one 1 ms sample early
    ev3["rmse"] = dict(n_control_instants=int(len(e)), sequential_vs_pairwise_rel=abs(r_seq - r_np) / r_np,
                       float_bound_rel=(len(e) - 1) * 2.0 ** -53,
                       structural_drop_last_instant_rel=abs(drop - r_np) / r_np,
                       structural_one_sample_misalignment_rel=abs(float(np.sqrt(np.mean(shift ** 2))) - r_np) / r_np,
                       rmse_ms=r_np)
    rec["R2-3_tolerance_evidence"] = ev3
    print("R2-3", json.dumps({"trip": ev3["trip_time"]["float_error_s"], "iover_max_diff": max(r["abs_diff_As"] for r in rows),
                              "rmse": {k: v for k, v in ev3["rmse"].items() if k != "n_control_instants"}}, default=float))
    rec["end"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    (out / "devchecks_rev2.json").write_text(json.dumps(rec, indent=1, default=float), encoding="utf-8")
    post = [dict(path=f.relative_to(out).as_posix(), bytes=f.stat().st_size, sha256=frozen.sha256(f))
            for f in sorted(out.rglob("*")) if f.is_file()]
    (out / "zz_post_run_sha256.csv").write_text(campaign.csv_text(post), encoding="utf-8", newline="\n")
    print("outdir", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
