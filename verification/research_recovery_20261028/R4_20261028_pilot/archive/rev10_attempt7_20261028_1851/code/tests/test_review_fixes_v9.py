"""Fixes of the independent review of release attempt 5 (review/R5_attempt5_review_agent_report_20261028.md), rev9:
R5-1 and R5-2 (MAJOR) and the MINOR findings fixed in code. Protocol semantics only; no test computes, reports or
targets an energy difference between arms."""

import csv
import json
import re
import subprocess
import sys
from types import SimpleNamespace

import numpy as np
import pytest

from r4h3 import campaign, checks, config, evaluator, frozen
from r4h3 import task as taskmod
from r4h3.closedloop import fixed_gain

CODE = frozen.PILOT / "code"


def _task(name="GENTLE"):
    v = np.array([0, 0, 0.5, 1, 1.5, 2, 2, 2, 2, 2, 1.5, 1, 1, 1, 1, 1, 1.5, 2, 2, 2, 2, 2, 1.5, 1, 0.5, 0, 0, 0], float)
    return taskmod.task_from_samples(name, np.arange(len(v), dtype=float), v)


def _cond(tag, cycle="GENTLE"):
    cid = f"DEV-V9-{tag}-{cycle}-M0-LR1-P1-dt1ms"
    return campaign.Condition(cid, "DEV", cycle, "M0", "L-R1", "P1", 1e-3, None,
                              {b: cid.replace("-dt", f"-{b}-dt") for b in ("B0", "B3")})


def _design(task, failed_b3=False):
    d = campaign.plan_design(task, "L-R1", config.params_for("P1"), config.motor_model("M0"))
    if failed_b3:
        d = dict(d, eco={"status": "unavailable", "rows": d["eco"]["rows"], "t": None, "v": None}, val_e=None,
                 eco_ok=False)
    return d


def _run(cond, design, task, tmp_path):
    return campaign.run_condition(cond, task, design, config.params_for("P1"), 1.0, config.LIMITS["L-R1"],
                                  config.motor_model("M0"), evaluator.motor_spec_from_protocol("M0", frozen.M1_CURVE),
                                  fixed_gain(config.params_for("P1")), tmp_path)


def _boom(*a, **k):
    raise RuntimeError("injected")


# ============================================================ R5-2 (MAJOR)
def test_r5_2_a_missing_profile_takes_precedence_over_a_failed_screen(tmp_path, monkeypatch):
    r = checks.pair_qs_dynamic("M0", {"B0": False, "B3": None}, {})
    assert r["pair_status"] == checks.QS_NA_PROFILE and r["ineligible_arms"] == "" and "also failed for B0" in r["reason"]
    t = next(a for a in checks.qs_dynamic_accounting([dict(motor="M0", set="NOM", qs_eligible_pair=False,
                                                          qs_ineligible_arms="", qs_vs_dyn_pair_status=r["pair_status"])])
             if a["set"] == "ALL")
    assert t["not_applicable_profile_unavailable"] == 1 and t["qs_ineligible_pairs"] == 0 and t["qs_ineligible_b0_only"] == 0
    # defence in depth: a nominal cell whose condition has no profile lacks evidence whatever its pair label
    rows = [dict(motor="M0", set="NOM", limits="L-R1", condition_id="a", status="PROFILE_UNAVAILABLE",
                 qs_vs_dyn_pair_status=checks.QS_NA_INFEASIBLE),
            dict(motor="M0", set="NOM", limits="L-EVE", condition_id="b", status=checks.COMPARABLE,
                 qs_vs_dyn_pair_status="PASS")]
    out = checks.branch_qs_dynamic_outcome("M0", rows, ["a", "b"])
    assert out["outcome"] == "INCONCLUSIVE" and "condition PROFILE_UNAVAILABLE" in out["nominal_evidence_missing"]
    # executor: B3 profile missing, B0 profile QS-infeasible
    real = campaign.checks.qs_energy
    monkeypatch.setattr(campaign.checks, "qs_energy", lambda plant, t, v: dict(
        real(plant, t, v), feasible=False, n_infeasible_pieces=1,
        infeasible_pieces=[dict(piece=3, t0_s=3.0, t1_s=4.0, v0_ms=1.0, v1_ms=1.5)]))
    task = _task()
    r = _run(_cond("R52"), _design(task, failed_b3=True), task, tmp_path)
    assert r["status"] == "PROFILE_UNAVAILABLE" and r["qs_vs_dyn_pair_status"] == checks.QS_NA_PROFILE
    assert r["b0_qs_feasible_on_eval_plant"] is False                                   # the screen result is kept


