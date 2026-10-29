# Controller cross-implementation report: Modelica vs the saved Python results

Written 2026-10-24 for the project owner and for a control-systems reviewer. Everything below comes from files under `verification/`; numbers are quoted from `controller-crosscheck-results.csv` (754 evaluation rows plus 30 preliminary and solver-study rows), `references/*.json` and `controller-crosscheck-runs/*.json`. Git root `D:\EURÉKA 2026 - KT`, HEAD `f264eca354d67dcdf786063ca36ae246466217d2`, nothing committed, `artifacts/` and `protocol/` untouched.

## 1. Bottom line

1. **Controller implementation agreement: yes, to within the Python scheme's own discretisation error, with one small named exception.** An independently written Modelica controller (separate gain design at 50 digits, `when sample(0, 0.01)` block, Modelica plant) reproduces the 16 saved S-A runs (S1, S2 x fixed, scheduled x SoH 1.0, 0.9, 0.8, 0.7). 554 of the evaluation checks pass. 16 fail: the S1 accumulated-distance trace and scalar (8 + 8 rows, relative size 4.6e-10; section 4.3). Agreement is at the level of the Python 1 ms step error, not better: Modelica differs from the saved series by about as much as the saved series differs from Python at 0.1 ms, and agrees with the 0.1 ms Python run 36 to 250 times more closely in speed (2e-9 m/s at worst; section 4.1).
2. **The small energy difference is numerically resolved.** At S1, SoH 0.8, dE = +0.003013823 % (Modelica), +0.003013799 % (saved Python, 1 ms), +0.003013822 % (Python, 0.1 ms). The numerical uncertainty of dE is about 2e-8 percentage points (Python step error) and 8e-11 (Modelica solver, nearest tolerance), i.e. five orders below the effect. Sign and size agree. The scheduled controller uses slightly *more* energy than the fixed one in this model (+0.003 %, +0.0023 % on S2), with a 1.1 % larger RMSE (ratio 1.0110).
3. **Decision label (preregistration section 9): NO PRACTICAL DIFFERENCE for all 16 runs, identical to the saved Python labels.** This is a decision-level agreement under an inherited rule. It is **not** a demonstration of practical equivalence (section 4.4), and the inherited +/-1 % margin does not become an equivalence threshold by being reused.
4. **Solver caveats you must know.** CVODE failed on all 8 closed-loop P-TUNE runs (runaway output) and IDA's state reverts at each event after t = 17.99 s; both are inadmissible. The selected solver is DASSL at tolerance 1e-12, supported only by its own tolerance sequence. There is no independent-solver confirmation. The frozen selection rule would have chosen the defective IDA run; this was fixed by amendment A2, after the P-TUNE result and before any S1/S2 case (section 3).
5. **What was not exercised.** The traction limit, the saturation/anti-windup branch and the friction brake are never active in S1 or S2 (`traction_limited_frac` and `friction_brake_Wh` are 0 in all 16 runs, in both implementations). They are covered only by the controller-logic unit test and the earlier open-loop plant checks. The regeneration and holding-brake (standstill) branches are exercised and agree (regeneration flag: 0 unexplained disagreements among about 4 000 to 5 400 samples per run; standstill: identical sample counts).
6. **Physical validity is unverified.** Both implementations use the same equations, the same unsourced or assumed parameters and one author lineage.

## 2. What was built and compared

