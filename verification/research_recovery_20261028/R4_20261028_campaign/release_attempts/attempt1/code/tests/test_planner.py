"""Component B: S-eco planner (protocol 5, 9 planner unit tests a-d) and the baseline task."""

import itertools

import numpy as np

from r4h3 import config, planner, validator

L = config.L


def test_segment_dp_equals_exhaustive_enumeration(plant_m0):
    # toy grid: 4 distance steps, speeds {0, .1, .2, .3}; enumerate every interior speed sequence
    tab = L.eco_segment_tables(plant_m0, 1.2, 0.3, -1.0, 1.0, 0.3, 0.1)
    assert tab["N"] == 4 and len(tab["v"]) == 4
    for lam in (0.01, 1.0, 50.0):
        sol = L.eco_segment_solve(tab, lam)
        best = np.inf
        for mid in itertools.product(range(len(tab["v"])), repeat=tab["N"] - 1):
            idx = (0, *mid, 0)
            c = sum(tab["E"][i, j] + lam * tab["t"][i, j] for i, j in zip(idx[:-1], idx[1:]))
            best = min(best, c)
        assert np.isfinite(best)
        assert abs((sol["E"] + lam * sol["t"]) - best) <= 1e-9 * max(1.0, abs(best))


def test_solve_segment_meets_time_and_bounds(plant_m0):
    tab = L.eco_segment_tables(plant_m0, 40.0, 4.0, -1.0, 1.0, 2.0, 0.1)
    for T_k in (16.0, 20.0, 30.0):                                 # minimum possible time is about 14 s
        r = planner.solve_segment(tab, T_k)
        assert r["status"] == "ok"
        assert r["sol"]["t"] <= T_k
        assert r["lb_J"] <= r["sol"]["E"] + 1e-9                  # weak duality on the grid


def test_tighter_time_budget_never_lowers_energy(plant_m0):
    tab = L.eco_segment_tables(plant_m0, 40.0, 4.0, -1.0, 1.0, 2.0, 0.1)
    E = [planner.solve_segment(tab, T)["sol"]["E"] for T in (40.0, 30.0, 20.0, 16.0)]
    assert all(b >= a - 1e-9 for a, b in zip(E, E[1:]))


def test_time_infeasible_segment_is_reported_not_replaced(plant_m0):
    tab = L.eco_segment_tables(plant_m0, 40.0, 4.0, -1.0, 1.0, 2.0, 0.1)
    r = planner.solve_segment(tab, 5.0)                            # 40 m at <= 4 m/s cannot take 5 s
    assert r["status"] == "time-infeasible" and r["sol"] is None


def test_seco_profile_respects_the_task(toy2_task, plant_m0):
    res = planner.plan_seco(plant_m0, toy2_task, ds=0.5, dv=0.1)
    assert res["status"] == "ok"
    for row in res["rows"]:
        assert row["t_k_s"] <= row["T_k_s"]                        # (c)
    val = validator.validate_trajectory(toy2_task, res["t"], res["v"], plant_m0)
    assert val["valid"], val["failures"]                           # (a) rest, (b) D_k, speed, accel, feasibility
    for seg, Dk in zip(val["segments"], toy2_task.D):
        assert abs(seg["D_traj_m"] - Dk) <= 1e-9
    # at rest at every reference-rest sample and every knot inside a rest interval (protocol 9a)
    v_on_grid = np.interp(toy2_task.t, res["t"], res["v"])
    assert np.all(v_on_grid[toy2_task.v_ref <= 1e-9] == 0.0)
    for t_a, t_d in toy2_task.rest:
        assert np.all(res["v"][(res["t"] >= t_a) & (res["t"] <= t_d)] == 0.0)


def test_planner_is_deterministic(toy2_task, plant_m0):
    a = planner.plan_seco(plant_m0, toy2_task, ds=0.5, dv=0.1)
    b = planner.plan_seco(plant_m0, toy2_task, ds=0.5, dv=0.1)
    assert np.array_equal(a["t"], b["t"]) and np.array_equal(a["v"], b["v"]) and a["rows"] == b["rows"]


def test_baseline_task_equals_feasible_reference(toy2_task, plant_m0):
    vb = planner.baseline_task(plant_m0, toy2_task)
    assert vb["equals_reference"] and not vb["hit_boundary"]
