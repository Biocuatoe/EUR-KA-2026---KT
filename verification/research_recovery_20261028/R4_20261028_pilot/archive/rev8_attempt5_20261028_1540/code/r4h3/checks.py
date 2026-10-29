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
# AMB-24, decided by the owner on 2026-10-28: formal feasibility on P3 is decided by the dynamic run's frozen
# protocol 8.2 checks. The quasi-static step check on the evaluated plant is a diagnostic screen: its failures are
# recorded exactly (qs_energy()['infeasible_pieces']) and never by themselves make a branch "infeasible".
P3_RULE = "dynamic_8_2_decides; QS screen diagnostic only"


# --------------------------------------------------------------------------- QS energy of a profile
def qs_energy(plant, t, v) -> dict:
    """Quasi-static totals of a piecewise-linear profile (constant acceleration between knots), the same
    QSPlant.step the planner uses. For knots on a uniform grid this equals r3_lib.evaluate()."""
    t, v = np.asarray(t, float), np.asarray(v, float)
    E, Fb, Ah, I2, s, ok = plant.step(v[:-1], v[1:], np.diff(t))
    bad = np.flatnonzero(~ok)
    return {"E_J": float(E.sum()), "fric_J": float(Fb.sum()), "dist_m": float(s.sum()), "feasible": bool(ok.all()),
            "n_infeasible_pieces": int(bad.size),
            "infeasible_pieces": [dict(piece=int(k), t0_s=float(t[k]), t1_s=float(t[k + 1]), v0_ms=float(v[k]),
                                       v1_ms=float(v[k + 1])) for k in bad]}


# N-A2 (owner ruling 2026-10-28; 03_protocol_v1_amendment_2_DRAFT.md): the protocol 9 QS-vs-dynamic check applies to
# an evaluation pair only if BOTH the B0 and the B3 profile pass the QS feasibility screen (QSPlant.step) on the
# condition's evaluated plant. Otherwise the pair's check is NOT_APPLICABLE_QS_INFEASIBLE: neither a pass nor a
# failure, and QS energy computed from torque beyond the QS model's admissible limits is never used for acceptance.
# Label rule: NOT_APPLICABLE_* never changes a branch outcome; NOT_EVALUABLE_* makes an M0/M1 branch INCONCLUSIVE.
QS_NA_INFEASIBLE = "NOT_APPLICABLE_QS_INFEASIBLE"
QS_NA_PROFILE = "NOT_APPLICABLE_PROFILE_UNAVAILABLE"    # AMB-29(a): a profile does not exist, so no pair to screen
QS_NOT_EVALUABLE = "NOT_EVALUABLE_RUN_MISSING"          # AMB-29(b): eligible pair, an arm has no finite energy
QS_UNDEFINED = "NOT_EVALUABLE_QS_UNDEFINED"             # AMB-29(c): eligible pair, QS energy <= 0 (ratio undefined)
QS_CONDITION_ERROR = "NOT_EVALUABLE_CONDITION_ERROR"    # AMB-29(d): exception before or during the pair evaluation
QS_RUN_INVALID = "NOT_EVALUABLE_RUN_INVALID"            # AMB-31 ruling: eligible pair, an arm fails 8.2 or recomputation
PAIR_QS_STATUSES = ("PASS", "FAIL", "REPORTED_ONLY", QS_NA_INFEASIBLE, QS_NA_PROFILE, QS_NOT_EVALUABLE, QS_UNDEFINED,
                    QS_CONDITION_ERROR, QS_RUN_INVALID)
_NOT_APPLICABLE = (QS_NA_INFEASIBLE, QS_NA_PROFILE)
_NOT_EVALUABLE = (QS_NOT_EVALUABLE, QS_UNDEFINED, QS_CONDITION_ERROR, QS_RUN_INVALID)
# Status vocabulary of the pair check (amendment 2 candidate rev5 section 2). The owner's term
# QS_COMPARISON_NOT_EVALUABLE (AMB-29(c) ruling) is the NOT_EVALUABLE class; QS energy <= 0 is NOT_EVALUABLE_QS_UNDEFINED.
PAIR_STATUS_CLASSES = {"PASS": ("PASS",), "FAIL": ("FAIL",), "REPORTED_ONLY": ("REPORTED_ONLY",),
                       "NOT_APPLICABLE": _NOT_APPLICABLE, "NOT_EVALUABLE": _NOT_EVALUABLE}
