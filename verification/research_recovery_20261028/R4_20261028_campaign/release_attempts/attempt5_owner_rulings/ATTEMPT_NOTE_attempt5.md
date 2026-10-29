# Release attempt 5: owner rulings AMB-29(a)–(d), AMB-30, AMB-31 and AMB-32

**Date:** 2026-10-28. **Campaign status: BLOCKED.** This attempt is not a release and has no protocol §10.1 gate.

**Attempt status: REVIEWED — NOT READY.** The independent review found **2 MAJOR** findings (R5-1, R5-2). They are fixed in a new attempt, `../attempt6_review_fixes/`. This directory is kept unchanged as it was reviewed.

## What this attempt contains

The code implements all of the owner's amendment 2 rulings of 2026-10-28 (rev8):
- **AMB-29(a)–(d):** profile failures, missing or invalid energy, QS energy ≤ 0 and evaluation errors stay explicit, stay in every denominator, and make the QS-versus-dynamic criterion INCONCLUSIVE.
- **AMB-30:** the branch can PASS only with a PASS on the held-out nominal set NOM. Failures in any set count against it.
- **AMB-31:** invalid energy is diagnostic only.
- **AMB-32:** a missing nominal cell gives INCONCLUSIVE, never NOT SUPPORTED.

The proposed text is `../../../R4_20261028_pilot/03_protocol_v1_amendment_2_rev5_CANDIDATE.md` (SHA-256 `e7ba73c11784b3cf38f48e32b69a7a7c21b070d039118547d638bc1bf06d4f5f`), **DRAFT — NOT APPROVED FOR RELEASE**.

| Path | What |
|---|---|
| `code/`, `config/`, `inputs/` | copy of 64 files. Each equals its pilot source, and the 56 code and config files equal `R4_20261028_pilot/logs/readiness_gate_v9.json` (`logs/copy_verification_attempt5*`) |
| `logs/pytest_release_attempt5.{txt,xml}` | full suite run from this copy: **248 passed, 0 failed, 0 errors** |
| `logs/readiness_gate_v1.json` | this copy's readiness gate (not the campaign gate) |
| `dry_run_20261028_152102/` | dry run: 170 runs (NOM 12, P3 12, INS 12, CNV 6, SEN 128). `schedule_170.csv` and `planner_jobs.csv` are byte-identical to attempt 2. No run was executed |
| `logs/preconditions_attempt5.json` | output of `preconditions()`. `run_campaign()` was **not** called |
| `logs/release_validation_attempt5.json` | release-readiness checks of the schedule and reporting rules: all true (no run executed) |
| `review/` | the review brief as sent, the scope record (hashes of the reviewed files), and the reviewer's report verbatim |
| `GATE_RECORD_attempt5.json` | hashes, the review outcome, the five gate criteria (none met) and the prior attempts |
| `zz_sha256_manifest_attempt5.csv` | manifest of this directory, written last |

## Independent review

The reviewer was a separate **AI review agent** ("Plan" type, no Edit or Write tools; Read, Grep and Glob only). This is **not a human independent audit**.
- Result: CRITICAL 0, MAJOR 2, MINOR 10, NOTE 3.
- R5-1: an exception in the QS screen or in the post-run reporting became a condition-level ERROR and relabelled valid dynamic runs.
- R5-2: a nominal cell without a profile, whose other profile was QS-infeasible, did not block a branch PASS.

Neither could produce a PASS of the H3 verdict, but each breaks a ruling's rule as stated.

## Why campaign mode is refused

`logs/preconditions_attempt5.json` lists five blockers:
1. no issued amendment 2;
2. no protocol §10.1 gate for this code;
3. no `campaign_authorization.json`;
4. not running from the campaign root;
5. the review and the owner's acceptance of its closure are pending (`config/code_review_status_v6.json` → `reviews_pending`).

## Prior attempts

Attempts 1–4 are unchanged. Attempt 2 is still at the campaign root, with amendment 1 only. None of the promotion steps was taken.
