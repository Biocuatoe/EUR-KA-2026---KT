"""Component A: trajectory validation (brief tests 1-3; protocol 3, 5, 9a)."""

import numpy as np

from r4h3 import config, validator

L = config.L


def fails(res, text):
    return any(text in f for f in res["failures"])


def test_exact_reference_is_valid(toy_task, toy2_task, plant_m0):
    for tk in (toy_task, toy2_task):
        r = validator.validate_trajectory(tk, tk.t, tk.v_ref, plant_m0)
        assert r["valid"], r["failures"]


# ---- 1. distance and duration
def test_shortened_distance_is_rejected(toy_task):
    r = validator.validate_trajectory(toy_task, toy_task.t, 0.9 * toy_task.v_ref)
    assert not r["valid"] and fails(r, "distance")


def test_shortened_duration_is_rejected(toy_task):
    r = validator.validate_trajectory(toy_task, toy_task.t[:-1], toy_task.v_ref[:-1])
    assert not r["valid"] and fails(r, "duration")


def test_extended_duration_is_rejected(toy_task):
    t = np.append(toy_task.t, 11.0)
    v = np.append(toy_task.v_ref, 0.0)
    r = validator.validate_trajectory(toy_task, t, v)
    assert not r["valid"] and fails(r, "duration")


def test_not_starting_or_ending_at_rest_is_rejected(toy_task):
    v = toy_task.v_ref.copy()
    v[-1] = 0.2
    r = validator.validate_trajectory(toy_task, toy_task.t, v)
    assert not r["valid"] and fails(r, "rest")


# ---- 2. stop times and durations
def test_motion_during_reference_stop_is_rejected(toy2_task):
    v = toy2_task.v_ref.copy()
    v[8] = 0.1                                            # creeping in the middle of the stop [7, 9]
    r = validator.validate_trajectory(toy2_task, toy2_task.t, v)
    assert not r["valid"] and fails(r, "moving during")


def test_late_arrival_is_rejected(toy_task):
    # same 6 m, but arriving at 7.5 s instead of 7 s (motion continues into the stop)
    t = np.array([0, 1, 2, 3, 4, 5, 6, 7.5, 10.0])
    v = np.array([0, 0, 1, 2, 1, 1, 1, 0, 0.0])
    r = validator.validate_trajectory(toy_task, t, v)
    assert not r["valid"]
    assert fails(r, "arrival") and fails(r, "moving during")


def test_early_departure_is_rejected(toy_task):
    t = np.array([0, 0.5, 2, 3, 4, 5, 6, 7, 10.0])
    v = np.array([0, 0, 1, 2, 1, 1, 1, 0, 0.0])
    r = validator.validate_trajectory(toy_task, t, v)
    assert not r["valid"] and fails(r, "departure")


def test_late_departure_is_rejected(toy_task):
    t = np.array([0, 1.5, 2.5, 3, 4, 5, 6, 7, 10.0])
    v = np.array([0, 0, 1, 2, 1, 1, 1, 0, 0.0])
    r = validator.validate_trajectory(toy_task, t, v)
    assert not r["valid"] and fails(r, "departure")


def test_early_arrival_with_waiting_is_valid(toy_task, plant_m0):
    # protocol 5.2-5.3: t_k <= T_k, departure at the reference time, then rest until the next departure
    t = np.array([0, 1, 2, 3, 4, 5, 6, 10.0])
    v = np.array([0, 0, 1, 2, 2, 1, 0, 0.0])
    r = validator.validate_trajectory(toy_task, t, v, plant_m0)
    assert r["valid"], r["failures"]
    assert r["segments"][0]["early_arrival_s"] == 1.0


def test_extra_stop_inside_a_segment_is_rejected(toy_task):
    t = np.array([0, 1, 2, 3, 4, 5, 6, 7, 10.0])
    v = np.array([0, 0, 1, 0, 2, 2, 1, 0, 0.0])          # stops at t = 3 inside the segment
    r = validator.validate_trajectory(toy_task, t, v)
    assert not r["valid"] and fails(r, "extra stop")


# ---- 3. speed and feasibility
def test_speed_above_segment_reference_maximum_is_rejected(toy_task):
    t = np.array([0, 1, 2, 3, 3.5, 4.5, 5.5, 7, 10.0])
    v = np.array([0, 0, 1, 2, 2.5, 1.5, 1.0, 0, 0.0])
    r = validator.validate_trajectory(toy_task, t, v)
    assert fails(r, "above segment reference maximum")


def test_acceleration_outside_bounds_is_rejected(toy_task):
    t = np.array([0, 1, 1.5, 3, 4, 5, 6, 7, 10.0])
    v = np.array([0, 0, 1, 2, 1, 1, 1, 0, 0.0])          # 2 m/s^2 over [1, 1.5]
    r = validator.validate_trajectory(toy_task, t, v)
    assert fails(r, "acceleration")


def test_negative_speed_is_rejected(toy_task):
    v = toy_task.v_ref.copy()
    v[8] = -0.1
    r = validator.validate_trajectory(toy_task, toy_task.t, v)
    assert fails(r, "negative speed")


def test_qs_infeasible_piece_is_rejected(toy_task, p1):
    weak = L.QSPlant(p1.with_overrides(T_max=0.5), 1.0, config.LIMITS["L-R1"], config.motor_model("M0"))
    r = validator.validate_trajectory(toy_task, toy_task.t, toy_task.v_ref, weak)
    assert not r["valid"] and fails(r, "QS-infeasible")


def test_malformed_or_nonfinite_input_is_rejected(toy_task):
    assert not validator.validate_trajectory(toy_task, [0.0], [0.0])["valid"]
    v = toy_task.v_ref.copy()
    v[3] = np.nan
    assert not validator.validate_trajectory(toy_task, toy_task.t, v)["valid"]
