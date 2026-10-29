# R4 H3: owner ruling N-A2, amendment 2 draft and release-readiness package (report 14)

**Date:** 2026-10-28.
**Status: CAMPAIGN BLOCKED.**
- Amendment 2 is a **DRAFT — NOT APPROVED FOR RELEASE**.
- No campaign authorisation exists. Campaign mode was not invoked, no official run was executed, and no energy difference between experimental arms was computed.

This task stopped after preparing the draft and the readiness package, as instructed.

## 1. Old and new release-attempt paths

All paths are under `verification/research_recovery_20261028/`.

| Attempt | Path | Scope | State |
|---|---|---|---|
| 1 | `R4_20261028_campaign/release_attempts/attempt1/` | amendment 1 | failed (183/184, test defect); preserved |
| 2 | `R4_20261028_campaign/` root: `code/`, `config/`, `inputs/`, `logs/`, `release/` | amendment 1 only | **preserved unchanged**: manifest re-verified, 122/122 rows, no unlisted file other than attempt 3 below |
| **3 (new)** | `R4_20261028_campaign/release_attempts/attempt3_amendment2/` | amendments 1 and 2 (draft) | readiness package; not a release; no protocol §10.1 gate |

## 2. Hashes (SHA-256)

| Item | SHA-256 |
|---|---|
| Frozen protocol v1 `R4_20261028_preflight/03_R4_protocol_v1.md` | `f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab` (unchanged) |
| Issued amendment 1 `R4_20261028_campaign/release/03_R4_protocol_v1_amendment_1.md` | `7720fed75bb678e47a229d00aff154e0aa14607c051f4a1163cc9bf67b6abee2` (unchanged) |
| Amendment 1 approval record | `03f835e9311410095e4447840ecb2b02d95c50279527df5fdf2f6d334e15eecd` (unchanged) |
| Attempt 2 release manifest `zz_sha256_manifest_release.csv` | `eae902275b363357674be7aed8a8b37162b687cd72ced0033dbfb84dfaff32e4` (unchanged) |
| Attempt 2 protocol §10.1 gate `logs/pre_run_hashes.txt` | `b4108d85c2bc35937e7c067aa922cca44e9b24f8d0a3e0a0286cf07fd7d69759` (unchanged) |
| Attempt 2 `GATE_RECORD_release.json` | `c25b2cfcd899f9ea7ce1bc2e4583c6879007a5b1a9cd71e2f9cf0f790b41f8e8` (unchanged) |
| Pilot readiness gate v7 `logs/readiness_gate_v7.json` | `0fd8606a6ad7b17d3513d458d40fa4aa91ea370d7ff7fc4447559a63e0568365` |
| Attempt 3 `GATE_RECORD_attempt3.json` | `c598f685d4e0c165f0345adbd49ab97cfe557a1001084921b33580b0c530b786` |
| Attempt 3 manifest `zz_sha256_manifest_attempt3.csv` | `e33cdcb9b9ff6c9e50d34ab00acdc53a21dac4fe87c20e79c41158f84f5da9d3` (73 files; also in `logs/zz_campaign_attempt3_manifest_sha256.txt`) |
| Campaign configuration `config/campaign_config_v6_DRAFT.json` | `f1d0fba15d73c75b124f2fc45e37f93a5d12bf4d7b42ae77f787dedb9f758167` |
| Review status `config/code_review_status_v4.json` | `91d15a69b2a6bf321ca1822b0de0554c1bbc1a4ed7578394d5691c1ac92a1b3b` |
| 170-run schedule `schedule_170.csv` (dry run) | `6011e3572ed6f99b0f306251de28580574b54ea18df495286baf8f4917a77dfc`, identical to attempt 2 |

The starting state was recorded before any change:
- `logs/zz_v5_pre_hash_started.txt` (09:27:44 +0700);
- `logs/zz_pre_hash_project_v5.csv` (25,037 project files);
- `logs/zz_start_inventory_v5_campaign_dir.csv`.

## 3. Amendment 2 draft

