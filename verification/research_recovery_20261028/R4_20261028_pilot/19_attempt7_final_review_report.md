# R4 H3: owner ruling I-1, fixes of the attempt-6 verification, and release attempt 7 (report 19)

**Date:** 2026-10-28.

**Status: CAMPAIGN BLOCKED; RELEASE BLOCKED.** The owner decisions I-2 to I-6 are open, and the code blocks on them.
- Amendment 2 is a draft. Candidate rev7 is marked NOT ISSUABLE.
- No campaign authorisation exists, and campaign mode was not invoked.
- No official run was executed, and no energy difference between arms was computed.

This report covers items 1–9 of the task "Final Amendment 2 Decisions and Release Attempt 7". The decision matrix for I-1 to I-6 is `18_owner_decision_matrix_I1_I6.md`.

## 1. Attempt 7 and its manifest

| Item | Value |
|---|---|
| Directory | `R4_20261028_campaign/release_attempts/attempt7_final_review/` (new; the name was free at the start, see `logs/zz_start_state_v8.json`) |
| Manifest | `zz_sha256_manifest_attempt7.csv`, 90 files, SHA-256 **`42e8c88f35edd49e206354173a79925050eae395a52b04a5fba7675f32a1f933`** |
| Self-exclusion | the manifest excludes itself. Its hash is in `logs/zz_campaign_attempt7_manifest_sha256.txt`; the rule is in `zz_sha256_manifest_attempt7.README.md` |
| Gate record | `GATE_RECORD_attempt7.json`, SHA-256 `1c87e6aa847f81189a69e3d7df2e4ceb922e36c2981e95dd7d7ab6a9eab29893`. No gate criterion is met |
| Code | rev10: `checks.py`, `campaign.py`, `recompute_from_traces.py`; changes in `logs/zz_code_changes_rev9_to_rev10.csv`; rev9 archived in `archive/rev9_attempt6_20261028_1727/` |

## 2. Tests from the copied release tree

| Run | Tree | Result | Log |
|---|---|---|---|
| 25a, targeted | pilot, new v10 file | 14 passed, **1 failed**. A test defect: the helper `_r()` had a parameter `status` that collided with a keyword argument. Fixed in the test | `logs/pytest_run25a_targeted_v10.txt` |
| 25b, targeted | pilot, the fixed test | 2 passed | `logs/pytest_run25b_targeted_v10_fixed.txt` |
| **25**, full | pilot rev10 | **273 passed, 0 failed, 0 errors** → readiness gate v11 | `logs/pytest_run25.*` |
| **attempt 7**, full | **the copied release tree** | **273 passed, 0 failed, 0 errors** → the attempt's readiness gate v1 | `attempt7_final_review/logs/pytest_release_attempt7.*` |

273 is 258 + 15 new tests. Every earlier test log is kept, including the failed runs.

## 3. Owner ruling I-1: implementation and regression tests

**The rule.** For M0 and M1, the required nominal cells are the protocol §8.1 nominal S2 P1 cells: NOM with L-R1 and NOM with L-EVE. Each must individually PASS.
- **Not a PASS:** an absent, duplicated, `NOT_APPLICABLE_*`, `NOT_EVALUABLE_*` or REPORTED_ONLY cell; a cell whose condition has no profile; and a PASS label on a condition that is not `COMPARABLE`. Each makes the branch INCONCLUSIVE.
- **FAIL** keeps the frozen §9 consequence.
- **S1 and every other set** never substitute.
- **M2** stays reported only.
- **Unchanged:** no threshold, condition status, energy role or denominator changes. A QS-infeasible nominal cell keeps its dynamic status.

**Where it is enforced:**
- `checks.branch_qs_dynamic_outcome`;
- `checks.h3_verdict_eligibility`, which checks it again from the rows (`qs_vs_dynamic_nominal_cells`), independently of the branch outcome;
- `qs_dynamic_branch_outcomes.csv` (columns `required_nominal_cells`, `n_required_nominal_cells`, `n_PASS_nominal`) and `h3_verdict_eligibility.json`;
- `NUMERICAL_CHECKS` row 7, `IMPLEMENTED_2` (`I_1_required_nominal_cells`, `AMB_30_branch_scope`), and candidate rev7 §1.9, §2, §3, §6 and §8.

**Regression tests** (`tests/test_owner_ruling_i1_v10.py`):

