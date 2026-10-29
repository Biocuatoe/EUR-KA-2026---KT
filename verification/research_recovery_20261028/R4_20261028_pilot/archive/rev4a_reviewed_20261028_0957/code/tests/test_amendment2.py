"""Owner ruling N-A2 (amendment 2 draft): pair-level applicability of the protocol 9 QS-vs-dynamic check.
These tests check protocol semantics only; none checks or targets an energy-saving value."""

import csv
import json

import numpy as np
import pytest

from r4h3 import campaign, checks, config, evaluator, frozen
from r4h3 import task as taskmod
from r4h3.closedloop import fixed_gain

NA = checks.QS_NA_INFEASIBLE
P = {"status": "pass", "diff_pct": 0.3}
F = {"status": "FAIL (branch INCONCLUSIVE, protocol 9)", "diff_pct": 1.7}


# ---- pair-level rule (cases 1-5, 11)
def test_case1_both_feasible_and_the_check_passes():
    r = checks.pair_qs_dynamic("M0", {"B0": True, "B3": True}, {"B0": P, "B3": P})
    assert r["pair_status"] == "PASS" and r["qs_eligible"] is True


def test_case2_both_feasible_and_an_applicable_check_fails():
    r = checks.pair_qs_dynamic("M1", {"B0": True, "B3": True}, {"B0": P, "B3": F})
    assert r["pair_status"] == "FAIL" and r["qs_eligible"] is True
    rows = [dict(motor="M1", set="NOM", qs_vs_dyn_pair_status="FAIL"), dict(motor="M1", set="NOM", qs_vs_dyn_pair_status="PASS")]
    assert checks.branch_qs_dynamic_outcome("M1", rows)["outcome"] == "INCONCLUSIVE"       # frozen protocol 9 consequence


@pytest.mark.parametrize("screen,arms", [({"B0": False, "B3": True}, "B0"), ({"B0": True, "B3": False}, "B3"),
                                         ({"B0": False, "B3": False}, "B0,B3")])
def test_cases3_to_5_any_qs_infeasible_profile_makes_the_pair_not_applicable(screen, arms):
    # the per-arm results must not be consulted: even a passing value cannot make the pair pass
    r = checks.pair_qs_dynamic("M0", screen, {"B0": P, "B3": P})
    assert r["pair_status"] == NA and r["qs_eligible"] is False and r["ineligible_arms"] == arms
    r = checks.pair_qs_dynamic("M0", screen, {"B0": F, "B3": F})
    assert r["pair_status"] == NA                                                    # nor a failing one fail it


def test_case11_not_applicable_is_never_a_pass():
    assert NA not in ("PASS", "FAIL") and campaign.IMPLEMENTED_2["N_A2_not_applicable_is_pass"] is False
    only_na = [dict(motor="M0", set="P3", qs_vs_dyn_pair_status=NA)] * 3
    assert checks.branch_qs_dynamic_outcome("M0", only_na)["outcome"] == "INCONCLUSIVE"
    with_pass = only_na + [dict(motor="M0", set="NOM", qs_vs_dyn_pair_status="PASS")]
    out = checks.branch_qs_dynamic_outcome("M0", with_pass)
    assert out["outcome"] == "PASS" and out["n_PASS"] == 1 and out[f"n_{NA}"] == 3     # only applicable checks count


# ---- branch rule (case 8) and AMB-29
def test_case8_a_branch_with_zero_eligible_comparisons_is_inconclusive():
    rows = [dict(motor="M1", set="P3", qs_vs_dyn_pair_status=NA),
            dict(motor="M1", set="NOM", qs_vs_dyn_pair_status=checks.QS_NA_PROFILE)]
    out = checks.branch_qs_dynamic_outcome("M1", rows)
    assert out["outcome"] == "INCONCLUSIVE" and "vacuity" in out["reason"]
    assert checks.branch_qs_dynamic_outcome("M1", [])["outcome"] == "INCONCLUSIVE"
    m2 = checks.branch_qs_dynamic_outcome("M2", rows)
    assert m2["outcome"] == "REPORTED_ONLY"                                           # M2: reported only, unchanged


