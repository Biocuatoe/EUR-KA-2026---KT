# R4 H3: owner decisions for amendment 2 — rulings made and decisions still open (document 15)

**Date:** 2026-10-28. **Campaign status: BLOCKED.**

This document separates the decisions the owner has made from those still open, and gives the exact text the owner can use to issue the open rulings. Nothing here decides an open item on the owner's behalf. The handling the code applies today to an open item is labelled **proposed**.

**Sources read:**
- `14_amendment2_release_readiness_report.md`;
- `03_protocol_v1_amendment_2_DRAFT.md` (rev3, `fdaf193d…`, unchanged);
- `02_protocol_ambiguity_register.md` and `02b_protocol_ambiguity_register_addendum_amendment2.md`;
- the review reports in `review/` (`CR-A…`, `N-A2_review…`, `N-A2_verification…` 1–3);
- the frozen protocol v1 (§8.1, §9, §10.4);
- issued amendment 1;
- `code/r4h3/checks.py`, `code/r4h3/campaign.py` and the tests.

The candidate text proposed for issue is `03_protocol_v1_amendment_2_rev4_CANDIDATE.md`.

## 1. Decisions already made by the owner (binding)

| Decision | Date | Source | Where implemented |
|---|---|---|---|
| AMB-14 (nominal P1 gain for every SEN draw), AMB-15 (campaign directory), AMB-24 (§8.2 decides P3 feasibility), tolerances, S2 role, CR-A6 residual accepted | 2026-10-28 | issued amendment 1 and its approval record | amendment 1 `IMPLEMENTED` (unchanged) |
| AMB-16: a draw with no comparable pair does not count toward "≥ 29 of 32"; the denominator is 32 | determined (literal) | `02_protocol_ambiguity_register.md` (A1-14) | `checks.h3_verdict_eligibility` |
| **N-A2**: the §9 QS-vs-dynamic check applies only to a pair whose B0 and B3 profiles both pass the QS screen; otherwise `NOT_APPLICABLE_QS_INFEASIBLE`, neither pass nor fail | 2026-10-28 | owner ruling (report 14) | candidate rev4 §1.1 |
| **AMB-29(a)**: missing profile (verbatim below) | 2026-10-28 | owner ruling (this task) | candidate rev4 §1.2 |
| **AMB-31**: energy from a run failing §8.2 (verbatim below) | 2026-10-28 | owner ruling (this task) | candidate rev4 §1.3 |

**AMB-29(a), owner's words:**

> The owner rejects any interpretation in which a missing profile is classified as `NOT_APPLICABLE` for the overall experiment outcome. […] Profile generation failure or planner infeasibility must remain an explicit outcome and count toward the planned-run and feasibility reporting. A specific QS-versus-dynamic check may be `NOT_APPLICABLE` only where its preregistered applicability conditions are objectively unmet. An inapplicable check is not a pass. A missing profile must never generate a valid paired energy comparison. Do not silently remove failed profile generation from the planned denominator.

**How it is applied:**
- The condition keeps the explicit status `PROFILE_UNAVAILABLE` or `BASELINE_UNAVAILABLE` (existing statuses).
- It is counted in `feasibility_accounting.csv`, the D5 denominator and the §8.1 verdict denominators.
- It is never `COMPARABLE`, and `paired_delta` refuses it.
- Only the pair's QS-vs-dynamic check is `NOT_APPLICABLE_PROFILE_UNAVAILABLE`: N-A2's applicability condition, both profiles passing the QS screen, cannot hold for a profile that does not exist.

**AMB-31, owner's words:**

> The owner rejects using energy from a run that fails mandatory §8.2 requirements as a valid confirmatory energy result. Such energy may be retained for debugging and diagnostic analysis, clearly labelled as belonging to an invalid or infeasible run. It cannot be credited toward the primary paired energy-saving endpoint. A valid paired energy comparison requires both arms to complete the prescribed task and satisfy every mandatory validity condition. […] Do not reinterpret a constraint failure as a harmless diagnostic deviation merely to retain the energy result.

