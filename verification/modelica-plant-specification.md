# Specification of the independent Modelica plant

- **Status:** written **before** any Modelica was coded (2026-10-23). Pass criteria in section 10 were fixed before any result existed.
- **Scope:** the project's *corrected* longitudinal plant only. The invalid thesis model (Eq. 4.3) is not reproduced. No controller, no EPA cycle, no component beyond what `docs/model.md` already defines.
- **Companion files:** `verification/references/hand_references.json` (analytic values), `verification/references/spec_derivation_checks.txt` (symbolic and dimensional checks).

## 0. Sources and how independence is kept

| Source | Used for |
|---|---|
| `docs/model.md` section 1 | the equations (primary) |
| `configs/parameters.yaml` | parameter values, units, provenance |
| `configs/cycles/profiles.yaml` | S1/S2 segment definitions |
| `src/eureka/plant.py` | read **only to resolve what `docs/model.md` leaves unstated** (section 9). Not imported, not called to produce any Modelica output |

The Modelica code is written from this specification. Parameters enter through a generated file (`verification/scripts/generate_modelica_inputs.py`, which reads the YAML and does not import `eureka`).
Independence is therefore: different language, different solver (variable-step DASSL with event location, against fixed-step RK4), different time stepping of the RC branch, and a separately derived analytic reference. It is **not** independence of authorship: the Python plant, this specification and the Modelica code share a common source document (`docs/model.md`), so a conceptual error in that document would be inherited by both.

## 1. Assumptions inherited from the corrected project model

1. Point-mass longitudinal dynamics on a flat road, still air, rigid drivetrain, no tyre slip.
2. Constant gear efficiency, applied in the direction of power flow.
3. Constant motor+inverter efficiency, applied in the direction of power flow.
4. Constant open-circuit voltage; 1-RC Thevenin battery; R0 and R1 depend on SoH through report Eqs. 4.28-4.29 (unsourced coefficients); SoH is constant within a run.
5. First-order torque actuator with a time constant that the project *assumed* (0.02 s).
6. Torque limit min(T_max, P_max/omega); braking beyond the motor's negative limit goes to a friction brake.
7. The vehicle never reverses; a net negative force at standstill is held by a holding brake.
8. Rolling resistance smoothed with tanh(v / 0.05 m/s), an assumed numerical device.
9. Rotor inertia enters as reflected mass J_m G^2 / r_w^2 with no efficiency factor.

All parameter values are `report_unverified`, `assumed` or `standard` (table in section 3). **Nothing here has been validated against a vehicle.**

## 2. State, input, outputs (units)

| Symbol | Meaning | Unit | Initial value |
|---|---|---|---|
| v | vehicle speed | m/s | 0 |
| T | delivered motor torque | N m | 0 |
| V1 | RC-branch voltage | V | 0 |
| SoC | state of charge (bookkeeping only; affects no other equation) | 1 | 0.8 |
| E_chem, E_rr, E_aero, E_fb, E_gear, E_visc, E_mi, E_R0, E_R1, E_regen | energy accumulators | J | 0 |
| dist | distance | m | 0 |
| Ah | absolute charge throughput | A h | 0 |

**Input:** T_ref, torque request, N m (no controller: it is a prescribed time function).
State vector size: 16 (4 physical + 10 energy + dist + Ah).

## 3. Parameters

Values are read from `configs/parameters.yaml` and not retyped. SoH is the only parameter not in the YAML (it is a run property; 1.0 unless stated).

