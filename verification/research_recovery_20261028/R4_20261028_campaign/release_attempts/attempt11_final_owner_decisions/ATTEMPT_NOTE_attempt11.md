# Release attempt 11: the owner's decisions of 2026-10-29 and the fixes of the attempt-10 review

**Date:** 2026-10-29. **Campaign status: BLOCKED.** This attempt is not a release and has no protocol §10.1 gate.

**Attempt status: REVIEWED, with 1 MAJOR finding open. NOT RELEASABLE.**
- The independent AI-agent review confirmed that the code implements both owner decisions correctly and narrowly.
- It found one MAJOR finding in the wording of the machine block (R11-1). The finding has no effect on any status, denominator or outcome.
- This attempt is **kept unchanged as reviewed**. The corrections go into a new attempt, `../attempt12_final_owner_decisions/`.

## What this attempt contains

It was built from the unchanged attempt-10 state: at the start, the pilot's code and configuration equalled attempt 10's copy file by file. The code is rev14:
- **Owner decision I-6b:** a QS-eligible pair whose run was attempted and raised an exception is `NOT_EVALUABLE_CONDITION_ERROR`, not `NOT_EVALUABLE_RUN_MISSING`. The earlier label is kept in `qs_vs_dyn_pair_status_before_error`.
- **Owner decision on the relabelling scope:** after a failure of the separate recomputation or its fold, only a `NOT_APPLICABLE_*` pair with an actually executed run is relabelled. This behaviour was already in rev13; the docstrings now cite the decision.
- **R10-1:** the machine block separates the owner's rulings, the owner's decisions, the rules as applied, and a labelled implementer reading.
- **R10-3:** counts and provenance headings in the candidate corrected.
- **R10-4:** bounded indexing in `fold_failed`.
- **R10-2:** tests that give behavioural evidence on the old code.

The candidate is `../../../R4_20261028_pilot/03_protocol_v1_amendment_2_rev12_CANDIDATE.md`, SHA-256 `ac376c0b362c2e99a9d3777fa849205844487e0be50a41dd1c5f1b2410b5ae1b`, marked **DRAFT — NOT APPROVED FOR RELEASE**. Candidate rev11 (`162b688d…`) was written and superseded before any test or review: its §1.1 heading said "first stated in rev3", but the N-A2 section is in rev0. Rev11 is kept unchanged, as is status file v12.

| Path | What |
|---|---|
| `code/`, `config/`, `inputs/` | copy of 83 files. Each equals its pilot source, and the 75 code and config files equal `R4_20261028_pilot/logs/readiness_gate_v15.json` |
| `logs/pytest_release_attempt11.{txt,xml}` | full suite run from this copy: **328 passed, 0 failed, 0 errors, 0 skipped** |
| `logs/readiness_gate_v1.json` | this copy's readiness gate |
| `dry_run_*/` | dry run: 170 runs (NOM 12, P3 12, INS 12, CNV 6, SEN 128). The schedule and planner jobs are byte-identical to attempt 2. No run was executed |
| `logs/preconditions_attempt11.json` | 6 campaign blockers; `run_campaign()` was **not** called |
| `logs/release_validation_attempt11.json` | all checks true: 170 unique official run IDs; smoke runs excluded; S2 held out; the fixed nominal P1 gain for all 32 draws; no invalid arm in the paired endpoint; every reporting test passed |
| `review/` | the review brief as sent, the scope record, and the reviewer's report verbatim |
| `GATE_RECORD_attempt11.json` | hashes, the line-ending and mutation evidence, the review outcome, the gate criteria (none met), and the prior attempts |
| `zz_sha256_manifest_attempt11.csv` | manifest of this directory, written last |

## Independent review

The reviewer was a new, separate **AI review agent** ("Plan" type; Read, Grep and Glob only). This is **not a human independent audit**.
- **Result:** CRITICAL 0, MAJOR 1, MINOR 3, NOTE 5.
- **Closure of R10:** R10-3 and R10-4 FIXED; R10-1 PARTLY FIXED; R10-2 PARTLY ADDRESSED.
- **MAJOR R11-1.** Under "Owner decision I-6b", the block glossed the owner's "genuinely absent run" as "an executed run without a finite simulator energy". That is an implementer interpretation presented as part of an owner decision.
- **MINOR R11-2:** the owner's I-6b words are quoted incompletely.
- **MINOR R11-3:** reading (a) is wrongly called outcome-free.
- **MINOR R11-4:** the status file claims I6FL mutation evidence that does not exist.
- **NOTE R11-5 to R11-9.**

## Status of the earlier MAJOR findings

`config/code_review_status_v13.json` keeps `open_major` 6: R5-1, R5-2, R8-1, R8-2, R8-3 and R9-1. All six are verified fixed by AI-agent reviews, and the owner's acceptance is **not recorded**. Nothing is closed on the owner's behalf.

## Prior attempts

Attempts 1–10 are unchanged. Attempt 2 is still at the campaign root, with amendment 1 only.