| Case the owner listed | Test |
|---|---|
| every required nominal S2 cell passes | `test_i1_every_required_nominal_s2_cell_passes`: branch PASS; verdict still possible |
| one nominal cell fails, the others pass | `test_i1_one_nominal_cell_fails_while_the_others_pass`: INCONCLUSIVE, FAIL counted per set; verdict blocked |
| one nominal cell missing | `test_i1_one_nominal_cell_missing`: absent and duplicated cells; planned row missing; verdict recheck |
| one nominal cell invalid or unevaluable | `test_i1_one_nominal_cell_invalid_or_unevaluable`: every `NOT_EVALUABLE_*` label, an invalid condition, and a PASS label on an `ERROR` condition |
| one nominal cell NOT_APPLICABLE | `test_i1_one_nominal_cell_not_applicable_and_qs_and_dynamic_feasibility_stay_distinct`: both N/A labels give INCONCLUSIVE. Executor check: a QS-infeasible nominal pair stays `COMPARABLE` |
| S1 passes while nominal S2 is missing or fails | `test_i1_an_s1_pass_never_substitutes_for_missing_or_failed_nominal_s2_evidence` |
| no pass by omission, or by treating NOT_APPLICABLE as PASS | `test_i1_no_branch_passes_by_omission_or_by_treating_not_applicable_as_pass`: all 10 × 10 combinations of the two nominal cells give PASS only if both are PASS. With forged branch outcomes, the verdict recheck allows SUPPORTED or NOT SUPPORTED only if every M0/M1 nominal cell is PASS |
| reporting layer | `test_i1_is_in_the_reporting_layer` (executor level) |

**Earlier tests changed by the ruling** (listed in candidate rev7 §12.1):
- `test_amendment2.py`: `test_case11`.
- `test_owner_rulings_v8.py`: a NOM N/A cell now gives INCONCLUSIVE, and the omission loop now includes N/A.
- The verdict fixtures in `test_owner_rulings_v7.py` and `test_owner_rulings_v8.py` gained nominal QS statuses.

The reviewer confirmed that no assertion was weakened except the one noted under R7-7.

## 4. I-2 to I-6: exact wording, alternatives, recommendations

The exact rev6 wording of each point, every interpretation, the effects and the risks are in `18_owner_decision_matrix_I1_I6.md`. **None is decided.** In summary:

| ID | Provisional reading (implemented) | Alternative | Recommended | Can it change the verdict? |
|---|---|---|---|---|
| I-2 | outside NOM, a pair without a profile does not affect the QS criterion | it makes the M0/M1 QS criterion INCONCLUSIVE | provisional (I-2a) | yes |
| I-3 | no relative saving percentage is computed with a non-positive denominator (all of them) | the QS ratio only | provisional (I-3a) | yes, only in a degenerate case |
| I-4 | both recomputations must confirm an arm used by the QS check | the separate one only | provisional (I-4a) | yes |
| I-5 | `QS_COMPARISON_NOT_EVALUABLE` = the NOT_EVALUABLE class; keep the label `NOT_EVALUABLE_QS_UNDEFINED` | rename the label | provisional (I-5a) | no |
| I-6 | an exception inside a run: a QS-ineligible pair keeps `NOT_APPLICABLE_*` | the pair is `NOT_EVALUABLE_CONDITION_ERROR` | **the alternative (I-6b)**: needs a code change | yes, only for a QS-ineligible pair outside NOM |

No option changes a condition status, a denominator, a feasibility count or an energy role. **The release stays blocked until the owner decides each of I-2 to I-6.** The precise question for each is worded in report 18, §3.

## 5. The three MINOR findings of the attempt-6 verification

| Finding (V6 report) | Fix | Closure evidence |
|---|---|---|
| **V6-1:** an exception while `recompute_from_traces.py` imports its modules or reads its arguments exited 1 (a "result"), and nothing went to `errors.csv` | **Script:** imports and argument handling now run inside the guarded block, and a failure exits 4. **Runner:** the process's full output goes to `recomputation_independent_process.log`. Each of these is recorded in `errors.csv` with its stage, the exception and the log as `diagnostic_path`, plus one row per affected run ID: a launch failure, an exit other than 0 or 1, a missing or unreadable output, and an executed run missing from the output. The manifest records the problem. Behaviour stays fail-closed | tests `test_v6_1_a_start_up_failure_of_the_separate_script_exits_4` and `test_v6_1_every_start_up_or_output_failure_is_in_the_ledger_with_run_ids` (four cases); the reviewer: **FIXED** |
| **V6-2:** candidate wording. A classification exception was not stated, "PASS or FAIL" left out REPORTED_ONLY, and a table was split by a blank line | candidate rev7 §1.6 and §3 state the classification exception; the text says "PASS, FAIL or REPORTED_ONLY"; the §4.2 table is whole | test `test_rev7_candidate…` (no split table); the reviewer: **FIXED** |
| **V6-3:** candidate wording. §9 claimed that I-2 to I-6 were the stricter readings | §9 rewritten: I-1 decided; I-2 to I-6 open, each row naming which reading is stricter (I-5 changes no outcome) | the reviewer: **FIXED**, per row correct. A new inaccuracy in the same section is noted as R7-1 |

