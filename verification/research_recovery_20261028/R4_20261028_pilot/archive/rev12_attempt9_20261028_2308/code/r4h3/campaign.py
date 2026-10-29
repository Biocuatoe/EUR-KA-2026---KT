"""H3 campaign: official schedule, amendment reader, preconditions and the per-condition executor
(protocol v1 8.1, 8.4, 9, 10; decisions D1-D5 of 03_protocol_v1_amendment_1_DRAFT.md).

    python -I -B code/run_campaign.py --build-config   write config/campaign_config_v1_DRAFT.json and the draw table
    python -I -B code/run_campaign.py --dry-run        plan validation only; executes no run

Design:
- The schedule is built from protocol 10.6 alone: 12 nominal S2 P1, 12 S2 P3, 12 S1 P1, 6 S2 0.5 ms and
  128 sensitivity runs = 170, each with a unique official run ID (prefix R4H3-). Planner (QS) jobs are listed
  separately and are not runs.
- D1-D5 are implemented in code (validator, checks.classify_pair, run_condition). The amendment's
  machine-readable block can only confirm them: a value that differs from what the code implements, or a key
  the reader does not know, is an error, never an override. Items the amendment leaves null stay open and block.
- run_campaign() refuses to start while preconditions("campaign") reports any blocker; it must run from a fresh
  campaign directory (protocol 10.1) named by the issued amendment. The executor functions are generic; tests
  drive them on toy tasks with development run IDs. Official IDs are refused unless official=True, which only
  run_campaign() passes.
- Every scheduled run gets a row, valid or not; exceptions go to errors.csv with the traceback and are never
  retried; non-finite runs keep their raw trace (protocol 10.4; D5).
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import platform
import re
import shutil
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from r4h3 import SCHEMA_VERSION, checks, config, evaluator, frozen, inputs, sensitivity

L = config.L
MOTORS = ("M0", "M1", "M2")
LIMITS = ("L-R1", "L-EVE")
BRANCHES = ("B0", "B3")
DT_NOMINAL, DT_CONV = 1e-3, 5e-4
PLANNED = {"NOM": 12, "P3": 12, "INS": 12, "CNV": 6, "SEN": 128}       # protocol 10.6
TOTAL_PLANNED = 170
OFFICIAL_PREFIX = "R4H3-"
GRID_COARSE, GRID_FINE = (config.ECO_DS, config.ECO_DV), (1.0, 0.05)    # protocol 5.2 and 9
# The development pilot holds the smoke test, the drafts and the candidate; the code is also run from the released copy
# in the campaign directory, so these paths name the pilot explicitly (rev2 release fix).
PILOT_DIR = frozen.RR / "R4_20261028_pilot"                        # SI-1: not relative to the code copy
DRAFT_AMENDMENT = PILOT_DIR / "03_protocol_v1_amendment_1_rev2_CANDIDATE.md"   # rev1 draft kept unchanged
# AMB-15 (owner decision 2026-10-28): the campaign release package and official outputs live in this fresh directory.
# The issued amendment and its approval record are placed in its release/ folder (the preflight directory is not
# written to). The file name follows the protocol header (03_R4_protocol_v1_amendment_N.md).
CAMPAIGN_DIR_NAME = "R4_20261028_campaign"
CAMPAIGN_DIR = frozen.RR / CAMPAIGN_DIR_NAME
ISSUED_AMENDMENT = CAMPAIGN_DIR / "release" / "03_R4_protocol_v1_amendment_1.md"
APPROVAL_RECORD = CAMPAIGN_DIR / "release" / "amendment_1_approval.json"
# Protocol approval is not campaign authorisation (owner, 2026-10-28). Campaign mode additionally requires this record,
# written by the owner after release; the code never writes it (VC-14).
CAMPAIGN_AUTHORIZATION = CAMPAIGN_DIR / "release" / "campaign_authorization.json"
# Amendment 2 (N-A2 ruling) is a second, separately issued amendment; amendment 1 is never edited.
AMENDMENT_1_SHA256 = "7720fed75bb678e47a229d00aff154e0aa14607c051f4a1163cc9bf67b6abee2"     # issued 2026-10-28 07:46
DRAFT_AMENDMENT_2 = PILOT_DIR / "03_protocol_v1_amendment_2_rev9_CANDIDATE.md"   # rev0-rev8 drafts kept unchanged
ISSUED_AMENDMENT_2 = CAMPAIGN_DIR / "release" / "03_R4_protocol_v1_amendment_2.md"
APPROVAL_RECORD_2 = CAMPAIGN_DIR / "release" / "amendment_2_approval.json"
AUTHORIZATION_SCOPE = "execute the 170-run H3 campaign of protocol v1 amendments 1 and 2"
def _gate_version(p: Path) -> int:
    return int(p.stem.rsplit("_v", 1)[1])


def latest_readiness_gate() -> Path:
    """Highest-numbered logs/readiness_gate_v<N>.json (earlier ones are kept; a gate is never overwritten)."""
    gates = sorted((frozen.PILOT / "logs").glob("readiness_gate_v*.json"), key=_gate_version)
    return gates[-1] if gates else frozen.PILOT / "logs" / "readiness_gate_v1.json"


def next_readiness_gate() -> Path:
    gates = sorted((frozen.PILOT / "logs").glob("readiness_gate_v*.json"), key=_gate_version)
    return frozen.PILOT / "logs" / f"readiness_gate_v{_gate_version(gates[-1]) + 1 if gates else 1}.json"


READINESS_GATE = latest_readiness_gate()
REVIEW_STATUS = frozen.PILOT / "config" / "code_review_status_v10.json"
CAMPAIGN_CONFIG = frozen.PILOT / "config" / "campaign_config_v12_DRAFT.json"
DRAWS_TABLE = frozen.PILOT / "config" / "sensitivity_draws_v1.csv"
SMOKE_DIR = PILOT_DIR / "outputs" / "slice_S1_M0_L-R1_P1"
BLOCK_MARK = "<!-- r4h3-amendment-block -->"


class CampaignBlocked(RuntimeError):
    pass


# --------------------------------------------------------------------------- schedule
@dataclass(frozen=True)
class Condition:
    cid: str
    set: str
    cycle: str
    motor: str
    limits: str
    pstate: str
    dt_s: float
    draw: int | None = None
    run_ids: dict = field(default_factory=dict, compare=False, hash=False)


def run_id(set_, cycle, motor, limits, pstate, branch, dt_s, draw=None) -> str:
    d = f"D{draw:02d}-" if draw else ""
    return f"{OFFICIAL_PREFIX}{set_}-{d}{cycle}-{motor}-{limits.replace('-', '')}-{pstate}-{branch}-dt{dt_s * 1e3:g}ms"


def _cond(set_, cycle, motor, limits, pstate, dt_s, draw=None) -> Condition:
    ids = {b: run_id(set_, cycle, motor, limits, pstate, b, dt_s, draw) for b in BRANCHES}
    return Condition(ids["B0"].replace("-B0-", "-"), set_, cycle, motor, limits, pstate, dt_s, draw, ids)


def build_schedule() -> list[Condition]:
    out = []
    for set_, cyc, ps in (("NOM", "S2", "P1"), ("P3", "S2", "P3"), ("INS", "S1", "P1")):
        for m in MOTORS:
            for lim in LIMITS:
                out.append(_cond(set_, cyc, m, lim, ps, DT_NOMINAL))
    for m in MOTORS:
        out.append(_cond("CNV", "S2", m, "L-EVE", "P1", DT_CONV))
    for d in range(1, sensitivity.N_DRAWS + 1):
        for m in sensitivity.MOTORS:
            out.append(_cond("SEN", sensitivity.CYCLE, m, sensitivity.LIMITS, sensitivity.PSTATE, DT_NOMINAL, d))
    return out


def profile_source(c: Condition, branch: str) -> str:
    draw = f", draw {c.draw}" if c.draw else ""
    if branch == "B0":
        return f"v_b({c.cycle}, {c.motor}, {c.limits}, P1{draw}) [baseline task, protocol 4; D2]"
    return f"S-eco({c.cycle}, {c.motor}, {c.limits}, P1{draw}; 2 m, 0.1 m/s) [protocol 5; designed on P1, D2]"


def schedule_rows(conds) -> list[dict]:
    rows, seq = [], 0
    for c in conds:
        for b in BRANCHES:
            seq += 1
            rows.append(dict(seq=seq, run_id=c.run_ids[b], condition_id=c.cid, set=c.set, cycle=c.cycle, motor=c.motor,
                             limits=c.limits, evaluated_pstate=c.pstate, design_pstate="P1", branch=b, dt_s=c.dt_s,
                             trace_dt_s=1e-3, draw=c.draw or "", tracked_profile=profile_source(c, b),
                             gain=("nominal P1 fixed gain, not retuned per draw (AMB-14), identical for B0 and B3"
                                   if c.draw else "R1 fixed Bryson gain designed on nominal P1, identical for B0 and B3"),
                             role=("held-out (protocol 3)" if c.cycle == "S2" else "in-sample (protocol 3)"),
                             counts_toward_170=True))
    return rows


def planner_jobs(conds) -> list[dict]:
    """QS planner jobs implied by the schedule (protocol 10.6: planner runs are QS only and are not runs)."""
    keys = {}
    for c in conds:
        keys.setdefault((c.cycle, c.motor, c.limits, c.draw or 0, GRID_COARSE), c.set)
    for m in MOTORS:
        for lim in LIMITS:
            keys[("S2", m, lim, 0, GRID_FINE)] = "GRID"                    # protocol 9 planner grid convergence
    rows = []
    for (cyc, m, lim, d, (ds, dv)), why in sorted(keys.items()):
        tag = f"D{d:02d}-" if d else ""
        rows.append(dict(job_id=f"PLN-{tag}{cyc}-{m}-{lim.replace('-', '')}-P1-ds{ds:g}-dv{dv:g}", cycle=cyc, motor=m,
                         limits=lim, design_pstate="P1", draw=d or "", ds_m=ds, dv_ms=dv,
                         purpose="grid convergence (protocol 9)" if why == "GRID" else f"profiles for set {why}",
                         counts_toward_170=False))
    return rows


def validate_schedule(conds) -> dict:
    rows = schedule_rows(conds)
    ids = [r["run_id"] for r in rows]
    by_set = {s: sum(1 for r in rows if r["set"] == s) for s in PLANNED}
    nom = {(c.cycle, c.motor, c.limits, c.pstate) for c in conds if c.set == "NOM"}
    smoke_ids = smoke_run_ids()
    res = {
        "total_is_170": len(rows) == TOTAL_PLANNED,
        "counts_per_set_equal_protocol_10_6": by_set == PLANNED,
        "run_ids_unique": len(set(ids)) == len(ids),
        "condition_ids_unique": len({c.cid for c in conds}) == len(conds),
        "every_condition_has_B0_and_B3": all(set(c.run_ids) == set(BRANCHES) for c in conds),
        "run_ids_official_format": all(re.fullmatch(r"R4H3-[A-Z0-9]+-(D\d\d-)?S[12]-M[012]-L(R1|EVE)-P[13]-B[03]-dt(1|0\.5)ms", i)
                                       for i in ids),
        "cycles_only_S1_S2": {c.cycle for c in conds} <= {"S1", "S2"},
        "S1_only_in_INS": all((c.cycle == "S1") == (c.set == "INS") for c in conds),
        "P3_only_in_P3_set": all((c.pstate == "P3") == (c.set == "P3") for c in conds),
        "half_ms_only_in_CNV": all((c.dt_s == DT_CONV) == (c.set == "CNV") for c in conds),
        "CNV_has_1ms_counterpart_in_NOM": all((c.cycle, c.motor, c.limits, c.pstate) in nom for c in conds if c.set == "CNV"),
        "CNV_is_S2_LEVE_P1_all_motors": sorted((c.cycle, c.limits, c.pstate, c.motor) for c in conds if c.set == "CNV")
        == [("S2", "L-EVE", "P1", m) for m in MOTORS],
        "SEN_is_32_draws_x_M0_M1_on_S2_LEVE_P1": sorted((c.draw, c.motor) for c in conds if c.set == "SEN")
        == [(d, m) for d in range(1, 33) for m in ("M0", "M1")]
        and all((c.cycle, c.limits, c.pstate) == ("S2", "L-EVE", "P1") for c in conds if c.set == "SEN"),
        "no_M2_in_SEN": not any(c.motor == "M2" for c in conds if c.set == "SEN"),
        "every_profile_designed_on_P1": all(r["design_pstate"] == "P1" for r in rows),
        "smoke_runs_not_reused_D4": not (set(ids) & set(smoke_ids)),
        "numerics_equal_protocol": (config.ECO_DS, config.ECO_DV, config.LAMBDA_LOG10, config.LAMBDA_ITERS, config.H)
        == (2.0, 0.1, (-3.0, 6.0), 40, 1.0),
        "no_planner_parameter_selection_job": all(j["purpose"].startswith(("profiles for set", "grid convergence"))
                                                  for j in planner_jobs(conds)),
    }
    return {"checks": res, "passed": all(res.values()), "counts_per_set": by_set, "n_runs": len(rows),
            "n_conditions": len(conds), "n_planner_jobs": len(planner_jobs(conds)), "smoke_run_ids_excluded": smoke_ids}


def smoke_run_ids() -> list[str]:
    p = SMOKE_DIR / "runs.csv"
    if not p.is_file():
        return []
    return [r["run_id"] for r in csv.DictReader(p.open(encoding="utf-8"))]


def csv_text(rows) -> str:
    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=keys, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


# --------------------------------------------------------------------------- amendment reader
RECOMPUTE_TOLERANCES = {"E_chem_rel": 1e-4, "E_DC_rel": 1e-4, "distance_rel": 1e-6,
                        **evaluator.PROTOCOL_TOLERANCES, "flags": "identical"}

# Protocol 9 numerical checks, in the order they are reached, with the consequence the protocol fixes in advance.
# Only "release" checks can stop anything; every S2 check is evaluated during or after the official campaign, never
# before release, and its consequence is a stated resolution or a per-run/per-branch label. None may change a
# planner setting, profile, tolerance, controller, task or the run list.
NUMERICAL_CHECKS = (
    dict(order=1, name="frozen_and_input_hashes", when="every process start", data="hashes",
         criterion="equal to the frozen values", on_fail="STOP: refuse to run (protocol 9 row 1)"),
    dict(order=2, name="planner_unit_tests", when="release gate (before any campaign run)", data="toy tasks",
         criterion="all pass (protocol 9 row 2)", on_fail="STOP: do not release"),
    dict(order=3, name="infrastructure_readiness", when="release gate", data="S1 development checks and tests",
         criterion="tests pass; recomputation and 0.5 ms path work", on_fail="STOP: do not release"),
    dict(order=4, name="planner_optimality", when="each official planner job (QS)", data="S2 and S1 designs",
         criterion="S_max - S_found <= 0.2 pp", on_fail="GO: the gap is the stated resolution (protocol 9)"),
    dict(order=5, name="planner_grid_convergence", when="after the six S2 fine-grid jobs (QS)", data="S2, P1",
         criterion="|dS_found| < 0.2 pp", on_fail="GO: results stated at the observed resolution (protocol 9)"),
    dict(order=6, name="independent_recomputation", when="every run", data="the run's trace",
         criterion="protocol group within tolerances; flags identical",
         on_fail="GO: run flagged and not credited until resolved by amendment (protocol 9)"),
    dict(order=7, name="qs_vs_dynamic", when="every pair whose B0 and B3 profiles both pass the QS screen (N-A2)",
         data="the pair's runs and profiles",
         criterion="M0, M1: |e_dyn - e_QS| / e_QS <= 1 % for both arms, using only protocol-8.2-valid, recomputation-"
                   "confirmed energy (AMB-31 ruling); M2 reported; QS-ineligible pairs are NOT_APPLICABLE_QS_INFEASIBLE "
                   "(neither pass nor fail); a FAIL or NOT_EVALUABLE_* pair in any set, or any required nominal NOM cell "
                   "(L-R1, L-EVE) that does not PASS individually -> INCONCLUSIVE (AMB-29(b)-(d), AMB-30, I-1 rulings)",
         on_fail="GO: that motor branch is INCONCLUSIVE (protocol 9)"),
    dict(order=8, name="dynamic_time_step", when="after NOM L-EVE and CNV runs complete", data="S2, L-EVE, P1",
         criterion="|dE_rel(0.5 ms) - dE_rel(1 ms)| < 0.01 pp", on_fail="GO: stated resolution (protocol 9, as R3)"),
    dict(order=9, name="baseline_sanity", when="S2 designs", data="v_b vs v_ref",
         criterion="v_b = v_ref exactly checked and recorded", on_fail="GO: shortfall and deviation reported"),
)


def numerical_check_consequence(name: str, passed: bool) -> str:
    """The predetermined consequence of one protocol 9 check (NUMERICAL_CHECKS)."""
    row = next((c for c in NUMERICAL_CHECKS if c["name"] == name), None)
    if row is None:
        raise KeyError(f"unknown check {name!r}")
    return "pass" if passed else row["on_fail"]
IMPLEMENTED = {
    "applies_to_protocol_sha256": frozen.FROZEN_SHA256[frozen.PROTOCOL],
    "D1_extra_stop_rule": "reject",
    "D1_rest_threshold_ms": 1e-9,
    "D2_p3_profiles": "B0 tracks v_b designed on P1; B3 tracks S-eco designed on P1; both run on the P3 plant",
    "D2_gain_design_state": "P1",
    "D3_arrival_rule": "arrival no later than the reference arrival, then at rest until the reference departure",
    "D3_timing_tolerance_s": 0.0,
    "D4_smoke_runs_count_toward_campaign": False,
    "D5_p3_infeasible_rule": "run and retain both arms; classify the condition infeasible; no paired energy difference",
    "canonical_sampled_cycles_sha256": dict(inputs.CANONICAL_SAMPLED_SHA256),
    "recompute_gate": list(evaluator.PROTOCOL_CHECKS),
    "recompute_tolerances": RECOMPUTE_TOLERANCES,
    "planned_runs": dict(PLANNED, total=TOTAL_PLANNED),
    "AMB_14_sensitivity_gain_basis": sensitivity.GAIN_BASIS,
    "AMB_15_campaign_directory": CAMPAIGN_DIR_NAME,
    "AMB_24_p3_feasibility": checks.P3_RULE,
    "numerical_check_order": [c["name"] for c in NUMERICAL_CHECKS],
}
OPEN_PARAMETERS = {}                           # every open item of draft rev1 was decided by the owner (09_ record)

# Amendment 2 (draft): N-A2 ruling. The block of the issued amendment 2 must equal this, value for value.
IMPLEMENTED_2 = {
    "applies_to_protocol_sha256": frozen.FROZEN_SHA256[frozen.PROTOCOL],
    "amends_amendment_1_sha256": AMENDMENT_1_SHA256,
    "N_A2_applicability": "protocol 9 QS-vs-dynamic applies to a pair only if both the B0 and the B3 profile pass the "
                          "QS feasibility screen (QSPlant.step) on the condition's evaluated plant",
    "N_A2_not_applicable_label": checks.QS_NA_INFEASIBLE,
    "N_A2_not_applicable_is_pass": False,
    "N_A2_not_applicable_is_fail": False,
    "N_A2_qs_energy_of_ineligible_pairs_used_for_acceptance": False,
    "N_A2_thresholds": {"M0_max_abs_pct": checks.QS_DYN_MAX_PCT, "M1_max_abs_pct": checks.QS_DYN_MAX_PCT,
                        "M2": "reported only"},
    "N_A2_applicable_failure": "the M0/M1 motor branch is INCONCLUSIVE (protocol 9, unchanged)",
    "N_A2_no_eligible_comparison": "the M0/M1 motor branch is INCONCLUSIVE with respect to this criterion",
    "N_A2_dynamic_8_2_independent": True,
    "N_A2_failed_check_record": "every failing piece with its failed QSPlant.step sub-check(s) (drive torque, battery "
                                "discriminant, discharge current) and their values at each Gauss node",
    "AMB_29_profile_unavailable": "owner ruling 2026-10-28: the condition keeps its explicit PROFILE_UNAVAILABLE or "
                                  "BASELINE_UNAVAILABLE status and counts in every planned-run, feasibility and verdict "
                                  "denominator; never COMPARABLE, never a paired comparison, never removed; only the "
                                  "pair's QS-vs-dynamic check is " + checks.QS_NA_PROFILE + " (its applicability "
                                  "condition is objectively unmet), which is not a pass",
    "AMB_29_eligible_run_missing": "owner ruling 2026-10-28 (AMB-29(b)): " + checks.QS_NOT_EVALUABLE + " (class "
                                   "NOT_EVALUABLE) -> the M0/M1 branch is INCONCLUSIVE for this criterion; M2 stays "
                                   "reported only; "
                                   "the pair stays in every planned-run denominator and every available energy trace "
                                   "is kept for diagnostics",
    "AMB_29_qs_energy_undefined": "owner ruling 2026-10-28 (AMB-29(c)): QS energy per reference km <= 0 -> "
                                  + checks.QS_UNDEFINED + " -> the M0/M1 branch is INCONCLUSIVE for this criterion; M2 "
                                  "stays reported only; the raw values and the exact non-positive term are recorded; no "
                                  "percentage, replacement denominator, epsilon, absolute value or substitute threshold; "
                                  "the runs' dynamic result is unaffected and protocol 8.2 still applies to it. Owner "
                                  "ruling I-5 (2026-10-28): the label " + checks.QS_UNDEFINED + " is kept unchanged; the "
                                  "owner's QS_COMPARISON_NOT_EVALUABLE is the NOT_EVALUABLE class",
    "AMB_29_condition_error": "owner ruling 2026-10-28 (AMB-29(d)): an exception before or during the pair evaluation, "
                              "including the QS screen -> " + checks.QS_CONDITION_ERROR + " -> the M0/M1 branch is "
                              "INCONCLUSIVE for this criterion; M2 stays reported only; both dynamic arms still run and are "
                              "classified by protocol 8.2 alone; the error, stage, traceback, traces and run IDs are kept "
                              "(errors.csv, conditions/, traces/); no retry, automatic replacement or substitute run; a rerun "
                              "only under the protocol and an explicitly authorised procedure with a distinct run ID. Owner "
                              "ruling I-6 (2026-10-28): an exception in a run or its evaluation (any recorded stage) makes "
                              "the pair NOT_EVALUABLE whatever its label would otherwise be (NOT_APPLICABLE_*, PASS, "
                              "REPORTED_ONLY or FAIL): a QS-eligible pair one of whose runs raised is "
                              + checks.QS_NOT_EVALUABLE + " (AMB-29(b)), any other pair " + checks.QS_CONDITION_ERROR
                              + "; a NOT_EVALUABLE_* label stays; the label it would otherwise have is kept in "
                              "qs_vs_dyn_pair_status_before_error, a measured failure in qs_vs_dyn_fail_arms and in the "
                              "accounting (fail_before_exception, n_FAIL_before_exception); after a failure of the separate "
                              "recomputation or its fold a NOT_APPLICABLE_* pair is " + checks.QS_CONDITION_ERROR
                              + " and a result that used unconfirmed energy " + checks.QS_RUN_INVALID + " (I-4); QS "
                              "applicability (qs_vs_dyn_applicability), dynamic validity (the condition status) and the "
                              "evaluation status are kept separate and counted separately",
    "AMB_30_branch_scope": "owner ruling 2026-10-28 (strict): an applicable FAIL or a NOT_EVALUABLE_* pair in any "
                           "preregistered set (NOM, P3, INS, CNV, SEN) makes the M0/M1 branch INCONCLUSIVE, counted per "
                           "set, never averaged; a PASS in another set, the in-sample S1 set INS included, never "
                           "substitutes for missing or failed nominal S2 evidence; a planned pair missing from the record "
                           "blocks PASS. Owner ruling I-1 (2026-10-28): every required nominal cell of the branch (NOM; "
                           "L-R1 and L-EVE) must individually PASS; an absent, duplicated, invalid, not-evaluable or "
                           "NOT_APPLICABLE_* nominal cell, or one whose condition has no profile, cannot count as PASS and "
                           "the branch is INCONCLUSIVE; a FAIL keeps the frozen protocol 9 consequence. Owner ruling I-2 "
                           "(2026-10-28): outside NOM a missing profile (NOT_APPLICABLE_PROFILE_UNAVAILABLE) does not by "
                           "itself make the QS check INCONCLUSIVE; it is never a PASS; the explicit missing-profile status "
                           "stays counted in the planned-run and feasibility reporting and never yields a paired energy "
                           "comparison",
    "I_1_required_nominal_cells": "owner ruling 2026-10-28: for M0 and M1 every required nominal cell on the held-out "
                                  "S2 set (NOM; L-R1 and L-EVE) must individually PASS the applicable QS-vs-dynamic check; "
                                  "a missing, invalid, unevaluable or NOT_APPLICABLE required nominal cell cannot count as "
                                  "PASS and the branch is INCONCLUSIVE; S1 never substitutes; a FAIL keeps the frozen "
                                  "consequence; thresholds unchanged; QS and dynamic feasibility stay distinct (a "
                                  "QS-infeasible profile is never reclassified as dynamically infeasible)",
    "AMB_31_energy_of_invalid_runs": "owner ruling 2026-10-28: energy of a run failing protocol 8.2, or not confirmed "
                                     "by its recomputation, is diagnostic only (energy_roles.csv DIAGNOSTIC_ONLY_*): never "
                                     "confirmatory, never credited to the paired endpoint, never used by the QS-vs-dynamic "
                                     "check. Owner ruling I-4 (2026-10-28): both runs must be confirmed by the separate "
                                     "recomputation (and by the in-process one) before the QS check uses their energy; an "
                                     "unconfirmed run supplies no confirmatory evidence for that check",
    "AMB_31_invalid_arm_label": checks.QS_RUN_INVALID + " (owner ruling AMB-29(b): M0/M1 branch INCONCLUSIVE; M2 stays "
                                                        "reported only)",
    "paired_endpoint_rule": "a paired energy comparison exists only for a condition whose final status is COMPARABLE: "
                            "both arms complete the task and pass every protocol 8.2 criterion and the separate "
                            "recomputation",
    "h3_verdict_denominators": "fixed by protocol 8.1: 6 nominal S2 P1 cells and 32 draws per M0/M1; a missing, "
                               "profile-failed, invalid or non-comparable cell or draw is never removed and never counts "
                               "toward SUPPORTED",
    "AMB_32_not_supported_needs_all_nominal_cells": "owner ruling 2026-10-28: NOT SUPPORTED requires a comparable pair "
                                                    "in all six nominal cells; a nominal cell that is missing, invalid "
                                                    "or not evaluable makes the H3 verdict INCONCLUSIVE, recorded with "
                                                    "its reason; no negative finding is inferred from missing data",
    "pair_statuses": list(checks.PAIR_QS_STATUSES),
    "pair_status_classes": {k: list(v) for k, v in checks.PAIR_STATUS_CLASSES.items()},
    "qs_applicability_values": list(checks.QS_ELIGIBLE_BY_APPLICABILITY),
    "qs_dynamic_accounting_classes": "review R8-2, owner ruling I-6: every row of qs_dynamic_accounting.csv adds up to "
                                     "its planned pairs two separate ways: by QS applicability (qs_eligible_pairs, "
                                     "qs_ineligible_pairs, not_applicable_profile_unavailable, qs_eligibility_unknown) "
                                     "and by pair status (qs_check_pass, qs_check_fail, qs_check_reported_only, "
                                     "qs_check_not_applicable_qs_infeasible, qs_check_not_applicable_profile_unavailable "
                                     "and the four not_evaluable_* columns); a pair made NOT_EVALUABLE by an exception "
                                     "stays in its applicability class",
    "non_positive_denominator_rule": "AMB-29(c) and owner ruling I-3 (2026-10-28), for every energy-saving percentage, "
                                     "the QS-vs-dynamic ratio (e_QS) and the others (paired dE_rel, B0 energy per "
                                     "reference km; planner S_found, S_max and grid dS, E(v_b)): none is computed with a "
                                     "denominator <= 0 or not finite; the value is not evaluable and the exact term and "
                                     "the raw values are recorded. The recomputation and shortfall tolerance comparisons of "
                                     "amendment 1 are not saving percentages and are unchanged",
    "record_invariant": "every scheduled condition and run has exactly one record (no drop, retry or replacement); a "
                        "violation is recorded in errors.csv and the manifest",
    "separate_recomputation_exit_codes": "0 every recomputed run passes; 1 a run fails a protocol check; 3 independence "
                                         "violation or refusal; 4 exception, including one while importing or reading the "
                                         "arguments. Only 0 and 1 are results: any other exit leaves every run unconfirmed "
                                         "and is recorded in errors.csv with its stderr; a fold that raises leaves no "
                                         "condition COMPARABLE",
    "separate_recomputation_ledger": "reviews V6-1, R7-4: the process's full output goes to "
                                     "recomputation_independent_process.log; a launch failure, an exit other than 0 or 1, "
                                     "a missing or unreadable output file, or an executed run missing from the output is "
                                     "recorded in errors.csv with its stage and that log; every executed run the separate "
                                     "recomputation does not confirm as recomputed (all of them after a process failure) "
                                     "gets its own row with its run ID",
    "errors_ledger": "reviews R7-3, R7-5, R8-5: every errors.csv row has a stage; diagnostic_path where a process log "
                     "exists; every failed output write (each conditions/<id>.json, conditions.csv and the process log "
                     "included) is recorded with stage 'write <file>' and listed in manifest output_write_failures, and "
                     "the remaining outputs are still written; a failed planner-file write during a condition is a "
                     "condition-level exception; a failed errors.csv write is recorded in the manifest; a failed "
                     "manifest or post-run hash-list write stops the run with an error",
    "owner_decisions_open": [],
    "planned_runs": dict(PLANNED, total=TOTAL_PLANNED),
}
# Owner decisions still open for amendment 2: none since the owner's rulings on I-2 to I-6 (2026-10-28). preconditions()
# still blocks on any item listed here, so a decision can never be assumed silently.
OWNER_DECISIONS_OPEN = IMPLEMENTED_2["owner_decisions_open"]
STATUSES = ("DRAFT", "APPROVED")


def read_amendment(path: Path, implemented: dict | None = None, open_parameters: dict | None = None) -> dict:
    """Parse and check the machine-readable block. Never applies anything: it only reports agreement,
    open items and errors. Defaults check amendment 1; amendment 2 passes IMPLEMENTED_2 and {}."""
    implemented = IMPLEMENTED if implemented is None else implemented
    open_parameters = OPEN_PARAMETERS if open_parameters is None else open_parameters
    path = Path(path)
    out = {"path": str(path), "exists": path.is_file(), "errors": [], "open": [], "decisions": {}}
    if not out["exists"]:
        out["errors"].append("file not found")
        return out
    text = path.read_text(encoding="utf-8")
    out["sha256"] = frozen.sha256(path)
    m = re.search(re.escape(BLOCK_MARK) + r"\s*```json\s*(\{.*?\})\s*```", text, re.S)
    if not m:
        out["errors"].append("machine-readable block not found")
        return out
    try:
        blk = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        out["errors"].append(f"block is not valid JSON: {e}")
        return out
    out["decisions"] = blk
    out["status"] = blk.get("status")
    if out["status"] not in STATUSES:
        out["errors"].append(f"status {out['status']!r} not in {STATUSES}")
    for k, v in blk.items():
        if k in ("status", "amendment", "note"):
            continue
        if k in implemented:
            if v != json.loads(json.dumps(implemented[k])):
                out["errors"].append(f"{k}: amendment value {v!r} differs from the implemented {implemented[k]!r}; "
                                     "the runner does not override code or the frozen protocol")
        elif k in open_parameters:
            allowed = open_parameters[k]
            if v is None:
                out["open"].append(k)
            elif allowed is not None and v not in allowed:
                out["errors"].append(f"{k}: {v!r} not one of {sorted(allowed)}")
            elif allowed is None and not (isinstance(v, str) and re.fullmatch(r"R4_\d{8}_pilot(_[a-z0-9]+)?", v)):
                out["errors"].append(f"{k}: expected a directory name R4_<yyyymmdd>_pilot[_suffix]")
        else:
            out["errors"].append(f"unknown key {k!r}: an amendment block may not introduce settings")
    missing = [k for k in list(implemented) + list(open_parameters) if k not in blk]
    if missing:
        out["errors"].append(f"missing keys {missing}")
    return out


# --------------------------------------------------------------------------- configuration
def config_content() -> dict:
    """Deterministic campaign configuration (DRAFT): every input hash the campaign depends on."""
    conds = build_schedule()
    return {
        "status": "DRAFT - NOT APPROVED FOR CAMPAIGN EXECUTION",
        "protocol": "../R4_20261028_preflight/03_R4_protocol_v1.md",
        "protocol_sha256": frozen.FROZEN_SHA256[frozen.PROTOCOL],
        "frozen_inputs_sha256": {Path(k).relative_to(frozen.REPO).as_posix(): v for k, v in frozen.FROZEN_SHA256.items()},
        "upstream_sha256": {Path(k).relative_to(frozen.REPO).as_posix(): v for k, v in frozen.UPSTREAM_SHA256.items()},
        "canonical_sampled_cycles": {c: {"path": f"inputs/cycles/{c}_sampled_h1.csv", "sha256": h}
                                     for c, h in inputs.CANONICAL_SAMPLED_SHA256.items()},
        "cycle_source_artefacts_sha256": inputs.SOURCE_SHA256,
        "cycle_inputs_manifest_sha256": inputs.MANIFEST_SHA256,
        "sensitivity_design": sensitivity.design_record(),
        "sensitivity_draws_table": "config/" + DRAWS_TABLE.name,
        "sensitivity_draws_sha256": hashlib.sha256(sensitivity_table_text().encode()).hexdigest(),
        "schedule_sha256": hashlib.sha256(csv_text(schedule_rows(conds)).encode()).hexdigest(),
        "planner_jobs_sha256": hashlib.sha256(csv_text(planner_jobs(conds)).encode()).hexdigest(),
        "planned_runs": dict(PLANNED, total=TOTAL_PLANNED),
        "implemented_decisions": IMPLEMENTED,
        "open_parameters": sorted(OPEN_PARAMETERS),
        "numerical_checks": list(NUMERICAL_CHECKS),
        "campaign_directory": CAMPAIGN_DIR_NAME,
        "issued_amendment_path": f"{CAMPAIGN_DIR_NAME}/release/03_R4_protocol_v1_amendment_1.md",
        "amendment_1_sha256": AMENDMENT_1_SHA256,
        "amendment_2_implemented": IMPLEMENTED_2,
        "issued_amendment_2_path": f"{CAMPAIGN_DIR_NAME}/release/03_R4_protocol_v1_amendment_2.md",
        "scenario_record": config.scenario_record(),
    }


def sensitivity_table_text() -> str:
    return csv_text(sensitivity.table_rows())


def build_config() -> dict:
    """Write the campaign configuration, the sensitivity draw table and the trace schema. A file that exists must
    already have exactly the content that would be written; otherwise it is never overwritten (refusal)."""
    from r4h3 import traces
    schema = frozen.PILOT / "config" / "trace_schema_v2.json"
    targets = {CAMPAIGN_CONFIG: json.dumps(config_content(), indent=1, default=str) + "\n",
               DRAWS_TABLE: sensitivity_table_text(), schema: json.dumps(traces.schema_record(), indent=1) + "\n"}
    for path, text in targets.items():
        if path.exists() and path.read_text(encoding="utf-8") != text:
            raise FileExistsError(f"refusing to overwrite {path} with different content")
    for path, text in targets.items():
        if not path.exists():
            path.write_text(text, encoding="utf-8", newline="\n")
    return {p.name: frozen.sha256(p) for p in targets}


def authorization_problems(auth: dict, issued_sha256: str | None, gate_sha256: str | None,
                           issued_2_sha256: str | None = None) -> list[str]:
    """Why a campaign-authorisation record does not authorise execution: it must name who authorised and when, state
    exactly AUTHORIZATION_SCOPE, and carry the SHA-256 of issued amendments 1 and 2 and of the release gate record
    logs/pre_run_hashes.txt it authorises."""
    out = []
    if not issued_2_sha256 or auth.get("amendment_2_sha256") != issued_2_sha256:
        out.append("campaign authorisation does not carry the issued amendment 2's SHA-256")
    if not auth.get("authorized_by") or not auth.get("date"):
        out.append("campaign authorisation does not name who authorised it and when")
    if auth.get("scope") != AUTHORIZATION_SCOPE:
        out.append(f"campaign authorisation scope is not {AUTHORIZATION_SCOPE!r}")
    if not issued_sha256 or auth.get("amendment_sha256") != issued_sha256:
        out.append("campaign authorisation does not carry the issued amendment's SHA-256")
    if not gate_sha256 or auth.get("pre_run_hashes_sha256") != gate_sha256:
        out.append("campaign authorisation does not carry the SHA-256 of logs/pre_run_hashes.txt")
    return out


def approval_problems(ap: dict, issued_sha256: str | None, review: dict) -> list[str]:
    """Why an approval record does not authorise the campaign: it must name the approver and date, carry the issued
    amendment's SHA-256, accept every review item pending owner acceptance, and approve exactly the implemented
    recomputation tolerances."""
    out = []
    if not ap.get("approved_by") or not ap.get("date"):
        out.append("approval record does not name an approver and a date")
    if not issued_sha256 or ap.get("amendment_sha256") != issued_sha256:
        out.append("approval record does not carry the issued amendment's SHA-256")
    missing = sorted(set(review.get("pending_owner_acceptance", [])) - set(ap.get("accepted_review_items", [])))
    if missing:
        out.append(f"approval record does not accept review items {missing}")
    if ap.get("approved_tolerances") != json.loads(json.dumps(RECOMPUTE_TOLERANCES)):
        out.append("approval record does not approve exactly the implemented recomputation tolerances")
    return out


# --------------------------------------------------------------------------- preconditions
def preconditions(mode: str = "readiness") -> list[str]:
    """Every reason the campaign may not start (empty list = may start). mode "readiness" checks this directory's
    readiness gate; mode "campaign" checks the protocol 10.1 gate logs/pre_run_hashes.txt of a fresh campaign
    directory named by the issued amendment (AMB-15)."""
    if mode not in ("readiness", "campaign"):
        raise ValueError(mode)
    blockers = []
    try:
        frozen.verify_frozen({**frozen.FROZEN_SHA256, **frozen.UPSTREAM_SHA256})
    except Exception as e:  # noqa: BLE001
        blockers.append(f"frozen or upstream inputs: {e}")
    try:
        inputs.verify_all()
    except Exception as e:  # noqa: BLE001
        blockers.append(f"canonical cycle inputs: {e}")
    if not CAMPAIGN_CONFIG.is_file() or not DRAWS_TABLE.is_file():
        blockers.append("campaign configuration or sensitivity draw table missing")
    else:
        try:                    # a failure to rebuild the configuration is a blocker, never an exception
            current = (CAMPAIGN_CONFIG.read_text(encoding="utf-8")
                       == json.dumps(config_content(), indent=1, default=str) + "\n")
        except Exception as e:  # noqa: BLE001
            current = False
            blockers.append(f"campaign configuration cannot be rebuilt: {e!r}")
        if not current:
            blockers.append("campaign configuration differs from the schedule, inputs and design it was built from")
        if DRAWS_TABLE.read_text(encoding="utf-8") != sensitivity_table_text():
            blockers.append("sensitivity draw table does not regenerate identically")
    iss = read_amendment(ISSUED_AMENDMENT)
    if not iss["exists"]:
        blockers.append(f"no issued amendment at {ISSUED_AMENDMENT} (the draft is not approved)")
    else:
        blockers += [f"issued amendment: {e}" for e in iss["errors"]]
        if iss.get("status") != "APPROVED":
            blockers.append(f"issued amendment status is {iss.get('status')!r}, not 'APPROVED'")
        blockers += [f"open item {k} (null in the issued amendment)" for k in iss["open"]]
        if not APPROVAL_RECORD.is_file():
            blockers.append(f"no approval record {APPROVAL_RECORD.name}")
        else:
            rv = json.loads(REVIEW_STATUS.read_text(encoding="utf-8")) if REVIEW_STATUS.is_file() else {}
            blockers += approval_problems(json.loads(APPROVAL_RECORD.read_text(encoding="utf-8")), iss.get("sha256"), rv)
    iss2 = read_amendment(ISSUED_AMENDMENT_2, IMPLEMENTED_2, {})
    if not iss2["exists"]:
        blockers.append(f"no issued amendment 2 at {ISSUED_AMENDMENT_2} (N-A2 ruling not yet approved)")
    else:
        blockers += [f"issued amendment 2: {e}" for e in iss2["errors"]]
        if iss2.get("status") != "APPROVED":
            blockers.append(f"issued amendment 2 status is {iss2.get('status')!r}, not 'APPROVED'")
        if iss.get("sha256") != AMENDMENT_1_SHA256:
            blockers.append("the issued amendment 1 is not the one amendment 2 amends")
        if not APPROVAL_RECORD_2.is_file():
            blockers.append(f"no approval record {APPROVAL_RECORD_2.name}")
        else:
            ap2 = json.loads(APPROVAL_RECORD_2.read_text(encoding="utf-8"))
            if not ap2.get("approved_by") or not ap2.get("date") or ap2.get("amendment_sha256") != iss2.get("sha256"):
                blockers.append("amendment 2 approval record does not name an approver, a date and its SHA-256")
    if mode == "readiness":
        if not READINESS_GATE.is_file():
            blockers.append("readiness gate record missing")
        else:
            rec = json.loads(READINESS_GATE.read_text(encoding="utf-8"))
            from r4h3.slice import code_hashes
            if rec.get("code_sha256") != code_hashes():
                blockers.append("code or config changed since the readiness gate record")
            if rec.get("junit", {}).get("failures", 1) or rec.get("junit", {}).get("errors", 1):
                blockers.append("readiness test run not clean")
    else:
        from r4h3.slice import check_gate
        try:
            check_gate()                                  # logs/pre_run_hashes.txt of this directory
        except Exception as e:  # noqa: BLE001
            blockers.append(f"protocol 10.1 gate record: {e}")
        from r4h3.slice import GATE_FILE
        if not CAMPAIGN_AUTHORIZATION.is_file():
            blockers.append(f"no campaign authorisation record {CAMPAIGN_AUTHORIZATION.name} "
                            "(protocol approval is not campaign authorisation)")
        else:
            blockers += authorization_problems(json.loads(CAMPAIGN_AUTHORIZATION.read_text(encoding="utf-8")),
                                               iss.get("sha256"),
                                               frozen.sha256(GATE_FILE) if GATE_FILE.is_file() else None,
                                               iss2.get("sha256"))
        if ((frozen.PILOT / "outputs" / SMOKE_DIR.name).exists() or frozen.PILOT.resolve() != CAMPAIGN_DIR.resolve()
                or (frozen.PILOT / "outputs" / "campaign").exists()):          # path, not name (review R3-1)
            blockers.append(f"campaign must run once, from the released copy in {CAMPAIGN_DIR_NAME} (AMB-15), "
                            f"not from {frozen.PILOT.name} (protocol 10.1)")
    blockers += [f"owner decision open: {k} (candidate section 9); it must be decided before issue"
                 for k in OWNER_DECISIONS_OPEN]                                                     # fail-closed
    if not REVIEW_STATUS.is_file():
        blockers.append("code review status missing")
    else:
        rv = json.loads(REVIEW_STATUS.read_text(encoding="utf-8"))
        if rv.get("open_critical", 1) or rv.get("open_major", 1):
            blockers.append(f"code review: {rv.get('open_critical')} critical and {rv.get('open_major')} major "
                            "findings not resolved or accepted by the owner")
        blockers += [f"code review item awaiting an owner decision: {k}" for k in rv.get("open_owner_decisions", [])]
        blockers += [f"code review not yet performed or its closure not yet accepted by the owner: {k}"
                     for k in rv.get("reviews_pending", [])]                                        # fail-closed
    return blockers


def run_campaign():
    """Campaign mode: the 170 runs plus the planner grid-convergence jobs, in the fresh campaign directory.
    Refuses while any blocker exists. Not started in the readiness task."""
    blockers = preconditions("campaign")
    if blockers:
        raise CampaignBlocked(blockers)
    from r4h3 import task as taskmod
    grid_keys = [("S2", m, lim) for m in MOTORS for lim in LIMITS]
    return execute_schedule(build_schedule(), taskmod.load_task, frozen.PILOT / "outputs" / "campaign", official=True,
                            grid_keys=grid_keys)


# --------------------------------------------------------------------------- executor (generic)
def env_record() -> dict:
    """Protocol 10.2. The package list is the pip-freeze equivalent read from importlib.metadata (no subprocess)."""
    from importlib import metadata
    import scipy
    return {"python": sys.version, "executable": sys.executable, "numpy": np.__version__, "scipy": scipy.__version__,
            "machine": platform.node(), "process_start": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "packages": sorted(f"{d.metadata['Name']}=={d.version}" for d in metadata.distributions())}


def eval_spec(p, soh, lim, motor_spec, task, knots=None) -> dict:
    """The evaluator's run specification: everything it needs besides the trace (written next to each trace)."""
    from r4h3.closedloop import TRACE_DT
    spec = {"battery": dict(V_oc=p.V_oc, R0=p.R0_new * (1 + p.k_r0 * (1 - soh)), Q_Ah=p.Q_Ah, c_dis=lim.c_dis,
                            c_ch=lim.c_ch, v_min_ratio=lim.v_min_ratio, v_max_ratio=lim.v_max_ratio),
            "motor": motor_spec, "G": p.G, "r_w": p.r_w, "v_eps": p.v_eps, "T_max": p.T_max, "P_max": p.P_max,
            "B_m": p.B_m, "eta_g": p.eta_g, "M_eff": p.M_eff, "C1": p.C1,
            "Ts_s": p.Ts, "dt_s": TRACE_DT, "d_ref_m": task.d_ref, "rest_intervals": [list(r) for r in task.rest]}
    if knots is not None:
        spec["tracked_knots"] = [[float(x) for x in knots[0]], [float(x) for x in knots[1]]]
    return spec


