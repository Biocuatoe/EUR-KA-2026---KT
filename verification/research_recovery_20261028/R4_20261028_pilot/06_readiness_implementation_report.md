# R4 H3 pilot: readiness implementation report

**Date:** 2026-10-28, 05:31–06:24 local time (UTC+7).
**Prepared by:** AI assistant. The independent code review was done by a separate read-only agent plus the author (`04_independent_code_review.md`).

**Scope:** decisions D1–D5, the S1/S2 cycle inputs, the review fixes, and the campaign-readiness components.

**Not done in this task:**
- no campaign run and no campaign mode;
- no S2 planner, QS or dynamic computation;
- no H1, H2, H4 or H5 work;
- no energy difference between arms and no headline.

## 1. Starting state and safeguards

| Check | Result |
|---|---|
| Protocol SHA-256 vs freeze record (full value) | `f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab`, **match** |
| Project files outside the pilot directory: end of the previous session (01:33) vs 05:31 today | 24,914 → 24,914; 0 added, 0 removed, 0 changed |
| Evidence snapshot | 570/570 consistent; manifest SHA-256 `A93EB44F…F279` unchanged |
| Pilot v1 manifest (`zz_sha256_manifest.csv`, 51 files) | 0 mismatches at start |
| rev0 archive | the 25 code, config and document files that might change, copied to `archive/rev0_20261028_0135/` **before any edit**. Every hash equals the v1 manifest and the smoke-test gate record (`ARCHIVE_INDEX.csv`) |

## 2. Versioned changes to existing code (VC)

The full per-file record of rev0 versus rev1 hashes is `logs/zz_code_changes_rev0_to_rev1.csv`:
- **changed:** 12 files (10 code and test files, 2 documents);
- **added:** 17 (13 code and test files, 4 config files);
- **unchanged:** 13, including `config.py`, `task.py`, `planner.py`, `run_slice.py`, `record_gate.py` and the original validator, planner, trace and frozen/task tests.

Each change has a regression test in `code/tests/test_regressions_v2.py` unless noted.

| ID | File(s) | Change | Reason | Regression tests |
|---|---|---|---|---|
| VC-01 | `validator.py` | "At rest" is the frozen §5.1 rule v ≤ 1e-9 m/s (was an invented 1e-12). Time comparisons are exact (was a 1e-9 s tolerance). Speed caps are exact. The wait after arrival must be at rest. The total-distance allowance is K × the §9(b) per-segment 1e-9 m | D1, D3; review CR-B1, CR-B2 | 8 tests: rest rule; interior knot at 5e-10 m/s is a stop; rest knot at 5e-10 is at rest; arrival +1e-10 s and departure −1e-10 s rejected; creep after early arrival rejected; wait speed reported; no planner input |
| VC-02 | `closedloop.py` | Traces sampled every 1 ms for every run (every second step at 0.5 ms, §10.3); `trace_dt` returned; a dt that does not divide 1 ms is refused | §10.3; CR-A1, CR-B4 | bitwise equality with `r3_lib.simulate(dt=0.0005)` for M0 and M2; trace spacing; refusal |
| VC-03 | `evaluator.py` | Refuses a trace whose spacing differs from the declared step. R1–R3 battery-limited fraction (old quantity renamed `limit_active_sample_frac`). Adds max \|e\| against v_ref | CR-A1, CR-B5, CR-B6 (§7.2) | step refusal; battery-limited fraction equals the simulator's |
| VC-04 | `evaluator.py` | `compare_with_simulator` separates `protocol_ok` (the §9 quantities, which decide crediting) from `diagnostics_ok` (reported only) | CR-B3; CR-A9 | a diagnostic disagreement does not decide; each protocol disagreement does; the check set equals §9 and the campaign record |
| VC-05 | `evaluator.py`, `closedloop.py` (new `trace_constraint_metrics`), `slice.py` | The deciding C-rate I_over and the constraint flag are compared with simulator-side values from the traced r3_lib current and V_t. Window I_over becomes a diagnostic. Wheel braking power recomputed with B_m and η_g. Tracked-profile check against the knots. Energy closure recomputed from the trace. The slice driver passes the trace step (CR-A1) | CR-A6, CR-A10, CR-A12, CR-B7 | protocol-disagreement tests; decimated-trace recomputation (both diagnostics present) |
| VC-06 | `slice.py` | Only interface updates: the specification gains T_max, P_max, B_m, η_g, M_eff and C1; trace step; simulator-side constraint metrics. Its rev0 behaviour for v_b is kept (CR-B8, development driver only) | consistency | existing suite |
| VC-07 | `frozen.py` | `UPSTREAM_SHA256`: 9 upstream physics, configuration and cycle files, checked before `r3_lib` is imported | CR-A7 | upstream hashes verified; a wrong hash is refused |
| VC-08 | `__init__.py`, `traces.py`, `closedloop.py` | Trace schema `r4h3-trace-v2` adds the 5 closure integrators (E_rr, E_aero, E_gear, E_visc, E_regen). The reader still accepts v1, so the smoke-test traces stay readable | CR-A12 | closure from the trace equals the simulator; a v1 file is read |
| test-spec | `tests/test_evaluator.py`, `test_closedloop.py`, `test_scope.py` | Specifications gain the new required fields; the synthetic trace gains `t_pos_Nm`; the simulator dictionary gains the new compared fields. No assertion or tolerance was changed | interface of VC-03 and VC-05 | existing tests pass unchanged in intent |

