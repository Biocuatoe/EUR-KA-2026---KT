# Release attempt 6: owner rulings with the fixes of the attempt-5 review

**Date:** 2026-10-28. **Campaign status: BLOCKED.** This attempt is not a release and has no protocol §10.1 gate.

**Attempt status: REVIEWED AND VERIFIED.** No CRITICAL or MAJOR finding is open in the code. MINOR findings remain open. It is not releasable until the owner acts (see below).

## What this attempt contains

The code (rev9) implements all of the owner's amendment 2 rulings of 2026-10-28:
- N-A2;
- AMB-29(a)–(d);
- AMB-30 (the strict nominal held-out requirement);
- AMB-31;
- AMB-32.

It also contains the fixes for the independent review of attempt 5, `../attempt5_owner_rulings/review/R5_attempt5_review_agent_report_20261028.md`:
- **R5-1 (MAJOR):** an exception in the QS screen, the classification or the condition report no longer relabels valid dynamic runs.
- **R5-2 (MAJOR):** a nominal cell without a profile now always blocks a branch PASS.
- **R5-3 to R5-11:** fixed (R5-6 partly).

The proposed text is `../../../R4_20261028_pilot/03_protocol_v1_amendment_2_rev6_CANDIDATE.md`, SHA-256 `0dcb767e97e19f40c00735d9efaecf8d21c396c23952b70e60ccb21a3f711e1f`, **DRAFT — NOT APPROVED FOR RELEASE**. Candidates rev0–rev5 are unchanged.

| Path | What |
|---|---|
| `code/`, `config/`, `inputs/` | copy of 67 files. Each equals its pilot source, and the 59 code and config files equal `R4_20261028_pilot/logs/readiness_gate_v10.json` (`logs/copy_verification_attempt6*`) |
| `logs/pytest_release_attempt6.{txt,xml}` | full suite run from this copy: **258 passed, 0 failed, 0 errors** |
| `logs/readiness_gate_v1.json` | this copy's readiness gate (not the campaign gate) |
| `dry_run_*/` | dry run: 170 runs (NOM 12, P3 12, INS 12, CNV 6, SEN 128). The schedule and planner jobs are byte-identical to attempt 2. No run was executed |
| `logs/preconditions_attempt6.json` | output of `preconditions()`. `run_campaign()` was **not** called |
| `logs/release_validation_attempt6.json` | release-readiness checks of the schedule and reporting rules: all true. No run was executed and no energy difference was computed |
| `review/` | the verification brief as sent, the scope record (hashes of the verified files), and the reviewer's verification report verbatim |
| `GATE_RECORD_attempt6.json` | hashes, the review and verification outcome, the five gate criteria (none met), and the prior attempts |
| `zz_sha256_manifest_attempt6.csv` | manifest of this directory, written last |

## Independent review and verification

Both were done by one separate **AI review agent** ("Plan" type, no Edit or Write tools; Read, Grep and Glob only). This is **not a human independent audit**.

| Round | State | CRITICAL | MAJOR | MINOR | NOTE |
|---|---|---|---|---|---|
| review | attempt 5 (rev8, candidate rev5) | 0 | 2 | 10 | 3 |
| verification, new findings | this attempt (rev9, candidate rev6) | 0 | 0 | 3 | 2 |

**Still open (MINOR):**
- **V6-1:** an exception while `recompute_from_traces.py` imports its modules or reads its arguments exits with 1. That is fail-closed (no CSV, so every run is unconfirmed), but it is not written to `errors.csv`.
- **V6-2, V6-3:** wording in candidate rev6 §1.6, §3, §4.2 and §9.
- **R5-6, partly:** a run whose evaluation raised keeps its simulator energy only in its kept trace.

**Notes:** V6-4, V6-5 and R5-14 are documented and need no action.

**Closed after the verification:** R5-12. Its record, `17_owner_rulings_attempts5_6_report.md`, was written after the verification.

## Why campaign mode is refused

`logs/preconditions_attempt6.json` lists six blockers:
1. no issued amendment 2;
2. no protocol §10.1 gate for this code;
3. no `campaign_authorization.json`;
4. not running from the campaign root;
5. `config/code_review_status_v7.json` counts `open_major` 2;
6. it lists the verification and the owner's acceptance of the closure as pending.

Blockers 5 and 6 are deliberate. The status file was written before the verification and does not lower the count on the developer's own word. Lowering it needs a later status file that records the verification and the owner's acceptance, followed by a new gate and attempt.

## Prior attempts

Attempts 1–5 are unchanged. Attempt 5 is kept as reviewed, with its 2 MAJOR findings open there. Attempt 2 is still at the campaign root, with amendment 1 only.