def _run_ids(c: Condition) -> str:
    return ";".join(f"{b}={i}" for b, i in c.run_ids.items())


def _blank(x):
    return "" if x is None else x


def _guard(ids, official):
    for i in ids:
        if i.startswith(OFFICIAL_PREFIX) and not official:
            raise CampaignBlocked([f"official run ID {i} outside campaign mode"])
        if not i.startswith(OFFICIAL_PREFIX) and official:
            raise CampaignBlocked([f"non-official run ID {i} in campaign mode"])


def plan_design(task, limits, p_design, mm, grid=GRID_COARSE) -> dict:
    """Baseline task and S-eco profile on the design plant (P1), each validated independently of the planner.
    The S-eco profile must pass the validator (D1, D3); v_b is reported, not rejected (protocol 9 baseline sanity)."""
    from r4h3 import planner, validator
    plant = L.QSPlant(p_design, config.PSTATES["P1"]["soh"], config.LIMITS[limits], mm)
    vb = planner.baseline_task(plant, task)
    eco = planner.plan_seco(plant, task, *grid)
    val_b = validator.validate_trajectory(task, task.t, vb["v_b"], plant, "B0 v_b") if vb["v_b"] is not None else None
    val_e = validator.validate_trajectory(task, eco["t"], eco["v"], plant, "B3 S-eco") if eco["status"] == "ok" else None
    return dict(plant=plant, vb=vb, eco=eco, val_b=val_b, val_e=val_e, grid=grid,
                baseline_ok=vb["v_b"] is not None,
                eco_ok=eco["status"] == "ok" and bool(val_e and val_e["valid"]),
                E_b_J=L.evaluate(plant, vb["v_b"], task.h)["E_J"] if vb["v_b"] is not None else float("nan"))