| Symbol | Value | Unit | Provenance | YAML key |
|---|---|---|---|---|
| M | 850.0 | kg | report_unverified | `vehicle.mass` |
| A_f | 2.2 | m^2 | report_unverified | `vehicle.frontal_area` |
| C_d | 0.35 | 1 | report_unverified | `vehicle.drag_coefficient` |
| C_rr | 0.008 | 1 | report_unverified | `vehicle.rolling_resistance` |
| r_w | 0.28 | m | report_unverified | `vehicle.wheel_radius` |
| rho | 1.225 | kg/m^3 | standard | `vehicle.air_density` |
| g | 9.81 | m/s^2 | standard | `vehicle.gravity` |
| G | 6.5 | 1 | report_unverified | `drivetrain.gear_ratio` |
| eta_g | 0.9702 | 1 | report_unverified | `drivetrain.gear_efficiency` |
| J_m | 0.05 | kg m^2 | report_unverified | `drivetrain.motor_inertia` |
| B_m | 0.001 | N m s | report_unverified | `drivetrain.motor_viscous_friction` |
| eta_mi | 0.874 | 1 | report_unverified | `drivetrain.motor_inverter_efficiency` |
| T_max | 85.0 | N m | report_unverified | `drivetrain.torque_max` |
| P_max | 18000.0 | W | report_unverified | `drivetrain.power_max` |
| tau_T | 0.02 | s | assumed | `drivetrain.torque_time_constant` |
| V_oc | 48.0 | V | assumed | `battery.open_circuit_voltage` |
| Q_Ah | 100.0 | A h | report_unverified | `battery.capacity` |
| R0_new | 0.005 | ohm | report_unverified | `battery.r0_new` |
| R1_new | 0.003 | ohm | report_unverified | `battery.r1_new` |
| C1 | 50000.0 | F | report_unverified | `battery.c1` |
| k_r0 | 0.5 | 1 | report_unverified | `battery.k_r0` |
| k_r1 | 0.3 | 1 | report_unverified | `battery.k_r1` |
| v_eps | 0.05 | m/s | assumed | `simulation.speed_smoothing` |

Not used by the plant: `drivetrain.speed_max` (837 rad/s; only a validity check in the project).
Derived: M_eff = M + J_m G^2/r_w^2 = 876.945 kg; gr = G/r_w = 23.2143 rad/m; R0 = R0_new (1 + k_r0 (1 - SoH)); R1 = R1_new (1 + k_r1 (1 - SoH)).

## 4. Equations

Let v+ = max(v, 0) (the speed that enters every force and power term). Then:

1. omega = gr v+  [rad/s]
2. T_lim = min(T_max, P_max / max(omega, eps_w)),  eps_w = 1e-6 rad/s
3. T_cmd = min(max(T_ref, -T_lim), T_lim)
4. t_s = T - B_m omega  [N m, shaft torque into the gearbox]
5. F_w = gr eta_g t_s if t_s >= 0 (motoring);  F_w = gr t_s / eta_g if t_s < 0 (regeneration)  [N, positive = forward]
6. s = tanh(v+ / v_eps)
7. F_rr = C_rr M g s
8. F_aero = 1/2 rho C_d A_f v+ |v+|   [N]
9. F_fb = gr max(0, -T_lim - T_ref) s
10. F_net = F_w - F_rr - F_aero - F_fb
11. dv/dt = 0 if (v <= 0 and F_net < 0), else F_net / M_eff   [holding brake; no reversing]
12. dT/dt = (T_cmd - T) / tau_T
13. P_m = T omega;  P_e = P_m/eta_mi if P_m >= 0, else P_m eta_mi   [W]
14. battery: Vo = V_oc - V1;  I = (Vo - sqrt(Vo^2 - 4 R0 P_e)) / (2 R0)  [A, positive = discharge]
15. dV1/dt = -V1/(R1 C1) + I/C1
16. dSoC/dt = -I / (3600 Q_Ah SoH)
17. accumulators: dE_chem = V_oc I;  dE_rr = F_rr v+;  dE_aero = F_aero v+;  dE_fb = F_fb v+;  dE_gear = t_s omega - F_w v+;  dE_visc = B_m omega^2;  dE_mi = P_e - P_m;  dE_R0 = R0 I^2;  dE_R1 = V1^2/R1;  d dist = v+;  dAh = |I|/3600;  dE_regen = min(P_e, 0).

Sign conventions: forward speed and traction force positive; battery current positive on discharge; regeneration has t_s < 0, P_m < 0, I < 0.
Battery root: the minus sign selects the branch that tends to P_e/Vo as R0 tends to 0. A real root needs P_e <= Vo^2/(4 R0) (about 115 kW at SoH 1), checked by an assertion.

Dimensional check: all terms above, including the algebraic forms of the derivations, were checked with Pint using the units in the YAML (28 of 28 correct, 4 of 4 deliberately wrong forms rejected; `verification/references/spec_derivation_checks.txt`). In particular F_w contains torque/radius and never motor speed in place of a force.

