# Amendment 2 to R4 protocol v1 (H3): N-A2, AMB-29(a) and AMB-31 — applicability of the QS-versus-dynamic check, missing profiles and energy of invalid runs

**Status: CANDIDATE rev4 — DRAFT — NOT APPROVED FOR RELEASE.** This candidate is not issued, not frozen and not approved, and has no force. It contains owner decisions that are still open (§7). The owner must decide them and issue the amendment (§13).

| Item | Value |
|---|---|
| Frozen protocol v1 | `../R4_20261028_preflight/03_R4_protocol_v1.md`, SHA-256 `f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab` (unchanged) |
| Amends | issued amendment 1, `../R4_20261028_campaign/release/03_R4_protocol_v1_amendment_1.md`, SHA-256 `7720fed75bb678e47a229d00aff154e0aa14607c051f4a1163cc9bf67b6abee2` (unchanged; it stays in force for everything this candidate does not address) |
| Basis | the owner's rulings of 2026-10-28: N-A2; AMB-29(a) (missing profile); AMB-31 (energy of a run failing §8.2) |
| Supersedes (as the text proposed for issue) | draft rev3, `03_protocol_v1_amendment_2_DRAFT.md`, SHA-256 `fdaf193de510488733f0e0899d50def86cbeafabdbecdd3bc7a144099b6f492c`, kept unchanged. Earlier drafts: rev2 `e0dc68827c57704b49b13886c455b281e4e3c10ce377a1f174742ff5529247cc`, rev1 `a936023af0a772ee2b81c720c76f9c462aba89afe1a8e1de38a286872a8744bf`, rev0 `c3e1ddfce7dca7909bb1cd2a6186f4d5044b5dfe81eeed43df0b9fcf215957d4` (all archived unchanged) |
| Decision record | `15_remaining_owner_decisions.md` (rulings made vs decisions still open, with the text needed to issue them) |
| Integrity identifier | the SHA-256 of this file is recorded in `03_protocol_v1_amendment_2_rev4_CANDIDATE.sha256.txt`. It identifies the text only; it is not an approval |

## 1. Owner rulings this candidate implements (binding)

### 1.1 N-A2 (unchanged from rev3)
The protocol §9 QS-versus-dynamic consistency check is applicable only to an evaluation pair for which **both** the baseline (B0) profile and the eco (B3) profile pass the prescribed quasi-static feasibility screen under the same applicable conditions. If either profile fails the screen, the pair's check is `NOT_APPLICABLE_QS_INFEASIBLE`: neither a pass nor a failure. The QS diagnostics and the exact failed feasibility check are preserved; QS energy computed from torque beyond the QS model's admissible limits is never used to pass or fail the check; no QS saving is computed for that pair for acceptance; the profile, plant, LQR gain, limits and task are never modified.

### 1.2 AMB-29(a): missing profile (owner ruling 2026-10-28)
- A profile-generation failure or planner infeasibility **remains an explicit outcome**: the condition's status is `PROFILE_UNAVAILABLE` (S-eco time-infeasible, no feasible path, or rejected by the validator) or `BASELINE_UNAVAILABLE` (no baseline task v_b), as amendment 1 already defines.
- That condition **counts** in the planned-run, feasibility and verdict denominators (§8). It is never removed from a denominator and never relabelled `NOT_APPLICABLE` for the experiment outcome.
- It **never yields a paired energy comparison**: it is never `COMPARABLE`, and `paired_delta` refuses it.
- Only the pair's **QS-versus-dynamic check** is `NOT_APPLICABLE_PROFILE_UNAVAILABLE`, because that check's applicability condition (both profiles exist and pass the QS screen, §1.1) is objectively unmet. An inapplicable check is **not a pass**.
- The arm whose profile exists is still run and recorded (amendment 1); its energy has the role `VALID_RUN_NOT_IN_PAIRED_ENDPOINT` or `DIAGNOSTIC_ONLY_RUN_INVALID` (§3).

