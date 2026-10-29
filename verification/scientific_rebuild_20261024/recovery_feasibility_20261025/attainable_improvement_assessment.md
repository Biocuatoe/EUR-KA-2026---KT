# Attainable energy improvement: assessment (Phase 1)

**Date:** 2026-10-25. **Status:** analysis of existing R1 outputs plus three small, deterministic,
parameter-free computations on the same plant equations. No controller was run, no protocol was
frozen, no R1 file was changed.

**Independence.** Prepared by the same AI assistant that built and analysed R1. No person has
checked it.

**Labels.** `MEAS` = integrated inside the R1 simulation (accumulator in the saved final state).
`DERIV` = exact algebra on saved quantities. `IDEAL` = new computation from the plant equations on
the reference trajectory alone (not an R1 output). `APPROX` = approximate. `NONE` = not modeled,
no number can be given. All plant parameters are the thesis's `report_unverified` values
(`parameter_registry.csv`); every number below is conditional on them.

---

## 1. Bottom line

1. **The controller can only change energy through the speed trajectory it realises, and through
   how braking is split between regeneration and friction when a limit binds.** It cannot change
   any loss coefficient (§4.1). This follows from the plant equations, not from the data.
2. **Measured controller influence is small.** Across F, S and F01 the largest spread in net
   energy is 0.28 % (a 19.7 Wh cycle, assumed-limit class C); in the unconstrained plant it is
   0.05–0.10 % (§4.2).
3. **Gap between the best tested controller and exact tracking** of the reference (class A,
   complete cycles): **0.11–0.20 %** of energy per km (§5.1). Exact tracking is infeasible on
   UDDS (the reference needs 20.96 kW against an 18 kW motor limit for 0.29 % of the time).
4. **Under the assumed charge limits, 91–98 % of the friction braking seen on S1 and UDDS is
   forced by the limit even with perfect tracking.** The excess a controller could in principle
   avoid is 0.23–0.56 % of net energy (§5.2). Those limits are unsourced assumptions.
5. **A general, defensible upper bound on attainable improvement cannot yet be calculated.**
   It requires the optimum over trajectories inside a tracking tolerance, and the tolerance is
   the quantity that decides the answer (§6). What can be said: for *exact same-cycle tracking*
   the headroom is of the order of 0.1–0.8 % (indicative, assumption-dependent), below the 1 %
   practical-difference margin pre-registered in R1.
6. **The resistance-loss fraction is not a bound on controller savings** and is not used as one
   (§4.3). R0 loss is 1.1–3.0 % of energy at SoH 1.0 on the complete cycles; at a fixed
   trajectory the controller cannot alter it at all.
7. **The speed reference has roughly 20–50 times more leverage than the controller gap above:** exact
   tracking of a 5 % slower reference (same distance) lowers energy per km by 4.1–5.4 % and a
   10 % slower one by 7.7–10.1 % (§5.4). This is a different task that trades trip time for
   energy, not a controller improvement.

---

## 2. What was run

| Item | Command / source | Result |
|---|---|---|
| Ledger from saved final states | `energy_ledger.py` (activated env), reads `../runs/R1_*/{metrics.csv,series.npz}` | exit 0; 336 rows; max \|closure\| = 2.2e-7 Wh |
| Reference wheel demand, exact-tracking energy, friction floor, stretched references | same script, plant equations only | exit 0 |
| Tables | `summarise_ledger.py` -> `ledger_tables.md` | exit 0 |
| Stress indicators | `stress_spread.py` -> `stress_spread.csv` | exit 0 |
| Citation checks | Crossref and DataCite metadata queries (see `extension_options.md`) | no dataset downloaded |

**Checks on the new computations.**
- *Closure of the ledger:* wheel work computed two independent ways (ΔKE + rolling + aero +
  friction, versus battery energy minus all other terms) agrees to 2.2e-7 Wh in all 336 runs.
- *Closure of the exact-tracking energy:* 3e-5 Wh on S1, i.e. about 3e-5 % of 107 Wh.
- *Time-step sensitivity of exact-tracking energy* (S1, SoH 1.0): 49.7134, 49.7141, 49.7142 Wh/km
  at 10, 5, 2.5 ms. The method's error (about 0.001 Wh/km) is 100 times smaller than the gaps
  reported in §5.1.
