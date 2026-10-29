"""Fixes of the attempt-9 review findings R9-1 to R9-7, rev13 (amendment 2 candidate rev10).
Protocol semantics only. No test computes, reports or targets an energy difference between arms; synthetic numbers in
pure-rule tests are not run energies."""

import json
import re
import subprocess

import numpy as np
import pytest

from r4h3 import campaign, checks, config, evaluator, frozen
from r4h3 import task as taskmod
from r4h3.closedloop import fixed_gain

NA, NA_PROFILE, CE = checks.QS_NA_INFEASIBLE, checks.QS_NA_PROFILE, checks.QS_CONDITION_ERROR
ELIG = ("qs_eligible_pairs", "qs_ineligible_pairs", "not_applicable_profile_unavailable", "qs_eligibility_unknown")
STATUS = ("qs_check_pass", "qs_check_fail", "qs_check_reported_only", "qs_check_not_applicable_qs_infeasible",
          "qs_check_not_applicable_profile_unavailable", "not_evaluable_run_missing", "not_evaluable_qs_undefined",
          "not_evaluable_condition_error", "not_evaluable_run_invalid")


def _task(name="GENTLE"):
    v = np.array([0, 0, 0.5, 1, 1.5, 2, 2, 2, 2, 2, 1.5, 1, 1, 1, 1, 1, 1.5, 2, 2, 2, 2, 2, 1.5, 1, 0.5, 0, 0, 0], float)
    return taskmod.task_from_samples(name, np.arange(len(v), dtype=float), v)


def _cond(tag, set_="DEV"):
    cid = f"DEV-V13-{tag}-GENTLE-M0-LR1-P1-dt1ms"
    return campaign.Condition(cid, set_, "GENTLE", "M0", "L-R1", "P1", 1e-3, None,
                              {b: cid.replace("-dt", f"-{b}-dt") for b in ("B0", "B3")})


def _design(task):
    return campaign.plan_design(task, "L-R1", config.params_for("P1"), config.motor_model("M0"))


def _run(cond, design, task, tmp_path):
    return campaign.run_condition(cond, task, design, config.params_for("P1"), 1.0, config.LIMITS["L-R1"],
                                  config.motor_model("M0"), evaluator.motor_spec_from_protocol("M0", frozen.M1_CURVE),
                                  fixed_gain(config.params_for("P1")), tmp_path)


def _boom(*a, **k):
    raise RuntimeError("injected")


def _is_b0(t):
    return len(t) > 2 and np.allclose(np.diff(t), 1.0)


def _screen_fails(arm):
    real = checks.qs_energy

    def screen(plant, t, v):
        r = real(plant, t, v)
        if (arm == "B0") == _is_b0(t):
            return dict(r, feasible=False, n_infeasible_pieces=1,
                        infeasible_pieces=[dict(piece=3, t0_s=3.0, t1_s=4.0, v0_ms=1.0, v1_ms=1.5)])
        return r
    return checks, "qs_energy", screen


def _fail():
    return dict(motor="M0", E_qs_J=1.0, E_dyn_Wh=1.0, d_ref_m=1.0, e_qs_Wh_per_km=1.0, e_dyn_Wh_per_km=1.02,
                diff_pct=2.0, decisive=True, status="FAIL (branch INCONCLUSIVE, protocol 9)", non_positive_term="")


def _cc():
    return type("C", (), {"run_ids": {"B0": "r0", "B3": "r3"}})()


