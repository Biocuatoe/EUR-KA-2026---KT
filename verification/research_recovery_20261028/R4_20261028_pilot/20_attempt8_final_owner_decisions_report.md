# R4 H3: owner rulings I-2 to I-6, release attempts 8 to 10 (report 20)

**Date:** 2026-10-28 to 2026-10-29 (+0700).

**Status: CAMPAIGN BLOCKED; NOT RELEASED.**
- Amendment 2 is a draft: candidate rev10, marked DRAFT — NOT APPROVED FOR RELEASE.
- No campaign authorisation exists. Campaign mode was not invoked. No official run was executed, and no energy difference between arms was computed.

This report covers items 1–9 of the task "R4 H3 — Apply Final Owner Decisions I-2 to I-6 and Prepare Attempt 8".

**What happened.**
- **Attempt 8** was built at the required path. Its independent AI review found **3 MAJOR** findings. As the task requires, it was kept unchanged as reviewed, and the corrections went into a new attempt.
- **Attempt 9:** its review verified the 3 MAJOR fixes and found **1 new MAJOR**. It was also kept, and the corrections went into a new attempt.
- **Attempt 10:** its review found **no CRITICAL or MAJOR finding**, so it is the current release-readiness package. One MINOR wording finding (R10-1) is open and should be corrected before amendment 2 is issued (§5, §8).

Every review was by an AI agent, not a human independent audit.

## 1. Attempt paths and manifests

All three are under `R4_20261028_campaign/release_attempts/`. The attempt-8 name was free at the start (`logs/zz_start_state_v9.json`, 2026-10-28 18:50:28). Each manifest excludes itself; its hash is in `logs/zz_campaign_attemptN_manifest_sha256.txt`, and the rule is in the attempt's `zz_sha256_manifest_attemptN.README.md`.

| Attempt | Directory | Manifest SHA-256 (files) | Gate record SHA-256 | Code / candidate | Review | Status |
|---|---|---|---|---|---|---|
| 8 | `attempt8_final_owner_decisions/` | `2ea8714f3f492e8ceaa5cf345182ce243ef8dab51415f55413fc45bf5300a617` (93) | `52fd8c20b97ebf2a7a7b18838d568e7bfeea28f0eab0885fd628f7cf59b5ee23` | rev11 / rev8 `f6430bf5…` | R8: CRITICAL 0, **MAJOR 3**, MINOR 3, NOTE 5 | preserved as reviewed; superseded |
| 9 | `attempt9_review_fixes/` | `0e317eef0a0a7ab54af9c2c69aee4af619693dabcf5ca441d2a7c386f5766ffc` (96) | `7c8aae1e4e2b5e239960b790aafcaedab1bcb5966169347567504c1c94727ac7` | rev12 / rev9 `cdeea032…` | R9: CRITICAL 0, **MAJOR 1**, MINOR 2, NOTE 5 | preserved as reviewed; superseded |
| **10** | **`attempt10_review_fixes/`** | **`9af4b502cbc01fb1ee657ac0f509f71a59b87f8467d7e7e5a8dfc0b9aa6c84a8`** (99) | `607bf045b4026a85ef218ffc039d21138029d9858f0d9fc50a8f3826e1a25bdf` | rev13 / **rev10 `5479f0e81b981c7977ea5a416762972d2a332d4fdb75beee7ad8379ade399804`** | R10: CRITICAL 0, **MAJOR 0**, MINOR 1, NOTE 3 | **current package; not released** |

**Final code (rev13, in attempt 10):**
- `r4h3/checks.py` `1b677cf124130fd4eca5bbf03d6c1318d6d495873aa507156c47236994dcdb04`;
- `r4h3/campaign.py` `cd354ea375414c25b1e8dc5f5264b1b1b397bfed426478c1ed446850b2245b2a`;
- `recompute_from_traces.py` `f29c3738c90b9956c2163095b113376896384629f5295fd418068c62b2348dc4` (unchanged since rev10).

