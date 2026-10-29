"""Release-readiness validation of the 170-run schedule and the reporting rules, from a release-attempt copy.
Executes no run, evaluates no plant energy, computes no arm-to-arm energy difference; never calls run_campaign() or
execute_schedule(). Reads the attempt's dry run and junit; writes only logs/release_validation_attempt12.json.
Usage: python -I -B attempt12_release_validation.py <attempt_dir>"""
import ast
import csv
import inspect
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

att = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(att / "code"))
import numpy as np  # noqa: E402

from r4h3 import campaign, checks, config, frozen, inputs, sensitivity  # noqa: E402
from r4h3.closedloop import fixed_gain  # noqa: E402

assert frozen.PILOT.resolve() == att, (frozen.PILOT, att)
target = att / "logs" / "release_validation_attempt12.json"
if target.exists():
    sys.exit(f"refused: {target} exists")
dry = sorted(att.glob("dry_run_*"))[-1]
rows = list(csv.DictReader((dry / "schedule_170.csv").open(encoding="utf-8")))
jobs = list(csv.DictReader((dry / "planner_jobs.csv").open(encoding="utf-8")))
dj = json.loads((dry / "dry_run.json").read_text(encoding="utf-8"))
ids = [r["run_id"] for r in rows]
res = {"written": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "attempt": str(att), "dry_run": dry.name,
       "note": "no run executed, no plant evaluated, no arm-to-arm energy difference computed"}

# 1. schedule: count, IDs, smoke exclusion, held-out S2, fixed gain
smoke = campaign.smoke_run_ids()
by_set = {s: sum(1 for r in rows if r["set"] == s) for s in campaign.PLANNED}
draws = sensitivity.draws()
k_nom = np.asarray(fixed_gain(config.params_for("P1")), float)
gain_same = [bool(np.array_equal(np.asarray(sensitivity.gain_for_draw(draws[d - 1]), float), k_nom))
             for d in range(1, 33)]
sen = [r for r in rows if r["set"] == "SEN"]
res["schedule"] = dict(
    runs=len(rows), equals_170=len(rows) == campaign.TOTAL_PLANNED, counts_per_set=by_set,
    counts_equal_protocol_10_6=by_set == campaign.PLANNED,
    run_ids_unique=len(set(ids)) == len(ids), all_official_prefix=all(i.startswith(campaign.OFFICIAL_PREFIX) for i in ids),
    every_condition_has_B0_and_B3=all(sorted(r["branch"] for r in rows if r["condition_id"] == c) == ["B0", "B3"]
                                      for c in {r["condition_id"] for r in rows}),
    dry_run_schedule_checks=dj["schedule"]["checks"], dry_run_schedule_passed=dj["schedule"]["passed"],
    smoke_run_ids=smoke, smoke_runs_excluded=not (set(ids) & set(smoke)),
    s2_rows_all_held_out=all(r["role"] == "held-out (protocol 3)" for r in rows if r["cycle"] == "S2"),
    s1_only_in_INS=all((r["cycle"] == "S1") == (r["set"] == "INS") for r in rows),
    every_profile_designed_on_P1=all(r["design_pstate"] == "P1" for r in rows),
    planner_jobs_only_profiles_or_grid=all(j["purpose"].startswith(("profiles for set", "grid convergence")) for j in jobs),
    planner_numerics_equal_protocol=(config.ECO_DS, config.ECO_DV, config.LAMBDA_LOG10, config.LAMBDA_ITERS, config.H)
    == (2.0, 0.1, (-3.0, 6.0), 40, 1.0),
    canonical_cycles_verified=inputs.verify_all(),
    sen_gain_text_all_fixed_P1=all("nominal P1 fixed gain, not retuned per draw (AMB-14)" in r["gain"] for r in sen),
    sen_gain_equal_nominal_P1_for_all_32_draws=all(gain_same), sen_draws_checked=len(gain_same),
    sensitivity_gain_basis=sensitivity.GAIN_BASIS)

# 2. QS and dynamic feasibility statuses are distinct
fn = ast.parse(inspect.getsource(checks.classify_pair)).body[0]
body = fn.body[1:] if isinstance(fn.body[0], ast.Expr) and isinstance(fn.body[0].value, ast.Constant) else fn.body
names = sorted({n.id for s in body for n in ast.walk(s) if isinstance(n, ast.Name)}
               | {n.attr for s in body for n in ast.walk(s) if isinstance(n, ast.Attribute)})
