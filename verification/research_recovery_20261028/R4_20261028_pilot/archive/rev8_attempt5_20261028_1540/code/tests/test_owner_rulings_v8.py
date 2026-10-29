"""Owner rulings of 2026-10-28 on AMB-29(b)-(d), AMB-30 and AMB-32 (amendment 2 candidate rev5), with the AMB-29(a) and
AMB-31 rulings kept. These tests check protocol semantics only. None computes, reports or targets an energy difference
between arms; the synthetic numbers in the pure-rule tests are not run energies."""

import csv
import inspect
import itertools
import json

import numpy as np
import pytest

from r4h3 import campaign, checks, config, frozen
from r4h3 import task as taskmod

NA, NA_PROFILE = checks.QS_NA_INFEASIBLE, checks.QS_NA_PROFILE
NOT_EVALUABLE = checks.PAIR_STATUS_CLASSES["NOT_EVALUABLE"]
_ids = itertools.count(1)


def _r(set_, limits, status, motor="M0"):
    return dict(motor=motor, set=set_, limits=limits, condition_id=f"T-{set_}-{motor}-{limits}-{next(_ids)}",
                qs_vs_dyn_pair_status=status)


def _nom(s_r1="PASS", s_eve="PASS", motor="M0"):
    return [_r("NOM", "L-R1", s_r1, motor), _r("NOM", "L-EVE", s_eve, motor)]


def _out(rows, motor="M0", planned=None):
    return checks.branch_qs_dynamic_outcome(motor, rows, planned)


def _status_rows(nom=None):
    """Condition statuses of a complete record: the 6 nominal cells and 32 draws per M0/M1 (protocol 8.1)."""
    rows = [dict(set="NOM", motor=m, limits=lim, status=(nom or {}).get((m, lim), checks.COMPARABLE))
            for m, lim in checks.H3_NOMINAL_CELLS]
    rows += [dict(set="SEN", motor=m, limits="L-EVE", status=checks.COMPARABLE) for m in ("M0", "M1") for _ in range(32)]
    return rows


QS_OK = [dict(motor="M0", outcome="PASS"), dict(motor="M1", outcome="PASS"), dict(motor="M2", outcome="REPORTED_ONLY")]


# ============================================================ AMB-30: the nominal held-out S2 requirement
def test_amb30_an_s1_pass_with_the_nominal_s2_cells_missing_is_inconclusive():
    ins = [_r("INS", "L-R1", "PASS"), _r("INS", "L-EVE", "PASS")]
    out = _out(ins)                                                        # nominal rows absent from the record
    assert out["outcome"] == "INCONCLUSIVE" and out["n_PASS_nominal"] == 0 and out["n_PASS_other_sets"] == 2
    assert out["nominal_L-R1"] == out["nominal_L-EVE"] == checks.NOT_IN_RECORD
    assert "cannot substitute" in out["reason"] and "held-out nominal set NOM" in out["reason"]
    for s in (NA_PROFILE, NA, *NOT_EVALUABLE):                             # nominal rows present, none passes
        assert _out(_nom(s, s) + ins)["outcome"] == "INCONCLUSIVE", s
    planned = [r["condition_id"] for r in _nom() + ins]                    # planned nominal pairs dropped
    out = _out(ins, planned=planned)
    assert out["outcome"] == "INCONCLUSIVE" and out["planned_pairs_missing_from_record"].count("T-NOM-") == 2


def test_amb30_an_s1_pass_with_a_failed_nominal_s2_check_is_inconclusive():
    ins = [_r("INS", "L-R1", "PASS"), _r("INS", "L-EVE", "PASS")]
    for nom in (_nom("FAIL", "FAIL"), _nom("FAIL", "PASS"), _nom("PASS", "FAIL")):
        out = _out(nom + ins)
        assert out["outcome"] == "INCONCLUSIVE" and out["fail_by_set"].startswith("NOM:"), out


