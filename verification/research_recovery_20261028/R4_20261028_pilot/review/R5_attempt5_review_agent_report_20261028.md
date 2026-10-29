# Release attempt 5: independent read-only review report (verbatim)

**Provenance.**
- **Who:** a separate **AI review agent** ("Plan" agent type, which has no Edit or Write tools), instructed to use Read, Grep and Glob only. **This is not a human independent audit.**
- **When:** started 2026-10-28 14:49 (+0700). It stopped once on a service rate limit while reading `campaign.py`, was resumed with its own context after 15:21, and delivered this report at about 15:55.
- **Brief:** `review_brief_attempt5_as_sent.md` (the brief as first sent). On resumption it was told only that the attempt's own logs, dry run, precondition record, release validation and `review_scope_attempt5.json` now existed, and were claims as well.
- **State reviewed:** this attempt's `code/` and `config/` (57 files, SHA-256 in `review_scope_attempt5.json`) and the amendment 2 candidate rev5, `R4_20261028_pilot/03_protocol_v1_amendment_2_rev5_CANDIDATE.md`, SHA-256 `e7ba73c11784b3cf38f48e32b69a7a7c21b070d039118547d638bc1bf06d4f5f`.
- **Format:** the text below the line is the agent's final message. The only edit is removing the two-space indentation that the message relay adds.
- **Outcome:** 2 MAJOR findings (R5-1, R5-2) are open in this attempt. They are fixed in a new attempt (`../attempt6_review_fixes/`), not here; this attempt is kept unchanged as reviewed.

---

I am an AI review agent (a read-only "Plan"-type agent, not a human auditor). I used only the Read, Grep and Glob tools. I ran nothing, wrote nothing, computed no hashes and did not use Git or the network.

**Summary: CRITICAL 0 · MAJOR 2 · MINOR 10 · NOTE 3**

Path abbreviations:
- ATT = `D:\EURÉKA 2026 - KT\verification\research_recovery_20261028\R4_20261028_campaign\release_attempts\attempt5_owner_rulings`
- PIL = `D:\EURÉKA 2026 - KT\verification\research_recovery_20261028\R4_20261028_pilot`
- DRAFT = `PIL\03_protocol_v1_amendment_2_rev5_CANDIDATE.md`
- Code references are `ATT\code\r4h3\<file>:<line>` unless stated otherwise.
- I compared the attempt's code against `PIL\archive\rev7_attempt4_20261028_1405\code` (rev7) and `PIL\archive\rev6_attempt3_20261028_1201\code` (rev6) by reading them.

---

## Q1. Do AMB-29(a)–(d), AMB-30 and AMB-32 behave as ruled, in the code and in the outputs?

**AMB-29(a), missing profile: mostly as ruled.**
- The condition stays an explicit outcome: `PROFILE_UNAVAILABLE` or `BASELINE_UNAVAILABLE` (checks.py:388-391; campaign.py:774-775). The missing arm gets a not-executed run row (campaign.py:750-754).
- It never yields a paired comparison: `paired_delta` refuses any non-COMPARABLE status (checks.py:408-409).
- It counts in every denominator: `feasibility_accounting` (checks.py:448-484), `denominator` (checks.py:417-425) and the nominal cells of `h3_verdict_eligibility` (checks.py:516-520).
- Only the pair's check becomes `NOT_APPLICABLE_PROFILE_UNAVAILABLE` (checks.py:151-154). Inside NOM such a cell blocks a branch PASS (checks.py:225).
- **Exception (R5-2, MAJOR):** if the other profile exists but fails the QS screen, `pair_qs_dynamic` labels the pair `NOT_APPLICABLE_QS_INFEASIBLE`, because "failed" is checked before "missing" (checks.py:145-150). A NOM cell without a profile then does not block a branch PASS (checks.py:225). This contradicts DRAFT §6 item 3, I-2 and the machine-block text "with both profiles".

