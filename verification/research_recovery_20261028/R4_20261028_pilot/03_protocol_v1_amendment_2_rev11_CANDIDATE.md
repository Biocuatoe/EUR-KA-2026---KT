# Amendment 2 to R4 protocol v1 (H3): owner rulings N-A2, AMB-29(a)–(d), AMB-30, AMB-31, AMB-32 and I-1 to I-6 — the QS-versus-dynamic check, missing and invalid evidence, and the nominal held-out requirement

**Status: CANDIDATE rev11 — DRAFT — NOT APPROVED FOR RELEASE.** This candidate is not issued, frozen or approved, and has no force. Every owner ruling on its content has been made: I-1 to I-6, and the owner's decisions of 2026-10-29 (§1, §9). Issuing and approving it are the owner's separate decisions (§15). Rev11 implements the decisions of 2026-10-29 (§1.15, §1.16). It also fixes, from the review of release attempt 10 (one MINOR finding and three notes): the MINOR finding R10-1 and the notes R10-3 and R10-4, and it addresses the note R10-2 with tests (§12). That review verified the rev10 fixes of the attempt-9 findings.

| Item | Value |
|---|---|
| Frozen protocol v1 | `../R4_20261028_preflight/03_R4_protocol_v1.md`, SHA-256 `f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab` (unchanged) |
| Amends | issued amendment 1, `../R4_20261028_campaign/release/03_R4_protocol_v1_amendment_1.md`, SHA-256 `7720fed75bb678e47a229d00aff154e0aa14607c051f4a1163cc9bf67b6abee2` (unchanged; it stays in force for everything this candidate does not address) |
| Basis | the owner's rulings of 2026-10-28: N-A2; AMB-29(a) and AMB-31; AMB-29(b), AMB-29(c), AMB-29(d), AMB-30 and AMB-32; I-1; I-2 to I-6. The owner's decisions of 2026-10-29: I-6b, and the scope of the I-6 relabelling after a failure of the separate recomputation or its fold |
| Supersedes (as the text proposed for review) | candidate rev10, `03_protocol_v1_amendment_2_rev10_CANDIDATE.md`, SHA-256 `5479f0e81b981c7977ea5a416762972d2a332d4fdb75beee7ad8379ade399804`, kept unchanged. Earlier drafts, all kept unchanged: rev9 `cdeea032c520f408f1f300a53cf1bc8b1ec4582d80340d3df2c2c94fa5d45719`; rev8 `f6430bf5512cb56065a2465bcfda1c4c42e244b80f73fcd3e88d985ac8811f7c`; rev7 `0e3ef3112c979237e7079f176b21dd4f2ce682c7ab435f36f33321ffe67a5996`; rev6 `0dcb767e97e19f40c00735d9efaecf8d21c396c23952b70e60ccb21a3f711e1f`; rev5 `e7ba73c11784b3cf38f48e32b69a7a7c21b070d039118547d638bc1bf06d4f5f`; rev4 `c726560d1e87036cbd94fe58724cafdc1e4746647f6cfacbb320f3e14ed143ab`; rev3 (`03_protocol_v1_amendment_2_DRAFT.md`) `fdaf193de510488733f0e0899d50def86cbeafabdbecdd3bc7a144099b6f492c`; rev2 `e0dc68827c57704b49b13886c455b281e4e3c10ce377a1f174742ff5529247cc`; rev1 `a936023af0a772ee2b81c720c76f9c462aba89afe1a8e1de38a286872a8744bf`; rev0 `c3e1ddfce7dca7909bb1cd2a6186f4d5044b5dfe81eeed43df0b9fcf215957d4` |
| Decision record | `15_remaining_owner_decisions.md`; `17_owner_rulings_attempts5_6_report.md`; `18_owner_decision_matrix_I1_I6.md` (the interpretations considered for I-1 to I-6); `19_attempt7_final_review_report.md`; `20_attempt8_final_owner_decisions_report.md` (the owner's rulings on I-2 to I-6, and release attempts 8 to 10); `21_attempt11_final_owner_decisions_report.md` (the owner's decisions of 2026-10-29, and release attempt 11) |
| Review | `review/R5_attempt5_review_agent_report_20261028.md`, `review/V6_attempt6_verification_agent_report_20261028.md`, `review/R7_attempt7_review_agent_report_20261028.md`, `review/R8_attempt8_review_agent_report_20261028.md`, `review/R9_attempt9_review_agent_report_20261028.md` and `review/R10_attempt10_review_agent_report_20261029.md`: separate AI review agents (read-only; not a human audit). Rev11 and the rev14 code fix R10-1, R10-3 and R10-4 and address R10-2 (§12) |
| Integrity identifier | the SHA-256 of this file is recorded in `03_protocol_v1_amendment_2_rev11_CANDIDATE.sha256.txt`. It identifies the text only; it is not an approval |

All thresholds of protocol v1 and amendment 1 are unchanged: QS-versus-dynamic ≤ 1 % per reference km for M0 and M1, M2 reported only; planner grid < 0.2 pp; optimality 0.2 pp; time step < 0.01 pp; the §8.2 criteria and the recomputation tolerances of amendment 1. Nothing here is tuned on S2.

## 1. Owner rulings this candidate implements (binding)

### 1.1 N-A2 (owner ruling 2026-10-28; first stated in rev3)
The protocol §9 QS-versus-dynamic consistency check applies only to an evaluation pair for which **both** the baseline (B0) profile and the eco (B3) profile pass the prescribed quasi-static feasibility screen under the same applicable conditions. If either profile fails the screen, the pair's check is `NOT_APPLICABLE_QS_INFEASIBLE`: neither a pass nor a failure. The QS diagnostics and the exact failed feasibility check are kept. QS energy computed from torque beyond the QS model's admissible limits is never used to pass or fail the check, and no QS saving is computed for that pair for acceptance. The profile, plant, LQR gain, limits and task are never modified.

Implementation note (added in rev10, review R9-1; not part of the ruling): if the diagnosis of a failing piece raises, the piece says so, the exception goes to `errors.csv`, and the pair is `NOT_EVALUABLE_CONDITION_ERROR` (§1.6, §1.14).

### 1.2 AMB-29(a): missing profile (owner ruling 2026-10-28; first stated in rev4)
- A profile-generation failure or planner infeasibility **remains an explicit outcome**: `PROFILE_UNAVAILABLE` or `BASELINE_UNAVAILABLE` (amendment 1).
- It counts in the planned-run, feasibility and verdict denominators (§7), is never removed, and is never relabelled `NOT_APPLICABLE` for the experiment outcome.
- It never yields a paired energy comparison.
- Only the pair's QS-versus-dynamic **check** is `NOT_APPLICABLE_PROFILE_UNAVAILABLE`, because its applicability condition is objectively unmet. This label takes precedence when the other profile also fails the QS screen. An inapplicable check is not a pass.

### 1.3 AMB-31: energy from a run failing §8.2 (owner ruling 2026-10-28; first stated in rev4, made precise in §4)
Energy from a run that fails any mandatory §8.2 criterion, or that is not confirmed by the recomputation, is not a valid confirmatory result. It is kept, labelled diagnostic only, and never credited to the primary paired endpoint. A valid paired comparison needs both arms to complete the task and satisfy every mandatory validity condition. A constraint failure is never reinterpreted as a harmless diagnostic deviation.

### 1.4 AMB-29(b): missing usable energy or invalid arm
Owner's words: "Approve: `NOT_EVALUABLE` → `INCONCLUSIVE`. A pair cannot contribute to the confirmatory paired energy endpoint unless both arms are valid and confirmed by the separate recomputation process. Retain all available energy traces for diagnostic purposes. Missing or invalid energy must not cause the pair to disappear from its planned-run denominator."
- A QS-eligible pair with an arm that was executed but has no finite dynamic energy, with no exception, is `NOT_EVALUABLE_RUN_MISSING` (an attempted run that raised is `NOT_EVALUABLE_CONDITION_ERROR`, owner decision I-6b, §1.15); with an arm whose energy is invalid or unconfirmed (§4) it is `NOT_EVALUABLE_RUN_INVALID`. Either makes the M0/M1 branch INCONCLUSIVE for this criterion. For M2 the label is recorded and the branch stays reported only.
- The paired endpoint uses a condition only if its final status is `COMPARABLE` (§5).
- Every trace and raw energy is kept. The pair stays in every denominator (§7).

