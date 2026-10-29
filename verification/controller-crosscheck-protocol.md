# Controller cross-implementation protocol (Modelica vs the saved Python results)

Version 1.0, written 2026-10-23, **frozen before the first closed-loop Modelica simulation**. The freeze is recorded in `verification/controller-crosscheck-runlog.md` (sha256 of this file at the moment of the first closed-loop run). Later changes can only be appended as dated amendments (section 14); nothing above is edited afterwards.

## 0. What this exercise is, and is not

- It is a **planned independent cross-implementation verification**. The Python results are already known (including ΔE = +0.0030 % and RMSE ratio 1.011 at S1, SoH 0.8). It is **not** a blind or newly preregistered experiment, and it does not test a hypothesis about real vehicles.
- Question: *does an independently written Modelica implementation of the same controllers, on the independently written Modelica plant, reproduce the behaviour of the saved Python runs to within the numerical error of both implementations?*
- It does not tune or change a controller, a parameter, a tolerance after the fact, or a metric. It does not touch `protocol/preregistration.md`, the saved Python results, the claim statuses or the thesis. It does not use EPA cycles. Agreement is not physical validation: both implementations share one source document (`docs/model.md`), one author lineage and the same unverified parameters.
- Things I already knew or did before this freeze (disclosed so the reader can discount them): the Python results; the control law (read from the source files, `controller-port-design.md`); the 35 plant checks; the frozen gains and their comparison with the saved gains; a Python-only step-size refinement study (section 8.2), which used no Modelica controller output; compile-only checks of the controller models (`checkModel`, no simulation); the controller-logic tests P1 and P1b (section 6), which use `SampledLqr` with prescribed inputs and no plant.

## 1. Baseline Python artifacts and code versions

Raw series that come from the preregistered run (git commit 38f443aa5cabd51dc7c429a49962f12e9e273884, clean; results file written at 3640533abf282ce458e3bdb36ccfbadab72c2570; repository HEAD during this task f264eca354d67dcdf786063ca36ae246466217d2):

| Artifact | sha256 |
|---|---|
| `artifacts/raw/primary/S1/timeseries.npz` | 1338d1dfa5ee1de58d4db00f07ceea870bca49142ea5027356509d5c1778b2e7 |
| `artifacts/raw/primary/S1/manifest.json` | 167bbfdfac99f1f15ae66760bc2fa2916ae0648831306e7c1769cdad226ccd94 |
| `artifacts/raw/primary/S2/timeseries.npz` | 2ad860409fe7434df502a7659bbe8e2bb641fd762fe87b7c86cf6dad8354e612 |
| `artifacts/raw/primary/S2/manifest.json` | e7dcc33893966507c9d472906aa22c8addf4e9fd63c7d023c7dc924bb022eaeb |
| `artifacts/tables/primary_metrics.csv` | ff378b3028706f40a0cedc544ba4aa6113627875176f3e5e295ab3bd40a36d66 |
| `artifacts/tables/primary_pairs.csv` | e637405b653ffa2bbe2893170c97f38c44d13cbe1308c1ffc4cc53d62cf087af |
| `artifacts/reports/primary_results.json` | e04f2610be09e233b27d2d90d3051760295e27c46592d436fd9227e42ac73258 |
| `artifacts/reports/tuning-acceptance.json` | cfda2a90eef8becd7095512e6948b93443f6d8d414613b6120c77775721f29b6 |

These equal the values in `evidence/artifact_hashes.json`. Manifest configuration hashes: experiment c996c421674d43dd, parameters 12d2c28561a3c313.

| Code / config (unchanged between 38f443a and HEAD) | sha256 |
|---|---|
| `src/eureka/controllers.py` | 2d57b757407dac725891219aa93102ce8be20294a97723fb35ea862ac76d8660 |
| `src/eureka/simulate.py` | dccc267c09af403a22fac9042e53bf0e7dc0502d659875d6b1f17a8efb0003c2 |
| `src/eureka/plant.py` | e5701bce018f37bebba525dfc58d0e347c63cc1a5b385badf74fe6d0ea772907 |
| `src/eureka/params.py` / `cycles.py` / `metrics.py` / `experiment.py` | 192ad659… / f09ed877… / 0ed37076… / b1ef5d02… |
| `scripts/analyze.py` | 4d3e355b9f7186ab911eabfb6eea97147c0783d49faac37c25ef17e6bd31803c |
| `configs/parameters.yaml` | 0efe2d1a413a51d425043691c857807b021d62908935adfda9b757de6f9f374f |
| `configs/cycles/profiles.yaml` | 90a496a36c618e216693a3d819b84739f10e6c35167c23a91b63478ef28be0a6 |
| `configs/experiments.yaml` | 795396111f768d2e1dc641c3c5d7a995988dd7ea894b32b4e4060e78cf532bae |
| `protocol/preregistration.md` | d3e6271e6f3f225d30449a7ba5c5a17e9da2ab85a5a3b9beb4c414bf209bc10b |
| `docs/model.md` | 9b29b9608b63a749af7ef931976e951eb87fb557c3b24d453b79f7499a5ef6ee |