- *Predicted versus actual accounting:* the wheel energy of the reference alone (no controller)
  against the simulated wheel energy of controller F, class A, SoH 1.0:

  | Cycle | Reference-only [Wh] | Simulated, F [Wh] | Difference |
  |---|---|---|---|
  | S1 | 73.449 | 73.534 | +0.12 % |
  | S2 | 11.551 | 11.577 | +0.22 % |
  | UDDS | 566.543 | 567.240 | +0.12 % |

  The two routes share no code path. The residual is the effect of tracking error and torque
  lag, which is the quantity the controller can influence.
- *Not independently verified:* the battery window itself (R1 has no second implementation); the
  new computations use the same parameters and the same author.

**Discrepancy noted, not corrected.** `analysis_report_20261024.md` §4 gives the generic
voltage-window threshold (R0 > 19.1 mΩ, k_r0 > 9.4 at SoH 0.7). `results/precheck_cycles.csv`
gives cycle-specific values (UDDS 16.4 mΩ, k_r0 7.6; US06 5.8 mΩ, k_r0 0.56). The conclusion
(the window never binds in the tested range) is unchanged because the motor limit binds first;
US06 is outside vehicle capability regardless.

---

## 3. Energy ledger and status of each component

Net battery chemical energy (V_oc·I) satisfies the exact identity

    E = ΔKE_eff + E_rr + E_aero + E_fb + E_gear + E_visc + E_mi + E_R0 + E_R1 + ΔE_C1

Shares for controller F, unconstrained plant (B0), SoH 1.0, per
`ledger_tables.md` §1:

| Component | Status | S1 | S2 | UDDS | US06* | Controller can influence? |
|---|---|---|---|---|---|---|
| Rolling resistance E_rr | MEAS | 37.2 % | 50.1 % | 26.4 % | 11.6 % | Only via trajectory (§4.1) |
| Aerodynamic drag E_aero | MEAS | 31.1 % | 8.7 % | 41.0 % | 60.0 % | Only via trajectory |
| Friction brake E_fb | MEAS | 0 | 0 | 0 | 1.2 % | Yes where a limit binds (§5.2) |
| Gearbox loss E_gear (constant η_g = 0.9702) | MEAS | 4.7 % | 6.8 % | 4.6 % | 3.1 % | Only via trajectory |
| Motor viscous E_visc | MEAS | 3.1 % | 1.9 % | 2.9 % | 2.5 % | Only via trajectory |
| Motor + inverter E_mi (constant η_mi = 0.874) | MEAS, but model is APPROX | 22.0 % | 31.4 % | 21.7 % | 15.0 % | See below |
| Battery ohmic E_R0 | MEAS | 1.75 % | 1.08 % | 3.01 % | 5.12 % | Only via trajectory |
| Battery polarisation dissipation E_R1 | MEAS | 0.09 % | 0.02 % | 0.36 % | 1.36 % | Only via trajectory |
| Polarisation storage ΔE_C1 + ΔKE | DERIV | 0.02 % | 0.01 % | 0.00 % | 0.09 % | No |
| Wheel net work E_wheel | DERIV (exact) | 68.3 % | 58.7 % | 67.3 % | 72.9 %† | Only via trajectory |
| Regenerated energy at terminals | MEAS | 38.5 Wh | 13.8 Wh | 297.8 Wh | 236.8 Wh | Only via trajectory / blending |
| Positive and negative wheel work (split) | IDEAL for the reference; **not stored** for simulated runs (series are 1 Hz) | 119.1 / −45.6 Wh | 27.9 / −16.3 Wh | 917.8 / −351.3 Wh | 1868 / −330 Wh | n/a |
| Tracking error | MEAS (RMSE, max) | 0.050 m/s | 0.054 m/s | 0.072 m/s | 1.39 m/s | It is the controller output |

\* US06 exceeds vehicle capability (shortfall 3.2 % even unconstrained); shown for completeness
only. † from the same identity, includes friction.