- **Control law** (reconstructed from `controllers.py`, `simulate.py`, preregistration section 5; details and sources in `controller-port-design.md`): `u_k = -(K_e e_k + K_T T_k + K_z z_k)`, `e = v - v_ref`, ZOH 10 ms, `z_{k+1} = z_k` if `u_k > T_lim` and `e_k < 0`, else `z_k + Ts e_k`; fixed `K` designed with `Q0 = diag(1/0.5^2, 1/85^2, 1/0.5^2)`, `R0 = 1/85^2`; scheduled `Q = Q0 diag(1, 1/(1 + gamma_v (1 - SoH)), 1)`, `R = R0 (1 + gamma_u (1 - SoH))`, gamma = 1, SoH known exactly, **no interpolation** (the gain is designed per SoH level).
- **Gains** (`references/controller_gains.json`, sha256 29c4df20...): designed by `controller_gain_design.py` with 50-digit exact ZOH and structured doubling, not importing project code. Agreement of three routes <= 2.2e-13 relative; the saved Python gains differ from the frozen ones by <= 3.1e-13 relative (all 16 runs). The gains in `Cases.mo` equal the JSON bitwise (check P4).
- **Modelica**: `EurekaController` (`SampledLqr`, `ClosedLoop`, generated `Cases.mo`) on the unmodified `EurekaPlant` v0.1.1. 16 primary runs + 8 sensitivity runs + 24 P-TUNE runs; each run 6 to 12 s (DASSL); the P-TUNE-selected configuration is DASSL, tolerance 1e-12, output on the 10 ms grid.
- **Python baseline**: the saved `artifacts/raw/primary` series (hashes in the protocol). I reproduced them bit-identically at dt = 1e-3 (max difference 0.0 in v, T, t_ref, z, t_lim, i, sat, E_chem, dist and gains for all 8 reproduced runs) and then re-ran the project's own simulator at dt = 5e-4, 2.5e-4, 1e-4 (and SoH 0.9/0.7 at 1e-4) writing only under `verification/`.

## 3. Protocol, deviations and amendments (everything that changed after the freeze)

The protocol was frozen on 2026-10-23 23:25 (sha256 `c7951936...`, run log). The final protocol file is `367f0c83...` because of amendments A1 to A4 appended in section 14; text above section 14 is unchanged. Honest list:

| ID | When | What | Why | Could it favour a result? |
|---|---|---|---|---|
| A1 | after the first P-TUNE launch, before any result was inspected | one case per `omc` call; output-size guard 500 MB | CVODE wrote a 10 GB file in a "Desired step to small!" loop; I killed it by hand, `omc` crashed and 15 runs did not start | No: changes how a non-terminating run is stopped |
| A2 | after the P-TUNE results, before any S1/S2 case | new admissibility criterion K (`|d dist - Ts (v_k + v_{k+1})/2| <= 1e-3 m`); reference may be DASSL; `u_ref = 0` when no second integrator | the frozen rule picked IDA at 1e-12 as reference; IDA's state reverts to its t = 17.99 s value at every later event (diagnostic `diag_ida_events.mos`), losing 1095 J by the end; the frozen closure test cannot see this (closure 6e-6 J) | No Python result was used; but it is a post-result change to a selection rule, and it is what makes DASSL the only admissible solver |
| A3 | same | selected DASSL 1e-12; sensitivity = DASSL at 1e-10 (u_mod) and 1e-8 (check); fallback 1e-10 | consequence of A2 | No |
| A4 | after the primary results were evaluated | P5 recomputation uses the update-row states (16 FAIL before, 3.9e-9 vs 1e-9; the criterion is unchanged); `u_py` for SoH 0.9/0.7 from new Python refinements instead of borrowing from 0.8 | evaluator design errors; one pair (S1 SoH 0.7 dE%, factor 1.8) and one metric (factor 1.13) failed marginally under the borrowed value, and passed once their own refinement existed | Possible direction: it removed two marginal failures. The new `u_py` values come from Python-only runs; the underlying differences did not change. Both outcomes are in the run log |

Other recorded failures: the first controller-logic test (step inputs) failed because of my test design (two events 1.7e-13 s apart merged in the row grouping) and was reproduced bit-identically later as the retained failing case (max |u| error 105.28091142582139); the ramp test passed; the step-input semantics test was added (section 4.5). A bug in the pair table (SoH 0.9/0.7 compared with the SoH 0.8 refinement) was found and fixed before the final evaluation.

