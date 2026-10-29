# Release attempt 10: fixes of the attempt-9 review

**Date:** 2026-10-29. **Campaign status: BLOCKED.** This attempt is not a release and has no protocol §10.1 gate.

**Attempt status: REVIEWED, with no CRITICAL or MAJOR finding. NOT RELEASED.**
- The independent AI-agent review found one MINOR finding (R10-1) and three notes. They are recorded for the owner; under the task rule they do not require a new attempt.
- **Before amendment 2 is issued, R10-1 should be corrected.** The machine block, which the owner approves word for word, states one implementer reading without marking it as such (see "Independent review" below).

## What this attempt contains

The code is rev13. It fixes the findings of the attempt-9 review:
- **R9-1 (MAJOR).** An exception in the QS screen's per-piece diagnosis is recorded in `errors.csv` (stage `qs_screen`, run ID, traceback, piece). It makes the pair `NOT_EVALUABLE_CONDITION_ERROR`; the screen verdict and the QS applicability are kept.
- **R9-2.** A measured FAIL stays visible on every exception path.
- **R9-3.** Candidate §3 row split.
- **R9-4.** The N/A split adds up on every path, and an unknown pair status raises.
- **R9-5.** The block marks the RUN_MISSING label as an implementer reading.
- **R9-6.** After a separate-recomputation or fold failure, only an N/A pair with an executed run is relabelled.
- **R9-7.** Test corrections, and behavioural mutation evidence for R8-5 and R8-9.
- **R9-8.** Documented.

The candidate is `../../../R4_20261028_pilot/03_protocol_v1_amendment_2_rev10_CANDIDATE.md`, SHA-256 `5479f0e81b981c7977ea5a416762972d2a332d4fdb75beee7ad8379ade399804`, marked **DRAFT — NOT APPROVED FOR RELEASE**. Candidates rev0–rev9 are unchanged.

| Path | What |
|---|---|
| `code/`, `config/`, `inputs/` | copy of 79 files. Each equals its pilot source, and the 71 code and config files equal `R4_20261028_pilot/logs/readiness_gate_v14.json` (`logs/copy_verification_attempt10*`) |
| `logs/pytest_release_attempt10.{txt,xml}` | full suite run from this copy: **311 passed, 0 failed, 0 errors** |
| `logs/readiness_gate_v1.json` | this copy's readiness gate (not the campaign gate) |
| `dry_run_*/` | dry run: 170 runs (NOM 12, P3 12, INS 12, CNV 6, SEN 128). The schedule and planner jobs are byte-identical to attempt 2. No run was executed |
| `logs/preconditions_attempt10.json` | output of `preconditions()`: 6 campaign blockers. `run_campaign()` was **not** called |
| `logs/release_validation_attempt10.json` | release-readiness checks, all true: <br>• 170 unique official run IDs; <br>• smoke runs excluded; <br>• S2 held out; <br>• the fixed nominal P1 gain for all 32 draws; <br>• no invalid arm in the paired endpoint; <br>• every reporting test passed; <br>• the 12 legacy-number hits are protocol section references |
| `review/` | the review brief as sent, the scope record, and the reviewer's report verbatim |
| `GATE_RECORD_attempt10.json` | hashes, the review outcome, the schedule validation, the gate criteria (none met), and the prior attempts |
| `zz_sha256_manifest_attempt10.csv` | manifest of this directory, written last |

## Independent review

The reviewer was a new, separate **AI review agent** ("Plan" type, no Edit or Write tools; Read, Grep and Glob only). This is **not a human independent audit**. It was stopped once by the account's session limit and resumed with its own context.
- **Result:** CRITICAL 0, MAJOR 0, MINOR 1, NOTE 3. R9-1 to R9-3 are FIXED, R9-4 to R9-8 ADDRESSED.
- **Exception sweep.** The reviewer listed every `except` clause in `code/r4h3` and `recompute_from_traces.py`. None on a path to a pair status, condition status, energy role, denominator or verdict leaves an exception unrecorded.
- **MINOR R10-1.** Inside "Owner ruling I-6 (2026-10-28): …", the machine block states the R9-6 scope reading ("a NOT_APPLICABLE_* pair with an executed run") without marking it as an implementer reading. Its closing clause also omits RUN_INVALID after a recomputation failure. The prose and the status file mark the reading correctly. The finding has no effect on any status, denominator or outcome.
- **NOTE R10-2:** weak mutation evidence for R9-6 and R9-4(b).
- **NOTE R10-3:** two wording slips in the candidate.
- **NOTE R10-4:** an unguarded index in `fold_failed`, not reachable with the executor's inputs.

## Why campaign mode is refused

`logs/preconditions_attempt10.json` lists 6 blockers:
- no issued amendment 2;
- no protocol §10.1 gate;
- no `campaign_authorization.json`;
- not running from the campaign root;
- `open_major` 6, the AI-verified findings awaiting the owner's acceptance;
- the review of this attempt and its closure, pending.

No owner decision is open. Two implementer readings await the owner's confirmation.

## Prior attempts

Attempts 1–9 are unchanged. Attempt 2 is still at the campaign root, with amendment 1 only.
