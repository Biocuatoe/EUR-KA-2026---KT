"""POST-HOC DIAGNOSTIC (not in the protocol): why the M2 dynamic runs use 6-14 % more energy than the QS model.

    python -I diagnose_m2_qs_gap.py      -> ../outputs/checks/m2_qs_gap.csv, ../outputs/checks/m2_qs_gap_trace_S2.npz

Re-runs the R3-C S2 baseline (fixed R1 LQR, P1, L-R1) for M0 and M2 with the r3_lib.simulate loop,
recording v, T and the electrical loss at every control sample. Hypothesis: under M2 (L = k_c T^2)
torque held at standstill and torque ripple cost energy that QS (smooth inverse-dynamics torque, zero
torque at rest) does not see. Splits the dynamic motor loss into standstill (v_ref = 0 and v < 0.05 m/s)
and moving parts and compares with the QS motor loss on the same profile.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r3_lib as L  # noqa: E402
import r3_pilot as P  # noqa: E402
from eureka.plant import BatchParams  # noqa: E402
from rebuild.model import IX, STATES  # noqa: E402

OUT = L.R3 / "outputs" / "checks"


def traced(prof, p, K, lim, mm):
    ts, dt = p.Ts, p.dt
    sub = round(ts / dt)
    steps = round(prof.duration / ts)
    bp = BatchParams.from_params([p], np.array([1.0]))
    gr = bp.G / bp.r_w
    y = np.zeros((1, len(STATES)))
    y[:, IX["SoC"]] = 0.8
    z = np.zeros(1)
    rec = []
    for k in range(steps + 1):
        v_ref = float(prof.sample(np.array([k * ts]))[0])
        v = y[:, IX["v"]]
        e = v - v_ref
        u = -(K[0] * e + K[1] * y[:, IX["T"]] + K[2] * z)
        t_pos, _, _ = L.torque_limits(gr * v, y[:, IX["V1"]], bp, lim, mm)
        sat = u > t_pos
        T = y[:, IX["T"]]
        pm = T * gr * v
        rec.append((k * ts, v_ref, float(v[0]), float(T[0]), float(mm.loss(pm, T)[0]), float(y[0, IX["E_mi"]])))
        if k == steps:
            break
        z = np.where(sat & (e < 0), z, z + ts * e)
        for _ in range(sub):
            y, _ = L.rk4_step(y, u, bp, lim, mm, dt)
    return np.array(rec)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    p = P.load_params().with_overrides(k_r0=0.5)
    K = np.ravel(P.r1_gain(p, "fixed"))
    z = np.load(L.R3 / "outputs" / "gates" / "paths" / "band_S2_M0_L-R1.npz")
    prof = P.Profile("S2_baseline", z["t"], z["P1_baseline"])
    rows, traces = [], {}
    for mk in ("M0", "M2"):
        mm = L.motor_models()[mk]
        r = traced(prof, p, K, P.LIM["L-R1"], mm)
        traces[mk] = r
        t, vr, v, T, loss = r[:, 0], r[:, 1], r[:, 2], r[:, 3], r[:, 4]
        still = (vr <= 1e-9) & (v < 0.05)
        Ts = p.Ts
        e_mi_dyn = r[-1, 5] / 3600
        # QS motor loss on the same profile (inverse-dynamics torque at 1 s, 3-point Gauss)
        pl = L.QSPlant(p, 1.0, P.LIM["L-R1"], mm)
        vv = z["P1_baseline"]
        qs_loss = 0.0
        a = np.diff(vv)
        for x, wgt in zip(L.GL_X, L.GL_W):
            vs = vv[:-1] + a * x
            gr = p.G / p.r_w
            f = p.M_eff * a + p.Crr * p.M * p.g * np.tanh(vs / p.v_eps) + 0.5 * p.rho * p.Cd * p.A_f * vs * vs
            Tq = np.where(f >= 0, f / (gr * p.eta_g), f * p.eta_g / gr) + p.B_m * gr * vs
            qs_loss += float(np.sum(wgt * mm.loss(Tq * gr * vs, Tq))) / 3600
        rows.append(dict(motor=mk, dyn_motor_loss_Wh=e_mi_dyn, qs_motor_loss_Wh=qs_loss,
                         dyn_loss_standstill_Wh=float(np.sum(loss[still]) * Ts / 3600),
                         dyn_loss_moving_Wh=float(np.sum(loss[~still]) * Ts / 3600),
                         standstill_time_s=float(still.sum() * Ts), mean_abs_T_standstill_Nm=float(np.mean(np.abs(T[still]))),
                         rms_T_dyn_moving_Nm=float(np.sqrt(np.mean(T[~still] ** 2)))))
    with (OUT / "m2_qs_gap.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    np.savez_compressed(OUT / "m2_qs_gap_trace_S2.npz", **traces)
    for r in rows:
        print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})


if __name__ == "__main__":
    main()
