"""Fixes of the attempt-8 review findings R8-1 to R8-6 and R8-8 to R8-10, rev12 (amendment 2 candidate rev9).
Protocol semantics only. No test computes, reports or targets an energy difference between arms; synthetic numbers in
pure-rule tests are not run energies."""

import csv
import json
import re
import subprocess
from pathlib import Path

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
    cid = f"DEV-V12-{tag}-GENTLE-M0-LR1-P1-dt1ms"
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


def _is_b0(t):                    # B0 tracks the 1 s grid profile, B3 the S-eco knots
    return len(t) > 2 and np.allclose(np.diff(t), 1.0)


def _screen_fails(arm):
    """Patch: the QS screen of one arm reports infeasible."""
    real = checks.qs_energy

    def screen(plant, t, v):
        r = real(plant, t, v)
        if (arm == "B0") == _is_b0(t):
            return dict(r, feasible=False, n_infeasible_pieces=1,
                        infeasible_pieces=[dict(piece=3, t0_s=3.0, t1_s=4.0, v0_ms=1.0, v1_ms=1.5)])
        return r
    return checks, "qs_energy", screen


def _arm_raises(branch):
    real = campaign.run_arm

    def arm(rid, b, *a, **k):
        if b == branch:
            raise RuntimeError(f"injected evaluation failure of {b}")
        return real(rid, b, *a, **k)
    return campaign, "run_arm", arm


def _first_call_raises(obj, name):
    real, n = getattr(obj, name), {"calls": 0}

    def f(*a, **k):
        n["calls"] += 1
        if n["calls"] == 1:
            raise RuntimeError(f"injected failure of the first {name} call")
        return real(*a, **k)
    return obj, name, f


def _fail_both():
    fail = dict(motor="M0", E_qs_J=1.0, E_dyn_Wh=1.0, d_ref_m=1.0, e_qs_Wh_per_km=1.0, e_dyn_Wh_per_km=1.02,
                diff_pct=2.0, decisive=True, status="FAIL (branch INCONCLUSIVE, protocol 9)", non_positive_term="")
    return checks, "qs_vs_dynamic", lambda *a, **k: dict(fail)


def _schedule(tmp_path, monkeypatch, tag, patches=(), fake=None):
    task = _task()
    for obj, name, value in patches:
        monkeypatch.setattr(obj, name, value)
    if fake is not None:
        monkeypatch.setattr(campaign.subprocess, "run", fake)
    c = _cond(tag)
    out = tmp_path / tag
    rows = campaign.execute_schedule([c], lambda n: task, out)
    monkeypatch.undo()

    def read(name):
        return list(csv.DictReader((out / name).open(encoding="utf-8")))
    return c, out, rows, read


# ============================================================ R8-1 (MAJOR), R8-6: no label survives an exception
def test_r8_1_a_measured_fail_never_survives_an_exception_and_stays_visible(tmp_path, monkeypatch):
    task = _task()
    design = _design(task)
    for obj, name, value in (_fail_both(), _first_call_raises(checks, "failed_criteria")):
        monkeypatch.setattr(obj, name, value)
    r = _run(_cond("R81RR"), design, task, tmp_path / "rr")                      # run_report raised; both arms FAIL
    assert r["qs_vs_dyn_pair_status"] == CE and r["qs_vs_dyn_pair_status_before_error"] == "FAIL"
    assert r["qs_vs_dyn_fail_arms"] == "B0,B3" and "owner ruling I-6" in r["qs_vs_dyn_pair_reason"]
    assert [e["stage"] for e in r["_errors"]] == ["run_report"] and r["qs_vs_dyn_applicability"] == checks.QS_APPLICABLE
    rows = [dict(motor="M0", set="NOM", limits="L-R1", condition_id="a", qs_vs_dyn_pair_status="PASS"),
            dict(motor="M0", set="NOM", limits="L-EVE", condition_id="b", qs_vs_dyn_pair_status="PASS"),
            dict(motor="M0", set="SEN", limits="L-EVE", condition_id="c", qs_vs_dyn_pair_status=CE,
                 qs_vs_dyn_pair_status_before_error="FAIL", qs_vs_dyn_applicability=checks.QS_APPLICABLE)]
    out = checks.branch_qs_dynamic_outcome("M0", rows, ["a", "b", "c"])
    assert out["outcome"] == "INCONCLUSIVE" and out["n_FAIL"] == 0 and out["n_FAIL_before_exception"] == 1
    assert out["fail_before_exception_by_set"] == "SEN:1" and "before an exception" in out["reason"]
    acct = {(a["motor"], a["set"]): a for a in checks.qs_dynamic_accounting(rows)}[("M0", "ALL")]
    assert acct["fail_before_exception"] == 1 and acct["qs_check_fail"] == 0
    block = campaign.IMPLEMENTED_2["AMB_29_condition_error"]                     # R8-6: no FAIL exception stated
    assert "stays FAIL" not in block and "REPORTED_ONLY or FAIL" in block and "AMB-29(b)" in block


