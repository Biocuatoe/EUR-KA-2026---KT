"""Owner rulings of 2026-10-28 on AMB-29(a) (missing profile) and AMB-31 (energy of a run failing protocol 8.2),
amendment 2 candidate rev4. These tests check protocol semantics only; none computes or targets an energy difference
between arms."""

import csv
import json
import re
from types import SimpleNamespace

import numpy as np
import pytest

from r4h3 import campaign, checks, config, evaluator, frozen
from r4h3 import task as taskmod
from r4h3.closedloop import fixed_gain

P = {"status": "pass", "diff_pct": 0.3}
F = {"status": "FAIL (branch INCONCLUSIVE, protocol 9)", "diff_pct": 1.7}
VALID = dict(sim_valid=True, complete=True, tracking_ok=True, stop_ok=True, constraint_ok=True, finite_ok=True,
             recompute_protocol_ok=True)


def _gentle(name="GENTLE"):
    v = np.array([0, 0, 0.5, 1, 1.5, 2, 2, 2, 2, 2, 1.5, 1, 1, 1, 1, 1, 1.5, 2, 2, 2, 2, 2, 1.5, 1, 0.5, 0, 0, 0], float)
    return taskmod.task_from_samples(name, np.arange(len(v), dtype=float), v)


def _cond(tag, pstate="P1", cycle="GENTLE", set_="DEV"):
    cid = f"DEV-V7-{tag}-{cycle}-M0-LR1-{pstate}-dt1ms"
    return campaign.Condition(cid, set_, cycle, "M0", "L-R1", pstate, 1e-3, None,
                              {b: cid.replace("-dt", f"-{b}-dt") for b in ("B0", "B3")})


def _failed_design(real):
    """The planner's own failure format (planner.plan_seco: status 'unavailable', no knots): an explicit failure."""
    return dict(real, eco={"status": "unavailable", "rows": real["eco"]["rows"], "t": None, "v": None},
                val_e=None, eco_ok=False)


def _run(cond, design, task, tmp_path, p=None):
    mm = config.motor_model("M0")
    return campaign.run_condition(cond, task, design, p or config.params_for("P1"), 1.0, config.LIMITS["L-R1"], mm,
                                  evaluator.motor_spec_from_protocol("M0", frozen.M1_CURVE),
                                  fixed_gain(config.params_for("P1")), tmp_path)


# ============================================================ AMB-29(a): missing profile
def test_amb29a_planner_failure_stays_an_explicit_outcome(tmp_path):
    task = _gentle()
    design = _failed_design(campaign.plan_design(task, "L-R1", config.params_for("P1"), config.motor_model("M0")))
    r = _run(_cond("PF"), design, task, tmp_path)
    assert r["status"] == "PROFILE_UNAVAILABLE" and r["eco_status"] == "unavailable"      # explicit, not N/A
    sims = {s["branch"]: s for s in r["_sims"]}
    assert sims["B3"]["executed"] is False and "unavailable" in sims["B3"]["reason"]       # recorded, not dropped
    assert sims["B0"]["executed"] is True                                                  # existing arm still run
    assert r["qs_vs_dyn_pair_status"] == checks.QS_NA_PROFILE and r["qs_eligible_pair"] is False
    with pytest.raises(ValueError):
        checks.paired_delta(r["status"], {}, {})                                           # never a paired comparison
    assert checks.denominator([r["status"]])["PROFILE_UNAVAILABLE"] == 1                   # counted in D5


def test_amb29a_missing_profile_check_is_not_applicable_and_never_a_pass():
    r = checks.pair_qs_dynamic("M0", {"B0": True, "B3": None}, {"B0": P, "B3": P})
    assert r["pair_status"] == checks.QS_NA_PROFILE and r["pair_status"] != "PASS"
    assert "explicit profile-failure status" in r["reason"]
    only = [dict(motor="M0", set=s, limits=lim, qs_vs_dyn_pair_status=checks.QS_NA_PROFILE)    # rev9 (review R5-10)
            for s in ("NOM", "P3", "INS") for lim in ("L-R1", "L-EVE")]
    out = checks.branch_qs_dynamic_outcome("M0", only)
    assert out["outcome"] == "INCONCLUSIVE" and "vacuity" in out["reason"]                # no pass by vacuity
    assert checks.classify_pair(None, None, eco_profile_ok=False, baseline_ok=True, pstate="P1") == "PROFILE_UNAVAILABLE"
    assert checks.classify_pair(None, None, eco_profile_ok=True, baseline_ok=False, pstate="P1") == "BASELINE_UNAVAILABLE"