@pytest.mark.parametrize("set_", ["P3", "INS", "CNV", "SEN"])
def test_amb30_a_nominal_pass_with_a_failure_in_another_preregistered_set_is_inconclusive(set_):
    out = _out(_nom() + [_r(set_, "L-EVE", "FAIL")])
    assert out["outcome"] == "INCONCLUSIVE" and out["fail_by_set"] == f"{set_}:1" and out["n_PASS_nominal"] == 2
    many = _nom() + [_r(set_, "L-EVE", "PASS") for _ in range(40)] + [_r(set_, "L-EVE", "FAIL")]
    assert _out(many)["outcome"] == "INCONCLUSIVE"                          # counted, never averaged away
    for s in NOT_EVALUABLE:                                                # AMB-29(b)-(d) in any set
        out = _out(_nom() + [_r(set_, "L-EVE", s)])
        assert out["outcome"] == "INCONCLUSIVE" and out["not_evaluable_by_set"] == f"{set_}:1", s


def test_amb30_all_required_checks_pass():
    rows = (_nom() + [_r("P3", "L-R1", "PASS"), _r("P3", "L-EVE", NA), _r("INS", "L-R1", "PASS"),
                      _r("CNV", "L-EVE", "PASS")] + [_r("SEN", "L-EVE", "PASS") for _ in range(30)]
            + [_r("SEN", "L-EVE", NA_PROFILE), _r("SEN", "L-EVE", NA)])
    out = _out(rows, planned=[r["condition_id"] for r in rows])
    assert out["outcome"] == "PASS" and out["n_PASS_nominal"] == 2 and out["fail_by_set"] == ""
    assert out["nominal_evidence_missing"] == "" and out["planned_pairs_missing_from_record"] == ""
    assert out["not_applicable_by_set"] == "P3:1,SEN:2"                     # reported, no effect outside NOM
    assert _out(_nom("PASS", NA))["outcome"] == "PASS"                       # N-A2: QS-infeasible is not missing
    m2 = [dict(r, motor="M2") for r in rows] + [_r("NOM", "L-R1", "FAIL", "M2")]
    assert _out(m2, "M2")["outcome"] == "REPORTED_ONLY"                      # M2 stays reported only


def test_no_eligible_qs_comparison_in_a_motor_branch_is_inconclusive():
    rows = [_r(s, lim, NA) for s in ("NOM", "P3", "INS", "SEN") for lim in ("L-R1", "L-EVE")]
    out = _out(rows)
    assert out["outcome"] == "INCONCLUSIVE" and "vacuity" in out["reason"] and out["n_PASS"] == 0
    assert _out([])["outcome"] == "INCONCLUSIVE"
    v = checks.h3_verdict_eligibility(_status_rows(), [out, QS_OK[1], QS_OK[2]])
    assert not v["supported_possible"] and not v["not_supported_possible"]
    assert v["verdict_without_energy"] == "INCONCLUSIVE"


# ============================================================ AMB-30 / AMB-32: a missing required nominal cell
def test_a_missing_required_nominal_cell():
    out = _out([_r("NOM", "L-R1", "PASS")])
    assert out["outcome"] == "INCONCLUSIVE" and out["nominal_L-EVE"] == checks.NOT_IN_RECORD
    dup = _out(_nom() + [_r("NOM", "L-R1", "PASS")])
    assert dup["outcome"] == "INCONCLUSIVE" and dup["nominal_L-R1"] == checks.DUPLICATE_IN_RECORD
    full = _status_rows()
    assert checks.h3_verdict_eligibility(full, QS_OK)["nominal_missing_evidence"] == []
    gone = [r for r in full if (r["set"], r["motor"], r["limits"]) != ("NOM", "M2", "L-R1")]
    v = checks.h3_verdict_eligibility(gone, QS_OK)
    assert not v["not_supported_possible"] and not v["supported_possible"] and v["verdict_without_energy"] == "INCONCLUSIVE"
    assert v["nominal_missing_evidence"] == [dict(cell="M2/L-R1", status=checks.NOT_IN_RECORD,
                                                  detail="no row in the record")]
    for st, extra, frag in (("INVALID_COMPARISON", dict(b3_failed_8_2="constraint compliance"), "constraint compliance"),
                            ("ERROR", dict(error="RuntimeError: injected"), "injected"),
                            ("PROFILE_UNAVAILABLE", dict(eco_status="unavailable"), "eco_status=unavailable"),
                            ("RECOMPUTATION_DISAGREEMENT",
                             dict(separate_recomputation="B3: separate recomputation fails a protocol check"),
                             "separate recomputation fails")):
        rows = [dict(r, status=st, **extra) if (r["set"], r["motor"], r["limits"]) == ("NOM", "M0", "L-EVE") else r
                for r in full]
        v = checks.h3_verdict_eligibility(rows, QS_OK)
        assert not v["not_supported_possible"] and v["verdict_without_energy"] == "INCONCLUSIVE", st
        me = v["nominal_missing_evidence"]                                  # AMB-32: the reason is recorded
        assert len(me) == 1 and me[0]["cell"] == "M0/L-EVE" and me[0]["status"] == st and frag in me[0]["detail"], me
        assert "not NOT SUPPORTED" in v["reasons"][0]


