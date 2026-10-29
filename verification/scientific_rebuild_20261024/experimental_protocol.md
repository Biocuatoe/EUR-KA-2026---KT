# Experimental protocol R1: does SoH matter once battery limits exist?

**Status:** frozen 2026-10-24, before any comparative run of this study. Its SHA-256 is
recorded in every run manifest. Any later change is logged in §9 as a dated deviation; this
text is not edited.

**Relation to earlier work.** The pre-registered study (`protocol/preregistration.md`) found
no practical difference between fixed and SoH-scheduled LQR (N01–N04). Its plant lets SoH
change only R0, R1 and the SoC rate, so SoH cannot alter any trajectory the controller acts
on. This study adds the smallest physically motivated mechanism by which SoH can reach the
controlled behaviour, and tests the thesis's scheduling law there. It does **not** reuse the
thesis's 12.5 %/15.3 % figures as targets.

## 1. Questions

- **Q1 (mechanism).** With battery current and voltage limits in the plant, does SoH change
  tracking or energy use of a *fixed* LQR at all, and on which cycles?
- **Q2 (thesis hypothesis).** Where SoH does matter, does the thesis's SoH-scheduled LQR
  (Eqs. 4.39–4.41, γ_v = γ_u = 1) use less energy per km than the fixed LQR without worse
  tracking?
- **Q3 (competing explanation).** Does a single retuned fixed gain match or beat the
  scheduled controller?

## 2. Plant (documented in `model_equations.md`)

The documented model (`docs/model.md`, `src/eureka/plant.py`) unchanged, plus a battery
operating window that bounds the motor torque:

- discharge current I ≤ I_dis = c_dis·Q_nom·s and charge current −I ≤ I_ch = c_ch·Q_nom·s,
  where s = SoH if the limits are *SoH-scaled* and s = 1 otherwise;
- terminal voltage V_min ≤ V_t ≤ V_max;
- the drive torque is limited to η_mi·P_dis,max/ω and the regenerative torque to
  P_ch,max/(η_mi·ω); braking demand beyond the regenerative limit goes to the friction brake.

R0 = R0_new(1 + k_r0(1 − SoH)), as in the thesis Eq. 4.28. Capacity enters only through
SoC and, when SoH-scaled, the current limits. **No capacity-fade model is used** (none is
justified; see `docs/scientific_rebuild/model_assumptions.md`).

## 3. Factors (full factorial; nothing is dropped after observing outcomes)

