# R4 H3 pilot: independent code review

**Date:** 2026-10-28.
**Scope:** `code/r4h3/` and `code/tests/`, plus the frozen and upstream modules they import (`r3_lib.py`, `eureka.controllers` / `plant` / `params` / `cycles`, `rebuild.model` / `run`).
**Reference text:** protocol v1 (`../R4_20261028_preflight/03_R4_protocol_v1.md`, SHA-256 `f9826318…2dab`, verified unchanged) and the owner's decisions D1–D5.

## 1. Method

| Reviewer | How | Record |
|---|---|---|
| **A: separate read-only agent** | Started with no knowledge of the implementation. Used only Read, Grep and Glob; ran and wrote nothing. Answered 13 set questions, including the 11 attention points of the readiness brief | Verbatim report: `review/CR-A_review_agent_report_20261028.md` (findings CR-A1 … A21) |
| **B: author re-derivation** | Re-opened the source and derived each check from the protocol text and the R1–R3 equations, not from memory | Findings CR-B1 … B8 below |

**Review baseline.**
- The code as it stood after the smoke test is archived unchanged in `archive/rev0_20261028_0135/` (25 files; every hash equals the v1 manifest and the smoke-test gate record).
- Reviewer A read that version and then the current one; changes were being made during its review.
- Every change since rev0 is a versioned change (VC-01 … VC-08 in `06_readiness_implementation_report.md`) with regression tests.
- No change was made only to make a test pass. The one failing test of run 4 was a defect in the new test itself (§4).

## 2. Verdict

| Severity | Found | Resolved in code with tests | Converted to an owner decision | Mitigated; residual needs owner acceptance | Documented (NOTE / MINOR) |
|---|---|---|---|---|---|
| CRITICAL | 0 | – | – | – | – |
| MAJOR | 7 (A) + 4 (B) | 9 | 1 (CR-A2 → AMB-24) | 1 (CR-A6) | – |
| MINOR | 9 (A) + 3 (B) | 11 | – | – | 1 (CR-A13) |
| NOTE | 5 (A) + 1 (B) | – | – | – | 6 |

**No unresolved CRITICAL issue.**

Two MAJOR items still need the owner, and `config/code_review_status_v1.json` records them (`open_major: 2`):
- **CR-A2:** the meaning of "infeasible on P3".
- **CR-A6:** the residual common-mode dependence of the evaluator.

`campaign.preconditions()` blocks while either is open.

## 3. Findings and responses

### 3.1 MAJOR

