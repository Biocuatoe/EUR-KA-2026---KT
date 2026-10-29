# Independent Modelica verification of the corrected EV plant

- **Date:** 2026-10-23. **Scope:** plant only. No controller, no EPA cycle, no 296-run batch, no new software, no commit.
- **Written for:** the project owner and any technical reviewer of the EV longitudinal-dynamics and LQR study.
- **Files:** `modelica-check-results.csv` (49 rows, every result with model version, parameters, source data, command, exit code, simulation status, artifact path and hash), `cross-implementation-comparison.csv` (25 quantities), `modelica-plant-specification.md` (written before coding, with a post-run section 13), `openmodelica-launcher.md`.

## 1. Result in one paragraph

An independent Modelica implementation of the corrected plant (OpenModelica 1.27.1, variable-step DASSL with event location) passes all 35 checks (33 from the pre-registered table in the specification, plus two I added during the run: A3, that the generated parameters equal the YAML, and D3_ref, that the saved reference is reproduced by its own algorithm), with no tolerance changed. It reproduces hand-calculated equilibria and instantaneous values to machine precision, the project's coast-down to 1.9×10⁻¹⁰ m/s, the exact analytic road-load energies of both synthetic profiles to 10⁻⁹, and the saved ideal-tracking energy (49.714 Wh/km on S1) within the discretisation error of the saved reference itself. It agrees with the corrected Python plant to 10⁻⁸ m/s in speed on a 66 s trajectory that exercises every branch of the model. **This shows the two implementations of the *specified* equations agree and that those equations are internally correct. It does not validate the model against any vehicle.** Along the way I made and corrected three errors of my own (section 6), and I found one numerical limitation of DASSL.

## 2. State of the project

| Item | Value |
|---|---|
| Git root | `D:\EURÉKA 2026 - KT` (unchanged), `HEAD` `f264eca354d67dcdf786063ca36ae246466217d2`, no remotes |
| Tracked files modified | `.gitignore` only (3 new rules for generated OpenModelica data); nothing staged or committed |
| Untracked | `audit/`, `verification/`, `technical-claim-matrix.csv`, `technical-foundation-audit.md` |
| Unchanged (hash re-checked) | `uv.lock`, the thesis `.docx`, `protocol/preregistration.md`, `evidence/evidence_matrix.csv`, all raw results |
| OpenModelica | `D:\EURÉKA 2026 - KT\tools\OpenModelica\bin\omc.exe`, `OpenModelica v1.27.1 (64-bit)`; not reinstalled; machine-wide `OPENMODELICAHOME` and Start Menu entries untouched |
| Alias | created and removed by every launcher run; `subst` lists nothing now; see `openmodelica-launcher.md` |
| Model version | `EurekaPlant 0.1.1` (sources hash 919e0b53f87a5e8b) |

## 3. Equations implemented (specification section 4)

With v⁺ = max(v, 0), ω = (G/r_w) v⁺, T_lim = min(T_max, P_max / max(ω, 10⁻⁶)), shaft torque t_s = T − B_m ω:

- traction force F_w = (G/r_w) η_g t_s when t_s ≥ 0, and (G/r_w) t_s / η_g when t_s < 0;
- rolling resistance C_rr M g tanh(v⁺/0.05 m/s); drag ½ ρ C_d A_f v⁺²; friction brake (G/r_w) max(0, −T_lim − T_ref) tanh(v⁺/0.05);
- M_eff dv/dt = F_w − F_rr − F_aero − F_fb with M_eff = M + J_m G²/r_w², and dv/dt = 0 when v ≤ 0 and the net force is negative;
- torque actuator dT/dt = (clip(T_ref, ±T_lim) − T)/τ_T;
- P_m = Tω; P_e = P_m/η_mi (motoring) or P_m η_mi (regeneration); battery current from V_oc − V1 and R0(SoH) by the quadratic root; dV1/dt = −V1/(R1 C1) + I/C1;
- ten energy accumulators, distance and charge, and the closure identity.