def baseline_sanity(design, task) -> dict:
    vb = design["vb"]
    out = dict(baseline_equals_reference=vb["equals_reference"], baseline_track_W=vb["W"],
               baseline_hit_boundary=vb["hit_boundary"], baseline_max_dev_ms=vb["max_dev_from_ref_ms"])
    if design["val_b"]:
        out.update(baseline_distance_err_m=design["val_b"]["distance_err_m"],
                   baseline_validator_failures="; ".join(design["val_b"]["failures"]))
    return out


def run_arm(run_id_, branch, task, knots, p, soh, lim, mm, motor_spec, K, dt, outdir: Path, meta_extra: dict):
    """One dynamic run: simulate, write the 1 ms trace and its spec, read the trace back, evaluate it, compare."""
    from rebuild.model import IX
    from r4h3 import traces
    from r4h3.closedloop import profile_from_knots, run_metrics, simulate_traced, trace_constraint_metrics
    from r4h3.slice import sim_stop_ok
    prof = profile_from_knots(run_id_, *knots)
    s0 = time.time()
    out, tr = simulate_traced(prof, p, K, soh, lim, mm, dt=dt)
    sim = run_metrics(out, p, soh, task.d_ref, prof.duration, p.Ts)
    sim["shortfall_vs_tracked_profile_pct"] = sim.pop("shortfall_pct")       # r3_lib's is against the profile (CR-A11)
    tr["v_ref_task_mps"] = np.interp(tr["t_s"], task.t, task.v_ref)
    tr["stop_ref_flag"] = np.zeros_like(tr["t_s"])
    for t_a, t_d in task.rest:
        tr["stop_ref_flag"][(tr["t_s"] >= t_a - 1e-12) & (tr["t_s"] <= t_d + 1e-12)] = 1.0
    sim["stop_ok_sim"] = sim_stop_ok(tr, task.rest, config.RULES)
    sim.update(trace_constraint_metrics(tr, p, lim, config.RULES))
    sim.update(run_id=run_id_, branch=branch, dt_s=dt, trace_dt_s=out["trace_dt"], runtime_s=time.time() - s0,
               n_samples=len(tr["t_s"]), **{k: meta_extra[k] for k in ("cycle", "motor_scenario", "limits", "pstate", "draw")
                                            if k in meta_extra})
    spec = eval_spec(p, soh, lim, motor_spec, task, knots)
    y0 = out["y0"][0]
    meta = dict(run_id=run_id_, schema_version=SCHEMA_VERSION, branch=branch, soh=soh, dt_s=dt, trace_dt_s=out["trace_dt"],
                Ts_s=p.Ts, initial_conditions={k: float(y0[IX[k]]) for k in ("v", "T", "V1", "SoC")} | {"z": 0.0},
                gain=[float(x) for x in K], d_ref_m=task.d_ref, T_ref_s=task.T_ref, seed=None, **meta_extra)
    (outdir / "traces").mkdir(parents=True, exist_ok=True)
    spath = outdir / "traces" / f"{run_id_}.spec.json"
    spath.write_text(json.dumps(dict(spec=spec, rules=config.RULES, meta=meta), indent=1, default=float), encoding="utf-8")
    meta["config_sha256"] = frozen.sha256(spath)
    if not all(np.all(np.isfinite(np.asarray(v_, float))) for v_ in tr.values()):
        raw = outdir / "traces" / f"{run_id_}.nonfinite.npz"         # retained, never evaluated (protocol 8.2 'valid')
        np.savez_compressed(raw, __meta__=np.array(json.dumps(meta, default=str)), **tr)
        ev = dict(run_id=run_id_, branch=branch, sim_valid=False, complete=False, tracking_ok=False, stop_ok=False,
                  constraint_ok=False, finite_ok=False, recompute_protocol_ok=False, recompute_diagnostics_ok=False,
                  comparable=False, credited=False, trace=raw.name, trace_sha256=frozen.sha256(raw),
                  note="non-finite states: raw trace retained, not evaluated")
        sim.update({k: ev[k] for k in ("complete", "tracking_ok", "stop_ok", "constraint_ok", "finite_ok", "comparable",
                                       "credited")})
        return sim, ev, [], {}
    tpath = outdir / "traces" / f"{run_id_}.npz"
    tsha = traces.write_trace(tpath, tr, meta)
    a, _, _ = traces.read_trace(tpath)
    ev = evaluator.evaluate_trace(a, spec, config.RULES)
    cmp = evaluator.compare_with_simulator(ev, sim, config.RULES)
    stop_rows = [dict(run_id=run_id_, **r) for r in ev.pop("stop_rows")]
    ev.update({k: meta_extra[k] for k in ("cycle", "motor_scenario", "limits", "pstate", "draw") if k in meta_extra})
    ev.update(run_id=run_id_, branch=branch, sim_valid=bool(sim["valid"]), recompute_protocol_ok=cmp["protocol_ok"],
              recompute_diagnostics_ok=cmp["diagnostics_ok"], trace=tpath.name, trace_sha256=tsha,
              spec=spath.name, spec_sha256=meta["config_sha256"])
    ev["comparable"] = checks.arm_comparable(ev)
    ev["credited"] = ev["comparable"] and ev["recompute_protocol_ok"]                     # CR-A8
    sim.update({k: ev[k] for k in ("complete", "tracking_ok", "stop_ok", "constraint_ok", "finite_ok", "comparable",
                                   "recompute_protocol_ok", "credited")})                # protocol 10.3 (CR-A11)
    return sim, ev, stop_rows, cmp


