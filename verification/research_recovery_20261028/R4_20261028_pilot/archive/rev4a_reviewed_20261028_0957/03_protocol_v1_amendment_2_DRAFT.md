# Amendment 2 to R4 protocol v1 (H3): N-A2 — applicability of the QS-versus-dynamic check

**Status: DRAFT — NOT APPROVED FOR RELEASE.** This draft is not issued, not frozen, not approved and has no force. The owner must review and issue it (§11).

| Item | Value |
|---|---|
| Frozen protocol v1 | `../R4_20261028_preflight/03_R4_protocol_v1.md`, SHA-256 `f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab` (unchanged) |
| Amends | issued amendment 1, `../R4_20261028_campaign/release/03_R4_protocol_v1_amendment_1.md`, SHA-256 `7720fed75bb678e47a229d00aff154e0aa14607c051f4a1163cc9bf67b6abee2` (unchanged; it stays in force for everything this draft does not address) |
| Basis | the owner's ruling on review finding N-A2 (2026-10-28); `review/CR-A2_CR-A6_rereview_agent_report_20261028.md` |
| Integrity identifier | the SHA-256 of this draft is in `03_protocol_v1_amendment_2_DRAFT.sha256.txt` and in `zz_sha256_manifest_v5.csv`. It identifies the text only; it is not an approval |

## 1. The owner's ruling (N-A2)

The protocol §9 QS-versus-dynamic consistency check is applicable only to an evaluation pair for which **both** the baseline (B0) profile and the eco (B3) profile pass the prescribed quasi-static feasibility screen under the same applicable conditions.

If either profile fails the QS feasibility screen:
- The pair's QS-versus-dynamic check is classified `NOT_APPLICABLE_QS_INFEASIBLE`. This is neither a pass nor a failure.
- The QS diagnostic outputs and the exact failed feasibility check are preserved.
- QS energy calculated from torque demand beyond the QS model's admissible limits is never used to pass or fail the check.
- No QS energy-saving percentage is calculated for that pair for acceptance purposes.
- The profile, plant, LQR gain, constraint limits and task are never modified to make the pair QS-feasible.

## 2. Pair-level applicability rule

| Term | Definition |
|---|---|
| **Pair** | the B0 and B3 runs of one scheduled condition: cycle, motor branch, limit set, evaluated plant state and, for SEN, draw |
| **QS feasibility screen** | every constant-acceleration piece of the tracked profile passes `QSPlant.step` (the §5.2 feasibility notion) on the condition's **evaluated** plant, with its motor branch and limit set. This is "the same applicable conditions": P1 for NOM, INS and CNV; P3 for the P3 set; the draw's P1 plant for SEN |
| **QS-eligible pair** | both profiles exist and both pass the screen |

**For a QS-eligible pair:**
- The existing §9 rule applies to each arm, unchanged: e_QS is the QS energy of the tracked knots, e_dyn the dynamic energy, both per reference km, and the deviation is 100·(e_dyn − e_QS)/e_QS.
- M0 and M1 must satisfy |deviation| ≤ 1 %. M2 is reported only.
- The pair status is PASS if both arms pass, FAIL if either M0/M1 arm fails, and REPORTED_ONLY for M2.

**Thresholds** are unchanged from protocol v1 §9 and amendment 1.

**Consequence of an applicable failure** (unchanged): the relevant M0/M1 motor branch is `INCONCLUSIVE`.

## 3. `NOT_APPLICABLE_QS_INFEASIBLE`