**Why the motor/inverter row is not a savings opportunity.** E_mi is proportional to |mechanical
power| by construction (constant efficiency). A real machine loses energy as copper loss ∝ T²,
iron loss depending on speed and flux, and inverter loss depending on current and switching, with
efficiency varying strongly across the torque-speed plane. The plant has no efficiency map, so
**how much of the 15–31 % motor/inverter share a controller or torque-allocation scheme could
change is unavailable (NONE)**. The model cannot support any numerical statement about it.

**Recovery chain.** Terminal regeneration divided by reference braking work at the wheel is
0.843 (S1) and 0.848 (UDDS). That is close to the product η_g·η_mi = 0.848. The
recovery ratio is set by two constants of the model, not by the controller.

**Missing physical loss mechanisms that block a credible calculation of absolute savings**
(none is modeled; none receives a number here):
- motor efficiency map, flux weakening, inverter switching losses;
- battery thermal behaviour and temperature dependence of R0 and of the charge limit;
- SoC- and temperature-dependent OCV and resistance, hysteresis, pack-level interconnect losses;
- auxiliary and thermal-management loads, DC/DC, BMS consumption;
- friction-brake blending logic, tyre slip, wheel and driveline inertia other than the motor rotor,
  road grade and wind;
- real BMS current and power limits (here assumed, §5.2).

---

## 4. What the controller can physically influence

### 4.1 Derivation

With no friction braking the longitudinal balance is

    F_w = M_eff·a + F_rr(v) + F_aero(v)

so for a given speed trajectory v(t) the wheel force is fixed. The shaft torque follows from the
gear efficiency and viscous friction, the electrical power p_e from the constant motor/inverter
efficiency, the current from p_e = (V_oc − V1 − R0·I)·I, and V1 from its linear ODE. Hence **every
ledger line is a functional of v(·) alone** (V1 carries memory but is itself driven by v(·)). The
loss coefficients (η_g, η_mi, R0, R1, C_rr, C_d·A_f) belong to the plant.

The controller therefore acts on energy through:
1. the realised trajectory v(·), i.e. its deviation from the reference (tracking error, lag);
2. the regeneration/friction split, only when a torque or battery limit binds (F_fb > 0).

It does **not** act through: R0 or R1, the efficiencies, the OCV, or the capacity. A scheduling
law that reads SoH can change the controller's response, but the trajectory it produces is what
matters (§5.1), and R1 showed that trajectory barely moves.

### 4.2 Measured controller influence (R1 outputs)

`ledger_controller_spread.csv`, maximum over all 112 cycle × case × SoH groups of
(max − min) over F, S and F01:

| Ledger line | Max spread [Wh] | Max spread [% of E(F)] | Where |
|---|---|---|---|
| Net energy E | 0.061 | 0.283 | S2 / BCS2 / SoH 0.7 |
| Friction brake E_fb | 0.060 | 0.278 | same |
| Regenerated energy | 0.054 | 0.251 | same |
| Motor + inverter E_mi | 0.371 | 0.044 | UDDS / B0 / SoH 0.7 |
| Ohmic E_R0 | 0.229 | 0.027 | UDDS / BV-k2 / SoH 0.7 |
| Rolling + aero | ≤ 0.117 | ≤ 0.031 | |
| Tracking RMSE | 0.020 m/s | | US06 / B0 / SoH 0.7 |
| Ah throughput | | 0.233 | UDDS / BCS2 / SoH 0.7 |
| RMS current | | 0.475 | S2 / BV-k2 / SoH 0.7 |
| Peak current | | 0.044 | UDDS / BCS2 / SoH 0.7 |

In the unconstrained plant on complete cycles the total spread is 0.037–0.099 %
(`ledger_tables.md` §3). These are the three controllers actually tested, not a bound on what a
better one could do.

### 4.3 The resistive fraction is not a bound

R0 loss is 1.1–3.0 % of energy (complete cycles, SoH 1.0) and rises by 0.16–0.27 % of energy at
SoH 0.7 with the thesis's k_r0 = 0.5 (1.1 % and 0.64 % at k_r0 = 2.0; `ledger_tables.md` §4).
Neither number bounds the saving from any controller: by §4.1 the I²R loss at a fixed trajectory is
fixed, so a controller that tracks equally well saves exactly zero of it; one that tracks differently
changes it through the trajectory, which is the term already measured in §5.1. No bound of the form
"controller savings ≤ resistive share" has been established, and none is claimed.

