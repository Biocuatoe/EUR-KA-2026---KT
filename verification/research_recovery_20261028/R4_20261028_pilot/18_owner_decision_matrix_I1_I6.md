# R4 H3: owner decision matrix for the amendment 2 readings I-1 to I-6 (document 18)

**Date:** 2026-10-28. **Campaign status: BLOCKED.**

**Source of the wording:** `03_protocol_v1_amendment_2_rev6_CANDIDATE.md`, §9. Its SHA-256 was verified at the start of this task as `0dcb767e97e19f40c00735d9efaecf8d21c396c23952b70e60ccb21a3f711e1f`, equal to the value in its `.sha256.txt` (`logs/zz_start_state_v8.json`). Each "rev6 wording" cell below is copied from that table without change.

**Status of the six points:**
- **I-1** is decided by the owner and implemented (rev10, candidate rev7).
- **I-2 to I-6 are not decided.** The code implements a provisional reading of each. Each is listed as an open owner decision, and campaign mode is blocked on it: `campaign.OWNER_DECISIONS_OPEN` and `config/code_review_status_v8.json` → `open_owner_decisions`. Amendment 2 cannot be issued with any of them assumed.

## 0. What no option below changes

The condition status of every scheduled pair is decided by amendment 1 §5: profile and baseline availability, errors, §8.2 on each arm, and the recomputation. It never reads a QS label. The following are therefore **the same under every option in this document**:
- the condition statuses;
- the D5 denominator and the planned-run and feasibility counts (`feasibility_accounting.csv`);
- the energy roles (`energy_roles.csv`), and so which energy is confirmatory;
- the §8.1 nominal-cell and sensitivity-draw counts (6 cells; 29 of 32 draws per M0/M1).

An option can change only two things:
- the pair's QS-versus-dynamic label;
- through it, the M0/M1 **QS-versus-dynamic branch outcome**. Because §8.1 requires "every check in §9 passes", that outcome can change whether SUPPORTED or NOT SUPPORTED remains possible.

I-3 is the exception: it can also change whether a relative percentage is computed at all.

## 1. Summary

| ID | Point | Status | Can it change the H3 verdict? | Decision required from the owner |
|---|---|---|---|---|
| I-1 | the required nominal PASS | **DECIDED** (owner ruling, §2) | — | none |
| I-2 | a profile-less pair outside the nominal set | **OPEN** | yes | §3.1 |
| I-3 | scope of "no relative saving percentage with a non-positive denominator" | **OPEN** | yes, only in a degenerate case | §3.2 |
| I-4 | which recomputation must confirm an arm for the QS check | **OPEN** | yes | §3.3 |
| I-5 | the term `QS_COMPARISON_NOT_EVALUABLE` | **OPEN**, vocabulary only | **no** | §3.4 |
| I-6 | an exception inside one run | **OPEN** | yes, only for a QS-ineligible pair outside the nominal set | §3.5 |

## 2. I-1: decided by the owner

**Rev6 wording (point / reading implemented / alternative):**

> "A required PASS must exist for the nominal held-out S2 set" | at least one PASS among the motor's two NOM cells, with both cells present with evidence. A QS-infeasible NOM cell is not missing evidence (N-A2: neither pass nor fail). This matches the "at least one" wording of the recommended option S4 in `15_remaining_owner_decisions.md` §3.4 | **stricter:** every NOM cell must PASS, so a QS-infeasible NOM cell blocks PASS. It would treat a check N-A2 rules "not applicable" as blocking

**Owner ruling, verbatim:**

> The owner rejects the "one nominal PASS per motor" interpretation.
> Every nominal cell required by the protocol on the held-out S2 set must individually pass the applicable QS-versus-dynamic check for the relevant branch.
> A missing, invalid, unevaluable, or NOT_APPLICABLE required nominal cell cannot count as PASS. Where mandatory evidence is missing, classify the branch as INCONCLUSIVE.
> A pass on S1 never substitutes for missing or failed nominal S2 evidence.
> For an applicable check that fails, retain the existing frozen protocol consequence. Do not alter numerical thresholds.
> Do not use this ruling to reclassify a QS-infeasible profile as dynamically infeasible automatically. QS and dynamic feasibility remain distinct.