**Final records:**
- review status `config/code_review_status_v11.json` `4a49d660567f089f865e518e9878bb2dfee81b18c3aae62c34d8572817f17bf8`;
- campaign configuration `config/campaign_config_v13_DRAFT.json` `d516ed295c8e934cf99290532bfe8933c4706f906ad97a795a149903e5f34d86`.

**File-level change lists:** `logs/zz_code_changes_rev10_to_rev11.csv`, `…_rev11_to_rev12.csv` and `…_rev12_to_rev13.csv`.

**Archives:** each earlier state was archived before it was changed: `archive/rev10_attempt7_20261028_1851/`, `archive/rev11_attempt8_20261028_2126/` and `archive/rev12_attempt9_20261028_2308/`.

## 2. The seven MINOR findings of the attempt-7 review (R7-1 to R7-7)

Each finding was read in full in `review/R7_attempt7_review_agent_report_20261028.md` (SHA-256 `aa8dc0a1…`). Each was fixed in rev11 and candidate rev8, and each was **verified FIXED by the independent AI review of attempt 8** (`review/R8_attempt8_review_agent_report_20261028.md`, closure table). The reviews of attempts 9 and 10 found no regression.

| ID | The finding (R7 report) | Type | Fix (rev11 / rev8) | Regression evidence |
|---|---|---|---|---|
| R7-1 | Candidate rev7 §9 said each of I-2 to I-6 changes only the QS label; I-3 does not | protocol wording | rev8 §9 states what each ruling decides; I-3 decides whether a saving percentage is computed at all | text; `test_owner_decisions_v11.py` (no "Provisional reading") |
| R7-2 | `code_review_status_v8.json` kept a sentence saying every owner decision had been made while decisions were open | record (documentation) | `code_review_status_v9.json`: the sentence is removed; `owner_rulings_implemented` and `pending_release_steps` are separate lists | `test_r7_7_…` asserts the separation and the absence of the sentence (now reading v9 by path) |
| R7-3 | Some `errors.csv` rows had no stage or `diagnostic_path` | reporting (code) | every `errors.append` has a stage; `diagnostic_path` where a process log exists | `test_r7_3_every_error_row_has_a_stage` (executor level) |
| R7-4 | Per-run ledger rows only for runs absent from the separate recomputation's output | reporting (code) | one row for every executed run not confirmed as recomputed (all of them after a process failure) | `test_r7_4_…` (3 cases, executor level) |
| R7-5 | Unguarded writes of `runs.csv`, `evaluation.csv`, `planner_checks.csv` and the summary outputs | code | `guarded()`: a failed write is recorded (stage `write <file>`, manifest `output_write_failures`), and the other outputs are still written. Rev12 extended it to every output (R8-5) | `test_r7_5_…`; `test_r8_5_…` (behavioural on rev11, §3) |
| R7-6 | Stale label-rule comment at `checks.py:46` | documentation (comment) | the comment states the I-1 and I-6 rules | — |
| R7-7 | Test gaps: the live status blocking on `open_major`; unreadable output; an exit outside {0, 1} with a complete CSV | testing | tests added | `test_r7_7_…`, `test_r7_4_…[unreadable_output, exit4_complete_output]` |

Changed files and hashes per revision are in the change lists named in §1.

## 3. Test results

**Release-tree runs.** Every full run from a copied release tree passed, and every log is kept.

| Run | Tree | Result | Log |
|---|---|---|---|
| 26a, targeted | pilot rev11, new v11 file | 15 passed | `logs/pytest_run26a_targeted_v11.txt` |
| 26, full | pilot rev11 | 288 passed, 0 failed → readiness gate v12 | `logs/pytest_run26.*` |
| **attempt 8**, full | **copied tree** | **288 passed, 0 failed, 0 errors** | `attempt8_final_owner_decisions/logs/pytest_release_attempt8.*` |
| 27a, targeted | pilot rev12 | 61 passed | `logs/pytest_run27a_targeted_v12.*` |
| 27, full | pilot rev12 | 302 passed, 0 failed → readiness gate v13 | `logs/pytest_run27.*` |
| **attempt 9**, full | **copied tree** | **302 passed, 0 failed, 0 errors** | `attempt9_review_fixes/logs/pytest_release_attempt9.*` |
| 28a, targeted | pilot rev13 | 89 passed | `logs/pytest_run28a_targeted_v13.*` |
| 28, full | pilot rev13 | 311 passed, 0 failed → readiness gate v14 (`00ddbd08…`) | `logs/pytest_run28.*` |
| **attempt 10**, full | **copied tree** | **311 passed, 0 failed, 0 errors** → the attempt's readiness gate v1 | `attempt10_review_fixes/logs/pytest_release_attempt10.*` |