# ============================================================ R9-1 (MAJOR): a QS-screen diagnosis exception
def test_r9_1_an_exception_in_the_qs_screen_diagnosis_is_recorded_and_makes_the_pair_not_evaluable(tmp_path,
                                                                                                    monkeypatch):
    task = _task()
    design = _design(task)
    monkeypatch.setattr(*_screen_fails("B3"))
    c0 = _cond("R91CTRL")
    r = _run(c0, design, task, tmp_path / "ctrl")                                        # control: diagnosis works
    assert r["qs_vs_dyn_pair_status"] == NA and r["_errors"] == [] and r["qs_screen_errors"] == ""
    monkeypatch.setattr(checks, "qs_piece_diagnosis", _boom)
    c = _cond("R91")
    r = _run(c, design, task, tmp_path / "diag")
    e = [x for x in r["_errors"] if x["stage"] == "qs_screen"]
    assert len(e) == 1 and e[0]["run_id"] == c.run_ids["B3"] and "diagnosis of piece 3" in e[0]["traceback"]
    assert "RuntimeError: injected" in e[0]["traceback"] and c.run_ids["B0"] in e[0]["run_ids"]  # traceback, run IDs
    assert r["qs_screen_errors"] == "B3" and r["b3_qs_feasible_on_eval_plant"] is False         # screen verdict kept
    assert r["qs_vs_dyn_pair_status"] == CE and r["qs_vs_dyn_pair_status_before_error"] == NA   # I-6
    assert r["qs_vs_dyn_applicability"] == NA and r["qs_eligible_pair"] is False and r["qs_ineligible_arms"] == "B3"
    assert all(s["executed"] is True for s in r["_sims"]) and r["status"] == checks.COMPARABLE   # runs untouched
    piece = r["_qs_val"]["B3"][0]
    assert piece["failed_checks"][0].startswith("diagnosis error") and piece["nodes"] == []
    plant = config.L.QSPlant(config.params_for("P1"), 1.0, config.LIMITS["L-R1"], config.motor_model("M0"))
    s = checks.qs_screen(plant, *(design["eco"]["t"], design["eco"]["v"]))                     # the pure function
    assert s["diagnosis_errors"] and s["diagnosis_errors"][0]["piece"] == 3
    assert "N_A2_failed_check_record" in campaign.IMPLEMENTED_2 and "R9-1" in campaign.IMPLEMENTED_2["N_A2_failed_check_record"]


# ============================================================ R9-2: a measured FAIL stays visible on every path
def test_r9_2_a_fail_relabelled_after_a_recomputation_or_fold_failure_is_kept_and_counted():
    def row():
        return dict(motor="M0", set="SEN", status=checks.COMPARABLE, qs_vs_dyn_pair_status="FAIL",
                    qs_vs_dyn_fail_arms="B0", qs_vs_dyn_pair_reason="x", qs_vs_dyn_pair_status_before_error="",
                    qs_vs_dyn_applicability=checks.QS_APPLICABLE)
    ok = [dict(run_id="r0", recomputed="True", protocol_ok="True"), dict(run_id="r3", recomputed="True", protocol_ok="True")]
    a, b = row(), row()
    campaign.fold_separate_recomputation([a], [_cc()], [], 4)                            # process failure
    campaign.fold_failed([b], "injected")                                                # fold exception
    for r in (a, b):
        assert r["qs_vs_dyn_pair_status"] == checks.QS_RUN_INVALID and r["qs_vs_dyn_pair_status_before_error"] == "FAIL"
    acct = checks.qs_dynamic_accounting([a, b])[0]
    assert acct["fail_before_exception"] == 2 and sum(acct[k] for k in STATUS) == 2
    out = checks.branch_qs_dynamic_outcome("M0", [a, b])
    assert out["n_FAIL_before_exception"] == 2 and out["outcome"] == "INCONCLUSIVE"
    n = row()                                       # not an exception: a run not confirmed (AMB-31), not a failure
    campaign.fold_separate_recomputation([n], [_cc()], [ok[0], dict(ok[1], protocol_ok="False")], 1)
    assert n["qs_vs_dyn_pair_status"] == "FAIL"                                          # B0's FAIL is confirmed
    n = dict(row(), qs_vs_dyn_fail_arms="B3")
    campaign.fold_separate_recomputation([n], [_cc()], [ok[0], dict(ok[1], protocol_ok="False")], 1)
    assert n["qs_vs_dyn_pair_status"] == checks.QS_RUN_INVALID and n["qs_vs_dyn_pair_status_before_error"] == ""


