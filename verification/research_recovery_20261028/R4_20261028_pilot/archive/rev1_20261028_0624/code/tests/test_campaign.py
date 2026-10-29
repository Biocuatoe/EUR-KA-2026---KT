"""Campaign infrastructure: schedule (protocol 10.6), amendment reader, guards, and the executor on toy tasks
with development run IDs (no S1/S2 run, no official ID, no campaign mode)."""

import csv
import json
import subprocess
import sys

import numpy as np
import pytest

from r4h3 import campaign, checks, config, frozen
from r4h3 import task as taskmod

CODE = frozen.PILOT / "code"


# ---- schedule
def test_schedule_is_the_170_run_plan_of_protocol_10_6():
    conds = campaign.build_schedule()
    v = campaign.validate_schedule(conds)
    assert v["passed"], {k: x for k, x in v["checks"].items() if not x}
    assert v["n_runs"] == 170 and v["counts_per_set"] == {"NOM": 12, "P3": 12, "INS": 12, "CNV": 6, "SEN": 128}
    ids = [r["run_id"] for r in campaign.schedule_rows(conds)]
    assert "R4H3-NOM-S2-M0-LR1-P1-B0-dt1ms" in ids and "R4H3-CNV-S2-M2-LEVE-P1-B3-dt0.5ms" in ids
    assert "R4H3-SEN-D32-S2-M1-LEVE-P1-B3-dt1ms" in ids and "R4H3-P3-S2-M1-LEVE-P3-B0-dt1ms" in ids


def test_schedule_validation_detects_a_broken_plan():
    conds = campaign.build_schedule()
    assert not campaign.validate_schedule(conds[:-1])["passed"]                       # 168 runs
    bad = conds[:]
    bad[0] = campaign._cond("NOM", "UDDS", "M0", "L-R1", "P1", 1e-3)
    assert not campaign.validate_schedule(bad)["passed"]


def test_smoke_runs_are_development_only():
    smoke = campaign.smoke_run_ids()
    assert len(smoke) == 2 and all(s.startswith("H3-slice-") for s in smoke)
    ids = {r["run_id"] for r in campaign.schedule_rows(campaign.build_schedule())}
    assert not ids & set(smoke)


def test_planner_jobs_are_not_runs():
    jobs = campaign.planner_jobs(campaign.build_schedule())
    assert len(jobs) == 6 + 6 + 64 + 6                 # S2 P1, S1 P1, 32 draws x M0/M1, S2 fine grid
    assert not any(j["counts_toward_170"] for j in jobs)


# ---- amendment reader
def _amendment(tmp_path, block: dict, raw=None):
    p = tmp_path / "a.md"
    body = raw if raw is not None else json.dumps(block, indent=1)
    p.write_text(f"# x\n\n{campaign.BLOCK_MARK}\n```json\n{body}\n```\n", encoding="utf-8")
    return p


def _block(**over):
    b = dict(status="DRAFT", **campaign.IMPLEMENTED, **{k: None for k in campaign.OPEN_PARAMETERS})
    b.update(over)
    return json.loads(json.dumps(b))


def test_reader_reports_open_items_and_never_overrides(tmp_path):
    r = campaign.read_amendment(_amendment(tmp_path, _block()))
    assert not r["errors"] and set(r["open"]) == set(campaign.OPEN_PARAMETERS) and r["status"] == "DRAFT"
    r = campaign.read_amendment(_amendment(tmp_path, _block(D3_timing_tolerance_s=0.5)))
    assert any("does not override" in e for e in r["errors"])
    r = campaign.read_amendment(_amendment(tmp_path, _block(threshold_pct=-0.5)))
    assert any("unknown key" in e for e in r["errors"])
    r = campaign.read_amendment(_amendment(tmp_path, _block(AMB_14_sensitivity_gain_basis="tuned_per_draw")))
    assert any("AMB_14" in e for e in r["errors"])
    r = campaign.read_amendment(_amendment(tmp_path, _block(AMB_15_campaign_directory="../elsewhere")))
    assert any("AMB_15" in e for e in r["errors"])
    r = campaign.read_amendment(_amendment(tmp_path, {}, raw="{not json"))
    assert r["errors"]
    r = campaign.read_amendment(_amendment(tmp_path, _block(status="FROZEN")))
    assert any("status" in e for e in r["errors"])


def test_draft_amendment_parses_and_stays_a_draft():
    r = campaign.read_amendment(campaign.DRAFT_AMENDMENT)
    assert r["exists"] and not r["errors"], r["errors"]
    assert r["status"] == "DRAFT" and set(r["open"]) == set(campaign.OPEN_PARAMETERS)
    assert "DRAFT — NOT APPROVED FOR CAMPAIGN EXECUTION" in campaign.DRAFT_AMENDMENT.read_text(encoding="utf-8")


