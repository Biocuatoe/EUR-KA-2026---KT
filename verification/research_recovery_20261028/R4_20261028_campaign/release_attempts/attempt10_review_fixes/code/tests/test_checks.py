"""Campaign-level protocol 9 checks and the pair classification of 8.1/8.2 with D2/D5 (r4h3.checks)."""

import numpy as np
import pytest

from r4h3 import checks, config

L = config.L


# ---- QS energy and QS vs dynamic
def test_qs_energy_equals_r3_lib_evaluate_on_a_uniform_grid(toy2_task, plant_m0):
    a = checks.qs_energy(plant_m0, toy2_task.t, toy2_task.v_ref)
    b = L.evaluate(plant_m0, toy2_task.v_ref, toy2_task.h)
    assert a["E_J"] == b["E_J"] and a["dist_m"] == b["dist_m"] and a["feasible"] == b["feasible"]


def test_qs_energy_of_rest_pieces_is_zero(plant_m0):
    assert checks.qs_energy(plant_m0, [0.0, 5.0, 12.0], [0.0, 0.0, 0.0])["E_J"] == 0.0


def test_qs_vs_dynamic_rule():
    d_ref = 1000.0
    ok = checks.qs_vs_dynamic("M0", 3600.0 * 100.0, 100.9, d_ref)          # +0.9 %
    bad = checks.qs_vs_dynamic("M1", 3600.0 * 100.0, 101.1, d_ref)         # +1.1 %
    m2 = checks.qs_vs_dynamic("M2", 3600.0 * 100.0, 120.0, d_ref)          # reported only
    assert ok["status"] == "pass" and ok["diff_pct"] == pytest.approx(0.9)
    assert bad["status"].startswith("FAIL") and bad["decisive"]
    assert m2["status"] == "reported only (M2)" and not m2["decisive"]
    assert checks.QS_DYN_DECISIVE == {"M0": True, "M1": True, "M2": False}


# ---- planner checks
def test_scenario_totals_and_optimality_resolution():
    r = checks.scenario_totals(E_b_J=100.0, E_seco_J=97.0, LB_total_J=96.9)
    assert r["S_found_pct"] == pytest.approx(3.0) and r["S_max_pct"] == pytest.approx(3.1)
    assert r["stated_resolution_pp"] is None
    r2 = checks.scenario_totals(100.0, 97.0, 96.5)
    assert r2["stated_resolution_pp"] == pytest.approx(0.5)


def test_grid_convergence_threshold_is_strictly_below_0p2_pp():
    assert checks.grid_convergence(100.0, 97.0, 96.85)["passed"]
    r = checks.grid_convergence(100.0, 97.0, 96.8)
    assert not r["passed"] and r["stated_resolution_pp"] == pytest.approx(0.2)


def test_timestep_threshold_is_strictly_below_0p01_pp():
    assert checks.timestep_check(-2.000, -2.005)["passed"]
    assert not checks.timestep_check(-2.00, -2.02)["passed"]


# ---- classification (D5 and protocol 8.1): every branch of the rule, in order
def arm(**kw):
    base = dict(sim_valid=True, complete=True, tracking_ok=True, stop_ok=True, constraint_ok=True, finite_ok=True,
                recompute_protocol_ok=True, Wh_per_ref_km=100.0, trip_time_s=213.0)
    base.update(kw)
    return base


