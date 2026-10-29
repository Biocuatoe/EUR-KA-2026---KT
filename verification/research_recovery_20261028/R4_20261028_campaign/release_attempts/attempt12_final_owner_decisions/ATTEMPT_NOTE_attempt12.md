# Release attempt 12: the owner's decisions of 2026-10-29, with the fixes of the attempt-11 review

**Date:** 2026-10-29. **Campaign status: BLOCKED.** This attempt is not a release and has no protocol §10.1 gate.

**Attempt status: REVIEWED, with no CRITICAL or MAJOR finding. NOT RELEASED.**
- The independent AI-agent review found two MINOR findings (R12-1, R12-2) and four notes. They are recorded for the owner.
- **Before the machine block is approved, R12-2 should be resolved.** Some other owner-ruling clauses still carry implementer extensions. They are stricter, and none can produce a PASS.

## What this attempt contains

The code is rev15:
- **The owner's decisions of 2026-10-29, as in attempt 11 (rev14):**
  - I-6b: an attempted run that raised gives `NOT_EVALUABLE_CONDITION_ERROR`, never `NOT_EVALUABLE_RUN_MISSING`;
  - only a `NOT_APPLICABLE_*` pair with an actually executed run is relabelled after a separate-recomputation or fold failure.
- **The fixes of the attempt-11 review:**
  - **R11-1 (MAJOR):** the I-6b clause of the machine block holds only the owner's sentences. The "genuinely absent run" mapping is part (c) of the labelled implementer reading.
  - **R11-2:** the owner's I-6b words are quoted in full.
  - **R11-3:** the effect of each part of the reading is stated.
  - **R11-4:** a standalone I6FL test, behavioural on rev13 and rev11.
  - **R11-6(b):** the fold rejects a length mismatch.
  - **R11-7:** tests added.
  - **R11-8:** the reason text cites I-6b only for an eligible pair.
  - **R11-9:** the I-1 and I-4 clauses are corrected.

The candidate is `../../../R4_20261028_pilot/03_protocol_v1_amendment_2_rev13_CANDIDATE.md`, SHA-256 `7f06dd1f1a825c55280fa220b740d617baf4fab1899300a4a31958f345d9759b`, marked **DRAFT — NOT APPROVED FOR RELEASE**. The owner's decisions are recorded verbatim in `../../../R4_20261028_pilot/21a_owner_decisions_20261029_verbatim.md`.

| Path | What |
|---|---|
| `code/`, `config/`, `inputs/` | copy of 86 files. Each equals its pilot source, and the 78 code and config files equal `R4_20261028_pilot/logs/readiness_gate_v16.json` |
| `logs/pytest_release_attempt12.{txt,xml}` | full suite run from this copy: **341 passed, 0 failed, 0 errors, 0 skipped** |
| `logs/readiness_gate_v1.json` | this copy's readiness gate |
| `dry_run_*/` | dry run: 170 runs (NOM 12, P3 12, INS 12, CNV 6, SEN 128). The schedule and planner jobs are byte-identical to attempt 2. No run was executed |
| `logs/preconditions_attempt12.json` | 6 campaign blockers; `run_campaign()` was **not** called |
| `logs/release_validation_attempt12.json` | all checks true: 170 unique official run IDs; every condition with B0 and B3; smoke runs excluded; S2 held out; S1 only in INS; the fixed nominal P1 gain for all 32 draws; no invalid arm in the paired endpoint; every reporting test passed |
| `review/` | the review brief as sent, the scope record, and the reviewer's report verbatim |
| `GATE_RECORD_attempt12.json` | hashes, the line-ending and mutation evidence, the review outcome, the gate criteria (none met), and the prior attempts |
| `zz_sha256_manifest_attempt12.csv` | manifest of this directory, written last |

## Independent review

The reviewer was a new, separate **AI review agent** ("Plan" type), instructed to use Read, Grep and Glob only. This is **not a human independent audit**.
- **Deviation from the brief:** the agent disclosed one read-only Bash call, a `sed` print of one line of the attempt-11 brief. Its transcript confirms it was the only call outside Read, Grep and Glob.
- **Interruption:** the account's session limit stopped the agent once, and it was resumed with its own context.
- **Result:** CRITICAL 0, MAJOR 0, MINOR 2, NOTE 4.
  - FIXED: R11-1 to R11-4.
  - ADDRESSED: R11-5, R11-7 (mostly), R11-8.
  - PARTLY ADDRESSED: R11-6, R11-9.
- **MINOR R12-1.** The reviewer could not find a recorded source for one sentence in the quote of the owner's I-6b words. The sentence is in the owner's message, now recorded verbatim in `21a_owner_decisions_20261029_verbatim.md`. That record also shows that the §1.16 quote omits the owner's last §2.2 sentence.
- **MINOR R12-2.** Implementer extensions remain inside other owner-ruling clauses of the block (AMB-31, AMB-30, AMB-29(a), AMB-29(d), I-3, the fold-scope qualifiers), in candidate §1.16, and in the status file.
- **NOTE R12-3 to R12-6:** record wording, a code comment, the examples in reading (a), test cases.

## Status of the earlier MAJOR findings

`config/code_review_status_v14.json` keeps `open_major` 7: R5-1, R5-2, R8-1, R8-2, R8-3, R9-1 and R11-1. All seven are now verified fixed by AI-agent reviews; R11-1 was verified by this review. The owner's acceptance is **not recorded**. Nothing is closed on the owner's behalf.

## Prior attempts

Attempts 1–11 are unchanged. Attempt 2 is still at the campaign root, with amendment 1 only.