**A passing suite is not a closure.** Attempts 8 and 9 passed in full while their reviews found MAJOR findings: one rev11 test asserted the behaviour that R8-1 rejected, and no test covered R9-1.

**Mutation checks** (new tests run against the archived previous `checks`/`campaign` modules, swapped into `sys.modules`):

| Log | Result | Behavioural evidence |
|---|---|---|
| `logs/zz_mutation_check_v12_tests_on_rev11.txt` | 11 of 14 fail on rev11 | R8-1, R8-2 (executor), R8-3, R8-10; the rest fail only on new names or versioning |
| `logs/zz_mutation_check_v12_r8_5_r8_9_tests_on_rev11.txt` | 2 of 2 fail on rev11 | R8-5 (unguarded write), R8-9 (N/A kept), after the tests were reworked for R9-7 |
| `logs/zz_mutation_check_v13_tests_on_rev12.txt` | 9 of 9 fail on rev12 | R9-1, R9-2 (two tests), R9-4(a); R9-6 only on the new signature (R10-2) |

The reviewers checked these claims against the logs and agree on what each shows.

**Developer pre-checks, not evidence.** Two unlogged runs were made in the session's scratch area before the logged runs:
- rev12 behavioural tests: 10 passed;
- rev13 behavioural tests: 7 passed, 1 failed. The failure was the v11-status test, run before `code_review_status_v11.json` existed.

## 4. Implementation map of I-1 to I-6 (rev13, `code/r4h3/`; candidate rev10)

| Ruling | Code | Reporting | Tests | Candidate |
|---|---|---|---|---|
| **I-1** every required nominal S2 cell (NOM; L-R1, L-EVE) must PASS individually for M0 and M1 | `checks.branch_qs_dynamic_outcome` `:217` (nominal cells, `lacking` at `:250-251`); rechecked from the rows in `checks.h3_verdict_eligibility` `:566` (`qs_vs_dynamic_nominal_cells`) | `qs_dynamic_branch_outcomes.csv`; `h3_verdict_eligibility.json` | `test_owner_ruling_i1_v10.py` (its rule tests unchanged since rev10; only the open-decision and candidate tests were updated in rev11) | §1.9, §6, §8 |
| **I-2** a missing profile outside NOM is counted, never a PASS, never paired, and not by itself INCONCLUSIVE | `NOT_APPLICABLE_PROFILE_UNAVAILABLE` is not in the NOT_EVALUABLE class; only NOM cells can lack evidence (`:251`); `classify_pair` `:445`; `paired_delta` `:466`; `feasibility_accounting` `:512` | `feasibility_accounting.csv`; `qs_dynamic_accounting.csv` | `test_i2_…` | §1.10 |
| **I-3** no energy-saving percentage with a denominator ≤ 0 or not finite; raw values and the reason kept; independent metrics intact | `non_positive_term` `:89`, used by `qs_vs_dynamic` `:355`, `scenario_totals` `:382`, `grid_convergence` `:397` and `paired_delta` `:466`; `timestep_check` `:408` | `non_positive_term` fields; `dE_rel_status` | `test_i3_…`, including an AST check that exactly those four functions form a percentage | §1.11, §4.2 |
| **I-4** both runs confirmed by the separate recomputation before the QS check uses their energy | in process `campaign.run_condition` `:906`; separate `fold_separate_recomputation` `:1005`; `fold_failed` `:1048`; energy role `:1280` | `conditions.csv` (`qs_vs_dyn_pair_status_in_process`); `energy_roles.csv` | `test_i4_…`; `test_r8_4_the_in_process_recomputation_gates_the_qs_check` | §1.12, §4.1 |
| **I-5** `NOT_EVALUABLE_QS_UNDEFINED` kept, same meaning everywhere | `checks.QS_UNDEFINED` `:55` | `not_evaluable_qs_undefined`; `n_NOT_EVALUABLE_QS_UNDEFINED` | `test_i5_…` | §1.13, §2 |
| **I-6** an exception makes the pair NOT_EVALUABLE even if its QS check would be NOT_APPLICABLE; exception, stage, run ID and log kept; the three concepts kept separate | see the I-6 breakdown below | `errors.csv` (stage, run ID(s), traceback, `diagnostic_path`); `conditions.csv` (`qs_vs_dyn_applicability`, `qs_vs_dyn_pair_status_before_error`, `qs_vs_dyn_fail_arms`); accounting `fail_before_exception`; branch `n_FAIL_before_exception` | `test_i6_…` (v11); `test_r8_*` (v12); `test_r9_*` (v13) | §1.14, §2, §3, §7.2 |

