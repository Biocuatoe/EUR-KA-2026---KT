"""The owner's decisions of 2026-10-29 (I-6b; the scope of the I-6 relabelling after a failure of the separate
recomputation or its fold) and the fixes of the attempt-10 review findings R10-1 to R10-4, rev14 (amendment 2 candidate
rev12). Protocol semantics only. No test computes, reports or targets an energy difference between arms; synthetic
numbers in pure-rule tests are not run energies."""

import json
import re
import subprocess

import numpy as np
import pytest

from r4h3 import campaign, checks, config, evaluator, frozen
from r4h3 import task as taskmod
from r4h3.closedloop import fixed_gain

NA, NA_PROFILE, CE = checks.QS_NA_INFEASIBLE, checks.QS_NA_PROFILE, checks.QS_CONDITION_ERROR
MISSING, INVALID, UNDEF = checks.QS_NOT_EVALUABLE, checks.QS_RUN_INVALID, checks.QS_UNDEFINED


def _task(name="GENTLE"):
    v = np.array([0, 0, 0.5, 1, 1.5, 2, 2, 2, 2, 2, 1.5, 1, 1, 1, 1, 1, 1.5, 2, 2, 2, 2, 2, 1.5, 1, 0.5, 0, 0, 0], float)
    return taskmod.task_from_samples(name, np.arange(len(v), dtype=float), v)


def _cond(tag, set_="DEV"):
    cid = f"DEV-V14-{tag}-GENTLE-M0-LR1-P1-dt1ms"
    return campaign.Condition(cid, set_, "GENTLE", "M0", "L-R1", "P1", 1e-3, None,
                              {b: cid.replace("-dt", f"-{b}-dt") for b in ("B0", "B3")})


def _design(task):
    return campaign.plan_design(task, "L-R1", config.params_for("P1"), config.motor_model("M0"))


def _run(cond, design, task, tmp_path):
    return campaign.run_condition(cond, task, design, config.params_for("P1"), 1.0, config.LIMITS["L-R1"],
                                  config.motor_model("M0"), evaluator.motor_spec_from_protocol("M0", frozen.M1_CURVE),
                                  fixed_gain(config.params_for("P1")), tmp_path)


def _arm(branch, how):
    """Patch run_arm: the given branch either raises (an attempted run) or returns a non-finite simulator energy."""
    real = campaign.run_arm

    def arm(rid, b, *a, **k):
        if b == branch and how == "raise":
            raise RuntimeError(f"injected failure of the attempted run {b}")
        sim, ev, st, cmp = real(rid, b, *a, **k)
        if b == branch and how == "nonfinite":
            sim = dict(sim, E_net_Wh=float("nan"))
        return sim, ev, st, cmp
    return campaign, "run_arm", arm


def _first_call_raises(obj, name):
    real, n = getattr(obj, name), {"calls": 0}

    def f(*a, **k):
        n["calls"] += 1
        if n["calls"] == 1:
            raise RuntimeError(f"injected failure of the first {name} call")
        return real(*a, **k)
    return obj, name, f


def _fail():
    return dict(motor="M0", E_qs_J=1.0, E_dyn_Wh=1.0, d_ref_m=1.0, e_qs_Wh_per_km=1.0, e_dyn_Wh_per_km=1.02,
                diff_pct=2.0, decisive=True, status="FAIL (branch INCONCLUSIVE, protocol 9)", non_positive_term="")


