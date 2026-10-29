# R4 H3: the owner's decisions of 2026-10-29, release attempts 11 and 12 (report 21)

**Date:** 2026-10-29 (+0700).

**Status: CAMPAIGN BLOCKED. AMENDMENT 2 NOT ISSUED.**
- Candidate rev13 is a draft, marked DRAFT — NOT APPROVED FOR RELEASE.
- No campaign authorisation exists. Campaign mode was not invoked, no official run was executed, and no energy difference between arms was computed.

This report covers items 1–8 of the task "R4 H3 — Attempt 11: Final Release-Candidate Correction and Independent Review". The owner's decisions are recorded verbatim in `21a_owner_decisions_20261029_verbatim.md`.

**What happened.**
- **Attempt 11** was built at the required path from the unchanged attempt-10 state. Its independent AI review confirmed the code, but found **one MAJOR finding in the wording of the machine block** (R11-1). As required, attempt 11 was kept unchanged as reviewed, and the correction went into attempt 12.
- **Attempt 12:** its review found **no CRITICAL or MAJOR finding**, but two MINOR findings and four notes (§6).
- **Attempt 12 is technically ready for the owner's next decisions.** It is **not ready to issue**, because the open items in §8 must be settled first.

Every review was by an AI agent. **None is a human audit, and none is the owner's acceptance of anything.**

## 1. Attempts, candidates and hashes

| Item | Attempt 11 | **Attempt 12 (current package)** |
|---|---|---|
| Directory (`R4_20261028_campaign/release_attempts/`) | `attempt11_final_owner_decisions/` | `attempt12_final_owner_decisions/` |
| Manifest SHA-256 (files) | `b62952650d79381ebb3c309dfe17049e03f08cbf7b3e8b929b6f83d3e5ef5768` (103) | **`6826f9fbde4fab1bc5b4635fcb4b13990165d2e752376c4e487a7372cb482502`** (106) |
| Gate record SHA-256 | `e15fd3f535c524049bbc843264dc82b099214c7c7d50905cdf70cb52658b9d38` | `0009a75edbc5b3649898c4db088ef8056e5cec5f6cdb82785a6a88ef15403bd1` |
| Code | rev14 | rev15: `campaign.py` `e434d8ce0fc15b295d91971f8e2dcdee247caa426c5b3662b3994a7c05020861`; `checks.py` `1b677cf1…` and `recompute_from_traces.py` `f29c3738…` unchanged since rev13 and rev10 |
| Candidate | rev12 `ac376c0b362c2e99a9d3777fa849205844487e0be50a41dd1c5f1b2410b5ae1b` | **rev13 `7f06dd1f1a825c55280fa220b740d617baf4fab1899300a4a31958f345d9759b`** |
| Review status / config | `code_review_status_v13.json` `ddb8700b…` / `campaign_config_v14_DRAFT.json` `f16d69cf…` | `code_review_status_v14.json` `2bc93710…` / `campaign_config_v15_DRAFT.json` `be1aa821…` |
| Review | R11: CRITICAL 0, **MAJOR 1**, MINOR 3, NOTE 5 | R12: CRITICAL 0, **MAJOR 0**, MINOR 2, NOTE 4 |

**Superseded before use, kept unchanged:**
- **Candidate rev11** (`162b688d…`) and **status file v12** (`47c88a19…`). Rev11's §1.1 heading said "first stated in rev3", but the N-A2 section is already in the first draft, rev0. Both files were superseded before any test or review.

**Baseline** (`logs/zz_start_state_v10.json`, 06:26, before any change):
- the pilot's code and configuration equalled attempt 10's copy, 72 of 72 files;
- every attempt 3 to 10 manifest, the pilot v9 manifest, the frozen hashes and candidates rev3 to rev10 verified.

## 2. Exact changes

### I-6b: an attempted run that raised (owner decision)

