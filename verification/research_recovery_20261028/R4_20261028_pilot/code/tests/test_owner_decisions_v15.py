"""Fixes of the attempt-11 review findings R11-1 to R11-9, rev15 (amendment 2 candidate rev13). Protocol semantics only.
No test computes, reports or targets an energy difference between arms; synthetic numbers in pure-rule tests are not
run energies. Where a test is meant as behavioural evidence against an older version, its first assertions use only
names every version has (review R10-2)."""

import json
import re
import subprocess

import numpy as np
import pytest

from r4h3 import campaign, checks, config, evaluator, frozen
from r4h3 import task as taskmod
from r4h3.closedloop import fixed_gain


def _task(name="GENTLE"):
    v = np.array([0, 0, 0.5, 1, 1.5, 2, 2, 2, 2, 2, 1.5, 1, 1, 1, 1, 1, 1.5, 2, 2, 2, 2, 2, 1.5, 1, 0.5, 0, 0, 0], float)
    return taskmod.task_from_samples(name, np.arange(len(v), dtype=float), v)


def _cond(tag, motor="M0", set_="DEV"):
    cid = f"DEV-V15-{tag}-GENTLE-{motor}-LR1-P1-dt1ms"
    return campaign.Condition(cid, set_, "GENTLE", motor, "L-R1", "P1", 1e-3, None,
                              {b: cid.replace("-dt", f"-{b}-dt") for b in ("B0", "B3")})


def _design(task, motor="M0"):
    return campaign.plan_design(task, "L-R1", config.params_for("P1"), config.motor_model(motor))


def _run(cond, design, task, tmp_path, motor="M0"):
    return campaign.run_condition(cond, task, design, config.params_for("P1"), 1.0, config.LIMITS["L-R1"],
                                  config.motor_model(motor), evaluator.motor_spec_from_protocol(motor, frozen.M1_CURVE),
                                  fixed_gain(config.params_for("P1")), tmp_path)


def _raise_b3(monkeypatch):
    real = campaign.run_arm

    def arm(rid, b, *a, **k):
        if b == "B3":
            raise RuntimeError("injected failure of the attempted run B3")
        return real(rid, b, *a, **k)
    monkeypatch.setattr(campaign, "run_arm", arm)


def _qs(status, pct):
    return lambda *a, **k: dict(motor="M0", E_qs_J=1.0, E_dyn_Wh=1.0, d_ref_m=1.0, e_qs_Wh_per_km=1.0,
                                e_dyn_Wh_per_km=1.0 + pct / 100.0, diff_pct=pct, decisive=True, status=status,
                                non_positive_term="")


def _first_call_raises(obj, name):
    real, n = getattr(obj, name), {"calls": 0}

    def f(*a, **k):
        n["calls"] += 1
        if n["calls"] == 1:
            raise RuntimeError(f"injected failure of the first {name} call")
        return real(*a, **k)
    return f


def _segments(b, marks):
    pos = [b.index(m) for m in marks]
    assert pos == sorted(pos)
    return {m: b[p:(pos[i + 1] if i + 1 < len(pos) else len(b))] for i, (m, p) in enumerate(zip(marks, pos))}


