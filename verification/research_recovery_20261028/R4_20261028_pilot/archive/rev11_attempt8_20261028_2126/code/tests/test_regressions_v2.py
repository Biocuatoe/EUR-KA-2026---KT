"""Regression tests for the versioned changes VC-01..VC-08 (06_readiness_implementation_report.md) and the
review findings they answer (04_independent_code_review.md)."""

import inspect
import json

import numpy as np
import pytest

from conftest import short_profile
from r4h3 import config, evaluator, frozen, traces, validator
from r4h3.closedloop import TRACE_DT, fixed_gain, run_metrics, simulate_traced, trace_constraint_metrics
from r4h3.task import REST_EPS

L = config.L


def fails(res, text):
    return any(text in f for f in res["failures"])


# ---- VC-01 (D1, D3): frozen rest rule, exact timing, stationary waiting, planner independence
def test_rest_threshold_is_the_frozen_protocol_5_1_rule():
    assert REST_EPS == 1e-9
    src = inspect.getsource(L.segments)
    assert "v_ref > 1e-9" in src                                   # protocol 5.1 / r3_lib.segments
    assert "TOL_V" not in inspect.getsource(validator) and "TOL_T" not in inspect.getsource(validator)


def test_interior_knot_below_the_rest_rule_is_an_extra_stop(toy_task):
    t = np.array([0, 1, 2, 3, 4, 5, 6, 7, 10.0])
    v = np.array([0, 0, 1, 5e-10, 2, 2, 1, 0, 0.0])                # "touch-and-go" at 5e-10 m/s (<= 1e-9): a stop
    r = validator.validate_trajectory(toy_task, t, v)
    assert fails(r, "extra stop")


def test_rest_knot_within_the_rest_rule_is_at_rest(toy2_task):
    v = toy2_task.v_ref.copy()
    v[8] = 5e-10                                                   # inside the stop [7, 9]: at rest under 5.1
    r = validator.validate_trajectory(toy2_task, toy2_task.t, v)
    assert not fails(r, "moving during"), r["failures"]


def test_arrival_one_tenth_of_a_nanosecond_late_is_rejected(toy_task):
    t = np.array([0, 1, 2, 3, 4, 5, 6, 7.0 + 1e-10, 10.0])
    v = np.array([0, 0, 1, 2, 1, 1, 1, 0, 0.0])
    r = validator.validate_trajectory(toy_task, t, v)
    assert fails(r, "arrival")                                     # rev0 accepted this (TOL_T = 1e-9 s)


def test_departure_one_tenth_of_a_nanosecond_early_is_rejected(toy_task):
    t = np.array([0, 1.0 - 1e-10, 2, 3, 4, 5, 6, 7, 10.0])
    v = np.array([0, 0, 1, 2, 1, 1, 1, 0, 0.0])
    r = validator.validate_trajectory(toy_task, t, v)
    assert fails(r, "departure")


def test_moving_again_after_an_early_arrival_is_rejected(toy_task, plant_m0):
    # arrives at 6 s (early), creeps at 6.5 s, stops at 7 s: the wait at the prescribed stop is not stationary
    t = np.array([0, 1, 2, 3, 4, 5, 6, 6.5, 7, 10.0])
    v = np.array([0, 0, 1, 2, 2, 1, 0, 0.0, 0, 0.0])
    ok = validator.validate_trajectory(toy_task, t, v, plant_m0)
    assert ok["valid"], ok["failures"]                             # (6.5, 0) is still at rest: valid early arrival
    v2 = v.copy()
    v2[7] = 0.1                                                    # creep at 6.5 s after arriving at 6 s
    r = validator.validate_trajectory(toy_task, t, v2, plant_m0)
    assert not r["valid"] and fails(r, "extra stop"), r["failures"]


def test_wait_speed_is_reported_per_segment(toy_task, plant_m0):
    t = np.array([0, 1, 2, 3, 4, 5, 6, 10.0])
    v = np.array([0, 0, 1, 2, 2, 1, 0, 0.0])
    r = validator.validate_trajectory(toy_task, t, v, plant_m0)
    assert r["segments"][0]["wait_max_speed_ms"] == 0.0 and r["segments"][0]["early_arrival_s"] == 1.0