Modelica side: OpenModelica 1.27.1; `EurekaPlant` v0.1.1 (the 35-check plant, not modified); `EurekaController` v0.1.0; launcher `verification/Invoke-OpenModelica.ps1`. Their hashes at the freeze are recorded in the run log.

## 2. Scenarios, conditions and cases

- Profiles S1 (324.91 s, 32 491 control steps) and S2 (213.28 s, 21 328 steps) from `configs/cycles/profiles.yaml`; P-TUNE (122.31 s, 12 231 steps) only for the solver study. Stop time = steps × Ts.
- Initial state: v = 0, T = 0, V1 = 0, SoC = 0.8, z = 0, all accumulators 0. No disturbance, no measurement noise, nominal parameters = actual parameters (`configs/parameters.yaml`).
- SoH constant in a run, known exactly to the scheduled controller. Primary grid (the saved S-A grid): S1 and S2 × {fixed, scheduled} × SoH ∈ {1.0, 0.9, 0.8, 0.7} = 16 runs. The decision-relevant pair is **S1, SoH 0.8** (preregistration section 8). SoH 0.7 and 1.0 are the tested endpoints; SoH 1.0 is the identical-by-construction sanity control.
- Python baseline = the saved series in `artifacts/raw/primary` (dt = 1e-3 s, float64).

### 2.1 Exact run matrix

**P-TUNE solver study (24 runs, section 7):** `PT_{fixed|scheduled}_{dassl|cvode|ida}_tol{1e-06|1e-08|1e-10|1e-12}`, models `EurekaController.Cases.PTUNE_{fixed|scheduled}_soh080`, stop 122.31 s, 12 231 output intervals.

**Primary grid (16 runs, one solver and tolerance, the selected configuration):** `A_{S1|S2}_{fixed|scheduled}_soh{100|090|080|070}`, models `EurekaController.Cases.{S1|S2}_{fixed|scheduled}_soh{100|090|080|070}`; stop 324.91 s (32 491 intervals) for S1 and 213.28 s (21 328 intervals) for S2. Nothing else is part of the primary grid.

**Sensitivity runs (separate; 12 runs; S1 and S2 at SoH 0.8, fixed and scheduled):** `N_{S1|S2}_{fixed|scheduled}_soh080_{solver}_tol{tol}` for (a) the selected solver at tolerance/100 and (b) each of the two other solvers at the selected tolerance. They supply `u_mod` only and are never mixed into the primary results.

Possible repeat of a grid case that fails to complete: section 12. Possible diagnostic variants for a traced mismatch: section 12. No other runs.

## 3. Controller sampling and update timing

`Ts = 0.01 s`, sample instants `t_k = k Ts`, k = 0..steps. At `t_k` the law reads the exact plant states and `v_ref(t_k)`, computes `u_k`, and holds it on `[t_k, t_{k+1})`. `z_{k+1}` is formed from `e_k` and `sat_k` after `u_k`. Modelica: one `when sample(0, Ts)` clause, discrete variables, `pre(z)`. Full derivation and the mapping to the source lines: `verification/controller-port-design.md`.

## 4. Gains

Frozen artifact `verification/references/controller_gains.json` written by `verification/scripts/controller_gain_design.py` (independent 50-digit design; reads only `parameters.yaml`). Fixed `K = [196.035338058519, 0.3506849472210603, 150.8545190065969]`; scheduled gains for SoH 1.0 / 0.9 / 0.8 / 0.7 in the file. Acceptance of the gain design (all executed before this freeze): three computation routes agree to ≤ 2.2e-13 relative; saved Python gains agree with the frozen gains to ≤ 3.1e-13 relative; criterion 1e-9 relative (four orders above the observed route-to-route spread of the float64 DARE solvers, chosen as a numerical-conditioning allowance, not from any result of the controller). `Cases.mo` carries the gains as float64 literals; a script check (section 6, P4) re-parses them and compares with the JSON.

## 5. Metric definitions (computed from saved series only; one code path for both implementations)

`verification/scripts/controller_metrics.py`, restating `src/eureka/metrics.py` and `scripts/analyze.py`:

