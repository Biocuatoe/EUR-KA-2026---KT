# R4 H3: remaining owner rulings implemented; release attempts 5 and 6 (report 17)

**Date:** 2026-10-28. **Status: CAMPAIGN BLOCKED.**
- Amendment 2 is a draft: it is neither approved nor issued.
- No campaign authorisation exists. Campaign mode was not invoked.
- No official run ID was executed, and no energy difference between arms was computed.

This task implemented the owner's rulings on AMB-29(b), (c), (d), AMB-30 and AMB-32, and kept the earlier rulings (N-A2, AMB-29(a), AMB-31). It ran an independent review and stopped after preparing the release attempts.

## 1. Attempt directories

| Attempt | Path | Code | Candidate | Status |
|---|---|---|---|---|
| 5 | `R4_20261028_campaign/release_attempts/attempt5_owner_rulings/` | rev8 | rev5 | **reviewed: 2 MAJOR findings open.** Kept unchanged as reviewed |
| **6** | `R4_20261028_campaign/release_attempts/attempt6_review_fixes/` | rev9 | rev6 | **reviewed and verified: no CRITICAL or MAJOR finding open in the code.** MINOR findings open (§5). The final attempt of this task |

Attempt 6 exists because the review of attempt 5 found MAJOR findings, and the task requires those fixes in a new attempt. Attempts 1–4 are unchanged.

## 2. Verified hashes

| Item | SHA-256 |
|---|---|
| Frozen protocol v1 (`R4_20261028_preflight/03_R4_protocol_v1.md`) | `f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab` |
| Issued amendment 1 (`R4_20261028_campaign/release/03_R4_protocol_v1_amendment_1.md`) | `7720fed75bb678e47a229d00aff154e0aa14607c051f4a1163cc9bf67b6abee2` |
| Amendment 1 approval record | `03f835e9311410095e4447840ecb2b02d95c50279527df5fdf2f6d334e15eecd` |
| **Amendment 2 candidate rev6** (`03_protocol_v1_amendment_2_rev6_CANDIDATE.md`), DRAFT — NOT APPROVED FOR RELEASE | **`0dcb767e97e19f40c00735d9efaecf8d21c396c23952b70e60ccb21a3f711e1f`** |
| Candidate rev5, superseded and unchanged | `e7ba73c11784b3cf38f48e32b69a7a7c21b070d039118547d638bc1bf06d4f5f` |
| Candidate rev4, unchanged | `c726560d1e87036cbd94fe58724cafdc1e4746647f6cfacbb320f3e14ed143ab` |
| Draft rev3, unchanged; rev0–rev2 present unchanged in the archive | `fdaf193de510488733f0e0899d50def86cbeafabdbecdd3bc7a144099b6f492c` |

The protocol, amendment 1 and its approval were checked at the start (`logs/zz_start_state_v7.json`), at each gate record, and at the end (`logs/zz_integrity_v7_post.json`). Each candidate's hash is also recorded in its `.sha256.txt`. Candidate rev6 lists both parents in full.

## 3. The owner's rulings and where they are implemented

References are to the attempt-6 code (`code/r4h3/`).

