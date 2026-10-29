# Amendment 2 to R4 protocol v1 (H3): owner rulings N-A2, AMB-29(a)–(d), AMB-30, AMB-31, AMB-32 and I-1 — the QS-versus-dynamic check, missing and invalid evidence, and the nominal held-out requirement

**Status: CANDIDATE rev7 — DRAFT — NOT APPROVED FOR RELEASE — NOT ISSUABLE: owner decisions I-2 to I-6 are open (§9).** This candidate is not issued, frozen or approved, and has no force. It implements the owner's ruling on I-1 and the fixes of the attempt-6 verification (§12). The points I-2 to I-6 in §9 are open owner decisions: the code implements a provisional reading of each, and both the code and the review status block the campaign while any is open. This text may not be issued with them assumed.

| Item | Value |
|---|---|
| Frozen protocol v1 | `../R4_20261028_preflight/03_R4_protocol_v1.md`, SHA-256 `f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab` (unchanged) |
| Amends | issued amendment 1, `../R4_20261028_campaign/release/03_R4_protocol_v1_amendment_1.md`, SHA-256 `7720fed75bb678e47a229d00aff154e0aa14607c051f4a1163cc9bf67b6abee2` (unchanged; it stays in force for everything this candidate does not address) |
| Basis | the owner's rulings of 2026-10-28: N-A2; AMB-29(a) and AMB-31; AMB-29(b), AMB-29(c), AMB-29(d), AMB-30 and AMB-32; I-1 |
| Supersedes (as the text proposed for review) | candidate rev6, `03_protocol_v1_amendment_2_rev6_CANDIDATE.md`, SHA-256 `0dcb767e97e19f40c00735d9efaecf8d21c396c23952b70e60ccb21a3f711e1f`, kept unchanged. Earlier drafts, all kept unchanged: rev5 `e7ba73c11784b3cf38f48e32b69a7a7c21b070d039118547d638bc1bf06d4f5f`; rev4 `c726560d1e87036cbd94fe58724cafdc1e4746647f6cfacbb320f3e14ed143ab`; rev3 (`03_protocol_v1_amendment_2_DRAFT.md`) `fdaf193de510488733f0e0899d50def86cbeafabdbecdd3bc7a144099b6f492c`; rev2 `e0dc68827c57704b49b13886c455b281e4e3c10ce377a1f174742ff5529247cc`; rev1 `a936023af0a772ee2b81c720c76f9c462aba89afe1a8e1de38a286872a8744bf`; rev0 `c3e1ddfce7dca7909bb1cd2a6186f4d5044b5dfe81eeed43df0b9fcf215957d4` |
| Decision record | `15_remaining_owner_decisions.md`; `17_owner_rulings_attempts5_6_report.md`; **`18_owner_decision_matrix_I1_I6.md`** (I-1 decided; I-2 to I-6 open, with their alternatives, effects and the decisions required); `19_attempt7_final_review_report.md` |
| Review | `review/R5_attempt5_review_agent_report_20261028.md` and `review/V6_attempt6_verification_agent_report_20261028.md`: a separate AI review agent (read-only; not a human audit). Rev7 and the rev10 code fix the three MINOR findings of V6 (§12) |
| Integrity identifier | the SHA-256 of this file is recorded in `03_protocol_v1_amendment_2_rev7_CANDIDATE.sha256.txt`. It identifies the text only; it is not an approval |

All thresholds of protocol v1 and amendment 1 are unchanged: QS-versus-dynamic ≤ 1 % per reference km for M0 and M1, M2 reported only; planner grid < 0.2 pp; optimality 0.2 pp; time step < 0.01 pp; the §8.2 criteria and the recomputation tolerances of amendment 1. Nothing here is tuned on S2.

## 1. Owner rulings this candidate implements (binding)

### 1.1 N-A2 (unchanged from rev3)
The protocol §9 QS-versus-dynamic consistency check applies only to an evaluation pair for which **both** the baseline (B0) profile and the eco (B3) profile pass the prescribed quasi-static feasibility screen under the same applicable conditions. If either profile fails the screen, the pair's check is `NOT_APPLICABLE_QS_INFEASIBLE`: neither a pass nor a failure. The QS diagnostics and the exact failed feasibility check are kept. QS energy computed from torque beyond the QS model's admissible limits is never used to pass or fail the check, and no QS saving is computed for that pair for acceptance. The profile, plant, LQR gain, limits and task are never modified.

### 1.2 AMB-29(a): missing profile (unchanged from rev4)
- A profile-generation failure or planner infeasibility **remains an explicit outcome**: `PROFILE_UNAVAILABLE` or `BASELINE_UNAVAILABLE` (amendment 1).
- It counts in the planned-run, feasibility and verdict denominators (§7), is never removed, and is never relabelled `NOT_APPLICABLE` for the experiment outcome.
- It never yields a paired energy comparison.
- Only the pair's QS-versus-dynamic **check** is `NOT_APPLICABLE_PROFILE_UNAVAILABLE`, because its applicability condition is objectively unmet. This label takes precedence when the other profile also fails the QS screen. An inapplicable check is not a pass.

### 1.3 AMB-31: energy from a run failing §8.2 (unchanged from rev4, made precise in §4)
Energy from a run that fails any mandatory §8.2 criterion, or that is not confirmed by the recomputation, is not a valid confirmatory result. It is kept, labelled diagnostic only, and never credited to the primary paired endpoint. A valid paired comparison needs both arms to complete the task and satisfy every mandatory validity condition. A constraint failure is never reinterpreted as a harmless diagnostic deviation.

