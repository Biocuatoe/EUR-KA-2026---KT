# EURÉKA 2026 KT: independent evaluation of the report's claims

Date: 2026-10-23. Author of this evaluation: Claude (AI research assistant), working in
the user's repository. Every number below is read from a saved artifact named in
`evidence/evidence_matrix.yaml`. This document reports results whatever their direction.

## Summary

- **None of the report's quantitative claims could be reproduced.** No code, run output or
  dataset behind them exists on this machine. Of the 40 registered claims, 25 are
  **CONTRADICTED** by reproducible checks of the report's own numbers or equations, or by
  the pre-registered experiment.
- **The existing figures are not simulation output.** They were generated from random
  noise around hard-coded values (`D:\EUREKA\scripts\render_kt01_figures.py`). The ± intervals
  on the headline numbers were added as an editorial fix (`D:\EUREKA\AUDIT_REPORT.md` L28, L195).
- **The report's vehicle model is dimensionally invalid** (traction depends on motor
  speed, not torque) and was replaced by a documented, verified model.
- **Pre-registered result:** on that model, the report's SoH-scheduled LQR changes
  model-computed energy per km by **+0.003 %** (S1, SoH 80 %) relative to a fixed-gain LQR,
  with 1.1 % worse tracking. This is **no practical difference** under the pre-registered
  ±1 % margin, and far from the claimed −12.5 % ± 2.1 %.
- **A single, well-tuned fixed gain does better** than the schedule on both energy and
  tracking, averaged over SoH (competing hypothesis H_C holds).
- **In this model no controller tracking the same profile could save 12.5 %.** Battery
  resistive losses, the part a controller can shape, are only 1.1-2.1 % of supplied energy.

## Phase 1: Claim registry

**What was done:**

- The original `.docx` was preserved read-only (SHA-256 `01363A06…8C`) and converted
  with pandoc 3.11.
- 40 material claims were registered with 84 verbatim quotes and line locations
  (`evidence/claim_registry.yaml`). A test asserts each quote occurs at its stated line,
  and all pass.
- 17 consistency checks recompute report numbers from the report's own inputs
  (`artifacts/reports/report-consistency-checks.json`).

**Results:** all 17 checks find an inconsistency. Selection bias is likely, because the
checks were written after reading the report, for suspected problems. The checks do record
consistent sub-results where they exist: NEDC and CLTC average speeds agree, and 6 of 7
terms of the report's A matrix are dimensionally consistent.

**Named claims:**

| Claim | Finding |
|---|---|
| 12.5 % ± 2.1 % energy improvement (C01) | The body implies 10.2 %; the ± was added editorially |
| 15.3 % ± 2.8 % less capacity fade (C02) | The body gives 14 %; the ageing model is underspecified |
| VUC provenance (C07, C08) | Called "derived from real-world measurements" yet "not real measured data". Its own statistics are impossible: 5.8 km in 600 s is 34.8 km/h, not 28.5, and 17 × 22 s of stops is 62 % idle, not 20.1 % |
| Monte Carlo counts (C10, C11) | 100 trials per configuration (2400 runs) vs N = 1000; the summary tables contradict "all samples < 0.6 m/s" |
| Safety and hardware (C17-C21) | ASIL B with 94 % diagnostic coverage, hardware timings, SIL/PIL and field data have no artefacts, and are contradicted by the report's own Declaration |
| Statistics (C13) | 9 of 18 reported p-values fail the Bonferroni threshold that the report says they pass |

**Gate:** the registry is complete, so Phase 2 may proceed. No claim is used as a target.

## Phase 2: Research question (pre-registered)

`protocol/preregistration.md` was committed in `126750a` **before** any plant or
controller code existed. It fixes:

- the hypotheses H1, H0, H_W and H_C;
- the primary outcome, energy per km on S1 at SoH 80 %;
- the decision rule (±1 % energy margin, RMSE ratio ≤ 1.10);
- the tuning procedure, the run-validity rules and the verification gate.

A clarification of the robustness analysis S-D (operating point, nominal-design gains) was
committed in `38f443a` before any evaluation run.