def test_amb29a_a_valid_but_qs_ineligible_profile_is_distinct_from_a_missing_one():
    r = checks.pair_qs_dynamic("M0", {"B0": True, "B3": False}, {"B0": P, "B3": P})
    assert r["pair_status"] == checks.QS_NA_INFEASIBLE and r["ineligible_arms"] == "B3"
    assert r["pair_status"] != checks.QS_NA_PROFILE
    b = dict(VALID, Wh_per_ref_km=1.0)
    assert checks.classify_pair(b, dict(b), eco_profile_ok=True, baseline_ok=True, pstate="P1") == checks.COMPARABLE


def _rows(nom=None, sen_m0=32, sen_m1=32, sen_other="PROFILE_UNAVAILABLE"):
    rows = [dict(set="NOM", motor=m, limits=lim, status=(nom or {}).get((m, lim), checks.COMPARABLE),
                 qs_vs_dyn_pair_status="PASS" if m != "M2" else "REPORTED_ONLY")        # rev10: I-1 read by the verdict
            for m, lim in checks.H3_NOMINAL_CELLS]
    for m, n in (("M0", sen_m0), ("M1", sen_m1)):
        rows += [dict(set="SEN", motor=m, limits="L-EVE", status=checks.COMPARABLE if i < n else sen_other)
                 for i in range(32)]
    return rows


QS_OK = [dict(motor="M0", outcome="PASS"), dict(motor="M1", outcome="PASS"), dict(motor="M2", outcome="REPORTED_ONLY")]


def test_amb29a_missing_profiles_cannot_produce_an_overall_verdict_by_omission():
    full = checks.h3_verdict_eligibility(_rows(), QS_OK)
    assert full["supported_possible"] and full["not_supported_possible"]
    one = checks.h3_verdict_eligibility(_rows(nom={("M2", "L-EVE"): "PROFILE_UNAVAILABLE"}), QS_OK)
    assert not one["supported_possible"] and not one["not_supported_possible"]
    assert one["verdict_without_energy"] == "INCONCLUSIVE" and "M2/L-EVE" in one["reasons"][0]
    gone = [r for r in _rows() if not (r["set"] == "NOM" and r["motor"] == "M1" and r["limits"] == "L-R1")]
    assert checks.h3_verdict_eligibility(gone, QS_OK)["nominal_cells"]["M1/L-R1"] == "NOT_IN_RECORD"
    assert not checks.h3_verdict_eligibility(gone, QS_OK)["supported_possible"]           # a dropped row never helps
    sen = checks.h3_verdict_eligibility(_rows(sen_m0=28), QS_OK)
    assert not sen["supported_possible"] and sen["sensitivity"]["M0"]["not_comparable_or_missing"] == 4
    short = [r for r in _rows() if not (r["set"] == "SEN" and r["motor"] == "M1")]       # M1 draws absent
    assert checks.h3_verdict_eligibility(short, QS_OK)["sensitivity"]["M1"]["max_draws_that_could_pass"] == 0
    qs_na = checks.h3_verdict_eligibility(_rows(), [dict(motor="M0", outcome="INCONCLUSIVE"), QS_OK[1]])
    assert not qs_na["supported_possible"] and not qs_na["not_supported_possible"]