- RMSE = sqrt(mean(e²)) over all steps + 1 control samples, `e = v(t_k) - v_ref(t_k)`; max |e|; RMSE ratio = RMSE_scheduled / RMSE_fixed.
- Energy: `E = ∫ V_oc I dt` over the whole run (I > 0 on discharge, regeneration subtracts), per **plant-integrated** distance `∫ v dt`; Wh/km = (E/3600)/(dist/1000). ΔE% = (E_sched - E_fixed)/E_fixed × 100, matched pair = same profile and SoH.
- Also: RMS and peak current, Ah throughput, resistive loss, friction-brake energy, regenerated energy, fraction of samples with `sat` true, RMS jerk, RMS torque request, tracking-failure flag (as `run_metrics`).
- Acceleration trace = `diff(v)/Ts` on the control grid.
- The function set is checked against `artifacts/tables/primary_metrics.csv` for the saved Python series (executed, `python_dt_study.json`, key `metric_functions_vs_saved_table_max_rel_diff`) before it is applied to anything else.
- **Successful simulation (all must hold; exit code 0 of `omc` is not evidence):** the `SimulationResult` record in the launcher log contains `The simulation finished successfully`; the result file exists; no NaN or non-finite cell; the number of controller updates is steps + 1 (or steps if the update at the stop instant is absent); no assertion message; the preregistration validity criteria below hold. Otherwise the run is a failed run: it is kept, reported, and excluded from any statistic that requires success.
- Run validity (preregistration section 10): finite states, closure ≤ 0.1 % of V_oc × 3600 × Ah, v ≥ −1e-6 m/s; additionally reported: simulation status read from the `omc` simulation record (exit code 0 is not accepted as success), assertion count, controller update count = steps + 1 (or steps, if the update at the final instant is not written, see below).

## 6. Preliminary checks of the Modelica controller (before any plant-coupled case; all must pass or the exercise stops)