| ID | Finding (short) | Response | Change | Test(s) | Status |
|---|---|---|---|---|---|
| CR-A1 | The 0.5 ms path passed the integration step as the trace step, so every convergence run would fail evaluation | Traces are sampled at 1 ms for every run (§10.3), so the specification passes the trace step, and meta records `dt_s` and `trace_dt_s` separately. The evaluator refuses a trace whose spacing differs from the declared step. Fixed in the slice driver and the campaign executor | VC-02, VC-03 | `test_half_ms_loop_equals_frozen_simulate_and_traces_at_1ms[M0, M2]` (bitwise equal to `r3_lib.simulate(dt=0.0005)`); `test_decimated_trace_is_recomputed_within_protocol_tolerances[0.0005]`; `test_evaluator_refuses_mismatched_trace_step`; `test_half_ms_condition_is_traced_at_1ms_and_evaluated`; DEV-4 (full S1 run at 0.5 ms) | **resolved** |
| CR-A2 | QS feasibility on P3 decided the outcome ahead of §8.2; D5 does not define "infeasible" | Both readings are implemented: (a) QS step feasibility on P3, (b) §8.2 only. `classify_pair` refuses a P3 condition unless the issued amendment names one. Both arms are always run and retained, so neither reading changes what is recorded | checks, campaign | `test_classification[...]` (both rules), `test_p3_needs_an_issued_rule_and_both_feasibility_flags`, `test_p3_profile_infeasible_on_the_evaluated_plant_is_run_and_classified`, `test_missing_open_decisions_refuse_before_any_run` | **owner decision AMB-24** (blocks the P3 set) |
| CR-A3 | v_b went through the S-eco validator, so B0 would be rejected whenever v_b ≠ v_ref | In the campaign v_b is validated and reported (§9 "baseline sanity") but never rejected. B0 runs whenever v_b exists, and §8.2 decides its validity. The §5.2 planner constraints apply to S-eco only. The rev0 slice driver keeps its old behaviour (CR-B8) | campaign | `test_time_infeasible_profile_is_unavailable_and_b0_still_runs`; baseline-sanity fields in `conditions.csv` | **resolved** |
| CR-A4 | A non-finite run left no row, no trace and no `errors.csv` | Non-finite runs keep their raw trace (`<run_id>.nonfinite.npz`) and become invalid rows. Exceptions go to `errors.csv` with the traceback and are never retried. Each condition's record is written as it finishes. A post-run SHA-256 list is written | campaign | `test_an_exception_is_recorded_not_retried`, `test_every_scheduled_run_has_a_row_and_the_denominator_is_kept` | **resolved** |
| CR-A5 | No campaign driver; B0 dropped when S-eco unavailable; classification untested | `campaign.execute_schedule` / `run_condition` always run B0, give every condition a status, keep every run in `runs.csv`, write `errors.csv`, and never compute ΔE. `paired_delta` refuses non-COMPARABLE conditions | campaign, checks | `test_campaign.py` (18 tests), `test_checks.py` (21 tests) | **resolved** |
| CR-A6 | The evaluator was not a "separate script reading only the saved traces"; it shared formulas, parameter objects and r3_lib-computed channels | Mitigated (see the table below) | VC-05, new script | `test_independent_recomputation_runs_as_a_separate_process`; `test_protocol_disagreement_decides[...]`; `test_decimated_trace_is_recomputed_within_protocol_tolerances` | **mitigated; residual needs owner acceptance** |
| CR-A7 | Upstream physics and data files were not hash-checked at runtime | `frozen.UPSTREAM_SHA256` holds 9 files (eureka plant / controllers / params / cycles, rebuild model / run, R1.yaml, parameters.yaml, profiles.yaml). Their values were recorded by R1 and are unchanged in the preflight snapshot. `load_r3_lib()` checks them before importing. `inputs.verify_all()` runs in official mode, in the readiness gate and in the dry run | VC-07 | `test_upstream_inputs_are_hash_checked` | **resolved** |
| CR-B1 | rev0 validator used an invented "at rest" threshold of 1e-12 m/s | Replaced by the frozen §5.1 rule v ≤ 1e-9 m/s (D1) | VC-01 | `test_rest_threshold_is_the_frozen_protocol_5_1_rule`, `test_interior_knot_below_the_rest_rule_is_an_extra_stop`, `test_rest_knot_within_the_rest_rule_is_at_rest` | **resolved** |
| CR-B2 | rev0 validator compared times with a 1e-9 s tolerance | All time comparisons exact (D3) | VC-01 | `test_arrival_one_tenth_of_a_nanosecond_late_is_rejected`, `test_departure_one_tenth_of_a_nanosecond_early_is_rejected` | **resolved** |
| CR-B3 | rev0 `compare_with_simulator().all_ok` combined §9 quantities with author diagnostics. Using it to credit runs would add exclusion criteria the protocol does not have | `protocol_ok` covers only the §9 quantities and decides crediting. `diagnostics_ok` is reported and flagged. The three tolerances §9 does not state are declared in draft A1-12 | VC-04 | `test_diagnostic_disagreement_is_flagged_but_does_not_decide_crediting`, `test_protocol_check_set_matches_protocol_9_and_the_campaign_record` | **resolved** (tolerances need owner acceptance, A1-12) |
| CR-B4 | rev0 traced every 0.5 ms step, contrary to §10.3 ("every second step for the 0.5 ms convergence runs") | 1 ms decimation | VC-02 | as CR-A1 | **resolved** |

**CR-A6 mitigation and residual.**

| Remedy suggested by reviewer A | Done |
|---|---|
| Separate script reading only the saved traces | Yes. `code/recompute_from_traces.py` runs in its own process on `traces/<run_id>.npz`, `traces/<run_id>.spec.json` and `runs.csv`. It asserts that no `r3_lib`, `eureka`, `rebuild`, planner, config or closed-loop module was imported. Proven in a test and in DEV-4 |
| Per-run frozen spec | Yes. Every trace has a `.spec.json` with every parameter the evaluator uses, the §8.2 rules and the tracked profile's knots. Its SHA-256 is the trace's `config_sha256` |
| Simulator-side C-rate I_over and min V_t | Yes (`closedloop.trace_constraint_metrics`, from the r3_lib current and terminal voltage). The deciding I_over and the constraint flag are now protocol checks |
| Check v_tracked against the knots | Yes (diagnostic `tracked_profile_abs_ms`, 1e-9 m/s) |
| Recompute or check t_neg / t_pos | **No.** The friction start value and the battery-limited fraction use the traced torque limits |