| Item | Value |
|---|---|
| Path | `R4_20261028_pilot/03_protocol_v1_amendment_2_DRAFT.md` |
| Status | **DRAFT — NOT APPROVED FOR RELEASE** (line 3, and `"status": "DRAFT"` in its machine-readable block). Not issued, not frozen, not approved |
| Revision | rev3 |
| SHA-256 | **`fdaf193de510488733f0e0899d50def86cbeafabdbecdd3bc7a144099b6f492c`** (`03_protocol_v1_amendment_2_DRAFT.sha256.txt`) |
| Earlier revisions (archived unchanged) | rev0 `c3e1ddfc…` (`archive/rev4a_reviewed_20261028_0957/`); rev1 `a936023a…` (`archive/rev4b_reviewed_20261028_1051/`); rev2 `e0dc6882…` (`archive/rev5_verified_20261028_1101/`) |
| Ambiguity register addendum | `02b_protocol_ambiguity_register_addendum_amendment2.md`. The original register is unchanged |

**Contents:**
- full hashes of protocol v1 and amendment 1;
- the ruling (§1);
- the pair rule and pair statuses (§2);
- the `NOT_APPLICABLE_QS_INFEASIBLE` label and the exact failed sub-check (§3);
- §8.2 independence (§4);
- the branch outcome, with zero eligible pairs giving INCONCLUSIVE and no pass by vacuity (§5);
- ambiguities AMB-29(a)–(d), AMB-30 and AMB-31, each with its direction (§6);
- the denominators (§7);
- the schedule effect: none (§8);
- the location rule (§9);
- the complete change list (§10);
- the retained blockers (§11);
- the issue steps (§12);
- the machine-readable block (§13).

The block equals the code's `IMPLEMENTED_2` key for key. The dry run read it with no errors. The amendment 1 thresholds are unchanged: M0/M1 ≤ 1 %, M2 reported only.

**Owner decisions requested in the draft (§6):**

| ID | Proposed handling | Direction |
|---|---|---|
| AMB-29(a) | profile unavailable → `NOT_APPLICABLE_PROFILE_UNAVAILABLE` | **can be favourable**: removes a B0-only failure path |
| AMB-29(b) | eligible pair without a finite energy → `NOT_EVALUABLE_RUN_MISSING`, M0/M1 INCONCLUSIVE | conservative |
| AMB-29(c) | QS energy ≤ 0 → `NOT_EVALUABLE_QS_UNDEFINED`, M0/M1 INCONCLUSIVE | conservative |
| AMB-29(d) | exception → `NOT_EVALUABLE_CONDITION_ERROR`, M0/M1 INCONCLUSIVE | conservative |
| AMB-30 | branch scope = all sets (literal §9) | mostly conservative |
| AMB-31 | "usable" energy = any finite simulator energy, whatever the §8.2 verdict | **can be favourable**. Stricter alternative: a PASS counts only on a dynamic-valid pair. Dynamic-valid PASS counts are reported separately |

## 4. Code changes

The pre-change code is archived in `archive/rev3_20261028_0928/`. The file-level comparison is `logs/zz_code_changes_rev3_to_rev6.csv`, with intermediate steps in `rev3_to_rev4`, `rev4b_to_rev5` and `rev5_to_rev6`.

**Files changed:**
- `code/r4h3/checks.py`, `code/r4h3/campaign.py`, `code/r4h3/frozen.py`;
- `code/tests/test_campaign.py`, `code/tests/test_rev2.py`;
- new `code/tests/test_amendment2.py`;
- new configs `campaign_config_v3`–`v6_DRAFT.json` (v3–v5 are kept and superseded);
- new `code_review_status_v4.json`.

**N-A2 implementation:**
- `checks.qs_screen` and `qs_piece_diagnosis` record the exact failed `QSPlant.step` sub-check: drive torque, battery discriminant or discharge current, per Gauss node.
- `pair_qs_dynamic` sets the pair status.
- `branch_qs_dynamic_outcome` applies the no-vacuity rule and raises on an unknown status.
- `qs_dynamic_accounting` produces every denominator. The eligibility classes and the check-status classes each add up to the planned pairs.
- `campaign.run_condition` screens both profiles on the evaluated plant. It computes per-arm QS-vs-dynamic only for an eligible pair with a finite energy, and never uses an ineligible pair's QS energy.
- `execute_schedule` writes `qs_dynamic_accounting.csv` and `qs_dynamic_branch_outcomes.csv`, and adds the outcomes to the manifest.
- **Unchanged:** the profile, plant, gain, limits, task, planner, controller and thresholds.