def run_condition(cond: Condition, task, design: dict, p_eval, soh_eval, lim, mm, motor_spec, K, outdir: Path,
                  official=False) -> dict:
    """Both arms of one condition on the same evaluated plant, with the same gain, limits, motor and initial state
    (protocol 6; D2). Both arms run whenever their profile exists. The QS step check of each profile on the evaluated
    plant is a recorded diagnostic screen (AMB-24); formal feasibility is decided by protocol 8.2 on the dynamic run.
    Every scheduled run gets a row; failures stay in the record (protocol 10.4)."""
    _guard(cond.run_ids.values(), official)
    knots = {"B0": (task.t, design["vb"]["v_b"]), "B3": (design["eco"]["t"], design["eco"]["v"])}
    ok = {"B0": design["baseline_ok"], "B3": design["eco_ok"]}
    rows, sims, stops, cmps, errors, e_dyn = {}, [], [], {}, [], {}
    # The QS screen is a diagnostic (AMB-24). Review R5-1: an exception in it is recorded with the run IDs and leaves
    # the pair's QS eligibility unknown; it never stops, skips or relabels a dynamic run.
    qs_screen, screen_errors = {}, []
    try:
        eval_plant = L.QSPlant(p_eval, soh_eval, lim, mm)
    except Exception:  # noqa: BLE001
        eval_plant = None
        errors.append(dict(run_id="", condition_id=cond.cid, run_ids=_run_ids(cond), stage="qs_screen",
                           traceback=traceback.format_exc()))
        screen_errors = [b for b in BRANCHES if ok[b]]
    for b in BRANCHES:
        if ok[b] and eval_plant is not None:
            try:
                qs_screen[b] = checks.qs_screen(eval_plant, *knots[b])
            except Exception:  # noqa: BLE001
                errors.append(dict(run_id=cond.run_ids[b], condition_id=cond.cid, run_ids=_run_ids(cond),
                                   stage="qs_screen", traceback=traceback.format_exc()))
                screen_errors.append(b)
    qs_feasible = {b: q["feasible"] for b, q in qs_screen.items()}
    qs_val = {b: q["infeasible_pieces"] for b, q in qs_screen.items()}
    for b in BRANCHES:
        rid = cond.run_ids[b]
        if not ok[b]:
            rows[b] = None
            sims.append(dict(run_id=rid, branch=b, executed=False, credited=False,
                             reason="baseline task unavailable" if b == "B0" else "S-eco profile unavailable or invalid"))
            continue
        try:
            sim, ev, st, cmp = run_arm(rid, b, task, knots[b], p_eval, soh_eval, lim, mm, motor_spec, K, cond.dt_s, outdir,
                                       dict(cycle=cond.cycle, motor_scenario=cond.motor, limits=cond.limits,
                                            pstate=cond.pstate, design_pstate="P1", draw=cond.draw,
                                            tracked_profile=profile_source(cond, b)))
        except Exception:  # noqa: BLE001  -- every exception is recorded, never retried (protocol 10.4)
            tb = traceback.format_exc()
            errors.append(dict(run_id=rid, condition_id=cond.cid, stage="run", traceback=tb))
            rows[b] = {"run_id": rid, "error": tb.strip().splitlines()[-1]}
            kept = sorted(p.name for p in (outdir / "traces").glob(f"{rid}.*")) if (outdir / "traces").is_dir() else []
            sims.append(dict(run_id=rid, branch=b, executed=False, credited=False,          # review R5-6: files named
                             reason="exception (errors.csv)" + ("; its trace files are kept" if kept else ""),
                             retained_files=";".join(kept)))
            continue
        sim["executed"] = True
        rows[b], e_dyn[b] = ev, sim.get("E_net_Wh")
        sims.append(sim)
        stops += st
        cmps[rid] = cmp
        try:                     # review R5-1: diagnostic fields only; a failure here never relabels the run
            qs = qs_screen.get(b)
            ev.update(qs_E_J_diagnostic=qs["E_J"] if qs else "", qs_screen_feasible=qs["feasible"] if qs else "",
                      qs_screen_n_failed=qs["n_infeasible_pieces"] if qs else "",
                      failed_8_2_criteria="; ".join(checks.failed_criteria(ev)))
        except Exception:  # noqa: BLE001
            errors.append(dict(run_id=rid, condition_id=cond.cid, stage="run_report", traceback=traceback.format_exc()))
    try:                         # review R5-1: a classification failure is recorded; the executed runs keep their records
        status = checks.classify_pair(rows["B0"], rows["B3"], eco_profile_ok=ok["B3"], baseline_ok=ok["B0"],
                                      pstate=cond.pstate)
        both_valid = all(rows.get(b) and "error" not in rows[b] and checks.arm_comparable(rows[b]) for b in BRANCHES)
    except Exception:  # noqa: BLE001
        errors.append(dict(run_id="", condition_id=cond.cid, run_ids=_run_ids(cond), stage="classify",
                           traceback=traceback.format_exc()))
        status, both_valid = "ERROR", False
    # protocol 9 QS-vs-dynamic at pair level (N-A2): computed only when both profiles pass the QS screen on this plant.
    # An exception here is recorded and never relabels the executed runs (review R3-9).
    arm_checks, diag, invalid = {}, {}, []
    # QS applicability, kept apart from the dynamic status and from the pair's evaluation status (owner ruling I-6).
    # Review R8-10: a profile failing the QS screen makes the check not applicable even if the other arm's screen raised.
    missing_profile = [b for b in BRANCHES if not ok[b]]
    screen_failed = [b for b in BRANCHES if qs_feasible.get(b) is False]
    applicability = (checks.QS_NA_PROFILE if missing_profile else checks.QS_NA_INFEASIBLE if screen_failed
                     else checks.QS_APPLICABILITY_UNKNOWN if screen_errors else checks.QS_APPLICABLE)
    eligible_pair = checks.QS_ELIGIBLE_BY_APPLICABILITY[applicability]
    try:
        if screen_errors:        # review R5-1; owner ruling I-6: the exception wins over a missing profile's N/A label
            pair = dict(pair_status=checks.QS_CONDITION_ERROR, qs_eligible=eligible_pair,
                        before_error=applicability if applicability in checks.PAIR_STATUS_CLASSES["NOT_APPLICABLE"] else "",
                        ineligible_arms="" if missing_profile else ",".join(screen_failed), fail_arms="",
                        reason=(f"profile unavailable for {', '.join(missing_profile)}; " if missing_profile else "")
                        + (f"QS feasibility screen failed for {', '.join(screen_failed)}; " if screen_failed else "")
                        + f"exception in the QS screen of {', '.join(screen_errors)} (errors.csv); not evaluable "
                          "(owner ruling I-6)")
        else:
            screen = {b: (qs_feasible[b] if ok[b] else None) for b in BRANCHES}
            eligible = all(screen[b] is True for b in BRANCHES)
            for b in BRANCHES:
                ev = rows.get(b)
                finite = ev is not None and "error" not in ev and e_dyn.get(b) is not None and bool(np.isfinite(e_dyn[b]))
                if eligible and finite:
                    q = checks.qs_vs_dynamic(motor_spec["sid"], qs_screen[b]["E_J"], e_dyn[b], task.d_ref)
                    # AMB-31 ruling: only energy of a run passing protocol 8.2 and its recomputation is used (the same
                    # rule as energy_role; the separate recomputation is applied in fold_separate_recomputation)
                    if checks.arm_comparable(ev) and bool(ev.get("recompute_protocol_ok")):
                        arm_checks[b] = q
                    else:                              # kept, labelled diagnostic only (invalid or unconfirmed run)
                        diag[b], invalid = q, invalid + [b]
            pair = checks.pair_qs_dynamic(motor_spec["sid"], screen, arm_checks, invalid)
    except Exception:  # noqa: BLE001  -- AMB-29(d) ruling: recorded with the run IDs, never retried
        tb = traceback.format_exc()
        errors.append(dict(run_id="", condition_id=cond.cid, run_ids=_run_ids(cond), stage="qs_vs_dynamic", traceback=tb))
        arm_checks, diag, invalid = {}, {}, []
        pair = dict(pair_status=checks.QS_CONDITION_ERROR, qs_eligible=eligible_pair, ineligible_arms="", fail_arms="",
                    reason="exception in the QS-vs-dynamic evaluation: " + tb.strip().splitlines()[-1])
    # Owner ruling I-6 (2026-10-28): an exception in a run or its evaluation (any stage recorded above) makes the pair
    # NOT_EVALUABLE whatever its label would otherwise be: NOT_APPLICABLE_*, PASS, REPORTED_ONLY, and (review R8-1) FAIL.
    # A QS-eligible pair one of whose runs raised has an arm without dynamic energy: NOT_EVALUABLE_RUN_MISSING (AMB-29(b));
    # any other pair NOT_EVALUABLE_CONDITION_ERROR (AMB-29(d)); a NOT_EVALUABLE_* label stays. The label it would
    # otherwise have is kept in qs_vs_dyn_pair_status_before_error, and a measured failure in qs_vs_dyn_fail_arms.
    if errors and pair["pair_status"] not in checks.PAIR_STATUS_CLASSES["NOT_EVALUABLE"]:
        stages = ", ".join(sorted({str(e.get("stage", "")) for e in errors}))
        run_raised = applicability == checks.QS_APPLICABLE and any(e.get("stage") == "run" for e in errors)
        pair = dict(pair, pair_status=checks.QS_NOT_EVALUABLE if run_raised else checks.QS_CONDITION_ERROR,
                    before_error=pair["pair_status"],
                    reason=f"exception(s) at stage {stages} (errors.csv): not evaluable ("
                           + ("an arm has no dynamic energy, AMB-29(b); " if run_raised else "AMB-29(d); ")
                           + f"owner ruling I-6); otherwise {pair['pair_status']}: {pair['reason']}")
    try:                         # review R5-1: a reporting failure is recorded; it never relabels the runs or the condition
        for b in BRANCHES:
            ev = rows.get(b)
            if ev is not None and "error" not in ev:
                q, qd = arm_checks.get(b), arm_checks.get(b) or diag.get(b)
                ev.update(qs_vs_dyn_pct=_blank(q["diff_pct"]) if q else "",
                          qs_vs_dyn_status=q["status"] if q else pair["pair_status"],
                          qs_vs_dyn_pair_status=pair["pair_status"],
                          qs_vs_dyn_pct_diagnostic_invalid_run=_blank(diag[b]["diff_pct"]) if b in diag else "",
                          qs_vs_dyn_e_qs_Wh_per_km=_blank(qd["e_qs_Wh_per_km"]) if qd else "",      # AMB-29(c): raw
                          qs_vs_dyn_e_dyn_Wh_per_km=_blank(qd["e_dyn_Wh_per_km"]) if qd else "",
                          qs_vs_dyn_non_positive_term=qd.get("non_positive_term", "") if qd else "")
        warn = {b: "; ".join(f"piece {x['piece']} [{x['t0_s']!r}, {x['t1_s']!r}] s, v {x['v0_ms']!r}->{x['v1_ms']!r} m/s"
                             + (f" failed {'+'.join(x['failed_checks'])}" if x.get("failed_checks") else "")
                             for x in qs_val[b]) for b in qs_val}
        report = dict(
            b0_qs_screen_warning=warn.get("B0", ""), b3_qs_screen_warning=warn.get("B3", ""),
            qs_vs_dyn_non_positive_terms="; ".join(f"{b}: {q['non_positive_term']}"
                                                   for b, q in sorted({**arm_checks, **diag}.items())
                                                   if q.get("non_positive_term")),
            b0_failed_8_2="; ".join(checks.failed_criteria(rows["B0"])) if rows["B0"] and "error" not in rows["B0"] else "",
            b3_failed_8_2="; ".join(checks.failed_criteria(rows["B3"])) if rows["B3"] and "error" not in rows["B3"] else "",
            eco_status=design["eco"]["status"], eco_valid=bool(design["val_e"] and design["val_e"]["valid"]),
            eco_validator_failures="; ".join(design["val_e"]["failures"]) if design["val_e"] else "",
            **baseline_sanity(design, task))
    except Exception:  # noqa: BLE001
        tb = traceback.format_exc()
        errors.append(dict(run_id="", condition_id=cond.cid, run_ids=_run_ids(cond), stage="condition_report",
                           traceback=tb))
        report = dict(reporting_error=tb.strip().splitlines()[-1])
        if pair["pair_status"] not in checks.PAIR_STATUS_CLASSES["NOT_EVALUABLE"]:   # AMB-29(d), I-6: record incomplete
            pair = dict(pair, pair_status=checks.QS_CONDITION_ERROR, before_error=pair["pair_status"],
                        reason="exception while recording the QS-vs-dynamic result (errors.csv): not evaluable (AMB-29(d), "
                               "owner ruling I-6); before: " + pair["reason"])
    return dict(condition_id=cond.cid, set=cond.set, cycle=cond.cycle, motor=cond.motor, limits=cond.limits,
                pstate=cond.pstate, dt_s=cond.dt_s, draw=cond.draw or "", status=status, p3_rule=checks.P3_RULE,
                b0_qs_feasible_on_eval_plant=qs_feasible.get("B0", ""), b3_qs_feasible_on_eval_plant=qs_feasible.get("B3", ""),
                qs_screen_errors=",".join(screen_errors), qs_vs_dyn_applicability=applicability,
                qs_eligible_pair=eligible_pair, qs_ineligible_arms=pair["ineligible_arms"],
                qs_vs_dyn_pair_status=pair["pair_status"], qs_vs_dyn_pair_status_before_error=pair.get("before_error", ""),
                qs_vs_dyn_pair_reason=pair["reason"],
                qs_vs_dyn_fail_arms=pair.get("fail_arms", ""), qs_vs_dyn_invalid_arms=",".join(invalid),
                dynamic_valid_pair=bool(both_valid), **report,
                _rows=rows, _sims=sims, _stops=stops, _cmps=cmps, _errors=errors, _qs_val=qs_val)


