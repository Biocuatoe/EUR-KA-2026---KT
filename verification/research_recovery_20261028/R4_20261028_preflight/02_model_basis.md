# R4 preflight — Phase 2: model-basis dossier

**Date:** 2026-10-28. **Prepared by:** AI assistant; no human review.
**Companion files:** `02_parameter_ledger.csv` (64 parameters, stable IDs) and `02_model_gaps.md` (blocker register).
**Sources inspected in this run:**
- R1 `parameter_registry.csv`, `R3_model_basis.md`, `R3_literature_and_parameter_sources.csv`, R3 code `r3_lib.py`;
- `docs/thesis_full_scientific_audit.md` (A-xx derivations, C-xx claims), `docs/battery-data-feasibility-audit.md`;
- `audit/external-data-provenance.csv` (EPA hashes re-verified), `configs/cycles/profiles.yaml`;
- the v8 thesis source in the snapshot.

No new literature, dataset or network source was consulted; the instructions forbid that in this phase.

**Provenance classes (as defined for R4):**
- **A:** primary authoritative source applicable to the system.
- **B:** peer-reviewed model or data, with applicability documented.
- **C:** secondary source or transparent engineering estimate, usable only in a declared sensitivity analysis.
- **D:** unsupported, contradictory or unavailable.

The ledger gives every parameter two classes:
- `category_as_KT01_value`: is this a supported fact about the thesis vehicle?
- `category_as_RP_assumption`: is it a transparent, range-swept assumption for a declared reference plant?

A C or D value is never described as validated.

---

## 1. Summary

| | Count (of 64 ledger rows) |
|---|---|
| Class A as a KT-01 value | 2 (air density, gravity), both physical constants |
| Class B as a KT-01 value | **0** |
| Class D as a KT-01 value | 51 |
| Not applicable (project definitions, test conditions, numerics) | 11 |
| Used in the proposed R4 pilot | 45, every one as a *declared reference-plant assumption* |
| Excluded or blocking | 19 |

**No KT-01 vehicle, motor, battery or ageing parameter is supported by a primary or peer-reviewed source.** Every thesis-printed value is class D as a statement about KT-01. Ten of them conflict with other statements in the same thesis (§3).

## 2. Model structure available for re-use

These are the equations already implemented and tested in R1–R3 (`verification/scientific_rebuild_20261024/model_equations.md`; `R3_20261025/code/r3_lib.py`, frozen hash `c2403adc…`). Phase 2 inspected them; it did not change them.

| Block | Equations (summary) | Status |
|---|---|---|
| Longitudinal dynamics | M_eff·v̇ = G·η_g·T/r_w − ½ρC_dA_f v² − C_rr M g tanh(v/0.05) − viscous terms; effective mass includes rotor inertia | executes; cross-checked against an independent Modelica port to ≈ 1e-9 [inherited] |
| Actuator | first-order torque lag τ_T; saturation at min(T_max, P_max/ω, battery-derived limits) | executes |
| Motor/inverter loss | three structures M0 (constant η), M1 (η vs power fraction, generic template), M2 (k_c·T²) | executes. **None is a measured map** (§4.2) |
| Battery | OCV source (constant 48 V) + R0 + one RC branch (R1, C1); current from the power balance; voltage window and current limits mapped into torque limits | executes. Parameters class D/C |
| SoH coupling | capacity Q·SoH (SoC bookkeeping); R0 and R1 grow with k_r0, k_r1. Current limits are SoH-independent, except in the exploratory L-EVE-s (class D) | executes |
| Braking | regeneration up to the motor and charge limits, the rest by friction | executes |
| Energy accounting | E_chem = ∫V_oc·i dt with i > 0 on discharge (regeneration netted). Separate E_pos and E_neg integrals allow an independent check | executes; recomputation agreed to ≤ 9e-14 relative in R3 [inherited] |
| Ageing | **none** | — |
| Thermal | **none** (isothermal) | — |

That the equations execute and agree across implementations shows **numerical consistency only**. It does not show physical validity. No part of this model has been compared with measurements of any vehicle, motor or battery.

## 3. Conflicting specifications (recorded, not resolved)