**Deviations forced by the report:**

- (a) α_v is applied to motor torque instead of battery current.
- (b) ΔA = 0, because the report's ΔA acts on an equation that has no physical counterpart.
- (c) γ_v = γ_u = 1 is assumed, because the report gives no values.
- (d) SoH is known exactly. This is the best case for the scheduled controller.

## Phase 3: Model and parameter provenance

**Model:** `docs/model.md` documents a nonlinear longitudinal plant. It has a 1-RC battery
whose R0 and R1 depend on SoH through report Eqs. 4.28-4.29, torque and power limits, a
friction brake, and energy accumulators.

**Parameters:** `configs/parameters.yaml` holds 33 parameters, each with value, unit,
source, location, provenance type, valid range, uncertainty and use. 20 are
*report_unverified*, 11 *assumed* and 2 *standard*. None are measured or come from a
cited primary source. Units are converted with Pint at load time, so a wrong dimension is
rejected (tested).

**Rejected:** report Eq. 4.3 (dimensionally inconsistent, CHK-AMATRIX-DIM).

**External validity:** none. The vehicle is hypothetical and the profiles are synthetic.

## Phase 4: Independent verification (gate)

**Gate result:** `scripts/run_gate.py` passed at `38f443a`, with 152 tests, 0 failures and a
clean tree.

**Independent references used:**

- hand-calculated resistance forces;
- torque equilibrium at steady speed;
- the closed-form coast-down (rel. 1e-9);
- DOP853 (rel. 1e-6);
- finite-difference linearisation;
- python-control's ZOH and dlqr;
- an independent value-iteration DARE;
- controllability;
- frozen-time stability for every SoH in [0.5, 1] and γ in [0, 10] (Hypothesis);
- saturation, anti-windup and friction-brake checks;
- non-negative loss rates (Hypothesis);
- energy-balance closure for arbitrary torque sequences (Hypothesis);
- profile arithmetic, parameter-unit rejection, and pipeline lineage.

**Tuning acceptance** (P-TUNE only) passed on attempt 1: overshoot 3.7 %, no oscillation,
max |λ| 0.989.

**Defects found and fixed before the gate:**

- a meaningless placeholder for the battery-feasibility flag (replaced by a real per-stage check);
- two wrong report line references in the parameter file;
- the pipeline test crashing on an unregistered experiment name.

Passing tests prove only the tested properties, not physical accuracy.

## Phase 5: Comparative experiment

| Item | Value |
|---|---|
| Runs | 16 attempted, 16 valid; worst closure error 5.4 × 10⁻¹⁰ |
| Sanity control | At SoH 100 % the two controllers were bit-identical, as designed |
| **H1 decision** | **NO PRACTICAL DIFFERENCE**: S1, SoH 80 %, ΔE = +0.0030 % (49.9025 → 49.9040 Wh/km), RMSE ratio 1.011 |
| All 8 pairs (S1/S2 × SoH 100/90/80/70) | NO PRACTICAL DIFFERENCE; the scheduled controller is marginally worse on both metrics, increasingly so as SoH falls (ΔE up to +0.005 %, RMSE up to +2.0 %) |
| Direction | Contrary to the report's narrative: its weight laws soften the controller as SoH falls, and in this model that increases both tracking error and energy slightly |

Figures: `primary_dE_rmse_vs_soh.png` and `tracking_error_S1_soh80.png`.

## Phase 6: Sensitivity and robustness

- **S-B (γ sweep, 15 settings):** all NO PRACTICAL DIFFERENCE; ΔE from −0.019 % to
  +0.040 %. Settings that lower energy also lower tracking error, and vice versa.
- **S-C (H_C):** 164 runs, all valid. The fixed-gain family R × 0.1 … 10 spans only 0.28 %
  in energy. Energy and RMSE fall *together* as R falls, so there is no trade-off. The best
  feasible fixed gain (R × 0.1) beats the schedule on SoH-averaged energy (49.854 vs
  49.881 Wh/km) **and** RMSE (0.038 vs 0.051 m/s), so **H_C holds**. The best point sits at
  the edge of the pre-registered range, which was not extended after seeing results.