def test_preconditions_block_the_campaign_now():
    b = campaign.preconditions("readiness")
    assert any("no issued amendment" in x for x in b)
    assert not campaign.ISSUED_AMENDMENT.exists()
    c = campaign.preconditions("campaign")
    assert any("fresh directory" in x for x in c) and any("gate record" in x for x in c)


# ---- guards
def test_official_ids_are_refused_outside_campaign_mode(tmp_path):
    c = campaign.build_schedule()[0]
    with pytest.raises(campaign.CampaignBlocked):
        campaign.execute_schedule([c], taskmod.load_task, tmp_path / "x")
    assert not (tmp_path / "x").exists()


def test_missing_open_decisions_refuse_before_any_run(tmp_path):
    p3 = _dev("TOY2", "M0", "L-R1", "P3")
    with pytest.raises(campaign.CampaignBlocked, match="AMB-24"):
        campaign.execute_schedule([p3], _loader, tmp_path / "a")
    sen = campaign.Condition("DEV-SEN", "DEV", "TOY2", "M0", "L-EVE", "P1", 1e-3, 1, {"B0": "DEV-S0", "B3": "DEV-S3"})
    with pytest.raises(campaign.CampaignBlocked, match="AMB-14"):
        campaign.execute_schedule([sen], _loader, tmp_path / "b")
    assert not (tmp_path / "a").exists() and not (tmp_path / "b").exists()


# ---- executor on toy tasks
def _fast_task():
    """6 m in 4 s with |a| <= 2 m/s^2 and v <= 2 m/s: the planner's grid cannot meet T_k (time-infeasible)."""
    t = np.arange(0.0, 8.0)
    v = np.array([0, 0, 2, 2, 2, 0, 0, 0], float)
    return taskmod.task_from_samples("FAST", t, v)


TOY = {}


def _loader(name):
    if not TOY:
        t = np.arange(0.0, 17.0)
        v = np.array([0, 0, 1, 2, 1, 1, 1, 0, 0, 0, 1, 2, 1, 1, 1, 0, 0], float)
        TOY["TOY2"] = taskmod.task_from_samples("TOY2", t, v)
        TOY["FAST"] = _fast_task()
    return TOY[name]


def _dev(cycle, motor, limits, pstate, dt=1e-3, tag=""):
    cid = f"DEV{tag}-{cycle}-{motor}-{limits.replace('-', '')}-{pstate}-dt{dt * 1e3:g}ms"
    return campaign.Condition(cid, "DEV", cycle, motor, limits, pstate, dt, None,
                              {b: cid.replace("-dt", f"-{b}-dt") for b in ("B0", "B3")})


@pytest.fixture(scope="module")
def toy_run(tmp_path_factory):
    out = tmp_path_factory.mktemp("exec") / "out"
    conds = [_dev("TOY2", "M0", "L-R1", "P1"), _dev("TOY2", "M1", "L-EVE", "P3"), _dev("FAST", "M0", "L-R1", "P1"),
             _dev("TOY2", "M0", "L-R1", "P1", dt=5e-4)]
    rows = campaign.execute_schedule(conds, _loader, out, p3_rule="qs_step_feasibility_on_P3",
                                     grid_keys=[("TOY2", "M0", "L-R1")])
    return out, conds, rows


def test_every_scheduled_run_has_a_row_and_the_denominator_is_kept(toy_run):
    out, conds, rows = toy_run
    runs = list(csv.DictReader((out / "runs.csv").open(encoding="utf-8")))
    assert {r["run_id"] for r in runs} == {i for c in conds for i in c.run_ids.values()}
    man = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert man["denominator"]["total"] == len(conds) == len(rows)
    assert man["n_runs_scheduled"] == 8
    for c in conds:
        assert (out / "conditions" / f"{c.cid}.json").is_file()
    assert (out / "zz_post_run_sha256.csv").is_file() and (out / "errors.csv").is_file()


def test_time_infeasible_profile_is_unavailable_and_b0_still_runs(toy_run):
    out, conds, rows = toy_run
    fast = next(r for r in rows if r["cycle"] == "FAST")
    assert fast["status"] == "PROFILE_UNAVAILABLE" and fast["eco_status"] == "unavailable"
    runs = {r["run_id"]: r for r in csv.DictReader((out / "runs.csv").open(encoding="utf-8"))}
    c = next(c for c in conds if c.cycle == "FAST")
    assert runs[c.run_ids["B0"]]["executed"] == "True" and runs[c.run_ids["B3"]]["executed"] == "False"


def test_classification_is_reproduced_from_the_written_rows(toy_run):
    out, conds, rows = toy_run
    ev = {r["run_id"]: r for r in csv.DictReader((out / "evaluation.csv").open(encoding="utf-8"))}
    for r, c in zip(rows, conds):
        assert r["status"] in checks.STATUSES
        if r["status"] == "PROFILE_UNAVAILABLE":
            continue
        b0, b3 = ({k: (v == "True") if v in ("True", "False") else v for k, v in ev[c.run_ids[b]].items()}
                  for b in ("B0", "B3"))
        again = checks.classify_pair(b0, b3, eco_profile_ok=True, baseline_ok=True, pstate=c.pstate,
                                     b0_qs_feasible=r["b0_qs_feasible_on_eval_plant"],
                                     b3_qs_feasible=r["b3_qs_feasible_on_eval_plant"], p3_rule=r["p3_rule"] or None)
        assert again == r["status"]


