"""Scenario separation and H3 scope: no SoH control, no capacity-fade content (brief tests 9 and 10)."""

import inspect
import re

import numpy as np
import pytest

from r4h3 import closedloop, config, evaluator, frozen, planner, slice as sl, traces

FORBIDDEN = re.compile(r"fade|ageing|aging|capacity_loss|cycle_life|soh_benefit|saving|scheduled", re.I)


def test_three_distinct_labelled_motor_scenarios():
    assert set(config.SCENARIOS) == {"M0", "M1", "M2"}
    kinds = {s.kind for s in config.SCENARIOS.values()}
    assert kinds == {"const", "curve", "copper"}
    for sid, s in config.SCENARIOS.items():
        assert s.label and s.provenance_class and s.validity_limits and s.ledger_id.startswith("MOT-")
        assert config.motor_model(sid).kind == s.kind
    assert "NOT a Renault Zoe map" in config.SCENARIOS["M1"].validity_limits
    assert [config.SCENARIOS[k].qs_usable for k in ("M0", "M1", "M2")] == [True, True, False]
    with pytest.raises(KeyError):
        config.motor_model("ZOE")


def test_scenarios_give_different_losses_for_the_same_operating_point():
    p_m, T = np.array([3000.0, -3000.0]), np.array([20.0, -20.0])
    losses = {sid: evaluator.motor_loss(evaluator.motor_spec_from_protocol(sid, frozen.M1_CURVE), p_m, T)
              for sid in ("M0", "M1", "M2")}
    assert not np.allclose(losses["M0"], losses["M1"]) and not np.allclose(losses["M0"], losses["M2"])
    assert not np.allclose(losses["M1"], losses["M2"])


def test_h3_configuration_has_no_soh_control_or_ageing():
    rec = config.scenario_record()
    assert rec["hypothesis"] == "H3 only"
    assert set(rec["pstates"]) == {"P1", "P3"}
    assert "fixed" in rec["controller"] and "identical" in rec["controller"]
    flat = {k: v for k, v in rec.items() if k != "excluded"}
    assert not FORBIDDEN.search(str(flat))
    assert all(not lim["soh_scaled"] for lim in rec["limits"].values())


def test_controller_and_planner_contain_no_soh_scheduling():
    for mod in (closedloop, planner):
        src = inspect.getsource(mod)
        assert "scheduled" not in src and "gamma_v" not in src and "soh_scaled=True" not in src
    assert '"fixed"' in inspect.getsource(closedloop.fixed_gain)


def test_outputs_have_no_fade_or_benefit_fields():
    assert not any(FORBIDDEN.search(k) for k in traces.CHANNELS)
    # evaluation keys on a trivial trace
    n = 101
    z = np.zeros(n)
    a = dict(t_s=np.arange(n) * 1e-3, v_mps=z, v_tracked_mps=z, v_ref_task_mps=z, T_Nm=z, w_radps=z, V1_V=z, i_A=z,
             P_regen_wheel_W=z, P_fric_W=z, limit_active=z, u_cmd_Nm=z, t_neg_Nm=z)
    spec = {"battery": dict(V_oc=48.0, R0=0.005, Q_Ah=100.0, c_dis=3.0, c_ch=1.0, v_min_ratio=0.78125,
                            v_max_ratio=1.140625), "motor": {"kind": "const", "eta": 0.874}, "G": 6.5, "r_w": 0.28, "v_eps": 0.05,
            "Ts_s": 0.01, "dt_s": 0.001, "d_ref_m": 1.0, "rest_intervals": []}
    ev = evaluator.evaluate_trace(a, spec, config.RULES)
    assert not any(FORBIDDEN.search(k) for k in ev)


def test_slice_never_computes_an_energy_difference_between_arms():
    src = inspect.getsource(sl.run)
    # no arithmetic combining the two arms' energy metrics
    assert not re.search(r"Wh_per_ref_km\"\]\s*[-/]", src) and "dE" not in src and "delta_E" not in src