V6-5 (NOTE) is fixed in `config/code_review_status_v8.json`. V6-4 (NOTE) is unchanged, as documented.

## 6. Independent AI review of attempt 7

- **Reviewer:** a new, separate **AI review agent** ("Plan" type, no Edit or Write tools; Read, Grep and Glob only). **This was an AI review, not a human audit**, and no human independent audit has taken place.
- **Brief and scope:** the brief as sent and the hashes of the 63 reviewed files are in `attempt7_final_review/review/`.
- **Report, verbatim:** `review/R7_attempt7_review_agent_report_20261028.md` (also in the attempt's `review/`).
- **Verdict:** **CRITICAL 0, MAJOR 0, MINOR 7, NOTE 6.**
- **Confirmed by the reviewer:**
  - I-1 is enforced in every verdict and reporting path;
  - all required nominal cells are accounted for, including absent and duplicated rows;
  - no non-PASS state creates a PASS or a SUPPORTED / NOT SUPPORTED possibility;
  - S1 never substitutes;
  - FAIL keeps its frozen consequence and no threshold changed;
  - QS-infeasibility is never reclassified as dynamic infeasibility;
  - the recomputation logging is complete in substance and fail-closed;
  - both wording defects are fixed;
  - the machine block equals `IMPLEMENTED_2`;
  - I-2 to I-6 are genuinely open and block;
  - the runner stays blocked;
  - no code writes the authorisation;
  - the decision matrix quotes rev6 exactly.

**Open MINOR findings** (none affects a status, denominator, outcome or verdict):

| ID | What |
|---|---|
| R7-1 | candidate rev7 §9 says each of I-2 to I-6 changes only the QS label. I-3 does not: it decides whether a percentage is computed at all |
| R7-2 | `code_review_status_v8.json` keeps a sentence copied from v7 saying every owner decision has been made, while the same file lists I-2 to I-6 as open. **My error.** It has no effect, because the open decisions block |
| R7-3 | some `errors.csv` rows (fold, `conditions.csv`, accounting) have no `stage` or `diagnostic_path`; §7.6 overstates this |
| R7-4 | per-run ledger rows are written only for runs absent from the output. An exit outside {0, 1} after a complete output, or a run present but not recomputed, gives no per-run row. Those runs stay unconfirmed |
| R7-5 | the writes of `runs.csv`, `evaluation.csv`, `planner_checks.csv` and the final outputs are unguarded (pre-existing) |
| R7-6 | a stale comment at `checks.py:46` ("NOT_APPLICABLE_* never changes a branch outcome") |
| R7-7 | test gaps: the live v8 status blocking on `open_major`; unreadable output; an exit outside {0, 1} with a complete output |

**Notes:**
- R7-8: this report was cited before it existed; it was written after the review.
- R7-9: decision-matrix clarifications.
- R7-10 to R7-13: optional hardening.

**Recommendation:** fix R7-1 to R7-7 in the next code and candidate revision. That revision must come anyway once the owner decides I-2 to I-6, together with a new attempt and another review.

**Closure status:** the code has no open CRITICAL or MAJOR finding, by this AI review. **Formally, the review is not closed.** `code_review_status_v8.json` still counts `open_major` 2 (R5-1 and R5-2, verified fixed in attempt 6 but not accepted by the owner) and lists the review and the owner's acceptance as pending. I did not lower these counts.

## 7. Protocol and parent-amendment hashes

| Item | Expected | Verified | Where |
|---|---|---|---|
| Frozen protocol v1 | `f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab` | equal at start, at the gate record and at the end | `logs/zz_start_state_v8.json`, `GATE_RECORD_attempt7.json`, `logs/zz_integrity_v8_post.json` |
| Issued amendment 1 | `7720fed75bb678e47a229d00aff154e0aa14607c051f4a1163cc9bf67b6abee2` | equal (approval record `03f835e9…` also equal) | same |
| Candidate rev6 (the input) | `0dcb767e97e19f40c00735d9efaecf8d21c396c23952b70e60ccb21a3f711e1f` | the actual file equals its recorded value | `logs/zz_start_state_v8.json` |
| Candidate rev7 (new) | — | `0e3ef3112c979237e7079f176b21dd4f2ce682c7ab435f36f33321ffe67a5996`, recorded in `03_protocol_v1_amendment_2_rev7_CANDIDATE.sha256.txt`; parents listed in full | — |

## 8. Remaining blockers and exact release status

**Release status:** NOT RELEASABLE. Candidate rev7 is **DRAFT — NOT APPROVED FOR RELEASE — NOT ISSUABLE**. The campaign is **BLOCKED**.

`attempt7_final_review/logs/preconditions_attempt7.json` lists 16 campaign blockers:
- no issued amendment 2;
- no protocol §10.1 gate;
- no `campaign_authorization.json`;
- not running from the campaign root;
- owner decisions I-2 to I-6 open, listed twice: from the code (`OWNER_DECISIONS_OPEN`) and from the review-status file;
- `open_major` 2 (R5-1 and R5-2, verified fixed by AI agents; owner acceptance pending);
- the review closure pending the owner's acceptance.

**Decisions required from the owner, in order:**
1. **I-2 to I-6.** Each question is worded in report 18, §3.1–§3.5. The recommendations are I-2a, I-3a, I-4a, I-5a and I-6b.
2. **The AI reviews.** Whether to accept the AI-agent reviews and verifications (R5, V6, R7) as closing R5-1 and R5-2, or to require a human review.
3. **The MINOR findings.** Whether R7-1 to R7-7 must be fixed before issue. Recommended: yes, in the same revision as the decisions.

**What follows:**
1. **Revision.** Code rev11 implements the decisions (under the recommendations, only I-6b changes behaviour) and the R7 fixes. `OWNER_DECISIONS_OPEN` is emptied. A new review-status file records the decisions and the owner's acceptance.
2. **Candidate.** Candidate rev8 records the decisions; it is the first candidate that can be issuable.
3. **Release attempt.** A new release attempt follows, with its own review.
4. **Issue.** The owner issues amendment 2 with its approval record.
5. **Promotion and authorisation.** Promotion to the campaign root by an owner-approved procedure, then the owner's separate `campaign_authorization.json`.

## 9. Confirmations

| Item | Result |
|---|---|
| Official campaign run | none. Campaign mode was not invoked, `run_campaign()` was never called, and no `outputs/` directory exists in the campaign directory or the attempts |
| Arm-to-arm energy comparison | none computed or reported. The executor tests run only development IDs on toy cycles. The pure-rule tests use synthetic numbers and assert labels or refusals only |
| `campaign_authorization.json` | not created. Absent; no code path writes it, as a test and the reviewer confirm |
| Amendment 2 | not issued or approved. Rev7 is NOT ISSUABLE |
| S2 | not used for tuning. The schedule's SHA-256 is unchanged; S2 rows are held out; the planner numerics equal the protocol |
| 170-run schedule | revalidated without execution (`release_validation_attempt7.json`, all true). 170 unique official IDs; smoke tests excluded; the fixed P1 gain is identical for all 32 sensitivity draws; S2 held out; the schedule and planner jobs are byte-identical to attempt 2 |
| Protected files | the project gained **91 files, all inside attempt 7**; 0 changed, 0 removed (`logs/zz_integrity_v8_post.json`). The manifests of attempts 2–6 verify, with no unlisted files. The preflight is 29/29 and unchanged. The evidence snapshot is 570/570 (copies only; `D:\EUREKA` not accessed). Drafts rev0–rev6 and all earlier reports are unchanged. In the pilot, only the live code and test files changed; their rev9 versions are archived |
| Tools | no Git, no installs, no network, no CNTT-02 material |

**Slips in this task, both corrected before anything ran:**
- **Heredoc backslashes:** a Bash heredoc mangled the backslashes of a path literal in the integrity script. I fixed it with the Edit tool and checked the result before running it.
- **Generator search strings:** two generator scripts stopped on their own assertions before writing anything, because a search string did not match. I then wrote them directly.