**How it is applied:**
- `energy_roles.csv` labels each run's energy. It is confirmatory only if the condition's final status is `COMPARABLE`; otherwise it is labelled `DIAGNOSTIC_ONLY_RUN_INVALID` or `DIAGNOSTIC_ONLY_RECOMPUTATION_NOT_CONFIRMED`.
- The QS-vs-dynamic check now uses only §8.2-valid energy confirmed by the separate recomputation.
- An eligible pair with an invalid arm is `NOT_EVALUABLE_RUN_INVALID`.

**Consequence of the AMB-31 ruling that falls under an open decision.** The ruling settles that invalid energy is not evidence. It does not settle what an eligible pair whose arm is invalid does to the QS-vs-dynamic branch outcome. That is the same question as AMB-29(b), so the code treats it the same way, and it is decided together with AMB-29(b) (§3.1).

## 2. Decisions still open

| ID | Question | Proposed (current code) | Code |
|---|---|---|---|
| AMB-29(b) | eligible pair, an arm has no finite energy; and an arm with invalid energy (AMB-31 consequence) | `NOT_EVALUABLE_RUN_MISSING` / `NOT_EVALUABLE_RUN_INVALID`; M0/M1 QS branch INCONCLUSIVE | `checks.py:151-156`, `:185` |
| AMB-29(c) | eligible pair, QS energy ≤ 0 (ratio undefined) | `NOT_EVALUABLE_QS_UNDEFINED`; M0/M1 QS branch INCONCLUSIVE | `checks.py:157-160`, `:185` |
| AMB-29(d) | exception before or during the pair evaluation (eligibility unknown) | `NOT_EVALUABLE_CONDITION_ERROR`; M0/M1 QS branch INCONCLUSIVE | `campaign.py:759`, `:882`; `checks.py:185` |
| AMB-30 | scope of the QS-vs-dynamic branch outcome | every planned pair of the motor across all sets | `checks.py:170` |
| AMB-32 (new) | NOT SUPPORTED when a nominal cell has no comparable pair | INCONCLUSIVE | `checks.py:417` |

These items are not listed as `open_owner_decisions` in `config/code_review_status_v5.json`; they are listed under `decided_through_amendment_2_approval`. Campaign mode cannot start until amendment 2 is issued, its block equals the code key for key, and the approval record exists. A different ruling therefore keeps the campaign blocked until the code and a new release attempt follow.

## 3. Each open decision: wording, options, consequences, risks and recommendation

**Common consequences (frozen protocol §8.1 and §9):**
- §8.1 SUPPORTED requires "Every check in §9 passes".
- §8.1 NOT SUPPORTED requires "with all checks passing".
- §9 states: "M0/M1 failure → INCONCLUSIVE for that branch".
- An M0/M1 QS-vs-dynamic branch that is not PASS therefore rules out both SUPPORTED and NOT SUPPORTED: the H3 verdict becomes INCONCLUSIVE.
- The condition's own status (`ERROR`, `INVALID_COMPARISON`, …) and its place in the D5 and §8.1 denominators are the same under every option below. **Only the QS-vs-dynamic criterion differs.**

### 3.1 AMB-29(b): an eligible pair without usable dynamic energy

**Operative wording, verbatim, draft rev3 §6:**

> | AMB-29(b) | A QS-eligible pair where an arm has **no finite dynamic energy** (an exception, or a non-finite simulator energy) | `NOT_EVALUABLE_RUN_MISSING`; M0/M1 branch INCONCLUSIVE. The same label applies to M2, whose branch stays reported only (R3-12) | conservative |

Draft rev3 §5 label rule, verbatim: "`NOT_APPLICABLE_*` pairs never change a branch outcome." and "`NOT_EVALUABLE_*` pairs make an M0/M1 branch INCONCLUSIVE."

**Extension from the AMB-31 ruling** (candidate rev4 §2): `NOT_EVALUABLE_RUN_INVALID` covers an arm with finite energy from a run that fails §8.2 or is not confirmed by the separate recomputation.

