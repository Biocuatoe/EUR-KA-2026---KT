# Amendment 2 to R4 protocol v1 (H3): N-A2 — applicability of the QS-versus-dynamic check

**Status: DRAFT — NOT APPROVED FOR RELEASE.** This draft (rev3) is not issued, not frozen and not approved, and has no force. The owner must review and issue it (§12).

| Item | Value |
|---|---|
| Frozen protocol v1 | `../R4_20261028_preflight/03_R4_protocol_v1.md`, SHA-256 `f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab` (unchanged) |
| Amends | issued amendment 1, `../R4_20261028_campaign/release/03_R4_protocol_v1_amendment_1.md`, SHA-256 `7720fed75bb678e47a229d00aff154e0aa14607c051f4a1163cc9bf67b6abee2` (unchanged; it stays in force for everything this draft does not address) |
| Basis | the owner's ruling on review finding N-A2 (2026-10-28) |
| Revision | **rev3**. It replaces rev2 (archived unchanged in `archive/rev5_verified_20261028_1101/`, SHA-256 in its `ARCHIVE_INDEX.csv`) after the second verification review `review/N-A2_verification2_agent_report_20261028.md` (findings R3-14, R3-15 and a residual note). rev2 replaced rev1 (SHA-256 `a936023af0a772ee2b81c720c76f9c462aba89afe1a8e1de38a286872a8744bf`, archived unchanged in `archive/rev4b_reviewed_20261028_1051/`) after the verification review `review/N-A2_verification_agent_report_20261028.md` (R3-6, R3-7 and R3-10 residuals; new findings R3-12 and R3-13). rev1 had replaced rev0 (SHA-256 `c3e1ddfce7dca7909bb1cd2a6186f4d5044b5dfe81eeed43df0b9fcf215957d4`, archived in `archive/rev4a_reviewed_20261028_0957/`) after the independent review `review/N-A2_review_agent_report_20261028.md` (findings R3-1 to R3-11) |
| Integrity identifier | the SHA-256 of this file is recorded, once this task is complete, in `03_protocol_v1_amendment_2_DRAFT.sha256.txt` and `zz_sha256_manifest_v5.csv`. It identifies the text only; it is not an approval |

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
- The existing §9 rule applies to each arm, unchanged: 100·(e_dyn − e_QS)/e_QS per reference km.
- M0 and M1 must satisfy |deviation| ≤ 1 %. M2 is reported only.

**Pair status:**

| Status | When |
|---|---|
| **FAIL** | an M0/M1 arm with a usable dynamic energy fails. This holds even if the other arm cannot be evaluated (R3-2) |
| **PASS** | both arms pass |
| **REPORTED_ONLY** | M2, when both arms have a usable dynamic energy and a defined ratio. An M2 pair without one is `NOT_EVALUABLE_RUN_MISSING` or `NOT_EVALUABLE_QS_UNDEFINED`, like any eligible pair (AMB-29(b)–(c), R3-12, R3-15); the M2 branch stays reported only |

**Thresholds** are unchanged from protocol v1 §9 and amendment 1.

**Consequence of an applicable failure** (unchanged): the relevant M0/M1 motor branch is `INCONCLUSIVE`.

## 3. `NOT_APPLICABLE_QS_INFEASIBLE`, and what "exact failed feasibility check" means

| Item | Rule |
|---|---|
| When | at least one profile of the pair fails the QS feasibility screen |
| Meaning | the check does not apply to this pair: **neither a pass nor a failure** |
| Recorded per arm | `qs_screen_feasible`, `qs_screen_n_failed`, the QS energy (diagnostic only, `qs_E_J_diagnostic`); `qs_vs_dyn_status = NOT_APPLICABLE_QS_INFEASIBLE`; `qs_vs_dyn_pct` left empty |
| Recorded per condition | `qs_eligible_pair = false`, `qs_ineligible_arms` (B0, B3 or B0,B3), `qs_vs_dyn_pair_status`, `qs_vs_dyn_pair_reason`, and a warning per failing arm |
| The exact failed check (R3-5) | For every failing piece: the piece index, time interval, start and end speed, and **which sub-check of `QSPlant.step` failed**. The sub-checks are drive torque T ≤ t_pos + 1e-9 N·m, battery discriminant ≥ 0, and discharge current i ≤ i_d + 1e-6 A. Their values are recorded at each of the three Gauss nodes, in `conditions/<id>.json` → `qs_screen_failures`, and summarised in `b0/b3_qs_screen_warning`. `diagnosis_consistent` records that the sub-checks reproduce the screen's verdict |
| Never | used as a pass; used to fail; used for a QS saving; a reason to drop or alter a run |