def test_arms_share_gain_plant_state_and_initial_conditions(toy_run):
    out, conds, rows = toy_run
    for c in conds:
        metas = []
        for b in ("B0", "B3"):
            p = out / "traces" / f"{c.run_ids[b]}.spec.json"
            if p.is_file():
                metas.append(json.loads(p.read_text(encoding="utf-8")))
        if len(metas) == 2:
            a, b = metas
            assert a["meta"]["gain"] == b["meta"]["gain"] and a["meta"]["soh"] == b["meta"]["soh"]
            assert a["meta"]["initial_conditions"] == b["meta"]["initial_conditions"] == \
                {"v": 0.0, "T": 0.0, "V1": 0.0, "SoC": 0.8, "z": 0.0}
            assert a["spec"]["battery"] == b["spec"]["battery"] and a["spec"]["motor"] == b["spec"]["motor"]
            assert a["meta"]["gain"] == [float(x) for x in np.ravel(
                __import__("r4h3.closedloop", fromlist=["fixed_gain"]).fixed_gain(config.params_for("P1")))]


def test_half_ms_condition_is_traced_at_1ms_and_evaluated(toy_run):
    out, conds, rows = toy_run
    c = next(c for c in conds if c.dt_s == 5e-4)
    runs = {r["run_id"]: r for r in csv.DictReader((out / "runs.csv").open(encoding="utf-8"))}
    r = runs[c.run_ids["B0"]]
    assert float(r["dt_s"]) == 5e-4 and float(r["trace_dt_s"]) == 1e-3 and r["recompute_protocol_ok"] == "True"


def test_grid_convergence_job_is_written(toy_run):
    out, *_ = toy_run
    pc = list(csv.DictReader((out / "planner_checks.csv").open(encoding="utf-8")))
    assert len(pc) == 1 and "dS_found_pp" in pc[0]


def test_independent_recomputation_runs_as_a_separate_process(toy_run):
    out, *_ = toy_run
    res = subprocess.run([sys.executable, "-I", "-B", str(CODE / "recompute_from_traces.py"), str(out)],
                         capture_output=True, text=True, timeout=600)
    assert res.returncode == 0, res.stdout + res.stderr
    summ = json.loads((out / "recomputation_independent.json").read_text(encoding="utf-8"))
    assert summ["simulator_modules_imported"] == [] and summ["n_protocol_fail"] == 0 and summ["n_recomputed"] >= 5


def test_an_exception_is_recorded_not_retried(tmp_path, monkeypatch):
    calls = []
    real = campaign.run_arm

    def flaky(rid, branch, *a, **k):
        calls.append(rid)
        if branch == "B3":
            raise RuntimeError("injected failure")
        return real(rid, branch, *a, **k)

    monkeypatch.setattr(campaign, "run_arm", flaky)
    c = _dev("TOY2", "M0", "L-R1", "P1", tag="ERR")
    rows = campaign.execute_schedule([c], _loader, tmp_path / "e")
    assert rows[0]["status"] == "ERROR" and calls == [c.run_ids["B0"], c.run_ids["B3"]]
    err = list(csv.DictReader((tmp_path / "e" / "errors.csv").open(encoding="utf-8")))
    assert len(err) == 1 and "injected failure" in err[0]["traceback"]
    runs = list(csv.DictReader((tmp_path / "e" / "runs.csv").open(encoding="utf-8")))
    assert len(runs) == 2


def test_p3_profile_infeasible_on_the_evaluated_plant_is_run_and_classified(tmp_path):
    """D5: both arms are run and retained; under the QS rule the condition is infeasible, never a saving."""
    task = _loader("TOY2")
    mm = config.motor_model("M0")
    design = campaign.plan_design(task, "L-R1", config.params_for("P1"), mm)
    weak = config.params_for("P3").with_overrides(T_max=2.0)                  # evaluated plant cannot drive the profile
    from r4h3 import evaluator
    from r4h3.closedloop import fixed_gain
    c = _dev("TOY2", "M0", "L-R1", "P3", tag="WEAK")
    r = campaign.run_condition(c, task, design, weak, 0.8, config.LIMITS["L-R1"], mm,
                               evaluator.motor_spec_from_protocol("M0", frozen.M1_CURVE),
                               fixed_gain(config.params_for("P1")), tmp_path, p3_rule="qs_step_feasibility_on_P3")
    assert r["status"] == "BASELINE_INFEASIBLE_ON_P3"
    assert all(s["executed"] for s in r["_sims"])
    with pytest.raises(ValueError):
        checks.paired_delta(r["status"], {}, {})
