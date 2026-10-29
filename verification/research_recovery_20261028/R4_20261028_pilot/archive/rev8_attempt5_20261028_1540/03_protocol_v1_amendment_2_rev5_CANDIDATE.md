# Amendment 2 to R4 protocol v1 (H3): owner rulings N-A2, AMB-29(a)–(d), AMB-30, AMB-31 and AMB-32 — the QS-versus-dynamic check, missing and invalid evidence, and the nominal held-out requirement

**Status: CANDIDATE rev5 — DRAFT — NOT APPROVED FOR RELEASE.** This candidate is not issued, frozen or approved, and has no force. Every owner decision it needs has been made (§1). The interpretation points in §9 are stated for the owner to confirm or replace when issuing (§15).

| Item | Value |
|---|---|
| Frozen protocol v1 | `../R4_20261028_preflight/03_R4_protocol_v1.md`, SHA-256 `f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab` (unchanged) |
| Amends | issued amendment 1, `../R4_20261028_campaign/release/03_R4_protocol_v1_amendment_1.md`, SHA-256 `7720fed75bb678e47a229d00aff154e0aa14607c051f4a1163cc9bf67b6abee2` (unchanged; it stays in force for everything this candidate does not address) |
| Basis | the owner's rulings of 2026-10-28: N-A2; AMB-29(a) and AMB-31; AMB-29(b), AMB-29(c), AMB-29(d), AMB-30 and AMB-32 |
| Supersedes (as the text proposed for issue) | candidate rev4, `03_protocol_v1_amendment_2_rev4_CANDIDATE.md`, SHA-256 `c726560d1e87036cbd94fe58724cafdc1e4746647f6cfacbb320f3e14ed143ab`, kept unchanged. Earlier drafts, all kept unchanged: rev3 `03_protocol_v1_amendment_2_DRAFT.md` `fdaf193de510488733f0e0899d50def86cbeafabdbecdd3bc7a144099b6f492c`; rev2 `e0dc68827c57704b49b13886c455b281e4e3c10ce377a1f174742ff5529247cc`; rev1 `a936023af0a772ee2b81c720c76f9c462aba89afe1a8e1de38a286872a8744bf`; rev0 `c3e1ddfce7dca7909bb1cd2a6186f4d5044b5dfe81eeed43df0b9fcf215957d4` |
| Decision record | `15_remaining_owner_decisions.md` (options and recommendations; unchanged) and `17_owner_rulings_attempt5_report.md` (the rulings' text and where each is implemented) |
| Integrity identifier | the SHA-256 of this file is recorded in `03_protocol_v1_amendment_2_rev5_CANDIDATE.sha256.txt`. It identifies the text only; it is not an approval |

All thresholds of protocol v1 and amendment 1 are unchanged: QS-versus-dynamic ≤ 1 % per reference km for M0 and M1, M2 reported only; planner grid < 0.2 pp; optimality 0.2 pp; time step < 0.01 pp; the §8.2 criteria and the recomputation tolerances of amendment 1. Nothing here is tuned on S2.

## 1. Owner rulings this candidate implements (binding)

### 1.1 N-A2 (unchanged from rev3)
The protocol §9 QS-versus-dynamic consistency check applies only to an evaluation pair for which **both** the baseline (B0) profile and the eco (B3) profile pass the prescribed quasi-static feasibility screen under the same applicable conditions. If either profile fails the screen, the pair's check is `NOT_APPLICABLE_QS_INFEASIBLE`: neither a pass nor a failure. The QS diagnostics and the exact failed feasibility check are kept. QS energy computed from torque beyond the QS model's admissible limits is never used to pass or fail the check, and no QS saving is computed for that pair for acceptance. The profile, plant, LQR gain, limits and task are never modified.

### 1.2 AMB-29(a): missing profile (unchanged from rev4)
- A profile-generation failure or planner infeasibility **remains an explicit outcome**: `PROFILE_UNAVAILABLE` or `BASELINE_UNAVAILABLE` (amendment 1).
- It counts in the planned-run, feasibility and verdict denominators (§7), is never removed, and is never relabelled `NOT_APPLICABLE` for the experiment outcome.
- It never yields a paired energy comparison.
- Only the pair's QS-versus-dynamic **check** is `NOT_APPLICABLE_PROFILE_UNAVAILABLE`, because its applicability condition is objectively unmet. An inapplicable check is not a pass.

### 1.3 AMB-31: energy from a run failing §8.2 (unchanged from rev4, made precise in §4)
Energy from a run that fails any mandatory §8.2 criterion, or that is not confirmed by the recomputation, is not a valid confirmatory result. It is kept, labelled diagnostic only, and never credited to the primary paired endpoint. A valid paired comparison needs both arms to complete the task and satisfy every mandatory validity condition. A constraint failure is never reinterpreted as a harmless diagnostic deviation.

### 1.4 AMB-29(b): missing usable energy or invalid arm
Owner's words: "Approve: `NOT_EVALUABLE` → `INCONCLUSIVE`. A pair cannot contribute to the confirmatory paired energy endpoint unless both arms are valid and confirmed by the separate recomputation process. Retain all available energy traces for diagnostic purposes. Missing or invalid energy must not cause the pair to disappear from its planned-run denominator."
- A QS-eligible pair with an arm without a finite dynamic energy is `NOT_EVALUABLE_RUN_MISSING`; with an arm whose energy is invalid or unconfirmed (§4) it is `NOT_EVALUABLE_RUN_INVALID`. Either makes the M0/M1 branch INCONCLUSIVE for this criterion. For M2 the label is recorded and the branch stays reported only.
- The paired endpoint uses a condition only if its final status is `COMPARABLE` (§5).
- Every trace and raw energy is kept. The pair stays in every denominator (§7).

### 1.5 AMB-29(c): QS energy ≤ 0
Owner's words: "Approve: `QS_COMPARISON_NOT_EVALUABLE` → `INCONCLUSIVE` for the applicable QS-versus-dynamic criterion. Retain the raw values and identify the exact non-positive term. Do not calculate a relative saving percentage using a non-positive denominator. This ruling applies to the affected QS comparison; it must not automatically invalidate a separate dynamic energy result that independently satisfies every applicable validity condition. Continue to enforce all dynamic §8.2 requirements. Do not invent a replacement denominator, epsilon adjustment, absolute-value transformation or substitute threshold."
- The label is `NOT_EVALUABLE_QS_UNDEFINED`, a member of the `NOT_EVALUABLE` class (the owner's `QS_COMPARISON_NOT_EVALUABLE`; §2, §9 I-5). It makes the M0/M1 branch INCONCLUSIVE for this criterion.
- No percentage is computed. The raw values (E_QS in J, the dynamic energy in Wh, d_ref, e_QS and e_dyn per reference km) and the exact non-positive term are recorded per arm (`qs_vs_dyn_non_positive_term`) and per pair (`qs_vs_dyn_non_positive_terms`).
- The runs' dynamic result is unaffected: the condition status comes from §8.2 and the recomputation alone (§3). Every §8.2 requirement still applies.
- No replacement denominator, epsilon, absolute value or substitute threshold is used. The same rule is applied to every other relative percentage in the H3 code (§4.2; §9 I-3).

### 1.6 AMB-29(d): evaluation error
Owner's words: "Approve: `NOT_EVALUABLE` → `INCONCLUSIVE`. Preserve the error, logs, traces and run ID. No silent retry, automatic replacement, or new official run may be substituted for a failed evaluation. Any future rerun must follow the existing protocol and an explicitly authorized procedure with a distinct run ID."
- An exception before or during a pair's QS-versus-dynamic evaluation labels the pair `NOT_EVALUABLE_CONDITION_ERROR` (eligibility unknown). An exception inside one run, including its evaluation, makes the condition `ERROR` and leaves the pair `NOT_EVALUABLE_RUN_MISSING` (§9 I-6). Either makes the M0/M1 branch INCONCLUSIVE for this criterion.
- The traceback goes to `errors.csv` with the run ID, or for a pair- or condition-level error with both run IDs (`run_ids`). The trace written before the failure, the condition record and the logs are kept.
- No run is retried, replaced or substituted. Every scheduled condition and run has exactly one record (`record_invariant`, §7.5). A rerun only under the protocol and an explicitly authorised procedure with a distinct run ID.

### 1.7 AMB-30: required sets for QS-versus-dynamic conclusions
Owner's words: "Approve the strict interpretation: 1. A required PASS must exist for the nominal held-out S2 set. 2. A pass on in-sample S1 cannot substitute for a missing or failed nominal S2 check. 3. Failures of applicable QS-versus-dynamic checks in any preregistered set count against the branch, according to the existing §9 consequence. 4. Do not average across sets to hide a failure. 5. A missing nominal S2 cell required by protocol cannot produce PASS. 6. If an applicable required check fails, or the mandatory held-out evidence is missing, classify the branch as INCONCLUSIVE where required by the existing protocol. 7. Do not modify any numerical threshold or reuse S2 to tune the planner."
The rule is in §6.

### 1.8 AMB-32: missing nominal cell
Owner's words: "A required nominal cell that is missing, invalid or not evaluable cannot be classified as NOT SUPPORTED merely because a result was absent. Use INCONCLUSIVE and record the missing evidence and its reason. Do not infer a negative scientific finding from missing data."
The rule is in §8.

## 2. Status vocabulary of the QS-versus-dynamic pair check

| Term | Definition |
|---|---|
| **Pair** | the B0 and B3 runs of one scheduled condition: set, cycle, motor branch, limit set, evaluated plant state and, for SEN, draw |
| **QS feasibility screen** | every constant-acceleration piece of the tracked profile passes `QSPlant.step` on the condition's **evaluated** plant, with its motor branch and limit set |
| **QS-eligible pair** | both profiles exist and both pass the screen |
| **Valid arm** (AMB-31) | an executed run with a finite simulator energy that passes every §8.2 criterion and its in-process recomputation, and is confirmed by the separate recomputation (§4) |

There are four classes, plus `REPORTED_ONLY` for M2. Every pair has exactly one status.

| Class | Status | When | M0/M1 branch consequence |
|---|---|---|---|
| PASS | `PASS` | eligible; both arms valid and within 1 % per reference km | counts as a pass; the required PASS must come from NOM (§6) |
| FAIL | `FAIL` | eligible; a **valid** arm exceeds 1 % (even if the other arm is not valid) | INCONCLUSIVE (protocol §9), in any set |
| — | `REPORTED_ONLY` | M2 only: eligible, both arms valid, ratio defined | none (M2 reported only); for M0/M1 an inconsistency that blocks PASS |
| NOT_APPLICABLE | `NOT_APPLICABLE_QS_INFEASIBLE` | a profile fails the QS screen (N-A2) | none; neither pass nor fail; not missing evidence |
| NOT_APPLICABLE | `NOT_APPLICABLE_PROFILE_UNAVAILABLE` | a profile does not exist (AMB-29(a)); the condition keeps its explicit failure status | none outside the nominal cells; in a required nominal cell it is missing held-out evidence (§6; §9 I-2) |
| NOT_EVALUABLE | `NOT_EVALUABLE_RUN_MISSING` | eligible; an arm has no finite energy (an exception or a non-finite run) | INCONCLUSIVE (AMB-29(b)) |
| NOT_EVALUABLE | `NOT_EVALUABLE_RUN_INVALID` | eligible; an arm's energy is finite but its run fails §8.2 or a recomputation | INCONCLUSIVE (AMB-29(b), AMB-31) |
| NOT_EVALUABLE | `NOT_EVALUABLE_QS_UNDEFINED` | eligible; QS energy per reference km ≤ 0 | INCONCLUSIVE (AMB-29(c)) |
| NOT_EVALUABLE | `NOT_EVALUABLE_CONDITION_ERROR` | an exception before or during the pair evaluation; eligibility unknown | INCONCLUSIVE (AMB-29(d)) |

For M2 every label is used the same way and the M2 branch stays reported only. An unknown status raises an error and is never counted.

**Order with the separate recomputation:** the pair status is set in process. After the separate recomputation, a PASS, FAIL or REPORTED_ONLY that used the energy of an arm the separate recomputation does not confirm becomes `NOT_EVALUABLE_RUN_INVALID`; the in-process value is kept in `qs_vs_dyn_pair_status_in_process`. A FAIL of a confirmed arm stays a FAIL.

## 3. A QS-only status is not a run status

| Situation | QS-versus-dynamic check | Condition status and energy role |
|---|---|---|
| Both runs pass §8.2 and both recomputations; a profile fails the QS screen | `NOT_APPLICABLE_QS_INFEASIBLE` | `COMPARABLE`; energy confirmatory |
| Both runs valid; QS energy ≤ 0 | `NOT_EVALUABLE_QS_UNDEFINED` | `COMPARABLE`; energy confirmatory (AMB-29(c): not invalidated) |
| Both runs valid; the pair's QS evaluation raised | `NOT_EVALUABLE_CONDITION_ERROR` | `COMPARABLE`; energy confirmatory |
| A run fails a §8.2 criterion | `NOT_EVALUABLE_RUN_INVALID` if eligible | `B0_INVALID_EXCLUDED`, `INVALID_COMPARISON`, or on P3 `BASELINE_INFEASIBLE_ON_P3` / `ECO_INFEASIBLE_ON_P3`; that run's energy `DIAGNOSTIC_ONLY_RUN_INVALID` |
| A run is not confirmed by a recomputation | `NOT_EVALUABLE_RUN_INVALID` if eligible | `RECOMPUTATION_DISAGREEMENT`; `DIAGNOSTIC_ONLY_RECOMPUTATION_NOT_CONFIRMED` |
| A profile is missing | `NOT_APPLICABLE_PROFILE_UNAVAILABLE` | `PROFILE_UNAVAILABLE` / `BASELINE_UNAVAILABLE`; the existing arm `VALID_RUN_NOT_IN_PAIRED_ENDPOINT` or a `DIAGNOSTIC_ONLY_*` role; the missing arm `NO_ENERGY_NOT_EXECUTED` |

The condition status is decided by amendment 1 §5 (profile and baseline availability, errors, §8.2 on each arm, the recomputation) and never reads the QS screen or the QS check. A QS status can make the §9 QS-versus-dynamic **criterion** INCONCLUSIVE; it never makes a run invalid and never excuses, overrides or replaces a §8.2 result.

## 4. Energy roles and non-positive denominators

### 4.1 Energy roles (AMB-31, AMB-29(b))
Every planned run has exactly one role in `energy_roles.csv`. No energy value is copied there; raw energies stay in `runs.csv`, `evaluation.csv` and the traces.

| Role | When | Use |
|---|---|---|
| `CONFIRMATORY_PAIRED_ENDPOINT` | the condition's final status is `COMPARABLE` | the only energy usable for the primary paired endpoint (§7.1, §8.1) |
| `VALID_RUN_NOT_IN_PAIRED_ENDPOINT` | the run is valid and confirmed, but its condition is not `COMPARABLE` | reported; never in the paired endpoint |
| `DIAGNOSTIC_ONLY_RUN_INVALID` | the run fails a §8.2 criterion (the failed criteria are recorded) | diagnostics only |
| `DIAGNOSTIC_ONLY_RECOMPUTATION_NOT_CONFIRMED` | the run passes §8.2 but its in-process or separate recomputation does not confirm it | diagnostics only |
| `NO_ENERGY_NOT_EXECUTED` | the run was not executed (missing profile, condition-level error) or raised an exception | none; counted |

The QS-versus-dynamic check uses an arm's energy under the same rule: only if the run passes §8.2 and its in-process recomputation, and, after the fold, the separate recomputation (§9 I-4). An invalid arm's QS-versus-dynamic value is kept in `qs_vs_dyn_pct_diagnostic_invalid_run` only.

### 4.2 No percentage with a non-positive denominator (AMB-29(c))
No relative percentage is computed with a denominator that is ≤ 0 or not finite. The value is recorded as not evaluable, with the exact term and the raw values:

| Quantity | Denominator | When ≤ 0 |
|---|---|---|
| QS vs dynamic, 100·(e_dyn − e_QS)/e_QS | e_QS per reference km (or d_ref) | `diff_pct` empty; pair `NOT_EVALUABLE_QS_UNDEFINED` |
| paired ΔE_rel, 100·(e_B3 − e_B0)/e_B0 (`paired_delta`) | the B0 energy per reference km | `dE_rel_pct` None, `dE_rel_status` `NOT_EVALUABLE_DENOMINATOR_NOT_POSITIVE`; ΔE_abs still reported |
| planner S_found, S_max (protocol §5.4) and grid ΔS_found (§9) | E(v_b), the QS baseline energy | values None; `status` `NOT_EVALUABLE_DENOMINATOR_NOT_POSITIVE`; the grid check is not passed |

The first row is the ruling's direct object. The other rows apply its rule to the code's other relative percentages (§9 I-3).

## 5. Paired endpoint
A paired energy comparison exists only for a condition whose final status is `COMPARABLE`: both arms complete the task, pass every §8.2 criterion and both recomputations. ΔE_abs and ΔE_rel are reported together, with trip time, and only for such conditions. A QS-only status (§3) does not remove a `COMPARABLE` condition from the endpoint.

## 6. Motor-branch outcome of the QS-versus-dynamic criterion (AMB-30)

M2 is reported only. An M0 or M1 branch is **INCONCLUSIVE**, with every applicable reason recorded, if any of these holds:
1. an applicable check **FAILs** in any preregistered set: NOM, P3, INS (S1, in-sample), CNV or SEN (items 3, 6);
2. a pair in any set is **NOT_EVALUABLE** (AMB-29(b)–(d));
3. a **required nominal cell** lacks evidence: the motor's NOM pair for L-R1 or for L-EVE is absent from the record, appears more than once, has no profile (`NOT_APPLICABLE_PROFILE_UNAVAILABLE`), is not evaluable, or has any status other than PASS, FAIL or `NOT_APPLICABLE_QS_INFEASIBLE` (items 5, 6);
4. **no NOM pair passes**. A PASS in any other set, INS included, never substitutes (items 1, 2). This also means no pass by vacuity;
5. a planned pair of the motor is missing from the record;
6. a pair is labelled `REPORTED_ONLY`, which applies to M2 only.

Otherwise the branch **PASSes**. Under this rule a nominal cell whose check is `NOT_APPLICABLE_QS_INFEASIBLE` is neither a pass nor missing evidence, so one NOM PASS with the other NOM cell QS-infeasible can pass (§9 I-1).

Failures and not-evaluable pairs are **counted per set and never averaged** (item 4). `qs_dynamic_branch_outcomes.csv` reports, per motor: the count of every status; `n_PASS_nominal` and `n_PASS_other_sets`; `nominal_L-R1` and `nominal_L-EVE`; `nominal_evidence_missing`; `fail_by_set`, `not_evaluable_by_set`, `pass_by_set` and `not_applicable_by_set`; `planned_pairs_missing_from_record`; the outcome and its reasons. A row is written for every motor branch, including one with no pair in the record. No threshold is changed and S2 is not used to tune the planner (item 7).

## 7. Denominator and exclusion reporting
Nothing is dropped from a denominator. Every exclusion is reported with its reason.
1. **Feasibility** (`feasibility_accounting.csv`; per motor and set, per motor, overall): planned conditions and runs; runs executed and not executed (and of those, profile failures); runs §8.2-valid and invalid; profile-failure conditions; conditions eligible for and excluded from the paired endpoint; one count per condition status and per energy role. The status counts add up to the planned conditions and the role counts to the planned runs.
2. **QS-versus-dynamic** (`qs_dynamic_accounting.csv`; per motor and set, per motor): planned pairs; eligible, QS-ineligible (B0 only, B3 only, both), profile-unavailable and eligibility-unknown pairs, which add up to the planned pairs; one count per pair status, which also add up; pairs passing on dynamic-valid arms; dynamic-valid and `COMPARABLE` pairs.
3. **Branch outcomes** (`qs_dynamic_branch_outcomes.csv`, §6).
4. **Energy roles** (`energy_roles.csv`, §4.1): one row per planned run with its §8.2 flags, failed criteria and recomputation result.
5. **Record invariant** (`manifest.json` → `record_invariant`): every scheduled condition and run has exactly one record, in schedule order. A violation is recorded in `errors.csv` and the manifest; it would be a defect, never a pass.
6. **Errors** (`errors.csv`): every exception with its traceback and its run ID or run IDs.
7. **Verdict eligibility** (`h3_verdict_eligibility.json`, §8).

## 8. Overall H3 verdict (protocol §8.1; AMB-32)
The §8.1 denominators are fixed and never reduced: 6 nominal S2 P1 cells (M0, M1, M2 × L-R1, L-EVE) and 32 sensitivity draws for each of M0 and M1.
- **SUPPORTED** needs a `COMPARABLE` pair in all six nominal cells, at least 29 of 32 sensitivity draws for M0 and for M1 separately, and every §9 check passing, together with the energy conditions of §8.1.
- **NOT SUPPORTED** needs a `COMPARABLE` pair in all six nominal cells, ΔE_rel > −1.0 % in every motor branch for the nominal S2 P1 runs, and all checks passing (AMB-32).
- Otherwise **INCONCLUSIVE**. A nominal cell that is missing, invalid or not evaluable makes the verdict INCONCLUSIVE, never NOT SUPPORTED. No negative finding is inferred from missing data, and no verdict is reached by omission. A `COMPARABLE` nominal cell whose ΔE_rel is not evaluable (§4.2) satisfies neither side of the −1 % rule, so it also leads to INCONCLUSIVE (§9 I-3).

`h3_verdict_eligibility.json` records, without reading any energy value, which verdicts remain possible from the condition statuses and the branch outcomes. For each nominal cell without a comparable pair it records the cell, its status and its reason (`nominal_missing_evidence`). It computes no energy difference. The other §9 checks can only remove possibilities.

## 9. Interpretation points recorded for the owner (not settled by the rulings' words)

Each point is the fail-closed reading the code implements. Approving this text confirms it; a different choice needs a code change, a review and a new release attempt.

| ID | Point | Reading implemented | Alternative |
|---|---|---|---|
| I-1 | "A required PASS must exist for the nominal held-out S2 set" | at least one PASS among the motor's two NOM cells, with both cells present with evidence. A QS-infeasible NOM cell is not missing evidence (N-A2: neither pass nor fail) | every NOM cell must PASS; a QS-infeasible NOM cell then blocks PASS |
| I-2 | Is a NOM cell without a profile "missing held-out evidence"? | yes: it blocks PASS. Outside NOM, `NOT_APPLICABLE_PROFILE_UNAVAILABLE` has no effect on the QS criterion (the condition still counts as a failure in §7) | no effect anywhere (the rev3/rev4 label rule) |
| I-3 | Scope of "no relative saving percentage with a non-positive denominator" | every relative percentage in the H3 code (§4.2), not only the QS ratio; an undefined ΔE_rel in a nominal cell leads to INCONCLUSIVE | the QS ratio only |
| I-4 | Which recomputation an arm must pass to be used by the QS check | both the in-process and the separate one, as for its energy role (rev4 text named the separate one; the code used the in-process one only through the condition status) | the separate one only |
| I-5 | The owner's term `QS_COMPARISON_NOT_EVALUABLE` | the `NOT_EVALUABLE` class; the label for QS energy ≤ 0 stays `NOT_EVALUABLE_QS_UNDEFINED` (record vocabulary unchanged since rev3) | rename the label |
| I-6 | An exception inside one run's evaluation | the condition is `ERROR` and the pair `NOT_EVALUABLE_RUN_MISSING` (same consequence as `NOT_EVALUABLE_CONDITION_ERROR`) | label it `NOT_EVALUABLE_CONDITION_ERROR` |

## 10. Effect on the planned 170-run schedule
None. The 170 official runs, their IDs, sets, plants, profiles, gains (nominal P1 gain for every SEN draw, AMB-14), tolerances and numerics are unchanged, and so is the schedule's SHA-256. No run is added, removed, retried, replaced or made conditional. Smoke-test runs stay excluded (D4). S2 stays held out and is not used for tuning.

## 11. Location rule for campaign mode
Unchanged from rev3 §9: campaign mode runs only when the running code's directory is, by resolved path, `R4_20261028_campaign/`.

## 12. Changes since rev4 (complete list)

| Change | Basis | Effect |
|---|---|---|
| `checks.branch_qs_dynamic_outcome`: AMB-30 rule (§6); optional `planned_condition_ids`; per-set and nominal-cell columns; REPORTED_ONLY for M0/M1 blocks PASS | AMB-30 ruling | stricter |
| `checks.h3_verdict_eligibility`: `nominal_missing_evidence`; reasons name AMB-32 | AMB-32 ruling | reporting; rule unchanged from the rev4 proposal |
| `checks.non_positive_term`; `qs_vs_dynamic` returns no percentage (None) and the raw values and the term when e_QS ≤ 0; `pair_qs_dynamic` names the term; `paired_delta`, `scenario_totals`, `grid_convergence` refuse a percentage with a denominator ≤ 0 | AMB-29(c) ruling | stricter |
| `checks.PAIR_STATUS_CLASSES`, `NOMINAL_SET`, `NOMINAL_LIMITS` | vocabulary (§2) | definitions |
| `campaign.run_condition`: the QS check uses an arm only if it passes §8.2 and its in-process recomputation; per-arm `qs_vs_dyn_e_qs_Wh_per_km`, `qs_vs_dyn_e_dyn_Wh_per_km`, `qs_vs_dyn_non_positive_term`; condition field `qs_vs_dyn_non_positive_terms`; a pair-level error row carries `run_ids` | AMB-31, AMB-29(c), AMB-29(d) rulings | stricter; reporting |
| `campaign.execute_schedule`: `record_invariant`; condition-level error rows carry `run_ids`; a branch outcome for every motor, with the planned pairs | AMB-29(a), (b), (d), AMB-30 rulings | stricter; reporting |
| `NUMERICAL_CHECKS` row 7 text names the AMB-29 and AMB-30 rules | rulings | wording; names and order unchanged |
| Machine block: the `AMB_29_*`, `AMB_30_branch_scope`, `AMB_31_*` and `AMB_32_*` values state the owner rulings; new keys `pair_status_classes`, `non_positive_denominator_rule`, `record_invariant` | rulings | — |
| `preconditions`: the review-pending message also names the owner's acceptance of the review's closure | fail-closed | wording |
| `DRAFT_AMENDMENT_2` → this candidate; `CAMPAIGN_CONFIG` → `campaign_config_v8_DRAFT.json`; `REVIEW_STATUS` → `code_review_status_v6.json` (earlier versions kept unchanged) | versioning | — |
| Tests: new `tests/test_owner_rulings_v8.py`. Updated fixtures or assertions in `test_amendment2.py` (`test_case11…`, `test_r3_3…`) and `test_owner_rulings_v7.py` (`test_rev3_draft…`), each because it encoded the superseded AMB-30 reading or the rev4 file name | rulings; versioning | — |

The file-level comparison with the rev4 state (`archive/rev7_attempt4_20261028_1405/`) is `logs/zz_code_changes_rev7_to_rev8.csv`. Unchanged: `classify_pair`, `energy_role`, `feasibility_accounting`, `qs_dynamic_accounting`, `fold_separate_recomputation`, the evaluator, the separate recomputation script, the closed loop, the planner, the schedule code and amendment 1's decision set.

## 13. Blockers retained
The campaign remains **BLOCKED** until all of these hold:
1. Amendment 2 is approved and issued (§15).
2. The rev7 and rev8 changes pass an independent review, and the owner accepts its closure (`config/code_review_status_v6.json` → `reviews_pending`, which blocks).
3. A release attempt of the final code passes all mandatory tests and reviews, and its manifest and protocol hashes are verified.
4. The approved attempt is promoted to the campaign root with its own protocol §10.1 gate, by an owner-approved procedure.
5. The owner explicitly authorises execution in `release/campaign_authorization.json`, with the scope "execute the 170-run H3 campaign of protocol v1 amendments 1 and 2" and the keys `amendment_sha256`, `amendment_2_sha256` and `pre_run_hashes_sha256`.

## 14. Reporting rules kept
Completed, invalid, infeasible, excluded, profile-failed and not-evaluable conditions are reported in separate rows (protocol §10.5). ΔE_abs and ΔE_rel are reported only for `COMPARABLE` conditions, always together, with trip time.

## 15. To issue (owner)
1. Confirm or replace the interpretation points of §9. If any is replaced, the code, the review and a new release attempt must follow before issue.
2. Copy the final text to `R4_20261028_campaign/release/03_R4_protocol_v1_amendment_2.md`, set `"status": "APPROVED"` in the block, and record its SHA-256.
3. Write `R4_20261028_campaign/release/amendment_2_approval.json` with `approved_by`, `date` and `amendment_sha256`.

## 16. Machine-readable block

`code/r4h3/campaign.py` (`IMPLEMENTED_2`) reads this block. Every value must equal what the code implements: a difference or an unknown key is an error, never an override.

<!-- r4h3-amendment-block -->
```json
{
 "amendment": "R4 protocol v1 amendment 2 (N-A2, AMB-29(a)-(d), AMB-30, AMB-31, AMB-32), candidate rev5",
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
 "AMB_29_eligible_run_missing": "owner ruling 2026-10-28 (AMB-29(b)): NOT_EVALUABLE_RUN_MISSING (class NOT_EVALUABLE) -> the M0/M1 branch is INCONCLUSIVE for this criterion; M2 stays reported only; the pair stays in every planned-run denominator and every available energy trace is kept for diagnostics",
 "AMB_29_qs_energy_undefined": "owner ruling 2026-10-28 (AMB-29(c)): QS energy per reference km <= 0 -> NOT_EVALUABLE_QS_UNDEFINED (the owner's QS_COMPARISON_NOT_EVALUABLE) -> the M0/M1 branch is INCONCLUSIVE for this criterion; M2 stays reported only; the raw values and the exact non-positive term are recorded; no percentage, replacement denominator, epsilon, absolute value or substitute threshold; the runs' dynamic result is unaffected and protocol 8.2 still applies to it",
 "AMB_29_condition_error": "owner ruling 2026-10-28 (AMB-29(d)): an exception before or during the pair evaluation -> NOT_EVALUABLE_CONDITION_ERROR (eligibility unknown; an exception inside one run leaves its pair NOT_EVALUABLE_RUN_MISSING) -> the M0/M1 branch is INCONCLUSIVE for this criterion; M2 stays reported only; the error, traceback, traces and run IDs are kept (errors.csv, conditions/, traces/); no retry, automatic replacement or substitute run; a rerun only under the protocol and an explicitly authorised procedure with a distinct run ID",
 "AMB_30_branch_scope": "owner ruling 2026-10-28: an applicable FAIL or a NOT_EVALUABLE_* pair in any preregistered set (NOM, P3, INS, CNV, SEN) makes the M0/M1 branch INCONCLUSIVE, counted per set, never averaged; the branch can PASS only if at least one pair of the held-out nominal S2 set NOM passes and both nominal cells (L-R1, L-EVE) are in the record once, with both profiles and evaluable; a PASS in another set, the in-sample S1 set INS included, never substitutes; a planned pair missing from the record blocks PASS",
 "AMB_31_energy_of_invalid_runs": "owner ruling 2026-10-28: energy of a run failing protocol 8.2, or not confirmed by its in-process or separate recomputation, is diagnostic only (energy_roles.csv DIAGNOSTIC_ONLY_*): never confirmatory, never credited to the paired endpoint, never used by the QS-vs-dynamic check",
 "AMB_31_invalid_arm_label": "NOT_EVALUABLE_RUN_INVALID (owner ruling AMB-29(b): M0/M1 branch INCONCLUSIVE; M2 stays reported only)",
 "paired_endpoint_rule": "a paired energy comparison exists only for a condition whose final status is COMPARABLE: both arms complete the task and pass every protocol 8.2 criterion and the separate recomputation",
 "h3_verdict_denominators": "fixed by protocol 8.1: 6 nominal S2 P1 cells and 32 draws per M0/M1; a missing, profile-failed, invalid or non-comparable cell or draw is never removed and never counts toward SUPPORTED",
 "AMB_32_not_supported_needs_all_nominal_cells": "owner ruling 2026-10-28: NOT SUPPORTED requires a comparable pair in all six nominal cells; a nominal cell that is missing, invalid or not evaluable makes the H3 verdict INCONCLUSIVE, recorded with its reason; no negative finding is inferred from missing data",
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
 "pair_status_classes": {
  "PASS": [
   "PASS"
  ],
  "FAIL": [
   "FAIL"
  ],
  "REPORTED_ONLY": [
   "REPORTED_ONLY"
  ],
  "NOT_APPLICABLE": [
   "NOT_APPLICABLE_QS_INFEASIBLE",
   "NOT_APPLICABLE_PROFILE_UNAVAILABLE"
  ],
  "NOT_EVALUABLE": [
   "NOT_EVALUABLE_RUN_MISSING",
   "NOT_EVALUABLE_QS_UNDEFINED",
   "NOT_EVALUABLE_CONDITION_ERROR",
   "NOT_EVALUABLE_RUN_INVALID"
  ]
 },
 "non_positive_denominator_rule": "AMB-29(c) ruling: no relative percentage is computed with a denominator <= 0 or not finite (QS-vs-dynamic e_QS; paired dE_rel, B0 energy per reference km; planner S_found, S_max and grid dS, E(v_b)); the value is not evaluable and the exact term and the raw values are recorded",
 "record_invariant": "every scheduled condition and run has exactly one record (no drop, retry or replacement); a violation is recorded in errors.csv and the manifest",
 "planned_runs": {
  "NOM": 12,
  "P3": 12,
  "INS": 12,
  "CNV": 6,
  "SEN": 128,
  "total": 170
 },
 "note": "CANDIDATE rev5 - DRAFT - NOT APPROVED FOR RELEASE. Values must equal the implementation."
}
```