# ============================================================ owner decision I-6b
def test_i6b_an_attempted_run_that_raised_is_condition_error_never_run_missing(tmp_path, monkeypatch):
    task = _task()
    design = _design(task)
    monkeypatch.setattr(*_arm("B3", "raise"))
    c = _cond("I6BR")
    r = _run(c, design, task, tmp_path / "raise")
    assert r["qs_vs_dyn_pair_status"] == CE and r["qs_vs_dyn_pair_status_before_error"] == MISSING
    assert r["qs_vs_dyn_applicability"] == checks.QS_APPLICABLE and r["qs_eligible_pair"] is True   # QS-eligible
    assert "owner decision I-6b" in r["qs_vs_dyn_pair_reason"] and r["status"] == "ERROR"
    e = [x for x in r["_errors"] if x["stage"] == "run"]
    assert len(e) == 1 and e[0]["run_id"] == c.run_ids["B3"] and "injected failure" in e[0]["traceback"]
    sims = {s["branch"]: s for s in r["_sims"]}
    assert sims["B0"]["executed"] is True and sims["B3"]["executed"] is False             # no retry, no replacement
    monkeypatch.setattr(checks, "qs_vs_dynamic", lambda *a, **k: _fail())                # B0's measured FAIL
    r = _run(_cond("I6BF"), design, task, tmp_path / "fail")
    assert r["qs_vs_dyn_pair_status"] == CE and r["qs_vs_dyn_pair_status_before_error"] == "FAIL"
    assert r["qs_vs_dyn_fail_arms"] == "B0"                                              # the failure stays visible


def test_i6b_a_genuinely_absent_run_energy_stays_on_the_missing_run_path(tmp_path, monkeypatch):
    task = _task()
    design = _design(task)
    monkeypatch.setattr(*_arm("B3", "nonfinite"))                    # executed, no finite energy, no exception
    r = _run(_cond("I6BN"), design, task, tmp_path / "nf")
    assert r["_errors"] == [] and r["qs_vs_dyn_pair_status"] == MISSING
    assert r["qs_vs_dyn_pair_status_before_error"] == ""
    monkeypatch.setattr(*_first_call_raises(checks, "failed_criteria"))  # then a run_report exception (not a run)
    r = _run(_cond("I6BNR"), design, task, tmp_path / "nfr")
    assert [x["stage"] for x in r["_errors"]] == ["run_report"]
    assert r["qs_vs_dyn_pair_status"] == MISSING                     # implementer reading (b): the NE label stays


def test_i6b_neither_label_counts_as_pass_and_an_exception_overrides_a_pass(tmp_path, monkeypatch):
    for label in (CE, MISSING):
        rows = [dict(motor="M0", set="NOM", limits="L-R1", condition_id="a", qs_vs_dyn_pair_status="PASS"),
                dict(motor="M0", set="NOM", limits="L-EVE", condition_id="b", qs_vs_dyn_pair_status=label)]
        out = checks.branch_qs_dynamic_outcome("M0", rows, ["a", "b"])
        assert out["outcome"] == "INCONCLUSIVE" and out["n_PASS_nominal"] == 1, label
    task = _task()
    design = _design(task)
    r = _run(_cond("I6BP0"), design, task, tmp_path / "ctrl")                            # control: no exception
    assert r["qs_vs_dyn_pair_status"] in ("PASS", "FAIL") and r["_errors"] == []
    monkeypatch.setattr(*_first_call_raises(checks, "failed_criteria"))
    r2 = _run(_cond("I6BP1"), design, task, tmp_path / "exc")
    assert r2["qs_vs_dyn_pair_status"] == CE and r2["qs_vs_dyn_pair_status_before_error"] == r["qs_vs_dyn_pair_status"]


# ============================================================ owner decision: recomputation or fold failure scope
CASES = [  # label before, executed run?, expected after an exception-driven fold relabel, before_error
    (NA, True, CE, NA), (NA_PROFILE, True, CE, NA_PROFILE), (NA_PROFILE, False, NA_PROFILE, ""),
    (NA, False, NA, ""), ("PASS", True, INVALID, "PASS"), ("FAIL", True, INVALID, "FAIL"),
    ("REPORTED_ONLY", True, INVALID, "REPORTED_ONLY"), (MISSING, True, MISSING, ""), (UNDEF, True, UNDEF, ""),
    (INVALID, True, INVALID, ""), (CE, True, CE, "")]


