# R4 H3: owner approval and campaign release-readiness report

**Date:** 2026-10-28, 07:44–08:40 (UTC+7). **Prepared by:** AI assistant (reproducibility audit).

**Campaign status: BLOCKED.** Two items block the campaign:
1. **N-A2**: an acceptance-logic ruling needed from the owner (below).
2. **No campaign authorisation**: by design, protocol approval does not authorise execution.

No campaign mode was invoked, no official run exists, and no energy difference was computed.

## 1. Amendment approval

| Item | Value |
|---|---|
| Frozen protocol v1 | `03_R4_protocol_v1.md`, SHA-256 `f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab`, unchanged |
| Candidate (verified before issue) | `03_protocol_v1_amendment_1_rev2_CANDIDATE.md`, SHA-256 `42a7a9f51afae7c059373b9048ed9b09c6b87c975705e54c485f2f6bfc133369`; matches the value given by the owner |
| Content check before issue | 18 of 18 checks passed: block equals the implementation, 0 open items, AMB-14/15/24, the three tolerances, protocol hash, 170 runs, and the AMB-14, AMB-24, S2 and CR-A6 wording |
| Released amendment | `R4_20261028_campaign/release/03_R4_protocol_v1_amendment_1.md`, SHA-256 `7720fed75bb678e47a229d00aff154e0aa14607c051f4a1163cc9bf67b6abee2` |
| Differences from the candidate | the status line, a source line, block `"status"` DRAFT → APPROVED, and the block note (`release/amendment_issue_diff.txt`). Nothing substantive |
| Approval record | `R4_20261028_campaign/release/amendment_1_approval.json`, SHA-256 `03f835e9311410095e4447840ecb2b02d95c50279527df5fdf2f6d334e15eecd` |
| Approval record content | approver; date 2026-10-28 07:46 (local clock); the protocol, candidate and released hashes; the decisions; the approved tolerances; the I_over note; acceptance of "CR-A6 residual"; scope "protocol amendment only"; campaign BLOCKED. `campaign.approval_problems()` = [] |
| Candidate and earlier drafts unchanged | candidate `42a7a9f5…`, rev1 `f4ffc4b7…`, rev0 `faf25d80…`: verified at the start and the end |

The I_over tolerance (1e-6 A·s) is recorded as a chosen numerical-comparison tolerance relative to the 0.01 A·s pass/fail threshold. It is not a measured physical uncertainty or a threshold change.

## 2. Gap closed before release: campaign authorisation (VC-14)

**Problem.** Before this task, once the amendment was issued and the release gate recorded, the runner had no remaining blocker. `--execute` would have started the campaign, so protocol approval would have acted as authorisation.

**Change.** Campaign mode now also requires `release/campaign_authorization.json`. It is written by the owner, never by code (enforced by a static test). It must name who authorised it and when, state the scope "execute the 170-run H3 campaign of protocol v1 amendment 1", and carry the SHA-256 of the issued amendment and of `logs/pre_run_hashes.txt` (`campaign.authorization_problems`).

**Also in VC-14.** Readiness gates now version themselves: v2 to v6 are all kept.

## 3. Independent re-review of CR-A2 and CR-A6

**The reviewer.** A separate read-only agent (Read, Grep and Glob only). It read the current source, the tests, the archives and the logs. Its report is kept verbatim in `review/CR-A2_CR-A6_rereview_agent_report_20261028.md`.

| Finding | Original (severity) | Corrective change | Regression tests | Verdict | Remaining |
|---|---|---|---|---|---|
| CR-A2 | "QS feasibility on the P3 plant decides the outcome before §8.2" (MAJOR) | `checks.py` (`P3_RULE`, `classify_pair` without a QS input, `failed_criteria`, `qs_energy` failing pieces); `campaign.run_condition` (QS screen recorded only; both arms always run) | `test_checks.py::test_classification[…]`, `::test_amb24_…`, `::test_qs_screen_records_the_exact_failing_pieces`; `test_campaign.py::test_p3_profile_infeasible_…`, `::test_qs_screen_failure_alone_never_labels_a_dynamically_valid_p3_condition` (new, N-A1); logs runs 10–14 and the release run | **CLOSED** (campaign path) | N-A2 (below); development slice driver keeps old semantics (N-A6, not used by the campaign) |
| CR-A6 | "evaluator does not meet §9's separate script…" (MAJOR) | separate-process script; per-run spec; simulator-side C-rate I_over and min V_t; independent torque limits (VC-09); **now also: the separate script's verdict decides crediting (N-B1)** | `test_rev2.py` (torque-limit boundary, agreement, sensitivity and independence tests; forced-over-current I_over); `test_regressions_v2.py` protocol/diagnostic tests; `test_campaign.py::test_independent_recomputation_…`, `::test_separate_recomputation_verdict_decides_crediting` (new) | **CLOSED as mitigated, residual accepted** by the owner (approval record) | shared model equations, parameters and integrated states; `tracking_ok` relies on the traced v_tracked; the torque-limit cross-check is a non-gating diagnostic. **Not physical validation.** The reviewer confirmed no document claims physical validation |

**New re-review findings and their handling.** No CRITICAL or MAJOR findings.

