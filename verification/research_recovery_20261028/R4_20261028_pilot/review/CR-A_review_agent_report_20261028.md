# Read-only review agent: final report (verbatim)

**Provenance.**
- **Who:** a separate AI review agent (the "Plan" agent type: no Edit/Write tools), started 2026-10-28 at about 05:33 local time and finished at about 05:50.
- **Instructions:** use only Read, Grep and Glob; run nothing and write nothing.
- **What it reviewed:** the frozen protocol and the code under `code/r4h3/` and `code/tests/`. While it was reading, the author was changing the code (validator VC-01, closedloop VC-02, evaluator VC-03/04, and new modules), so its findings refer to the state at that time. It says so itself.
- **Format:** the text below is its final message, reproduced without edits except that the uniform indentation the message relay adds to every line was removed. File references in it are relative to `code/`.
- **The author's responses** are in `../04_independent_code_review.md`.

---

I found no CRITICAL defect in the code as it stands. Nothing in the current paths computes a paired energy difference for an invalid arm, and the gain, plant, limit set, motor model and initial conditions match between the two arms. But seven MAJOR issues must be fixed or explicitly accepted before the campaign. The most urgent are a broken 0.5 ms evaluation path, a QS-feasibility gate on P3 that conflicts with draft A1-10 and is not defined by D5, and missing campaign accounting.

I used only Read, Grep and Glob, ran nothing and wrote nothing.

**The code changed while I was reviewing it.** `archive/rev0_20261028_0135/` holds the version I first read. After that:
- `validator.py`, `evaluator.py`, `closedloop.py`, `slice.py` and three test files were rewritten.
- `checks.py`, `inputs.py`, `sensitivity.py`, `build_cycle_inputs.py`, `inputs/cycles/*` and `logs/pytest_run3.*` appeared.
- I re-read every changed or new file, and the findings below refer to the current text. Where an issue existed only in rev0, I say so.
- `frozen.py`, `config.py`, `task.py`, `planner.py` and `traces.py` were unchanged at my last check (confirmed for `config.py`; inferred from modification order for the rest).
- `logs/pytest_run3.txt` says "67 passed". I could not verify which code that run covered. No tests exist for `checks.py`, `inputs.py` or `sensitivity.py`.
- `logs/pre_run_hashes.txt` is now stale: the code no longer matches it.

