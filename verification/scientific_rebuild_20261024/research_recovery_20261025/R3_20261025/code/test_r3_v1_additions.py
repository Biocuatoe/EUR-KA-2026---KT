"""Tests for the R3 v1 additions to r3_lib (track_dp, band tables, dual bounds, EcoSolver).

    python -I test_r3_v1_additions.py

Synthetic references only; no R3 outcome is computed.
"""

from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r3_lib as L  # noqa: E402
from eureka.params import load_params  # noqa: E402
from rebuild.model import BatteryLimits  # noqa: E402

WIN = dict(v_min_ratio=0.78125, v_max_ratio=1.140625)
MM = L.motor_models()
LEVE = BatteryLimits(c_dis=2.0, c_ch=1.0, **WIN)


def say(*a):
    print("   ", *a)


def _synthetic(n=60, seed=3):
    rng = np.random.default_rng(seed)
    v = np.clip(np.cumsum(rng.normal(0, 0.6, n)), 0, 14)
    v[0] = v[-1] = 0.0
    return v


def test_band_tables_equal_band_dp():
    p = load_params()
    worst = 0.0
    for mk in ("M0", "M1", "M2"):
        pl = L.QSPlant(p.with_overrides(k_r0=3.5), 0.8, LEVE, MM[mk])
        vr = _synthetic()
        tr, _, _ = L.track_dp(pl, vr, 1.0, 3.0, 0.05)
        tab = L.band_tables(pl, tr, 1.0, 0.25, 0.01, chunk=7)
        for mu in (0.0, 40.0, 400.0):
            a = L.band_dp(pl, tr, 1.0, 0.25, 0.01, mu)
            b, _ = L.band_dp_tab(tab, mu)
            assert a is not None and b is not None
            worst = max(worst, float(np.max(np.abs(a - b))))
    assert worst < 1e-12, worst
    say(f"band_dp_tab vs band_dp, 3 models x 3 mu: max path difference {worst:.1e} m/s")


def test_band_min_energy_tab_and_bound():
    p = load_params()
    pl = L.QSPlant(p, 1.0, BatteryLimits(c_dis=3.0, c_ch=1.0, **WIN), MM["M1"])
    vr = np.array([0.0, 1.0, 2.2, 2.6, 1.4, 0.0])
    h, dv, J = 1.0, 0.1, 2
    d_t = L.evaluate(pl, vr, h)["dist_m"] + 0.25
    tab = L.band_tables(pl, vr, h, J * dv, dv)
    r = L.band_min_energy_tab(pl, tab, d_t)
    old = L.band_min_energy(pl, vr, h, J * dv, dv, d_t)
    feas = []
    for c in itertools.product(range(-J, J + 1), repeat=len(vr) - 2):
        v = vr + np.r_[0, np.array(c) * dv, 0]
        if np.all(v >= -1e-12):
            e = L.evaluate(pl, v, h)
            if e["feasible"] and e["dist_m"] >= d_t - 1e-9:
                feas.append(e["E_J"])
    exact = min(feas)
    assert np.allclose(r["path"], old)
    assert r["lb_J"] <= exact + 1e-6 <= r["E_J"] + 2e-6, (r["lb_J"], exact, r["E_J"])
    say(f"tab bisection = original bisection; dual bound {r['lb_J']:.3f} <= exact {exact:.3f} <= found {r['E_J']:.3f} J")


def test_track_dp_feasible_reference_is_itself():
    p = load_params()
    pl = L.QSPlant(p, 1.0, BatteryLimits(), MM["M0"])
    vr = np.array([0.0, 0.8, 1.6, 2.0, 2.0, 1.2, 0.0])
    path, sse, hit = L.track_dp(pl, vr, 1.0, 1.0, 0.05)
    assert np.allclose(path, vr) and sse == 0.0 and not hit
    say("feasible reference: track_dp returns it with zero error")


def test_track_dp_global_and_feasible_on_infeasible_reference():
    p = load_params()
    pl = L.QSPlant(p, 1.0, LEVE, MM["M0"])
    vr = np.array([0.0, 3.0, 6.0, 8.0, 4.0, 0.0])    # 3 m/s^2 at speed: beyond the 2C envelope
    assert not L.evaluate(pl, vr, 1.0)["feasible"]
    W, dv = 3.0, 0.5
    path, sse, hit = L.track_dp(pl, vr, 1.0, W, dv)
    assert path is not None and L.evaluate(pl, path, 1.0)["feasible"]
    J = int(round(W / dv))
    best = np.inf
    for c in itertools.product(range(-J, J + 1), repeat=len(vr) - 2):
        v = vr + np.r_[0, np.array(c) * dv, 0]
        if np.all(v >= -1e-12) and L.evaluate(pl, v, 1.0)["feasible"]:
            best = min(best, float(np.sum((v - vr) ** 2)))
    assert abs(sse - best) < 1e-9, (sse, best)
    say(f"infeasible reference: track_dp feasible, squared error {sse:.3f} equals exhaustive minimum over {(2*J+1)**4} paths")


def test_eco_solver_bound():
    p = load_params()
    pl = L.QSPlant(p, 1.0, BatteryLimits(c_dis=3.0, c_ch=1.0, **WIN), MM["M1"])
    tab = L.eco_segment_tables(pl, 20.0, 2.0, -1.5, 1.5, 5.0, 0.5)
    sol = L.EcoSolver([tab], 3.0)
    t_fast = sol.trip(1e4)["T_total"]
    T_target = t_fast * 1.3
    best, lam, lb, t_min = sol.for_time(T_target)
    nv = len(tab["v"])
    exact = np.inf
    for c in itertools.product(range(nv), repeat=tab["N"] - 1):
        idx = (0,) + c + (0,)
        E = sum(tab["E"][a, b] for a, b in zip(idx[:-1], idx[1:]))
        t = sum(tab["t"][a, b] for a, b in zip(idx[:-1], idx[1:]))
        if np.isfinite(E) and t + 3.0 <= T_target + 1e-9:
            exact = min(exact, E)
    assert best["T_total"] <= T_target + 1e-9
    assert lb <= exact + 1e-6 <= best["E"] + 2e-6, (lb, exact, best["E"])
    say(f"eco time-constrained: dual bound {lb:.2f} <= exact {exact:.2f} <= found {best['E']:.2f} J (time {best['T_total']:.2f} <= {T_target:.2f} s)")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
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