# ============================================================ R8-2 (MAJOR): applicability and status both add up
def test_r8_2_the_accounting_adds_up_two_ways_after_an_override_in_the_executor(tmp_path, monkeypatch):
    c, out, rows, read = _schedule(tmp_path, monkeypatch, "R82", patches=[_screen_fails("B3"), _arm_raises("B0")])
    cond = read("conditions.csv")[0]
    assert cond["qs_vs_dyn_pair_status"] == CE and cond["qs_vs_dyn_applicability"] == NA
    assert cond["qs_vs_dyn_pair_status_before_error"] == NA and cond["qs_eligible_pair"] == "False"
    for a in read("qs_dynamic_accounting.csv"):
        planned = int(a["planned_pairs"])
        assert planned == 1 and sum(int(a[k]) for k in ELIG) == planned, a              # applicability
        assert sum(int(a[k]) for k in STATUS) == planned, a                             # evaluation status
        assert a["qs_ineligible_pairs"] == "1" and a["qs_check_not_applicable_qs_infeasible"] == "0"
        assert a["not_evaluable_condition_error"] == "1" and a["qs_ineligible_b3_only"] == "1"
    assert "qs_dynamic_accounting_classes" in campaign.IMPLEMENTED_2


def test_r8_2_applicability_of_rows_without_the_field_and_unknown_values():
    assert checks.pair_applicability(dict(qs_vs_dyn_pair_status=NA)) == NA
    assert checks.pair_applicability(dict(qs_vs_dyn_pair_status=NA_PROFILE, qs_eligible_pair=False)) == NA_PROFILE
    assert checks.pair_applicability(dict(qs_vs_dyn_pair_status="PASS", qs_eligible_pair=True)) == checks.QS_APPLICABLE
    assert checks.pair_applicability(dict(qs_vs_dyn_pair_status=CE, qs_eligible_pair=False)) == "UNKNOWN"
    with pytest.raises(ValueError):
        checks.pair_applicability(dict(qs_vs_dyn_applicability="SOMETIMES"))
    t = checks.qs_dynamic_accounting([dict(motor="M0", set="P3", qs_vs_dyn_pair_status=CE, qs_eligible_pair=False,
                                           qs_vs_dyn_applicability=NA_PROFILE)])[0]
    assert t["not_applicable_profile_unavailable"] == 1 and t["qs_check_not_applicable_profile_unavailable"] == 0
    assert sum(t[k] for k in ELIG) == sum(t[k] for k in STATUS) == t["planned_pairs"] == 1


# ============================================================ R8-3 (MAJOR): candidate section 1.6
def test_r8_3_candidate_section_1_6_states_the_exception_precedence():
    text = campaign.DRAFT_AMENDMENT_2.read_text(encoding="utf-8")
    sec = text[text.index("### 1.6 "):text.index("### 1.7 ")]
    assert "or `NOT_APPLICABLE_PROFILE_UNAVAILABLE` if a profile is missing" not in text
    assert "also when a profile is missing" in sec and "qs_vs_dyn_applicability" in sec


# ============================================================ R8-4: I-6 at every stage with a NOT_APPLICABLE pair; I-4
@pytest.mark.parametrize("stage", ["classify", "run_report", "condition_report"])
def test_r8_4_an_exception_at_each_stage_makes_a_not_applicable_pair_not_evaluable(tmp_path, monkeypatch, stage):
    task = _task()
    design = _design(task)
    inject = {"classify": (checks, "classify_pair", _boom),
              "run_report": _first_call_raises(checks, "failed_criteria"),
              "condition_report": (campaign, "baseline_sanity", _boom)}[stage]
    for obj, name, value in (_screen_fails("B3"), inject):
        monkeypatch.setattr(obj, name, value)
    r = _run(_cond("R84" + stage.upper().replace("_", "")[:6]), design, task, tmp_path / stage)
    assert stage in [e["stage"] for e in r["_errors"]]
    assert r["qs_vs_dyn_pair_status"] == CE and r["qs_vs_dyn_pair_status_before_error"] == NA      # not NOT_APPLICABLE
    assert r["qs_vs_dyn_applicability"] == NA and r["qs_eligible_pair"] is False                  # kept apart
    assert all(s["executed"] is True for s in r["_sims"])                                          # no retry, kept