Code paths below are relative to `D:\EURÉKA 2026 - KT\verification\research_recovery_20261028\R4_20261028_pilot\code\`. `r3_lib` is the R3 `r3_lib.py`.

## Findings

**CR-A1 MAJOR — the 0.5 ms convergence path cannot be evaluated.** `r4h3/slice.py:142,170,192`; `r4h3/closedloop.py:23,64-66,117`; `r4h3/evaluator.py:79-83`.
- **Defect:** `simulate_traced` now records at 1 ms (`TRACE_DT`). `slice.py` still passes the integration step (0.5 ms) to the evaluator as `dt_s` and writes it to the trace meta.
- **Failure:** all 6 time-step runs reach `evaluate_trace`, which raises because the trace step (1 ms) is not 0.5 ms. Each becomes ERROR with no `runs.csv` row, so `checks.timestep_check` can never run. The meta also mislabels the trace step. No test runs `dt=0.0005`.
- **Remedy:** pass `out["trace_dt"]` to `eval_spec` and to the meta (separate `trace_dt_s` from `dt_s`). Add a 0.5 ms test that compares bitwise with `r3_lib.simulate(dt=0.0005)` and then writes, reads and evaluates the trace.

**CR-A2 MAJOR — QS feasibility on the P3 plant decides the outcome before §8.2.**
- **Defect:** `slice.py:159,164-166` validates the P1-designed profile against the evaluated plant (P3 on P3 runs) and stops with no dynamic run. `checks.py:104-110` classifies `ECO_INFEASIBLE_ON_P3` or `BASELINE_INFEASIBLE_ON_P3` from QS flags ahead of the §8.2 flags. This contradicts draft A1-10 ("still run the dynamic case … comparability decided by §8.2 alone"). D5 does not say that "infeasible" means QS-infeasible.
- **Failure:** a profile with one QS-infeasible piece on P3 is never run, or is classified infeasible even though the closed loop would pass §8.2. P3 counts change.
- **Also inconsistent:** `slice.py` checks B3 against the evaluated plant, while `checks.py:75` assumes the validator ran on the design plant and that P3 feasibility is a separate flag.
- **Remedy:** owner ruling on what "infeasible on P3" means. Then implement it once, always run both arms dynamically, and record the QS flag either way.

**CR-A3 MAJOR — the baseline v_b is put through the S-eco validator.** `slice.py:149`; `validator.py:64,70,101-112,121`.
- **Defect:** v_b must meet D_k equality, the segment speed cap, the acceleration bounds, exact departure timing and exact v ≥ 0. Protocol §9 "Baseline sanity" says that if v_b ≠ v_ref the shortfall and deviation are reported, not that B0 is rejected.
- **Failure:** whenever v_b ≠ v_ref (P3, S1, or a sensitivity draw), B0 fails validation and nothing runs. `r3_lib.track_dp` accepts speeds ≥ −1e-12 (`r3_lib.py:536`), so offsets such as 0.6 − 12×0.05 = −1.1e-16 also fail the exact "negative speed" test.
- **Note:** this is latent on S2 at P1, where the code and R3 indicate v_b = v_ref.
- **Remedy:** use a separate baseline check (finite, QS-feasible on its own plant, at rest at the reference rest samples, start and end at rest) and record the deviation instead of rejecting.

**CR-A4 MAJOR — runs that blow up cannot be recorded.** `r4h3/traces.py:79-82`; `slice.py:197,219-221,231-235`.
- **Defect:** `write_trace` refuses non-finite data, and rows are written only after both arms finish.
- **Failure:** a run whose states go non-finite raises an exception. Neither arm then gets a `runs.csv` or `evaluation.csv` row and the trace is lost. No `errors.csv` is written either; the traceback goes only into the manifest. This breaks protocol §10.4 ("every run is written") and D5's denominator rule.
- **Remedy:** write invalid traces (flag them, or truncate and record the index), write each run's row as it finishes, and write `errors.csv`.

**CR-A5 MAJOR — no campaign driver; conditions and B0 runs are dropped.** `slice.py:154-156,164-166`; `r4h3/checks.py:93-137`.
- **Defect:** when the S-eco profile is unavailable or invalid, the slice returns before the B0 run. `classify_pair`, `paired_delta` and `denominator` are not wired into any driver and have no tests.
- **Failure:** `PROFILE_UNAVAILABLE` conditions have no B0 result, so baseline sanity and QS-vs-dynamic for B0 are missing. A hand-written loop could silently shrink the denominator.
- **Remedy:** a campaign runner that always runs B0, assigns each condition a status from `checks.STATUSES`, writes `errors.csv`, and has unit tests for the classification order and for `paired_delta` refusing non-COMPARABLE pairs.

**CR-A6 MAJOR — the evaluator does not meet protocol §9's "separate script reading only the saved traces".**
- **Defect:** `evaluator.py:1-6` claims formulas "from the protocol text". The protocol contains no current, friction or window-limit equations; the evaluator copies the `r3_lib` and `rebuild` ones.
  - It runs in-process with a spec built from the same `Params`/`BatteryLimits` objects (`slice.py:91-100,170`).
  - It reads channels computed by `r3_lib`: `t_neg_Nm`, `t_pos_Nm`, `P_fric_W`, `P_regen_wheel_W`, `v_tracked_mps` (`evaluator.py:92,98,109-112`).
- **Single computations:** the deciding I_over (C-rate) and min V_t flags are computed only once. `sim_stop_ok` (`slice.py:78-88`) reads the same `v_mps` trace channel.
- **Remedy:** a standalone script reading the traces plus a frozen spec file written from the protocol and ledger. Add the C-rate I_over and min V_t on the simulator side. Check `v_tracked` against the knots in `profiles.npz`. Recompute or check `t_neg`/`t_pos`.

**CR-A7 MAJOR — physics inputs are not verified when a process starts.** `r4h3/frozen.py:24-28,57-64`; `slice.py:32-35,239-240`; `r4h3/inputs.py:58-74`.
- **Defect:** only the protocol, `r3_lib` and the M1 curve are hash-checked. Not checked: `src/eureka/*.py` (plant, controllers, params, cycles), `rebuild/model.py` and `run.py`, `configs/parameters.yaml` (R1 recorded `0efe2d1a…`), `configs/cycles/profiles.yaml` (`90a496a3…`), and `configs/R1.yaml`.
  - The gate binds only pilot code.
  - `inputs.verify_all()` is never called.
  - Tests do not check the gain inputs (v0, e_max, T_bryson, z_max) or v_eps.
- **Failure:** an edit to any of these after the gate changes every run without being noticed.
- **Remedy:** add these files to `FROZEN_SHA256`, call `inputs.verify_all()` at start, and record all of them in the manifest.

**CR-A8 MINOR — the `comparable` column ignores recomputation.** `slice.py:202-203` leaves the protocol §9 recomputation result out of `comparable`; `checks.py:115` handles it, so a reader of `evaluation.csv` alone could credit an uncredited run. Rename the column and add a `credited` field.

**CR-A9 MINOR — the friction recomputation is approximate and several tolerances are invented.** `evaluator.py:106-111,187-195`.
- The per-interval trapezoid is second-order, not exact.
- These tolerances are not in protocol §9: friction 1e-6 Wh absolute, trip time 1e-9 s, RMSE 1e-9 relative, window I_over 1e-4 A·s, batt-limited fraction 1e-12, current 1e-9 A, friction power 1e-9 W. Protocol §9 names only 1e-4 relative for energy, 1e-6 relative for distance, and identical flags.
- The friction-power check is circular: same law, same inputs.
- **Failure:** friction-heavy runs (P3, M2) may be marked as recomputation disagreements by an invented threshold.
- **Remedy:** declare these tolerances in the amendment, or use the 1e-4 relative energy rule.

**CR-A10 MINOR — the braking work used for η_regen is not independent.** `closedloop.py:44-49`, `evaluator.py:112`.
- `P_regen_wheel = max(−f_w·v, 0)` also counts motor viscous drag while coasting (T < B_m·w).
- The evaluator cannot recompute it because B_m and η_g are not in its spec.
- **Remedy:** define the term in the amendment, then add B_m and η_g to the spec and recompute.

**CR-A11 MINOR — `runs.csv` mislabels shortfall and lacks the §8.2 flags.**
- Its `shortfall_pct` comes from `r3_lib.sim_metrics` and is measured against the tracked profile's own distance (`r3_lib.py:250,264`), not d_ref.
- The §8.2 flags appear only in `evaluation.csv`; protocol §10.3 wants them in `runs.csv`.

**CR-A12 MINOR — traces cannot be re-evaluated on their own.** `traces.py:54-55`; `slice.py:191-195`; `closedloop.py:22`.
- The trace meta lacks R0 or k_r0, G, r_w, v_eps, T_max, P_max, the limit values and the motor spec, so re-evaluation also needs `run_config.json`.
- The E_rr, E_aero, E_gear, E_visc and E_regen integrators are not traced, so energy closure cannot be recomputed.
- `initial_conditions` is hard-coded rather than taken from the start state y0.

**CR-A13 MINOR — exact time comparisons and the planner use different arithmetic.**
- The planner accepts t_k ≤ T_k using `np.sum` of table times (`r3_lib.py:464`, `planner.py:43,54`).
- The knots are built with `cumsum` (`planner.py:71-72`), and the validator compares them exactly (`validator.py:105`).
- A t_k within a few ULPs of T_k (floating-point rounding) would be marked PROFILE_UNAVAILABLE. This is unlikely.

**CR-A14 MINOR — the gate process.**
- The gate path is fixed and `record_gate.py:21-22` refuses to overwrite it. The current code already differs from the gate record, so a new gate requires deleting the old evidence.
- The new modules have no tests.
- **Remedy:** versioned gate files.

**CR-A15 MINOR — the baseline sanity check is only logged.** `equals_reference` and the maximum deviation go only to the log (`slice.py:150`), and a run with `hit_boundary=True` continues (`planner.py:28`). Protocol §9 says "checked and recorded".

**CR-A16 MINOR — missing protocol §10.2 and §10.4 records.** There is no `pip freeze`, no `errors.csv`, and no post-run manifest that covers `manifest.json` itself (`slice.py:236-249`).

**CR-A17 NOTE — which plant v_b is computed on for P3.** `slice.py:148` computes v_b on the evaluated plant, which is draft A1-4 (not issued). D2 does not settle it.

**CR-A18 NOTE — the planner can propose extra stops; the validator catches them.**
- The DP can place v = 0 at an interior knot. Only 0→0 steps are excluded (`r3_lib.py:438`).
- The tanh(v/v_eps) smoothing (`r3_lib.py:294`, v_eps = 0.05 m/s) lowers QS rolling resistance near 0, so crawling or stopping can be optimal at small λ.
- The validator rejects such a profile, which then becomes "unavailable" and is not replaced (D1). No test covers segments the size of S1 or S2 segments.

**CR-A19 NOTE — dynamic checks around stops (D3).**
- No check that the vehicle in the B3 run is stationary during the early-arrival wait before t_a + 1 s.
- No check for unplanned stops inside a segment, or for the stop position in the closed-loop trace.
- Protocol §8.2 only requires the [t_a + 1, t_d] window.

**CR-A20 NOTE — M2 profile design.** The M2 S-eco profile is designed on the M2 QS model, although protocol §2.3 calls that model non-representative. `qs_usable` (`config.py:38`) is unused. This follows protocol §5.2 literally, so it needs a ruling rather than a fix.

**CR-A21 NOTE — sensitivity gain basis.** `sensitivity.gain_for_draw` (`sensitivity.py:79-88`) correctly refuses to choose a gain basis while AMB-14 is open.

## Answers to questions 1–13

**Q1. Extra stops.**
- **Can the planner create one?** Yes. `eco_segment_tables` sets `valid = (va+vb>0) & …` (`r3_lib.py:438`), which allows v→0 and 0→v at any step. `eco_segment_solve` fixes only the two endpoints (`r3_lib.py:450,460`). `planner.py` adds no constraint and still reports "ok". `test_planner.py:19-21` enumerates interior index 0, which confirms such paths are allowed.
- **Does the validator catch it independently?** Yes. It works from the knots alone: it counts knots ≤ REST_EPS between the first and last moving knot in [ks·h, ke·h] (`validator.py:86,94,109-110`), which is exact for piecewise-linear profiles. `slice.py:159,164-166` runs it on every "ok" profile and stops if it fails.
- **Is the threshold invented?** Not any more. It is now `task.REST_EPS = 1e-9`, the protocol §5.1 rule (`validator.py:21`). Rev0 used an invented 1e-12, replaced during this review. Planner speeds are either exactly 0 or at least about 0.1 m/s, so the threshold cannot change any planner outcome.

**Q2. Timing and tolerances.**
- **Timing is now exact** (`validator.py`):
  - start time = 0 (line 58);
  - end time = T_ref (60);
  - departure = ks·h (103);
  - arrival ≤ ke·h (105);
  - at rest from arrival to the segment end (95, 107);
  - at rest in every reference rest interval (73).
- **Tolerance constants:**

| Constant | Value | Source |
|---|---|---|
| REST_EPS | 1e-9 m/s | protocol §5.1 / `r3_lib.segments` |
| TOL_SEG_D | 1e-9 m per segment | protocol §9(b) |
| Total distance | 1e-9 × K m | sum of the §9(b) allowance; aggregation invented |
| TOL_A | 1e-9 m/s² | `r3_lib` (`r3_lib.py:438`) |
| Speed cap | exact | protocol §5.2 |
| Domain cap | 50/3.6 m/s | `02_model_basis.md`, not the protocol |
| v ≥ 0 | exact | invented; stricter than `r3_lib`'s −1e-12 (see CR-A3) |
| QS check | T ≤ t_pos + 1e-9 N·m, i ≤ i_d + 1e-6 A | `r3_lib` (`r3_lib.py:301,314`) |
| Evaluator float guards | 2 s − 1e-9; ±1e-12 s window edges; 1e-9 trace-step tolerance; 1e-12 period check | invented (`evaluator.py:82,85,166,169`) |

There is no time tolerance in the validator now. Rev0 had TOL_T = 1e-9 s.

**Q3. Gain.**
- The gain comes from `fixed_gain(config.params_for("P1"))` (`slice.py:169`), is used for both arms (line 182), and is recorded in the meta and run config.
- `eureka.controllers.gain` (`controllers.py:11-17,28-31,60-62`) depends on rho, Cd, A_f, v0, B_m, G, r_w, η_g, M and J_m (through M_eff), τ_T, Ts, e_max, T_bryson and z_max.
- It does not depend on k_r0, SoH, R0, the limits or the motor model. So it is identical on P1 and P3 and is never computed from the plant state.

**Q4. Matched arms.** Yes. The same `p`, `soh`, `lim`, `mm`, `dt` and `K` objects are used for both arms (`slice.py:136-142,178-182`). Initial state: all zeros, SoC 0.8, z = 0, which also gives V1 = 0, T = 0 and v = 0 (`closedloop.py:71-74`). The meta's initial conditions are hard-coded rather than read from that state (CR-A12).

**Q5. Paired differences and denominators.**
- **(a)** No path computes a paired difference for an invalid arm. The slice computes none, and `checks.paired_delta` refuses anything not COMPARABLE (`checks.py:120-123`); it is not wired in.
- **(b)** Yes, records can drop out:
  - unavailable profile → return before B0 (`slice.py:154-156`);
  - validation failure → no dynamic runs (164-166);
  - exception or non-finite trace → no rows (231-235; `traces.py:79-82`).
- **Missing for a P3 campaign:**
  - a runner and per-condition status table;
  - `errors.csv`;
  - the decision rules of §8.1;
  - wiring for baseline sanity, QS-vs-dynamic, grid convergence and S_found/S_max;
  - the 0.5 ms fix (CR-A1);
  - a ruling on P3 infeasibility (CR-A2);
  - `pip freeze`;
  - a post-run manifest.

**Q6. Metric definitions.**
- E_chem = trapezoid integral of V_oc·i (i > 0 on discharge), in J ÷ 3600 → Wh (`evaluator.py:100,120`).
- E_DC = trapezoid integral of V_t·i (123).
- Shortfall uses d_ref (128).
- RMSE and max |e| are taken at the control instants k·Ts, k = 0…steps, which matches the simulator count (91-92,129-130).
- Stop compliance (162-175) matches §8.2.
- I_over uses the C-rate limits c_dis·Q and c_ch·Q with Q not SoH-scaled, in A·s (114,142).
- V_t ≥ V_min − 0.01 V is checked at every 1 ms sample (144-145,156-157).
- η_regen is \|∫min(V_oc·i, 0)\| divided by (∫P_regen_wheel + friction) (112-113,137).
- Ah is in A·h, ∫i² in A²·s, Wh per km correct.
- Gaps: standstills shorter than 2 s are marked "reported" but carry only NaN values (167). The braking-work term is defined as in CR-A10.

**Q7. Independence of the evaluator.** Shared with the simulator:
- the parameter values, from the same `Params` object;
- the R0 ageing law, duplicated from `eureka/plant.py:84`;
- the battery-current quadratic and the motor-loss laws (copies; the M1 curve is the same hashed JSON);
- the window-limit law (copied from `rebuild/model.py:44-62`);
- the friction law (copied from `r3_lib.py:147`), with t_neg read from the trace;
- the starting values of `P_fric_W` and the `P_regen_wheel_W`, `t_pos_Nm` and `v_tracked_mps` channels;
- the task, rest intervals and d_ref (same `task.py`);
- the integrated states T, V1 and v.

Errors that would pass unnoticed:
- wrong parameters or ageing law;
- a wrong regen torque limit (t_neg, including the MotorModel table inversion);
- the wrong profile being tracked;
- a wrong task definition;
- any error in the dynamics themselves.

The check confirms the bookkeeping and integration only.

**Q8. Friction integration.**
- **Alignment is correct.** `rec()` runs before `rk4_step` (`closedloop.py:117-119`). Sample n therefore holds y(t_n) and the command held over [t_n, t_n + 1 ms]. `sub % every == 0`, so this also holds at 0.5 ms. The final sample's u is never applied.
- **The evaluator pairs correctly.** It uses the traced start value with an end value recomputed from (u_n, t_neg_{n+1}, v_{n+1}) (`evaluator.py:109-111`).
- **The rule is approximate, not exact.** It is a per-interval trapezoid (second order) against the simulator's RK4 with stage states; error grows at friction onset kinks and where the tanh term bends near v ≈ v_eps. Agreement rests on an invented 1e-6 Wh tolerance (CR-A9). At 0.5 ms the rule still applies, but evaluation currently fails (CR-A1).

**Q9. Is the trace sufficient?** The channels cover the protocol §10.3 list. Missing for recomputation without the simulator:
- the spec parameters (in `run_config.json`, not in the trace);
- the closure integrators;
- B_m and η_g, so P_regen_wheel and η_regen cannot be recomputed;
- the tracked-profile knots;
- an independent t_neg and t_pos;
- y0.

E_DC and P3 can be recomputed given `run_config.json`. The 0.5 ms runs are now decimated to 1 ms, but the spec and meta are wrong (CR-A1).

**Q10. Tests.** The failure-case tests are mostly synthetic: toy tasks, a 4 s profile, zeroed channels.

Untested failure modes:
- interior stops produced by the planner on real-length segments;
- v_b ≠ v_ref going through the validator;
- P3 (SoH 0.8, k_r0 3.5): the R0 used by the evaluator against BatchParams, and the closed loop at P3;
- any 0.5 ms path;
- a full-cycle port equivalence check;
- non-finite runs and the slice's stop/error paths;
- disagreement on the stop flag or the I_over flag;
- η_regen and the friction rule on analytic signals;
- `checks.py`, `inputs.py`, `sensitivity.py` and the gate check;
- ULP-level arrival timing;
- creep after an early arrival.

**Q11. Writes to protected trees.** I found no path that writes to the protocol, the preflight folder, the R3 tree, `src/` or legacy trees.
- `dont_write_bytecode` is set in `r4h3/__init__.py:9`, `frozen.py:60`, `conftest.py:3`, `run_slice.py:10`, `record_gate.py:13` and `build_cycle_inputs.py:28`. The last of these imports R3 `run_gates`, which has no side effects at import.
- `pytest.ini` uses `-p no:cacheprovider`.
- All outputs go under the pilot folder: `outputs/<tag>` (created with `exist_ok=False`), `logs/`, `inputs/cycles`. Existing files are never overwritten.
- If pytest is run without `-B`, the assertion rewriter may write `code/tests/__pycache__/conftest*.pyc` before `conftest.py` sets the flag. That folder is in the pilot, not a frozen tree.
- The `__pycache__` folders in `src/eureka` and `rebuild` already existed; they appear in `zz_pre_hash_project.csv` lines 179-191.

**Q12. Task construction.** It is identical to R3's `run_gates.reference()` (`task.py:76-77`; `run_gates.py:60-63`).
- T_ref is 213 s for S2 and 324 s for S1, so the YAML's final 0.278 s and 0.911 s are dropped (AMB-01).
- The sampled rest intervals are up to about 1 s shorter than the YAML ones.
- Both arms use the same task.
- `logs/build_cycle_inputs.txt` claims a bitwise match with R3's 24 retained paths and with the protocol's d_ref and T_ref. I treat this as the author's claim; it is consistent with the code.
- Remaining risk: `load_task` re-derives the task from `profiles.yaml` every time, and that file is not hash-checked at runtime (CR-A7).

**Q13. Other points.** `config.py`'s limit sets, P-states and motor models match R3 and the protocol. The `simulate_traced` port matches `r3_lib.simulate` line for line; `_signals` has no side effects. The bitwise test covers only 4 s at SoH 1 and 1 ms. See also CR-A2, A3, A13 and A20.