def test_validator_cannot_be_satisfied_by_a_planner_flag():
    import ast
    params = list(inspect.signature(validator.validate_trajectory).parameters)
    assert params == ["task", "t", "v", "plant", "label"]
    tree = ast.parse(inspect.getsource(validator))
    imported = {a.name for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom)) for a in n.names}
    imported |= {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
    assert not any("planner" in m for m in imported), imported            # run 4 used a text search (test defect)


# ---- VC-02: 0.5 ms runs, traced every second step (protocol 10.3)
@pytest.mark.parametrize("motor", ["M0", "M2"])
def test_half_ms_loop_equals_frozen_simulate_and_traces_at_1ms(p1, motor):
    K = fixed_gain(p1)
    prof = short_profile()
    lim, mm = config.LIMITS["L-EVE"], config.motor_model(motor)
    ref = L.simulate(prof, [p1], np.array([K]), np.array([1.0]), lim, mm, dt=5e-4)
    out, tr = simulate_traced(prof, p1, K, 1.0, lim, mm, dt=5e-4)
    assert np.array_equal(ref["y_end"], out["y_end"]) and np.array_equal(ref["closure_J"], out["closure_J"])
    for k in ref["acc"]:
        assert np.array_equal(ref["acc"][k], out["acc"][k]), k
    assert out["trace_dt"] == TRACE_DT
    assert len(tr["t_s"]) == round(prof.duration / TRACE_DT) + 1
    assert np.allclose(np.diff(tr["t_s"]), 1e-3, atol=1e-12, rtol=0)
    assert tr["t_s"][-1] == pytest.approx(prof.duration, abs=1e-12)


def test_dt_that_does_not_divide_the_trace_step_is_refused(p1):
    with pytest.raises(ValueError):
        simulate_traced(short_profile(), p1, fixed_gain(p1), 1.0, config.LIMITS["L-R1"], config.motor_model("M0"),
                        dt=4e-4)


def _spec(p, lim, motor, d_ref, soh=1.0, knots=None):
    from r4h3 import campaign
    from r4h3.task import task_from_samples
    tk = task_from_samples("X", np.array([0.0, 1.0]), np.array([0.0, 0.0]))
    s = campaign.eval_spec(p, soh, lim, evaluator.motor_spec_from_protocol(motor, frozen.M1_CURVE), tk, knots)
    s.update(d_ref_m=d_ref, rest_intervals=[])
    return s


@pytest.mark.parametrize("dt", [1e-3, 5e-4])
def test_decimated_trace_is_recomputed_within_protocol_tolerances(p1, dt):
    K = fixed_gain(p1)
    prof = short_profile()
    lim = config.LIMITS["L-R1"]
    out, tr = simulate_traced(prof, p1, K, 1.0, lim, config.motor_model("M1"), dt=dt)
    d_ref = float(prof.stats()["distance_m"])
    sim = run_metrics(out, p1, 1.0, d_ref, prof.duration, p1.Ts)
    sim.update(trace_constraint_metrics(tr, p1, lim, config.RULES), stop_ok_sim=True)
    tr["v_ref_task_mps"] = tr["v_tracked_mps"]
    tr["stop_ref_flag"] = np.zeros_like(tr["t_s"])
    ev = evaluator.evaluate_trace(tr, _spec(p1, lim, "M1", d_ref, knots=(prof.knots_t, prof.knots_v)), config.RULES)
    cmp = evaluator.compare_with_simulator(ev, sim, config.RULES)
    assert cmp["protocol_ok"], {k: v for k, v in cmp.items() if isinstance(v, dict) and not v["ok"]}
    assert cmp["diagnostics_ok"], {k: v for k, v in cmp.items() if isinstance(v, dict) and not v["ok"]}
    assert "tracked_profile_abs_ms" in cmp and "closure_rel_abs" in cmp


# ---- VC-03: the evaluator refuses a trace whose spacing differs from the declared step
def test_evaluator_refuses_mismatched_trace_step(p1):
    out, tr = simulate_traced(short_profile(), p1, fixed_gain(p1), 1.0, config.LIMITS["L-R1"], config.motor_model("M0"),
                              dt=5e-4)
    tr["v_ref_task_mps"] = tr["v_tracked_mps"]
    tr["stop_ref_flag"] = np.zeros_like(tr["t_s"])
    spec = _spec(p1, config.LIMITS["L-R1"], "M0", 10.0)
    spec["dt_s"] = 5e-4                                            # the integration step, not the trace step (CR-A1)
    with pytest.raises(ValueError, match="trace sample step"):
        evaluator.evaluate_trace(tr, spec, config.RULES)


# ---- VC-04/05: only protocol-9 quantities decide crediting
def _ev_sim_pair(p1):
    K = fixed_gain(p1)
    prof = short_profile()
    lim = config.LIMITS["L-EVE"]
    out, tr = simulate_traced(prof, p1, K, 1.0, lim, config.motor_model("M0"))
    d_ref = float(prof.stats()["distance_m"])
    sim = run_metrics(out, p1, 1.0, d_ref, prof.duration, p1.Ts)
    sim.update(trace_constraint_metrics(tr, p1, lim, config.RULES), stop_ok_sim=True)
    tr["v_ref_task_mps"] = tr["v_tracked_mps"]
    tr["stop_ref_flag"] = np.zeros_like(tr["t_s"])
    ev = evaluator.evaluate_trace(tr, _spec(p1, lim, "M0", d_ref), config.RULES)
    return ev, sim


def test_diagnostic_disagreement_is_flagged_but_does_not_decide_crediting(p1):
    ev, sim = _ev_sim_pair(p1)
    sim = dict(sim, friction_brake_Wh=sim["friction_brake_Wh"] + 1e-3)
    cmp = evaluator.compare_with_simulator(ev, sim, config.RULES)
    assert cmp["protocol_ok"] and not cmp["diagnostics_ok"] and not cmp["all_ok"]
    assert cmp["friction_abs_Wh"]["group"] == "diagnostic"


@pytest.mark.parametrize("key,delta", [("E_net_Wh", 1.01), ("I_over_protocol_As", None), ("constraint_ok_sim", None),
                                       ("stop_ok_sim", None)])
def test_protocol_disagreement_decides(p1, key, delta):
    ev, sim = _ev_sim_pair(p1)
    sim = dict(sim)
    if key == "E_net_Wh":
        sim[key] *= delta
    elif key == "I_over_protocol_As":
        sim[key] += 1.0
    else:
        sim[key] = not sim[key]
    cmp = evaluator.compare_with_simulator(ev, sim, config.RULES)
    assert not cmp["protocol_ok"]


def test_protocol_check_set_matches_protocol_9_and_the_campaign_record():
    from r4h3 import campaign
    assert set(evaluator.PROTOCOL_CHECKS) == {"E_chem_rel", "E_DC_rel", "distance_rel", "trip_time_abs_s",
                                              "I_over_protocol_abs_As", "rmse_rel", "stop_ok_equal", "complete_equal",
                                              "tracking_ok_equal", "constraint_ok_equal"}
    assert config.RULES["recompute_energy_rel"] == campaign.RECOMPUTE_TOLERANCES["E_chem_rel"] == 1e-4
    assert config.RULES["recompute_distance_rel"] == campaign.RECOMPUTE_TOLERANCES["distance_rel"] == 1e-6


def test_battery_limited_fraction_is_the_r1_r3_definition(p1):
    ev, sim = _ev_sim_pair(p1)
    assert ev["batt_limited_frac"] == sim["batt_limited_frac"]
    assert "batt_limited_time_frac" not in ev and "limit_active_sample_frac" in ev


# ---- VC-07: upstream physics and data are hash-checked before r3_lib is imported
def test_upstream_inputs_are_hash_checked():
    assert frozen.verify_frozen(frozen.UPSTREAM_SHA256)
    p = next(iter(frozen.UPSTREAM_SHA256))
    with pytest.raises(frozen.FrozenInputError):
        frozen.verify_frozen({p: "0" * 64})
    assert "UPSTREAM_SHA256" in inspect.getsource(frozen.load_r3_lib)


# ---- VC-08: trace schema v2 (closure integrators); v1 stays readable
def test_v2_trace_closure_equals_simulator_and_v1_is_readable(tmp_path, p1):
    from r4h3 import SCHEMA_VERSION
    assert SCHEMA_VERSION == "r4h3-trace-v2"
    assert {"int_E_rr", "int_E_aero", "int_E_gear", "int_E_visc", "int_E_regen"} <= set(traces.CHANNELS)
    ev, sim = _ev_sim_pair(p1)
    assert ev["closure_rel_from_trace"] == pytest.approx(sim["closure_rel"], abs=1e-12)
    # a v1 file (as written by the smoke test) is still read, with its own channel list
    v1 = {k: v for k, v in traces.CHANNELS.items() if not k.startswith(("int_E_rr", "int_E_aero", "int_E_gear",
                                                                         "int_E_visc", "int_E_regen"))}
    schema = {"schema_version": "r4h3-trace-v1", "channels": [dict(name=k, unit=u, description=d, source=s)
                                                             for k, (u, d, s) in v1.items()], "required_meta": []}
    path = tmp_path / "v1.npz"
    np.savez_compressed(path, __schema__=np.array(json.dumps(schema)), __meta__=np.array(json.dumps({"run_id": "x"})),
                        **{k: np.zeros(3) for k in v1})
    a, meta, sch = traces.read_trace(path)
    assert set(a) == set(v1) and sch["schema_version"] == "r4h3-trace-v1"


# ---- P3 plumbing (review Q10): same gain, R0 law, loop identical to r3_lib at SoH 0.8
def test_gain_is_identical_at_p1_and_p3():
    assert np.array_equal(fixed_gain(config.params_for("P1")), fixed_gain(config.params_for("P3")))


def test_evaluator_r0_at_p3_equals_batchparams():
    from eureka.plant import BatchParams
    p3 = config.params_for("P3")
    soh = config.PSTATES["P3"]["soh"]
    spec = _spec(p3, config.LIMITS["L-R1"], "M0", 1.0, soh=soh)
    bp = BatchParams.from_params([p3], np.array([soh]))
    assert spec["battery"]["R0"] == float(bp.R0[0])
    assert spec["battery"]["R0"] == pytest.approx(0.005 * (1 + 3.5 * 0.2), rel=1e-15)


def test_traced_loop_equals_frozen_simulate_at_p3():
    p3 = config.params_for("P3")
    K = fixed_gain(config.params_for("P1"))
    prof = short_profile()
    lim, mm = config.LIMITS["L-R1"], config.motor_model("M1")
    ref = L.simulate(prof, [p3], np.array([K]), np.array([0.8]), lim, mm)
    out, _ = simulate_traced(prof, p3, K, 0.8, lim, mm)
    assert np.array_equal(ref["y_end"], out["y_end"])
