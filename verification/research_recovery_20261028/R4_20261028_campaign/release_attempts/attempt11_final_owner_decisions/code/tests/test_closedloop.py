"""Component C: the traced closed loop equals the frozen r3_lib.simulate; repeatability; recomputation
agreement on a short run (brief tests 6 and 8; protocol 9 'independent recomputation')."""

import numpy as np
import pytest

from conftest import short_profile
from r4h3 import config, evaluator, frozen
from r4h3.closedloop import fixed_gain, run_metrics, simulate_traced, trace_constraint_metrics
from r4h3.traces import CHANNELS

L = config.L


@pytest.fixture(scope="module")
def K(p1):
    return fixed_gain(p1)


@pytest.mark.parametrize("motor", ["M0", "M1", "M2"])
@pytest.mark.parametrize("limits", ["L-R1", "L-EVE"])
def test_traced_loop_equals_frozen_simulate_bitwise(p1, K, motor, limits):
    prof = short_profile()
    lim, mm = config.LIMITS[limits], config.motor_model(motor)
    ref = L.simulate(prof, [p1], np.array([K]), np.array([1.0]), lim, mm)
    out, tr = simulate_traced(prof, p1, K, 1.0, lim, mm)
    assert np.array_equal(ref["y_end"], out["y_end"])
    for k in ref["acc"]:
        assert np.array_equal(ref["acc"][k], out["acc"][k]), k
    assert np.array_equal(ref["closure_J"], out["closure_J"])
    assert np.array_equal(ref["feasible"], out["feasible"])
    assert len(tr["t_s"]) == round(prof.duration / p1.Ts) * round(p1.Ts / p1.dt) + 1


def test_trace_end_matches_integrator_state(p1, K):
    from rebuild.model import IX
    out, tr = simulate_traced(short_profile(), p1, K, 1.0, config.LIMITS["L-R1"], config.motor_model("M0"))
    for ch in ("E_chem", "dist", "I_over", "E_fb"):
        assert tr[f"int_{ch}"][-1] == out["y_end"][0][IX[ch]]
    assert tr["t_s"][-1] == pytest.approx(short_profile().duration, abs=1e-12)


def test_repeatability_bitwise(p1, K):
    args = (short_profile(), p1, K, 1.0, config.LIMITS["L-EVE"], config.motor_model("M1"))
    _, a = simulate_traced(*args)
    _, b = simulate_traced(*args)
    assert a.keys() == b.keys()
    for k in a:
        assert np.array_equal(a[k], b[k]), k


def test_gain_is_the_r1_fixed_design(p1, K):
    from eureka.controllers import gain
    assert np.array_equal(K, np.ravel(gain(p1, "fixed")))
    assert K.shape == (3,)


@pytest.mark.parametrize("motor", ["M0", "M1", "M2"])
def test_evaluator_recomputes_simulator_metrics_from_trace(p1, K, motor):
    prof = short_profile()
    lim = config.LIMITS["L-R1"]
    out, tr = simulate_traced(prof, p1, K, 1.0, lim, config.motor_model(motor))
    d_ref = float(prof.stats()["distance_m"])
    sim = run_metrics(out, p1, 1.0, d_ref, prof.duration, p1.Ts)
    tr["v_ref_task_mps"] = tr["v_tracked_mps"]
    tr["stop_ref_flag"] = np.zeros_like(tr["t_s"])
    sim["stop_ok_sim"] = True
    sim.update(trace_constraint_metrics(tr, p1, lim, config.RULES))
    assert set(CHANNELS) == set(tr)
    spec = {"battery": dict(V_oc=p1.V_oc, R0=p1.R0_new, Q_Ah=p1.Q_Ah, c_dis=lim.c_dis, c_ch=lim.c_ch,
                            v_min_ratio=lim.v_min_ratio, v_max_ratio=lim.v_max_ratio),
            "motor": evaluator.motor_spec_from_protocol(motor, frozen.M1_CURVE), "G": p1.G, "r_w": p1.r_w, "v_eps": p1.v_eps, "T_max": p1.T_max, "P_max": p1.P_max, "B_m": p1.B_m, "eta_g": p1.eta_g, "M_eff": p1.M_eff, "C1": p1.C1,
            "Ts_s": p1.Ts, "dt_s": p1.dt, "d_ref_m": d_ref, "rest_intervals": [[0.0, 0.0]]}
    ev = evaluator.evaluate_trace(tr, spec, config.RULES)
    cmp = evaluator.compare_with_simulator(ev, sim, config.RULES)
    assert cmp["all_ok"], {k: v for k, v in cmp.items() if k != "all_ok" and not v["ok"]}