## 4. Dynamic feasibility is independent

- Formal feasibility remains governed by the dynamic run's §8.2 criteria (amendment 1, §5).
- **QS ineligibility never overrides, excuses or replaces a §8.2 result:**
  - a QS-ineligible pair whose runs pass §8.2 keeps its §8.2 status (for example COMPARABLE);
  - a QS-ineligible pair whose run fails §8.2 is classified as amendment 1 prescribes (for example BASELINE_INFEASIBLE_ON_P3), with no paired energy result.
- The pair status of amendment 1 §5 does not use the QS screen.
- The code constant `P3_RULE` keeps amendment 1's wording, "dynamic_8_2_decides; QS screen diagnostic only" (amendment 1's AMB-24 decision, which this draft does not edit). Under this amendment the QS screen has one further role: it decides whether the §9 QS-versus-dynamic check **applies** to a pair (§2). It still never decides feasibility, pair status or crediting (R3-10).

## 5. Motor-branch outcome of the QS-versus-dynamic criterion

**Label rule:**
- `NOT_APPLICABLE_*` pairs never change a branch outcome.
- `NOT_EVALUABLE_*` pairs make an M0/M1 branch INCONCLUSIVE.

| Branch | Outcome |
|---|---|
| **M2** | REPORTED_ONLY; no consequence |
| **M0 / M1: INCONCLUSIVE** | if any applicable check fails (FAIL) |
| | if no eligible comparison passed or exists. The branch **cannot pass by vacuity** |
| | if any pair is `NOT_EVALUABLE_*` (§6, AMB-29 (b)–(d)) |
| **M0 / M1: PASS** | only if every applicable check passes and at least one does |

- **No minimum eligible-count threshold** is introduced beyond "at least one".
- **Scope:** every planned pair of the motor across all sets (§6, AMB-30).

## 6. Ambiguities found while implementing the ruling (documented; the owner confirms or replaces each)

The handling below is what the implementation does. It is stated so that the owner can decide; it is not presented as settled.

| ID | Question | Handling in this draft | Direction |
|---|---|---|---|
| AMB-29(a) | A pair whose B0 or B3 profile **does not exist** (baseline task unavailable, or S-eco unavailable or invalid) has nothing to screen | `NOT_APPLICABLE_PROFILE_UNAVAILABLE`; no effect on the branch | **Disclosure:** the amendment-1 implementation computed a B0-only check for such a pair, which could have made a branch INCONCLUSIVE. Under the ruling's "both profiles" wording that check is no longer computed. This removes one way a branch could become INCONCLUSIVE, so it can be the more favourable reading. Owner to confirm |
| AMB-29(b) | A QS-eligible pair where an arm has **no finite dynamic energy** (an exception, or a non-finite simulator energy) | `NOT_EVALUABLE_RUN_MISSING`; M0/M1 branch INCONCLUSIVE. The same label applies to M2, whose branch stays reported only (R3-12) | conservative |
| AMB-29(c) | A QS-eligible pair whose QS energy is ≤ 0, so the ratio is undefined | `NOT_EVALUABLE_QS_UNDEFINED`; M0/M1 branch INCONCLUSIVE. The same label applies to M2, whose branch stays reported only (R3-15) | conservative |
| AMB-29(d) | An exception before or during the pair evaluation, so eligibility is unknown | `NOT_EVALUABLE_CONDITION_ERROR`, `qs_eligible_pair` unknown; M0/M1 branch INCONCLUSIVE; M2 stays reported only | conservative |
| AMB-30 | Scope of "the motor branch". §9 says "every B0 and B3 profile"; amendment 1 is itself ambiguous (its §10 says "every B0 and B3 run", its §10 preamble "QS-versus-dynamic on S2 profiles") | every planned pair of the motor across all sets (NOM, P3, INS, CNV, SEN), with per-set counts in `qs_dynamic_accounting.csv` | Mostly conservative, because more pairs can fail. But a pass from a non-decisive set can supply the "at least one" that prevents vacuity. Owner to confirm the scope |
| AMB-31 (R3-4) | Which dynamic energy is "usable" for an eligible pair | any executed run with a finite simulator energy, **whatever its §8.2 verdict or recomputation status** (the literal ruling: "apply the existing §9 rule" to an eligible pair). PASS pairs that are also dynamic-valid are reported separately: `n_PASS_dynamic_valid` and `qs_check_pass_dynamic_valid` | **Can be favourable:** a branch's only PASS could come from a dynamically invalid pair. The stricter alternative would require §8.2 validity for a PASS to count. Owner to choose |

## 7. Required denominators and reporting