def _rows_and_conds():
    rows, conds, executed = [], [], set()
    for i, (label, ex, _, _) in enumerate(CASES):
        ids = {"B0": f"r{i}b0", "B3": f"r{i}b3"}
        conds.append(type("C", (), {"run_ids": ids})())
        rows.append(dict(status=checks.COMPARABLE, qs_vs_dyn_pair_status=label, qs_vs_dyn_fail_arms="B0" if label == "FAIL"
                         else "", qs_vs_dyn_pair_reason="x", qs_vs_dyn_pair_status_before_error=""))
        if ex:
            executed.add(ids["B0"])                                  # one executed run is enough
    return rows, conds, executed


@pytest.mark.parametrize("path", ["exit4", "launch", "unreadable", "fold_failed"])
def test_after_a_recomputation_or_fold_failure_only_executed_na_pairs_are_relabelled(path):
    rows, conds, executed = _rows_and_conds()
    if path == "fold_failed":
        campaign.fold_failed(rows, "injected", conds, executed)
    else:
        exit_, err = {"exit4": (4, ""), "launch": (-1, "launch"), "unreadable": (0, "unreadable output")}[path]
        campaign.fold_separate_recomputation(rows, conds, [], exit_, err, executed)
    for r, (label, ex, want, before) in zip(rows, CASES):
        assert r["qs_vs_dyn_pair_status"] == want, (path, label, ex)
        assert r["qs_vs_dyn_pair_status_before_error"] == before, (path, label, ex)
        assert r["status"] == "RECOMPUTATION_DISAGREEMENT" and r["paired_endpoint_eligible"] is False   # never COMPARABLE
    assert not any(r["qs_vs_dyn_pair_status"] == "PASS" for r in rows)
    assert {r["qs_vs_dyn_pair_status"] for r in rows if r["qs_vs_dyn_pair_status"] in checks.PAIR_STATUS_CLASSES[
        "NOT_APPLICABLE"]} <= {NA_PROFILE, NA}                                            # only the unexecuted pairs


def test_without_a_recomputation_failure_no_na_pair_is_relabelled():
    rows, conds, executed = _rows_and_conds()
    sep = [dict(run_id=rid, recomputed="True", protocol_ok="True") for c in conds for rid in c.run_ids.values()]
    campaign.fold_separate_recomputation(rows, conds, sep, 0, "", executed)              # all confirmed
    assert [r["qs_vs_dyn_pair_status"] for r in rows] == [c[0] for c in CASES]
    rows, conds, executed = _rows_and_conds()
    sep[0] = dict(sep[0], protocol_ok="False")                                            # one run not confirmed (I-4)
    sep = [dict(s, protocol_ok="False") if s["run_id"].endswith("b3") else s for s in sep]
    campaign.fold_separate_recomputation(rows, conds, sep, 1, "", executed)
    for r, (label, *_r) in zip(rows, CASES):
        if label in ("PASS", "REPORTED_ONLY"):                    # used unconfirmed energy: RUN_INVALID, not an exception
            assert r["qs_vs_dyn_pair_status"] == INVALID and r["qs_vs_dyn_pair_status_before_error"] == ""
        elif label in checks.PAIR_STATUS_CLASSES["NOT_APPLICABLE"]:
            assert r["qs_vs_dyn_pair_status"] == label                                    # no exception: N/A stays


# ============================================================ R10-2: behavioural on the old code
def test_r10_2_after_a_process_failure_a_pair_without_an_executed_run_keeps_its_label_in_the_executor(tmp_path,
                                                                                                         monkeypatch):
    real_design, real_run = campaign.plan_design, subprocess.run

    def no_profiles(*a, **k):
        d = real_design(*a, **k)
        return dict(d, baseline_ok=False, eco_ok=False, val_e=None,
                    eco={"status": "unavailable", "rows": d["eco"]["rows"], "t": None, "v": None})

    def fake(args, **k):
        res = real_run(args, **k)
        return subprocess.CompletedProcess(args, 4, res.stdout, "RuntimeError: injected crash")
    task = _task()
    monkeypatch.setattr(campaign, "plan_design", no_profiles)
    monkeypatch.setattr(campaign.subprocess, "run", fake)
    rows = campaign.execute_schedule([_cond("R102")], lambda n: task, tmp_path / "R102")
    monkeypatch.undo()
    assert rows[0]["qs_vs_dyn_pair_status"] == NA_PROFILE and rows[0]["status"] in checks.PROFILE_FAILURE_STATUSES