## 4. Results

### 4.1 Controller implementation agreement

All numbers: Modelica DASSL 1e-12 vs the saved Python series (dt = 1e-3), SoH 0.8; the tolerance is `3 (u_py + u_mod) + 1e-11 max|Q|` (protocol 8.1) and its inputs come from the Python step-size study and the Modelica sensitivity runs, not from the observed difference.

| Quantity (max over the grid) | S1 fixed | S1 sched. | S2 fixed | S2 sched. |
|---|---|---|---|---|
| v difference, m/s | 7.5e-08 | 1.65e-07 | 3.8e-08 | 6.9e-08 |
| same, vs Python dt 1e-4 | 2.1e-09 | 6.7e-10 | 5.2e-10 | 4.3e-10 |
| T, N m | 9.8e-06 | 2.1e-05 | 4.9e-06 | 8.6e-06 |
| u (= T_ref), N m | 1.5e-05 | 3.1e-05 | 7.3e-06 | 1.3e-05 |
| u vs Python dt 1e-4 | 4.3e-07 | 1.2e-07 | 1.0e-07 | 6.8e-08 |
| battery current I, A | 2.0e-06 | 2.5e-06 | 5.6e-07 | 1.0e-06 |
| E_chem(t), J | 3.1e-04 | 2.8e-04 | 6.4e-05 | 1.7e-04 |
| energy, Wh/km | 4.7e-08 | 5.9e-08 | 2.4e-08 | 7.0e-08 |
| RMSE, m/s | 1.1e-10 | 2.4e-10 | 1.4e-10 | 1.2e-10 |

- Over all 16 runs, 136 of 144 trace comparisons and 216 of 224 metric comparisons that carry a tolerance pass; the 16 failures are the S1 distance rows; the smallest margin among passing rows is tolerance/difference = 1.5 (S1 scheduled SoH 0.7, energy in Wh) and 1.8 (E_chem(t) there); most rows sit at about 3.0, i.e. the difference *equals* the Python 1 ms error that sets the tolerance. Interpretation: Python at 1 ms is the less accurate side; Modelica agrees with the 0.1 ms Python run to 1e-9 m/s in speed.
- Constraint activation (64 rows): the traction limit and the friction brake are inactive in every run in both implementations; regeneration (I < 0) and standstill (|v| < 1e-9) sample counts are identical in all 16 runs (e.g. S1 fixed SoH 0.8: 5419 and 7072 samples), and no disagreeing sample lies outside its switching-margin tolerance.
- Internal controller recomputation from the saved Modelica series (P5, 64 rows): `u` <= 2.1e-12, `z` recursion <= 1e-12, `sat` flags identical, RMSE from the running sum = RMSE from the series; the Modelica `v_ref` equals the saved one to 1.2e-10 (P6).
- Sampling/integration: the controller update rows lie within 1.5e-10 s of `k Ts` in the longest run (protocol criterion 1e-9); the number of updates is steps + 1 in all runs; the final update at the stop time is present.

### 4.2 Numerical convergence

- **Python step size** (`python_dt_convergence.json`; protocol 8.2): convergent; energy per km changes by 3e-8 to 2.3e-7 Wh/km between 1 ms and 0.1 ms, dE% by 2.3e-8 (S1), 2.6e-7 (S2), RMSE ratio by <= 7e-9. The successive differences are not a clean fourth-order sequence (they flatten at 1e-10 to 2e-9), so 0.1 ms is not claimed exact. All `sat` flags are identical at all steps.
- **Modelica solver study on P-TUNE** (24 runs, `ptune_solver_study.csv`, `controller_solver_selection.json`):