**AMB-29(b), missing usable energy or invalid arm: as ruled.**
- Labels: `NOT_EVALUABLE_RUN_MISSING` and `NOT_EVALUABLE_RUN_INVALID` (checks.py:155-160, 176-181).
- Any `NOT_EVALUABLE_*` pair makes an M0/M1 branch INCONCLUSIVE (checks.py:248-251).
- The QS check uses an arm only if it passes §8.2 and its in-process recomputation (campaign.py:789-792). `fold_separate_recomputation` then demotes any PASS, FAIL or REPORTED_ONLY that used an arm the separate recomputation does not confirm (campaign.py:861-873).
- The paired endpoint needs the final status COMPARABLE after the separate recomputation (campaign.py:858-860). The energy role is CONFIRMATORY only for a COMPARABLE condition whose run is confirmed by both recomputations (campaign.py:1017-1028; checks.py:435-445).
- Traces are written before evaluation, and non-finite traces are kept (campaign.py:703-716).
- **Gap (R5-6, MINOR):** a run whose simulation finished but whose evaluation raised is recorded as `executed=False` and `NO_ENERGY_NOT_EXECUTED` (campaign.py:769-773). Its simulator energy is discarded, and the separate script skips it (recompute_from_traces.py:41-43). Its trace file is kept on disk.

**AMB-29(c), QS energy ≤ 0: as ruled for the QS check.**
- `qs_vs_dynamic` returns `diff_pct=None`, keeps the raw `E_qs_J`, `E_dyn_Wh` and `d_ref_m`, and names the term (checks.py:295-318; `non_positive_term` at checks.py:78-83).
- The pair becomes `NOT_EVALUABLE_QS_UNDEFINED` with the term in its reason (checks.py:182-186; M2 at 165-169). The M0/M1 branch becomes INCONCLUSIVE (checks.py:248-251).
- Per-arm raw values and terms are written to the evaluation rows (campaign.py:803-812). The condition-level field is `qs_vs_dyn_non_positive_terms`.
- The condition status and energy role are untouched, because `classify_pair` reads no QS input.
- No epsilon, absolute value or substitute threshold is used in the QS path.

**AMB-29(d), evaluation error: as ruled inside the guarded blocks; not for the code paths outside them.**
- Per-run exceptions are recorded with the run ID (campaign.py:769-773).
- Pair-evaluation exceptions are recorded with both run IDs, give `NOT_EVALUABLE_CONDITION_ERROR`, and leave the runs and the condition status intact (campaign.py:794-799).
- Condition-level exceptions are recorded with the run IDs and give status ERROR plus `NOT_EVALUABLE_CONDITION_ERROR` (campaign.py:922-933).
- There is no retry. `record_invariant` is computed (campaign.py:944-954).
- **R5-1 (MAJOR):** the QS screen (campaign.py:741-746) and the post-run reporting block (campaign.py:800-833) are outside any try. An exception there becomes a condition-level ERROR, the dynamic arms are never run or their records are replaced, and the runs are labelled "not executed".
- **R5-8 (MINOR):** the separate-recomputation subprocess, the fold and the `conditions.csv` write (campaign.py:979-986) are also unguarded.

**AMB-30, required sets: as ruled, apart from R5-2.**
`branch_qs_dynamic_outcome` (checks.py:200-264) makes the branch INCONCLUSIVE in each of these cases:
- a FAIL in any set, counted per set and never averaged (lines 245-247; `_by_set` at 191-197);
- any `NOT_EVALUABLE_*` pair (248-251);
- a required nominal cell that is absent, duplicated, without a profile or not evaluable (219-225, 252-254);
- no PASS on NOM (226, 255-258);
- a REPORTED_ONLY label on M0/M1 (243-244);
- a planned pair missing from the record (227-228, 241-242).

A branch outcome is written for every motor, with the planned condition IDs (campaign.py:996-1004). No threshold changed.

**AMB-32: as ruled.**
- `h3_verdict_eligibility` (checks.py:502-542) blocks both SUPPORTED and NOT SUPPORTED whenever any of the six nominal cells is not COMPARABLE.
- It records each such cell with its status and reasons (`_missing_evidence`, checks.py:493-499) and says "INCONCLUSIVE, not NOT SUPPORTED" (532-533).

## Q2. Can anything disappear from a denominator, or create a PASS or SUPPORTED / NOT SUPPORTED by omission?