def test_r9_2_a_qs_vs_dynamic_exception_keeps_the_arm_results_and_the_fail(tmp_path, monkeypatch):
    task = _task()
    design = _design(task)
    calls = {"n": 0}

    def qs(*a, **k):                     # B0's comparison is a FAIL; the comparison of B3 then raises
        calls["n"] += 1
        if calls["n"] == 2:
            raise RuntimeError("injected failure of the second comparison")
        return _fail()
    monkeypatch.setattr(checks, "qs_vs_dynamic", qs)
    r = _run(_cond("R92Q"), design, task, tmp_path)
    assert [e["stage"] for e in r["_errors"]] == ["qs_vs_dynamic"]
    assert r["qs_vs_dyn_pair_status"] == CE and r["qs_vs_dyn_fail_arms"] == "B0"
    assert r["qs_vs_dyn_pair_status_before_error"] == "FAIL" and r["qs_vs_dyn_applicability"] == checks.QS_APPLICABLE
    assert r["_rows"]["B0"]["qs_vs_dyn_pct"] == 2.0 and r["_rows"]["B0"]["qs_vs_dyn_status"].startswith("FAIL")


# ============================================================ R9-4: the N/A split and unknown statuses
def test_r9_4_a_qs_vs_dynamic_exception_on_a_not_applicable_pair_keeps_its_label_and_failed_arms(tmp_path, monkeypatch):
    task = _task()
    design = _design(task)
    for obj, name, value in (_screen_fails("B3"), (checks, "pair_qs_dynamic", _boom)):
        monkeypatch.setattr(obj, name, value)
    r = _run(_cond("R94"), design, task, tmp_path)
    assert r["qs_vs_dyn_pair_status"] == CE and r["qs_vs_dyn_pair_status_before_error"] == NA
    assert r["qs_vs_dyn_applicability"] == NA and r["qs_ineligible_arms"] == "B3"
    t = checks.qs_dynamic_accounting([dict(r, motor="M0", set="DEV")])[0]
    assert t["qs_ineligible_pairs"] == t["qs_ineligible_b3_only"] == 1                   # the split adds up
    with pytest.raises(ValueError):
        checks.qs_dynamic_accounting([dict(motor="M0", set="NOM", qs_vs_dyn_pair_status="SKIPPED")])


# ============================================================ R9-6: only pairs with an executed run
def test_r9_6_after_a_recomputation_failure_only_pairs_with_an_executed_run_become_not_evaluable(tmp_path, monkeypatch):
    def row():
        return dict(status="PROFILE_UNAVAILABLE", qs_vs_dyn_pair_status=NA_PROFILE, qs_vs_dyn_fail_arms="",
                    qs_vs_dyn_pair_reason="x")
    for executed, want in ((set(), NA_PROFILE), ({"r0"}, CE), (None, CE)):
        r = row()
        campaign.fold_separate_recomputation([r], [_cc()], [], 4, "", executed)
        assert r["qs_vs_dyn_pair_status"] == want, executed
        r = row()
        campaign.fold_failed([r], "injected", [_cc()], executed)
        assert r["qs_vs_dyn_pair_status"] == want, executed
    real_design, real_run = campaign.plan_design, subprocess.run

    def no_profiles(*a, **k):                                                            # neither profile exists
        d = real_design(*a, **k)
        return dict(d, baseline_ok=False, eco_ok=False, val_e=None,
                    eco={"status": "unavailable", "rows": d["eco"]["rows"], "t": None, "v": None})

    def fake(args, **k):
        res = real_run(args, **k)
        return subprocess.CompletedProcess(args, 4, res.stdout, "RuntimeError: injected crash")
    task = _task()
    monkeypatch.setattr(campaign, "plan_design", no_profiles)
    monkeypatch.setattr(campaign.subprocess, "run", fake)
    c = _cond("R96")
    rows = campaign.execute_schedule([c], lambda n: task, tmp_path / "R96")
    monkeypatch.undo()
    assert rows[0]["qs_vs_dyn_pair_status"] == NA_PROFILE and rows[0]["status"] in checks.PROFILE_FAILURE_STATUSES