# AMB-29(a) owner ruling (2026-10-28): QS_NA_PROFILE is the label of the pair's QS-vs-dynamic CHECK only (its
# applicability condition, both profiles passing the QS screen, is objectively unmet). The condition itself keeps its
# explicit PROFILE_UNAVAILABLE / BASELINE_UNAVAILABLE status in every planned-run, feasibility and verdict denominator
# (feasibility_accounting, h3_verdict_eligibility) and never yields a paired comparison (classify_pair, paired_delta).
# AMB-31 owner ruling (2026-10-28): energy of a run failing protocol 8.2 (or not confirmed by the recomputation) is
# diagnostic only: never confirmatory, never credited to the paired endpoint (energy_role), never used by the QS check.
# AMB-29(b)-(d) owner rulings (2026-10-28): every NOT_EVALUABLE_* pair makes the M0/M1 branch INCONCLUSIVE for this
# criterion and never disappears from a denominator. (c): no percentage with a denominator <= 0 (non_positive_term).
# (d): an exception is recorded with its traceback and run IDs and is never retried or replaced by another run.
# AMB-30 owner ruling (2026-10-28): the M0/M1 branch can PASS only with a PASS on the held-out nominal S2 set (NOM),
# every required nominal cell present with evidence, and no FAIL or NOT_EVALUABLE pair in any preregistered set.
# AMB-32 owner ruling (2026-10-28): a nominal cell without a comparable pair makes the H3 verdict INCONCLUSIVE.
NOMINAL_SET = "NOM"                                  # protocol 8.1: the held-out nominal S2 P1 set
NOMINAL_LIMITS = ("L-R1", "L-EVE")
NOT_IN_RECORD, DUPLICATE_IN_RECORD = "NOT_IN_RECORD", "DUPLICATE_IN_RECORD"


def non_positive_term(name: str, value, *parts) -> str | None:
    """AMB-29(c) ruling: the exact denominator that makes a relative percentage undefined (<= 0 or not finite), with
    its value and the raw terms it is built from; None if the denominator is usable."""
    if value is not None and np.isfinite(value) and value > 0:
        return None
    return f"{name} = {value!r} is not > 0" + (f" ({'; '.join(parts)})" if parts else "")


def qs_piece_diagnosis(plant, v0: float, v1: float, h: float) -> dict:
    """Which sub-check of QSPlant.step fails for one constant-acceleration piece, at which Gauss node and by how much
    (diagnostic only; review R3-5). Re-evaluates the three conditions of r3_lib QSPlant.point at the step's nodes:
    drive torque T <= t_pos + 1e-9, battery discriminant >= 0, discharge current i <= i_d + 1e-6. `consistent` says
    whether their conjunction reproduces QSPlant.step's verdict for the piece."""
    from rebuild.model import battery_limits
    L = config.L
    bp, lim, mm = plant.bp, plant.lim, plant.mm
    R0, Voc = float(bp.R0[0]), float(bp.V_oc[0])
    gr = float(bp.G[0] / bp.r_w[0])
    M, Meff, g, eta_g, Bm = float(bp.M[0]), float(bp.M_eff[0]), float(bp.g[0]), float(bp.eta_g[0]), float(bp.B_m[0])
    a = (v1 - v0) / h
    nodes = []
    for x in L.GL_X:
        v = max(v0 + a * x * h, 0.0)
        w = gr * v
        f_req = Meff * a + float(bp.Crr[0]) * M * g * np.tanh(v / float(bp.v_eps[0])) \
            + 0.5 * float(bp.rho[0] * bp.Cd[0] * bp.A_f[0]) * v * v
        t_s = f_req / (gr * eta_g) if f_req >= 0 else f_req * eta_g / gr
        T = t_s + Bm * w
        tp, tn, _ = L.torque_limits(np.array([w]), np.zeros(1), L._broadcast(bp, np.array([w])), lim, mm)
        tp, tn = float(tp[0]), float(tn[0])
        T_m = max(T, -tn)
        p_m = T_m * w
        p_e = p_m + float(mm.loss(np.array([p_m]), np.array([T_m]))[0])
        disc = Voc * Voc - 4.0 * R0 * p_e
        i = (Voc - np.sqrt(max(disc, 0.0))) / (2.0 * R0)
        i_d = float(battery_limits(np.zeros(1), bp, lim)[0][0]) if lim.active else float("inf")
        nodes.append(dict(node=float(x), v_ms=v, T_req_Nm=T, t_pos_Nm=tp, drive_torque_ok=bool(T <= tp + 1e-9),
                          discriminant=disc, battery_discriminant_ok=bool(disc >= 0), i_A=float(i), i_d_A=i_d,
                          discharge_current_ok=bool(i <= i_d + 1e-6)))
    names = ("drive_torque", "battery_discriminant", "discharge_current")
    failed = [n for n in names if not all(d[f"{n}_ok"] for d in nodes)]
    step_ok = bool(plant.step(np.array([v0]), np.array([v1]), np.array([h]))[-1][0])
    return dict(failed_checks=failed, consistent=(not failed) == step_ok, nodes=nodes)


def qs_screen(plant, t, v) -> dict:
    """The N-A2 QS feasibility screen of one profile: qs_energy() plus, for every failing piece, the failed
    sub-check(s) (qs_piece_diagnosis)."""
    r = qs_energy(plant, t, v)
    for p in r["infeasible_pieces"]:
        try:                     # a diagnosis failure must never stop or change a run; it is recorded
            d = qs_piece_diagnosis(plant, p["v0_ms"], p["v1_ms"], p["t1_s"] - p["t0_s"])
            p.update(failed_checks=d["failed_checks"], diagnosis_consistent=d["consistent"], nodes=d["nodes"])
        except Exception as e:  # noqa: BLE001
            p.update(failed_checks=[f"diagnosis error: {e!r}"], diagnosis_consistent=False, nodes=[])
    return r