**In normal operation, no.**
- `execute_schedule` appends exactly one row per scheduled condition, including condition-level errors (campaign.py:898-943).
- `feasibility_accounting` groups every row by motor and set, by motor, and overall (checks.py:458-459).
- `qs_dynamic_accounting` groups every row by motor and set and by motor; its eligibility classes add up (checks.py:270-291).
- `energy_roles.csv` has one row for each run ID of each condition (campaign.py:1017-1028).
- The D5 denominator counts every status (campaign.py:1006).
- `h3_verdict_eligibility` uses fixed denominators: 6 nominal cells and 32 draws per motor (checks.py:516-526).
- A branch PASS needs the planned IDs to be present (checks.py:227, 241).
- The exception handlers for the branch outcome, denominator and verdict produce INCONCLUSIVE or an error record, never a PASS (campaign.py:999-1004, 1007-1010, 1036-1040).

**Residual issues:**
- **R5-2 (MAJOR):** a NOM cell without a profile can avoid blocking a branch PASS. The H3 verdict still cannot become SUPPORTED or NOT SUPPORTED, because that cell is not COMPARABLE (checks.py:518, 530-531).
- **R5-9 (MINOR):** if the energy-role loop raises part-way, a partial `energy_roles.csv` is written (campaign.py:1013-1041).
- **R5-8 (MINOR):** an exception in the subprocess, fold or CSV step stops `execute_schedule` before `conditions.csv`, the accounting files, the manifest and the post-run SHA list are written.
- **R5-14 (NOTE):** a `record_invariant` violation is only recorded. Sensitivity rows are not de-duplicated by draw (checks.py:523-526).

## Q3. Can a pass in INS (S1) or any set other than NOM substitute for a missing or failed nominal S2 check?

**No.**
- `n_nom_pass` counts only the motor's two NOM cells (checks.py:219-226). With no NOM PASS the branch is INCONCLUSIVE, and the reason states that other sets cannot substitute (checks.py:255-258).
- A failed NOM check counts as a FAIL (checks.py:245).
- A missing, duplicated, profile-less or not-evaluable NOM cell is listed in `lacking` (checks.py:225, 252-254).
- `h3_verdict_eligibility` reads only NOM rows for the nominal cells (checks.py:513-520).
- The schedule check confines S1 to INS, P3 to the P3 set, and 0.5 ms to CNV (campaign.py:190-193). The dry run reports all of these true, and I counted 170 rows (12 of them S1) in `ATT\dry_run_20261028_152102\schedule_170.csv`.
- **Caveat:** R5-2, and the I-1 reading that one NOM PASS plus one QS-infeasible NOM cell can PASS (DRAFT §9 I-1).

## Q4. Can a QS-only inapplicability or non-evaluability invalidate, or change the status or energy role of, a valid dynamic run?

**Through labels, no.**
- `classify_pair` takes no QS input (checks.py:382-400), and `energy_role` reads none (checks.py:435-445).
- The fold changes only QS fields for QS reasons (campaign.py:861-873).
- The executor tests cover this path: QSNEG and PEX give COMPARABLE and CONFIRMATORY (`ATT\code\tests\test_owner_rulings_v8.py:296-304`).

**Through exceptions, yes (R5-1, MAJOR).**
- `eval_plant` and the per-profile `checks.qs_screen(...)` run before the arms and outside any try (campaign.py:741-746). The screen is diagnostic only (AMB-24), yet an exception there propagates to the condition-level handler (campaign.py:924-933). The condition becomes ERROR, neither dynamic arm runs, and both runs get `NO_ENERGY_NOT_EXECUTED`.
- An exception in the post-run reporting block (campaign.py:800-833), after both arms have run, has the same effect. The handler replaces `_sims` and `_rows`, so the executed runs are listed as not executed and their traces are left unreferenced.
- This contradicts DRAFT §3 (the condition status "never reads the QS screen or the QS check"; a QS status "never makes a run invalid") and the AMB-24 rule that the screen is diagnostic only.
- Likelihood is low, and the effect is fail-closed: it cannot produce a PASS, SUPPORTED or NOT SUPPORTED.

## Q5. Is non-positive QS energy handled without any fabricated percentage? What about other percentages?

**QS path: yes.**
- `diff_pct` is None and written as an empty string (`_blank`, campaign.py:641-642, 804, 807). No NaN is written as a number; rev7 wrote `float("nan")` (rev7 checks.py:228).
- The raw values and the exact term are kept (checks.py:299-310). No epsilon, absolute value or substitute threshold is used.
- `paired_delta` (checks.py:411-414), `scenario_totals` (325-329) and `grid_convergence` (340-343) refuse a percentage when the denominator is ≤ 0 or not finite. `grid_convergence` then returns `passed=None`, which `numerical_check_consequence` maps to `on_fail` (campaign.py:266-271).

