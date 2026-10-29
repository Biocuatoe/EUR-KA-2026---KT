"""Supplementary pre-freeze tests for r3_lib (added 2026-10-25; test_r3.py is unchanged).

    python -I test_r3_supplementary.py

Each test prints the margin it measured. They check implementation only: the optimiser tests use a
tiny synthetic reference, never S1/S2/UDDS, so no R3 outcome is observed before the protocol freeze.
"""

from __future__ import annotations

import csv
import itertools
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r3_lib as L  # noqa: E402
from eureka.params import load_params  # noqa: E402
from eureka.plant import BatchParams  # noqa: E402
from rebuild import model as R1  # noqa: E402
from rebuild.model import IX, STATES, BatteryLimits, battery_limits  # noqa: E402
from rebuild.run import load_cycle  # noqa: E402

WIN = dict(v_min_ratio=0.78125, v_max_ratio=1.140625)
MM = L.motor_models()
LIMS = {"none": BatteryLimits(), "L-R1": BatteryLimits(c_dis=3.0, c_ch=1.0, **WIN),
        "L-EVE": BatteryLimits(c_dis=2.0, c_ch=1.0, **WIN)}
LEDGER = L.R1 / "recovery_feasibility_20261025" / "ledger_ideal.csv"


def say(*a):
    print("   ", *a)


def test_m1_curve_physical():
    m = MM["M1"]
    x = np.linspace(0.0, 1.0, 100001)
    eta = m._eta(x * m.p_rated)
    assert eta.min() >= 0.84 - 1e-12 and eta.max() <= 0.95 + 1e-12
    pm = np.linspace(-18000.0, 18000.0, 200001)
    Ls = m.loss(pm, pm / 100.0)
    assert np.all(Ls >= 0)
    step = np.max(np.abs(np.diff(Ls)))            # no jump larger than the slope allows
    assert step < 0.2 * (pm[1] - pm[0]) + 1e-9, step
    assert abs(m.loss(np.array([1e-9]), 0)[0]) < 1e-9 and abs(m.loss(np.array([-1e-9]), 0)[0]) < 1e-9
    pe = pm + Ls
    assert np.all(np.diff(pe) > 0)                 # electrical power strictly increasing: inverse maps well defined
    say(f"M1 eta range [{eta.min():.4f}, {eta.max():.4f}], max |dL| per {pm[1]-pm[0]:.2f} W step = {step:.4f} W")


def test_m1_inverse_maps():
    m = MM["M1"]
    w = np.array([20.0, 100.0, 212.0, 600.0])
    worst = 0.0
    for pe in (100.0, 900.0, 4800.0, 15000.0):
        pm = m.pm_drive_max(np.full(4, pe), w)
        worst = max(worst, float(np.max(np.abs(pm + m.loss(pm, pm / w) - pe) / pe)))
    for pc in (100.0, 2400.0, 9000.0):
        pm = m.pm_regen_max(np.full(4, pc), w)
        worst = max(worst, float(np.max(np.abs(pm - m.loss(-pm, -pm / w) - pc) / pc)))
    assert worst < 1e-3, worst
    say(f"M1 inverse-map worst relative error {worst:.2e}")


def test_m0_margin_vs_r1():
    rng = np.random.default_rng(7)
    p = load_params()
    worst = 0.0
    for lim in LIMS.values():
        for soh in (1.0, 0.8):
            bp = BatchParams.from_params([p] * 500, np.full(500, soh))
            y = np.zeros((500, len(STATES)))
            y[:, IX["v"]] = rng.uniform(0, 20, 500)
            y[:, IX["T"]] = rng.uniform(-90, 90, 500)
            y[:, IX["V1"]] = rng.uniform(-1, 1, 500)
            u = rng.uniform(-150, 150, 500)
            a, _ = R1.derivatives(y, u, bp, lim)
            b, _ = L.derivatives(y, u, bp, lim, MM["M0"])
            worst = max(worst, float(np.max(np.abs(a - b) / (1 + np.abs(a)))))
    assert worst < 1e-12, worst
    say(f"M0 vs R1 derivatives: worst |diff|/(1+|R1|) = {worst:.2e} over 3000 random states")