**How it is implemented (rev10):**
- **Required nominal cells.** For M0 and M1, the two NOM cells L-R1 and L-EVE: the nominal S2 P1 cells of protocol §8.1, restricted to the branch. M2 stays reported only.
- **Branch outcome** (`checks.branch_qs_dynamic_outcome`). The branch can PASS only if **both** cells are PASS. A FAIL keeps the frozen §9 consequence (INCONCLUSIVE). Any other state is missing mandatory evidence and gives INCONCLUSIVE: an absent or duplicated cell, `NOT_APPLICABLE_QS_INFEASIBLE`, `NOT_APPLICABLE_PROFILE_UNAVAILABLE`, any `NOT_EVALUABLE_*`, REPORTED_ONLY, or a condition without a profile. A PASS in INS or any other set never substitutes.
- **Verdict** (`checks.h3_verdict_eligibility`). The function checks I-1 again from the condition rows (`qs_vs_dynamic_nominal_cells`), independently of the branch outcome. Any required nominal cell that is not PASS rules out SUPPORTED and NOT SUPPORTED.
- **QS and dynamic feasibility stay distinct.** A QS-infeasible nominal cell keeps its dynamic status, for example `COMPARABLE`, and its confirmatory energy. Only the QS criterion becomes INCONCLUSIVE.
- **Tests.** `tests/test_owner_ruling_i1_v10.py` covers every case the owner listed; see `19_attempt7_final_review_report.md`. No threshold changed.

**Effect compared with the rev6 reading:**
- One more case gives INCONCLUSIVE: a branch with one nominal PASS and one QS-infeasible nominal cell.
- No status, denominator or feasibility count changes.

## 3. I-2 to I-6: open decisions

### 3.1 I-2

**Rev6 wording:**

> Is a NOM cell without a profile "missing held-out evidence"? | yes: it blocks PASS, whatever the other profile's screen result. Outside NOM, `NOT_APPLICABLE_PROFILE_UNAVAILABLE` has no effect on the QS criterion (the condition still counts as a failure in §7) | no effect anywhere (the rev3/rev4 label rule)

**Effect of the I-1 ruling.** The first half is now settled by the I-1 ruling: a NOT_APPLICABLE or missing nominal cell cannot count as PASS. What remains open is the second half: the effect **outside NOM** (P3, INS, CNV, SEN).

| Interpretation | QS label | M0/M1 QS branch | H3 verdict | Status, denominators, feasibility |
|---|---|---|---|---|
| **I-2a (provisional, implemented):** outside NOM, a pair without a profile is neither pass nor fail | `NOT_APPLICABLE_PROFILE_UNAVAILABLE` | unaffected | SUPPORTED stays possible if every other requirement holds. A SEN draw without a profile still counts against "29 of 32" | unchanged (§0): the condition stays `PROFILE_UNAVAILABLE` / `BASELINE_UNAVAILABLE` in every denominator |
| **I-2b:** outside NOM, a pair without a profile makes the M0/M1 QS criterion INCONCLUSIVE | same label, treated as missing evidence | INCONCLUSIVE | INCONCLUSIVE whenever any planned M0/M1 pair in any set lacks a profile. Example: one SEN draw without an S-eco profile ends the H3 test | unchanged |
| I-2c (the rev6 "alternative"): no effect anywhere | — | — | — | **excluded by the I-1 ruling** for nominal cells |

**Risks:**
- **I-2a:** no failure is excluded. A missing profile is not a failed applicable check, and the profile failure stays explicit and counted in every denominator, as the AMB-29(a) ruling requires. It allows no pass by omission: the nominal cells must all PASS (I-1). It credits no invalid energy.
- **I-2b:** no integrity risk. It adds a requirement that no ruling states, and it makes the model-consistency criterion depend on planner feasibility in non-decisive sets, which the profile failure already penalises through the denominators.

**Recommended: I-2a.** It follows the words of the AMB-29(a) ruling (the check "may be NOT_APPLICABLE where its preregistered applicability conditions are unmet. This is not a pass"), N-A2 (not applicable is neither pass nor fail), and AMB-30 item 3 (failures of **applicable** checks count).

**Decision required:** "For a planned M0/M1 pair **outside the nominal set** whose B0 or B3 profile does not exist, does the QS-versus-dynamic criterion (a) stay unaffected, or (b) become INCONCLUSIVE?"

### 3.2 I-3

**Rev6 wording:**

