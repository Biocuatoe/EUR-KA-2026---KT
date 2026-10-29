"""Owner ruling I-1 (2026-10-28) and the fix of review finding V6-1, rev10 (amendment 2 candidate rev7). Protocol
semantics only. No test computes, reports or targets an energy difference between arms; synthetic numbers in pure-rule
tests are not run energies."""

import csv
import itertools
import json
import re
import shutil
import subprocess
import sys

import numpy as np
import pytest

from r4h3 import campaign, checks, config, evaluator, frozen
from r4h3 import task as taskmod
from r4h3.closedloop import fixed_gain

NA, NA_PROFILE = checks.QS_NA_INFEASIBLE, checks.QS_NA_PROFILE
NOT_EVALUABLE = checks.PAIR_STATUS_CLASSES["NOT_EVALUABLE"]
CODE = frozen.PILOT / "code"
_ids = itertools.count(1)


def _r(set_, limits, qs, motor="M0", **kw):
    """One condition row; qs is the pair's QS-vs-dynamic status, kw may add the condition status."""
    return dict(motor=motor, set=set_, limits=limits, condition_id=f"I1-{set_}-{motor}-{limits}-{next(_ids)}",
                qs_vs_dyn_pair_status=qs, **kw)


def _nom(s_r1="PASS", s_eve="PASS", motor="M0", **kw):
    return [_r("NOM", "L-R1", s_r1, motor, **kw), _r("NOM", "L-EVE", s_eve, motor, **kw)]


OTHERS = [_r("P3", "L-R1", "PASS"), _r("INS", "L-R1", "PASS"), _r("INS", "L-EVE", "PASS"), _r("CNV", "L-EVE", "PASS"),
          _r("SEN", "L-EVE", "PASS"), _r("P3", "L-EVE", NA), _r("SEN", "L-EVE", NA_PROFILE)]


def _out(rows, motor="M0"):
    return checks.branch_qs_dynamic_outcome(motor, rows, [r["condition_id"] for r in rows if r["motor"] == motor])


def _verdict_rows(qs=None, status=None):
    """Condition rows of a complete record (6 nominal cells, 32 draws per M0/M1); qs/status override nominal cells."""
    rows = [dict(set="NOM", motor=m, limits=lim, status=(status or {}).get((m, lim), checks.COMPARABLE),
                 qs_vs_dyn_pair_status=(qs or {}).get((m, lim), "PASS" if m != "M2" else "REPORTED_ONLY"))
            for m, lim in checks.H3_NOMINAL_CELLS]
    rows += [dict(set="SEN", motor=m, limits="L-EVE", status=checks.COMPARABLE) for m in ("M0", "M1") for _ in range(32)]
    return rows


QS_OK = [dict(motor="M0", outcome="PASS"), dict(motor="M1", outcome="PASS"), dict(motor="M2", outcome="REPORTED_ONLY")]


# ============================================================ owner ruling I-1
def test_i1_every_required_nominal_s2_cell_passes():
    out = _out(_nom() + OTHERS)
    assert out["outcome"] == "PASS" and out["n_PASS_nominal"] == 2 == out["n_required_nominal_cells"]
    assert out["required_nominal_cells"] == "M0/L-R1,M0/L-EVE" and out["nominal_evidence_missing"] == ""
    v = checks.h3_verdict_eligibility(_verdict_rows(), QS_OK)
    assert v["supported_possible"] and v["not_supported_possible"]
    assert v["qs_vs_dynamic_nominal_cells"] == {"M0/L-R1": "PASS", "M0/L-EVE": "PASS", "M1/L-R1": "PASS",
                                                "M1/L-EVE": "PASS"}                    # M2 is reported only