def test_amb29_eligible_pair_without_usable_energy_does_not_pass():
    r = checks.pair_qs_dynamic("M0", {"B0": True, "B3": True}, {"B0": P})
    assert r["pair_status"] == checks.QS_NOT_EVALUABLE and r["qs_eligible"] is True
    rows = [dict(motor="M0", set="NOM", qs_vs_dyn_pair_status="PASS"),
            dict(motor="M0", set="NOM", qs_vs_dyn_pair_status=checks.QS_NOT_EVALUABLE)]
    assert checks.branch_qs_dynamic_outcome("M0", rows)["outcome"] == "INCONCLUSIVE"
    r = checks.pair_qs_dynamic("M0", {"B0": True, "B3": None}, {})
    assert r["pair_status"] == checks.QS_NA_PROFILE and r["qs_eligible"] is False


def test_thresholds_are_unchanged():
    assert checks.QS_DYN_MAX_PCT == 1.0 and checks.QS_DYN_DECISIVE == {"M0": True, "M1": True, "M2": False}
    assert campaign.IMPLEMENTED_2["N_A2_thresholds"] == {"M0_max_abs_pct": 1.0, "M1_max_abs_pct": 1.0, "M2": "reported only"}


# ---- denominators (case 9)
def test_case9_denominator_and_exclusion_accounting():
    rows = [
        dict(motor="M0", set="P3", status="COMPARABLE", qs_vs_dyn_pair_status=NA, qs_eligible_pair=False,
             qs_ineligible_arms="B3", dynamic_valid_pair=True),
        dict(motor="M0", set="P3", status="BASELINE_INFEASIBLE_ON_P3", qs_vs_dyn_pair_status=NA, qs_eligible_pair=False,
             qs_ineligible_arms="B0,B3", dynamic_valid_pair=False),
        dict(motor="M0", set="NOM", status="COMPARABLE", qs_vs_dyn_pair_status="PASS", qs_eligible_pair=True,
             qs_ineligible_arms="", dynamic_valid_pair=True),
        dict(motor="M0", set="NOM", status="PROFILE_UNAVAILABLE", qs_vs_dyn_pair_status=checks.QS_NA_PROFILE,
             qs_eligible_pair=False, qs_ineligible_arms="", dynamic_valid_pair=False),
    ]
    acct = {(a["motor"], a["set"]): a for a in checks.qs_dynamic_accounting(rows)}
    t = acct[("M0", "ALL")]
    assert t["planned_pairs"] == 4 and t["qs_eligible_pairs"] == 1 and t["qs_ineligible_pairs"] == 2
    assert t["qs_ineligible_b3_only"] == 1 and t["qs_ineligible_both"] == 1 and t["qs_ineligible_b0_only"] == 0
    assert t["not_evaluable_profile_unavailable"] == 1 and t["qs_check_pass"] == 1 and t["qs_check_fail"] == 0
    assert t["dynamic_valid_pairs"] == 2 and t["valid_energy_comparison_pairs"] == 2
    assert acct[("M0", "P3")]["planned_pairs"] == 2 and acct[("M0", "NOM")]["planned_pairs"] == 2
    # every planned pair is in exactly one status class
    keys = ("qs_check_pass", "qs_check_fail", "qs_check_reported_only", "qs_ineligible_pairs",
            "not_evaluable_profile_unavailable", "not_evaluable_run_missing")
    assert sum(t[k] for k in keys) == t["planned_pairs"]


# ---- executor level (cases 6, 7, 10)
def _gentle():
    v = np.array([0, 0, 0.5, 1, 1.5, 2, 2, 2, 2, 2, 1.5, 1, 1, 1, 1, 1, 1.5, 2, 2, 2, 2, 2, 1.5, 1, 0.5, 0, 0, 0], float)
    return taskmod.task_from_samples("GENTLE", np.arange(len(v), dtype=float), v)


def _cond(tag, pstate="P3", cycle="GENTLE"):
    cid = f"DEV-NA2-{tag}-{cycle}-M0-LR1-{pstate}-dt1ms"
    return campaign.Condition(cid, "DEV", cycle, "M0", "L-R1", pstate, 1e-3, None,
                              {b: cid.replace("-dt", f"-{b}-dt") for b in ("B0", "B3")})