# ============================================================ R11-1, R11-3, R11-9: the machine block
def test_r11_1_the_owner_clauses_hold_only_the_owner_sentences_and_the_reading_has_three_labelled_parts():
    b = campaign.IMPLEMENTED_2["AMB_29_condition_error"]
    marks = ["Owner ruling I-6 (2026-10-28):", "Owner decision I-6b (2026-10-29):",
             "Owner decision (2026-10-29) on a failure of the separate recomputation or its fold:",
             "As applied under these rulings:", "Implementer reading (not an owner ruling), for the owner's confirmation:"]
    seg = _segments(b, marks)
    i6b = seg[marks[1]]
    for owner in ("whose run was attempted but raised an exception", "it must not be labelled NOT_EVALUABLE_RUN_MISSING, "
                  "because the run was attempted and an exception occurred", "a genuinely absent run follows the existing "
                  "missing-run path", "an attempted run that raises follows the condition-error path",
                  "neither may count as PASS"):
        assert owner in i6b, owner
    for gloss in ("executed", "finite", "simulator", "energy"):
        assert gloss not in i6b, gloss                               # review R11-1: no implementer gloss here
    reading = seg[marks[4]]
    assert "(c) the owner's 'genuinely absent run' (I-6b) is the AMB-29(b) case" in reading
    assert "this can change an outcome" in reading                                       # review R11-3: part (a)
    assert reading.count("(no outcome effect)") == 2                                      # parts (b) and (c)
    applied = seg[marks[3]]
    assert "none of whose runs was executed keeps its label" in applied                   # review R11-9
    assert "execution validity" in applied and "recomputation validity" in applied
    # review R11-9: the I-1 and I-4 owner clauses hold the owner's words; details follow under "As implemented"
    s30 = campaign.IMPLEMENTED_2["AMB_30_branch_scope"]
    i1 = s30[s30.index("Owner ruling I-1 (2026-10-28):"):s30.index("As implemented (review R5-2):")]
    assert "duplicated" not in i1 and "no profile" not in i1
    assert "a missing, invalid, unevaluable or NOT_APPLICABLE required nominal cell cannot count as PASS" in i1
    s31 = campaign.IMPLEMENTED_2["AMB_31_energy_of_invalid_runs"]
    i4 = s31[s31.index("Owner ruling I-4 (2026-10-28):"):s31.index("As implemented:")]
    assert "in-process" not in i4 and "if either run is not confirmed, it cannot supply confirmatory evidence" in i4
    rv = json.loads(campaign.REVIEW_STATUS.read_text(encoding="utf-8"))
    assert "executed run" not in rv["owner_rulings_implemented"]["I-6b"]
    assert "(c)" in rv["implementer_readings_for_owner_confirmation"][0] and len(rv["implementer_readings_for_owner_confirmation"]) == 1


# ============================================================ R11-2, R11-3, R11-5: the candidate text
def test_r11_2_r11_3_r11_5_the_candidate_quotes_the_owner_in_full_and_states_the_effects():
    text = campaign.DRAFT_AMENDMENT_2.read_text(encoding="utf-8")
    s15 = text[text.index("### 1.15 "):text.index("### 1.16 ")]
    quote = s15.split('Owner\'s words: "', 1)[1].split('"\n', 1)[0]
    assert quote.endswith("Do not perform a broad label rewrite. Inspect the affected branch and its tests, then verify "
                          "all exception paths retain their intended classification and reporting.")
    assert "executed run" not in quote                                                    # the owner's words only
    s14 = text[text.index("### 1.14 "):text.index("### 1.15 ")]
    assert "**This part can change an outcome.**" in s14 and s14.count("No outcome effect") == 2
    assert "It changes no branch outcome, which is INCONCLUSIVE either way" not in text
    s12 = text[text.index("## 12. "):text.index("## 13. ")]
    assert "zz_code_changes_rev14_to_rev15.csv" in s12 and "zz_line_endings_rev14_to_rev15.csv" in s12
    assert "written after the review of release attempt 12" in text.splitlines()[10]


# ============================================================ R11-4: I6FL as its own test (behavioural on rev13 and rev11)
def test_r11_4_a_raised_run_with_a_failing_other_arm_is_condition_error_with_the_fail_kept(tmp_path, monkeypatch):
    task = _task()
    design = _design(task)
    _raise_b3(monkeypatch)
    monkeypatch.setattr(checks, "qs_vs_dynamic", _qs("FAIL (branch INCONCLUSIVE, protocol 9)", 2.0))   # B0 FAILs
    r = _run(_cond("R114"), design, task, tmp_path)
    assert r["qs_vs_dyn_pair_status"] == "NOT_EVALUABLE_CONDITION_ERROR"                  # rev13: RUN_MISSING; rev11: FAIL
    assert r["qs_vs_dyn_pair_status_before_error"] == "FAIL" and r["qs_vs_dyn_fail_arms"] == "B0"