@pytest.mark.parametrize("kwargs,expected", [
    (dict(eco_profile_ok=False, baseline_ok=True, pstate="P1"), "PROFILE_UNAVAILABLE"),
    (dict(eco_profile_ok=True, baseline_ok=False, pstate="P1"), "BASELINE_UNAVAILABLE"),
    (dict(eco_profile_ok=True, baseline_ok=True, pstate="P1", b3={"error": "x"}), "ERROR"),
    (dict(eco_profile_ok=True, baseline_ok=True, pstate="P3", b0=arm(tracking_ok=False)), "BASELINE_INFEASIBLE_ON_P3"),
    (dict(eco_profile_ok=True, baseline_ok=True, pstate="P3", b3=arm(constraint_ok=False)), "ECO_INFEASIBLE_ON_P3"),
    (dict(eco_profile_ok=True, baseline_ok=True, pstate="P3", b3=arm(complete=False)), "ECO_INFEASIBLE_ON_P3"),
    (dict(eco_profile_ok=True, baseline_ok=True, pstate="P3"), "COMPARABLE"),
    (dict(eco_profile_ok=True, baseline_ok=True, pstate="P1", b0=arm(complete=False)), "B0_INVALID_EXCLUDED"),
    (dict(eco_profile_ok=True, baseline_ok=True, pstate="P1", b3=arm(stop_ok=False)), "INVALID_COMPARISON"),
    (dict(eco_profile_ok=True, baseline_ok=True, pstate="P1", b3=arm(constraint_ok=False)), "INVALID_COMPARISON"),
    (dict(eco_profile_ok=True, baseline_ok=True, pstate="P1", b3=arm(recompute_protocol_ok=False)),
     "RECOMPUTATION_DISAGREEMENT"),
    (dict(eco_profile_ok=True, baseline_ok=True, pstate="P1"), "COMPARABLE"),
])
def test_classification(kwargs, expected):
    b0 = kwargs.pop("b0", arm())
    b3 = kwargs.pop("b3", arm())
    assert checks.classify_pair(b0, b3, **kwargs) == expected


def test_amb24_qs_screen_is_not_an_input_to_the_feasibility_verdict():
    """AMB-24 (owner decision): a QS-screen failure alone never makes a P3 branch infeasible; protocol 8.2 decides."""
    import inspect
    assert "qs" not in str(inspect.signature(checks.classify_pair)).lower()
    b3 = arm(qs_screen_feasible=False, qs_screen_n_failed=3)
    assert checks.classify_pair(arm(), b3, eco_profile_ok=True, baseline_ok=True, pstate="P3") == "COMPARABLE"
    assert checks.failed_criteria(arm(stop_ok=False, sim_valid=False)) == ["valid", "stop compliance"]


def test_qs_screen_records_the_exact_failing_pieces(p1):
    weak = L.QSPlant(p1.with_overrides(T_max=0.5), 1.0, config.LIMITS["L-R1"], config.motor_model("M0"))
    r = checks.qs_energy(weak, [0.0, 1.0, 3.0, 5.0], [0.0, 0.0, 2.0, 0.0])
    assert not r["feasible"] and r["n_infeasible_pieces"] == len(r["infeasible_pieces"]) >= 1
    assert r["infeasible_pieces"][0] == dict(piece=1, t0_s=1.0, t1_s=3.0, v0_ms=0.0, v1_ms=2.0)


def test_classification_ignores_any_planner_flag():
    # a planner 'ok' never rescues an arm that fails 8.2; only evaluator/simulator flags are read
    b3 = arm(stop_ok=False, planner_status="ok", eco_valid=True)
    assert checks.classify_pair(arm(), b3, eco_profile_ok=True, baseline_ok=True, pstate="P1") == "INVALID_COMPARISON"


def test_paired_delta_only_for_comparable_conditions():
    for s in checks.STATUSES:
        if s != checks.COMPARABLE:
            with pytest.raises(ValueError):
                checks.paired_delta(s, arm(), arm(Wh_per_ref_km=90.0))
    d = checks.paired_delta(checks.COMPARABLE, arm(Wh_per_ref_km=100.0), arm(Wh_per_ref_km=90.0, trip_time_s=213.0))
    assert d["dE_abs_Wh_per_km"] == pytest.approx(-10.0) and d["dE_rel_pct"] == pytest.approx(-10.0)
    assert d["trip_time_B0_s"] == d["trip_time_B3_s"] == 213.0               # protocol 10.5: always with trip time


def test_denominator_keeps_every_status():
    d = checks.denominator(["COMPARABLE", "ECO_INFEASIBLE_ON_P3", "ERROR", "COMPARABLE"])
    assert d["total"] == 4 and d["COMPARABLE"] == 2 and d["ECO_INFEASIBLE_ON_P3"] == 1 and d["ERROR"] == 1
    with pytest.raises(ValueError):
        checks.denominator(["SKIPPED"])