def test_i1_one_nominal_cell_fails_while_the_others_pass():
    for nom in (_nom("FAIL", "PASS"), _nom("PASS", "FAIL")):
        out = _out(nom + OTHERS)
        assert out["outcome"] == "INCONCLUSIVE" and out["fail_by_set"] == "NOM:1" and "failed" in out["reason"]
        assert out["n_PASS_nominal"] == 1                                                # frozen consequence kept
    v = checks.h3_verdict_eligibility(_verdict_rows(qs={("M1", "L-EVE"): "FAIL"}), QS_OK)
    assert not v["supported_possible"] and not v["not_supported_possible"]
    assert any("M1/L-EVE=FAIL" in r and "I-1" in r for r in v["reasons"])


def test_i1_one_nominal_cell_missing():
    rows = _nom() + OTHERS
    out = checks.branch_qs_dynamic_outcome("M0", rows[1:], [r["condition_id"] for r in rows])  # L-R1 row dropped
    assert out["outcome"] == "INCONCLUSIVE" and out["nominal_L-R1"] == checks.NOT_IN_RECORD
    assert "I-1" in out["reason"] and out["planned_pairs_missing_from_record"]
    assert _out(_nom() + [_r("NOM", "L-EVE", "PASS")] + OTHERS)["nominal_L-EVE"] == checks.DUPLICATE_IN_RECORD
    rows = [r for r in _verdict_rows() if (r["set"], r["motor"], r["limits"]) != ("NOM", "M0", "L-R1")]
    v = checks.h3_verdict_eligibility(rows, QS_OK)
    assert v["qs_vs_dynamic_nominal_cells"]["M0/L-R1"] == checks.NOT_IN_RECORD
    assert not v["supported_possible"] and not v["not_supported_possible"]


def test_i1_one_nominal_cell_invalid_or_unevaluable():
    for s in NOT_EVALUABLE:
        out = _out(_nom("PASS", s) + OTHERS)
        assert out["outcome"] == "INCONCLUSIVE" and f"M0/L-EVE {s}" in out["nominal_evidence_missing"].replace("=", " "), s
        v = checks.h3_verdict_eligibility(_verdict_rows(qs={("M0", "L-EVE"): s}), QS_OK)
        assert not v["supported_possible"] and not v["not_supported_possible"], s
    out = _out([_r("NOM", "L-R1", "PASS"), _r("NOM", "L-EVE", checks.QS_RUN_INVALID, status="INVALID_COMPARISON")]
               + OTHERS)
    assert out["outcome"] == "INCONCLUSIVE"
    # an invalid cell cannot count as PASS even with a PASS label (the classification raised: condition ERROR)
    out = _out([_r("NOM", "L-R1", "PASS", status=checks.COMPARABLE), _r("NOM", "L-EVE", "PASS", status="ERROR")]
               + OTHERS)
    assert out["outcome"] == "INCONCLUSIVE" and "condition ERROR" in out["nominal_evidence_missing"]
    assert _out(_nom(status=checks.COMPARABLE) + OTHERS)["outcome"] == "PASS"


def test_i1_one_nominal_cell_not_applicable_and_qs_and_dynamic_feasibility_stay_distinct(tmp_path, monkeypatch):
    for s in (NA, NA_PROFILE):
        out = _out(_nom("PASS", s) + OTHERS)
        assert out["outcome"] == "INCONCLUSIVE" and "owner ruling I-1" in out["reason"], s
    # the QS-infeasible nominal cell is still COMPARABLE: the ruling never makes it dynamically infeasible
    v = checks.h3_verdict_eligibility(_verdict_rows(qs={("M0", "L-R1"): NA}), QS_OK)
    assert v["nominal_cells"]["M0/L-R1"] == checks.COMPARABLE and v["nominal_missing_evidence"] == []
    assert not v["supported_possible"] and not v["not_supported_possible"]              # but the QS criterion blocks
    speeds = np.array([0, 0, 0.5, 1, 1.5, 2, 2, 2, 2, 2, 1.5, 1, 1, 1, 1, 1, 1.5, 2, 2, 2, 2, 2, 1.5, 1, 0.5, 0, 0, 0], float)
    task = taskmod.task_from_samples("GENTLE", np.arange(len(speeds), dtype=float), speeds)
    design = campaign.plan_design(task, "L-R1", config.params_for("P1"), config.motor_model("M0"))
    real = campaign.checks.qs_energy
    monkeypatch.setattr(campaign.checks, "qs_energy", lambda plant, t, vv: dict(
        real(plant, t, vv), feasible=False, n_infeasible_pieces=1,
        infeasible_pieces=[dict(piece=3, t0_s=3.0, t1_s=4.0, v0_ms=1.0, v1_ms=1.5)]))
    cid = "DEV-V10-I1NA-GENTLE-M0-LR1-P1-dt1ms"
    c = campaign.Condition(cid, "NOM", "GENTLE", "M0", "L-R1", "P1", 1e-3, None,
                           {b: cid.replace("-dt", f"-{b}-dt") for b in ("B0", "B3")})
    r = campaign.run_condition(c, task, design, config.params_for("P1"), 1.0, config.LIMITS["L-R1"],
                               config.motor_model("M0"), evaluator.motor_spec_from_protocol("M0", frozen.M1_CURVE),
                               fixed_gain(config.params_for("P1")), tmp_path)
    assert r["qs_vs_dyn_pair_status"] == NA and r["status"] == checks.COMPARABLE and r["dynamic_valid_pair"] is True