def pair_qs_dynamic(motor: str, screen: dict, arm_checks: dict, invalid_arms=()) -> dict:
    """Pair-level QS-vs-dynamic status (N-A2). screen: {branch: True/False QS-screen result, or None if the profile
    does not exist}. arm_checks: {branch: qs_vs_dynamic() result} for the arms whose dynamic energy may be used, i.e.
    finite AND from a run passing protocol 8.2 and its in-process recomputation (AMB-31 ruling); only consulted for an
    eligible pair. invalid_arms: arms with a finite energy from a run failing 8.2 or its recomputation (diagnostic only,
    never used here). Thresholds are the frozen protocol 9 ones (qs_vs_dynamic). An applicable FAIL of a valid arm is
    reported as FAIL even when the other arm cannot be evaluated (review R3-2). 'fail_arms' names the arms whose valid
    energy failed."""
    arms = ("B0", "B3")
    failed = [b for b in arms if screen.get(b) is False]
    missing = [b for b in arms if screen.get(b) is None]
    if failed:
        return dict(pair_status=QS_NA_INFEASIBLE, qs_eligible=False, ineligible_arms=",".join(failed), fail_arms="",
                    reason="QS feasibility screen failed for " + ", ".join(failed)
                           + (f"; profile unavailable for {', '.join(missing)}" if missing else ""))
    if missing:
        return dict(pair_status=QS_NA_PROFILE, qs_eligible=False, ineligible_arms="", fail_arms="",
                    reason="profile unavailable for " + ", ".join(missing) + " (check not applicable; the condition "
                           "keeps its explicit profile-failure status, AMB-29(a) ruling)")
    avail = {b: arm_checks[b] for b in arms if arm_checks.get(b) is not None}
    invalid = [b for b in arms if b in invalid_arms and b not in avail]
    no_energy = [b for b in arms if b not in avail and b not in invalid]
    tail = (f"; no usable dynamic energy for {', '.join(no_energy)}" if no_energy else "") \
        + (f"; energy of {', '.join(invalid)} is diagnostic only (run fails protocol 8.2 or its recomputation)"
           if invalid else "")
    if not QS_DYN_DECISIVE[motor]:
        if no_energy or invalid:  # review R3-12, AMB-31 ruling: nothing valid to report; M2 stays REPORTED_ONLY
            return dict(pair_status=QS_NOT_EVALUABLE if no_energy else QS_RUN_INVALID, qs_eligible=True,
                        ineligible_arms="", fail_arms="", reason="M2 (reported only): eligible pair" + tail)
        undefined = [b for b, c in avail.items() if c["status"].startswith("undefined")]
        if undefined:            # review R3-15: same labels as M0/M1; the M2 branch outcome stays REPORTED_ONLY
            return dict(pair_status=QS_UNDEFINED, qs_eligible=True, ineligible_arms="", fail_arms="",
                        reason="M2 (reported only): check undefined (QS energy <= 0) for " + "; ".join(
                            f"{b}: {avail[b].get('non_positive_term') or 'QS energy <= 0'}" for b in undefined))
        return dict(pair_status="REPORTED_ONLY", qs_eligible=True, ineligible_arms="", fail_arms="",
                    reason="M2: reported only")
    fails = [b for b, c in avail.items() if c["status"].startswith("FAIL")]
    if fails:
        return dict(pair_status="FAIL", qs_eligible=True, ineligible_arms="", fail_arms=",".join(fails),
                    reason="applicable check failed for " + ", ".join(fails) + tail)
    if no_energy:
        return dict(pair_status=QS_NOT_EVALUABLE, qs_eligible=True, ineligible_arms="", fail_arms="",
                    reason="eligible pair without a usable dynamic energy" + tail)
    if invalid:
        return dict(pair_status=QS_RUN_INVALID, qs_eligible=True, ineligible_arms="", fail_arms="",
                    reason="eligible pair" + tail + " (AMB-31 ruling)")
    undefined = [b for b, c in avail.items() if c["status"] != "pass"]
    if undefined:                # AMB-29(c) ruling: the exact non-positive term is named; no percentage is computed
        return dict(pair_status=QS_UNDEFINED, qs_eligible=True, ineligible_arms="", fail_arms="",
                    reason="check undefined (QS energy <= 0) for " + "; ".join(
                        f"{b}: {avail[b].get('non_positive_term') or 'QS energy <= 0'}" for b in undefined))
    return dict(pair_status="PASS", qs_eligible=True, ineligible_arms="", fail_arms="",
                reason="both protocol-8.2-valid arms within the threshold")


def _by_set(rows, statuses) -> str:
    """'SET:count' for the rows whose pair status is in statuses, per preregistered set (never averaged)."""
    c = {}
    for r in rows:
        if r.get("qs_vs_dyn_pair_status") in statuses:
            c[r["set"]] = c.get(r["set"], 0) + 1
    return ",".join(f"{k}:{v}" for k, v in sorted(c.items()))


