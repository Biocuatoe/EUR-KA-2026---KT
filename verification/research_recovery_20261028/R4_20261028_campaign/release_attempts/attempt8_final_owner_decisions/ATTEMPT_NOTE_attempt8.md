# Release attempt 8: owner rulings I-2 to I-6 and the fixes of the attempt-7 review

**Date:** 2026-10-28. **Campaign status: BLOCKED.** This attempt is not a release and has no protocol §10.1 gate.

**Attempt status: REVIEWED, with 3 MAJOR findings open. NOT RELEASABLE.**
- The independent AI-agent review found three MAJOR findings (R8-1, R8-2, R8-3).
- Following the task rule, this attempt is **kept unchanged as reviewed**. The corrections go into a new attempt, `../attempt9_review_fixes/`.
- No finding was downgraded.

## What this attempt contains

The code is rev11:
- **Owner rulings I-2 to I-6 (2026-10-28):**
  - **I-2:** a missing profile outside NOM is counted, never a PASS and never paired, and not by itself INCONCLUSIVE.
  - **I-3:** no energy-saving percentage over a denominator ≤ 0 or not finite.
  - **I-4:** both runs must be confirmed by the separate recomputation.
  - **I-5:** the `NOT_EVALUABLE_QS_UNDEFINED` label is kept.
  - **I-6:** an exception makes the pair NOT_EVALUABLE even when its QS check would be NOT_APPLICABLE. Applicability is kept separately in `qs_vs_dyn_applicability`.
- **I-1** is unchanged.
- **Fixes of the seven MINOR findings of review R7:**
  - a stage on every `errors.csv` row;
  - a per-run ledger of the separate recomputation;
  - guarded output writes;
  - the corrected review-status file `code_review_status_v9.json`, which separates the resolved owner rulings from the pending release steps;
  - the comment and test fixes.

The candidate text is `../../../R4_20261028_pilot/03_protocol_v1_amendment_2_rev8_CANDIDATE.md`, SHA-256 `f6430bf5512cb56065a2465bcfda1c4c42e244b80f73fcd3e88d985ac8811f7c`, marked **DRAFT — NOT APPROVED FOR RELEASE**. Candidates rev0–rev7 are unchanged.

| Path | What |
|---|---|
| `code/`, `config/`, `inputs/` | copy of 73 files. Each equals its pilot source, and the 65 code and config files equal `R4_20261028_pilot/logs/readiness_gate_v12.json` (`logs/copy_verification_attempt8*`) |
| `logs/pytest_release_attempt8.{txt,xml}` | full suite run from this copy: **288 passed, 0 failed, 0 errors**. One test (I6FL) asserts the behaviour that R8-1 rejects |
| `logs/readiness_gate_v1.json` | this copy's readiness gate (not the campaign gate) |
| `dry_run_*/` | dry run: 170 runs (NOM 12, P3 12, INS 12, CNV 6, SEN 128). The schedule and planner jobs are byte-identical to attempt 2. No run was executed |
| `logs/preconditions_attempt8.json` | output of `preconditions()`. `run_campaign()` was **not** called |
| `logs/release_validation_attempt8.json` | release-readiness checks of the schedule and reporting rules: all true. The 12 legacy-number hits are identical to attempt 7's, and each is a protocol section reference. No run was executed and no energy difference was computed |
| `review/` | the review brief as sent, the scope record (hashes of the reviewed files), and the reviewer's report verbatim |
| `GATE_RECORD_attempt8.json` | hashes, the review outcome, the gate criteria (none met), and the prior attempts |
| `zz_sha256_manifest_attempt8.csv` | manifest of this directory, written last |

## Independent review

The reviewer was a new, separate **AI review agent** ("Plan" type, no Edit or Write tools; Read, Grep and Glob only). This is **not a human independent audit**. It was stopped once by a service rate limit and resumed with its own context.
- **Result:** CRITICAL 0, MAJOR 3, MINOR 3, NOTE 5. R7-1 to R7-7 are FIXED.
- **MAJOR R8-1:** when a run raised and the other valid arm FAILed, the code kept the pair FAIL. The I-6 ruling, the stricter interpretation, says the pair becomes NOT_EVALUABLE.
- **MAJOR R8-2:** the QS accounting counted eligibility from the pair status. A pair relabelled by I-6 then fell out of every eligibility class, so a reported denominator dropped pairs.
- **MAJOR R8-3:** candidate §1.6 still gave `NOT_APPLICABLE_PROFILE_UNAVAILABLE` for a QS-screen exception with a missing profile.
- **MINOR R8-4 to R8-6:** test gaps, unguarded writes, and block wording.
- **NOTE R8-7 to R8-11.**
- **Effect on outcomes:** according to the reviewer, none of the MAJOR findings can produce a PASS, SUPPORTED or NOT SUPPORTED, or start the campaign. They are still MAJOR under the brief's scale, because each changes a pair status or a reported denominator, or misstates a ruling.

## Why campaign mode is refused

`logs/preconditions_attempt8.json` lists 6 blockers:
- no issued amendment 2;
- no protocol §10.1 gate;
- no `campaign_authorization.json`;
- not running from the campaign root;
- `open_major` 2 (R5-1 and R5-2, verified fixed but not accepted by the owner);
- the review of this attempt and its closure, pending.

No owner decision is open.

## Prior attempts

Attempts 1–7 are unchanged. Attempt 2 is still at the campaign root, with amendment 1 only.