Parameters come from `configs/parameters.yaml` through a generator that does not import `eureka`; check A3 confirms all 23 values equal the YAML. Every parameter is `report_unverified`, `assumed` or `standard`.

## 4. Results

### A. Dimensions and structure
- All five test models compile with `--unitChecking`, equations equal variables, and no unit warning (A1). Two wrong-unit fixtures (a power assigned to a force; traction built from motor speed) and a charge-integral probe are flagged (E_A1), so the clean result is meaningful.
- Pint check of all 28 specification terms: 28 correct, 4 deliberately wrong forms rejected.
- **Limit:** equations containing the bare literal `3600` pass `omc`'s checker regardless of units; the A·h to A·s factor is verified only by Pint.

### B. Equilibrium, instantaneous values, limits
| Case | Result (pre-registered tolerance) |
|---|---|
| Equilibrium at 20, 30, 50 km/h from the hand-calculated T_eq (3.737108, 4.609469, 7.323644 N m) | max \|a\| ≤ 3.2×10⁻¹⁷ m/s², max \|F_net\| ≤ 2.8×10⁻¹⁴ N, speed drift 0 (1e-9, 1e-6, 1e-9) |
| Four instantaneous points (two motoring, two regenerating, one with the friction brake active): F_w, F_rr, F_aero, F_fb, F_net, a, P_m, P_e, I | relative error ≤ 5.4×10⁻¹⁶ (1e-9) |
| T_lim and dT/dt at 13 m/s and 2 m/s | exact to printed precision (1e-9) |

### C. Coast-down
- **What the "3.6×10⁻⁹ m/s" was:** the maximum error of a *toy* linear-drag model (m = 850 kg, c = 25 N s/m, v₀ = 10 m/s), 20 s, DASSL tolerance 1e-10, 2001 output points, metric max |v − v₀ e^(−ct/m)| against a closed form evaluated in double precision. It is the solver's global error at that tolerance, not an exact-arithmetic error, and not the project's coast-down. Rerun: **3.6307×10⁻⁹ m/s absolute, 5.1×10⁻¹⁰ relative; the earlier value reproduced exactly.**
- **Project coast-down** (zero torque, regeneration-branch shaft friction, quadratic drag, rolling resistance; v₀ = 13 m/s, 20 s): closed form verified symbolically (residual exactly 0). Modelica v(20) = 9.92838962..., max error **1.89×10⁻¹⁰ m/s absolute, 1.83×10⁻¹¹ relative** (limit 1e-7).
- Error against solver tolerance: 6.9×10⁻⁷ (1e-6), 5.2×10⁻⁹ (1e-8), 1.9×10⁻¹⁰ (1e-10), 6.1×10⁻¹² (1e-12); it falls with the tolerance as it should (C3).

### D. Ideal-tracking energy (the saved 49.714 Wh/km)
**What the reference is:** a saved *numerical* result, not an analytic value. It exists as the text "49.714" in `technical-foundation-audit.md` and as an algorithm in `audit/technical-verification/ind_checks_b.py` (midpoint sampling at a fixed 1 ms step, exact exponential update of V1 for piecewise-constant current, actuator lag not modelled). No data file holds it.

Exact analytic checks first (all pass, limit 1e-7): distance, aero energy and rolling energy of S1 and S2 agree with exact integrals to ≤ 4.5×10⁻⁹. The rolling integral needs the tanh-smoothing correction (about 4×10⁻⁶ relative); without it the analytic value would be wrong. Energy closure ≤ 7×10⁻¹² (an identity, not a physics test).

