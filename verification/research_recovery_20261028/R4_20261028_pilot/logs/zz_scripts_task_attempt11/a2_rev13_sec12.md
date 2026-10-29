### 12.1 Since rev12 (complete list)

| Change | Basis | Effect |
|---|---|---|
| `IMPLEMENTED_2` → `AMB_29_condition_error`. The owner-ruling and owner-decision clauses hold only the owner's sentences: I-6 in its own words; I-6b without the "an executed run without a finite simulator energy" gloss; the scope decision. The "As applied" clause names the case of a pair with no executed run and reports execution validity and recomputation validity separately. The implementer reading has three parts: (a), which can change an outcome; (b); and (c), the "genuinely absent run" mapping, moved out of the I-6b clause | reviews R11-1 (MAJOR), R11-3, R11-9 | wording; no status or outcome change |
| `IMPLEMENTED_2` → `AMB_30_branch_scope` (I-1) and `AMB_31_energy_of_invalid_runs` (I-4): the owner-ruling sentences hold the owner's words. The implementation details follow under "As implemented": a duplicated cell or a cell without a profile counts as missing evidence; the in-process recomputation is also required (AMB-31) | review R11-9 | wording; no status or outcome change |
| `campaign.run_condition`: the reason text cites owner decision I-6b only for a QS-eligible pair | review R11-8 | reporting |
| `campaign.fold_separate_recomputation`: a length mismatch between condition rows and conditions raises, instead of leaving extra rows unfolded. The executor then applies `fold_failed`. Unreachable with the executor's inputs, which are one to one | review R11-6 | robustness; fail-closed |
| `config/code_review_status_v14.json`: the R11 findings; `open_major` 7 (R11-1 added, not yet verified; nothing lowered; no owner acceptance recorded); R8-1 notes the rev14 label; R10-1 recorded as partly fixed in rev14 and completed in rev15; the R10-2 record corrected for I6FL; the implementer reading in three parts | reviews R11-1 to R11-9 | record |
| Text: header; supersedes and review rows; §1.14 ("As applied" and the implementer reading); §1.15 (the owner's words in full, including "Do not perform a broad label rewrite.", review R11-2, and the "genuinely absent run" line attributed to reading (c)); §2 (`NOT_EVALUABLE_RUN_MISSING` row); §9; §12; §13. The decision record states that report 21 is written after the review of release attempt 12 (review R11-5) | reviews R11-1 to R11-5, R11-9 | wording |
| Tests: new `tests/test_owner_decisions_v15.py`. Updated `test_owner_decisions_v14.py`: the R10-1 test expects the owner's sentences in the I-6b clause and reading (c), review R11-1; the R10-3 header check is pinned to rev12; the v13 status and rev12 candidate are read by path; the blocking test reads the live count (versioning). Updated `test_review_fixes_v13.py`: the stale comment (review R11-7) and the live count (versioning) | reviews R11-1, R11-4, R11-7; versioning | — |
| `DRAFT_AMENDMENT_2` → this candidate; `CAMPAIGN_CONFIG` → `campaign_config_v15_DRAFT.json`; `REVIEW_STATUS` → `code_review_status_v14.json` | versioning | — |

**Not changed:**
- the behaviour of the I-6b override and of the fold-scope rule, which the review of release attempt 11 confirmed;
- `checks.py` and `recompute_from_traces.py`;
- R11-6 (a): a direct call of the folds without the executed run IDs still treats every N/A pair as executed (fail-closed), and the `fold_failed` call is still unguarded; both are unreachable from the executor and documented (§1.16).

The file-level comparison with the rev12 state (`archive/rev14_attempt11_20261029_0807/`) is `logs/zz_code_changes_rev14_to_rev15.csv`. The byte-level line-ending check is `logs/zz_line_endings_rev14_to_rev15.csv`, with the diff in `logs/zz_diff_rev14_to_rev15.txt`. For the rev10 to rev12 step, the final lists are the `_final` files of `logs/zz_code_changes_rev13_to_rev14*` (review R11-5).

### 12.2 Earlier changes

The changes from rev4 to rev5, and each later step up to rev10 to rev12, are listed in §12 of the rev5 to rev10 and rev12 candidates, all kept unchanged.