def _force_screen_failure(monkeypatch, arms=("B0", "B3")):
    """Make the QS screen report a failure for the given arms (B0 = the 1 s grid profile, B3 = the S-eco knots)."""
    real = campaign.checks.qs_energy

    def screen(plant, t, v):
        r = real(plant, t, v)
        is_b0 = len(t) > 2 and np.allclose(np.diff(t), 1.0)
        if ("B0" in arms and is_b0) or ("B3" in arms and not is_b0):
            return dict(r, feasible=False, n_infeasible_pieces=1,
                        infeasible_pieces=[dict(piece=3, t0_s=3.0, t1_s=4.0, v0_ms=1.0, v1_ms=1.5)])
        return r

    monkeypatch.setattr(campaign.checks, "qs_energy", screen)


def test_case6_qs_ineligible_but_dynamically_feasible(tmp_path, monkeypatch):
    task, mm = _gentle(), config.motor_model("M0")
    design = campaign.plan_design(task, "L-R1", config.params_for("P1"), mm)
    _force_screen_failure(monkeypatch, ("B3",))
    r = campaign.run_condition(_cond("C6"), task, design, config.params_for("P3"), 0.8, config.LIMITS["L-R1"], mm,
                               evaluator.motor_spec_from_protocol("M0", frozen.M1_CURVE),
                               fixed_gain(config.params_for("P1")), tmp_path)
    assert r["qs_vs_dyn_pair_status"] == NA and r["qs_ineligible_arms"] == "B3" and r["qs_eligible_pair"] is False
    assert r["status"] == "COMPARABLE" and r["dynamic_valid_pair"] is True              # 8.2 decides feasibility
    for b in ("B0", "B3"):
        ev = r["_rows"][b]
        assert ev["qs_vs_dyn_status"] == NA and ev["qs_vs_dyn_pct"] == ""             # no QS value used
        assert "qs_E_J_diagnostic" in ev                                               # diagnostic preserved
    assert r["b3_qs_screen_warning"].startswith("piece 3") and r["b0_qs_screen_warning"] == ""


def test_case7_qs_ineligible_and_dynamically_infeasible(tmp_path):
    task, mm = _gentle(), config.motor_model("M0")
    design = campaign.plan_design(task, "L-R1", config.params_for("P1"), mm)
    weak = config.params_for("P3").with_overrides(T_max=2.0)            # real QS failure and real 8.2 failure
    r = campaign.run_condition(_cond("C7"), task, design, weak, 0.8, config.LIMITS["L-R1"], mm,
                               evaluator.motor_spec_from_protocol("M0", frozen.M1_CURVE),
                               fixed_gain(config.params_for("P1")), tmp_path)
    assert r["qs_vs_dyn_pair_status"] == NA and r["qs_eligible_pair"] is False
    assert r["status"] == "BASELINE_INFEASIBLE_ON_P3" and r["b0_failed_8_2"]           # QS N/A excuses nothing
    assert r["dynamic_valid_pair"] is False
    with pytest.raises(ValueError):
        checks.paired_delta(r["status"], {}, {})


def test_eligible_pair_is_evaluated_with_the_frozen_rule(tmp_path):
    task, mm = _gentle(), config.motor_model("M0")
    design = campaign.plan_design(task, "L-R1", config.params_for("P1"), mm)
    r = campaign.run_condition(_cond("ELIG", pstate="P1"), task, design, config.params_for("P1"), 1.0,
                               config.LIMITS["L-R1"], mm, evaluator.motor_spec_from_protocol("M0", frozen.M1_CURVE),
                               fixed_gain(config.params_for("P1")), tmp_path)
    assert r["qs_eligible_pair"] is True and r["qs_vs_dyn_pair_status"] in ("PASS", "FAIL")
    arm = {b: r["_rows"][b] for b in ("B0", "B3")}
    assert all(isinstance(arm[b]["qs_vs_dyn_pct"], float) for b in arm)
    expect = "PASS" if all(abs(arm[b]["qs_vs_dyn_pct"]) <= 1.0 for b in arm) else "FAIL"
    assert r["qs_vs_dyn_pair_status"] == expect