> Scope of "no relative saving percentage with a non-positive denominator" | every relative saving percentage in the H3 code (§4.2), not only the QS ratio; tolerance comparisons are out of scope. An undefined ΔE_rel in a nominal cell leads to INCONCLUSIVE in the later analysis | the QS ratio only

| Interpretation | What is computed when the denominator is ≤ 0 or not finite | H3 verdict | Status, denominators, feasibility |
|---|---|---|---|
| **I-3a (provisional, implemented):** every relative saving percentage | nothing. QS ratio, paired ΔE_rel, planner S_found and S_max, grid ΔS and the time-step check are all "not evaluable"; the term and raw values are recorded | a `COMPARABLE` nominal cell whose ΔE_rel is undefined satisfies neither side of the −1 % rule, so the verdict is INCONCLUSIVE (protocol §8.1 "INCONCLUSIVE otherwise") | unchanged |
| **I-3b:** the QS ratio only | the QS ratio is not computed; ΔE_rel, S_found, S_max and ΔS are computed with the non-positive denominator | an inverted-sign ΔE_rel could satisfy "ΔE_rel ≤ −1 %" (towards SUPPORTED) or "> −1 %" (towards NOT SUPPORTED) | unchanged |

**When it matters:** only if the B0 energy per reference km, or the QS baseline energy E(v_b), is ≤ 0 over a cycle. That would require net regeneration at least equal to consumption, which is not expected for the H3 cycles. The rule gives the code a defined answer.

**Risks:**
- **I-3b:** it can produce a fabricated relative saving and so a verdict from a meaningless number. That conflicts with the AMB-29(c) sentence "Do not calculate a relative saving percentage using a non-positive denominator" read as written.
- **I-3a:** none found. It never credits invalid energy and never passes by omission.

**Recommended: I-3a.**

**Decision required:** "Does the AMB-29(c) sentence apply to (a) every relative saving percentage, or (b) the QS-versus-dynamic ratio only?"

### 3.3 I-4

**Rev6 wording:**

> Which recomputation an arm must pass to be used by the QS check | both the in-process and the separate one, as for its energy role (rev4 text named the separate one; the code used the in-process one only through the condition status) | the separate one only

| Interpretation | An arm valid under §8.2 and confirmed by the separate recomputation, whose in-process recomputation disagrees | M0/M1 QS branch | H3 verdict | Status, denominators, feasibility, energy role |
|---|---|---|---|---|
| **I-4a (provisional, implemented):** both recomputations | its QS value is diagnostic only; the pair is `NOT_EVALUABLE_RUN_INVALID` | INCONCLUSIVE | INCONCLUSIVE | unchanged: the condition is `RECOMPUTATION_DISAGREEMENT` and the energy `DIAGNOSTIC_ONLY_RECOMPUTATION_NOT_CONFIRMED` under both options |
| **I-4b:** the separate recomputation only | its QS value is used (PASS or FAIL) | can PASS | outside NOM, for example a SEN draw, SUPPORTED can remain possible. In NOM the cell is not `COMPARABLE`, so the verdict is INCONCLUSIVE anyway (AMB-32) | unchanged |

**Risks:**
- **I-4b:** the QS-versus-dynamic criterion could PASS using the energy of a run that protocol §9 marks "not credited until resolved by amendment". The energy role already treats that energy as diagnostic only, so the criterion and the role would disagree (the AMB-31 ruling).
- **I-4a:** none found.

**Recommended: I-4a.**

**Decision required:** "Must an arm's energy be confirmed by (a) both the in-process and the separate recomputation, or (b) only the separate recomputation, to be used by the QS-versus-dynamic check?"

### 3.4 I-5

**Rev6 wording:**

> The owner's term `QS_COMPARISON_NOT_EVALUABLE` | the `NOT_EVALUABLE` class; the label for QS energy ≤ 0 stays `NOT_EVALUABLE_QS_UNDEFINED` (record vocabulary unchanged since rev3) | rename the label

| Interpretation | Effect |
|---|---|
| **I-5a (provisional, implemented):** keep the label `NOT_EVALUABLE_QS_UNDEFINED` as a member of the `NOT_EVALUABLE` class | none on any label's consequence, status, denominator, feasibility or verdict |
| **I-5b:** rename the label to `QS_COMPARISON_NOT_EVALUABLE` | the same consequence (INCONCLUSIVE for M0/M1); a vocabulary change in code, records and tests, which breaks continuity with the rev3–rev6 records |

**Risks:** none for either option. This is vocabulary only.