| Option | Denominator | Applicability | Feasibility | Energy crediting | H3 verdict | Integrity risk |
|---|---|---|---|---|---|---|
| **B1 (proposed)**: `NOT_EVALUABLE_*`, M0/M1 branch INCONCLUSIVE | pair kept in every denominator | applicable, not evaluable | the run failure stays explicit | none: the condition is not `COMPARABLE` | INCONCLUSIVE if the pair is M0/M1 | none found. Strict: one failed run anywhere in scope (AMB-30) makes the criterion INCONCLUSIVE |
| B2: treat as `NOT_APPLICABLE` (no effect on the branch) | kept in the counts, removed from the criterion | wrongly "not applicable": the applicability condition (both profiles pass the screen) **is** met | explicit | none | the remaining PASS pairs can carry the branch to PASS | **pass by exclusion.** A failed or invalid run is removed from the check. For invalid arms this treats a §8.2 failure as harmless, which the AMB-31 ruling forbids, and contradicts the AMB-29(a) ruling ("NOT_APPLICABLE only where applicability conditions are objectively unmet") |
| B3: treat as FAIL | kept | applicable | explicit | none | INCONCLUSIVE (same as B1) | mislabels: records a failed model-consistency comparison that was never measured; the record then reads as evidence of model disagreement |

**Recommendation: B1.** The pair meets N-A2's applicability condition, so "not applicable" is excluded by the AMB-29(a) ruling. A check that applies but cannot be evaluated cannot support a pass. Keeping the label separate from FAIL records what happened. It is the only option that neither hides a failed run (B2) nor fabricates a measurement (B3).

### 3.2 AMB-29(c): an eligible pair whose QS energy is ≤ 0

**Operative wording, verbatim, draft rev3 §6:**

> | AMB-29(c) | A QS-eligible pair whose QS energy is ≤ 0, so the ratio is undefined | `NOT_EVALUABLE_QS_UNDEFINED`; M0/M1 branch INCONCLUSIVE. The same label applies to M2, whose branch stays reported only (R3-15) | conservative |

The frozen ratio (protocol §9; AMB-17) is 100·(e_dyn − e_QS)/e_QS, undefined for e_QS ≤ 0. For the H3 cycles this would need net regeneration to equal or exceed consumption over the cycle, so it is not expected. The rule exists so that the code has a defined, fail-closed answer.

| Option | Applicability | H3 verdict | Integrity risk |
|---|---|---|---|
| **C1 (proposed)**: `NOT_EVALUABLE_QS_UNDEFINED`, M0/M1 branch INCONCLUSIVE | applicable, not evaluable | INCONCLUSIVE | none found |
| C2: `NOT_APPLICABLE` | wrongly not applicable (the screen was passed) | the remaining PASS pairs can carry the branch | **pass by exclusion**; contradicts the AMB-29(a) ruling |
| C3: substitute an absolute criterion (for example \|e_dyn − e_QS\| ≤ x Wh/km) | applicable | depends on x | introduces a threshold not in the frozen protocol, chosen after the code exists: **post hoc**; rejected |
| C4: FAIL | applicable | INCONCLUSIVE | mislabels an undefined ratio as a measured disagreement |

Under all options the denominators, feasibility and energy crediting are unchanged.

**Recommendation: C1**, for the reasons given under B1. C3 is not admissible without a new preregistered threshold.

### 3.3 AMB-29(d): an exception before or during the pair evaluation

**Operative wording, verbatim, draft rev3 §6:**

> | AMB-29(d) | An exception before or during the pair evaluation, so eligibility is unknown | `NOT_EVALUABLE_CONDITION_ERROR`, `qs_eligible_pair` unknown; M0/M1 branch INCONCLUSIVE; M2 stays reported only | conservative |

Frozen protocol §10.4, verbatim: "Exceptions go to `errors.csv` with the traceback. **No silent retry.** A rerun needs an amendment that states the cause and the fix."