# ============================================================ no pass by omission
def test_no_situation_yields_a_pass_by_omission():
    base = _nom() + [_r("P3", "L-R1", "FAIL"), _r("INS", "L-EVE", checks.QS_RUN_INVALID),
                     _r("SEN", "L-EVE", NA_PROFILE), _r("SEN", "L-EVE", "PASS")]
    planned = [r["condition_id"] for r in base]
    assert _out(base, planned=planned)["outcome"] == "INCONCLUSIVE"
    for k in range(1, len(base) + 1):                                      # drop any subset of the record
        for drop in itertools.combinations(range(len(base)), k):
            kept = [r for i, r in enumerate(base) if i not in drop]
            assert _out(kept, planned=planned)["outcome"] == "INCONCLUSIVE", drop
    others = [_r(s, "L-EVE", "PASS") for s in ("P3", "INS", "CNV", "SEN")]
    for s in set(checks.PAIR_QS_STATUSES) - {"PASS", NA}:                  # any other status in a nominal cell
        for nom in (_nom(s, "PASS"), _nom("PASS", s), _nom(s, s)):
            assert _out(nom + others)["outcome"] == "INCONCLUSIVE", s
    full = _status_rows()
    for cell in checks.H3_NOMINAL_CELLS:                                   # verdict level: drop any nominal cell
        v = checks.h3_verdict_eligibility([r for r in full if (r["set"], r["motor"], r["limits"]) != ("NOM", *cell)],
                                          QS_OK)
        assert not (v["supported_possible"] or v["not_supported_possible"]), cell


# ============================================================ AMB-29(c): non-positive denominators (pure rules)
def test_amb29c_non_positive_qs_energy_keeps_raw_values_and_computes_no_percentage():
    for e in (0.0, -250.0, float("nan")):
        q = checks.qs_vs_dynamic("M0", e, 0.05, 213.0)
        assert q["diff_pct"] is None and q["status"].startswith("undefined")
        assert q["E_qs_J"] == e or (np.isnan(e) and np.isnan(q["E_qs_J"]))
        assert q["non_positive_term"].startswith("e_QS") and repr(e) in q["non_positive_term"]
        assert q["E_dyn_Wh"] == 0.05 and q["d_ref_m"] == 213.0                  # raw values retained
    assert checks.qs_vs_dynamic("M0", 1.0e4, 0.05, 0.0)["non_positive_term"].startswith("d_ref_m")
    u = checks.qs_vs_dynamic("M0", -250.0, 0.05, 213.0)
    r = checks.pair_qs_dynamic("M0", {"B0": True, "B3": True}, {"B0": {"status": "pass", "diff_pct": 0.3}, "B3": u})
    assert r["pair_status"] == checks.QS_UNDEFINED and "B3: e_QS" in r["reason"] and "-250.0 J" in r["reason"]
    assert checks.QS_UNDEFINED in checks.PAIR_STATUS_CLASSES["NOT_EVALUABLE"]        # QS_COMPARISON_NOT_EVALUABLE
    d = checks.paired_delta(checks.COMPARABLE, dict(Wh_per_ref_km=0.0, trip_time_s=1.0),
                            dict(Wh_per_ref_km=1.0, trip_time_s=1.0))
    assert d["dE_rel_pct"] is None and d["dE_rel_status"] == "NOT_EVALUABLE_DENOMINATOR_NOT_POSITIVE"
    assert d["non_positive_term"].startswith("B0 energy per reference km")
    s = checks.scenario_totals(0.0, 1.0, 1.0)
    assert s["S_found_pct"] is None and s["S_max_pct"] is None and s["status"] == "NOT_EVALUABLE_DENOMINATOR_NOT_POSITIVE"
    g = checks.grid_convergence(-1.0, 1.0, 1.0)
    assert g["passed"] is None and g["dS_found_pp"] is None
    assert campaign.numerical_check_consequence("planner_grid_convergence", g["passed"]) != "pass"