| ID | Severity | Handling |
|---|---|---|
| N-A1 | MINOR (test gap) | fixed: executor-level test with a forced QS-screen failure on a dynamically nominal P3 condition. A physical "QS fails, dynamic passes" case could not be built from torque limits: in this model, anti-windup saturation also costs distance, so completeness fails first |
| **N-A2** | MINOR, acceptance logic | **open, owner ruling required.** §9 "QS vs dynamic" (M0/M1 failure → branch INCONCLUSIVE) is computed for every run, including P3 profiles that fail the QS screen, whose QS energy uses unclipped over-limit torque. AMB-24 does not say whether this check is decisive for such profiles. Under §8.1 ("every check in §9 passes") the ruling can change the H3 verdict. No default was chosen. The executor records both `qs_screen_*` and `qs_vs_dyn_*` per run, so either ruling can be applied, **but it must be issued before the campaign** (e.g. as amendment 2). The campaign is blocked on it (`config/code_review_status_v3.json` → `open_owner_decisions`) |
| N-A3, N-A4 | NOTE | status ordering and counts as written in the amendment's table; documented |
| N-A5 | MINOR | fixed: condition-level and grid-job exceptions are recorded; accounting files are always written (test) |
| N-A6, N-A7, N-B2, N-B3 | NOTE | documented. Stale text sits in superseded documents (02, 04, 08), which are kept unchanged. The evaluator header wording is fixed. The issued amendment's phrase "verifies … the torque-limit calculation" refers to a diagnostic, as its own §9 says |
| N-B1 | MINOR, acceptance logic | fixed: `execute_schedule` runs `recompute_from_traces.py` in a separate process. A condition stays COMPARABLE only if that process confirms both runs; otherwise it becomes RECOMPUTATION_DISAGREEMENT (`fold_separate_recomputation`, tests) |

Code record: `logs/zz_code_changes_rev1_to_rev2.csv`. Archive of the state before this task: `archive/rev2_20261028_0744/` (44 files, all matching manifest v3).

## 4. Release checklist (`11_campaign_release_checklist.md`)

| Step | Result |
|---|---|
| B1–B5 Approval and issue | done (§1). Campaign authorisation is now an additional step (§2) |
| C6 Copy `code/`, `config/` and `inputs/` | attempt 2: 52 files byte-identical to the pilot; all 44 code/config hashes equal `logs/readiness_gate_v6.json`; all 7 canonical input hashes match. The pilot tree was not modified by the copy |
| C7 Tests from the release copy | **attempt 1: 183 passed, 1 failed.** The failing test (`test_readiness_gates_are_versioned`) assumed a readiness gate exists; there is none in the release directory. Test defect, preserved in `R4_20261028_campaign/release_attempts/attempt1/`. Fixed in the pilot and re-gated (pilot run 14, 184/184, gate v6). **Attempt 2: 184 passed, 0 failed** (`logs/pytest_release.*`) |
| C8 Protocol §10.1 gate | `R4_20261028_campaign/logs/pre_run_hashes.txt`, SHA-256 `b4108d85c2bc35937e7c067aa922cca44e9b24f8d0a3e0a0286cf07fd7d69759`; binds the release junit and every code hash |
| C9 Dry run | `R4_20261028_campaign/release/dry_run_20261028_083731/`: 170 unique official IDs (12/12/12/6/128); both smoke runs excluded; canonical inputs verified; configuration current; draw table regenerates; S2 rules and P3 handling consistent with the issued block (0 reader errors) |
| C10 Release manifest | `R4_20261028_campaign/zz_sha256_manifest_release.csv`: 122 files, self-excluding. Its SHA-256 `eae902275b363357674be7aed8a8b37162b687cd72ced0033dbfb84dfaff32e4` is in the pilot's `logs/zz_campaign_release_manifest_sha256.txt` |
| Gate record | `R4_20261028_campaign/GATE_RECORD_release.json`, SHA-256 `c25b2cfcd899f9ea7ce1bc2e4583c6879007a5b1a9cd71e2f9cf0f790b41f8e8`. The earlier `GATE_RECORD_not_released.json` is kept |
| Campaign mode cannot start while blocked | `preconditions("campaign")` from the release copy returns exactly 2 blockers: no campaign authorisation; N-A2. It was checked directly; `--execute` was not invoked |
| No official outputs | `R4_20261028_campaign/outputs/` does not exist |

**Release criteria.** Every one passed (attempt 2), except the two blockers above.

## 5. To unblock (owner)

1. **Rule on N-A2.** Is §9 QS-vs-dynamic decisive (branch INCONCLUSIVE on an M0/M1 failure) for P3 profiles that failed the QS screen? Issue the ruling as amendment 2 before any run.
2. After the ruling: update the review status (`open_owner_decisions`). Any code change requires a new readiness gate and a new release attempt in a fresh `release_attempts`-style record.
3. Write `R4_20261028_campaign/release/campaign_authorization.json` with:
   - `authorized_by`;
   - `date`;
   - `scope` = "execute the 170-run H3 campaign of protocol v1 amendment 1";
   - `amendment_sha256` = `7720fed7…` (the issued amendment);
   - `pre_run_hashes_sha256` of the then-current `logs/pre_run_hashes.txt`.

## 6. Integrity

| Check | Result |
|---|---|
| Project files outside the pilot, before (07:44) vs after (08:41) | 24,917 → 25,037: **120 added, 0 removed, 0 changed**. All 120 are in `R4_20261028_campaign/` (`logs/zz_pre_post_comparison_v4.txt`) |
| Frozen protocol | `f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab`, unchanged |
| Preflight directory | not written to; manifest 29/29 |
| Candidate and earlier drafts | rev2 candidate `42a7a9f5…`, rev1 `f4ffc4b7…`, rev0 `faf25d80…`: unchanged |
| Earlier audit reports, test logs, smoke traces, review reports, manifests | unchanged. The 9 pilot code and test files changed in this task are archived in `archive/rev2_20261028_0744/` with their manifest-v3 hashes |
| Evidence snapshot | 570/570 |
| Bytecode | no `__pycache__` in the R3 tree, the pilot or the campaign directory |
| Git, installs, network, CNTT-02 | none used |
