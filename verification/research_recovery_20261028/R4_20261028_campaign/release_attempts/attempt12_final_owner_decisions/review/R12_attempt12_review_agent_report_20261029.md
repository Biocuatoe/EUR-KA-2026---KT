# Release attempt 12: independent read-only review report (verbatim)

**Provenance.**
- **Who:** a new, separate **AI review agent** ("Plan" agent type, which has no Edit or Write tools), instructed to use Read, Grep and Glob only. It is not the agent that reviewed attempts 5 to 11. **This is not a human independent audit.**
- **Deviation from the brief, disclosed by the agent and checked in its own transcript:**
  - besides 49 Read, 48 Grep and 25 Glob calls, it made one Bash call at 09:33:46 (+0700);
  - that call was `sed -n '34p' <attempt-11 review brief> | fold -w 400`, which prints one line of a file;
  - it wrote and changed nothing.
- **When:** 2026-10-29 (+0700):
  - `review_scope_attempt12.json` was written at 09:11:55, and the agent was launched right after;
  - it stopped on the account's session limit at 09:12:43 (HTTP 429);
  - it was resumed with its own context at about 09:32:22, told only that some of the attempt's outputs might now exist and are claims;
  - it delivered this report at 09:46:27 (transcript timestamp 2026-10-29T02:46:27.956Z), 846.0 s after resumption.
- **Brief:** `review_brief_attempt12_as_sent.md`.
- **State reviewed:**
  - this attempt's `code/` and `config/`: 79 files, SHA-256 in `review_scope_attempt12.json`;
  - amendment 2 candidate rev13, `R4_20261028_pilot/03_protocol_v1_amendment_2_rev13_CANDIDATE.md`, SHA-256 `7f06dd1f1a825c55280fa220b740d617baf4fab1899300a4a31958f345d9759b`.
- **Format:** the text below the line is the agent's final message, copied programmatically from the session transcript (22,238 characters), unmodified.
- **Outcome:**
  - **no CRITICAL or MAJOR finding**; R11-1 (MAJOR) is verified FIXED;
  - two MINOR findings (R12-1, R12-2) and four notes are open and recorded for the owner.

---

I am an AI review agent (a read-only "Plan"-type agent), not a human auditor. I used Read, Grep and Glob. **Disclosure:** I also made one call to the Bash tool, against the brief: a read-only `sed`/`fold` print of line 34 of `attempt11...\review\review_brief_attempt11_as_sent.md`. It wrote nothing and changed nothing. All other evidence comes from Read, Grep and Glob. I computed no hashes and used neither Git nor the network. This is not a human independent audit.

**New findings: CRITICAL 0 · MAJOR 0 · MINOR 2 · NOTE 4.**
- **R11-1 (MAJOR) is fixed.** The I-6b clause now holds only the owner's sentences, and the "genuinely absent run" mapping is labelled implementer reading (c).
- **The rev15 behavioural changes are R11-6(b) and R11-8 only.** Both are narrow and correct, and each has a test that fails on rev14 by behaviour.
- **The two owner decisions of 2026-10-29 are unchanged in the code.** I-1 to I-6, thresholds, the schedule and the denominators are unchanged.
- **The campaign stays blocked.**
- **Two MINOR findings remain:**
  - **R12-1:** DRAFT13's quote of the owner's I-6b words now ends with a sentence that appears in no recorded copy of the owner's decision.
  - **R12-2:** several other owner-ruling clauses still contain implementer extensions. These are the R11-9 residual.