| Item | Rule |
|---|---|
| When | at least one profile of the pair fails the QS feasibility screen |
| Meaning | the check does not apply to this pair: **neither a pass nor a failure** |
| Recorded per arm | `qs_screen_feasible`, `qs_screen_n_failed`, the QS energy (as a diagnostic only, `qs_E_J_diagnostic`); `qs_vs_dyn_status = NOT_APPLICABLE_QS_INFEASIBLE`; `qs_vs_dyn_pct` left empty |
| Recorded per condition | `qs_eligible_pair = false`, `qs_ineligible_arms` (B0, B3 or B0,B3), the exact failed pieces (piece index, time interval, start and end speed) in `b0/b3_qs_screen_warning`, `qs_vs_dyn_pair_status`, `qs_vs_dyn_pair_reason` |
| Never | used as a pass; used to fail; used for a QS saving; a reason to drop or alter a run |

## 4. Dynamic feasibility is independent

- Formal feasibility remains governed by the dynamic run's §8.2 criteria (amendment 1, §5).
- **QS ineligibility never overrides, excuses or replaces a §8.2 result:**
  - a QS-ineligible pair whose dynamic runs pass §8.2 keeps its §8.2 status (for example COMPARABLE);
  - a QS-ineligible pair whose dynamic run fails §8.2 is classified exactly as amendment 1 prescribes (for example BASELINE_INFEASIBLE_ON_P3), with no paired energy result.
- The pair status of amendment 1 §5 does not depend on the QS screen at all.

## 5. Motor-branch outcome of the QS-versus-dynamic criterion

- **Scope.** The criterion is evaluated per motor branch over every planned pair of that motor, across all sets. This is the literal reading of §9's "every B0 and B3 profile" (see §6, AMB-30).
- **M2:** REPORTED_ONLY; no consequence.
- **M0 / M1:**
  - **INCONCLUSIVE** if any applicable check fails (FAIL).
  - **INCONCLUSIVE** if no eligible comparison passed or exists. The branch **cannot pass by vacuity**: a branch whose pairs are all not applicable or not evaluable is INCONCLUSIVE with respect to this criterion.
  - **INCONCLUSIVE** if an eligible pair could not be evaluated (AMB-29(b)).
  - **PASS** only if every applicable check passes and at least one does. Pairs that are not applicable do not count either way.
- **No minimum eligible-count threshold** is introduced beyond "at least one".

## 6. Ambiguities found while implementing the ruling (documented; owner to confirm)

| ID | Question | Handling in the draft (not a favourable choice; owner to confirm or replace) |
|---|---|---|
| AMB-29(a) | A pair whose B0 or B3 **profile does not exist** (baseline task unavailable, or S-eco unavailable or invalid) has nothing to screen. Is the check applicable? | **Not applicable**, labelled `NOT_EVALUABLE_PROFILE_UNAVAILABLE`, kept separate from `NOT_APPLICABLE_QS_INFEASIBLE`. It does not by itself change the branch outcome, and such a pair can never contribute a pass. Under the ruling's pair-level wording, a B0-only check is no longer computed for such a pair (amendment 1's implementation computed one) |
| AMB-29(b) | A **QS-eligible** pair without a usable dynamic energy (an arm raised an exception or its states became non-finite). Is that a pass, a failure or not applicable? | **Not evaluable**, labelled `NOT_EVALUABLE_RUN_MISSING`. It makes the M0/M1 branch **INCONCLUSIVE**, because a check that applied could not be shown to pass (conservative) |
| AMB-30 | §9's "every B0 and B3 profile" makes the branch outcome depend on all sets: NOM, P3, INS, CNV and SEN. Is that the intended scope, or only the decisive S2 P1 set? | **Literal reading** (all sets), as already implied by amendment 1. Per-set counts are reported in `qs_dynamic_accounting.csv`, so the scope is visible. Not changed by this draft |

## 7. Required denominators and reporting

Per motor branch and set, and per motor overall (`qs_dynamic_accounting.csv`):