def branch_qs_dynamic_outcome(motor: str, cond_rows, planned_condition_ids=None) -> dict:
    """Protocol 9 QS-vs-dynamic consequence for one motor branch (N-A2; owner rulings AMB-29(b)-(d), AMB-30).
    M2 is reported only. M0/M1 are INCONCLUSIVE, with every reason recorded, if any of these holds:
    - an applicable check FAILs in any preregistered set (NOM, P3, INS, CNV, SEN), counted per set, never averaged;
    - a pair in any set is NOT_EVALUABLE_* (AMB-29(b)-(d));
    - a required nominal cell (NOM, L-R1 and L-EVE) is absent from the record, duplicated, without a profile or not
      evaluable (any status but PASS, FAIL or NOT_APPLICABLE_QS_INFEASIBLE): the mandatory held-out evidence is
      missing (AMB-30 items 5-6);
    - a pair is REPORTED_ONLY, a label for M2 only (inconsistent for M0/M1);
    - no nominal NOM pair PASSes: a PASS in any other set, the in-sample S1 set INS included, cannot substitute (AMB-30
      items 1-2; never a pass by vacuity);
    - planned_condition_ids is given and a planned pair of this motor is missing from the record.
    A NOT_APPLICABLE_QS_INFEASIBLE pair (N-A2) is neither pass nor fail and is not missing evidence. Thresholds are the
    frozen ones. An unknown status raises."""
    rows = [r for r in cond_rows if r["motor"] == motor]
    unknown = sorted({str(r.get("qs_vs_dyn_pair_status")) for r in rows} - set(PAIR_QS_STATUSES))
    if unknown:
        raise ValueError(f"unknown QS-vs-dynamic pair status {unknown}")
    n = {s: sum(1 for r in rows if r.get("qs_vs_dyn_pair_status") == s) for s in PAIR_QS_STATUSES}
    nominal = {}
    for lim in NOMINAL_LIMITS:
        st = [r.get("qs_vs_dyn_pair_status") for r in rows if r["set"] == NOMINAL_SET and r.get("limits") == lim]
        nominal[f"{motor}/{lim}"] = st[0] if len(st) == 1 else NOT_IN_RECORD if not st else DUPLICATE_IN_RECORD
    # a nominal cell lacks evidence unless it PASSes, FAILs (counted as a failure) or is QS-infeasible (N-A2); this
    # includes absent, duplicated, profile-unavailable and NOT_EVALUABLE_* cells, and REPORTED_ONLY for M0/M1
    lacking = {k: s for k, s in nominal.items() if s not in ("PASS", "FAIL", QS_NA_INFEASIBLE)}
    n_nom_pass = sum(1 for s in nominal.values() if s == "PASS")              # only the two required nominal cells
    missing_rows = sorted(set(planned_condition_ids) - {r.get("condition_id") for r in rows}) \
        if planned_condition_ids is not None else []
    out = dict(motor=motor, planned_pairs=len(rows), **{f"n_{k}": v for k, v in n.items()},
               n_PASS_dynamic_valid=sum(1 for r in rows if r.get("qs_vs_dyn_pair_status") == "PASS"
                                        and r.get("dynamic_valid_pair") is True),
               required_pass_set=NOMINAL_SET, n_PASS_nominal=n_nom_pass, n_PASS_other_sets=n["PASS"] - n_nom_pass,
               **{f"nominal_{lim}": nominal[f"{motor}/{lim}"] for lim in NOMINAL_LIMITS},
               nominal_evidence_missing=",".join(f"{k}={s}" for k, s in lacking.items()),
               fail_by_set=_by_set(rows, ("FAIL",)), not_evaluable_by_set=_by_set(rows, _NOT_EVALUABLE),
               pass_by_set=_by_set(rows, ("PASS",)), not_applicable_by_set=_by_set(rows, _NOT_APPLICABLE),
               planned_pairs_missing_from_record=",".join(missing_rows))
    if not QS_DYN_DECISIVE[motor]:
        return dict(out, outcome="REPORTED_ONLY", reason="M2 is reported only (protocol 2.3, 9)")
    reasons = []
    if missing_rows:
        reasons.append(f"{len(missing_rows)} planned pair(s) missing from the record")
    if n["REPORTED_ONLY"]:
        reasons.append(f"{n['REPORTED_ONLY']} pair(s) labelled REPORTED_ONLY, which applies to M2 only (inconsistent)")
    if n["FAIL"]:
        reasons.append(f"{n['FAIL']} applicable QS-vs-dynamic check(s) failed ({out['fail_by_set']}); a failure in any "
                       "preregistered set counts (AMB-30)")
    ne = sum(n[s] for s in _NOT_EVALUABLE)
    if ne:
        reasons.append(f"{ne} eligible or unknown-eligibility comparison(s) could not be evaluated "
                       f"({out['not_evaluable_by_set']}; AMB-29(b)-(d))")
    if lacking:
        reasons.append("mandatory held-out nominal evidence missing or not evaluable: "
                       + ", ".join(f"{k} {s}" for k, s in lacking.items()) + " (AMB-30)")
    if not n_nom_pass:
        reasons.append(f"no PASS on the held-out nominal set {NOMINAL_SET} (never a pass by vacuity)"
                       + (f"; {out['n_PASS_other_sets']} PASS in other sets ({out['pass_by_set']}) cannot substitute "
                          "(AMB-30)" if out["n_PASS_other_sets"] else ""))
    if reasons:
        return dict(out, outcome="INCONCLUSIVE", reason="; ".join(reasons))
    return dict(out, outcome="PASS", reason=f"all {n['PASS']} applicable checks pass, {n_nom_pass} of them on the held-out "
                                            f"nominal set {NOMINAL_SET} ({out['n_PASS_dynamic_valid']} on dynamic-valid "
                                            f"pairs, AMB-31); {n[QS_NA_INFEASIBLE]} not applicable (QS-infeasible), "
                                            f"{n[QS_NA_PROFILE]} without a profile outside the nominal cells")