def _write_csv(path: Path, rows):
    if rows:
        path.write_text(csv_text(rows), encoding="utf-8", newline="\n")


def _write_text(path: Path, text: str, **kw):
    path.write_text(text, encoding="utf-8", **kw)


def _na_pair_not_evaluable(r, why: str) -> None:
    """Owner ruling I-6 (review R8-9): the separate recomputation is part of the runs' evaluation, so after it fails (or
    its fold raises) a NOT_APPLICABLE_* pair becomes NOT_EVALUABLE_CONDITION_ERROR; its label is kept as before."""
    ps = r.get("qs_vs_dyn_pair_status")
    if ps in checks.PAIR_STATUS_CLASSES["NOT_APPLICABLE"]:
        r.update(qs_vs_dyn_pair_status_in_process=ps, qs_vs_dyn_pair_status_before_error=ps,
                 qs_vs_dyn_pair_status=checks.QS_CONDITION_ERROR,
                 qs_vs_dyn_pair_reason=f"{why}: not evaluable (owner ruling I-6); otherwise {ps}: "
                                       f"{r.get('qs_vs_dyn_pair_reason')}")


def fold_separate_recomputation(cond_rows, conds, sep_rows, sep_exit: int, process_error: str = "") -> None:
    """Apply the separate-process recomputation to the condition statuses (protocol 9, re-review N-B1). A condition
    stays COMPARABLE only if the separate script recomputed both of its runs and both pass every protocol check;
    otherwise it becomes RECOMPUTATION_DISAGREEMENT. The in-process status is kept as status_in_process.
    process_error: the runner's own failure around the process (launch, missing or unreadable output), if any."""
    by_run = {r["run_id"]: r for r in sep_rows}
    failed = f"separate script exit {sep_exit}" if sep_exit not in (0, 1) else process_error
    for r, c in zip(cond_rows, conds):
        r["status_in_process"] = r["status"]
        problems = []
        for b, rid in c.run_ids.items():
            s = by_run.get(rid)
            if s is None or s.get("recomputed") != "True":
                problems.append(f"{b}: not recomputed by the separate script")
            elif s.get("protocol_ok") != "True":
                problems.append(f"{b}: separate recomputation fails a protocol check")
        if sep_exit not in (0, 1):
            problems.append(f"separate script exit {sep_exit}")
        r["separate_recomputation"] = "; ".join(problems) or "ok"
        if r["status"] == checks.COMPARABLE and problems:
            r["status"] = "RECOMPUTATION_DISAGREEMENT"
        r["paired_endpoint_eligible"] = r["status"] == checks.COMPARABLE                        # AMB-31 ruling
        # AMB-31 ruling: a QS-vs-dynamic result that used the energy of a run the separate recomputation does not
        # confirm is not evidence; it becomes NOT_EVALUABLE_RUN_INVALID (a FAIL of a confirmed arm stays a FAIL).
        bad = list(c.run_ids) if sep_exit not in (0, 1) else [
            b for b, rid in c.run_ids.items() if by_run.get(rid) is None or by_run[rid].get("recomputed") != "True"
            or by_run[rid].get("protocol_ok") != "True"]
        ps = r.get("qs_vs_dyn_pair_status")
        if bad and ps in ("PASS", "FAIL", "REPORTED_ONLY"):
            confirmed_fail = set(filter(None, str(r.get("qs_vs_dyn_fail_arms", "")).split(","))) - set(bad)
            if not (ps == "FAIL" and confirmed_fail):
                r["qs_vs_dyn_pair_status_in_process"] = ps
                r["qs_vs_dyn_pair_status"] = checks.QS_RUN_INVALID
                r["qs_vs_dyn_pair_reason"] = (f"separate recomputation does not confirm {', '.join(bad)}; its energy is "
                                              f"diagnostic only (AMB-31 ruling). In process: {r.get('qs_vs_dyn_pair_reason')}")
        if failed:
            _na_pair_not_evaluable(r, f"the separate recomputation failed ({failed})")