---

## 5. Quantities that can be calculated

### 5.1 Gap to exact tracking (IDEAL; class A; complete, in-capability cycles)

Energy per km if the reference is tracked exactly (inverse-dynamics torque, torque lag
compensated), against the saved R1 runs (`ledger_tables.md` §3):

| Cycle | SoH | Exact tracking [Wh/km] | F | S | F01 | F − exact | F01 − exact |
|---|---|---|---|---|---|---|---|
| S1 | 1.0 | 49.713 | 49.811 | 49.811 | 49.787 | +0.098 (+0.20 %) | +0.074 (+0.15 %) |
| S1 | 0.7 | 49.847 | 49.948 | 49.951 | 49.922 | +0.101 (+0.20 %) | +0.075 (+0.15 %) |
| S2 | 1.0 | 36.948 | 37.004 | 37.004 | 36.990 | +0.056 (+0.15 %) | +0.042 (+0.11 %) |
| S2 | 0.7 | 37.007 | 37.065 | 37.066 | 37.050 | +0.058 (+0.16 %) | +0.043 (+0.12 %) |
| UDDS | any | undefined: the reference needs 20.96 kW, 0.29 % of the time above the 18 kW limit | | | | | |

**Meaning.** For the problem "follow this reference exactly", the most any controller could add to
the three tested is the remaining gap: at most about 0.15–0.20 %. F01 already closes about a
quarter of it on S1. **This is not a lower bound on energy over all admissible trajectories**
because a trajectory that deviates from the reference can use less energy (§5.4). It is the limit
for *zero* tracking tolerance.

### 5.2 Friction braking forced by the charge limit (IDEAL; depends on assumed limits)

At exact tracking, the friction energy that the assumed charge-current limit and the motor torque
limit cannot absorb (V1 set to 0; lag ignored), against controller F in R1
(`ledger_tables.md` §5):

| Cycle | Case | SoH | Forced floor [Wh] | Measured F [Wh] | Excess [Wh] | Excess as % of net E |
|---|---|---|---|---|---|---|
| S1 | BCS | 0.7 | 5.58 | 6.01 | 0.43 | 0.38 |
| S1 | BCS2 | 0.7 | 19.57 | 20.05 | 0.48 | 0.39 |
| UDDS | BCN | 1.0 | 70.07 | 73.50 | 3.44 | 0.38 |
| UDDS | BCS | 0.7 | 121.36 | 125.33 | 3.97 | 0.44 |
| UDDS | BCS2 | 0.7 | 211.02 | 215.95 | 4.93 | 0.56 |
| S2 | BCS2 | 0.7 | 1.82 | 2.07 | 0.25 | 1.17 (of a 19.7 Wh cycle) |

The forced share is 91–98 % of the measured friction braking on S1 and UDDS, and 61–88 % on S2
(where the amounts are below 2.1 Wh). On US06 the
floor exceeds the measurement because the vehicle does not complete the cycle, so that row is not
interpretable and is excluded.

**Meaning.** If the charge-current limit were as assumed, a battery-aware controller could avoid
at most the excess, about 0.2–0.6 % of net energy (up to 1.2 % only on the smallest cycle in the
harshest assumed case). The *forced* part is a property of the battery limit and the reference,
not of the controller. **The limit values (3 C / 1 C or 2 C / 0.5 C, scaled with SoH or not) are
assumptions with no datasheet; if the real charge limit is higher, the floor falls toward zero, and
if lower it rises, and the controller-avoidable excess changes with it.**

### 5.3 Battery stress indicators

Ah throughput, RMS current and peak current differ between controllers by at most 0.23 %, 0.48 %
and 0.044 % (§4.2; `stress_spread.csv`). For any fade law that is sublinear in Ah throughput
(Q_loss ∝ Ah^z with z ≤ 1) the relative difference in fade between these controllers is therefore at
most about 0.23 %, and the dependence on peak current would have to be extreme to matter. This is a
statement about the three tested controllers, **not a fade estimate**: no fade model is used and
none is justified yet (`extension_options.md` option C).

### 5.4 Leverage of the speed reference (IDEAL; different task)