def qs_dynamic_accounting(cond_rows) -> list[dict]:
    """Every denominator the N-A2 ruling requires, per motor and set and per motor overall. Eligibility classes add
    up to the planned pairs: qs_eligible + qs_ineligible + profile_unavailable + eligibility_unknown = planned."""
    groups = {}
    for r in cond_rows:
        for key in ((r["motor"], r["set"]), (r["motor"], "ALL")):
            groups.setdefault(key, []).append(r)
    out = []
    for (motor, set_), rows in sorted(groups.items()):
        st = [r.get("qs_vs_dyn_pair_status") for r in rows]
        ia = [r.get("qs_ineligible_arms", "") for r in rows]
        out.append(dict(
            motor=motor, set=set_, planned_pairs=len(rows),
            qs_eligible_pairs=sum(1 for r in rows if r.get("qs_eligible_pair") is True),
            qs_ineligible_pairs=st.count(QS_NA_INFEASIBLE),
            qs_ineligible_b0_only=ia.count("B0"), qs_ineligible_b3_only=ia.count("B3"), qs_ineligible_both=ia.count("B0,B3"),
            not_applicable_profile_unavailable=st.count(QS_NA_PROFILE),
            qs_eligibility_unknown=sum(1 for r in rows if r.get("qs_eligible_pair") is None),
            not_evaluable_run_missing=st.count(QS_NOT_EVALUABLE), not_evaluable_qs_undefined=st.count(QS_UNDEFINED),
            not_evaluable_condition_error=st.count(QS_CONDITION_ERROR), not_evaluable_run_invalid=st.count(QS_RUN_INVALID),
            qs_check_pass=st.count("PASS"), qs_check_fail=st.count("FAIL"), qs_check_reported_only=st.count("REPORTED_ONLY"),
            qs_check_pass_dynamic_valid=sum(1 for r in rows if r.get("qs_vs_dyn_pair_status") == "PASS"
                                            and r.get("dynamic_valid_pair") is True),
            dynamic_valid_pairs=sum(1 for r in rows if r.get("dynamic_valid_pair") is True),
            valid_energy_comparison_pairs=sum(1 for r in rows if r.get("status") == COMPARABLE)))
    return out


def qs_vs_dynamic(motor: str, E_qs_J: float, E_dyn_Wh: float, d_ref_m: float) -> dict:
    """Protocol 9 'QS vs dynamic' for one run: both energies per reference km, R3's definition
    100 (e_dyn - e_QS) / e_QS. AMB-29(c) ruling: if e_QS <= 0 (or d_ref <= 0) no percentage is computed (diff_pct None),
    the raw values are returned and non_positive_term names the exact term; no substitute criterion is used."""
    raw = dict(motor=motor, E_qs_J=E_qs_J, E_dyn_Wh=E_dyn_Wh, d_ref_m=d_ref_m)
    bad_d = non_positive_term("d_ref_m", d_ref_m)
    if bad_d:
        return dict(raw, e_qs_Wh_per_km=None, e_dyn_Wh_per_km=None, diff_pct=None, decisive=False,
                    status="undefined (QS energy <= 0)", non_positive_term=bad_d)
    e_qs = E_qs_J / 3600.0 / (d_ref_m / 1000.0)
    e_dyn = E_dyn_Wh / (d_ref_m / 1000.0)
    bad = non_positive_term("e_QS (Wh per reference km, the ratio's denominator)", e_qs,
                            f"E_QS = {E_qs_J!r} J", f"d_ref = {d_ref_m!r} m")
    if bad:
        return dict(raw, e_qs_Wh_per_km=e_qs, e_dyn_Wh_per_km=e_dyn, diff_pct=None, decisive=False,
                    status="undefined (QS energy <= 0)", non_positive_term=bad)
    diff = 100.0 * (e_dyn - e_qs) / e_qs
    decisive = QS_DYN_DECISIVE[motor]
    if not decisive:
        status = "reported only (M2)"
    else:
        status = "pass" if abs(diff) <= QS_DYN_MAX_PCT else "FAIL (branch INCONCLUSIVE, protocol 9)"
    return dict(raw, e_qs_Wh_per_km=e_qs, e_dyn_Wh_per_km=e_dyn, diff_pct=diff, decisive=decisive, status=status,
                non_positive_term="")