def test_r10_2_the_accounting_rejects_an_unknown_pair_status():
    with pytest.raises(ValueError):
        checks.qs_dynamic_accounting([dict(motor="M0", set="NOM", qs_vs_dyn_pair_status="SKIPPED")])


def test_r10_2_r3_9_eligibility_stays_known_when_the_pair_evaluation_raised(tmp_path, monkeypatch):
    # the rev12 change behind the R3-9 assertion (review R8-2), asserted with names every version has, so that the test
    # fails on rev11 by its behaviour (rev11 gave qs_eligible_pair None), not on a missing name
    def boom(*a, **k):
        raise RuntimeError("injected pair failure")
    task = _task()
    design = _design(task)
    monkeypatch.setattr(checks, "pair_qs_dynamic", boom)
    r = _run(_cond("R1039"), design, task, tmp_path)
    assert r["qs_vs_dyn_pair_status"] == "NOT_EVALUABLE_CONDITION_ERROR"
    assert r["qs_vs_dyn_applicability"] == "APPLICABLE" and r["qs_eligible_pair"] is True


# ============================================================ R10-4
def test_r10_4_fold_failed_with_fewer_conditions_than_rows_does_not_raise():
    c = type("C", (), {"run_ids": {"B0": "x0", "B3": "x3"}})()
    rows = [dict(status=checks.COMPARABLE, qs_vs_dyn_pair_status=NA_PROFILE, qs_vs_dyn_pair_reason="x") for _ in range(2)]
    campaign.fold_failed(rows, "injected", [c], set())                                    # one condition, two rows
    assert rows[0]["qs_vs_dyn_pair_status"] == NA_PROFILE                                 # matched, not executed
    assert rows[1]["qs_vs_dyn_pair_status"] == CE                                         # unmatched: fail-closed
    assert all(r["status"] == "RECOMPUTATION_DISAGREEMENT" for r in rows)


# ============================================================ R10-1: the block separates rulings, decisions and readings
def test_r10_1_the_block_states_only_owner_decisions_as_rulings_and_labels_the_implementer_reading():
    b = campaign.IMPLEMENTED_2["AMB_29_condition_error"]
    marks = ["owner ruling 2026-10-28 (AMB-29(d)):", "Owner ruling I-6 (2026-10-28):", "Owner decision I-6b (2026-10-29):",
             "Owner decision (2026-10-29) on a failure of the separate recomputation or its fold:",
             "As applied under these rulings:", "Implementer reading (not an owner ruling), for the owner's confirmation:"]
    pos = [b.index(m) for m in marks]
    assert pos == sorted(pos) and all(b.count(m) == 1 for m in marks)
    seg = {m: b[p:(pos[i + 1] if i + 1 < len(pos) else len(b))] for i, (m, p) in enumerate(zip(marks, pos))}
    i6 = seg[marks[1]]
    # rev15 (review R11-1): the owner's own words, "the pair's QS check"
    assert "if a run or evaluation raises an exception, the pair becomes NOT_EVALUABLE even if the pair's QS check " \
           "would otherwise be NOT_APPLICABLE" in i6
    for word in ("executed run", "RUN_MISSING", "keeps that label", "recorded stage", "Implementer"):
        assert word not in i6, word                                  # the owner's ruling holds only the owner's words
    # rev15 (review R11-1): the I-6b clause holds only the owner's sentences; the "genuinely absent run" mapping is a
    # labelled implementer reading (c)
    assert CE in seg[marks[2]] and f"must not be labelled {MISSING}" in seg[marks[2]]
    assert "a genuinely absent run follows the existing missing-run path" in seg[marks[2]]
    assert "executed run" not in seg[marks[2]] and "finite" not in seg[marks[2]]
    assert "actually executed run" in seg[marks[3]] and "must not retain N/A" in seg[marks[3]]
    applied = seg[marks[4]]
    assert INVALID in applied and "(AMB-31, I-4)" in applied and "remain applicable under their own rules" in applied
    assert all(lbl in applied for lbl in (MISSING, UNDEF, INVALID)) and "no pair becomes NOT_APPLICABLE_* or PASS" in applied
    reading = seg[marks[5]]
    assert "(a) every recorded stage" in reading and "(b) after an exception at a stage other than one of its runs" in reading
    assert "(c) the owner's 'genuinely absent run' (I-6b)" in reading                    # rev15 (review R11-1)
    assert b.count("Implementer reading") == 1 and "Implementer reading of the standing AMB-29(b)" not in b
    text = campaign.DRAFT_AMENDMENT_2.read_text(encoding="utf-8")                        # the candidate agrees
    r = campaign.read_amendment(campaign.DRAFT_AMENDMENT_2, campaign.IMPLEMENTED_2, {})
    assert not r["errors"] and r["decisions"]["AMB_29_condition_error"] == b
    s14 = text[text.index("### 1.14 "):text.index("### 1.15 ")]
    for h in ("**Owner rulings and decisions.**", "**As applied.**",
              "**Implementer reading (not an owner ruling), for the owner's confirmation.**"):
        assert s14.count(h) == 1, h
    s15 = text[text.index("### 1.15 "):text.index("### 1.16 ")]
    s16 = text[text.index("### 1.16 "):text.index("## 2. ")]
    assert "It must not be labelled `NOT_EVALUABLE_RUN_MISSING`, because the run was attempted and an exception " \
           "occurred." in s15 and "(owner decision 2026-10-29)" in s15.splitlines()[0]
    assert "Only a pair currently classified as `NOT_APPLICABLE_*` with an actually executed run is eligible for the " \
           "I-6 relabelling described here." in s16 and "(owner decision 2026-10-29)" in s16.splitlines()[0]