**Code** (`campaign.run_condition`, the I-6 override):
- A `run`-stage exception now always gives `NOT_EVALUABLE_CONDITION_ERROR`, also where the pair evaluation said `NOT_EVALUABLE_RUN_MISSING`. In rev13, a QS-eligible pair whose run raised was `NOT_EVALUABLE_RUN_MISSING`, whether or not the other arm FAILed.
- The earlier label is kept in `qs_vs_dyn_pair_status_before_error`, and a measured FAIL also in `qs_vs_dyn_fail_arms`.
- `NOT_EVALUABLE_RUN_MISSING` stays for an executed run without a finite energy and no exception.
- Exceptions at other stages are unchanged.
- **The change is narrow:** only two labels change, and only for an eligible pair with a `run`-stage error. RUN_MISSING becomes CONDITION_ERROR, and FAIL becomes CONDITION_ERROR (in rev13, RUN_MISSING). R11 confirmed this on every path, and R12 confirmed it is unchanged in rev15.

**Tests:** `test_owner_decisions_v14.py` (I-6b, three tests); `v15.py` (a standalone I6FL test, M1 and M2, an unconfirmed other arm, a forced PASS). Updated, to expect CONDITION_ERROR: `test_owner_decisions_v11.py` (I6EL, I6FL), `test_owner_rulings_v7.py` and `test_owner_rulings_v8.py`.

### Relabelling scope after a failure of the separate recomputation or its fold (owner decision)

- **Behaviour** was already as decided in rev13: only a `NOT_APPLICABLE_*` pair with an actually executed run becomes `NOT_EVALUABLE_CONDITION_ERROR`. PASS, FAIL and REPORTED_ONLY become `NOT_EVALUABLE_RUN_INVALID`, and every NOT_EVALUABLE label stays.
- **rev14:** the docstrings cite the decision.
- **rev15 (R11-6):** the fold rejects a length mismatch between condition rows and conditions instead of leaving rows unfolded. The executor's fail-closed fallback then applies.
- **A direct call of the folds without the executed run IDs** treats every N/A pair as executed (fail-closed). The executor never makes such a call. This is documented.
- **Tests:** a precedence table of 11 labels × 4 failure paths, a no-failure control, and two executor tests (`v14.py`, `v15.py`).

### R10-1: the machine block (`IMPLEMENTED_2` → `AMB_29_condition_error`)

The block now has five parts, in this order:
1. **Owner ruling I-6** in the owner's words.
2. **Owner decision I-6b** in the owner's sentences only. The rev14 gloss, "an executed run without a finite simulator energy", was removed in rev15 (R11-1).
3. **The owner's scope decision.**
4. **"As applied"**, which names:
   - the exceptions: RUN_INVALID after a recomputation or fold failure, and an N/A pair without an executed run;
   - the NOT_EVALUABLE labels that remain applicable: RUN_MISSING, QS_UNDEFINED and RUN_INVALID;
   - four things reported separately: applicability, execution validity, recomputation validity and the final outcome.
5. **One "Implementer reading (not an owner ruling), for the owner's confirmation"**, in three parts:
   - (a) every recorded stage counts as "a run or evaluation". **This part can change an outcome.**
   - (b) a NOT_EVALUABLE label stays after an exception at a later stage. No outcome effect.
   - (c) the owner's "genuinely absent run" is the AMB-29(b) case of an executed run without a finite energy. No outcome effect.

**Also in rev15 (R11-9):** the I-1 and I-4 owner clauses hold the owner's words, with the details after "As implemented".

**Candidate:** rev13 §1.14 to §1.16, §2, §3 and §9 say the same, and the block equals `IMPLEMENTED_2` value for value (`read_amendment` with no errors). The owner's text is quoted in §1.15 and §1.16.

### R10-3: counts and provenance in the candidate

- The header counts are now accurate. Rev12 states the attempt-10 findings exactly; rev13 states the attempt-11 findings.
- The §1.1 to §1.3 headings say "first stated in rev0" (N-A2) and "first stated in rev4" (AMB-29(a), AMB-31). Both were checked against rev0, rev3 and rev4.
- The rev10 diagnosis sentence is now a separate implementation note, outside the N-A2 ruling paragraph.

## 3. R10-2 and R10-4

**R10-4: fixed in rev14.** `fold_failed` indexes `conds` only within its length. The test fails on rev13 by behaviour (an `IndexError`).

**R10-2: addressed**, with tests whose first calls work on the old code, and mutation runs against the archived modules.