def test_r8_4_the_in_process_recomputation_gates_the_qs_check(tmp_path, monkeypatch):
    task = _task()
    design = _design(task)
    real, n = evaluator.compare_with_simulator, {"calls": 0}

    def cmp(*a, **k):                     # the second arm (B3) is not confirmed by the in-process recomputation
        n["calls"] += 1
        r = real(*a, **k)
        return dict(r, protocol_ok=False) if n["calls"] == 2 else r
    monkeypatch.setattr(campaign.evaluator, "compare_with_simulator", cmp)
    r = _run(_cond("R84I4"), design, task, tmp_path / "i4")
    assert r["_rows"]["B3"]["recompute_protocol_ok"] is False and r["_rows"]["B0"]["recompute_protocol_ok"] is True
    assert r["qs_vs_dyn_pair_status"] == checks.QS_RUN_INVALID and r["qs_vs_dyn_invalid_arms"] == "B3"
    assert r["qs_vs_dyn_applicability"] == checks.QS_APPLICABLE and r["_errors"] == []


# ============================================================ R8-5: every failed write is listed
def test_r8_5_every_failed_output_write_is_recorded_and_listed(tmp_path, monkeypatch):
    # rev13 (review R9-7): the failure is injected at Path.write_text, which every version of the executor uses, so the
    # test also fails on rev11 by its behaviour (an unguarded write), not only by a missing name
    real = Path.write_text

    def text(self, *a, **k):
        if self.parent.name == "conditions" or self.name in ("conditions.csv", "recomputation_independent_process.log"):
            raise OSError(f"injected write failure of {self.name}")
        return real(self, *a, **k)
    c, out, rows, read = _schedule(tmp_path, monkeypatch, "R85", patches=[(Path, "write_text", text)])
    want = {f"write conditions/{c.cid}.json", "write conditions.csv", "write recomputation_independent_process.log"}
    man = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert want <= set(man["output_write_failures"])
    assert want <= {e["stage"] for e in read("errors.csv")}
    for f in ("runs.csv", "evaluation.csv", "energy_roles.csv", "qs_dynamic_accounting.csv", "zz_post_run_sha256.csv"):
        assert (out / f).is_file(), f
    assert not (out / "conditions.csv").exists() and not (out / "conditions" / f"{c.cid}.json").exists()


# ============================================================ R8-9, R8-10
def test_r8_9_a_not_applicable_pair_is_not_evaluable_after_the_separate_recomputation_fails(tmp_path, monkeypatch):
    c = type("C", (), {"run_ids": {"B0": "r0", "B3": "r3"}})()
    ok = [dict(run_id="r0", recomputed="True", protocol_ok="True"), dict(run_id="r3", recomputed="True", protocol_ok="True")]

    def row():
        return dict(status=checks.COMPARABLE, qs_vs_dyn_pair_status=NA, qs_vs_dyn_fail_arms="", qs_vs_dyn_pair_reason="x")
    # rev13 (review R9-7): the calls every version accepts come first, so the test fails on rev11 by its behaviour
    r = row()
    campaign.fold_failed([r], "injected")
    assert r["qs_vs_dyn_pair_status"] == CE and r["qs_vs_dyn_pair_status_before_error"] == NA
    r = row()
    campaign.fold_separate_recomputation([r], [c], [], 4)
    assert r["qs_vs_dyn_pair_status"] == CE and r["qs_vs_dyn_pair_status_before_error"] == NA
    r = row()
    campaign.fold_separate_recomputation([r], [c], ok, 0)                               # control: no failure
    assert r["qs_vs_dyn_pair_status"] == NA
    for exit_, err in ((4, ""), (3, ""), (-1, "launch"), (0, "unreadable output")):
        r = row()
        campaign.fold_separate_recomputation([r], [c], ok if exit_ in (0, 1) else [], exit_, err)
        assert r["qs_vs_dyn_pair_status"] == CE and r["qs_vs_dyn_pair_status_before_error"] == NA, (exit_, err)
    real = subprocess.run

    def fake(args, **k):                                                                # executor: exit 4
        res = real(args, **k)
        return subprocess.CompletedProcess(args, 4, res.stdout, "RuntimeError: injected crash")
    c, out, rows, read = _schedule(tmp_path, monkeypatch, "R89", patches=[_screen_fails("B3")], fake=fake)
    cond = read("conditions.csv")[0]
    assert cond["qs_vs_dyn_pair_status"] == CE and cond["qs_vs_dyn_applicability"] == NA
    a = {(x["motor"], x["set"]): x for x in read("qs_dynamic_accounting.csv")}[("M0", "ALL")]
    assert sum(int(a[k]) for k in ELIG) == sum(int(a[k]) for k in STATUS) == 1