## 5. Zero-speed behaviour

At v = 0: omega = 0, T_lim = T_max, F_aero = 0 and, because tanh(0) = 0, F_rr = 0 and F_fb = 0. If F_net >= 0 the vehicle accelerates; if F_net < 0 it stays at rest (equation 11). Speed is not allowed to become negative; any excursion below zero within solver tolerance is removed by the event that switches equation 11.
A brief note on a Modelica-specific point: the conditional derivative in equation 11 must not chatter at standstill. If it does, that is a finding, not something to hide.

## 6. Energy accounting

Supplied chemical energy E_chem = integral of V_oc I dt  [J]; reported energy per distance = (E_chem / 3600) / (dist / 1000)  [Wh/km] over the whole run, with dist = integral of v+ dt.
Closure identity (must hold for every run): E_chem = 1/2 M_eff (v^2 - v(0)^2) + 1/2 C1 (V1^2 - V1(0)^2) + E_rr + E_aero + E_fb + E_gear + E_visc + E_mi + E_R0 + E_R1.
It is a conservation identity of the model, not a test of the physical laws: it would hold with wrong coefficients.

## 7. Derived analytic references (all verified symbolically or by dimension before use)

- **Equilibrium torque** (dv/dt = 0, motoring branch, v well above 0.5 m/s): T_eq = (F_rr + F_aero) / (gr eta_g) + B_m gr v. Values: 3.737108 N m (20 km/h), 4.609469 (30 km/h), 7.323644 (50 km/h).
- **Instantaneous acceleration** at a given (v, T): a = F_net / M_eff from equations 4-10. Four points are tabulated in `hand_references.json` (two motoring, two regenerating).
- **Coast-down** (T_ref = 0 and T = 0, so t_s = -B_m omega < 0 and the regeneration branch applies): M_eff dv/dt = -(F0 + c v + k v^2) with F0 = C_rr M g, c = B_m G^2 / (eta_g r_w^2) = 0.555456 N s/m, k = 1/2 rho C_d A_f. For 4 alpha gamma > beta^2 (alpha, beta, gamma = F0, c, k divided by M_eff) the solution is v(t) = (s tan(atan((2 gamma v0 + beta)/s) - s t/2) - beta)/(2 gamma), s = sqrt(4 alpha gamma - beta^2). SymPy confirms the residual is exactly 0. For v0 = 13 m/s, v(20 s) = 9.928390 m/s. It needs tanh = 1, i.e. v above about 1 m/s.
- **Road-load energy over a piecewise-linear profile** (exact): aero integral of k v^3 dt = k (v1^4 - v0^4)/(4a) per ramp and k v^3 T per hold. Rolling: C_rr M g (distance - correction), where the tanh smoothing removes C_rr M g eps^2 pi^2/(24 |a|) at each departure from, and arrival at, rest (uses integral from 0 to infinity of x (1 - tanh x) dx = pi^2/24). S1: distance 2161.04727 m, duration 324.9107 s, E_aero 120256.697 J, E_rr 144158.504 J. S2: 531.67806 m, 213.2778 s, 6118.556 J, 35465.906 J.
- **Ideal tracking** (no analytic closed form): v(t) = piecewise-linear reference; required F_w = M_eff a + F_rr + F_aero (no friction brake, so the speed trace is followed exactly); then t_s from the inverse of equation 5, T = t_s + B_m omega, and equations 13-15 and 17. The delivered torque equals the required torque (the actuator lag is not modelled in this reference, as in the reference being checked). The value 49.714 Wh/km on S1 (SoH 1) comes from `audit/technical-verification/ind_checks_b.py`, which computes it by a fixed-step 1 ms midpoint scheme with an exact exponential update of V1 for piecewise-constant current. **It is a saved numerical result, quoted only in `technical-foundation-audit.md`, not a closed-form value and not stored as a data file.**

## 8. Implementation choices that are new (not inherited)

