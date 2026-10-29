# Model equations (rebuild 2026-10-24)

The plant is the documented model (`docs/model.md`, `src/eureka/plant.py`) with one addition,
a battery operating window (§3). Code: `src/rebuild/model.py`. With the window disabled, the
derivatives equal `eureka.plant.derivatives` exactly, and the closed loop reproduces
`eureka.simulate` to 1e-9 (`tests/test_rebuild.py`).

## 1. Vehicle and drive (unchanged)

- **Kinematics:** ω = G v / r_w. **Effective mass:** M_eff = M + J_m G²/r_w².
- **Shaft torque:** T_s = T − B_m ω.
- **Wheel force:**
  - motoring (T_s ≥ 0): F_w = G·T_s·η_g/r_w;
  - regenerating: F_w = G·T_s/(η_g·r_w).
- **Road loads:** F_rr = C_rr M g tanh(v/v_ε); F_aero = ½ρC_dA_f v².
- **Friction brake:** F_fb = (G/r_w)·max(0, −T_neg − T_ref)·tanh(v/v_ε).
- **Motion:** M_eff v̇ = F_w − F_rr − F_aero − F_fb. A holding brake acts at v = 0.
- **Torque lag:** Ṫ = (clip(T_ref, −T_neg, T_pos) − T)/τ_T.

## 2. Battery (unchanged)

- **Electrical power:** P_m = Tω, and P_e = P_m/η_mi (motoring) or P_m·η_mi (regenerating).
- **Current:** solve P_e = (V_oc − V1 − R0 I)·I for I.
- **Polarisation:** V̇1 = −V1/(R1C1) + I/C1.
- **SoC:** ṠoC = −I/(3600·Q·SoH).
- **Resistance growth:** R0 = R0,new(1 + k_r0(1 − SoH)); R1 = R1,new(1 + k_r1(1 − SoH)).

## 3. Battery operating window (new)

Let V_o = V_oc − V1 and s = SoH (SoH-scaled cases) or s = 1.

**Discharge (I > 0):**

    I_d = min( c_dis·Q·s ,  (V_o − V_min)/R0 ,  V_o/(2 R0) )        [A]
    P_d = (V_o − R0·I_d)·I_d                                         [W]

- c_dis·Q·s is the current limit, as a C-rate of capacity.
- (V_o − V_min)/R0 keeps V_t = V_o − R0·I ≥ V_min.
- V_o/(2R0) is the maximum-power point of the source.
- P_d is the largest electrical power the battery may deliver.

**Charge (I < 0, magnitude I_c):**

    I_c = min( c_ch·Q·s ,  (V_max − V_o)/R0 )
    P_c = (V_o + R0·I_c)·I_c

**Torque limits:**

    T_base = min(T_max, P_max/ω)
    T_pos  = min(T_base, η_mi·P_d/ω)          drive
    T_neg  = min(T_base, P_c/(η_mi·ω))        regeneration; braking beyond it goes to F_fb

The closed form for P_d and P_c is checked against a brute-force search over I to 1e-4
(`tests/test_rebuild.py`).

**Behaviour at the limits:**
- Because T lags T_cmd by τ_T, the battery current can briefly exceed I_d or I_c. This
  exceedance is integrated as `I_over` [A·s] and reported, not hidden.
- The controller's anti-windup (z frozen while u > T_pos and e < 0) uses T_pos. It
  therefore knows the battery limit, identically for every controller.

**How SoH reaches the controlled behaviour:**
1. through R0 in the voltage term;
2. through s in the current terms (SoH-scaled cases only).

**Analytical consequence (pre-check, `results/precheck_cycles.csv`):**
- The motor limits electrical power to P_max/η_mi ≈ 20.6 kW.
- The voltage window alone binds only if V_min(V_oc − V_min)/R0 < 20.6 kW, i.e.
  R0 > 19.1 mΩ = 3.8·R0,new.
- At SoH 0.7 this requires k_r0 > 9.4; the thesis uses 0.5 and the sensitivity case 2.0.
- **With the thesis's resistance law, resistance growth alone cannot limit the drive.**
- Only current limits that shrink with SoH can.

## 4. Controllers (unchanged; `src/eureka/controllers.py`)

- **Design model:** x = [e, T, z] with e = v − v_ref and z = ∫e dt, input T_ref:

      ė = −a e + b T,   Ṫ = (u − T)/τ_T,   ż = e
      a = (ρC_dA_f v0 + B_m G² η_g / r_w²)/M_eff,   b = G η_g/(r_w M_eff),   v0 = 8.33 m/s

- **Discretisation:** exact ZOH at T_s = 10 ms. The gain is K = (R + BᵀPB)⁻¹BᵀPA, from the
  DARE. The law is u = −K x.
- **F:** Q0 = diag(1/0.5², 1/85², 1/0.5²), R0 = 1/85².
- **F01:** R = 0.1·R0.
- **S:** Q = Q0·diag(1, α, 1), α = 1/(1 + γ_v(1 − SoH)); R = R0(1 + γ_u(1 − SoH)); γ = 1.
- **Stability:** every gain gives |eig(A_d − B_d K)| < 1, so each frozen-SoH closed loop is
  stable for the design model.
- SoH is constant within a run, so no time-varying stability question arises in these
  experiments (see `docs/thesis_full_scientific_audit.md` M-11 for the slow-variation
  condition).

## 5. Metrics (protocol §5)

- **Tracking:** RMSE = √(mean over control steps k = 0…N of (v_k − v_ref,k)²); max |e| over
  the same steps.
- **Energy:**
  - net E = ∫V_oc I dt;
  - E⁺ = ∫max(V_oc I, 0) dt;
  - E⁻ = ∫min(V_oc I, 0) dt (regenerated, negative);
  - E per actual km = E/d;
  - E per reference km = E/d_ref.
- **Relative differences:** ΔE % = 100·(E_a − E_b)/E_b, so the **denominator is the
  comparison controller** (F for S vs F).
- **Energy closure:** E = ΔKE + ½C1ΔV1² + the loss terms. The check passes when the closure
  error is ≤ 1e-3 of ∫|V_oc I| dt.