Exact tracking of the reference slowed uniformly (v' = v(t/s)/s, same distance, duration × s),
k_r0 = 0.5 (`ledger_tables.md` §6):

| Cycle | Slower by | Duration [s] | Energy per km change vs exact tracking of the original |
|---|---|---|---|
| S1 | 2 % / 5 % / 10 % | 331 / 341 / 357 | −2.3 % / −5.4 % / −10.1 % |
| S2 | 2 % / 5 % / 10 % | 218 / 224 / 235 | −1.7 % / −4.1 % / −7.7 % |
| UDDS | 10 % | 1506 | 61.16 Wh/km, 12.9 % below simulated F (70.24); the unstretched reference is infeasible |

This is arithmetic on the aerodynamic and inertial terms, not an optimised eco-driving profile.
It is shown only to size the effect: a roughly 10 % slower UDDS gives a saving of the same
magnitude as the unverified 12.5 % claim. That coincidence of magnitude does not explain the
thesis figure, but it shows how easily a tracking-tolerance or speed-reference change can be
mistaken for a controller improvement, and why the tracking and completion guards in Phase 3 are
needed. It also bounds the other way: savings of this kind are paid for in trip time.

---

## 6. Is a defensible attainable-improvement bound available?

| Question | Answer |
|---|---|
| Zero tracking tolerance, same cycle, classes A/B (no binding limit) | **Yes, per cycle:** E_exact. Headroom of the tested controllers 0.11–0.20 % (S1, S2). Undefined on UDDS and US06. Conditional on the thesis's unverified plant parameters. |
| Zero tolerance, with the assumed charge limits | Additional avoidable friction 0.2–0.6 % of E (§5.2), conditional on unsourced limits. The two numbers are not additive without a joint calculation; their rough sum, **≲ 0.8 %**, is indicative only. |
| Non-zero tolerance (eco-driving within a tracking specification) | **No bound yet.** Needs the minimum of E over trajectories with |v − v_ref| inside the tolerance and the distance fixed. The thesis quotes a 0.6 m/s RMSE specification (parameter registry, `controller.bryson_velocity_error_max` note), 10 times the tracking error actually achieved, and the speed reference is so influential (§5.4) that the result would be dominated by how much lag the tolerance is allowed to buy. That is exactly the "lower energy from degraded tracking" outcome the study must not report as an improvement. A bound is only meaningful together with a stated trip-time and distance requirement. |
| Resistive-loss fraction as a bound | **Not a bound.** See §4.3. |
| Motor/inverter or thermal savings | **Unavailable.** No efficiency map or thermal model (§3). |
| Capacity fade | **Unavailable.** No justified fade model; §5.3 gives only a conditional statement about stress indicators. |

The calculation that would settle the third row is a model-only trajectory optimisation
(minimise E over v(·) with tolerance and distance constraints, using a relaxation that drops R0 and
R1 to give a valid lower bound). It uses no parameter beyond those already in the model, but it
answers a different question from the one posed in R1 and is specified, not run, in
`recommended_model_spec.md`.

---

## 7. Limits of this assessment

- All vehicle and battery parameters are the thesis's unverified values; the cell is unidentified
  and the 100 Ah capacity and the proportionality of current limits to SoH are not established
  facts (owner item OC-1).
- Exact-tracking energy uses a 10 ms midpoint scheme with explicit V1; sensitivity checked (§2).
  It ignores the actuator lag by construction.
- The friction floor ignores lag and V1 and applies only where the cycle is completed.
- One vehicle, flat road, no thermal state, constant OCV, SoH known exactly.
- The three controllers compared are those of R1; S used γ = 1 without tuning while F01 was tuned
  once on S1, an asymmetry R1 itself reports.

## 8. Files

`energy_ledger.py`, `summarise_ledger.py`, `stress_spread.py`; `ledger_runs.csv`,
`ledger_controller_spread.csv`, `ledger_reference.csv`, `ledger_ideal.csv`,
`ledger_friction_floor.csv`, `stress_spread.csv`, `ledger_tables.md`. Rerun: activate the
environment, then `python energy_ledger.py`, `python summarise_ledger.py`,
`python -I stress_spread.py` from this directory.
