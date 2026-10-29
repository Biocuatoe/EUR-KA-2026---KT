# Release attempt 11: independent read-only review report (verbatim)

**Provenance.**
- **Who:** a new, separate **AI review agent** ("Plan" agent type, which has no Edit or Write tools), instructed to use Read, Grep and Glob only. It is not the agent that reviewed attempts 5 to 10. **This is not a human independent audit.**
- **When:** 2026-10-29 (+0700):
  - `review_scope_attempt11.json` was written at 07:45:53, and the agent was launched right after;
  - it ran without interruption for 1,112.0 s (the agent's reported duration), so it started about 07:46:32;
  - it delivered this report at 08:05:04 (transcript timestamp 2026-10-29T01:05:04.741Z).
- **Brief:** `review_brief_attempt11_as_sent.md`.
- **State reviewed:**
  - this attempt's `code/` and `config/`: 76 files, SHA-256 in `review_scope_attempt11.json`;
  - amendment 2 candidate rev12, `R4_20261028_pilot/03_protocol_v1_amendment_2_rev12_CANDIDATE.md`, SHA-256 `ac376c0b362c2e99a9d3777fa849205844487e0be50a41dd1c5f1b2410b5ae1b`.
- **Format:** the text below the line is the agent's final message, copied programmatically from the session transcript (26,143 characters), unmodified.
- **Outcome:**
  - **1 MAJOR finding (R11-1, wording of the machine block) is open in this attempt.** As required, it is corrected in a new attempt, `../attempt12_final_owner_decisions/`; this attempt is kept unchanged as reviewed.
  - The rev14 code changes are confirmed correct and narrow.

---

I am an AI review agent (a read-only "Plan"-type agent), not a human auditor. I used only the Read, Grep and Glob tools. I ran nothing, wrote nothing, computed no hashes, and used neither Git nor the network. This is not a human independent audit.

**New findings: CRITICAL 0 · MAJOR 1 · MINOR 3 · NOTE 5.**
- **The rev14 code changes are correct and narrow.**
  - I-6b holds on every in-process path.
  - The fold-scope decision holds on both fold paths in the executor.
  - The R10-4 change is safe.
  - No threshold, denominator, schedule or gate changed.
- **The one MAJOR finding (R11-1) is wording in the binding machine block.** It has no effect on any status, denominator, branch outcome or verdict.
  - I rate it MAJOR only because this attempt's scale lists "presents an interpretation as an owner decision" as MAJOR (the attempt-10 scale did not).
  - Under "Owner decision I-6b", the block defines the owner's "genuinely absent run" as "an executed run without a finite simulator energy". This is the R10-1 pattern again, which the owner has already ruled on.
- **No path to a campaign start exists.** The campaign stays blocked.

**Abbreviations**
- **Folders:** ATT11 = `...\release_attempts\attempt11_final_owner_decisions`; PIL = `...\R4_20261028_pilot`.
- **Code:** CAMP = `ATT11\code\r4h3\campaign.py`; CHK = `ATT11\code\r4h3\checks.py`; rev13 = `PIL\archive\rev13_attempt10_20261029_0629\code\r4h3\campaign.py`.
- **Text and status:** DRAFT12 = `PIL\03_protocol_v1_amendment_2_rev12_CANDIDATE.md`; V13 = `ATT11\config\code_review_status_v13.json`.
- **Tests (in `ATT11\code\tests\`):** T14 = `test_owner_decisions_v14.py`; T11 = `test_owner_decisions_v11.py`; T7 = `test_owner_rulings_v7.py`; T8 = `test_owner_rulings_v8.py`; T13 = `test_review_fixes_v13.py`; A2 = `test_amendment2.py`.
- **Mutation logs (in `PIL\logs\`):**
  - M-14/13 = `zz_mutation_check_v14_tests_on_rev13_run2.txt`
  - M-R102 = `zz_mutation_check_v14_r10_2_tests_on_rev12_run2.txt`
  - M-11/13 = `zz_mutation_check_v11_i6_tests_on_rev13_run2.txt`
  - M-A2 = `zz_mutation_check_a2_r3_9_test_on_rev11_run2.txt`
  - M-R39 = `zz_mutation_check_v14_r3_9_test_on_rev11.txt`
  - DIFF = `zz_diff_rev13_to_rev14_final.txt`

---

## Closure of R10-1 to R10-4

| ID | Verdict | Evidence | Residual |
|---|---|---|---|
| R10-1 (MINOR) | **PARTLY FIXED** | **Fixed:**<br>- "Owner ruling I-6" now holds only the owner's ruling (CAMP:334-340; DRAFT12:357).<br>- Both decisions of 2026-10-29 carry their own dated labels (CAMP:340, :344).<br>- The closing clause covers RUN_INVALID after a recomputation or fold failure and names the NOT_EVALUABLE labels that remain (CAMP:346-353).<br>- Readings (a) and (b) are labelled "Implementer reading (not an owner ruling)" (CAMP:356-360).<br>- The block and DRAFT12 agree value for value.<br>**Not fixed:**<br>- A new unlabelled implementer gloss sits inside the I-6b clause (CAMP:342-343): R11-1.<br>- The readings are described as having no outcome effect, which is wrong for (a): R11-3. | R11-1, R11-3 |
| R10-2 (NOTE) | **PARTLY ADDRESSED** | Now behavioural:<br>- R9-6 in the executor and R9-4(b) on rev12 (M-R102:27-31, :37-39);<br>- I-6b on rev13 (M-14/13:16-20; M-11/13:16-20);<br>- R3-9 on rev11 through the new test (M-R39:20-23). | **I6FL is reached in no mutation run** (R11-4). The fold_failed half of R9-6 is in no mutation run (R11-7). |
| R10-3 (NOTE) | **FIXED** | - Header DRAFT12:3: "(one MINOR finding and three notes)".<br>- §1.1 heading "first stated in rev0" is correct (rev0 `:12`).<br>- §1.2 and §1.3 "first stated in rev4" are correct (rev3 has no such section; rev4 `:19`, `:26`).<br>- The rev10 sentence is now a separate implementation note (DRAFT12:22). | New pointer issues in §11 and §12: R11-5 |
| R10-4 (NOTE) | **FIXED** | - CAMP:1083 bounds the index.<br>- T14:213-219 fails on rev13 by behaviour (IndexError, M-14/13:57-61). | The call is still unguarded; zip truncation remains in the fold (R11-6) |

## The owner's decisions of 2026-10-29

### I-6b: IMPLEMENTED correctly and narrowly in the code. The text has R11-1 and R11-2.

**The change** (CAMP:941-948 against rev13 `:927-934`; DIFF:59-84):
- Any `run`-stage error now turns any label other than NOT_EVALUABLE_CONDITION_ERROR into NOT_EVALUABLE_CONDITION_ERROR.
- The earlier label goes to `before_error`.
- rev13 instead gave RUN_MISSING to an APPLICABLE pair whose run raised.

**Why it holds on every path.** A raised arm has `rows[b]={"run_id","error"}` and no `e_dyn` (CAMP:860-868), so `finite` is False (CAMP:913) and the arm is in `no_energy` (CHK:174).

| Case | Label from `pair_qs_dynamic` | Final label | Evidence |
|---|---|---|---|
| M0/M1, other arm valid and FAILs | FAIL | NOT_EVALUABLE_CONDITION_ERROR; `fail_arms` kept by `dict(pair, …)`, FAIL in `before_error` | CHK:189-192; T14:86-89, T11:121-125 (not mutation-tested, R11-4) |
| M0/M1, other arm passing | RUN_MISSING | NOT_EVALUABLE_CONDITION_ERROR | CHK:193-195; T14:79, T11:116-117, T7:195, T8:264-266 |
| M0/M1, other arm invalid, unconfirmed, non-finite or with QS energy ≤ 0 | RUN_MISSING (`no_energy` is checked before invalid and undefined, CHK:193-203) | NOT_EVALUABLE_CONDITION_ERROR | by reading only |
| M2 | RUN_MISSING (CHK:178-181) | NOT_EVALUABLE_CONDITION_ERROR | by reading only |
| A QS-screen exception (CAMP:900-907) or a `qs_vs_dynamic` exception (CAMP:923-933) | — | already NOT_EVALUABLE_CONDITION_ERROR | — |

- PASS, RUN_INVALID and QS_UNDEFINED cannot arise when an arm raised.
- No fold path touches NOT_EVALUABLE_CONDITION_ERROR afterwards (CAMP:1050, :1013).

**The missing-run path is unchanged.** An executed run with `E_net_Wh` None or NaN and no exception still gives RUN_MISSING (CHK:193-195), and the override does not fire (CAMP:942-943). T14:92-102 shows this, including a `run_report` exception (reading (b)).

**A missing profile keeps its own path.** It is NOT_APPLICABLE_PROFILE_UNAVAILABLE (CHK:163-168), and becomes NOT_EVALUABLE_CONDITION_ERROR only after an exception (T11:95-107).

**The change is narrow.** Only two labels change, and only for eligible pairs with a `run`-stage error:
- RUN_MISSING becomes NOT_EVALUABLE_CONDITION_ERROR;
- FAIL becomes NOT_EVALUABLE_CONDITION_ERROR (it was RUN_MISSING in rev13).

Everything else is as before:
- A NOT_APPLICABLE pair with a run that raised becomes NOT_EVALUABLE_CONDITION_ERROR, as in rev13.
- Exceptions at other stages are unchanged.
- Accounting moves counts between `not_evaluable_run_missing` and `not_evaluable_condition_error`. Applicability, condition status, energy roles and every sum are unchanged.

**Neither label counts as PASS:**
- NOT_EVALUABLE gives INCONCLUSIVE (CHK:280-283);
- a nominal cell without PASS lacks evidence (CHK:250);
- the verdict check repeats the nominal-cell test (CHK:601-603);
- tested at T14:105-110.

**An exception overrides a PASS** at any stage (CAMP:942-948, :979-982). The executor test of this does not force a PASS (R11-7).

### Recomputation or fold failure scope: IMPLEMENTED (behaviour unchanged from rev13; docstrings now cite the decision)

- **Executed runs only, in the executor:**
  - the executor collects executed run IDs (CAMP:1245) and passes them to both folds (:1247, :1252); these are the only call sites (Grep);
  - `_na_pair_not_evaluable` skips a pair with no executed run (CAMP:1010-1011) and relabels only NOT_APPLICABLE_* (:1013-1017).
- **Other labels:**
  - PASS, FAIL and REPORTED_ONLY become RUN_INVALID (CAMP:1050-1058, :1077-1081);
  - NOT_EVALUABLE labels are untouched;
  - nothing becomes NOT_APPLICABLE or PASS.
- **Tests:** T14:121-154 covers 11 labels on 4 failure paths, T14:157-170 is the no-failure control, and T14:174-191 is the executor test.
- **Direct calls without executed IDs** relabel every N/A pair. This is broader than the decision's "only", but it is documented and no production call omits the IDs (R11-6).

---

## 2. Recomputation or fold failure

**On the separate-recomputation failure path:**
- `failed` is set for an exit other than 0 or 1, or for a process error: launch, unreadable output or missing output (CAMP:1028, :1218-1224, :1247).
- The relabel is at CAMP:1059-1060.
- An executed run missing from an otherwise complete output is not a process failure (:1224-1227). This is unchanged, as R10 accepted.

**On the `fold_failed` path:** CAMP:1070-1083, with the same rule.

**Which pairs count as executed:**
- "Executed" means `run_arm` returned (CAMP:869).
- A run that raised has `executed=False` (CAMP:865), but such a pair is already NOT_EVALUABLE_CONDITION_ERROR in process.
- So only a NOT_APPLICABLE_* pair with at least one returned run is relabelled.

**RUN_INVALID and the NOT_EVALUABLE labels are preserved.** Nothing becomes N/A or PASS; there is no assignment of either in these functions.

**The fallback is stated honestly:**
- CAMP:1008-1009 and :1068-1069; DRAFT12:120 says "the executor never makes such a call".
- "Fails closed" is accurate: NOT_EVALUABLE_CONDITION_ERROR can only make a branch INCONCLUSIVE.
- It conflates a pair without an executed run with one that has one, so in direct calls it departs from the decision's "only" (R11-6). It is not reachable from `run_campaign` or `execute_schedule`.

**Both recomputations are still required:**
- the in-process gate at CAMP:918 is unchanged;
- the separate confirmation in the fold (CAMP:1046-1058) is unchanged.
- A FAIL of an arm the separate script confirmed stays FAIL when the process succeeded (:1051-1052), as DRAFT12:85 states.

## 3. R10-1: the machine block

- **The I-6 clause** (CAMP:334-340 = DRAFT12:357) is the owner's ruling, plus field names. T14:231-235 checks that it holds no reading.
- **Attribution:**
  - The fold-scope clause (CAMP:344-346) faithfully paraphrases the decision.
  - **The I-6b clause (CAMP:340-343) is not only the owner's decision.** It adds "a genuinely absent run energy (an executed run without a finite simulator energy, no exception) stays NOT_EVALUABLE_RUN_MISSING" (R11-1).
  - The owner wrote "a genuinely absent run", and in the companion decision "do not conflate it with an executed run".
  - V13:108 repeats the gloss.
  - T14:236 requires the gloss to stay in the owner-decision segment.
- **The closing clause** ("As applied under these rulings", CAMP:346-355) covers RUN_INVALID and lists RUN_MISSING, QS_UNDEFINED and RUN_INVALID as remaining applicable. Two observations, both in R11-9:
  - it is labelled neither as a ruling nor as a reading;
  - "a pair with an exception whose label would otherwise be NOT_APPLICABLE_* … is NOT_EVALUABLE_CONDITION_ERROR" reads against the preceding sentence for pairs with no executed run.
- **Readings (a) and (b)** are labelled (CAMP:356-360). The claim that they change no outcome is wrong for (a) (R11-3).
- **Value for value:**
  - DRAFT12:357 equals the concatenated CAMP:329-360 at every string join, by reading.
  - IMPLEMENTED_2 changed only in this key (DIFF:16-57).
  - `read_amendment` showing no errors is a passing-test claim (T14:244-246, :297-298; `pytest_run29b`:16, :19).
- **Prose:** §1.14:95-99, §1.16:116-120, §2:140, :143, :147, §3:159, :164, §9:261, :270-272 and §12:288-291 match the code. The exceptions are:
  - §1.15:109 truncates the owner's quote (R11-2);
  - §1.15:111 states the gloss without attributing it to the owner, while the block attributes it (R11-1);
  - §1.14:97 and §9:261 make the "no outcome" claim (R11-3).

## 4. R10-3: counts and provenance

- **Counts and headings:** accurate, as in the closure table.
- **Superseded rev11 and status v12, handled honestly:**
  - The supersedes row (DRAFT12:10) agrees with `zz_start_state_v10.json`:161-199 for rev3 to rev10, and with `rev11_CANDIDATE.sha256.txt`:1.
  - rev11 is kept and pinned (T14:293-295); its heading said "rev3" (rev11 `:19`), as DRAFT12:296 says.
  - v12 is kept and marked superseded (V13:3). Its wording ("candidate rev11"; v12:60) confirms the stated reason.
- **New pointer issues (R11-5):**
  - §12:306 cites the non-final logs, which record T14 as `d6a839ff…` with 304 lines, not the reviewed `5c1735ef…` with 317 lines.
  - DRAFT12:11 cites `21_attempt11_final_owner_decisions_report.md`, which does not exist (Glob).

## 5. R10-2 and R10-4: evidence

| Item | Test | Result on the old modules | Kind |
|---|---|---|---|
| R9-6, separate-recomputation fold in the executor | T14:174-191 | rev12: NOT_EVALUABLE_CONDITION_ERROR instead of NOT_APPLICABLE_PROFILE_UNAVAILABLE (M-R102:27-31) | **behavioural** |
| R9-6, `fold_failed` | T14:140-154 [fold_failed]; T13:167 | not in any mutation run; on rev12 the four-argument call would be a TypeError | **API-level by reading only** |
| R9-4(b) | T14:194-196 | rev12: DID NOT RAISE (M-R102:37-39) | **behavioural** |
| I-6b | T14:73-80; T11:110-117 | rev13: RUN_MISSING (M-14/13:16-20; M-11/13:16-20) | **behavioural** |
| I6FL | T14:86-89; T11:118-125 | **never reached**: both tests fail earlier (:79, :116) | **none** (R11-4) |
| R3-9 | A2:307-322 | rev11: AttributeError, no `checks.QS_APPLICABLE` (M-A2:22-24) | **API-level** |
| R3-9 | T14:199-209 | rev11: `qs_eligible_pair` None (M-R39:20-23) | **behavioural** |
| R10-4 | T14:213-219 | rev13: IndexError (M-14/13:57-61) | **behavioural** |
| Fold-scope CASES and no-failure tests | T14:140-170 | pass on rev13 (M-14/13:123-127); the behaviour is unchanged | documentation |
| R10-1, R10-3, status, candidate | T14:223-308 | fail on text or versioning | text or versioning |

**How the runs were made:**
- M-14/13 ran the earlier 16-test file: 16 results (`:3`, `:137`), and line numbers 13 lower after `:197`.
- The R3-9 test ran on the final 17-test file (M-R39:28, "16 deselected").
- I read the developer's runner script (session scratchpad, `run_tests_on_archived.py`:9-21). It swaps only `r4h3.checks` and `r4h3.campaign` and asserts the archived candidate name, consistent with the logs' first two lines.
- The four first-invocation logs stop at `import r4h3` with ModuleNotFoundError before pytest starts (for example `zz_mutation_check_v14_tests_on_rev13.txt`:1-5). This is consistent with the stated argument error.

**R10-4 is safe:**
- the bounded index (CAMP:1083) changes nothing for 1:1 inputs;
- an unmatched row is relabelled (fail-closed);
- the test is behavioural.

## 6. Governance (V13)

- **Majors stay open and unaccepted:**
  - `open_critical` 0 and `open_major` 6 (:5-6);
  - the six majors, each "owner acceptance pending" (:8-15);
  - `owner_acceptance_of_major_closures` "not recorded" (:127).
  - Nothing is presented as owner-accepted.
- **Owner decisions:**
  - `open_owner_decisions` is `[]` (:92);
  - the decisions of 2026-10-29 are listed as owner rulings (:108-109), but the I-6b entry carries the "run energy" gloss (R11-1);
  - `implementer_readings_decided_by_owner` (:128-131) is accurate.
- **Implementer readings:** exactly one is listed (:124-126). Per R11-1, a second reading (an executed run without finite energy counts as "genuinely absent") is unlisted, and :112 and :125 call (a) outcome-free (R11-3).
- **Pending items:** `reviews_pending` (:120-122) and its rule (:123) are kept; `pending_release_steps` is separate (:113-119).
- **Implementer claims in the minor entries:**
  - R10-1 is marked "fixed" (:58) but is only partly fixed;
  - R10-2 claims I6FL mutation evidence (:59) that does not exist (R11-4);
  - the R8-1 description (:11) still states the label rev14 changed (R11-8).

## 7. Line endings and integrity

**campaign.py keeps CRLF:**
- Grep finds 1412 lines of CAMP ending in CR before LF, no line ending otherwise, and no bare LF lines.
- rev13 has 1395 CRLF lines; 1395 − 32 removed + 49 added = 1412. This matches DIFF (every line tagged `[CRLF]`) and `zz_line_endings_rev13_to_rev14_final.csv`:2 (49 added).

**The other changed and new files keep LF:**
- T7, T8, T11, T13 and T14 contain no CR. Grep for `\r` in the tests matches only eight unchanged CRLF files; for example `test_campaign.py` has 351, equal to the baseline at :26.
- The new configs v12, v13 and v14 contain no CR. This matches the CSV at :3-10.

**Changes are limited to the approved corrections:**
- DIFF hunks: version pointers, AMB_29_condition_error, the override, docstrings and the bound, plus the listed test edits.
- `zz_code_changes_rev13_to_rev14_final.csv` lists every other file as unchanged, including `checks.py` and `recompute_from_traces.py`.
- PIL code matches ATT11 at :67, :87-88, :342, :941 and :1083 (Grep).

**Referenced documents are unchanged by their recorded values:**
- Recorded SHA-256 values agree across DRAFT12:7-10, CAMP:66, the block (:338-339), the rev12 `sha256.txt`, `zz_start_state_v10.json`:143-199, T14:267, :293-295 and T13:216-218.
- `review_scope_attempt11.json` agrees with `readiness_gate_v15.json` for every entry compared.
- `release\` holds only the amendment 1 files.

## 8. No regression; nothing fixed has moved

- **I-1 to I-5:** `checks.py` is unchanged (same hash), so I-1 (CHK:217-301, :566-617), I-2, I-3 (CHK:89-94, :355-414, :466-477) and I-5 (CHK:55) are unchanged. I-4 is unchanged at CAMP:918 and :1046-1058.
- **R8 fixes:**
  - R8-1 holds: no FAIL survives a run exception.
  - R8-2: the accounting is unchanged.
  - R8-5: the writes are still guarded (:1109-1114, :1159-1162, :1234-1238).
  - R8-10: unchanged (:894-897).
- **R9 fixes:**
  - R9-1: unchanged (:839-845).
  - R9-2: unchanged (:1057-1058, :1080-1081).
  - R9-4: (a) unchanged at :926-933; (b) unchanged at CHK:330-332.
  - R9-6: unchanged.
- **Thresholds, schedule and denominators:**
  - thresholds: CHK:20-23 and config v14:277;
  - `schedule_sha256` `6011e357…`, `planner_jobs_sha256` and `draws` are equal in config v13 and v14 (:121-123);
  - PLANNED and TOTAL_PLANNED: CAMP:47-48;
  - `paired_delta` and the denominator functions are unchanged.
- **Pilot run:** "328 passed" (`pytest_run29.txt`:336), a claim.

## 9. Fail-closed

- `preconditions` and `run_campaign` are unchanged (no DIFF hunk in CAMP:578-687). Each of these blocks independently:
  - issued amendment 1 and its approval (:606-618);
  - issued amendment 2, APPROVED and equal to IMPLEMENTED_2 (:619-627);
  - the amendment 2 approval record (:628-633);
  - the §10.1 gate (:645-649);
  - the campaign authorisation (:651-658);
  - the location (:659-662);
  - open owner decisions (:663-664);
  - `open_major` (:669-671);
  - `reviews_pending` (:673-674).
- No code writes `campaign_authorization.json`, the issued amendment 2 or its approval record. Grep finds only the path constants (CAMP:64, :68-69) and reads.
- No campaign outputs exist.
- A pending review still blocks both modes (T14:279-289, :311-317). `run_campaign.py` is unchanged.

## 10. Tests

**The new tests are not vacuous:**
- They drive the real `run_condition` and `execute_schedule` with one injected fault each.
- They assert QS-eligibility (T14:80), so a non-eligible toy would fail.
- They assert the absence of errors on the missing-run path (T14:97).
- The fold tests cover 11 labels on 4 failure paths, with a no-failure control.

**Changed assertions, each justified:**
- T11:116-117, :124, T7:195 and T8:264-266: RUN_MISSING to NOT_EVALUABLE_CONDITION_ERROR (I-6b). T11 also gains a `before_error` assertion, which is stronger.
- T13:201-211: reads v11 by path (versioning). The live v13 is checked at T14:279-289.
- T13:214-230: drops the rev10 block-match check (versioning). It moved to T14:297-298 for rev12.
- No threshold or count assertion is weaker (T8:331-345 unchanged).

**Weaknesses:**
- R11-4 (I6FL);
- R11-7 (no forced PASS; missing arm and motor cases; `fold_failed` not mutation-tested; stale comment T13:202);
- T14:236 enforces the R11-1 wording.

## 11. New defects; CRITICAL or MAJOR?

- **Code:** no new behavioural defect. The override (CAMP:941-948) and the bound (:1083) are correct.
- **CRITICAL:** none.
- **MAJOR:** R11-1 only. It is wording only, with no status, denominator, branch or verdict effect.

---

## Findings

| ID | Sev | file:line | What | Why it matters | Fix |
|---|---|---|---|---|---|
| R11-1 | MAJOR (an interpretation presented as an owner decision; no outcome effect) | CAMP:340-343; DRAFT12:357; V13:108; T14:236 | Under "Owner decision I-6b (2026-10-29)" the block says "a genuinely absent run **energy** (an executed run without a finite simulator energy, no exception) stays NOT_EVALUABLE_RUN_MISSING". The owner wrote "A genuinely absent run follows the existing missing-run path", and said a genuinely missing run must not be conflated with an executed run. The mapping is the implementer's. It is not labelled, and V13:124-126 and DRAFT12:261 say only one reading remains. | The owner's R10-1 decision requires such scope statements to be labelled "Implementer reading". In a QS-eligible pair both runs are always attempted (CAMP:848-859), so the owner's term has no literal instance here. The label of an executed run with non-finite energy (RUN_MISSING now; arguably RUN_INVALID, since it fails §8.2 "finite") was not decided by the owner. Approving the block would attribute that choice to the owner. | Put the owner's sentence in the clause. Move "an executed run without a finite simulator energy and no exception stays NOT_EVALUABLE_RUN_MISSING (unchanged)" into the implementer reading as (c). List it in V13. Adjust T14:236. |
| R11-2 | MINOR | DRAFT12:109 | The "Owner's words" for I-6b omit the final sentence, "Do not perform a broad label rewrite." There is no ellipsis, and Grep finds no "broad" anywhere in DRAFT12. | The quoted owner text drops a binding constraint. The code complies. | Quote the decision in full. |
| R11-3 | MINOR | DRAFT12:97, :261; V13:112, :125 | Reading (a) is said to change no outcome ("INCONCLUSIVE either way"). Under a narrower reading, a `run_report` or `condition_report` exception on a PASS pair, or a diagnosis exception on an N/A pair outside NOM, would leave PASS or N/A. Under (a) the pair is NOT_EVALUABLE_CONDITION_ERROR and the branch INCONCLUSIVE. | The owner is asked to confirm (a) on an inaccurate basis. The implemented behaviour is the stricter, fail-closed one, and the R9-1 fix depends on it. | Keep "no outcome effect" for (b) only, and state the effect of (a). |
| R11-4 | MINOR | V13:59; T11:118-125; T14:86-89; M-11/13:16-25; M-14/13:16-22 | V13 claims mutation runs of I6FL "against the modules before their change". I6FL's assertions are never reached: both tests fail earlier on rev13. No run used rev11. | The R10-2 residual for I6FL remains while the record says it is addressed. | Make the FAIL case its own test. Run it on rev13 (expects RUN_MISSING) and rev11 (expects FAIL). Correct V13:59. |
| R11-5 | NOTE | DRAFT12:306, :11 | §12 cites the non-final comparison logs, whose T14 hash and line count differ from the reviewed file. The decision record cites report 21, which does not exist, and the text does not say it will be written later. | Provenance pointers. | Cite the `_final` logs. Write report 21, or say that it is pending. |
| R11-6 | NOTE | CAMP:1008-1011, :1068-1069, :1083, :1029, :1252 | (a) Without executed IDs, both folds relabel every N/A pair. This is broader than "only"; it is documented and unreachable. (b) `fold_separate_recomputation` still uses `zip`, so with fewer conditions than rows, extra rows are silently not folded. `fold_failed` is still called unguarded. All pre-existing and unreachable, because the inputs are 1:1 (record invariant :1165-1173). | Robustness only. | Reject a length mismatch in the fold. Guard the `fold_failed` call and record its failure in the manifest. |
| R11-7 | NOTE | T14:113-117, :140-154; T13:202 | (a) "Overrides a pass" accepts a control result of PASS or FAIL. (b) No executor test of I-6b with the other arm invalid or non-finite, or for M1 or M2. (c) The `fold_failed` half of R9-6 is in no mutation run. (d) T13:202 says "the live file is v12"; it is v13. | Test weakness. | Force a PASS by monkeypatching `qs_vs_dynamic`. Add the missing cases. Add `fold_failed(rows, reason)` to the rev12 run. Fix the comment. |
| R11-8 | NOTE | V13:11; CAMP:947 | The R8-1 entry, which is pending owner acceptance, still describes the RUN_MISSING label that rev14 replaced. The reason text cites "owner decision I-6b" also for QS-ineligible pairs whose run raised. | Records and cosmetic text. | Note the rev14 label in R8-1. Cite I-6b only when the pair is APPLICABLE. |
| R11-9 | NOTE | CAMP:381-384, :365-368, :338-340, :346-348; DRAFT12:119 | Other values carry implementer additions inside owner-ruling attributions (pre-existing; stricter direction): "(and by the in-process one)" in I-4, and "duplicated" in I-1. §1.16 reads the owner's "Both separate recomputations" as in-process plus separate. The I-6 clause merges execution validity and recomputation validity, which the owner's R10-1 decision lists separately. The "As applied" clause is ambiguous for pairs with no executed run. | The same pattern as R10-1, at lower risk. | Apply the R11-1 treatment to every "Owner ruling" clause. |

## What I could not verify

- **The attempt's own outputs:**
  - its test run (`pytest_release_attempt11.txt` is partial, at 21%);
  - its readiness gate, dry run, preconditions and release validation;
  - its gate record and attempt note.
  These are absent or still in progress.
- **Pilot results:** all pilot results and mutation logs are claims. Runtime behaviour was judged by reading; for example, that the toy B0 arm is valid and does not FAIL, and that 0.96 s is a plausible duration for M-R102.
- **Hashes and line endings:** I computed no hash. Line endings were checked by Grep on CR before LF only.
- **Unchanged files** were not compared line by line beyond the comparison logs.
- **Frozen upstream modules** were not inspected.
- **The text of the owner's 2026-10-29 decisions** exists only in the review brief and in DRAFT11 and DRAFT12. I cannot confirm that it matches the owner's original.
- **The supersession timing:** that rev11 and v12 were superseded "before any test or review" rests only on timestamps (06:35:27 and 06:38:33).
- **The runner script** I read in the scratchpad may not be the exact version that was used.
