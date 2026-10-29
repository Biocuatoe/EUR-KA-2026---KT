# Release attempt 8: independent read-only review report (verbatim)

**Provenance.**
- **Who:** a new, separate **AI review agent** ("Plan" agent type, which has no Edit or Write tools), instructed to use Read, Grep and Glob only. It is not the agent that reviewed attempts 5 to 7. **This is not a human independent audit.**
- **When:**
  - started 2026-10-28 at about 19:44:10 (+0700), after `review_scope_attempt8.json` was written at 19:44:05;
  - stopped on a service rate limit before 19:53;
  - resumed with its own context at about 19:53:15 (the clock read 19:53:10 just before);
  - delivered this report at about 19:57:15, 241 s after resumption (the agent's reported duration for the resumed part). The clock read 19:58:25 just after the report was received.
- **Brief:** `review_brief_attempt8_as_sent.md`. On resumption it was told only that some of the attempt's own outputs might now exist and are claims.
- **State reviewed:**
  - this attempt's `code/` and `config/`: 66 files, SHA-256 in `review_scope_attempt8.json`;
  - amendment 2 candidate rev8, `R4_20261028_pilot/03_protocol_v1_amendment_2_rev8_CANDIDATE.md`, SHA-256 `f6430bf5512cb56065a2465bcfda1c4c42e244b80f73fcd3e88d985ac8811f7c`.
- **Format:** the text below the line is the agent's final message. The only edit is removing the two-space indentation that the message relay adds.
- **Outcome:**
  - **3 MAJOR findings (R8-1, R8-2, R8-3) are open in this attempt.** As the task requires, they are fixed in a new attempt, `../attempt9_review_fixes/`; this attempt is kept unchanged as reviewed.
  - R7-1 to R7-7 are verified FIXED.

---

I am an AI review agent (a read-only "Plan"-type agent), not a human auditor; I used only the Read, Grep and Glob tools. I ran nothing, wrote nothing, computed no hashes, and used neither Git nor the network. This is not a human independent audit.

**New findings: CRITICAL 0 · MAJOR 3 · MINOR 3 · NOTE 5.** R7-1 to R7-7 are all FIXED. No path to a campaign start, a confirmatory result, a branch PASS, SUPPORTED or NOT SUPPORTED contrary to a ruling was found. The three MAJOR findings (R8-1 to R8-3) all come from how the I-6 ruling was implemented and described. None of them can change a branch outcome or the verdict, but each changes a pair status or a reported denominator, or misstates the ruled precedence.

Abbreviations:
- **ATT8** = `...\R4_20261028_campaign\release_attempts\attempt8_final_owner_decisions`
- **PIL** = `...\R4_20261028_pilot`
- **DRAFT8** = `PIL\03_protocol_v1_amendment_2_rev8_CANDIDATE.md`
- **MATRIX** = `PIL\18_owner_decision_matrix_I1_I6.md`
- **v11 tests** = `ATT8\code\tests\test_owner_decisions_v11.py`
- **rev10** = `PIL\archive\rev10_attempt7_20261028_1851\code`
- Unless stated otherwise, `campaign.py` and `checks.py` mean `ATT8\code\r4h3\...`.

**How rev10 and rev11 were compared:** I read both versions of `checks.py` and `campaign.py` side by side.
- `checks.py` differs only in the label-rule comment (`:46-48`) and one docstring line (`:216`). The logic is identical, offset by 2 lines.
- `campaign.py` differs in:
  - `IMPLEMENTED_2` (`:294-405`);
  - one message in `preconditions` (`:631`);
  - `run_condition` (`:852-892` new; `:923` changed; `:929` new field);
  - `execute_schedule`: stage fields, `guarded()`, the per-run ledger (`:1050`, `:1070`, `:1089`, `:1093-1101`, `:1127-1150`, `:1155-1231`, `:1234-1253`);
  - the paths at `:67`, `:87`, `:88`.
- `test_owner_ruling_i1_v10.py` lines 1-235 are identical to rev10; only `:238-263` changed.
- `test_review_fixes_v9.py` changed only at `:99-101` and `:227-228`.
- Spot check by Grep: PIL `code\r4h3\campaign.py` has the same text as ATT8 at `:888`, `:929`, `:1093` and `:1129`, and PIL `checks.py` the same at `:46` and `:235`.

---

## Closure of R7-1 to R7-7

| ID | Verdict | Evidence | Regression test that fails without the fix? |
|---|---|---|---|
| R7-1 | **FIXED** | The DRAFT8 §9 table names I-3 as deciding "whether a saving percentage is computed at all … It changes no QS label" (`:239`), and `:244` names I-3 as the exception. (Separately, the `:244` clause "none … changes a denominator" is now inaccurate because of R8-2.) | Text only. `v11 tests:300` checks only that no "Provisional reading I-" remains. |
| R7-2 | **FIXED** | `config\code_review_status_v9.json`: the false sentence is gone; `open_owner_decisions` [] (`:69`); `owner_rulings_implemented` N-A2 … I-6 (`:70-85`); separate `pending_release_steps` (`:88-94`); accurate rule text (`:87`). | Record. `v11 tests:276-278` asserts the separation and the absence of the sentence. |
| R7-3 | **FIXED** | Every `errors.append` in `campaign.py` now has a `stage` (`:795`, `:803`, `:822`, `:840`, `:846`, `:880`, `:920`, `:1050`, `:1070`, `:1089`, `:1097`, `:1143`, `:1146`, `:1148`, `:1155`, `:1164`, `:1172`, `:1180`, `:1188`, `:1197`, `:1216`, `:1225`, `:1231`). `diagnostic_path` is on the separate-recomputation and fold rows (`:1147`, `:1150`, `:1156`). DRAFT8 §7.6 `:209`. | Yes: `v11 tests:206-215`. Rev10 rows such as QS-DYN-ACCOUNTING had an empty stage. It injects 5 of the ~20 sites, then asserts a stage on every row present. |
| R7-4 | **FIXED** | `process_failed` (`:1129`). After a process failure every executed run gets a ledger row; otherwise each run absent from the output, or present with `recomputed != "True"` with its reason, gets one (`:1135-1138`, `:1148-1150`). Manifest `runs_not_recomputed` (`:1159`). DRAFT8 §7.8 `:213`. | Yes: `v11 tests:218-251`. The `exit4_complete_output` and `not_recomputed_row` cases would fail on rev10 (no per-run rows). The `unreadable_output` case would also pass on rev10; it serves R7-7. |
| R7-5 | **FIXED** for the writes listed: `guarded()` (`:1093-1098`) wraps `planner_checks.csv`, `runs.csv` and `evaluation.csv` (`:1099-1101`) and the summary outputs (`:1234-1244`). The `errors.csv` failure goes to the manifest (`:1246-1253`). Residual write gaps: R8-5. | Yes: `v11 tests:254-269`. On rev10 the injected `runs.csv` failure propagated out of `execute_schedule`. |
| R7-6 | **FIXED** | `checks.py:46-48` now states the I-1 and I-6 rules. The docstring at `:216` names I-2 as a ruling. | Comment only. |
| R7-7 | **FIXED** | (1) The live v9 file is asserted to be the one in use, with `open_major` 2 and `reviews_pending`, and to block readiness (`v11 tests:273-281`). (2) Unreadable output, and exit 4 after a complete output, are tested (`:218-251`). (3) Each "Owner ruling I-n" is checked in `IMPLEMENTED_2` (`:282-283`). | Yes. |

**R7-8 to R7-13:**
- **R7-8:** resolved. `19_attempt7_final_review_report.md` exists (Glob). The same pattern recurs for report 20 (R8-7).
- **R7-9:** superseded by the rulings.
- **R7-10:** closed in practice by the I-6 override. A `classify` exception now relabels a PASS to `NOT_EVALUABLE_CONDITION_ERROR` (`campaign.py:888`). But DRAFT8 `:269` and v9 `:38` still say "unchanged" (R8-8).
- **R7-11 and R7-13:** unchanged (optional hardening), as stated.
- **R7-12:** superseded. Grep finds no "provisional" anywhere in DRAFT8.

---

## Q2. Is each of I-1 to I-6 implemented exactly as ruled?

**I-1: yes, unchanged from rev10.**
- `checks.branch_qs_dynamic_outcome` (`:224-238`, `:256-276`) and the recheck from the rows in `h3_verdict_eligibility` (`:550-559`) are identical in logic to rev10.
- The I-6 override strengthens I-1: any exception in a NOM cell now leaves it NOT_EVALUABLE, or FAIL (R8-1), so it is never PASS.
- The tests in `test_owner_ruling_i1_v10.py:57-169` are unchanged. DRAFT8 §1.9, §6 and §8 match.

**I-2: yes.**
- **Not by itself INCONCLUSIVE.** Only NOM cells enter `lacking` (`checks.py:224-237`), and `NOT_APPLICABLE_PROFILE_UNAVAILABLE` is not in `_NOT_EVALUABLE` (`:57-58`). So outside NOM it does not, by itself, make the branch INCONCLUSIVE.
- **Never a PASS.** It is counted as `n_NOT_APPLICABLE_PROFILE_UNAVAILABLE`, never as PASS.
- **Counted.**
  - The condition keeps PROFILE_/BASELINE_UNAVAILABLE (`classify_pair`, `:407-410`).
  - It is counted in `feasibility_accounting` (`:494-499`).
  - A SEN draw without a profile counts against 29 of 32 (`:545-549`).
- **Never a paired comparison.** `paired_delta` refuses it (`:427-428`), and `energy_role` never makes it confirmatory (`:465`).
- **Test:** `v11 tests:124-138`.
- **Interaction with I-6:** when the existing arm raises, the pair becomes `NOT_EVALUABLE_CONDITION_ERROR` (I-6 precedence; tested at `v11 tests:95-107`). In that case `qs_dynamic_accounting` stops counting it as profile-unavailable (R8-2). `feasibility_accounting` still counts it.

**I-3: yes.**
- **Guards.** Every energy-saving percentage the code computes refuses a denominator that is ≤ 0 or not finite through `non_positive_term` (`checks.py:80-85`):
  - QS ratio (`:316-326`);
  - S_found and S_max (`:341-345`);
  - grid ΔS (`:356-359`);
  - ΔE_rel (`:430-432`);
  - the time-step check is not evaluable for an undefined input (`:367-368`).
- **No other saving percentage exists.** Grep finds only:
  - shortfall against the fixed d_ref (`closedloop.py:139`, `evaluator.py:223`);
  - a tolerance comparison (`evaluator.py:300`).
  Both are out of scope as stated (DRAFT8 `:179-184`). `planner.py` has no percentage at all.
- **No epsilon, absolute value or replacement denominator.** `abs` is applied only to the result, as the protocol defines (`:332`, `:360`).
- **Recorded.** The raw values, the metric and the reason are recorded (`:315`, `:325`, `:344-345`, `:432`).
- **Independent metrics intact.** ΔE_abs is kept (`:431`), and COMPARABLE is untouched by an undefined QS ratio.
- **Test:** `v11 tests:141-161`.

**I-4: yes, and stated consistently.**
- **In process:** the arm must pass §8.2 and the in-process recomputation (`campaign.py:873`).
- **Separate recomputation:** after the fold, a PASS, FAIL or REPORTED_ONLY whose arm is not `recomputed`, `protocol_ok` and from exit 0/1 becomes `NOT_EVALUABLE_RUN_INVALID`. A FAIL of a confirmed arm stays FAIL (`:965-975`).
- **Fold failure:** `fold_failed` (`:987-989`).
- **Energy roles** use the same rule (`:1206-1208`).
- **Stated** in DRAFT8 §1.12 (`:81-83`), §4.1 (`:163`) and block `:325`.
- **Test** (`v11 tests:164-173`): fold level. The in-process half is checked only by source-string match (R8-4).

**I-5: yes.**
- The label is unchanged: `checks.py:52` and `:55-62`.
- It reads the same in:
  - `IMPLEMENTED_2` (`:320-326`) and block `:321`;
  - DRAFT8 §1.13 and §2 (`:122`);
  - the accounting column `not_evaluable_qs_undefined` (`checks.py:301`) and the branch key `n_NOT_EVALUABLE_QS_UNDEFINED` (`:241`);
  - v9 `:75`;
  - the tests (`v11 tests:176-188`).
- The per-arm string "undefined (QS energy <= 0)" (`:326`) is an arm-level status with the same meaning.

**I-6: implemented for every NOT_APPLICABLE case, but not exactly as ruled (R8-1, R8-2, R8-3).**
- **Can a NOT_APPLICABLE label hide an exception at a listed stage?** No.
  - `run` (`:820-828`) → override at `:888`;
  - `run_report` (`:839-840`) → `:888`;
  - `qs_screen`, including with a missing profile (`:793-805`) → `CONDITION_ERROR` (`:857-862`);
  - `classify` (`:845-848`) → `:888`;
  - `qs_vs_dynamic` (`:878-883`) → `CONDITION_ERROR`;
  - `condition_report`: everything except NOT_EVALUABLE is relabelled, NOT_APPLICABLE and FAIL included (`:923-925`);
  - condition-level → `CONDITION_ERROR`, applicability UNKNOWN (`:1040-1050`).
- **Outside the listed stages:** an exception in the separate recomputation (exit 4, or the fold) leaves `NOT_APPLICABLE_*` labels as they were. It cannot change an outcome, because every PASS then becomes RUN_INVALID (R8-9).
- **Separation of the three concepts.** In the executor they are separate:
  - applicability: `qs_vs_dyn_applicability` (`:853-855`, `:929`);
  - dynamic validity: `status` (`:842-848`);
  - evaluation status: `qs_vs_dyn_pair_status`, with `_before_error` (`:931`).
  The QS accounting does **not** keep them separate (R8-2).
- **Precedence test:** yes, `v11 tests:77-107`. It would fail on rev10, where the label stayed NOT_APPLICABLE and the applicability field did not exist. Stages `classify`, `run_report` and `condition_report` with a NOT_APPLICABLE pair are not tested (R8-4).
- **FAIL-stays-FAIL.**
  - **Stated:** `campaign.py:884-888`, `IMPLEMENTED_2:337` and block `:322`, DRAFT8 §1.14 `:95` and §3 `:138`.
  - **Not covered by the ruling:**
    - The ruling says "the pair becomes NOT_EVALUABLE", without exception.
    - The owner approved "the stricter interpretation", which MATRIX defines as I-6b, "always NOT_EVALUABLE_CONDITION_ERROR". It explicitly lists "QS-eligible pair, the other valid arm FAILs → CONDITION_ERROR" (MATRIX `:149-152`, `:166`).
    - The stated justification, R3-2, is an earlier review finding, not an owner ruling.
  - **Effect:** the outcome is identical (M0/M1 INCONCLUSIVE; M2 cannot FAIL), but the pair status and the per-status counts differ. It is presented as part of the owner's ruling (R8-1).
- **Reporting layer:**
  - `conditions.csv` gains `qs_vs_dyn_applicability` and `qs_vs_dyn_pair_status_before_error`;
  - `errors.csv` has a stage and run ID(s) on every row;
  - the manifest records `separate_recomputation.process_log`;
  - `qs_dynamic_branch_outcomes.csv` and `h3_verdict_eligibility.json` treat CONDITION_ERROR as not PASS (`checks.py:236`, `:263`, `:557`).

## Q3. Is any decision presented as open, or any open item as settled?

- **Consistent:** `OWNER_DECISIONS_OPEN` is [] (`campaign.py:400`, `:405`), v9 `open_owner_decisions` is [] (`:69`), and DRAFT8 §9 (`:233`) says the same. This matches the binding rulings.
- **Presented as settled, but not settled as implemented:**
  - The FAIL-with-exception label (R8-1).
  - The optional I-6 sub-question, RUN_MISSING or CONDITION_ERROR for an eligible pair whose run raised (MATRIX `:168`), was not answered by the owner. The code keeps RUN_MISSING (DRAFT8 `:93`). That is within the ruling's words (NOT_EVALUABLE) and changes no outcome; it should be recorded as the owner's choice.
- **R7-2 is FIXED:** v9 separates `owner_rulings_implemented` from `pending_release_steps`.
- **v9 is honest about the counts:**
  - `open_major` 2 keeps R5-1 and R5-2 until the owner accepts their closure (`:6-7`);
  - `reviews_pending` names this review (`:95-97`), and its rule keeps it until a later status file (`:98`).
- **Its claims of "fixed" for R7-1 to R7-7** (`:31-37`) agree with this review. "R7-10 unchanged" (`:38`) is stale (R8-8).
- **MATRIX** (`:7-9`, `:27-34`) still says I-2 to I-6 are OPEN. It is a pre-ruling record that DRAFT8 cites only as "the interpretations considered" (`:233`); not a defect.

## Q4. Does DRAFT8 match the implementation?

- **Machine block** (`:300-377`) against `IMPLEMENTED_2` (`campaign.py:294-402`): all 32 keys checked by reading, value for value and in order, plus amendment, status and note. All match.
  - `applies_to_protocol_sha256` equals `frozen.py:39`.
  - `amends_amendment_1_sha256` equals `campaign.py:66`.
- **§1.9 to §1.14:** match the code, except:
  - §1.14 `:95` presents the FAIL exception as part of the ruling (R8-1);
  - **§1.6 `:47` contradicts the code and §1.14.** It says a QS-screen exception gives `NOT_APPLICABLE_PROFILE_UNAVAILABLE` if a profile is missing. The code gives `NOT_EVALUABLE_CONDITION_ERROR` (`:857-862`), as do §1.14 (`:94`), §3 (`:142`) and §12.1 (`:258`). R8-3.
- **§2, §3, §6, §8:** match. The §6 column list matches `checks.py:241-252`.
- **§7.2 `:205`** says the eligibility classes "add up to the planned pairs". After the I-6 override they do not (R8-2). §7 `:203` "Nothing is dropped from a denominator" and §9 `:244` "None of these rulings changes … a denominator" are inaccurate for the same reason.
- **§7.6 `:209`** is broader than the code (R8-5).
- **§9:** I-3 is correctly the exception (R7-1 fixed).
- **§12.1:** complete for the code changes. The one-line message change at `campaign.py:631` is not listed (trivial). "R7-10 not changed" is stale (R8-8).
- **Thresholds kept** (`:15`): `checks.py:18-21`; block `:310-314`; config v11 `:277`.
- **Parent hashes present:**
  - protocol `f9826318…` (`:7`);
  - amendment 1 `7720fed7…` (`:8`);
  - rev7 `0e3ef311…`, equal to R7 report `:9` (`:10`);
  - rev6 `0dcb767e…`, equal to MATRIX `:5`;
  - rev5 `e7ba73c1…`, equal to the test pin.
- **DRAFT marking:** "DRAFT — NOT APPROVED FOR RELEASE" on line 3, block `"status": "DRAFT"` (`:302`), and the note (`:376`).

## Q5. Is the campaign runner fail-closed?

**Yes.**
- **`preconditions("campaign")`** (`campaign.py:546-643`; logic unchanged from rev10) blocks on each of these independently:
  - the issued amendment 1 and its approval (`:574-586`);
  - the issued amendment 2: it must exist, be APPROVED, and its block must equal `IMPLEMENTED_2` (`:587-593`);
  - the amendment 2 approval record (`:596-601`);
  - the §10.1 gate (`:613-617`);
  - `campaign_authorization.json` with its scope and three hashes (`:619-626`, `:509-525`);
  - the campaign-root location by resolved path (`:627-630`);
  - review status: `open_major` 2 (`:637-639`), open owner decisions (`:640`), `reviews_pending` (`:641-642`).
- **Pending review:** emptying `OWNER_DECISIONS_OPEN` removes one blocker. The pending review still blocks, through `open_major` and `reviews_pending` (asserted at `v11 tests:279-281`).
- **Entry points:** `run_campaign` raises before executing (`:649-651`); `run_campaign.py --execute` goes only through it (`:29-31`).
- **No code writes `campaign_authorization.json`:** Grep finds only reads (`:619-623`) and test assertions that it is absent.
- **On disk:** `R4_20261028_campaign\release\` holds only the amendment 1 files and an old dry run (Glob).
- **Schedule unchanged:** `schedule_sha256` is `6011e357…` in both config v10 and v11 (`:122`).

## Q6. Are the tests meaningful, and were any assertions weakened?

- **New tests:** mostly meaningful, and they drive the real executor:
  - I-6 (`:77-120`);
  - R7-3, R7-4 and R7-5 through `execute_schedule` (`:192-269`).
- **Weak spots (R8-4):**
  - I-4's in-process half (`:171-172`) is a source-string check.
  - I-6 is untested at `classify` (pair label), `run_report`, and `condition_report` with a NOT_APPLICABLE pair. The last is the changed line `:923`.
  - Nothing checks the QS accounting after an override.
  - `:116-120` (I6FL) enshrines the R8-1 behaviour.
- **Changed assertions, each justified:**
  - `test_review_fixes_v9.py:99-101`: NOT_APPLICABLE_PROFILE_UNAVAILABLE becomes CONDITION_ERROR (I-6; stricter).
  - `test_review_fixes_v9.py:228`: the regex now accepts "Reading|Ruling" (versioning). The precise per-ruling check is at `v11 tests:282-283`.
  - `test_owner_ruling_i1_v10.py:238-247`: the open-decision mechanism is now tested with an injected list. The decisions are ruled; the mechanism is still exercised in both modes.
  - `test_owner_ruling_i1_v10.py:250-263`: rev7 is pinned by hash instead of being the current candidate (versioning). Its `read_amendment` check moves to `v11 tests:290-291`.
- **No threshold changed, no tuning:** the only synthetic `diff_pct` (2.0, `v11 tests:116`) is a forged FAIL. No test computes or targets an energy difference.

## Q7. Did the rev11 changes introduce new defects?

- **I-6 override:** R8-1, R8-2 and R8-6, and the R8-3 text. The override is placed correctly:
  - after the pair evaluation and before reporting, so `evaluation.csv` and the conditions get the final label;
  - it can only turn a label into NOT_EVALUABLE, never into PASS.
- **Per-run ledger:** correct.
  - A non-finite run, whose trace is `.nonfinite.npz`, appears as "not recomputed: no evaluable trace". That is accurate.
  - The head row is written only on a process failure.
- **Guarded writes:** correct for the listed files. Remaining gaps are in R8-5.
- **Stage fields:** complete.

## Q8. Are there CRITICAL or MAJOR findings?

- **CRITICAL: none.**
- **MAJOR: R8-1, R8-2, R8-3.** None can produce a PASS, SUPPORTED or NOT SUPPORTED, or start the campaign.

---

## Findings

| ID | Sev | file:line | What | Why it matters | Fix |
|---|---|---|---|---|---|
| R8-1 | MAJOR | `campaign.py:884-888`; `IMPLEMENTED_2:337` (block `:322`); DRAFT8 `:95`, `:138`; `v11 tests:116-120`; MATRIX `:149-152`, `:166` | When a run raises and the other valid arm FAILs, the pair stays FAIL. The I-6 ruling says "the pair becomes NOT_EVALUABLE", and the approved option I-6b explicitly labels this case `NOT_EVALUABLE_CONDITION_ERROR`. The justification (R3-2) is a review finding, not a ruling. Yet the exception is presented as part of the owner's ruling, and §9 says nothing is open. | A pair status (and the FAIL / NOT_EVALUABLE counts per set) differs from the ruling as approved. Branch outcome and verdict are unaffected (INCONCLUSIVE either way). | Either the owner confirms the exception explicitly (record it with the ruling text in report 20 and the next status file), or remove "FAIL" from `:888`, keeping `before_error=FAIL`, and change the test. Also record the owner's answer to the RUN_MISSING / CONDITION_ERROR sub-question (MATRIX `:168`). |
| R8-2 | MAJOR | `checks.py:283-300` with `campaign.py:858`, `:888-892`, `:923-925`; DRAFT8 `:203`, `:205`, `:244` | After the override, a QS-ineligible or profile-less pair keeps `qs_eligible_pair=False` but has status CONDITION_ERROR. It is then counted in **none** of the four eligibility classes: eligible counts `True`, ineligible counts the pair status `NOT_APPLICABLE_QS_INFEASIBLE`, profile-unavailable counts the pair status `NOT_APPLICABLE_PROFILE_UNAVAILABLE`, unknown counts `None`. Meanwhile `qs_ineligible_b3_only` still counts it. Exactly this case is built at `v11 tests:88`, but the accounting is never run on it. `test_owner_rulings_v8.py:336-337` asserts the sum, but its fixture has no override case. | A reported N-A2 denominator (QS-ineligible and profile-unavailable pairs) drops pairs. The docstring invariant and DRAFT8 §7.2 are broken. The accounting mixes applicability with evaluation status, against I-6's "keep … separate". Rev10 had no such case. | Count the eligibility classes from `qs_vs_dyn_applicability` (falling back to the pair status for rows without it). Add an executor-level test (a NOT_APPLICABLE pair plus a run exception through `execute_schedule`) asserting both sums equal the planned pairs. Correct DRAFT8 `:203`, `:205` and `:244` if needed. |
| R8-3 | MAJOR | DRAFT8 §1.6 `:47` | Carried over unchanged from rev6/rev7: "…labels the pair `NOT_EVALUABLE_CONDITION_ERROR` …, or `NOT_APPLICABLE_PROFILE_UNAVAILABLE` if a profile is missing." The code (`campaign.py:857-862`), §1.14 `:94`, §3 `:142`, §12.1 `:258` and the next line (`:48`) say the opposite. | Normative text that would be issued states, for one ruled case, the NOT_APPLICABLE-over-exception precedence that I-6 forbids. Applied outside NOM it would give a different branch outcome than the code. | Replace it with: "…labels the pair `NOT_EVALUABLE_CONDITION_ERROR`, also when a profile is missing (I-6, §1.14); `qs_vs_dyn_applicability` keeps `NOT_APPLICABLE_PROFILE_UNAVAILABLE`." |
| R8-4 | MINOR | `v11 tests:77-120`, `:171-172`; `test_review_fixes_v9.py:116-119` | No I-6 test at `classify` (pair label), `run_report`, or `condition_report` with a NOT_APPLICABLE pair (the changed `:923`). Nothing checks the QS accounting after an override. The in-process half of I-4 is a source-string check. | Test weakness. | Add the three stage cases and the accounting check (see R8-2). Test the in-process rule behaviourally: an arm with `recompute_protocol_ok=False` gives `NOT_EVALUABLE_RUN_INVALID`. |
| R8-5 | MINOR | `campaign.py:1052-1054`, `:1164`, `:1143`, `:1245`; DRAFT8 `:209` | Three gaps: the `conditions/<id>.json` write is unguarded (a failure aborts the run with no `errors.csv` or manifest); a failed `conditions.csv` write is not listed in the manifest's `output_write_failures`; neither is a failed process-log write, which has its own condition ID. §7.6 says failed writes are listed and the other outputs are still written. | Reporting gap (protocol §10.4 logging). Fail-closed. | Guard the per-condition write, and list every `write …` stage in `output_write_failures`. Or narrow the §7.6 wording. |
| R8-6 | MINOR | `IMPLEMENTED_2:337` (block `:322`) and `campaign.py:923` | The block says "a measured FAIL of a valid arm stays FAIL (never hidden)". But `:923` relabels FAIL to CONDITION_ERROR at `condition_report`, as §1.14 `:95` states. | Machine-block wording is incomplete. | Add the `condition_report` exception to the block text, or settle it under R8-1. |
| R8-7 | NOTE | DRAFT8 `:11` | Cites `20_attempt8_final_owner_decisions_report.md`, which is absent (Glob). The I-2 to I-6 rulings exist on disk verbatim only in DRAFT8 and the brief. | Same pattern as R5-12 and R7-8. | Write report 20 before issue. |
| R8-8 | NOTE | DRAFT8 `:269`; v9 `:38` | "R7-10 unchanged". The I-6 override now labels a `classify`-exception PASS as `NOT_EVALUABLE_CONDITION_ERROR` (`:888`), which closes R7-10. | Stale record, in the safe direction. | Update it. |
| R8-9 | NOTE | `campaign.py:965-975`, `:987-989` | I-6 is not applied after an exception in the separate recomputation (exit 4) or in the fold. `NOT_APPLICABLE_*` labels remain. No outcome effect, since every PASS becomes RUN_INVALID. DRAFT8's stage list (`:92`) excludes this case. | Scope of "evaluation" in I-6. | Have the owner confirm the scope, or relabel those pairs too. |
| R8-10 | NOTE | `campaign.py:854-855`, `:858` | When one arm's screen raises and the other's screen fails, applicability is reported as UNKNOWN (and `qs_eligible` None), although NOT_APPLICABLE_QS_INFEASIBLE is knowable. | Reporting precision (V6-4 residue). | Optional. |
| R8-11 | NOTE | MATRIX `:7-9`, `:27-34` | Still says I-2 to I-6 are OPEN. | It is a historical record; DRAFT8 cites it only for the interpretations. | Optionally add a superseded note. |

## What I could not verify
- **Test results.** All are claims:
  - `ATT8\logs\pytest_release_attempt8.txt` was still in progress (117 results, no summary).
  - `PIL\logs\pytest_run26.txt` says "288 passed" (273 plus the 15 new tests, which is consistent); `pytest_run26a` says 15 passed.
  - `readiness_gate_v12.json` records 288/0/0.
  - The attempt's readiness gate, dry run, preconditions and release validation did not exist.
- **Hashes.** I cannot compute SHA-256.
  - `copy_verification_attempt8_summary.json` (73 files, no mismatch), `review_scope_attempt8.json` and `zz_code_changes_rev10_to_rev11.csv` agree with each other for every entry I compared.
  - The PIL and ATT8 code agree at the six lines I spot-checked.
  - I did not compare the files marked "unchanged" against rev10 line by line.
- **Runtime behaviour was judged by reading.** For example: that the toy S-eco knots are not on a uniform 1 s grid (`v11 tests:58`), and that both arms are 8.2-valid in the I6FL case.
- **Owner acceptance:** none verified, and none recorded. The I-2 to I-6 ruling text is taken from the brief and DRAFT8.
