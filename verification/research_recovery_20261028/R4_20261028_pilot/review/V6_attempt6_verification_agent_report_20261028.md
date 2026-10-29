# Release attempt 6: independent read-only verification report (verbatim)

**Provenance.**
- **Who:** the same separate **AI review agent** that reviewed release attempt 5 ("Plan" agent type, no Edit or Write tools), resumed with its own context and instructed to use Read, Grep and Glob only. **This is not a human independent audit.**
- **When:** resumed 2026-10-28 at about 16:18:40 (+0700), after `review_scope_attempt6.json` was written at 16:18:35. It delivered this report at about 16:24, after about 315 s of work (the agent's reported duration). The time was read from the clock at 16:24:23.
- **Brief:** `verification_brief_attempt6_as_sent.md`.
- **State verified:** this attempt's `code/` and `config/` (60 files, SHA-256 in `review_scope_attempt6.json`) and the amendment 2 candidate rev6, `R4_20261028_pilot/03_protocol_v1_amendment_2_rev6_CANDIDATE.md`, SHA-256 `0dcb767e97e19f40c00735d9efaecf8d21c396c23952b70e60ccb21a3f711e1f`.
- **Format:** the text below the line is the agent's final message. The only edit is removing the two-space indentation that the message relay adds.
- **Outcome:**
  - R5-1 and R5-2 (MAJOR) are verified fixed; no CRITICAL or MAJOR finding remains in the code.
  - Open: V6-1, V6-2 and V6-3 (MINOR), R5-6 partly fixed (MINOR), and V6-4 and V6-5 (NOTE).
  - R5-12 was open at review time. Its cited record, `17_owner_rulings_attempts5_6_report.md`, was written after this report.

---

I am an AI review agent (a read-only "Plan"-type agent, not a human auditor). I used only the Read, Grep and Glob tools. I ran nothing, wrote nothing, computed no hashes and did not use Git or the network.

**New findings: CRITICAL 0 · MAJOR 0 · MINOR 3 · NOTE 2.** Of the old findings, R5-6 is only partly fixed and R5-12 is not fixed; both are MINOR.

Path abbreviations:
- ATT6 = `D:\EURÉKA 2026 - KT\verification\research_recovery_20261028\R4_20261028_campaign\release_attempts\attempt6_review_fixes`
- PIL = `D:\EURÉKA 2026 - KT\verification\research_recovery_20261028\R4_20261028_pilot`
- DRAFT6 = `PIL\03_protocol_v1_amendment_2_rev6_CANDIDATE.md`
- Code references are `ATT6\code\r4h3\<file>:<line>` unless stated otherwise.
- I compared against the attempt-5 code (rev8) I reviewed before.
- `zz_code_changes_rev8_to_rev9.csv` lists only `checks.py`, `campaign.py`, `recompute_from_traces.py`, four test files and two config files as changed. This is consistent with what I read; I could not check its hashes.

---

## 1. Closure table, R5-1 to R5-14

| ID | Sev | Verdict | Evidence |
|---|---|---|---|
| R5-1 | MAJOR | **FIXED** | Every former crash point in `run_condition` is now guarded and logged with its stage and run IDs: building the QS plant (campaign.py:761-767), the per-arm QS screen (768-775), the per-run diagnostic fields (804-810), the classification (811-818) and the condition report (851-883). A screen exception gives `NOT_EVALUABLE_CONDITION_ERROR`, or `NOT_APPLICABLE_PROFILE_UNAVAILABLE` if a profile is missing (824-829). Both arms still run (778-803), and the condition status still comes from `classify_pair` alone. A failure while recording the result turns a PASS, FAIL or REPORTED_ONLY into `CONDITION_ERROR` and keeps the earlier value in `before_error` (881-883). Executed run records are never replaced. Tests: test_review_fixes_v9.py:78-117. The only code left outside the guards before the arms is trivial reads (V6-4). |
| R5-2 | MAJOR | **FIXED** | Two fixes. A missing profile now takes precedence over the other profile's failed screen, giving `NOT_APPLICABLE_PROFILE_UNAVAILABLE` with `ineligible_arms` empty (checks.py:147-155). As a second safeguard, `branch_qs_dynamic_outcome` treats any NOM cell whose condition status is `PROFILE_UNAVAILABLE` or `BASELINE_UNAVAILABLE` as lacking evidence, whatever its pair label (checks.py:229-231). The same precedence holds on the screen-error path (campaign.py:824-826). Tested at the pair, accounting, branch and executor levels (test_review_fixes_v9.py:52-74). |
| R5-3 | MINOR | **FIXED** | DRAFT6 §9 (line 183) now says I-1 is not the strict reading. I-3 and §8 (lines 176, 189) say the ΔE_rel rule belongs to the later analysis. `timestep_check` returns `passed=None` for a None or non-finite input (checks.py:354-358), which `numerical_check_consequence` maps to its on-fail consequence (test_review_fixes_v9.py:197-201). A new wording inaccuracy in §9 is reported as V6-3. |
| R5-4 | MINOR | **FIXED** | `IMPLEMENTED_2` values now keep the ruling text separate from labelled "Reading I-n" text (campaign.py:320-349, 364-369). DRAFT6's block matches (lines 283-286, 323). A test checks every reading label (test_review_fixes_v9.py:220-225). |
| R5-5 | MINOR | **FIXED** (documentation) | DRAFT6 §4.2 (lines 124-141) and the machine-block rule (campaign.py:364-369) now cover relative *saving* percentages only. The 1e-12 and 1e-9 denominator floors, the closure check and the shortfall percentages are listed as out of scope. That listing is accurate; `evaluator.py` and `closedloop.py` are unchanged. |
| R5-6 | MINOR | **PARTIALLY FIXED** | A run whose evaluation raised now names its kept files in `retained_files` (campaign.py:794-797). It is still recorded as `executed=False` and `NO_ENERGY_NOT_EXECUTED`; its simulator energy is still missing from `runs.csv`; the separate script still skips it. DRAFT6 §7.7 (line 168) now documents this accurately. No status effect. |
| R5-7 | MINOR | **FIXED** (documentation) | DRAFT6 §4.1 (lines 119-121) states that `evaluation.csv` and `conditions/<id>.json` hold in-process values, and that `conditions.csv` holds the final ones. |
| R5-8 | MINOR | **FIXED**, one residual (V6-1) | The script exits 3 or 4 on a stop or an exception (recompute_from_traces.py:86-98). In the runner, the launch, CSV read, fold and `conditions.csv` write are guarded. Any exit other than 0 or 1 goes to `errors.csv` with the full stderr. A fold that raises triggers `fold_failed`, which leaves nothing COMPARABLE (campaign.py:936-947, 1055-1079; test_review_fixes_v9.py:137-170). |
| R5-9 | MINOR | **FIXED** | There is one `energy_roles` row per planned run. A failure gives `NOT_DETERMINED_ERROR` plus an `errors.csv` row (campaign.py:1106-1134). `ROLE_NOT_DETERMINED` is added to `ENERGY_ROLES` (checks.py:439-441), so the role counts still add up to the planned runs. `energy_role()` never returns it. Tested at test_review_fixes_v9.py:173-193. |
| R5-10 | MINOR | **FIXED** | The old fixtures now include both NOM cells and check the reason: test_amendment2.py:28-33, 71-76, 215-221; test_owner_rulings_v7.py:66-69, 205-209. There are new tests for R5-1 and R5-2. The static-string check for an authorisation writer (test_owner_rulings_v8.py:387-389) is unchanged; my Grep finds no writer. |
| R5-11 | MINOR | **FIXED** | `d_ref` ≤ 0 is now labelled "undefined (d_ref <= 0)" (checks.py:307-309). DRAFT6 §2 (lines 79-82), I-6 (line 192) and the machine-block AMB_30 text are corrected. |
| R5-12 | MINOR | **NOT FIXED** | DRAFT6 line 11 and `code_review_status_v7.json:22` now cite `17_owner_rulings_attempts5_6_report.md`. That file does not exist in PIL (Glob at review time). |
| R5-13 | NOTE | **STATED as requested** | DRAFT6 §1.5 (line 43), §3 (line 101), §8 (line 177). |
| R5-14 | NOTE | **UNCHANGED, as stated** | The record invariant is still non-blocking (campaign.py:1026-1028). Sensitivity counts are not de-duplicated by draw (checks.py:531-536). `dynamic_valid_pair` is still set before the recomputation (campaign.py:814). DRAFT6 line 218 says so. |

## 2. Regressions and new defects in the rev9 changes

**Guards in `run_condition`: correct and fail-closed.**
- A classification exception now gives status ERROR while the runs keep their records (811-818). DRAFT6 does not state this (V6-2).
- With a classification exception, the pair check can in theory still PASS. In practice it cannot: `classify_pair` and the pair block read the same flags. I found no path that produces it.
- If the screen raised for one arm and the other arm's screen showed infeasible, the pair is labelled `CONDITION_ERROR` ("eligibility unknown"), not `NOT_APPLICABLE_QS_INFEASIBLE`. That is the conservative choice and consistent with AMB-29(d) (V6-4).

**`execute_schedule`: correct.**
- `sep_exit` defaults to -1, so a launch failure counts as "unconfirmed".
- A CSV read failure leaves `sep_rows` empty, which also fails closed.
- `rec_ok` for energy roles requires an exit of 0 or 1 (1120).

**New exit codes (V6-1, MINOR):** the import at recompute_from_traces.py:25, and the code at 87-89, sit outside the try. An uncaught exception there makes Python exit with 1, which the runner treats as a result. The outcome is still fail-closed: no CSV is written, so every run is unconfirmed. But nothing goes to `errors.csv`, contrary to IMPLEMENTED_2 ("any other exit … recorded in errors.csv"). Only the last 2,000 characters of stderr appear in the manifest.

**`fold_failed`: correct.**
- Every status becomes non-COMPARABLE, `paired_endpoint_eligible` is set to False, and any PASS, FAIL or REPORTED_ONLY becomes `RUN_INVALID`.
- It does not update `qs_vs_dyn_pair_reason`; this is a reporting gap only (V6-4).

**Precedence change in `pair_qs_dynamic`: no regression.**
- Outside NOM, both labels have no effect.
- In `qs_dynamic_accounting`, the pair now counts as profile-unavailable rather than B0-only ineligible. The eligibility classes still add up.

**Condition-status rule in `branch_qs_dynamic_outcome`: correct.**
- It uses the final status. `PROFILE_UNAVAILABLE` and `BASELINE_UNAVAILABLE` never change in the fold.

**`ROLE_NOT_DETERMINED`: correct.** It is counted in `feasibility_accounting` and never confirmatory. `h3_verdict_eligibility` does not read roles.

## 3. Re-check of focus questions 1-8 on attempt 6

**Q1, rulings as ruled: yes.**
- AMB-29(a): checks.py:147-152 and 229-231.
- AMB-29(b): checks.py:156-182; campaign.py:833-844, 901-933.
- AMB-29(c): checks.py:301-324.
- AMB-29(d): campaign.py:758-883, 998-1007, 1063-1074.
- AMB-30: checks.py:201-270.
- AMB-32: checks.py:503-552.

**Q2, nothing disappears from a denominator and nothing passes by omission: yes.**
- One condition row per scheduled condition (972-1017).
- One role row per planned run (1113-1134).
- `conditions.csv` and the fold are guarded.
- The branch outcomes, the D5 denominator and the verdict keep their fail-closed handlers.
- Planned condition IDs are still passed to the branch outcome (1091).

**Q3, S1 cannot substitute for S2: confirmed.** Only the NOM cells count toward the required PASS (checks.py:220-232, 261-264).

**Q4, a QS-only issue cannot invalidate a valid dynamic run: confirmed.** See R5-1. The tests check that the status stays COMPARABLE and both runs are executed when the screen, its plant or the reporting raise (test_review_fixes_v9.py:78-111).

**Q5, no fabricated percentage: confirmed.**
- No NaN is written as a number; no epsilon, absolute value or substitute threshold is used for any saving percentage.
- `timestep_check` now refuses undefined inputs.
- The tolerance comparisons are unchanged, and DRAFT6 now documents them.

**Q6, the runner is fail-closed: yes.**
- `preconditions` is unchanged apart from `REVIEW_STATUS`, which is now `code_review_status_v7.json` (campaign.py:87).
- `open_major` is 2 there (lines 6-10), which blocks (campaign.py:607-609). The `reviews_pending` item also blocks (611-612; v7 lines 69-72).
- The status file is honest: it says R5-1 and R5-2 stay open until verified and accepted.
- No code writes `campaign_authorization.json` (Grep).
- The location, gate and authorisation checks are unchanged (585-602).

**Q7, does DRAFT6 match the implementation?**
- The machine block matches `IMPLEMENTED_2` key for key, by reading (DRAFT6 lines 262-335 against campaign.py:294-377).
- §6 matches checks.py:201-270.
- §9 I-1 to I-6 describe the code accurately.
- The §12.1 list is complete for what I found.
- The rulings and the readings are now separated.
- **Inaccuracies:**
  - V6-2: §1.6 and §3 omit that a classification exception sets the condition to ERROR. They say "PASS or FAIL" where the code also relabels REPORTED_ONLY (campaign.py:881). The §4.2 table is split by a blank line (DRAFT6 line 131), so its time-step row falls outside the table.
  - V6-3: §9 line 183 says "I-2 to I-6 are the stricter (fail-closed)". I-5 makes no difference to any outcome. For I-6, keeping `NOT_APPLICABLE_*` on an ineligible pair whose run raised is less strict than the alternative (`CONDITION_ERROR`, which gives INCONCLUSIVE).
  - R5-12: the dangling decision-record reference remains.

**Q8, tests not vacuous: yes.**
- The new tests exercise each fix at the unit and executor levels. The old fixtures are repaired.
- No threshold changed: checks.py:18-21 and 498; the schedule SHA-256 `6011e357…` is unchanged in `campaign_config_v9_DRAFT.json:122`.

## 4. Does any CRITICAL or MAJOR finding remain open?

**No CRITICAL or MAJOR finding remains in the code.**
- R5-1 and R5-2 are fixed by reading, and no new CRITICAL or MAJOR defect was found.
- Formally both stay listed as open (`open_major` 2) in `code_review_status_v7.json` until a later status file records this verification and the owner's acceptance. Until then they keep the campaign blocked, together with `reviews_pending` and the missing issued amendment 2, gate and authorisation.

---

## New findings

| ID | Sev | file:line | What | Why it matters | Fix |
|---|---|---|---|---|---|
| V6-1 | MINOR | `ATT6\code\recompute_from_traces.py:25`, `86-89`; campaign.py:1060-1068 | An exception during import or argument handling happens outside the try, so Python exits with 1. The runner treats 1 as a result: no CSV, every run unconfirmed (fail-closed), but no `errors.csv` row, only truncated stderr in the manifest. | Contradicts the `separate_recomputation_exit_codes` statement (campaign.py:372-375; DRAFT6 §7.8). | Move the imports and argument handling inside the try. In the runner, also treat "exit 0 or 1 but no CSV, or an executed run missing from the CSV" as a failure and record it. |
| V6-2 | MINOR | DRAFT6 lines 47-50, 95-96, 131; campaign.py:815-818, 881 | DRAFT6 does not state that a classification exception sets the condition to ERROR. It says "PASS or FAIL" where REPORTED_ONLY is also relabelled. A blank line splits the §4.2 table. | Draft accuracy and readability; no status effect. | Correct the text and the table. |
| V6-3 | MINOR | DRAFT6 line 183 (and rows 191-192) | "I-2 to I-6 are the stricter (fail-closed)" is inaccurate. I-5 makes no difference to any outcome. I-6 is less strict than its alternative for an ineligible pair whose run raised. | The owner is asked to confirm the readings on this basis; it repeats the R5-3 pattern. | Say that I-1 and I-6 (ineligible case) have stricter alternatives, and that I-5 makes no difference. |
| V6-4 | NOTE | campaign.py:755-756, 776-777, 794, 824-829, 945-947 | A few trivial reads before the arms run are unguarded (design keys, screen-result keys, the glob in the except handler). A screen error plus an infeasible other arm is labelled `CONDITION_ERROR` rather than `NOT_APPLICABLE`. `fold_failed` leaves the old pair reason. | Fail-closed or negligible. | Optional. |
| V6-5 | NOTE | `ATT6\config\code_review_status_v7.json:7`, `22` | The key `basis_for_zero_counts` now explains non-zero counts. The R5-12 entry says a record exists that does not. | Record wording. | Correct it in the next status file. |

---

## What I could not verify

- **Test results.** I cannot run tests. `ATT6\logs\pytest_release_attempt6.txt` was still in progress when I read it (13 test results, no summary). The attempt-6 readiness gate, dry run, precondition record and release validation did not exist yet. "258 passed" in `PIL\logs\pytest_run24.txt`, and 10 passed in `pytest_run24a_targeted_v9.txt`, are claims. 258 equals 248 plus the 10 tests in `test_review_fixes_v9.py`, which is consistent.
- **Hashes.** I cannot compute SHA-256 values. The hashes in `copy_verification_attempt6.csv`, `review_scope_attempt6.json` and `zz_code_changes_rev8_to_rev9.csv` agree with each other for `campaign.py`, `checks.py` and `recompute_from_traces.py`, but I did not check them against the files. I read the attempt-6 copies of the code.
- **The decision record.** `17_owner_rulings_attempts5_6_report.md` was absent at review time and may be written later.
