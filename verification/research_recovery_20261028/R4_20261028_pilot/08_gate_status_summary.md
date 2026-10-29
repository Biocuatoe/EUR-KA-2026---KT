# R4 H3: campaign readiness gate status

**Date:** 2026-10-28, 06:24 (UTC+7).
**Verdict:** the 170-run campaign remains **BLOCKED**. Five of the nine stop conditions are met. Two need owner decisions. One (condition 6) cannot be met before the campaign as worded, because the protocol defines it on S2 campaign data. The amendment is a draft and is not approved.

**Not done:**
- the campaign was not started, and campaign mode was never invoked;
- H1, H2, H4 and H5 were not touched;
- no energy difference between arms and no headline was computed.

## 1. Stop conditions of the readiness brief

| # | Condition | Status | Evidence |
|---|---|---|---|
| 1 | The exact canonical 1 s-sampled S1/S2 data have verified provenance and hashes | **MET** | `05_cycle_input_provenance.md`. The sampled tasks were produced by R3's frozen `run_gates.reference()` and match bit for bit R4 `task.load_task()` and all 24 hash-checked R3-retained references per cycle. S1 `87151e5c…b7da`, S2 `def9d757…e990`; checked by `inputs.verify_all()` in the gate, the dry run and campaign start |
| 2 | The amendment has been reviewed and explicitly approved | **NOT MET** | `03_protocol_v1_amendment_1_DRAFT.md` (rev1, SHA-256 `f4ffc4b7…b69e`) is DRAFT — NOT APPROVED FOR CAMPAIGN EXECUTION. No issued file, no approval record |
| 3 | The P3 comparison and infeasibility-handling rules are implemented and tested | **IMPLEMENTED AND TESTED; RULE CHOICE OPEN** | D2 and D5 are implemented in `campaign` and `checks`. Tests: 11 classification cases in `test_checks.py`, covering both P3 readings. Executor tests: a P3 condition in the toy campaign run; refusal of P3 without an issued rule; a P3 plant on which the profile is infeasible, where both arms still run and the condition is classified, not credited. Which reading of "infeasible on P3" applies is AMB-24 (review CR-A2); P3 conditions are refused until it is issued |
| 4 | Stop compliance does not depend on planner success flags | **MET** | Planned trajectories: the validator takes only knots (D1, D3; tests on signature and imports). Dynamic runs: the evaluator decides §8.2 stop compliance from the trace. The classification reads only evaluator and simulator flags (test `test_classification_ignores_any_planner_flag`) |
| 5 | Energy metrics can be recomputed from retained traces with documented tolerances | **MET; three tolerances need acceptance** | Per-run trace (schema v2) and spec file. `recompute_from_traces.py` runs in a separate process, and no simulator module was imported (test plus DEV-4 at full S1 length: all checks pass). §9 tolerances are used as written; the three it does not state (trip time 1e-9 s, I_over 1e-4 A·s, RMSE 1e-9 relative) are declared in A1-12 for the owner to accept |
| 6 | The grid, QS-versus-dynamic and 0.5 ms checks pass their protocol requirements | **NOT MET as worded (AMB-18)** | Protocol §9 defines these on S2 campaign data. Pre-campaign they are implemented and validated on S1 development data: DEV-2 (QS-versus-dynamic +0.53 % and +0.20 %, within ±1 %), DEV-3 (fine grid valid, 6.5 s), DEV-4 (0.5 ms path, recomputation passes). Owner to confirm this interpretation |
| 7 | The 170-run schedule, run IDs, sensitivity design and held-out S2 role are validated without executing campaign runs | **MET (validation); SEN gain basis open** | `07_campaign_dry_run_report.md`: 18 of 18 schedule checks pass; 170 unique official IDs; 82 planner jobs, none a run; smoke IDs excluded; S2 used only as an input; numerics equal §5.2. Sensitivity table regenerates identically. The SEN gain basis is AMB-14 |
| 8 | Independent code review finds no unresolved critical issue | **MET for critical (0); 2 MAJOR need the owner** | `04_independent_code_review.md`: CR-A2 (= AMB-24) and the CR-A6 residual (common-mode equations and traced torque limits). `config/code_review_status_v1.json` (`open_major: 2`) keeps the campaign blocked until the owner rules |
| 9 | No result is selected or retuned to match a legacy percentage | **MET** | No outcome was computed. No legacy figure appears in code, config, inputs or reports (searched). No parameter was tuned; planner numerics are frozen constants |