- **S-D (paired robustness):**
  - The pilot sd of ΔE was 0.014 pp, so the pre-registered rule gave N = 50 and the pilot
    is the full sample. All 100 runs are valid, seeds 20261023 + draw.
  - Mean ΔE = −0.054 % (bootstrap 95 % for the Monte Carlo mean: −0.058 to −0.050 %). The
    scheduled controller is lower in all 50 draws, but every draw is inside ±1 %.
  - Median RMSE ratio 1.011, with 0 tracking failures.
  - The sign differs from the noise-free primary result. A plausible reason is that lower
    gains amplify measurement noise less; this was not tested separately.
  - Parameter ranges are *assumed*. The interval is Monte Carlo uncertainty over that
    assumption, not an inference about vehicles. No p-values are reported.
- **Energy decomposition (S1, SoH 80 %):** road loads 68.2 %, motor/inverter 22.0 %, gear
  4.7 %, battery resistive 2.0 %, friction brake 0 %.

## Phase 7: Data lineage

The chain is: `configs/` → `scripts/run_experiment.py` (gate-checked, clean tree) →
`artifacts/raw/<exp>/<batch>/{manifest.json,timeseries.npz}` → `scripts/analyze.py`
(validation, then `data/processed/<exp>/runs.csv`) → `artifacts/tables`, `artifacts/reports`
→ `scripts/make_figures.py` → `artifacts/figures/evaluation` → `evidence/evidence_matrix.yaml`.

Each manifest records:

- the Git commit and dirty flag;
- software versions;
- the configuration and parameter hashes;
- the profile knots;
- per-run gains, overrides and seeds.

`evidence/artifact_hashes.json` holds the SHA-256 of every result file. Commands are in
`docs/lineage.md`. No claimed number appears in source code, tests or plots, except as
labelled references to the report, such as the annotation "report claim −12.5 %".

## Phase 8: Optional components

NSGA-II, battery ageing, safety/ASIL and the other benchmarks are excluded with reasons
(`docs/optional-components.md`).

## Phase 9: Evidence matrix

`evidence/evidence_matrix.{yaml,csv,json}` has 44 rows: 40 original claims and 4 restated.

| Status | Rows |
|---|---|
| CONTRADICTED | 25 |
| NOT_TESTED | 8 |
| REQUIRES_PHYSICAL_VALIDATION | 4 |
| IMPLEMENTED_NOT_VALIDATED | 2 |
| CONSISTENT_WITH_RECORD | 1 |
| SIMULATION_SUPPORTED | 4 (only the restated claims N01-N04) |

Status conditions and precedence are defined in `src/eureka/evidence.py` and exported
with the matrix.

## Phase 10: Unsupported conclusions and limits

**Unsupported, must not appear in a revised report:**

- any energy saving from SoH scheduling;
- any capacity-fade reduction;
- the VUC as measured data;
- Monte Carlo success rates;
- statistical significance;
- ASIL compliance or diagnostic coverage;
- hardware timings, SIL/PIL, field data;
- benchmark rankings;
- NSGA-II results;
- economic payback derived from the energy claim.

**Limits of this study** (they bound N01-N04):

- The profiles are synthetic and never activated the traction limit or friction brake, so
  actuator-constrained behaviour is untested.
- Constant motor/inverter efficiency hides part-load efficiency effects.
- V_oc is constant, the road flat, the temperature fixed, and there are no auxiliary loads.
- SoH is known exactly.
- In S-D the controllers keep their nominal designs.
- γ values and the deviation mappings (a)-(b) were assumptions forced by the report.
- Standard cycles were not used: the official tables could not be retrieved, and a
  reconstruction from memory failed its acceptance check.
- Nothing here has been validated against a real vehicle.

**What would change the conclusions:**

- a measured motor efficiency map;
- grades and actuator-saturating profiles;
- official standard cycles;
- an SoH estimator with error;
- a validated LFP degradation model.

The pipeline accepts each of these without changing the analysis code.