# ============================================================ executor level: one mixed development schedule
def _task(name):
    v = np.array([0, 0, 0.5, 1, 1.5, 2, 2, 2, 2, 2, 1.5, 1, 1, 1, 1, 1, 1.5, 2, 2, 2, 2, 2, 1.5, 1, 0.5, 0, 0, 0], float)
    return taskmod.task_from_samples(name, np.arange(len(v), dtype=float), v)


def _dev(tag, cycle):
    cid = f"DEV-V8-{tag}-{cycle}-M0-LR1-P1-dt1ms"
    return campaign.Condition(cid, "DEV", cycle, "M0", "L-R1", "P1", 1e-3, None,
                              {b: cid.replace("-dt", f"-{b}-dt") for b in ("B0", "B3")})


# tag -> cycle; each cycle name triggers one injected situation below (all development run IDs)
CASES = {"OK": "GENTLE", "PF": "FAILX", "INV": "INVX", "RCX": "RCX", "QSNEG": "QSNEG", "EXC": "EXCX", "PEX": "PEXX",
         "CEX": "CEXX"}


@pytest.fixture(scope="module")
def mixed(tmp_path_factory):
    """OK: normal. PF: planner failure (missing S-eco profile). INV: B3 fails 8.2 (constraint). RCX: B3 not confirmed by
    the in-process recomputation. QSNEG: QS energy <= 0 on both profiles. EXC: an exception in B3's evaluation, after
    its trace is written. PEX: an exception in the pair's QS-vs-dynamic evaluation. CEX: a condition-level exception."""
    conds = [_dev(t, c) for t, c in CASES.items()]
    out = tmp_path_factory.mktemp("v8") / "mixed"
    calls, state = {}, {}
    with pytest.MonkeyPatch.context() as mp:
        real_plan, real_arm, real_eval = campaign.plan_design, campaign.run_arm, campaign.evaluator.evaluate_trace
        real_rc, real_qs, real_pair = campaign.run_condition, checks.qs_screen, checks.pair_qs_dynamic

        def plan(task, lim, p, mm, grid=campaign.GRID_COARSE):
            d = real_plan(task, lim, p, mm, grid)
            if task.cycle != "FAILX":
                return d
            return dict(d, eco={"status": "unavailable", "rows": d["eco"]["rows"], "t": None, "v": None},
                        val_e=None, eco_ok=False)

        def rc(cond, *a, **k):
            state["cycle"] = cond.cycle
            return real_rc(cond, *a, **k)

        def qs(plant, t, v):
            r = real_qs(plant, t, v)
            return dict(r, E_J=-250.0) if state["cycle"] == "QSNEG" else r

        def pair(*a, **k):
            if state["cycle"] == "PEXX":
                raise RuntimeError("injected pair evaluation failure")
            return real_pair(*a, **k)

        def ev_trace(*a, **k):
            if state["cycle"] == "EXCX" and state["branch"] == "B3":
                raise RuntimeError("injected evaluation failure")
            return real_eval(*a, **k)

        def arm(rid, branch, *a, **k):
            calls[rid] = calls.get(rid, 0) + 1
            state["branch"] = branch
            sim, ev, st, cmp = real_arm(rid, branch, *a, **k)
            if branch == "B3" and state["cycle"] == "INVX":
                ev["constraint_ok"] = False                        # the evaluator's verdict: B3 fails 8.2
            if branch == "B3" and state["cycle"] == "RCX":
                ev["recompute_protocol_ok"] = False                # in-process recomputation disagrees
            return sim, ev, st, cmp

        def loader(name):
            if name == "CEXX":
                raise RuntimeError("injected condition failure")
            return _task(name)
        mp.setattr(campaign, "plan_design", plan)
        mp.setattr(campaign, "run_condition", rc)
        mp.setattr(campaign, "run_arm", arm)
        mp.setattr(campaign.evaluator, "evaluate_trace", ev_trace)
        mp.setattr(checks, "qs_screen", qs)
        mp.setattr(checks, "pair_qs_dynamic", pair)
        rows = campaign.execute_schedule(conds, loader, out)
    read = lambda f: list(csv.DictReader((out / f).open(encoding="utf-8")))          # noqa: E731
    return dict(out=out, conds={c.cid.split("-")[2]: c for c in conds}, rows={r["condition_id"].split("-")[2]: r
                for r in rows}, calls=calls, read=read,
                manifest=json.loads((out / "manifest.json").read_text(encoding="utf-8")))


