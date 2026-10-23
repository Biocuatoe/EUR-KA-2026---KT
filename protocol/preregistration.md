# Pre-registration: fixed-gain vs SoH-scheduled LQR on a documented EV longitudinal model

Status: **locked before implementation** of the plant, controllers and experiment code.
The Git commit containing this file is the registration timestamp. Any later change to
this file must be a new commit with a "Deviation" entry in section 12. Results never
change hypotheses, metrics, thresholds or tuning.

## 1. Scope

Phase 1 found that none of the report's quantitative claims can be reproduced: there is no
code or data, and the inconsistencies are listed in `evidence/claim_registry.yaml`. This
study therefore does **not** try to reproduce 12.5 % or 15.3 %. It asks the smallest
question the report's method can actually be tested on.

Kept apart from this question and not tested here: battery ageing (C02, C04-C06),
NSGA-II (C31), safety and certification (C17, C18), hardware (C19, C20), the other
benchmarks (C30) and the EKF (C29). See `docs/optional-components.md`, which will be
written in Phase 8.

## 2. Research question

On a documented, dimensionally consistent longitudinal model of a 48 V micro-EV with
SoH-dependent battery resistance, does the report's SoH-scheduled LQR (Eqs. 4.39-4.42,
mapped as in section 5) change **model-computed battery energy per km** and **velocity
tracking error** relative to a fixed-gain LQR designed at SoH = 100 %? Conditions are
flat road, 0-50 km/h synthetic urban profiles, SoH 70-100 %, and SoH known exactly.

## 3. Hypotheses

- **H1 (primary, from the report):** at SoH = 80 % on profile S1, the scheduled LQR uses
  less battery energy per km than the fixed LQR without worse tracking, i.e.
  ΔE ≤ −1.0 % and RMSE_sched / RMSE_fixed ≤ 1.10.
- **H0 (null):** |ΔE| < 1.0 % (no practical difference).
- **H_W (worse):** ΔE ≥ +1.0 %.
- **H_C (competing explanation):** any energy difference is a tracking-vs-energy weight
  trade-off that a single, non-scheduled fixed gain can match over the battery's life. At a
  fixed SoH the scheduled controller *is* a fixed-gain LQR with weights Q(SoH), R(SoH),
  so adaptation can only add value across SoH levels (see S-C in section 8).

Here ΔE = (E_sched − E_fixed) / E_fixed × 100 %, where E is energy per km. The decision
rule is applied exactly as written in section 9.

## 4. Plant model (documented in `docs/model.md`; parameters in `configs/parameters.yaml`)

- Point-mass longitudinal dynamics with effective mass M + J_m G²/r_w². Rolling
  resistance C_rr M g (smoothed with tanh(v/0.05 m/s)) and aerodynamic drag ½ρC_dA_f v|v|.
  No grade. The vehicle cannot reverse: at v = 0, a net negative force is absorbed by the
  holding brake.
- Traction force G (T − B_m ω) η_g^{±1} / r_w, where the efficiency is applied in the
  direction of power flow. The motor speed is ω = G v / r_w.
- Motor torque follows the command through a first-order lag with τ_T = 0.02 s. The
  command is limited to |T| ≤ min(T_max, P_max/ω). Braking demand beyond the negative
  limit goes to a lossy friction brake, so both controllers get their braking request.
- Electrical side: constant motor+inverter efficiency, applied in the direction of power
  flow. The battery is a Thevenin model with one RC branch: V_oc = 48 V constant, with
  R0(SoH) and R1(SoH) from report Eqs. 4.28-4.29. SoH is constant within a run.
- Integration: fixed-step RK4 at 1 ms. Controller: zero-order hold at T_s = 10 ms.
- The report's Eq. 4.3 is **not** used: it is dimensionally inconsistent (CHK-AMATRIX-DIM).

## 5. Controllers

