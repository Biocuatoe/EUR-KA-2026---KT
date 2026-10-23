"""Controller verification: design model, DARE gains, stability, schedule, anti-windup."""

import control
import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from eureka.controllers import bryson_weights, design_model, dlqr, gain, scheduled_weights, zoh
from eureka.cycles import build
from eureka.params import load_params
from eureka.plant import IX, BatchParams, derivatives, initial_state
from eureka.simulate import simulate

P = load_params()
AD, BD = zoh(*design_model(P), P.Ts)


def test_design_model_matches_finite_difference_linearisation_of_plant():
    A, B = design_model(P)
    bp = BatchParams.from_params([P], np.array([1.0]))
    v0 = P.v0
    w0 = P.G * v0 / P.r_w
    load = P.Crr * P.M * P.g + 0.5 * P.rho * P.Cd * P.A_f * v0**2
    t0 = load * P.r_w / (P.G * P.eta_g) + P.B_m * w0

    def dv(v, T):
        y = initial_state(1)
        y[0, IX["v"]], y[0, IX["T"]] = v, T
        return derivatives(y, np.array([T]), bp)[0][0, IX["v"]]

    h = 1e-4
    assert (dv(v0 + h, t0) - dv(v0 - h, t0)) / (2 * h) == pytest.approx(A[0, 0], rel=1e-4)
    assert (dv(v0, t0 + h) - dv(v0, t0 - h)) / (2 * h) == pytest.approx(A[0, 1], rel=1e-6)
    assert B[1, 0] == pytest.approx(1 / P.tau_T)


def test_zoh_matches_python_control():
    A, B = design_model(P)
    sysd = control.c2d(control.ss(A, B, np.eye(3), np.zeros((3, 1))), P.Ts, method="zoh")
    np.testing.assert_allclose(AD, sysd.A, rtol=1e-12, atol=1e-14)
    np.testing.assert_allclose(BD, sysd.B, rtol=1e-12, atol=1e-14)


def test_design_model_is_controllable():
    assert np.linalg.matrix_rank(control.ctrb(AD, BD)) == 3


def value_iteration_gain(Ad, Bd, Q, R, iters=200000, tol=1e-13):
    """Independent DARE solution: iterate the Riccati recursion to its fixed point."""
    P_ = Q.copy()
    for _ in range(iters):
        K = np.linalg.solve(R + Bd.T @ P_ @ Bd, Bd.T @ P_ @ Ad)
        P_new = Q + Ad.T @ P_ @ (Ad - Bd @ K)
        if np.max(np.abs(P_new - P_)) <= tol * np.max(np.abs(P_new)):
            return K
        P_ = P_new
    raise RuntimeError("value iteration did not converge")


def test_dare_gain_matches_value_iteration_and_python_control():
    Q, R = bryson_weights(P)
    K, _, _ = dlqr(AD, BD, Q, R)
    np.testing.assert_allclose(K, value_iteration_gain(AD, BD, Q, R), rtol=1e-6)
    K_ctrl, _, _ = control.dlqr(AD, BD, Q, R)
    np.testing.assert_allclose(K, K_ctrl, rtol=1e-8)


def test_closed_loop_poles_inside_unit_circle_python_control():
    K = gain(P, "fixed")
    poles = control.ss(AD - BD @ K, BD, np.eye(3), np.zeros((3, 1)), P.Ts).poles()
    assert np.max(np.abs(poles)) < 1.0


def test_scheduled_equals_fixed_at_full_soh():
    np.testing.assert_array_equal(gain(P, "scheduled", soh=1.0), gain(P, "fixed"))


def test_schedule_follows_report_equations():
    Q0, R0 = bryson_weights(P)
    Q, R = scheduled_weights(Q0, R0, soh=0.8, gamma_v=1.0, gamma_u=1.0)
    assert Q[1, 1] == pytest.approx(Q0[1, 1] / 1.2)
    assert Q[0, 0] == Q0[0, 0]
    assert Q[2, 2] == Q0[2, 2]
    assert R[0, 0] == pytest.approx(R0[0, 0] * 1.2)


@settings(max_examples=100, deadline=None)
@given(soh=st.floats(0.5, 1.0), gv=st.floats(0.0, 10.0), gu=st.floats(0.0, 10.0))
def test_frozen_time_schedule_is_always_stabilising(soh, gv, gu):
    Q0, R0 = bryson_weights(P)
    Q, R = scheduled_weights(Q0, R0, soh, gv, gu)
    K, P_, eig = dlqr(AD, BD, Q, R)
    assert np.max(np.abs(eig)) < 1.0
    assert np.all(np.linalg.eigvalsh((P_ + P_.T) / 2) > 0)


def test_anti_windup_freezes_integrator_while_traction_limited():
    # A request of 3 m/s^2 to 45 km/h exceeds what 85 Nm / 18 kW can deliver.
    prof = build("windup", [{"idle": 1}, {"accel": 3.0, "to_kmh": 45}, {"cruise": 10}])
    out = simulate(prof, [P], gain(P, "fixed"), np.array([1.0]))
    sat = out["sat"][:, 0].astype(bool)
    e = out["v"][:, 0] - out["v_ref"][:, 0]
    frozen = sat[:-1] & (e[:-1] < 0)
    assert frozen.sum() > 50
    dz = np.diff(out["z"][:, 0])
    np.testing.assert_array_equal(dz[frozen], 0.0)
    assert np.all(dz[~frozen] == pytest.approx(P.Ts * e[:-1][~frozen], abs=1e-12))
