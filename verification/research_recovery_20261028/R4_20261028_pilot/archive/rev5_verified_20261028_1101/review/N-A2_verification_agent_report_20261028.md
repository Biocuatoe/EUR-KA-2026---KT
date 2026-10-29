# N-A2 fix verification: read-only reviewer report (verbatim)

**Date:** 2026-10-28.
**Reviewer:** read-only review agent a6d24bd6ca8c2b9fd. It is the same agent that wrote `N-A2_review_agent_report_20261028.md`, resumed with its context, and it used Read, Grep and Glob only.
**State reviewed:** the pilot source after the R3-1 to R3-11 fixes, archived unchanged in `archive/rev4b_reviewed_20261028_1051/`, with draft rev1 (`a936023a…`).

The reviewer's text below is unchanged. The author's handling of each item is in `14_amendment2_release_readiness_report.md` §6.

---

Re-verification of R3-1 to R3-11 in the current pilot source (read-only)

I used Read, Grep and Glob only; I ran nothing and wrote nothing. PIL = `D:\EURÉKA 2026 - KT\verification\research_recovery_20261028\R4_20261028_pilot`. Short names mean files under PIL: `checks.py` and `campaign.py` are in `PIL\code\r4h3\`, `T_A2` is `PIL\code\tests\test_amendment2.py`, `T_C` is `PIL\code\tests\test_campaign.py`, `DRAFT2` is `PIL\03_protocol_v1_amendment_2_DRAFT.md` (rev1), and `02b` is `PIL\02b_protocol_ambiguity_register_addendum_amendment2.md`.

**Summary:** 8 of the 11 findings are fixed and 3 are partially fixed (R3-6, R3-7, R3-10). I found 2 new defects, both NOTE level. The most important open item: there is still no complete, clean test run of the current code.

## Verdict per finding

| ID | Verdict | Evidence |
|---|---|---|
| R3-1 | **FIXED** | The location check now compares resolved paths: `frozen.PILOT.resolve() != CAMPAIGN_DIR.resolve()` (`campaign.py:539-542`). `T_A2:239-244` puts a same-named copy in a temporary directory. The old name-only check would have let that copy through, so the test does tell the two rules apart. `frozen.py` itself is unchanged. |
| R3-2 | **FIXED** | A FAIL is now tested among the arms that have an energy before the missing-energy test (`checks.py:122-133`). The reason text records the missing arm (`checks.py:124`). Tested at `T_A2:198-200`. |
| R3-3 | **FIXED** | There are now separate labels for undefined QS energy and for a condition error (`checks.py:50-54`, `134-137`). A condition-level exception gets `qs_eligible_pair=None` (`campaign.py:843`). An exception during the pair evaluation is handled the same way (`campaign.py:736`). The four eligibility classes now add up to the planned pairs (`checks.py:183-187`). Tested at `T_A2:101-102`, `203-223`. |
| R3-4 | **FIXED (documented)** | The literal reading is kept and disclosed as AMB-31, with its "can be favourable" direction (`DRAFT2:95`, `02b:14`). It is also a machine-readable key (`campaign.py:313-314`). PASS pairs that are also dynamic-valid are counted separately (`checks.py:151-153`, `191-192`). |
| R3-5 | **FIXED** | `qs_piece_diagnosis` (`checks.py:57-91`) re-implements `r3_lib` `QSPlant.point` term by term and records, per integration node, which of the three checks failed: drive torque, battery discriminant, discharge current. `consistent` compares the result with `plant.step` on the same piece. The record is kept in `conditions/<id>.json` → `qs_screen_failures` (`campaign.py:851`) and summarised in the warning string (`campaign.py:745-747`). A diagnosis error is recorded, never raised (`checks.py:99-103`). Tested on a real QS failure at `T_A2:226-236`. |
| R3-6 | **PARTIALLY FIXED** | Fixed: the location rule (`DRAFT2:125-129`), the AMB table with a direction column (`DRAFT2:88-95`), the amendment 1 §10 ambiguity (`DRAFT2:94`), the authorisation keys and scope (`DRAFT2:156`), and the integrity-file note, now worded as future (`DRAFT2:11`). Residual: `DRAFT2:146` still says "No other behaviour changes", but the change list at `DRAFT2:131-144` omits three changes: a failed config rebuild now becomes a blocker (`campaign.py:476-483`), `config_content` now uses fixed path strings (`campaign.py:384`, `393`, `396`), and new defect R3-12. |
| R3-7 | **PARTIALLY FIXED** | New tests cover the amendment-2 precondition branches (`T_A2:262-277`), the same-named copy (`T_A2:239`), condition errors (`T_A2:216`) and FAIL with a missing arm (`T_A2:198`). The static no-write check now covers 5 names (`T_C:116-118`). Residual: (a) **no complete clean run of the current code** (`pytest_run17`: 6 failed, 205 passed; `pytest_run18.txt` is incomplete, 37 dots); (b) the blocker for an issued amendment 1 with the wrong hash (`campaign.py:506-507`) is never exercised, because case kw1 tests a wrong key in amendment 2's block instead; (c) the R3-9 exception path has no test; (d) the assert for the missing approval record (`T_A2:265`) would also be satisfied if amendment 1's approval record went missing. |
| R3-8 | **FIXED** | The scope now reads "…amendments 1 and 2" (`campaign.py:70`). The draft names `scope`, `amendment_sha256`, `amendment_2_sha256` and `pre_run_hashes_sha256` (`DRAFT2:156`). |
| R3-9 | **FIXED** | The pair evaluation is wrapped in `try/except`. An exception is recorded in `errors.csv` and the pair is labelled `NOT_EVALUABLE_CONDITION_ERROR`; executed runs keep their rows (`campaign.py:722-737`). Lines 738-747 remain outside the `try`, but they are trivial dictionary and string operations. There is no test. |
| R3-10 | **PARTIALLY FIXED** | Fixed: an unknown status now raises (`checks.py:147-149`); the labels are renamed to `NOT_APPLICABLE_*` / `NOT_EVALUABLE_*` with a stated label rule (`checks.py:46-54`); the ambiguity register addendum exists (`02b`); AMB-30 is a machine-readable key (`campaign.py:312`). Not changed: `P3_RULE` "QS screen diagnostic only" (`checks.py:26`). It cannot change without breaking amendment 1's `AMB_24` value, and the draft does not say that the screen now also decides whether §9 applies. New issue: see R3-13. |
| R3-11 | **FIXED** | The JSON round-trip comparison is declared, with no effect on current values (`DRAFT2:140`). |

## New defects

**R3-12 — NOTE — `checks.py:125-126`: an M2 pair with a missing dynamic energy is now `REPORTED_ONLY`; rev0 labelled it `NOT_EVALUABLE_RUN_MISSING`.**
- **Conflict:** the documented rule says every QS-eligible pair with an arm that has no finite energy is `NOT_EVALUABLE_RUN_MISSING` (`DRAFT2:91`, `02b:10`). The change is not in the list at `DRAFT2:131-144`.
- **Effect:** no branch outcome changes, because M2 is reported only. But `qs_check_reported_only` now counts M2 pairs that have no value to report.
- **Remedy:** label it `NOT_EVALUABLE_RUN_MISSING` for M2 too (the branch stays REPORTED_ONLY), or document the M2 exception.

**R3-13 — NOTE — the new raise in `branch_qs_dynamic_outcome` (`checks.py:147-149`) would cut the run accounting short.**
- **Where:** it is called at `campaign.py:892`, after `conditions.csv` is written but before `qs_dynamic_*.csv`, `stop_compliance.csv`, `errors.csv`, `recomputation.json`, `manifest.json` and `zz_post_run_sha256.csv`.
- **Effect:** if it ever triggered, those files would not be written (protocol 10.4).
- **Likelihood:** it cannot trigger today, because every code path sets a status from the fixed list (`checks.py:116-138`, `campaign.py:736`, `843`).
- **Remedy:** catch the error, record it, write an ERROR/INCONCLUSIVE outcome, and finish writing the outputs.

## Other checks
- **Machine-readable block:** it equals `IMPLEMENTED_2` key for key and value for value. The 21 keys in `campaign.py:292-317` match `DRAFT2:173-212`; `amendment`, `status` and `note` are skipped by the reader.
- **`config\campaign_config_v4_DRAFT.json`:** it exists and contains the new keys. Whether it is byte-current with the code is not verified.
- **`config\code_review_status_v4.json`:** it is absent, so campaign mode is blocked (fail-closed).
- **Release folder:** it still holds only amendment 1, its approval record and the issue diff.
- **Write sites:** no new ones in `campaign.py`, `checks.py` or `frozen.py`.
- **Unchanged files:** `evaluator.py`, `closedloop.py`, `sensitivity.py`, `recompute_from_traces.py`, `record_gate.py`, `record_readiness_gate.py`, `run_campaign.py` and `frozen.py` have the same line counts and key lines as before; I did not compare them byte for byte. The schedule code (`campaign.py:112-155`) and `classify_pair` / `paired_delta` (`checks.py:265-292`) are unchanged.

## One-line re-confirmations
- **CR-A2:** still closed. `classify_pair` takes no QS input, and arms are gated only by whether their profile exists (`campaign.py:692-698`). QS results affect only whether §9 applies.
- **CR-A6:** still mitigated with the accepted residual. The evaluator, the separate recomputation and the fold into crediting (`campaign.py:770-788`, `883-887`) are unchanged, and the limit diagnostics still do not gate crediting (`evaluator.py:334`, `342`).
- **Torque limits:** still independent and equivalent. `evaluator.py` imports only `json`, `Path` and `numpy`, and its torque-limit code is unchanged. The new `qs_piece_diagnosis` uses `r3_lib`/`rebuild` in the simulator process only. It is a diagnostic, it is not imported by the recomputation script, and it is not part of the independent evaluator.
- **Fail-closed:** **YES.** Every listed precondition is enforced, including the location check by resolved path, and no code writes an owner document.
- **Amendment 2 draft:** **not yet ACCURATE.** The remaining errors are minor: the "No other behaviour changes" claim (R3-6 residual) and the M2 rule (R3-12). The machine-readable block is exact.