### 1.3 AMB-31: energy from a run failing §8.2 (owner ruling 2026-10-28)
- Energy from a run that fails any mandatory §8.2 criterion (valid, complete, tracking, stop compliance, constraint compliance, finite), or that the separate recomputation does not confirm (§9), is **not a valid confirmatory energy result**.
- It is retained for debugging and diagnostics, **labelled** as belonging to an invalid or unconfirmed run (§3). It is never credited to the primary paired energy endpoint.
- A valid paired energy comparison requires **both** arms to complete the prescribed task and to satisfy every mandatory validity condition: the condition's **final** status (after the separate recomputation) is `COMPARABLE`.
- A constraint failure is never reinterpreted as a harmless diagnostic deviation to keep the energy result. No raw energy output or failure record is discarded.
- **The QS-versus-dynamic check uses only valid energy:** for a QS-eligible pair, an arm counts only if its run passes §8.2 (in process) and is confirmed by the separate recomputation. An eligible pair with an invalid or unconfirmed arm is `NOT_EVALUABLE_RUN_INVALID` (§2). The invalid arm's QS-vs-dynamic value is kept in `qs_vs_dyn_pct_diagnostic_invalid_run` only.

## 2. Pair-level QS-versus-dynamic status

| Term | Definition |
|---|---|
| **Pair** | the B0 and B3 runs of one scheduled condition: cycle, motor branch, limit set, evaluated plant state and, for SEN, draw |
| **QS feasibility screen** | every constant-acceleration piece of the tracked profile passes `QSPlant.step` on the condition's **evaluated** plant, with its motor branch and limit set (P1 for NOM, INS and CNV; P3 for the P3 set; the draw's P1 plant for SEN) |
| **QS-eligible pair** | both profiles exist and both pass the screen |
| **Valid arm** (AMB-31) | an executed run with a finite simulator energy that passes every §8.2 criterion and is confirmed by the separate recomputation |

| Pair status | When | M0/M1 branch consequence |
|---|---|---|
| **PASS** | eligible; both arms valid and within 1 % per reference km | counts toward "at least one" |
| **FAIL** | eligible; a **valid** arm exceeds 1 % (even if the other arm is not valid, R3-2) | branch INCONCLUSIVE (protocol §9, unchanged) |
| **REPORTED_ONLY** | M2, eligible, both arms valid, ratio defined | none (M2 reported only) |
| `NOT_APPLICABLE_QS_INFEASIBLE` | a profile fails the QS screen | none; not a pass, not a fail |
| `NOT_APPLICABLE_PROFILE_UNAVAILABLE` | a profile does not exist (§1.2); the condition keeps its explicit failure status | none for this check; not a pass. The condition counts as a failure in §8 |
| `NOT_EVALUABLE_RUN_MISSING` | eligible; an arm has no finite energy (exception, non-finite) | **open: AMB-29(b)** (proposed: INCONCLUSIVE) |
| `NOT_EVALUABLE_RUN_INVALID` | eligible; an arm's energy is finite but its run fails §8.2 or is not confirmed by the separate recomputation (AMB-31 ruling) | **open: follows AMB-29(b)** (proposed: INCONCLUSIVE) |
| `NOT_EVALUABLE_QS_UNDEFINED` | eligible; QS energy ≤ 0 | **open: AMB-29(c)** (proposed: INCONCLUSIVE) |
| `NOT_EVALUABLE_CONDITION_ERROR` | an exception before or during the pair evaluation; eligibility unknown | **open: AMB-29(d)** (proposed: INCONCLUSIVE) |

For M2 every `NOT_EVALUABLE_*` label is used the same way; the M2 branch stays reported only. Thresholds are unchanged from protocol v1 §9 and amendment 1 (M0/M1 ≤ 1 %, M2 reported only).