def test_mixed_schedule_statuses(mixed):
    st = {k: r["status"] for k, r in mixed["rows"].items()}
    ps = {k: r["qs_vs_dyn_pair_status"] for k, r in mixed["rows"].items()}
    assert st["OK"] == st["QSNEG"] == st["PEX"] == checks.COMPARABLE, st
    assert (st["PF"], st["INV"], st["RCX"], st["EXC"], st["CEX"]) == (
        "PROFILE_UNAVAILABLE", "INVALID_COMPARISON", "RECOMPUTATION_DISAGREEMENT", "ERROR", "ERROR")
    assert ps["OK"] in ("PASS", "FAIL")
    assert (ps["PF"], ps["INV"], ps["RCX"], ps["QSNEG"], ps["EXC"], ps["PEX"], ps["CEX"]) == (
        NA_PROFILE, checks.QS_RUN_INVALID, checks.QS_RUN_INVALID, checks.QS_UNDEFINED, checks.QS_NOT_EVALUABLE,
        checks.QS_CONDITION_ERROR, checks.QS_CONDITION_ERROR)


def test_missing_profile_and_invalid_arm_accounting(mixed):
    feas = {(a["motor"], a["set"]): a for a in mixed["read"]("feasibility_accounting.csv")}
    t = feas[("ALL", "ALL")]
    assert t["planned_conditions"] == "8" and t["planned_runs"] == "16"
    assert t["runs_executed"] == "12" and t["runs_not_executed"] == "4" and t["runs_not_executed_profile_failure"] == "1"
    assert t["runs_8_2_valid"] == "11" and t["runs_8_2_invalid"] == "1" and t["profile_failure_conditions"] == "1"
    roles = {x["run_id"]: x["energy_role"] for x in mixed["read"]("energy_roles.csv")}
    ids = {k: c.run_ids for k, c in mixed["conds"].items()}
    assert roles[ids["PF"]["B3"]] == "NO_ENERGY_NOT_EXECUTED" and roles[ids["PF"]["B0"]] == "VALID_RUN_NOT_IN_PAIRED_ENDPOINT"
    assert roles[ids["INV"]["B3"]] == "DIAGNOSTIC_ONLY_RUN_INVALID"
    assert roles[ids["RCX"]["B3"]] == "DIAGNOSTIC_ONLY_RECOMPUTATION_NOT_CONFIRMED"
    inv = {e["run_id"]: e for e in mixed["read"]("evaluation.csv")}[ids["INV"]["B3"]]
    assert inv["qs_vs_dyn_pct"] == "" and inv["qs_vs_dyn_pct_diagnostic_invalid_run"] != ""   # diagnostic only
    assert (mixed["out"] / "traces" / f"{ids['INV']['B3']}.npz").is_file()                    # trace retained
    acct = {(a["motor"], a["set"]): a for a in mixed["read"]("qs_dynamic_accounting.csv")}[("M0", "ALL")]
    assert acct["not_applicable_profile_unavailable"] == "1" and acct["not_evaluable_run_invalid"] == "2"


def test_amb29c_non_positive_qs_energy_in_the_executor(mixed):
    r, ids = mixed["rows"]["QSNEG"], mixed["conds"]["QSNEG"].run_ids
    assert r["qs_vs_dyn_pair_status"] == checks.QS_UNDEFINED and r["qs_eligible_pair"] is True
    assert "B0: e_QS" in r["qs_vs_dyn_non_positive_terms"] and "B3: e_QS" in r["qs_vs_dyn_non_positive_terms"]
    ev = {e["run_id"]: e for e in mixed["read"]("evaluation.csv")}
    for b in ("B0", "B3"):
        e = ev[ids[b]]
        assert e["qs_vs_dyn_pct"] == "" and e["qs_vs_dyn_pct_diagnostic_invalid_run"] == ""   # no percentage at all
        assert float(e["qs_E_J_diagnostic"]) == -250.0 and float(e["qs_vs_dyn_e_qs_Wh_per_km"]) < 0   # raw values
        assert e["qs_vs_dyn_non_positive_term"].startswith("e_QS") and "nan" not in e["qs_vs_dyn_pct"].lower()