| Ruling | Implementation |
|---|---|
| **AMB-29(a)** (kept): a missing profile | an explicit `PROFILE_UNAVAILABLE` / `BASELINE_UNAVAILABLE` status (`checks.classify_pair`). The pair's check is `NOT_APPLICABLE_PROFILE_UNAVAILABLE`, which now takes precedence over a failed screen of the other profile (`checks.pair_qs_dynamic`, :136). Counted in `feasibility_accounting` (:458) and `h3_verdict_eligibility` (:512) |
| **AMB-29(b)**: missing or invalid energy → NOT_EVALUABLE → INCONCLUSIVE | `NOT_EVALUABLE_RUN_MISSING` / `NOT_EVALUABLE_RUN_INVALID` (`pair_qs_dynamic`). The QS check uses an arm only if it passes §8.2 and both recomputations (`campaign.run_condition`, :748; `fold_separate_recomputation`, :901). The paired endpoint needs a final `COMPARABLE` (`energy_role`, :445). Traces kept. One record per planned run (`record_invariant`, campaign.py:1028) |
| **AMB-29(c)**: QS energy ≤ 0 → INCONCLUSIVE for the QS criterion | `qs_vs_dynamic` (:301) computes no percentage, keeps the raw values and names the term (`non_positive_term`, :78). The pair is `NOT_EVALUABLE_QS_UNDEFINED`. The condition status and energy role are unaffected; §8.2 still applies. `paired_delta` (:412), `scenario_totals` (:328), `grid_convergence` (:343) and `timestep_check` (:354) refuse a saving percentage with a non-positive or undefined input (reading I-3) |
| **AMB-29(d)**: evaluation error → INCONCLUSIVE | every exception is recorded in `errors.csv` with its stage and run IDs. A QS-screen, pair or reporting exception gives `NOT_EVALUABLE_CONDITION_ERROR`, and both dynamic arms still run (`run_condition`). A run-level exception keeps its trace (`retained_files`, :797). Nothing is retried or replaced. A failure in the separate recomputation or the fold fails closed (`execute_schedule`, :950; `fold_failed`, :936; `recompute_from_traces.py` exits 3 or 4) |
| **AMB-30**: strict | `checks.branch_qs_dynamic_outcome` (:201). A FAIL or a `NOT_EVALUABLE_*` pair in any set makes the branch INCONCLUSIVE; counts are per set, never averaged. The required PASS must come from the held-out nominal set NOM, and a PASS in INS or any other set never substitutes. A nominal cell that is absent, duplicated, without a profile or not evaluable blocks PASS. So does a planned pair missing from the record |
| **AMB-31** (kept): invalid energy is diagnostic only | `energy_roles.csv` roles (`checks.energy_role`); `qs_vs_dyn_pct_diagnostic_invalid_run` |
| **AMB-32**: a missing nominal cell → INCONCLUSIVE, never NOT SUPPORTED | `checks.h3_verdict_eligibility` (:512). NOT SUPPORTED needs all six nominal cells `COMPARABLE`. Each missing cell is recorded with its status and reason (`nominal_missing_evidence`, `_missing_evidence` :503) |

Candidate rev6 states each ruling with the owner's words (§1), the status vocabulary (§2), the difference between a QS-only status and an invalid run (§3), energy roles and non-positive denominators (§4), the branch rule (§6), denominator and exclusion reporting (§7) and the verdict (§8). The 170-run schedule is unchanged (§10).

**Interpretation points for the owner (candidate §9).** These are readings where the rulings' words leave a choice. The code implements each one; approving rev6 confirms them.
- **I-1:** the required nominal PASS is at least one of the motor's two NOM cells. A QS-infeasible NOM cell is not missing evidence. **The alternative, every NOM cell must PASS, is stricter.** The owner is asked to state I-1 explicitly.
- **I-2:** a NOM cell without a profile blocks PASS.
- **I-3:** the non-positive-denominator rule covers every relative saving percentage.
- **I-4:** the QS check needs both recomputations.
- **I-5:** "QS_COMPARISON_NOT_EVALUABLE" is the `NOT_EVALUABLE` class.
- **I-6:** an exception inside a run leaves a QS-eligible pair `NOT_EVALUABLE_RUN_MISSING`.

The verification found one more inaccuracy in how rev6 describes these points (V6-3, §5).

## 4. Tests

Every log is kept in `logs/` or the attempt's `logs/`, failed runs included.

| Run | Tree | Result | Note |
|---|---|---|---|
| 23a, targeted (`pytest_run23a_targeted_existing.txt`) | pilot rev8 | 58 passed, **10 failed** | expected before rev5 existed. 8 failed because the candidate file was missing. 2 (`test_case11`, `test_r3_3`) encoded the superseded all-sets AMB-30 reading, so their fixtures and assertions were updated |
| 23b, targeted (`pytest_run23b_targeted_v8.txt`) | pilot rev8, new v8 file | 17 passed, **2 failed** | both needed the rev5 candidate, written afterwards |
| **23** (`pytest_run23.*`) | pilot rev8 | **248 passed, 0 failed** | readiness gate v9 |
| attempt 5 (`pytest_release_attempt5.*`) | copy | **248 passed, 0 failed** | |
| 24a, targeted (`pytest_run24a_targeted_v9.txt`) | pilot rev9, new v9 file | 10 passed | |
| **24** (`pytest_run24.*`) | pilot rev9 | **258 passed, 0 failed** | readiness gate v10 |
| **attempt 6** (`pytest_release_attempt6.*`) | copy | **258 passed, 0 failed** | attempt readiness gate v1 |

**New tests:**
- `test_owner_rulings_v8.py`, 19 tests: the rulings, including the 13 requested situations;
- `test_review_fixes_v9.py`, 10 tests: the review fixes.

**Changed tests**, each documented in candidate rev6 §12:
- `test_amendment2.py`: `test_case11` and `test_r3_3` changed under AMB-30. `test_case2`, `test_amb29` and `test_r3_3` got fuller fixtures under R5-10.
- `test_owner_rulings_v7.py`: two fixtures under R5-10, plus the candidate-name check.
- `test_owner_rulings_v8.py`: the candidate-name check.

