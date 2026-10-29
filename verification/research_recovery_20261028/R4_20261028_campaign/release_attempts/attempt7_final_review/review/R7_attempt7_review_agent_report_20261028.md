# Release attempt 7: independent read-only review report (verbatim)

**Provenance.**
- **Who:** a new, separate **AI review agent** ("Plan" agent type, which has no Edit or Write tools), instructed to use Read, Grep and Glob only. It is not the agent that reviewed attempts 5 and 6. **This is not a human independent audit.**
- **When:** started 2026-10-28 at about 18:14:40 (+0700), after `review_scope_attempt7.json` was written at 18:14:37. It delivered this report at about 18:27:30, after 769 s of work (the agent's reported duration). The time was read from the clock at 18:28:28.
- **Brief:** `review_brief_attempt7_as_sent.md`.
- **State reviewed:**
  - this attempt's `code/` and `config/`: 63 files, SHA-256 in `review_scope_attempt7.json`;
  - amendment 2 candidate rev7, `R4_20261028_pilot/03_protocol_v1_amendment_2_rev7_CANDIDATE.md`, SHA-256 `0e3ef3112c979237e7079f176b21dd4f2ce682c7ab435f36f33321ffe67a5996`;
  - the decision matrix `R4_20261028_pilot/18_owner_decision_matrix_I1_I6.md`.
- **Format:** the text below the line is the agent's final message. The only edit is removing the two-space indentation that the message relay adds.
- **Outcome:**
  - no CRITICAL or MAJOR finding; V6-1, V6-2 and V6-3 are verified FIXED;
  - 7 MINOR and 6 NOTE findings are open, documented for the next revision (`../../../R4_20261028_pilot/19_attempt7_final_review_report.md`);
  - R7-8 was open at review time: its cited record, report 19, was written after this report.

---

I am an AI review agent (a read-only "Plan"-type agent, not a human auditor). I used only the Read, Grep and Glob tools. I ran nothing, wrote nothing, computed no hashes, and used neither Git nor the network. This is not a human independent audit.

**Findings: CRITICAL 0 · MAJOR 0 · MINOR 7 · NOTE 6.** V6-1, V6-2 and V6-3 are FIXED. One new inaccuracy appeared in the rewritten §9 (R7-1, MINOR).

Abbreviations: ATT7 = `...\R4_20261028_campaign\release_attempts\attempt7_final_review`; PIL = `...\R4_20261028_pilot`; DRAFT7/DRAFT6 = the rev7/rev6 candidates; MATRIX = `PIL\18_owner_decision_matrix_I1_I6.md`. Unless stated otherwise, code references are to `ATT7\code\...`.

**How rev9 and rev10 were compared:** I read the changed functions of both versions side by side, and checked the line offsets of everything else. `run_condition`, `fold_separate_recomputation` and `fold_failed` have the same length and the same text. A spot check by Grep shows the PIL code has the same lines as ATT7 at `checks.py:233`, `checks.py:555` and `campaign.py:1100`.

---

## Q1. Is I-1 enforced in every verdict and reporting path?
**Yes.**
- **`checks.branch_qs_dynamic_outcome`** (`checks.py:201-278`):
  - A nominal cell lacks evidence unless its label is exactly PASS or FAIL (`:234`).
  - It also lacks evidence if its condition is PROFILE_/BASELINE_UNAVAILABLE (`:230`), or if it carries a PASS label on a condition that is not COMPARABLE (`:233`).
  - `NOT_APPLICABLE_QS_INFEASIBLE` no longer counts as evidence. In rev9 it was exempt (`rev9 checks.py:230`).
  - `n_PASS_nominal` counts only cells that are not lacking (`:236`). Any count below 2 gives INCONCLUSIVE (`:268-272`).
- **`checks.h3_verdict_eligibility`** (`:550-557`, `:563-565`): rechecks I-1 directly from the rows. Any M0/M1 nominal pair status other than PASS rules out both SUPPORTED and NOT SUPPORTED, whatever the branch outcomes say.
- **`execute_schedule`**:
  - writes both results to `qs_dynamic_branch_outcomes.csv` and `h3_verdict_eligibility.json`, and into the manifest (`campaign.py:1135-1143`, `:1187-1200`);
  - with an exception, the fallback is INCONCLUSIVE and supported/not-supported are False (`:1141`, `:1192`).
- **Other consumers:** Grep finds no other code that reads branch outcomes or the verdict.
- **`NUMERICAL_CHECKS` row 7:** `campaign.py:252-258`; also in config v10 at line 245.
- **`IMPLEMENTED_2`:** `AMB_30_branch_scope` and `I_1_required_nominal_cells` (`campaign.py:337-352`).
- **DRAFT7:** §1.9 (`:62-65`), §2 (`:80`, `:83-84`), §6 (`:153-162`), §8 (`:187`, `:191`).
- **Exception:** the comment at `checks.py:46` is stale (R7-6).

## Q2. Are all required nominal S2 cells accounted for?
**Yes.**
- **Cells:** `NOMINAL_SET`/`NOMINAL_LIMITS` (`checks.py:73-74`); NOM × {L-R1, L-EVE} per motor (`:222-226`). `H3_NOMINAL_CELLS` has all six cells (`:505`), but the QS recheck covers only decisive motors, M0 and M1 (`:551-554`).
- **Absent or duplicated rows:** become `NOT_IN_RECORD` / `DUPLICATE_IN_RECORD` in both functions (`:226`, `:536-537`, `:554`).
- **Planned IDs:** each motor's planned condition IDs are passed in (`campaign.py:1137`). A planned pair missing from the record blocks PASS (`checks.py:237-238`, `:254-255`).
- **M2:** REPORTED_ONLY (`:251-252`); it is not in the QS recheck.
- **Every motor gets a row**, even one with no pairs (`campaign.py:1135`).
- **Condition-level exceptions** still produce a NOM row (`:1020-1027`).
- **Gap:** a row without a status is accepted with a PASS label (`checks.py:233`). This is reachable only from pure-rule inputs (R7-13).

## Q3. Can any non-PASS state produce a PASS or a SUPPORTED / NOT SUPPORTED possibility?
**No path found.**
- **Branch PASS requires all of:**
  - both cells are exactly PASS, are not lacking evidence, and are on COMPARABLE conditions;
  - no FAIL (`:258`), NOT_EVALUABLE (`:261`) or REPORTED_ONLY (`:256`) anywhere;
  - no missing planned row.
- **Rev10 is never looser than rev9:** every input that gives PASS in rev10 also gave PASS in rev9 (by reading). The exhaustive tests support this: 10×10 cell statuses (`test_owner_ruling_i1_v10.py:138-147`), and every subset of the record dropped (`test_owner_rulings_v8.py:131-148`).
- **SUPPORTED / NOT SUPPORTED** remain possible only if:
  - all six nominal cells are COMPARABLE;
  - the M0 and M1 branch outcomes are PASS;
  - every M0/M1 nominal QS cell is PASS (`checks.py:556-557`).

  The code never declares a verdict itself.
- **S1 and other sets cannot substitute.** PASSes in INS, P3, CNV and SEN count only in `n_PASS_other_sets` (`:244-245`).
- **FAIL keeps the frozen consequence** (protocol §9, line 307: "M0/M1 failure → INCONCLUSIVE for that branch"). It is applied in any set (`:258-260`); a NOM FAIL also blocks through `:268`.
- **Thresholds unchanged:** `checks.py:18-21` and `:330`. `schedule_sha256` is `6011e357…` in both config v9 and v10 (line 122).
- **Residual:** a theoretical path outside NOM remains (R7-10, NOTE).

## Q4. Does the I-1 change reclassify a QS-infeasible profile or change any status, role or denominator?
**No.**
- Both I-1 functions only read rows.
- `classify_pair` has no QS input (`checks.py:399-417`). Neither do `energy_role` (`:453-463`) and `feasibility_accounting` (`:466-502`).
- The executor test confirms that a QS-infeasible NOM pair stays COMPARABLE with `dynamic_valid_pair` True (`test_owner_ruling_i1_v10.py:113-126`).
- In the verdict, such a cell keeps `nominal_cells` = COMPARABLE and an empty `nominal_missing_evidence`. Only the QS recheck blocks it (`:110-112`).

## Q5. Is error logging around the separate recomputation complete (V6-1)? Is it still fail-closed?
**Largely yes, and it is fail-closed.** Covered:
- **Start-up and imports:**
  - imports and argument handling now sit inside the try and exit 4 on failure (`recompute_from_traces.py:85-102`);
  - stdlib lines 14-23 remain outside the try, but the runner's "exit … without its output file" check covers them (R7-11).
- **Launch** (`campaign.py:1080-1086`).
- **Unreadable output** (`:1087-1091`).
- **Exit other than 0 or 1** (`:1092-1093`).
- **Exit 0 or 1 with no output file** (`:1094-1095`).
- **Executed runs missing from the output** (`:1096-1100`).
- **Ledger:**
  - full process log (`:1101-1106`);
  - a head row with `stage`, the traceback/stderr and `diagnostic_path`, plus per-run rows with run ID, condition and log (`:1107-1112`);
  - manifest fields `problem`, `process_log` and `runs_not_recomputed` (`:1119-1121`).
- **Fold failure:** recorded, and `fold_failed` applies (`:1113-1118`).
- **`conditions.csv` write failure:** recorded (`:1122-1125`).
- **Fail-closed:**
  - with `sep_exit` -1 or any value outside {0, 1}, every condition loses COMPARABLE and every PASS, FAIL or REPORTED_ONLY becomes RUN_INVALID (`:935-951`);
  - energy roles need an exit of 0 or 1 and a confirmed row (`:1166-1168`).

Gaps (reporting only, no status effect):
- **Missing fields:** the fold, `conditions.csv` and the other post-run rows have no `stage` or `diagnostic_path` (R7-3).
- **Missing per-run rows:** they are written only for runs absent from the output (R7-4).
- **Unguarded writes:** `planner_checks.csv`, `runs.csv`, `evaluation.csv` and the final outputs (R7-5).
- **No timeout:** `subprocess.run` has none (`:1081-1083`). A hung script stalls the campaign; it does not fail open.

## Q6. Are the V6-2 and V6-3 wording defects fixed?
- **V6-2: fixed.**
  - A classification exception now sets the condition to ERROR (DRAFT7 `:49`, §3 `:103`, `:109`).
  - The text says "PASS, FAIL or REPORTED_ONLY" (`:50`, `:102`), matching `campaign.py:901`.
  - The §4.2 table is contiguous (`:134-139`); the test at `test_owner_ruling_i1_v10.py:263` checks this.
- **V6-3: fixed.**
  - The blanket claim of DRAFT6 `:183` is gone.
  - Each row of the §9 table (DRAFT7 `:212-219`) names the stricter option, and each is correct against the code: I-2 alternative; I-3 and I-4 provisional; I-5 neither; I-6 the alternative, for a QS-ineligible pair outside NOM only.
  - However, the new sentence at `:210` is wrong for I-3 (R7-1).

## Q7. Does DRAFT7 match the code?
- **Machine block:** matches `IMPLEMENTED_2` key for key and value for value, by reading. There are 31 keys plus status/amendment/note (DRAFT7 `:277-359` against `campaign.py:294-392`); key order and list order match too.
- **Sections:** §1.9, §2, §3, §6 (including the column list against `checks.py:239-250`), §7.8 and §8 match the code. The exceptions are R7-1 and R7-4, and §7.6 (R7-3).
- **§12.1:** complete for everything I found. It does not list separately that the I-6 text in `AMB_29_condition_error` now adds "an ineligible pair keeps its NOT_APPLICABLE_* label" (`campaign.py:335-336`); this falls under the "Provisional reading" row.
- **Open readings are marked open:** I-2 to I-6 are marked OPEN or "provisional" at DRAFT7 `:3`, `:39`, `:42`, `:48`, `:127`, `:141`, `:162`, `:186`, `:197-219`, `:256` and `:267`.
- **Untagged spots (R7-12):** two places state parts of provisional readings without the tag at that point (`:74` for I-4, `:48` for the eligible-pair label under I-6).
- **A settled statement that is not settled:** `code_review_status_v8.json:70` still says every owner decision has been made (R7-2).
- **The code blocks while any reading is open:**
  - `OWNER_DECISIONS_OPEN` (`campaign.py:395`, `:621-622`) blocks both readiness and campaign mode;
  - `open_owner_decisions` (`v8.json:61-67` via `campaign.py:630`) blocks as well;
  - the test is at `test_owner_ruling_i1_v10.py:238-248`.

## Q8. Is the campaign runner still blocked?
**Yes.**
- **Blockers:** `preconditions("campaign")` (`campaign.py:536-633`) blocks on each of these:
  - an issued amendment 2, APPROVED, whose block equals `IMPLEMENTED_2` (`:577-585`);
  - its approval record with approver, date and SHA-256 (`:586-591`);
  - the §10.1 gate (`:603-607`);
  - the authorisation file, its scope and its three hashes (`:609-616`, `:499-515`);
  - the campaign-root location, by resolved path (`:617-620`);
  - the open owner decisions (`:621-622`);
  - review status: `open_major` 2, open decisions, `reviews_pending` (`:623-632`).
- **Entry points:** `run_campaign` raises before execution (`:639-641`); `run_campaign.py --execute` goes only through it.
- **On disk:** `R4_20261028_campaign\release\` holds only the amendment 1 files (Glob).
- **No code writes `campaign_authorization.json`.** Grep finds only reads (`:609-616`); tests assert that the file is absent.

## Q9. Are the tests meaningful, and were any assertions weakened?
**The new tests are meaningful.**
- **Coverage:**
  - every case of the ruling, at pure-rule level, with forged branch outcomes (to exercise the verdict recheck), and at executor level (`test_owner_ruling_i1_v10.py:57-169`);
  - V6-1 start-up failure, launch failure, exit 4, no output and partial output, each with stage, `diagnostic_path`, per-run IDs and the manifest (`:173-234`);
  - blocking on the open readings (`:238-248`).
- **Changed assertions, each justified by I-1:**
  - `test_amendment2.py:50-57`: a NOM cell that is not applicable is now INCONCLUSIVE;
  - `test_owner_rulings_v8.py:87`: same change;
  - `test_owner_rulings_v8.py:141`: the loop now also covers N/A, which makes it stricter.
- **Fixtures:** the verdict fixtures gained nominal QS statuses (`v7.py:83-84`, `v8.py:37-38`). This is needed so that a "full" record can still be SUPPORTED, and it makes the INCONCLUSIVE tests target their intended cause.
- **Versioning changes:** `test_review_fixes_v9.py:212-214` and `:230-236`.
- **Weakening:** the live review-status file (v8) blocking on `open_major` is no longer asserted (R7-7).

## Q10. Is the decision matrix faithful to DRAFT6 §9?
**The quotes are exact.** I compared all six rows: MATRIX `:40`, `:68`, `:90`, `:111`, `:130` and `:147` against DRAFT6 `:187-192`.
- **Effect statements:** correct against the code, and §0 correctly flags I-3 as the exception (`:23`).
- **Observations (R7-9, NOTE):**
  - The I-2 question is reframed as "outside NOM", with a new alternative, I-2b. DRAFT6's alternative is relabelled I-2c. This is transparent.
  - The "one more case" statement (`:59`) leaves out the other case that now gives INCONCLUSIVE: a PASS label on a nominal condition that is not COMPARABLE.

## Q11. Are there CRITICAL or MAJOR findings?
**None.**

---

## Closure of V6-1 to V6-3

| ID | Verdict | Evidence |
|---|---|---|
| V6-1 | **FIXED** | Imports and arguments are inside the try (`recompute_from_traces.py:85-102`). The runner treats an exit of 0 or 1 without output, or with executed runs missing, as a failure and records it with stage, log and run IDs (`campaign.py:1078-1121`). Tested at `test_owner_ruling_i1_v10.py:173-234`. Residual reporting gaps: R7-3, R7-4. |
| V6-2 | **FIXED** | DRAFT7 `:49-50`, `:102-103`, `:109`, `:131-139`. |
| V6-3 | **FIXED** | DRAFT7 `:197-219`, per-row strictness correct. New inaccuracy in the same section: R7-1. |

V6-5 is fixed (`v8.json:7`, `:22`; `17_…md` exists). V6-4 is unchanged, as documented.

## Findings

| ID | Sev | file:line | What | Why it matters | Fix |
|---|---|---|---|---|---|
| R7-1 | MINOR | DRAFT7 `:210` | Says each of I-2 to I-6 "changes only the QS-versus-dynamic label". I-3 changes no QS label. It changes whether ΔE_rel, S_found/S_max, grid ΔS and the time-step check are computed (`checks.py:336-368`, `:420-431`). MATRIX `:23` says so correctly. | Misstates an open decision's scope in the section the owner decides from. | rev8: name I-3 as the exception. |
| R7-2 | MINOR | `config\code_review_status_v8.json:70` | "Every owner decision for amendment 2 has been made", while `:61-67` lists I-2 to I-6 as open. | A gate-hashed record states as settled what is open. No effect: preconditions block. | Correct it in v9. |
| R7-3 | MINOR | `campaign.py:1027`, `:1047`, `:1065`, `:1117`, `:1125`, `:1132`, `:1140`, `:1148`, `:1157`, `:1176`, `:1185`, `:1191`; DRAFT7 `:173` | These `errors.csv` rows (including the fold and `conditions.csv`) have no `stage` or `diagnostic_path`; the stage appears only as a pseudo `condition_id`. §7.6 claims every row has its stage. | Reporting gap. | Add `stage=`, or reword §7.6. |
| R7-4 | MINOR | `campaign.py:1096-1098`, `:1110-1112`; DRAFT7 `:177`; `campaign.py:385-389` | Per-run rows are written only for executed runs absent from the output. An exit outside {0, 1} after a complete CSV (e.g. `recompute_from_traces.py:80-81` raising) gives no per-run rows. Neither does an executed run present with `recomputed=False` (`:45-48`). In both cases the runs are unconfirmed (`:935-945`). | The ledger is narrower than "every executed run left unrecomputed". Fail-closed. | Define "unrecomputed" as not `recomputed=="True"`, and list every executed run when the exit is outside {0, 1}. |
| R7-5 | MINOR | `campaign.py:1068-1070`, `:1194-1217` (pre-existing, rev9 `:1048-1050`) | The writes of `runs.csv`, `evaluation.csv` and `planner_checks.csv`, and the final writes, are unguarded. An exception aborts the run without `errors.csv` or a manifest. | Protocol §10.4 logging. Fail-closed (no complete verdict record). | Guard these writes and record the failures. |
| R7-6 | MINOR | `checks.py:46` | The comment "NOT_APPLICABLE_* never changes a branch outcome" contradicts I-1 (`:227-235`). | A stale claim in code. | Update the comment. |
| R7-7 | MINOR | `test_review_fixes_v9.py:230-236`, `:223-226` | 1. No test now asserts that the live v8 file (`open_major` 2) blocks. 2. No test covers "unreadable output" or an exit outside {0, 1} with a complete CSV. 3. The check that I-1 is a "reading" passes only through the I-2 text. | Test weakness. | Add the v8 assertion and the missing cases. |
| R7-8 | NOTE | DRAFT7 `:11`; MATRIX `:56` | Both cite `19_attempt7_final_review_report.md`, which was absent at review time (Glob). | Same pattern as R5-12. | Write the file, or correct the reference in rev8. |
| R7-9 | NOTE | MATRIX `:59`, `:70-76` | The I-2 reframing and the incomplete "one more case" statement (see Q10). | The owner's decision basis. | Clarify. |
| R7-10 | NOTE | `campaign.py:831-838`; `checks.py:233` | Outside NOM, a PASS label on a condition whose `classify_pair` raised does not block the branch, although `IMPLEMENTED_2` says "an exception before … the pair evaluation → CONDITION_ERROR". DRAFT7 `:103` documents this. It is unreachable without monkeypatching (see V6). | Theoretical. | Optionally label the pair CONDITION_ERROR. |
| R7-11 | NOTE | `recompute_from_traces.py:10-11`, `:14-23`; `campaign.py:1081` | Lines 14-23 are outside the try (the runner catches the result). There is no subprocess timeout. | Robustness. | Optional. |
| R7-12 | NOTE | DRAFT7 `:74`, `:48` | Parts of the provisional readings I-4 and I-6 are stated without the "provisional" tag at the point of use. They are tagged elsewhere. | Clarity. | Tag them in rev8. |
| R7-13 | NOTE | `checks.py:233` | A row without a status counts with a PASS label. Rows from the executor always carry a status. | Robustness. | Optional. |

## What I could not verify
- **Test results.**
  - I cannot run tests. `PIL\logs\pytest_run25.txt` says "273 passed"; that is 258 plus the 15 new tests, which is consistent.
  - `pytest_run25a` shows an earlier version of the new test failing (a TypeError). `pytest_run25b` shows 2 passed.
  - `readiness_gate_v11.json` records 273/0/0 with the same test-file hashes. All of this is a claim.
  - `ATT7\logs\pytest_release_attempt7.txt` was still in progress (53 results, no summary).
  - The attempt-7 readiness gate, dry run, preconditions and release validation did not exist yet.
- **Hashes.** I cannot compute SHA-256. The hashes in `zz_code_changes_rev9_to_rev10.csv`, `review_scope_attempt7.json`, `copy_verification_attempt7.csv` and `readiness_gate_v11.json` agree with each other for every file I compared. That DRAFT6 is unchanged rests on the pinned hash in a test.
- **Runtime behaviour** (for example, that both arms execute in the toy executor tests) was judged by reading only.
- **Owner acceptance:** I verified none, and none is recorded.