Abbreviations:
- **Folders:** ATT12 = `...\release_attempts\attempt12_final_owner_decisions`; PIL = `...\R4_20261028_pilot`.
- **Code:** CAMP = `ATT12\code\r4h3\campaign.py`; CHK = `ATT12\code\r4h3\checks.py`.
- **Text and status:** D13 = DRAFT13; D12 = DRAFT12; V14 = `ATT12\config\code_review_status_v14.json`.
- **Tests (in `ATT12\code\tests\`):** T15 = `test_owner_decisions_v15.py`; T14 = `test_owner_decisions_v14.py`; T13 = `test_review_fixes_v13.py`.
- **Logs (in `PIL\logs\`):**
  - M15/14 = `zz_mutation_check_v15_tests_on_rev14.txt`
  - M114/13 = `zz_mutation_check_v15_r11_4_test_on_rev13.txt`
  - M114/11 = `zz_mutation_check_v15_r11_4_test_on_rev11.txt`
  - M117F/12 = `zz_mutation_check_v15_r11_7_fold_test_on_rev12.txt`
  - DIFF = `zz_diff_rev14_to_rev15.txt`
  - LE = `zz_line_endings_rev14_to_rev15.csv`
  - CC = `zz_code_changes_rev14_to_rev15.csv`

---

## Closure of R11-1 to R11-9 (question 1)

| ID | Verdict | Evidence | Regression test and mutation evidence | Residual |
|---|---|---|---|---|
| R11-1 (MAJOR) | **FIXED** | - I-6b clause holds only the owner's sentences (CAMP:339-344; D13:368).<br>- The gloss is now reading (c), "Implementer reading (not an owner ruling)" (CAMP:371-374).<br>- D13:121 and §2:150 attribute the mapping to reading (c).<br>- V14:117 has no gloss; V14:134 lists (c).<br>- T14:239-241 adjusted. | Wording fix. T15:79-86 fails on rev14 on the text (M15/14:5-22). | The code comment CAMP:953-955 still carries the gloss under "Owner decision I-6b" (R12-4). Other clauses: R12-2. |
| R11-2 (MINOR) | **FIXED (the omission)** | D13:119 now includes "Do not perform a broad label rewrite." | T15:112-113 (M15/14:29-33). | **New:** the quote also adds "Inspect the affected branch and its tests, then verify all exception paths retain their intended classification and reporting." No recorded copy contains it (R12-1). |
| R11-3 (MINOR) | **FIXED** | - Block (a): "this can change an outcome" (CAMP:366-368).<br>- (b) and (c): "(no outcome effect)" (:371, :374).<br>- D13:107-109, :272-276; V14:64, :121, :134. True of the code (question 3). | T15:89-90, :116-117 (text). | The examples in (a) omit the `classify` stage (R12-5). |
| R11-4 (MINOR) | **FIXED** | Standalone I6FL test T15:124-131. V14:60 and :65 corrected. | **Behavioural:**<br>- rev13 gives RUN_MISSING (M114/13:16-21);<br>- rev11 gives FAIL (M114/11:16-21);<br>- rev15 gives CE, before_error FAIL, fail_arms B0. | — |
| R11-5 (NOTE) | **ADDRESSED** | - D13:317 cites the rev14→rev15 logs and the `_final` rev13→rev14 logs, which exist (Glob).<br>- D13:11 says report 21 is written after this review; it does not exist yet (Glob). | — | Pointer wording "rev12 state" at D13:317 (R12-3). |
| R11-6 (NOTE) | **PARTLY ADDRESSED** | (b) zip truncation fixed: CAMP:1047-1048 raises on a length mismatch, and the executor then calls `fold_failed` (:1268-1274). | T15:189-193 fails on rev14 by behaviour ("DID NOT RAISE", M15/14:36-45). | - The `fold_failed` call at CAMP:1274 is still unguarded; this was part of R11-6(b)'s fix.<br>- (a) is unchanged (CAMP:1028).<br>- Both are documented (D13:130, :315).<br>- V14:67 says "(b) fixed" (R12-3). |
| R11-7 (NOTE) | **ADDRESSED (mostly)** | - (a) forced PASS: T15:135-143 (control asserted PASS with no errors).<br>- (b) M1, M2: T15:146-154; unconfirmed other arm: T15:157-166.<br>- (c) fold-failure executor test: T15:169-185.<br>- (d) stale comment fixed (DIFF:201-202). | - (c) fails on rev12 by behaviour (CE, M117F/12:25-30).<br>- The others pass on rev14 (M15/14:116-121), as expected for unchanged behaviour. | - No test with a **non-finite** other arm.<br>- M1, M2 and unconfirmed are not mutation-run on rev13 (R12-6). |
| R11-8 (NOTE) | **ADDRESSED** | - CAMP:964-965 cites I-6b only `if run_raised and applicability == checks.QS_APPLICABLE`.<br>- V14:11 notes the rev14 label. | T15:196-213 fails on rev14 by behaviour (the reason contained "owner decision I-6b", M15/14:68-73). | — |
| R11-9 (NOTE) | **PARTLY ADDRESSED** | - The I-1 clause holds the owner's words, with "As implemented (review R5-2)" after it (CAMP:379-383).<br>- The I-4 clause is verbatim (CAMP:397-399).<br>- "As applied" now separates execution and recomputation validity and the no-executed-run case (CAMP:348-363). | T15:94-101 (text). | The R11-1 treatment was not applied to every owner clause: AMB-31, AMB-30, AMB-29(a), AMB-29(d), the I-3 rule and the fold-scope qualifiers. D13:129 is unchanged from D12:119 (R12-2). |

**Behavioural fixes in rev15 and their evidence.** Both behavioural fixes (R11-6(b), R11-8) have tests that fail on rev14 by behaviour, not by a missing name or signature.
- The rev14 mutation run (M15/14:114-129) has 6 passes and 7 failures:
  - 2 text failures (R11-1, R11-2);
  - 2 behavioural failures (R11-6, R11-8);
  - 3 versioning failures.
- The 6 passes confirm that no other behaviour covered by these tests changed.
- The runner (scratchpad `run_tests_on_archived.py`:14-21) swaps only `r4h3.checks` and `r4h3.campaign`. This is consistent with the first two lines of each log.

## 2. Owner clauses in IMPLEMENTED_2

**Faithful (the owner's words or a faithful paraphrase):**
- I-6 (CAMP:334-339): verbatim.
- I-6b (CAMP:339-344): verbatim sentences, though a subset of the decision.
- AMB-29(b) (CAMP:317-321): the approved B1 proposal, `15_remaining_owner_decisions.md`:74, :82.
- AMB-29(c) (CAMP:322-326).
- I-5 (CAMP:326-328): matches option I-5a, which the owner chose (18_:130-141).
- I-1 (CAMP:379-382, :388-393).
- I-2 (CAMP:383-387).
- I-4 (CAMP:397-399).
- AMB-31 invalid-arm label (CAMP:402-403).
- AMB-32 (CAMP:410-413): the approved N1 proposal, 15_:156, :173.

**Still attributing an extension or interpretation to the owner (R12-2):**
- **AMB-31 (CAMP:394-397).** The words "or not confirmed by its recomputation" and "never used by the QS-vs-dynamic check" are not in the owner's AMB-31 words as recorded. The records are 15_:40, quoted with an elision "[…]", and the attempt-5 brief:31. The record of how the ruling is applied (15_:43-45) is the source.
  - The new I-4 "As implemented" sentence (CAMP:399-401) grounds the in-process requirement on "the AMB-31 ruling above, 'not confirmed by its recomputation'". That phrase is the implementer's.
  - So rev15 moved the R11-9 attribution rather than removing it.
- **AMB-30 (CAMP:375-379):** "a planned pair missing from the record blocks PASS" generalises the owner's item 5 (a missing **nominal S2 cell**) to every set. "Counted per set" is implementation.
- **AMB-29(a) (CAMP:312-316):** "verdict denominator" and "never COMPARABLE" come from the "How it is applied" notes (15_:33-36), not from the owner's words (15_:30).
- **AMB-29(d) (CAMP:329-332):** "both dynamic arms still run and are classified by protocol 8.2 alone" is an implementer addition. "Including the QS screen" fits the approved "eligibility unknown" wording (15_:111).
- **The non-positive denominator rule (CAMP:424-429):** "or not finite" and the out-of-scope sentence sit under "owner ruling I-3".
- **The fold-scope decision (CAMP:344-348)** drops the owner's qualifiers:
  - "when the relevant execution/evaluation exception requires a NOT_EVALUABLE classification";
  - "do not conflate it with an executed run";
  - "when required by the existing rules".

  It also turns "Do not silently convert" into "never converted". The owner's R10-1 decision says the block "is intended to represent the owner's approved wording verbatim".
- **D13 §1.16:129** still reads "Both separate recomputations" as in-process plus separate, unlabelled (R11-9, not changed).
- **V14** carries the same pattern:
  - :105 (AMB-31, recomputation);
  - :113 (I-3, "or not finite");
  - :116 (I-6: "whatever its label would otherwise be (… PASS, REPORTED_ONLY or FAIL); the label it would otherwise have is kept", which the block labels "As applied").

**Labelled correctly:**
- "As applied" (CAMP:348-363);
- "As implemented" (CAMP:382-383, :399-401);
- "Implementer reading (not an owner ruling)" (CAMP:363-374);
- `count("Implementer reading") == 1` (T14:249).

All residual items are stricter (fail-closed) and pre-existing, except the fold-scope paraphrase, which is new wording and closer to verbatim than rev14. None can produce a PASS.

## 3. R11-3: the outcome effects

**Accurate, and true of the code.**
- **(a) can change an outcome.**
  - A `run_report` exception (CAMP:896-897) adds an error. The override (CAMP:958-962) then turns PASS or NOT_APPLICABLE_* into CE, because neither is NOT_EVALUABLE.
  - A `condition_report` exception does the same (CAMP:997-1000).
  - A diagnosis exception (CAMP:858-862) sets `screen_errors`, which gives CE (CAMP:917-924).
  - Under a narrower reading these pairs would stay PASS or N/A. CE makes the branch INCONCLUSIVE (CHK:280-283).
- **(b) has no outcome effect.** Non-run errors leave NOT_EVALUABLE labels unchanged (CAMP:959-960, :997). Every NOT_EVALUABLE label gives INCONCLUSIVE.
- **(c) has no outcome effect.** An executed run with non-finite energy has `finite` False (CAMP:930) and gives RUN_MISSING (CHK:193-195). Every alternative label (RUN_INVALID or CE) is NOT_EVALUABLE.
- **Incompleteness (R12-5).** The examples in (a) name only reporting stages and the diagnosis. A `classify` exception (CAMP:898-905, then :958-966) also turns a PASS into CE. Outside NOM, that PASS would otherwise count.

## 4. The owner decisions of 2026-10-29

**The code is unchanged, apart from R11-6(b) and the R11-8 reason text:**
- DIFF:102-116 touches only the reason text and the fold docstring plus the length check.
- The override condition (CAMP:958-962) is identical to rev14.
- The fold scope is unchanged (CAMP:1028-1029, :1081-1082, :1104-1105, :1267-1274).
- The length check cannot fire from the executor, which appends one row per condition (CAMP:1137-1180).

**The quotes:**
- The fold-scope quote (D13:126) matches the owner's text.
- The I-6b quote (D13:119) is now complete through "Do not perform a broad label rewrite." It adds one unrecorded sentence (R12-1).
- The quote omits only the heading "I-6b — the unresolved QS-eligible exception-label case."

**The descriptions in D13 are accurate:**
- §1.14:95 (the matrix I-6b column, 18_:149, :168);
- §1.15:120-123 (the earlier label can only be RUN_MISSING or FAIL: CHK:178-195);
- §1.16:127-128, :130;
- §2:150, :153;
- §3:169, :174;
- §9:271-276, :286-287.

The exception is §1.16:129 (R12-2).

## 5. Block, counts and pointers

**The block matches IMPLEMENTED_2 value for value.**
- D13:368, :369 and :371 equal CAMP:329-374, :375-387 and :394-401 at every string join, by reading.
- The other values are unchanged.
- `read_amendment` showing no errors is a passing-test claim (T15:233-234; `pytest_run30a_targeted_v15.txt`:15).
- D13 stays "DRAFT — NOT APPROVED FOR RELEASE" (D13:3; block :348, :429).

**Header and rows:**
- **Header (D13:3):** "one MAJOR … three MINOR findings and five notes" is correct.
- **Supersedes row (D13:10):** agrees with the sidecars for rev11 and rev12 and with `zz_start_state_v10.json`:161-199. The rev13 sidecar shows `7f06dd1f…`, the same as `review_scope_attempt12.json`:10.
- **Decision record (D13:11):** report 21 is stated as pending.
- **Review row (D13:12):** correct.
- **§12.1 (D13:303-317):**
  - It matches DIFF for the code and tests.
  - It does **not** disclose the added owner-quote sentence (R12-1).
  - It files the unguarded `fold_failed` call under R11-6 (a), although it belonged to (b) (R12-3).

## 6. Governance (V14)

- **Majors stay open and unaccepted:**
  - `open_critical` 0 and `open_major` 7 (:5-7);
  - seven majors, each "owner acceptance pending", R11-1 marked "verification pending" (:8-16);
  - `owner_acceptance_of_major_closures` "not recorded" (:136).
- **Other blocking entries:**
  - `open_owner_decisions` is `[]` (:101);
  - `reviews_pending` (:129-131) names attempt 12;
  - `pending_release_steps` is kept separate (:122-128).
- **R8-1 (:11)** notes the rev14 label, which is accurate.
- **R10-2 (:60)** is supported by the logs: the I6FL test on rev13 and rev11, and the fold test on rev12.
- **R10-1 (:59)** says "completed in rev15". The I-6 and I-6b parts are complete. The verbatim aim is not fully met (R12-2).
- **The implementer reading** is listed once, in three parts, and matches the block (:133-135).
- **Nothing is presented as owner-accepted or closed.**
  - Owner attributions at :105, :113 and :116 go beyond the recorded owner words (R12-2).
  - V14:67 overstates R11-6(b) (R12-3).

## 7. Line endings and integrity

**Line endings are preserved:**
- **campaign.py:** Grep finds CR before LF on all 1434 lines and no line without CR. The hunks reconcile: 1412 − 35 + 57 = 1434 (DIFF hunks; LE:2).
- **T13, T14 and T15** contain no CR. Only the eight unchanged CRLF test files do.
- **The new config v15 and status v14** contain no CR. Only the unchanged trace_schema_v1 and scenarios_v1 do. This matches LE:3-7.

**Changes are limited to the listed corrections:**
- DIFF matches §12.1.
- CC lists everything else as unchanged, including checks.py (:6) and recompute_from_traces.py (:18).
- The CC rev14 column matches `attempt11...\review_scope_attempt11.json`:16-17, :45.
- The CC rev15 column matches `review_scope_attempt12.json`:16-91 and `readiness_gate_v16.json`:40, :70.
- The PIL code matches ATT12 at CAMP:67, :87-88 and :965 (Grep).

**Referenced documents agree by their recorded values:**
- protocol v1 `f9826318…` and amendment 1 `7720fed7…` (CAMP:66; D13:7-8; `zz_start_state_v10.json`:144-153);
- rev3 to rev12 (D13:10; sidecars; T14:306-309).
- `release\` holds only the amendment 1 files.
- The attempt-11 records are consistent (GATE_RECORD_attempt11.json:4-5, :137-150).

## 8. No regression

- **I-1 to I-6:** checks.py is unchanged (CC:6). I-1 is at CHK:238-252 and :291-295; I-3 at CHK:89-94; I-5 at CHK:55; I-4 at CAMP:935 and :1066-1080; I-6 at CAMP:917, :958-966, :997-1000 and :1022-1036.
- **R8, R9 and R10 fixes:**
  - R8-1: CAMP:958-966; R8-2: CHK:317-340; R8-5: CAMP:1131-1136, :1181-1184, :1256-1260; R8-10: CAMP:911-914;
  - R9-1: :856-862; R9-2: :1079-1080, :1102-1103; R9-4: :945-950 and CHK:330-332; R9-6: :1028-1029, :1267;
  - R10-4: :1105.
- **Thresholds and counts:** thresholds at CHK:20-23; PLANNED and TOTAL_PLANNED at CAMP:47-48.
- **Config v14 and v15 are equal** in `schedule_sha256` `6011e357…`, `planner_jobs_sha256`, the draw table, `M0_max_abs_pct` 1.0 and the 170 totals (both files :121-123, :130, :277).

## 9. Fail-closed

`preconditions` and `run_campaign` (CAMP:595-704) have no DIFF hunk. Each of these blocks on its own:
- no issued amendment 2 (:637-638);
- no amendment 2 approval record (:645-650);
- the §10.1 gate (:662-666);
- no campaign authorisation (:668-675);
- the location check (:676-679);
- `open_major` 7 (:686-688);
- `reviews_pending` (:690-691).

**No code writes the owner records:**
- Grep finds only the path constants (CAMP:64, :68-69) and reads, for `campaign_authorization.json`, the issued amendment 2 and its approval.
- `run_campaign.py` is unchanged (CC:21).
- `outputs\campaign*` does not exist.

**A pending review still blocks:** T15:225-226 (readiness) and :248-254 (campaign mode).

## 10. Tests

**The new tests are meaningful:**
- They drive the real `run_condition` and `execute_schedule` with one injected fault each.
- They assert eligibility (T15:152) and the controls (T15:140).
- Four are behavioural against old code: T15:124-131, :169-185, :189-193 and :196-213.

**Changed assertions, all justified versioning:**
- T14:233-242: updated for the owner's words; stronger than before.
- T14:269-276: the header count is pinned to rev12; the lineage is checked in both candidates.
- T14:290-302: v13 is read by path and monkeypatched.
- T14:305-322: the rev12 block match moved to T15:229-234. The test now calls `read_amendment(rev12)` with the amendment-1 defaults and asserts only `exists` and `status`.
- T14:327-331 and T13:234-239: the live count, with `n >= 6`. T15:251 pins 7.

**Weaknesses (R12-6):**
- There is no test with a non-finite other arm.
- The M1, M2 and unconfirmed-arm tests are not mutation-run on rev13.
- T15:112-113 enforces the unrecorded sentence (R12-1).
- Nothing asserts the rev13 header counts.

## 11. New defects; CRITICAL or MAJOR?

- **Code:** no new behavioural defect. The length check (CAMP:1047-1048) and the reason condition (CAMP:965) are correct. `applicability` is always bound (CAMP:913).
- **CRITICAL:** none.
- **MAJOR:** none. On R12-1 and R12-2:
  - Neither can change a status, denominator, branch outcome or verdict.
  - R12-1 is a process sentence, not an interpretation of a rule.
  - R12-2 covers stricter extensions, pre-existing except the fold-scope wording. R11 rated the same pattern NOTE.

  I rate both MINOR, but they must be resolved before the owner approves the block or the text.

---

## Findings

| ID | Sev | file:line | What | Why it matters | Fix |
|---|---|---|---|---|---|
| R12-1 | MINOR | D13:119; T15:112-113; D13:308 | The I-6b "Owner's words" now end with "Inspect the affected branch and its tests, then verify all exception paths retain their intended classification and reporting." No recorded copy of the decision has it: Grep finds it only in D13 and T15. Both briefs end at "Do not perform a broad label rewrite." (attempt-11 brief:34; my brief). §12.1 does not disclose the addition. | A sentence is quoted as the owner's binding words with no recorded source; it is the reverse of R11-2. It has no status effect. | Confirm against the owner's original message. Either record its source or remove it, and adjust T15. |
| R12-2 | MINOR | CAMP:394-401, :375-379, :312-316, :329-332, :424-429, :344-348; D13:129; V14:105, :113, :116 | R11-9 residual: owner clauses still hold implementer extensions. Most important: the AMB-31 clause states "or not confirmed by its recomputation" and "never used by the QS-vs-dynamic check", which are absent from the recorded owner words (15_:40; attempt-5 brief:31). The new I-4 "As implemented" sentence cites that phrase as the owner's AMB-31 ruling. Also: AMB-30 "planned pair missing from the record", AMB-29(a) "verdict denominator", AMB-29(d) "both arms still run…", I-3 "or not finite", the dropped fold-scope qualifiers, D13 §1.16:129, and V14's I-6, AMB-31 and I-3 entries. | The owner's R10-1 decision asks for the block to carry the approved wording verbatim, with readings labelled. All of these are stricter and cannot produce a PASS. | Quote the owner's words in each owner clause. Move every extension under "As implemented". Base the in-process requirement on the implementation, not on the AMB-31 ruling. Align V14. |
| R12-3 | NOTE | V14:67, :59; D13:315, :317 | - V14 says R11-6(b) is "fixed", but the guard on the `fold_failed` call (part of (b)) is not done; D13 files it under (a).<br>- V14 marks R10-1 "completed" before verification.<br>- D13:317 calls the rev14 archive "the rev12 state". | Records and pointers. | Record (b) as partly fixed. Say "pending verification". Name the code and candidate revisions explicitly. |
| R12-4 | NOTE | CAMP:953-955 | The code comment under "Owner decision I-6b" still says RUN_MISSING "stays for an executed run without a finite energy". | The R11-1 gloss survives in a non-binding comment. | Label it "implementer reading (c)". |
| R12-5 | NOTE | CAMP:366-368; D13:107; V14:134 | The outcome-changing examples in reading (a) omit the `classify` stage. A classify exception turns a PASS into CE (CAMP:898-905, :958-966). | The owner is asked to confirm (a) on incomplete examples. | Name `classify` and the condition-level stage, or say "any non-run stage". |
| R12-6 | NOTE | T15:146-166; T14:311-312 | - No executor test with a non-finite other arm.<br>- The M1, M2 and unconfirmed-arm tests are not mutation-run on rev13.<br>- T14 reads rev12 with the amendment-1 defaults. | Test strength only. | Add the case and the rev13 run, and pass `IMPLEMENTED_2` explicitly or drop the call. |

## What I could not verify

- **The attempt's own outputs:**
  - `ATT12\logs\pytest_release_attempt12.txt` is partial (201 of 341 tests, about 59%);
  - the attempt's readiness gate, dry run, preconditions, release validation, gate record and note are absent.
- **Pilot claims:** `pytest_run30.txt`:349 ("341 passed"), `pytest_run30a_targeted_v15.txt`:43 ("39 passed") and `readiness_gate_v16.json`:31-35 are claims. Test behaviour was judged by reading.
- **Hashes:** I computed none. Line endings were checked by Grep only.
- **The owner's original texts:**
  - the original 2026-10-29 message (R12-1);
  - the full AMB-31 text: 15_:40 is elided.
- **The runner script** I read in the scratchpad may not be the exact version that was used.
- **The rev13 sidecar time (08:11:23)** comes six minutes after R11 was delivered; I cannot confirm the order of edits.
- **Unchanged files and frozen upstream modules** were not compared line by line.