| Option | Denominator / feasibility | Applicability | H3 verdict | Integrity risk |
|---|---|---|---|---|
| **D1 (proposed)**: `NOT_EVALUABLE_CONDITION_ERROR`, M0/M1 branch INCONCLUSIVE | condition `ERROR` (or its own status) stays counted; traceback in `errors.csv` | unknown | INCONCLUSIVE | none found. A software fault makes the criterion inconclusive until an amendment under §10.4 resolves it |
| D2: `NOT_APPLICABLE` | counted | unknown cannot be "objectively unmet" | the remaining PASS pairs can carry the branch | **pass by exclusion**: an error would silently remove a pair from the check; contradicts the AMB-29(a) ruling |
| D3: retry until it succeeds | — | — | — | violates §10.4 ("No silent retry"); rejected |

Energy crediting is unaffected under every option: an `ERROR` condition is never `COMPARABLE`.

**Recommendation: D1.** A rerun stays possible only through an amendment that states the cause and the fix (§10.4), issued before the affected analysis.

### 3.4 AMB-30: scope of the QS-vs-dynamic branch outcome

**Operative wording, verbatim:**
- Frozen protocol §9: "| QS vs dynamic | every B0 and B3 profile | M0, M1: ≤ 1 % per reference km. M2: reported only | M0/M1 failure → INCONCLUSIVE for that branch |".
- Amendment 1 §10 table: "| 7 | QS vs dynamic | every B0 and B3 run | M0, M1: ≤ 1 % per reference km; M2 reported | GO: that motor branch is INCONCLUSIVE (§9) |".
- Amendment 1 §10 preamble: "the §9 checks that §9 places on S2 (grid convergence, the time step, and QS-versus-dynamic on S2 profiles)".
- Draft rev3 §6: "| AMB-30 | Scope of "the motor branch". […] | every planned pair of the motor across all sets (NOM, P3, INS, CNV, SEN), with per-set counts in `qs_dynamic_accounting.csv` | Mostly conservative, because more pairs can fail. But a pass from a non-decisive set can supply the "at least one" that prevents vacuity. Owner to confirm the scope |".

These wordings conflict: "every profile/run" against "on S2 profiles". INS is S1, in-sample.

| Option | Pairs that can fail the criterion | Pairs that can supply the one PASS | H3 verdict effect | Integrity risk |
|---|---|---|---|---|
| **S1 (proposed, current code)**: all sets | all (NOM, P3, INS, CNV, SEN) | any set, including INS (S1, in-sample) and P3 | most chances of INCONCLUSIVE | **pass via a non-decisive set**: if every held-out S2 P1 pair were QS-ineligible, one in-sample S1 PASS would avoid "no pass by vacuity" |
| S2: S2 sets only (NOM, P3, CNV, SEN) | S2 pairs | any S2 set, including P3 (secondary) | fewer pairs can fail | in-sample (INS) failures are reported but cannot make the branch INCONCLUSIVE; a P3 PASS can still carry the branch |
| S3: S2 P1 decisive sets only (NOM, SEN, CNV) | decisive pairs | decisive pairs | fewest pairs | INS and P3 failures cannot affect the verdict: a failed consistency check is kept out of the decision |
| **S4 (recommended)**: failures from all sets; the required PASS from the held-out nominal set NOM | all | NOM only | most conservative | none found. It also ensures the consistency check is demonstrated on the decisive held-out cells |

Under every option the condition statuses, feasibility, energy crediting and D5/§8.1 denominators are unchanged; only the §9 criterion changes.

**Recommendation: S4.** It keeps the literal "every profile" reach for failures, so no failed check is hidden. It closes the one route to a pass through a non-decisive or in-sample set, and adds no new minimum count beyond "at least one".

**S4 is not implemented.** If the owner chooses it, `branch_qs_dynamic_outcome` needs a small change (count PASS only where `set == "NOM"`), followed by review and a new release attempt. If the owner prefers the literal reading, S1 is what the code does now.

### 3.5 AMB-32 (new): NOT SUPPORTED when a nominal cell has no comparable pair