No threshold was changed, and no assertion was weakened (the reviewer confirmed both).

## 5. Independent review

**Reviewer: one separate AI review agent** ("Plan" type, with no Edit or Write tools; Read, Grep and Glob only). **It is not a human independent audit.** It read the attempt directories directly. Its briefs and reports are saved verbatim, together with a hash record of the state it read (`review/` of each attempt; copies in `review/` here).

| Round | Report | CRITICAL | MAJOR | MINOR | NOTE |
|---|---|---|---|---|---|
| review of attempt 5 | `review/R5_attempt5_review_agent_report_20261028.md` | 0 | **2** | 10 | 3 |
| verification of attempt 6 (new findings) | `review/V6_attempt6_verification_agent_report_20261028.md` | 0 | 0 | 3 | 2 |

**The two MAJOR findings, both verified FIXED in attempt 6:**
- **R5-1:** an exception in the QS screen or in the post-run reporting became a condition-level ERROR and relabelled valid dynamic runs.
- **R5-2:** a nominal cell without a profile, whose other profile failed the QS screen, did not block a branch PASS.

**Earlier findings.** R5-3, R5-4, R5-5, R5-7, R5-8, R5-9, R5-10 and R5-11 are verified FIXED. R5-6 is only partly fixed. R5-12 was open at verification time; this report is the record it cites, so it is now resolved. R5-13 is stated in the draft, and R5-14 is unchanged as documented.

**Still open (MINOR; none affects a status, denominator, outcome or verdict):**
- **V6-1:** an exception while `recompute_from_traces.py` imports its modules or reads its arguments exits with 1. The outcome is fail-closed (no CSV, so every run is unconfirmed), but nothing is written to `errors.csv`, contrary to the stated exit-code rule.
- **V6-2:** candidate rev6 omits that a classification exception makes the condition ERROR. It says "PASS or FAIL" where REPORTED_ONLY is also relabelled, and a blank line splits the §4.2 table.
- **V6-3:** candidate rev6 §9 calls I-2 to I-6 the stricter readings. I-5 makes no difference to any outcome, and I-6 has a stricter alternative for an ineligible pair.
- **R5-6, partly fixed:** a run whose evaluation raised is `executed=False`. Its simulator energy is only in its kept trace.

**Notes:** V6-4, V6-5 and R5-14 are optional.

**Recommendation:** fix V6-1 to V6-3 in the next code and candidate revision, before amendment 2 is issued. That needs a new attempt and another verification.

**Closure status.** The code has no open CRITICAL or MAJOR finding, by the reviewer's verification. **Formally the review is not closed.** `config/code_review_status_v7.json` was written before the verification and is part of the gate. It still counts `open_major` 2 and lists the verification and the owner's acceptance under `reviews_pending`, and both block. I did not lower these counts on my own word.

## 6. Schedule validation (no run executed)

The dry run and `logs/release_validation_attempt6.json` were produced from the attempt-6 copy. **All checks are true:**
- **170 runs:** NOM 12, P3 12, INS 12, CNV 6, SEN 128. All official run IDs are unique and in the official format.
- `schedule_170.csv` and `planner_jobs.csv` are byte-identical to attempt 2.
- **Smoke tests:** the smoke-test runs stay excluded.
- **Held-out S2:** S2 stays held out. Every S2 row is "held-out (protocol 3)", and S1 appears only in INS. There is no planner parameter-selection job, and the planner numerics equal the protocol.
- **Fixed gain:** the P1-designed gain is identical for all 32 sensitivity draws (compared array by array).
- **Separate vocabularies:** the QS and dynamic feasibility statuses are disjoint, and `classify_pair` reads no QS input.
- **Paired endpoint:** CONFIRMATORY is assigned only when a run is executed, §8.2-valid and confirmed, and its condition is `COMPARABLE` (an exhaustive table of 72 cases). `paired_delta` refuses every non-`COMPARABLE` status.
- **Reporting tests:** the tests for denominators, omission, invalid arms, exceptions and the review fixes all passed in the attempt's own junit record.
- **Legacy figures:** no legacy percentage is a target or a threshold. The scan for 12.5, 15.3, 2.1, 2.8, 10.3 and 5.3 found 12 hits; each is a protocol section reference (10.3, 2.1, 5.3), inspected by hand. The acceptance constants equal the protocol values.

## 7. Manifests