**Residual common mode**, which cannot be removed without a second, independently written plant model:
- The evaluator's laws (battery current, motor loss, window limit, friction, gear) are rewritten from the same R1–R3 model basis.
- It reads the integrated states (v, T, V1) and the r3_lib-computed torque limits from the trace.

So the recomputation verifies bookkeeping, integration, sampling and metric definitions. It does not verify the plant dynamics, the parameter values or the torque-limit inversion. Those rest on R1–R3's own verification (bitwise port tests, the controller cross-check) and on the frozen hashes. The owner should accept this scope or ask for an independent limit recomputation.

### 3.2 MINOR

| ID | Finding | Response | Status |
|---|---|---|---|
| CR-A8 | `comparable` ignored the recomputation | `credited = comparable and recompute_protocol_ok`, in `evaluation.csv` and `runs.csv` | resolved |
| CR-A9 | Friction rule approximate; several tolerances invented | Friction, current, friction-power, window-I_over and battery-limited tolerances are now diagnostics only (VC-04). The protocol group's unstated tolerances are declared (A1-12). The per-interval trapezoid is second order; the friction comparison is diagnostic, so it cannot exclude a run | resolved / declared |
| CR-A10 | η_regen braking work not recomputable; includes viscous drag while coasting | Evaluator recomputes the wheel braking power from (T, ω, v) with B_m and η_g (VC-05). Definition stated in A1-17 | resolved / clarified |
| CR-A11 | `runs.csv` shortfall measured against the tracked profile; §8.2 flags absent | Renamed `shortfall_vs_tracked_profile_pct`; `shortfall_vs_dref_pct` kept; §8.2 flags and `credited` copied into `runs.csv` | resolved |
| CR-A12 | Traces not self-describing; closure integrators missing; initial conditions hard-coded | Per-run spec file; trace schema v2 adds E_rr, E_aero, E_gear, E_visc and E_regen (VC-08), so closure can be recomputed from the trace (diagnostic); initial conditions read from y0 | resolved |
| CR-A13 | Exact arrival comparison against a planner using a different floating-point sum | Kept exact, as D3 requires ("no extra timing tolerances"). The risk is a spurious "unavailable", which is conservative. Recorded as AMB-28. Smoke-test margins are ≥ 0.076 s | documented |
| CR-A14 | Gate path fixed and not versioned; new modules untested | Versioned readiness gate `logs/readiness_gate_v2.json`; the smoke-test gate record is untouched. The campaign gate is written in a fresh directory (A1-13). 72 new tests: campaign 18, checks 21, inputs and sensitivity 7, regressions 26 | resolved |
| CR-A15 | Baseline sanity only logged | `conditions.csv`: equals reference, W, boundary hit, max deviation, distance error, validator remarks | resolved |
| CR-A16 | No pip freeze, `errors.csv` or post-run manifest | `env_record()` (installed distributions via `importlib.metadata`, A1-18), `errors.csv`, `zz_post_run_sha256.csv` (covers `manifest.json`; excludes itself) | resolved |
| CR-B5 | `batt_limited_time_frac` counted any torque limit, so it was not "battery-limited" (§7.2) | R1–R3 definition `batt_limited_frac`; old quantity renamed `limit_active_sample_frac` (VC-03) | resolved |
| CR-B6 | §7.2 max \|e\| against v_ref missing | `max_abs_err_vs_task_ref_ms` (VC-03) | resolved |
| CR-B7 | The deciding (C-rate) I_over was compared with nothing on the simulator side | VC-05 | resolved |

### 3.3 NOTE