# ============================================================ R5-1 (MAJOR)
def test_r5_1_a_qs_screen_exception_never_stops_or_relabels_the_dynamic_runs(tmp_path, monkeypatch):
    task = _task()
    design = _design(task)
    monkeypatch.setattr(campaign.checks, "qs_screen", _boom)
    r = _run(_cond("R51S"), design, task, tmp_path / "s")
    assert r["status"] == checks.COMPARABLE and r["dynamic_valid_pair"] is True        # protocol 8.2 alone decides
    assert all(s["executed"] is True for s in r["_sims"])                                # both arms ran
    assert r["qs_vs_dyn_pair_status"] == checks.QS_CONDITION_ERROR and r["qs_eligible_pair"] is None
    assert r["qs_screen_errors"] == "B0,B3"
    errs = [e for e in r["_errors"] if e["stage"] == "qs_screen"]
    assert len(errs) == 2 and all(set(_cond("R51S").run_ids.values()) <= set(e["run_ids"].replace("=", ";").split(";"))
                                  for e in errs)
    assert all(r["_rows"][b]["qs_E_J_diagnostic"] == "" and "error" not in r["_rows"][b] for b in ("B0", "B3"))
    monkeypatch.undo()
    monkeypatch.setattr(campaign, "L", SimpleNamespace(QSPlant=_boom))                   # the plant cannot be built
    r = _run(_cond("R51P"), design, task, tmp_path / "p")
    assert r["status"] == checks.COMPARABLE and r["qs_vs_dyn_pair_status"] == checks.QS_CONDITION_ERROR
    assert [e["stage"] for e in r["_errors"]] == ["qs_screen"] and r["_errors"][0]["run_ids"]
    monkeypatch.undo()
    monkeypatch.setattr(campaign.checks, "qs_screen", _boom)                             # with a missing profile
    r = _run(_cond("R51M"), _design(task, failed_b3=True), task, tmp_path / "m")
    assert r["status"] == "PROFILE_UNAVAILABLE" and r["qs_vs_dyn_pair_status"] == checks.QS_NA_PROFILE
    assert next(s for s in r["_sims"] if s["branch"] == "B0")["executed"] is True


def test_r5_1_a_reporting_or_classification_exception_keeps_the_executed_runs(tmp_path, monkeypatch):
    task = _task()
    design = _design(task)
    monkeypatch.setattr(campaign, "baseline_sanity", _boom)
    r = _run(_cond("R51R"), design, task, tmp_path / "r")
    assert r["status"] == checks.COMPARABLE and all(s["executed"] is True for s in r["_sims"])
    assert all("error" not in r["_rows"][b] for b in ("B0", "B3")) and r["reporting_error"]
    assert r["qs_vs_dyn_pair_status"] == checks.QS_CONDITION_ERROR                    # AMB-29(d): record incomplete
    assert r["qs_vs_dyn_pair_status_before_error"] in ("PASS", "FAIL")
    assert [e["stage"] for e in r["_errors"]] == ["condition_report"]
    monkeypatch.undo()
    monkeypatch.setattr(campaign.checks, "classify_pair", _boom)
    r = _run(_cond("R51C"), design, task, tmp_path / "c")
    assert r["status"] == "ERROR" and all(s["executed"] is True for s in r["_sims"])     # runs kept, condition ERROR
    assert "classify" in [e["stage"] for e in r["_errors"]] and r["dynamic_valid_pair"] is False