**I-6 code, in `campaign.py` unless noted:**
- applicability `:884`;
- a QS-screen diagnosis exception recorded `:829-833`;
- the override `:929` (`run_raised`);
- the `condition_report` relabel;
- `_na_pair_not_evaluable` `:990`, applied in both folds;
- in `checks.py`: `pair_applicability` `:304` and `qs_dynamic_accounting` `:317`.

**Two implementer readings, listed for the owner's confirmation** (`code_review_status_v11.json` → `implementer_readings_for_owner_confirmation`; candidate §1.12, §1.14, §9). Neither changes an outcome.
1. **Label of a QS-eligible pair whose run raised:** `NOT_EVALUABLE_RUN_MISSING`, following the standing AMB-29(b) ruling. Every other pair with an exception is `NOT_EVALUABLE_CONDITION_ERROR`. The matrix's I-6b column listed CONDITION_ERROR for this case, and the owner did not answer that optional sub-question.
2. **Scope after a failure of the separate recomputation or its fold:** only a NOT_APPLICABLE pair with an executed run becomes `NOT_EVALUABLE_CONDITION_ERROR`.

## 5. Independent AI reviews and remaining findings

Each review was by a new, separate AI agent ("Plan" type, Read, Grep and Glob only), with a written brief that treated every developer statement as a claim. **None is a human independent audit.** Each report is saved verbatim, with a provenance header, in the attempt's `review/` folder and in `review/` here.