| Choice | Reason / consequence |
|---|---|
| OpenModelica 1.27.1, DASSL, tolerance 1e-10 (1e-12 for convergence checks) | variable-step error control with event location |
| Holding brake as a conditional derivative (equation 11), not a post-step clamp | the Python plant clamps v after each RK4 step; a small difference only at standstill |
| Piecewise-linear profile as a segment index advanced by `when time >= t_knot` | forces the solver to hit every knot |
| `min`, `max`, `if` with state-dependent conditions produce events | their locations are found, not stepped over |
| Output grid 0.01 s for the forward model | same sampling instants as the Python record |
| Battery discriminant check by `assert` instead of a recorded flag | a violation would stop the run |
| Profile knots built inside Modelica from the segment list | avoids reusing the Python profile builder |

## 9. What `docs/model.md` leaves unstated (resolved from `plant.py`; flagged as such)

- eps_w = 1e-6 rad/s in equation 2 (the document says only "epsilon").
- Equations 1-10 use the clamped speed v+, and the energy accumulators and distance integrate v+.
- The holding-brake condition is "v <= 0 and dv/dt < 0".
- The initial SoC value 0.8 and the zero initial T, V1.
- No inconsistency between the two was found in the plant equations.

## 10. Verification cases, expected behaviour and pass criteria (fixed before any run)

| ID | Case | Expected | Pass criterion |
|---|---|---|---|
| A1 | units and structure | the model compiles with unit checking, all declared units consistent | no unit warning on the authoritative model; a deliberately wrong-unit fixture is flagged |
| B1 | equilibrium at 20, 30, 50 km/h: start at (v_eq, T_eq) with T_ref = T_eq | dv/dt = 0, dT/dt = 0, F_net = 0, v constant | \|dv/dt\| <= 1e-9 m/s^2; \|F_net\| <= 1e-6 N; \|v(1 s) - v_eq\| <= 1e-9 m/s |
| B2 | instantaneous points of section 7 (algebraic values at t = 0) | match `hand_references.json` | relative error <= 1e-9 for F_w, F_rr, F_aero, F_net, a, P_m, P_e, I |
| B3 | actuator limit | T_lim = 59.645 N m at 13 m/s; dT/dt = 2982.25 N m/s for T_ref = 1000, T = 0 | relative error <= 1e-9 |
| C1 | toy coast-down from the earlier smoke test | v(20) = 10 exp(-25*20/850) | reproduce the earlier maximum error (3.6e-9 m/s) within 20 % and below 1e-7 m/s |
| C2 | project coast-down, v0 = 13 m/s, 20 s, tolerance 1e-10, 2001 output points | closed form of section 7 | max abs error <= 1e-7 m/s (observed global error for the toy was about 36 times the tolerance; margin about 30) |
| C3 | convergence | error falls as tolerance tightens (1e-6, 1e-8, 1e-10, 1e-12) | monotone non-increasing, down to the output-roundoff floor |
| D1 | S1, SoH 1.0: distance, E_aero, E_rr against the exact analytic values | analytic | relative error <= 1e-7 |
| D2 | closure of the inverse model | residual of the identity of section 6 | \|residual\| / throughput <= 1e-7 |
| D3 | ideal-tracking energy: S1 SoH 1.0 / 0.8, S2 SoH 1.0 / 0.8 against the saved reference (49.714073, 49.803003, 36.951337, 36.990473 Wh/km) | agreement up to the discretisation error of the reference | relative gap <= 3e-4 (worst-case bound: about 14 slope changes per profile, each misassigning at most h/2 of a power jump of about 16 kW, h = 1 ms, against about 387 kJ; typical 3e-5), **and** the gap must shrink when the reference scheme is rerun with a 10x finer step |
| E | negative controls | each perturbed fixture fails its check | every control exceeds its tolerance by at least a factor 10 |
| F1 | forward plant against the Python plant, the same deterministic torque schedule (section 11) | states, forces, power, energy | see below |

Phase 6 tolerances (compare Modelica, DASSL tolerance 1e-10, with the Python plant at h = 1e-4 s, then report the Python h = 1e-3 s deviation separately):

| Quantity | Absolute tolerance |
|---|---|
| v | 1e-5 m/s |
| T | 1e-4 N m |
| V1 | 1e-6 V |
| SoC | 1e-8 |
| dist | 1e-4 m |
| energy accumulators | relative 1e-6 of the final value (floor 1e-3 J) |
| F_w, F_rr, F_aero, F_fb, F_net | 5e-3 N |
| acceleration | 1e-5 m/s^2 |
| P_m, P_e | 0.1 W |
| I | 5e-3 A |