| Manifest | SHA-256 | Files | Self-exclusion |
|---|---|---|---|
| **`attempt6_review_fixes/zz_sha256_manifest_attempt6.csv`** | **`b19ddce7373aff8e02ae854986f3107355ea244a05e0a4b62831623b96ad4c3a`** | 87 | excludes itself (`zz_sha256_manifest_attempt6.README.md`); its hash is in `logs/zz_campaign_attempt6_manifest_sha256.txt` |
| `attempt5_owner_rulings/zz_sha256_manifest_attempt5.csv` | `c32601c33365dc5c06f563d0ccec01c483208809499d87f3f2d7d944a4f3ca00` | 84 | same scheme (`logs/zz_campaign_attempt5_manifest_sha256.txt`) |
| pilot `zz_sha256_manifest_v7.csv` | in `logs/zz_manifest_v7_sha256.txt` | see the README | written after this report; excludes itself and its hash record |

The gate records are `GATE_RECORD_attempt5.json` (`d696aa8e…`) and `GATE_RECORD_attempt6.json` (`7d4c6026…`).

## 8. Remaining blockers and approval status

Amendment 2 is **not approved and not issued**. Campaign mode refuses, with six blockers in `attempt6_review_fixes/logs/preconditions_attempt6.json`:
1. no issued amendment 2;
2. no protocol §10.1 gate for this code;
3. no `campaign_authorization.json`;
4. not running from the campaign root;
5. `code_review_status_v7.json` counts 2 major findings;
6. the verification and the owner's acceptance of the review closure are pending.

**The owner's next steps:**
1. Decide whether to accept the AI-agent review and verification, or to require a human review.
2. Decide on the readings I-1 to I-6, I-1 in particular.
3. Decide whether V6-1 to V6-3 must be fixed before issue. Recommended: yes.

**What follows those decisions:**
- a revised review-status file, a new gate and a new attempt;
- issue of the final candidate as `release/03_R4_protocol_v1_amendment_2.md`, with `amendment_2_approval.json`;
- an owner-approved promotion procedure: the campaign root still holds attempt 2, whose §10.1 gate cannot be overwritten;
- the owner's separate authorisation.

## 9. No official run and no arm-to-arm energy comparison

| Item | Result |
|---|---|
| `campaign_authorization.json` | absent; no code path writes it (checked by a test and by the reviewer) |
| Campaign mode | not invoked; `run_campaign()` never called; no official run ID executed; no `outputs/` in the campaign directory or the attempts |
| Arm-to-arm energy | no difference computed or reported. The development tests run only development IDs on toy cycles. The pure-rule tests use synthetic numbers and assert only refusals or labels |
| S2 | not used for tuning |

## 10. Protected files and prior attempts

The full results are in `logs/zz_integrity_v7_post.json` and `logs/zz_pre_post_comparison_v7.txt`.

| Item | Result |
|---|---|
| Project outside the pilot (25,188 files at the start) | 173 added, **all inside attempts 5 and 6** (85 + 88, including each manifest); **0 changed, 0 removed** |
| Attempts 2, 3, 4 | manifests verify: 122, 73 and 76 files; no unlisted file |
| Attempts 5 and 6 | manifests verify: 84 and 87 files; no unlisted file |
| Preflight | 29/29 rows; no file added, removed or changed |
| Evidence snapshot | manifest `A93EB44F…` matches; 570/570 rows pass (snapshot copies only; `D:\EUREKA` not accessed) |
| Protocol v1, amendment 1 and its approval; drafts rev0–rev5 | unchanged |
| Pilot history | of the 654 files in manifest v6, only the live `campaign.py`, `checks.py`, `recompute_from_traces.py`, `test_amendment2.py` and `test_owner_rulings_v7.py` changed. Their earlier versions are archived in `archive/rev7_attempt4_20261028_1405/` and `archive/rev8_attempt5_20261028_1540/`. Every new file has a versioned name |
| Thesis, R1–R3, CNTT-02 | not touched |

## Deviations and errata

- **Erratum, R5 provenance:** the header of the saved attempt-5 review report gives the delivery time as "about 15:55". The real time was about 15:34. The report is hashed into attempt 5's records, so it was not edited; the correction is `review/R5_attempt5_review_agent_report_20261028.ERRATUM.md`.
- **Reviewer interruption:** the reviewer stopped once on a service rate limit and was resumed with its own context. The interruption and resumption are recorded in both reports' provenance headers.
- **Text-editing slip:** one Bash heredoc mangled the backslashes of a text edit to the review brief and failed with an assertion error before writing anything. The edit was then made with the Edit tool.
- **Rules kept:** no Git, installs, downloads or network were used in this task.
