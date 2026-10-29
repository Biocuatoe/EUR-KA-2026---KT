"""Component E: sign convention, integration on analytic signals, independent formulas, rejection of
invalid or incomplete runs, and refusal to pool (brief tests 4, 5, 6, 9)."""

import numpy as np
import pytest

from r4h3 import config, evaluator, frozen

L = config.L
RULES = config.RULES
B = dict(V_oc=48.0, R0=0.005, Q_Ah=100.0, c_dis=3.0, c_ch=1.0, v_min_ratio=0.78125, v_max_ratio=1.140625)


# ---- 5. integration and sign convention on analytic signals
def test_trapezoid_is_exact_on_linear_and_known_signals():
    t = np.linspace(0.0, 3.6, 3601)
    assert evaluator._trapz(np.full_like(t, 1000.0), t) / 3600.0 == pytest.approx(1.0, rel=1e-12)   # 1 kW x 3.6 s
    assert evaluator._trapz(2.0 * t + 1.0, t) == pytest.approx(3.6 ** 2 + 3.6, rel=1e-12)
    ts = np.linspace(0.0, 2 * np.pi, 200001)
    assert evaluator._trapz(np.sin(ts), ts) == pytest.approx(0.0, abs=1e-9)                      # full period
    assert evaluator._trapz(np.maximum(np.sin(ts), 0), ts) == pytest.approx(2.0, rel=1e-8)


def test_battery_current_sign_convention():
    motor = {"kind": "const", "eta": 0.874}
    i_drive, *_ = evaluator.battery_current(np.array([50.0]), np.array([100.0]), np.array([0.0]), B, motor)
    i_regen, *_ = evaluator.battery_current(np.array([-50.0]), np.array([100.0]), np.array([0.0]), B, motor)
    i_zero, *_ = evaluator.battery_current(np.array([0.0]), np.array([100.0]), np.array([0.0]), B, motor)
    assert i_drive[0] > 0 > i_regen[0] and i_zero[0] == 0.0
    # power balance V_oc i - R0 i^2 = p_e, with p_e = p_m / eta (motoring) and p_m eta (regenerating)
    for i, p_e in ((i_drive[0], 5000 / 0.874), (i_regen[0], -5000 * 0.874)):
        assert 48.0 * i - 0.005 * i * i == pytest.approx(p_e, rel=1e-12)


def test_net_energy_signs_and_parts():
    t = np.linspace(0.0, 10.0, 10001)
    i = 50.0 * np.sin(2 * np.pi * t / 10.0)
    e_pos = evaluator._trapz(np.maximum(48 * i, 0), t)
    e_neg = evaluator._trapz(np.minimum(48 * i, 0), t)
    assert e_pos > 0 > e_neg
    assert e_pos + e_neg == pytest.approx(evaluator._trapz(48 * i, t), abs=1e-9)
    assert e_pos + e_neg == pytest.approx(0.0, abs=1e-6)


# ---- 6. independent formulas agree with the frozen simulator functions
@pytest.mark.parametrize("sid", ["M0", "M1", "M2"])
def test_independent_current_formula_equals_r3_lib(p1, sid):
    from eureka.plant import BatchParams
    rng = np.random.default_rng(1)
    T = rng.uniform(-85, 85, 500)
    w = rng.uniform(0, 600, 500)
    V1 = rng.uniform(-0.2, 0.2, 500)
    bp = BatchParams.from_params([p1] * 500, np.ones(500))
    i_ref, pe_ref, _, ok_ref = L.battery_current(T, w, V1, bp, config.motor_model(sid))
    spec = evaluator.motor_spec_from_protocol(sid, frozen.M1_CURVE)
    i, pe, ok = evaluator.battery_current(T, w, V1, B, spec)
    assert np.allclose(i, i_ref, rtol=1e-12, atol=1e-12) and np.array_equal(ok, ok_ref)


def test_independent_window_limits_equal_r3_lib(p1):
    from eureka.plant import BatchParams
    from rebuild.model import battery_limits
    V1 = np.linspace(-1.0, 1.0, 11)
    bp = BatchParams.from_params([p1] * 11, np.ones(11))
    for name, lim in config.LIMITS.items():
        i_d, i_c, _, _ = battery_limits(V1, bp, lim)
        b = dict(B, c_dis=lim.c_dis, c_ch=lim.c_ch)
        e_d, e_c = evaluator.window_limits(V1, b)
        assert np.allclose(e_d, i_d, rtol=1e-12) and np.allclose(e_c, i_c, rtol=1e-12), name