# ============================================================ R11-7: forced PASS, other motors and arms, fold_failed path
def test_r11_7_an_exception_overrides_a_forced_pass(tmp_path, monkeypatch):
    task = _task()
    design = _design(task)
    monkeypatch.setattr(checks, "qs_vs_dynamic", _qs("pass", 0.5))                        # both arms within 1 %
    r = _run(_cond("R117P0"), design, task, tmp_path / "ctrl")
    assert r["qs_vs_dyn_pair_status"] == "PASS" and r["_errors"] == []                    # the control is a PASS
    monkeypatch.setattr(checks, "failed_criteria", _first_call_raises(checks, "failed_criteria"))
    r = _run(_cond("R117P1"), design, task, tmp_path / "exc")
    assert r["qs_vs_dyn_pair_status"] == "NOT_EVALUABLE_CONDITION_ERROR" and r["qs_vs_dyn_pair_status_before_error"] == "PASS"


@pytest.mark.parametrize("motor", ["M1", "M2"])
def test_r11_7_an_attempted_run_that_raised_is_condition_error_for_m1_and_m2(tmp_path, monkeypatch, motor):
    task = _task()
    design = _design(task, motor)
    _raise_b3(monkeypatch)
    r = _run(_cond("R117" + motor, motor), design, task, tmp_path, motor)
    assert r["qs_vs_dyn_applicability"] == checks.QS_APPLICABLE
    assert r["qs_vs_dyn_pair_status"] == checks.QS_CONDITION_ERROR
    assert r["qs_vs_dyn_pair_status_before_error"] in (checks.QS_NOT_EVALUABLE, "FAIL")  # B0 may FAIL on this motor


def test_r11_7_an_attempted_run_that_raised_beside_an_unconfirmed_arm_is_condition_error(tmp_path, monkeypatch):
    task = _task()
    design = _design(task)
    _raise_b3(monkeypatch)
    real = evaluator.compare_with_simulator
    monkeypatch.setattr(campaign.evaluator, "compare_with_simulator",
                        lambda *a, **k: dict(real(*a, **k), protocol_ok=False))           # B0 not confirmed in process
    r = _run(_cond("R117U"), design, task, tmp_path)
    assert r["_rows"]["B0"]["recompute_protocol_ok"] is False
    assert r["qs_vs_dyn_pair_status"] == checks.QS_CONDITION_ERROR


def test_r11_7_a_fold_exception_keeps_the_label_of_a_pair_without_an_executed_run(tmp_path, monkeypatch):
    real_design = campaign.plan_design

    def no_profiles(*a, **k):
        d = real_design(*a, **k)
        return dict(d, baseline_ok=False, eco_ok=False, val_e=None,
                    eco={"status": "unavailable", "rows": d["eco"]["rows"], "t": None, "v": None})

    def boom(*a, **k):
        raise RuntimeError("injected fold failure")
    task = _task()
    monkeypatch.setattr(campaign, "plan_design", no_profiles)
    monkeypatch.setattr(campaign, "fold_separate_recomputation", boom)
    rows = campaign.execute_schedule([_cond("R117F")], lambda n: task, tmp_path / "R117F")
    monkeypatch.undo()
    assert rows[0]["qs_vs_dyn_pair_status"] == "NOT_APPLICABLE_PROFILE_UNAVAILABLE"     # rev12: CONDITION_ERROR
    assert rows[0]["separate_recomputation"].startswith("not applied: the fold raised")


# ============================================================ R11-6, R11-8
def test_r11_6_the_fold_rejects_a_length_mismatch():
    c = type("C", (), {"run_ids": {"B0": "y0", "B3": "y3"}})()
    rows = [dict(status=checks.COMPARABLE, qs_vs_dyn_pair_status="PASS") for _ in range(2)]
    with pytest.raises(ValueError):
        campaign.fold_separate_recomputation(rows, [c], [], 0)