Algebraic quantities (forces, acceleration, power, current) are not compared at the exact instants where the torque request switches (t = 10, 20, 30, 38, 46, 56 s), because the left and right limits there are different values and the CSV does not state which one a sample is. States and accumulators are continuous and are compared at every sample.
If the primary criterion fails, the result is reported as a failure and investigated; the tolerance is not widened after the fact.

## 11. Deterministic trajectory for the cross-implementation comparison

Open loop, SoH 0.8, initial state (v, T, V1, SoC) = (0, 0, 0, 0.8), T_ref piecewise constant, switching at integer seconds (so a 1 ms fixed step sees every switch exactly):

| Interval (s) | T_ref (N m) | Exercises |
|---|---|---|
| 0-10 | 85 | start from rest (tanh), torque limit, then the power-limit corner (omega above 211.8 rad/s) |
| 10-20 | 20 | motoring below the limit |
| 20-30 | 0 | coasting, torque decay, sign change of P_m |
| 30-38 | -40 | regeneration, friction brake beginning where T_lim falls below 40 |
| 38-46 | -200 | strong friction braking, arrival at rest, holding brake |
| 46-56 | -20 | held at rest |
| 56-66 | 10 | departure from rest |

Length 66 s. The Python side uses the same schedule via `rk4_step`; neither side feeds the other.

## 12. Known gaps

1. The ideal-tracking reference exists only as a number in the audit report and as the algorithm in a preserved script. There is no saved data file behind it.
2. The torque time constant (0.02 s), the V_oc, the tanh smoothing width and the SoH coefficients are assumptions, so every check here is conditional on them.
3. eps_w, the holding-brake rule and the initial state are not in `docs/model.md` (section 9).
4. Nothing links these equations to a physical vehicle.

## 13. Post-run notes (added after the results existed; the text above is unchanged)

1. **Hand reference error, corrected.** The first version of `hand_references.py` left out the friction-brake force (equation 9) at the instantaneous points. At v = 20 m/s, T = -40 N m the motor limit is only 38.77 N m, so the request is beyond it and the brake is active (28.57 N). The Modelica run disagreed by 2.3 % in net force, which equals F_fb / |F_net| to four digits. The error was in the hand reference, not the model. It was corrected; the first-run failing output is kept as `modelica-build/check_results_FIRST_RUN_with_B2_failure.csv`. No tolerance was changed.
2. **Implementation changed once, no equation changed.** Version 0.1.0 advanced the segment and interval indices with `when pre(k) < n and time >= t[...]`. At DASSL tolerance 1e-12 that run ended in NaN right after the switch at t = 30 s (the switches at 10 s and 20 s were passed). Version 0.1.1 computes the index statelessly as `1 + sum(if time >= t[i] then 1 else 0 ...)`. The `omc` event log still labels these switches "state event" (the reason was not investigated), and the 1e-12 failure remained at the same instant (section 3 of the report); the version-0.1.0 outputs are kept in `modelica-build/cases_v0.1.0_when_pre`. All results quoted are version 0.1.1.
3. **A prediction in section 11 was wrong.** The 30-38 s interval does not reach the friction brake: T_lim stays at or above 46.6 N m, above the 40 N m request. Friction braking is exercised in the -200 N m interval (124 output rows with F_fb > 0), and at the single instantaneous point B2 (v = 20 m/s, T_ref = -40).
4. **D3 wording.** The code first tested that the gap shrank at every step of the reference's convergence series; the pre-registered text asks only that it shrink with a 10x finer step (h = 1e-4 against 1e-3). The code was aligned to the text before the Modelica comparison was run, after the (non-monotone) reference series had been seen.
5. **The tolerances were conservative.** Observed Modelica-to-Python differences are 16 to 10^5 times smaller than the tolerances in section 10 (smallest margin: net force at the instant the vehicle stops). They were not tightened afterwards.
6. **omc unit-check limits.** Equations containing the bare literal 3600 are accepted by omc whatever their units (a literal acts as any unit); the A h to A s factor is verified only by the Pint check. omc does flag a missing factor when no literal is present (probe fixture `WrongUnitChargeIntegral`).