### 1.4 AMB-29(b): missing usable energy or invalid arm
Owner's words: "Approve: `NOT_EVALUABLE` → `INCONCLUSIVE`. A pair cannot contribute to the confirmatory paired energy endpoint unless both arms are valid and confirmed by the separate recomputation process. Retain all available energy traces for diagnostic purposes. Missing or invalid energy must not cause the pair to disappear from its planned-run denominator."
- A QS-eligible pair with an arm without a finite dynamic energy is `NOT_EVALUABLE_RUN_MISSING`; with an arm whose energy is invalid or unconfirmed (§4) it is `NOT_EVALUABLE_RUN_INVALID`. Either makes the M0/M1 branch INCONCLUSIVE for this criterion. For M2 the label is recorded and the branch stays reported only.
- The paired endpoint uses a condition only if its final status is `COMPARABLE` (§5).
- Every trace and raw energy is kept. The pair stays in every denominator (§7).

### 1.5 AMB-29(c): QS energy ≤ 0
Owner's words: "Approve: `QS_COMPARISON_NOT_EVALUABLE` → `INCONCLUSIVE` for the applicable QS-versus-dynamic criterion. Retain the raw values and identify the exact non-positive term. Do not calculate a relative saving percentage using a non-positive denominator. This ruling applies to the affected QS comparison; it must not automatically invalidate a separate dynamic energy result that independently satisfies every applicable validity condition. Continue to enforce all dynamic §8.2 requirements. Do not invent a replacement denominator, epsilon adjustment, absolute-value transformation or substitute threshold."
- The label is `NOT_EVALUABLE_QS_UNDEFINED`, a member of the `NOT_EVALUABLE` class (§2; the owner's term `QS_COMPARISON_NOT_EVALUABLE` is read as that class, provisional reading I-5, §9). It makes the M0/M1 branch INCONCLUSIVE for this criterion.
- No percentage is computed. The raw values (E_QS in J, the dynamic energy in Wh, d_ref, e_QS and e_dyn per reference km) and the exact non-positive term are recorded per arm (`qs_vs_dyn_non_positive_term`) and per pair (`qs_vs_dyn_non_positive_terms`).
- The runs' dynamic result is unaffected: the condition status comes from §8.2 and the recomputation alone (§3). Every §8.2 requirement still applies.
- No replacement denominator, epsilon, absolute value or substitute threshold is used. The same rule is applied to the code's other relative **saving** percentages (§4.2; provisional reading I-3, §9).
- The QS-versus-dynamic criterion is a §9 check, so its INCONCLUSIVE outcome still makes the H3 verdict INCONCLUSIVE through §8.1 ("every check in §9 passes"). That is the existing §9 consequence, not an invalidation of the dynamic result (§3, §8).

### 1.6 AMB-29(d): evaluation error
Owner's words: "Approve: `NOT_EVALUABLE` → `INCONCLUSIVE`. Preserve the error, logs, traces and run ID. No silent retry, automatic replacement, or new official run may be substituted for a failed evaluation. Any future rerun must follow the existing protocol and an explicitly authorized procedure with a distinct run ID."
- An exception before or during a pair's QS-versus-dynamic evaluation, the QS screen included, labels the pair `NOT_EVALUABLE_CONDITION_ERROR` (eligibility unknown), or `NOT_APPLICABLE_PROFILE_UNAVAILABLE` if a profile is missing. Both dynamic arms still run, and the condition status comes from §8.2 alone (§3).
- An exception inside one run, including its evaluation, makes the condition `ERROR`. For a QS-eligible pair it leaves the pair `NOT_EVALUABLE_RUN_MISSING` unless the other, valid arm FAILs, which stays a FAIL; either makes the M0/M1 branch INCONCLUSIVE for this criterion. For a QS-ineligible pair the provisional reading I-6 (§9, open) keeps its `NOT_APPLICABLE_*` label.
- An exception while classifying the pair (`classify_pair`) is recorded and makes the **condition `ERROR`**; the executed runs keep their records (they are not relabelled as not executed).
- An exception while recording the pair's result is recorded too. The executed runs keep their records, and the condition keeps its status; a PASS, FAIL or REPORTED_ONLY whose record could not be completed becomes `NOT_EVALUABLE_CONDITION_ERROR` (the earlier value is kept in `qs_vs_dyn_pair_status_before_error`).
- The traceback goes to `errors.csv` with the stage (`run`, `run_report`, `qs_screen`, `classify`, `qs_vs_dynamic`, `condition_report`) and the run ID, or for a pair- or condition-level error both run IDs (`run_ids`). The trace written before the failure, the condition record and the logs are kept; `runs.csv` names the kept trace files of a run whose evaluation raised (`retained_files`).
- No run is retried, replaced or substituted. Every scheduled condition and run has exactly one record (`record_invariant`, §7.5). A rerun only under the protocol and an explicitly authorised procedure with a distinct run ID.

### 1.7 AMB-30: required sets for QS-versus-dynamic conclusions
Owner's words: "Approve the strict interpretation: 1. A required PASS must exist for the nominal held-out S2 set. 2. A pass on in-sample S1 cannot substitute for a missing or failed nominal S2 check. 3. Failures of applicable QS-versus-dynamic checks in any preregistered set count against the branch, according to the existing §9 consequence. 4. Do not average across sets to hide a failure. 5. A missing nominal S2 cell required by protocol cannot produce PASS. 6. If an applicable required check fails, or the mandatory held-out evidence is missing, classify the branch as INCONCLUSIVE where required by the existing protocol. 7. Do not modify any numerical threshold or reuse S2 to tune the planner."
The rule is in §6.

### 1.8 AMB-32: missing nominal cell
Owner's words: "A required nominal cell that is missing, invalid or not evaluable cannot be classified as NOT SUPPORTED merely because a result was absent. Use INCONCLUSIVE and record the missing evidence and its reason. Do not infer a negative scientific finding from missing data."
The rule is in §8.

### 1.9 I-1: every required nominal cell must pass (owner ruling 2026-10-28)
Owner's words: "The owner rejects the "one nominal PASS per motor" interpretation. Every nominal cell required by the protocol on the held-out S2 set must individually pass the applicable QS-versus-dynamic check for the relevant branch. A missing, invalid, unevaluable, or NOT_APPLICABLE required nominal cell cannot count as PASS. Where mandatory evidence is missing, classify the branch as INCONCLUSIVE. A pass on S1 never substitutes for missing or failed nominal S2 evidence. For an applicable check that fails, retain the existing frozen protocol consequence. Do not alter numerical thresholds. Do not use this ruling to reclassify a QS-infeasible profile as dynamically infeasible automatically. QS and dynamic feasibility remain distinct."
- The required nominal cells of a branch are the protocol §8.1 nominal S2 P1 cells of that motor: NOM with L-R1 and NOM with L-EVE. The ruling applies to the decisive branches M0 and M1; M2 stays reported only.
- The rule is in §6 (branch outcome) and §8 (verdict). It changes no condition status, energy role, denominator or threshold.

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
| PASS | `PASS` | eligible; both arms valid and within 1 % per reference km | counts as a pass; every required nominal cell (NOM, L-R1 and L-EVE) must be PASS (§6; I-1) |
| FAIL | `FAIL` | eligible; a **valid** arm exceeds 1 % (even if the other arm is not valid) | INCONCLUSIVE (protocol §9), in any set |
| — | `REPORTED_ONLY` | M2 only: eligible, both arms valid, ratio defined | none (M2 reported only); for M0/M1 an inconsistency that blocks PASS |
| NOT_APPLICABLE | `NOT_APPLICABLE_QS_INFEASIBLE` | a profile fails the QS screen (N-A2) | outside the nominal cells: none, neither pass nor fail. In a required nominal cell it cannot count as PASS, so INCONCLUSIVE (I-1). The condition's dynamic status is unchanged |
| NOT_APPLICABLE | `NOT_APPLICABLE_PROFILE_UNAVAILABLE` | a profile does not exist (AMB-29(a)), whatever the other profile's screen result; the condition keeps its explicit failure status | outside the nominal cells: none (provisional reading I-2, §9). In a required nominal cell it cannot count as PASS, so INCONCLUSIVE (I-1) |
| NOT_EVALUABLE | `NOT_EVALUABLE_RUN_MISSING` | eligible; an arm has no finite simulator energy (the run raised, or its simulator energy is not finite) | INCONCLUSIVE (AMB-29(b)) |
| NOT_EVALUABLE | `NOT_EVALUABLE_RUN_INVALID` | eligible; an arm's simulator energy is finite but its run fails §8.2 (non-finite states included) or a recomputation | INCONCLUSIVE (AMB-29(b), AMB-31) |
| NOT_EVALUABLE | `NOT_EVALUABLE_QS_UNDEFINED` | eligible; QS energy per reference km ≤ 0 (or d_ref ≤ 0, labelled by its own term) | INCONCLUSIVE (AMB-29(c)) |
| NOT_EVALUABLE | `NOT_EVALUABLE_CONDITION_ERROR` | an exception before or during the pair evaluation, the QS screen included, or while recording its result; eligibility unknown | INCONCLUSIVE (AMB-29(d)) |

For M2 every label is used the same way and the M2 branch stays reported only. An unknown status raises an error and is never counted.

**Order with the separate recomputation:** the pair status is set in process. After the separate recomputation, a PASS, FAIL or REPORTED_ONLY that used the energy of an arm the separate recomputation does not confirm becomes `NOT_EVALUABLE_RUN_INVALID`; the in-process value is kept in `qs_vs_dyn_pair_status_in_process`. A FAIL of a confirmed arm stays a FAIL.

## 3. A QS-only status is not a run status

| Situation | QS-versus-dynamic check | Condition status and energy role |
|---|---|---|
| Both runs pass §8.2 and both recomputations; a profile fails the QS screen | `NOT_APPLICABLE_QS_INFEASIBLE` | `COMPARABLE`; energy confirmatory |
| Both runs valid; QS energy ≤ 0 | `NOT_EVALUABLE_QS_UNDEFINED` | `COMPARABLE`; energy confirmatory (AMB-29(c): not invalidated) |
| Both runs valid; the pair's QS evaluation raised | `NOT_EVALUABLE_CONDITION_ERROR` | `COMPARABLE`; energy confirmatory |
| Both runs valid; the QS screen (or its plant) raised before the runs | `NOT_EVALUABLE_CONDITION_ERROR` | both runs still executed; `COMPARABLE`; energy confirmatory |
| Both runs valid; recording the condition's result raised | `NOT_EVALUABLE_CONDITION_ERROR` (a PASS, FAIL or REPORTED_ONLY is kept in `qs_vs_dyn_pair_status_before_error`) | unchanged: the executed runs keep their records and the condition keeps its status |
| Both runs executed; classifying the pair (`classify_pair`) raised | the pair status as evaluated (the classification does not feed it); in a required nominal cell a PASS label on a condition that is not `COMPARABLE` does not count (I-1, §6) | the condition is `ERROR`, so not `COMPARABLE`, and no energy is confirmatory; the executed runs keep their records |
| A QS-infeasible pair in a required nominal cell | `NOT_APPLICABLE_QS_INFEASIBLE`; the M0/M1 branch is INCONCLUSIVE (I-1) | unchanged, for example `COMPARABLE` with confirmatory energy: the ruling never makes it dynamically infeasible |
| A run fails a §8.2 criterion | `NOT_EVALUABLE_RUN_INVALID` if eligible | `B0_INVALID_EXCLUDED`, `INVALID_COMPARISON`, or on P3 `BASELINE_INFEASIBLE_ON_P3` / `ECO_INFEASIBLE_ON_P3`; that run's energy `DIAGNOSTIC_ONLY_RUN_INVALID` |
| A run is not confirmed by a recomputation | `NOT_EVALUABLE_RUN_INVALID` if eligible | `RECOMPUTATION_DISAGREEMENT`; `DIAGNOSTIC_ONLY_RECOMPUTATION_NOT_CONFIRMED` |
| A profile is missing | `NOT_APPLICABLE_PROFILE_UNAVAILABLE` | `PROFILE_UNAVAILABLE` / `BASELINE_UNAVAILABLE`; the existing arm `VALID_RUN_NOT_IN_PAIRED_ENDPOINT` or a `DIAGNOSTIC_ONLY_*` role; the missing arm `NO_ENERGY_NOT_EXECUTED` |

The condition status is decided by amendment 1 §5 (profile and baseline availability, errors, §8.2 on each arm, the recomputation) and never reads the QS screen or the QS check. A failure of the QS screen, or of recording the QS result, is caught and recorded; it never stops, skips or relabels a dynamic run. A failure of the classification itself makes the condition `ERROR` (it cannot be shown `COMPARABLE`) without relabelling the executed runs. A QS status can make the §9 QS-versus-dynamic **criterion** INCONCLUSIVE; it never makes a run invalid and never excuses, overrides or replaces a §8.2 result. Through §8.1 ("every check in §9 passes"), an INCONCLUSIVE QS criterion still makes the H3 verdict INCONCLUSIVE; that is the frozen §9 consequence, not an invalidation of the energy.

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
| `NOT_DETERMINED_ERROR` | the executor could not determine the role (the exception is in `errors.csv`) | none; counted; never confirmatory |

There is exactly one row per planned run, including when its role cannot be determined.

The QS-versus-dynamic check uses an arm's energy under the same rule: only if the run passes §8.2 and its in-process recomputation, and, after the fold, the separate recomputation (provisional reading I-4, §9). An arm that fails §8.2 or the in-process recomputation has its QS-versus-dynamic value only in `qs_vs_dyn_pct_diagnostic_invalid_run`.

**In-process and final values.** `evaluation.csv` and `conditions/<id>.json` are written as each condition finishes, before the separate recomputation. Their per-arm `qs_vs_dyn_pct` and `qs_vs_dyn_pair_status` are in-process values. For an arm the separate recomputation does not confirm, the final pair status is the one in `conditions.csv` (`NOT_EVALUABLE_RUN_INVALID`, with the in-process value in `qs_vs_dyn_pair_status_in_process`). Only `conditions.csv` and `energy_roles.csv` give final values.

### 4.2 No relative saving percentage with a non-positive denominator (AMB-29(c))
No relative **saving** percentage is computed with a denominator that is ≤ 0 or not finite. The value is recorded as not evaluable, with the exact term and the raw values:

| Quantity | Denominator | When ≤ 0 |
|---|---|---|
| QS vs dynamic, 100·(e_dyn − e_QS)/e_QS | e_QS per reference km (or d_ref) | `diff_pct` empty; pair `NOT_EVALUABLE_QS_UNDEFINED` |
| paired ΔE_rel, 100·(e_B3 − e_B0)/e_B0 (`paired_delta`) | the B0 energy per reference km | `dE_rel_pct` None, `dE_rel_status` `NOT_EVALUABLE_DENOMINATOR_NOT_POSITIVE`; ΔE_abs still reported |
| planner S_found, S_max (protocol §5.4) and grid ΔS_found (§9) | E(v_b), the QS baseline energy | values None; `status` `NOT_EVALUABLE_DENOMINATOR_NOT_POSITIVE`; the grid check is not passed |
| dynamic time-step check (§9) | uses two ΔE_rel values | a ΔE_rel that is not evaluable makes the check not evaluable (`passed` None), never a pass |

The first row is the ruling's direct object. The other rows apply its rule to the code's other relative saving percentages (provisional reading I-3, §9).

**Out of scope, unchanged:**
- the recomputation tolerance comparisons (relative differences with a denominator floor of 1e-12 in `evaluator.compare_with_simulator`, and of 1e-9 in the closed loop's `recompute_pos_neg_rel` diagnostic);
- the energy-closure check, which fails closed with an infinite value;
- the shortfall percentages, whose denominator is the task's fixed reference distance d_ref (> 0).

These are tolerance or validity measures, not savings. Their tolerances are the ones approved with amendment 1, and this candidate does not change their definitions.

## 5. Paired endpoint
A paired energy comparison exists only for a condition whose final status is `COMPARABLE`: both arms complete the task, pass every §8.2 criterion and both recomputations. ΔE_abs and ΔE_rel are reported together, with trip time, and only for such conditions. A QS-only status (§3) does not remove a `COMPARABLE` condition from the endpoint.

## 6. Motor-branch outcome of the QS-versus-dynamic criterion (AMB-30, I-1)

M2 is reported only. An M0 or M1 branch is **INCONCLUSIVE**, with every applicable reason recorded, if any of these holds:
1. an applicable check **FAILs** in any preregistered set: NOM, P3, INS (S1, in-sample), CNV or SEN (AMB-30 items 3, 6). A FAIL in a required nominal cell keeps this frozen consequence;
2. a pair in any set is **NOT_EVALUABLE** (AMB-29(b)–(d));
3. **a required nominal cell does not PASS individually** (owner ruling I-1). The required nominal cells are the motor's NOM pairs for L-R1 and for L-EVE. A cell that is absent from the record, appears more than once, is `NOT_APPLICABLE_QS_INFEASIBLE` or `NOT_APPLICABLE_PROFILE_UNAVAILABLE`, is `NOT_EVALUABLE_*`, is `REPORTED_ONLY`, belongs to a condition without a profile (`PROFILE_UNAVAILABLE` / `BASELINE_UNAVAILABLE`, whatever its pair label), or carries a PASS label on a condition that is not `COMPARABLE`, is missing or invalid mandatory evidence and never counts as PASS (AMB-30 items 5, 6). A PASS in any other set, INS included, never substitutes (AMB-30 items 1, 2), and with no nominal PASS there is no pass by vacuity;
4. a planned pair of the motor is missing from the record;
5. a pair is labelled `REPORTED_ONLY`, which applies to M2 only.

Otherwise the branch **PASSes**: both required nominal cells PASS and no applicable check in any set fails or is not evaluable. Outside NOM, a `NOT_APPLICABLE_*` pair is neither a pass nor a failure (N-A2; provisional reading I-2 for a missing profile). A QS-infeasible profile is never reclassified as dynamically infeasible: the condition keeps its §8.2 status.

Failures and not-evaluable pairs are **counted per set and never averaged** (AMB-30 item 4). `qs_dynamic_branch_outcomes.csv` reports, per motor: the count of every status; `required_nominal_cells`, `n_required_nominal_cells` and `n_PASS_nominal`; `n_PASS_other_sets`; `nominal_L-R1` and `nominal_L-EVE`; `nominal_evidence_missing`; `fail_by_set`, `not_evaluable_by_set`, `pass_by_set` and `not_applicable_by_set`; `planned_pairs_missing_from_record`; the outcome and its reasons. A row is written for every motor branch, including one with no pair in the record. No threshold is changed and S2 is not used to tune the planner (AMB-30 item 7).

## 7. Denominator and exclusion reporting
Nothing is dropped from a denominator. Every exclusion is reported with its reason.
1. **Feasibility** (`feasibility_accounting.csv`; per motor and set, per motor, overall): planned conditions and runs; runs executed and not executed (and of those, profile failures); runs §8.2-valid and invalid; profile-failure conditions; conditions eligible for and excluded from the paired endpoint; one count per condition status and per energy role. The status counts add up to the planned conditions and the role counts to the planned runs.
2. **QS-versus-dynamic** (`qs_dynamic_accounting.csv`; per motor and set, per motor): planned pairs; eligible, QS-ineligible (B0 only, B3 only, both), profile-unavailable and eligibility-unknown pairs, which add up to the planned pairs; one count per pair status, which also add up; pairs passing on dynamic-valid arms; dynamic-valid and `COMPARABLE` pairs.
3. **Branch outcomes** (`qs_dynamic_branch_outcomes.csv`, §6).
4. **Energy roles** (`energy_roles.csv`, §4.1): one row per planned run with its §8.2 flags, failed criteria and recomputation result.
5. **Record invariant** (`manifest.json` → `record_invariant`): every scheduled condition and run has exactly one record, in schedule order. A violation is recorded in `errors.csv` and the manifest; it would be a defect, never a pass. It does not stop the run (protocol §10.4: nothing is retried or replaced).
6. **Errors** (`errors.csv`): every exception with its traceback, its stage and its run ID or run IDs.
7. **Runs** (`runs.csv`): `executed` means the run was simulated and returned its record (evaluated, or kept unevaluated with its raw trace when its states are non-finite). A run whose simulation or evaluation raised has `executed=False`, its error in `errors.csv`, and its kept trace and specification files in `retained_files`. Its simulator energy is in the kept trace, not in `runs.csv`, because the run raised before returning its summary.
8. **Separate recomputation:** the script exits 0 (every recomputed run passes), 1 (a run fails a protocol check), 3 (an independence violation or a refusal) or 4 (an exception, including one while importing its modules or reading its arguments). Only 0 and 1 are results.
   - **Ledger (review V6-1).** The process's full output is kept in `recomputation_independent_process.log`. A failure before, during or at the end of the process is written to `errors.csv` (condition `SEPARATE-RECOMPUTATION`) with its stage and that log as `diagnostic_path`. The failures covered are: a launch failure, an exit other than 0 or 1, a missing or unreadable output file, and an executed run missing from the output.
   - **Per run.** One more row goes to `errors.csv` for every executed run left unrecomputed, with its run ID, condition, stage and log.
   - **Manifest.** `manifest.json` → `separate_recomputation` records the exit, the problem, the log and the number of runs not recomputed.
   - **Fail-closed.** Every unrecomputed run stays unconfirmed. If applying the recomputation (the fold) itself raises, no condition stays `COMPARABLE` or eligible for the paired endpoint, and no unconfirmed QS PASS or FAIL stands. The summary outputs are still written.
9. **Verdict eligibility** (`h3_verdict_eligibility.json`, §8).

## 8. Overall H3 verdict (protocol §8.1; AMB-32)
The §8.1 denominators are fixed and never reduced: 6 nominal S2 P1 cells (M0, M1, M2 × L-R1, L-EVE) and 32 sensitivity draws for each of M0 and M1.
- **SUPPORTED** needs a `COMPARABLE` pair in all six nominal cells, at least 29 of 32 sensitivity draws for M0 and for M1 separately, and every §9 check passing, together with the energy conditions of §8.1.
- **NOT SUPPORTED** needs a `COMPARABLE` pair in all six nominal cells, ΔE_rel > −1.0 % in every motor branch for the nominal S2 P1 runs, and all checks passing (AMB-32).
- Otherwise **INCONCLUSIVE**. A nominal cell that is missing, invalid or not evaluable makes the verdict INCONCLUSIVE, never NOT SUPPORTED. No negative finding is inferred from missing data, and no verdict is reached by omission. A `COMPARABLE` nominal cell whose ΔE_rel is not evaluable (§4.2) satisfies neither side of the −1 % rule, so it also leads to INCONCLUSIVE (provisional reading I-3, §9). This is a rule for the later analysis: no code in this release computes the verdict from energy, and `paired_delta` only refuses the percentage.
- An INCONCLUSIVE QS-versus-dynamic criterion makes the verdict INCONCLUSIVE through "every check in §9 passes", even when every nominal cell is `COMPARABLE` with confirmatory energy (§3). The criterion is INCONCLUSIVE when there is any `NOT_EVALUABLE_*` pair, a FAIL, or a required nominal cell that does not PASS (I-1).

`h3_verdict_eligibility.json` records, without reading any energy value, which verdicts remain possible from the condition statuses and the branch outcomes:
- For each nominal cell without a comparable pair it records the cell, its status and its reason (`nominal_missing_evidence`).
- It checks the I-1 ruling again from the condition rows, independently of the branch outcome. For M0 and M1, every required nominal cell's pair status must be PASS (`qs_vs_dynamic_nominal_cells`); otherwise SUPPORTED and NOT SUPPORTED are both ruled out.

It computes no energy difference. The other §9 checks can only remove possibilities.

## 9. Owner decisions on the readings I-1 to I-6

**I-1 is decided by the owner (§1.9). I-2 to I-6 are open.** For each open point:
- the code implements a provisional reading, labelled "Provisional reading I-n (owner decision open)" in the machine block;
- the point is listed in `owner_decisions_open` (machine block) and `campaign.OWNER_DECISIONS_OPEN`, and in `config/code_review_status_v8.json` → `open_owner_decisions`;
- campaign mode and readiness are blocked while any point is listed.

**This candidate may not be issued with these points assumed.** `18_owner_decision_matrix_I1_I6.md` gives, for each point:
- the exact rev6 wording;
- every interpretation;
- the effect on statuses, denominators, feasibility and the H3 verdict;
- the risks;
- a recommendation;
- the precise decision required.

No interpretation of I-2 to I-6 changes a condition status, a denominator, a feasibility count or an energy role. Each changes only the QS-versus-dynamic label and so, possibly, the M0/M1 QS branch outcome.

| ID | Point | Status | Provisional reading (implemented) | Alternative | Which is stricter | Can it change the H3 verdict? |
|---|---|---|---|---|---|---|
| I-1 | the required nominal PASS | **DECIDED** (owner ruling, §1.9) | not provisional: the ruling (every required nominal cell must PASS individually) | — | — | — |
| I-2 | a pair without a profile **outside** NOM (the NOM case is settled by I-1) | **OPEN** | neither pass nor fail; the QS criterion is unaffected (the condition still counts as a failure in §7) | the M0/M1 QS criterion is INCONCLUSIVE | the alternative | yes |
| I-3 | scope of "no relative saving percentage with a non-positive denominator" | **OPEN** | every relative saving percentage (§4.2); tolerance comparisons out of scope | the QS ratio only | the provisional reading | yes, only if a baseline energy is ≤ 0 |
| I-4 | which recomputation must confirm an arm used by the QS check | **OPEN** | both the in-process and the separate one | the separate one only | the provisional reading | yes |
| I-5 | the owner's term `QS_COMPARISON_NOT_EVALUABLE` | **OPEN** (vocabulary) | the `NOT_EVALUABLE` class; the label `NOT_EVALUABLE_QS_UNDEFINED` is kept | rename the label | neither | **no** |
| I-6 | an exception inside one run | **OPEN** | condition `ERROR`; a QS-eligible pair `NOT_EVALUABLE_RUN_MISSING` (or FAIL if the other valid arm FAILs); a QS-ineligible pair keeps its `NOT_APPLICABLE_*` label | the pair is `NOT_EVALUABLE_CONDITION_ERROR` in every case | the alternative, for a QS-ineligible pair outside NOM; otherwise the outcome is the same | yes, only for a QS-ineligible pair outside NOM |

## 10. Effect on the planned 170-run schedule
None. The 170 official runs, their IDs, sets, plants, profiles, gains (nominal P1 gain for every SEN draw, AMB-14), tolerances and numerics are unchanged, and so is the schedule's SHA-256. No run is added, removed, retried, replaced or made conditional. Smoke-test runs stay excluded (D4). S2 stays held out and is not used for tuning.

## 11. Location rule for campaign mode
Unchanged from rev3 §9: campaign mode runs only when the running code's directory is, by resolved path, `R4_20261028_campaign/`.

## 12. Changes

### 12.1 Since rev6 (complete list)

| Change | Basis | Effect |
|---|---|---|
| `checks.branch_qs_dynamic_outcome`: every required nominal cell must PASS individually. `NOT_APPLICABLE_QS_INFEASIBLE` in a nominal cell no longer counts as evidence, and a PASS label on a condition that is not `COMPARABLE` does not count. New columns `required_nominal_cells` and `n_required_nominal_cells` | owner ruling I-1 | stricter |
| `checks.h3_verdict_eligibility`: checks I-1 again from the condition rows (`qs_vs_dynamic_nominal_cells`, reason "owner ruling I-1") | owner ruling I-1 | stricter (defence in depth) |
| `recompute_from_traces.py`: imports and argument handling run inside the guarded block, so a start-up failure exits 4 (it exited 1) | review V6-1 | stricter |
| `campaign.execute_schedule`: `recomputation_independent_process.log`; a launch failure, an exit other than 0 or 1, a missing or unreadable output, or an executed run missing from the output is recorded in `errors.csv` with its stage, the log and one row per affected run ID; `manifest.json` → `separate_recomputation` gains `problem`, `process_log` and `runs_not_recomputed` | review V6-1 | stricter; reporting |
| `campaign.preconditions`: blocks while `OWNER_DECISIONS_OPEN` (= the machine-block key `owner_decisions_open`) is not empty | owner instruction (no silent assumption) | stricter |
| `IMPLEMENTED_2`: new keys `I_1_required_nominal_cells`, `owner_decisions_open` and `separate_recomputation_ledger`; `AMB_30_branch_scope` states the I-1 ruling; the readings I-2 to I-6 are labelled "Provisional reading … (owner decision open)"; the exit-code text covers start-up failures | owner ruling I-1; review V6-1; reviews R5-4 and V6-3 | — |
| `NUMERICAL_CHECKS` row 7 names the I-1 rule | owner ruling I-1 | wording; names and order unchanged |
| Text: §1.6 and §3 state that a classification exception makes the condition `ERROR`, and say "PASS, FAIL or REPORTED_ONLY"; the §4.2 table is one table | review V6-2 | wording |
| Text: §9 rewritten. I-1 is decided; I-2 to I-6 are open, with the stricter reading of each identified (I-5 changes no outcome); the decisions are in `18_owner_decision_matrix_I1_I6.md` | review V6-3; owner instruction | wording |
| Text: §1.9 (I-1), §2, §6, §7.8 and §8 follow the changes above | owner ruling I-1; review V6-1 | wording |
| Tests: new `tests/test_owner_ruling_i1_v10.py`. Assertions changed by the I-1 ruling: `test_amendment2.py` (`test_case11…`), `test_owner_rulings_v8.py` (`test_amb30_all_required_checks_pass`, `test_no_situation_yields_a_pass_by_omission`). The verdict fixtures of `test_owner_rulings_v7.py` and `test_owner_rulings_v8.py` gained nominal QS statuses. The candidate-name and review-status checks of `test_review_fixes_v9.py` no longer name one revision | owner ruling I-1; versioning | — |
| `DRAFT_AMENDMENT_2` → this candidate; `CAMPAIGN_CONFIG` → `campaign_config_v10_DRAFT.json`; `REVIEW_STATUS` → `code_review_status_v8.json` (open_major 2 and open owner decisions I-2 to I-6, both blocking) | versioning | — |

Not changed: review notes V6-4 (trivial unguarded reads; the conservative `CONDITION_ERROR` label when one screen raised and the other failed; `fold_failed` keeps the old reason) and R5-14; the partly fixed R5-6 (a run whose evaluation raised keeps its simulator energy only in its trace, §7.7).

The file-level comparison with the rev6 state (`archive/rev9_attempt6_20261028_1727/`) is `logs/zz_code_changes_rev9_to_rev10.csv`.

### 12.2 Earlier changes

The changes from rev4 to rev5 and from rev5 to rev6 are listed in §12 of `03_protocol_v1_amendment_2_rev5_CANDIDATE.md` and `03_protocol_v1_amendment_2_rev6_CANDIDATE.md`, both kept unchanged.

## 13. Blockers retained
The campaign remains **BLOCKED** until all of these hold:
1. The owner decides I-2 to I-6 (§9; `18_owner_decision_matrix_I1_I6.md`), and the code, the review and a new release attempt follow any decision that differs from the provisional reading. Until then `campaign.OWNER_DECISIONS_OPEN` and `open_owner_decisions` block.
2. Amendment 2 is approved and issued (§15).
3. The rev7 to rev10 changes pass an independent review, and the owner accepts its closure. R5-1 and R5-2 (MAJOR) were verified fixed by the AI-agent verification of release attempt 6. The review of release attempt 7 and the owner's acceptance are pending: `config/code_review_status_v8.json` keeps `open_major` 2 and a `reviews_pending` item until the owner accepts, and each blocks.
4. A release attempt of the final code passes all mandatory tests and reviews, and its manifest and protocol hashes are verified.
5. The approved attempt is promoted to the campaign root with its own protocol §10.1 gate, by an owner-approved procedure.
6. The owner explicitly authorises execution in `release/campaign_authorization.json`, with the scope "execute the 170-run H3 campaign of protocol v1 amendments 1 and 2" and the keys `amendment_sha256`, `amendment_2_sha256` and `pre_run_hashes_sha256`.

## 14. Reporting rules kept
Completed, invalid, infeasible, excluded, profile-failed and not-evaluable conditions are reported in separate rows (protocol §10.5). ΔE_abs and ΔE_rel are reported only for `COMPARABLE` conditions, always together, with trip time.

## 15. To issue (owner)
1. Decide I-2 to I-6 (§9; the decisions required are worded in `18_owner_decision_matrix_I1_I6.md`). Then the code must remove them from `owner_decisions_open`, implement any decision that differs from the provisional reading, and pass a review and a new release attempt. A later candidate (rev8 or later) records the decisions. **This rev7 text is not to be issued.**
2. Copy the final text to `R4_20261028_campaign/release/03_R4_protocol_v1_amendment_2.md`, set `"status": "APPROVED"` in the block, and record its SHA-256.
3. Write `R4_20261028_campaign/release/amendment_2_approval.json` with `approved_by`, `date` and `amendment_sha256`.

## 16. Machine-readable block

`code/r4h3/campaign.py` (`IMPLEMENTED_2`) reads this block. Every value must equal what the code implements: a difference or an unknown key is an error, never an override.

<!-- r4h3-amendment-block -->
```json
{
 "amendment": "R4 protocol v1 amendment 2 (N-A2, AMB-29(a)-(d), AMB-30, AMB-31, AMB-32, I-1), candidate rev7",
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
 "AMB_29_qs_energy_undefined": "owner ruling 2026-10-28 (AMB-29(c)): QS energy per reference km <= 0 -> NOT_EVALUABLE_QS_UNDEFINED -> the M0/M1 branch is INCONCLUSIVE for this criterion; M2 stays reported only; the raw values and the exact non-positive term are recorded; no percentage, replacement denominator, epsilon, absolute value or substitute threshold; the runs' dynamic result is unaffected and protocol 8.2 still applies to it. Provisional reading I-5 (owner decision open; it changes no outcome): the owner's QS_COMPARISON_NOT_EVALUABLE is the NOT_EVALUABLE class",
 "AMB_29_condition_error": "owner ruling 2026-10-28 (AMB-29(d)): an exception before or during the pair evaluation, including the QS screen -> NOT_EVALUABLE_CONDITION_ERROR (eligibility unknown; NOT_APPLICABLE_PROFILE_UNAVAILABLE if a profile is missing) -> the M0/M1 branch is INCONCLUSIVE for this criterion; M2 stays reported only; both dynamic arms still run and are classified by protocol 8.2 alone; the error, traceback, traces and run IDs are kept (errors.csv, conditions/, traces/); no retry, automatic replacement or substitute run; a rerun only under the protocol and an explicitly authorised procedure with a distinct run ID. Provisional reading I-6 (owner decision open): an exception inside one run makes the condition ERROR and leaves a QS-eligible pair NOT_EVALUABLE_RUN_MISSING unless a valid arm FAILs; an ineligible pair keeps its NOT_APPLICABLE_* label",
 "AMB_30_branch_scope": "owner ruling 2026-10-28 (strict): an applicable FAIL or a NOT_EVALUABLE_* pair in any preregistered set (NOM, P3, INS, CNV, SEN) makes the M0/M1 branch INCONCLUSIVE, counted per set, never averaged; a PASS in another set, the in-sample S1 set INS included, never substitutes for missing or failed nominal S2 evidence; a planned pair missing from the record blocks PASS. Owner ruling I-1 (2026-10-28): every required nominal cell of the branch (NOM; L-R1 and L-EVE) must individually PASS; an absent, duplicated, invalid, not-evaluable or NOT_APPLICABLE_* nominal cell, or one whose condition has no profile, cannot count as PASS and the branch is INCONCLUSIVE; a FAIL keeps the frozen protocol 9 consequence. Provisional reading I-2 (owner decision open): outside NOM a NOT_APPLICABLE_PROFILE_UNAVAILABLE pair is neither pass nor fail and does not change the branch outcome",
 "I_1_required_nominal_cells": "owner ruling 2026-10-28: for M0 and M1 every required nominal cell on the held-out S2 set (NOM; L-R1 and L-EVE) must individually PASS the applicable QS-vs-dynamic check; a missing, invalid, unevaluable or NOT_APPLICABLE required nominal cell cannot count as PASS and the branch is INCONCLUSIVE; S1 never substitutes; a FAIL keeps the frozen consequence; thresholds unchanged; QS and dynamic feasibility stay distinct (a QS-infeasible profile is never reclassified as dynamically infeasible)",
 "AMB_31_energy_of_invalid_runs": "owner ruling 2026-10-28: energy of a run failing protocol 8.2, or not confirmed by its recomputation, is diagnostic only (energy_roles.csv DIAGNOSTIC_ONLY_*): never confirmatory, never credited to the paired endpoint, never used by the QS-vs-dynamic check. Provisional reading I-4 (owner decision open): both the in-process and the separate recomputation must confirm the run",
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
 "non_positive_denominator_rule": "AMB-29(c) ruling for the QS-vs-dynamic ratio (e_QS), and provisional reading I-3 (owner decision open) for the other relative saving percentages (paired dE_rel, B0 energy per reference km; planner S_found, S_max and grid dS, E(v_b)): none is computed with a denominator <= 0 or not finite; the value is not evaluable and the exact term and the raw values are recorded. The recomputation and shortfall tolerance comparisons of amendment 1 are not saving percentages and are unchanged",
 "record_invariant": "every scheduled condition and run has exactly one record (no drop, retry or replacement); a violation is recorded in errors.csv and the manifest",
 "separate_recomputation_exit_codes": "0 every recomputed run passes; 1 a run fails a protocol check; 3 independence violation or refusal; 4 exception, including one while importing or reading the arguments. Only 0 and 1 are results: any other exit leaves every run unconfirmed and is recorded in errors.csv with its stderr; a fold that raises leaves no condition COMPARABLE",
 "separate_recomputation_ledger": "review V6-1: the process's full output goes to recomputation_independent_process.log; a launch failure, an exit other than 0 or 1, a missing output file, or an executed run missing from the output is recorded in errors.csv with its stage and that log, plus one row per executed run left unrecomputed, with its run ID",
 "owner_decisions_open": [
  "I-2",
  "I-3",
  "I-4",
  "I-5",
  "I-6"
 ],
 "planned_runs": {
  "NOM": 12,
  "P3": 12,
  "INS": 12,
  "CNV": 6,
  "SEN": 128,
  "total": 170
 },
 "note": "CANDIDATE rev7 - DRAFT - NOT APPROVED FOR RELEASE - NOT ISSUABLE (owner decisions I-2..I-6 open). Values must equal the implementation."
}
```