## 3. New components

| Component | File | What it does |
|---|---|---|
| Canonical cycle inputs | `code/build_cycle_inputs.py`, `r4h3/inputs.py`, `inputs/cycles/*` | §2 of the brief; see `05_cycle_input_provenance.md`. `inputs.verify_all()` re-hashes the artefacts and checks `task.load_task()` bit for bit |
| Protocol §9 checks | `r4h3/checks.py` | `qs_energy` (QS energy of any knot profile), `qs_vs_dynamic` (M0/M1 ±1 %, M2 reported only), `scenario_totals` (S_found, S_max, optimality gap), `grid_convergence` (< 0.2 pp), `timestep_check` (< 0.01 pp), `classify_pair` (D5 and §8.1 order, P3 rule from the issued amendment), `paired_delta` (only for COMPARABLE, always with trip time), `denominator` |
| Sensitivity design | `r4h3/sensitivity.py`, `config/sensitivity_draws_v1.csv` | §8.4 draws (seed, generator, ranges and ledger IDs, mapping, purpose); per-draw plant and motor; the gain basis is refused until AMB-14 is issued |
| Campaign runner | `r4h3/campaign.py`, `code/run_campaign.py` | Official 170-run schedule and IDs; 82 planner jobs; schedule validation; amendment reader (confirms, never overrides; unknown keys and differing values are errors; nulls are open); campaign configuration; preconditions; the executor (`plan_design`, `run_arm`, `run_condition`, `execute_schedule`, with planner grid convergence); dry run. `--execute` refuses while any precondition fails |
| Separate-process recomputation | `code/recompute_from_traces.py` | §9 "separate script reading only the saved traces": reads traces, per-run spec files and `runs.csv`; asserts that no simulator module was imported |
| Readiness gate | `code/record_readiness_gate.py` → `logs/readiness_gate_v2.json` | Binds the clean test run (run 5) to the SHA-256 of every code and config file, the protocol, and the frozen, upstream and cycle inputs. Versioned: the smoke-test gate `logs/pre_run_hashes.txt` is untouched |
| Development checks | `code/run_devchecks.py` | S1 checks DEV-1 to DEV-4 (§5) |

**Executor guarantees, each tested in `test_campaign.py`:**
- **Every run gets a row.** Every scheduled run gets a `runs.csv` row, valid or not. B0 runs even when S-eco is unavailable.
- **Failures are recorded, not retried.** Exceptions go to `errors.csv` with the traceback and are not retried. A non-finite run keeps its raw trace and becomes an invalid row.
- **Matched arms.** Both arms of a condition share the gain, plant, limits, motor and initial state, and that state is read from y0.
- **Profiles are designed once, on P1.** Profiles are designed on P1 once per (cycle, motor, limits, draw) and reused at P3 (D2).
- **Records written as they finish.** Each condition's record is written when it finishes. Post-run outputs: a SHA-256 list and `manifest.json` (environment record, frozen and upstream hashes, code hashes, denominator).
- **Official IDs only in campaign mode.** Official IDs (`R4H3-…`) are refused outside campaign mode, and non-official IDs inside it.
- **Open decisions refuse first.** A missing decision (AMB-14 for SEN, AMB-24 for P3) refuses before any run.

## 4. Tests

| Run | Time | Result | Notes |
|---|---|---|---|
| 3 | 05:58 | 67 passed | existing suite after VC-01 to VC-03 |
| 4 | 06:06 | **138 passed, 1 failed** | `test_validator_cannot_be_satisfied_by_a_planner_flag` text-searched the validator source for "planner" and matched a comment. A test defect: the validator imports no planner. Log kept: `logs/pytest_run4.txt` and `.xml` |
| 5 | 06:10 | **139 passed, 0 failed, 0 skipped** (214 s) | the test now checks imports with an AST; no code changed. Basis of `logs/readiness_gate_v2.json` (06:14) |

Run 5 by file: campaign 18, checks 21, regressions 26, inputs and sensitivity 7, plus the 67 original tests (validator 16, evaluator 13, closed loop 12, frozen and task 8, planner 7, scope 6, traces 5). Runs 1 and 2 from the smoke-test phase are kept unchanged.

