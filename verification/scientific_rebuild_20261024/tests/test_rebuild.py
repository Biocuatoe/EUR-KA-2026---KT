"""Tests of the rebuild extension. A passing test establishes only the tested property."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from eureka import plant as base_plant  # noqa: E402
from eureka.controllers import gain  # noqa: E402
from eureka.cycles import load_profiles  # noqa: E402
from eureka.params import load_params  # noqa: E402
from eureka.plant import BatchParams  # noqa: E402
from eureka.simulate import simulate as base_simulate  # noqa: E402
from rebuild import model  # noqa: E402

P = load_params()
WINDOW = dict(v_min_ratio=0.78125, v_max_ratio=1.140625)
BCS = model.BatteryLimits(c_dis=3.0, c_ch=1.0, soh_scaled=True, **WINDOW)


def _bp(soh, k_r0=0.5, n=1):
    p = P.with_overrides(k_r0=k_r0)
    return BatchParams.from_params([p] * n, np.full(n, soh))


def test_derivatives_equal_base_plant_when_limits_disabled():
    rng = np.random.default_rng(1)
    n = 64
    bp = _bp(0.8, n=n)
    y = np.zeros((n, len(model.STATES)))
    y[:, model.IX["v"]] = rng.uniform(0, 25, n)
    y[:, model.IX["T"]] = rng.uniform(-85, 85, n)
    y[:, model.IX["V1"]] = rng.uniform(-0.5, 0.5, n)
    y[:, model.IX["SoC"]] = 0.8
    t_ref = rng.uniform(-150, 150, n)
    dy, feas = model.derivatives(y, t_ref, bp, model.BatteryLimits())
    dy0, aux = base_plant.derivatives(y[:, : len(base_plant.STATES)], t_ref, bp)
    assert np.array_equal(dy[:, : len(base_plant.STATES)], dy0)
    assert np.array_equal(feas, aux["feasible"])


def test_simulate_reproduces_eureka_simulate_without_limits():
    prof = load_profiles()["P-TUNE"]
    K = np.vstack([gain(P, "fixed"), gain(P, "scheduled", soh=0.8)])
    soh = np.array([0.8, 0.8])
    ref = base_simulate(prof, [P, P], K, soh)
    new = model.simulate(prof, [P, P], K, soh, [model.BatteryLimits()] * 2)
    nb = len(base_plant.STATES)
    np.testing.assert_allclose(new["y_end"][:, :nb], ref["y_end"], rtol=0, atol=1e-9)
    e = ref["v"] - ref["v_ref"]
    rmse_ref = np.sqrt(np.mean(e**2, axis=0))
    rmse_new = np.sqrt(new["acc"]["se2"] / new["acc"]["steps"])
    np.testing.assert_allclose(rmse_new, rmse_ref, rtol=1e-12)


@pytest.mark.parametrize("soh,k_r0,V1", [(1.0, 0.5, 0.0), (0.7, 0.5, 0.3), (0.7, 2.0, -0.2), (0.8, 30.0, 0.1)])
def test_battery_limits_match_brute_force(soh, k_r0, V1):
    bp = _bp(soh, k_r0)
    i_d, i_c, p_d, p_c = model.battery_limits(np.array([V1]), bp, BCS)
    vo, R0 = bp.V_oc[0] - V1, bp.R0[0]
    I = np.linspace(0, 2000, 400001)
    ok = (vo - R0 * I >= WINDOW["v_min_ratio"] * bp.V_oc[0]) & (I <= 3.0 * bp.Q_Ah[0] * soh)
    p = (vo - R0 * I) * I
    assert abs(p[ok].max() - p_d[0]) / p_d[0] < 1e-4
    okc = (vo + R0 * I <= WINDOW["v_max_ratio"] * bp.V_oc[0]) & (I <= 1.0 * bp.Q_Ah[0] * soh)
    pc = (vo + R0 * I) * I
    assert abs(pc[okc].max() - p_c[0]) / p_c[0] < 1e-4


def test_limits_shrink_with_soh_and_resistance():
    V1 = np.zeros(1)
    pd = [model.battery_limits(V1, _bp(s), BCS)[2][0] for s in (1.0, 0.9, 0.8, 0.7)]
    assert all(a > b for a, b in zip(pd, pd[1:]))
    bv = model.BatteryLimits(**WINDOW)
    p_lo = model.battery_limits(V1, _bp(0.7, 0.5), bv)[2][0]
    p_hi = model.battery_limits(V1, _bp(0.7, 2.0), bv)[2][0]
    assert p_hi < p_lo


def test_energy_closure_and_friction_brake_with_limits():
    prof = load_profiles()["P-TUNE"]
    strict = model.BatteryLimits(c_dis=1.0, c_ch=0.2, soh_scaled=True, **WINDOW)
    out = model.simulate(prof, [P], gain(P, "fixed")[None, :], np.array([0.7]), [strict], record_every=1)
    y1 = out["y_end"][0]
    throughput = P.V_oc * 3600 * y1[model.IX["Ah"]]
    assert abs(out["closure_J"][0]) / throughput < 1e-6
    assert y1[model.IX["E_fb"]] > 0  # regen capped at 0.2 C x 0.7 -> friction brake takes the rest
    assert out["acc"]["sat_batt"][0] > 0  # 1 C x 0.7 = 70 A binds during acceleration
    assert out["feasible"][0]


def test_soh_scaled_and_unscaled_identical_at_full_health():
    prof = load_profiles()["P-TUNE"]
    bcn = model.BatteryLimits(c_dis=3.0, c_ch=1.0, soh_scaled=False, **WINDOW)
    K = np.vstack([gain(P, "fixed")] * 2)
    out = model.simulate(prof, [P, P], K, np.array([1.0, 1.0]), [BCS, bcn])
    assert np.array_equal(out["y_end"][0], out["y_end"][1])