| ID | Quantity | Conflicting statements | Effect if unresolved |
|---|---|---|---|
| X-1 | Vehicle mass | 850 kg = curb + 150 kg (Table 8); Monte Carlo centre curb + 75 kg; "calibrated against" Wuling Mini (665 kg) and VF3 (1,035 kg); thesis L7e definition 600 kg | road load, inertia (VEH-01) |
| X-2 | Wheel radius | 0.28 m (Table 8); 0.165 m from the "13-inch" note; 0.265 m in the LHS | motor speed/torque operating point (VEH-06) |
| X-3 | Drivetrain efficiency | Table 8 combined 0.88; Appendix A product 0.848 | loss level (DRV-02, MOT-05) |
| X-4 | Motor capability | 85 N·m to base speed on 48 V vs back-EMF and inductive limits that permit it only below 0.46 m/s | the printed motor is not physically consistent (MOT-01) |
| X-5 | Motor power | 18 kW (Table 8) vs the thesis's own 15 kW L7e limit | vehicle category (MOT-02) |
| X-6 | Pack voltage / cells | 48 V (Table 8, model) vs 16 × 3.2 V = 51.2 V (BOM) | series count, per-cell limits (BAT-03, BAT-04) |
| X-7 | Pack energy | 4.8 kWh (48 V × 100 Ah) vs 5.12 kWh (16 × 3.2 V × 100 Ah) | range, C-rate mapping (BAT-05) |
| X-8 | Drag coefficient basis | "wind tunnel data" (Table 8) vs "micro-EV average" (Appendix A) | justification only (VEH-04) |
| X-9 | Control timing | Ts = 10 ms vs the thesis's own ≤ 2 ms rule; bandwidth 62.8 vs 100 rad/s | controller design basis (CTL-01) |
| X-10 | Fade definitions | 13.94 % (16.5 → 14.2), 16.67 % (Fig. 11 formulas), 5.33 % (v1 tables), 15.3 % (abstract) | no single fade quantity exists (AGE-01) |

None of these is resolved by choice in R4. Where a value is needed for the reference plant, the ledger keeps the thesis-printed value as a declared assumption and sweeps a range. Where the conflict would change the structure (X-4, X-6), the thesis-specific branch is blocked.

## 4. Audit by subsystem

### 4.1 Vehicle and longitudinal dynamics
- Mass, payload, frontal area, C_d, C_rr, wheel radius, gear ratio and efficiency are all thesis-printed without source (class D as KT-01 values) and partly conflicting (X-1 to X-3, X-8).
- As reference-plant assumptions with declared ranges (ledger VEH-01 to DRV-04) they are class C.
- **Drive cycles:**
  - S1 and S2 are synthetic, project-defined and frozen (class C, in domain).
  - UDDS, US06 and HWFET are authentic EPA schedules (class A as cycles; hashes re-verified this run). Their speeds exceed the 0–50 km/h micro-EV domain, so they are **not applicable** to the micro-EV plant except as labelled out-of-domain stress cases.
  - The thesis VUC is undefined (D).
  - **Only one in-domain held-out cycle (S2, 213 s, 0.53 km) is available locally.**
- **Speed tracking and stopping constraints:**
  - The thesis states an RMSE specification of 0.6 m/s (L5047) without a source.
  - R1–R3 used RMSE ≤ 0.10 m/s and max |e| ≤ 1.0 m/s as acceptance criteria (class C, project choices).
  - No stop-compliance rule existed for trajectories before R3's A1.1, which covered the band DP only (`01_r3c_reassessment.md` §1).

### 4.2 Motor and inverter
- **No efficiency map, loss model or datasheet exists for the KT-01 motor.** The printed PMSM parameters are not even self-consistent on a 48 V bus (X-4).
- **The M1 curve is not a vehicle measurement.** It is the generic FASTSim e-machine template; the "2022 Renault Zoe" entry equals the template + 0.01. This is stated in `R3_literature_and_parameter_sources.csv` row M02, read in this run, and detailed in `R3_motor_curve_audit.md`, which was not re-read here [inherited]. It must not be presented as a Zoe map, and certainly not as the KT-01 motor map.
- The thesis's 0.874 is a peak motor efficiency (0.92) times a peak inverter efficiency (0.95), applied as a constant. Motor-only and inverter-only losses cannot be separated in any branch.
- Regeneration uses the same efficiency rule as motoring. Torque limits are symmetric, plus the charge-current limit.
- **Consequence:** a motor-specific energy benefit **cannot be established for the claimed system.** On the reference plant, M0/M1/M2 serve as a *structural bracket*. A conclusion is reportable only if it holds in all three, with M2 taken from dynamic runs only (its QS model misses the stall loss).
- A different, real reference vehicle could be proposed as a separately labelled research system. That needs a primary motor map (class A or B), which is not available locally.

