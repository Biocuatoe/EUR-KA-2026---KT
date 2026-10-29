# Release attempt 10: independent read-only review report (verbatim)

**Provenance.**
- **Who:** a new, separate **AI review agent** ("Plan" agent type, which has no Edit or Write tools), instructed to use Read, Grep and Glob only. It is not the agent that reviewed attempts 5 to 9. **This is not a human independent audit.**
- **When:** 2026-10-28 to 2026-10-29 (+0700):
  - `review_scope_attempt10.json` was written at 2026-10-29 00:31:51, and the agent was launched right after (before 00:32:26);
  - it stopped on the account's session limit at 00:41:20 (HTTP 429; transcript 2026-10-28T17:41:20Z);
  - it was resumed with its own context at about 05:27:47, told only that some of the attempt's outputs might now exist and are claims;
  - it delivered this report at 05:31:00 (transcript timestamp 2026-10-28T22:31:00.820Z), 202.7 s after resumption (the agent's reported duration for the resumed part).
- **Brief:** `review_brief_attempt10_as_sent.md`.
- **State reviewed:**
  - this attempt's `code/` and `config/`: 72 files, SHA-256 in `review_scope_attempt10.json`;
  - amendment 2 candidate rev10, `R4_20261028_pilot/03_protocol_v1_amendment_2_rev10_CANDIDATE.md`, SHA-256 `5479f0e81b981c7977ea5a416762972d2a332d4fdb75beee7ad8379ade399804`.
- **Format:** the text below the line is the agent's final message, copied programmatically from the session transcript (27,829 characters), unmodified.
- **Outcome:**
  - **no CRITICAL or MAJOR finding**; R9-1 to R9-3 are verified FIXED, and R9-4 to R9-8 ADDRESSED;
  - one MINOR finding (R10-1, the wording of the machine block) and three notes are open and recorded for the owner; under the task rule they do not require a new attempt.

---

I am an AI review agent (a read-only "Plan"-type agent), not a human auditor. I used only the Read, Grep and Glob tools. I ran nothing, wrote nothing, computed no hashes, and used neither Git nor the network. This is not a human independent audit. A service rate limit interrupted this review once; I resumed it with the same brief and rules.

**New findings: CRITICAL 0 · MAJOR 0 · MINOR 1 · NOTE 3.**
- The MAJOR finding R9-1 and the MINOR findings R9-2 and R9-3 are FIXED. Notes R9-4 to R9-8 are ADDRESSED (R9-8 by documentation only, as stated).
- The new MINOR finding, R10-1, is a wording defect in the binding machine block, and repeats the pattern R9-5 flagged. It has no effect on any status, denominator, outcome or verdict.
- No path to a campaign start was found. The campaign stays blocked.

Abbreviations:
- **ATT10** = `...\R4_20261028_campaign\release_attempts\attempt10_review_fixes`; **PIL** = `...\R4_20261028_pilot`
- **DRAFT10** = `PIL\03_protocol_v1_amendment_2_rev10_CANDIDATE.md`; **DRAFT9** = the rev9 candidate
- **MATRIX** = `PIL\18_owner_decision_matrix_I1_I6.md`; **DEC15** = `PIL\15_remaining_owner_decisions.md`
- **rev12** = `PIL\archive\rev12_attempt9_20261028_2308\code`
- **v11** = `ATT10\config\code_review_status_v11.json`
- **v13 tests**, **v12 tests**, **v11 tests** = `test_review_fixes_v13.py`, `test_review_fixes_v12.py`, `test_owner_decisions_v11.py`; **A2** = `test_amendment2.py`; **v8 tests** = `test_owner_rulings_v8.py`
- **MUT13** = `PIL\logs\zz_mutation_check_v13_tests_on_rev12.txt`; **MUT12b** = `PIL\logs\zz_mutation_check_v12_r8_5_r8_9_tests_on_rev11.txt`
- Unless stated otherwise, `campaign.py` and `checks.py` mean `ATT10\code\r4h3\...`.

**How rev12 and rev13 were compared.** I read both versions side by side.
- **checks.py changes:** `import traceback` (`:14`); `qs_screen` (`:134-148`, against rev12 `:132-142`); the unknown-status rejection in `qs_dynamic_accounting` (`:330-332`). Everything else I compared is identical, including `branch_qs_dynamic_outcome` (`:217-301` against rev12 `:211-295`) and `h3_verdict_eligibility` (`:566-617` against rev12 `:557-608`).
- **campaign.py changes:**
  - the three version pointers (`:67`, `:87-88`);
  - two `IMPLEMENTED_2` keys (`:308-311`, `:335-348`);
  - `run_condition` (`:826-833`, `:911-921`);
  - `_na_pair_not_evaluable`, `fold_separate_recomputation` and `fold_failed` (`:990-1066`);
  - `execute_schedule` (`:1228-1235`).
- `preconditions` and `run_campaign` (`:566-675`) are identical to rev12 `:561-670`.
- The PIL code, which produced the pilot test logs, matches ATT10 at every changed line I grep'd: checks `:137`, `:140`, `:147`, `:331`; campaign `:829`, `:832`, `:1011`, `:1042`, `:1051`, `:1228`.
- The SHA-256 values agree across `review_scope_attempt10.json`, `zz_code_changes_rev12_to_rev13.csv` and `readiness_gate_v14.json` for every entry I compared.

---

## 1. Closure of R9-1 to R9-8

| ID | Verdict | Evidence | Regression test; what the mutation logs show |
|---|---|---|---|
| R9-1 (MAJOR) | **FIXED** | `checks.qs_screen` returns each diagnosis exception (piece and full traceback) in `diagnosis_errors` (`checks.py:140`, `:145-147`). `run_condition` writes one `errors.csv` row per exception, with stage `qs_screen`, `run_id`, `run_ids` and the traceback (`campaign.py:829-831`), and adds the arm to `screen_errors` (`:832-833`). The pair is then `NOT_EVALUABLE_CONDITION_ERROR`, the N/A label goes to `before_error`, and `ineligible_arms` holds the failed arms (`:888-895`). The screen verdict is kept (`qs_feasible`, `:834`, `:971`), and so is the applicability `NOT_APPLICABLE_QS_INFEASIBLE` (`:883-885`). Text: block `N_A2_failed_check_record` (`:308-311`; DRAFT10 `:336`); DRAFT10 §1.1 `:20`, §1.6 `:47`, `:51`, §1.14 `:93`, §3 `:148`. | v13 `:74-97`. **Behavioural** on rev12: MUT13 `:21-24` fails at `:86` with no `qs_screen` error recorded. Not vacuous: it has a control run (`:80-81`), injects at `qs_piece_diagnosis`, and asserts the traceback, run IDs, verdict, label, applicability, the untouched runs and the pure function. |
| R9-2 (MINOR) | **FIXED** | (a) After a process failure, the fold keeps a relabelled PASS, FAIL or REPORTED_ONLY in `before_error` (`campaign.py:1042-1043`); `fold_failed` does the same (`:1063-1064`). (b) A `qs_vs_dynamic`-stage exception no longer resets `arm_checks`. It keeps a valid arm's FAIL in `fail_arms` and `before_error` (`:916-920`). DRAFT10 §1.14 `:99` is now accurate. | v13 `:101-121` is behavioural (MUT13 `:39-44`). It also asserts that the non-exception I-4 path does not set `before_error` (`:119-121`), which is the correct discrimination. v13 `:124-139` is behavioural (MUT13 `:65-70`). |
| R9-3 (MINOR) | **FIXED** | DRAFT10 §3 `:148-149` splits the row. After a run or classification exception the condition is ERROR. It is unchanged after a QS-screen, diagnosis or report exception. After a separate-recomputation or fold failure it is unchanged, or `RECOMPUTATION_DISAGREEMENT` if it was COMPARABLE. This matches `campaign.py:1026-1027`, `:1056-1057` and `checks.classify_pair` (`:451-463`). | v13 `:195-197` (text). On rev12 the test fails earlier, at `:191` (the R9-5 assertion), so MUT13 is no evidence for this part. By reading, DRAFT9's merged row would fail `:196`. |
| R9-4 (NOTE) | **ADDRESSED** | (a) `campaign.py:917-920` keeps a known N/A label in `before_error` and the failed arms in `qs_ineligible_arms`. (b) `checks.py:330-332` rejects an unknown pair status. | v13 `:143-154`. Part (a) is behavioural (MUT13 `:84-89`). Part (b), `:153-154`, is not reached on rev12. By reading it would fail there, because rev12 maps an unknown status to UNKNOWN applicability and does not raise (rev12 `checks.py:302-307`). |
| R9-5 (NOTE) | **ADDRESSED** (residual: R10-1) | The block now marks the label as an implementer reading: "Implementer reading of the standing AMB-29(b) ruling, for the owner's confirmation … the matrix's I-6b column listed CONDITION_ERROR" (`campaign.py:345-348`; DRAFT10 `:340`). §1.14 `:98` cites the I-6b column (MATRIX `:149-152`) and §3.5. | v13 `:189-194` (text and block). It fails on rev12 at `:191` (MUT13 `:111-112`). |
| R9-6 (NOTE) | **ADDRESSED** by restriction (residuals: R10-1, R10-2) | `_na_pair_not_evaluable` returns early for a pair none of whose runs was executed (`campaign.py:995-996`). `execute_schedule` passes the executed run IDs (`:1228`, `:1230`, `:1235`). The prose labels this as an implementer reading: DRAFT10 §1.12 `:84`, §9 `:246`, §12 `:275`, §15 `:307`; v11 `:120`. | v13 `:158-185`. On rev12 it fails **only on the new signature**, a TypeError at `:164` (MUT13 `:103-104`). That is not behavioural evidence. Its behavioural executor part (`:169-185`) never runs on rev12 (R10-2). |
| R9-7 (NOTE) | **ADDRESSED** | (a) The status sums now use the status columns: A2 `:108-112` and v8 `:338-342`. Both are stronger than before; the old A2 sum lacked `not_evaluable_run_invalid`. (b) The rev8 test is renamed (v11 `:291`). (c) The R8-5 test now injects at `Path.write_text` (v12 `:203-219`), and the R8-9 test calls first what every version accepts (v12 `:229-235`). | MUT12b shows both tests failing on rev11 **behaviourally**. R8-5 fails on the unguarded `conditions/<id>.json` write (rev11 `campaign.py:1052`; MUT12b `:27-38`). R8-9 fails because `fold_failed` leaves N/A unchanged (MUT12b `:53-60`). Residuals: I6FL and R3-9 are still not in any mutation run, and the new R9-6 test has the same ordering weakness (R10-2). |
| R9-8 (NOTE) | **ADDRESSED** (documentation; code unchanged, as stated) | DRAFT10 §4.1 `:172`. The code at `campaign.py:935-968` is still as described. | No test needed for a documentation fix. |

**What the mutation logs show overall.**
- **MUT13:** 9 of 9 v13 tests fail on rev12.
  - **Behavioural:** R9-1, R9-2 (both tests) and R9-4(a).
  - **Text or block content:** the R9-5 and R9-3 test (fails at its R9-5 part).
  - **Versioning only:** the status v11, rev10-candidate and blocking tests.
  - **Signature only:** R9-6.
- **MUT12b:** behavioural for R8-5 and R8-9 on rev11, as R9-7 asked.
- Both logs are claims. They are consistent with the archived modules named in their first two lines, but I cannot confirm how the runner was invoked.

## 2. R9-1 and every other caught exception

**Inside the QS screen, every exception is now recorded and makes the pair NOT_EVALUABLE.**

| Where it raises | How it is recorded |
|---|---|
| `QSPlant` construction | `campaign.py:811-817`: stage `qs_screen`, both run IDs, traceback. `screen_errors` gets every arm with a profile. With no profile at all, the I-6 override (`:927-934`) applies. |
| `qs_energy` / `QSPlant.step` | Propagates out of `checks.qs_screen` (`checks.py:139`, not caught there) and is caught at `campaign.py:820-826`: stage `qs_screen`, the arm's run ID, `run_ids`, traceback. |
| `qs_piece_diagnosis`, including its `rebuild.model` import | `checks.py:142-147` → `campaign.py:829-833`, with the piece named in the traceback field. |
| Later uses of the screen result | `qs_screen[b]["E_J"]` in the pair check is inside the try at `:887-921`; the run-report fields at `:862-868`; the warning text at `:947-949`. All are guarded and recorded. |

- A diagnosis runs only on infeasible pieces, so `qs_feasible[b]` is False, and precedence gives applicability `NOT_APPLICABLE_QS_INFEASIBLE` (`:883-885`), with `qs_eligible_pair` False.
- The pair is `NOT_EVALUABLE_CONDITION_ERROR` with `before_error` set to the N/A label (`:888-895`).
- The dynamic runs and the condition status are untouched (v13 `:91`).
- The only production caller of `checks.qs_screen` is `campaign.py:821` (Grep). A future caller that ignored `diagnosis_errors` would lose the record again. That is acceptable as long as the documentation (`checks.py:136-138`) stays.

**Every other `except` in `ATT10\code\r4h3` and `recompute_from_traces.py`:**

| Catch | Feeds | Recorded? / effect |
|---|---|---|
| `campaign.py:447` (JSON of an amendment block) | campaign gate | → blocker via `read_amendment` errors; fail-closed |
| `:575`, `:579`, `:587`, `:636` (preconditions) | campaign gate | → blockers; fail-closed |
| `:813`, `:822`, `:829-833`, `:848`, `:867`, `:873`, `:911`, `:960` (`run_condition`) | pair, condition | → `_errors` → `errors.csv` (`:1140`, `:1321-1326`) with stage and run ID(s) |
| `:852` (glob inside the run handler) | condition | if it raises, the exception goes to `:1124` (stage `condition`, chained traceback); recorded; pair CE |
| `:1095` (`guarded`), `:1124`, `:1172`, `:1194`, `:1198`, `:1219`, `:1231`, `:1244`, `:1252`, `:1260`, `:1270`, `:1288`, `:1297`, `:1303` (`execute_schedule`) | writes, condition, grid, separate recomputation, fold, accounting, branch, denominator, roles, feasibility, verdict | → `errors.csv` with a stage; branch → INCONCLUSIVE, role → `NOT_DETERMINED_ERROR`, verdict → INCONCLUSIVE |
| `:1327` (`errors.csv` write) | ledger | → manifest `errors_csv_write_failure` |
| `:1373` (dry run) | dry run only | → `dry_run.json` |
| `slice.py:233`, `:247` | smoke test only | `:233` → manifest ERROR; `:247` silently drops the scipy version, metadata only |
| `recompute_from_traces.py:32-35` (`_value`, ValueError) | separate confirmation | parse fallback, not an error swallow. A numeric field left as a string makes `compare_with_simulator` raise TypeError (`evaluator.py:293`, `:301`) → exit 4 → `campaign.py:1201-1202`, `:1222-1227`. A NaN fails `x <= tol` (`evaluator.py:327`, `:334`). Either way it fails closed. |
| `recompute_from_traces.py:97-102` | separate confirmation | exit 3 or 4 with the traceback on stderr → recorded by the runner |

**Conclusion:** no catch on a path to a pair status, condition status, energy role, denominator or verdict leaves an exception unrecorded. I did not inspect the frozen upstream modules (`r3_lib`, `rebuild`, `eureka`) for internal exception handling.

## 3. I-6 overall

**Can a label survive an exception?** In process, no:
- `run` → RUN_MISSING (eligible) or CE (`:927-934`);
- `run_report` and `classify` → override to CE;
- `qs_screen` (plant, energy or diagnosis) → CE (`:888-895`);
- `qs_vs_dynamic` → CE (`:911-921`);
- `condition_report` → CE (`:965-968`);
- condition-level → CE (`:1124-1134`).

After the run, a label survives in three cases:
- **Deliberately (the R9-6 reading):** a `NOT_APPLICABLE_*` pair none of whose runs was executed keeps its label after a separate-recomputation or fold failure (`:995-996`).
- **Pre-existing, as R9 accepted:** exceptions at post-fold stages (output writes, accounting, branch, roles, feasibility, verdict) relabel no pair. Their own outputs fail closed.
- **Pre-existing, not an exception:** "an executed run missing from the output" (`:1208-1210`) is recorded in `errors.csv` but is not a process failure. N/A labels stay, and PASS, FAIL or REPORTED_ONLY become RUN_INVALID without `before_error`. That is consistent with I-4 (non-confirmation) and practically unreachable, because the script reads every `runs.csv` row.

**Is a measured FAIL kept visible?** Yes, on all five named paths:
- in-process override: `before_error` FAIL, `fail_arms` kept (`:930-931`);
- `condition_report`: `:966`;
- `qs_vs_dynamic`: `:916-920`;
- separate-recomputation failure: `:1042-1043`;
- fold failure: `:1063-1064`.

Each is counted in `checks.py:346` and `:267-268`. One edge remains:
- If the fold raises after it has already relabelled a FAIL whose failing arm was unconfirmed, with no process failure, that FAIL stays only in `qs_vs_dyn_pair_status_in_process`.
- That is consistent with I-4, since the FAIL rests on unconfirmed energy. It is not a finding.

**The R9-6 restriction is consistent with I-6 and I-2.**
- I-6 applies when "a run or evaluation raises". A pair with no executed run has no run that the failed separate process evaluated.
- I-2 makes a check inconclusive "only when required evidence for that specific check is missing or invalid". A pair without profiles has no evidence that the process failure could affect.
- It has no outcome effect. After any such failure every PASS becomes RUN_INVALID (`:1031-1039`, `:1060-1062`), so every M0/M1 branch is INCONCLUSIVE anyway.

**Is it presented honestly as an implementer reading?**
- **Yes in the prose and the status file:** DRAFT10 `:84`, `:246`, `:275`, `:307`; v11 `:118-121`.
- **No in the machine block**, which the owner approves verbatim. The block states "after a failure of the separate recomputation or its fold a NOT_APPLICABLE_* pair with an executed run is NOT_EVALUABLE_CONDITION_ERROR" inside "Owner ruling I-6 (2026-10-28): …" without marking it (`campaign.py:340-343`; DRAFT10 `:340`). This is **R10-1**.

**Is the RUN_MISSING reading marked in the block?** Yes (`campaign.py:345-348`). Its closing clause, "any other pair with an exception is NOT_EVALUABLE_CONDITION_ERROR", glosses over RUN_INVALID after a recomputation failure and over NOT_EVALUABLE labels that stay; see R10-1.

**The three concepts stay separate:**
- applicability (`:883-886`, `:972-973`);
- dynamic validity (status `:870`, `:977`);
- evaluation status (`:974`).

## 4. Accounting decompositions

- **By applicability:** they always add up. `pair_applicability` returns one of four values or raises (`checks.py:304-314`).
- **By status:** they now always add up when the function returns, because an unknown status raises (`checks.py:330-332`).
- **No executor path creates an unknown status.** Every assignment uses `PAIR_QS_STATUSES`: `campaign.py:889`, `:910`, `:917`, `:930`, `:966`, `:1000`, `:1039`, `:1062`, `:1129`.
- **The B0/B3/both split now adds up to `qs_ineligible_pairs` on every executor path:** `pair_qs_dynamic` `:170`, screen error `:891`, `qs_vs_dynamic` exception `:920`; the overrides inherit it; condition-level rows have UNKNOWN and "".
- **The new rejection fails closed in the executor:**
  - the accounting exception goes to `errors.csv` and an error row (`campaign.py:1242-1247`);
  - the branch outcome rejects independently (`checks.py:233-235`), giving INCONCLUSIVE (`campaign.py:1250-1257`);
  - the verdict then blocks on `qs_block` (`checks.py:595`).
- **Pilot tests (claims):** the executor-level sums are asserted at v12 `:139-144` and `:251-252`, and v8 `:335-342`.

## 5. I-1 to I-5 and the R8 fixes: no regression from rev12

| Item | Evidence |
|---|---|
| I-1 | `branch_qs_dynamic_outcome` and `h3_verdict_eligibility` are identical to rev12 (see the comparison above). |
| I-2 | Unchanged. R9-6 now keeps `NOT_APPLICABLE_PROFILE_UNAVAILABLE` for a pair with no executed run after a process failure, which is closer to I-2. v11 `:127-141` is unchanged. |
| I-3 | `non_positive_term`, `qs_vs_dynamic`, `scenario_totals`, `grid_convergence`, `timestep_check` and `paired_delta` are identical (`checks.py:89-94`, `:355-414`, `:466-477`). |
| I-4 | The in-process gate `campaign.py:906` equals rev12 `:893`. The fold rule `:1031-1041` equals rev12 `:1007-1017`; the only addition is `:1042-1043`. |
| I-5 | `checks.py:55` is unchanged. |
| R8-1 | Override `:927-934` equals rev12 `:909-916`. |
| R8-2 | `pair_applicability` is unchanged. |
| R8-5 | `:1092-1097`, `:1142-1145`, `:1217-1221`, `:1239`, `:1320` are unchanged. |
| R8-9 | Kept, now restricted as described under R9-6. |
| R8-10 | `:884-885` is unchanged. |

## 6. Does DRAFT10 match the implementation?

**Machine block.**
- The two changed keys match `IMPLEMENTED_2` value for value: `N_A2_failed_check_record` (`campaign.py:308-311` = DRAFT10 `:336`) and `AMB_29_condition_error` (`:329-348` = `:340`).
- Every other key is unchanged from rev12's `IMPLEMENTED_2` (rev12 `:294-417`), and the block keys match by reading.
- v13 `:216-217` asserts `read_amendment` gives no errors (a claim; it passed in the logs).

**Sections:**
- **Accurate:**
  - §1.1 `:20`; §1.6 `:47`, `:51`; §1.12 `:84`; §1.14 `:93-99`;
  - §2 `:121-132`; §3 `:140-150`; §4.1 `:172`; §7.2 `:215`; §7.8 `:228`;
  - §9 `:246`; §13 `:297`; §15 `:307`.
- **§12.1 `:271-289` is complete for the code changes.** I found no unlisted change; the added `continue` at `:826` is trivial.
- **Wording slips (R10-3):** `:3` says "six of its notes" (R9 had five), and the heading `:19` still says "(unchanged from rev3)".

**Thresholds** are unchanged: DRAFT10 `:15`; block `:328-332`; `checks.py:20-23`; config v13 `:277`. The schedule is unchanged: `schedule_sha256` `6011e357…` in both config v12 and v13 (`:122`).

**Parent hashes** are all present (DRAFT10 `:7-10`):
- protocol `f9826318…`;
- amendment 1 `7720fed7…`, equal to `campaign.py:66`;
- rev9 `cdeea032…`, equal to the R9 report `:12`;
- rev8 `f6430bf5…`, and rev7 to rev0.

`03_protocol_v1_amendment_2_rev10_CANDIDATE.sha256.txt:1` gives `5479f0e8…`, equal to `review_scope_attempt10.json:10`.

**DRAFT marking** is in place: `:3` ("DRAFT — NOT APPROVED FOR RELEASE"), block `"status": "DRAFT"` (`:320`), and the note (`:401`).

## 7. Is v11 honest? Yes.

- **`open_major` 6** (`:6`), with its basis (`:7`):
  - R5-1, R5-2 and R8-1 to R8-3 stay until the owner accepts their closure;
  - R9-1 stays as "not yet verified";
  - nothing is lowered.
- **The R8 entries** (`:11-13`, `:43-50`) and **the R9 entries** (`:14`, `:51-57`) agree with my closure table. The R9-6 and R9-8 entries correctly say "restricting" and "documented; code not changed".
- **Rulings, release steps and readings are kept apart:**
  - `owner_rulings_implemented` (`:89-104`) states rulings only; the I-6 entry `:103` does not claim either reading;
  - `pending_release_steps` (`:107-113`) is a separate list;
  - the two `implementer_readings_for_owner_confirmation` (`:118-121`) are listed separately;
  - `open_owner_decisions` is `[]` (`:88`).
  - Nothing claims that a pending step is complete.
- **`reviews_pending`** (`:114-116`) names this review, and its rule (`:117`) keeps it until a later status file records the outcome and the owner's acceptance.
- **Not yet recorded anywhere:** the R10-1 wording issue in the block.

## 8. Is the runner fail-closed? Yes.

`preconditions` and `run_campaign` are identical to rev12. Campaign mode is blocked independently by each of these:
- issued amendment 1 and its approval (`:594-606`);
- issued amendment 2, APPROVED, with its block equal to `IMPLEMENTED_2` (`:607-615`);
- the amendment 2 approval record (`:616-621`);
- the §10.1 gate (`:633-637`);
- `campaign_authorization.json`, with its scope and three SHA-256 values (`:639-646`, `:529-545`);
- the campaign-root location, by resolved path (`:647-650`);
- open owner decisions (`:651-652`);
- `open_major` (`:657-659`);
- `reviews_pending` (`:661-662`).

**The pending review still blocks.** With v11, `open_major` 6 and `reviews_pending` block both modes (asserted at v13 `:201-209` and `:230-235`).

**Entry points and files:**
- `run_campaign.py --execute` goes only through `run_campaign` (`run_campaign.py:29-36`).
- No code writes `campaign_authorization.json`, the issued amendment 2 or its approval record. Grep finds only path constants (`campaign.py:64`, `:68-69`) and a test assertion (v8 `:391`).
- `R4_20261028_campaign\release\` holds only the amendment 1 files and an old dry run (Glob).

## 9. Tests

**The new tests are not vacuous.** They drive the real `run_condition`, `execute_schedule` and the real separate process, inject one fault each, and include controls (v13 `:80-81`, `:116-121`, `:162-168`). The toy-result dependency is the same as in R9: both GENTLE arms valid, and `_is_b0` telling the arms apart. I judged it by reading; the logs claim the tests pass.

**Changed assertions, each justified:**
- A2 `:108-112` and v8 `:338-342`: stronger (R9-7).
- v12 R8-5 `:203-219`: same assertions, a more realistic injection point (R9-7).
- v12 R8-9 `:229-242`: reordered, with an added `before_error` assertion (R9-7).
- v12 v10-status test `:273-285`: reads v10 by path (versioning).
- v12 rev9 test `:288-306`: now pins rev9's hash; its code-match moved to v13 `:212-227` (versioning).
- v12 blocking test `:309-316`: reads the live count, `n >= 5`. Slightly looser, but v13 `:234` asserts exactly 6 (versioning).
- v11 `:291`: renamed only.

**Thresholds and tuning.** No threshold changed (A2 `:84-86`). The only synthetic percentage is the forged FAIL `diff_pct` 2.0 (v13 `:64-66`). Nothing is tuned toward a legacy number.

**Gaps:**
- R10-2 (R9-6 and R9-4(b) not shown behaviourally);
- I6FL (v11 `:116-123`) and R3-9 (A2 `:307-322`) are still in no mutation run.

## 10. New defects; CRITICAL or MAJOR?

- **The rev13 changes are correct.** Each one only narrows a label to NOT_EVALUABLE, keeps more information, or (R9-6) restricts a relabel with no outcome effect.
- **New in rev13:** R10-1 (block wording), R10-3 (candidate wording) and R10-4 (robustness of the fail-closed fallback).
- **CRITICAL:** none. No path produces a PASS, SUPPORTED or NOT SUPPORTED contrary to a ruling, and no path starts the campaign.
- **MAJOR:** none.

---

## Findings

| ID | Sev | file:line | What | Why it matters | Fix |
|---|---|---|---|---|---|
| R10-1 | MINOR | `campaign.py:340-343`, `:347-348`; DRAFT10 `:340` (block); compare DRAFT10 `:84`, `:246`, v11 `:120` | The new R9-6 scope reading ("a NOT_APPLICABLE_* pair **with an executed run**"), and the R8-9 extension of I-6 to the separate recomputation it qualifies, sit inside "Owner ruling I-6 (2026-10-28): …" in the machine block, unmarked. The prose and v11 call it an implementer reading for the owner's confirmation. The block's closing clause, "any other pair with an exception is NOT_EVALUABLE_CONDITION_ERROR", also omits RUN_INVALID after a recomputation failure and the NOT_EVALUABLE labels that stay. These are stated correctly elsewhere in the same value and in §1.14 `:94-97`. | The owner approves the block verbatim, so approving it would attribute an implementer reading to the owner's I-6 ruling. This is the pattern R9-5 flagged, repeated for a new reading. No status or outcome effect; R9 rated the analogous issue a NOTE, and I rate it MINOR because it is a defect in binding text. | Move the "with an executed run" restriction into the "Implementer reading … for the owner's confirmation" sentence, as was done for RUN_MISSING. Make the closing clause precise ("any other pair with an exception is NOT_EVALUABLE_CONDITION_ERROR, except RUN_INVALID as above; a NOT_EVALUABLE_* label stays"). Record the owner's answers on both readings in the approval record. |
| R10-2 | NOTE | v13 `:162-168` before `:169-185`; MUT13 `:103-104`; v13 `:153-154` | The R9-6 test calls the new six-argument `fold_separate_recomputation` first, so on rev12 it fails only with a TypeError. Its behavioural executor part is never reached. The R9-4(b) unknown-status assertion is likewise never reached on rev12 (the test fails earlier, at `:149`). | This is the weakness R9-7(c) asked to fix for R8-9. By reading, both parts would fail on rev12 behaviourally (rev12 `campaign.py:972-980` relabels unconditionally; rev12 `checks.py:302-307` does not raise). | Run the executor part (and `fold_failed` without `executed`) first, or split the R9-4(b) check into its own test. Add both to the mutation run, together with I6FL and R3-9. |
| R10-3 | NOTE | DRAFT10 `:3`, `:19` | `:3` says rev10 fixes "six of its notes". R9 had five notes (R9 report `:22`), and R9-8 is documented, not fixed. The §1.1 heading still says "(unchanged from rev3)", although rev10 added a sentence at `:20` (listed in §12 `:278`). The added sentence also sits inside the N-A2 ruling paragraph. | Wording only. | Change "six" to "five (one by documentation)". Change the heading to "(rev3; one sentence added in rev10)", or move the sentence out of the ruling paragraph. |
| R10-4 | NOTE | `campaign.py:1065-1066`, `:1231-1235` | `fold_failed` now indexes `conds[i]`. It is called unguarded inside the fold's `except` handler, so an exception there would abort `execute_schedule` before `errors.csv` and the manifest are written. rev12's `fold_failed` did not touch `conds`. | Not reachable with the executor's own inputs, which are built one to one. If it were reached, the run would fail closed (no outputs, no verdict) but without the §10.4 ledger. | Optionally guard the `fold_failed` call, recording its own failure in the manifest, or fall back to `run_ids=None` when the indexing fails. |

## What I could not verify

- **Test results** are all claims:
  - `ATT10\logs\pytest_release_attempt10.txt:319` ("311 passed"); its xml: tests 311, failures 0, errors 0;
  - `PIL\logs\pytest_run28.txt:319` ("311 passed");
  - `pytest_run28a_targeted_v13.txt:94` ("89 passed");
  - `readiness_gate_v14.json:32-34`.
- **The attempt's other outputs** do not exist yet in `ATT10\logs`: its readiness gate, dry run, preconditions, release validation, and the gate record and attempt note for attempt 10.
- **MUT13 and MUT12b** are claims. They are consistent with the archived modules they name, but I cannot confirm how the runner was invoked.
- **Hashes:** I computed none. I only compared the recorded values across files.
- **Unchanged files:** I did not compare them line by line. Exceptions: `preconditions` and `run_campaign`, `h3_verdict_eligibility` and the `checks.py` regions shown above. `recompute_from_traces.py` I read in full.
- **Runtime behaviour** was judged by reading. Examples: the toy arms being valid and eligible in v13 `:124-139`; the B3 knots not being on the 1 s grid.
- **Frozen upstream modules** (`r3_lib`, `rebuild`, `eureka`) were not inspected for internal exception handling.
- **R9-1 reachability:** I found no concrete input that makes `qs_piece_diagnosis` raise.
- **Owner records:** no owner confirmation of either implementer reading and no owner acceptance are recorded. `20_attempt8_final_owner_decisions_report.md` does not exist (Glob), as DRAFT10 `:287` states (R8-7, still deferred).