def test_r11_8_the_reason_cites_i6b_only_for_a_qs_eligible_pair(tmp_path, monkeypatch):
    task = _task()
    design = _design(task)
    _raise_b3(monkeypatch)
    r = _run(_cond("R118E"), design, task, tmp_path / "e")
    assert "owner decision I-6b" in r["qs_vs_dyn_pair_reason"]
    real = checks.qs_energy

    def screen(plant, t, v):                                                              # B0's screen fails
        res = real(plant, t, v)
        if len(t) > 2 and np.allclose(np.diff(t), 1.0):
            return dict(res, feasible=False, n_infeasible_pieces=1,
                        infeasible_pieces=[dict(piece=3, t0_s=3.0, t1_s=4.0, v0_ms=1.0, v1_ms=1.5)])
        return res
    monkeypatch.setattr(checks, "qs_energy", screen)
    r = _run(_cond("R118N"), design, task, tmp_path / "n")
    assert r["qs_vs_dyn_applicability"] == checks.QS_NA_INFEASIBLE and r["qs_vs_dyn_pair_status"] == checks.QS_CONDITION_ERROR
    assert "owner decision I-6b" not in r["qs_vs_dyn_pair_reason"]


# ============================================================ status v14, candidate rev13, fail-closed
def test_review_status_v14_counts_r11_1_and_records_no_owner_acceptance():
    rv = json.loads(campaign.REVIEW_STATUS.read_text(encoding="utf-8"))
    assert campaign.REVIEW_STATUS.name == "code_review_status_v14.json"
    assert rv["open_critical"] == 0 and rv["open_major"] == 7
    assert set(rv["major_findings"]) == {"R5-1", "R5-2", "R8-1", "R8-2", "R8-3", "R9-1", "R11-1"}
    assert rv["owner_acceptance_of_major_closures"].startswith("not recorded")
    assert "NOT_EVALUABLE_CONDITION_ERROR" in rv["major_findings"]["R8-1"].split("note (review R11-8)")[1]
    assert rv["open_owner_decisions"] == [] and rv["reviews_pending"] and "attempt 12" in rv["reviews_pending"][0]
    b = " | ".join(campaign.preconditions("readiness"))
    assert "7 major findings not resolved" in b and "closure not yet accepted by the owner" in b


def test_rev13_candidate_matches_the_code():
    assert frozen.sha256(campaign.PILOT_DIR / "03_protocol_v1_amendment_2_rev12_CANDIDATE.md") == \
        "ac376c0b362c2e99a9d3777fa849205844487e0be50a41dd1c5f1b2410b5ae1b"
    assert campaign.DRAFT_AMENDMENT_2.name == "03_protocol_v1_amendment_2_rev13_CANDIDATE.md"
    r = campaign.read_amendment(campaign.DRAFT_AMENDMENT_2, campaign.IMPLEMENTED_2, {})
    assert r["exists"] and not r["errors"] and r["status"] == "DRAFT", r["errors"]
    text = campaign.DRAFT_AMENDMENT_2.read_text(encoding="utf-8")
    assert "DRAFT — NOT APPROVED FOR RELEASE" in text.splitlines()[2]
    for h in (frozen.FROZEN_SHA256[frozen.PROTOCOL], campaign.AMENDMENT_1_SHA256,
              "ac376c0b362c2e99a9d3777fa849205844487e0be50a41dd1c5f1b2410b5ae1b",
              "162b688d2a1665831705bc3a1bc68273f5ede15cc87b0d226837cf4f015998e9",
              "5479f0e81b981c7977ea5a416762972d2a332d4fdb75beee7ad8379ade399804"):
        assert h in text
    for n, i in zip(range(9, 15), range(1, 7)):
        assert re.search(rf"^### 1\.{n} I-{i}\b", text, re.M), i
    assert re.search(r"^### 1\.15 I-6b\b", text, re.M) and re.search(r"^### 1\.16 I-6: scope", text, re.M)
    assert r["decisions"]["owner_decisions_open"] == [] and "|\n\n|" not in text


def test_campaign_mode_stays_blocked_in_rev15():
    b = " | ".join(campaign.preconditions("campaign"))
    for x in ("no issued amendment 2", "no campaign authorisation record", "protocol 10.1 gate record",
              "7 major findings not resolved", "code review not yet performed"):
        assert x in b, x
    assert not campaign.CAMPAIGN_AUTHORIZATION.exists() and not campaign.ISSUED_AMENDMENT_2.exists()
    assert not campaign.APPROVAL_RECORD_2.exists()
