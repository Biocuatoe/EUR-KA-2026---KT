# Baseline scientific position (Phase 1)

**Date:** 2026-10-25. **Scope:** what the submitted thesis claims, what R1 implemented and tested,
and where the two differ. No new simulation is used in this file; every statement points to a
project file. **Independence:** written by the AI assistant that built R1; no person has checked it.

Evidence labels: **analytical derivation**, **numerical verification**, **simulation result**,
**source-grounded parameter**, **assumed scenario**, **unverified physical behaviour**.

---

## 1. The hypothesis the thesis intended to test

Thesis (`data/processed/report/report.md`, in-project copy; DOCX untouched):

- **Main research question (L581):** how to design an adaptive control framework that
  simultaneously optimises energy efficiency, battery longevity and driving performance for an
  urban micro-EV across battery ageing states.
- **Claimed mechanism (L3174–3194, Eqs. 4.37–4.42):** ageing changes the plant,
  A(t) = A₀ + ΔA(SoH) with ΔA = ΔR_int(SoH)/L_eq. The LQR weights are scheduled on SoH,
  Q(SoH) = Q₀·diag(1, α_v(SoH), 1) and R(SoH) = R₀(1 + γ_u(1 − SoH)), and the gain is recomputed
  from a **real-time SoH estimate** (Coulomb counting with correction, and an EKF; L5, L822–824).
- **Claimed results (abstract L9):** "up to 12.5 % ± 2.1 % improvement in energy efficiency and
  15.3 % ± 2.8 % reduction in battery capacity fade over 1000 operational cycles compared to the
  fixed-gain LQR baseline". The thesis also reports NSGA-II Pareto fronts, an SEI/Arrhenius ageing
  model, six benchmark controllers and the NEDC, WLTP, CLTC and VUC cycles.

The implied hypothesis: *scheduling LQR weights on battery SoH reduces energy use and capacity fade
relative to a fixed-gain LQR on the same micro-EV task.*

## 2. What R1 actually implemented

`experimental_protocol.md` (frozen, SHA-256 `d80b5b4f…479c`), `model_equations.md`,
`src/rebuild/model.py`, `src/eureka/controllers.py`:

| Element | R1 implementation |
|---|---|
| Plant | 1-D longitudinal model, effective mass, rolling + aero, gearbox (constant η_g), motor viscous loss, first-order torque lag τ_T = 20 ms, constant motor/inverter efficiency η_mi, 1-RC battery with constant V_oc, R0 and R1 growing linearly with (1 − SoH), SoC integrator, friction brake for braking beyond the regen limit |
| Battery window | voltage window, discharge and charge current limits; limits SoH-scaled only in class C |
| Design model | x = [e, T, z], linearised at 30 km/h; **contains no battery state**, so SoH does not enter A or B |
| Controllers | F: Bryson LQR; S: thesis weight law with γ_v = γ_u = 1; F01: fixed gain with R × 0.1 |
| SoH | **oracle**, constant within a run (best case for scheduling); no estimator |
| Scenarios | S1, S2 (synthetic), UDDS, US06 (EPA); SoH 1.0/0.9/0.8/0.7; 7 battery cases; 336 + 12 runs |
| Ageing model | **none**; SoH is an input, capacity fade is not computed |

**The thesis's ΔA mechanism was not implementable.** The thesis models battery current as an
inductive state with R_int/L_eq, and L_eq and K_e have no values (`docs/thesis_full_scientific_audit.md`
M-16, C3-28). In a vehicle with an inverter and a current-controlled machine, battery resistance
sits on the DC side and does not appear in the speed or torque dynamics: it changes DC-link
voltage and losses, not the controlled channel (**analytical derivation**, audit M-16). R1 therefore
used the documented model, in which SoH reaches the trajectory only through battery limits.

## 3. Mechanisms that can affect the simulated trajectory and energy

| Mechanism | In R1? | Can it change the trajectory? | Can it change energy? | Evidence |
|---|---|---|---|---|
| Rolling, aero, inertia | yes | via the trajectory only | yes | simulation result (ledger: 59–68 % of energy on complete cycles) |
| Gearbox, motor viscous | yes, constant coefficients | no | via the trajectory | ledger |
| Motor/inverter loss | **constant η_mi = 0.874** | no | proportional to \|P_m\|; operating-point dependence absent | `attainable_improvement_assessment.md` §3 |
| Battery R0 and R1 loss | yes; grows with (1 − SoH) | no | +0.16 % to +1.1 % at SoH 0.7 | simulation result (ledger §4) |
| Motor torque/power envelope | yes (85 N·m, 18 kW) | yes, when it binds | yes | UDDS reference exceeds 18 kW for 0.29 % of the time; US06 exceeds capability in every class |
| Battery voltage window | yes | only if R0 > 3.3–3.8× new | — | never reached in R1 (terminal voltage 42.97–50.41 V) |
| Battery discharge/charge current limits | yes, **assumed values** (3C/1C, 2C/0.5C) | yes | yes (friction braking, shortfall) | simulation result under assumed scenario |
| SoH-proportional current limits | class C only, **assumed BMS law** | yes, the only route by which SoH changes the trajectory | yes | assumed scenario; no source |
| Actuator lag (τ_T) | yes | small | causes current-limit exceedance up to 50.2 A·s | simulation result |
| Capacity fade | **no** | — | — | not modelled |
| Thermal, OCV(SoC), efficiency map, auxiliaries, grade | **no** | — | — | absent |

## 4. Absent features and constant-coefficient approximations