def test_qs_vs_r1_ledger_all_rows():
    """QS energy (V1 = 0) vs R1's exact-tracking ledger (minus its R1-branch loss), every feasible unstretched row."""
    worst = 0.0
    n = 0
    with LEDGER.open(encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["feasible"] == "True" and float(r["stretch"]) == 1.0]
    cache = {}
    for r in rows:
        p = load_params().with_overrides(k_r0=float(r["k_r0"]))
        if r["cycle"] not in cache:
            prof = load_cycle(r["cycle"])
            t = np.arange(0.0, prof.duration + 1e-9, 0.1)
            cache[r["cycle"]] = prof.sample(t)
        res = L.evaluate(L.QSPlant(p, float(r["soh"]), LIMS["none"], MM["M0"]), cache[r["cycle"]], 0.1)
        ref = float(r["E_chem_Wh"]) - float(r["E_R1_Wh"])
        d = abs(res["E_J"] / 3600.0 - ref) / float(r["E_chem_Wh"])
        worst = max(worst, d)
        n += 1
    assert n > 0 and worst < 2e-3, worst
    say(f"QS vs R1 ideal ledger: {n} rows, worst relative difference {100*worst:.4f} % (limit 0.2 %)")


def _ref_point(p, v, a, eta):
    """Hand formula: (terminal power, friction power). Regeneration beyond the motor envelope goes to friction.

    Run 1 of this file omitted the envelope; its (12 m/s, -2 m/s^2) case needs -67.4 N m against a
    64.6 N m envelope and failed (logs/test_r3_supplementary_run1.txt). The model was right.
    """
    gr = p.G / p.r_w
    w = gr * v
    f = p.M_eff * a + p.Crr * p.M * p.g * np.tanh(v / p.v_eps) + 0.5 * p.rho * p.Cd * p.A_f * v * v
    T = (f / (gr * p.eta_g) if f >= 0 else f * p.eta_g / gr) + p.B_m * w
    T_m = max(T, -min(p.T_max, p.P_max / w))
    f_m = gr * (T_m - p.B_m * w) * (p.eta_g if T_m - p.B_m * w >= 0 else 1 / p.eta_g)
    pm = T_m * w
    return (pm / eta if pm >= 0 else pm * eta), max(f_m - f, 0.0) * v


def test_signs_and_independent_point_power():
    p = load_params()
    pl = L.QSPlant(p, 1.0, LIMS["none"], MM["M0"])
    R0 = float(pl.bp.R0[0])
    worst = 0.0
    for v, a in ((10.0, 0.0), (10.0, 1.0), (5.0, 1.5), (10.0, -1.0), (12.0, -2.0), (3.0, -0.5)):
        pc, pf, ia, i2, ok = pl.point(np.array([v]), np.array([a]))
        pe = pc[0] - R0 * i2[0]                    # terminal power = OCV power - R0 loss
        exp, exp_f = _ref_point(p, v, a, 0.874)
        worst = max(worst, abs(pe - exp) / abs(exp), abs(pf[0] - exp_f) / abs(exp))
        assert ok[0]
        assert np.sign(pc[0]) == np.sign(exp)      # positive = discharge, negative = regeneration
    assert worst < 1e-9, worst
    say(f"QS point terminal and friction power vs hand formula (with motor envelope): worst relative difference {worst:.1e}; signs consistent")


def test_regen_limit_friction_and_current():
    p = load_params()
    pl = L.QSPlant(p, 1.0, LIMS["L-EVE"], MM["M0"])
    i_d, i_c, _, _ = battery_limits(np.zeros(1), pl.bp, LIMS["L-EVE"])
    pc, pf, ia, i2, ok = pl.point(np.array([12.0]), np.array([-3.0]))
    i = pc[0] / float(pl.bp.V_oc[0])
    assert pf[0] > 0 and i < 0 and -i <= float(i_c[0]) + 1e-6
    say(f"hard braking 12 m/s, -3 m/s^2, L-EVE: charge current {-i:.1f} A (limit {float(i_c[0]):.1f} A), friction {pf[0]:.0f} W")