| Category | Columns |
|---|---|
| Planned pairs | `planned_pairs` |
| QS-eligible pairs | `qs_eligible_pairs` |
| QS-ineligible pairs, in total and by arm | `qs_ineligible_pairs`; `qs_ineligible_b0_only`, `qs_ineligible_b3_only`, `qs_ineligible_both` |
| Not evaluable | `not_evaluable_profile_unavailable`, `not_evaluable_run_missing` |
| Check outcomes | `qs_check_pass`, `qs_check_fail`, `qs_check_reported_only` |
| Pairs whose two dynamic runs pass §8.2 | `dynamic_valid_pairs` |
| Valid energy-comparison pairs (status COMPARABLE after the separate recomputation) | `valid_energy_comparison_pairs` |

- Every planned pair falls in exactly one check-status class.
- Branch outcomes go to `qs_dynamic_branch_outcomes.csv` and `manifest.json`.
- No run record is deleted, dropped or altered because a check is not applicable; `runs.csv`, `evaluation.csv` and the traces keep every run.
- No energy comparison is credited for an invalid or incomplete pair (amendment 1, §5).

## 8. Effect on the planned 170-run schedule

None. The 170 official runs, their IDs, sets, plants, profiles, gains (the nominal P1 gain for every SEN draw, AMB-14), tolerances and numerics are unchanged. No run is added, removed or made conditional. S2 is not used for tuning.

## 9. Changes outside the ruling (separate issues; not part of N-A2)

- **SI-1 — location-independent path resolution** (`code/r4h3/frozen.py`, `campaign.py`).
  - **What changed:** the project root and the preflight, pilot and campaign directories are now found from markers, not from a fixed folder depth.
  - **Why:** this lets a release attempt be tested from a versioned sub-directory (`R4_20261028_campaign/release_attempts/attempt3_amendment2/`) without overwriting the amendment-1 release package.
  - **Behaviour:** unchanged from the pilot and the campaign root; every path resolves to the same location (test `test_si1_paths_are_location_independent`).
  - **Campaign mode:** still runs only from the campaign root.

No other behaviour changes.

## 10. Blockers retained

The campaign remains **BLOCKED**. Campaign mode is refused until all of these hold:

1. Amendment 2 is reviewed and approved by the owner and issued (§11).
2. The new release attempt passes all mandatory tests and independent reviews.
3. The final release manifest and protocol hashes are verified.
4. All release criteria are met. This includes promoting the approved attempt to the campaign root with its own protocol §10.1 gate record, because campaign mode runs only there.
5. The owner explicitly authorises campaign execution in a separate action: `release/campaign_authorization.json`, which must also carry this amendment's issued SHA-256.

## 11. To issue (owner)

1. Review this draft, decide AMB-29 and AMB-30, and review the new release attempt's report.
2. Copy the reviewed text to `R4_20261028_campaign/release/03_R4_protocol_v1_amendment_2.md`, set `"status": "APPROVED"` in the block, and record its SHA-256.
3. Write `R4_20261028_campaign/release/amendment_2_approval.json` with `approved_by`, `date` and `amendment_sha256`.

## 12. Machine-readable block

`code/r4h3/campaign.py` (`IMPLEMENTED_2`) reads this block. Every value must equal what the code implements: a difference or an unknown key is an error, never an override.

<!-- r4h3-amendment-block -->
```json
{
 "amendment": "R4 protocol v1 amendment 2 (N-A2), draft",
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
 "AMB_29_profile_unavailable": "NOT_EVALUABLE_PROFILE_UNAVAILABLE",
 "AMB_29_eligible_run_missing": "NOT_EVALUABLE_RUN_MISSING (branch INCONCLUSIVE)",
 "pair_statuses": [
  "PASS",
  "FAIL",
  "REPORTED_ONLY",
  "NOT_APPLICABLE_QS_INFEASIBLE",
  "NOT_EVALUABLE_PROFILE_UNAVAILABLE",
  "NOT_EVALUABLE_RUN_MISSING"
 ],
 "planned_runs": {
  "NOM": 12,
  "P3": 12,
  "INS": 12,
  "CNV": 6,
  "SEN": 128,
  "total": 170
 },
 "note": "DRAFT - NOT APPROVED FOR RELEASE. Values must equal the implementation."
}
```