def test_amb29a_planned_run_and_feasibility_denominators(tmp_path, monkeypatch):
    real_plan = campaign.plan_design

    def plan(task, lim, p, mm, grid=campaign.GRID_COARSE):
        d = real_plan(task, lim, p, mm, grid)
        return _failed_design(d) if task.cycle == "FAILX" else d
    monkeypatch.setattr(campaign, "plan_design", plan)
    tasks = {"GENTLE": _gentle(), "FAILX": _gentle("FAILX")}
    out = tmp_path / "o"
    rows = campaign.execute_schedule([_cond("OK"), _cond("PF", cycle="FAILX")], lambda n: tasks[n], out)
    assert [r["status"] for r in rows].count("PROFILE_UNAVAILABLE") == 1
    feas = {(a["motor"], a["set"]): a for a in csv.DictReader((out / "feasibility_accounting.csv").open(encoding="utf-8"))}
    t = feas[("ALL", "ALL")]
    assert t["planned_conditions"] == "2" and t["planned_runs"] == "4"                   # nothing removed
    assert t["runs_executed"] == "3" and t["runs_not_executed"] == "1" and t["runs_not_executed_profile_failure"] == "1"
    assert t["profile_failure_conditions"] == "1" and t["status_PROFILE_UNAVAILABLE"] == "1"
    assert sum(int(t[f"status_{s}"]) for s in checks.STATUSES) == 2
    assert sum(int(t[f"runs_{k}"]) for k in checks.ENERGY_ROLES) == 4
    assert int(t["paired_endpoint_eligible_conditions"]) + int(t["excluded_from_paired_endpoint_conditions"]) == 2
    roles = {x["run_id"]: x for x in csv.DictReader((out / "energy_roles.csv").open(encoding="utf-8"))}
    pf = _cond("PF", cycle="FAILX").run_ids
    assert roles[pf["B3"]]["energy_role"] == "NO_ENERGY_NOT_EXECUTED"
    assert roles[pf["B0"]]["energy_role"] != checks.CONFIRMATORY                       # valid run, pair not comparable
    man = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert man["n_runs_scheduled"] == 4 and man["denominator"]["total"] == 2
    assert man["h3_verdict_eligibility"]["supported_possible"] is False                # no nominal cells at all
    assert (out / "h3_verdict_eligibility.json").is_file()


# ============================================================ AMB-31: energy of a run failing 8.2
def test_amb31_both_arms_valid_is_eligible_for_the_paired_endpoint():
    b0, b3 = dict(VALID), dict(VALID)
    st = checks.classify_pair(b0, b3, eco_profile_ok=True, baseline_ok=True, pstate="P1")
    assert st == checks.COMPARABLE
    assert checks.energy_role(True, checks.arm_comparable(b0), True, st) == checks.CONFIRMATORY
    r = checks.pair_qs_dynamic("M0", {"B0": True, "B3": True}, {"B0": P, "B3": P})
    assert r["pair_status"] == "PASS"


def _invalidate_b3(monkeypatch, field="constraint_ok"):
    real = campaign.run_arm

    def arm(rid, branch, *a, **k):
        sim, ev, st, cmp = real(rid, branch, *a, **k)
        if branch == "B3":
            ev[field] = False                                  # the evaluator's verdict: B3 fails a protocol 8.2 rule
        return sim, ev, st, cmp
    monkeypatch.setattr(campaign, "run_arm", arm)


def test_amb31_an_arm_failing_8_2_keeps_its_energy_as_diagnostic_only(tmp_path, monkeypatch):
    task = _gentle()
    design = campaign.plan_design(task, "L-R1", config.params_for("P1"), config.motor_model("M0"))
    _invalidate_b3(monkeypatch)
    r = _run(_cond("INV"), design, task, tmp_path)
    assert r["status"] == "INVALID_COMPARISON" and "constraint compliance" in r["b3_failed_8_2"]
    assert r["qs_eligible_pair"] is True and r["qs_vs_dyn_pair_status"] == checks.QS_RUN_INVALID
    assert r["qs_vs_dyn_invalid_arms"] == "B3"
    b3 = r["_rows"]["B3"]
    assert b3["qs_vs_dyn_pct"] == "" and isinstance(b3["qs_vs_dyn_pct_diagnostic_invalid_run"], float)  # diagnostic
    sim3 = next(s for s in r["_sims"] if s["branch"] == "B3")
    assert sim3["executed"] is True and np.isfinite(sim3["E_net_Wh"])                    # raw energy preserved
    assert checks.energy_role(True, checks.arm_comparable(b3), True, r["status"]) == "DIAGNOSTIC_ONLY_RUN_INVALID"
    with pytest.raises(ValueError):
        checks.paired_delta(r["status"], r["_rows"]["B0"], b3)                             # excluded from the endpoint