The design model is linearised at v0 = 8.33 m/s (30 km/h), with state
x = [v − v_ref, T, z], where z = ∫(v − v_ref) dt and the input is T_ref. It is discretised
by ZOH at T_s = 10 ms, and gains come from the DARE (`scipy.linalg.solve_discrete_are`).
The control law is u = −K x, with conditional anti-windup: z is frozen while the positive
traction limit is active and the error would push further into the limit. Both
controllers share identical implementation, limits, friction brake and anti-windup.

**Pre-registered tuning (Bryson's rule at SoH = 100 %):** Q0 = diag(1/0.5², 1/85², 1/0.5²)
and R0 = 1/85². These use maxima of 0.5 m/s velocity error, 85 Nm torque, 0.5 m
integrated error and 85 Nm input.

- **Acceptance check on the tuning profile P-TUNE only (never on S1/S2):** all closed-loop
  eigenvalues |λ| < 1, step overshoot < 10 %, and no sustained oscillation (zero-crossing
  rate of the error during holds < 0.5 Hz).
- **If it fails:** double the velocity-error maximum and repeat, at most 3 times; record
  each attempt. The tuning result is frozen in a commit before evaluation runs.

**Fixed LQR:** K(Q0, R0) at every SoH.

**Scheduled LQR (report Eqs. 4.39-4.42):** K(Q(SoH), R(SoH)), with
Q(SoH) = diag(q_v, α_v(SoH)·q_T, q_z), where α_v = 1/(1 + γ_v(1 − SoH)), and
R(SoH) = R0 (1 + γ_u(1 − SoH)).

Mapping and deviations, all forced by the report:

- (a) The report applies α_v to its second state, battery current. Here it is applied to
  motor torque, which is proportional to current under current control.
- (b) The report's ΔA(SoH) acts on its battery-current equation, which has no counterpart
  in a physically consistent torque-input model, so ΔA = 0.
- (c) γ_v and γ_u are not given in the report. **Primary: γ_v = γ_u = 1.0**, with a
  sweep in S-B.
- (d) SoH is known exactly (no EKF). This is the best case for the scheduled controller.

## 6. Reference profiles (`configs/cycles/*.yaml`, all **synthetic**)

- **P-TUNE:** steps and ramps, used for tuning and verification only.
- **S1 (primary evaluation):** urban stop-and-go, 0-50 km/h, accelerations 0.5-1.0 m/s²,
  decelerations 0.5-1.0 m/s², four stops. The traction power limit becomes active above
  about 33 km/h.
- **S2 (secondary evaluation):** congested low speed, ≤ 25 km/h, six short stop-and-go events.

Standard cycles (ECE-15/NEDC, WLTC, CLTC) are **not** used. Their official time series
could not be retrieved in this session (UNECE/ARAI sources unreachable). A reconstruction
of ECE-15 from memory, checked by hand before this registration, gave 1014.6 m and 60 s
idle against DieselNet's published 994.1 m and 57 s, so it fails the acceptance check
(±1 %). The report's VUC has no time series and impossible statistics (C08). Standard
cycles can be added later as `data/raw/cycles/*.csv` with their source recorded.

## 7. Variables

| Kind | Variables |
|---|---|
| Independent | controller ∈ {fixed, scheduled}; SoH ∈ {1.00, 0.90, 0.80, 0.70}; profile ∈ {S1, S2}; (S-B) γ_u ∈ {0, 0.5, 1, 2, 5} × γ_v ∈ {0, 1, 5}; (S-D) parameter draw and noise seed |
| Controlled (identical for both controllers in every pair) | plant parameters, initial state (v = 0, T = 0, z = 0, V1 = 0, SoC = 0.8), horizon = profile duration, T_s, integrator, limits, friction-brake logic, anti-windup, disturbance realisation (none in primary) |

## 8. Outcomes and analyses

**Primary outcome:** E = battery chemical energy ∫V_oc I dt per distance travelled [Wh/km]
on S1 at SoH = 0.80, γ = 1, as ΔE (%).

**Secondary outcomes:** tracking RMSE and max |v − v_ref| [m/s]; RMS and peak battery
current [A]; Ah throughput; resistive loss energy [Wh]; friction-brake energy [Wh];
recovered regen energy [Wh]; fraction of time traction-limited; RMS jerk [m/s³].

| ID | Analysis |
|---|---|
| S-A | Both profiles × all four SoH levels, γ = 1. |
| S-B | γ sweep at SoH = 0.80 on S1. |
| S-C (tests H_C) | Fixed-gain family K(Q0, c·R0) with c ∈ logspace(−1, 1, 41), evaluated at all four SoH levels on S1. Rank each member by SoH-averaged E (equal weights) subject to SoH-averaged RMSE ≤ the scheduled controller's SoH-averaged RMSE. **H_C holds** if some member's averaged E ≤ the scheduled controller's averaged E + 0.1 %. |
| S-D (robustness) | Paired parameter perturbations, uniform within ranges labelled *assumed* in `configs/parameters.yaml`, plus Gaussian velocity-measurement noise σ = 0.05 m/s. The same draw and noise realisation are used for both controllers. Pilot of N = 50; then N = min(1000, max(50, ⌈(1.96·sd/h)²⌉)) with h = max(0.1 percentage points, 0.1·|mean ΔE|). Base seed 20261023, per-draw seeds recorded. Reports the mean paired ΔE with a bootstrap 95 % CI (10 000 resamples) and the fraction of draws with ΔE < 0. |

S-D's interval describes Monte Carlo uncertainty over an *assumed* parameter distribution.
It is not a statement about real vehicles, and **no p-values or significance claims will
be made** (the simulations are deterministic given their inputs).

**Sanity control:** at SoH = 1.00 the two controllers are identical by construction, so
ΔE must be exactly 0. If it isn't, the experiment is invalid.

## 9. Decision rule for H1 (applied verbatim)

| Outcome | Condition |
|---|---|
| IMPROVES | ΔE ≤ −1.0 % and RMSE ratio ≤ 1.10 |
| TRADE-OFF | ΔE ≤ −1.0 % and RMSE ratio > 1.10 |
| NO PRACTICAL DIFFERENCE | \|ΔE\| < 1.0 % |
| WORSE | ΔE ≥ +1.0 % |

The ±1 % margin is fixed in advance. It is about the resolution at which a model this
simplified (constant efficiencies, constant V_oc) can be trusted to rank energy use.

## 10. Run validity (inclusion and exclusion)

All attempted runs are logged with run ID, configuration hash, seed and Git commit. A run
is **excluded** only if it is numerically invalid:

- a non-finite state,
- energy-balance closure error > 0.1 % of the energy throughput ∫|V_oc I| dt, or
- v < −1e-6 m/s.

Excluded runs are counted and reported. There is no performance-based exclusion.

Tracking failure (RMSE > 1.5 m/s or max |e| > 3 m/s, the report's own specification) is
an **outcome**, not an exclusion. If any primary-analysis run is invalid, the primary
analysis is reported as failed and later phases that depend on it do not run.

## 11. Verification gate (must pass before any evaluation run)

The following must pass first:

- analytic resistance forces and steady-speed torque equilibrium;
- coast-down against the closed-form solution;
- the dimensional check of every parameter unit;
- the linear design model checked against finite-difference linearisation of the plant;
- controllability of the design model;
- DARE gains checked against an independent value-iteration solution;
- closed-loop eigenvalues inside the unit circle, checked independently with python-control;
- correct saturation, anti-windup and friction-brake behaviour;
- energy-balance closure;
- RK4 checked against `solve_ivp` (rtol 1e-9);
- profile generator checks;
- property-based tests (Hypothesis).

A passing test establishes only the tested property, never physical accuracy.

## 12. Deviations log

(none yet)
