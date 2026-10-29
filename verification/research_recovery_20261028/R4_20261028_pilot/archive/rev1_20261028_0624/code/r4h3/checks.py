"""Campaign-level checks of protocol v1 section 9 and the pair classification of 8.1/8.2 with decisions D2/D5.

Every function here is a pure rule on numbers or flags already produced elsewhere; none runs a plant.
Thresholds are the frozen ones (protocol 9) and are not parameters:
    QS vs dynamic        M0, M1: |e_dyn - e_QS| / e_QS <= 1 % (per reference km); M2 reported only
    planner grid         |S_found(1 m, 0.05) - S_found(2 m, 0.1)| < 0.2 pp
    planner optimality   S_max - S_found reported; > 0.2 pp makes the gap the stated resolution
    dynamic time step    |dE_rel(0.5 ms) - dE_rel(1 ms)| < 0.01 pp
A paired energy difference is produced only by paired_delta(), and only for a pair classified COMPARABLE.
"""

from __future__ import annotations

import numpy as np

from r4h3 import config

QS_DYN_MAX_PCT = 1.0
GRID_MAX_PP = 0.2
OPTIMALITY_PP = 0.2
TIMESTEP_MAX_PP = 0.01
QS_DYN_DECISIVE = {k: s.qs_usable for k, s in config.SCENARIOS.items()}   # protocol 2.3 and 9: M2 reported only
# Open item AMB-24 (review CR-A2): what "infeasible on P3" means in D5. Neither reading is chosen here.
P3_RULES = ("qs_step_feasibility_on_P3",   # a profile piece fails QSPlant.step on the P3 plant (protocol 5.2 notion)
            "dynamic_8_2_only")            # only the dynamic run's protocol 8.2 flags decide; QS flags reported


# --------------------------------------------------------------------------- QS energy of a profile
def qs_energy(plant, t, v) -> dict:
    """Quasi-static totals of a piecewise-linear profile (constant acceleration between knots), the same
    QSPlant.step the planner uses. For knots on a uniform grid this equals r3_lib.evaluate()."""
    t, v = np.asarray(t, float), np.asarray(v, float)
    E, Fb, Ah, I2, s, ok = plant.step(v[:-1], v[1:], np.diff(t))
    return {"E_J": float(E.sum()), "fric_J": float(Fb.sum()), "dist_m": float(s.sum()), "feasible": bool(ok.all()),
            "n_infeasible_pieces": int((~ok).sum())}


def qs_vs_dynamic(motor: str, E_qs_J: float, E_dyn_Wh: float, d_ref_m: float) -> dict:
    """Protocol 9 'QS vs dynamic' for one run: both energies per reference km, R3's definition
    100 (e_dyn - e_QS) / e_QS."""
    e_qs = E_qs_J / 3600.0 / (d_ref_m / 1000.0)
    e_dyn = E_dyn_Wh / (d_ref_m / 1000.0)
    if not e_qs > 0:
        return dict(motor=motor, e_qs_Wh_per_km=e_qs, e_dyn_Wh_per_km=e_dyn, diff_pct=float("nan"), decisive=False,
                    status="undefined (QS energy <= 0)")
    diff = 100.0 * (e_dyn - e_qs) / e_qs
    decisive = QS_DYN_DECISIVE[motor]
    if not decisive:
        status = "reported only (M2)"
    else:
        status = "pass" if abs(diff) <= QS_DYN_MAX_PCT else "FAIL (branch INCONCLUSIVE, protocol 9)"
    return dict(motor=motor, e_qs_Wh_per_km=e_qs, e_dyn_Wh_per_km=e_dyn, diff_pct=diff, decisive=decisive, status=status)


# --------------------------------------------------------------------------- planner checks
def scenario_totals(E_b_J: float, E_seco_J: float, LB_total_J: float) -> dict:
    """Protocol 5.4: S_found = 1 - E_Seco/E(v_b), S_max = 1 - sum LB_k / E(v_b), both on the QS plant (in %)."""
    s_found = 100.0 * (1.0 - E_seco_J / E_b_J)
    s_max = 100.0 * (1.0 - LB_total_J / E_b_J)
    gap = s_max - s_found
    return dict(S_found_pct=s_found, S_max_pct=s_max, optimality_gap_pp=gap,
                stated_resolution_pp=gap if gap > OPTIMALITY_PP else None)


def grid_convergence(E_b_J: float, E_seco_coarse_J: float, E_seco_fine_J: float) -> dict:
    """Protocol 9 planner grid convergence: (2 m, 0.1 m/s) vs (1 m, 0.05 m/s)."""
    d = abs(100.0 * (E_seco_coarse_J - E_seco_fine_J) / E_b_J)
    return dict(dS_found_pp=d, passed=d < GRID_MAX_PP, stated_resolution_pp=None if d < GRID_MAX_PP else d)


