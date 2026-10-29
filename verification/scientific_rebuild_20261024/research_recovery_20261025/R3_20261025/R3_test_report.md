# R3 test report (Step 3)

**Date:** 2026-10-25.

**Environment:**
- Project venv `D:\EURÉKA 2026 - KT\.venv` (Python 3.14.7, numpy 2.5.4), activated by `scripts\activate.ps1`.
- Command form: `python -I <test>.py` from `code/`.
- FASTSim checks ran in `verification\python-env` (FASTSim 3.1.0).

**Scope.** A passing test confirms only what that test checks. None of these tests compares the model with a real vehicle, motor or battery. The plant's parameters remain thesis values (`report_unverified`) or the R3 assumptions listed in `R3_literature_and_parameter_sources.csv`.

## 1. Runs

| Run | File | Result | Log |
|---|---|---|---|
| 1 | `test_r3.py` (original, unchanged) | 6/6 PASS, exit 0, 95 s | `logs/test_r3_run1.txt` |
| 1 | `test_r3_supplementary.py` | **11/12; 1 FAIL**, exit 1 | `logs/test_r3_supplementary_run1.txt` |
| 2 | `test_r3_supplementary.py` (test corrected, §3) | 12/12 PASS, exit 0 | `logs/test_r3_supplementary_run2.txt` |
| 1 | `test_r3_v1_additions.py` | 5/5 PASS, exit 0 | `logs/test_r3_v1_additions_run1.txt` |
| final | all three files, on the code hashed at the freeze | 6/6, 12/12, 5/5 PASS; all exit 0; stderr empty | `logs/*_prefreeze_final.txt` |

`r3_lib.py` changed twice after `test_r3.py` run 1: it gained `motor_models()` and the v1 additions. Both changes were new functions; no existing function changed. The final runs used the frozen code (`logs/protocol_v1_sha256_at_freeze.txt`, `r3_lib.py` SHA-256 `c2403adc…1c97`).

## 2. What each requirement rests on

| # | Requirement (task list) | Test(s) | Measured margin |
|---|---|---|---|
| 1 | M0 reproduces the R1 plant | `test_r3::test_const_model_equals_r1` (200 states × 3 limit sets × 2 SoH, rtol 1e-12); `supp::test_m0_margin_vs_r1` (3,000 random states incl. \|T\| to 90 N·m, \|V1\| to 1 V) | worst \|Δ\|/(1+\|R1\|) = **9.1e-14**; torque-limit feasibility flags identical |
| 2 | New energy accounting matches R1's exact-tracking ledger within 0.2 % | `test_r3::test_quasistatic_matches_r1_exact_tracking` (S1); `supp::test_qs_vs_r1_ledger_all_rows` (every feasible unstretched row of `../../recovery_feasibility_20261025/ledger_ideal.csv`: 16 rows, S1/S2, SoH 0.7–1.0, k_r0 0.5–3.5) | worst **0.071 %**. R1's ledger is a separate implementation (midpoint sums at 10 ms, exact V1 propagation) by the same author with the same physics: a cross-implementation check, not independent replication |
| 3 | Units and signs: mechanical, electrical, current, positive energy, regeneration | `supp::test_signs_and_independent_point_power` (6 operating points; terminal and friction power against a hand formula); `supp::test_dynamic_closure_m0_m1` (E_pos ≥ 0 ≥ E_neg, E_pos + E_neg = E_chem, E_regen ≤ 0) | **5.3e-15** relative; E_pos + E_neg − E_chem ≤ 1.2e-9 J |
| 4 | Energy closure | `test_r3::test_dynamic_closure_copper` (M2); `supp::test_dynamic_closure_m0_m1` (M0, M1; S2, L-EVE) | closure **2.6e-10 / 2.7e-10** of throughput (criterion 1e-3) |
| 5 | Interpolation gives physical values | `supp::test_m1_curve_physical` (η on 100,001 points; L ≥ 0 on 200,001 points; L continuous at 0; P_e strictly increasing) | η ∈ **[0.8400, 0.9500]**; max \|ΔL\| 0.034 W per 0.18 W step |
| 6 | Zero power, zero speed, sign changes, regeneration | `supp::test_grid_finite_and_constraints_enforced` (5,751 (v, a) points incl. v = 0 and a from −3.5 to 3.5 m/s², × 3 models × 3 limit sets × 2 SoH); `supp::test_m1_curve_physical` (L(±1e-9 W)) | all finite; friction ≥ 0 everywhere |
| 7 | Constraints enforced or flagged | same grid test: every feasible point within torque/power envelope, discharge limit and charge limit; M1 never beyond x = 1. `supp::test_regen_limit_friction_and_current`: hard braking clamps charge current at the limit and sends the rest to friction | 71,215 feasible points satisfy every limit; 32,303 flagged infeasible. Charge current **100.0 A at a 100.0 A limit**, friction 24.2 kW |
| 8 | Same equations in every objective | `supp::test_qs_and_dynamic_share_equations` (QS point vs dynamic `derivatives` at the same (v, T), 3 models × 4 points); every optimiser computes energy only through `QSPlant.step` | current difference **0**, acceleration difference **1.1e-16 m/s²** |
| 9 | Inverse maps (battery limit → torque limit) | `test_r3::test_inverse_maps` (3 models incl. a synthetic curve); `supp::test_m1_inverse_maps` (actual M1) | M1 worst **1.5e-5** relative |
| 10 | Optimisers exact on their grids | `supp::test_band_dp_is_global_on_its_grid` (625 paths); `supp::test_eco_dp_is_global_on_its_grid` (125 sequences); `v1::test_track_dp_global_…` (28,561 paths) | objective equal to enumeration |
| 11 | Dual bounds valid | `supp::test_band_lagrangian_bound_valid`; `v1::test_band_min_energy_tab_and_bound`; `v1::test_eco_solver_bound` | LB ≤ exact ≤ found in all three. In one case found > exact (1210.5 vs 1199.7 J): the bisection returns a *supported* point, not the constrained optimum (§ `R3_optimizer_validity.md`) |
| 12 | Fast table DP identical to original | `v1::test_band_tables_equal_band_dp` (3 models × 3 μ); `v1::test_band_min_energy_tab_and_bound` | path difference **0** |

## 3. The failure, and what was changed

**Run 1 of `test_r3_supplementary.py`**: `test_signs_and_independent_point_power` raised a bare AssertionError. The diagnosis (command and output in the session; values reproduced here) found:

- At 12 m/s and −2 m/s², braking needs −67.40 N·m.
- The motor envelope there is P_max/ω = 64.62 N·m.
- The model clamps regeneration at the envelope and sends 798 W to the friction brake.
- The test's hand formula ignored the envelope and asserted zero friction.

**Origin:** the test's assumption, not the model, the environment or the numerics.

**Change:** the hand formula now applies the envelope and also checks the friction power (a stronger check). The case was kept, not removed. The reason is written in the test's docstring, and the failed log is preserved.

No other test was changed after it ran.

## 4. What the tests do not establish

- That any parameter matches the thesis vehicle or any real vehicle.
- That M1 or M2 represent a real motor (`R3_motor_curve_audit.md`).
- That the grid optimum equals the continuous optimum. Discretisation is checked separately in the gates (protocol §8).
- Anything about battery ageing.