# ============================================================ R5-6, R5-8, R5-9 (MINOR)
def test_r5_6_a_run_whose_evaluation_raised_names_its_kept_trace_files(tmp_path, monkeypatch):
    task = _task()
    monkeypatch.setattr(campaign.evaluator, "evaluate_trace", _boom)
    c = _cond("R56")
    r = _run(c, _design(task), task, tmp_path)
    assert r["status"] == "ERROR"
    for s in r["_sims"]:
        assert s["executed"] is False and "trace files are kept" in s["reason"]
        assert f"{s['run_id']}.npz" in s["retained_files"].split(";") and (tmp_path / "traces" / f"{s['run_id']}.npz").is_file()
    assert sorted(e["run_id"] for e in r["_errors"]) == sorted(c.run_ids.values())


def _read(out, f):
    return list(csv.DictReader((out / f).open(encoding="utf-8")))


def test_r5_8_a_failed_separate_recomputation_or_fold_is_recorded_and_fails_closed(tmp_path, monkeypatch):
    real = subprocess.run
    monkeypatch.setattr(campaign.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(
        a[0], 4, stdout="", stderr="Traceback (most recent call last):\nRuntimeError: injected crash"))
    task = _task()
    out = tmp_path / "sep"
    rows = campaign.execute_schedule([_cond("R58S")], lambda n: task, out)
    err = [e for e in _read(out, "errors.csv") if e["condition_id"] == "SEPARATE-RECOMPUTATION"]
    assert len(err) == 1 and err[0]["stage"] == "exit 4" and "injected crash" in err[0]["traceback"]
    assert rows[0]["status"] != checks.COMPARABLE and rows[0]["qs_vs_dyn_pair_status"] not in ("PASS", "REPORTED_ONLY")
    assert all(x["energy_role"] != checks.CONFIRMATORY for x in _read(out, "energy_roles.csv"))
    for f in ("conditions.csv", "feasibility_accounting.csv", "qs_dynamic_branch_outcomes.csv", "manifest.json",
              "zz_post_run_sha256.csv"):
        assert (out / f).is_file(), f
    monkeypatch.setattr(campaign.subprocess, "run", real)
    monkeypatch.setattr(campaign, "fold_separate_recomputation", _boom)
    out = tmp_path / "fold"
    rows = campaign.execute_schedule([_cond("R58F")], lambda n: task, out)
    assert rows[0]["status"] != checks.COMPARABLE and rows[0]["paired_endpoint_eligible"] is False
    assert rows[0]["separate_recomputation"].startswith("not applied")
    assert rows[0]["qs_vs_dyn_pair_status"] not in ("PASS", "FAIL", "REPORTED_ONLY")
    assert any(e["condition_id"] == "RECOMPUTATION-FOLD" for e in _read(out, "errors.csv"))
    assert (out / "manifest.json").is_file() and (out / "zz_post_run_sha256.csv").is_file()


def test_r5_8_the_separate_script_exit_codes_distinguish_results_from_failures(tmp_path):
    script = [sys.executable, "-I", "-B", str(CODE / "recompute_from_traces.py")]
    assert subprocess.run(script + [str(tmp_path / "missing")], capture_output=True, text=True).returncode == 4
    d = tmp_path / "empty"
    d.mkdir()
    (d / "runs.csv").write_text("run_id,executed\n", encoding="utf-8")
    assert subprocess.run(script + [str(d)], capture_output=True, text=True).returncode == 0      # no run: nothing fails
    assert subprocess.run(script + [str(d)], capture_output=True, text=True).returncode == 3      # refuses to overwrite
    assert campaign.IMPLEMENTED_2["separate_recomputation_exit_codes"].startswith("0 every")


def test_r5_9_an_energy_role_failure_leaves_one_marked_row_per_planned_run(tmp_path, monkeypatch):
    real = checks.energy_role
    c = _cond("R59")

    def role(executed, valid, rec, status):
        if executed and not hasattr(role, "done"):
            role.done = True
            raise RuntimeError("injected role failure")
        return real(executed, valid, rec, status)
    monkeypatch.setattr(campaign.checks, "energy_role", role)
    task = _task()
    out = tmp_path / "o"
    campaign.execute_schedule([c], lambda n: task, out)
    roles = _read(out, "energy_roles.csv")
    assert sorted(x["run_id"] for x in roles) == sorted(c.run_ids.values())              # one row per planned run
    assert [x["energy_role"] for x in roles].count(checks.ROLE_NOT_DETERMINED) == 1
    assert checks.ROLE_NOT_DETERMINED not in (checks.CONFIRMATORY,)
    t = {(a["motor"], a["set"]): a for a in _read(out, "feasibility_accounting.csv")}[("ALL", "ALL")]
    assert t[f"runs_{checks.ROLE_NOT_DETERMINED}"] == "1"
    assert sum(int(t[f"runs_{k}"]) for k in checks.ENERGY_ROLES) == int(t["planned_runs"]) == 2
    assert any(e["condition_id"] == "ENERGY-ROLE" and e["run_id"] for e in _read(out, "errors.csv"))