## 2. Ready

**Code:**
- validator (D1, D3);
- executor with D2/D5 handling and full run accounting;
- §9 checks: QS-versus-dynamic, grid convergence, optimality, time step and recomputation;
- separate-process recomputation;
- sensitivity design;
- schedule and dry run;
- amendment reader;
- precondition gate.

**Evidence:**
- **Tests:** 139 of 139 pass (run 5). Run 4 had 1 failure, a test defect, and its log is kept.
- **Readiness gate:** `logs/readiness_gate_v2.json`.
- **Canonical inputs:** hashed.
- **Draft campaign configuration:** `config/campaign_config_v1_DRAFT.json` (`9f3043f0…ad13`).

## 3. Blocked, and what unblocks it

| Blocks | Item | Needs |
|---|---|---|
| Whole campaign | amendment approval and issue | owner review; issued file at `../R4_20261028_preflight/03_R4_protocol_v1_amendment_1.md`; `approvals/amendment_1_approval.json` |
| Whole campaign | AMB-15 campaign directory | owner names a fresh `R4_<date>_pilot` directory; code, config and inputs are copied there; a clean test run; its own `logs/pre_run_hashes.txt` |
| Whole campaign | review CR-A6 residual | owner accepts the stated scope of the recomputation, or asks for an independent torque-limit recomputation |
| P3 set (12 runs) | AMB-24 / CR-A2 | owner chooses `qs_step_feasibility_on_P3` or `dynamic_8_2_only` |
| SEN set (128 runs) | AMB-14 | owner chooses `nominal_P1` or `draw_P1` |
| Crediting rule | A1-12 tolerances | owner accepts or replaces them |

## 4. Requires human approval

1. Amendment 1 as a whole (D1–D5 wording, A1-1 to A1-18).
2. AMB-14, AMB-15 and AMB-24.
3. The A1-12 tolerances.
4. Review rulings on CR-A2 and CR-A6.
5. Confirmation of the AMB-18 interpretation of stop condition 6.

None of these was assumed or set by the implementation.

## 5. Integrity

| Check | Result |
|---|---|
| Frozen protocol `03_R4_protocol_v1.md` | SHA-256 `f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab`, unchanged (checked at start, gate, dry run, development checks and end) |
| Preflight directory | `zz_R4_file_manifest.csv`: 29 of 29 files match |
| Project files outside the pilot directory, before (05:31) vs after (06:22), SHA-256, size and mtime | 24,914 → 24,914; **0 added, 0 removed, 0 changed** (`logs/zz_pre_post_comparison_v2.txt`). This covers the preflight directory, R1–R3 source and outputs, `src/`, `configs/`, the thesis and every other legacy file in the project |
| Evidence snapshot `GATE1_20261028` | 570 of 570 consistent; manifest SHA-256 `A93EB44F…F279` unchanged (`logs/zz_snapshot_summary_v2_post.json`) |
| Smoke-test outputs (D4) | all 13 files byte-identical to the v1 manifest |
| Bytecode | no `__pycache__` or `.pyc` created in the R3 tree or the pilot. The caches in `src/eureka` and `rebuild` predate R4 (dated 23–25 Oct) and are in the before-snapshot |
| Git, installs, network, CNTT-02, `D:\EUREKA` | none used |
| Pilot manifest | `zz_sha256_manifest_v2.csv` (self-exclusion policy: `zz_sha256_manifest_v2.README.md`). The v1 manifest is kept unchanged |
