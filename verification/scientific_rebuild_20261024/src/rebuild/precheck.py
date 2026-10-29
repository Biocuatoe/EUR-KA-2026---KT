"""Analytical pre-check (protocol section 8): demand along each reference vs motor and battery limits.

Quasi-static inverse model on the reference itself (no controller): wheel force from
M_eff*a + road loads, then motor torque, mechanical and electrical power, and the battery
current at V1 = 0. Writes results/precheck_*.csv. Indicative only (no torque lag, no tracking error).
"""

from __future__ import annotations

import csv

import numpy as np

from eureka.params import load_params
from eureka.plant import BatchParams
from rebuild.model import BatteryLimits, battery_limits
from rebuild.run import CFG, HERE, load_cycle


def demand(prof, p):
    t = np.arange(0.0, prof.duration + 1e-9, 0.01)
    v = prof.sample(t)
    a = np.gradient(v, t)
    w = p.G / p.r_w * v
    F = p.M_eff * a + p.Crr * p.M * p.g * (v > 0) + 0.5 * p.rho * p.Cd * p.A_f * v * v
    T_s = np.where(F >= 0, F * p.r_w / (p.G * p.eta_g), F * p.r_w * p.eta_g / p.G)
    T = T_s + p.B_m * w
    P_m = T * w
    P_e = np.where(P_m >= 0, P_m / p.eta_mi, P_m * p.eta_mi)
    return t, v, a, w, T, P_m, P_e


def main():
    base = load_params()
    rows, thr = [], []
    for cyc in CFG["cycles"]:
        prof = load_cycle(cyc)
        t, v, a, w, T, P_m, P_e = demand(prof, base)
        T_lim = np.minimum(base.T_max, base.P_max / np.maximum(w, 1e-6))
        motor_viol = np.mean(T > T_lim + 1e-9)
        pe_max = float(P_e.max())
        vmin, vmax = 0.78125 * base.V_oc, 1.140625 * base.V_oc
        r0_star = vmin * (base.V_oc - vmin) / pe_max
        thr.append({"cycle": cyc, "label": CFG["cycles"][cyc]["label"], "max_accel_ms2": float(a.max()),
                    "max_speed_kmh": float(v.max() * 3.6), "max_motor_torque_Nm": float(T.max()),
                    "max_mech_power_kW": float(P_m.max() / 1e3), "max_elec_power_kW": pe_max / 1e3,
                    "min_elec_power_kW": float(P_e.min() / 1e3), "frac_steps_exceeding_motor_limits": float(motor_viol),
                    "R0_star_voltage_window_binds_mohm": r0_star * 1e3,
                    "k_r0_needed_at_soh_0.7": (r0_star / base.R0_new - 1) / 0.3})
        for case, cs in CFG["cases"].items():
            if not cs["limits"]:
                continue
            lim = BatteryLimits(**cs["limits"])
            p = base.with_overrides(k_r0=cs["k_r0"])
            for soh in CFG["soh"]:
                bp = BatchParams.from_params([p], np.array([soh]))
                i_d, i_c, p_d, p_c = battery_limits(np.zeros(1), bp, lim)
                rows.append({"cycle": cyc, "case": case, "soh": soh, "P_dis_max_kW": float(p_d[0] / 1e3),
                             "P_ch_max_kW": float(p_c[0] / 1e3), "I_dis_max_A": float(i_d[0]), "I_ch_max_A": float(i_c[0]),
                             "frac_time_drive_demand_above_battery": float(np.mean(P_e > p_d[0])),
                             "frac_time_regen_demand_above_battery": float(np.mean(-P_e > p_c[0])),
                             "max_drive_ratio": float(P_e.max() / p_d[0]), "max_regen_ratio": float(-P_e.min() / p_c[0])})
    for name, data in (("precheck_cycles.csv", thr), ("precheck_battery_limits.csv", rows)):
        with (HERE / "results" / name).open("w", newline="", encoding="utf-8") as f:
            wr = csv.DictWriter(f, fieldnames=list(data[0]))
            wr.writeheader()
            wr.writerows(data)
    for r in thr:
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
    for r in rows:
        if r["case"] in ("BV", "BCS", "BCS2") and r["soh"] in (1.0, 0.7):
            print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})


if __name__ == "__main__":
    main()