# ============================================================ R10-3: counts and provenance in the candidate
def test_r10_3_the_candidate_states_counts_and_lineage_accurately():
    # rev15: the header counts are checked in rev12 (by path), the candidate that fixed R10-3; the lineage in the
    # live candidate as well
    rev12 = (campaign.PILOT_DIR / "03_protocol_v1_amendment_2_rev12_CANDIDATE.md").read_text(encoding="utf-8")
    assert "six of its notes" not in rev12 and "(one MINOR finding and three notes)" in rev12.splitlines()[2]
    text = campaign.DRAFT_AMENDMENT_2.read_text(encoding="utf-8")
    assert "six of its notes" not in text
    for t in (rev12, text):
        assert not re.search(r"^### .*unchanged from rev", t, re.M)
        h = {n: re.search(rf"^### 1\.{n} .*$", t, re.M).group(0) for n in (1, 2, 3)}
        assert h[1].endswith("first stated in rev0)") and "first stated in rev4" in h[2] and "first stated in rev4" in h[3]
    rev0 = campaign.PILOT_DIR / "archive/rev4a_reviewed_20261028_0957/03_protocol_v1_amendment_2_DRAFT.md"
    assert frozen.sha256(rev0) == "c3e1ddfce7dca7909bb1cd2a6186f4d5044b5dfe81eeed43df0b9fcf215957d4"
    assert "## 1. The owner's ruling (N-A2)" in rev0.read_text(encoding="utf-8")         # N-A2 is in rev0
    rev3 = (campaign.PILOT_DIR / "03_protocol_v1_amendment_2_DRAFT.md").read_text(encoding="utf-8")
    rev4 = (campaign.PILOT_DIR / "03_protocol_v1_amendment_2_rev4_CANDIDATE.md").read_text(encoding="utf-8")
    assert not re.search(r"^### .*AMB-29\(a\)", rev3, re.M) and re.search(r"^### 1\.2 AMB-29\(a\)", rev4, re.M)
    assert re.search(r"^### 1\.3 AMB-31", rev4, re.M)                                     # first stated in rev4
    s11 = text[text.index("### 1.1 "):text.index("### 1.2 ")]
    ruling = s11.split("\n\n")[0]
    assert "diagnosis" not in ruling and "Implementation note (added in rev10, review R9-1; not part of the ruling)" in s11