| Change | Old code | Result there | Evidence kind | Log (`logs/`) |
|---|---|---|---|---|
| R9-6, separate-recomputation failure, executor | rev12 | the unexecuted pair relabelled | behavioural | `zz_mutation_check_v14_r10_2_tests_on_rev12_run2.txt` |
| R9-6, fold failure, executor | rev12 | CE instead of N/A | behavioural | `zz_mutation_check_v15_r11_7_fold_test_on_rev12.txt` |
| R9-4(b), unknown status rejected | rev12 | did not raise | behavioural | `…_v14_r10_2_tests_on_rev12_run2.txt` |
| I-6b and I6EL | rev13 | RUN_MISSING | behavioural | `…_v14_tests_on_rev13_run2.txt`, `…_v11_i6_tests_on_rev13_run2.txt` |
| I6FL (standalone test) | rev13 and rev11 | RUN_MISSING; FAIL | behavioural | `…_v15_r11_4_test_on_rev13.txt`, `…_v15_r11_4_test_on_rev11.txt` |
| R3-9 (new test) | rev11 | `qs_eligible_pair` None | behavioural | `…_v14_r3_9_test_on_rev11.txt` |
| R3-9 (the old assertion) | rev11 | missing name | **API-level only** | `…_a2_r3_9_test_on_rev11_run2.txt` |
| R11-6(b) and R11-8 | rev14 | did not raise; I-6b cited for an N/A pair | behavioural | `…_v15_tests_on_rev14.txt` |

**A failed first invocation.** The first invocation of four mutation runs (the files without `_run2`) failed before any test ran: an unquoted path split into several arguments. They are kept. The rerun used correct quoting.

**Not mutation-run, as R12 notes:** the M1, M2 and unconfirmed-arm tests, which pass on rev14 because that behaviour is unchanged. There is no test with a non-finite other arm.

## 4. Test results and schedule validation

**Commands:**
- **Suite**, from the directory in each row: `python -I -B -m pytest -c code/pytest.ini --rootdir code -p no:cacheprovider -q -rA code/tests --junitxml logs/<run>.xml`.
- **Readiness gate:** `python -I -B code/record_readiness_gate.py logs/<run>.xml`.

| Run | Tree | Exit | Passed / failed / errors / skipped |
|---|---|---|---|
| 29a, targeted, rev14 | pilot | 0 | 72 / 0 / 0 / 0 |
| 29b, targeted (`v14.py` after one test was added) | pilot | 0 | 17 / 0 / 0 / 0 |
| 29, full, rev14 → gate v15 (`3b829dc3…`) | pilot | 0 | 328 / 0 / 0 / 0 |
| **attempt 11, full** | **copied tree** | 0 | **328 / 0 / 0 / 0** |
| 30a, targeted, rev15 | pilot | 0 | 39 / 0 / 0 / 0 |
| 30, full, rev15 → gate v16 (`28ea1e47…`) | pilot | 0 | 341 / 0 / 0 / 0 |
| **attempt 12, full** | **copied tree** | 0 | **341 / 0 / 0 / 0** |

**Unlogged pre-checks (not evidence).** Two were run in the session's scratch area before the logged runs: the new rev14 tests (16 passed) and the rev15 tests (18 passed).

**Schedule validation.** Recorded in `attempt12_final_owner_decisions/logs/release_validation_attempt12.json` and its gate record. Each check was made against the established schedule and protocol; no run was executed.

| Check | Result |
|---|---|
| Runs | 170: NOM 12, P3 12, INS 12, CNV 6, SEN 128 |
| Run IDs | all unique and official |
| Arms | every condition has B0 and B3 |
| Smoke runs | excluded |
| S2 | every row held out |
| S1 | only in INS, so it never substitutes for S2 |
| Profiles | all designed on P1 |
| Gain | the fixed nominal P1 gain equals the gain of all 32 sensitivity draws |
| Schedule and planner jobs | byte-identical to attempt 2; `schedule_sha256` `6011e357…` unchanged in config v13, v14 and v15 |
| Paired endpoint | no invalid arm can enter it |
| Thresholds | the acceptance constants equal the protocol |

**Limitations:**
- These are executions of the code's own checks; the 170 runs were not executed.
- The candidate's block-to-code equality is a test result (`read_amendment`).

