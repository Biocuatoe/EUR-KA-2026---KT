"""S1 development checks of the campaign infrastructure (readiness brief section 5). NOT campaign runs.

    python -I -B code/run_devchecks.py

All checks use S1 (in-sample) at M0, L-R1 and only what is needed to validate infrastructure; nothing reads,
plans or runs S2. Outputs go to outputs/dev_readiness_<timestamp>/ (never overwritten). No energy difference
between arms, no S_found and no saving is computed or written:
  DEV-1 revalidate  the smoke-test profiles under the VC-01 validator on P1, and their QS feasibility on P3 (D5 path)
  DEV-2 qs_vs_dyn   QS energy of each smoke-test profile vs its existing dynamic energy (per run; protocol 9 rule)
  DEV-3 grid        S-eco on S1 at (2 m, 0.1 m/s) and (1 m, 0.05 m/s): runtime, validity, relative change of the
                    eco profile's own QS energy (no baseline energy is used)
  DEV-4 dt          one S1 run (B0 tracking v_b) at dt = 0.5 ms through the campaign executor's run_arm, its 1 ms
                    trace recomputed in a separate process; compared per run with the smoke B0 run at 1 ms
"""

import csv
import json
import subprocess
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout.reconfigure(encoding="utf-8")

import numpy as np  # noqa: E402

from r4h3 import campaign, checks, config, evaluator, frozen, inputs, planner, validator  # noqa: E402
from r4h3 import task as taskmod  # noqa: E402
from r4h3.closedloop import fixed_gain  # noqa: E402

L = config.L
SMOKE = campaign.SMOKE_DIR
CYCLE, MOTOR, LIM = "S1", "M0", "L-R1"