def test_valid_dynamic_energy_is_kept_when_only_the_qs_comparison_is_not_evaluable(mixed):
    for tag in ("QSNEG", "PEX"):                                             # AMB-29(c) and AMB-29(d) on the QS check
        r, ids = mixed["rows"][tag], mixed["conds"][tag].run_ids
        assert r["status"] == checks.COMPARABLE and r["dynamic_valid_pair"] is True and r["paired_endpoint_eligible"]
        roles = {x["run_id"]: x["energy_role"] for x in mixed["read"]("energy_roles.csv")}
        assert roles[ids["B0"]] == roles[ids["B3"]] == checks.CONFIRMATORY, tag
        assert r["b0_failed_8_2"] == r["b3_failed_8_2"] == ""                 # protocol 8.2 still applied and passed
    br = {b["motor"]: b for b in mixed["read"]("qs_dynamic_branch_outcomes.csv")}
    assert br["M0"]["outcome"] == "INCONCLUSIVE"                             # the QS criterion, not the dynamic result


def test_amb29d_evaluation_exceptions_are_kept_without_retry_or_replacement(mixed):
    ids = {k: c.run_ids for k, c in mixed["conds"].items()}
    scheduled = sorted(i for c in mixed["conds"].values() for i in c.run_ids.values())
    assert set(mixed["calls"].values()) == {1}                               # every attempted run exactly once
    assert ids["CEX"]["B0"] not in mixed["calls"] and ids["PF"]["B3"] not in mixed["calls"]
    runs = mixed["read"]("runs.csv")
    assert sorted(r["run_id"] for r in runs) == scheduled                    # no substitute or extra run ID
    assert {p.name.split(".")[0] for p in (mixed["out"] / "traces").iterdir()} <= set(scheduled)
    err = mixed["read"]("errors.csv")
    exc = [e for e in err if e["run_id"] == ids["EXC"]["B3"]]
    assert len(exc) == 1 and "injected evaluation failure" in exc[0]["traceback"]
    assert (mixed["out"] / "traces" / f"{ids['EXC']['B3']}.npz").is_file()   # its trace is kept
    for tag, msg in (("PEX", "injected pair evaluation failure"), ("CEX", "injected condition failure")):
        e = [x for x in err if x["condition_id"] == mixed["conds"][tag].cid]
        assert len(e) == 1 and msg in e[0]["traceback"], tag
        assert ids[tag]["B0"] in e[0]["run_ids"] and ids[tag]["B3"] in e[0]["run_ids"]   # run IDs preserved
    inv = mixed["manifest"]["record_invariant"]
    assert inv["condition_ids_match"] and inv["run_ids_match"] and inv["scheduled_runs"] == inv["run_rows"] == 16
    assert not any(e["condition_id"] == "RECORD-INVARIANT" for e in err)


def test_planned_run_and_feasibility_denominators_stay_fixed(mixed):
    t = {(a["motor"], a["set"]): a for a in mixed["read"]("feasibility_accounting.csv")}[("ALL", "ALL")]
    assert sum(int(t[f"status_{s}"]) for s in checks.STATUSES) == int(t["planned_conditions"]) == 8
    assert sum(int(t[f"runs_{k}"]) for k in checks.ENERGY_ROLES) == int(t["planned_runs"]) == 16
    assert int(t["paired_endpoint_eligible_conditions"]) + int(t["excluded_from_paired_endpoint_conditions"]) == 8
    a = {(x["motor"], x["set"]): x for x in mixed["read"]("qs_dynamic_accounting.csv")}[("M0", "ALL")]
    elig = ("qs_eligible_pairs", "qs_ineligible_pairs", "not_applicable_profile_unavailable", "qs_eligibility_unknown")
    assert sum(int(a[k]) for k in elig) == int(a["planned_pairs"]) == 8
    status_cols = ("qs_check_pass", "qs_check_fail", "qs_check_reported_only", "qs_ineligible_pairs",
                   "not_applicable_profile_unavailable", "not_evaluable_run_missing", "not_evaluable_qs_undefined",
                   "not_evaluable_condition_error", "not_evaluable_run_invalid")
    assert sum(int(a[k]) for k in status_cols) == 8
    assert len(mixed["read"]("energy_roles.csv")) == 16 and len(mixed["read"]("conditions.csv")) == 8
    assert mixed["manifest"]["denominator"]["total"] == 8 and mixed["manifest"]["n_runs_scheduled"] == 16
    br = {b["motor"]: b for b in mixed["read"]("qs_dynamic_branch_outcomes.csv")}
    assert set(br) == {"M0", "M1", "M2"} and br["M0"]["planned_pairs"] == "8"   # every branch reported
    assert br["M0"]["outcome"] == br["M1"]["outcome"] == "INCONCLUSIVE" and br["M2"]["outcome"] == "REPORTED_ONLY"
    v = mixed["manifest"]["h3_verdict_eligibility"]
    assert v["verdict_without_energy"] == "INCONCLUSIVE" and len(v["nominal_missing_evidence"]) == 6