def test_grid_finite_and_constraints_enforced():
    p = load_params()
    v, a = np.meshgrid(np.linspace(0, 20, 81), np.linspace(-3.5, 3.5, 71))
    v, a = v.ravel(), a.ravel()
    gr = p.G / p.r_w
    n_ok = n_bad = 0
    for mk, m in MM.items():
        for lk, lim in LIMS.items():
            for soh in (1.0, 0.8):
                pl = L.QSPlant(p.with_overrides(k_r0=3.5), soh, lim, m)
                pc, pf, ia, i2, ok = pl.point(v, a)
                assert np.all(np.isfinite(pc)) and np.all(np.isfinite(pf)) and np.all(pf >= 0)
                i = pc / float(pl.bp.V_oc[0])
                w = gr * v
                base = np.minimum(p.T_max, p.P_max / np.maximum(w, 1e-6))
                f = p.M_eff * a + p.Crr * p.M * p.g * np.tanh(v / p.v_eps) + 0.5 * p.rho * p.Cd * p.A_f * v * v
                T = np.where(f >= 0, f / (gr * p.eta_g), f * p.eta_g / gr) + p.B_m * w
                assert np.all(T[ok] <= base[ok] + 1e-6)                 # torque/power envelope
                if lim.active:
                    i_d, i_c, _, _ = battery_limits(np.zeros(1), pl.bp, lim)
                    assert np.all(i[ok] <= float(i_d[0]) + 1e-6)
                    assert np.all(-i <= float(i_c[0]) + 1e-6)             # charge limit always respected (excess -> friction)
                if mk == "M1":
                    assert np.all(T[ok] * w[ok] <= 18000.0 + 1e-6)        # M1 never extrapolates beyond x = 1
                n_ok += int(ok.sum())
                n_bad += int((~ok).sum())
    say(f"{len(v)} (v, a) points x 3 models x 3 limit sets x 2 SoH: all finite; {n_ok} feasible points satisfy every limit; {n_bad} flagged infeasible")


def test_qs_and_dynamic_share_equations():
    p = load_params()
    worst_i = worst_a = 0.0
    for mk, m in MM.items():
        for v, a in ((8.0, 0.0), (8.0, 0.8), (11.0, -0.8), (2.0, 0.3)):
            pl = L.QSPlant(p, 1.0, LIMS["none"], m)
            pc, *_ = pl.point(np.array([v]), np.array([a]))
            gr = p.G / p.r_w
            f = p.M_eff * a + p.Crr * p.M * p.g * np.tanh(v / p.v_eps) + 0.5 * p.rho * p.Cd * p.A_f * v * v
            T = (f / (gr * p.eta_g) if f >= 0 else f * p.eta_g / gr) + p.B_m * gr * v
            y = np.zeros((1, len(STATES)))
            y[0, IX["v"]], y[0, IX["T"]] = v, T
            bp = BatchParams.from_params([p], np.array([1.0]))
            dy, _ = L.derivatives(y, np.array([T]), bp, LIMS["none"], m)
            i_dyn = dy[0, IX["E_chem"]] / p.V_oc
            worst_i = max(worst_i, abs(i_dyn - pc[0] / p.V_oc) / max(abs(i_dyn), 1.0))
            worst_a = max(worst_a, abs(dy[0, IX["v"]] - a))
    assert worst_i < 1e-9 and worst_a < 1e-9, (worst_i, worst_a)
    say(f"QS point vs dynamic derivatives at the same (v, T): current {worst_i:.1e} rel., acceleration {worst_a:.1e} m/s^2")