def fold_failed(cond_rows, reason: str) -> None:
    """Fail-closed fallback when fold_separate_recomputation itself raised (review R5-8): no condition stays COMPARABLE,
    none is eligible for the paired endpoint, no QS-vs-dynamic PASS, FAIL or REPORTED_ONLY stands unconfirmed, and no
    NOT_APPLICABLE_* label stands over the exception (owner ruling I-6, review R8-9)."""
    for r in cond_rows:
        r.setdefault("status_in_process", r["status"])
        r["separate_recomputation"] = f"not applied: the fold raised ({reason})"
        if r["status"] == checks.COMPARABLE:
            r["status"] = "RECOMPUTATION_DISAGREEMENT"
        r["paired_endpoint_eligible"] = False
        if r.get("qs_vs_dyn_pair_status") in ("PASS", "FAIL", "REPORTED_ONLY"):
            r["qs_vs_dyn_pair_status_in_process"] = r["qs_vs_dyn_pair_status"]
            r["qs_vs_dyn_pair_status"] = checks.QS_RUN_INVALID
        _na_pair_not_evaluable(r, f"the recomputation fold raised ({reason})")


def execute_schedule(conds, task_loader, outdir: Path, official=False, grid_keys=()) -> list[dict]:
    """Run every condition in order. Designs are computed once per (cycle, motor, limits, draw) on P1 and reused
    by every evaluated state (D2). grid_keys: (cycle, motor, limits) scenarios also planned on the fine grid for the
    protocol 9 grid-convergence check (QS only). Writes runs.csv, evaluation.csv, conditions.csv,
    conditions/<id>.json (as each finishes), stop_compliance.csv, recomputation.json, errors.csv, planner_checks.csv,
    planner/*, traces/*, manifest.json and a post-run SHA-256 list under outdir (which must not exist)."""
    from r4h3.closedloop import fixed_gain
    from r4h3.slice import code_hashes
    _guard([i for c in conds for i in c.run_ids.values()], official)
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=False)
    for sub in ("planner", "conditions", "traces"):
        (outdir / sub).mkdir()
    manifest = {"kind": "H3 campaign" if official else "H3 executor (development; not campaign runs)",
                "start": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "env": env_record(),
                "frozen": frozen.verify_frozen({**frozen.FROZEN_SHA256, **frozen.UPSTREAM_SHA256}),
                "code_sha256": code_hashes(), "gain_basis_draws": sensitivity.GAIN_BASIS, "p3_rule": checks.P3_RULE,
                "numerical_checks": list(NUMERICAL_CHECKS)}
    if official:
        manifest["canonical_cycle_inputs"] = inputs.verify_all()
    draws = sensitivity.draws() if any(c.draw for c in conds) else None
    designs, cond_rows, sims, evs, stops, cmps, errors = {}, [], [], [], [], {}, []

    def guarded(name, write):    # reviews R7-5, R8-5: a failed write is recorded and never stops the remaining outputs
        try:
            write()
        except Exception:  # noqa: BLE001
            errors.append(dict(run_id="", condition_id="OUTPUT-WRITE", stage=f"write {name}",
                               traceback=traceback.format_exc()))
    for c in conds:
        try:                    # a condition-level exception is recorded as an ERROR condition (re-review N-A5)
            task = task_loader(c.cycle)
            row = draws[c.draw - 1] if c.draw else None
            p_design = sensitivity.draw_params(row) if c.draw else config.params_for("P1")
            mm = sensitivity.draw_motor(row, c.motor) if c.draw else config.motor_model(c.motor)
            mspec = (sensitivity.draw_eval_motor_spec(row, c.motor, frozen.M1_CURVE) if c.draw
                     else evaluator.motor_spec_from_protocol(c.motor, frozen.M1_CURVE))
            key = (c.cycle, c.motor, c.limits, c.draw)
            if key not in designs:
                d = designs[key] = plan_design(task, c.limits, p_design, mm)
                tag = f"{c.cycle}_{c.motor}_{c.limits}" + (f"_D{c.draw:02d}" if c.draw else "")
                _write_csv(outdir / "planner" / f"planner_rows_{tag}.csv", d["eco"]["rows"])
                np.savez_compressed(outdir / "planner" / f"profiles_{tag}.npz", t_task=task.t, v_ref=task.v_ref,
                                    v_b=d["vb"]["v_b"] if d["baseline_ok"] else np.array([]),
                                    t_seco=d["eco"]["t"] if d["eco"]["status"] == "ok" else np.array([]),
                                    v_seco=d["eco"]["v"] if d["eco"]["status"] == "ok" else np.array([]))
                (outdir / "planner" / f"validation_{tag}.json").write_text(
                    json.dumps({"B0": d["val_b"], "B3": d["val_e"]}, indent=1, default=float), encoding="utf-8")
            p_eval = p_design if c.draw else config.params_for(c.pstate)
            soh_eval = config.PSTATES[c.pstate]["soh"]
            K = sensitivity.gain_for_draw(row) if c.draw else fixed_gain(config.params_for("P1"))     # AMB-14
            r = run_condition(c, task, designs[key], p_eval, soh_eval, config.LIMITS[c.limits], mm, mspec, K, outdir,
                              official)
        except CampaignBlocked:
            raise
        except Exception:  # noqa: BLE001
            tb = traceback.format_exc()
            r = dict(condition_id=c.cid, set=c.set, cycle=c.cycle, motor=c.motor, limits=c.limits, pstate=c.pstate,
                     dt_s=c.dt_s, draw=c.draw or "", status="ERROR", error=tb.strip().splitlines()[-1],
                     qs_eligible_pair=None, qs_ineligible_arms="", qs_vs_dyn_applicability="UNKNOWN",
                     qs_vs_dyn_pair_status=checks.QS_CONDITION_ERROR,
                     qs_vs_dyn_pair_reason="condition-level exception", dynamic_valid_pair=False,
                     _rows={}, _cmps={}, _stops=[], _qs_val={},
                     _sims=[dict(run_id=i, branch=b, executed=False, credited=False, reason="condition-level exception")
                            for b, i in c.run_ids.items()],
                     _errors=[dict(run_id="", condition_id=c.cid, run_ids=_run_ids(c), stage="condition", traceback=tb)])
        rec = {k: r.pop(k) for k in ("_rows", "_sims", "_stops", "_cmps", "_errors", "_qs_val")}
        sims += rec["_sims"]
        evs += [v for v in rec["_rows"].values() if v and "error" not in v]
        stops += rec["_stops"]
        cmps.update(rec["_cmps"])
        errors += rec["_errors"]
        cond_rows.append(r)
        guarded(f"conditions/{c.cid}.json", lambda: _write_text(
            outdir / "conditions" / f"{c.cid}.json",
            json.dumps(dict(condition=r, runs=rec["_sims"], errors=rec["_errors"], qs_screen_failures=rec["_qs_val"]),
                       indent=1, default=str)))
    # AMB-29(a), (b), (d) rulings: every scheduled condition and run has exactly one record; nothing is dropped, retried
    # or replaced by another run. A violation would be a defect: it is recorded in errors.csv and the manifest.
    planned_ids = [i for c in conds for i in c.run_ids.values()]
    recorded = [s.get("run_id") for s in sims]
    invariant = dict(scheduled_conditions=len(conds), condition_rows=len(cond_rows),
                     condition_ids_match=[r["condition_id"] for r in cond_rows] == [c.cid for c in conds],
                     scheduled_runs=len(planned_ids), run_rows=len(recorded),
                     run_ids_match=sorted(recorded) == sorted(planned_ids) and len(set(recorded)) == len(recorded))
    if not (invariant["condition_ids_match"] and invariant["run_ids_match"]):
        errors.append(dict(run_id="", condition_id="RECORD-INVARIANT", stage="record invariant",
                           traceback=json.dumps(invariant)))
    manifest["record_invariant"] = invariant
    pchecks = []
    for cyc, m, lim in grid_keys:                         # protocol 9 planner grid convergence and optimality (QS)
        try:
            task = task_loader(cyc)
            mm = config.motor_model(m)
            coarse = designs.get((cyc, m, lim, None)) or plan_design(task, lim, config.params_for("P1"), mm)
            fine = plan_design(task, lim, config.params_for("P1"), mm, GRID_FINE)
            _write_csv(outdir / "planner" / f"planner_rows_{cyc}_{m}_{lim}_fine.csv", fine["eco"]["rows"])
            row = dict(cycle=cyc, motor=m, limits=lim, coarse_status=coarse["eco"]["status"],
                       fine_status=fine["eco"]["status"], coarse_valid=coarse["eco_ok"], fine_valid=fine["eco_ok"])
            if coarse["eco"]["status"] == "ok" and fine["eco"]["status"] == "ok":
                row.update({f"coarse_{k}": v for k, v in checks.scenario_totals(
                    coarse["E_b_J"], coarse["eco"]["E_seco_J"], coarse["eco"]["LB_total_J"]).items()})
                row.update(checks.grid_convergence(coarse["E_b_J"], coarse["eco"]["E_seco_J"], fine["eco"]["E_seco_J"]))
        except Exception:  # noqa: BLE001
            tb = traceback.format_exc()
            errors.append(dict(run_id="", condition_id=f"GRID-{cyc}-{m}-{lim}", stage="planner grid check", traceback=tb))
            row = dict(cycle=cyc, motor=m, limits=lim, error=tb.strip().splitlines()[-1])
        pchecks.append(row)
    guarded("planner_checks.csv", lambda: _write_csv(outdir / "planner_checks.csv", pchecks))
    guarded("runs.csv", lambda: _write_csv(outdir / "runs.csv", sims))
    guarded("evaluation.csv", lambda: _write_csv(outdir / "evaluation.csv", evs))
    # protocol 9: the recomputation that decides crediting is the separate script reading only the saved traces
    # (re-review N-B1). It runs here in its own process; its verdict is folded into the condition statuses.
    # Review R5-8: every step is guarded and fails closed (no condition stays COMPARABLE without a confirmed fold); the
    # script's own failure (exit other than 0 or 1) goes to errors.csv with its full stderr.
    # Review V6-1: the process's full output is kept in sep_log, and any failure before, during or at the end of the
    # separate process (launch, exit other than 0 or 1, missing or unreadable output, an executed run missing from the
    # output) is recorded with its stage and sep_log; review R7-4: plus one row per executed run left unconfirmed.
    sep_exit, sep_out, sep_err, sep_rows, problem = -1, "", "", [], ""
    sep_csv, sep_log = outdir / "recomputation_independent.csv", outdir / "recomputation_independent_process.log"
    try:
        sep = subprocess.run([sys.executable, "-I", "-B",
                              str(Path(__file__).resolve().parents[1] / "recompute_from_traces.py"), str(outdir)],
                             capture_output=True, text=True)
        sep_exit, sep_out, sep_err = sep.returncode, sep.stdout or "", sep.stderr or ""
    except Exception:  # noqa: BLE001
        sep_err, problem = traceback.format_exc(), "launch"
    try:
        sep_rows = list(csv.DictReader(sep_csv.open(encoding="utf-8"))) if sep_csv.is_file() else []
    except Exception:  # noqa: BLE001
        sep_err += "\n" + traceback.format_exc()
        problem = problem or "unreadable output"
    if not problem and sep_exit not in (0, 1):
        problem = f"exit {sep_exit}"
    if not problem and not sep_csv.is_file():
        problem = f"exit {sep_exit} without its output file"
    cid_by_run = {rid: c.cid for c in conds for rid in c.run_ids.values()}
    sep_by_id = {r.get("run_id"): r for r in sep_rows}
    process_failed = bool(problem)                       # launch, unreadable or missing output, exit other than 0/1
    absent = [e["run_id"] for e in evs if e["run_id"] not in sep_by_id]
    if not problem and absent:
        problem = f"{len(absent)} executed run(s) missing from its output"
    # review R7-4: every executed run the separate recomputation does not confirm as recomputed gets a ledger row: all of
    # them after a process failure; otherwise each one absent from the output or recorded there as not recomputed
    unrecomputed = ([(e["run_id"], problem) for e in evs] if process_failed else
                    [(rid, "absent from its output") for rid in absent]
                    + [(e["run_id"], f"not recomputed: {sep_by_id[e['run_id']].get('reason', '')}") for e in evs
                       if e["run_id"] in sep_by_id and sep_by_id[e["run_id"]].get("recomputed") != "True"])
    try:
        _write_text(sep_log, f"exit {sep_exit}\n--- stdout ---\n{sep_out}\n--- stderr ---\n{sep_err}\n", newline="\n")
    except Exception:  # noqa: BLE001
        errors.append(dict(run_id="", condition_id="SEPARATE-RECOMPUTATION", stage=f"write {sep_log.name}",
                           traceback=traceback.format_exc()))
    if problem:
        errors.append(dict(run_id="", condition_id="SEPARATE-RECOMPUTATION", stage=problem, traceback=sep_err,
                           diagnostic_path=sep_log.name))
    errors += [dict(run_id=rid, condition_id=cid_by_run.get(rid, ""), stage=f"separate recomputation: {why}",
                    traceback="not recomputed by the separate script; its energy is not confirmed",
                    diagnostic_path=sep_log.name) for rid, why in unrecomputed]
    try:
        fold_separate_recomputation(cond_rows, conds, sep_rows, sep_exit, problem if process_failed else "")
    except Exception:  # noqa: BLE001
        tb = traceback.format_exc()
        errors.append(dict(run_id="", condition_id="RECOMPUTATION-FOLD", stage="recomputation fold", traceback=tb,
                           diagnostic_path=sep_log.name))
        fold_failed(cond_rows, tb.strip().splitlines()[-1])
    manifest["separate_recomputation"] = dict(exit=sep_exit, problem=problem, process_log=sep_log.name,
                                              runs_not_recomputed=len(unrecomputed), stdout=sep_out.strip(),
                                              stderr=sep_err.strip()[-2000:])
    guarded("conditions.csv", lambda: _write_csv(outdir / "conditions.csv", cond_rows))
    # N-A2 denominators and branch outcomes (never a dropped record). An exception is recorded in errors.csv, the
    # affected outcome is never a pass, and the remaining outputs are still written (review R3-13, protocol 10.4).
    try:
        acct = checks.qs_dynamic_accounting(cond_rows)
    except Exception:  # noqa: BLE001
        tb = traceback.format_exc()
        errors.append(dict(run_id="", condition_id="QS-DYN-ACCOUNTING", stage="qs-vs-dynamic accounting", traceback=tb))
        acct = [dict(motor="", set="", error=tb.strip().splitlines()[-1])]
    branch = []
    for m in sorted(set(MOTORS) | {r["motor"] for r in cond_rows}):   # every motor branch, even with no row (AMB-30)
        try:
            branch.append(checks.branch_qs_dynamic_outcome(m, cond_rows, [c.cid for c in conds if c.motor == m]))
        except Exception:  # noqa: BLE001
            tb = traceback.format_exc()
            errors.append(dict(run_id="", condition_id=f"QS-DYN-BRANCH-{m}", stage="branch outcome", traceback=tb))
            branch.append(dict(motor=m, outcome="INCONCLUSIVE" if checks.QS_DYN_DECISIVE.get(m, True) else "REPORTED_ONLY",
                               reason="exception in the branch evaluation (errors.csv); never a pass",
                               error=tb.strip().splitlines()[-1]))
    try:                                                   # D5 status denominator, same handling (review R3-13 note)
        denom = checks.denominator([r["status"] for r in cond_rows])
    except Exception:  # noqa: BLE001
        tb = traceback.format_exc()
        errors.append(dict(run_id="", condition_id="STATUS-DENOMINATOR", stage="status denominator", traceback=tb))
        denom = dict(error=tb.strip().splitlines()[-1])
    # owner rulings AMB-31 and AMB-29(a): the final role of every planned run's energy, the planned-run and feasibility
    # denominators, and which protocol 8.1 verdicts remain possible (no energy value is read). Same error handling.
    roles, feas, verdict = [], [], {}
    try:
        ev_by_run = {e["run_id"]: e for e in evs}
        sep_by_run = {s["run_id"]: s for s in sep_rows}
    except Exception:  # noqa: BLE001
        errors.append(dict(run_id="", condition_id="ENERGY-ROLE", stage="energy role index", traceback=traceback.format_exc()))
        ev_by_run = sep_by_run = None
    for r, c in zip(cond_rows, conds):    # review R5-9: one row per planned run, even when its role cannot be set
        for b, rid in c.run_ids.items():
            try:
                if ev_by_run is None:
                    raise RuntimeError("run records could not be indexed (errors.csv)")
                ev = ev_by_run.get(rid)
                valid = ev is not None and checks.arm_comparable(ev)
                rec_ok = (sep_exit in (0, 1) and ev is not None and bool(ev.get("recompute_protocol_ok"))
                          and sep_by_run.get(rid, {}).get("recomputed") == "True"
                          and sep_by_run.get(rid, {}).get("protocol_ok") == "True")
                roles.append(dict(run_id=rid, condition_id=c.cid, set=c.set, motor=c.motor, branch=b,
                                  executed=ev is not None, arm_8_2_valid=valid,
                                  failed_8_2_criteria="; ".join(checks.failed_criteria(ev)) if ev is not None else "",
                                  recomputation_confirmed=rec_ok, condition_status=r["status"],
                                  energy_role=checks.energy_role(ev is not None, valid, rec_ok, r["status"])))
            except Exception:  # noqa: BLE001
                tb = traceback.format_exc()
                errors.append(dict(run_id=rid, condition_id="ENERGY-ROLE", stage="energy role", traceback=tb))
                roles.append(dict(run_id=rid, condition_id=c.cid, set=c.set, motor=c.motor, branch=b,
                                  executed=bool(ev_by_run) and rid in ev_by_run, arm_8_2_valid=False, failed_8_2_criteria="",
                                  recomputation_confirmed=False, condition_status=r.get("status", ""),
                                  energy_role=checks.ROLE_NOT_DETERMINED, error=tb.strip().splitlines()[-1]))
    try:
        feas = checks.feasibility_accounting(cond_rows, roles)
    except Exception:  # noqa: BLE001
        tb = traceback.format_exc()
        errors.append(dict(run_id="", condition_id="FEASIBILITY-ACCOUNTING", stage="feasibility accounting", traceback=tb))
        feas = [dict(motor="", set="", error=tb.strip().splitlines()[-1])]
    try:
        verdict = checks.h3_verdict_eligibility(cond_rows, branch)
    except Exception:  # noqa: BLE001
        tb = traceback.format_exc()
        errors.append(dict(run_id="", condition_id="H3-VERDICT-ELIGIBILITY", stage="verdict eligibility", traceback=tb))
        verdict = dict(error=tb.strip().splitlines()[-1], supported_possible=False, not_supported_possible=False,
                       verdict_without_energy="INCONCLUSIVE")
    guarded("energy_roles.csv", lambda: _write_csv(outdir / "energy_roles.csv", roles))
    guarded("feasibility_accounting.csv", lambda: _write_csv(outdir / "feasibility_accounting.csv", feas))
    guarded("h3_verdict_eligibility.json", lambda: _write_text(outdir / "h3_verdict_eligibility.json",
                                                               json.dumps(verdict, indent=1, default=str)))
    manifest["h3_verdict_eligibility"] = verdict
    guarded("qs_dynamic_accounting.csv", lambda: _write_csv(outdir / "qs_dynamic_accounting.csv", acct))
    guarded("qs_dynamic_branch_outcomes.csv", lambda: _write_csv(outdir / "qs_dynamic_branch_outcomes.csv", branch))
    manifest["qs_dynamic_branch_outcomes"] = branch
    guarded("stop_compliance.csv", lambda: _write_csv(outdir / "stop_compliance.csv", stops))
    guarded("recomputation.json", lambda: _write_text(outdir / "recomputation.json",
                                                      json.dumps(cmps, indent=1, default=float)))
    # review R8-5: every failed output write, the per-condition records, conditions.csv and the process log included
    manifest["output_write_failures"] = [e["stage"] for e in errors if str(e.get("stage", "")).startswith("write ")]
    try:                         # the ledger itself; if it cannot be written, the manifest says so
        if errors:
            _write_csv(outdir / "errors.csv", errors)
        else:
            (outdir / "errors.csv").write_text(csv_text([dict(run_id="", condition_id="", traceback="")]).split("\n")[0]
                                               + "\n", encoding="utf-8", newline="\n")
    except Exception:  # noqa: BLE001
        manifest["errors_csv_write_failure"] = traceback.format_exc()
    # the manifest and the post-run hash list are the last record; a failure to write them propagates (fail-closed)
    manifest.update(end=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                    n_runs_scheduled=sum(len(c.run_ids) for c in conds),
                    n_runs_executed=sum(1 for s in sims if s.get("executed")),
                    denominator=denom,
                    outputs={f.relative_to(outdir).as_posix(): frozen.sha256(f) for f in sorted(outdir.rglob("*"))
                             if f.is_file()})
    (outdir / "manifest.json").write_text(json.dumps(manifest, indent=1, default=str), encoding="utf-8")
    post = [dict(path=f.relative_to(outdir).as_posix(), bytes=f.stat().st_size, sha256=frozen.sha256(f))
            for f in sorted(outdir.rglob("*")) if f.is_file()]
    (outdir / "zz_post_run_sha256.csv").write_text(csv_text(post), encoding="utf-8", newline="\n")  # excludes itself
    return cond_rows