**Order with the separate recomputation:** the pair status is first set in process. After the separate recomputation, a PASS, FAIL or REPORTED_ONLY that used the energy of an arm the recomputation does not confirm becomes `NOT_EVALUABLE_RUN_INVALID`; the in-process value is kept in `qs_vs_dyn_pair_status_in_process`. A FAIL of a confirmed arm stays a FAIL.

## 3. Energy roles (AMB-31 ruling)

Every planned run has exactly one role in `energy_roles.csv` (no energy value is copied there; raw energies stay in `runs.csv`, `evaluation.csv` and the traces):

| Role | When | Use |
|---|---|---|
| `CONFIRMATORY_PAIRED_ENDPOINT` | the condition's final status is `COMPARABLE` | the only energy usable for the primary paired endpoint (§7.1, §8.1) |
| `VALID_RUN_NOT_IN_PAIRED_ENDPOINT` | the run is valid and confirmed, but its condition is not `COMPARABLE` (for example the other arm failed or a profile is missing) | reported; never in the paired endpoint |
| `DIAGNOSTIC_ONLY_RUN_INVALID` | the run fails a §8.2 criterion (the failed criteria are recorded) | diagnostics only |
| `DIAGNOSTIC_ONLY_RECOMPUTATION_NOT_CONFIRMED` | the run passes §8.2 in process but the separate recomputation does not confirm it | diagnostics only |
| `NO_ENERGY_NOT_EXECUTED` | the run was not executed (missing profile) or raised an exception | none; counted |

The role depends only on the run's executed flag, its §8.2 flags, the recomputation result and the final condition status. No other field (for example a `credited` flag) can make an invalid run confirmatory.

## 4. Dynamic feasibility is independent

- Formal feasibility remains governed by the dynamic run's §8.2 criteria (amendment 1, §5). QS ineligibility never overrides, excuses or replaces a §8.2 result.
- The pair status of amendment 1 §5 does not use the QS screen. `P3_RULE` keeps amendment 1's wording; the QS screen additionally decides only whether the §9 QS-versus-dynamic check applies (R3-10).

## 5. Motor-branch outcome of the QS-versus-dynamic criterion

- `NOT_APPLICABLE_*` pairs never change the branch outcome; `NOT_EVALUABLE_*` pairs make an M0/M1 branch INCONCLUSIVE **as proposed, subject to AMB-29(b)–(d)** (§7).
- M0/M1 INCONCLUSIVE if any applicable check fails, or if no eligible comparison passed or exists (**never a pass by vacuity**). PASS only if every applicable check passes and at least one does. No minimum eligible count beyond one.
- Scope: every planned pair of the motor across all sets (**open: AMB-30**, §7).
- Because PASS now requires valid arms, `n_PASS_dynamic_valid` equals `n_PASS`; both stay reported.

## 6. Consequences for denominators, feasibility and the overall H3 verdict

### 6.1 Planned-run and feasibility reporting (`feasibility_accounting.csv`)
Per motor and set, per motor, and overall: `planned_conditions`, `planned_runs`, `runs_executed`, `runs_not_executed`, `runs_not_executed_profile_failure`, `runs_8_2_valid`, `runs_8_2_invalid`, `profile_failure_conditions`, `paired_endpoint_eligible_conditions`, `excluded_from_paired_endpoint_conditions`, one `status_<S>` count per condition status and one `runs_<role>` count per energy role. The status counts add up to `planned_conditions`; the role counts add up to `planned_runs`. Nothing is dropped.

### 6.2 QS-versus-dynamic denominators (`qs_dynamic_accounting.csv`)
As rev3 §7, plus `not_evaluable_run_invalid`. The eligibility classes and the check-status classes each add up to `planned_pairs`.