# ============================================================ R5-3, R5-11 (MINOR)
def test_r5_3_and_r5_11_undefined_inputs_are_not_evaluable_and_labelled_by_their_term():
    for a, b in ((None, 0.1), (0.1, None), (float("nan"), 0.1)):
        t = checks.timestep_check(a, b)
        assert t["passed"] is None and t["change_pp"] is None
        assert campaign.numerical_check_consequence("dynamic_time_step", t["passed"]) != "pass"
    q = checks.qs_vs_dynamic("M0", 1.0e4, 0.05, 0.0)
    assert q["status"] == "undefined (d_ref <= 0)" and q["diff_pct"] is None and q["non_positive_term"].startswith("d_ref_m")
    r = checks.pair_qs_dynamic("M0", {"B0": True, "B3": True}, {"B0": q, "B3": q})
    assert r["pair_status"] == checks.QS_UNDEFINED


# ============================================================ amendment candidate and review status
def test_rev6_candidate_is_a_draft_rev5_is_unchanged_and_readings_are_labelled():
    assert frozen.sha256(campaign.PILOT_DIR / "03_protocol_v1_amendment_2_rev5_CANDIDATE.md") == \
        "e7ba73c11784b3cf38f48e32b69a7a7c21b070d039118547d638bc1bf06d4f5f"
    # rev10: the current candidate is rev6 or later (rev6 itself is pinned in test_owner_ruling_i1_v10.py)
    m = re.fullmatch(r"03_protocol_v1_amendment_2_rev(\d+)_CANDIDATE\.md", campaign.DRAFT_AMENDMENT_2.name)
    assert m and int(m.group(1)) >= 6
    r = campaign.read_amendment(campaign.DRAFT_AMENDMENT_2, campaign.IMPLEMENTED_2, {})
    assert r["exists"] and not r["errors"] and r["status"] == "DRAFT", r["errors"]
    text = campaign.DRAFT_AMENDMENT_2.read_text(encoding="utf-8")
    assert "DRAFT — NOT APPROVED FOR RELEASE" in text.splitlines()[2]
    for h in (frozen.FROZEN_SHA256[frozen.PROTOCOL], campaign.AMENDMENT_1_SHA256,
              "e7ba73c11784b3cf38f48e32b69a7a7c21b070d039118547d638bc1bf06d4f5f"):
        assert h in text
    imp = campaign.IMPLEMENTED_2                                                         # review R5-4: readings named
    where = {"I-1": "AMB_30_branch_scope", "I-2": "AMB_30_branch_scope", "I-3": "non_positive_denominator_rule",
             "I-4": "AMB_31_energy_of_invalid_runs", "I-5": "AMB_29_qs_energy_undefined", "I-6": "AMB_29_condition_error"}
    for i, k in where.items():
        assert re.search(rf"\b{i}\b", imp[k]) and re.search(r"[Rr]eading", imp[k]), (i, k)
    assert "QS_COMPARISON_NOT_EVALUABLE" in imp["AMB_29_qs_energy_undefined"]


def test_review_status_v7_counts_the_major_findings_until_verified_and_blocks(tmp_path, monkeypatch):
    v7 = frozen.PILOT / "config" / "code_review_status_v7.json"                         # rev10: read by path
    rv = json.loads(v7.read_text(encoding="utf-8"))
    assert rv["open_major"] == 2 and set(rv["major_findings"]) == {"R5-1", "R5-2"} and rv["reviews_pending"]
    monkeypatch.setattr(campaign, "REVIEW_STATUS", v7)
    b = " | ".join(campaign.preconditions("readiness"))
    assert "2 major findings not resolved" in b and "closure not yet accepted by the owner" in b