**Fail-closed changes:**
- Amendment 2 is read and enforced as a separate issued amendment, with its own approval record and the check that it amends the issued amendment 1 (SI-2).
- The authorisation must carry `amendment_2_sha256`, and its scope covers amendments 1 and 2.
- Campaign mode is allowed only from the campaign root, by resolved path (R3-1).
- Every exception in a pair evaluation, the accounting, a branch outcome or the D5 denominator is recorded, never a pass, and all outputs are still written.

**Location independence (SI-1):** paths are found by a repository marker, so a release attempt can be tested from a versioned sub-directory.

**Unchanged:**
- the amendment-1 decision set (`IMPLEMENTED`);
- the numerical-check names and order (only row 7's text changed);
- `classify_pair`, `paired_delta`, the evaluator, the separate recomputation, the closed loop and the schedule code.

**The 12 required tests** are all in `code/tests/test_amendment2.py`:

| # | Requirement | Test |
|---|---|---|
| 1 | both feasible, pass | `test_case1_both_feasible_and_the_check_passes` |
| 2 | both feasible, applicable fail → INCONCLUSIVE | `test_case2_both_feasible_and_an_applicable_check_fails` |
| 3–5 | B0, B3 or both infeasible → not applicable, whatever the arm values | `test_cases3_to_5_any_qs_infeasible_profile_makes_the_pair_not_applicable` (3 cases) |
| 6 | ineligible, dynamically feasible: keeps COMPARABLE; no QS value used | `test_case6_qs_ineligible_but_dynamically_feasible` (executor level) |
| 7 | ineligible, dynamically infeasible: 8.2 status kept; no paired delta | `test_case7_qs_ineligible_and_dynamically_infeasible` (real QS and 8.2 failure) |
| 8 | zero eligible → INCONCLUSIVE | `test_case8_a_branch_with_zero_eligible_comparisons_is_inconclusive` |
| 9 | denominators | `test_case9_denominator_and_exclusion_accounting` |
| 10 | records preserved | `test_case10_records_are_preserved_and_accounting_written` (executor; runs, traces and evaluation rows kept) |
| 11 | not applicable ≠ pass | `test_case11_not_applicable_is_never_a_pass` |
| 12 | runner blocked without authorisation | `test_case12_campaign_mode_stays_blocked_without_authorisation_and_amendment_2`, plus the precondition-branch tests |

Further tests cover the review findings: R3-1, R3-2, R3-3 (×2), R3-5, R3-7 (×6), R3-9, R3-12, R3-13, R3-15, AMB-29, the unchanged thresholds, the eligible-pair evaluation, the draft's DRAFT status and SI-1. `test_amendment2.py` has 32 tests.

## 5. Test counts and logs

All logs are kept. No failing log was deleted or overwritten.

| Run | Code state | Result | Log |
|---|---|---|---|
| 15 | first N-A2 implementation | 200 passed, **1 failed**: the authorisation test lacked `amendment_2_sha256`. The test was made stricter; no rule was relaxed | `logs/pytest_run15.*` |
| 16 | rev4a (pre-review) | 201 passed | `logs/pytest_run16.*` |
| 17 | first R3 fixes | 205 passed, **6 failed**: `config_content` used `relative_to` on monkeypatched paths. Fixed with literal paths, so the content is unchanged, and a rebuild failure now becomes a blocker | `logs/pytest_run17.*` |
| 18 | rev4b | 211 passed | `logs/pytest_run18.*` |
| 19 | rev5 | 215 passed | `logs/pytest_run19.*` |
| 20 | rev6 | 216 passed | `logs/pytest_run20.*` |
| **21** | rev6 + review status v4 (final pilot) | **216 passed, 0 failed, 0 errors** → readiness gate v7 | `logs/pytest_run21.*`, `logs/readiness_gate_v7.json` |
| **attempt 3** | the copy in `attempt3_amendment2/` | **216 passed, 0 failed, 0 errors** → attempt readiness gate v1 | `attempt3_amendment2/logs/pytest_release_attempt3.*`, `logs/readiness_gate_v1.json` |

Every run used `python -I -B -m pytest -c code/pytest.ini --rootdir code`.

**Copy verification:** 58 files copied, each SHA-256 equal to its pilot source. The 50 code and config files equal gate v7's `code_sha256` (`attempt3_amendment2/logs/copy_verification_attempt3*.{csv,json}`).

## 6. Independent review: findings and closure

The reviewer was a separate **read-only AI review agent**, not a human. It used Read, Grep and Glob only, and inspected the actual changed pilot code and the amendment draft. Its four reports are stored verbatim in `review/`. Its hashes are the developer's; it could not hash. The attempt-3 copy is byte-identical to the reviewed source by SHA-256 (§5).

| Report | State reviewed | Findings | Closure |
|---|---|---|---|
| `N-A2_review_agent_report_20261028.md` | rev4a, draft rev0 | R3-1 **MAJOR** (campaign-mode location check by name only after SI-1); R3-2…R3-11 MINOR/NOTE | fixed in rev4b and draft rev1 |
| `N-A2_verification_agent_report_20261028.md` | rev4b, draft rev1 | 8 fixed; R3-6, R3-7, R3-10 partly fixed; new R3-12, R3-13 (NOTE) | fixed in rev5 and draft rev2 |
| `N-A2_verification2_agent_report_20261028.md` | rev5, draft rev2 | R3-7(b–d), R3-10, R3-12, R3-13 fixed; new R3-14 (MINOR, stale config name in draft), R3-15 (NOTE, M2 wording); residual note on the D5 denominator | fixed in rev6 and draft rev3 |
| `N-A2_verification3_agent_report_20261028.md` | rev6, draft rev3 | R3-14, R3-15 and the residual fixed; **no new defect; no CRITICAL or MAJOR finding open** | — |

**Re-confirmed in every report:**
- **CR-A2** stays closed: `classify_pair` takes no QS input.
- **CR-A6** stays mitigated, with the residual the owner accepted.
- **Torque limits:** the independent evaluator is unchanged; the new QS diagnosis is simulator-side only.
- **Fail-closed: YES.**

**Recorded in `config/code_review_status_v4.json`:**
- `open_critical 0`, `open_major 0`, `open_owner_decisions []`.
- `pending_owner_acceptance ["CR-A6 residual"]`, which amendment 1's approval record satisfies.

**A choice I made that you may override:** AMB-29, AMB-30 and AMB-31 are not listed in `open_owner_decisions`. Campaign mode already blocks until amendment 2 is issued, approved and its block equals `IMPLEMENTED_2`. A different decision would therefore keep campaign mode blocked until the code and a new attempt are revised.

**Noted, not changed:** an empty stop list writes no `stop_compliance.csv`. This behaviour predates this task.

## 7. 170-run schedule

The dry run from attempt 3 (`attempt3_amendment2/dry_run_20261028_114044/`) validated it:
- NOM 12, P3 12, INS 12, CNV 6, SEN 128, **total 170**;
- `schedule_passed: true`; the configuration is current and its schedule SHA-256 matches;
- the sensitivity table regenerates identically.

`schedule_170.csv` and `planner_jobs.csv` are byte-identical to attempt 2's dry run. No run was added, removed or made conditional. S2 was not used for tuning. No controller was retuned and the planner was not changed.

## 8. The runner refuses campaign mode

This was checked with `preconditions("campaign")` from the attempt-3 copy (`logs/preconditions_attempt3.json`). `run_campaign()` was **not** called; it raises `CampaignBlocked` whenever this list is non-empty. The blockers:

1. no issued amendment 2 at `R4_20261028_campaign/release/03_R4_protocol_v1_amendment_2.md`;
2. no protocol §10.1 gate record for this code;
3. no campaign authorisation record `campaign_authorization.json`;
4. not running from the campaign root by resolved path (AMB-15, protocol §10.1).

`preconditions("readiness")` has one blocker, the missing issued amendment 2. Official run IDs are refused outside campaign mode (`test_official_ids_are_refused_outside_campaign_mode`). No code path writes the issued amendment, either approval record or the authorisation (`test_code_never_writes_approval_or_authorisation`, which covers all five names).

## 9. Remaining blockers

Status of the five gate criteria (`GATE_RECORD_attempt3.json` → `gate_criteria`):

| # | Criterion | Met? |
|---|---|---|
| 1 | Amendment 2 reviewed, approved and issued by the owner (draft §12) | **no** |
| 2 | New attempt passes all mandatory tests and independent reviews | yes: 216/216, no open CRITICAL or MAJOR finding. The owner decisions ride on criterion 1 |
| 3 | Final release manifest and protocol hashes verified | **no**: this attempt's manifest and the protocol hashes are verified, but the final release manifest exists only after promotion |
| 4 | All release criteria met, including promotion to the campaign root with its own §10.1 gate | **no** |
| 5 | Separate explicit owner authorisation: `release/campaign_authorization.json` with scope "execute the 170-run H3 campaign of protocol v1 amendments 1 and 2", `amendment_sha256`, `amendment_2_sha256` and `pre_run_hashes_sha256` | **no**: absent |

**Procedural point for the owner.** Campaign mode runs only from the campaign root. The root holds attempt 2 and its §10.1 gate, which `record_gate.py` refuses to overwrite. Promoting attempt 3 therefore needs an owner-approved procedure:
1. move attempt 2, unchanged, into a versioned `release_attempts/` directory;
2. copy attempt 3 to the root and verify it against its manifest;
3. run the full tests there and record a new §10.1 gate;
4. write a new release manifest.

`ATTEMPT_NOTE_attempt3.md` lists these steps. None was taken. If the owner decides any AMB item differently from the draft, the code, the review and a new attempt (attempt 4) are needed.

## 10. No official run and no energy comparison between arms

- No official run ID was executed, and there is no campaign `outputs/` directory at the root or in attempt 3.
- The only simulations were the test suite's development conditions, on a synthetic task in temporary directories.
- No energy difference between experimental arms was calculated or reported, and no energy-saving claim is made.
- `campaign_authorization.json` was not created, and amendment 2 was not approved or issued.

## 11. Prior releases, preflight, snapshot and legacy material unchanged

Final checks are in `logs/zz_integrity_v5_post.json`.

| Item | Result |
|---|---|
| Project files (scope as the v5 pre-hash: repository minus `.git`, `.venv`, `cache`, `tools` and this pilot directory) | before 25,037, after 25,111. **74 added, all inside `attempt3_amendment2/`** (73 manifest rows plus the manifest). 0 removed, 0 changed (`logs/zz_pre_post_comparison_v5.txt`) |
| Attempt 2 package and `release/` | 122/122 manifest rows verified. Amendment 1, its approval record, the §10.1 gate and `GATE_RECORD_release.json` are unchanged |
| Attempt 1 | unchanged (covered by the attempt-2 manifest) |
| Preflight directory | manifest 29/29. No file added, removed or changed |
| Frozen protocol v1 | `f9826318…` unchanged |
| Evidence snapshot `C:\Users\HLC\EUREKA_EVIDENCE\GATE1_20261028` | manifest SHA-256 `A93EB44F…` matches; **570/570** rows pass. Only the snapshot copies were read; `D:\EUREKA` was not accessed |
| Thesis and R1–R3 artefacts | not written (no change anywhere in the project scope outside attempt 3) |
| Pilot history | 315 of 320 v4-manifest files unchanged, including every earlier draft, the amendment 1 drafts, all historical test logs (runs 1–14), manifests v1–v4, readiness gates v2–v6, the smoke-test outputs and reports 00–13. The 5 changed files are the live code files listed in §4, whose earlier versions are archived. All other pilot files are new and versioned |

The pilot manifest of this state is `zz_sha256_manifest_v5.csv` (self-exclusion in `zz_sha256_manifest_v5.README.md`). Its SHA-256 is in `logs/zz_manifest_v5_sha256.txt`.

No Git command, install, download or network access was used.