# --------------------------------------------------------------------------- planner checks
def scenario_totals(E_b_J: float, E_seco_J: float, LB_total_J: float) -> dict:
    """Protocol 5.4: S_found = 1 - E_Seco/E(v_b), S_max = 1 - sum LB_k / E(v_b), both on the QS plant (in %).
    AMB-29(c) ruling: with E(v_b) <= 0 no percentage is computed; the term is named and the check is not evaluable."""
    bad = non_positive_term("E(v_b) (QS baseline energy, J)", E_b_J)
    if bad:
        return dict(S_found_pct=None, S_max_pct=None, optimality_gap_pp=None, stated_resolution_pp=None,
                    status="NOT_EVALUABLE_DENOMINATOR_NOT_POSITIVE", non_positive_term=bad,
                    E_b_J=E_b_J, E_seco_J=E_seco_J, LB_total_J=LB_total_J)
    s_found = 100.0 * (1.0 - E_seco_J / E_b_J)
    s_max = 100.0 * (1.0 - LB_total_J / E_b_J)
    gap = s_max - s_found
    return dict(S_found_pct=s_found, S_max_pct=s_max, optimality_gap_pp=gap,
                stated_resolution_pp=gap if gap > OPTIMALITY_PP else None)


def grid_convergence(E_b_J: float, E_seco_coarse_J: float, E_seco_fine_J: float) -> dict:
    """Protocol 9 planner grid convergence: (2 m, 0.1 m/s) vs (1 m, 0.05 m/s). AMB-29(c) ruling: with E(v_b) <= 0 the
    check is not evaluable (passed None), never a pass."""
    bad = non_positive_term("E(v_b) (QS baseline energy, J)", E_b_J)
    if bad:
        return dict(dS_found_pp=None, passed=None, stated_resolution_pp=None,
                    status="NOT_EVALUABLE_DENOMINATOR_NOT_POSITIVE", non_positive_term=bad)
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
    "BASELINE_INFEASIBLE_ON_P3",   # D5/AMB-24: B0 fails protocol 8.2 on the P3 plant -> non-comparable for energy
    "ECO_INFEASIBLE_ON_P3",        # D5/AMB-24: the P1-designed S-eco run fails protocol 8.2 on the P3 plant
    "B0_INVALID_EXCLUDED",         # protocol 8.1: B0 fails 8.2 -> condition excluded and reported
    "INVALID_COMPARISON",          # protocol 8.1: B3 fails 8.2
    "RECOMPUTATION_DISAGREEMENT",  # protocol 9: not credited until resolved by amendment
    COMPARABLE,
)


def arm_comparable(ev_row: dict) -> bool:
    """Protocol 8.2 from the independent evaluator's flags and the simulator validity (never a planner flag)."""
    return bool(ev_row["sim_valid"] and ev_row["complete"] and ev_row["tracking_ok"] and ev_row["stop_ok"]
                and ev_row["constraint_ok"] and ev_row["finite_ok"])


def failed_criteria(ev_row: dict) -> list[str]:
    """The protocol 8.2 criteria an executed arm fails (from evaluator and simulator flags only)."""
    names = {"sim_valid": "valid", "complete": "complete", "tracking_ok": "tracking", "stop_ok": "stop compliance",
             "constraint_ok": "constraint compliance", "finite_ok": "finite"}
    return [n for k, n in names.items() if not ev_row.get(k)]


def classify_pair(b0: dict | None, b3: dict | None, *, eco_profile_ok: bool, baseline_ok: bool, pstate: str) -> str:
    """Status of one (cycle, motor, limits, plant state[, draw]) condition, in this order: profile/baseline
    availability, errors, B0 protocol 8.2, B3 protocol 8.2, recomputation (protocol 9).
    On P3 (D5, AMB-24) an 8.2 failure is the formal infeasibility verdict: B0 -> BASELINE_INFEASIBLE_ON_P3
    (non-comparable for energy), B3 -> ECO_INFEASIBLE_ON_P3. On P1 the protocol 8.1 labels apply. The QS screen
    is not an input. b0/b3: evaluation rows (None if not executed); a row with key 'error' records an exception."""
    if not eco_profile_ok:
        return "PROFILE_UNAVAILABLE"
    if not baseline_ok:
        return "BASELINE_UNAVAILABLE"
    if b0 is None or b3 is None or b0.get("error") or b3.get("error"):
        return "ERROR"
    if not arm_comparable(b0):
        return "BASELINE_INFEASIBLE_ON_P3" if pstate == "P3" else "B0_INVALID_EXCLUDED"
    if not arm_comparable(b3):
        return "ECO_INFEASIBLE_ON_P3" if pstate == "P3" else "INVALID_COMPARISON"
    if not (b0["recompute_protocol_ok"] and b3["recompute_protocol_ok"]):
        return "RECOMPUTATION_DISAGREEMENT"
    return COMPARABLE