Per motor branch and set, and per motor overall (`qs_dynamic_accounting.csv`):

| Category | Columns |
|---|---|
| Planned pairs | `planned_pairs` |
| Eligibility classes, which add up to `planned_pairs` | `qs_eligible_pairs`, `qs_ineligible_pairs`, `not_applicable_profile_unavailable`, `qs_eligibility_unknown` |
| QS-ineligible pairs by arm | `qs_ineligible_b0_only`, `qs_ineligible_b3_only`, `qs_ineligible_both` |
| Check-status classes, which also add up to `planned_pairs` | `qs_check_pass`, `qs_check_fail`, `qs_check_reported_only`, `qs_ineligible_pairs`, `not_applicable_profile_unavailable`, `not_evaluable_run_missing`, `not_evaluable_qs_undefined`, `not_evaluable_condition_error` |
| Passing pairs that are also dynamic-valid | `qs_check_pass_dynamic_valid` |
| Pairs whose two dynamic runs pass §8.2 | `dynamic_valid_pairs` |
| Valid energy-comparison pairs (status COMPARABLE after the separate recomputation) | `valid_energy_comparison_pairs` |

- Branch outcomes go to `qs_dynamic_branch_outcomes.csv` and `manifest.json`.
- No run record is deleted, dropped or altered because a check is not applicable. An exception in the pair evaluation is recorded without relabelling the executed runs (R3-9).
- An exception while computing the denominators (N-A2 or D5) or a branch outcome is recorded in `errors.csv`. The affected M0/M1 branch is written INCONCLUSIVE (M2 REPORTED_ONLY), never PASS, and every remaining output file is still written (R3-13; protocol §10.4).
- No energy comparison is credited for an invalid or incomplete pair (amendment 1, §5).

## 8. Effect on the planned 170-run schedule

None. These are unchanged:
- the 170 official runs;
- their IDs, sets, plants and profiles;
- the gains: the nominal P1 gain for every SEN draw (AMB-14);
- the tolerances and numerics.

The schedule's SHA-256 is unchanged. No run is added, removed or made conditional. S2 is not used for tuning.

## 9. Location rule for campaign mode (R3-1)

- Campaign mode runs only when the running code's directory **is**, by resolved path, `verification/research_recovery_20261028/R4_20261028_campaign/`.
- A same-named copy anywhere else is refused (test `test_r3_1_a_same_named_nested_copy_cannot_enter_campaign_mode`).
- This restores amendment 1 §7's statement that `run_campaign` refuses any other directory, which the path change SI-1 (§10) would otherwise have weakened.

## 10. All changes in this revision of the code (complete list)

| Change | Ruling? | Effect |
|---|---|---|
| Pair-level QS-vs-dynamic applicability, its labels, branch outcome and denominators (`checks.py`; `campaign.run_condition`, `execute_schedule`) | **N-A2** | as §§2–7 |
| Recording of the failed `QSPlant.step` sub-check per Gauss node (`checks.qs_piece_diagnosis`, `qs_screen`) | N-A2 ("exact failed feasibility check") | diagnostic only |
| The per-arm QS energy column renamed `qs_E_J` → `qs_E_J_diagnostic` | N-A2 | output naming |
| `NUMERICAL_CHECKS` row 7 text (applicability and the no-vacuity rule) | N-A2 | wording; names and order unchanged |
| Amendment 2 read and enforced as a second issued amendment (`IMPLEMENTED_2`, `read_amendment(path, implemented, open_parameters)`, `ISSUED_AMENDMENT_2`, `APPROVAL_RECORD_2`, preconditions) | separate issue **SI-2**, needed to issue this amendment without editing amendment 1 | fail-closed |
| `read_amendment` compares JSON round-tripped values (R3-11) | SI-2 | no effect for the current values (no tuples, no non-string keys) |
| Campaign authorisation must also carry `amendment_2_sha256`; its scope reads "…of protocol v1 amendments 1 and 2" (R3-8) | SI-2 | stricter |
| `REVIEW_STATUS` → `config/code_review_status_v4.json`; `CAMPAIGN_CONFIG` → `config/campaign_config_v6_DRAFT.json`. The intermediate `campaign_config_v3/v4/v5_DRAFT.json` are kept unchanged but superseded, because `IMPLEMENTED_2` is part of the configuration (R3-14) | versioning | — |
| **SI-1** location-independent path resolution (`frozen.py`, `campaign.py`), so a release attempt can be tested from a versioned sub-directory | separate issue | identical paths from the pilot and the campaign root (test `test_si1_paths_are_location_independent`) |
| Campaign-mode location check by resolved path (§9, R3-1) | follows from SI-1 | stricter |
| `config_content` writes its path entries as fixed strings instead of computing them relative to the running directory | follows from SI-1 | the configuration text is the same from any location; `config/campaign_config_v6_DRAFT.json` regenerates identically |
| A failure to rebuild the campaign configuration in `preconditions` becomes a blocker instead of an exception | robustness | fail-closed |
| An exception in the pair-level QS-vs-dynamic evaluation is caught, recorded in `errors.csv`, and labels the pair `NOT_EVALUABLE_CONDITION_ERROR` (R3-9) | N-A2 (AMB-29(d)) | fail-closed; executed runs keep their records |
| An unknown pair status makes `branch_qs_dynamic_outcome` raise (R3-10) | N-A2 | fail-closed |
| An M2 pair without a usable dynamic energy is `NOT_EVALUABLE_RUN_MISSING`, and one with an undefined ratio `NOT_EVALUABLE_QS_UNDEFINED`, instead of `REPORTED_ONLY` (R3-12, R3-15) | N-A2 (AMB-29(b)–(c)) | accounting only; the M2 branch stays REPORTED_ONLY |
| An exception in the N-A2 denominators, a branch outcome or the D5 status denominator is recorded in `errors.csv`, never yields a pass, and the remaining outputs are still written (R3-13 and its residual note) | protocol §10.4 | fail-closed |