| Report | Timing (+0700) | Result |
|---|---|---|
| `R8_attempt8_review_agent_report_20261028.md` (`8cec721e…`) | 19:44 → 19:57; one rate-limit stop | R7-1 to R7-7 FIXED. **MAJOR R8-1**: FAIL survived an exception. **MAJOR R8-2**: eligibility classes dropped relabelled pairs. **MAJOR R8-3**: candidate §1.6 stated the wrong precedence. Plus 3 MINOR and 5 NOTE |
| `R9_attempt9_review_agent_report_20261028.md` (`5461ae14…`) | 22:48 → 23:06 | R8-1 to R8-6 FIXED. **MAJOR R9-1**: an exception in the QS screen's per-piece diagnosis was swallowed (older than rev12). Plus 2 MINOR and 5 NOTE |
| `R10_attempt10_review_agent_report_20261029.md` (`bc6019d4…`) | 00:32 → 05:31 (stopped 00:41 on the account's session limit; resumed 05:27) | R9-1 to R9-3 FIXED, R9-4 to R9-8 ADDRESSED. **No CRITICAL or MAJOR.** Plus 1 MINOR and 3 NOTE. Its sweep of every `except` clause found no unrecorded exception on a path to a status, role, denominator or verdict |

**Open after attempt 10:**
- **R10-1 (MINOR; correct before issue).** The machine block is the text the owner approves verbatim.
  - **The problem:** inside "Owner ruling I-6 (2026-10-28): …" it states reading 2 of §4 ("a NOT_APPLICABLE_* pair with an executed run") without marking it as an implementer reading. Its closing clause also omits RUN_INVALID after a recomputation failure, and the NOT_EVALUABLE labels that stay.
  - **The fix:** move the restriction into the "Implementer reading … for the owner's confirmation" sentence and make the closing clause precise. This needs a code change to `IMPLEMENTED_2`, a new candidate, a new release attempt and a review.
  - **Effect:** no status, denominator or outcome.
- **R10-2 (NOTE).** The R9-6 and R9-4(b) tests show their effect on rev12 only through a new signature. I6FL and R3-9 are in no mutation run.
- **R10-3 (NOTE).** Candidate rev10 says "six of its notes" (there were five), and its §1.1 heading still says "unchanged from rev3".
- **R10-4 (NOTE).** `fold_failed` indexes `conds[i]` unguarded inside the fold's exception handler. This is not reachable with the executor's own inputs.
- **Earlier notes left as optional hardening, unchanged:** R7-11, R7-13, V6-4, R5-14 and the partly fixed R5-6.
- **Not edited:** `18_owner_decision_matrix_I1_I6.md` (R8-11). It is the pre-ruling record and still lists I-2 to I-6 as open; the owner's rulings supersede it.

**Counts in the status file.** `code_review_status_v11.json` counts `open_major` 6: R5-1, R5-2, R8-1, R8-2, R8-3 and R9-1. All six are now verified fixed by AI reviews. They stay counted, and block, until a later status file records the owner's acceptance of the closure.

## 6. Parent hash verification

Integrity run v9 (`logs/zz_integrity_v9_post.json`, against the pre-task hash `logs/zz_pre_hash_project_v9.csv`):

| Item | Established value | Now |
|---|---|---|
| Frozen protocol v1 `R4_20261028_preflight/03_R4_protocol_v1.md` | `f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab` | equal |
| Issued amendment 1 `R4_20261028_campaign/release/03_R4_protocol_v1_amendment_1.md` | `7720fed75bb678e47a229d00aff154e0aa14607c051f4a1163cc9bf67b6abee2` | equal |
| Amendment 1 approval record | `03f835e9311410095e4447840ecb2b02d95c50279527df5fdf2f6d334e15eecd` | equal |
| Preflight directory | 29 manifest rows; 30 files | 29/29 verified; nothing added, removed or changed |
| Evidence snapshot (570 files) | manifest `A93EB44F…D4F279` | manifest equal; 570/570 rows pass |
| Release manifests | attempt 2 (root) and attempts 3 to 9 | each manifest's own hash equal to its record; every listed file present, with its size and hash |
| Amendment 2 drafts | rev0 to rev9 | all present and unchanged |
| Project outside the pilot | 25,452 files at the start | 25,743. All 291 added files are inside attempts 8 to 10; 0 removed; 0 changed |
| `campaign_authorization.json`, issued amendment 2, its approval record, `R4_20261028_campaign/outputs/` | absent | absent |

**Candidate rev10.**
- **Parents:** protocol `f9826318…`, amendment 1 `7720fed7…`, and supersedes rev9 `cdeea032…`. The full hashes of rev0 to rev8 are in its header table.
- **Machine block:** `read_amendment` finds it equal to `IMPLEMENTED_2`, value for value (`test_rev10_candidate_matches_the_code`; and the dry run of attempt 10: status DRAFT, no errors).
- **Thresholds:** unchanged (QS-versus-dynamic ≤ 1 %, grid < 0.2 pp, optimality 0.2 pp, time step < 0.01 pp, 29 of 32 draws).

## 7. Schedule validation (attempt 10; no run executed)

Recorded in `attempt10_review_fixes/logs/release_validation_attempt10.json` and in its gate record.

**The schedule:**
- **170 runs:** NOM 12, P3 12, INS 12, CNV 6, SEN 128. Equal to protocol §10.6.
- **Run IDs:** official IDs, all unique; every condition has B0 and B3.
- **Unchanged:** the schedule and planner jobs are byte-identical to attempt 2; `schedule_sha256` `6011e357…` is unchanged in config v11, v12 and v13.
- **Smoke-test runs** are excluded.
- **S2** rows are all held out. S1 appears only in INS. Every profile is designed on P1.
- **Gain:** the fixed nominal P1 gain is equal to the gain of all 32 sensitivity draws (AMB-14).
- **Planner numerics** equal the protocol.

**No invalid run is credited to the confirmatory paired endpoint:**
- an exhaustive table of `energy_role` gives CONFIRMATORY only for an executed, §8.2-valid, recomputation-confirmed run in a COMPARABLE condition;
- `paired_delta` refuses every other condition status.

**Nothing is tuned to the legacy headline numbers:**
- the acceptance constants equal the protocol;
- the 12 legacy-number matches in the code (the same 12 since attempt 7) are protocol section references (10.3, 2.1, 5.3), not targets or thresholds.

**Fail-closed:** `run_campaign()` was not called, and `preconditions("campaign")` returns 6 blockers (§8).

## 8. Remaining release blockers

`attempt10_review_fixes/logs/preconditions_attempt10.json` lists 6 campaign-mode blockers:
1. no issued amendment 2 (`release/03_R4_protocol_v1_amendment_2.md`);
2. no protocol §10.1 gate record (`logs/pre_run_hashes.txt`);
3. no `campaign_authorization.json`;
4. not running from the campaign root (AMB-15);
5. `open_major` 6, not yet accepted by the owner;
6. the review of rev13 and the owner's acceptance of the rev7 to rev13 review closure, pending (`reviews_pending`).

No owner decision on the content of amendment 2 is open.

**Owner's steps, in order:**
1. **Decide on R10-1.** It is recommended to correct it, with R10-3 and optionally R10-2 and R10-4, in a final revision before issue. That revision needs a new candidate, a new release attempt and a review.
2. **Confirm or change the two implementer readings** (§4).
3. **Accept, or not, the closure** of R5-1, R5-2, R8-1 to R8-3 and R9-1. Accepting it is recorded in a new review-status file. The AI reviews are not a human audit; a human audit is the owner's option.
4. **Issue and approve amendment 2:** copy the final candidate to `release/03_R4_protocol_v1_amendment_2.md` with `"status": "APPROVED"`, and write `release/amendment_2_approval.json`.
5. **Promote** the approved attempt to the campaign root with its own §10.1 gate.
6. **Write the separate campaign authorisation** `release/campaign_authorization.json`.

## 9. Confirmations

- **The campaign remains BLOCKED.** `campaign_authorization.json` was not created, and no code path writes it.
- Campaign mode was not invoked; `run_campaign()` was never called.
- No candidate was promoted to the campaign root, which still holds attempt 2 (amendment 1 only), unchanged.
- No official run was executed. No arm-to-arm energy difference was computed: no test computes, reports or targets one, and the only synthetic percentage is a forged FAIL value in pure-rule tests.
- S2 was not used for tuning, and no threshold was changed.
- **Not edited:** attempts 1 to 7, drafts rev0 to rev7 (or rev8 and rev9, once written), frozen protocol v1, issued amendment 1, the preflight directory, the evidence snapshot, the thesis, and R1–R3 material. Integrity run v9 confirms it.
- **Not used:** Git, software installation, the network, and CNTT-02 material. All Python ran with `-I -B`.

**Process notes:**
- **Line endings.** A shell `sed -i` command converted `code/r4h3/campaign.py` (rev13 work in progress) from CRLF to LF. A line-ending check caught it before any test run or archive. The file was restored to CRLF, and a diff against the archived rev12 showed only the intended lines changed. Since then, code is edited only with the editor tool.
- **Interrupted reviews.** Two of the three reviews were interrupted by service limits. Each was resumed with its own context, and the provenance headers state the times.