**Recommended: I-5a.**

**Decision required (confirmation of vocabulary; it changes no outcome):** "Keep `NOT_EVALUABLE_QS_UNDEFINED` (a), or rename it `QS_COMPARISON_NOT_EVALUABLE` (b)?"

### 3.5 I-6

**Rev6 wording:**

> An exception inside one run's evaluation | the condition is `ERROR`; a QS-eligible pair is `NOT_EVALUABLE_RUN_MISSING`, unless the other, valid arm FAILs (then FAIL); an ineligible pair keeps its `NOT_APPLICABLE_*` label. In each case the consequence is that of the label (§2) | label it `NOT_EVALUABLE_CONDITION_ERROR`

| Case | I-6a (provisional, implemented) | I-6b: always `NOT_EVALUABLE_CONDITION_ERROR` | Same outcome? |
|---|---|---|---|
| QS-eligible pair, other arm not FAIL | `NOT_EVALUABLE_RUN_MISSING` → M0/M1 INCONCLUSIVE | `NOT_EVALUABLE_CONDITION_ERROR` → INCONCLUSIVE | yes (label only) |
| QS-eligible pair, the other valid arm FAILs | FAIL → INCONCLUSIVE | CONDITION_ERROR → INCONCLUSIVE | yes (label only) |
| QS-ineligible pair (screen already failed) **in NOM** | `NOT_APPLICABLE_QS_INFEASIBLE` → cannot PASS (I-1) → INCONCLUSIVE | INCONCLUSIVE | yes |
| QS-ineligible pair **outside NOM** | `NOT_APPLICABLE_*` → QS branch unaffected | INCONCLUSIVE | **no** |

Under both options the condition is `ERROR` in every denominator, its run's error, trace and run ID are kept, and no energy is confirmatory.

**Risks:**
- **I-6a:** the run's failure is never hidden, because it is counted as an `ERROR` condition everywhere. But an error in a pair outside NOM whose QS check is not applicable does not make the QS criterion INCONCLUSIVE.
- **I-6b:** stricter. It ties the QS criterion to a dynamic-run error in a pair whose QS check would not apply.

**The rulings' wording supports either reading:**
- AMB-29(d) as first framed (`15_remaining_owner_decisions.md` §3.3) covers "an exception before or during the pair evaluation, so eligibility is unknown". For an ineligible pair the eligibility is known, which fits I-6a.
- The owner's AMB-29(d) ruling is headed "Evaluation error", approves "NOT_EVALUABLE → INCONCLUSIVE", and speaks of "a failed evaluation" with its "run ID". That fits I-6b.

**Recommended: I-6b**, the stricter reading. It matches the wording of the owner's AMB-29(d) ruling and the strict direction of the I-1 ruling. Choosing it needs a small code change: an exception in either run of a pair makes the pair `NOT_EVALUABLE_CONDITION_ERROR`, whatever its eligibility. The label choice for eligible pairs (`RUN_MISSING` or `CONDITION_ERROR`) changes no outcome.

**Decision required:** "When a run of a pair raises an exception and that pair's QS check is already known not to apply (a profile failed the QS screen), does the pair (a) keep its NOT_APPLICABLE label, so the QS criterion is unaffected outside NOM, or (b) become NOT_EVALUABLE, so the M0/M1 QS criterion is INCONCLUSIVE?" Optionally also: should a QS-eligible pair whose run raised be labelled `NOT_EVALUABLE_RUN_MISSING` or `NOT_EVALUABLE_CONDITION_ERROR`? That label changes no outcome.

## 4. What follows the owner's decisions

1. **Implementing them.** For each decision that differs from the provisional reading (I-2b, I-3b, I-4b, I-5b or I-6b), the code, its tests and the candidate text change. Under the recommendations above that is **I-6b only**; I-2a, I-3a, I-4a and I-5a are already implemented.
2. **Clearing the open list.** `campaign.OWNER_DECISIONS_OPEN` is emptied, and a new review-status file records the decisions. This is a code change, so a new readiness gate, a new release attempt and a review follow.
3. **Issuing.** Only then can a candidate be issued as `release/03_R4_protocol_v1_amendment_2.md`, with `amendment_2_approval.json` stating the decisions.

Candidate rev7, prepared in this task, carries the I-1 ruling and the wording fixes. It is marked **NOT ISSUABLE**, because I-2 to I-6 are open.
