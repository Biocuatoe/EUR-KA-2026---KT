"""Plant verification: forces, equilibrium, coast-down, energy balance, integrator accuracy.

Each test checks one property against an independent reference (hand formula, closed-form
solution, or a different integrator). Passing proves that property only, not that the
model represents a real vehicle.
"""

import math

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from scipy.integrate import solve_ivp

from eureka.params import load_params
from eureka.plant import (
    IX,
    STATES,
    BatchParams,
    derivatives,
    energy_closure,
    initial_state,
    rk4_step,
)

P = load_params()


def batch(soh=1.0, p=P):
    return BatchParams.from_params([p], np.array([soh]))


def state(v=0.0, T=0.0, V1=0.0):
    y = initial_state(1)
    y[0, IX["v"]], y[0, IX["T"]], y[0, IX["V1"]] = v, T, V1
    return y


def test_resistance_forces_match_hand_calculation():
    v = 10.0
    _, aux = derivatives(state(v), np.array([0.0]), batch())
    dy, _ = derivatives(state(v), np.array([0.0]), batch())
    f_aero = 0.5 * 1.225 * 0.35 * 2.2 * v**2  # 47.16 N
    f_rr = 0.008 * 850 * 9.81 * math.tanh(v / 0.05)  # 66.71 N
    assert dy[0, IX["E_aero"]] == pytest.approx(f_aero * v, rel=1e-12)
    assert dy[0, IX["E_rr"]] == pytest.approx(f_rr * v, rel=1e-12)
    assert aux["f_fb"][0] == 0.0


def test_effective_mass_includes_reflected_rotor_inertia():
    assert P.M_eff == pytest.approx(850 + 0.05 * 6.5**2 / 0.28**2)  # 876.945 kg


def test_steady_speed_torque_equilibrium():
    v = 12.0
    w = P.G * v / P.r_w
    load = 0.008 * 850 * 9.81 * math.tanh(v / 0.05) + 0.5 * 1.225 * 0.35 * 2.2 * v**2
    t_star = load * P.r_w / (P.G * P.eta_g) + P.B_m * w
    dy, _ = derivatives(state(v, t_star), np.array([t_star]), batch())
    assert abs(dy[0, IX["v"]]) < 1e-12
    assert abs(dy[0, IX["T"]]) < 1e-12


def coastdown_closed_form(v0, t, p=P):
    """M_eff v' = -(F0 + c v + k v^2), valid while tanh(v / v_eps) == 1 to machine precision."""
    f0 = p.Crr * p.M * p.g
    c = p.B_m * p.G**2 / (p.eta_g * p.r_w**2)  # shaft friction reflected through the gearbox
    k = 0.5 * p.rho * p.Cd * p.A_f
    al, be, ga = f0 / p.M_eff, c / p.M_eff, k / p.M_eff
    s = math.sqrt(4 * al * ga - be**2)
    return (s * np.tan(np.arctan((2 * ga * v0 + be) / s) - s * t / 2) - be) / (2 * ga)


def test_coastdown_matches_closed_form():
    y = state(v=13.0)
    bp = batch()
    t_end, h = 20.0, P.dt
    for _ in range(round(t_end / h)):
        y, _ = rk4_step(y, np.array([0.0]), bp, h)
    expected = coastdown_closed_form(13.0, t_end)
    assert expected > 2.0  # stays in the region where tanh(v/v_eps) == 1
    assert y[0, IX["v"]] == pytest.approx(expected, rel=1e-9)


def test_rk4_matches_adaptive_high_order_solver():
    bp = batch(soh=0.8)
    t_ref = np.array([40.0])  # passes through the power-limit corner at 9.12 m/s
    y = state()
    t_end = 15.0
    for _ in range(round(t_end / P.dt)):
        y, _ = rk4_step(y, t_ref, bp, P.dt)

    def f(_t, yy):
        dy, _ = derivatives(yy.reshape(1, -1), t_ref, bp)
        return dy[0]

    sol = solve_ivp(
        f, (0, t_end), state()[0], method="DOP853", rtol=1e-10, atol=1e-10, max_step=0.01
    )
    for name in ("v", "T", "V1", "E_chem", "dist", "E_R0"):
        assert y[0, IX[name]] == pytest.approx(sol.y[IX[name], -1], rel=1e-6, abs=1e-8), name


def test_power_and_torque_limits_applied_to_command():
    v = 13.0  # above base speed
    w = P.G * v / P.r_w
    dy, aux = derivatives(state(v, 0.0), np.array([1000.0]), batch())
    assert aux["t_lim"][0] == pytest.approx(P.P_max / w)
    assert dy[0, IX["T"]] == pytest.approx(P.P_max / w / P.tau_T)
    dy, _ = derivatives(state(2.0, 0.0), np.array([1000.0]), batch())
    assert dy[0, IX["T"]] == pytest.approx(P.T_max / P.tau_T)


def test_friction_brake_takes_braking_beyond_motor_limit():
    v = 10.0
    w = P.G * v / P.r_w
    t_lim = min(P.T_max, P.P_max / w)
    _, aux = derivatives(state(v, -t_lim), np.array([-200.0]), batch())
    assert aux["f_fb"][0] == pytest.approx(P.G / P.r_w * (200.0 - t_lim) * math.tanh(v / 0.05))


def test_vehicle_never_reverses_at_standstill():
    dy, _ = derivatives(state(0.0, -50.0), np.array([-50.0]), batch())
    assert dy[0, IX["v"]] == 0.0


def test_soh_increases_battery_resistance_as_in_report_eq_4_28():
    bp = BatchParams.from_params([P, P], np.array([1.0, 0.8]))
    assert bp.R0[0] == pytest.approx(0.005)
    assert bp.R0[1] == pytest.approx(0.005 * (1 + 0.5 * 0.2))
    assert bp.R1[1] == pytest.approx(0.003 * (1 + 0.3 * 0.2))


@settings(max_examples=200, deadline=None)
@given(
    v=st.floats(0.0, 20.0),
    T=st.floats(-85.0, 85.0),
    V1=st.floats(-1.0, 1.0),
    t_ref=st.floats(-300.0, 300.0),
    soh=st.floats(0.5, 1.0),
)
def test_loss_rates_are_never_negative(v, T, V1, t_ref, soh):
    dy, aux = derivatives(state(v, T, V1), np.array([t_ref]), batch(soh))
    assert aux["feasible"][0]
    for name in ("E_rr", "E_aero", "E_fb", "E_gear", "E_visc", "E_mi", "E_R0", "E_R1"):
        assert dy[0, IX[name]] >= -1e-9, name


@settings(max_examples=25, deadline=None)
@given(
    torques=st.lists(st.floats(-120.0, 120.0), min_size=3, max_size=3),
    soh=st.floats(0.5, 1.0),
)
def test_energy_balance_closes_for_arbitrary_torque_sequences(torques, soh):
    bp = batch(soh)
    y = state(v=5.0)
    y0 = y.copy()
    for t_ref in torques:  # 0.5 s per torque level
        for _ in range(500):
            y, feasible = rk4_step(y, np.array([t_ref]), bp, P.dt)
            assert feasible[0]
    c = energy_closure(y, y0, bp)
    throughput = abs(c["supplied_J"][0]) + 0.5 * P.M_eff * 25.0 + 1.0
    assert abs(c["abs_J"][0]) / throughput < 1e-6


def test_state_layout_is_stable():
    assert STATES[:4] == ("v", "T", "V1", "SoC")