def paired_delta(status: str, b0: dict, b3: dict) -> dict:
    """Protocol 7.1: dE_abs and dE_rel per reference km, always together; refused unless COMPARABLE. AMB-29(c) ruling
    (no relative percentage with a non-positive denominator): if the B0 energy per reference km is <= 0, dE_rel is not
    computed (None, NOT_EVALUABLE_DENOMINATOR_NOT_POSITIVE) and the term is named; such a cell cannot show either side
    of the protocol 8.1 -1 % rule."""
    if status != COMPARABLE:
        raise ValueError(f"refusing a paired energy difference for a {status} condition (protocol 8.1, D5)")
    e0, e3 = b0["Wh_per_ref_km"], b3["Wh_per_ref_km"]
    bad = non_positive_term("B0 energy per reference km (dE_rel denominator)", e0)
    return dict(dE_abs_Wh_per_km=e3 - e0, dE_rel_pct=None if bad else 100.0 * (e3 - e0) / e0,
                dE_rel_status="NOT_EVALUABLE_DENOMINATOR_NOT_POSITIVE" if bad else "defined", non_positive_term=bad or "",
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


# --------------------------------------------------------------------------- owner rulings AMB-29(a), AMB-31
CONFIRMATORY = "CONFIRMATORY_PAIRED_ENDPOINT"
ENERGY_ROLES = (CONFIRMATORY, "VALID_RUN_NOT_IN_PAIRED_ENDPOINT", "DIAGNOSTIC_ONLY_RUN_INVALID",
                "DIAGNOSTIC_ONLY_RECOMPUTATION_NOT_CONFIRMED", "NO_ENERGY_NOT_EXECUTED")
PROFILE_FAILURE_STATUSES = ("PROFILE_UNAVAILABLE", "BASELINE_UNAVAILABLE")


def energy_role(executed: bool, arm_valid: bool, recompute_ok: bool, condition_status: str) -> str:
    """Role of one run's energy (AMB-31 ruling). Only a run of a condition whose FINAL status is COMPARABLE (both arms
    complete the task and pass every 8.2 criterion and the separate recomputation) is confirmatory. The energy of an
    8.2-invalid or unconfirmed run is kept, labelled diagnostic only; no flag of the run can change this."""
    if not executed:
        return "NO_ENERGY_NOT_EXECUTED"
    if not arm_valid:
        return "DIAGNOSTIC_ONLY_RUN_INVALID"
    if not recompute_ok:
        return "DIAGNOSTIC_ONLY_RECOMPUTATION_NOT_CONFIRMED"
    return CONFIRMATORY if condition_status == COMPARABLE else "VALID_RUN_NOT_IN_PAIRED_ENDPOINT"


def feasibility_accounting(cond_rows, run_roles) -> list[dict]:
    """Planned-run and feasibility denominators per motor and set, per motor and overall (AMB-29(a) ruling). Every
    planned condition and run stays counted; profile failures are explicit (never NOT_APPLICABLE, never removed).
    run_roles: one row per planned run with condition_id, executed, arm_8_2_valid and energy_role. Invariants:
    the status counts add up to planned_conditions and the energy roles to planned_runs."""
    by_cond = {}
    for x in run_roles:
        by_cond.setdefault(x["condition_id"], []).append(x)
    groups = {}
    for r in cond_rows:
        for key in ((r["motor"], r["set"]), (r["motor"], "ALL"), ("ALL", "ALL")):
            groups.setdefault(key, []).append(r)
    out = []
    for (motor, set_), rows in sorted(groups.items()):
        st = [r["status"] for r in rows]
        unknown = sorted(set(st) - set(STATUSES))
        if unknown:
            raise ValueError(f"unknown condition status {unknown}")
        runs = [x for r in rows for x in by_cond.get(r["condition_id"], [])]
        roles = [x["energy_role"] for x in runs]
        unknown = sorted(set(roles) - set(ENERGY_ROLES))
        if unknown:
            raise ValueError(f"unknown energy role {unknown}")
        row = dict(motor=motor, set=set_, planned_conditions=len(rows), planned_runs=len(runs),
                   runs_executed=sum(1 for x in runs if x["executed"]),
                   runs_not_executed=sum(1 for x in runs if not x["executed"]),
                   runs_not_executed_profile_failure=sum(1 for x in runs if not x["executed"]
                                                         and x["condition_status"] in PROFILE_FAILURE_STATUSES),
                   runs_8_2_valid=sum(1 for x in runs if x["executed"] and x["arm_8_2_valid"]),
                   runs_8_2_invalid=sum(1 for x in runs if x["executed"] and not x["arm_8_2_valid"]),
                   profile_failure_conditions=sum(st.count(s) for s in PROFILE_FAILURE_STATUSES),
                   paired_endpoint_eligible_conditions=st.count(COMPARABLE),
                   excluded_from_paired_endpoint_conditions=len(rows) - st.count(COMPARABLE))
        row.update({f"status_{s}": st.count(s) for s in STATUSES})
        row.update({f"runs_{k}": roles.count(k) for k in ENERGY_ROLES})
        out.append(row)
    return out


H3_NOMINAL_CELLS = tuple((m, lim) for m in ("M0", "M1", "M2") for lim in NOMINAL_LIMITS)    # protocol 8.1, NOM set
H3_SEN_MOTORS, H3_SEN_DRAWS, H3_SEN_MIN = ("M0", "M1"), 32, 29                              # protocol 8.1, 8.4
_EVIDENCE_FIELDS = ("error", "b0_failed_8_2", "b3_failed_8_2", "separate_recomputation", "eco_status",
                    "eco_validator_failures", "qs_vs_dyn_pair_status")


def _missing_evidence(cell: str, status: str, rows) -> dict:
    """AMB-32 ruling: the record of why a nominal cell has no comparable pair (its status and the row's own reasons)."""
    detail = []
    for r in rows:
        detail += [f"{k}={r[k]}" for k in _EVIDENCE_FIELDS if r.get(k) not in (None, "", "ok")]
    return dict(cell=cell, status=status, detail="; ".join(detail) or ("no row in the record" if not rows
                                                                       else "more than one row in the record"))


def h3_verdict_eligibility(cond_rows, branch_outcomes) -> dict:
    """Which protocol 8.1 verdicts remain POSSIBLE, from condition statuses and the QS-vs-dynamic branch outcomes only.
    It never reads an energy value and computes no energy difference. The 8.1 denominators are fixed (6 nominal
    S2 P1 cells; 32 draws per M0/M1): a missing, profile-failed, invalid or non-comparable cell or draw is never
    removed and never counts toward SUPPORTED, so no verdict can be reached by omission. AMB-32 owner ruling
    (2026-10-28): NOT SUPPORTED needs a comparable pair in all six nominal cells; a nominal cell that is missing, invalid
    or not evaluable makes the verdict INCONCLUSIVE, recorded with its reason (nominal_missing_evidence); no negative
    finding is inferred from missing data. Other protocol 9 checks (grid, optimality, time step, recomputation) are not
    evaluated here; they can only remove possibilities."""
    nom, nom_rows = {}, {}
    for r in cond_rows:
        if r["set"] == NOMINAL_SET:
            nom.setdefault((r["motor"], r["limits"]), []).append(r["status"])
            nom_rows.setdefault((r["motor"], r["limits"]), []).append(r)
    nominal = {f"{m}/{lim}": (nom.get((m, lim)) or [NOT_IN_RECORD])[0] if len(nom.get((m, lim), [])) <= 1
               else DUPLICATE_IN_RECORD for m, lim in H3_NOMINAL_CELLS}
    nominal_missing = sorted(k for k, s in nominal.items() if s != COMPARABLE)
    missing_evidence = [_missing_evidence(f"{m}/{lim}", nominal[f"{m}/{lim}"], nom_rows.get((m, lim), []))
                        for m, lim in H3_NOMINAL_CELLS if nominal[f"{m}/{lim}"] != COMPARABLE]
    sen = {}
    for m in H3_SEN_MOTORS:
        st = [r["status"] for r in cond_rows if r["set"] == "SEN" and r["motor"] == m]
        sen[m] = dict(protocol_draws=H3_SEN_DRAWS, planned_in_record=len(st), comparable=st.count(COMPARABLE),
                      not_comparable_or_missing=H3_SEN_DRAWS - st.count(COMPARABLE),
                      max_draws_that_could_pass=min(st.count(COMPARABLE), H3_SEN_DRAWS))
    sen_short = [m for m in H3_SEN_MOTORS if sen[m]["max_draws_that_could_pass"] < H3_SEN_MIN]
    qs = {b.get("motor"): b.get("outcome") for b in branch_outcomes}
    qs_block = [m for m in ("M0", "M1") if qs.get(m) != "PASS"]
    supported = not nominal_missing and not sen_short and not qs_block
    not_supported = not nominal_missing and not qs_block
    reasons = ([f"nominal cell(s) without a comparable pair: {', '.join(nominal_missing)} (AMB-32: INCONCLUSIVE, "
                f"not NOT SUPPORTED)"] if nominal_missing else []) \
        + [f"{m}: at most {sen[m]['max_draws_that_could_pass']} of {H3_SEN_DRAWS} sensitivity draws comparable "
           f"(< {H3_SEN_MIN})" for m in sen_short] \
        + [f"QS-vs-dynamic branch {m} outcome {qs.get(m)!r}, not PASS" for m in qs_block]
    return dict(nominal_cells=nominal, nominal_missing_evidence=missing_evidence, sensitivity=sen,
                qs_vs_dynamic_branch_outcomes=qs,
                supported_possible=supported, not_supported_possible=not_supported,
                verdict_without_energy="INCONCLUSIVE" if not (supported or not_supported)
                else "not determined here (needs the energy results, which this function never reads)",
                reasons=reasons, note="other protocol 9 checks are not evaluated by this function")
