# The owner's decisions of 2026-10-29, verbatim (record for report 21)

**Source.** The owner's task message "R4 H3 — Attempt 11: Final Release-Candidate Correction and Independent Review", received in the working session at 2026-10-29 06:23:37 (+0700) (session transcript line 9740, timestamp 2026-10-28T23:23:37.961Z). Its sections 2, 3 and 5 are copied below programmatically, unmodified. The text was not edited; heading levels are the owner's.

**Why this file exists.**
- Review R12-1 found that the quoted sentence "Inspect the affected branch and its tests, then verify all exception paths retain their intended classification and reporting." had no recorded source. It is the last sentence of section 2.1 below.
- The reviewer could see only the review briefs, not the owner's message.

**How the candidates quote it.**
- Candidate rev13 §1.15 renders section 2.1 as running sentences, without the list markers.
- Its §1.16 renders section 2.2 the same way, but omits the last sentence of section 2.2: "Add targeted regression tests covering each applicable branch and its precedence." That instruction was carried out (`tests/test_owner_decisions_v14.py`, `v15.py`).

SHA-256 of the owner's full message as extracted (UTF-8): `be2208babeae5416b577e9f97abf51dba01e7ce613f12e13e2255ff6aff015ce`.

---

## 2. Binding owner decisions

### 2.1 I-6b — the unresolved QS-eligible exception-label case

The specific unresolved case is a QS-eligible pair whose run was attempted but raised an exception. For that case, the pair-level status must be:

`NOT_EVALUABLE_CONDITION_ERROR`

It must not be labelled `NOT_EVALUABLE_RUN_MISSING`, because the run was attempted and an exception occurred.

Keep the semantic distinction explicit:

- A genuinely absent run follows the existing missing-run path.
- An attempted run that raises follows the condition-error path.
- Either case remains NOT_EVALUABLE / INCONCLUSIVE as applicable. Neither may count as PASS.
- An exception must override a prior PASS when the standing I-6 rules require it.
- Do not retry silently, replace the original evidence, or change unrelated valid outcomes.

Do not perform a broad label rewrite. Inspect the affected branch and its tests, then verify all exception paths retain their intended classification and reporting.

### 2.2 Separate recomputation or fold failure — relabelling scope

Apply this owner decision to a failure of the separate recomputation **or its fold**:

- Only a pair currently classified as `NOT_APPLICABLE_*` with an actually executed run is eligible for the I-6 relabelling described here.
- Such a pair must not retain N/A when the relevant execution/evaluation exception requires a NOT_EVALUABLE classification.
- Preserve the existing handling of a genuinely missing run; do not conflate it with an executed run.
- Preserve the applicable `RUN_INVALID` and NOT_EVALUABLE classifications when required by the existing rules. Do not silently convert either to N/A or PASS.
- Both separate recomputations must confirm a run before its energy is usable for the QS check.
- Do not invent replacement energy values, use invalid energy as confirmatory evidence, or change unrelated statuses.

Add targeted regression tests covering each applicable branch and its precedence.

## 3. R10-1 — correct owner-ruling provenance and exact machine wording

The machine block is intended to represent the owner's approved wording verbatim. Correct `IMPLEMENTED_2` and the corresponding candidate wording so that:

- The owner's I-6 ruling contains only decisions actually made by the owner.
- Any narrower scope statement that is an implementer interpretation is explicitly labelled **“Implementer reading”**, rather than presented as an owner ruling.
- The optional sub-question now resolved in §2 above is represented accurately.
- The closing clause explicitly accounts for `RUN_INVALID` after a recomputation/fold failure and states which NOT_EVALUABLE labels remain applicable.
- The machine block and candidate wording agree exactly, value for value.
- The distinction among N/A applicability, execution validity, recomputation validity, and final pair outcome remains explicit.

Do not change thresholds, the estimand, denominators, planned-run accounting, the 170-run schedule, or unrelated decision rules.

## 5. Review-closure governance

The six previously reported MAJOR findings are:

- R5-1
- R5-2
- R8-1
- R8-2
- R8-3
- R9-1

Their fixes have been reported as verified by subsequent AI reviews. Preserve all original findings and closure evidence.

**Do not automatically accept or close these six findings on the owner's behalf.** Do not set `open_major` to zero or represent owner acceptance as completed unless there is an explicit existing owner decision authorizing that status change. Report them as AI-verified fixes pending owner acceptance if that acceptance has not been recorded.

A new AI review is not a human audit and does not itself constitute the owner's acceptance of historical MAJOR closures.