def test_case10_records_are_preserved_and_accounting_written(tmp_path, monkeypatch):
    _force_screen_failure(monkeypatch, ("B0", "B3"))
    task = _gentle()
    rows = campaign.execute_schedule([_cond("C10")], lambda name: task, tmp_path / "out")
    out = tmp_path / "out"
    runs = list(csv.DictReader((out / "runs.csv").open(encoding="utf-8")))
    ev = list(csv.DictReader((out / "evaluation.csv").open(encoding="utf-8")))
    assert len(runs) == 2 and all(r["executed"] == "True" for r in runs)               # nothing dropped
    assert len(ev) == 2 and all(e["qs_vs_dyn_status"] == NA and e["qs_screen_feasible"] == "False" for e in ev)
    assert all((out / "traces" / f"{r['run_id']}.npz").is_file() for r in runs)
    acct = list(csv.DictReader((out / "qs_dynamic_accounting.csv").open(encoding="utf-8")))
    t = next(a for a in acct if a["set"] == "ALL")
    assert t["planned_pairs"] == "1" and t["qs_ineligible_both"] == "1" and t["qs_eligible_pairs"] == "0"
    br = list(csv.DictReader((out / "qs_dynamic_branch_outcomes.csv").open(encoding="utf-8")))
    assert br[0]["outcome"] == "INCONCLUSIVE"                                           # no eligible pair: not a pass
    man = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert man["qs_dynamic_branch_outcomes"][0]["outcome"] == "INCONCLUSIVE"
    assert rows[0]["qs_vs_dyn_pair_status"] == NA


# ---- fail-closed (case 12) and the amendment 2 draft
def test_case12_campaign_mode_stays_blocked_without_authorisation_and_amendment_2():
    c = " ".join(campaign.preconditions("campaign"))
    if not campaign.CAMPAIGN_AUTHORIZATION.exists():
        assert "no campaign authorisation record" in c
    if not campaign.ISSUED_AMENDMENT_2.exists():
        assert "no issued amendment 2" in c
    good = dict(authorized_by="o", date="d", scope=campaign.AUTHORIZATION_SCOPE, amendment_sha256="a" * 64,
                pre_run_hashes_sha256="b" * 64, amendment_2_sha256="c" * 64)
    assert campaign.authorization_problems(good, "a" * 64, "b" * 64, "c" * 64) == []
    assert campaign.authorization_problems(dict(good, amendment_2_sha256=""), "a" * 64, "b" * 64, "c" * 64)
    assert campaign.authorization_problems(good, "a" * 64, "b" * 64, None)


def test_amendment_2_draft_parses_and_is_a_draft():
    r = campaign.read_amendment(campaign.DRAFT_AMENDMENT_2, campaign.IMPLEMENTED_2, {})
    assert r["exists"] and not r["errors"], r["errors"]
    assert r["status"] == "DRAFT" and r["open"] == []
    text = campaign.DRAFT_AMENDMENT_2.read_text(encoding="utf-8")
    assert "DRAFT — NOT APPROVED FOR RELEASE" in text.splitlines()[2]
    assert frozen.FROZEN_SHA256[frozen.PROTOCOL] in text and campaign.AMENDMENT_1_SHA256 in text
    # amendment 1 stays valid and unedited
    assert campaign.read_amendment(campaign.ISSUED_AMENDMENT)["errors"] == []
    assert frozen.sha256(campaign.ISSUED_AMENDMENT) == campaign.AMENDMENT_1_SHA256


def test_si1_paths_are_location_independent():
    assert (frozen.REPO / "src" / "eureka").is_dir()
    assert frozen.PREFLIGHT == frozen.REPO / "verification" / "research_recovery_20261028" / "R4_20261028_preflight"
    assert campaign.CAMPAIGN_DIR == frozen.RR / "R4_20261028_campaign" and campaign.PILOT_DIR == frozen.RR / "R4_20261028_pilot"
    if frozen.PILOT.name in ("R4_20261028_pilot", "R4_20261028_campaign"):
        assert frozen.REPO == frozen.PILOT.parents[2]                                  # unchanged from the former rule