### 6.3 Overall H3 verdict (protocol §8.1, unchanged rules)
The §8.1 denominators are fixed and are never reduced:
- **SUPPORTED** needs a `COMPARABLE` pair in all **six** nominal S2 P1 cells (M0, M1, M2 × L-R1, L-EVE), at least **29 of 32** sensitivity draws for M0 and for M1 separately, and every §9 check passing. A missing profile, an invalid arm, an error or a recomputation disagreement in a nominal cell makes SUPPORTED impossible; a non-comparable draw can never count as one of the 29.
- **NOT SUPPORTED** needs every motor branch to show ΔE_rel > −1.0 % with all checks passing. Read here as requiring a comparable pair in all six nominal cells (**open: AMB-32**, §7).
- Otherwise **INCONCLUSIVE**. No verdict is reached by omission.

`h3_verdict_eligibility.json` records, without reading any energy value, which verdicts remain possible from the condition statuses and the QS-vs-dynamic branch outcomes. It computes no energy difference. The remaining §9 checks can only remove possibilities.

## 7. Owner decisions still open (not settled by this candidate)

The handling below is what the code does now; it is proposed, not settled. The options and their consequences are in `15_remaining_owner_decisions.md`.

| ID | Question | Proposed handling | Direction |
|---|---|---|---|
| AMB-29(b) | An eligible pair with an arm without a finite energy; and (by the AMB-31 ruling) an arm whose energy is invalid | `NOT_EVALUABLE_RUN_MISSING` / `NOT_EVALUABLE_RUN_INVALID`; M0/M1 branch INCONCLUSIVE | conservative |
| AMB-29(c) | An eligible pair whose QS energy is ≤ 0 | `NOT_EVALUABLE_QS_UNDEFINED`; M0/M1 branch INCONCLUSIVE | conservative |
| AMB-29(d) | An exception before or during the pair evaluation | `NOT_EVALUABLE_CONDITION_ERROR`; eligibility unknown; M0/M1 branch INCONCLUSIVE | conservative |
| AMB-30 | Scope of the QS-vs-dynamic branch outcome | every planned pair of the motor across all sets | mostly conservative; a pass from a non-decisive set can supply the "at least one" |
| AMB-32 (new) | NOT SUPPORTED with a nominal cell lacking a comparable pair | INCONCLUSIVE (NOT SUPPORTED needs all six cells comparable) | conservative |

## 8. Effect on the planned 170-run schedule

None. The 170 official runs, their IDs, sets, plants, profiles, gains (nominal P1 gain for every SEN draw, AMB-14), tolerances and numerics are unchanged; the schedule's SHA-256 is unchanged. No run is added, removed or made conditional. S2 is not used for tuning.

## 9. Location rule for campaign mode

Unchanged from rev3 §9: campaign mode runs only when the running code's directory is, by resolved path, `R4_20261028_campaign/`.

## 10. Changes since rev3 (complete list)

| Change | Basis | Effect |
|---|---|---|
| A QS-vs-dynamic arm counts only if its run passes §8.2; `pair_qs_dynamic(..., invalid_arms)`; new label `NOT_EVALUABLE_RUN_INVALID`; diagnostic column `qs_vs_dyn_pct_diagnostic_invalid_run` | AMB-31 ruling | stricter |
| After the separate recomputation, a QS result that used an unconfirmed arm becomes `NOT_EVALUABLE_RUN_INVALID` (`fold_separate_recomputation`); condition fields `qs_vs_dyn_fail_arms`, `qs_vs_dyn_invalid_arms`, `qs_vs_dyn_pair_status_in_process`, `paired_endpoint_eligible` | AMB-31 ruling | stricter |
| `energy_roles.csv` (`checks.energy_role`) | AMB-31 ruling | labelling only; no energy value copied |
| `feasibility_accounting.csv` (`checks.feasibility_accounting`) | AMB-29(a) ruling | reporting only |
| `h3_verdict_eligibility.json` (`checks.h3_verdict_eligibility`; reads no energy) | AMB-29(a) and AMB-31 rulings; protocol §8.1 | reporting only; AMB-32 proposed |
| `qs_dynamic_accounting.csv` gains `not_evaluable_run_invalid` | AMB-31 ruling | reporting |
| `NUMERICAL_CHECKS` row 7 text names the AMB-31 rule | AMB-31 ruling | wording; names and order unchanged |
| Machine block: `AMB_29_profile_unavailable` and `AMB_31_*` state the rulings; new keys `AMB_31_invalid_arm_label`, `paired_endpoint_rule`, `h3_verdict_denominators`, `AMB_32_...`; `pair_statuses` gains `NOT_EVALUABLE_RUN_INVALID`; the key `AMB_31_usable_dynamic_energy` is replaced by `AMB_31_energy_of_invalid_runs` | rulings | — |
| `preconditions` blocks on any `reviews_pending` item of the review status | fail-closed | stricter |
| `DRAFT_AMENDMENT_2` → this candidate; `CAMPAIGN_CONFIG` → `campaign_config_v7_DRAFT.json`; `REVIEW_STATUS` → `code_review_status_v5.json` (earlier versions kept unchanged) | versioning | — |