# --------------------------------------------------------------------------- dry run
def disk_and_time_estimate(conds) -> dict:
    est = {"basis": "smoke-test runs (S1, 324 s, 1 ms): trace bytes and runtime scaled by cycle duration and 1/dt"}
    p = SMOKE_DIR / "runs.csv"
    if not p.is_file():
        return {**est, "available": False}
    rows = list(csv.DictReader(p.open(encoding="utf-8")))
    rt = float(np.mean([float(r["runtime_s"]) for r in rows]))
    sizes = [f.stat().st_size for f in SMOKE_DIR.glob("trace_*.npz")]
    per_s_bytes = float(np.mean(sizes)) / 324.0 if sizes else float("nan")
    dur = {"S1": 324.0, "S2": 213.0}
    secs = sum(rt * dur[c.cycle] / 324.0 * (DT_NOMINAL / c.dt_s) * 2 for c in conds)
    byts = sum(per_s_bytes * dur[c.cycle] * 2 for c in conds)
    free = shutil.disk_usage(frozen.PILOT).free
    return {**est, "available": True, "smoke_runtime_s_mean": rt, "est_dynamic_runtime_h": secs / 3600.0,
            "est_trace_GB": byts / 1e9, "disk_free_GB": free / 1e9, "disk_ok": free > 2 * byts}


