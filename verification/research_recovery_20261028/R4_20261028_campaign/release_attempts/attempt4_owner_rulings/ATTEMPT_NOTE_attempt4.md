# Release attempt 4: owner rulings AMB-29(a) and AMB-31

**Date:** 2026-10-28. **Campaign status: BLOCKED.** This attempt is not a release and has no protocol §10.1 gate.

## What this attempt contains

The code here implements two owner rulings of 2026-10-28:

- **AMB-29(a):** a missing profile stays an explicit outcome in every denominator. Only the QS-vs-dynamic check is "not applicable", and that is not a pass.
- **AMB-31:** energy from a run that fails §8.2, or that the separate recomputation does not confirm, is diagnostic only.

The proposed amendment text is `../../../R4_20261028_pilot/03_protocol_v1_amendment_2_rev4_CANDIDATE.md` (SHA-256 `c726560d1e87036cbd94fe58724cafdc1e4746647f6cfacbb320f3e14ed143ab`). It is a **CANDIDATE — DRAFT — NOT APPROVED FOR RELEASE**, and its open owner decisions are AMB-29(b)–(d), AMB-30 and AMB-32. The owner's decision record is `../../../R4_20261028_pilot/15_remaining_owner_decisions.md`.

| Path | What |
|---|---|
| `code/`, `config/`, `inputs/` | copy of 61 files. Each file's SHA-256 equals its pilot source, and the 53 code and config files equal `R4_20261028_pilot/logs/readiness_gate_v8.json` (see `logs/copy_verification_attempt4*`) |
| `logs/pytest_release_attempt4.{txt,xml}` | full suite run from this copy: **229 passed, 0 failed, 0 errors** |
| `logs/readiness_gate_v1.json` | this copy's readiness gate (not the campaign gate) |
| `dry_run_20261028_123642/` | dry run: 170 runs (NOM 12, P3 12, INS 12, CNV 6, SEN 128). `schedule_170.csv` and `planner_jobs.csv` are byte-identical to attempts 2 and 3. No run was executed |
| `logs/preconditions_attempt4.json` | output of `preconditions()`. `run_campaign()` was **not** called |
| `GATE_RECORD_attempt4.json` | hashes, the five gate criteria (none met), and the prior attempts |
| `zz_sha256_manifest_attempt4.csv` | manifest of this directory, written last |

## Why campaign mode is refused

`logs/preconditions_attempt4.json` lists five blockers:

1. No issued amendment 2.
2. No protocol §10.1 gate for this code.
3. No `campaign_authorization.json`.
4. Not running from the campaign root.
5. **The rev7 changes have not been independently reviewed.** `code_review_status_v5.json` lists this under `reviews_pending`, which blocks.

## Prior attempts

All prior attempts are unchanged:

- Attempt 1: `release_attempts/attempt1/`.
- Attempt 2: the campaign root, amendment 1 only.
- Attempt 3: `release_attempts/attempt3_amendment2/`, amendment 2 draft rev3.

Promotion to the root needs the owner-approved procedure described in attempt 3's note. None of those steps was taken.