res["qs_vs_dynamic_distinct"] = dict(
    condition_statuses=list(checks.STATUSES), pair_qs_statuses=list(checks.PAIR_QS_STATUSES),
    vocabularies_disjoint=not (set(checks.STATUSES) & set(checks.PAIR_QS_STATUSES)),
    classify_pair_parameters=list(inspect.signature(checks.classify_pair).parameters),
    classify_pair_body_names=names, classify_pair_reads_no_qs_name=not any("qs" in n.lower() for n in names),
    implemented_2_dynamic_8_2_independent=campaign.IMPLEMENTED_2["N_A2_dynamic_8_2_independent"])

# 3. no invalid arm in the paired confirmatory endpoint (exhaustive rule tables)
table = [(e, v, r, s, checks.energy_role(e, v, r, s)) for e in (True, False) for v in (True, False)
         for r in (True, False) for s in checks.STATUSES]
refused = []
for s in checks.STATUSES:
    try:
        checks.paired_delta(s, {}, {})
    except ValueError:
        refused.append(s)
    except KeyError:                     # COMPARABLE passes the guard and then needs the energy fields (none given)
        pass
res["paired_endpoint"] = dict(
    energy_role_cases=len(table),
    confirmatory_only_if_executed_valid_confirmed_and_COMPARABLE=all(
        (role == checks.CONFIRMATORY) == (e and v and r and s == checks.COMPARABLE) for e, v, r, s, role in table),
    paired_delta_refuses=refused,
    paired_delta_refuses_every_non_COMPARABLE_status=sorted(refused) == sorted(set(checks.STATUSES) - {checks.COMPARABLE}))

# 4. denominators, omission, invalid arms, exceptions: the attempt's own test run (junit), by test name
jx = ET.parse(att / "logs" / "pytest_release_attempt12.xml").getroot()
cases = {f"{c.get('classname')}::{c.get('name')}": ("failed" if c.find("failure") is not None or c.find("error") is not None
                                                    else "skipped" if c.find("skipped") is not None else "passed")
         for c in jx.iter("testcase")}
want = ["test_missing_profile_and_invalid_arm_accounting", "test_planned_run_and_feasibility_denominators_stay_fixed",
        "test_no_situation_yields_a_pass_by_omission", "test_amb29d_evaluation_exceptions_are_kept_without_retry",
        "test_valid_dynamic_energy_is_kept_when_only_the_qs_comparison_is_not_evaluable",
        "test_amb29c_non_positive_qs_energy", "test_a_missing_required_nominal_cell", "test_amb30_",
        "test_amb29a_planned_run_and_feasibility_denominators", "test_amb31_", "test_case9_denominator",
        "test_case10_records_are_preserved", "test_campaign_execution_stays_blocked",
        "test_r5_1_", "test_r5_2_", "test_r5_6_", "test_r5_8_", "test_r5_9_", "test_review_status_v7",
        "test_i1_", "test_v6_1_", "test_open_owner_decisions_block",
        "test_i2_", "test_i3_", "test_i4_", "test_i5_", "test_i6_", "test_r7_3_", "test_r7_4_", "test_r7_5_",
        "test_r7_7_", "test_rev8_candidate", "test_campaign_mode_stays_blocked",
        "test_r8_1_", "test_r8_2_", "test_r8_3_", "test_r8_4_", "test_r8_5_", "test_r8_9_", "test_r8_10_",
        "test_review_status_v10", "test_rev9_candidate", "test_campaign_mode_stays_blocked_in_rev12",
        "test_r9_1_", "test_r9_2_", "test_r9_4_", "test_r9_5_", "test_r9_6_",
        "test_review_status_v11", "test_rev10_candidate", "test_campaign_mode_stays_blocked_in_rev13",
        "test_i6b_", "test_after_a_recomputation_or_fold_failure_", "test_without_a_recomputation_failure_",
        "test_r10_1_", "test_r10_2_", "test_r10_3_", "test_r10_4_", "test_review_status_v13",
        "test_rev12_candidate", "test_campaign_mode_stays_blocked_in_rev14",
        "test_r11_1_", "test_r11_2_", "test_r11_4_", "test_r11_6_", "test_r11_7_", "test_r11_8_",
        "test_review_status_v14", "test_rev13_candidate", "test_campaign_mode_stays_blocked_in_rev15"]