# ============================================================ R9-5, R9-3: the candidate and the block
def test_r9_5_the_label_reading_is_marked_in_the_block_and_r9_3_the_condition_status_rows_are_split():
    block = campaign.IMPLEMENTED_2["AMB_29_condition_error"]
    assert "Implementer reading" in block and "owner's confirmation" in block and "I-6b" in block
    text = campaign.DRAFT_AMENDMENT_2.read_text(encoding="utf-8")
    sec = text[text.index("### 1.14 "):text.index("## 2. ")]
    assert "always `NOT_EVALUABLE_CONDITION_ERROR`" in sec and "§3.5" in sec
    s3 = text[text.index("## 3. "):text.index("## 4. ")]
    assert "or the separate recomputation or its fold failed | `NOT_EVALUABLE_CONDITION_ERROR` (I-6)" not in s3
    assert "RECOMPUTATION_DISAGREEMENT" in s3 and "the separate recomputation fails, or its fold raises" in s3


# ============================================================ status v11, candidate rev10, fail-closed
def test_review_status_v11_counts_r9_1_until_verified_and_blocks():
    rv = json.loads(campaign.REVIEW_STATUS.read_text(encoding="utf-8"))
    assert campaign.REVIEW_STATUS.name == "code_review_status_v11.json"
    assert rv["open_critical"] == 0 and rv["open_major"] == 6
    assert set(rv["major_findings"]) == {"R5-1", "R5-2", "R8-1", "R8-2", "R8-3", "R9-1"}
    assert rv["open_owner_decisions"] == [] and rv["reviews_pending"] and "attempt 10" in rv["reviews_pending"][0]
    assert len(rv["implementer_readings_for_owner_confirmation"]) == 2                    # label and R9-6 scope
    b = " | ".join(campaign.preconditions("readiness"))
    assert "6 major findings not resolved" in b and "closure not yet accepted by the owner" in b


def test_rev10_candidate_matches_the_code():
    rev9 = campaign.PILOT_DIR / "03_protocol_v1_amendment_2_rev9_CANDIDATE.md"
    assert frozen.sha256(rev9) == "cdeea032c520f408f1f300a53cf1bc8b1ec4582d80340d3df2c2c94fa5d45719"
    assert campaign.DRAFT_AMENDMENT_2.name == "03_protocol_v1_amendment_2_rev10_CANDIDATE.md"
    r = campaign.read_amendment(campaign.DRAFT_AMENDMENT_2, campaign.IMPLEMENTED_2, {})
    assert r["exists"] and not r["errors"] and r["status"] == "DRAFT", r["errors"]
    text = campaign.DRAFT_AMENDMENT_2.read_text(encoding="utf-8")
    assert "DRAFT — NOT APPROVED FOR RELEASE" in text.splitlines()[2]
    for h in (frozen.FROZEN_SHA256[frozen.PROTOCOL], campaign.AMENDMENT_1_SHA256,
              "cdeea032c520f408f1f300a53cf1bc8b1ec4582d80340d3df2c2c94fa5d45719",
              "f6430bf5512cb56065a2465bcfda1c4c42e244b80f73fcd3e88d985ac8811f7c"):
        assert h in text
    for n, i in zip(range(9, 15), range(1, 7)):
        assert re.search(rf"^### 1\.{n} I-{i}\b", text, re.M), i
    assert r["decisions"]["owner_decisions_open"] == [] and "|\n\n|" not in text
    assert "R9-1" in text and "diagnosis" in text[text.index("### 1.6 "):text.index("### 1.7 ")]


def test_campaign_mode_stays_blocked_in_rev13():
    b = " | ".join(campaign.preconditions("campaign"))
    for x in ("no issued amendment 2", "no campaign authorisation record", "protocol 10.1 gate record",
              "6 major findings not resolved"):
        assert x in b, x
    assert not campaign.CAMPAIGN_AUTHORIZATION.exists() and not campaign.ISSUED_AMENDMENT_2.exists()
