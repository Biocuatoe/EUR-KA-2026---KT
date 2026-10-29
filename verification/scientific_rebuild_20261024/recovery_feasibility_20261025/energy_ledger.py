"""Phase 1 energy ledger for the recovery-oriented feasibility study (read-only on R1 outputs).

Usage (activated env):  python energy_ledger.py
Reads  ../runs/R1_*/{metrics.csv,series.npz}  and  ../configs/R1.yaml  (never writes there).
Writes ./ledger_runs.csv, ./ledger_controller_spread.csv, ./ledger_reference.csv, ./ledger_ideal.csv.

Three kinds of numbers appear, labelled in the column names / file headers:
  MEAS  = accumulator integrated inside the R1 simulation (stored in y_end)
  DERIV = algebra on recorded states / accumulators (exact identities of the model)
  IDEAL = new computation from the plant equations on the reference trajectory (not an R1 output)
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
R1 = HERE.parent
REPO = R1.parents[1]
sys.path[:0] = [str(REPO / "src"), str(R1 / "src")]

from eureka.params import load_params  # noqa: E402
from eureka.plant import BatchParams  # noqa: E402
from rebuild.model import IX  # noqa: E402
from rebuild.run import CFG, load_cycle  # noqa: E402

J2WH = 1.0 / 3600.0
CYCLES = list(CFG["cycles"])


def ledger_rows() -> list[dict]:
    base = load_params()
    out = []
    for cyc in CYCLES:
        tag = f"R1_{cyc}"
        with (R1 / "runs" / tag / "metrics.csv").open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        z = np.load(R1 / "runs" / tag / "series.npz")
        y0, y1 = z["y0"], z["y_end"]
        assert len(rows) == y1.shape[0], (tag, len(rows), y1.shape)
        for j, r in enumerate(rows):
            p = base.with_overrides(k_r0=float(r["k_r0"]))
            bp = BatchParams.from_params([p], np.array([float(r["soh"])]))
            d = y1[j] - y0[j]
            g = lambda k: d[IX[k]] * J2WH  # noqa: E731
            ke = 0.5 * p.M_eff * (y1[j, IX["v"]] ** 2 - y0[j, IX["v"]] ** 2) * J2WH
            ec1 = 0.5 * p.C1 * (y1[j, IX["V1"]] ** 2 - y0[j, IX["V1"]] ** 2) * J2WH
            E = g("E_chem")
            led = {
                "run_id": r["run_id"], "cycle": cyc, "case": r["case"], "soh": float(r["soh"]),
                "controller": r["controller"], "tracking_failure": r["tracking_failure"],
                "shortfall_pct": float(r["shortfall_pct"]), "distance_km": float(r["distance_km"]),
                "rmse_ms": float(r["rmse_ms"]),
                "E_chem_Wh_MEAS": E, "E_pos_Wh_MEAS": g("E_pos"), "E_neg_Wh_MEAS": g("E_neg"),
                "E_rr_Wh_MEAS": g("E_rr"), "E_aero_Wh_MEAS": g("E_aero"), "E_fb_Wh_MEAS": g("E_fb"),
                "E_gear_Wh_MEAS": g("E_gear"), "E_visc_Wh_MEAS": g("E_visc"), "E_mi_Wh_MEAS": g("E_mi"),
                "E_R0_Wh_MEAS": g("E_R0"), "E_R1_Wh_MEAS": g("E_R1"),
                "regen_terminal_Wh_MEAS": float(r["regen_terminal_Wh"]),
                "dKE_eff_Wh_DERIV": ke, "dEC1_Wh_DERIV": ec1,
            }
            led["E_wheel_net_Wh_DERIV"] = ke + led["E_rr_Wh_MEAS"] + led["E_aero_Wh_MEAS"] + led["E_fb_Wh_MEAS"]
            # second route to the same quantity: shaft work minus gear loss
            led["E_wheel_net_check_Wh_DERIV"] = (
                E - ec1 - led["E_R0_Wh_MEAS"] - led["E_R1_Wh_MEAS"] - led["E_mi_Wh_MEAS"]
                - led["E_visc_Wh_MEAS"] - led["E_gear_Wh_MEAS"]
            )
            led["closure_Wh"] = led["E_wheel_net_Wh_DERIV"] - led["E_wheel_net_check_Wh_DERIV"]
            out.append(led)
    return out


def reference_demand(cyc: str, p, dt: float = 0.01) -> dict:
    """Wheel-level demand of the reference trajectory itself (no controller, no battery). IDEAL."""
    prof = load_cycle(cyc)
    t = np.arange(0.0, prof.duration + 1e-9, dt)
    v = prof.sample(t)
    vm = 0.5 * (v[1:] + v[:-1])
    a = np.diff(v) / dt
    s = np.tanh(vm / p.v_eps)
    f_rr = p.Crr * p.M * p.g * s
    f_aero = 0.5 * p.rho * p.Cd * p.A_f * vm**2
    f_w = p.M_eff * a + f_rr + f_aero
    pw = f_w * vm
    gr = p.G / p.r_w
    T_req = np.where(f_w >= 0, f_w / (gr * p.eta_g), f_w * p.eta_g / gr) + p.B_m * gr * vm
    w = gr * vm
    lim = np.minimum(p.T_max, p.P_max / np.maximum(w, 1e-6))
    over = np.abs(T_req) > lim + 1e-9
    return dict(
        cycle=cyc, dist_km=float(np.sum(vm) * dt / 1000), dur_s=prof.duration,
        wheel_pos_Wh=float(np.sum(np.maximum(pw, 0)) * dt * J2WH),
        wheel_neg_Wh=float(np.sum(np.minimum(pw, 0)) * dt * J2WH),
        wheel_net_Wh=float(np.sum(pw) * dt * J2WH),
        rr_Wh=float(np.sum(f_rr * vm) * dt * J2WH), aero_Wh=float(np.sum(f_aero * vm) * dt * J2WH),
        inertia_net_Wh=float(0.5 * p.M_eff * (v[-1] ** 2 - v[0] ** 2) * J2WH),
        max_T_req_Nm=float(np.max(T_req)), min_T_req_Nm=float(np.min(T_req)),
        max_P_mech_kW=float(np.max(T_req * w) / 1000), min_P_mech_kW=float(np.min(T_req * w) / 1000),
        frac_time_over_motor_limit=float(np.mean(over)),
        frac_steps_over_motor_limit=float(np.mean(over)),
    )


def ideal_run(cyc: str, k_r0: float, soh: float, dt: float = 0.01, stretch: float = 1.0) -> dict:
    """Battery-side energy if the reference is tracked exactly (inverse-dynamics torque). IDEAL.

    Not a lower bound on energy over admissible trajectories: it is the energy of the reference itself.
    Defined only where the motor limit is never exceeded.
    """
    p = load_params().with_overrides(k_r0=k_r0)
    bp = BatchParams.from_params([p], np.array([soh]))
    R0, R1, C1, Voc = float(bp.R0[0]), float(bp.R1[0]), p.C1, p.V_oc
    prof = load_cycle(cyc)
    # stretch > 1 slows the reference uniformly: v'(t) = v(t/stretch)/stretch (same distance, duration x stretch)
    t = np.arange(0.0, prof.duration * stretch + 1e-9, dt)
    v = prof.sample(np.minimum(t / stretch, prof.duration)) / stretch
    vm = 0.5 * (v[1:] + v[:-1])
    a = np.diff(v) / dt
    gr = p.G / p.r_w
    f_rr = p.Crr * p.M * p.g * np.tanh(vm / p.v_eps)
    f_aero = 0.5 * p.rho * p.Cd * p.A_f * vm**2
    f_w = p.M_eff * a + f_rr + f_aero
    w = gr * vm
    T =np.where(f_w >= 0, f_w / (gr * p.eta_g), f_w * p.eta_g / gr) + p.B_m * w
    lim = np.minimum(p.T_max, p.P_max / np.maximum(w, 1e-6))
    if np.any(np.abs(T) > lim + 1e-9):
        return dict(cycle=cyc, k_r0=k_r0, soh=soh, stretch=stretch, feasible=False)
    t_s = T - p.B_m * w
    pm = T * w
    pe = np.where(pm >= 0, pm / p.eta_mi, pm * p.eta_mi)
    tau = R1 * C1
    ex = np.exp(-dt / tau)
    V1 = 0.0
    E = ER0 = ER1 = 0.0
    for k in range(len(vm)):
        vo = Voc - V1
        i = (vo - np.sqrt(vo * vo - 4 * R0 * pe[k])) / (2 * R0)
        E += Voc * i * dt
        ER0 += R0 * i * i * dt
        V1n = V1 * ex + i * R1 * (1 - ex)
        ER1 += 0.5 * (V1 * V1 + V1n * V1n) / R1 * dt
        V1 = V1n
    gear = float(np.sum(t_s * w - f_w * vm) * dt)
    visc = float(np.sum(p.B_m * w * w) * dt)
    mi = float(np.sum(pe - pm) * dt)
    ke = 0.5 * p.M_eff * (v[-1] ** 2 - v[0] ** 2)
    ec1 = 0.5 * C1 * V1 * V1
    rr = float(np.sum(f_rr * vm) * dt)
    ae = float(np.sum(f_aero * vm) * dt)
    clo = E - (ke + ec1 + rr + ae + gear + visc + mi + ER0 + ER1)
    return dict(cycle=cyc, k_r0=k_r0, soh=soh, stretch=stretch, feasible=True, duration_s=float(len(vm) * dt),
                E_chem_Wh=E * J2WH, dist_km=float(np.sum(vm) * dt / 1000),
                Wh_per_km=E * J2WH / (float(np.sum(vm) * dt / 1000)),
                E_R0_Wh=ER0 * J2WH, E_R1_Wh=ER1 * J2WH, E_mi_Wh=mi * J2WH, E_gear_Wh=gear * J2WH,
                E_visc_Wh=visc * J2WH, closure_Wh=clo * J2WH)


def friction_floor(cyc: str, case: str, soh: float, dt: float = 0.01) -> float:
    """Friction-brake energy [Wh] that the charge/regen limit forces even under exact tracking. IDEAL.

    Uses V1 = 0 (V1 is O(1 V) against 48 V), the case's charge-current limit and the motor torque limit.
    Ignores torque lag and any discharge-side shortfall.
    """
    cs = CFG["cases"][case]
    lim = cs["limits"]
    p = load_params().with_overrides(k_r0=cs["k_r0"])
    R0 = p.R0_new * (1 + p.k_r0 * (1 - soh))
    prof = load_cycle(cyc)
    t = np.arange(0.0, prof.duration + 1e-9, dt)
    v = prof.sample(t)
    vm = 0.5 * (v[1:] + v[:-1])
    a = np.diff(v) / dt
    gr = p.G / p.r_w
    w = gr * vm
    f_req = p.M_eff * a + p.Crr * p.M * p.g * np.tanh(vm / p.v_eps) + 0.5 * p.rho * p.Cd * p.A_f * vm**2
    base = np.minimum(p.T_max, p.P_max / np.maximum(w, 1e-6))
    c_ch = lim.get("c_ch", np.inf)
    s = soh if lim.get("soh_scaled", False) else 1.0
    i_c = c_ch * p.Q_Ah * s
    if np.isfinite(i_c):
        i_c = min(i_c, (lim["v_max_ratio"] - 1.0) * p.V_oc / R0)
        p_c = (p.V_oc + R0 * i_c) * i_c
        t_neg = np.minimum(base, p_c / (p.eta_mi * np.maximum(w, 1e-6)))
    else:
        t_neg = base
    f_regen = gr * (t_neg + p.B_m * w) / p.eta_g  # largest braking force the motor path can supply at the wheel
    f_fb = np.maximum(0.0, -f_req - f_regen)
    return float(np.sum(f_fb * vm) * dt * J2WH)


def write_csv(path: Path, rows: list[dict]) -> None:
    keys: list[str] = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    led = ledger_rows()
    write_csv(HERE / "ledger_runs.csv", led)
    print("ledger rows:", len(led), " max |closure| Wh:", max(abs(r["closure_Wh"]) for r in led))

    # controller spread: for each (cycle, case, soh) the max-min of every ledger line over F, S, F01
    comp = [k for k in led[0] if k.endswith(("_MEAS", "_DERIV")) and not k.endswith("check_Wh_DERIV")]
    groups: dict[tuple, list[dict]] = {}
    for r in led:
        groups.setdefault((r["cycle"], r["case"], r["soh"]), []).append(r)
    spread = []
    for (cyc, case, soh), rs in groups.items():
        row = {"cycle": cyc, "case": case, "soh": soh, "E_chem_F_Wh": next(r for r in rs if r["controller"] == "F")["E_chem_Wh_MEAS"]}
        for k in comp:
            vals = [r[k] for r in rs]
            row[k.replace("_Wh_", "_range_Wh_")] = max(vals) - min(vals)
        row["rmse_range_ms"] = max(r["rmse_ms"] for r in rs) - min(r["rmse_ms"] for r in rs)
        row["shortfall_range_pp"] = max(r["shortfall_pct"] for r in rs) - min(r["shortfall_pct"] for r in rs)
        spread.append(row)
    write_csv(HERE / "ledger_controller_spread.csv", spread)

    base = load_params()
    ref = [reference_demand(c, base) for c in CYCLES]
    write_csv(HERE / "ledger_reference.csv", ref)
    for r in ref:
        print("REF", {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})

    ideal = []
    for cyc in CYCLES:
        for k_r0 in (0.5, 2.0):
            for soh in (1.0, 0.9, 0.8, 0.7):
                ideal.append(ideal_run(cyc, k_r0, soh))
    for cyc in ("S1", "S2", "UDDS"):
        for st in (1.02, 1.05, 1.10):
            for soh in (1.0, 0.7):
                ideal.append(ideal_run(cyc, 0.5, soh, stretch=st))
    write_csv(HERE / "ledger_ideal.csv", ideal)
    ff = []
    for cyc in CYCLES:
        for case in ("B0", "BCN", "BCS", "BCS2"):
            for soh in (1.0, 0.9, 0.8, 0.7):
                meas = next(r["E_fb_Wh_MEAS"] for r in led if (r["cycle"], r["case"], r["soh"], r["controller"]) == (cyc, case, soh, "F"))
                ff.append(dict(cycle=cyc, case=case, soh=soh, floor_fb_Wh=friction_floor(cyc, case, soh), measured_fb_F_Wh=meas))
    write_csv(HERE / "ledger_friction_floor.csv", ff)
    for r in ff:
        if r["soh"] in (1.0, 0.7):
            print("FFLOOR", r["cycle"], r["case"], r["soh"], round(r["floor_fb_Wh"], 2), "measured F", round(r["measured_fb_F_Wh"], 2))
    for r in ideal:
        if r["feasible"] and r["soh"] in (1.0, 0.7) and r["stretch"] == 1.0:
            print("IDEAL", r["cycle"], r["k_r0"], r["soh"], round(r["Wh_per_km"], 4), "closure", f'{r["closure_Wh"]:.2e}')
        elif r["feasible"] and r["stretch"] > 1.0 and r["soh"] == 1.0:
            print("STRETCH", r["cycle"], r["stretch"], round(r["Wh_per_km"], 4), round(r["duration_s"], 1))
        elif not r["feasible"] and r["soh"] == 1.0:
            print("IDEAL infeasible (exceeds motor limit):", r["cycle"], r["k_r0"])


if __name__ == "__main__":
    main()