**Operative wording, verbatim, protocol §8.1:** "**NOT SUPPORTED** if ΔE_rel > −1.0 % in every motor branch for the nominal S2 P1 runs, with all checks passing." "**INCONCLUSIVE** otherwise."

The rule does not say what happens when a motor branch has one comparable nominal cell and one missing or invalid cell. This came up while implementing the AMB-29(a) ruling ("cannot turn into an overall pass by omission").

| Option | Effect | Integrity risk |
|---|---|---|
| **N1 (proposed, implemented in `h3_verdict_eligibility`)**: NOT SUPPORTED needs a comparable pair in all six nominal cells; otherwise INCONCLUSIVE | a missing cell blocks both SUPPORTED and NOT SUPPORTED | none found |
| N2: a branch "shows ΔE_rel > −1 %" if its comparable cells do; missing cells are ignored | NOT SUPPORTED reachable with missing evidence | **verdict by omission**: a profile failure or invalid run in a nominal cell would be silently dropped from the negative verdict |

**Recommendation: N1.** It is symmetric with SUPPORTED, which already needs all six cells ("every motor branch … and both limit sets give a comparable pair").

## 4. Exact text for the owner to issue the open rulings

The recommended texts follow. They match the code except S4 (§3.4). To choose an alternative, replace the text. The machine-readable block of the amendment must then change to match, which needs a code change, review and a new release attempt.

> **Owner ruling AMB-29(b) (date):** A QS-eligible pair in which an arm has no finite dynamic energy (`NOT_EVALUABLE_RUN_MISSING`), or in which an arm's energy comes from a run that fails a protocol §8.2 criterion or is not confirmed by the separate recomputation (`NOT_EVALUABLE_RUN_INVALID`), is neither a pass nor a failure of the §9 QS-versus-dynamic check. Any such pair makes the M0/M1 motor branch INCONCLUSIVE for that criterion. For M2 the label is recorded and the branch stays reported only.

> **Owner ruling AMB-29(c) (date):** A QS-eligible pair whose QS energy per reference km is ≤ 0 is `NOT_EVALUABLE_QS_UNDEFINED`. It is neither a pass nor a failure and makes the M0/M1 motor branch INCONCLUSIVE for that criterion; for M2 the branch stays reported only. No substitute criterion is used.

> **Owner ruling AMB-29(d) (date):** An exception before or during a pair's QS-versus-dynamic evaluation is recorded in `errors.csv` and labels the pair `NOT_EVALUABLE_CONDITION_ERROR`, with eligibility unknown. It makes the M0/M1 motor branch INCONCLUSIVE for that criterion; for M2 the branch stays reported only. No retry without an amendment that states the cause and the fix (protocol §10.4).

> **Owner ruling AMB-30 (date), recommended form S4:** Every planned pair of the motor branch in every set (NOM, P3, INS, CNV, SEN) can make the branch INCONCLUSIVE for the QS-versus-dynamic criterion. The branch can PASS only if at least one eligible pair of the held-out nominal set NOM passes and no pair in any set fails or is not evaluable. *[Literal alternative S1: "…PASS only if at least one eligible pair in any set passes…" — the current code.]*

> **Owner ruling AMB-32 (date):** H3 is NOT SUPPORTED only if all six nominal S2 P1 cells (M0, M1, M2 × L-R1, L-EVE) have a COMPARABLE pair, every one shows ΔE_rel > −1.0 %, and all checks pass. A nominal cell without a comparable pair makes the H3 verdict INCONCLUSIVE.

## 5. Documentation notes (not decisions)

- `evaluation.csv` → `qs_vs_dyn_pair_status` is the in-process value. It is written before the separate recomputation. The final value, with `qs_vs_dyn_pair_status_in_process` where it changed, is in `conditions.csv`.
- `runs.csv` / `evaluation.csv` → `credited` is the run-level, in-process flag (`comparable` and in-process recomputation). The role of a run's energy for the paired endpoint is the final `energy_role` in `energy_roles.csv`.
- None of these changes alters the 170-run schedule, its IDs or its SHA-256, and S2 is not used for tuning.