The file-level comparison with the rev3 state (`archive/rev6_attempt3_20261028_1201/`) is `logs/zz_code_changes_rev6_to_rev7.csv`. Unchanged: `classify_pair`, `paired_delta`, the evaluator, the separate recomputation script, the closed loop, the planner, the schedule code and amendment 1's decision set.

## 11. Blockers retained

The campaign remains **BLOCKED** until all of these hold:
1. The owner decides AMB-29(b)–(d), AMB-30 and AMB-32, and amendment 2 is approved and issued (§13).
2. The changes of this candidate pass an **independent** review (pending; recorded in `config/code_review_status_v5.json` → `reviews_pending`, which blocks).
3. A release attempt of the final code passes all mandatory tests and reviews; the final release manifest and protocol hashes are verified.
4. The approved attempt is promoted to the campaign root with its own protocol §10.1 gate, by an owner-approved procedure.
5. The owner explicitly authorises execution in `release/campaign_authorization.json` (scope "execute the 170-run H3 campaign of protocol v1 amendments 1 and 2", with `amendment_sha256`, `amendment_2_sha256` and `pre_run_hashes_sha256`).

## 12. Reporting rules kept

Completed, invalid, infeasible, excluded and profile-failed conditions are reported in separate rows (protocol §10.5). ΔE_abs and ΔE_rel are reported only for `COMPARABLE` conditions, always together, with trip time.

## 13. To issue (owner)

1. Decide AMB-29(b)–(d), AMB-30 and AMB-32 (`15_remaining_owner_decisions.md` §4 gives the text). If any decision differs from §7, the code, the review and a new release attempt must follow before issue.
2. Copy the final text to `R4_20261028_campaign/release/03_R4_protocol_v1_amendment_2.md`, set `"status": "APPROVED"` in the block, and record its SHA-256.
3. Write `R4_20261028_campaign/release/amendment_2_approval.json` with `approved_by`, `date` and `amendment_sha256`.

## 14. Machine-readable block

`code/r4h3/campaign.py` (`IMPLEMENTED_2`) reads this block. Every value must equal what the code implements: a difference or an unknown key is an error, never an override.

