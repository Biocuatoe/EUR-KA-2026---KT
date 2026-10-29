# Release attempt 9: independent read-only review report (verbatim)

**Provenance.**
- **Who:** a new, separate **AI review agent** ("Plan" agent type, which has no Edit or Write tools), instructed to use Read, Grep and Glob only. It is not the agent that reviewed attempts 5 to 8. **This is not a human independent audit.**
- **When:** 2026-10-28 (+0700):
  - `review_scope_attempt9.json` was written at 22:47:57, and the agent was launched right after;
  - it ran without interruption for 1,101.7 s (the agent's reported duration), so it started about 22:48:25;
  - it delivered this report at 23:06:47 (transcript timestamp 2026-10-28T16:06:47.535Z).
- **Brief:** `review_brief_attempt9_as_sent.md`.
- **State reviewed:**
  - this attempt's `code/` and `config/`: 69 files, SHA-256 in `review_scope_attempt9.json`;
  - amendment 2 candidate rev9, `R4_20261028_pilot/03_protocol_v1_amendment_2_rev9_CANDIDATE.md`, SHA-256 `cdeea032c520f408f1f300a53cf1bc8b1ec4582d80340d3df2c2c94fa5d45719`.
- **Format:** the text below the line is the agent's final message, copied programmatically from the session transcript (29,937 characters), unmodified.
- **Outcome:**
  - **1 MAJOR finding (R9-1) is open in this attempt.** As the task requires, it is fixed in a new attempt, `../attempt10_review_fixes/`; this attempt is kept unchanged as reviewed.
  - R8-1 to R8-6 are verified FIXED.

---

I am an AI review agent (a read-only "Plan"-type agent), not a human auditor. I used only the Read, Grep and Glob tools. I ran nothing, wrote nothing, computed no hashes, and used neither Git nor the network. This is not a human independent audit.

**New findings: CRITICAL 0 · MAJOR 1 · MINOR 2 · NOTE 5.**
- The three R8 MAJOR findings (R8-1 to R8-3) and the three R8 MINOR findings (R8-4 to R8-6) are fixed.
- Notes R8-8, R8-9 and R8-10 are addressed. R8-7 and R8-11 are not addressed; both deferrals are stated and acceptable.
- The new MAJOR finding, R9-1, is an exception that the QS screen swallows. The code is older than rev12. The I-6 ruling, and rev12's own claim that the rule holds "at every stage", now make it non-compliant.
- No path to a campaign start was found. The campaign stays blocked.

Abbreviations:
- **ATT9** = `...\R4_20261028_campaign\release_attempts\attempt9_review_fixes`
- **PIL** = `...\R4_20261028_pilot`
- **DRAFT9** = `PIL\03_protocol_v1_amendment_2_rev9_CANDIDATE.md`; **DRAFT8** = the rev8 candidate
- **MATRIX** = `PIL\18_owner_decision_matrix_I1_I6.md`; **DEC15** = `PIL\15_remaining_owner_decisions.md`
- **v12 tests** = `ATT9\code\tests\test_review_fixes_v12.py`; **v11 tests** = `test_owner_decisions_v11.py`; **A2 tests** = `test_amendment2.py`
- **v10** = `ATT9\config\code_review_status_v10.json`
- **MUT** = `PIL\logs\zz_mutation_check_v12_tests_on_rev11.txt`
- **rev11** = `PIL\archive\rev11_attempt8_20261028_2126\code`
- Unless stated otherwise, `campaign.py` and `checks.py` mean `ATT9\code\r4h3\...`.

**How rev11 and rev12 were compared:**
- I read every changed region of both versions side by side: `run_condition`, the fold, `fold_failed`, `execute_schedule`, `IMPLEMENTED_2`, the branch outcome and the accounting.
- rev12 `checks.py:346-608` is identical to rev11 `:311-574`.
- `preconditions` and `run_campaign` are identical (rev12 `:561-670`, rev11 `:546-655`).
- The PIL code, which produced the pilot test logs, matches ATT9 at the nine changed lines I checked: `campaign.py:911`, `:972`, `:1111`, `:1189`, `:1288`; `checks.py:141`, `:261`, `:298`, `:326`.

---

## Closure of R8-1 to R8-11

| ID | Verdict | Evidence | Regression test; what MUT shows |
|---|---|---|---|
| R8-1 | **FIXED** (the owner's confirmation of the label is pending, see Q2) | `campaign.py:909-916` no longer exempts FAIL; the earlier label goes to `before_error` (`:913`); `fail_arms` is kept (`:958`). `IMPLEMENTED_2` `:327-343` (block DRAFT9 `:341`). DRAFT9 §1.14 `:93-99`, §2 `:121`, `:125`, §3 `:143-144`. | v12 `:111-130` (run_report exception, both arms FAIL) fails on rev11 behaviourally (MUT `:16-20`). The exact R8-1 case (a run raised, the other valid arm FAILs) is v11 `:119-123` (I6FL). It was **not** in the mutation run. By reading, rev11 `campaign.py:888` kept FAIL, so it would fail there. Residual: R9-2. |
| R8-2 | **FIXED** | `checks.py:298-343`: applicability is counted from `qs_vs_dyn_applicability`, and there are two new status columns. `campaign.py:869-873`, `:955`. DRAFT9 §7 `:209-214`, §9 `:256`. | v12 `:134-145` (executor level) fails on rev11 behaviourally: the applicability sum is 0, not 1 (MUT `:35-39`). v12 `:148-158` fails on rev11 only because `pair_applicability` is missing (MUT `:45-47`); that is not behavioural evidence. Residual: R9-4. |
| R8-3 | **FIXED** | DRAFT9 §1.6 `:47` | v12 `:162-166` (text check); fails against the DRAFT8 text (MUT `:55-60`). |
| R8-4 | **FIXED** (tests added) | v12 `:170-183` (classify, run_report and condition_report with a NOT_APPLICABLE pair); `:186-199` (in-process I-4, now behavioural); `:134-145` (accounting after an override). | These are regression guards, not evidence of a behaviour change, which is expected for a test-gap finding. The three stage cases pass on rev11 (MUT `:184-186`). The I-4 test's behavioural asserts (`:197-198`) also pass on rev11; it fails there only on the new name `QS_APPLICABLE` (MUT `:83-85`). By reading, removing the gate at `campaign.py:893` would make `:198` fail. |
| R8-5 | **FIXED** | `guarded()` now sits before the loop (`:1061-1066`). Each `conditions/<id>.json` write is guarded (`:1111-1114`). A failed process-log write has stage `write recomputation_independent_process.log` (`:1186-1190`). `conditions.csv` is guarded (`:1207`). `output_write_failures` selects by stage prefix (`:1288`). `_write_text` (`:968-969`) keeps the old encoding and line endings. DRAFT9 §7.6 `:218-221`. | v12 `:203-223` is behavioural on rev12. On rev11 it fails only because `_write_text` does not exist (MUT `:94-96`), so the log is no behavioural evidence. By reading, rev11 `:1052-1054` (unguarded write) and `:1245` (filter on `OUTPUT-WRITE`) confirm both gaps were real. |
| R8-6 | **FIXED** | `IMPLEMENTED_2` `:327-343` and block DRAFT9 `:341` no longer say a FAIL "stays FAIL". | v12 `:129-130`. Not reached on rev11, because that test fails earlier at `:117`. |
| R8-7 (NOTE) | **NOT ADDRESSED** (deferred, stated) | DRAFT9 `:11` still cites `20_attempt8_final_owner_decisions_report.md`, and Glob finds no such file. DRAFT9 `:288` and v10 `:45` say it is written after this review. | v12 `:301` checks that the citation is present, not that the file exists. |
| R8-8 (NOTE) | **ADDRESSED** | v10 `:41`, `:46`; DRAFT9 `:288` | v12 `:279`, `:301` |
| R8-9 (NOTE) | **ADDRESSED** | `campaign.py:972-980`, `:989`, `:1018-1019`, `:1035`, `:1198`. DRAFT9 §1.12 `:84`, §2 `:132`, §7.8 `:227`. | v12 `:227-252`. On rev11 it fails at the five-argument call (TypeError, MUT `:115-116`), so the log is no behavioural evidence. Its `fold_failed` part (`:240-242`) and executor part (`:243-252`) would have failed behaviourally on rev11, but are never reached. |
| R8-10 (NOTE) | **ADDRESSED** | `campaign.py:869-872`: a failed screen now takes precedence over a screen exception. Also `:876-878`. | v12 `:255-269` fails on rev11 behaviourally: rev11 gives UNKNOWN (MUT `:137-141`). |
| R8-11 (NOTE) | **NOT ADDRESSED** (by choice) | MATRIX `:7-9` and `:27-34` are unchanged; DRAFT9 `:286` explains why. | Acceptable: DRAFT9 cites MATRIX only for the interpretations considered. |

**What MUT shows overall.** 11 of the 14 new tests fail on rev11 (MUT `:198`):
- **Behavioural failures:** R8-1 via run_report (`:117`), R8-2 at executor level (`:141`), R8-10 (`:268`), and the R8-3 text check.
- **Failures only because a new name or signature is missing:** R8-2 (pure rule), the R8-4 I-4 test, R8-5 and R8-9.
- **Versioning only:** the v10 status test, the rev9 candidate test and the "5 major" blocking test (MUT `:148-149`, `:162-167`, `:177-179`).
- **Not part of the run:** the changed v11 I6FL test and the changed A2 R3-9 test.

## Q2. I-6

**Can a NOT_APPLICABLE_\*, PASS, REPORTED_ONLY or FAIL label survive an exception?** Stage by stage:
- **run:** no. Recorded at `:835-843`. The override (`:909-916`) gives `NOT_EVALUABLE_RUN_MISSING` if the pair is APPLICABLE, otherwise `NOT_EVALUABLE_CONDITION_ERROR`, a FAIL included.
- **run_report:** no. `:854-855`, then the override gives CONDITION_ERROR (v12 `:111-130`, `:170-183`).
- **qs_screen** (an exception from `QSPlant` or `checks.qs_screen`): no. `:806-820` and `:875-882` give CONDITION_ERROR, with the N/A label kept in `before_error` (`:877`).
  - **Exception:** an exception inside the per-piece diagnosis (`checks.qs_piece_diagnosis`) is caught inside `checks.qs_screen` (`checks.py:140-141`). It never reaches `errors.csv`, and the pair stays `NOT_APPLICABLE_QS_INFEASIBLE`. This is **R9-1 (MAJOR)**.
- **classify:** no. `:860-863`, then the override gives CONDITION_ERROR (v12 `:170-183`).
- **qs_vs_dynamic:** no. `:898-903` give CONDITION_ERROR.
- **condition_report:** no. `:942-950` relabel PASS, FAIL, REPORTED_ONLY and N/A to CONDITION_ERROR, with the earlier label in `before_error`.
- **condition-level:** no. `:1093-1103` give CONDITION_ERROR, applicability UNKNOWN, `qs_eligible_pair` None.
- **separate recomputation:** no.
  - A per-run exception in the script aborts the whole script with exit 4 (`recompute_from_traces.py:39-60`, `:100-102`), so the script swallows nothing.
  - On an exit other than 0 or 1, a launch failure, or a missing or unreadable output, N/A pairs become CONDITION_ERROR (`:1018-1019`). PASS, FAIL and REPORTED_ONLY become RUN_INVALID (`:1007-1017`).
- **fold:** no. `fold_failed` (`:1022-1035`).
- **Later stages** (accounting, branch outcome, denominator, energy role, feasibility, verdict, output writes) do not relabel pairs. They run after the pair evaluation, and a branch or verdict exception fails closed (`:1223`, `:1274-1275`). I treat them as outside "a run or evaluation".

**Is a measured FAIL kept visible after an override?**
- **For the in-process override and the condition_report relabel: yes.**
  - `conditions.csv`: `qs_vs_dyn_pair_status_before_error` (`:913`, `:948`, `:956`) and `qs_vs_dyn_fail_arms` (`:958`).
  - Accounting: `fail_before_exception` (`checks.py:337`).
  - Branch outcome: `n_FAIL_before_exception`, `fail_before_exception_by_set` and a reason line (`checks.py:260-262`, `:278-281`).
- **Not on two other paths (R9-2, MINOR; no outcome effect):**
  - After a separate-recomputation failure or a fold exception, a FAIL becomes RUN_INVALID. Its value is kept only in `qs_vs_dyn_pair_status_in_process` (`:1014`, `:1033`), and it is not counted.
  - A qs_vs_dynamic-stage exception discards any arm FAIL already computed (`:901`).

**The `NOT_EVALUABLE_RUN_MISSING` label for a QS-eligible pair whose run raised:**
- **Consistent with the rulings.**
  - The AMB-29(b) operative wording covers it: "no finite dynamic energy (an exception, or a non-finite simulator energy)" (DEC15 `:74`).
  - I-6 requires only the NOT_EVALUABLE class. Both labels give the same outcome (`checks.py:244`, `:274-277`).
- **It departs from one matrix column, but the matrix itself left the question open.**
  - The I-6b column is headed "always NOT_EVALUABLE_CONDITION_ERROR". It lists CONDITION_ERROR for "QS-eligible pair, the other valid arm FAILs" (MATRIX `:149-152`).
  - But the matrix made the eligible-pair label a separate, optional question (`:166`, `:168`), and the owner did not answer it.
- **Presented honestly.** It is not silently settled and not presented as an owner ruling:
  - DRAFT9 §1.14 `:98` ("Label reading, for the owner's confirmation"), §9 `:245`, §15 `:308`;
  - v10 `:98` and `:110-112` (`implementer_readings_for_owner_confirmation`);
  - v10's I-6 ruling entry (`:95`) does not claim the label.
- **Two presentation gaps (R9-5, NOTE):**
  - The machine block states the label inside the sentence "Owner ruling I-6 (2026-10-28): …" without marking it as a reading (`campaign.py:333-336`; DRAFT9 `:341`).
  - §1.14 `:98` does not mention the I-6b column header.

**Are the three concepts kept separate and counted separately? Yes.**
- **QS applicability:** `qs_vs_dyn_applicability` and `qs_eligible_pair` (`:869-873`, `:954-955`); counted at `checks.py:330-332`.
- **Dynamic validity:** the condition status and `dynamic_valid_pair` (`:857-863`, `:952`, `:959`); counted in `feasibility_accounting` (`checks.py:517`, `:536`).
- **Evaluation status:** `qs_vs_dyn_pair_status` (`:956`); counted at `checks.py:333-338` and in the branch's `n_*` counts.

## Q3. R8-2 accounting

**Do the rows add up?**
- **By applicability: always, by construction.** `pair_applicability` (`checks.py:298-308`) returns one of exactly four values or raises.
- **By pair status: whenever every status is one of the nine `PAIR_QS_STATUSES`.** Executor rows always are. The accounting does not reject an unknown status itself; the branch outcome does (`:227-229`).

**Case by case:**
- **Override** (run, run_report, classify): the applicability class is unchanged; the status is RUN_MISSING or CONDITION_ERROR. ✓ (v12 `:134-145`)
- **Condition-level exception:** UNKNOWN + CONDITION_ERROR. ✓ (A2 `:236-243`)
- **QS-screen exception:** ✓ in every variant (`:871-878`; v11 `:95-107`; v12 `:255-269`).
  - with no profile problem: UNKNOWN + CONDITION_ERROR;
  - with a missing profile: NOT_APPLICABLE_PROFILE_UNAVAILABLE + CONDITION_ERROR;
  - with a failed profile: NOT_APPLICABLE_QS_INFEASIBLE + CONDITION_ERROR, with the failed arm in `qs_ineligible_arms`.
- **`QSPlant` construction fails and both profiles are missing:** `screen_errors` is empty, the pair is NOT_APPLICABLE_PROFILE_UNAVAILABLE, and `:909` then makes it CONDITION_ERROR. ✓
- **Separate-recomputation failure and fold failure:** applicability unchanged. ✓ (v12 `:243-252`)
- **Rows without `qs_vs_dyn_applicability`:** the fallback reads the N/A label or `qs_eligible_pair`. ✓ (v12 `:148-158`)

**Is `qs_eligible_pair` consistent with `qs_vs_dyn_applicability`?** Yes, on every path.
- It is derived from the applicability (`:873`, `:876`, `:902`, `:955`), or set together with it (`:1097`).
- Neither fold changes either value.
- Residue (R9-4, NOTE): on the qs_vs_dynamic-exception path, `qs_ineligible_arms` is empty even when the pair is NOT_APPLICABLE_QS_INFEASIBLE (`:902`). The B0/B3/both split then does not add up to `qs_ineligible_pairs`.

**Is the changed R3-9 assertion (A2 `:317-319`) justified? Yes.**
- Both screens passed, so N-A2 applicability is known, and I-6 requires it to be kept apart from the evaluation status.
- The owner's AMB-29(d) words (DRAFT9 `:46`) do not require "eligibility unknown". That phrase is in the pre-ruling wording (DEC15 `:111`, `:169`), where it describes the usual case.
- The change is listed in DRAFT9 `:272`, and the CONDITION_ERROR assertion is unchanged.

## Q4. I-1 to I-5: no regression found

- **I-1.**
  - The nominal-cell logic is identical (rev12 `checks.py:231-246` and rev11 `:223-238`), and so is `h3_verdict_eligibility` (rev12 `:557-608`, rev11 `:522-573`).
  - The I-1 test file is unchanged (`zz_code_changes` `:34`).
  - The new override only adds NOT_EVALUABLE labels, never a PASS.
- **I-2.**
  - A NOT_APPLICABLE_PROFILE_UNAVAILABLE pair is never a PASS; `feasibility_accounting` is unchanged; v11 `:127-141` is unchanged.
  - The accounting is now better: a profile-less pair overridden by I-6 still counts in `not_applicable_profile_unavailable`.
  - See R9-6 for the fold.
- **I-3.** The guarded functions are identical (`:346-405`, `:457-468`); v11 `:144-164` is unchanged.
- **I-4.**
  - The in-process gate `campaign.py:893` equals rev11 `:873`, and the fold rule `:1005-1017` equals rev11 `:963-975`.
  - It is now also tested behaviourally (v12 `:186-199`).
- **I-5.** The label at `checks.py:53` is unchanged; it reads the same in `IMPLEMENTED_2` `:320-326`, DRAFT9 §1.13 `:86-89` and v11 `:179-191`.
- **DRAFT9.** §1.9 to §1.13 equal DRAFT8 `:62-88`, plus one I-6 bullet in §1.12 (`:84`).

## Q5. Does DRAFT9 match the implementation?

**Machine block.** I compared DRAFT9 `:317-403` with `IMPLEMENTED_2` (`campaign.py:294-417`): all 34 keys value by value and in order, plus `amendment`, `status` and `note`. They match, including the new keys:
- `qs_applicability_values` equals `list(QS_ELIGIBLE_BY_APPLICABILITY)` (`checks.py:68-69`);
- `qs_dynamic_accounting_classes` is present.

The match is also asserted by v12 `:290-291`.

**Text, section by section:**
- **§1.6 `:47-50`:** match (R8-3 fixed).
- **Not true when the QS-screen diagnosis raises (R9-1):**
  - §1.6 `:51` and §1.14 `:93`, which claim the rule holds at every stage, `qs_screen` included;
  - §2 `:123` ("An exception in the pair makes it NOT_EVALUABLE_CONDITION_ERROR");
  - §1.1 `:20` and `N_A2_failed_check_record` (`campaign.py:308-309`): the exact failed check is not kept in that case.
- **§1.12 `:84`:** matches `:989`, `:1018-1019` and `:1035`.
- **§1.14 `:94-104`:** match, except `:99` (R9-2).
- **§2 `:121-132`:** match.
- **§3 `:140-147`:** match. **§3 `:148`** gives the condition status ERROR also after a separate-recomputation or fold failure. In fact the status is kept, or becomes RECOMPUTATION_DISAGREEMENT (`:1002-1003`, `:1029-1030`). This is **R9-3 (MINOR)**.
- **§6 `:206`:** matches `checks.py:249-263`.
- **§7.2 `:211-214`:** matches `:326-342` (split caveat in R9-4).
- **§7.6 `:218-221`** and **§7.8 `:223-227`:** match.
- **§9 `:245-256`:** accurate now that R8-2 is fixed.
- **§12.1 `:266-290`:** complete for the code changes. Only trivial items are unlisted: the reason wording at `:949-950` and the `_by_set` key parameter.
- **§13 `:296-302`** and **§15 `:307-311`:** consistent with v10.

**Thresholds** are unchanged: DRAFT9 `:15`, `checks.py:18-21`, block `:329-333`, config v12 `:277`.

**Parent hashes** are all present and identical to DRAFT8 `:7-10`:
- protocol `f9826318…`;
- amendment 1 `7720fed7…`, equal to `campaign.py:66`;
- rev8 `f6430bf5…`, equal to the R8 report `:13`;
- rev7 `0e3ef311…`;
- rev6 `0dcb767e…`, equal to MATRIX `:5`;
- rev5 to rev0.

**DRAFT marking** is in place: line 3, block `"status": "DRAFT"` (`:321`), and the note (`:402`).

## Q6. Is v10 honest? Yes.

- **`open_major` 5** (`:6`) with its basis (`:7`): R5-1 and R5-2 stay until the owner accepts their closure; R8-1 to R8-3 stay as "not yet verified". Nothing is lowered.
- **The R8 entries** (`:11-13`, `:42-49`) agree with my closure table. R8-7 and R8-11 are correctly not claimed as fixed.
- **Rulings, release steps and the reading are kept apart:**
  - `owner_rulings_implemented` (`:81-96`) lists N-A2, AMB-29(a)-(d), AMB-30, AMB-31, AMB-32 and I-1 to I-6. The I-6 entry states the ruling without the label reading.
  - `pending_release_steps` is a separate list (`:99-105`).
  - The implementer reading is listed separately (`:110-112`).
  - `open_owner_decisions` is [] (`:80`).
  - Nothing claims that an open item is complete.
- **`reviews_pending`** (`:106-108`) names this review, and its rule (`:109`) keeps it until a later status file.
- **Next step:** R9-1 should be counted in the next status file's `open_major`.

## Q7. Is the runner fail-closed? Yes.

`preconditions` and `run_campaign` are unchanged from rev11. Campaign mode is blocked independently by each of these:
- issued amendment 1 and its approval (`:589-601`);
- issued amendment 2, APPROVED, with its block equal to `IMPLEMENTED_2` (`:602-610`);
- the amendment 2 approval record (`:611-616`);
- the §10.1 gate (`:628-632`);
- `campaign_authorization.json`, with its scope and three hashes (`:633-641`, `:524-540`);
- the campaign-root location, by resolved path (`:642-645`);
- open owner decisions (`:646-647`, `:655`);
- `open_major` (`:652-654`);
- `reviews_pending` (`:656-657`).

**The pending review still blocks.** With v10, `open_major` 5 and `reviews_pending` block both modes (asserted at v12 `:273-283` and `:305-310`).

**Entry points and files:**
- `run_campaign.py --execute` goes only through `run_campaign` (`run_campaign.py:29-33`).
- No code writes `campaign_authorization.json` or the issued amendment 2. Grep finds only reads and test assertions.
- On disk, `R4_20261028_campaign\release\` holds only the amendment 1 files and an old dry run (Glob).
- The schedule is unchanged: `schedule_sha256` is `6011e357…` in both config v11 and v12 (`:122`).

## Q8. Tests

**The new tests are not vacuous.** They drive the real `run_condition` and `execute_schedule`, including the real separate process. Each injects one fault and asserts the label, the applicability, `before_error`, the stages or the sums.
- Toy-result dependency: v12 `:186-199` needs the toy B0 arm not to FAIL its QS check. I judged this by reading; the logs claim it passes.

**Gaps:**
- no test injects an exception into `qs_piece_diagnosis` (R9-1);
- no test checks FAIL visibility on the fold paths (R9-2).

**Changed assertions, each justified:**
- v11 `:119-123`: FAIL becomes RUN_MISSING with `before_error` FAIL (R8-1, I-6).
- A2 `:317-319`: None becomes True with APPLICABLE (I-6, R8-2).
- v11 `:276-288`: v9 is read by path and `REVIEW_STATUS` is patched to v9 (versioning). The live-file check moved to v12 `:273-283`.
- v11 `:291-307`: rev8 is pinned by hash and read only for its status (versioning). The test name "…matches_the_code" is now stale (R9-7).

**Unchanged tests whose meaning changed:** A2 `:108-112` and `test_owner_rulings_v8.py:338-341`.
- They sum a "status" decomposition that includes `qs_ineligible_pairs` and `not_applicable_profile_unavailable`. rev12 redefines both as applicability counts.
- They still pass because their fixtures contain no overridden N/A pair. With one, they would fail, not pass (R9-7).

**Thresholds and tuning.** No threshold changed (`checks.py:18-21`; A2 `:84-86`). Nothing is tuned: the only synthetic percentage is the forged FAIL `diff_pct` 2.0 (v12 `:89-90`, v11 `:116-117`).

## Q9. New defects from the rev12 changes

- **The override:** correct; it can only produce NOT_EVALUABLE.
  - RUN_MISSING is used only for an APPLICABLE pair with a stage-`run` error (`:911`), which implies an arm without energy.
  - Gap on the fold paths: R9-2.
- **Applicability:** correct on every path (residue in R9-4).
- **The accounting:** correct (residue in R9-4).
- **The fold changes:** correct, but they over-reach to pairs with no executed run (R9-6).
- **The moved guard and `_write_text`:**
  - The closure runs immediately.
  - Encoding and line endings are the same as before: `:968-969` against rev11 `:1052-1054`, `:1140-1141`, `:1236-1237`, `:1243-1244`.
- **The branch-outcome fields:** correct. The new reason line only adds to a branch that is already INCONCLUSIVE.
- **An older inconsistency the new relabel path exposes:** R9-8.

## Q10. Are there CRITICAL or MAJOR findings?

- **CRITICAL:** none found. See the caveat in R9-1.
- **MAJOR:** R9-1. R8-1 to R8-3 are closed.

---

## Findings

| ID | Sev | file:line | What | Why it matters | Fix |
|---|---|---|---|---|---|
| R9-1 | MAJOR | `checks.py:132-142` (catch `:140-141`); `campaign.py:816`, `:870-872`, `:909`; DRAFT9 `:20`, `:51`, `:93`, `:123`; `IMPLEMENTED_2:308-309`; protocol `03_R4_protocol_v1.md:335` | `checks.qs_screen` runs `qs_piece_diagnosis` for every infeasible piece. An exception there is caught and stored only as text in that piece (`failed_checks=["diagnosis error: …"]`, `nodes=[]`). There is no `errors.csv` row, traceback, stage or run ID. The executor sees a normal screen result, so the pair stays `NOT_APPLICABLE_QS_INFEASIBLE` and the override at `:909` never fires. The code is unchanged from rev11 (`checks.py:125-135`), and no earlier review flagged it. | It conflicts with protocol §10.4 ("Exceptions go to `errors.csv` with the traceback"). It also conflicts with I-6 ("Preserve the exception, stage, affected run ID"; NOT_APPLICABLE never overrides an exception) and with rev12's own "every stage, qs_screen included" claim. Outside NOM the surviving N/A label leaves the M0/M1 branch unaffected, so the branch could PASS where the I-6 rule as implemented elsewhere gives INCONCLUSIVE. **Why MAJOR, not CRITICAL:** the `QSPlant.step` verdict behind the N/A label is computed without error, and the owner has not said whether a diagnostic-only sub-step counts as "evaluation". Under the broad reading the code already applies to the diagnostic-only run_report stage, this would meet the CRITICAL definition. | Let the exception propagate, or return it, and record it in `errors.csv` with stage `qs_screen`, the run ID and the traceback. Treat the pair as after a screen error: CONDITION_ERROR, applicability NOT_APPLICABLE_QS_INFEASIBLE kept, `before_error` the N/A label. Add a regression test that injects an exception into `qs_piece_diagnosis`. If the owner rules diagnostics out of I-6, still log the exception (§10.4) and narrow DRAFT9 `:51`, `:93` and `:123`. |
| R9-2 | MINOR | `campaign.py:1011-1017`, `:1032-1034`, `:898-903` (`:901`); `checks.py:261-262`, `:337`; DRAFT9 `:99` | A measured FAIL stays fully visible only after the in-process override and the condition_report relabel. After a separate-recomputation failure or a fold exception, a FAIL becomes RUN_INVALID. Its value is kept only in `qs_vs_dyn_pair_status_in_process`, without `before_error`, so it is not counted in `fail_before_exception` or `n_FAIL_before_exception`. (`_na_pair_not_evaluable` at `:977` does set `before_error` for N/A pairs.) A qs_vs_dynamic-stage exception discards any arm FAIL already computed (`:901`). | §1.14 `:99` ("A measured failure is never hidden … counted as `fail_before_exception`") overstates. There is no status or outcome effect: every such pair is NOT_EVALUABLE, hence INCONCLUSIVE. | Set `before_error` in the exception-driven fold relabels. Keep the arm results computed before a qs_vs_dynamic exception. Or narrow `:99`. |
| R9-3 | MINOR | DRAFT9 §3 `:148` | The row covering "…or the separate recomputation or its fold failed" gives the condition status `ERROR`. In fact the condition keeps its status, or becomes `RECOMPUTATION_DISAGREEMENT` if it was COMPARABLE (`:1002-1003`, `:1029-1030`). | The candidate wording misstates a condition status. The code is unaffected. | Split the row: ERROR for a run exception; otherwise unchanged or RECOMPUTATION_DISAGREEMENT. |
| R9-4 | NOTE | `campaign.py:898-903`; `checks.py:331`, `:333-338` | (a) On the qs_vs_dynamic-exception path with applicability NOT_APPLICABLE_QS_INFEASIBLE, `before_error` and `qs_ineligible_arms` are empty, unlike the screen-error branch (`:877-878`). The B0/B3/both split then does not add up to `qs_ineligible_pairs`. This path is reachable only through an exception in pure code. (b) The accounting does not reject an unknown pair status. | Reporting precision: DRAFT9 §7.2 `:212` says the count is "split into" the three. | In that branch, set `before_error` to the applicability and `ineligible_arms` to the failed arms. Optionally reject unknown statuses in the accounting. |
| R9-5 | NOTE | `campaign.py:333-336` (block DRAFT9 `:341`); DRAFT9 `:98`; MATRIX `:149-152`, `:166`, `:168` | The RUN_MISSING reading is flagged honestly in the prose and in v10. But the machine block, which the owner would approve verbatim, states it inside "Owner ruling I-6 (2026-10-28): …". And `:98` does not mention that the I-6b column was headed "always NOT_EVALUABLE_CONDITION_ERROR" and listed CONDITION_ERROR for this exact case. | The owner should see the full basis when confirming. No outcome effect. | Cite MATRIX `:149-152` in §1.14 and in report 20, and record the owner's answer in the approval record. |
| R9-6 | NOTE | `campaign.py:972-980`, `:1018-1019`, `:1035` | After a separate-recomputation or fold failure, every N/A pair becomes CONDITION_ERROR, including pairs none of whose runs was executed (for example, both profiles missing). | This is stricter than I-6 ("a run or evaluation raises"). It is also in tension with I-2 ("inconclusive only when required evidence for that specific check is missing or invalid"). No outcome effect: after a process failure no PASS remains, so every M0/M1 branch is INCONCLUSIVE anyway. | Restrict the relabel to pairs with an executed run, or record it as a deliberate fail-closed reading for the owner's confirmation. |
| R9-7 | NOTE | A2 `:108-112`; `test_owner_rulings_v8.py:338-341`; v11 `:291`, `:297`; MUT | (a) Two unchanged tests now mix applicability columns into a "status" sum. (b) The v11 rev8 test's name says "matches_the_code", but it no longer checks a match. (c) MUT shows behavioural failure on rev11 only for R8-1 (run_report path), R8-2 (executor level), R8-10 and the R8-3 text. R8-5 and R8-9 fail only on missing names or signatures, and I6FL and R3-9 were not run. | The tests' meaning has drifted, and the mutation evidence is weaker than its 11-of-14 count suggests. | Use the `qs_check_not_applicable_*` columns in the two sums and rename the rev8 test. Add mutation variants for R8-5 (patch `Path.write_text`) and R8-9 (call `fold_failed` and the executor path first). |
| R9-8 | NOTE | `campaign.py:917-950` | After a condition_report exception, the per-arm `qs_vs_dyn_pair_status` in the evaluation rows keeps the label from before the relabel. Those rows are updated at `:918-928`, before the failing statement. Example: NOT_APPLICABLE_QS_INFEASIBLE in the condition_report case of v12 `:170-183`. Meanwhile `conditions.csv` and `conditions/<id>.json` say CONDITION_ERROR. The behaviour predates rev12. | Two in-process records disagree. DRAFT9 §4.1 `:171` already says only `conditions.csv` is final. | Update the evaluation rows after the relabel, or say so in §4.1. |

## What I could not verify

- **Test results** are all claims:
  - `PIL\logs\pytest_run27.txt` ends "302 passed" (`:310`), consistent with 288 plus the 14 new tests;
  - `pytest_run27a_targeted_v12.txt` reports "61 passed" (`:65`);
  - `readiness_gate_v13.json` records 302 tests, 0 failures, 0 errors (`:32-35`).
- **The attempt's own outputs:** `ATT9\logs\pytest_release_attempt9.txt` contains no results yet. The attempt's readiness gate, dry run, preconditions and release validation are not in `ATT9\logs`.
- **MUT** is a claim. Its output is consistent with the rev11 modules (rev8 text, v9 status), but I cannot confirm how it was run.
- **Hashes:** I cannot compute SHA-256.
  - `review_scope_attempt9.json`, `zz_code_changes_rev11_to_rev12.csv` and `readiness_gate_v13.json` agree for every entry I compared: `campaign.py`, `checks.py`, the changed tests, v10 and config v12.
  - I did not compare the files marked unchanged line by line. Exceptions: I read `recompute_from_traces.py` in full, and compared `preconditions` and `run_campaign` with rev11.
- **Runtime behaviour** was judged by reading. Examples: that both toy arms are §8.2-valid in v12 `:111-130`, and that the toy B0 arm passes its QS check in v12 `:186-199`.
- **R9-1 reachability:** I found no concrete input that makes `qs_piece_diagnosis` raise. R9-1 is about what happens if it does.
- **Owner records:** no owner acceptance and no owner answer on the label are recorded. Report 20 does not exist.
- **Not read:** `GATE_RECORD_attempt8.json` and `ATTEMPT_NOTE_attempt8.md`.
