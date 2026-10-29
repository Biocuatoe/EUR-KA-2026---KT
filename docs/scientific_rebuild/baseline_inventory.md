# Baseline inventory: what actually implements each part of the study

**Date:** 2026-10-24. **Workspace:** `D:\EURÉKA 2026 - KT` (confirmed with `pwd` and a
directory listing).

Every entry was read from the files themselves; the thesis description was not assumed to
match.

| # | Component | Authoritative implementation | Thesis description | Match? | Status |
|---|---|---|---|---|---|
| 1 | Longitudinal dynamics | `src/eureka/plant.py` `derivatives` (point mass, M_eff = M + J_m G²/r_w², rolling resistance with tanh smoothing, quadratic drag, holding brake at v = 0, flat road); `docs/model.md` §1 | Eq. 2.17–2.25 (correct) and Eq. 4.1–4.7 (dimensionally invalid) | Eq. 2.17–2.25 yes; Eq. 4.1–4.7 no | Gate-tested: coast-down closed form, steady-speed equilibrium, finite-difference linearisation (`tests/test_plant.py`) |
| 2 | Motor and drivetrain | `plant.py` `torque_limit` (T_max = 85 N·m, P_max = 18 kW), first-order torque lag τ_T = 20 ms (**assumed**), gear efficiency 0.9702 (motoring/regenerating directions), constant motor/inverter efficiency 0.874 (**peak value**), viscous friction | PMSM dq model (Table 8), shown infeasible on 48 V (`docs/thesis_full_scientific_audit.md` D2) | No: the project uses a torque-controlled drive, not the thesis's PMSM | Gate-tested; efficiency map absent |
| 3 | Battery electrical model and energy | `plant.py`: 1-RC Thevenin, constant V_oc = 48 V (**assumed**), R0 5 mΩ, R1 3 mΩ, C1 50 kF; battery current from the quadratic P_e = (V_oc − V1 − R0 I) I; energy E_chem = ∫V_oc·I dt with a full loss ledger and a closure check | Eq. 2.11–2.13 (polynomial OCV not used) | Structure yes; OCV constant | Closure ≤ 5.4e-10 in the saved runs (`artifacts/tables/energy_breakdown.csv`) |
| 4 | Capacity fade and resistance growth | **No capacity-fade model.** R0, R1 scale with SoH (Eq. 4.28–4.29, k_r0 = 0.5, k_r1 = 0.3, report_unverified); capacity enters only the SoC rate (Q·SoH). SoH is constant within a run | Eq. 4.21–4.27 SEI model (not implementable: k_c and k_cal missing) | No | — |
| 5 | SoH definition and estimation | SoH is a **known input** (oracle) per run. There is no estimator | Coulomb counting + voltage correction (Eq. 2.61) and EKF (Eq. 4.52–4.64); the EKF cannot identify capacity as written (audit M-21) | No | Oracle SoH is the best case for scheduling (`protocol/preregistration.md` §5(d)) |
| 6 | Fixed-gain LQR | `src/eureka/controllers.py` `design_model` (x = [e, T, z], linearised at 30 km/h), `zoh` (exact), `bryson_weights`, `dlqr` (`scipy.linalg.solve_discrete_are`); `gain(…, "fixed")` | Eq. 6.5: Q = diag(10, 1, 1, 0.5), R = 1 (contradicts Bryson: C27) | Method yes, weights no | Gate: DARE vs value iteration, eigenvalues vs python-control, controllability |
| 7 | SoH-scheduled LQR | `controllers.py` `scheduled_weights` (thesis Eq. 4.39–4.41, α_v on the torque state; γ_v = γ_u = 1 **assumed**); `gain(…, "scheduled", soh)` | Eq. 4.37–4.42 incl. ΔA(SoH) on the invalid current state | Weights yes; ΔA = 0 (pre-registered deviation) | Frozen-time stability over SoH ∈ [0.5, 1], γ ∈ [0, 10] (Hypothesis test) |
| 8 | Drive cycles and initial conditions | `configs/cycles/profiles.yaml` + `src/eureka/cycles.py` (P-TUNE, S1, S2: **synthetic** piecewise-linear); `data/processed/drive_cycles/epa/*.csv` (official EPA UDDS, HWFET, US06; provenance in `audit/external-data-provenance.csv`). Initial state: rest, SoC 0.8, V1 = 0 | NEDC, WLTP, CLTC, VUC (no time series; VUC impossible) | No | EPA files validated (`data/processed/drive_cycles/epa/validation_results.json`) |
| 9 | Tuning and optimisation | Bryson's rule with stated maxima (`configs/parameters.yaml` controller.*), pre-registered acceptance on P-TUNE (`scripts/tuning_acceptance.py`); fixed-gain family S-C (41 R scalings) | NSGA-II, PSO, fmincon (none exist) | No | — |
| 10 | Metrics, statistics, figures | `src/eureka/metrics.py`, `scripts/analyze.py`, `scripts/energy_breakdown.py`, `scripts/make_figures.py`; pre-registered decision rule (±1 % ΔE); bootstrap only for S-D | Monte Carlo, Morris, ANOVA, t-tests (no data) | No | Saved outputs hashed in `evidence/artifact_hashes.json` |
| — | Independent implementation | `verification/modelica/…` (OpenModelica controller and plant), `verification/controller-crosscheck-report.md`: 554/570 checks pass; DASSL only; S1 distance FAIL unresolved | — | — | Cross-implementation only; same author |

**Consequences for the hypothesis (Phase B finding).**
- In the authoritative plant, SoH changes only R0, R1 and the SoC integration rate.
- No battery current, voltage or power limit exists, so **SoH cannot change any trajectory
  the controller acts on**. Energy differs only through I²R losses: 1.1–2.1 % of supplied
  energy in the tested runs (N04).
- This is why the pre-registered study found no practical difference (N01).
- The rebuild (`verification/scientific_rebuild_20261024/`) adds the smallest physically
  motivated pathway, a battery operating window, and tests the hypothesis there.

**Baseline test status in this session:**
- Full suite in the activated environment (`. .\scripts\activate.ps1; python -m pytest -q`):
  **155 passed** (46 s).
- The same suite run from an unactivated shell gave 16 failures, all in
  `tests/test_environment.py` (environment-variable checks). That is expected without
  activation.
