"""R3 reference plant, quasi-static trajectory evaluation and the two dynamic-programming bounds.

Model: ../R3_model_basis.md. Protocol: ../R3_protocol.md.

- Dynamic plant: R1's plant (src/rebuild/model.py) with the motor/inverter loss as an
  interchangeable model, P_e = P_m + L(P_m, T, w). With MotorModel('const') it equals R1's
  derivatives exactly (tests/test_r3.py). R1 and R2 code are imported, never modified.
- Quasi-static evaluation of a speed trajectory (constant acceleration per step, 3-point
  Gauss-Legendre in time), used by both DP bounds:
    band_dp : minimum energy over all trajectories within |v - v_ref| <= delta at every sample,
              same duration, distance >= the reference's (the "same tracking task" bound);
    eco_dp  : distance-domain minimum of energy + lambda * time between the reference's stops
              (the separate eco-driving task, R3-C).
  The quasi-static model ignores the RC polarisation voltage V1 (R1 share of R1 losses
  0.02-0.36 % of energy); the dynamic plant keeps it.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
R3 = HERE.parent                       # R3_20261025
RR = R3.parent                         # research_recovery_20261025
R1 = RR.parent                         # scientific_rebuild_20261024
REPO = R1.parents[1]
for p in (str(REPO / "src"), str(R1 / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

from eureka.plant import BatchParams  # noqa: E402
from rebuild.model import IX, LOSS_TERMS, STATES, BatteryLimits, battery_limits  # noqa: E402

INF = np.inf
GL_X = np.array([0.5 - np.sqrt(15) / 10, 0.5, 0.5 + np.sqrt(15) / 10])   # Gauss-Legendre nodes on [0, 1]
GL_W = np.array([5 / 18, 8 / 18, 5 / 18])


# --------------------------------------------------------------------------- motor/inverter loss
@dataclass(frozen=True)
class MotorModel:
    """Combined motor + inverter loss L >= 0, so that P_e = P_m + L (both directions).

    const  : L = P_m (1/eta - 1) motoring, |P_m| (1 - eta) regenerating   (R1, eta = 0.874)
    curve  : as const with eta = eta(|P_m| / p_rated) interpolated from a published curve
    copper : L = k_c T^2 (all loss as copper loss; controller-favourable stress model)
    """

    kind: str
    eta: float = 0.874
    frac: tuple = ()
    eff: tuple = ()
    p_rated: float = 18000.0
    k_c: float = 0.0
    label: str = ""

    def _eta(self, pm_abs):
        if self.kind == "const":
            return np.full_like(pm_abs, self.eta, dtype=float)
        return np.interp(pm_abs / self.p_rated, self.frac, self.eff)

    def loss(self, pm, T):
        if self.kind == "copper":
            return self.k_c * T * T
        eta = self._eta(np.abs(pm))
        return np.where(pm >= 0, pm * (1.0 / eta - 1.0), -pm * (1.0 - eta))

    # inverse maps used for the battery-derived torque limits ------------------------------
    def _table(self):
        pm = np.linspace(0.0, 1.5 * self.p_rated, 3001)
        eta = self._eta(pm)
        return pm, pm / eta, pm * eta          # mechanical, electrical drawn (drive), electrical returned (regen)

    def pm_drive_max(self, pe_max, w):
        """Largest mechanical drive power whose electrical demand is <= pe_max (>= 0)."""
        pe_max = np.maximum(pe_max, 0.0)
        if self.kind == "copper":
            a = self.k_c / np.maximum(w, 1e-6) ** 2
            return (-1.0 + np.sqrt(1.0 + 4.0 * a * pe_max)) / (2.0 * a)
        pm, pe, _ = self._table()
        return np.interp(pe_max, pe, pm, right=INF)

    def pm_regen_max(self, pc_max, w):
        """Largest mechanical braking power whose electrical return is <= pc_max (>= 0); INF if never reached."""
        pc_max = np.maximum(pc_max, 0.0)
        if self.kind == "copper":
            a = self.k_c / np.maximum(w, 1e-6) ** 2
            disc = 1.0 - 4.0 * a * pc_max
            return np.where(disc >= 0, (1.0 - np.sqrt(np.maximum(disc, 0.0))) / (2.0 * a), INF)
        pm, _, pr = self._table()
        return np.interp(pc_max, pr, pm, right=INF)


def motor_models() -> dict:
    """The three R3 loss branches, built one way for every script (R3_motor_curve_audit.md)."""
    import json
    m1 = json.loads((R3 / "data" / "motor_curve_m1_derived.json").read_text(encoding="utf-8"))
    return {
        "M0": MotorModel("const", eta=0.874, label="M0 constant 0.874 (thesis)"),
        "M1": MotorModel("curve", frac=tuple(m1["frac"]), eff=tuple(m1["eff"]), p_rated=m1["p_rated_W"],
                         label="M1 FASTSim generic e-machine curve (illustrative)"),
        "M2": MotorModel("copper", k_c=18000.0 * (1 / 0.874 - 1) / 85.0**2, label="M2 copper-loss stress model"),
    }


# --------------------------------------------------------------------------- dynamic plant
def torque_limits(w, V1, bp: BatchParams, lim: BatteryLimits, mm: MotorModel):
    w_pos = np.maximum(w, 1e-6)
    base = np.minimum(bp.T_max, bp.P_max / w_pos)
    if not lim.active:
        return base, base, base
    _, _, p_d, p_c = battery_limits(V1, bp, lim)
    t_pos = np.minimum(base, mm.pm_drive_max(p_d, w_pos) / w_pos)
    t_neg = np.minimum(base, mm.pm_regen_max(p_c, w_pos) / w_pos)
    return t_pos, t_neg, base


def battery_current(T, w, V1, bp, mm: MotorModel):
    p_m = T * w
    p_e = p_m + mm.loss(p_m, T)
    vo = bp.V_oc - V1
    disc = vo * vo - 4.0 * bp.R0 * p_e
    i = (vo - np.sqrt(np.maximum(disc, 0.0))) / (2.0 * bp.R0)
    return i, p_e, p_m, disc >= 0


def derivatives(y, t_ref, bp: BatchParams, lim: BatteryLimits, mm: MotorModel):
    """R1 rebuild.model.derivatives with P_e = P_m + L. Same states and ledger terms."""
    v_raw = y[:, IX["v"]]
    v = np.maximum(v_raw, 0.0)
    T = y[:, IX["T"]]
    V1 = y[:, IX["V1"]]
    gr = bp.G / bp.r_w
    w = gr * v
    t_pos, t_neg, _ = torque_limits(w, V1, bp, lim, mm)
    t_cmd = np.clip(t_ref, -t_neg, t_pos)

    t_s = T - bp.B_m * w
    f_w = np.where(t_s >= 0, gr * t_s * bp.eta_g, gr * t_s / bp.eta_g)
    s = np.tanh(v / bp.v_eps)
    f_rr = bp.Crr * bp.M * bp.g * s
    f_aero = 0.5 * bp.rho * bp.Cd * bp.A_f * v * v
    f_fb = gr * np.maximum(0.0, -t_neg - t_ref) * s
    dv = (f_w - f_rr - f_aero - f_fb) / bp.M_eff
    dv = np.where((v_raw <= 0.0) & (dv < 0.0), 0.0, dv)

    i, p_e, p_m, feasible = battery_current(T, w, V1, bp, mm)
    if lim.active:
        i_d, i_c, _, _ = battery_limits(V1, bp, lim)

    dy = np.empty_like(y)
    dy[:, IX["v"]] = dv
    dy[:, IX["T"]] = (t_cmd - T) / bp.tau_T
    dy[:, IX["V1"]] = -V1 / (bp.R1 * bp.C1) + i / bp.C1
    dy[:, IX["SoC"]] = -i / (3600.0 * bp.Q_Ah * bp.soh)
    dy[:, IX["E_chem"]] = bp.V_oc * i
    dy[:, IX["E_rr"]] = f_rr * v
    dy[:, IX["E_aero"]] = f_aero * v
    dy[:, IX["E_fb"]] = f_fb * v
    dy[:, IX["E_gear"]] = t_s * w - f_w * v
    dy[:, IX["E_visc"]] = bp.B_m * w * w
    dy[:, IX["E_mi"]] = p_e - p_m
    dy[:, IX["E_R0"]] = bp.R0 * i * i
    dy[:, IX["E_R1"]] = V1 * V1 / bp.R1
    dy[:, IX["dist"]] = v
    dy[:, IX["Ah"]] = np.abs(i) / 3600.0
    dy[:, IX["E_regen"]] = np.minimum(p_e, 0.0)
    dy[:, IX["E_pos"]] = np.maximum(bp.V_oc * i, 0.0)
    dy[:, IX["E_neg"]] = np.minimum(bp.V_oc * i, 0.0)
    if lim.active:
        over = np.maximum(i - i_d, 0.0) + np.maximum(-i - i_c, 0.0)
        dy[:, IX["I_over"]] = np.where(np.isfinite(over), over, 0.0)
    else:
        dy[:, IX["I_over"]] = 0.0
    return dy, feasible


def rk4_step(y, t_ref, bp, lim, mm, h):
    k1, f1 = derivatives(y, t_ref, bp, lim, mm)
    k2, f2 = derivatives(y + 0.5 * h * k1, t_ref, bp, lim, mm)
    k3, f3 = derivatives(y + 0.5 * h * k2, t_ref, bp, lim, mm)
    k4, f4 = derivatives(y + h * k3, t_ref, bp, lim, mm)
    out = y + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
    out[:, IX["v"]] = np.maximum(out[:, IX["v"]], 0.0)
    return out, f1 & f2 & f3 & f4


def energy_closure(y_end, y0, bp):
    ke = 0.5 * bp.M_eff * (y_end[:, IX["v"]] ** 2 - y0[:, IX["v"]] ** 2)
    ec1 = 0.5 * bp.C1 * (y_end[:, IX["V1"]] ** 2 - y0[:, IX["V1"]] ** 2)
    sinks = ke + ec1 + sum(y_end[:, IX[k]] - y0[:, IX[k]] for k in LOSS_TERMS)
    supplied = y_end[:, IX["E_chem"]] - y0[:, IX["E_chem"]]
    return supplied - sinks, supplied


def simulate(profile, params, gains, soh, lim: BatteryLimits, mm: MotorModel, dt=None):
    """Closed loop as R1 (10 ms ZOH, RK4 substeps, conditional anti-windup on T_pos), one limit set.

    Tracking metrics are taken against `profile` (the reference the controller tracks)."""
    n = len(params)
    ts = params[0].Ts
    dt = params[0].dt if dt is None else dt
    sub = round(ts / dt)
    if abs(sub * dt - ts) > 1e-12:
        raise ValueError("Ts must be an integer multiple of dt")
    steps = round(profile.duration / ts)
    gains = np.asarray(gains, dtype=float).reshape(n, 3)
    bp = BatchParams.from_params(params, np.asarray(soh, dtype=float))
    gr = bp.G / bp.r_w
    y = np.zeros((n, len(STATES)))
    y[:, IX["SoC"]] = 0.8
    y0 = y.copy()
    z = np.zeros(n)
    acc = {k: np.zeros(n) for k in ("se2", "max_e", "i2", "max_i", "sat_batt", "steps")}
    feasible = np.ones(n, dtype=bool)
    nonfinite = np.zeros(n, dtype=bool)
    for k in range(steps + 1):
        v_ref = float(profile.sample(np.array([k * ts]))[0])
        v = y[:, IX["v"]]
        e = v - v_ref
        u = -(gains[:, 0] * e + gains[:, 1] * y[:, IX["T"]] + gains[:, 2] * z)
        t_pos, _, base = torque_limits(gr * v, y[:, IX["V1"]], bp, lim, mm)
        sat = u > t_pos
        i, _, _, _ = battery_current(y[:, IX["T"]], gr * v, y[:, IX["V1"]], bp, mm)
        acc["se2"] += e * e
        acc["max_e"] = np.maximum(acc["max_e"], np.abs(e))
        acc["i2"] += i * i
        acc["max_i"] = np.maximum(acc["max_i"], np.abs(i))
        acc["sat_batt"] += sat & (t_pos < base - 1e-9)
        acc["steps"] += 1
        nonfinite |= ~np.all(np.isfinite(y), axis=1)
        if k == steps:
            break
        z = np.where(sat & (e < 0), z, z + ts * e)
        for _ in range(sub):
            y, f = rk4_step(y, u, bp, lim, mm, dt)
            feasible &= f
    closure, supplied = energy_closure(y, y0, bp)
    return {"y0": y0, "y_end": y, "acc": acc, "closure_J": closure, "feasible": feasible, "nonfinite": nonfinite,
            "ref_distance_m": float(profile.stats()["distance_m"]), "dt": dt}


def sim_metrics(out, j, p) -> dict:
    y0, y1, a = out["y0"][j], out["y_end"][j], out["acc"]
    d = (y1[IX["dist"]] - y0[IX["dist"]]) / 1000.0
    dref = out["ref_distance_m"] / 1000.0
    E = (y1[IX["E_chem"]] - y0[IX["E_chem"]]) / 3600.0
    ah = y1[IX["Ah"]] - y0[IX["Ah"]]
    thr = p.V_oc * 3600.0 * ah
    clos = float(abs(out["closure_J"][j]) / thr) if thr > 0 else float("inf")
    st = a["steps"][j]
    reasons = []
    if out["nonfinite"][j] or not np.all(np.isfinite(y1)):
        reasons.append("non-finite state")
    if not out["feasible"][j]:
        reasons.append("battery solution infeasible")
    if clos > 1e-3:
        reasons.append(f"closure {clos:.2e}")
    ledger = {f"{k}_Wh": float((y1[IX[k]] - y0[IX[k]]) / 3600.0) for k in LOSS_TERMS}
    return {"distance_km": d, "shortfall_pct": 100 * (dref - d) / dref, "rmse_ms": float(np.sqrt(a["se2"][j] / st)),
            "max_abs_err_ms": float(a["max_e"][j]), "E_net_Wh": E, "Wh_per_km": E / d if d > 0 else float("nan"),
            "Ah": float(ah), "rms_current_A": float(np.sqrt(a["i2"][j] / st)), "peak_current_A": float(a["max_i"][j]),
            "batt_limited_frac": float(a["sat_batt"][j] / st),
            "I_over_As": float(y1[IX["I_over"]] - y0[IX["I_over"]]), "closure_rel": clos,
            "valid": not reasons, "invalid_reasons": "; ".join(reasons), **ledger}


# --------------------------------------------------------------------------- quasi-static plant
@dataclass(frozen=True)
class QSPlant:
    """Quasi-static (V1 = 0) version of the dynamic plant for one parameter set."""

    p: object                 # eureka Params with overrides applied
    soh: float
    lim: BatteryLimits
    mm: MotorModel
    bp: BatchParams = field(init=False, repr=False, compare=False)

    def __post_init__(self):
        object.__setattr__(self, "bp", BatchParams.from_params([self.p], np.array([self.soh])))

    def point(self, v, a):
        """Chemical power, friction power, |current| and feasibility at speed v [m/s], acceleration a [m/s^2]."""
        bp, mm = self.bp, self.mm
        R0 = float(bp.R0[0])
        gr = float(bp.G[0] / bp.r_w[0])
        M, Meff, g = float(bp.M[0]), float(bp.M_eff[0]), float(bp.g[0])
        v = np.maximum(v, 0.0)
        w = gr * v
        f_req = Meff * a + float(bp.Crr[0]) * M * g * np.tanh(v / float(bp.v_eps[0])) \
            + 0.5 * float(bp.rho[0] * bp.Cd[0] * bp.A_f[0]) * v * v
        eta_g, Bm = float(bp.eta_g[0]), float(bp.B_m[0])
        t_s = np.where(f_req >= 0, f_req / (gr * eta_g), f_req * eta_g / gr)
        T = t_s + Bm * w
        bp1 = self.bp
        t_pos, t_neg, _ = torque_limits(w, np.zeros_like(w), _broadcast(bp1, w), self.lim, mm)
        drive_ok = T <= t_pos + 1e-9
        T_m = np.maximum(T, -t_neg)                          # regen beyond the limit goes to the friction brake
        t_s_m = T_m - Bm * w
        f_motor = np.where(t_s_m >= 0, gr * t_s_m * eta_g, gr * t_s_m / eta_g)
        p_fb = np.maximum(f_motor - f_req, 0.0) * v          # friction-brake dissipation
        p_m = T_m * w
        p_e = p_m + mm.loss(p_m, T_m)
        Voc = float(bp.V_oc[0])
        disc = Voc * Voc - 4.0 * R0 * p_e
        i = (Voc - np.sqrt(np.maximum(disc, 0.0))) / (2.0 * R0)
        ok = drive_ok & (disc >= 0)
        if self.lim.active:
            i_d, i_c, _, _ = battery_limits(np.zeros(1), bp1, self.lim)
            ok &= (i <= float(i_d[0]) + 1e-6)
        return Voc * i, p_fb, np.abs(i), i * i, ok

    def step(self, va, vb, h):
        """Energy [J], friction [J], Ah, int i^2 dt, distance [m], feasible for constant-acceleration steps."""
        a = (vb - va) / h
        E = np.zeros(np.broadcast(va, vb, h).shape)
        Fb = np.zeros_like(E)
        Ah = np.zeros_like(E)
        I2 = np.zeros_like(E)
        ok = np.ones_like(E, dtype=bool)
        for x, wgt in zip(GL_X, GL_W):
            pc, pf, ia, i2, f = self.point(va + a * x * h, a)
            E += wgt * pc * h
            Fb += wgt * pf * h
            Ah += wgt * ia * h / 3600.0
            I2 += wgt * i2 * h
            ok &= f
        return E, Fb, Ah, I2, 0.5 * (va + vb) * h, ok


def _broadcast(bp, like):
    """BatchParams with one run, usable against arrays of any shape (scalars per field)."""
    return _ScalarBP(bp)


class _ScalarBP:
    def __init__(self, bp):
        self._bp = bp

    def __getattr__(self, name):
        val = getattr(self._bp, name)
        return float(val[0]) if isinstance(val, np.ndarray) and val.size == 1 else val


def evaluate(plant: QSPlant, v, h):
    """Quasi-static totals of a sampled trajectory v[0..N] with step h."""
    E, Fb, Ah, I2, s, ok = plant.step(v[:-1], v[1:], h)
    return {"E_J": float(E.sum()), "fric_J": float(Fb.sum()), "Ah": float(Ah.sum()), "I2_A2s": float(I2.sum()),
            "dist_m": float(s.sum()), "feasible": bool(ok.all()), "n_infeasible_steps": int((~ok).sum())}


# --------------------------------------------------------------------------- band DP (same task)
def band_dp(plant: QSPlant, v_ref, h, delta, dv, mu):
    """min sum(E - mu*s) over v_k = v_ref_k + j*dv, |j*dv| <= delta, v_k >= 0, v_0 = v_ref_0, v_N = v_ref_N."""
    J = int(round(delta / dv))
    offs = np.arange(-J, J + 1) * dv
    n = len(v_ref) - 1
    cost = np.full(2 * J + 1, INF)
    cost[J] = 0.0
    back = np.zeros((n, 2 * J + 1), dtype=np.int32)
    for k in range(n):
        va = v_ref[k] + offs
        vb = v_ref[k + 1] + offs
        E, _, _, _, s, ok = plant.step(va[:, None], vb[None, :], h)
        ok &= (va[:, None] >= -1e-12) & (vb[None, :] >= -1e-12)
        tot = cost[:, None] + np.where(ok, E - mu * s, INF)
        back[k] = np.argmin(tot, axis=0)
        cost = tot[back[k], np.arange(2 * J + 1)]
        if k == n - 1:
            cost = np.where(np.arange(2 * J + 1) == J, cost, INF)
    if not np.isfinite(cost[J]):
        return None
    j = J
    path = np.empty(n + 1, dtype=int)
    path[n] = J
    for k in range(n - 1, -1, -1):
        j = back[k, j]
        path[k] = j
    return v_ref + offs[path]


def band_min_energy(plant: QSPlant, v_ref, h, delta, dv, d_target, iters=40):
    """Smallest-energy trajectory in the band whose distance is >= d_target (bisection on mu)."""
    lo, hi = 0.0, 1.0
    v_hi = band_dp(plant, v_ref, h, delta, dv, hi)
    if v_hi is None:
        return None
    while evaluate(plant, v_hi, h)["dist_m"] < d_target - 1e-9:
        hi *= 4.0
        v_hi = band_dp(plant, v_ref, h, delta, dv, hi)
        if hi > 1e6:
            return None
    best = v_hi
    v_lo = band_dp(plant, v_ref, h, delta, dv, lo)
    if evaluate(plant, v_lo, h)["dist_m"] >= d_target - 1e-9:
        return v_lo
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        vm = band_dp(plant, v_ref, h, delta, dv, mid)
        if evaluate(plant, vm, h)["dist_m"] >= d_target - 1e-9:
            hi, best = mid, vm
        else:
            lo = mid
    return best


# --------------------------------------------------------------------------- eco DP (separate task)
def segments(v_ref, h):
    """Moving segments between standstills of a sampled reference: list of (k_start, k_end)."""
    moving = v_ref > 1e-9
    segs, k = [], 0
    n = len(v_ref)
    while k < n:
        if moving[k]:
            ks = max(k - 1, 0)
            while k < n and moving[k]:
                k += 1
            segs.append((ks, min(k, n - 1)))
        else:
            k += 1
    return segs


def eco_segment_tables(plant: QSPlant, D, v_lim, a_lo, a_hi, ds, dv):
    """Transition energy and time matrices for one segment of length D (fixed step ds' = D/N)."""
    N = max(int(round(D / ds)), 2)
    dsp = D / N
    nv = int(round(v_lim / dv)) + 1
    vg = np.linspace(0.0, v_lim, nv)
    va, vb = vg[:, None], vg[None, :]
    with np.errstate(divide="ignore", invalid="ignore"):
        tt = 2.0 * dsp / (va + vb)
        a = (vb * vb - va * va) / (2.0 * dsp)
    valid = (va + vb > 0) & (a >= a_lo - 1e-9) & (a <= a_hi + 1e-9)
    hh = np.where(valid, tt, 1.0)
    E, Fb, Ah, I2, _, ok = plant.step(np.broadcast_to(va, hh.shape), np.broadcast_to(vb, hh.shape), hh)
    valid &= ok
    return {"N": N, "ds": dsp, "v": vg, "E": np.where(valid, E, INF), "t": np.where(valid, tt, INF),
            "Fb": Fb, "Ah": Ah, "I2": I2}


def eco_segment_solve(tab, lam):
    """Min sum(E + lam*t) from v = 0 to v = 0 over N equal distance steps; returns (E, t, Ah, I2, Fb, speeds)."""
    N, nv = tab["N"], len(tab["v"])
    C = tab["E"] + lam * tab["t"]
    cost = np.full(nv, INF)
    cost[0] = 0.0
    back = np.zeros((N, nv), dtype=np.int32)
    for k in range(N):
        tot = cost[:, None] + C
        back[k] = np.argmin(tot, axis=0)
        cost = tot[back[k], np.arange(nv)]
    if not np.isfinite(cost[0]):
        return None
    idx = np.empty(N + 1, dtype=int)
    idx[N] = 0
    for k in range(N - 1, -1, -1):
        idx[k] = back[k, idx[k + 1]]
    ia, ib = idx[:-1], idx[1:]
    return {"E": float(tab["E"][ia, ib].sum()), "t": float(tab["t"][ia, ib].sum()), "Ah": float(tab["Ah"][ia, ib].sum()),
            "I2": float(tab["I2"][ia, ib].sum()), "Fb": float(tab["Fb"][ia, ib].sum()), "v": tab["v"][idx]}


def eco_trip(tables, idle_s, lam):
    sols = [eco_segment_solve(t, lam) for t in tables]
    if any(s is None for s in sols):
        return None
    tot = {k: sum(s[k] for s in sols) for k in ("E", "t", "Ah", "I2", "Fb")}
    tot["T_total"] = tot["t"] + idle_s
    tot["sols"] = sols
    return tot


def eco_for_time(tables, idle_s, T_target, iters=40):
    """Lowest-energy trip (supported DP point) whose total time is <= T_target (bisection on log lambda)."""
    lo, hi = -3.0, 4.0                       # log10(lambda [W])
    best = eco_trip(tables, idle_s, 10 ** hi)
    if best is None or best["T_total"] > T_target:
        return None, None
    lam_best = 10 ** hi
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        r = eco_trip(tables, idle_s, 10 ** mid)
        if r is not None and r["T_total"] <= T_target:
            hi, best, lam_best = mid, r, 10 ** mid
        else:
            lo = mid
    return best, lam_best


def eco_profile(trip, tables, v_ref, h):
    """Time-domain knots of an eco trip: idle intervals of the reference are kept where they are in sequence."""
    segs = segments(v_ref, h)
    t, v = [0.0], [0.0]
    k_prev = 0
    for (ks, ke), sol, tab in zip(segs, trip["sols"], tables):
        idle = (ks - k_prev) * h
        if idle > 0:
            t.append(t[-1] + idle)
            v.append(0.0)
        vs = sol["v"]
        dts = 2.0 * tab["ds"] / (vs[:-1] + vs[1:])
        for dt_, vv in zip(dts, vs[1:]):
            t.append(t[-1] + dt_)
            v.append(vv)
        k_prev = ke
    tail = (len(v_ref) - 1 - k_prev) * h
    if tail > 0:
        t.append(t[-1] + tail)
        v.append(0.0)
    return np.array(t), np.array(v)


# --------------------------------------------------------------------------- R3 v1 additions (2026-10-25, before the freeze)
# Same equations as above (every energy comes from QSPlant.step); faster tables, the baseline task
# for references that cannot be tracked exactly, and Lagrangian dual bounds. R3_optimizer_validity.md.
def track_dp(plant: QSPlant, v_ref, h, W, dv):
    """Feasible trajectory closest to v_ref: min sum_k (v_k - v_ref,k)^2 over v_k = v_ref,k + j dv, |j dv| <= W,
    v_k >= 0, ends fixed to the reference. Returns (path, sse, hit_boundary) or (None, inf, True)."""
    J = int(round(W / dv))
    offs = np.arange(-J, J + 1) * dv
    m = 2 * J + 1
    n = len(v_ref) - 1
    cost = np.full(m, INF)
    cost[J] = 0.0
    back = np.zeros((n, m), dtype=np.int32)
    pen = offs * offs
    for k in range(n):
        va = v_ref[k] + offs
        vb = v_ref[k + 1] + offs
        *_, ok = plant.step(va[:, None], vb[None, :], h)
        ok &= (va[:, None] >= -1e-12) & (vb[None, :] >= -1e-12)
        tot = cost[:, None] + np.where(ok, pen[None, :], INF)
        back[k] = np.argmin(tot, axis=0)
        cost = tot[back[k], np.arange(m)]
    if not np.isfinite(cost[J]):
        return None, INF, True
    path = np.empty(n + 1, dtype=int)
    path[n] = J
    for k in range(n - 1, -1, -1):
        path[k] = back[k, path[k + 1]]
    hit = bool(np.any(np.abs(path - J) == J))
    return v_ref + offs[path], float(cost[J]), hit


def band_tables(plant: QSPlant, centre, h, delta, dv, chunk=64):
    """Step-energy tables E[k, i, j] for the band |v - centre| <= delta (INF where infeasible or v < 0)."""
    J = int(round(delta / dv))
    offs = np.arange(-J, J + 1) * dv
    n = len(centre) - 1
    m = 2 * J + 1
    E = np.empty((n, m, m))
    for c0 in range(0, n, chunk):
        c1 = min(c0 + chunk, n)
        va = (centre[c0:c1, None] + offs)[:, :, None]
        vb = (centre[c0 + 1:c1 + 1, None] + offs)[:, None, :]
        e, _, _, _, _, ok = plant.step(va, vb, h)
        ok = ok & (va >= -1e-12) & (vb >= -1e-12)
        E[c0:c1] = np.where(ok, e, INF)
    return {"E": E, "offs": offs, "centre": np.asarray(centre, dtype=float), "h": h, "J": J}


def band_dp_tab(tab, mu):
    """band_dp on precomputed tables: (path or None, min sum(E - mu s))."""
    E, offs, c, h, J = tab["E"], tab["offs"], tab["centre"], tab["h"], tab["J"]
    n, m, _ = E.shape
    cost = np.full(m, INF)
    cost[J] = 0.0
    back = np.zeros((n, m), dtype=np.int32)
    for k in range(n):
        s = 0.5 * ((c[k] + offs)[:, None] + (c[k + 1] + offs)[None, :]) * h
        tot = cost[:, None] + (E[k] - mu * s)
        back[k] = np.argmin(tot, axis=0)
        cost = tot[back[k], np.arange(m)]
    if not np.isfinite(cost[J]):
        return None, INF
    path = np.empty(n + 1, dtype=int)
    path[n] = J
    for k in range(n - 1, -1, -1):
        path[k] = back[k, path[k + 1]]
    return c + offs[path], float(cost[J])


def band_min_energy_tab(plant: QSPlant, tab, d_target, iters=40):
    """Best feasible band trajectory with distance >= d_target (bisection on mu), plus the Lagrangian
    lower bound max_mu [min sum(E - mu s) + mu d_target] over every mu evaluated (valid for the
    discretised problem only). Returns dict(path, E_J, dist_m, lb_J, mu, n_dp) or None."""
    lb = -INF
    n_dp = 0

    def run(mu):
        nonlocal lb, n_dp
        path, val = band_dp_tab(tab, mu)
        n_dp += 1
        if path is None:
            return None, None
        lb = max(lb, val + mu * d_target)
        return path, evaluate(plant, path, tab["h"])

    lo, hi = 0.0, 1.0
    p_hi, r_hi = run(hi)
    if p_hi is None:
        return None
    while r_hi["dist_m"] < d_target - 1e-9:
        hi *= 4.0
        if hi > 1e6:
            return None
        p_hi, r_hi = run(hi)
    best, rb, mu_b = p_hi, r_hi, hi
    p_lo, r_lo = run(lo)
    if r_lo["dist_m"] >= d_target - 1e-9:
        best, rb, mu_b = p_lo, r_lo, lo
    else:
        for _ in range(iters):
            mid = 0.5 * (lo + hi)
            pm_, rm = run(mid)
            if rm["dist_m"] >= d_target - 1e-9:
                hi, best, rb, mu_b = mid, pm_, rm, mid
            else:
                lo = mid
    return {"path": best, "E_J": rb["E_J"], "dist_m": rb["dist_m"], "lb_J": lb, "mu": mu_b, "n_dp": n_dp, "eval": rb}


class EcoSolver:
    """Eco DP over all segments with a cache of lambda evaluations; dual bound for each time budget."""

    def __init__(self, tables, idle_s):
        self.tables, self.idle = tables, idle_s
        self.cache = {}

    def trip(self, lam):
        if lam not in self.cache:
            self.cache[lam] = eco_trip(self.tables, self.idle, lam)
        return self.cache[lam]

    def for_time(self, T_target, iters=30):
        """Best supported trip with T_total <= T_target, and lb = max_lambda [E + lambda t - lambda (T_target - idle)]
        over every cached lambda (valid for the discretised problem). Returns (trip or None, lam, lb_J, t_min)."""
        fast = self.trip(10 ** 4.0)
        t_min = fast["T_total"] if fast else INF
        if fast is None or fast["T_total"] > T_target + 1e-9:
            return None, None, None, t_min
        lo, hi = -3.0, 4.0
        best, lam_b = fast, 10 ** hi
        for _ in range(iters):
            mid = 0.5 * (lo + hi)
            r = self.trip(10 ** mid)
            if r is not None and r["T_total"] <= T_target + 1e-9:
                hi, best, lam_b = mid, r, 10 ** mid
            else:
                lo = mid
        tau = T_target - self.idle
        lb = max(r["E"] + lam * (r["t"] - tau) for lam, r in self.cache.items() if r is not None)
        return best, lam_b, lb, t_min