| solver | tolerances | result |
|---|---|---|
| DASSL | 1e-6, 1e-8, 1e-10, 1e-12 | all completed (1.6 to 2.7 s), admissible; errors vs the 1e-12 run fall monotonically: energy 1.4e-7, 1.2e-8, 3.3e-10 Wh/km; speed 2.2e-6, 8.3e-8, 1.1e-9 m/s; only 1e-12 meets 0.1 x `u_py` (it is the reference) |
| IDA | all four | "finished successfully" and closure-clean, but state reverts at each event after t = 17.99 s (kinematic residual 0.111 m, 103 samples; DASSL 1.2e-5 m): inadmissible |
| CVODE | all four | all 8 failed: "Desired step to small!" (first run: at update 1799, t = 17.99 s, 16.8 million rows, 10 GB, killed by hand; the other 7 were stopped by the 500 MB guard, their stopping time was not analysed); evidence in `failed_runs/` |

  `omc` exit code 0 occurred for some failed runs; success was read from the `SimulationResult` record, then the result file, then NaN/update-count/closure/kinematic checks. The cause of the CVODE/IDA failure at that instant is unknown (the event log shows only `sample` time events); DASSL passes. The earlier finding that DASSL gave NaN at tolerance 1e-12 in the *open-loop* plant check did not occur here.
- **Modelica sensitivity (S1, S2 SoH 0.8, 8 runs)**: energy per km changes by 3.6e-10 to 1.4e-7 Wh/km between 1e-12 and 1e-10, and by 1.2e-7 to 1.8e-5 between 1e-12 and 1e-8, roughly proportional to the tolerance. `u_mod(dE%)` is 7.9e-11 pp (S1) and 5.2e-8 pp (S2). Because the variants are the *same* solver, this is evidence of convergence, not of independence.
- **No independent solver confirmed any S1/S2 result.**

### 4.3 The S1 distance discrepancy (16 FAIL rows; traced, not re-tolerated)

`max |dist_Mod(t) - dist_Py(t)|` on S1 is 0.99e-6 to 1.05e-6 m (tolerance 4.8e-7 to 6.5e-7); the end distance differs by 8.4e-7 m of 2161.3 m (3.9e-10 relative) against the 1e-4 Python run; S2 passes (margins 4.4 and 8.1 at SoH 0.8). Trace: (a) the difference grows quadratically during the 50 km/h cruise (157 to 197 s) and does not appear in v (max v difference 2e-9 m/s; the trapezoid integral of the v difference is <= 1.2e-9 m); (b) in that cruise Modelica's distance increments per 10 ms are 1.34e-10 m smaller than `v Ts` (relative 9.7e-10), while Python's are consistent with its own v to 1e-11; (c) the deficit does not change between DASSL tolerances 1e-10 and 1e-12 (1.4e-8 m difference) nor with `-maxStepSize=0.001` (8.4e-7 m again); (d) E_chem(t) shows the same relative size (1.6e-4 J of 3.9e5 J); (e) the Python distance is self-consistent with its own speed to 1e-11 m/s. I therefore attribute it to a tolerance-independent bias of Modelica's accumulated integral states between restarts, not to the Python scheme and not to the controller. The mechanism is **not established**. The Python side was checked with a diagnostic run at dt = 2e-5 (S1 fixed SoH 0.8, 2 792 s, `DIAG_S1_fixed_soh0.80_dt2e-05.npz`): Python's end distance moves by only 5.8e-8 m from dt = 1e-4 to 2e-5 (2161.2843812220 to 2161.2843811638), whereas Modelica's is 7.8e-7 m below the 2e-5 value (2161.2843803824); the speed trace of Modelica is within 1.4e-10 m/s of the 2e-5 Python run. So the discrepancy is not the Python step error; it sits in Modelica's accumulated distance (and, at the same relative size, energy: 1.45e-4 J). Effects: Wh/km changes by at most 4.6e-10 relative (<= 2.3e-8 Wh/km, inside the energy tolerance); the bias is common to both controllers and cancels in dE% (Modelica vs Python 1e-4: 1.6e-9 pp at S1 SoH 0.8).