# ---- 4. invalid or incomplete runs are flagged, never credited
def synthetic_trace(v, v_track, T, dt=0.001, Ts=0.01):
    n = len(v)
    t = np.arange(n) * dt
    G_rw = 6.5 / 0.28
    z = np.zeros(n)
    return dict(t_s=t, v_mps=v, v_tracked_mps=v_track, v_ref_task_mps=v_track, T_Nm=T, w_radps=G_rw * np.maximum(v, 0),
                V1_V=z, i_A=z, P_regen_wheel_W=z, P_fric_W=z, limit_active=z, u_cmd_Nm=z, t_neg_Nm=z)


def spec(d_ref, rest=()):
    return {"battery": B, "motor": {"kind": "const", "eta": 0.874}, "G": 6.5, "r_w": 0.28, "v_eps": 0.05, "Ts_s": 0.01, "dt_s": 0.001,
            "d_ref_m": d_ref, "rest_intervals": [list(r) for r in rest]}


def run_eval(v, v_track, T, d_ref, rest=()):
    a = synthetic_trace(v, v_track, T)
    i, *_ = evaluator.battery_current(a["T_Nm"], a["w_radps"], a["V1_V"], B, {"kind": "const", "eta": 0.874})
    a["i_A"] = i
    return evaluator.evaluate_trace(a, spec(d_ref, rest), RULES)


def test_shortfall_above_0p1_percent_is_incomplete():
    v = np.full(10001, 1.0)                                         # 10 m in 10 s
    assert run_eval(v, v, np.zeros_like(v), 10.0)["complete"]
    ev = run_eval(v, v, np.zeros_like(v), 10.0 / 0.998)             # 0.2 % short
    assert not ev["complete"] and ev["shortfall_pct"] == pytest.approx(0.2, rel=1e-6)


def test_tracking_breach_is_flagged():
    v = np.full(10001, 1.0)
    ev = run_eval(v, v + 0.2, np.zeros_like(v), 10.0)
    assert not ev["tracking_ok"] and ev["rmse_ms"] == pytest.approx(0.2)


def test_stop_window_breach_is_flagged_but_settling_is_allowed():
    n = 10001
    t = np.arange(n) * 0.001
    v = np.zeros(n)
    v[(t > 2.0) & (t < 2.5)] = 0.3                                  # inside the first second: allowed
    ok = run_eval(v, np.zeros(n), np.zeros(n), 1.0, rest=[(2.0, 10.0)])
    assert ok["stop_ok"]
    v[(t > 5.0) & (t < 6.0)] = 0.06                                 # creep after settling: breach
    bad = run_eval(v, np.zeros(n), np.zeros(n), 1.0, rest=[(2.0, 10.0)])
    assert not bad["stop_ok"]
    short = run_eval(v, np.zeros(n), np.zeros(n), 1.0, rest=[(5.0, 6.5)])
    assert short["stop_rows"][0]["tested"] is False                 # < 2 s standstills are reported, not tested


def test_current_limit_breach_is_flagged():
    v = np.full(10001, 8.0)
    ev = run_eval(v, v, np.full_like(v, 85.0), 80.0)                # about 85 N m x 186 rad/s -> > 300 A
    assert ev["I_over_protocol_As"] > RULES["i_over_max_As"] and not ev["constraint_ok"]


def test_comparison_detects_disagreement():
    v = np.full(10001, 1.0)
    ev = run_eval(v, v, np.full_like(v, 5.0), 10.0)
    sim = dict(E_net_Wh=ev["E_chem_Wh"] * 1.01, E_DC_Wh=ev["E_DC_Wh"], E_pos_Wh=ev["E_pos_Wh"],
               friction_brake_Wh=ev["friction_brake_Wh"], distance_km=ev["distance_m"] / 1000, trip_time_s=ev["trip_time_s"],
               rmse_ms=ev["rmse_ms"], max_abs_err_ms=ev["max_abs_err_ms"], I_over_As=ev["I_over_window_As"],
               stop_ok_sim=ev["stop_ok"])
    cmp = evaluator.compare_with_simulator(ev, sim, RULES)
    assert not cmp["all_ok"] and not cmp["E_chem_rel"]["ok"]
    sim["E_net_Wh"] = ev["E_chem_Wh"]
    assert evaluator.compare_with_simulator(ev, sim, RULES)["all_ok"]


# ---- 9. scenarios are never pooled
def test_pooling_across_motor_scenarios_is_refused():
    rows = [dict(motor_scenario="M0", cycle="S1", limits="L-R1", pstate="P1"),
            dict(motor_scenario="M1", cycle="S1", limits="L-R1", pstate="P1")]
    with pytest.raises(ValueError):
        evaluator.refuse_pooling(rows)
    assert evaluator.refuse_pooling(rows[:1]) == ("M0", "S1", "L-R1", "P1")
