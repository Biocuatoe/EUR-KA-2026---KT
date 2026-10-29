# Release attempt 7: owner ruling I-1 and the fixes of the attempt-6 verification

**Date:** 2026-10-28. **Campaign status: BLOCKED.** This attempt is not a release and has no protocol §10.1 gate.

**Attempt status: REVIEWED.** The independent AI-agent review found no CRITICAL or MAJOR finding; MINOR findings are open. **The attempt is NOT RELEASABLE:** the owner decisions I-2 to I-6 are open, and the code blocks on them.

## What this attempt contains

The code is rev10:
- **Owner ruling I-1:** every required nominal cell of the held-out S2 set (NOM; L-R1 and L-EVE, for M0 and M1) must individually PASS the QS-versus-dynamic check. A missing, invalid, not-evaluable or NOT_APPLICABLE nominal cell never counts as PASS, and S1 never substitutes. A FAIL keeps the frozen consequence. QS and dynamic feasibility stay distinct.
- **Where I-1 is enforced:** in `checks.branch_qs_dynamic_outcome`, and again from the rows in `checks.h3_verdict_eligibility`.
- **V6-1:** a start-up failure of the separate recomputation exits 4. The runner records every launch, exit, output or missing-run failure in `errors.csv`, with its stage, the process log and the affected run IDs.
- **V6-2 and V6-3:** corrected wording in candidate rev7.
- **Open decisions:** I-2 to I-6 are open. The code implements a provisional reading of each and blocks while any is open (`campaign.OWNER_DECISIONS_OPEN`).

The candidate text is `../../../R4_20261028_pilot/03_protocol_v1_amendment_2_rev7_CANDIDATE.md`, SHA-256 `0e3ef3112c979237e7079f176b21dd4f2ce682c7ab435f36f33321ffe67a5996`, marked **DRAFT — NOT APPROVED FOR RELEASE — NOT ISSUABLE**. The decisions required are in `../../../R4_20261028_pilot/18_owner_decision_matrix_I1_I6.md`. Candidates rev0–rev6 are unchanged.

| Path | What |
|---|---|
| `code/`, `config/`, `inputs/` | copy of 70 files. Each equals its pilot source, and the 62 code and config files equal `R4_20261028_pilot/logs/readiness_gate_v11.json` (`logs/copy_verification_attempt7*`) |
| `logs/pytest_release_attempt7.{txt,xml}` | full suite run from this copy: **273 passed, 0 failed, 0 errors** |
| `logs/readiness_gate_v1.json` | this copy's readiness gate (not the campaign gate) |
| `dry_run_*/` | dry run: 170 runs (NOM 12, P3 12, INS 12, CNV 6, SEN 128). The schedule and planner jobs are byte-identical to attempt 2. No run was executed |
| `logs/preconditions_attempt7.json` | output of `preconditions()`. `run_campaign()` was **not** called |
| `logs/release_validation_attempt7.json` | release-readiness checks of the schedule and reporting rules: all true. No run was executed and no energy difference was computed |
| `review/` | the review brief as sent, the scope record (hashes of the reviewed files), and the reviewer's report verbatim |
| `GATE_RECORD_attempt7.json` | hashes, the review outcome, the gate criteria (none met), and the prior attempts |
| `zz_sha256_manifest_attempt7.csv` | manifest of this directory, written last |

## Independent review

The reviewer was a new, separate **AI review agent** ("Plan" type, no Edit or Write tools; Read, Grep and Glob only). This is **not a human independent audit**.
- **Result:** CRITICAL 0, MAJOR 0, MINOR 7, NOTE 6. V6-1, V6-2 and V6-3 are FIXED.
- **Open MINOR findings**, all without effect on any status, denominator or verdict:
  - R7-1: a wording error about I-3 in candidate §9;
  - R7-2: a stale sentence in `code_review_status_v8.json`;
  - R7-3 to R7-5: gaps in the error-ledger fields and coverage;
  - R7-6: a stale code comment;
  - R7-7: test gaps.
- They are listed for the next revision, which must follow the owner's I-2 to I-6 decisions.

## Why campaign mode is refused

`logs/preconditions_attempt7.json` lists 16 blockers:
- no issued amendment 2;
- no protocol §10.1 gate;
- no `campaign_authorization.json`;
- not running from the campaign root;
- the five open owner decisions, each counted twice: once from the code and once from the review-status file;
- `open_major` 2 (R5-1 and R5-2, verified fixed but not accepted by the owner);
- the review closure pending the owner's acceptance.

## Prior attempts

Attempts 1–6 are unchanged. Attempt 2 is still at the campaign root, with amendment 1 only.