- **Constant motor/inverter efficiency.** It removes any lever for torque-dependent loss
  minimisation. With a real efficiency map, a controller could change losses at equal trajectory
  only by changing the torque profile (single motor: hardly, since torque is fixed by the
  trajectory). This is a model limitation, not a savings opportunity with a known size.
- **Constant OCV, no thermal state, no SoC- or temperature-dependent resistance or limits.**
- **Battery limits as constants.** Their values are assumptions; R1 classes B and C show they
  dominate behaviour when they bind.
- **No capacity-fade model.** The thesis's SEI/Arrhenius model lacks constants (k_c, k_cal) and has
  inconsistent units (R1 report §6).
- **No SoH estimator.** R1 gives the controller the true SoH. A real estimator adds error and lag,
  which can only reduce any scheduling benefit; since R1 found none with the oracle, adding an
  estimator cannot create one (**analytical argument**, with the caveat that an estimator could add
  harm, which R1 did not test).

## 5. Parameter provenance (`parameter_registry.csv`, 39 entries)

| Status | Count | Examples |
|---|---|---|
| Source-verified for this vehicle | **0** | — |
| Physical standard | 2 | air density, gravity |
| Thesis value without primary source (`report_unverified`) | 20 | mass 850 kg, C_d 0.35, T_max 85 N·m, P_max 18 kW, η_mi 0.874, Q = 100 Ah, R0 = 5 mΩ, k_r0 = 0.5 |
| Assumed by the project | 17 | OCV 48 V constant, τ_T, linearisation speed, Bryson weights, γ, voltage window, c_dis, c_ch, SoH scaling |
| Literature-derived | 0 in R1 | (Phase 2 identifies candidates; none characterises the thesis cell) |
| Unknown | the cell itself (16 × "3.2 V/100 Ah CATL", no part number; 16 × 3.2 V ≠ 48 V) | owner item OC-1 |

## 6. What the completed runs establish, and what they do not

**Established (simulation results in the documented model; numerical verification passed):**
1. Across 112 matched pairs (S1, S2, UDDS, US06; SoH 1.0–0.7; 7 battery cases), the thesis's
   SoH weight schedule (γ_v = γ_u = 1) changed energy per km by −0.0019 % to +0.034 % and never
   improved tracking (`analysis_report_20261024.md` §3).
2. A fixed gain selected once (F01) matched or beat S in 28 of 28 cycle × case combinations (Q3).
3. SoH changes the vehicle's behaviour substantially only when the current limits are assumed to
   shrink with SoH (class C), and then it changes F and S alike.
4. The energy gap between the best tested controller and exact tracking of the reference is
   0.11–0.20 % on S1/S2; at least 91 % of friction braking under the assumed charge limits is forced
   by the limit itself (`recovery_feasibility_20261025/attainable_improvement_assessment.md` §5).

**Not established:**
- anything about a real vehicle, a real pack or the thesis's cell;
- capacity fade or battery life (no model);
- behaviour with an estimated SoH, a motor efficiency map, temperature, OCV(SoC), grade;
- behaviour of a controller designed to *use* the battery limits (only the thesis law and fixed
  gains were tested);
- behaviour on NEDC, WLTP, CLTC or the VUC cycle used in the thesis.

## 7. Original claim versus the question R1 actually tested

| | Submitted thesis | R1 |
|---|---|---|
| Comparison | adaptive vs fixed LQR (plus 5 other controllers) | fixed vs SoH-scheduled LQR (plus one retuned fixed gain) |
| Mechanism | ΔA(SoH) in the design model; real-time SoH estimate | SoH reaches only R0, R1, SoC rate and (class C) current limits; oracle SoH |
| Task | thesis cycles; multi-objective (energy, longevity, performance) with NSGA-II | fixed-reference speed tracking; energy and tracking only |
| Energy claim | +12.5 % ± 2.1 % efficiency | −0.0019 % to +0.034 % change, tested plant and scenarios only |
| Fade claim | −15.3 % ± 2.8 % over 1000 cycles | **not tested**: no fade model; R1 does not support or refute it |
| Statistics | "± values", ANOVA | deterministic runs; no p-values or intervals |

**Precise statement of the R1 result.** In a documented, numerically verified longitudinal model
of the thesis's vehicle (thesis parameters, unverified), with oracle SoH, on S1, S2, UDDS and US06,
and with battery limits absent, fixed, or assumed to scale with SoH, the thesis's SoH weight
schedule gave no practical energy or tracking benefit over a fixed-gain LQR. This contradicts the
12.5 % claim *within that model and those scenarios*. It does not test the 15.3 % fade claim.

## 8. Items the recovery work must account for

| Item | Status going in | Where handled |
|---|---|---|
| Constant motor/inverter efficiency | limitation; no efficiency map | `path_decision_matrix.md` P1, P3 |
| Battery current, voltage, power and regen limits | modelled with assumed values | P2 pilot (bracketed scenarios) |
| SoH-proportional current-limit rule | assumed, no source | P2 pilot E4 only, labelled exploratory |
| Tracking failures and motor infeasibility | US06 always; UDDS 0.29 % over 18 kW | excluded US06; UDDS reported with shortfall |
| Actuator lag and current-limit exceedance | up to 50.2 A·s in R1 | reported per run in the pilot |
| Capacity fade vs resistance growth | only resistance growth modelled | fade claim stays unresolved |
| Oracle vs estimated SoH | oracle | stated as best case; estimator not added |
| Unequal tuning budgets | fixed family: 41 R-scales × 4 SoH (164 runs), best at the range edge c = 0.1; scheduled: 15 γ pairs at one SoH (S-B), and γ = 1 untuned in R1 | P2 pilot: 24 Latin-hypercube candidates per branch, same objective and training set |