def timestep_check(dE_rel_1ms_pct: float, dE_rel_05ms_pct: float) -> dict:
    """Protocol 9 dynamic time step: the paired dE_rel may change by < 0.01 pp between 1 ms and 0.5 ms."""
    d = abs(dE_rel_05ms_pct - dE_rel_1ms_pct)
    return dict(change_pp=d, passed=d < TIMESTEP_MAX_PP, stated_resolution_pp=None if d < TIMESTEP_MAX_PP else d)


# --------------------------------------------------------------------------- pair classification
COMPARABLE = "COMPARABLE"
STATUSES = (
    "PROFILE_UNAVAILABLE",         # S-eco time-infeasible or rejected by the validator on the design plant (D1, D3)
    "BASELINE_UNAVAILABLE",        # no baseline task v_b
    "ERROR",                       # an attempted run raised; traceback in errors.csv
    "BASELINE_INFEASIBLE_ON_P3",   # D5: v_b not QS-feasible on the evaluated P3 plant -> non-comparable
    "ECO_INFEASIBLE_ON_P3",        # D5: the P1-designed profile not QS-feasible on the evaluated P3 plant
    "B0_INVALID_EXCLUDED",         # protocol 8.1: B0 fails 8.2 -> condition excluded and reported
    "INVALID_COMPARISON",          # protocol 8.1: B3 fails 8.2
    "RECOMPUTATION_DISAGREEMENT",  # protocol 9: not credited until resolved by amendment
    COMPARABLE,
)


def arm_comparable(ev_row: dict) -> bool:
    """Protocol 8.2 from the independent evaluator's flags and the simulator validity (never a planner flag)."""
    return bool(ev_row["sim_valid"] and ev_row["complete"] and ev_row["tracking_ok"] and ev_row["stop_ok"]
                and ev_row["constraint_ok"] and ev_row["finite_ok"])


def classify_pair(b0: dict | None, b3: dict | None, *, eco_profile_ok: bool, baseline_ok: bool,
                  pstate: str, b0_qs_feasible: bool | None = None, b3_qs_feasible: bool | None = None,
                  p3_rule: str | None = None) -> str:
    """Status of one (cycle, motor, limits, plant state[, draw]) condition, in this order:
    profile/baseline availability, errors, P3 feasibility (D5, under the issued p3_rule), B0 validity, B3 validity,
    recomputation. b0/b3: evaluation rows (None if the run was not executed); a row with key 'error' records an
    exception. Both arms are always run when their profile exists, so every rule sees the same record."""
    if not eco_profile_ok:
        return "PROFILE_UNAVAILABLE"
    if not baseline_ok:
        return "BASELINE_UNAVAILABLE"
    if b0 is None or b3 is None or b0.get("error") or b3.get("error"):
        return "ERROR"
    if pstate == "P3":
        if p3_rule not in P3_RULES:
            raise ValueError(f"AMB-24 open: P3 feasibility rule {p3_rule!r} not one of {P3_RULES}")
        if b0_qs_feasible is None or b3_qs_feasible is None:
            raise ValueError("P3 classification needs the QS feasibility of both profiles on the P3 plant")
        if p3_rule == "qs_step_feasibility_on_P3":
            if not b0_qs_feasible:
                return "BASELINE_INFEASIBLE_ON_P3"
            if not b3_qs_feasible:
                return "ECO_INFEASIBLE_ON_P3"
    if not arm_comparable(b0):
        return "B0_INVALID_EXCLUDED"
    if not arm_comparable(b3):
        return "INVALID_COMPARISON"
    if not (b0["recompute_protocol_ok"] and b3["recompute_protocol_ok"]):
        return "RECOMPUTATION_DISAGREEMENT"
    return COMPARABLE


def paired_delta(status: str, b0: dict, b3: dict) -> dict:
    """Protocol 7.1: dE_abs and dE_rel per reference km, always together; refused unless COMPARABLE."""
    if status != COMPARABLE:
        raise ValueError(f"refusing a paired energy difference for a {status} condition (protocol 8.1, D5)")
    e0, e3 = b0["Wh_per_ref_km"], b3["Wh_per_ref_km"]
    return dict(dE_abs_Wh_per_km=e3 - e0, dE_rel_pct=100.0 * (e3 - e0) / e0,
                trip_time_B0_s=b0["trip_time_s"], trip_time_B3_s=b3["trip_time_s"])


def denominator(statuses: list[str]) -> dict:
    """Counts of every status (failures stay in the denominator, D5)."""
    out = {s: 0 for s in STATUSES}
    for s in statuses:
        if s not in out:
            raise ValueError(f"unknown status {s!r}")
        out[s] += 1
    out["total"] = len(statuses)
    return out