def test_r8_10_a_failed_screen_makes_the_check_not_applicable_even_if_the_other_screen_raised(tmp_path, monkeypatch):
    task = _task()
    design = _design(task)
    real = checks.qs_screen

    def screen(plant, t, v):
        if _is_b0(t):
            raise RuntimeError("injected screen failure of B0")
        return real(plant, t, v)
    for obj, name, value in (_screen_fails("B3"), (checks, "qs_screen", screen)):
        monkeypatch.setattr(obj, name, value)
    r = _run(_cond("R810"), design, task, tmp_path)
    assert r["qs_screen_errors"] == "B0" and r["b3_qs_feasible_on_eval_plant"] is False
    assert r["qs_vs_dyn_applicability"] == NA and r["qs_eligible_pair"] is False and r["qs_ineligible_arms"] == "B3"
    assert r["qs_vs_dyn_pair_status"] == CE and r["qs_vs_dyn_pair_status_before_error"] == NA


# ============================================================ status v10, candidate rev9, fail-closed
def test_review_status_v10_counts_the_r8_major_findings_until_verified_and_blocks(monkeypatch):
    # rev13: v10 is read by path (the live file is v11, checked in test_review_fixes_v13.py)
    v10 = frozen.PILOT / "config" / "code_review_status_v10.json"
    rv = json.loads(v10.read_text(encoding="utf-8"))
    monkeypatch.setattr(campaign, "REVIEW_STATUS", v10)
    assert rv["open_critical"] == 0 and rv["open_major"] == 5
    assert set(rv["major_findings"]) == {"R5-1", "R5-2", "R8-1", "R8-2", "R8-3"}
    assert rv["open_owner_decisions"] == [] and rv["reviews_pending"] and "attempt 9" in rv["reviews_pending"][0]
    assert "R7-10 closed" in rv["minor_findings"]["R7-8..R7-13 (NOTE)"]                     # R8-8
    assert "AMB-29(b)" in rv["implementer_readings_for_owner_confirmation"][0]
    b = " | ".join(campaign.preconditions("readiness"))
    assert "5 major findings not resolved" in b and "closure not yet accepted by the owner" in b
    assert "owner decision open" not in b


def test_rev9_candidate_fixes_the_r8_text_and_is_pinned():
    rev8 = campaign.PILOT_DIR / "03_protocol_v1_amendment_2_rev8_CANDIDATE.md"
    assert frozen.sha256(rev8) == "f6430bf5512cb56065a2465bcfda1c4c42e244b80f73fcd3e88d985ac8811f7c"
    # rev13: rev9 is kept unchanged (pinned) and superseded by rev10 (its match with the code: test_review_fixes_v13.py)
    rev9 = campaign.PILOT_DIR / "03_protocol_v1_amendment_2_rev9_CANDIDATE.md"
    assert frozen.sha256(rev9) == "cdeea032c520f408f1f300a53cf1bc8b1ec4582d80340d3df2c2c94fa5d45719"
    r = campaign.read_amendment(rev9)
    assert r["exists"] and r["status"] == "DRAFT"
    text = rev9.read_text(encoding="utf-8")
    assert "DRAFT — NOT APPROVED FOR RELEASE" in text.splitlines()[2]
    for h in (frozen.FROZEN_SHA256[frozen.PROTOCOL], campaign.AMENDMENT_1_SHA256,
              "f6430bf5512cb56065a2465bcfda1c4c42e244b80f73fcd3e88d985ac8811f7c",
              "0e3ef3112c979237e7079f176b21dd4f2ce682c7ab435f36f33321ffe67a5996"):
        assert h in text
    for n, i in zip(range(9, 15), range(1, 7)):
        assert re.search(rf"^### 1\.{n} I-{i}\b", text, re.M), i
    assert "unless a valid arm FAILed" not in text and "stays FAIL" not in text                 # R8-1
    assert "R7-10 not changed" not in text and "20_attempt8_final_owner_decisions_report.md" in text   # R8-8, R8-7
    assert r["decisions"]["owner_decisions_open"] == [] and "|\n\n|" not in text


def test_campaign_mode_stays_blocked_in_rev12():
    b = " | ".join(campaign.preconditions("campaign"))
    n = json.loads(campaign.REVIEW_STATUS.read_text(encoding="utf-8"))["open_major"]        # rev13: the live count
    assert n >= 5
    for x in ("no issued amendment 2", "no campaign authorisation record", "protocol 10.1 gate record",
              f"{n} major findings not resolved"):
        assert x in b, x
    assert not campaign.CAMPAIGN_AUTHORIZATION.exists() and not campaign.ISSUED_AMENDMENT_2.exists()