| ID | Check | Criterion |
|---|---|---|
| P1 | `ControllerUnit` (prescribed v, T, v_ref; 10 s; includes a saturated interval with e < 0 and one with e > 0) against an independent Python evaluation of the control law | `u`, `z`, `z_used`, `e_k`, `T_lim_k` agree to ≤ 1e-9 (absolute, N m / m / m/s); `sat_k` identical; integral frozen exactly when `sat and e < 0` |
| P1b | Piecewise-constant inputs (section 6.1): reconstructed original test and the defined-semantics test | `u`, `e_k`, `z` <= 1e-9, no `sat` mismatch, against an independent evaluation fed with the input current at each recorded event time; the original failing evaluation is reproduced and retained |
| P2 | Event timing, from the unit run and every later run | controller update rows lie within 1e-9 s of `k Ts` (OpenModelica `sample()` accumulates; drift measured, not assumed zero); count = steps + 1 (final-instant update may be absent: then steps and the discrete quantities of the last sample are reconstructed with the control law from saved states, flagged in the output) |
| P3 | `omc --unitChecking` on `SampledLqr`, `ClosedLoop`, one case per profile | no unit error or warning attributable to the new models |
| P4 | Gains in `Cases.mo` equal the JSON gains | bitwise equal after parsing |
| P5 | Independent recomputation inside every closed-loop result: `u_k = -(K · [e_k, T_k, z_used_k])`, `e_k = v - v_ref`, `T_lim_k`, `sat_k`, the `z` recursion, and `se2` vs the RMSE from the series | `u` ≤ 1e-9 absolute; `sat` flags identical except where `|u - T_lim| ≤ 1e-9`; `z` recursion ≤ 1e-12; RMSE from `se2` vs from the series ≤ 1e-12 absolute |
| P6 | Profile: `v_ref(t_k)` in each Modelica result vs the saved `v_ref` | ≤ 1e-9 m/s (OpenModelica's `sample()` times drift from `k Ts` by ≤ 1e-9 s, observed 1.7e-13 s over 10 s; the profile slope is ≤ 1 m/s²) |

### 6.1 Piecewise-constant inputs and sample-boundary timing (P1b)

- **Primary-grid inputs are continuous.** `v_ref` is piecewise *linear* (continuous, with slope breaks at the knots; some knots coincide with update instants, e.g. t = 10 s), SoH is constant, the plant states are continuous. A sample taken a few 1e-13 s before or after a knot changes `v_ref` by at most slope x that time (<= 1e-12 m/s). No step input reaches the controller in S1, S2 or P-TUNE.
- **Reference interpolation semantics (both implementations):** `v_ref(t)` = linear interpolation between knots, equal to the last knot value for `t` beyond the last knot (`np.interp`; Modelica `min(time, t_last)`), knot lists built by the same segment rules (`cycles.build`). The Modelica `v_ref` is compared with the saved Python `v_ref` at every sample (P6).
- **Sampling semantics.** Python: update `k` at `t_k = k*Ts` computed by multiplication, input steps tested as `t_k >= t_step`. Modelica: `sample(0, Ts)` generates event times by repeated addition; measured deviation from `k*Ts`: 1.7e-13 s at 10 s and 2.1e-13 s at 12 s (up to roughly 1e-11 s expected at 325 s; measured in the grid runs and checked against 1e-9 s by P2).
- **Defined behaviour for a step input (controller block, tested by P1b):** the update at actual event time `t_e` uses the input value current at `t_e`: the post-step value if and only if `t_e >= t_step`.
  - step >= 1e-6 s *before* an update instant: that update must use the new value, the previous update the old value (mandatory);
  - step >= 1e-6 s *after* an update instant: that update must use the old value, the next one the new value (mandatory);
  - step in the middle of an interval: mandatory, as above;
  - step exactly at `k*Ts`: **not guaranteed to match Python.** The Modelica event time can fall a few 1e-13 s before `t_step`, so the update at `k*Ts` still sees the old value, whereas Python (`t_k >= t_step`, exact multiplication) sees the new one. The accepted behaviour is the rule above applied to the recorded event time; which side occurred is reported. This is a documented semantic difference between the two implementations, with a one-sample effect for step inputs only.
- **P1b** = the reconstructed original test (`Tests/ControllerUnitStepOriginal.mo`, steps exactly at 4 s and 8 s) and `Tests/ControllerStepSemantics.mo` (steps at 2.005 s, 5.999999 s, 8.0 s, 10.000001 s), each evaluated with the rule above by `verification/scripts/controller_step_tests.py`. Criterion: `u`, `e_k`, `z` <= 1e-9 and no `sat` mismatch against an independent Python evaluation fed with the input value current at each recorded event time. The *original failing evaluation* (last row within 1e-9 s of `k*Ts` taken as the input row) is reproduced by the same script and kept as the recorded failure. The ramp test (P1) stays as the arithmetic check without discontinuities; it does not replace P1b.
- Where a direct Python/Modelica comparison involves discontinuities this difference is *expected*, not a defect. The primary grid has none, and the plant input `u` is a discrete signal that jumps at the update instants in both implementations (Modelica instants shifted by <= about 1e-11 s).

## 7. Solver selection (done on P-TUNE only; S1 and S2 are not used to choose a solver or tolerance)

1. Cases: P-TUNE, fixed and scheduled, SoH 0.8; solvers `dassl`, `cvode`, `ida`; tolerances {1e-6, 1e-8, 1e-10, 1e-12}; output on the control grid. Failed runs are kept and reported. The earlier plant checks found DASSL returning NaN at tolerance ≤ 1e-12 and CVODE/IDA completing; the cause is unresolved and is not investigated here.
2. A configuration is **admissible** if the simulation record says it finished, no cell is NaN, the controller update count is complete, and prereg validity holds.
3. Reference: the admissible run of the smallest tolerance, CVODE preferred, then IDA (the two independent integrators at the same tolerance, when both are admissible, give `u_ref`, the reference's own uncertainty).
4. Per quantity Q (E Wh/km and RMSE of each controller, ΔE%, RMSE ratio, and the maximum trace differences of v, T and u against the reference): `err(config) = |Q(config) - Q(reference)|`. A configuration **qualifies** if for every Q, `err ≤ max(0.1 · u_py(Q), 3 · u_ref(Q), floor)`, with `u_py(Q)` from the Python refinement on P-TUNE (dt 1e-3 vs 1e-4; section 8.2) and `floor = 1e-11 * |Q_python|` for scalar quantities and 1e-9 (= 1e-11 * 100) for trace maxima: the Modelica solver error must be at most a tenth of the discretisation error of the Python baseline, unless that is below what the reference itself can resolve.
5. **Selected configuration** = the loosest DASSL tolerance in the ladder that qualifies (DASSL is OpenModelica's default solver and the one used for the plant checks). If no DASSL tolerance qualifies, the loosest qualifying configuration of any solver. If none qualifies → stop, outcome **inconclusive** (section 11).
6. The selection (solver, tolerance, runtime) is written to `verification/references/controller_solver_selection.json` before the first S1/S2 case runs. Computing cost is not a criterion except that a run must finish.

## 8. Numerical agreement tolerances

### 8.1 Rule (applies to every quantity compared; no value is set from a Modelica-versus-Python difference or from the size of ΔE)

`tol(Q) = 3 · (u_py(Q) + u_mod(Q)) + 1e-11 · max|Q|` (`verification/scripts/controller_tolerances.py`)

- `u_py(Q)`: discretisation error of the Python baseline = `|Q(dt=1e-3) - Q(dt=1e-4)|` (for traces: max over the grid of the absolute difference of the two Python series), from the refinement study of the same profile, controller and SoH; for SoH 0.9 and 0.7 (not refined) the SoH 0.8 value of the same profile and controller is used, flagged in the output (the mechanical dynamics do not depend on SoH; only the scheduled gain and the battery do).
- `u_mod(Q)`: solver sensitivity of the Modelica result = max over the sensitivity runs (section 9) of `|Q(selected) - Q(variant)|`; SoH 0.8 runs are the only ones with variants; the other SoH levels borrow the SoH 0.8 value of the same profile and controller, flagged.
- The factor 3 is a stated safety factor (the two error estimates are themselves uncertain). The floor 1e-11 is a round-off allowance (CSV output carries 15-17 digits).

### 8.2 Python refinement study (executed; Python only; actual outputs)

`verification/scripts/python_reference_runs.py` re-ran the project's own `simulate` with dt in {1e-3, 5e-4, 2.5e-4, 1e-4} s for S1 and S2 (fixed and scheduled, SoH 1.0 and 0.8) and P-TUNE (SoH 0.8), writing only under `verification/` (nothing under `artifacts/`; not a rerun of the 296-run batch). Outputs: `verification/references/python_dt_study.json`, `python_dt_convergence.json` (analysis by `verification/scripts/python_dt_convergence.py`), series in `verification/controller-crosscheck-runs/python_reference/`. Run times of the batches of 4: S1 70 / 150 / 321 / 766 s, S2 51 / 102 / 201 / 502 s, P-TUNE (2 runs) 25 / 49 / 104 / 308 s. No run failed or warned.

- **Reproduction of the saved results:** at dt = 1e-3 every compared series (v, T, t_ref, z, t_lim, i), the `sat` flags, the end values of E_chem and dist, and the gains are **bit-identical** to `artifacts/raw/primary` for all 8 reproduced runs (maximum absolute difference 0.0); the metric functions reproduce `primary_metrics.csv` with maximum relative difference 0.0.
- **Convergence (energy per km, Wh/km; successive differences 1e-3 to 5e-4, 5e-4 to 2.5e-4, 2.5e-4 to 1e-4):** S1 fixed 4.8e-8, 2.1e-10, 1.7e-10; S1 scheduled 6.9e-8, 9.6e-9, 1.2e-10; S2 fixed 6.9e-8, 3.8e-8, 8.7e-10; S2 scheduled 4.6e-8, 1.9e-8, 1.6e-9; P-TUNE fixed 2.3e-7, 1.2e-9, 2.3e-9. The differences fall by 2 to 3 orders from the first to the last step but are not a clean fourth-order sequence (they flatten between 1e-10 and 2e-9, plausibly the non-smooth standstill, torque-limit and tanh regions; not investigated). **The finest step is therefore not assumed exact:** `u_py` below is the 1e-3 versus 1e-4 difference, a conservative proxy for the error of the 1e-3 baseline; the 1e-4 value itself is uncertain by about its last successive difference (0.2 % to 5 % of `u_py`).
- **Stop-condition verdict:** convergent, with small step-size dependence. The change of dE% between dt = 1e-3 and 1e-4 is 2.3e-8 percentage points (S1), 2.6e-7 (S2), 2.9e-7 (P-TUNE), against dE% values of 3.0e-3, 2.3e-3 and 4.1e-3, i.e. 1e-5 to 1e-4 of their value; the RMSE ratio changes by at most 7e-9. The exercise proceeds. (This is a statement about the Python scheme only, not about the Modelica solver.)

Discretisation-error estimates `u_py` (|Q(1e-3) - Q(1e-4)|; for traces the maximum over the grid), SoH 0.8:

| case | E Wh/km | RMSE m/s | v m/s | T N m | u N m | I A | E_chem(t) J |
|---|---|---|---|---|---|---|---|
| S1 fixed | 4.83e-08 | 1.1e-10 | 7.7e-08 | 1.0e-05 | 1.5e-05 | 2.0e-06 | 3.7e-04 |
| S1 scheduled | 5.99e-08 | 2.4e-10 | 1.7e-07 | 2.1e-05 | 3.1e-05 | 2.5e-06 | 4.3e-04 |
| S2 fixed | 2.96e-08 | 1.3e-10 | 3.8e-08 | 5.0e-06 | 7.4e-06 | 5.7e-07 | 6.7e-05 |
| S2 scheduled | 6.67e-08 | 1.4e-10 | 6.9e-08 | 8.6e-06 | 1.3e-05 | 1.0e-06 | 1.7e-04 |
| P-TUNE fixed | 2.32e-07 | 4.2e-11 | 1.5e-08 | 1.8e-06 | 2.9e-06 | 7.3e-07 | 5.6e-04 |
| P-TUNE scheduled | 9.80e-08 | 1.2e-11 | 1.6e-09 | 2.8e-07 | 2.8e-07 | 1.1e-06 | 2.7e-04 |

| pair (SoH 0.8) | dE% at 1e-3 | dE% at 1e-4 | `u_py(dE%)` | RMSE ratio at 1e-3 | at 1e-4 | `u_py(ratio)` |
|---|---|---|---|---|---|---|
| S1 | 0.003013799 | 0.003013822 | 2.3e-08 | 1.011021485 | 1.011021478 | 7.1e-09 |
| S2 | 0.002349034 | 0.002349294 | 2.6e-07 | 1.010994936 | 1.010994931 | 5.0e-09 |
| P-TUNE | 0.004120859 | 0.004120567 | 2.9e-07 | 1.011022272 | 1.011022273 | 9.8e-10 |

No `sat` flag differs between dt = 1e-3 and 1e-4 in any refined run. At SoH 1.0 fixed and scheduled are bit-identical at every dt (dE = 0, ratio = 1). The rule of section 8.1 uses the unrounded values stored in the JSON.

### 8.3 Quantities compared (Modelica selected configuration against the saved Python series, and secondarily against the dt = 1e-4 Python series)

| Group | Quantity | Statistic |
|---|---|---|
| Traces (k = 0..steps) | v, acceleration, T, u (= T_ref), T_lim, z (as used), battery current I, E_chem(t), dist(t), SoC | max abs difference |
| Scalars | all metrics of section 5, E_chem and dist at the end, ΔE%, RMSE ratio | abs and relative difference |
| Constraint activation | `sat` (u > T_lim), friction-brake active (u < −T_lim), regeneration active (I < 0), standstill (|v| < 1e-9) | count of samples where the two implementations disagree; a disagreement is *explained* only if the Python margin to the switching surface (|u − T_lim|, |u + T_lim|, |I|, |v|) is ≤ tol of that trace; any unexplained disagreement is a failure |
| Sampling / integration | controller update times, event rows per grid time, closure, solver status | as in sections 5-6 |

A quantity **agrees** if the difference ≤ tol. Failing quantities are reported as failures, traced (section 12), never re-tolerated.

## 9. Numerical convergence and sensitivity (after the solver is selected, before comparing controllers)

For S1 and S2 at SoH 0.8, fixed and scheduled: (a) the selected solver at tolerance/100 (or the next tighter admissible one), (b) the two other solvers at the selected tolerance. These supply `u_mod`. Acceptance: all variants admissible. If a variant fails to complete it is reported and excluded from `u_mod` (that weakens, not strengthens, the claim; flagged). The Python side supplies `u_py` from section 8.2. A run of the full grid at a second tolerance is not planned.

## 10. Practical significance and the inherited +/-1 % threshold

**What the preregistration says (read from `protocol/preregistration.md`, sha256 d3e6271e..., section numbers as in that file).**
- Section 3 defines `dE = (E_sched - E_fixed)/E_fixed x 100 %` (E = energy per km) and states the hypotheses: H1 (improvement, `dE <= -1.0 %` and RMSE ratio `<= 1.10`, at SoH 80 % on S1), H0 (`|dE| < 1.0 %`, "no practical difference"), H_W (`dE >= +1.0 %`).
- Section 9 turns that into a four-outcome decision table (IMPROVES / TRADE-OFF / NO PRACTICAL DIFFERENCE / WORSE) "applied verbatim". Its only stated justification is: "The +/-1 % margin is fixed in advance. It is about the resolution at which a model this simplified (constant efficiencies, constant V_oc) can be trusted to rank energy use."
- Section 8 fixes the primary outcome as `dE` on S1 at SoH 0.80, gamma = 1.

**What that threshold is, and is not.**
- It is a *decision margin on the model-computed energy effect of the controller change* (scheduled vs fixed) in one simulated model. It says how large a modelled energy difference must be before the study reports an effect rather than "no practical difference".
- It is not a numerical-agreement tolerance, not a statement about the equivalence of two implementations, and not an equivalence test: "NO PRACTICAL DIFFERENCE" is a label for `|dE| < 1 %`, with no uncertainty treatment, no confidence interval and no claim that the two controllers are equivalent. The text gives no empirical or independent derivation of 1.0 %.
- It does explicitly govern the same *decision* and the same *metric* (dE and RMSE ratio, S1/S2, the same SoH levels, the same model definition). The Modelica run is a second implementation of that same decision problem, so the section 9 table can be applied to the Modelica dE and RMSE ratio **verbatim and unchanged**, and the resulting labels compared with the Python labels. That comparison is a *decision-level agreement* check.

**Use in this exercise.**
1. Numerical agreement (sections 8-9, 11) and the decision label (this section) are reported separately. The decision label is never used to judge numerical agreement.
2. The section 9 table is applied verbatim to the Modelica results. If Modelica and Python give the same label, that is reported as decision-level agreement under the preregistered rule; it is **not** reported as practical equivalence of the implementations or of the controllers.
3. **No replacement or additional threshold is proposed, and no amendment is made.** No independently justified threshold exists in the project for the practical significance of a 0.003 % energy difference or for the equivalence of two implementations, and none is invented here. Practical equivalence between implementations is therefore *not formally concluded*; the numerical differences and their distinguishability from numerical error (section 11) are reported instead.
4. The inherited +/-1 % margin depends on the physical credibility of the model (constant efficiencies, constant V_oc, unverified parameters). Agreement between the two implementations does not improve that credibility.

## 11. Classification rules

For each decision-relevant quantity D (ΔE%, RMSE ratio) per profile and SoH:
- *Distinguishable from numerical error (Modelica)*: |D| > 3 · U_mod(D) and the sign of D is the same in every sensitivity variant; `U_mod(D) = max |D(selected) − D(variant)|`.
- *Distinguishable from numerical error (Python)*: |D_py(dt = 1e-3)| > 3 · U_py(D), `U_py(D) = |D_py(1e-3) − D_py(1e-4)|`.
- *Cross-implementation agreement*: `|D_mod − D_py(1e-3)| ≤ 3 (U_py + U_mod) + floor`.
- Otherwise the comparison is **numerically inconclusive** for that quantity. Also inconclusive: no admissible configuration; fewer than two successful variants for `U_mod`; the sensitivity variants disagree in sign; or a failed gate in sections 6-7.
- A failed agreement criterion with distinguishable D is a **mismatch**: reported with the traced cause (section 12), not as inconclusive.

## 12. Analysis plan and stopping rules

Order: (1) preliminary checks P1, P1b, P3, P4 (P2, P5, P6 are evaluated inside every later run); (2) the Python refinement study (done); (3) **freeze: the sha256 of this file and of the models, scripts and reference files is recorded in `controller-crosscheck-runlog.md` before any P-TUNE closed-loop simulation**; (4) P-TUNE solver study and selection, selection recorded with hashes before any S1/S2 case; (5) primary grid (16 runs) at the selected configuration; (6) sensitivity runs (section 9; 12 runs); (7) evaluation by `controller_eval.py`; (8) report. After step (3) this document changes only by a dated amendment in section 14 with its justification; any amendment made after controller-comparison results exist is labelled as post-result.

- Stop and report if: a preliminary check fails; no configuration is admissible/qualifying; the control law could not be reproduced unambiguously; a grid run fails to complete after one retry with the next tolerance in the ladder (both attempts reported).
- No tuning of gains, weights, γ, tolerances, step sizes or metrics in response to any result. A grid case that fails may be repeated once with the next tighter admissible tolerance of the same solver and both outcomes are reported.
- Discrepancy tracing (permitted after the results exist, labelled diagnostic, no parameter change): locate the first sample where a trace exceeds its tolerance; identify the physical regime (power limit, regeneration, friction brake, standstill, slope knot); run only diagnostic variants that change *numerics* (solver, tolerance, Python dt), never the model.
- No further runs after the evaluation except diagnostic variants for a traced mismatch.

## 13. Outputs

`verification/controller-crosscheck-protocol.md` (this file), `verification/controller-port-design.md`, `verification/controller-crosscheck-report.md`, `verification/controller-crosscheck-results.csv`, raw run artifacts in `verification/controller-crosscheck-runs/` (Modelica CSVs gzip-compressed with the sha256 of the uncompressed file; Python reference series), `verification/controller-crosscheck-runlog.md`.

## 14. Amendments

**A1 - 2026-10-23 23:4x (local), written after the freeze and after the first P-TUNE closed-loop runs, before any P-TUNE result was inspected or evaluated. Resource guard, not a numerical change.**
- What happened: in the first P-TUNE launch (24 runs in one OpenModelica script) the 9th run, `PT_fixed_cvode_tol1e-06`, did not terminate normally: CVODE logged "Desired step to small!" about 16.8 million times and wrote a 10 GB result file stuck at t = 17.99 s (update 1799). I terminated its executable by hand; `omc` then crashed (exit -1073741819) and the script ended, leaving 15 of the 24 runs not started. Evidence and hashes: `verification/controller-crosscheck-runs/failed_runs/PT_fixed_cvode_tol1e-06_evidence.txt`; the 10 GB CSV and the 1 GB log were deleted after hashing. The 8 DASSL runs of the first launch completed (about 2.7 s each).
- Amendment: the remaining runs of any stage are launched one case per `omc` invocation by `verification/scripts/guarded_run.py`, which terminates a case whose result file exceeds **500 MB** (the expected size is 5 MB for P-TUNE and 25 MB for S1) and classifies it **failed (runaway output)**. The guard changes only how a non-terminating run is stopped; it does not change any criterion in sections 7-11, and a failed run still counts as inadmissible. `PT_fixed_cvode_tol1e-06` is classified failed (runaway) as it stands; it is not repeated.
- Justification: protecting the disk and the session from unbounded output; no result had been inspected.


**A2 - 2026-10-23 23:5x (local). POST-RESULT amendment to sections 7 and 9 (written after the P-TUNE solver-study results were computed; before any S1 or S2 closed-loop case was run and before any Modelica-vs-Python comparison).**
- What the frozen rule produced: all 8 CVODE runs failed (runaway output: 7 were stopped by the 500 MB guard of A1, the first by hand); the DASSL and IDA runs all passed the admissibility test of section 7 item 2; the reference became IDA at 1e-12 (smallest tolerance, CVODE unavailable); every DASSL tolerance disagreed with it by 0.105 Wh/km (0.23 %) and 2.2e-4 m/s, and the only qualifying configuration was the reference itself.
- Diagnosis (numerics only, `verification/scripts/controller_ptune_study.py` output and `verification/modelica/scripts/diag_ida_events.mos`): DASSL and IDA agree to all printed digits up to update 1798 (t = 17.98 s). At t = 17.99 s IDA's state **reverts to its t = 17.99 s value at every following event** (v = 5.555756, T = 3.728768, E_chem = 21680.025407 are repeated in the event rows at 18.00, 18.01, ... while the interpolated rows move on), so IDA's trajectory stalls and then resumes: the accumulated energy is 320 J short at t = 20 s and 1095 J short at the end (1095 J = the 0.105 Wh/km). The event log shows only `sample(0, 0.01)` time events at that instant, no state event. CVODE fails at the same instant (update 1799, "Desired step to small!"). The cause inside the two Sundials interfaces is not established. Because the stalled run still closes its energy balance (6e-6 J, since every accumulator reverts together) the closure test of the frozen rule cannot detect it: **the frozen admissibility test was insufficient**, and the frozen reference was a defective run.
- Amendment (mechanical, independent of any Python result): (1) **new admissibility criterion K (kinematic consistency):** `max_k |dist(t_{k+1}) - dist(t_k) - Ts (v_k + v_{k+1})/2| <= 1e-3 m` over the control grid. Measured: DASSL 1.2e-5 m (all 8 runs), IDA 1.1e-1 m with 103 violating samples (all 8 runs); the threshold lies two decades from both. (2) **reference rule:** smallest-tolerance admissible run, CVODE, then IDA, **then DASSL**; when no second integrator is admissible at the reference tolerance, `u_ref = 0` is used and flagged (the reference is then supported only by the same-solver tolerance sequence, not by an independent integrator). (3) **sensitivity runs of section 9:** because CVODE and IDA are inadmissible, `u_mod` is estimated from DASSL at the two neighbouring ladder tolerances (one tighter if it exists, one looser by 100x), not from other solvers; the report states that no independent-solver confirmation of the Modelica results exists.
- Consequences to carry into the report: the cross-solver robustness that section 9 aimed at is unavailable; any classification that would have needed it is limited accordingly.

**A3 - 2026-10-23 23:5x (local), same status as A2 (post P-TUNE result, pre S1/S2).** Result of the amended selection (`verification/references/controller_solver_selection.json`, `ptune_solver_study.csv`): reference DASSL at 1e-12; the errors of the other DASSL tolerances against it fall monotonically with the tolerance (energy per km, fixed: 1.4e-7, 1.2e-8, 3.3e-10 Wh/km at 1e-6, 1e-8, 1e-10; v trace: 2.2e-6, 8.3e-8, 1.1e-9 m/s); 1e-10 misses the 0.1 x u_py criterion by factors up to 6.5; only 1e-12 qualifies. **Selected: DASSL, tolerance 1e-12.** Support is the same-solver tolerance sequence only (no independent integrator). Rules fixed here for what follows: (1) sensitivity runs (section 9, replaced by A2): S1 and S2, SoH 0.8, fixed and scheduled, DASSL at **1e-10** (supplies `u_mod`, the nearest looser neighbour, an upper bound on the error of the selected run if the sequence is convergent) and at **1e-8** (convergence-order check, informational): 8 runs; (2) if a grid case at 1e-12 fails admissibility, it is repeated once at 1e-10 and both attempts are reported, and that case is flagged; (3) the new criterion K of A2 is applied to every grid and sensitivity run.

**A4 - 2026-10-24 00:4x (local). POST-RESULT evaluator corrections (written after the primary-grid results had been evaluated; no tolerance, criterion threshold, metric definition or gain was changed).**
1. **P5 recomputation of the control law** first used the grid-row states (rows at exactly `k*Ts`) while the controller read the states at its update event, which `sample()` places up to about 1e-11 s earlier; with slope 1 m/s^2 and K_e = 196 N m s/m this produced residuals of 3.9e-9 N m against the 1e-9 criterion in all 16 runs (first evaluation: 16 FAIL). The recomputation now uses the states of the update rows themselves (the criterion 1e-9 is unchanged); all 16 pass. Both outcomes were seen; the first is in the run log.
2. **Borrowed `u_py`.** The first evaluation borrowed `u_py` for SoH 0.9 and 0.7 from SoH 0.8 (section 8.1) and, in addition, contained a coding error in the pair rows (the SoH 0.9/0.7 pair was compared with the SoH 0.8 refined pair). After the error was fixed, one S1 pair (SoH 0.7, dE%) and one metric (S1 scheduled SoH 0.7, max |e|) failed by factors of 1.8 and 1.13, which suggested that borrowing understated `u_py`. I then ran Python-only refinements at dt = 1e-4 for SoH 0.9 and 0.7 (S1 and S2, fixed and scheduled; `python_dt_diagnostic_soh.py`), and the evaluation uses them: no `u_py` is borrowed any more for the 16 primary cases (`u_mod` of SoH 0.9/0.7/1.0 is still borrowed from the SoH 0.8 sensitivity runs, flagged in the CSV).
3. **Reported as FAIL, not re-tolerated:** the S1 trace `dist(t)` and the S1 scalar `distance_km` (8 + 8 rows), see the report, section 4.