hits = {w: {k: v for k, v in cases.items() if k.split("::")[1].startswith(w)} for w in want}
res["reporting_tests"] = dict(junit_cases=len(cases), by_prefix={w: h for w, h in hits.items()},
                              every_prefix_found=all(hits.values()),
                              all_passed=all(v == "passed" for h in hits.values() for v in h.values()))

# 5. no legacy percentage as a target or acceptance threshold
legacy = ("12.5", "15.3", "2.1", "2.8", "10.3", "5.3")
pat = re.compile(r"(?<![\w.])(" + "|".join(re.escape(x) for x in legacy) + r")(?![\w])")
scan = []
for p in sorted((att / "code").rglob("*.py")):
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        if pat.search(line):
            scan.append(dict(file=p.relative_to(att).as_posix(), line=i, text=line.strip()[:160]))
res["legacy_numbers"] = dict(
    protocol_line_12="the thesis's 12.5 %, 15.3 %, +/- 2.1 %, +/- 2.8 % and every other legacy number are not targets",
    also_scanned=["10.3", "5.3"], hits_in_code=scan,
    acceptance_constants=dict(QS_DYN_MAX_PCT=checks.QS_DYN_MAX_PCT, GRID_MAX_PP=checks.GRID_MAX_PP,
                              OPTIMALITY_PP=checks.OPTIMALITY_PP, TIMESTEP_MAX_PP=checks.TIMESTEP_MAX_PP,
                              H3_SEN_DRAWS=checks.H3_SEN_DRAWS, H3_SEN_MIN=checks.H3_SEN_MIN),
    acceptance_constants_equal_protocol=(checks.QS_DYN_MAX_PCT, checks.GRID_MAX_PP, checks.OPTIMALITY_PP,
                                         checks.TIMESTEP_MAX_PP, checks.H3_SEN_DRAWS, checks.H3_SEN_MIN)
    == (1.0, 0.2, 0.2, 0.01, 32, 29))

# 6. fail-closed
res["fail_closed"] = dict(campaign_authorization_exists=campaign.CAMPAIGN_AUTHORIZATION.exists(),
                          issued_amendment_2_exists=campaign.ISSUED_AMENDMENT_2.exists(),
                          campaign_blockers=campaign.preconditions("campaign"),
                          run_campaign_called=False)
flat = [res["schedule"][k] for k in ("equals_170", "counts_equal_protocol_10_6", "run_ids_unique", "all_official_prefix",
                                     "every_condition_has_B0_and_B3", "dry_run_schedule_passed", "smoke_runs_excluded",
                                     "s2_rows_all_held_out", "s1_only_in_INS", "every_profile_designed_on_P1",
                                     "planner_jobs_only_profiles_or_grid", "planner_numerics_equal_protocol",
                                     "sen_gain_text_all_fixed_P1", "sen_gain_equal_nominal_P1_for_all_32_draws")]
flat += [res["qs_vs_dynamic_distinct"][k] for k in ("vocabularies_disjoint", "classify_pair_reads_no_qs_name",
                                                     "implemented_2_dynamic_8_2_independent")]
flat += [res["paired_endpoint"]["confirmatory_only_if_executed_valid_confirmed_and_COMPARABLE"],
         res["paired_endpoint"]["paired_delta_refuses_every_non_COMPARABLE_status"],
         res["reporting_tests"]["every_prefix_found"], res["reporting_tests"]["all_passed"],
         res["legacy_numbers"]["acceptance_constants_equal_protocol"],
         not res["fail_closed"]["campaign_authorization_exists"], bool(res["fail_closed"]["campaign_blockers"])]
res["all_checks_true"] = all(flat)
res["legacy_hits_need_inspection"] = len(scan)
target.write_text(json.dumps(res, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
print(json.dumps({k: res[k] for k in ("all_checks_true", "legacy_hits_need_inspection")}, indent=1))
print(json.dumps(scan, indent=1))