### 4.4 Model-based control performance and the decision label

Modelica / saved Python (recomputed from the saved series) / Python dt = 1e-4; dE in %, RMSE ratio dimensionless:

| profile, SoH | dE Modelica | dE saved Py | dE Py 1e-4 | ratio Modelica | ratio saved Py | label (both) |
|---|---|---|---|---|---|---|
| S1, 1.0 | 0 | 0 | 0 | 1 | 1 | NO PRACTICAL DIFFERENCE |
| S1, 0.9 | 0.001248234 | 0.001248293 | 0.001248232 | 1.004071749 | 1.004071748 | same |
| **S1, 0.8** | **0.003013823** | **0.003013799** | 0.003013822 | **1.011021478** | **1.011021485** | same |
| S1, 0.7 | 0.005176010 | 0.005176137 | 0.005176009 | 1.020103362 | 1.020103367 | same |
| S2, 1.0 | 0 | 0 | 0 | 1 | 1 | same |
| S2, 0.9 | 0.001012965 | 0.001012774 | 0.001012966 | 1.004058972 | 1.004058974 | same |
| S2, 0.8 | 0.002349289 | 0.002349034 | 0.002349294 | 1.010994931 | 1.010994936 | same |
| S2, 0.7 | 0.003934792 | 0.003934590 | 0.003934794 | 1.020062367 | 1.020062369 | same |

- All 12 dE and RMSE-ratio pair rows at SoH < 1 pass the agreement criterion; the differences from the saved values (1e-8 to 2.6e-7 pp) equal the Python 1 ms error `u_py`, and Modelica agrees with Python at 0.1 ms to <= 3e-9 pp. At SoH 1.0 fixed and scheduled are bit-identical in Modelica (dE = 0 and ratio = 1 exactly): prereg sanity control passed.
- **Distinguishability from numerical error**: at every SoH < 1, |dE| exceeds 3 x (numerical uncertainty of dE) in Modelica and Python (S1 SoH 0.8: 3.0e-3 vs 3 x 2.3e-8 and 3 x 7.9e-11), and, at SoH 0.8 (the only level with sensitivity variants), its sign is the same in every variant (`u_mod` for the other levels is borrowed from SoH 0.8). The energy comparison is therefore **not** numerically inconclusive. The scheduled controller costs slightly more energy and has a 0.4 to 2 % larger RMSE at every SoH < 1 in this model.
- The scheduled-vs-fixed difference is a property of the simulated model with these assumed parameters (resistive losses are 1 to 2 % of supplied energy), not a finding about real vehicles.

### 4.5 Practical equivalence

- The inherited +/-1 % margin (preregistration sections 3, 8, 9) is a decision margin on the model-computed energy effect of the controller change, with the one-sentence justification "about the resolution at which a model this simplified can be trusted to rank energy use". It explicitly governs the same decision and metric (dE and RMSE ratio, S1/S2), so applying the section 9 table verbatim to the Modelica results is legitimate and gives the same labels.
- It does not define equivalence between two implementations, has no uncertainty treatment and no empirical derivation, so it does not establish practical equivalence of the implementations or the controllers. I did not propose a replacement threshold; none exists in the project. **Practical equivalence is not formally concluded.** What is concluded: the numerical difference between the implementations is explained by the Python step error, and the energy effect is resolved and about 330 times smaller than the inherited margin.

### 4.6 Piecewise-constant inputs (sample-boundary semantics)

The primary grid has none (continuous piecewise-linear reference). The controller block was tested with step inputs (`controller-crosscheck-protocol.md` 6.1): all steps away from an update instant behave as defined (update at event time `t_e` uses the input current at `t_e`); for steps exactly at an update instant (4.0 s, 8.0 s) the Modelica update fired 4.1e-14 s and 1.3e-13 s *before* the step and saw the **old** value, where Python (`t_k >= t_step`, exact multiplication) would see the new one. That is a documented one-sample semantic difference for step inputs only. The original failing evaluation is retained and reproduced (`step_input_tests.json`).