def test_amb31_an_incomplete_arm(tmp_path, monkeypatch):
    inc = dict(VALID, complete=False)                                                     # shortfall > 0.1 % of d_ref
    assert checks.classify_pair(dict(VALID), inc, eco_profile_ok=True, baseline_ok=True, pstate="P1") == "INVALID_COMPARISON"
    assert checks.failed_criteria(inc) == ["complete"]
    assert checks.energy_role(True, checks.arm_comparable(inc), True, "INVALID_COMPARISON") == "DIAGNOSTIC_ONLY_RUN_INVALID"
    real = campaign.run_arm

    def arm(rid, branch, *a, **k):
        if branch == "B3":
            raise RuntimeError("injected: run did not complete")
        return real(rid, branch, *a, **k)
    monkeypatch.setattr(campaign, "run_arm", arm)
    task = _gentle()
    design = campaign.plan_design(task, "L-R1", config.params_for("P1"), config.motor_model("M0"))
    r = _run(_cond("INC"), design, task, tmp_path)
    # rev14 (owner decision I-6b, 2026-10-29): the attempted B3 run raised, so the pair is CONDITION_ERROR, not RUN_MISSING
    assert r["status"] == "ERROR" and r["qs_vs_dyn_pair_status"] == checks.QS_CONDITION_ERROR
    assert next(s for s in r["_sims"] if s["branch"] == "B3")["executed"] is False
    assert checks.energy_role(False, False, False, r["status"]) == "NO_ENERGY_NOT_EXECUTED"


def test_amb31_invalid_energy_never_passes_or_fails_the_qs_check():
    r = checks.pair_qs_dynamic("M0", {"B0": True, "B3": True}, {"B0": P}, invalid_arms=["B3"])
    assert r["pair_status"] == checks.QS_RUN_INVALID                                      # not PASS
    r = checks.pair_qs_dynamic("M0", {"B0": True, "B3": True}, {"B0": F}, invalid_arms=["B3"])
    assert r["pair_status"] == "FAIL" and r["fail_arms"] == "B0"                          # a valid arm's FAIL counts
    r = checks.pair_qs_dynamic("M2", {"B0": True, "B3": True}, {"B0": P}, invalid_arms=["B3"])
    assert r["pair_status"] == checks.QS_RUN_INVALID
    rows = [dict(motor="M0", set="NOM", limits="L-R1", qs_vs_dyn_pair_status="PASS"),        # rev9 (review R5-10)
            dict(motor="M0", set="NOM", limits="L-EVE", qs_vs_dyn_pair_status="PASS"),
            dict(motor="M0", set="P3", limits="L-R1", qs_vs_dyn_pair_status=checks.QS_RUN_INVALID)]
    out = checks.branch_qs_dynamic_outcome("M0", rows)
    assert out["outcome"] == "INCONCLUSIVE" and "could not be evaluated" in out["reason"]  # AMB-29(b) ruling
    assert checks.branch_qs_dynamic_outcome("M2", rows[2:])["outcome"] == "REPORTED_ONLY"
    t = next(a for a in checks.qs_dynamic_accounting([dict(r, qs_eligible_pair=True) for r in rows]) if a["set"] == "ALL")
    assert t["not_evaluable_run_invalid"] == 1 and t["qs_check_pass"] == 2


def test_amb31_an_unconfirmed_recomputation_demotes_a_qs_result():
    c = SimpleNamespace(run_ids={"B0": "r0", "B3": "r3"})
    sep = [dict(run_id="r0", recomputed="True", protocol_ok="True"), dict(run_id="r3", recomputed="True", protocol_ok="False")]
    row = dict(status=checks.COMPARABLE, qs_vs_dyn_pair_status="PASS", qs_vs_dyn_fail_arms="", qs_vs_dyn_pair_reason="x")
    campaign.fold_separate_recomputation([row], [c], sep, 0)
    assert row["status"] == "RECOMPUTATION_DISAGREEMENT" and row["paired_endpoint_eligible"] is False
    assert row["qs_vs_dyn_pair_status"] == checks.QS_RUN_INVALID and row["qs_vs_dyn_pair_status_in_process"] == "PASS"
    keep = dict(status="INVALID_COMPARISON", qs_vs_dyn_pair_status="FAIL", qs_vs_dyn_fail_arms="B0", qs_vs_dyn_pair_reason="x")
    campaign.fold_separate_recomputation([keep], [c], sep, 0)
    assert keep["qs_vs_dyn_pair_status"] == "FAIL"                                        # confirmed arm's FAIL stays
    ok = dict(status=checks.COMPARABLE, qs_vs_dyn_pair_status="PASS", qs_vs_dyn_fail_arms="", qs_vs_dyn_pair_reason="x")
    campaign.fold_separate_recomputation([ok], [c], [dict(sep[0]), dict(sep[1], protocol_ok="True")], 0)
    assert ok["status"] == checks.COMPARABLE and ok["paired_endpoint_eligible"] is True
    assert ok["qs_vs_dyn_pair_status"] == "PASS"


