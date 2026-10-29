### 12.1 Since rev10 (complete list)

| Change | Basis | Effect |
|---|---|---|
| `campaign.run_condition`: when a run was attempted and raised (stage `run`), the pair is `NOT_EVALUABLE_CONDITION_ERROR` also where the pair evaluation gave `NOT_EVALUABLE_RUN_MISSING`; the earlier label goes to `qs_vs_dyn_pair_status_before_error`. In rev13 such a QS-eligible pair kept `NOT_EVALUABLE_RUN_MISSING`. `NOT_EVALUABLE_RUN_MISSING` stays for an executed run without a finite energy and no exception. Exceptions at other stages are unchanged | owner decision I-6b (2026-10-29) | label only; no outcome effect (NOT_EVALUABLE either way) |
| `campaign._na_pair_not_evaluable`, `fold_separate_recomputation`, `fold_failed`: the docstrings cite the owner's decision on the relabelling scope; the behaviour is unchanged from rev13 (only a `NOT_APPLICABLE_*` pair with an executed run is relabelled) | owner decision of 2026-10-29 (§1.16) | none |
| `campaign.fold_failed`: `conds` is indexed only within its length; a row without a matching condition is treated as executed (fail-closed), so the fallback cannot raise on the indexing | review R10-4 | robustness |
| `IMPLEMENTED_2` → `AMB_29_condition_error`: rewritten as the owner's I-6 ruling (its own words), the owner's decisions I-6b and on the relabelling scope (2026-10-29), the rules as applied (with RUN_INVALID after a recomputation or fold failure, and the NOT_EVALUABLE labels that remain applicable), and one sentence labelled "Implementer reading (not an owner ruling)" | review R10-1; owner decisions of 2026-10-29 | — |
| `config/code_review_status_v12.json`: the R10 findings; the owner's decisions of 2026-10-29 in `owner_rulings_implemented`; the two former implementer readings in `implementer_readings_decided_by_owner`; one remaining implementer reading; `open_major` stays 6, with `owner_acceptance_of_major_closures` "not recorded"; `reviews_pending` names the review of release attempt 11 | reviews R10-1 to R10-4; owner decisions of 2026-10-29 | record |
| Text: header (R10-3: the counts of the attempt-10 findings stated exactly); §1.1 to §1.3 headings ("first stated in", R10-3) and the rev10 sentence moved out of the N-A2 ruling paragraph; §1.4, §1.6, §1.12, §1.14 (R10-1); new §1.15 and §1.16 (the owner's words); §2, §3, §7.8, §9, §12, §13, §15 | owner decisions of 2026-10-29; reviews R10-1, R10-3 | wording |
| Tests: new `tests/test_owner_decisions_v14.py`. Updated: `test_owner_decisions_v11.py` (I6EL and I6FL expect `NOT_EVALUABLE_CONDITION_ERROR`; one test renamed), `test_owner_rulings_v7.py` and `test_owner_rulings_v8.py` (the attempted-run exception cases expect `NOT_EVALUABLE_CONDITION_ERROR`), `test_review_fixes_v13.py` (the v11 status file and the rev10 candidate read by path; one test renamed) | owner decision I-6b; reviews R10-1 to R10-4; versioning | — |
| `DRAFT_AMENDMENT_2` → this candidate; `CAMPAIGN_CONFIG` → `campaign_config_v14_DRAFT.json`; `REVIEW_STATUS` → `code_review_status_v12.json` | versioning | — |

**Not changed:**
- the review notes R7-11 and R7-13 (optional hardening), V6-4 and R5-14, and the partly fixed R5-6 (§7.7);
- R8-11: `18_owner_decision_matrix_I1_I6.md` is the pre-ruling record and is not edited;
- R9-8: documented in §4.1; the code is unchanged;
- `checks.py` and `recompute_from_traces.py`.

**R10-2** is addressed by tests in `tests/test_owner_decisions_v14.py` whose first call works on the old code, and by the mutation runs in `logs/zz_mutation_check_*`.

The file-level comparison with the rev10 state (`archive/rev13_attempt10_20261029_0629/`) is `logs/zz_code_changes_rev13_to_rev14.csv`; the byte-level line-ending check is `logs/zz_line_endings_rev13_to_rev14.csv`.

### 12.2 Earlier changes

The changes from rev4 to rev5, and each later step up to rev9 to rev10, are listed in §12 of the rev5 to rev10 candidates, all kept unchanged.