## 5. Integrity and line endings

**Integrity v10** (`logs/zz_integrity_v10_post.json`, against the task's pre-hash `logs/zz_pre_hash_project_v10.csv`):

| Item | Result |
|---|---|
| Protocol v1 | `f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab`, equal |
| Amendment 1 | `7720fed75bb678e47a229d00aff154e0aa14607c051f4a1163cc9bf67b6abee2`, equal; its approval record `03f835e9…`, equal |
| Preflight | 29/29 rows; nothing added, removed or changed |
| Evidence snapshot | 570/570 rows pass; manifest equal |
| Release manifests | attempt 2 (root) and attempts 3 to 12: each manifest's own hash equals its record, and every listed file matches |
| Amendment 2 drafts | rev0 to rev12 all present and unchanged |
| Project outside the pilot | 25,743 files at the start, now 25,954. All 211 added files are inside attempts 11 and 12; 0 removed; 0 changed |
| Owner records | no `campaign_authorization.json`, issued amendment 2, amendment 2 approval record or campaign outputs |

**Line endings.**
- **Before editing:** the convention of every code file was recorded in `logs/zz_line_endings_rev13_baseline.csv`. `campaign.py`, `checks.py` and some tests are CRLF; the others are LF; `closedloop.py` has historical mixed endings, unchanged since at least attempt 3 and not edited.
- **How code was edited:** with the editor tool only, never a shell rewrite.
- **After each revision:** a byte-aware check confirmed that every changed or added file keeps its convention and every added line uses it.
  - rev13 to rev14: `logs/zz_line_endings_rev13_to_rev14_final.csv` and `logs/zz_diff_rev13_to_rev14_final.txt`. The files without `_final` were written before one test was added to `v14.py` and differ only in that file.
  - rev14 to rev15: `logs/zz_line_endings_rev14_to_rev15.csv` and `logs/zz_diff_rev14_to_rev15.txt`.
- **The diff shows only the approved corrections** (`logs/zz_code_changes_rev13_to_rev14_final.csv`, `…_rev14_to_rev15.csv`).
- **campaign.py** stays entirely CRLF: 1,434 lines, none LF-only.

## 6. Independent AI reviews

Each review was by a new, separate AI agent ("Plan" type), instructed to use Read, Grep and Glob only. **None is a human independent audit.** Each report is saved verbatim with a provenance header.

| Report | Timing (2026-10-29) | Result |
|---|---|---|
| `review/R11_attempt11_review_agent_report_20261029.md` (`8acd666e…`) | 07:46 → 08:05 | R10-3 and R10-4 FIXED; R10-1 PARTLY FIXED; R10-2 PARTLY ADDRESSED. Both owner decisions implemented correctly and narrowly in the code. **MAJOR R11-1:** the I-6b clause glossed the owner's words. MINOR R11-2 to R11-4; NOTE R11-5 to R11-9 |
| `review/R12_attempt12_review_agent_report_20261029.md` (`2ca05030…`) | 09:12 → 09:46 (stopped 09:12:43 on the account's session limit; resumed 09:32) | R11-1 to R11-4 FIXED; R11-5, R11-7 and R11-8 ADDRESSED; R11-6 and R11-9 PARTLY ADDRESSED. **No CRITICAL or MAJOR.** MINOR R12-1, R12-2; NOTE R12-3 to R12-6 |

**Deviation in R12.** The agent made one Bash call against its brief, a read-only `sed` print of one line of a review brief. It disclosed the call, and its transcript confirms it was the only call outside Read, Grep and Glob.

**Open after attempt 12:**
- **R12-1 (MINOR).** The reviewer found no recorded source for the sentence "Inspect the affected branch and its tests, then verify all exception paths retain their intended classification and reporting." in the quote of I-6b. It is the owner's: the last sentence of §2.1 of the owner's message, now recorded in `21a_owner_decisions_20261029_verbatim.md`.
  - That record also shows that the rev13 §1.16 quote omits the owner's last §2.2 sentence, "Add targeted regression tests covering each applicable branch and its precedence." The instruction itself was carried out.
- **R12-2 (MINOR).** Implementer extensions remain inside other owner-ruling clauses of the block, in candidate §1.16 and in the status file. Examples:
  - AMB-31: "or not confirmed by its recomputation" and "never used by the QS-vs-dynamic check";
  - AMB-30: "a planned pair missing from the record";
  - AMB-29(a): "verdict denominator";
  - AMB-29(d): "both dynamic arms still run…";
  - I-3: "or not finite";
  - the fold-scope qualifiers.

  All of them are stricter, and none can produce a PASS. They should be moved under "As implemented" before the owner approves the block verbatim.
- **R12-3 to R12-6 (NOTE):**
  - record wording (R11-6(b) is only partly fixed; R10-1 "completed");
  - a code comment that still carries the R11-1 gloss;
  - reading (a)'s examples omit the `classify` stage;
  - test cases (a non-finite other arm; rev13 mutation runs of the M1, M2 and unconfirmed-arm tests).

## 7. The earlier MAJOR findings

`config/code_review_status_v14.json` keeps **`open_major` 7**. All seven are **AI-verified fixes pending the owner's acceptance**:

| Finding | Verified fixed by |
|---|---|
| R5-1, R5-2 | the attempt-6 verification |
| R8-1, R8-2, R8-3 | the attempt-9 review |
| R9-1 | the attempt-10 review |
| R11-1 | the attempt-12 review |

- `owner_acceptance_of_major_closures` is "not recorded". Nothing was closed or lowered on the owner's behalf.
- The original findings and their closure evidence are kept in the review reports and the status files v7 to v14.

## 8. Release-gate status

`attempt12_final_owner_decisions/logs/preconditions_attempt12.json` lists six campaign-mode blockers, each blocking on its own:
1. no issued amendment 2 (`release/03_R4_protocol_v1_amendment_2.md`);
2. no protocol §10.1 gate record (`logs/pre_run_hashes.txt`);
3. no campaign authorisation (`release/campaign_authorization.json`);
4. not running from the campaign root (AMB-15);
5. `open_major` 7, not accepted by the owner;
6. `reviews_pending`: the review of rev15 and the owner's acceptance of the rev7 to rev15 review closure.

No owner decision on the content of amendment 2 is open.

**Before issue, the owner's next decisions are:**
1. Correct R12-2, and the §1.16 quote of R12-1, in a final text revision. That revision needs a code change to `IMPLEMENTED_2`, a new candidate, a new attempt and a review.
2. Confirm or change the implementer reading, parts (a) to (c). Part (a) can change an outcome.
3. Accept, or not, the closure of the seven MAJOR findings.
4. Issue and approve amendment 2.
5. Promote the approved attempt to the campaign root with its own §10.1 gate.
6. Give the separate campaign authorisation.

**Readiness:**
- **Attempt 12 is technically ready for those decisions:** every test passes from the copied tree, the schedule validates, integrity holds, and no CRITICAL or MAJOR finding is open.
- **Amendment 2 is not ready to issue.** Owner acceptance of the MAJOR closures, the implementer reading and the R12 text corrections are unresolved, and so is every later gate.

## Confirmations and process notes

- **The campaign remains BLOCKED.**
- **No forbidden actions were taken.** Nothing created `campaign_authorization.json`, issued or approved amendment 2, wrote an approval record, promoted a candidate, invoked campaign mode or called `run_campaign()`. No official run was executed and no energy difference between arms was computed. No threshold was changed, nothing was tuned, and no new result was used to validate the thesis's claims.
- **Protected material is untouched.** Attempts 1 to 10, the earlier candidates, review reports, manifests and gate records, protocol v1, amendment 1, the preflight directory, the evidence snapshot, the thesis and R1–R3 material were not modified; integrity run v10 confirms this.
- **Tools and environment:** no Git, no installation, no network, and no CNTT-02 material.
- **Process notes:**
  - Candidate rev11 and status v12 were superseded before use (§1).
  - The four failed first mutation invocations are kept (§3).
  - A heredoc-escaping slip in the integrity script was caught by a syntax check before the script ran.
  - Run 30 was started with a plain shell `&` and confirmed by a log-watching waiter; it completed with exit 0 (`scratchpad` exit record).
  - The helper scripts that produced this evidence are copied, with hashes, to `logs/zz_scripts_task_attempt11/`.
