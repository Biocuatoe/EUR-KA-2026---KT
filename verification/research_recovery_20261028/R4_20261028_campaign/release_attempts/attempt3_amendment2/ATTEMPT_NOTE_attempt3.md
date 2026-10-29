# Release attempt 3: amendment 2 readiness package

**Date:** 2026-10-28. **Campaign status: BLOCKED.** This attempt is **not** a release and has no protocol §10.1 gate.

## What this is

This directory is a readiness package for the code that implements the owner's N-A2 ruling (draft amendment 2). It was copied from the pilot under readiness gate v7 and tested from here.

- The draft is `../../../R4_20261028_pilot/03_protocol_v1_amendment_2_DRAFT.md`, rev3, SHA-256 `fdaf193de510488733f0e0899d50def86cbeafabdbecdd3bc7a144099b6f492c`, marked "DRAFT — NOT APPROVED FOR RELEASE".
- Amendment 2 is not issued or approved, and there is no campaign authorisation.

## Contents

| Path | What |
|---|---|
| `code/`, `config/`, `inputs/` | the copy: 58 files, each SHA-256 equal to its pilot source; the 50 code and config files equal `R4_20261028_pilot/logs/readiness_gate_v7.json` (`logs/copy_verification_attempt3*.{csv,json}`) |
| `logs/pytest_release_attempt3.{txt,xml}` | full test suite run from this copy: **216 passed, 0 failed, 0 errors** |
| `logs/readiness_gate_v1.json` | this copy's readiness gate (binds that test run to these code hashes). Not the campaign gate |
| `dry_run_20261028_114044/` | dry run: the 170-run schedule validated (NOM 12, P3 12, INS 12, CNV 6, SEN 128). No run executed, no plant evaluated. `schedule_170.csv` and `planner_jobs.csv` are byte-identical to release attempt 2's dry run |
| `logs/preconditions_attempt3.json` | `preconditions("readiness")` and `preconditions("campaign")` from this copy. `run_campaign()` was **not** called |
| `GATE_RECORD_attempt3.json` | the gate record: every hash, the five gate criteria, and the prior attempts |
| `zz_sha256_manifest_attempt3.csv` | the manifest of this directory, written last; self-exclusion rule in `zz_sha256_manifest_attempt3.README.md` |

## Why campaign mode is refused (from `logs/preconditions_attempt3.json`)

1. No issued amendment 2 at `release/03_R4_protocol_v1_amendment_2.md` (the N-A2 ruling is not yet approved as an amendment).
2. No protocol §10.1 gate record (`logs/pre_run_hashes.txt`) for this code.
3. No campaign authorisation record `release/campaign_authorization.json`.
4. Not running from the campaign root by resolved path (AMB-15, protocol §10.1).

## Prior attempts (unchanged)

| Attempt | Location | Result |
|---|---|---|
| 1 | `release_attempts/attempt1/` | 183 passed, 1 failed (test defect); preserved |
| 2 | the campaign root (`code/`, `config/`, `inputs/`, `logs/`, `release/`) | amendment 1 only; 184/184; manifest `zz_sha256_manifest_release.csv` (SHA-256 `eae90227…`) re-verified 122/122 in this task; preserved unchanged |

## What promotion would need (owner, later; not done here)

Campaign mode runs only from the campaign root. The root currently holds attempt 2 and its §10.1 gate, which `record_gate.py` refuses to overwrite. After amendment 2 is issued and approved, promoting this attempt needs an owner-approved procedure:

1. Preserve attempt 2 by moving it, unchanged and with its manifest, into a versioned `release_attempts/` directory.
2. Copy this attempt to the root and verify it against its manifest.
3. Run the full tests there and record a new protocol §10.1 gate.
4. Write a new release manifest.
5. Only after a separate owner authorisation (`campaign_authorization.json` carrying `amendment_sha256`, `amendment_2_sha256` and `pre_run_hashes_sha256`) can campaign mode start.

None of these steps was taken.