### 1.5 AMB-29(c): QS energy ≤ 0
Owner's words: "Approve: `QS_COMPARISON_NOT_EVALUABLE` → `INCONCLUSIVE` for the applicable QS-versus-dynamic criterion. Retain the raw values and identify the exact non-positive term. Do not calculate a relative saving percentage using a non-positive denominator. This ruling applies to the affected QS comparison; it must not automatically invalidate a separate dynamic energy result that independently satisfies every applicable validity condition. Continue to enforce all dynamic §8.2 requirements. Do not invent a replacement denominator, epsilon adjustment, absolute-value transformation or substitute threshold."
- The label is `NOT_EVALUABLE_QS_UNDEFINED`, a member of the `NOT_EVALUABLE` class (§2; the owner's term `QS_COMPARISON_NOT_EVALUABLE` is that class; the label is kept unchanged, owner ruling I-5, §1.13). It makes the M0/M1 branch INCONCLUSIVE for this criterion.
- No percentage is computed. The raw values (E_QS in J, the dynamic energy in Wh, d_ref, e_QS and e_dyn per reference km) and the exact non-positive term are recorded per arm (`qs_vs_dyn_non_positive_term`) and per pair (`qs_vs_dyn_non_positive_terms`).
- The runs' dynamic result is unaffected: the condition status comes from §8.2 and the recomputation alone (§3). Every §8.2 requirement still applies.
- No replacement denominator, epsilon, absolute value or substitute threshold is used. The same rule is applied to the code's other relative **saving** percentages (§4.2; owner ruling I-3, §1.11).
- The QS-versus-dynamic criterion is a §9 check, so its INCONCLUSIVE outcome still makes the H3 verdict INCONCLUSIVE through §8.1 ("every check in §9 passes"). That is the existing §9 consequence, not an invalidation of the dynamic result (§3, §8).

### 1.6 AMB-29(d): evaluation error
Owner's words: "Approve: `NOT_EVALUABLE` → `INCONCLUSIVE`. Preserve the error, logs, traces and run ID. No silent retry, automatic replacement, or new official run may be substituted for a failed evaluation. Any future rerun must follow the existing protocol and an explicitly authorized procedure with a distinct run ID."
- An exception before or during a pair's QS-versus-dynamic evaluation, the QS screen included (its per-piece diagnosis too; review R9-1), labels the pair `NOT_EVALUABLE_CONDITION_ERROR`, also when a profile is missing (I-6, §1.14; review R8-3). QS applicability is kept apart in `qs_vs_dyn_applicability`: `NOT_APPLICABLE_PROFILE_UNAVAILABLE` if a profile is missing, `NOT_APPLICABLE_QS_INFEASIBLE` if a profile fails the screen, `UNKNOWN` if a screen raised and neither holds, otherwise `APPLICABLE`. Both dynamic arms still run, and the condition status comes from §8.2 alone (§3).
- An exception inside one run, including its evaluation, makes the condition `ERROR`. For a QS-eligible pair it makes the pair `NOT_EVALUABLE_CONDITION_ERROR` (owner decision I-6b, §1.15), also when the other, valid arm FAILs; that measured FAIL is kept (§1.14). For a QS-ineligible pair it makes the pair `NOT_EVALUABLE_CONDITION_ERROR`: a NOT_APPLICABLE label never overrides an execution error (owner ruling I-6, §1.14). Either makes the M0/M1 branch INCONCLUSIVE for this criterion.
- An exception while classifying the pair (`classify_pair`) is recorded and makes the **condition `ERROR`** and the pair `NOT_EVALUABLE_CONDITION_ERROR` (I-6); the executed runs keep their records (they are not relabelled as not executed).
- An exception while recording the pair's result is recorded too. The executed runs keep their records, and the condition keeps its status; a PASS, FAIL, REPORTED_ONLY or `NOT_APPLICABLE_*` label whose record could not be completed becomes `NOT_EVALUABLE_CONDITION_ERROR` (the earlier value is kept in `qs_vs_dyn_pair_status_before_error`).
- The traceback goes to `errors.csv` with the stage (`run`, `run_report`, `qs_screen` (also for an exception in a failing piece's diagnosis, with the piece named), `classify`, `qs_vs_dynamic`, `condition_report`; the executor's own stages are in §7.6 and §7.8) and the run ID, or for a pair- or condition-level error both run IDs (`run_ids`). The trace written before the failure, the condition record and the logs are kept; `runs.csv` names the kept trace files of a run whose evaluation raised (`retained_files`).
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

### 1.10 I-2: missing profile outside the nominal set (owner ruling 2026-10-28)
Owner's words: "Approve the existing interpretation: a missing profile outside the nominal set does not automatically make the QS check inconclusive. Requirements: Preserve the explicit missing-profile status and count it in planned-run and feasibility reporting. Do not count it as PASS. Make a QS check inconclusive only when required evidence for that specific check is missing or invalid under the frozen rules. Do not allow a missing profile to create a valid paired energy comparison."
- Outside NOM, a pair whose profile is missing is `NOT_APPLICABLE_PROFILE_UNAVAILABLE`. It is neither a pass nor a failure and does not by itself make the M0/M1 QS criterion INCONCLUSIVE (§6).
- The condition keeps its explicit `PROFILE_UNAVAILABLE` / `BASELINE_UNAVAILABLE` status. It counts in the planned-run, feasibility and verdict reporting (§7); for SEN it counts against "29 of 32". It is never `COMPARABLE`, and `paired_delta` refuses it.
- In a required nominal cell, a missing profile never counts as PASS (I-1). An exception in the existing arm makes the pair not evaluable (I-6).

### 1.11 I-3: non-positive denominator (owner ruling 2026-10-28)
Owner's words: "Approve the strict interpretation: do not calculate any energy-saving percentage if its denominator is less than or equal to zero, not merely the QS ratio. Requirements: Preserve raw energy values. Record which metric is undefined and why. Do not use epsilon, absolute-value transformations, replacement denominators or post-hoc thresholds. Do not invalidate an independently valid metric unless its own prerequisites fail."
- Every energy-saving percentage refuses a denominator that is ≤ 0 or not finite: the QS-versus-dynamic ratio, the paired ΔE_rel, the planner's S_found and S_max, and the grid ΔS_found. The time-step check, which uses two ΔE_rel values, is not evaluable when either is undefined. The value is None; the metric and the reason are recorded (`non_positive_term`, `status`); the raw energies are kept (§4.2).
- An independent metric is not invalidated. ΔE_abs is still reported when ΔE_rel is undefined, and a `COMPARABLE` condition stays `COMPARABLE` when only its QS ratio is undefined.
- No epsilon, absolute value, replacement denominator or post-hoc threshold is used.

### 1.12 I-4: independent recomputation (owner ruling 2026-10-28)
Owner's words: "Approve the requirement that both runs must be confirmed by the separate recomputation process before the QS-versus-dynamic check uses their energy results. If either run is not confirmed, it cannot supply confirmatory evidence for that check. Preserve all traces, error records and run identifiers."
- The QS-versus-dynamic check uses an arm's energy only if its run is confirmed by the separate recomputation: `recomputed` and `protocol_ok` in `recomputation_independent.csv`, with the script's exit 0 or 1 (`fold_separate_recomputation`).
- As before, the arm must also pass §8.2 and its in-process recomputation, the same rule as its energy role (AMB-31, §4.1).
- A PASS, FAIL or REPORTED_ONLY that relied on an unconfirmed arm becomes `NOT_EVALUABLE_RUN_INVALID`. A FAIL of a confirmed arm stays a FAIL. Traces, errors and run IDs are kept (§7).
- If the separate recomputation fails (an exit other than 0 or 1, a launch failure, a missing or unreadable output) or applying it (the fold) raises, no arm is confirmed. A `NOT_APPLICABLE_*` pair with an actually executed run then becomes `NOT_EVALUABLE_CONDITION_ERROR`; a pair none of whose runs was executed keeps its label (owner decision of 2026-10-29, §1.16; reviews R8-9, R9-6). A PASS, FAIL or REPORTED_ONLY relabelled `NOT_EVALUABLE_RUN_INVALID` by such a failure keeps its label in `qs_vs_dyn_pair_status_before_error` (review R9-2).

### 1.13 I-5: the label for QS energy ≤ 0 (owner ruling 2026-10-28)
Owner's words: "Keep the current status label for QS energy less than or equal to zero. Do not rename it. Ensure the same label and meaning appear in the amendment, code, logs, tests and reporting."
- The label stays **`NOT_EVALUABLE_QS_UNDEFINED`**, with the same meaning everywhere: an eligible pair whose QS energy per reference km is ≤ 0 (§2). It is a member of the `NOT_EVALUABLE` class, which is what the owner's AMB-29(c) term `QS_COMPARISON_NOT_EVALUABLE` refers to.
- In the code it is `checks.QS_UNDEFINED`; in the reports, `qs_dynamic_accounting.csv` → `not_evaluable_qs_undefined` and the branch count `n_NOT_EVALUABLE_QS_UNDEFINED`.

### 1.14 I-6: an exception when the QS check is already inapplicable (owner ruling 2026-10-28)
Owner's words: "Approve the stricter interpretation: if a run or evaluation raises an exception, the pair becomes NOT_EVALUABLE even if the pair's QS check would otherwise be NOT_APPLICABLE. Requirements: Preserve the exception, stage, affected run ID and process log. Do not silently retry, replace a run, or treat NOT_APPLICABLE as overriding an execution error. Keep QS applicability, dynamic validity and overall evaluation status as separate concepts. Implement a regression test for this precedence rule."
- **Owner rulings and decisions.** I-6 (above) requires the NOT_EVALUABLE class and keeps the exception, stage, run ID and process log. The owner decided the optional sub-question of `18_owner_decision_matrix_I1_I6.md` §3.5 on 2026-10-29 in line with that matrix's I-6b column, headed "always `NOT_EVALUABLE_CONDITION_ERROR`": an attempted run that raised gives `NOT_EVALUABLE_CONDITION_ERROR` (§1.15). The owner also decided the scope after a failure of the separate recomputation or its fold (§1.16).
- **As applied.** A pair with an exception whose label would otherwise be `NOT_APPLICABLE_QS_INFEASIBLE`, `NOT_APPLICABLE_PROFILE_UNAVAILABLE`, PASS, REPORTED_ONLY or FAIL (review R8-1) is `NOT_EVALUABLE_CONDITION_ERROR` (AMB-29(d)). There is one exception: after a failure of the separate recomputation or its fold, a PASS, FAIL or REPORTED_ONLY that used energy the separate recomputation did not confirm is `NOT_EVALUABLE_RUN_INVALID` (AMB-31, I-4, §1.12). `NOT_EVALUABLE_RUN_MISSING` (AMB-29(b)), `NOT_EVALUABLE_QS_UNDEFINED` (AMB-29(c)) and `NOT_EVALUABLE_RUN_INVALID` (AMB-31) remain applicable under their own rules. After an exception no pair becomes `NOT_APPLICABLE_*` or PASS.
- **Implementer reading (not an owner ruling), for the owner's confirmation.** It changes no branch outcome, which is INCONCLUSIVE either way:
  - (a) every recorded stage of a pair counts as "a run or evaluation": `run`, `run_report`, `qs_screen` with its per-piece diagnosis (review R9-1), `classify`, `qs_vs_dynamic`, `condition_report` and the condition-level stage;
  - (b) after an exception at a stage other than one of its runs, a pair already `NOT_EVALUABLE_RUN_MISSING`, `NOT_EVALUABLE_QS_UNDEFINED` or `NOT_EVALUABLE_RUN_INVALID` keeps that label.
- **A measured failure is never hidden.** The label before the exception rule is kept in `qs_vs_dyn_pair_status_before_error`, and a valid arm's failure in `qs_vs_dyn_fail_arms`. This holds on every exception path: the in-process override, the `condition_report` relabel, a `qs_vs_dynamic`-stage exception (the arm results computed before it are kept) and a fold relabel after a failure of the separate recomputation or of the fold (review R9-2). Such failures are counted as `fail_before_exception` in `qs_dynamic_accounting.csv`, and as `n_FAIL_before_exception` and `fail_before_exception_by_set` in `qs_dynamic_branch_outcomes.csv` (§6, §7.2). Every one of these outcomes makes the M0/M1 criterion INCONCLUSIVE, as a FAIL would.
- **Three separate concepts:**
  - QS applicability: `qs_vs_dyn_applicability`. It is `NOT_APPLICABLE_PROFILE_UNAVAILABLE` if a profile is missing; otherwise `NOT_APPLICABLE_QS_INFEASIBLE` if a profile fails the QS screen, even when the other arm's screen raised (review R8-10); otherwise `UNKNOWN` if a screen raised; otherwise `APPLICABLE`. `qs_eligible_pair` is True, False or None to match;
  - dynamic validity: the condition status, from §8.2 and the recomputations;
  - the evaluation status: `qs_vs_dyn_pair_status`.
  - The three are counted separately: applicability and evaluation status each add up to the planned pairs (§7.2; review R8-2).
- **Records.** The exception, its stage, the run ID or IDs and, for the separate recomputation, the process log are kept (§7). Nothing is retried or replaced.

### 1.15 I-6b: an attempted run that raised (owner decision 2026-10-29)
Owner's words: "The specific unresolved case is a QS-eligible pair whose run was attempted but raised an exception. For that case, the pair-level status must be: `NOT_EVALUABLE_CONDITION_ERROR`. It must not be labelled `NOT_EVALUABLE_RUN_MISSING`, because the run was attempted and an exception occurred. Keep the semantic distinction explicit: A genuinely absent run follows the existing missing-run path. An attempted run that raises follows the condition-error path. Either case remains NOT_EVALUABLE / INCONCLUSIVE as applicable. Neither may count as PASS. An exception must override a prior PASS when the standing I-6 rules require it. Do not retry silently, replace the original evidence, or change unrelated valid outcomes."
- A QS-eligible pair one of whose runs was attempted and raised (stage `run`) is `NOT_EVALUABLE_CONDITION_ERROR`, never `NOT_EVALUABLE_RUN_MISSING`. The pair evaluation's earlier label (`NOT_EVALUABLE_RUN_MISSING`, or a FAIL of the other, valid arm) is kept in `qs_vs_dyn_pair_status_before_error`, and a measured failure in `qs_vs_dyn_fail_arms` (§1.14).
- The missing-run path is unchanged: an eligible pair whose arm was executed but has no finite simulator energy, with no exception, is `NOT_EVALUABLE_RUN_MISSING` (AMB-29(b), §1.4). An arm not executed because its profile is missing stays on the profile path (`NOT_APPLICABLE_PROFILE_UNAVAILABLE`, AMB-29(a), §1.2).
- Both labels are NOT_EVALUABLE, so the M0/M1 criterion is INCONCLUSIVE; neither counts as PASS. The run is not retried, and its error, trace and run ID are kept (§1.6).
- This replaces the implementer reading of rev9 and rev10, which kept `NOT_EVALUABLE_RUN_MISSING` for this case. The decision answers the optional sub-question of `18_owner_decision_matrix_I1_I6.md` §3.5 in line with that matrix's I-6b column (headed "always `NOT_EVALUABLE_CONDITION_ERROR`").

### 1.16 I-6: scope after a failure of the separate recomputation or its fold (owner decision 2026-10-29)
Owner's words: "Apply this owner decision to a failure of the separate recomputation or its fold: Only a pair currently classified as `NOT_APPLICABLE_*` with an actually executed run is eligible for the I-6 relabelling described here. Such a pair must not retain N/A when the relevant execution/evaluation exception requires a NOT_EVALUABLE classification. Preserve the existing handling of a genuinely missing run; do not conflate it with an executed run. Preserve the applicable `RUN_INVALID` and NOT_EVALUABLE classifications when required by the existing rules. Do not silently convert either to N/A or PASS. Both separate recomputations must confirm a run before its energy is usable for the QS check. Do not invent replacement energy values, use invalid energy as confirmatory evidence, or change unrelated statuses."
- After a failure of the separate recomputation (an exit other than 0 or 1, a launch failure, a missing or unreadable output) or of its fold, a `NOT_APPLICABLE_*` pair with an actually executed run becomes `NOT_EVALUABLE_CONDITION_ERROR` (its N/A label kept in `qs_vs_dyn_pair_status_before_error`). A `NOT_APPLICABLE_*` pair none of whose runs was executed keeps its label (`_na_pair_not_evaluable`, called from `fold_separate_recomputation` and `fold_failed`).
- A PASS, FAIL or REPORTED_ONLY that used energy the separate recomputation did not confirm becomes `NOT_EVALUABLE_RUN_INVALID` (AMB-31, I-4, §1.12), with its earlier label in `qs_vs_dyn_pair_status_before_error`. `NOT_EVALUABLE_RUN_MISSING`, `NOT_EVALUABLE_QS_UNDEFINED`, `NOT_EVALUABLE_RUN_INVALID` and `NOT_EVALUABLE_CONDITION_ERROR` stay. No label becomes `NOT_APPLICABLE_*` or PASS.
- Both recomputations must confirm a run before the QS check uses its energy: the in-process one (`run_condition`) and the separate one (the fold) (I-4, §1.12). No energy value is replaced or invented.
- Implementation: the executor passes the run IDs it executed. A direct call of the folds without them treats every N/A pair as executed, which fails closed; the executor never makes such a call.

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
| FAIL | `FAIL` | eligible; a **valid** arm exceeds 1 % (even if the other arm is not valid), and no run or evaluation of the pair raised (otherwise NOT_EVALUABLE, I-6) | INCONCLUSIVE (protocol §9), in any set |
| — | `REPORTED_ONLY` | M2 only: eligible, both arms valid, ratio defined | none (M2 reported only); for M0/M1 an inconsistency that blocks PASS |
| NOT_APPLICABLE | `NOT_APPLICABLE_QS_INFEASIBLE` | a profile fails the QS screen (N-A2) | outside the nominal cells: none, neither pass nor fail. In a required nominal cell it cannot count as PASS, so INCONCLUSIVE (I-1). The condition's dynamic status is unchanged. An exception in the pair makes it `NOT_EVALUABLE_CONDITION_ERROR` (I-6) |
| NOT_APPLICABLE | `NOT_APPLICABLE_PROFILE_UNAVAILABLE` | a profile does not exist (AMB-29(a)), whatever the other profile's screen result; the condition keeps its explicit failure status | outside the nominal cells: none; counted, never a PASS (owner ruling I-2). In a required nominal cell it cannot count as PASS, so INCONCLUSIVE (I-1). An exception in the pair makes it `NOT_EVALUABLE_CONDITION_ERROR` (I-6) |
| NOT_EVALUABLE | `NOT_EVALUABLE_RUN_MISSING` | eligible; an arm was executed but its simulator energy is not finite, with no exception (the missing-run path). An attempted run that raised is `NOT_EVALUABLE_CONDITION_ERROR` (owner decision I-6b, §1.15) | INCONCLUSIVE (AMB-29(b)) |
| NOT_EVALUABLE | `NOT_EVALUABLE_RUN_INVALID` | eligible; an arm's simulator energy is finite but its run fails §8.2 (non-finite states included) or a recomputation | INCONCLUSIVE (AMB-29(b), AMB-31) |
| NOT_EVALUABLE | `NOT_EVALUABLE_QS_UNDEFINED` | eligible; QS energy per reference km ≤ 0 (or d_ref ≤ 0, labelled by its own term) | INCONCLUSIVE (AMB-29(c)) |
| NOT_EVALUABLE | `NOT_EVALUABLE_CONDITION_ERROR` | an exception before or during the pair evaluation, the QS screen included, or while recording its result; or an exception in a run or its evaluation of a pair whose label would otherwise be `NOT_APPLICABLE_*`, PASS, REPORTED_ONLY or FAIL (I-6); or a QS-eligible pair one of whose runs was attempted and raised (owner decision I-6b, §1.15); or a `NOT_APPLICABLE_*` pair with an actually executed run after a failure of the separate recomputation or its fold (owner decision of 2026-10-29, §1.16). QS applicability is reported separately (`qs_vs_dyn_applicability`) | INCONCLUSIVE (AMB-29(d), I-6) |

For M2 every label is used the same way and the M2 branch stays reported only. An unknown status raises an error and is never counted.

**Order with the separate recomputation:** the pair status is set in process. After the separate recomputation, a PASS, FAIL or REPORTED_ONLY that used the energy of an arm the separate recomputation does not confirm becomes `NOT_EVALUABLE_RUN_INVALID`; the in-process value is kept in `qs_vs_dyn_pair_status_in_process`. A FAIL of a confirmed arm stays a FAIL. If the separate recomputation fails or its fold raises, a `NOT_APPLICABLE_*` pair with an executed run becomes `NOT_EVALUABLE_CONDITION_ERROR` (I-6), and a relabelled PASS, FAIL or REPORTED_ONLY keeps its label in `qs_vs_dyn_pair_status_before_error`.

## 3. A QS-only status is not a run status

| Situation | QS-versus-dynamic check | Condition status and energy role |
|---|---|---|
| Both runs pass §8.2 and both recomputations; a profile fails the QS screen | `NOT_APPLICABLE_QS_INFEASIBLE` | `COMPARABLE`; energy confirmatory |
| Both runs valid; QS energy ≤ 0 | `NOT_EVALUABLE_QS_UNDEFINED` | `COMPARABLE`; energy confirmatory (AMB-29(c): not invalidated) |
| Both runs valid; the pair's QS evaluation raised | `NOT_EVALUABLE_CONDITION_ERROR` | `COMPARABLE`; energy confirmatory |
| Both runs valid; the QS screen (or its plant) raised before the runs | `NOT_EVALUABLE_CONDITION_ERROR` | both runs still executed; `COMPARABLE`; energy confirmatory |
| Both runs valid; recording the condition's result raised | `NOT_EVALUABLE_CONDITION_ERROR` (the label it would otherwise have, `NOT_APPLICABLE_*` included, is kept in `qs_vs_dyn_pair_status_before_error`) | unchanged: the executed runs keep their records and the condition keeps its status |
| Both runs executed; classifying the pair (`classify_pair`) raised | `NOT_EVALUABLE_CONDITION_ERROR` (I-6), whatever the label would otherwise be, a FAIL included (kept in `qs_vs_dyn_pair_status_before_error`); in a required nominal cell a PASS label on a condition that is not `COMPARABLE` would not count either (I-1, §6) | the condition is `ERROR`, so not `COMPARABLE`, and no energy is confirmatory; the executed runs keep their records |
| QS-eligible pair; one attempted run raised (the other arm valid, a FAIL included) | `NOT_EVALUABLE_CONDITION_ERROR` (owner decision I-6b, §1.15); the earlier label (`NOT_EVALUABLE_RUN_MISSING`, or the FAIL) is kept in `qs_vs_dyn_pair_status_before_error`, a FAIL also in `qs_vs_dyn_fail_arms` | `ERROR`; no energy is confirmatory; the other arm's run keeps its record |
| A QS-infeasible pair in a required nominal cell | `NOT_APPLICABLE_QS_INFEASIBLE`; the M0/M1 branch is INCONCLUSIVE (I-1) | unchanged, for example `COMPARABLE` with confirmatory energy: the ruling never makes it dynamically infeasible |
| A run fails a §8.2 criterion | `NOT_EVALUABLE_RUN_INVALID` if eligible | `B0_INVALID_EXCLUDED`, `INVALID_COMPARISON`, or on P3 `BASELINE_INFEASIBLE_ON_P3` / `ECO_INFEASIBLE_ON_P3`; that run's energy `DIAGNOSTIC_ONLY_RUN_INVALID` |
| A run is not confirmed by a recomputation | `NOT_EVALUABLE_RUN_INVALID` if eligible | `RECOMPUTATION_DISAGREEMENT`; `DIAGNOSTIC_ONLY_RECOMPUTATION_NOT_CONFIRMED` |
| A profile fails the QS screen or is missing, and a run or its evaluation raised (the QS screen and its diagnosis included) | `NOT_EVALUABLE_CONDITION_ERROR` (I-6); the N/A label is kept in `qs_vs_dyn_pair_status_before_error`, and applicability in `qs_vs_dyn_applicability` | `ERROR` if a run or the classification raised; unchanged after an exception in the QS screen, its diagnosis or a report; `PROFILE_UNAVAILABLE` / `BASELINE_UNAVAILABLE` come first. A run that raised supplies no confirmatory energy |
| A profile fails the QS screen or is missing, and the separate recomputation fails, or its fold raises | `NOT_EVALUABLE_CONDITION_ERROR` (I-6) if the pair has an actually executed run; otherwise its N/A label (owner decision of 2026-10-29, §1.16) | unchanged, or `RECOMPUTATION_DISAGREEMENT` if it was `COMPARABLE` (§7.8); no energy is confirmatory |
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

The QS-versus-dynamic check uses an arm's energy under the same rule: only if the run passes §8.2 and its in-process recomputation, and, after the fold, the separate recomputation (owner ruling I-4, §1.12). An arm that fails §8.2 or the in-process recomputation has its QS-versus-dynamic value only in `qs_vs_dyn_pct_diagnostic_invalid_run`.

**In-process and final values.** `evaluation.csv` and `conditions/<id>.json` are written as each condition finishes, before the separate recomputation. Their per-arm `qs_vs_dyn_pct` and `qs_vs_dyn_pair_status` are in-process values. For an arm the separate recomputation does not confirm, the final pair status is the one in `conditions.csv` (`NOT_EVALUABLE_RUN_INVALID`, with the in-process value in `qs_vs_dyn_pair_status_in_process`). Only `conditions.csv` and `energy_roles.csv` give final values. After an exception while recording a condition's result (`condition_report`), the per-arm `qs_vs_dyn_pair_status` in `evaluation.csv` can keep the label from before the relabel; `conditions.csv` and `conditions/<id>.json` give `NOT_EVALUABLE_CONDITION_ERROR` (review R9-8).

### 4.2 No relative saving percentage with a non-positive denominator (AMB-29(c))
No relative **saving** percentage is computed with a denominator that is ≤ 0 or not finite. The value is recorded as not evaluable, with the exact term and the raw values:

| Quantity | Denominator | When ≤ 0 |
|---|---|---|
| QS vs dynamic, 100·(e_dyn − e_QS)/e_QS | e_QS per reference km (or d_ref) | `diff_pct` empty; pair `NOT_EVALUABLE_QS_UNDEFINED` |
| paired ΔE_rel, 100·(e_B3 − e_B0)/e_B0 (`paired_delta`) | the B0 energy per reference km | `dE_rel_pct` None, `dE_rel_status` `NOT_EVALUABLE_DENOMINATOR_NOT_POSITIVE`; ΔE_abs still reported |
| planner S_found, S_max (protocol §5.4) and grid ΔS_found (§9) | E(v_b), the QS baseline energy | values None; `status` `NOT_EVALUABLE_DENOMINATOR_NOT_POSITIVE`; the grid check is not passed |
| dynamic time-step check (§9) | uses two ΔE_rel values | a ΔE_rel that is not evaluable makes the check not evaluable (`passed` None), never a pass |

The first row is the ruling's direct object. The other rows apply its rule to the code's other relative saving percentages (owner ruling I-3, §1.11).

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
2. a pair in any set is **NOT_EVALUABLE** (AMB-29(b)–(d); I-6 included);
3. **a required nominal cell does not PASS individually** (owner ruling I-1). The required nominal cells are the motor's NOM pairs for L-R1 and for L-EVE. A cell that is absent from the record, appears more than once, is `NOT_APPLICABLE_QS_INFEASIBLE` or `NOT_APPLICABLE_PROFILE_UNAVAILABLE`, is `NOT_EVALUABLE_*`, is `REPORTED_ONLY`, belongs to a condition without a profile (`PROFILE_UNAVAILABLE` / `BASELINE_UNAVAILABLE`, whatever its pair label), or carries a PASS label on a condition that is not `COMPARABLE`, is missing or invalid mandatory evidence and never counts as PASS (AMB-30 items 5, 6). A PASS in any other set, INS included, never substitutes (AMB-30 items 1, 2), and with no nominal PASS there is no pass by vacuity;
4. a planned pair of the motor is missing from the record;
5. a pair is labelled `REPORTED_ONLY`, which applies to M2 only.

Otherwise the branch **PASSes**: both required nominal cells PASS and no applicable check in any set fails or is not evaluable. Outside NOM, a `NOT_APPLICABLE_*` pair is neither a pass nor a failure (N-A2; owner ruling I-2 for a missing profile). A QS-infeasible profile is never reclassified as dynamically infeasible: the condition keeps its §8.2 status.

Failures and not-evaluable pairs are **counted per set and never averaged** (AMB-30 item 4). `qs_dynamic_branch_outcomes.csv` reports, per motor: the count of every status; `required_nominal_cells`, `n_required_nominal_cells` and `n_PASS_nominal`; `n_PASS_other_sets`; `nominal_L-R1` and `nominal_L-EVE`; `nominal_evidence_missing`; `fail_by_set`, `not_evaluable_by_set`, `pass_by_set` and `not_applicable_by_set`; `n_FAIL_before_exception` and `fail_before_exception_by_set` (a measured FAIL that an exception made NOT_EVALUABLE, §1.14); `planned_pairs_missing_from_record`; the outcome and its reasons. A row is written for every motor branch, including one with no pair in the record. No threshold is changed and S2 is not used to tune the planner (AMB-30 item 7).

## 7. Denominator and exclusion reporting
Nothing is dropped from a denominator. Every exclusion is reported with its reason.
1. **Feasibility** (`feasibility_accounting.csv`; per motor and set, per motor, overall): planned conditions and runs; runs executed and not executed (and of those, profile failures); runs §8.2-valid and invalid; profile-failure conditions; conditions eligible for and excluded from the paired endpoint; one count per condition status and per energy role. The status counts add up to the planned conditions and the role counts to the planned runs.
2. **QS-versus-dynamic** (`qs_dynamic_accounting.csv`; per motor and set, per motor). Each row adds up to its planned pairs in two separate ways (review R8-2; owner ruling I-6 keeps them apart):
   - by QS applicability, from `qs_vs_dyn_applicability`: `qs_eligible_pairs`, `qs_ineligible_pairs` (split into B0 only, B3 only and both), `not_applicable_profile_unavailable` and `qs_eligibility_unknown`;
   - by pair status: `qs_check_pass`, `qs_check_fail`, `qs_check_reported_only`, `qs_check_not_applicable_qs_infeasible`, `qs_check_not_applicable_profile_unavailable` and the four `not_evaluable_*` counts.
   - A pair that an exception made NOT_EVALUABLE stays in its applicability class, with its failed arms in the B0/B3/both split (review R9-4). An unknown pair status raises. Also reported: `fail_before_exception` (§1.14), pairs passing on dynamic-valid arms, and dynamic-valid and `COMPARABLE` pairs.
3. **Branch outcomes** (`qs_dynamic_branch_outcomes.csv`, §6).
4. **Energy roles** (`energy_roles.csv`, §4.1): one row per planned run with its §8.2 flags, failed criteria and recomputation result.
5. **Record invariant** (`manifest.json` → `record_invariant`): every scheduled condition and run has exactly one record, in schedule order. A violation is recorded in `errors.csv` and the manifest; it would be a defect, never a pass. It does not stop the run (protocol §10.4: nothing is retried or replaced).
6. **Errors** (`errors.csv`): every exception with its traceback and its **stage** (review R7-3: every row has one), and its run ID or run IDs where they apply. `diagnostic_path` names the log where one exists (the separate recomputation and its fold). Output writes (reviews R7-5, R8-5):
   - Every failed write of an output file is a row with stage `write <file>` and is listed in `manifest.json` → `output_write_failures`; the other outputs are still written. This covers each `conditions/<id>.json`, `conditions.csv`, `planner_checks.csv`, `runs.csv`, `evaluation.csv`, `energy_roles.csv`, `feasibility_accounting.csv`, `h3_verdict_eligibility.json`, `qs_dynamic_accounting.csv`, `qs_dynamic_branch_outcomes.csv`, `stop_compliance.csv` and `recomputation.json` (condition `OUTPUT-WRITE`), and the process log `recomputation_independent_process.log` (condition `SEPARATE-RECOMPUTATION`).
   - A failed write of a planner file is recorded where it happens: during a condition it is a condition-level exception (stage `condition`; the condition is `ERROR`), during the grid check a row with stage `planner grid check`.
   - A failure to write `errors.csv` itself goes to the manifest (`errors_csv_write_failure`). A failure to write the manifest or the post-run hash list stops the run with an error.
7. **Runs** (`runs.csv`): `executed` means the run was simulated and returned its record (evaluated, or kept unevaluated with its raw trace when its states are non-finite). A run whose simulation or evaluation raised has `executed=False`, its error in `errors.csv`, and its kept trace and specification files in `retained_files`. Its simulator energy is in the kept trace, not in `runs.csv`, because the run raised before returning its summary.
8. **Separate recomputation:** the script exits 0 (every recomputed run passes), 1 (a run fails a protocol check), 3 (an independence violation or a refusal) or 4 (an exception, including one while importing its modules or reading its arguments). Only 0 and 1 are results.
   - **Ledger (review V6-1).** The process's full output is kept in `recomputation_independent_process.log`. A failure before, during or at the end of the process is written to `errors.csv` (condition `SEPARATE-RECOMPUTATION`) with its stage and that log as `diagnostic_path`. The failures covered are: a launch failure, an exit other than 0 or 1, a missing or unreadable output file, and an executed run missing from the output.
   - **Per run (review R7-4).** One more row goes to `errors.csv` for every executed run that the separate recomputation does not confirm as recomputed, with its run ID, condition, stage and log. After a process failure, including an exit other than 0 or 1 after a complete output, that is every executed run. Otherwise it is each run absent from the output or recorded there as not recomputed (with its reason).
   - **Manifest.** `manifest.json` → `separate_recomputation` records the exit, the problem, the log and the number of runs not recomputed.
   - **Fail-closed.** Every unrecomputed run stays unconfirmed. If applying the recomputation (the fold) itself raises, no condition stays `COMPARABLE` or eligible for the paired endpoint, and no unconfirmed QS PASS or FAIL stands. After a process failure or a fold exception, a `NOT_APPLICABLE_*` pair with an actually executed run becomes `NOT_EVALUABLE_CONDITION_ERROR` (I-6; owner decision of 2026-10-29, §1.16), and a relabelled PASS, FAIL or REPORTED_ONLY keeps its label in `qs_vs_dyn_pair_status_before_error` (review R9-2). The summary outputs are still written.
9. **Verdict eligibility** (`h3_verdict_eligibility.json`, §8).

## 8. Overall H3 verdict (protocol §8.1; AMB-32)
The §8.1 denominators are fixed and never reduced: 6 nominal S2 P1 cells (M0, M1, M2 × L-R1, L-EVE) and 32 sensitivity draws for each of M0 and M1.
- **SUPPORTED** needs a `COMPARABLE` pair in all six nominal cells, at least 29 of 32 sensitivity draws for M0 and for M1 separately, and every §9 check passing, together with the energy conditions of §8.1.
- **NOT SUPPORTED** needs a `COMPARABLE` pair in all six nominal cells, ΔE_rel > −1.0 % in every motor branch for the nominal S2 P1 runs, and all checks passing (AMB-32).
- Otherwise **INCONCLUSIVE**. A nominal cell that is missing, invalid or not evaluable makes the verdict INCONCLUSIVE, never NOT SUPPORTED. No negative finding is inferred from missing data, and no verdict is reached by omission. A `COMPARABLE` nominal cell whose ΔE_rel is not evaluable (§4.2) satisfies neither side of the −1 % rule, so it also leads to INCONCLUSIVE (owner ruling I-3, §1.11). This is a rule for the later analysis: no code in this release computes the verdict from energy, and `paired_delta` only refuses the percentage.
- An INCONCLUSIVE QS-versus-dynamic criterion makes the verdict INCONCLUSIVE through "every check in §9 passes", even when every nominal cell is `COMPARABLE` with confirmatory energy (§3). The criterion is INCONCLUSIVE when there is any `NOT_EVALUABLE_*` pair, a FAIL, or a required nominal cell that does not PASS (I-1).

`h3_verdict_eligibility.json` records, without reading any energy value, which verdicts remain possible from the condition statuses and the branch outcomes:
- For each nominal cell without a comparable pair it records the cell, its status and its reason (`nominal_missing_evidence`).
- It checks the I-1 ruling again from the condition rows, independently of the branch outcome. For M0 and M1, every required nominal cell's pair status must be PASS (`qs_vs_dynamic_nominal_cells`); otherwise SUPPORTED and NOT SUPPORTED are both ruled out.

It computes no energy difference. The other §9 checks can only remove possibilities.

## 9. Owner rulings on I-1 to I-6

All six points are decided by the owner (§1.9 to §1.14), and so are the two questions of 2026-10-29 (§1.15, §1.16). No owner decision on the content of this amendment is open: `owner_decisions_open` in the machine block and `campaign.OWNER_DECISIONS_OPEN` are empty, and `config/code_review_status_v12.json` → `open_owner_decisions` is empty. The interpretations considered are in `18_owner_decision_matrix_I1_I6.md`. The two implementer readings that rev10 listed were decided by the owner on 2026-10-29: the label became `NOT_EVALUABLE_CONDITION_ERROR` (§1.15), and the scope was confirmed (§1.16). One implementer reading remains for the owner's confirmation (`implementer_readings_for_owner_confirmation`): which stages count as "a run or evaluation", and that an existing NOT_EVALUABLE label stays after an exception at a later stage (§1.14). It changes no outcome.

| ID | Ruling (§) | What it decides (review R7-1) | Implementation |
|---|---|---|---|
| I-1 | every required nominal S2 cell (NOM; L-R1 and L-EVE) must PASS individually for M0 and M1 (§1.9) | the M0/M1 QS branch outcome and the verdict's QS requirement | `checks.branch_qs_dynamic_outcome`; checked again in `checks.h3_verdict_eligibility` (§6, §8) |
| I-2 | outside NOM, a missing profile does not by itself make the QS check INCONCLUSIVE; it is counted and never a PASS (§1.10) | the effect of a `NOT_APPLICABLE_PROFILE_UNAVAILABLE` pair outside NOM on the QS branch outcome | `checks.branch_qs_dynamic_outcome` (§6); `feasibility_accounting` (§7) |
| I-3 | no energy-saving percentage with a denominator ≤ 0 (§1.11) | **whether a saving percentage is computed at all**: the QS ratio, ΔE_rel, S_found, S_max and grid ΔS. It changes no QS label | `checks.non_positive_term`, `qs_vs_dynamic`, `paired_delta`, `scenario_totals`, `grid_convergence`, `timestep_check` (§4.2) |
| I-4 | both runs confirmed by the separate recomputation before the QS check uses their energy (§1.12) | which arms the QS check may use | `campaign.run_condition`; `fold_separate_recomputation` (§2, §4.1) |
| I-5 | the label `NOT_EVALUABLE_QS_UNDEFINED` is kept (§1.13) | vocabulary only; changes no outcome | `checks.QS_UNDEFINED` (§2) |
| I-6 | an exception makes the pair NOT_EVALUABLE even if its QS check would otherwise be NOT_APPLICABLE (§1.14) | the pair label when a run or its evaluation raised | `campaign.run_condition`, `fold_separate_recomputation`, `fold_failed`; `qs_vs_dyn_applicability`; `checks.qs_dynamic_accounting` (§2, §3, §7.2) |
| I-6b | an attempted run that raised gives `NOT_EVALUABLE_CONDITION_ERROR`, never `NOT_EVALUABLE_RUN_MISSING` (owner decision 2026-10-29, §1.15) | the label of a QS-eligible pair whose run raised | `campaign.run_condition` (§2, §3) |
| I-6 scope | after a failure of the separate recomputation or its fold only a `NOT_APPLICABLE_*` pair with an actually executed run is relabelled (owner decision 2026-10-29, §1.16) | which N/A pairs become NOT_EVALUABLE after such a failure | `campaign._na_pair_not_evaluable`, `fold_separate_recomputation`, `fold_failed`, `execute_schedule` (§2, §3, §7.8) |

None of these rulings changes a threshold, a condition status, an energy role, or a planned-run, feasibility, verdict or QS-accounting denominator: each still adds up to its planned total (§7). I-3 can change whether a percentage exists. The others change only a QS-versus-dynamic label, its per-status count, or the branch outcome.

## 10. Effect on the planned 170-run schedule
None. The 170 official runs, their IDs, sets, plants, profiles, gains (nominal P1 gain for every SEN draw, AMB-14), tolerances and numerics are unchanged, and so is the schedule's SHA-256. No run is added, removed, retried, replaced or made conditional. Smoke-test runs stay excluded (D4). S2 stays held out and is not used for tuning.

## 11. Location rule for campaign mode
Unchanged from rev3 §9: campaign mode runs only when the running code's directory is, by resolved path, `R4_20261028_campaign/`.

## 12. Changes

### 12.1 Since rev10 (complete list)

| Change | Basis | Effect |
|---|---|---|
| `campaign.run_condition`: when a run was attempted and raised (stage `run`), the pair is `NOT_EVALUABLE_CONDITION_ERROR` also where the pair evaluation gave `NOT_EVALUABLE_RUN_MISSING`; the earlier label goes to `qs_vs_dyn_pair_status_before_error`. In rev13 such a QS-eligible pair kept `NOT_EVALUABLE_RUN_MISSING`. `NOT_EVALUABLE_RUN_MISSING` stays for an executed run without a finite energy and no exception. Exceptions at other stages are unchanged | owner decision I-6b (2026-10-29) | label only; no outcome effect (NOT_EVALUABLE either way) |
| `campaign._na_pair_not_evaluable`, `fold_separate_recomputation`, `fold_failed`: the docstrings cite the owner's decision on the relabelling scope; the behaviour is unchanged from rev13 (only a `NOT_APPLICABLE_*` pair with an executed run is relabelled) | owner decision of 2026-10-29 (§1.16) | none |
| `campaign.fold_failed`: `conds` is indexed only within its length; a row without a matching condition is treated as executed (fail-closed), so the fallback cannot raise on the indexing | review R10-4 | robustness |
| `IMPLEMENTED_2` → `AMB_29_condition_error`: rewritten as the owner's I-6 ruling (its own words), the owner's decisions I-6b and on the relabelling scope (2026-10-29), the rules as applied (with RUN_INVALID after a recomputation or fold failure, and the NOT_EVALUABLE labels that remain applicable), and one sentence labelled "Implementer reading (not an owner ruling)" | review R10-1; owner decisions of 2026-10-29 | — |
| `config/code_review_status_v12.json`: the R10 findings; the owner's decisions of 2026-10-29 in `owner_rulings_implemented`; the two former implementer readings in `implementer_readings_decided_by_owner`; one remaining implementer reading; `open_major` stays 6, with `owner_acceptance_of_major_closures` "not recorded"; `reviews_pending` names the review of release attempt 11 | reviews R10-1 to R10-4; owner decisions of 2026-10-29 | record |
| Text: header (R10-3: the counts of the attempt-10 findings stated exactly); §1.1 to §1.3 headings ("first stated in", R10-3) and the rev10 sentence moved out of the N-A2 ruling paragraph; §1.4, §1.6, §1.12, §1.14 (R10-1); new §1.15 and §1.16 (the owner's words); §2, §3, §7.8, §9, §12, §13, §15 | owner decisions of 2026-10-29; reviews R10-1, R10-3 | wording |
| Tests: new `tests/test_owner_decisions_v14.py`. Updated: `test_owner_decisions_v11.py` (I6EL and I6FL expect `NOT_EVALUABLE_CONDITION_ERROR`; one test renamed), `test_owner_rulings_v7.py` and `test_owner_rulings_v8.py` (the attempted-run exception cases expect `NOT_EVALUABLE_CONDITION_ERROR`), `test_review_fixes_v13.py` (the v11 status file and the rev10 candidate read by path; one test renamed) | owner decision I-6b; reviews R10-1 to R10-4; versioning | — |
| `DRAFT_AMENDMENT_2` → this candidate; `CAMPAIGN_CONFIG` → `campaign_config_v14_DRAFT.json`; `REVIEW_STATUS` → `code_review_status_v12.json` | versioning | — |

**Not changed:**
- the review notes R7-11 and R7-13 (optional hardening), V6-4 and R5-14, and the partly fixed R5-6 (§7.7);
- R8-11: `18_owner_decision_matrix_I1_I6.md` is the pre-ruling record and is not edited;
- R9-8: documented in §4.1; the code is unchanged;
- `checks.py` and `recompute_from_traces.py`.

**R10-2** is addressed by tests in `tests/test_owner_decisions_v14.py` whose first call works on the old code, and by the mutation runs in `logs/zz_mutation_check_*`.

The file-level comparison with the rev10 state (`archive/rev13_attempt10_20261029_0629/`) is `logs/zz_code_changes_rev13_to_rev14.csv`; the byte-level line-ending check is `logs/zz_line_endings_rev13_to_rev14.csv`.

### 12.2 Earlier changes

The changes from rev4 to rev5, and each later step up to rev9 to rev10, are listed in §12 of the rev5 to rev10 candidates, all kept unchanged.

## 13. Blockers retained
The campaign remains **BLOCKED** until all of these hold:
1. The rev7 to rev14 changes pass an independent review, and the owner accepts the closure. The six MAJOR findings R5-1, R5-2, R8-1, R8-2, R8-3 and R9-1 are verified fixed by AI-agent reviews (R9-1 by the review of release attempt 10); the owner's acceptance is not recorded. The review of release attempt 11 and the owner's acceptance are pending: `config/code_review_status_v12.json` keeps `open_major` 6 and a `reviews_pending` item until then, and each blocks. An AI-agent review is not a human audit.
2. The owner approves and issues amendment 2 (§15).
3. A release attempt of the final code passes all mandatory tests and reviews, and its manifest and protocol hashes are verified.
4. The approved attempt is promoted to the campaign root with its own protocol §10.1 gate, by an owner-approved procedure.
5. The owner explicitly authorises execution in `release/campaign_authorization.json`, with the scope "execute the 170-run H3 campaign of protocol v1 amendments 1 and 2" and the keys `amendment_sha256`, `amendment_2_sha256` and `pre_run_hashes_sha256`.

## 14. Reporting rules kept
Completed, invalid, infeasible, excluded, profile-failed and not-evaluable conditions are reported in separate rows (protocol §10.5). ΔE_abs and ΔE_rel are reported only for `COMPARABLE` conditions, always together, with trip time.

## 15. To issue (owner)
No owner decision on the content is open (§9); the owner may confirm the implementer reading of §1.14. Issuing and approving are the owner's decisions:
1. Copy the final text to `R4_20261028_campaign/release/03_R4_protocol_v1_amendment_2.md`, set `"status": "APPROVED"` in the block, and record its SHA-256. The block must otherwise equal `IMPLEMENTED_2`, value for value.
2. Write `R4_20261028_campaign/release/amendment_2_approval.json` with `approved_by`, `date` and `amendment_sha256`.
3. The steps of §13 follow: the review closure, promotion with its own §10.1 gate, and the separate campaign authorisation.

## 16. Machine-readable block

`code/r4h3/campaign.py` (`IMPLEMENTED_2`) reads this block. Every value must equal what the code implements: a difference or an unknown key is an error, never an override.

<!-- r4h3-amendment-block -->
```json
{
 "amendment": "R4 protocol v1 amendment 2 (N-A2, AMB-29(a)-(d), AMB-30, AMB-31, AMB-32, I-1 to I-6), candidate rev11",
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
 "N_A2_failed_check_record": "every failing piece with its failed QSPlant.step sub-check(s) (drive torque, battery discriminant, discharge current) and their values at each Gauss node; if that diagnosis raises, the piece says so and the exception is recorded in errors.csv (stage qs_screen, review R9-1)",
 "AMB_29_profile_unavailable": "owner ruling 2026-10-28: the condition keeps its explicit PROFILE_UNAVAILABLE or BASELINE_UNAVAILABLE status and counts in every planned-run, feasibility and verdict denominator; never COMPARABLE, never a paired comparison, never removed; only the pair's QS-vs-dynamic check is NOT_APPLICABLE_PROFILE_UNAVAILABLE (its applicability condition is objectively unmet), which is not a pass",
 "AMB_29_eligible_run_missing": "owner ruling 2026-10-28 (AMB-29(b)): NOT_EVALUABLE_RUN_MISSING (class NOT_EVALUABLE) -> the M0/M1 branch is INCONCLUSIVE for this criterion; M2 stays reported only; the pair stays in every planned-run denominator and every available energy trace is kept for diagnostics",
 "AMB_29_qs_energy_undefined": "owner ruling 2026-10-28 (AMB-29(c)): QS energy per reference km <= 0 -> NOT_EVALUABLE_QS_UNDEFINED -> the M0/M1 branch is INCONCLUSIVE for this criterion; M2 stays reported only; the raw values and the exact non-positive term are recorded; no percentage, replacement denominator, epsilon, absolute value or substitute threshold; the runs' dynamic result is unaffected and protocol 8.2 still applies to it. Owner ruling I-5 (2026-10-28): the label NOT_EVALUABLE_QS_UNDEFINED is kept unchanged; the owner's QS_COMPARISON_NOT_EVALUABLE is the NOT_EVALUABLE class",
 "AMB_29_condition_error": "owner ruling 2026-10-28 (AMB-29(d)): an exception before or during the pair evaluation, including the QS screen -> NOT_EVALUABLE_CONDITION_ERROR -> the M0/M1 branch is INCONCLUSIVE for this criterion; M2 stays reported only; both dynamic arms still run and are classified by protocol 8.2 alone; the error, stage, traceback, traces and run IDs are kept (errors.csv, conditions/, traces/); no retry, automatic replacement or substitute run; a rerun only under the protocol and an explicitly authorised procedure with a distinct run ID. Owner ruling I-6 (2026-10-28): if a run or evaluation raises an exception, the pair becomes NOT_EVALUABLE even if its QS check would otherwise be NOT_APPLICABLE; the exception, stage, affected run ID and process log are kept; no silent retry or replacement; NOT_APPLICABLE never overrides an execution error; QS applicability (qs_vs_dyn_applicability), dynamic validity (the condition status) and the evaluation status (qs_vs_dyn_pair_status) are kept separate. Owner decision I-6b (2026-10-29): a QS-eligible pair one of whose runs was attempted and raised an exception is NOT_EVALUABLE_CONDITION_ERROR, not NOT_EVALUABLE_RUN_MISSING; a genuinely absent run energy (an executed run without a finite simulator energy, no exception) stays NOT_EVALUABLE_RUN_MISSING (AMB-29(b)). Owner decision (2026-10-29) on a failure of the separate recomputation or its fold: only a NOT_APPLICABLE_* pair with an actually executed run becomes NOT_EVALUABLE_CONDITION_ERROR; a pair none of whose runs was executed keeps its NOT_APPLICABLE_* label. As applied under these rulings: a pair with an exception whose label would otherwise be NOT_APPLICABLE_*, PASS, REPORTED_ONLY or FAIL is NOT_EVALUABLE_CONDITION_ERROR, except that after a failure of the separate recomputation or its fold a PASS, FAIL or REPORTED_ONLY that used energy the separate recomputation did not confirm is NOT_EVALUABLE_RUN_INVALID (AMB-31, I-4); NOT_EVALUABLE_RUN_MISSING (AMB-29(b)), NOT_EVALUABLE_QS_UNDEFINED (AMB-29(c)) and NOT_EVALUABLE_RUN_INVALID (AMB-31) remain applicable under their own rules; no pair becomes NOT_APPLICABLE_* or PASS after an exception; the label before the exception rule is kept in qs_vs_dyn_pair_status_before_error, a measured failure in qs_vs_dyn_fail_arms and in the accounting (fail_before_exception, n_FAIL_before_exception). Implementer reading (not an owner ruling), for the owner's confirmation: (a) every recorded stage of a pair (run, run_report, qs_screen with its per-piece diagnosis, classify, qs_vs_dynamic, condition_report, condition) counts as a run or its evaluation; (b) after an exception at a stage other than one of its runs, a pair already NOT_EVALUABLE_RUN_MISSING, NOT_EVALUABLE_QS_UNDEFINED or NOT_EVALUABLE_RUN_INVALID keeps that label",
 "AMB_30_branch_scope": "owner ruling 2026-10-28 (strict): an applicable FAIL or a NOT_EVALUABLE_* pair in any preregistered set (NOM, P3, INS, CNV, SEN) makes the M0/M1 branch INCONCLUSIVE, counted per set, never averaged; a PASS in another set, the in-sample S1 set INS included, never substitutes for missing or failed nominal S2 evidence; a planned pair missing from the record blocks PASS. Owner ruling I-1 (2026-10-28): every required nominal cell of the branch (NOM; L-R1 and L-EVE) must individually PASS; an absent, duplicated, invalid, not-evaluable or NOT_APPLICABLE_* nominal cell, or one whose condition has no profile, cannot count as PASS and the branch is INCONCLUSIVE; a FAIL keeps the frozen protocol 9 consequence. Owner ruling I-2 (2026-10-28): outside NOM a missing profile (NOT_APPLICABLE_PROFILE_UNAVAILABLE) does not by itself make the QS check INCONCLUSIVE; it is never a PASS; the explicit missing-profile status stays counted in the planned-run and feasibility reporting and never yields a paired energy comparison",
 "I_1_required_nominal_cells": "owner ruling 2026-10-28: for M0 and M1 every required nominal cell on the held-out S2 set (NOM; L-R1 and L-EVE) must individually PASS the applicable QS-vs-dynamic check; a missing, invalid, unevaluable or NOT_APPLICABLE required nominal cell cannot count as PASS and the branch is INCONCLUSIVE; S1 never substitutes; a FAIL keeps the frozen consequence; thresholds unchanged; QS and dynamic feasibility stay distinct (a QS-infeasible profile is never reclassified as dynamically infeasible)",
 "AMB_31_energy_of_invalid_runs": "owner ruling 2026-10-28: energy of a run failing protocol 8.2, or not confirmed by its recomputation, is diagnostic only (energy_roles.csv DIAGNOSTIC_ONLY_*): never confirmatory, never credited to the paired endpoint, never used by the QS-vs-dynamic check. Owner ruling I-4 (2026-10-28): both runs must be confirmed by the separate recomputation (and by the in-process one) before the QS check uses their energy; an unconfirmed run supplies no confirmatory evidence for that check",
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
 "qs_applicability_values": [
  "APPLICABLE",
  "NOT_APPLICABLE_QS_INFEASIBLE",
  "NOT_APPLICABLE_PROFILE_UNAVAILABLE",
  "UNKNOWN"
 ],
 "qs_dynamic_accounting_classes": "review R8-2, owner ruling I-6: every row of qs_dynamic_accounting.csv adds up to its planned pairs two separate ways: by QS applicability (qs_eligible_pairs, qs_ineligible_pairs, not_applicable_profile_unavailable, qs_eligibility_unknown) and by pair status (qs_check_pass, qs_check_fail, qs_check_reported_only, qs_check_not_applicable_qs_infeasible, qs_check_not_applicable_profile_unavailable and the four not_evaluable_* columns); a pair made NOT_EVALUABLE by an exception stays in its applicability class",
 "non_positive_denominator_rule": "AMB-29(c) and owner ruling I-3 (2026-10-28), for every energy-saving percentage, the QS-vs-dynamic ratio (e_QS) and the others (paired dE_rel, B0 energy per reference km; planner S_found, S_max and grid dS, E(v_b)): none is computed with a denominator <= 0 or not finite; the value is not evaluable and the exact term and the raw values are recorded. The recomputation and shortfall tolerance comparisons of amendment 1 are not saving percentages and are unchanged",
 "record_invariant": "every scheduled condition and run has exactly one record (no drop, retry or replacement); a violation is recorded in errors.csv and the manifest",
 "separate_recomputation_exit_codes": "0 every recomputed run passes; 1 a run fails a protocol check; 3 independence violation or refusal; 4 exception, including one while importing or reading the arguments. Only 0 and 1 are results: any other exit leaves every run unconfirmed and is recorded in errors.csv with its stderr; a fold that raises leaves no condition COMPARABLE",
 "separate_recomputation_ledger": "reviews V6-1, R7-4: the process's full output goes to recomputation_independent_process.log; a launch failure, an exit other than 0 or 1, a missing or unreadable output file, or an executed run missing from the output is recorded in errors.csv with its stage and that log; every executed run the separate recomputation does not confirm as recomputed (all of them after a process failure) gets its own row with its run ID",
 "errors_ledger": "reviews R7-3, R7-5, R8-5: every errors.csv row has a stage; diagnostic_path where a process log exists; every failed output write (each conditions/<id>.json, conditions.csv and the process log included) is recorded with stage 'write <file>' and listed in manifest output_write_failures, and the remaining outputs are still written; a failed planner-file write during a condition is a condition-level exception; a failed errors.csv write is recorded in the manifest; a failed manifest or post-run hash-list write stops the run with an error",
 "owner_decisions_open": [],
 "planned_runs": {
  "NOM": 12,
  "P3": 12,
  "INS": 12,
  "CNV": 6,
  "SEN": 128,
  "total": 170
 },
 "note": "CANDIDATE rev11 - DRAFT - NOT APPROVED FOR RELEASE. Values must equal the implementation."
}
```