# ============================================================ status v13, candidate rev12, fail-closed
def test_review_status_v13_keeps_the_six_major_findings_open_pending_owner_acceptance(monkeypatch):
    # rev15: v13 is read by path (the live file is checked in test_owner_decisions_v15.py)
    v13 = frozen.PILOT / "config" / "code_review_status_v13.json"
    rv = json.loads(v13.read_text(encoding="utf-8"))
    monkeypatch.setattr(campaign, "REVIEW_STATUS", v13)
    assert rv["open_critical"] == 0 and rv["open_major"] == 6
    assert set(rv["major_findings"]) == {"R5-1", "R5-2", "R8-1", "R8-2", "R8-3", "R9-1"}
    assert rv["owner_acceptance_of_major_closures"].startswith("not recorded")
    assert "I-6b" in rv["owner_rulings_implemented"] and "I-6 recomputation or fold failure scope" in rv["owner_rulings_implemented"]
    assert len(rv["implementer_readings_for_owner_confirmation"]) == 1 and len(rv["implementer_readings_decided_by_owner"]) == 2
    assert rv["open_owner_decisions"] == [] and rv["reviews_pending"] and "attempt 11" in rv["reviews_pending"][0]
    b = " | ".join(campaign.preconditions("readiness"))
    assert "6 major findings not resolved" in b and "closure not yet accepted by the owner" in b


def test_rev12_candidate_is_pinned_and_earlier_candidates_are_pinned():   # rev15: renamed; code match in v15 tests
    for n, h in ((10, "5479f0e81b981c7977ea5a416762972d2a332d4fdb75beee7ad8379ade399804"),
                 (11, "162b688d2a1665831705bc3a1bc68273f5ede15cc87b0d226837cf4f015998e9"),
                 (12, "ac376c0b362c2e99a9d3777fa849205844487e0be50a41dd1c5f1b2410b5ae1b")):
        assert frozen.sha256(campaign.PILOT_DIR / f"03_protocol_v1_amendment_2_rev{n}_CANDIDATE.md") == h, n
    rev12 = campaign.PILOT_DIR / "03_protocol_v1_amendment_2_rev12_CANDIDATE.md"
    r = campaign.read_amendment(rev12)
    assert r["exists"] and r["status"] == "DRAFT"
    text = rev12.read_text(encoding="utf-8")
    assert "DRAFT — NOT APPROVED FOR RELEASE" in text.splitlines()[2]
    for h in (frozen.FROZEN_SHA256[frozen.PROTOCOL], campaign.AMENDMENT_1_SHA256,
              "162b688d2a1665831705bc3a1bc68273f5ede15cc87b0d226837cf4f015998e9",
              "5479f0e81b981c7977ea5a416762972d2a332d4fdb75beee7ad8379ade399804"):
        assert h in text
    for n, i in zip(range(9, 15), range(1, 7)):
        assert re.search(rf"^### 1\.{n} I-{i}\b", text, re.M), i
    assert re.search(r"^### 1\.15 I-6b\b", text, re.M) and re.search(r"^### 1\.16 I-6: scope", text, re.M)
    assert r["decisions"]["owner_decisions_open"] == [] and "|\n\n|" not in text


def test_campaign_mode_stays_blocked_in_rev14():
    b = " | ".join(campaign.preconditions("campaign"))
    n = json.loads(campaign.REVIEW_STATUS.read_text(encoding="utf-8"))["open_major"]        # rev15: the live count
    assert n >= 6
    for x in ("no issued amendment 2", "no campaign authorisation record", "protocol 10.1 gate record",
              f"{n} major findings not resolved", "code review not yet performed"):
        assert x in b, x
    assert not campaign.CAMPAIGN_AUTHORIZATION.exists() and not campaign.ISSUED_AMENDMENT_2.exists()
    assert not campaign.APPROVAL_RECORD_2.exists()
