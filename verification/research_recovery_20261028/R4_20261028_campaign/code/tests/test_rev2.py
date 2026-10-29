"""Rev2 (owner decisions AMB-14/15/24; tolerance register; independent torque limits VC-09)."""

import numpy as np
import pytest

from r4h3 import campaign, config, evaluator, frozen
from r4h3.closedloop import fixed_gain, profile_from_knots, run_metrics, simulate_traced, trace_constraint_metrics

L = config.L


def bat(pstate="P1", limits="L-R1"):
    p, lim = config.params_for(pstate), config.LIMITS[limits]
    soh = config.PSTATES[pstate]["soh"]
    return dict(V_oc=p.V_oc, R0=p.R0_new * (1 + p.k_r0 * (1 - soh)), Q_Ah=p.Q_Ah, c_dis=lim.c_dis, c_ch=lim.c_ch,
                v_min_ratio=lim.v_min_ratio, v_max_ratio=lim.v_max_ratio)


M0 = {"sid": "M0", "kind": "const", "eta": 0.874}


# ---- D: analytically checkable boundary cases (P1, L-R1, M0, V1 = 0)
# i_d = min(3C = 300 A, (48 - 37.5)/0.005 = 2100 A, 48/(2*0.005) = 4800 A) = 300 A -> p_d = (48 - 0.005*300)*300 = 13950 W
# P_m,drive = 0.874 * 13950 = 12192.3 W; base = min(85, 18000 / w); battery limit equals 85 N m at w_b = 12192.3/85
P_D, P_M = 13950.0, 0.874 * 13950.0
W_B = P_M / 85.0
W_CORNER = 18000.0 / 85.0


@pytest.mark.parametrize("w,expected", [
    (100.0, 85.0),                       # below the battery boundary: motor torque limit binds
    (W_B, 85.0),                         # at the boundary: both equal 85
    (180.0, P_M / 180.0),                # above it (still below the corner speed): battery binds
    (W_CORNER, P_M / W_CORNER),          # at the motor corner speed: battery (57.6) below base (85)
    (300.0, P_M / 300.0),                # above the corner: battery (40.6) below P_max/w (60)
    (0.0, 85.0),                         # standstill: speed floor, motor limit binds
])
def test_drive_limit_boundaries(w, expected):
    t_pos, _, base = evaluator.torque_limits(np.array([w]), np.array([0.0]), bat(), M0, 85.0, 18000.0)
    assert t_pos[0] == pytest.approx(expected, rel=1e-13)
    assert base[0] == pytest.approx(min(85.0, 18000.0 / max(w, 1e-6)), rel=1e-15)
    p_d, p_c = evaluator.battery_power_limits(np.array([0.0]), bat())
    assert p_d[0] == pytest.approx(P_D, rel=1e-15) and p_c[0] == pytest.approx((48 + 0.005 * 100) * 100, rel=1e-15)


def test_regen_limit_and_voltage_window_cases():
    # charge: i_c = min(1C = 100 A, (54.75 - 48)/0.005 = 1350 A) = 100 A -> p_c = 4850 W; P_m,brake = 4850 / 0.874
    _, t_neg, _ = evaluator.torque_limits(np.array([200.0]), np.array([0.0]), bat(), M0, 85.0, 18000.0)
    assert t_neg[0] == pytest.approx(4850.0 / 0.874 / 200.0, rel=1e-13)
    # voltage window binding: V1 = 10 V -> vo = 38 V, i_v = (38 - 37.5)/0.005 = 100 A < 300 A -> p_d = 37.5*100
    p_d, _ = evaluator.battery_power_limits(np.array([10.0]), bat())
    assert p_d[0] == pytest.approx(3750.0, rel=1e-13)
    t_pos, _, _ = evaluator.torque_limits(np.array([100.0]), np.array([10.0]), bat(), M0, 85.0, 18000.0)
    assert t_pos[0] == pytest.approx(0.874 * 3750.0 / 100.0, rel=1e-13)