No other behaviour changes were made. The file-by-file comparison with the pre-change code (`archive/rev3_20261028_0928/`) is `logs/zz_code_changes_rev3_to_rev6.csv`. Amendment 1's implemented decision set and the 170-run schedule are byte-identical to the released amendment-1 package.

## 11. Blockers retained

The campaign remains **BLOCKED**. Campaign mode is refused until all of these hold:

1. Amendment 2 is reviewed and approved by the owner and issued (§12).
2. The new release attempt passes all mandatory tests and independent reviews.
3. The final release manifest and protocol hashes are verified.
4. All release criteria are met. This includes promoting the approved attempt to the campaign root (§9) with its own protocol §10.1 gate record.
5. The owner explicitly authorises campaign execution in a separate action: `release/campaign_authorization.json`. It must have `scope` = "execute the 170-run H3 campaign of protocol v1 amendments 1 and 2" and carry `amendment_sha256` (amendment 1), **`amendment_2_sha256`** (this amendment as issued) and `pre_run_hashes_sha256`.

## 12. To issue (owner)

1. Review this draft. Decide AMB-29 (a)–(d), AMB-30 and AMB-31 (§6). Review the new release attempt's report.
2. Copy the reviewed text to `R4_20261028_campaign/release/03_R4_protocol_v1_amendment_2.md`, set `"status": "APPROVED"` in the block, and record its SHA-256.
3. Write `R4_20261028_campaign/release/amendment_2_approval.json` with `approved_by`, `date` and `amendment_sha256`.

## 13. Machine-readable block

`code/r4h3/campaign.py` (`IMPLEMENTED_2`) reads this block. Every value must equal what the code implements: a difference or an unknown key is an error, never an override.

<!-- r4h3-amendment-block -->
```json
{
 "amendment": "R4 protocol v1 amendment 2 (N-A2), draft rev3",
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
 "AMB_29_profile_unavailable": "NOT_APPLICABLE_PROFILE_UNAVAILABLE (no effect on the branch outcome)",
 "AMB_29_eligible_run_missing": "NOT_EVALUABLE_RUN_MISSING (M0/M1 branch INCONCLUSIVE; M2 stays reported only)",
 "AMB_29_qs_energy_undefined": "NOT_EVALUABLE_QS_UNDEFINED (M0/M1 branch INCONCLUSIVE; M2 stays reported only)",
 "AMB_29_condition_error": "NOT_EVALUABLE_CONDITION_ERROR (eligibility unknown; M0/M1 branch INCONCLUSIVE; M2 stays reported only)",
 "AMB_30_branch_scope": "every planned pair of the motor branch across all sets (literal protocol 9 reading)",
 "AMB_31_usable_dynamic_energy": "an executed run with a finite simulator energy, whatever its protocol 8.2 verdict (literal reading); PASS pairs that are also dynamic-valid are reported separately",
 "pair_statuses": [
  "PASS",
  "FAIL",
  "REPORTED_ONLY",
  "NOT_APPLICABLE_QS_INFEASIBLE",
  "NOT_APPLICABLE_PROFILE_UNAVAILABLE",
  "NOT_EVALUABLE_RUN_MISSING",
  "NOT_EVALUABLE_QS_UNDEFINED",
  "NOT_EVALUABLE_CONDITION_ERROR"
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
