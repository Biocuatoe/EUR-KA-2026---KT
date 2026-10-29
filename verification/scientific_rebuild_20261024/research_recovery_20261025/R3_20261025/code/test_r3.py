"""Correctness tests for r3_lib (run before the protocol freeze; they check implementation, not outcomes).

    python -I test_r3.py        (or pytest)
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r3_lib as L  # noqa: E402
from eureka.params import load_params  # noqa: E402
from eureka.plant import BatchParams  # noqa: E402
from rebuild import model as R1  # noqa: E402
from rebuild.model import IX, STATES, BatteryLimits  # noqa: E402
from rebuild.run import load_cycle  # noqa: E402

WIN = dict(v_min_ratio=0.78125, v_max_ratio=1.140625)
CONST = L.MotorModel("const", eta=0.874)
COPPER = L.MotorModel("copper", k_c=18000.0 * (1 / 0.874 - 1) / 85.0**2)
CURVE = L.MotorModel("curve", frac=(0.0, 0.05, 0.2, 0.5, 1.0, 1.5), eff=(0.70, 0.80, 0.90, 0.93, 0.92, 0.90))


def _states(n, rng):
    y = np.zeros((n, len(STATES)))
    y[:, IX["v"]] = rng.uniform(0, 15, n)
    y[:, IX["T"]] = rng.uniform(-85, 85, n)
    y[:, IX["V1"]] = rng.uniform(-0.5, 0.5, n)
    return y


def test_const_model_equals_r1():
    rng = np.random.default_rng(1)
    p = load_params()
    for lim in (BatteryLimits(), BatteryLimits(c_dis=3.0, c_ch=1.0, **WIN), BatteryLimits(c_dis=2.0, c_ch=0.5, soh_scaled=True, **WIN)):
        for soh in (1.0, 0.8):
            bp = BatchParams.from_params([p] * 200, np.full(200, soh))
            y = _states(200, rng)
            u = rng.uniform(-120, 120, 200)
            a, fa = R1.derivatives(y, u, bp, lim)
            b, fb = L.derivatives(y, u, bp, lim, CONST)
            assert np.array_equal(fa, fb)
            assert np.allclose(a, b, rtol=1e-12, atol=1e-9), np.max(np.abs(a - b))


def test_inverse_maps():
    w = np.array([20.0, 100.0, 212.0, 600.0])
    for mm in (CONST, COPPER, CURVE):
        for pe in (500.0, 4800.0, 15000.0):
            pm = mm.pm_drive_max(np.full(4, pe), w)
            T = pm / w
            assert np.allclose(pm + mm.loss(pm, T), pe, rtol=1e-3), (mm.kind, pe)
        for pc in (300.0, 2400.0):
            pm = mm.pm_regen_max(np.full(4, pc), w)
            fin = np.isfinite(pm)
            T = -pm[fin] / w[fin]
            back = -(-pm[fin] + mm.loss(-pm[fin], T))
            assert np.allclose(back, pc, rtol=1e-3), (mm.kind, pc)


def test_quasistatic_matches_r1_exact_tracking():
    """R1 IDEAL exact tracking, S1, SoH 1.0, k_r0 0.5, unconstrained: 107.4329 Wh incl. 0.0993 Wh of R1 loss."""
    p = load_params().with_overrides(k_r0=0.5)
    prof = load_cycle("S1")
    h = 0.1
    t = np.arange(0.0, prof.duration + 1e-9, h)
    v = prof.sample(t)
    r = L.evaluate(L.QSPlant(p, 1.0, BatteryLimits(), CONST), v, h)
    E_Wh = r["E_J"] / 3600.0
    assert r["feasible"]
    assert abs(E_Wh - (107.4329 - 0.0993)) / 107.4329 < 2e-3, E_Wh


def test_band_dp_zero_band_is_reference():
    p = load_params()
    prof = load_cycle("S2")
    h = 1.0
    v = prof.sample(np.arange(0.0, prof.duration + 1e-9, h))
    pl = L.QSPlant(p, 1.0, BatteryLimits(c_dis=3.0, c_ch=1.0, **WIN), COPPER)
    path = L.band_dp(pl, v, h, 0.0, 0.01, 0.0)
    assert np.allclose(path, v)
    best = L.band_min_energy(pl, v, h, 0.10, 0.01, L.evaluate(pl, v, h)["dist_m"])
    e_ref, e_b = L.evaluate(pl, v, h), L.evaluate(pl, best, h)
    assert e_b["dist_m"] >= e_ref["dist_m"] - 1e-6
    assert e_b["E_J"] / e_b["dist_m"] <= e_ref["E_J"] / e_ref["dist_m"] + 1e-9   # DP can never be worse than exact tracking
    assert np.max(np.abs(best - v)) <= 0.10 + 1e-9


def test_eco_tables_consistency():
    p = load_params()
    pl = L.QSPlant(p, 1.0, BatteryLimits(c_dis=3.0, c_ch=1.0, **WIN), CONST)
    tab = L.eco_segment_tables(pl, 400.0, 13.9, -1.5, 1.5, 2.0, 0.1)
    trip = L.eco_trip([tab], 0.0, 50.0)
    sol = trip["sols"][0]
    assert sol["v"][0] == 0.0 and sol["v"][-1] == 0.0
    ds = tab["ds"]
    assert abs(tab["N"] * ds - 400.0) < 1e-9
    # time recomputed from the speed sequence equals the DP time
    vs = sol["v"]
    assert abs(np.sum(2 * ds / (vs[:-1] + vs[1:])) - sol["t"]) < 1e-6


def test_dynamic_closure_copper():
    p = load_params()
    prof = load_cycle("S2")
    from eureka.controllers import gain
    K = gain(p, "fixed")
    out = L.simulate(prof, [p], np.array([K]), np.array([1.0]), BatteryLimits(c_dis=3.0, c_ch=1.0, **WIN), COPPER)
    m = L.sim_metrics(out, 0, p)
    assert m["valid"], m["invalid_reasons"]
    assert m["rmse_ms"] < 0.2


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print("PASS", name)
            except Exception as e:  # noqa: BLE001
                fails += 1
                print("FAIL", name, repr(e))
    sys.exit(1 if fails else 0)
