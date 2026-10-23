# Plant and design model

This model replaces report Eq. 4.3, which is dimensionally inconsistent (claim C24,
check CHK-AMATRIX-DIM). Parameter values and their provenance are in
`configs/parameters.yaml`. Symbols follow that file.

## 1. Plant (simulated, nonlinear)

**States:** v [m/s], T [N·m] (delivered motor torque), V1 [V] (RC branch voltage) and
SoC [-]. Energy accumulators are integrated with the states (RK4, 1 ms).

**Kinematics:** ω = G v / r_w. Effective mass: M_eff = M + J_m G² / r_w².

**Shaft torque into the gearbox:** T_s = T − B_m ω.

**Traction force** (efficiency applied in the direction of power flow):

- F_w = G T_s η_g / r_w when T_s ≥ 0 (motoring)
- F_w = G T_s / (η_g r_w) when T_s < 0 (regenerating)

**Road loads:**

- F_rr = C_rr M g tanh(v / v_ε)
- F_aero = ½ ρ C_d A_f v |v|

**Friction brake:** F_fb = G · max(0, −T_lim(ω) − T_ref) / r_w · tanh(v / v_ε). Braking
requested beyond the motor's negative limit is fulfilled and dissipated.

**Motion:** M_eff dv/dt = F_w − F_rr − F_aero − F_fb. At v ≤ 0 a net negative force is held
by the holding brake, so dv/dt = 0 and the vehicle never reverses.

**Torque actuator:**

- T_lim(ω) = min(T_max, P_max / max(ω, ε)), so the power limit is active above
  ω_base = 211.8 rad/s, i.e. v = 9.12 m/s (32.8 km/h).
- T_cmd = clip(T_ref, −T_lim, +T_lim), with dT/dt = (T_cmd − T) / τ_T.

**Electrical:**

- P_m = T ω (mechanical power at the rotor).
- P_e = P_m / η_mi when P_m ≥ 0, and P_e = P_m · η_mi otherwise.
- Battery (1-RC Thevenin): V_t = V_oc − V1 − R0 I and P_e = V_t I, so
  I = [(V_oc − V1) − √((V_oc − V1)² − 4 R0 P_e)] / (2 R0).
- dV1/dt = −V1 / (R1 C1) + I / C1, and dSoC/dt = −I / (3600 · Q · SoH).
- SoH dependence (report Eqs. 4.28-4.29): R0 = R0_new (1 + k_r0 (1 − SoH)) and
  R1 = R1_new (1 + k_r1 (1 − SoH)). SoH is constant within a run.

**Energy balance (checked every run):** the chemical energy supplied, ∫V_oc I dt, must
equal the sum of:

- the kinetic-energy change of M_eff;
- the rolling, aerodynamic and friction-brake losses;
- the gear loss (T_s ω − F_w v);
- the shaft friction loss (B_m ω²);
- the motor/inverter loss (P_e − P_m);
- the battery losses, R0 I² and V1² / R1;
- the energy stored in the RC branch, ½ C1 V1².

## 2. Design model (linear, used only to compute gains)

The design model is linearised at v0 with x = [e, T, z], where e = v − v_ref and
z = ∫e dt, and input u = T_ref:

- de/dt = −a e + b T (reference acceleration and the constant load are treated as disturbances),
- dT/dt = (u − T) / τ_T,
- dz/dt = e.

The coefficients are:

- a = ρ C_d A_f v0 / M_eff + B_m G² / (r_w² M_eff) · η_g
- b = G η_g / (r_w M_eff)

The model is discretised by ZOH at T_s = 10 ms, and the gain is K = DARE(A_d, B_d, Q, R).
A test checks this design model against a finite-difference linearisation of the plant.

## 3. Assumptions and what they mean for validity

| Assumption | Effect on conclusions |
|---|---|
| Constant motor/inverter efficiency (peak value from report) | Energy is a function of the mechanical trajectory only; part-load efficiency differences between controllers are not captured. Absolute Wh/km is optimistic. |
| Constant V_oc = 48 V | Battery losses slightly misestimated; no SoC-dependent behaviour |
| SoH affects only R0 and R1 | The vehicle dynamics are independent of SoH under torque control, so tracking can differ only through controller weights |
| SoH known exactly | Best case for the scheduled controller (no estimation error) |
| Flat road, no wind, 25 °C, no auxiliaries | Results do not cover grades, cold weather or HVAC load |
| Rigid drivetrain, no tyre slip | No driveline oscillation; jerk is optimistic |
| Synthetic speed profiles | No claim about Vietnamese or standard-cycle driving |
| Parameters as printed in the report, without primary sources | The vehicle is hypothetical; parameters are not measured |

**External validity:** none of the model, the parameters or the profiles has been
validated against a measured vehicle. Every result is a property of this model only.