| Factor | Levels |
|---|---|
| Cycle | S1, S2 (synthetic, existing); UDDS (official EPA schedule, reference); US06 (official EPA schedule, **stress**: known to exceed the vehicle's acceleration and power) |
| SoH | 1.0, 0.9, 0.8, 0.7 |
| Plant case | **B0** no battery limits (= existing model); **BV** voltage window only, k_r0 = 0.5; **BV-k2** voltage window, k_r0 = 2.0; **BCS** voltage window + SoH-scaled current limits c_dis = 3 C, c_ch = 1 C, k_r0 = 0.5; **BCS-k2** as BCS with k_r0 = 2.0; **BCN** as BCS but current limits **not** SoH-scaled (control for the scaling assumption); **BCS2** as BCS with c_dis = 2 C, c_ch = 0.5 C (stricter) |
| Controller | **F** fixed Bryson LQR (pre-registered Q0, R0); **S** SoH-scheduled LQR, γ_v = γ_u = 1; **F01** fixed LQR with R × 0.1 |

That is 4 × 4 × 7 × 3 = **336 runs**.

**Window values** (assumed, generic LFP): V_min = 0.781·V_oc and V_max = 1.141·V_oc. These
are the ratios 2.5/3.2 and 3.65/3.2 of the thesis's LFP cell range (L1211–1213); the thesis
gives no source for them. The current limits (2–3 C discharge, 0.5–1 C charge) and
k_r0 = 2.0 are **assumptions for sensitivity analysis**, with no manufacturer source.

**F01 provenance.** It is the best SoH-averaged member of the pre-registered fixed-gain family
S-C, selected on S1 in the earlier study (`artifacts/reports/fixed_family_results.json`).
It is not tuned again here. On S2, UDDS and US06 it is out-of-sample.

**Design point.** Gains are designed at v0 = 30 km/h, as pre-registered. UDDS and US06 lie
partly outside that domain; this is reported, not corrected.

## 4. Fixed settings for every paired comparison

- Same plant parameters, cycle, initial state (rest, SoC 0.8, V1 = 0) and solver.
- Solver: RK4 at dt = 1 ms, controller ZOH at Ts = 10 ms.
- Conditional anti-windup on the positive torque limit. That limit now includes the battery
  limit, identically for all controllers.
- No noise and no stochastic element. Each run is deterministic, so no p-values and no
  confidence intervals are computed.

## 5. Outcomes (computed at every 10 ms control step, then stored)

- **Distance:**
  - actual distance d and reference distance d_ref [km];
  - shortfall (d_ref − d)/d_ref [%].
- **Tracking:** RMSE and max |v − v_ref| [m/s] over all control steps.
- **Energy:**
  - net battery chemical energy E = ∫V_oc·I dt [Wh];
  - its positive part E⁺ and negative (regenerated) part E⁻;
  - E per actual km [Wh/km];
  - E per reference km [Wh/km].
  - The primary denominator is the actual distance. The reference denominator is reported
    to expose any "saving" that comes from not completing the cycle.
- **Saturation:**
  - fraction of steps where the drive limit binds, and where the binding limit is the
    battery;
  - friction-brake energy [Wh].
- **Battery:**
  - peak and RMS current [A];
  - minimum and maximum terminal voltage [V];
  - integrated current-limit exceedance [A·s], caused by the torque lag;
  - Ah throughput;
  - resistive losses [Wh].
- **Validity:** energy-closure error; non-finite states; infeasible battery solution.
- **Not computed:** capacity fade or battery life. Ah throughput and RMS current are
  reported only as stress indicators, and are not converted to fade.

## 6. Decision rules (fixed in advance)

- **Q2 (S vs F per cycle × SoH × case).** These are the pre-registered rules
  (`protocol/preregistration.md` §9), with ΔE = (E_S − E_F)/E_F × 100 %:

  | Outcome | Condition |
  |---|---|
  | IMPROVES | ΔE ≤ −1 % and RMSE ratio ≤ 1.10 |
  | TRADE-OFF | ΔE ≤ −1 % and RMSE ratio > 1.10 |
  | NO PRACTICAL DIFFERENCE | \|ΔE\| < 1 % |
  | WORSE | ΔE ≥ +1 % |

  - A comparison is also flagged *INCOMPLETE-CYCLE* if either run's distance shortfall
    exceeds 1 %, because energy per km is then not comparable.
- **Q1.** For each case, cycle and controller, take the change from SoH 1.0 to SoH 0.7 in
  RMSE and in energy per km.
  - SoH "matters" when the RMSE changes by more than 5 % or the energy by more than 1 %.
- **Q3.** Holds on a cycle × case if, averaged over SoH with equal weights, F01's energy is
  ≤ S's energy + 0.1 % and F01's RMSE is ≤ S's RMSE.
- **Sanity controls:**
  - at SoH = 1.0, S ≡ F, so ΔE must be exactly 0;
  - BCS and BCN must be identical at SoH = 1.0;
  - B0 must reproduce the saved primary runs (`artifacts/tables/primary_pairs.csv`) to
    ≤ 1e-9 relative in Wh/km.

## 7. Validity (no performance-based exclusion)

A run is invalid only if it has:
- a non-finite state;
- an energy-closure error above 0.1 % of ∫|V_oc·I| dt;
- v < −1e-6 m/s;
- or a battery-current solution that is infeasible at any RK4 stage.

Invalid runs are counted and reported. Tracking failure (RMSE > 1.5 m/s or max |e| > 3 m/s)
is an outcome, not an exclusion.

## 8. Numerical checks (run on the same code)

- **Unit tests:**
  - the extended plant with limits disabled equals `eureka.plant` exactly;
  - the battery-limit formulas match a brute-force root search;
  - energy closure holds with limits active;
  - limit monotonicity in SoH and R0.
- **Timestep convergence:** UDDS and US06, case BCS, SoH 0.7, controllers F and S, at
  dt ∈ {1, 0.5, 0.25} ms.
  - Criterion: ΔE changes by < 0.01 percentage points between successive halvings, and
    Wh/km changes by < 1e-4 relative.
  - A failure is reported and does not change the dt used for the grid.
- **Analytical pre-check** (before the grid):
  - required wheel torque and power along each reference;
  - the R0 value at which the voltage window alone would bind.

## 9. Deviations log

(empty at freezing)