def test_dynamic_closure_m0_m1():
    p = load_params()
    from eureka.controllers import gain
    K = gain(p, "fixed")
    prof = load_cycle("S2")
    for mk in ("M0", "M1"):
        out = L.simulate(prof, [p], np.array([K]), np.array([1.0]), LIMS["L-EVE"], MM[mk])
        m = L.sim_metrics(out, 0, p)
        y0, y1 = out["y0"][0], out["y_end"][0]
        pos, neg, chem = (y1[IX[k]] - y0[IX[k]] for k in ("E_pos", "E_neg", "E_chem"))
        assert m["valid"], m["invalid_reasons"]
        assert neg <= 0 <= pos and abs(pos + neg - chem) < 1e-6 * abs(pos)
        assert (y1[IX["E_regen"]] - y0[IX["E_regen"]]) <= 0
        say(f"{mk} S2 L-EVE dynamic: closure {m['closure_rel']:.1e} of throughput, E_pos+E_neg-E_chem {pos+neg-chem:.1e} J")


def _tiny():
    p = load_params()
    return L.QSPlant(p, 1.0, LIMS["L-R1"], MM["M2"]), np.array([0.0, 1.0, 2.2, 2.6, 1.4, 0.0])


def test_band_dp_is_global_on_its_grid():
    pl, vr = _tiny()
    h, dv, J, mu = 1.0, 0.1, 2, 30.0
    path = L.band_dp(pl, vr, h, J * dv, dv, mu)

    def obj(v):
        E, _, _, _, s, ok = pl.step(v[:-1], v[1:], h)
        return float(np.sum(E - mu * s)) if ok.all() and np.all(v >= -1e-12) else np.inf

    best = min(obj(vr + np.r_[0, np.array(c) * dv, 0]) for c in itertools.product(range(-J, J + 1), repeat=len(vr) - 2))
    assert abs(obj(path) - best) < 1e-6 * abs(best), (obj(path), best)
    say(f"band DP vs exhaustive enumeration of {(2*J+1)**(len(vr)-2)} trajectories: objective equal ({best:.4f} J)")


def test_band_lagrangian_bound_valid():
    pl, vr = _tiny()
    h, dv, J = 1.0, 0.1, 2
    d_t = L.evaluate(pl, vr, h)["dist_m"] + 0.25
    feas = []
    for c in itertools.product(range(-J, J + 1), repeat=len(vr) - 2):
        v = vr + np.r_[0, np.array(c) * dv, 0]
        if np.all(v >= -1e-12):
            r = L.evaluate(pl, v, h)
            if r["feasible"] and r["dist_m"] >= d_t - 1e-9:
                feas.append(r["E_J"])
    exact = min(feas)
    best = L.band_min_energy(pl, vr, h, J * dv, dv, d_t)
    e_best = L.evaluate(pl, best, h)["E_J"]
    lbs = []
    for mu in np.linspace(0, 400, 81):
        pth = L.band_dp(pl, vr, h, J * dv, dv, mu)
        E, _, _, _, s, _ = pl.step(pth[:-1], pth[1:], h)
        lbs.append(float(np.sum(E - mu * s)) + mu * d_t)
    lb = max(lbs)
    assert lb <= exact + 1e-6 <= e_best + 2e-6, (lb, exact, e_best)
    say(f"distance-constrained: dual bound {lb:.3f} <= exact {exact:.3f} <= bisection result {e_best:.3f} J")


def test_eco_dp_is_global_on_its_grid():
    p = load_params()
    pl = L.QSPlant(p, 1.0, LIMS["L-R1"], MM["M1"])
    tab = L.eco_segment_tables(pl, 20.0, 2.0, -1.5, 1.5, 5.0, 0.5)
    lam = 50.0
    sol = L.eco_segment_solve(tab, lam)
    C = tab["E"] + lam * tab["t"]
    nv = len(tab["v"])
    best = np.inf
    for c in itertools.product(range(nv), repeat=tab["N"] - 1):
        idx = (0,) + c + (0,)
        best = min(best, sum(C[a, b] for a, b in zip(idx[:-1], idx[1:])))
    got = sol["E"] + lam * sol["t"]
    assert abs(got - best) < 1e-6 * abs(best), (got, best)
    say(f"eco DP vs exhaustive enumeration of {nv**(tab['N']-1)} speed sequences: objective equal ({best:.4f})")


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