def test_amb31_crediting_an_invalid_arm_changes_no_status_role_denominator_or_verdict():
    inv = dict(VALID, constraint_ok=False)
    forged = dict(inv, credited=True, comparable=True, recompute_protocol_ok=True, Wh_per_ref_km=0.1)  # attempted credit
    for arm in (inv, forged):
        assert checks.classify_pair(dict(VALID), arm, eco_profile_ok=True, baseline_ok=True, pstate="P1") == "INVALID_COMPARISON"
        assert checks.energy_role(True, checks.arm_comparable(arm), True, "INVALID_COMPARISON") == "DIAGNOSTIC_ONLY_RUN_INVALID"
        assert checks.energy_role(True, checks.arm_comparable(arm), True, checks.COMPARABLE) == "DIAGNOSTIC_ONLY_RUN_INVALID"
    with pytest.raises(ValueError):
        checks.paired_delta("INVALID_COMPARISON", dict(VALID, Wh_per_ref_km=1.0), forged)
    rows = _rows(nom={("M0", "L-R1"): "INVALID_COMPARISON"})
    tampered = [dict(r, credited=True, E_net_Wh=1.0, dE_rel_pct=-5.0) for r in rows]
    a, b = checks.h3_verdict_eligibility(rows, QS_OK), checks.h3_verdict_eligibility(tampered, QS_OK)
    assert a == b and not a["supported_possible"]
    assert checks.denominator([r["status"] for r in rows]) == checks.denominator([r["status"] for r in tampered])


# ============================================================ amendment handling and fail-closed
def test_rev3_draft_is_unchanged_and_the_candidate_is_a_draft():
    assert frozen.sha256(campaign.PILOT_DIR / "03_protocol_v1_amendment_2_DRAFT.md") == \
        "fdaf193de510488733f0e0899d50def86cbeafabdbecdd3bc7a144099b6f492c"
    # rev8/rev9: candidate rev4 is kept unchanged and superseded by a later candidate revision
    assert frozen.sha256(campaign.PILOT_DIR / "03_protocol_v1_amendment_2_rev4_CANDIDATE.md") == \
        "c726560d1e87036cbd94fe58724cafdc1e4746647f6cfacbb320f3e14ed143ab"
    m = re.fullmatch(r"03_protocol_v1_amendment_2_rev(\d+)_CANDIDATE\.md", campaign.DRAFT_AMENDMENT_2.name)
    assert m and int(m.group(1)) > 4
    r = campaign.read_amendment(campaign.DRAFT_AMENDMENT_2, campaign.IMPLEMENTED_2, {})
    assert r["exists"] and not r["errors"] and r["status"] == "DRAFT", r["errors"]
    text = campaign.DRAFT_AMENDMENT_2.read_text(encoding="utf-8")
    assert "NOT APPROVED FOR RELEASE" in text.splitlines()[2]
    assert frozen.FROZEN_SHA256[frozen.PROTOCOL] in text and campaign.AMENDMENT_1_SHA256 in text
    assert "AMB_31_usable_dynamic_energy" not in campaign.IMPLEMENTED_2
    assert "explicit" in campaign.IMPLEMENTED_2["AMB_29_profile_unavailable"]
    assert checks.QS_RUN_INVALID in campaign.IMPLEMENTED_2["pair_statuses"]


def test_a_pending_review_blocks_campaign_and_readiness(tmp_path, monkeypatch):
    b = " | ".join(campaign.preconditions("readiness"))
    if json.loads(campaign.REVIEW_STATUS.read_text(encoding="utf-8")).get("reviews_pending"):
        assert "code review not yet performed" in b
    rv = json.loads(campaign.REVIEW_STATUS.read_text(encoding="utf-8"))
    rv["reviews_pending"] = []
    p = tmp_path / "rv.json"
    p.write_text(json.dumps(rv), encoding="utf-8")
    monkeypatch.setattr(campaign, "REVIEW_STATUS", p)
    assert "code review not yet performed" not in " | ".join(campaign.preconditions("readiness"))
