"""Metric definitions for the controller cross-check, written once and applied to BOTH the Python and the Modelica series.

The definitions restate src/eureka/metrics.py (run_metrics) and scripts/analyze.py (decide, dE_pct, rmse_ratio) from their
text; nothing is imported from eureka. A test in python_reference_runs.py confirms that these functions reproduce the
metrics stored in the project's artifacts/tables/primary_metrics.csv for the saved Python series.

Series convention (control-sample grid, k = 0..steps, t_k = k*Ts): arrays v, v_ref, T, u, t_lim, sat, i of length steps+1;
scalar end values of the integrated accumulators (y_end - y0): E_chem [J], dist [m], E_fb, E_regen, E_R0, E_R1 [J], Ah [A h].
"""
import numpy as np

TS = 0.01
V_OC = 48.0


def metrics(s: dict) -> dict:
    """s: dict with arrays v, v_ref, i, sat, u (len steps+1) and scalars E_chem, dist, E_fb, E_regen, E_R0, E_R1, Ah."""
    v, vr = np.asarray(s["v"], float), np.asarray(s["v_ref"], float)
    e = v - vr
    acc = np.diff(v) / TS
    jerk = np.diff(acc) / TS
    dist_km = s["dist"] / 1000.0
    e_wh = s["E_chem"] / 3600.0
    i = np.asarray(s["i"], float)
    rmse = float(np.sqrt(np.mean(e**2)))
    return {
        "distance_km": float(dist_km),
        "energy_Wh": float(e_wh),
        "energy_Wh_per_km": float(e_wh / dist_km),
        "rmse_ms": rmse,
        "max_abs_err_ms": float(np.max(np.abs(e))),
        "rms_current_A": float(np.sqrt(np.mean(i**2))),
        "peak_current_A": float(np.max(np.abs(i))),
        "ah_throughput": float(s["Ah"]),
        "resistive_loss_Wh": float((s["E_R0"] + s["E_R1"]) / 3600.0),
        "friction_brake_Wh": float(s["E_fb"] / 3600.0),
        "regen_recovered_Wh": float(-s["E_regen"] / 3600.0),
        "traction_limited_frac": float(np.mean(np.asarray(s["sat"], float))),
        "rms_jerk_ms3": float(np.sqrt(np.mean(jerk**2))),
        "rms_torque_cmd_Nm": float(np.sqrt(np.mean(np.asarray(s["u"], float) ** 2))),
        "tracking_failure": bool(rmse > 1.5 or np.max(np.abs(e)) > 3.0),
    }


def pair(fixed: dict, sched: dict) -> dict:
    """dE [%] relative to the matched fixed-gain run, RMSE ratio, and the preregistration section 9 decision."""
    d_e = (sched["energy_Wh_per_km"] - fixed["energy_Wh_per_km"]) / fixed["energy_Wh_per_km"] * 100.0
    ratio = sched["rmse_ms"] / fixed["rmse_ms"]
    return {"dE_pct": d_e, "rmse_ratio": ratio, "decision": decide(d_e, ratio)}


def decide(d_e: float, ratio: float) -> str:
    """Preregistration section 9, verbatim thresholds (-1.0 %, +1.0 %, 1.10)."""
    if d_e <= -1.0:
        return "IMPROVES" if ratio <= 1.10 else "TRADE-OFF"
    if d_e >= 1.0:
        return "WORSE"
    return "NO PRACTICAL DIFFERENCE"