## 5. Failed and inconclusive items

| Item | Status |
|---|---|
| S1 `dist(t)` (8 rows) and `distance_km` (8 rows) | FAIL, 3.9e-10 relative; traced (4.3); mechanism not established |
| CVODE, 8 P-TUNE runs | FAIL (runaway) |
| IDA, 8 P-TUNE runs | inadmissible (state reverts after t = 17.99 s) |
| DASSL 1e-6, 1e-8, 1e-10 | do not qualify under 0.1 x `u_py` (they are still convergent) |
| Independent-solver confirmation | not available |
| First controller-logic test; first P5 evaluation; first pair table | failed through my design/code errors; corrected and recorded |
| Physical validity | unverified |
| Practical equivalence | not formally concluded |
| Constraint branches (traction limit, anti-windup, friction brake) in S1/S2 | not exercised by these scenarios |

No result is "numerically inconclusive" in the sense of protocol section 11.

## 6. For a human control-systems expert

1. Is the selected solver defensible when CVODE and IDA fail at the same instant and DASSL is the only admissible integrator? The Sundials failures (CVODE at update 1799 in the first run; IDA from t = 17.99 s) are unexplained and may indicate a limit or defect in how OpenModelica 1.27.1 restarts them after many events.
2. The 4e-10 relative bias in Modelica's accumulated distance and energy states in S1: confirm or refute the tolerance-independent-restart explanation, and decide whether `dist`/`E_chem` should be integrated with another formulation.
3. The inherited +/-1 % margin and the weighting `alpha_v` applied to the torque state (preregistration deviation (a)) are modelling choices, not facts about the report's EKF-based scheme; SoH is known exactly in both implementations.
4. Whether a scenario that actually reaches the traction limit and the friction brake is needed before the saturation/anti-windup port can be called verified in closed loop (protocol excludes new scenarios; P-TUNE and the plant checks do not reach them either).
5. The common-source limitation: one document, one author, same unverified parameters.

## 7. Artifact index

| Artifact | Location | sha256 (prefix) |
|---|---|---|
| Protocol (final, with A1-A4) | `verification/controller-crosscheck-protocol.md` | 367f0c83... |
| Port design | `verification/controller-port-design.md` | ed83526d... |
| Results (784 rows) | `verification/controller-crosscheck-results.csv` | 5cc670b0... |
| Run log (frozen hashes, events) | `verification/controller-crosscheck-runlog.md` | see file |
| Frozen gains / selection / Python dt study | `verification/references/controller_gains.json` / `controller_solver_selection.json` / `python_dt_study.json`, `python_dt_convergence.json` | 29c4df20... / 5d46973e... / 82f485e1..., f375bdb6... |
| Evaluation summary, solver study, preliminary and step tests | `verification/controller-crosscheck-runs/{evaluation_summary.json, ptune_solver_study.csv, preliminary_checks.json, step_input_tests.json}` | b1de6dba... / dae7cbbc... / e8be1f1a... / 04b93180... |
| Raw Modelica CSVs (gzip, sha256 of the uncompressed file in `evaluation_summary.json`) | `verification/controller-crosscheck-runs/raw/` (40 files) | |
| Python reference series | `verification/controller-crosscheck-runs/python_reference/` | |
| Failed-run evidence | `verification/controller-crosscheck-runs/failed_runs/` | |
| Models | `verification/modelica/EurekaController/` | in the run log |
| Scripts | `verification/scripts/controller_*.py`, `python_*`, `guarded_run.py`, `runlog_record.py`, `generate_controller_*.py` | in the run log |

The `controller-crosscheck-runs/` folder is about 275 MB (raw CSVs, Python series). Nothing was added to `.gitignore` and nothing was committed.
