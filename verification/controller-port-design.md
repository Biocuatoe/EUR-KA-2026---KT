# Controller port design (Modelica)

Written 2026-10-23, before any closed-loop Modelica case was run. Companion to `verification/controller-crosscheck-protocol.md`.
Everything below was reconstructed from the project's own files; the sources are named so a reviewer can re-check each line.

## 1. Sources read

| Item | File (sha256 prefix) |
|---|---|
| Control law, design model, weights, schedule | `src/eureka/controllers.py` (2d57b757) |
| Sampling, hold, anti-windup, recording | `src/eureka/simulate.py` (dccc267c) |
| Plant, torque limit, brakes, battery, accumulators | `src/eureka/plant.py` (e5701bce); `docs/model.md` (9b29b960) |
| Parameters and controller constants | `configs/parameters.yaml` (0efe2d1a) |
| Profiles | `configs/cycles/profiles.yaml` (90a496a3), `src/eureka/cycles.py` (f09ed877) |
| How runs were built (gains on nominal parameters, batch layout, saved fields) | `src/eureka/experiment.py` (b1ef5d02), `configs/experiments.yaml` (79539611) |
| Metric and decision definitions | `src/eureka/metrics.py` (0ed37076), `scripts/analyze.py` (4d3e355b), preregistration sections 8-10 |
| Saved results | `artifacts/raw/primary/{S1,S2}/{manifest.json,timeseries.npz}`, `artifacts/tables/primary_metrics.csv`, `primary_pairs.csv`, `artifacts/reports/primary_results.json` |

`git diff 38f443a HEAD` shows no change to `controllers.py`, `plant.py`, `simulate.py`, `params.py`, `cycles.py`, `metrics.py`, `experiment.py`, `configs/` or `protocol/` since the commit that produced the raw series (38f443a; the results JSON was written at 3640533). The saved raw-file hashes equal the ones in `evidence/artifact_hashes.json`.

## 2. Reconstructed control law

State of the design model: `x = [e, T, z]`, `e = v - v_ref` [m/s], `T` = delivered motor torque [N m], `z = integral of e` [m]. Input `u = T_ref` [N m].

- Continuous design model (linearised at v0 = 8.333333 m/s, `docs/model.md` section 2):
  `A = [[-a, b, 0], [0, -1/tau_T, 0], [1, 0, 0]]`, `B = [0, 1/tau_T, 0]^T`,
  `a = (rho C_d A_f v0 + B_m G^2/r_w^2 eta_g) / M_eff`, `b = G eta_g / (r_w M_eff)`, `M_eff = M + J_m G^2 / r_w^2`.
- ZOH discretisation at `Ts = 0.01 s`; `K = (R + Bd' P Bd)^-1 Bd' P Ad` with `P` the DARE solution.
- Weights (Bryson, frozen by the P-TUNE acceptance at attempt 1): `Q0 = diag(1/0.5^2, 1/85^2, 1/0.5^2)`, `R0 = 1/85^2`.
- **Fixed LQR:** `K(Q0, R0)` at every SoH.
- **Scheduled LQR:** `Q = Q0 diag(1, alpha_v, 1)`, `alpha_v = 1/(1 + gamma_v (1 - SoH))` (applied to the **torque** state, preregistration deviation (a)); `R = R0 (1 + gamma_u (1 - SoH))`; `gamma_v = gamma_u = 1`. The design model itself does not depend on SoH (preregistration deviation (b), `Delta A = 0`).
- Law at each sample: `u_k = -(K_e e_k + K_T T_k + K_z z_k)`; `u_k` is not clipped by the controller.
- Integral update: `z_{k+1} = z_k` if `sat_k and e_k < 0`, else `z_k + Ts e_k` (forward Euler on `e_k`); `sat_k := u_k > T_lim(w_k)` (positive limit only). The braking side has no anti-windup: braking requests beyond `-T_lim` go to the friction brake inside the plant.

## 3. Answers to the items the task asks to identify