def main() -> int:
    gate = json.loads(campaign.READINESS_GATE.read_text(encoding="utf-8"))
    from r4h3.slice import code_hashes
    if gate["code_sha256"] != code_hashes():
        raise SystemExit("STOP: code differs from the readiness gate record")
    out = frozen.PILOT / "outputs" / f"dev_readiness_{time.strftime('%Y%m%d_%H%M%S')}"
    out.mkdir(parents=True, exist_ok=False)
    rec = {"kind": "development checks (S1 only; not campaign runs; no energy difference computed)",
           "start": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "readiness_gate_sha256": frozen.sha256(campaign.READINESS_GATE),
           "frozen": frozen.verify_frozen({**frozen.FROZEN_SHA256, **frozen.UPSTREAM_SHA256}),
           "canonical_cycle_inputs": inputs.verify_all(), "env": campaign.env_record()}
    tk = taskmod.load_task(CYCLE)
    lim, mm = config.LIMITS[LIM], config.motor_model(MOTOR)
    p1, p3 = config.params_for("P1"), config.params_for("P3")
    plant1 = L.QSPlant(p1, 1.0, lim, mm)
    plant3 = L.QSPlant(p3, config.PSTATES["P3"]["soh"], lim, mm)
    z = np.load(SMOKE / "profiles.npz", allow_pickle=False)
    prof = {"B0": (z["t_task"], z["v_b"]), "B3": (z["t_seco"], z["v_seco"])}

    # DEV-1 ------------------------------------------------------------------
    d1 = {}
    for b, (t, v) in prof.items():
        r1 = validator.validate_trajectory(tk, t, v, plant1, f"smoke {b} on P1")
        r3 = validator.validate_trajectory(tk, t, v, plant3, f"smoke {b} on P3")
        d1[b] = dict(valid_on_P1=r1["valid"], failures_on_P1=r1["failures"], n_extra_stop_knots=sum(
            s["n_extra_stops"] for s in r1["segments"]), max_wait_speed_ms=max(
            (s["wait_max_speed_ms"] for s in r1["segments"] if np.isfinite(s["wait_max_speed_ms"])), default=0.0),
            early_arrival_s=[s["early_arrival_s"] for s in r1["segments"]],
            departures_s=[s["t_dep_s"] for s in r1["segments"]],
            qs_feasible_on_P3=r3["n_infeasible_pieces"] == 0, n_infeasible_pieces_on_P3=r3["n_infeasible_pieces"])
    rec["DEV-1_revalidate"] = d1
    print("DEV-1", json.dumps({b: {k: d1[b][k] for k in ("valid_on_P1", "n_extra_stop_knots", "qs_feasible_on_P3")}
                               for b in d1}))

    # DEV-2 ------------------------------------------------------------------
    runs = {r["branch"]: r for r in csv.DictReader((SMOKE / "runs.csv").open(encoding="utf-8"))}
    d2 = {}
    for b, (t, v) in prof.items():
        qs = checks.qs_energy(plant1, t, v)
        q = checks.qs_vs_dynamic(MOTOR, qs["E_J"], float(runs[b]["E_net_Wh"]), tk.d_ref)
        d2[b] = dict(run_id=runs[b]["run_id"], qs_vs_dyn_pct=q["diff_pct"], status=q["status"], qs_feasible=qs["feasible"])
    rows_seco = list(csv.DictReader((SMOKE / "planner_rows.csv").open(encoding="utf-8")))
    e_dp = sum(float(r["E_k_J"]) for r in rows_seco)
    d2["B3_knots_QS_equals_planner_DP_sum_rel"] = abs(checks.qs_energy(plant1, *prof["B3"])["E_J"] - e_dp) / abs(e_dp)
    rec["DEV-2_qs_vs_dynamic"] = d2
    print("DEV-2", json.dumps(d2))

    # DEV-3 ------------------------------------------------------------------
    d3 = {}
    for name, (ds, dv) in (("coarse", campaign.GRID_COARSE), ("fine", campaign.GRID_FINE)):
        s0 = time.time()
        eco = planner.plan_seco(plant1, tk, ds, dv)
        el = time.time() - s0
        val = validator.validate_trajectory(tk, eco["t"], eco["v"], plant1, f"S-eco {name}") if eco["status"] == "ok" else None
        d3[name] = dict(ds=ds, dv=dv, status=eco["status"], runtime_s=el, valid=bool(val and val["valid"]),
                        failures=val["failures"] if val else None,
                        n_extra_stop_knots=sum(s["n_extra_stops"] for s in val["segments"]) if val else None,
                        segment_status=[r["status"] for r in eco["rows"]],
                        segment_time_margin_s=[r["T_k_s"] - r["t_k_s"] for r in eco["rows"]],
                        n_lambda_evals=[r["n_lambda_evals"] for r in eco["rows"]], _E=eco.get("E_seco_J"))
    e_c, e_f = d3["coarse"].pop("_E"), d3["fine"].pop("_E")
    d3["eco_QS_energy_rel_change_fine_vs_coarse"] = (e_f - e_c) / e_c if e_c and e_f else None
    d3["note"] = "eco-arm quantity only; protocol 9 judges |dS_found| on S2 in the campaign, not here"
    rec["DEV-3_grid"] = d3
    print("DEV-3", json.dumps({k: (v if not isinstance(v, dict) else {kk: v[kk] for kk in ("status", "runtime_s", "valid")})
                               for k, v in d3.items()}))

    # DEV-4 ------------------------------------------------------------------
    rid = "DEV-S1-M0-LR1-P1-B0-dt0.5ms"
    s0 = time.time()
    sim, ev, stops, cmp = campaign.run_arm(rid, "B0", tk, prof["B0"], p1, 1.0, lim, mm,
                                           evaluator.motor_spec_from_protocol(MOTOR, frozen.M1_CURVE), fixed_gain(p1),
                                           5e-4, out, dict(cycle=CYCLE, motor_scenario=MOTOR, limits=LIM, pstate="P1",
                                                           design_pstate="P1", draw=None, tracked_profile="smoke-test v_b"))
    sim["executed"] = True
    (out / "runs.csv").write_text(campaign.csv_text([sim]), encoding="utf-8", newline="\n")
    (out / "evaluation.csv").write_text(campaign.csv_text([ev]), encoding="utf-8", newline="\n")
    (out / "stop_compliance.csv").write_text(campaign.csv_text(stops), encoding="utf-8", newline="\n")
    (out / "recomputation.json").write_text(json.dumps({rid: cmp}, indent=1, default=float), encoding="utf-8")
    sep = subprocess.run([sys.executable, "-I", "-B", str(Path(__file__).resolve().parent / "recompute_from_traces.py"),
                          str(out)], capture_output=True, text=True, timeout=1800)
    e1 = float(runs["B0"]["E_net_Wh"])
    rec["DEV-4_dt"] = dict(run_id=rid, wall_s=time.time() - s0, dt_s=sim["dt_s"], trace_dt_s=sim["trace_dt_s"],
                           n_samples=sim["n_samples"], credited_flags={k: ev[k] for k in (
                               "sim_valid", "complete", "tracking_ok", "stop_ok", "constraint_ok", "finite_ok",
                               "recompute_protocol_ok", "credited")},
                           recompute_protocol_ok=cmp["protocol_ok"], recompute_diagnostics_ok=cmp["diagnostics_ok"],
                           failed_checks=[k for k, v in cmp.items() if isinstance(v, dict) and not v["ok"]],
                           separate_process_exit=sep.returncode, separate_process_stdout=sep.stdout.strip(),
                           separate_process_stderr=sep.stderr.strip()[-2000:],
                           single_run_E_rel_change_05ms_vs_1ms=(sim["E_net_Wh"] - e1) / e1,
                           note="one arm only: a per-run time-step sensitivity, not the protocol 9 paired dE_rel check")
    print("DEV-4", json.dumps({k: rec["DEV-4_dt"][k] for k in ("recompute_protocol_ok", "separate_process_exit",
                                                               "single_run_E_rel_change_05ms_vs_1ms", "wall_s")}))
    rec["end"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    (out / "devchecks.json").write_text(json.dumps(rec, indent=1, default=float), encoding="utf-8")
    post = [dict(path=f.relative_to(out).as_posix(), bytes=f.stat().st_size, sha256=frozen.sha256(f))
            for f in sorted(out.rglob("*")) if f.is_file()]
    (out / "zz_post_run_sha256.csv").write_text(campaign.csv_text(post), encoding="utf-8", newline="\n")
    print("outdir", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