def dry_run(outdir: Path) -> dict:
    """Validate the schedule and read every input and the draft amendment. Executes no run; refuses to overwrite."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=False)
    conds = build_schedule()
    res = {"generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "mode": "dry run (no run executed, no plant evaluated)",
           "frozen_and_upstream": frozen.verify_frozen({**frozen.FROZEN_SHA256, **frozen.UPSTREAM_SHA256}),
           "schedule": validate_schedule(conds)}
    (outdir / "schedule_170.csv").write_text(csv_text(schedule_rows(conds)), encoding="utf-8", newline="\n")
    (outdir / "planner_jobs.csv").write_text(csv_text(planner_jobs(conds)), encoding="utf-8", newline="\n")
    try:
        res["canonical_cycle_inputs"] = inputs.verify_all()
    except Exception as e:  # noqa: BLE001
        res["canonical_cycle_inputs"] = {"error": str(e)}
    cfg = config_content()
    res["campaign_config"] = {"path": CAMPAIGN_CONFIG.relative_to(frozen.PILOT).as_posix(),
                              "sha256": frozen.sha256(CAMPAIGN_CONFIG) if CAMPAIGN_CONFIG.is_file() else None,
                              "current": CAMPAIGN_CONFIG.is_file() and CAMPAIGN_CONFIG.read_text(encoding="utf-8")
                              == json.dumps(cfg, indent=1, default=str) + "\n",
                              "schedule_sha256_matches": cfg["schedule_sha256"] == frozen.sha256(outdir / "schedule_170.csv")}
    res["sensitivity"] = {"table": DRAWS_TABLE.relative_to(frozen.PILOT).as_posix(),
                          "table_sha256": frozen.sha256(DRAWS_TABLE) if DRAWS_TABLE.is_file() else None,
                          "regenerates_identically": DRAWS_TABLE.is_file()
                          and DRAWS_TABLE.read_text(encoding="utf-8") == sensitivity_table_text()}
    res["draft_amendment"] = read_amendment(DRAFT_AMENDMENT)
    res["draft_amendment_2"] = read_amendment(DRAFT_AMENDMENT_2, IMPLEMENTED_2, {})
    res["issued_amendment_2_present"] = ISSUED_AMENDMENT_2.is_file()
    res["issued_amendment_present"] = ISSUED_AMENDMENT.is_file()
    res["estimate"] = disk_and_time_estimate(conds)
    res["blockers"] = preconditions("readiness")
    res["campaign_may_start"] = False if res["blockers"] else "only from a fresh campaign directory (protocol 10.1)"
    (outdir / "dry_run.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    res["outputs"] = {f.name: frozen.sha256(f) for f in sorted(outdir.iterdir())}
    (outdir / "dry_run_outputs_sha256.json").write_text(json.dumps(res["outputs"], indent=1), encoding="utf-8")
    return res