<!-- r4h3-amendment-block -->
```json
{
 "amendment": "R4 protocol v1 amendment 2 (N-A2, AMB-29(a), AMB-31), candidate rev4",
 "status": "DRAFT",
 "applies_to_protocol_sha256": "f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab",
 "amends_amendment_1_sha256": "7720fed75bb678e47a229d00aff154e0aa14607c051f4a1163cc9bf67b6abee2",
 "N_A2_applicability": "protocol 9 QS-vs-dynamic applies to a pair only if both the B0 and the B3 profile pass the QS feasibility screen (QSPlant.step) on the condition's evaluated plant",
 "N_A2_not_applicable_label": "NOT_APPLICABLE_QS_INFEASIBLE",
 "N_A2_not_applicable_is_pass": false,
 "N_A2_not_applicable_is_fail": false,
 "N_A2_qs_energy_of_ineligible_pairs_used_for_acceptance": false,
 "N_A2_thresholds": {
  "M0_max_abs_pct": 1.0,
  "M1_max_abs_pct": 1.0,
  "M2": "reported only"
 },
 "N_A2_applicable_failure": "the M0/M1 motor branch is INCONCLUSIVE (protocol 9, unchanged)",
 "N_A2_no_eligible_comparison": "the M0/M1 motor branch is INCONCLUSIVE with respect to this criterion",
 "N_A2_dynamic_8_2_independent": true,
 "N_A2_failed_check_record": "every failing piece with its failed QSPlant.step sub-check(s) (drive torque, battery discriminant, discharge current) and their values at each Gauss node",
 "AMB_29_profile_unavailable": "owner ruling 2026-10-28: the condition keeps its explicit PROFILE_UNAVAILABLE or BASELINE_UNAVAILABLE status and counts in every planned-run, feasibility and verdict denominator; never COMPARABLE, never a paired comparison, never removed; only the pair's QS-vs-dynamic check is NOT_APPLICABLE_PROFILE_UNAVAILABLE (its applicability condition is objectively unmet), which is not a pass",
 "AMB_29_eligible_run_missing": "NOT_EVALUABLE_RUN_MISSING (M0/M1 branch INCONCLUSIVE; M2 stays reported only)",
 "AMB_29_qs_energy_undefined": "NOT_EVALUABLE_QS_UNDEFINED (M0/M1 branch INCONCLUSIVE; M2 stays reported only)",
 "AMB_29_condition_error": "NOT_EVALUABLE_CONDITION_ERROR (eligibility unknown; M0/M1 branch INCONCLUSIVE; M2 stays reported only)",
 "AMB_30_branch_scope": "every planned pair of the motor branch across all sets (literal protocol 9 reading)",
 "AMB_31_energy_of_invalid_runs": "owner ruling 2026-10-28: energy of a run failing protocol 8.2, or not confirmed by the separate recomputation, is diagnostic only (energy_roles.csv DIAGNOSTIC_ONLY_*): never confirmatory, never credited to the paired endpoint, never used by the QS-vs-dynamic check",
 "AMB_31_invalid_arm_label": "NOT_EVALUABLE_RUN_INVALID (consequence as AMB-29(b): M0/M1 branch INCONCLUSIVE; M2 stays reported only)",
 "paired_endpoint_rule": "a paired energy comparison exists only for a condition whose final status is COMPARABLE: both arms complete the task and pass every protocol 8.2 criterion and the separate recomputation",
 "h3_verdict_denominators": "fixed by protocol 8.1: 6 nominal S2 P1 cells and 32 draws per M0/M1; a missing, profile-failed, invalid or non-comparable cell or draw is never removed and never counts toward SUPPORTED",
 "AMB_32_not_supported_needs_all_nominal_cells": "NOT SUPPORTED requires a comparable pair in all six nominal cells; otherwise INCONCLUSIVE (proposed; owner to confirm)",
 "pair_statuses": [
  "PASS",
  "FAIL",
  "REPORTED_ONLY",
  "NOT_APPLICABLE_QS_INFEASIBLE",
  "NOT_APPLICABLE_PROFILE_UNAVAILABLE",
  "NOT_EVALUABLE_RUN_MISSING",
  "NOT_EVALUABLE_QS_UNDEFINED",
  "NOT_EVALUABLE_CONDITION_ERROR",
  "NOT_EVALUABLE_RUN_INVALID"
 ],
 "planned_runs": {
  "NOM": 12,
  "P3": 12,
  "INS": 12,
  "CNV": 6,
  "SEN": 128,
  "total": 170
 },
 "note": "CANDIDATE rev4 - DRAFT - NOT APPROVED FOR RELEASE. Values must equal the implementation."
}
```