| ID | Note | Where handled |
|---|---|---|
| CR-A17 | v_b computed on the evaluated plant in the rev0 slice | D2: the campaign designs v_b on P1 |
| CR-A18 | The DP can produce interior stops (tanh smoothing near 0) | The validator rejects them (D1); the profile is then "unavailable". DEV-3 checked S1 at both grids |
| CR-A19 | No dynamic check of the planned early-arrival wait | §8.2 governs the dynamic run; AMB-26 |
| CR-A20 | M2 profile designed on the M2 QS model | follows §5.2 literally; AMB-27. `qs_usable` now drives the QS-vs-dynamic decisiveness |
| CR-A21 | Sensitivity gain basis refused while AMB-14 is open | as intended |
| CR-B8 | The slice driver (`slice.py`, `run_slice.py`) keeps its rev0 semantics: it validates v_b strictly and computes v_b on the evaluated plant. It is retained as the D4 development driver that produced the smoke test, with only the CR-A1 and VC-05 interface fixes; the campaign never calls it | documented here |

## 4. Test evidence

| Run | Code state | Result | Log |
|---|---|---|---|
| 1 | rev0 | 64 passed, 3 failed (friction ZOH defect, fixed then) | `logs/pytest_run1.*` |
| 2 | rev0 | 67 passed | `logs/pytest_run2.*` (smoke-test gate) |
| 3 | after VC-01–03, before the new modules | 67 passed | `logs/pytest_run3.*` |
| 4 | full readiness code | 138 passed, **1 failed**: `test_validator_cannot_be_satisfied_by_a_planner_flag`. The test text-searched the validator source for "planner" and matched a comment citing the frozen planner's tolerance; the code was correct | `logs/pytest_run4.*` |
| 5 | test 4's search replaced by an import check (AST); no code change | **139 passed, 0 failed** | `logs/pytest_run5.*` (readiness gate `logs/readiness_gate_v2.json`) |

**Coverage of the brief's failure modes now includes:**
- interior stops below the rest rule;
- arrival and departure off by 1e-10 s;
- creep after an early arrival;
- the 0.5 ms path (bitwise to r3_lib, then evaluated);
- P3 (gain identity, R0 law, bitwise loop at SoH 0.8);
- disagreement on each deciding flag;
- non-finite and exception handling;
- profile-unavailable conditions keeping B0;
- the separate-process recomputation;
- tampered cycle inputs;
- amendment blocks that try to override a value.

**Not covered:**
- interior stops on real-length S2 segments: not tested, to keep S2 untouched;
- a full-cycle bitwise port test, because the 4 s profile test plus the full-length DEV-4 recomputation were judged sufficient;
- a non-finite run produced by a real plant: none exists; covered only by the code path's construction.

## 5. Answers to the readiness brief's attention points

| Point | Answer |
|---|---|
| Planner can create unregistered stops? | Yes (CR-A18). The validator catches every one from the knots alone and rejects the profile (D1) |
| Stop validator verifies stationary waiting and timing independently? | Yes, exactly, with no timing tolerance; planner flags are not an input (VC-01) |
| Fixed-LQR gain identical in both arms, not retuned at P3? | Yes. P1 gain for both arms. The gain does not depend on SoH, k_r0, R0, limits or motor, so P1 and P3 designs are bitwise equal (test). The SEN gain basis is open (AMB-14) |
| P3 failures retained in the denominator and excluded from energy comparisons? | Yes (CR-A4, A5, D5). `paired_delta` refuses every status except COMPARABLE. The P3 rule awaits AMB-24 |
| Matched plant states and initial conditions? | Yes, the same objects for both arms. The initial state (v 0, T 0, V1 0, SoC 0.8, z 0) is read from y0 and is equal across arms (test) |
| Evaluator reproduces the required equations and units? | Yes for §7.1–7.3 and §8.2 (reviewer A Q6). Battery-limited fraction and max \|e\| against v_ref corrected or added (VC-03) |
| Trace records everything needed? | With schema v2 and the per-run spec, yes, except an independent torque-limit computation (CR-A6 residual) |
| Shared source or assumptions? | Yes, listed under CR-A6. Mitigated; the residual is stated |
| Friction-integration defect fixed for piecewise-constant torque? | Yes. Each 1 ms interval uses the command held over it; alignment verified by reviewer A (Q8), also at 0.5 ms. The rule is second order; on the two S1 smoke runs the friction energy agreed to 3.5e-8 Wh and 0 Wh. The check is a diagnostic |
| Tests exercise real failure modes? | Now largely yes (§4). Before readiness they were mostly synthetic (reviewer A Q10) |
| Anything writes into frozen or legacy trees? | No (reviewer A Q11). The before/after hash comparison of 24,914 files is in `08_gate_status_summary.md`. `-B` is used throughout; no `__pycache__` was created |