def test_copper_and_curve_inverses_satisfy_the_forward_law():
    w = np.array([100.0, 150.0, 400.0])          # 4 k_c p_c / w^2 <= 1 needs w >= 65.7 rad/s for p_c = 3000 W
    m2 = evaluator.motor_spec_from_protocol("M2", frozen.M1_CURVE)
    _, pc_hi = evaluator.mech_power_limits(np.ones(1), np.full(1, 3000.0), np.array([50.0]), m2)
    assert np.isinf(pc_hi[0])                     # beyond the copper model's maximum return: unbounded, as declared
    pd, pc = evaluator.mech_power_limits(np.full(3, 9000.0), np.full(3, 3000.0), w, m2)
    assert np.allclose(pd + m2["k_c"] * (pd / w) ** 2, 9000.0, rtol=1e-12)
    assert np.allclose(pc - m2["k_c"] * (pc / w) ** 2, 3000.0, rtol=1e-12)
    m1 = evaluator.motor_spec_from_protocol("M1", frozen.M1_CURVE)
    grid = np.linspace(0.0, 1.5 * m1["p_rated"], 20001)
    drive = grid + evaluator.motor_loss(m1, grid, np.zeros(1))
    regen = grid - evaluator.motor_loss(m1, -grid, np.zeros(1))
    assert np.all(np.diff(drive) > 0) and np.all(np.diff(regen) > 0)      # bisection precondition (monotone)
    target = np.array([500.0, 6000.0, 15000.0])
    pd, pc = evaluator.mech_power_limits(target, target, np.ones(3), m1)
    f = lambda x: x + evaluator.motor_loss(m1, x, np.zeros(1))            # noqa: E731
    assert np.all(f(pd) <= target) and np.all(f(pd + 1e-9) > target - 1e-9)
    assert np.allclose(f(pd), target, rtol=1e-12)


@pytest.mark.parametrize("pstate", ["P1", "P3"])
@pytest.mark.parametrize("limits", ["L-R1", "L-EVE"])
@pytest.mark.parametrize("sid", ["M0", "M1", "M2"])
def test_independent_limits_agree_with_r3_lib_within_the_diagnostic_tolerance(pstate, limits, sid):
    from eureka.plant import BatchParams
    rng = np.random.default_rng(7)
    w = np.concatenate([rng.uniform(0, 700, 4000), [0.0, 1e-7, W_B, W_CORNER, 837.0]])
    V1 = rng.uniform(-0.5, 0.5, len(w))
    p = config.params_for(pstate)
    bp = BatchParams.from_params([p], np.array([config.PSTATES[pstate]["soh"]]))
    tp, tn, base = L.torque_limits(w, V1, bp, config.LIMITS[limits], config.motor_model(sid))
    m = evaluator.motor_spec_from_protocol(sid, frozen.M1_CURVE)
    op, on, ob = evaluator.torque_limits(w, V1, bat(pstate, limits), m, p.T_max, p.P_max)
    tol = evaluator.TORQUE_LIMIT_TOL[m["kind"]]
    assert np.max(np.abs(tp - op)) <= tol and np.max(np.abs(tn - on)) <= tol and np.array_equal(base, ob)


def test_the_limit_check_detects_a_wrong_input():
    from eureka.plant import BatchParams
    w, V1 = np.linspace(50, 600, 200), np.zeros(200)
    p = config.params_for("P1")
    tp, _, _ = L.torque_limits(w, V1, BatchParams.from_params([p], np.ones(1)), config.LIMITS["L-R1"],
                               config.motor_model("M0"))
    wrong = dict(bat(), R0=0.0075)                                         # R0 of a different plant state
    op, _, _ = evaluator.torque_limits(w, V1, wrong, M0, p.T_max, p.P_max)
    assert np.max(np.abs(tp - op)) > 1e3 * evaluator.TORQUE_LIMIT_TOL["const"]