**Other relative quantities that do not follow the stated rule (R5-5, MINOR; outside AMB-29(c)'s direct object, but DRAFT §1.5, §4.2 and I-3 claim "every relative percentage in the H3 code"):**
- `evaluator.compare_with_simulator.rel()` uses `abs(x - y) / max(abs(y), 1e-12)`, an absolute value plus an epsilon floor (evaluator.py:292-293). It decides crediting through E_chem, E_DC, distance and RMSE.
- `recompute_pos_neg_rel` uses `max(abs(E_pos), 1e-9)` (closedloop.py:143).
- `shortfall_pct` and `shortfall_vs_dref_pct` divide by `d_ref` without a guard (evaluator.py:223; closedloop.py:139).
- `closure_rel` fails closed with `inf` (evaluator.py:205).
- `timestep_check` would raise a TypeError on a `dE_rel` of None (checks.py:348-351). It is never called by the runner, and neither is `paired_delta`.
- Wording issue: when `d_ref` ≤ 0 the status string still says "undefined (QS energy <= 0)" (checks.py:302-303; R5-11).

## Q6. Does the runner stay fail-closed?

**Yes.**
- `run_campaign` raises `CampaignBlocked` before calling `execute_schedule` (campaign.py:602-611). The `--execute` entry point catches it and exits with code 2 (`ATT\code\run_campaign.py:29-36`).
- `preconditions("campaign")` requires:
  - frozen inputs and cycle inputs (campaign.py:511-518);
  - an up-to-date config (519-531);
  - issued amendment 1 with status APPROVED and its approval record, which must accept the pending review items (532-544);
  - issued amendment 2 with status APPROVED, a block equal to `IMPLEMENTED_2`, its approval record, and amendment 1's SHA-256 (545-559);
  - the §10.1 gate in `logs\pre_run_hashes.txt`, with code hashes and a clean junit record (571-575; slice.py:48-64);
  - `campaign_authorization.json` with the scope, both amendment SHA-256 values and the gate SHA-256 (577-584; 467-483);
  - the campaign root by resolved path, with no earlier smoke or campaign outputs (585-588);
  - review status with zero critical and major findings, no open owner decisions, and no `reviews_pending` items (589-598).
- **No code path writes the authorisation record.** A Grep over `ATT\code` outside `tests` finds only reads (campaign.py:64, 577-584).
- `_guard` refuses official run IDs outside campaign mode (campaign.py:645-650), and an existing output directory is refused (campaign.py:886).
- **A pending review blocks both modes.** `code_review_status_v6.json` lists `reviews_pending` (lines 50-52). `ATT\logs\preconditions_attempt5.json` reports the review blocker in readiness and campaign mode, plus missing amendment 2, missing gate, missing authorisation and wrong location (claimed output; consistent with the code).
- After this review, the next review-status file should record `open_major` = 2 unless R5-1 and R5-2 are fixed or accepted.

## Q7. Does DRAFT match the implementation?

**Machine block:** its keys and values match `IMPLEMENTED_2` key for key (DRAFT lines 217-289 against campaign.py:294-363; checked by reading). The dry run reports `draft_amendment_2.errors = []`.

**§6 branch rule:** matches checks.py:200-264, except the profile case in R5-2.

**§12 change list:** complete for checks.py and campaign.py as far as I can tell. By reading, I confirmed unchanged from rev7: `classify_pair`, `energy_role`, `feasibility_accounting`, `qs_dynamic_accounting`, `fold_separate_recomputation` and `run_arm`. The schedule SHA-256 `6011e357…` is identical in config v6, v7 and v8.

**Mismatches and overstatements:**
- **R5-2 (MAJOR):** I-2, §6 item 3 and the machine-block value "with both profiles" are not enforced when the other profile is QS-infeasible.
- **R5-3 (MINOR):** §9 (line 160) says "Each point is the fail-closed reading the code implements". For I-1 the implemented reading is the less strict of the two; the alternative, every NOM cell must PASS, is stricter. It does match the "at least one" wording of the recommended S4 option in `15_remaining_owner_decisions.md:140, 171`. For I-3, the consequence "an undefined ΔE_rel in a nominal cell leads to INCONCLUSIVE" (also §8, line 154) is implemented by no code: no verdict function reads ΔE_rel.
- **R5-4 (MINOR):** the machine-block and `IMPLEMENTED_2` values present the interpretation readings I-1 to I-6 as "owner ruling 2026-10-28". Examples: "at least one pair", "in-process or separate", the I-6 mapping, and the planner-percentage scope under "AMB-29(c) ruling" (campaign.py:315-359). `test_owner_rulings_v8.py:362-365` enforces that wording. The prose in §9 does disclose these as interpretations.
- **R5-7 (MINOR):** §4.1 says an invalid arm's QS value is kept "in `qs_vs_dyn_pct_diagnostic_invalid_run` only". That is false for arms the separate recomputation fails to confirm. `evaluation.csv` and `conditions\<id>.json` are written before the fold (campaign.py:935-937, 976). They keep the in-process `qs_vs_dyn_pct` and pair status. Rev5 does not say this; `15_…md` §5 did.
- **R5-11 (MINOR):**
  - §2 row `NOT_EVALUABLE_RUN_MISSING` says "a non-finite run". A non-finite run whose simulator energy is finite is classed `RUN_INVALID`.
  - §1.6 and I-6 say an exception inside a run "leaves the pair RUN_MISSING". That holds only if the pair is QS-eligible and the other arm does not FAIL (checks.py:145-150, 172-178).
- **R5-12 (MINOR):** the decision record `17_owner_rulings_attempt5_report.md` cited in DRAFT line 11 does not exist in PIL.

## Q8. Do the tests test what they claim? Were assertions weakened or thresholds changed?

**Changed assertions:**
- `test_case11` (`ATT\code\tests\test_amendment2.py:42-50`): the fixture now includes both NOM cells, as AMB-30 requires. Same strength.
- `test_r3_3` (test_amendment2.py:211-217): NA_PROFILE moved to P3 for the "no effect" assertion, and a new assertion that a NOM cell without a profile gives INCONCLUSIVE. Stricter; justified by AMB-30 and I-2.
- `test_rev3_draft…` (test_owner_rulings_v7.py:243-257): file-name update plus a rev4 hash pin. Stronger.
- `PIL\logs\pytest_run23a_targeted_existing.txt` shows these as the only semantic failures before the update (plus file-not-found failures caused by the rename). No assertion was weakened.
- **No threshold changed:** `QS_DYN_MAX_PCT` 1.0, `GRID_MAX_PP` 0.2, `OPTIMALITY_PP` 0.2, `TIMESTEP_MAX_PP` 0.01, `H3_SEN_DRAWS` 32, `H3_SEN_MIN` 29 (checks.py:18-21, 488).

**Vacuity (R5-10, MINOR):**
Several older tests build rows without `limits`. Since rev8 these assertions are INCONCLUSIVE only because the nominal cells are recorded as `NOT_IN_RECORD`, not because of the rule each test names:
- test_amendment2.py:28-29, 67-69 and 208-210;
- test_owner_rulings_v7.py:65-66 and 202-204.

The new v8 tests cover those rules properly:
- `test_amb30_a_nominal_pass_with_a_failure_in_another_preregistered_set_is_inconclusive` (test_owner_rulings_v8.py:66-74);
- `test_no_situation_yields_a_pass_by_omission` (lines 129-146);
- `test_amb30_all_required_checks_pass` (lines 77-87), which shows PASS is reachable.

**Coverage gaps:**
- Nothing tests an exception in the QS screen or in post-run reporting. `test_valid_dynamic_energy_is_kept_when_only_the_qs_comparison_is_not_evaluable` (test_owner_rulings_v8.py:296-304) injects only inside the guarded pair block (R5-1).
- Nothing tests the (screen False, profile None) NOM case (R5-2).
- The "never writes the authorisation" check is a static string search (test_owner_rulings_v8.py:384-386). My Grep confirms there is no writer.

**Test runs:** `ATT\logs\pytest_release_attempt5.txt` and `PIL\logs\pytest_run23.txt` both say "248 passed". I cannot confirm either.

## Q9. Are there CRITICAL or MAJOR findings?

**No CRITICAL finding.** The campaign cannot start, and no code path writes the authorisation. No confirmatory result is possible without COMPARABLE plus both recomputations. No PASS, SUPPORTED or NOT SUPPORTED possibility arises by omission.

**Two MAJOR findings:**
- **R5-1:** a QS-only exception outside the guarded blocks can change a condition's status and its runs' energy roles.
- **R5-2:** a nominal cell without a profile does not block a branch PASS when the other profile is QS-infeasible, contrary to DRAFT §6, I-2 and the machine block.

Both are fail-closed for the H3 verdict.

---

## Findings

| ID | Sev | file:line | What is wrong | Why it matters | Suggested fix |
|---|---|---|---|---|---|
| R5-1 | MAJOR | `campaign.py:741-746`, `800-833`; handler `924-933` | `eval_plant` and `checks.qs_screen` run before the arms, and the post-run reporting runs after them, all outside any try. An exception turns the condition into ERROR, skips the dynamic runs or overwrites their records with `executed=False`, and gives them `NO_ENERGY_NOT_EXECUTED`. | A QS-only diagnostic failure can change the condition status and energy roles. This contradicts AMB-24, the spirit of AMB-29(c)/(d) and DRAFT §3, and orphans traces. Low likelihood; fail-closed. | Wrap the screen per arm. On an exception, log it with the run IDs, treat eligibility as unknown (`NOT_EVALUABLE_CONDITION_ERROR`) and still run both arms. Wrap the post-run block so executed rows survive. Add executor tests for both paths. |
| R5-2 | MAJOR | `checks.py:145-150`, `225` | When one profile is missing and the other fails the QS screen, the pair is labelled `NOT_APPLICABLE_QS_INFEASIBLE`. In NOM that label is not counted as missing evidence, so a NOM cell without a profile does not block a branch PASS. The pair is also counted as "QS-ineligible" rather than "profile unavailable" in `qs_dynamic_accounting`. | Contradicts DRAFT §6 item 3, I-2 and the machine-block text "with both profiles". The QS branch outcome could be PASS where the stated rule gives INCONCLUSIVE. The H3 verdict is unaffected, because the cell is not COMPARABLE. | In `branch_qs_dynamic_outcome`, treat a NOM cell as lacking evidence when its condition status is `PROFILE_UNAVAILABLE` or `BASELINE_UNAVAILABLE`, or give "missing" precedence over "failed" in `pair_qs_dynamic`. Add a (False, None) test. |
| R5-3 | MINOR | DRAFT lines 154, 160, 164, 166 | "Each point is the fail-closed reading" is false for I-1, whose alternative is stricter. The I-3 verdict consequence is implemented by no code (`paired_delta` and `timestep_check` are never called; `timestep_check` raises on None). | The owner may approve I-1 believing it is the strictest reading. | Reword §9. Have the owner choose I-1 explicitly in the approval record. State that the ΔE_rel consequence belongs to the later analysis. |
| R5-4 | MINOR | `campaign.py:315-359`; DRAFT lines 237-241, 278; `test_owner_rulings_v8.py:362-365` | Interpretation readings I-1 to I-6 are labelled "owner ruling 2026-10-28" in the binding block, and a test enforces that label. | Readings not settled by the rulings are presented as settled. | Label them as readings confirmed by approval of amendment 2, or cite the §9 IDs. |
| R5-5 | MINOR | `evaluator.py:223`, `292-293`; `closedloop.py:139`, `143` | Relative quantities use `abs()` plus an epsilon floor, or an unguarded `d_ref` denominator. DRAFT §1.5, §4.2 and I-3 claim the rule covers every relative percentage. | The documentation overclaims. No effect in practice, because `d_ref` > 0 and these are tolerance checks, not savings. | Narrow the DRAFT wording or list these quantities with their reasoning. |
| R5-6 | MINOR | `campaign.py:769-773`; `recompute_from_traces.py:41-43`; `checks.py:473-474` | A run that was simulated and whose evaluation then raised is recorded `executed=False`. Its simulator energy is dropped, the separate script skips it, and `runs_executed` undercounts. | Reporting accuracy for AMB-29(b) "retain all available energy" and protocol 10.4. | Keep the `sim` row with `executed=True` and an `evaluation_error` field. Reference the trace. |
| R5-7 | MINOR | `campaign.py:935-937`, `976`; DRAFT line 110 | `evaluation.csv` and `conditions\<id>.json` keep the in-process QS status and `qs_vs_dyn_pct` of arms that the separate recomputation later fails to confirm. | Contradicts DRAFT §4.1 ("… only"); a reader can take a stale PASS or percentage at face value. | Document it in DRAFT, or rewrite or mark the per-arm fields after the fold. |
| R5-8 | MINOR | `campaign.py:979-986`, `984-985`; `recompute_from_traces.py:60-62` | Exit code 1 means both "a run failed a check" and "the script crashed or stopped on an independence violation". The separate script's traceback goes only to the manifest, truncated to 2,000 characters, and never to `errors.csv`. The subprocess, fold and `conditions.csv` steps are unguarded, so an exception stops before the summary outputs are written. | Partial preservation under AMB-29(d) and protocol 10.4. Fail-closed for statuses. | Use distinct exit codes. Write the separate script's failure to `errors.csv`. Guard these steps and still write the summary outputs. |
| R5-9 | MINOR | `campaign.py:1013-1041` | If the energy-role loop raises part-way, a partial `energy_roles.csv` is written with no marker in the file. | Breaks "one role per planned run" (DRAFT §4.1). | Build the list fully or write an explicit error row for every planned run. |
| R5-10 | MINOR | `test_amendment2.py:28-29`, `67-69`, `208-210`; `test_owner_rulings_v7.py:65-66`, `202-204`; `test_owner_rulings_v8.py:296-304`, `384-386` | Older tests now pass only because the nominal cells are absent, so they no longer test the rule they name. No test covers R5-1 or R5-2. The authorisation-writer check is a static string search. | These tests can pass vacuously; the gaps are covered only in part by the v8 tests. | Add `limits` and both NOM cells to the old fixtures. Add tests for R5-1 and R5-2. |
| R5-11 | MINOR | `checks.py:302-303`; DRAFT lines 45, 75, 240 | The `d_ref` ≤ 0 case is labelled "QS energy <= 0". The RUN_MISSING and I-6 wording is imprecise. "with both profiles and evaluable" sits beside an allowed QS-infeasible cell. | Wording only. | Correct the labels and the text. |
| R5-12 | MINOR | DRAFT line 11 | The cited decision record `17_owner_rulings_attempt5_report.md` does not exist in PIL. | The traceability reference dangles. | Produce the record or remove the citation. |
| R5-13 | NOTE | `checks.py:528-531` | A `NOT_EVALUABLE_QS_UNDEFINED` pair leaves the energy CONFIRMATORY and the condition COMPARABLE. Through the protocol §8.1 rule "every check in §9 passes", the H3 verdict still becomes INCONCLUSIVE. | This is the existing §9 consequence, not an invalidation; the owner should see it stated. | Say so explicitly in DRAFT §3 or §8. |
| R5-14 | NOTE | `campaign.py:952-954`; `checks.py:523-526`; `campaign.py:813` | A `record_invariant` violation is recorded but does not block. Sensitivity counts are not de-duplicated by draw. `dynamic_valid_pair` is computed before the recomputation. | Reporting only. | Optional hardening. |
| R5-15 | NOTE | — | Verified by reading: the rev7-to-rev8 "unchanged" claims; thresholds unchanged; the 170-run schedule hash unchanged in config v6, v7 and v8; S2 not used for tuning; the test changes are justified by AMB-30 or the file rename. | — | — |

---

## What I could not verify

- **Test results.** I cannot run tests. "248 passed" in both `ATT\logs\pytest_release_attempt5.txt` and `PIL\logs\pytest_run23.txt`, the junit summary in `ATT\logs\readiness_gate_v1.json`, and all dry-run, precondition and release-validation outputs are unverified claims. I checked only that they agree with the code as read.
- **Hashes.** I cannot compute SHA-256 values. The claims that the attempt is byte-identical to the pilot, and the hashes in `copy_verification_attempt5.csv`, `review_scope_attempt5.json`, `readiness_gate_v1.json` and `zz_code_changes_rev7_to_rev8.csv`, agree with each other. I could not check them against the files. I read the attempt's copies of the code, not the pilot's.
- **External code.** I did not inspect `r3_lib` or `rebuild`, so I cannot say whether `QSPlant.step` or `QSPlant` construction can raise in practice. This determines how likely R5-1 is.
- **Review brief.** The SHA-256 of `review_brief_attempt5_as_sent.md` is unverified.