def test_i1_an_s1_pass_never_substitutes_for_missing_or_failed_nominal_s2_evidence():
    ins = [_r("INS", "L-R1", "PASS"), _r("INS", "L-EVE", "PASS")]
    for nom in ([], _nom("FAIL", "FAIL"), _nom("PASS", "FAIL"), _nom(NA, NA), _nom("PASS", NA_PROFILE),
                _nom(checks.QS_CONDITION_ERROR, "PASS")):
        out = _out(nom + ins)
        assert out["outcome"] == "INCONCLUSIVE" and out["n_PASS_other_sets"] == 2, nom
    assert "cannot substitute" in _out(ins)["reason"]


def test_i1_no_branch_passes_by_omission_or_by_treating_not_applicable_as_pass():
    cells = (*checks.PAIR_QS_STATUSES, None)                                             # None: no row in the record
    for a, b in itertools.product(cells, cells):
        nom = ([_r("NOM", "L-R1", a)] if a else []) + ([_r("NOM", "L-EVE", b)] if b else [])
        out = checks.branch_qs_dynamic_outcome("M0", nom + OTHERS)
        assert (out["outcome"] == "PASS") == (a == b == "PASS"), (a, b)
    for qs in itertools.product(("PASS", NA, NA_PROFILE, "FAIL", checks.QS_RUN_INVALID, None), repeat=2):
        q = {("M0", "L-R1"): qs[0], ("M1", "L-EVE"): qs[1]}
        v = checks.h3_verdict_eligibility(_verdict_rows(qs=q), QS_OK)                    # branch outcomes forged PASS
        assert v["supported_possible"] == v["not_supported_possible"] == (qs == ("PASS", "PASS")), qs
    m2 = checks.branch_qs_dynamic_outcome("M2", [_r("NOM", "L-R1", NA, "M2")])
    assert m2["outcome"] == "REPORTED_ONLY"                                              # M2 stays reported only