def test_evaluator_uses_its_own_limits_not_the_traced_ones(p1):
    out, tr = simulate_traced(profile_from_knots("s", [0, 0.5, 2, 3, 4], [0, 0, 3, 3, 0]), p1, fixed_gain(p1), 1.0,
                              config.LIMITS["L-R1"], config.motor_model("M1"))
    tr["v_ref_task_mps"] = tr["v_tracked_mps"]
    tr["stop_ref_flag"] = np.zeros_like(tr["t_s"])
    spec = _spec(p1, "L-R1", "M1", 6.0)
    ev = evaluator.evaluate_trace(tr, spec, config.RULES)
    tampered = dict(tr, t_neg_Nm=tr["t_neg_Nm"] + 5.0, t_pos_Nm=tr["t_pos_Nm"] + 5.0)
    ev2 = evaluator.evaluate_trace(tampered, spec, config.RULES)
    assert ev2["friction_brake_Wh"] == ev["friction_brake_Wh"] and ev2["batt_limited_frac"] == ev["batt_limited_frac"]
    assert ev2["torque_limit_neg_max_abs_diff_Nm"] == pytest.approx(5.0, abs=1e-5)


def _spec(p, limits, sid, d_ref, soh=1.0):
    from r4h3.task import task_from_samples
    tk = task_from_samples("X", np.array([0.0, 1.0]), np.array([0.0, 0.0]))
    s = campaign.eval_spec(p, soh, config.LIMITS[limits], evaluator.motor_spec_from_protocol(sid, frozen.M1_CURVE), tk)
    s.update(d_ref_m=d_ref, rest_intervals=[])
    return s


# ---- C: evidence behind the three A1-12 tolerances
@pytest.mark.parametrize("sid", ["M0", "M1", "M2"])
@pytest.mark.parametrize("limits", ["L-R1", "L-EVE"])
def test_forced_overcurrent_i_over_agrees_far_inside_the_tolerance(sid, limits):
    """A 2 m/s^2 ramp on a 15 Ah pack exceeds the C-rate limit (I_over > 0.01 A s), so agreement is tested on a
    non-zero quantity. The bound |dI_over| <= T max|di| is far below 1e-6 A s."""
    p = config.params_for("P1").with_overrides(Q_Ah=15.0)
    lim = config.LIMITS[limits]
    prof = profile_from_knots("hard", [0, 0.2, 3.0, 4.0, 6.0], [0, 0, 6.0, 6.0, 0])
    out, tr = simulate_traced(prof, p, fixed_gain(config.params_for("P1")), 1.0, lim, config.motor_model(sid))
    sim = run_metrics(out, p, 1.0, float(prof.stats()["distance_m"]), prof.duration, p.Ts)
    sim.update(trace_constraint_metrics(tr, p, lim, config.RULES), stop_ok_sim=True)
    tr["v_ref_task_mps"] = tr["v_tracked_mps"]
    tr["stop_ref_flag"] = np.zeros_like(tr["t_s"])
    ev = evaluator.evaluate_trace(tr, _spec(p, limits, sid, float(prof.stats()["distance_m"])), config.RULES)
    assert sim["I_over_protocol_As"] > config.RULES["i_over_max_As"]
    d = abs(ev["I_over_protocol_As"] - sim["I_over_protocol_As"])
    assert d <= prof.duration * max(ev["current_max_abs_diff_A"], 1e-12) + 1e-15
    assert d < 1e-3 * evaluator.PROTOCOL_TOLERANCES["I_over_protocol_abs_As"]
    cmp = evaluator.compare_with_simulator(ev, sim, config.RULES)
    assert cmp["I_over_protocol_abs_As"]["ok"] and cmp["constraint_ok_equal"]["ok"] and not ev["constraint_ok"]


@pytest.mark.parametrize("T_ref,dt", [(213.0, 1e-3), (324.0, 1e-3), (213.0, 5e-4), (324.0, 5e-4)])
def test_trip_time_float_error_bound(T_ref, dt):
    """Trace time = step * dt (one multiplication); its error against T_ref is a few units in the last place."""
    steps = round(T_ref / 0.01) * round(0.01 / dt)
    t_last = steps * dt
    assert abs(t_last - T_ref) <= 1e-13 < 1e-4 * evaluator.PROTOCOL_TOLERANCES["trip_time_abs_s"]


@pytest.mark.parametrize("n", [21301, 32401])
def test_rmse_summation_order_error_bound(n):
    """Simulator: sequential sum of e^2; evaluator: numpy pairwise mean. Relative difference <= (n - 1) * 2^-53."""
    rng = np.random.default_rng(n)
    e = rng.normal(0.0, 0.05, n) * rng.uniform(0, 3, n)
    seq = 0.0
    for x in e:
        seq += x * x
    a, b = np.sqrt(seq / n), float(np.sqrt(np.mean(e * e)))
    bound = (n - 1) * 2.0 ** -53
    assert abs(a - b) / b <= bound < 1e-2 * evaluator.PROTOCOL_TOLERANCES["rmse_rel"]