**Limitations:**
- The executor is tested on toy tasks: a 16 s two-segment task, a deliberately time-infeasible task, and a P3 plant weakened to T_max = 2 N·m.
- Full-length behaviour is shown only by DEV-4 (§5).
- S2 is in no test beyond its input hash and d_ref/T_ref.

## 5. Development checks on S1 (not campaign runs)

**Run:** 06:14:53–06:20:54, `python -I -B code/run_devchecks.py`, under the readiness gate (its hash is recorded). Output: `outputs/dev_readiness_20261028_061453/` (`devchecks.json`, run files, the trace and spec of DEV-4, the separate-process recomputation, and a post-run SHA-256 list). Console: `logs/devchecks_console.txt`.

**Scope limits:**
- S1 (in-sample), M0, L-R1 only.
- No S2.
- No baseline-versus-eco difference, S_found or saving is computed or written. DEV-2 records only each run's own QS-versus-dynamic agreement. DEV-3 records only the eco profile's change between grids.
- None of these counts toward the 170 runs (D4).

| Check | Purpose | Result |
|---|---|---|
| **DEV-1**: re-validate the two smoke-test profiles under the VC-01 validator on P1, and their QS feasibility on the P3 plant | D1 and D3 on real-length S1 segments; exercises the D5 feasibility path | **B0 (v_b):** valid; departures 10, 53, 137 and 289 s; no early arrival; 0 extra stops. **B3 (S-eco):** valid; departures 10, 53, 137 and 289 s exactly; arrivals 0.157, 0.308, 0.483 and 0.076 s early; at rest while waiting (max 0.0 m/s); 0 extra-stop knots. Both profiles are QS-feasible on P3 (0 infeasible pieces) |
| **DEV-2**: QS energy of each smoke profile on P1 against its existing 1 ms dynamic energy, per reference km | The protocol §9 QS-versus-dynamic rule on real runs | B0: +0.53 %, B3: +0.20 %; both within ±1 % (M0, decisive). The QS energy of the S-eco knots equals the planner's DP sum to 1.2e-14 relative (A1-15) |
| **DEV-3**: S1 S-eco at (2 m, 0.1 m/s) and (1 m, 0.05 m/s) | Runtime, validity and size of the fine-grid planner job | Coarse: 1.0 s, valid, 0 extra stops. Fine: 6.5 s, valid, 0 extra stops; segment time margins 0.108, 0.156, 0.421 and 0.015 s; 42 λ evaluations per segment. The eco profile's own QS energy changes by −0.24 % from coarse to fine (an eco-arm quantity, not ΔS_found) |
| **DEV-4**: one full S1 run (B0 tracking v_b) at dt = 0.5 ms through `campaign.run_arm`, then `recompute_from_traces.py` in a separate process | The full-length 0.5 ms path (VC-02), the per-run spec file, v2 trace and recomputation at scale | 354 s wall time. 324,001 samples at 1 ms, from 648,000 steps of 0.5 ms. Every §8.2 flag passes, so the run is credited. Recomputation passes both in-process and in the separate process: every protocol-group and diagnostic check, 0 failed. Separate-process values: E_chem 6.1e-7 relative, distance 4.7e-12, trip time 0, I_over 0, RMSE 2.5e-15, friction 2.7e-8 Wh, closure from the trace equal to the simulator. The separate process exits 0 with 1 run recomputed, 0 protocol failures and **no simulator module imported**. The run's energy differs from the 1 ms smoke B0 run by −1.7e-10 relative. This is one arm only, not the §9 paired check |

**What this establishes.**
- The 0.5 ms and recomputation infrastructure works at full cycle length.
- The validator accepts real planner profiles under exact timing.
- The fine-grid planner is fast (seconds on S1).
- QS-versus-dynamic is computed as R3 defined it.

**What it does not establish.** None of the protocol's S2 criteria: |ΔS_found| < 0.2 pp, paired ΔE_rel change < 0.01 pp, and ±1 % on S2 profiles. Those are evaluated in the campaign (AMB-18).

## 6. What is ready and what is not

| Component | State |
|---|---|
| D1, D3 validation | implemented, tested; S1 smoke profiles re-validated (DEV-1) |
| D2 matched P3 design | implemented, tested on toy tasks |
| D4 development/confirmatory separation | implemented (ID guard, dry-run check) |
| D5 classification and denominators | implemented and tested; **the P3 rule awaits AMB-24** |
| Canonical cycle inputs | established and hashed; no blocker |
| QS vs dynamic | implemented; validated on S1 (DEV-2) |
| Planner grid convergence | implemented; S1 runtime and validity at both grids (DEV-3). The protocol's |ΔS_found| check runs on S2 in the campaign |
| 0.5 ms time step | implemented; full S1 run traced and recomputed (DEV-4). The protocol's paired-ΔE_rel check runs on S2 in the campaign |
| Campaign runner | dry run passes; campaign mode refuses (amendment not issued; 2 review items) |
| Sensitivity design | specified, table hashed; **gain basis awaits AMB-14** |