def test_i1_is_in_the_reporting_layer(tmp_path):
    v = np.array([0, 0, 0.5, 1, 1.5, 2, 2, 2, 2, 2, 1.5, 1, 1, 1, 1, 1, 1.5, 2, 2, 2, 2, 2, 1.5, 1, 0.5, 0, 0, 0], float)
    task = taskmod.task_from_samples("GENTLE", np.arange(len(v), dtype=float), v)
    cid = "DEV-V10-I1REP-GENTLE-M0-LR1-P1-dt1ms"
    c = campaign.Condition(cid, "NOM", "GENTLE", "M0", "L-R1", "P1", 1e-3, None,
                           {b: cid.replace("-dt", f"-{b}-dt") for b in ("B0", "B3")})
    out = tmp_path / "o"
    rows = campaign.execute_schedule([c], lambda n: task, out)
    br = {b["motor"]: b for b in csv.DictReader((out / "qs_dynamic_branch_outcomes.csv").open(encoding="utf-8"))}
    assert br["M0"]["required_nominal_cells"] == "M0/L-R1,M0/L-EVE" and br["M0"]["n_required_nominal_cells"] == "2"
    assert br["M0"]["nominal_L-EVE"] == checks.NOT_IN_RECORD and br["M0"]["outcome"] == "INCONCLUSIVE"
    assert br["M0"]["nominal_L-R1"] == rows[0]["qs_vs_dyn_pair_status"]
    h3 = json.loads((out / "h3_verdict_eligibility.json").read_text(encoding="utf-8"))
    assert h3["qs_vs_dynamic_nominal_cells"]["M0/L-R1"] == rows[0]["qs_vs_dyn_pair_status"]
    assert h3["qs_vs_dynamic_nominal_cells"]["M1/L-EVE"] == checks.NOT_IN_RECORD
    assert h3["verdict_without_energy"] == "INCONCLUSIVE"
    assert campaign.IMPLEMENTED_2["I_1_required_nominal_cells"].startswith("owner ruling 2026-10-28")
    assert "individually PASS" in campaign.IMPLEMENTED_2["I_1_required_nominal_cells"]


# ============================================================ V6-1: start-up failures of the separate recomputation
def test_v6_1_a_start_up_failure_of_the_separate_script_exits_4(tmp_path):
    lone = tmp_path / "lone"
    lone.mkdir()
    shutil.copy2(CODE / "recompute_from_traces.py", lone / "recompute_from_traces.py")   # no r4h3 package beside it
    res = subprocess.run([sys.executable, "-I", "-B", str(lone / "recompute_from_traces.py"), str(tmp_path)],
                         capture_output=True, text=True)
    assert res.returncode == 4 and "ModuleNotFoundError" in res.stderr                   # was exit 1, a "result"
    res = subprocess.run([sys.executable, "-I", "-B", str(CODE / "recompute_from_traces.py")], capture_output=True,
                         text=True)
    assert res.returncode == 4 and "IndexError" in res.stderr                            # no arguments


def _gentle_cond(tag):
    cid = f"DEV-V10-{tag}-GENTLE-M0-LR1-P1-dt1ms"
    return campaign.Condition(cid, "DEV", "GENTLE", "M0", "L-R1", "P1", 1e-3, None,
                              {b: cid.replace("-dt", f"-{b}-dt") for b in ("B0", "B3")})


def _run_with(monkeypatch, tmp_path, tag, fake):
    v = np.array([0, 0, 0.5, 1, 1.5, 2, 2, 2, 2, 2, 1.5, 1, 1, 1, 1, 1, 1.5, 2, 2, 2, 2, 2, 1.5, 1, 0.5, 0, 0, 0], float)
    task = taskmod.task_from_samples("GENTLE", np.arange(len(v), dtype=float), v)
    monkeypatch.setattr(campaign.subprocess, "run", fake)
    c = _gentle_cond(tag)
    out = tmp_path / tag
    rows = campaign.execute_schedule([c], lambda n: task, out)
    monkeypatch.undo()
    err = list(csv.DictReader((out / "errors.csv").open(encoding="utf-8")))
    return c, out, rows, err


