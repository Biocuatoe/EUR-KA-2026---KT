"""POST-FREEZE CHECK (not part of R3_protocol_v1.md): size of the regeneration/friction-split lever under M2.

    python -I check_m2_regen_split.py      -> ../outputs/checks/m2_regen_split.csv

Under M2 (L = k_c T^2) the battery return of motor braking, -(T w + k_c T^2), is largest at
T* = -w / (2 k_c). R3's plant always brakes with the motor up to its limit T_m and sends the rest to
friction; below about 2.5 m/s that is not energy-optimal. For each baseline and gate-band (delta 0.25)
trajectory saved by run_gates.py, this recomputes the QS energy with motor braking torque
T' = clamp(T*, T_m, 0) (rest to friction) and reports the difference. Same equations as QSPlant.point
otherwise (re-implemented here for the braking branch only; checked against QSPlant at T' = T_m).
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r3_lib as L  # noqa: E402
import run_gates as RG  # noqa: E402
from rebuild.model import battery_limits  # noqa: E402

OUT = L.R3 / "outputs" / "checks"


def energy(pl, v, h, optimal_split):
    bp, mm = pl.bp, pl.mm
    R0, Voc = float(bp.R0[0]), float(bp.V_oc[0])
    gr = float(bp.G[0] / bp.r_w[0])
    M, Meff, g = float(bp.M[0]), float(bp.M_eff[0]), float(bp.g[0])
    eta_g, Bm = float(bp.eta_g[0]), float(bp.B_m[0])
    va, vb = v[:-1], v[1:]
    a = (vb - va) / h
    E = 0.0
    for x, wgt in zip(L.GL_X, L.GL_W):
        vv = np.maximum(va + a * x * h, 0.0)
        w = gr * vv
        f_req = Meff * a + float(bp.Crr[0]) * M * g * np.tanh(vv / float(bp.v_eps[0])) \
            + 0.5 * float(bp.rho[0] * bp.Cd[0] * bp.A_f[0]) * vv * vv
        t_s = np.where(f_req >= 0, f_req / (gr * eta_g), f_req * eta_g / gr)
        T = t_s + Bm * w
        _, t_neg, _ = L.torque_limits(w, np.zeros_like(w), L._broadcast(bp, w), pl.lim, mm)
        T_m = np.maximum(T, -t_neg)
        if optimal_split:
            t_star = -w / (2.0 * mm.k_c)
            T_m = np.where(T_m < 0, np.clip(t_star, T_m, 0.0), T_m)   # brake less with the motor when that returns more
        p_m = T_m * w
        p_e = p_m + mm.loss(p_m, T_m)
        disc = Voc * Voc - 4.0 * R0 * p_e
        i = (Voc - np.sqrt(np.maximum(disc, 0.0))) / (2.0 * R0)
        E += float(np.sum(wgt * Voc * i * h))
    return E


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for cyc in RG.CYCLES:
        for lim in ("L-R1", "L-EVE"):
            f = RG.OUT / "paths" / f"band_{cyc}_M2_{lim}.npz"
            if not f.exists():
                continue
            z = np.load(f)
            for pk in ("P1", "P3"):
                pl = RG.plant("M2", lim, pk)
                for key in (f"{pk}_baseline", f"{pk}_band0.25"):
                    if key not in z:
                        continue
                    v = z[key]
                    e_qs = L.evaluate(pl, v, RG.H)["E_J"]
                    e_max = energy(pl, v, RG.H, False)
                    e_opt = energy(pl, v, RG.H, True)
                    rows.append(dict(cycle=cyc, limits=lim, pstate=pk, trajectory=key.split("_", 1)[1],
                                     E_QSPlant_Wh=e_qs / 3600, E_maxregen_reimpl_Wh=e_max / 3600,
                                     reimpl_check_rel=abs(e_max - e_qs) / abs(e_qs), E_optimal_split_Wh=e_opt / 3600,
                                     split_saving_pct=100 * (1 - e_opt / e_max)))
    with (OUT / "m2_regen_split.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print({k: (round(v, 5) if isinstance(v, float) else v) for k, v in r.items()})


if __name__ == "__main__":
    main()