# ============================================================ amendment candidate and fail-closed campaign mode
def test_rev5_candidate_is_a_draft_with_full_parent_hashes_and_matches_the_code():
    assert campaign.DRAFT_AMENDMENT_2.name == "03_protocol_v1_amendment_2_rev5_CANDIDATE.md"
    r = campaign.read_amendment(campaign.DRAFT_AMENDMENT_2, campaign.IMPLEMENTED_2, {})
    assert r["exists"] and not r["errors"] and r["status"] == "DRAFT", r["errors"]
    text = campaign.DRAFT_AMENDMENT_2.read_text(encoding="utf-8")
    assert "DRAFT — NOT APPROVED FOR RELEASE" in text.splitlines()[2]
    for h in (frozen.FROZEN_SHA256[frozen.PROTOCOL], campaign.AMENDMENT_1_SHA256,
              "c726560d1e87036cbd94fe58724cafdc1e4746647f6cfacbb320f3e14ed143ab",
              "fdaf193de510488733f0e0899d50def86cbeafabdbecdd3bc7a144099b6f492c"):
        assert h in text
    assert frozen.sha256(campaign.PILOT_DIR / "03_protocol_v1_amendment_2_rev4_CANDIDATE.md") == \
        "c726560d1e87036cbd94fe58724cafdc1e4746647f6cfacbb320f3e14ed143ab"
    for k in ("AMB_29_eligible_run_missing", "AMB_29_qs_energy_undefined", "AMB_29_condition_error",
              "AMB_30_branch_scope", "AMB_32_not_supported_needs_all_nominal_cells"):
        v = campaign.IMPLEMENTED_2[k]
        assert "owner ruling 2026-10-28" in v and "proposed" not in v and "owner to confirm" not in v, k
    assert checks.QS_DYN_MAX_PCT == 1.0 and campaign.IMPLEMENTED_2["planned_runs"]["total"] == 170   # unchanged


def test_campaign_execution_stays_blocked_without_a_separate_authorization(tmp_path, monkeypatch):
    assert not campaign.CAMPAIGN_AUTHORIZATION.exists()
    assert any("no campaign authorisation record" in b for b in campaign.preconditions("campaign"))
    text = campaign.DRAFT_AMENDMENT_2.read_text(encoding="utf-8").replace('"status": "DRAFT"', '"status": "APPROVED"')
    a2, ap = tmp_path / "a2.md", tmp_path / "ap2.json"                    # amendment 2 issued and approved ...
    a2.write_text(text, encoding="utf-8")
    ap.write_text(json.dumps(dict(approved_by="owner", date="2026-11-01", amendment_sha256=frozen.sha256(a2))),
                  encoding="utf-8")
    monkeypatch.setattr(campaign, "ISSUED_AMENDMENT_2", a2)
    monkeypatch.setattr(campaign, "APPROVAL_RECORD_2", ap)
    b = campaign.preconditions("campaign")
    assert not any("amendment 2" in x for x in b), b
    assert any("no campaign authorisation record" in x for x in b)        # ... still needs the owner's authorisation
    src = inspect.getsource(campaign.run_campaign)                          # refusal precedes any execution
    assert src.index("raise CampaignBlocked(blockers)") < src.index("execute_schedule(")
    code = "\n".join(p.read_text(encoding="utf-8") for p in (frozen.PILOT / "code").rglob("*.py")
                     if "tests" not in p.parts)
    assert "CAMPAIGN_AUTHORIZATION.write" not in code and "campaign_authorization.json\").write" not in code
    assert not campaign.CAMPAIGN_AUTHORIZATION.exists()