| Case | Saved reference (h = 1 ms) | Modelica | Gap to saved reference | Converged value (DOP853, step-capped) | Modelica vs converged |
|---|---|---|---|---|---|
| S1, SoH 1.0 | 49.714073 | **49.714619** | 1.10×10⁻⁵ | 49.714619 | 1.2×10⁻¹⁰ |
| S1, SoH 0.8 | 49.803003 | 49.803551 | 1.10×10⁻⁵ | 49.803551 | 1.4×10⁻¹⁰ |
| S2, SoH 1.0 | 36.951337 | 36.949492 | 4.99×10⁻⁵ | 36.949492 | 2.0×10⁻⁹ |
| S2, SoH 0.8 | 36.990473 | 36.988627 | 4.99×10⁻⁵ | 36.988627 | 1.4×10⁻⁹ |

**Verdict: the saved reference is reproduced** (the preserved algorithm at 1 ms returns 49.714073 exactly, within 4.7×10⁻⁴ of the quoted 3-decimal figures) **and Modelica agrees with it within 3×10⁻⁴ (limit); the remaining 1.1×10⁻⁵ and 5×10⁻⁵ gaps are the saved reference's own discretisation error.**
Why the gap exists, shown by intervention: re-running the *same* scheme with steps aligned to the profile knots at the same h = 1 ms gives errors of 3×10⁻⁸ (S1) and 2×10⁻⁸ (S2), 350 to 2400 times smaller. A global fixed step lets a step straddle a slope change and assigns the wrong power to part of it. This error is O(h·ΔP) per knot and does not shrink smoothly (the saved scheme's gap at h = 10⁻⁴ is 2.3×10⁻⁷ for S1 but 6×10⁻⁶ for S2).
The items you asked me to check: units and distance normalisation (distance exact to 10⁻⁹), resistance equations and energy definition (exact integrals), efficiency assumptions (constant, direction of power flow, closure holds), negative power (regeneration included in E_chem and the closure), sampling and integration (the cause above). The ideal trace never exceeds the actuator limits: the smallest T_lim − |T| is 21.25 N m (S1) and 57.51 N m (S2), so no friction braking is needed.
I did not tune anything: parameters are the YAML values.

### E. Negative controls (all detected, none by less than the required factor of 10)
| Control (separate fixture or run-time override; the authoritative model was never edited) | Detected by a factor of |
|---|---|
| Gear efficiency 0.98 instead of 0.9702 at the 30 km/h equilibrium (model response equals the analytic prediction, 1.004644 N) | 1×10⁶ over the B1 force tolerance |
| Coast-down with efficiency applied as a multiplier while regenerating (equation-level fixture) | 7.5×10⁴ |
| Coast-down with C_rr +1 % | 1.3×10⁵ |
| Ideal-tracking energy with C_d +1 % | 12.1 over the D3 tolerance (energy 49.8938 vs 49.7141) |
| Ideal-tracking energy with η_mi +1 % | 56.9 |
| Python plant with C_rr +1 % against the unperturbed Modelica run | 2.1×10³ over the speed tolerance |
| Three wrong-unit fixtures | flagged by `omc` |

### F. Cross-implementation comparison (Modelica against the project's Python plant)
- **Setup:** the same 66 s open-loop torque schedule, SoH 0.8, initial state (0, 0, 0, 0.8). The schedule (85, 20, 0, −40, −200, −20, 10 N m, switching at 10, 20, 30, 38, 46, 56 s) exercises the power limit (563 output rows with the request clipped), regeneration, the friction brake (124 output rows with F_fb > 0), arrival at rest at 39.23 s, the holding brake (|v| ≤ 1.3×10⁻¹² m/s over the 46.5-55.9 s window I examined, no chattering) and departure from rest. Modelica: DASSL, tolerance 1e-10. Python: `eureka.plant.rk4_step`, run at its native 1 ms and at 0.1 ms. Neither side reads the other's output; the comparison is made afterwards on saved files. The two implementations share no numerical routine.
- **Result: 25 of 25 quantities within the pre-registered tolerances**, against the 0.1 ms Python run. Examples (largest difference, tolerance): speed 9.9×10⁻⁹ m/s (1e-5); torque 1.0×10⁻⁷ N m (1e-4); V1 6.5×10⁻¹² V; final E_chem 190039.762775 J against 190039.762783 J; net force 3.1×10⁻⁴ N (5e-3). Margins range from 16× (net force and friction-brake force, at the instant the vehicle stops) to 10⁵×.
- **Python's own step error:** Modelica against Python at 1 ms and Python at 1 ms against Python at 0.1 ms differ by about the same amount (ratio 0.3 to 2.4), so the difference is dominated by Python's discretisation at 1 ms, which is itself tiny (5×10⁻⁸ m/s).
- **Solver independence (informational):** final E_chem from DASSL (1e-8 to 3e-12), CVODE (1e-10, 1e-12) and IDA (1e-12) agree to 3×10⁻⁹ relative or better.
- The Modelica CSV contains 21 extra rows at event instants (pre- and post-event values); the comparison uses the first row at each 0.01 s grid time, and algebraic quantities are not compared at the six torque-switch instants (the left and right limits differ). The solver locates those switches to about 10⁻¹² s.
- Tolerances were far looser than the observed agreement. They were not tightened afterwards.

## 5. Findings and failed checks

| # | What | Status |
|---|---|---|
| 1 | **DASSL fails at tolerance ≤ 1e-12**: the log shows a located event at t = 30 s, then NaN. Tolerances 3e-12 and 1e-11 finish; CVODE and IDA at 1e-12 finish the same model. | Not part of the pass criteria, so it does not fail anything. Mechanism not established; a DASSL-at-extreme-tolerance limitation is the likely reading, not a model error (hypothesis). `omc` exits 0 even though the simulation failed |
| 2 | `omc`'s fixed-step `rungekutta` method gave a larger final-energy error (9×10⁻⁷ relative at step 1e-4) than the variable-step methods | Reported as observed; deprecated method; not explained |
| 3 | Equations with the literal 3600 are not unit-checked by `omc` | Covered by Pint |
| 4 | Every number depends on assumed parameters: V_oc, τ_T, tanh width, SoH coefficients, and the unsourced vehicle parameters | Unresolved (outside the scope of an equation check) |

## 6. Errors of my own, found and corrected

1. **Launcher exit code (first run).** The launcher reported failure because `ExitCode` was null for a process started with redirected output. Fixed; the cleanup path had already worked.
2. **Hand reference omitted the friction brake.** The first B2 run **failed** at v = 20 m/s, T = −40 N m (2.3 % in net force). That state is beyond the motor limit (38.77 N m), so the friction brake is active (28.57 N); 28.57/1223.56 = 2.335×10⁻², equal to the observed error to four digits. The model was right and my hand reference was wrong. I corrected the reference, kept the failing output (`modelica-build/check_results_FIRST_RUN_with_B2_failure.csv`), and changed no tolerance.
3. **A defective adjudicating reference.** My first segment-wise DOP853 reference (free step) suggested a 5.9×10⁻⁶ error in Modelica's S2 energy. I localised it to five equal quanta of 0.083 J, one per stop, in the last 0.08 s of each deceleration (v < 0.07 m/s, inside the rolling-resistance smoothing). Direct quadrature of the specification integrand agreed with Modelica to 2 µJ per step and disagreed with DOP853. A free-step integrator crosses the 0.07 s knee in a few steps and never samples it (with a step cap of 0.5 s down to 0.5 ms it converges). The model was right and my tool was wrong. The defective output is kept; the corrected reference agrees with Modelica to ≤ 2×10⁻⁹.
4. **A specification prediction was wrong** (no friction braking in the −40 N m interval). Recorded in specification section 13, together with the model change from version 0.1.0 to 0.1.1 (equations unchanged).
5. **Housekeeping:** a 0-byte file I created by mistake in `C:\Users\HLC\AppData\Local\Temp` was removed; a test drive mapping `Z:` I created to test the launcher was removed. Nothing else outside the project was touched.

## 7. What the agreement means, and what it does not

- **Supported:** the equations in `docs/model.md` are internally consistent (units, signs, force balance, energy accounting); two independent numerical implementations (and a third integrator for the energy) agree on them to 10⁻⁸ to 10⁻¹⁰; the saved 49.714 Wh/km reference is a faithful, slightly discretisation-limited number.
- **Not shown:** that the equations describe a real vehicle (no measured data, all parameters unsourced); that the shared source (`docs/model.md`) contains no conceptual error, since both implementations and the specification derive from it and from one author; behaviour with a controller; anything about SoH scheduling.
- The Modelica plant gives the same energy as the saved reference for an *ideal* trajectory. It says nothing yet about the closed-loop trajectories that make the study's null result.

## 8. Next highest-value validation step

Implement the fixed-gain and the SoH-scheduled LQR in Modelica as a separate phase, with the gains computed outside the project code (for example by the DARE routine preserved in `audit/technical-verification/ind_checks_a.py`), run S1 and S2 at SoH 1.0 and 0.8 on this plant, and compare ΔE and the RMSE ratio with the saved results (+0.0030 %, 1.011 at S1, SoH 0.8) **without tuning anything to match**. That tests the study's actual null result, which depends on the closed-loop tracking difference of a few millimetres, with an independent implementation. Decide beforehand what ΔE tolerance counts as agreement (the quantity is of order 10⁻³ %, so it needs a tolerance fixed in advance, and the DASSL tolerance has to be set far below it).

## 9. Artifact index

| Artifact | SHA-256 (first 16) |
|---|---|
| `verification/modelica/EurekaPlant/Plant.mo` | 41e6b28e2bb7f24d |
| `verification/modelica/EurekaPlant/InverseTracking.mo` | 1e56ff93fc0ed7a2 |
| `verification/modelica/EurekaPlant/Parameters.mo` (generated) | 806f6600bba08b9d |
| `verification/modelica/EurekaPlant/Profiles.mo` (generated) | 26357ad31d9834a1 |
| `verification/modelica/EurekaPlant/Tests/OpenLoop66.mo` | 5c968b3529fa79cd |
| `verification/modelica/negative_fixtures/NegativeFixtures.mo` | c4170d577d420578 |
| `verification/modelica-check-results.csv` | 38168065364ce8dd |
| `verification/cross-implementation-comparison.csv` | fb477e58debc6775 |
| `verification/references/hand_references.json` | 91fdcf26131a8cb3 |
| `verification/references/ideal_reference_segmentwise_dop853.json` | 45047fda7b8e3732 |
| `verification/references/ideal_reference_convergence.json` | 276ca912aca068e1 |
| `verification/references/ideal_reference_knot_aligned.json` | f5c79c8f4986ed27 |
| `verification/Invoke-OpenModelica.ps1` | e69f16113e8f690d |
| `verification/scripts/modelica_checks.py` | 44043bb7577f21c9 |

Raw simulation outputs (git-ignored): `verification/modelica-build/cases/` (27 version-0.1.1 cases plus the diagnostics) and `cases_v0.1.0_when_pre/`; Python references in `verification/modelica-build/python_reference/`; launcher and `omc` logs in `verification/modelica-build/logs/`. Each row of `modelica-check-results.csv` carries the hash of its own artifact.

To reproduce: `generate_modelica_inputs.py`, `hand_references.py`, `generate_case_scripts.py`, the launcher on the five scripts in `verification/modelica/scripts/`, `run_python_plant_openloop.py` (1e-3, 1e-3 with 1.01, 1e-4), `reference_scheme_convergence.py`, `segmentwise_ode_reference.py`, then `modelica_checks.py`. The Python-plant and DOP853 scripts need the project's locked `.venv`; the others run in `verification/python-env`.