### 4.3 Battery
- **Chemistry** LFP per the thesis text. **Cell** unidentified ("3.2V/100Ah", CATL, no part number). **Arrangement** unresolved (X-6). **Rated capacity** 100 Ah printed, without a datasheet.
- **ECM:** R0 5 mΩ, R1 3 mΩ, C1 50 kF printed in Appendix A without a source (D as KT-01; C as reference-pack assumptions with R0 swept 4–6 mΩ).
- **OCV(SoC):** none for any applicable cell. The constant OCV is defensible only because the SoC swing within one cycle is < 2 % on an LFP plateau.
- **Voltage window:** generic LFP 2.5–3.65 V per cell, mapped to 37.5–54.75 V with an assumed 15-cell equivalent. It never binds in R1–R3.
- **Current limits:**
  - 3C/1C (R1 assumption) and 2C/1C (retailer summaries of a *different* cell, EVE LF100; official specification blocked).
  - Both are C as reference-pack assumptions and D as KT-01 values.
  - They decide UDDS friction braking but never bind on S2.
- **SoH-dependent limits:** no source (D). This removes the only plausible SoH mechanism for both H2 and H4.
- **Temperature:** nothing modelled (isothermal). Missing thermal effects are a stated limitation, not an approximation.

### 4.4 Battery ageing

| Requirement from the R4 brief | Status |
|---|---|
| Specific ageing equation and source | Thesis: "SEI growth, Arrhenius" with no parameter source. Fig. 11 consists of typed quadratics (AGE-01). Literature laws exist only for other cells (AGE-02 to AGE-04) |
| Parameter values and units | none read from primary text for any applicable cell |
| Chemistry / temperature / C-rate / SoC / DoD domain | not established for a 100 Ah prismatic LFP pack |
| Calibration or validation data | none. The thesis claim of "agreement within 5 %" with accelerated ageing tests (v8 L2706) has no supporting data anywhere inspected |
| Causal path from control action to ageing-state update | not implemented. Ah throughput and ∫i²dt are stress indicators only. Lower current peaks need not slow ageing (Keil 2015, as cited in R3) |
| Support for the selected pack | none |

**Conclusion:** R4 must not report any numerical capacity-fade figure, fade reduction or cycle-life extension. An energy and electrical-stress study is still possible (§5, RP-E).

## 5. Model branches and their status (Gate G2)

| Branch | Definition | Critical inputs and class | G2 |
|---|---|---|---|
| **K: KT-01 thesis vehicle** | the vehicle as specified in the thesis | vehicle, motor and battery all D; X-1 to X-7 unresolved; no motor map; no cell | **FAIL**: cannot represent the claimed system |
| **RP-E: reference plant, energy and electrical stress** | hypothetical micro-EV with thesis-printed road-load values as declared assumptions (ranges swept); motor bracket M0/M1/M2; generic 48 V / 100 Ah LFP reference pack; limit sets L-R1 and L-EVE; isothermal; no ageing; in-domain cycles S1 (in-sample) and S2 (held out) | all C as declared assumptions, except M1 (D, used only as a labelled illustrative bracket member). No input is A or B | **PASS (narrow).** Executable with every input declared, ranged and traceable. Results are statements about this hypothetical plant only. This is **not physical validation and not KT-01** |
| **RP-S: SoH-dependent feasibility** | RP-E plus SoH-dependent current/voltage limits or derating | BAT-14, BAT-15: no source (D) | **FAIL**: blocked (gap G-BAT-2) |
| **AGE: capacity fade** | any branch plus an ageing law | AGE-01 to AGE-06: none applicable (D) | **FAIL**: blocked (gap G-AGE-1) |
| **RV: real reference vehicle** | a separately labelled real micro-EV with a primary motor map and cell data | not available locally | **NOT ASSESSABLE**: requires sourcing (gap G-RV-1) |

**Why RP-E passes only narrowly:**
- Every value is declared and its range swept.
- The motor-loss structure, which is the uncertainty most likely to change conclusions, is bracketed structurally, not assumed away.
- The cycles are inside the plant's speed and power envelope.
- Conclusions are limited to those robust across the bracket and the ranges.

**What RP-E cannot provide:**
- any number for the thesis vehicle;
- any motor-specific benefit;
- any SoH mechanism beyond resistance growth;
- any fade figure;
- generalisation beyond one short held-out cycle (gap G-CYC-1).

## Gate G2 — PASS for branch RP-E only; FAIL for K, RP-S and AGE

The protocol (`03_R4_protocol_v1.md`) may define executable work only on RP-E. Hypotheses that need K, RP-S or AGE are carried as **blocked**, with the exact missing input named in `02_model_gaps.md`.