@pytest.mark.parametrize("case", ["exit4", "exit0_no_output", "launch", "partial_output"])
def test_v6_1_every_start_up_or_output_failure_is_in_the_ledger_with_run_ids(tmp_path, monkeypatch, case):
    real = subprocess.run

    def fake(args, **k):
        if case == "launch":
            raise OSError("injected: cannot start the interpreter")
        if case == "exit4":
            return subprocess.CompletedProcess(args, 4, "", "Traceback (most recent call last):\n"
                                                            "ModuleNotFoundError: injected import failure")
        if case == "exit0_no_output":
            return subprocess.CompletedProcess(args, 0, "", "")
        res = real(args, **k)                                                            # partial_output: drop one run
        p = __import__("pathlib").Path(args[-1]) / "recomputation_independent.csv"
        lines = p.read_text(encoding="utf-8").splitlines()
        p.write_text("\n".join(lines[:1] + [x for x in lines[1:] if "-B3-" not in x]) + "\n", encoding="utf-8")
        return res
    c, out, rows, err = _run_with(monkeypatch, tmp_path, "V61" + case.replace("_", "").upper(), fake)
    head = [e for e in err if e["condition_id"] == "SEPARATE-RECOMPUTATION"]
    assert len(head) == 1 and head[0]["diagnostic_path"] == "recomputation_independent_process.log", head
    stage = {"exit4": "exit 4", "exit0_no_output": "exit 0 without its output file", "launch": "launch",
             "partial_output": "1 executed run(s) missing from its output"}[case]
    assert head[0]["stage"] == stage
    per_run = {e["run_id"]: e for e in err if e["run_id"] and e["stage"].startswith("separate recomputation")}
    expect = {c.run_ids["B3"]} if case == "partial_output" else set(c.run_ids.values())
    assert set(per_run) == expect and all(e["diagnostic_path"] for e in per_run.values())
    assert all(e["condition_id"] == c.cid for e in per_run.values())
    log = (out / "recomputation_independent_process.log").read_text(encoding="utf-8")
    assert log.startswith("exit ") and ("injected" in log or case in ("exit0_no_output", "partial_output"))
    assert rows[0]["status"] != checks.COMPARABLE                                        # fail-closed
    man = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert man["separate_recomputation"]["problem"] == stage


# ============================================================ owner decisions, candidate and review status
def test_open_owner_decisions_block_campaign_and_readiness(monkeypatch):
    assert campaign.OWNER_DECISIONS_OPEN == ["I-2", "I-3", "I-4", "I-5", "I-6"]
    for mode in ("readiness", "campaign"):
        b = " | ".join(campaign.preconditions(mode))
        assert all(f"owner decision open: {k}" in b for k in campaign.OWNER_DECISIONS_OPEN), mode
    monkeypatch.setattr(campaign, "OWNER_DECISIONS_OPEN", [])
    assert "owner decision open" not in " | ".join(campaign.preconditions("readiness"))
    rv = json.loads(campaign.REVIEW_STATUS.read_text(encoding="utf-8"))
    assert [d.split(":")[0] for d in rv["open_owner_decisions"]] == ["I-2", "I-3", "I-4", "I-5", "I-6"]
    for k in ("I-2", "I-3", "I-4", "I-5", "I-6"):                                         # labelled provisional
        assert re.search(rf"[Pp]rovisional reading {k}\b", json.dumps(campaign.IMPLEMENTED_2)), k


def test_rev7_candidate_is_a_non_issuable_draft_and_rev6_is_unchanged():
    assert frozen.sha256(campaign.PILOT_DIR / "03_protocol_v1_amendment_2_rev6_CANDIDATE.md") == \
        "0dcb767e97e19f40c00735d9efaecf8d21c396c23952b70e60ccb21a3f711e1f"
    assert campaign.DRAFT_AMENDMENT_2.name == "03_protocol_v1_amendment_2_rev7_CANDIDATE.md"
    r = campaign.read_amendment(campaign.DRAFT_AMENDMENT_2, campaign.IMPLEMENTED_2, {})
    assert r["exists"] and not r["errors"] and r["status"] == "DRAFT", r["errors"]
    text = campaign.DRAFT_AMENDMENT_2.read_text(encoding="utf-8")
    assert "DRAFT — NOT APPROVED FOR RELEASE" in text.splitlines()[2] and "NOT ISSUABLE" in text.splitlines()[2]
    for h in (frozen.FROZEN_SHA256[frozen.PROTOCOL], campaign.AMENDMENT_1_SHA256,
              "0dcb767e97e19f40c00735d9efaecf8d21c396c23952b70e60ccb21a3f711e1f"):
        assert h in text
    assert r["decisions"]["owner_decisions_open"] == ["I-2", "I-3", "I-4", "I-5", "I-6"]
    assert "|\n\n|" not in text                                                          # V6-2: no split table