# ---- B: S2 numerical checks have predetermined consequences; only release checks can stop
def test_numerical_check_plan():
    names = [c["name"] for c in campaign.NUMERICAL_CHECKS]
    assert names == campaign.IMPLEMENTED["numerical_check_order"]
    assert [c["order"] for c in campaign.NUMERICAL_CHECKS] == list(range(1, len(names) + 1))
    stops = {c["name"] for c in campaign.NUMERICAL_CHECKS if c["on_fail"].startswith("STOP")}
    assert stops == {"frozen_and_input_hashes", "planner_unit_tests", "infrastructure_readiness"}
    s2 = {c["name"] for c in campaign.NUMERICAL_CHECKS if "S2" in c["data"]}
    assert s2 and not s2 & stops                                      # no S2 check is a release gate
    assert campaign.numerical_check_consequence("planner_grid_convergence", False).startswith("GO: results stated")
    assert campaign.numerical_check_consequence("qs_vs_dynamic", False).startswith("GO: that motor branch is INCONCLUSIVE")
    assert campaign.numerical_check_consequence("dynamic_time_step", True) == "pass"
    blockers = " ".join(campaign.preconditions("readiness"))
    assert "S2" not in blockers


# ---- F: approval record requirements (no approval is written by the code)
def test_approval_record_requirements():
    review = {"pending_owner_acceptance": ["CR-A6 residual"]}
    good = dict(approved_by="owner", date="2026-11-01", amendment_sha256="ab" * 32, accepted_review_items=["CR-A6 residual"],
                approved_tolerances=dict(campaign.RECOMPUTE_TOLERANCES))
    assert campaign.approval_problems(good, "ab" * 32, review) == []
    assert campaign.approval_problems(dict(good, amendment_sha256="cd" * 32), "ab" * 32, review)
    assert campaign.approval_problems(dict(good, accepted_review_items=[]), "ab" * 32, review)
    assert campaign.approval_problems(dict(good, approved_tolerances={}), "ab" * 32, review)
    assert campaign.approval_problems(dict(good, approved_by=""), "ab" * 32, review)


def test_campaign_authorisation_is_separate_from_protocol_approval():
    """VC-14: campaign mode needs an owner-written authorisation naming the issued amendment and the release gate."""
    good = dict(authorized_by="owner", date="2026-11-01", scope=campaign.AUTHORIZATION_SCOPE,
                amendment_sha256="ab" * 32, pre_run_hashes_sha256="cd" * 32)
    assert campaign.authorization_problems(good, "ab" * 32, "cd" * 32) == []
    assert campaign.authorization_problems(dict(good, scope="approve the amendment"), "ab" * 32, "cd" * 32)
    assert campaign.authorization_problems(dict(good, pre_run_hashes_sha256="ef" * 32), "ab" * 32, "cd" * 32)
    assert campaign.authorization_problems(dict(good, amendment_sha256="ef" * 32), "ab" * 32, "cd" * 32)
    assert campaign.authorization_problems(dict(good, authorized_by=""), "ab" * 32, "cd" * 32)
    assert campaign.authorization_problems(good, "ab" * 32, None)
    if not campaign.CAMPAIGN_AUTHORIZATION.exists():
        assert any("no campaign authorisation record" in b for b in campaign.preconditions("campaign"))


def test_readiness_gates_are_versioned():
    """State-aware (release attempt 1 failed here: the release directory has no readiness gate yet)."""
    latest, nxt = campaign.latest_readiness_gate(), campaign.next_readiness_gate()
    assert not nxt.exists()
    if latest.exists():
        assert campaign._gate_version(nxt) == campaign._gate_version(latest) + 1
    else:
        assert nxt == latest and nxt.name == "readiness_gate_v1.json"


def test_schedule_is_still_170_unique_official_runs():
    v = campaign.validate_schedule(campaign.build_schedule())
    assert v["passed"] and v["n_runs"] == 170
