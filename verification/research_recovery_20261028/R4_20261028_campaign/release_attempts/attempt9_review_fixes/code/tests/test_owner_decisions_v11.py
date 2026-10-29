"""Owner rulings I-2 to I-6 (2026-10-28) and the fixes of the attempt-7 review findings R7-1 to R7-7, rev11 (amendment 2
candidate rev8). Protocol semantics only. No test computes, reports or targets an energy difference between arms;
synthetic numbers in pure-rule tests are not run energies."""

import ast
import csv
import inspect
import json
import re
import subprocess
from pathlib import Path

import numpy as np
import pytest

from r4h3 import campaign, checks, config, evaluator, frozen
from r4h3 import task as taskmod
from r4h3.closedloop import fixed_gain

NA, NA_PROFILE = checks.QS_NA_INFEASIBLE, checks.QS_NA_PROFILE


def _task(name="GENTLE"):
    v = np.array([0, 0, 0.5, 1, 1.5, 2, 2, 2, 2, 2, 1.5, 1, 1, 1, 1, 1, 1.5, 2, 2, 2, 2, 2, 1.5, 1, 0.5, 0, 0, 0], float)
    return taskmod.task_from_samples(name, np.arange(len(v), dtype=float), v)


def _cond(tag, set_="DEV"):
    cid = f"DEV-V11-{tag}-GENTLE-M0-LR1-P1-dt1ms"
    return campaign.Condition(cid, set_, "GENTLE", "M0", "L-R1", "P1", 1e-3, None,
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


def _screen_fails(monkeypatch, arm):
    """The QS screen of one arm reports infeasible (B0 = the 1 s grid profile, B3 = the S-eco knots)."""
    real = campaign.checks.qs_energy

    def screen(plant, t, v):
        r = real(plant, t, v)
        is_b0 = len(t) > 2 and np.allclose(np.diff(t), 1.0)
        if (arm == "B0") == is_b0:
            return dict(r, feasible=False, n_infeasible_pieces=1,
                        infeasible_pieces=[dict(piece=3, t0_s=3.0, t1_s=4.0, v0_ms=1.0, v1_ms=1.5)])
        return r
    monkeypatch.setattr(campaign.checks, "qs_energy", screen)


def _arm_raises(monkeypatch, branch):
    real = campaign.run_arm

    def arm(rid, b, *a, **k):
        if b == branch:
            raise RuntimeError(f"injected evaluation failure of {b}")
        return real(rid, b, *a, **k)
    monkeypatch.setattr(campaign, "run_arm", arm)


# ============================================================ I-6: an exception wins over NOT_APPLICABLE
def test_i6_an_exception_makes_a_not_applicable_pair_not_evaluable(tmp_path, monkeypatch):
    task = _task()
    design = _design(task)
    _screen_fails(monkeypatch, "B3")
    r = _run(_cond("I6CTRL"), design, task, tmp_path / "ctrl")                            # control: no exception
    assert r["qs_vs_dyn_pair_status"] == NA and r["qs_vs_dyn_applicability"] == NA and r["status"] == checks.COMPARABLE
    _arm_raises(monkeypatch, "B0")
    c = _cond("I6NA")
    r = _run(c, design, task, tmp_path / "na")
    assert r["qs_vs_dyn_pair_status"] == checks.QS_CONDITION_ERROR                       # not NOT_APPLICABLE
    assert r["qs_vs_dyn_pair_status_before_error"] == NA and "owner ruling I-6" in r["qs_vs_dyn_pair_reason"]
    assert r["qs_vs_dyn_applicability"] == NA and r["qs_eligible_pair"] is False         # applicability kept apart
    assert r["status"] == "ERROR"                                                        # dynamic status apart
    e = [x for x in r["_errors"] if x["stage"] == "run"]
    assert len(e) == 1 and e[0]["run_id"] == c.run_ids["B0"] and "injected" in e[0]["traceback"]   # exception kept
    assert next(s for s in r["_sims"] if s["branch"] == "B3")["executed"] is True         # no retry, no replacement


def test_i6_an_exception_makes_a_profile_unavailable_pair_not_evaluable(tmp_path, monkeypatch):
    task = _task()
    design = _design(task, failed_b3=True)
    r = _run(_cond("I6PFC"), design, task, tmp_path / "ctrl")
    assert r["qs_vs_dyn_pair_status"] == NA_PROFILE                                      # control (I-2)
    _arm_raises(monkeypatch, "B0")
    r = _run(_cond("I6PF"), design, task, tmp_path / "pf")
    assert r["qs_vs_dyn_pair_status"] == checks.QS_CONDITION_ERROR and r["qs_vs_dyn_applicability"] == NA_PROFILE
    assert r["status"] == "PROFILE_UNAVAILABLE"                                          # explicit outcome kept
    monkeypatch.undo()
    monkeypatch.setattr(campaign.checks, "qs_screen", _boom)                             # an evaluation exception
    r = _run(_cond("I6SC"), design, task, tmp_path / "sc")
    assert r["qs_vs_dyn_pair_status"] == checks.QS_CONDITION_ERROR and r["qs_vs_dyn_applicability"] == NA_PROFILE


def test_i6_an_eligible_pair_keeps_its_labels(tmp_path, monkeypatch):
    task = _task()
    design = _design(task)
    _arm_raises(monkeypatch, "B3")
    r = _run(_cond("I6EL"), design, task, tmp_path / "el")
    assert r["qs_vs_dyn_pair_status"] == checks.QS_NOT_EVALUABLE and r["qs_vs_dyn_applicability"] == "APPLICABLE"
    fail = dict(motor="M0", E_qs_J=1.0, E_dyn_Wh=1.0, d_ref_m=1.0, e_qs_Wh_per_km=1.0, e_dyn_Wh_per_km=1.02,
                diff_pct=2.0, decisive=True, status="FAIL (branch INCONCLUSIVE, protocol 9)", non_positive_term="")
    monkeypatch.setattr(campaign.checks, "qs_vs_dynamic", lambda *a, **k: dict(fail))     # B0's measured FAIL
    r = _run(_cond("I6FL"), design, task, tmp_path / "fl")
    # rev12 (review R8-1, owner ruling I-6): the exception makes the pair NOT_EVALUABLE, a FAIL included (AMB-29(b)
    # label for an eligible pair whose run raised); the measured failure stays recorded, never hidden
    assert r["qs_vs_dyn_pair_status"] == checks.QS_NOT_EVALUABLE and r["qs_vs_dyn_fail_arms"] == "B0"
    assert r["qs_vs_dyn_pair_status_before_error"] == "FAIL"


# ============================================================ I-2, I-3, I-4, I-5
def test_i2_a_missing_profile_outside_nom_is_counted_never_a_pass_and_never_a_paired_comparison():
    nom = [dict(motor="M0", set="NOM", limits=lim, condition_id=f"n{lim}", qs_vs_dyn_pair_status="PASS",
                status=checks.COMPARABLE) for lim in ("L-R1", "L-EVE")]
    pf = dict(motor="M0", set="SEN", limits="L-EVE", condition_id="pf", qs_vs_dyn_pair_status=NA_PROFILE,
              status="PROFILE_UNAVAILABLE")
    out = checks.branch_qs_dynamic_outcome("M0", nom + [pf], ["nL-R1", "nL-EVE", "pf"])
    assert out["outcome"] == "PASS" and out["n_PASS"] == 2 and out[f"n_{NA_PROFILE}"] == 1   # not automatically INCONCLUSIVE
    feas = {(a["motor"], a["set"]): a for a in checks.feasibility_accounting(
        nom + [pf], [dict(condition_id="pf", executed=False, arm_8_2_valid=False, condition_status="PROFILE_UNAVAILABLE",
                          energy_role="NO_ENERGY_NOT_EXECUTED")])}
    assert feas[("ALL", "ALL")]["profile_failure_conditions"] == 1 and feas[("ALL", "ALL")]["planned_conditions"] == 3
    assert checks.classify_pair(None, None, eco_profile_ok=False, baseline_ok=True, pstate="P1") == "PROFILE_UNAVAILABLE"
    with pytest.raises(ValueError):
        checks.paired_delta("PROFILE_UNAVAILABLE", {}, {})
    assert "Owner ruling I-2" in campaign.IMPLEMENTED_2["AMB_30_branch_scope"]


def test_i3_every_energy_saving_percentage_rejects_a_non_positive_denominator():
    for bad in (0.0, -1.0, float("nan")):
        q = checks.qs_vs_dynamic("M0", bad, 0.05, 213.0)
        assert q["diff_pct"] is None and q["E_qs_J"] is bad and q["non_positive_term"]
        d = checks.paired_delta(checks.COMPARABLE, dict(Wh_per_ref_km=bad, trip_time_s=1.0),
                                dict(Wh_per_ref_km=1.0, trip_time_s=1.0))
        assert d["dE_rel_pct"] is None and d["dE_rel_status"] == "NOT_EVALUABLE_DENOMINATOR_NOT_POSITIVE"
        assert np.isnan(bad) or d["dE_abs_Wh_per_km"] == 1.0 - bad                    # an independent metric is kept
        s = checks.scenario_totals(bad, 1.0, 1.0)
        assert s["S_found_pct"] is None and s["S_max_pct"] is None and s["non_positive_term"]
        g = checks.grid_convergence(bad, 1.0, 1.0)
        assert g["dS_found_pp"] is None and g["passed"] is None
    assert checks.timestep_check(None, 0.1)["passed"] is None
    # every function of checks.py that forms a percentage (100.0 * ...) guards its denominator
    tree = ast.parse(inspect.getsource(checks))
    pct = {f.name for f in ast.walk(tree) if isinstance(f, ast.FunctionDef) and "100.0 *" in ast.get_source_segment(
        inspect.getsource(checks), f)}
    assert pct == {"qs_vs_dynamic", "scenario_totals", "grid_convergence", "paired_delta"}, pct
    for name in pct:
        assert "non_positive_term(" in inspect.getsource(getattr(checks, name)), name
    assert "owner ruling I-3" in campaign.IMPLEMENTED_2["non_positive_denominator_rule"]


def test_i4_both_recomputations_must_confirm_a_run_used_by_the_qs_check():
    c = type("C", (), {"run_ids": {"B0": "r0", "B3": "r3"}})()
    ok = [dict(run_id="r0", recomputed="True", protocol_ok="True"), dict(run_id="r3", recomputed="True", protocol_ok="True")]
    for sep in ([ok[0], dict(ok[1], recomputed="False")], [ok[0], dict(ok[1], protocol_ok="False")], [ok[0]]):
        row = dict(status=checks.COMPARABLE, qs_vs_dyn_pair_status="PASS", qs_vs_dyn_fail_arms="", qs_vs_dyn_pair_reason="x")
        campaign.fold_separate_recomputation([row], [c], sep, 0)
        assert row["qs_vs_dyn_pair_status"] == checks.QS_RUN_INVALID and row["status"] != checks.COMPARABLE
    src = inspect.getsource(campaign.run_condition)                                      # the in-process one
    assert 'checks.arm_comparable(ev) and bool(ev.get("recompute_protocol_ok"))' in src
    assert "Owner ruling I-4" in campaign.IMPLEMENTED_2["AMB_31_energy_of_invalid_runs"]


def test_i5_the_qs_energy_label_is_unchanged_everywhere():
    label = "NOT_EVALUABLE_QS_UNDEFINED"
    assert checks.QS_UNDEFINED == label and label in checks.PAIR_QS_STATUSES
    assert label in checks.PAIR_STATUS_CLASSES["NOT_EVALUABLE"]
    assert label in campaign.IMPLEMENTED_2["pair_statuses"] and label in campaign.IMPLEMENTED_2["AMB_29_qs_energy_undefined"]
    assert "Owner ruling I-5" in campaign.IMPLEMENTED_2["AMB_29_qs_energy_undefined"]
    assert "QS_COMPARISON_NOT_EVALUABLE" not in checks.PAIR_QS_STATUSES                   # not renamed
    text = campaign.DRAFT_AMENDMENT_2.read_text(encoding="utf-8")
    assert text.count(label) >= 3
    out = checks.branch_qs_dynamic_outcome("M0", [dict(motor="M0", set="NOM", limits="L-R1", qs_vs_dyn_pair_status=label)])
    assert out[f"n_{label}"] == 1
    acct = checks.qs_dynamic_accounting([dict(motor="M0", set="NOM", qs_vs_dyn_pair_status=label, qs_eligible_pair=True)])
    assert acct[0]["not_evaluable_qs_undefined"] == 1


# ============================================================ R7-3, R7-4, R7-5 (executor level)
def _schedule(tmp_path, monkeypatch, tag, fake=None, patches=()):
    task = _task()
    if fake is not None:
        monkeypatch.setattr(campaign.subprocess, "run", fake)
    for obj, name, value in patches:
        monkeypatch.setattr(obj, name, value)
    c = _cond(tag)
    out = tmp_path / tag
    rows = campaign.execute_schedule([c], lambda n: task, out)
    monkeypatch.undo()
    err = list(csv.DictReader((out / "errors.csv").open(encoding="utf-8")))
    return c, out, rows, err


def test_r7_3_every_error_row_has_a_stage(tmp_path, monkeypatch):
    c, out, rows, err = _schedule(tmp_path, monkeypatch, "R73", patches=[
        (campaign.checks, "qs_dynamic_accounting", _boom), (campaign.checks, "denominator", _boom),
        (campaign.checks, "feasibility_accounting", _boom), (campaign.checks, "h3_verdict_eligibility", _boom),
        (campaign, "fold_separate_recomputation", _boom)])
    ids = {e["condition_id"] for e in err}
    assert {"QS-DYN-ACCOUNTING", "STATUS-DENOMINATOR", "FEASIBILITY-ACCOUNTING", "H3-VERDICT-ELIGIBILITY",
            "RECOMPUTATION-FOLD"} <= ids
    assert err and all(e["stage"] for e in err), [e for e in err if not e["stage"]]
    assert next(e for e in err if e["condition_id"] == "RECOMPUTATION-FOLD")["diagnostic_path"]


@pytest.mark.parametrize("case", ["exit4_complete_output", "not_recomputed_row", "unreadable_output"])
def test_r7_4_every_unconfirmed_executed_run_has_a_ledger_row(tmp_path, monkeypatch, case):
    real = subprocess.run

    def fake(args, **k):
        res = real(args, **k)
        p = Path(args[-1]) / "recomputation_independent.csv"
        if case == "exit4_complete_output":
            return subprocess.CompletedProcess(args, 4, res.stdout, "Traceback (most recent call last):\nRuntimeError: "
                                                                     "injected crash after the output was written")
        if case == "not_recomputed_row":                                                 # B3 present, not recomputed
            rows_ = list(csv.DictReader(p.open(encoding="utf-8")))
            fields = list(rows_[0]) + ([] if "reason" in rows_[0] else ["reason"])
            for d in rows_:
                if "-B3-" in d["run_id"]:
                    d.update(recomputed="False", reason="injected not recomputed")
            with open(p, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
                w.writeheader()
                w.writerows(rows_)
            return res
        p.write_bytes(b"\xff\xfe\x00 not utf-8 \x81")                                     # unreadable output
        return res
    c, out, rows, err = _schedule(tmp_path, monkeypatch, "R74" + case.split("_")[0].upper(), fake=fake)
    per_run = {e["run_id"]: e for e in err if e["run_id"] and e["stage"].startswith("separate recomputation")}
    head = [e for e in err if e["condition_id"] == "SEPARATE-RECOMPUTATION"]
    if case == "not_recomputed_row":
        assert set(per_run) == {c.run_ids["B3"]} and "injected not recomputed" in per_run[c.run_ids["B3"]]["stage"]
        assert head == []                                                                # not a process failure
    else:
        assert set(per_run) == set(c.run_ids.values())                                   # every executed run
        assert len(head) == 1 and head[0]["stage"] == ("exit 4" if case.startswith("exit4") else "unreadable output")
    assert rows[0]["status"] != checks.COMPARABLE                                        # fail-closed
    assert all(e["diagnostic_path"] == "recomputation_independent_process.log" for e in per_run.values())


def test_r7_5_a_failed_output_write_is_recorded_and_the_other_outputs_are_written(tmp_path, monkeypatch):
    real = campaign._write_csv

    def write(path, rows):
        if Path(path).name in ("runs.csv", "stop_compliance.csv"):
            raise OSError(f"injected write failure of {Path(path).name}")
        return real(path, rows)
    c, out, rows, err = _schedule(tmp_path, monkeypatch, "R75", patches=[(campaign, "_write_csv", write)])
    stages = {e["stage"] for e in err if e["condition_id"] == "OUTPUT-WRITE"}
    assert {"write runs.csv", "write stop_compliance.csv"} <= stages
    man = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert {"write runs.csv", "write stop_compliance.csv"} <= set(man["output_write_failures"])
    for f in ("conditions.csv", "energy_roles.csv", "feasibility_accounting.csv", "qs_dynamic_branch_outcomes.csv",
              "zz_post_run_sha256.csv"):
        assert (out / f).is_file(), f
    assert not (out / "runs.csv").exists() and rows[0]["status"] != checks.COMPARABLE   # fail-closed downstream


# ============================================================ R7-7, R7-2: the live status file and the candidate
def test_r7_7_the_live_review_status_blocks_and_r7_2_rulings_are_separate_from_release_steps(monkeypatch):
    # rev12: v9 is read by path (the live file is v10, checked in test_review_fixes_v12.py)
    v9 = frozen.PILOT / "config" / "code_review_status_v9.json"
    rv = json.loads(v9.read_text(encoding="utf-8"))
    assert rv["open_major"] == 2 and rv["reviews_pending"] and rv["open_owner_decisions"] == []
    assert {f"I-{i}" for i in range(1, 7)} <= set(rv["owner_rulings_implemented"]) and rv["pending_release_steps"]
    assert "Every owner decision for amendment 2 has been made" not in json.dumps(rv)       # R7-2
    monkeypatch.setattr(campaign, "REVIEW_STATUS", v9)
    b = " | ".join(campaign.preconditions("readiness"))
    assert "2 major findings not resolved" in b and "closure not yet accepted by the owner" in b
    assert "owner decision open" not in b and campaign.OWNER_DECISIONS_OPEN == []
    for i in range(1, 7):                                                                 # each label is a ruling
        assert re.search(rf"[Oo]wner ruling I-{i}\b", json.dumps(campaign.IMPLEMENTED_2)), i


def test_rev8_candidate_states_every_ruling_and_matches_the_code():
    assert frozen.sha256(campaign.PILOT_DIR / "03_protocol_v1_amendment_2_rev7_CANDIDATE.md") == \
        "0e3ef3112c979237e7079f176b21dd4f2ce682c7ab435f36f33321ffe67a5996"
    # rev12: rev8 is kept unchanged (pinned) and superseded by rev9 (its match with the code: test_review_fixes_v12.py)
    rev8 = campaign.PILOT_DIR / "03_protocol_v1_amendment_2_rev8_CANDIDATE.md"
    assert frozen.sha256(rev8) == "f6430bf5512cb56065a2465bcfda1c4c42e244b80f73fcd3e88d985ac8811f7c"
    r = campaign.read_amendment(rev8)
    assert r["exists"] and r["status"] == "DRAFT"
    text = rev8.read_text(encoding="utf-8")
    assert "DRAFT — NOT APPROVED FOR RELEASE" in text.splitlines()[2]
    for h in (frozen.FROZEN_SHA256[frozen.PROTOCOL], campaign.AMENDMENT_1_SHA256,
              "0e3ef3112c979237e7079f176b21dd4f2ce682c7ab435f36f33321ffe67a5996"):
        assert h in text
    for n, i in zip(range(9, 15), range(1, 7)):
        assert re.search(rf"^### 1\.{n} I-{i}\b", text, re.M), i
    assert r["decisions"]["owner_decisions_open"] == [] and "|\n\n|" not in text
    assert "Provisional reading I-" not in text and "Provisional reading I-" not in json.dumps(campaign.IMPLEMENTED_2)


def test_campaign_mode_stays_blocked_without_issue_and_authorisation():
    b = " | ".join(campaign.preconditions("campaign"))
    for x in ("no issued amendment 2", "no campaign authorisation record", "protocol 10.1 gate record"):
        assert x in b, x
    assert not campaign.CAMPAIGN_AUTHORIZATION.exists() and not campaign.ISSUED_AMENDMENT_2.exists()
