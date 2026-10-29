# Release attempt 9: fixes of the attempt-8 review

**Date:** 2026-10-28. **Campaign status: BLOCKED.** This attempt is not a release and has no protocol §10.1 gate.

**Attempt status: REVIEWED, with 1 MAJOR finding open. NOT RELEASABLE.**
- The independent AI-agent review found one MAJOR finding (R9-1).
- Following the task rule, this attempt is **kept unchanged as reviewed**. The corrections go into a new attempt, `../attempt10_review_fixes/`.
- No finding was downgraded.

## What this attempt contains

The code is rev12. It fixes the findings of the attempt-8 review:
- **R8-1:** no label survives an exception, a FAIL included. A QS-eligible pair whose run raised is `NOT_EVALUABLE_RUN_MISSING` (AMB-29(b)), any other pair `NOT_EVALUABLE_CONDITION_ERROR`. The FAIL stays visible in `before_error`, `fail_arms` and the counts.
- **R8-2:** the QS accounting counts applicability from `qs_vs_dyn_applicability`; applicability and pair status each add up to the planned pairs.
- **R8-3:** candidate §1.6 corrected.
- **R8-4 to R8-6:** tests added; every output write guarded and listed; block wording.
- **R8-8 to R8-10:** R7-10 recorded as closed; the fold applies I-6; a failed screen gives NOT_APPLICABLE_QS_INFEASIBLE even when the other screen raised.

The candidate is `../../../R4_20261028_pilot/03_protocol_v1_amendment_2_rev9_CANDIDATE.md`, SHA-256 `cdeea032c520f408f1f300a53cf1bc8b1ec4582d80340d3df2c2c94fa5d45719`, marked **DRAFT — NOT APPROVED FOR RELEASE**. Candidates rev0–rev8 are unchanged.

| Path | What |
|---|---|
| `code/`, `config/`, `inputs/` | copy of 76 files. Each equals its pilot source, and the 68 code and config files equal `R4_20261028_pilot/logs/readiness_gate_v13.json` (`logs/copy_verification_attempt9*`) |
| `logs/pytest_release_attempt9.{txt,xml}` | full suite run from this copy: **302 passed, 0 failed, 0 errors** |
| `logs/readiness_gate_v1.json` | this copy's readiness gate (not the campaign gate) |
| `dry_run_*/` | dry run: 170 runs (NOM 12, P3 12, INS 12, CNV 6, SEN 128). The schedule and planner jobs are byte-identical to attempt 2. No run was executed |
| `logs/preconditions_attempt9.json` | output of `preconditions()`: 6 campaign blockers. `run_campaign()` was **not** called |
| `logs/release_validation_attempt9.json` | release-readiness checks: all true. The 12 legacy-number hits are the same as before; each is a protocol section reference |
| `review/` | the review brief as sent, the scope record, and the reviewer's report verbatim |
| `GATE_RECORD_attempt9.json` | hashes, the review outcome, the gate criteria (none met), and the prior attempts |
| `zz_sha256_manifest_attempt9.csv` | manifest of this directory, written last |

## Independent review

The reviewer was a new, separate **AI review agent** ("Plan" type, no Edit or Write tools; Read, Grep and Glob only). This is **not a human independent audit**.
- **Result:** CRITICAL 0, MAJOR 1, MINOR 2, NOTE 5. R8-1 to R8-6 are FIXED, R8-8 to R8-10 ADDRESSED; R8-7 and R8-11 deferred as stated.
- **MAJOR R9-1:** `checks.qs_screen` caught an exception in a failing piece's diagnosis (`qs_piece_diagnosis`) and kept it only as text in the piece. Nothing went to `errors.csv`, and the pair stayed `NOT_APPLICABLE_QS_INFEASIBLE`. That conflicts with I-6 and protocol §10.4, and with this candidate's claim that the rule holds at the QS screen. The code is older than rev12; no earlier review flagged it.
- **MINOR R9-2:** a FAIL is not kept on two exception paths.
- **MINOR R9-3:** a condition status is misstated in candidate §3.
- **NOTE R9-4 to R9-8.**

## Why campaign mode is refused

`logs/preconditions_attempt9.json` lists 6 blockers:
- no issued amendment 2;
- no protocol §10.1 gate;
- no `campaign_authorization.json`;
- not running from the campaign root;
- `open_major` 5;
- the review of this attempt and its closure, pending.

## Prior attempts

Attempts 1–8 are unchanged. Attempt 2 is still at the campaign root, with amendment 1 only.