| Item | Finding | Source |
|---|---|---|
| Plant states / inputs | 16 states (v, T, V1, SoC, 10 energy/charge accumulators incl. dist and Ah); input `T_ref` held between samples | `plant.py` `STATES` |
| Controller sample period | `Ts = 0.01 s`; plant RK4 step `dt = 1e-3 s` (10 substeps); `u` held constant over all RK4 stages | `parameters.yaml`, `simulate.py` |
| Sampling instants | `t_k = k Ts`, `k = 0..steps`; at `k` the law is evaluated on the plant state at the start of the interval; `steps = round(duration/Ts)` | `simulate.py` |
| Measurement | exact `v` (the velocity-noise option exists only for S-D, which is not part of this task); `T` and `z` exact | `simulate.py` (`noise=None` in the primary batch) |
| Tracking formulation | `e = v - v_ref(t_k)`, `v_ref` piecewise linear (`np.interp`), no feed-forward of reference acceleration | `simulate.py` |
| Fixed gain and provenance | `K = [196.0353380585201, 0.350684947221061, 150.85451900658825]`; produced by `gain(nominal, "fixed")`; saved in each manifest; tuning accepted at attempt 1 (`tuning-acceptance.json`) | manifests |
| SoH scheduling | **No interpolation and no table.** The gain is computed offline for the run's exact SoH from the closed-form weights above. In the primary experiment SoH takes four values {1.0, 0.9, 0.8, 0.7}, constant within a run, and is known exactly to the controller (preregistration deviation (d), no estimator). The scheduled gain therefore does not change within a run. | `controllers.py`, `experiment.py` |
| Q, R | see section 2 | `controllers.py` |
| Torque and power constraints | `T_lim(w) = min(T_max, P_max / max(w, 1e-6))`, `T_max = 85 N m`, `P_max = 18 kW`, `w = (G/r_w) v`; plant clips the command to `[-T_lim, T_lim]` | `plant.py` |
| Regeneration, friction and holding brake | regeneration: `P_e < 0` through the efficiency in the direction of power flow (no separate cap); friction brake force `(G/r_w) max(0, -T_lim - T_ref) tanh(v/v_eps)`; holding brake: `dv/dt = 0` when `v <= 0` and the net force is negative; RK4 additionally clips `v` to `>= 0` after each step | `plant.py`, preregistration section 4 |
| Battery inputs/parameters | `V_oc = 48 V`, `R0, R1` scaled by `1 + k (1 - SoH)` with `k_r0 = 0.5`, `k_r1 = 0.3`, `C1 = 50 kF`, capacity 100 A h; current from the quadratic with the low-current root; infeasible power flagged | `plant.py`, `parameters.yaml` |
| Initial conditions | `v = 0, T = 0, V1 = 0, SoC = 0.8, z = 0`, all accumulators 0 | `plant.py` `initial_state`, preregistration section 7 |
| Scenario profiles | S1 (324.9107 s, 2161.05 m), S2 (213.2778 s, 531.68 m), piecewise linear, synthetic; simulated to `steps*Ts` = 324.91 s and 213.28 s (the reference is held at 0 after the last knot) | `profiles.yaml`, `cycles.py` |
| Energy definition and sign | `E = integral V_oc I dt` over the run [J] (I > 0 on discharge, regeneration subtracts) divided by 3600 and by the **plant-integrated** distance `integral v dt` / 1000 → Wh/km; ΔE% = (E_sched - E_fixed)/E_fixed x 100 | `metrics.py`, `analyze.py` |
| RMSE definition | `sqrt(mean(e^2))` over all `steps + 1` control samples (including `k = 0` and `k = steps`), not a time integral | `metrics.py` |
| Existing criteria | closure error ≤ 0.1 % of ∫\|V_oc I\| dt, no non-finite state, `v >= -1e-6`; decision table IMPROVES / TRADE-OFF / NO PRACTICAL DIFFERENCE (\|ΔE\| < 1.0 %) / WORSE (ΔE ≥ +1.0 %), RMSE-ratio limit 1.10; sanity: SoH 1.0 gives ΔE = 0 and ratio = 1 exactly | preregistration sections 9-10 |

## 4. Ambiguity assessment (stop condition)

I looked for ambiguity in the control law, gain provenance and sampling method. None blocks the port: the law, weights, schedule, hold and update order are fully determined by `controllers.py` and `simulate.py`, and the gains can be regenerated from `configs/parameters.yaml` (done independently, section 6). Points that are *not* ambiguous but that a port can get wrong, and how each is handled:

1. **Update order within a sample.** `u_k` uses the pre-update `z_k`; `z_{k+1}` is formed afterwards from `e_k` and `sat_k`. Modelica: `pre(z)` inside the `when` equation.
2. **`sat` uses the true speed through the same `T_lim` as the plant, and tests `u > T_lim` only.**
3. **Run length.** `steps*Ts`, not the last knot time. The Modelica stop time is set to `steps*Ts`; the reference after the last knot is held (`min(time, t_last)`).
4. **The last sample (`k = steps`)** is recorded by Python but never applied. Modelica compares samples 0..steps; the controller update at `t = steps*Ts` does not affect any metric.
5. **Standstill handling differs in form.** Python clips `v >= 0` after every RK4 step *and* zeroes negative `dv/dt` at `v <= 0`. Modelica uses only the second rule (a state event on `v <= 0 and F_net < 0`). The plant-level checks (35 passed) exercised this, but closed-loop stops are a different regime; this is a candidate explanation for any discrepancy near standstill and is examined if one appears.
6. **Gains were designed on nominal parameters** for every run (preregistration deviation (2)); in the primary experiment nominal = actual, so there is no model mismatch except the SoH-dependent battery that the design model ignores.
7. **Controller unit of `K`.** `K_e` [N m s/m], `K_T` [1], `K_z` [N m/m]; units are declared in the Modelica block and checked by `omc --unitChecking`.

The existing protocol does **not** supply (a) a numerical-agreement tolerance between implementations, (b) a practical-equivalence threshold *between implementations*. Section 7 of the protocol handles both.

## 5. Modelica implementation

Files (all under `verification/modelica/EurekaController/`, the plant package `EurekaPlant` is loaded unmodified):

| File | Role |
|---|---|
| `SampledLqr.mo` | the controller block: one `when sample(0, Ts)` clause computing `e_k, z_used, T_lim_k, u, sat_k, z, k_ctrl, se2` from the plant states at the event |
| `ClosedLoop.mo` | `extends EurekaPlant.Plant`; adds the profile (`v_ref` from the knots, held after the last knot), instantiates `SampledLqr`, binds `T_ref = ctrl.u` |
| `ControllerProfiles.mo`, `Cases.mo` | **generated** by `verification/scripts/generate_controller_models.py`: P-TUNE/S1/S2 constants; one wrapper per (profile, controller, SoH) with the gains as float64 literals |
| `Tests/ControllerUnit.mo` | the block driven by prescribed signals (controller-logic test, no plant) |

Timing and loop-freedom:

- `u`, `z` and the other controller quantities are `discrete`; they change only inside the `when`. The plant reads `ctrl.u` (a discrete value), the controller reads the plant states at the event. There is no continuous algebraic path from a plant state to `T_ref`, so no algebraic loop and no solver-dependent update.
- Sampling events are generated by `sample(0, Ts)`. Their times are verified against `k*Ts` (protocol, check P2) rather than assumed.
- The `when` clause is the only place where `pre(z)` appears; `z` is initialised to 0 with `fixed = true`.
- Equations: every one of the four in section 2 maps to one line of the `when` clause (`u = -(K_e*e_k + K_T*T + K_z*pre(z))`, `sat_k = u > T_lim_k`, `z = if sat_k and e_k < 0 then pre(z) else pre(z) + Ts*e_k`).

## 6. Gain generation (separate numerical procedure)

`verification/scripts/controller_gain_design.py` (does not import `eureka`; reads only `configs/parameters.yaml`) computes each gain three ways:

1. 50-digit `mpmath`: exact ZOH (matrix exponential of the augmented matrix) and the structured doubling algorithm (SDA); the frozen gain is this result rounded to float64;
2. the same SDA in float64;
3. `scipy.linalg.expm` + `solve_discrete_are` (the project's own route, for the record).

Only after the frozen gains were written were the gains saved by the Python experiment read and compared (`verification/references/controller_gains.json`, key `comparison_with_saved_python_gains`). Executed result: the three routes agree with the 50-digit gain to ≤ 2.2e-13 relative (float64 SDA ≤ 1.4e-14, scipy ≤ 2.2e-13), the ZOH matrices from scipy and mpmath differ by 1.7e-18, and the saved Python gains differ from the frozen gains by ≤ 3.1e-13 relative (all 16 saved runs). Closed-loop spectral radius 0.98940 (fixed) to 0.98937 (scheduled SoH 0.7), inside the unit circle. The gains are written into `Cases.mo` with `repr()` (17 digits); the hashes of the generator input and output files are in `verification/modelica/controller_generated_inputs.json`.

## 7. What this port does not do

- No controller tuning, no new gains, no estimator, no feed-forward, no noise (S-D is out of scope), no EPA cycles.
- No claim about the physical truth of the plant or of any parameter: all parameters stay `report_unverified` or `assumed`.
