# Research gap and next experiments: fixed vs SoH-scheduled LQR

Date: 2026-10-24. Scope: the EV longitudinal-dynamics project in `D:\EURÉKA 2026 - KT` only.

**Inputs.** This document builds on four existing records:

- `docs/literature_review_soh_scheduled_lqr.md` (citations [Key] refer to its §8);
- `docs/research-contribution-review.md` (the project's own findings N01–N04 and the claim
  status);
- `verification/controller-crosscheck-integrity-review.md` (numerical agreement and
  constraint headroom);
- `docs/model.md` and `configs/parameters.yaml` (plant and parameters).

It adds no simulations or results. Arithmetic marked **[review]** is derived here from
recorded numbers. It is not a project result.

**Independence.** The model, the experiments, the earlier reviews and this document were all
produced by the same AI research assistant. No person has independently checked them.

---

## 1. What is already established

**In the literature:**

1. **Gain scheduling is a mature method.**
   - It is used when plant dynamics vary with a measurable scheduling variable
     [Rugh2000; Leith2000; Shamma1992].
   - In vehicle speed control the variables scheduled on are mass, speed and grade, which
     change the longitudinal dynamics [Tran2022; Vahidi2005; Hattori2020].
2. **Health-aware energy management is established for HEVs and PHEVs.** Battery wear
   enters the cost, and the controller decides the power split [Serrao2011; Ebbesen2012;
   Moura2013; Xie2019; DePascali2020; Anselma2021].
   - Ageing-aware gains in total cost can be small, e.g. 1.29–1.65 % [Xie2019].
   - Experimental ageing validation exists but is rare [Anselma2021].
3. **Degradation-aware BEV speed control exists.**
   - It obtains energy or ageing benefits by changing the speed or spacing trajectory,
     usually against weak baselines: cruise control, a preceding vehicle, regular driving
     [Pan2023; Jia2022; Zhang2022; Shao2019; Wang2024].
   - Lifetime benefits are evaluated with the same ageing model the optimiser uses.
   - A 2026 systematic review found SoH or thermal effects in fewer than 10 % of 60 Eco-ACC
     studies, and real-world tests in 10 % [Mahdy2026].
4. **Energy-aware LQ control exists.**
   - Loss terms enter the LQR cost, and savings come from reshaping the trajectory
     [Hattori2020].
   - LQ tracking can be competitive with adaptive schemes [Razi2021].
5. **SoH reduces battery power capability through resistance growth and voltage and current
   limits** [Plett2004; Waag2013 (SEC); Etxandi2024].
   - In simulation, small packs reach power limits before capacity limits [Etxandi2024].
   - LFP resistance-growth data exist for specific cells [Severson2019; Naumann2020;
     Pan2023]. They are cell-, temperature- and protocol-specific.
6. **A fixed versus weight-adapted comparison exists** [Pan2023]. A fixed-weight,
   degradation-aware MPC matched or beat the adapted one in some regimes, and the
   differences were in the third or fourth significant digit.

**In this project** (records, not literature):

- N01: no practical energy difference (+0.003 % at S1, SoH 0.8).
- N02: a once-retuned fixed gain is better on both metrics (H_C).
- N03: robustness mean −0.054 %.
- N04: the resistive share is 1.1–2.1 % of supplied energy.
- The Python and Modelica implementations agree to within numerical error, except for an
  unresolved, bounded S1 accumulator discrepancy (≤ 4.3 × 10⁻⁹ percentage points in ΔE).

## 2. What is genuinely different about this study

| Feature | Literature status (from the searches; see the review §1.2) | Difference |
|---|---|---|
| SoH-scheduled **LQR weights** for **speed tracking on a fixed trace** | No counterpart found. The thesis's own Table 6 entry "Huang et al. 2023, LQR, SoH-based" could not be identified (review §9) | Different object of study. It is a test of a specific law, not a new method |
| **Pre-registered** hypotheses, including a competing explanation (H_C: one retuned fixed gain) | Literature baselines are usually PID, SMC, cruise control or human-like driving [Pan2023; Zhang2022; Wang2024; Pusztai2025]. No pre-registered vehicle-control comparison was found | **Stronger baseline discipline** than the reviewed studies |
| **Energy decomposition** showing how small the battery resistive share is on the same trace (an explanation, not a bound on controller differences; see §4.3) | Literature attributes savings to trajectory freedom [Hattori2020; Han2019] | Helps explain *why* the tested result is null |
| **Two independent implementations** (Python RK4; Modelica with DASSL), with the paired-difference numerical error compared with the effect size | Not found in vehicle-control papers. Cross-code checks are standard V&V practice [Roache1997] | A reproducibility practice, not a methodological invention |
| Bibliographic and claim audit of the original thesis | — | Research integrity. Not a scientific finding |

**Not different:**

- LQR and DARE design, gain scheduling, the Thevenin ECM, the point-mass model, Monte Carlo
  robustness;
- the idea of SoH-aware control;
- the idea that power limits tighten with ageing [Etxandi2024; Plett2004].

## 3. What kind of contribution the evidence supports

| Candidate | Verdict | Reason |
|---|---|---|
| Applied control contribution (a better controller) | **Not supported** | No energy or tracking benefit (N01, N02). There is no physical pathway for SoH into the controlled dynamics (§4). No new design |
| Methodological or reproducibility contribution | **Supported in a narrow form** | A worked, pre-registered and cross-implementation-verified negative result with a fair fixed-gain baseline and an energy-decomposition explanation. Limits: (i) produced by one assistant, with no independent replication; (ii) the methods themselves are standard; (iii) one numerical discrepancy is unresolved, though bounded |
| Bounded empirical finding | **Supported** | In the tested model, profiles and controllers, scheduling LQR weights on SoH did not materially change energy. The first-order ageing-induced change in resistive loss was ≈ 0.3 %, which is not a bound on controller differences (§4.3) |

**Overall.** The thesis can defend:

- a **bounded negative result**;
- a **model-class explanation** of it;
- a **reproducibility case study**.

It cannot defend an applied-control contribution or a novelty claim.

## 4. Does SoH scheduling have a physical pathway into the current plant?

### 4.1 Where SoH enters

From `docs/model.md` §1 and `src/eureka/plant.py`:

- **Controlled dynamics** (speed and torque):
  - M_eff dv/dt = F_w(T) − F_rr(v) − F_aero(v) − F_fb;
  - dT/dt = (T_cmd − T)/τ_T;
  - T_cmd = clip(T_ref, ±T_lim(ω)), with T_lim(ω) = min(T_max, P_max/ω).

  **None of these terms depends on SoH.** T_max = 85 N·m and P_max = 18 kW are constants
  (`configs/parameters.yaml`).
- **Battery** (the only place SoH enters):
  - R0 = R0_new(1 + k_r0(1 − SoH)) and R1 = R1_new(1 + k_r1(1 − SoH));
  - dSoC/dt = −I/(3600 Q SoH);
  - the current I solves P_e = (V_oc − V1 − R0 I) I.
- **Coupling.** The battery feeds back into the vehicle only if a battery-side quantity
  limits torque. The model has **no** minimum terminal voltage, no current limit, no
  SoH-dependent power derating and no dependence of T_lim on DC-bus voltage
  (integrity review §6).

**Consequence.** For a given torque trajectory T(t), the speed trajectory v(t) is identical
at every SoH. SoH changes only the **cost of delivering** that trajectory, through I²R and
V1 losses.

### 4.2 Why changing controller gains is not modelling battery health

1. **Gains are a design choice; health is a plant property.**
   - A health effect is modelled when the plant (losses, limits, capacity) changes with
     SoH.
   - The scheduled controller changes Q and R as a *label-driven* function of SoH.
   - No plant term that the controller acts on changes with SoH.
2. **At any fixed SoH, the "adaptive" controller is just another fixed LQR.** Whether a
   different weighting helps is answered by the fixed-gain family (S-C), independently of
   SoH. There, energy and tracking error fell together as R decreased, so there was no
   trade-off for scheduling to exploit (N02; `docs/research-contribution-review.md` §5.1).
3. **The law's direction is not derived from any optimality condition involving SoH.**
   - The law softens the torque-state weight and raises R as SoH falls.
   - An energy-optimal LQ design would add a loss term weighted by R0(SoH) [review,
     following the structure of Hattori2020 and Han2019].
   - Battery ohmic loss ≈ R0(SoH)·(Tω/(η V_oc))². At a linearisation speed ω0 this is a
     quadratic torque penalty with weight ∝ R0(SoH)·ω0²/(η V_oc)².
   - That is a *principled* scheduling of R, and it is not the thesis's law. It is listed
     as a baseline in §7–§8.
4. **The thesis's stated mechanism is absent from the documented model.**
   - The thesis attributes the scheduling to "reduced control authority due to increased
     battery internal resistance" (report.md L3328, L6112) and to "changes in vehicle
     dynamics due to battery aging" (L3174; O1 at L609).
   - In the documented model, control authority is unchanged: S1 peak torque request is
     ≤ 0.62 of T_lim; S1 peak electrical power is 12.8 kW against a computed battery
     capability of 99.8–114.7 kW (`review_constraint_headroom.json`).
   - Authority could fall only through a battery-side limit, which the model does not
     contain.
5. **Exact SoH knowledge favours the scheduler.** Even in that best case it showed no
   benefit. A real SoH estimator adds error.

### 4.3 Size of the ageing-induced resistive-loss change in the tested runs [review]

- **Recorded inputs:**
  - battery resistive loss is 1.1–2.1 % of supplied energy (N04);
  - with k_r0 = 0.5 and k_r1 = 0.3 (both `report_unverified`), R0 rises by 15 % and R1 by
    9 % at SoH 0.7.
- **Estimate.** The first-order increase in battery resistive energy loss caused by ageing
  is about 0.15 × 2.1 % ≈ 0.3 % of supplied energy, under the assumptions listed under
  "Limits of the estimate" below.
- **What the estimate is not.** It is **not** a mathematical upper bound on the
  energy difference between two controllers (`docs/battery-data-feasibility-audit.md` §7).
  - ΔE compares controllers at the same SoH.
  - Their energy can differ through every trajectory-dependent term, not only the ageing
    increment:
    - motor/inverter loss, applied as ÷η_mi when motoring and ×η_mi when regenerating;
    - gear loss, with the same direction-dependent asymmetry;
    - the R1 (polarisation) loss;
    - how much energy is regenerated rather than consumed;
    - friction braking;
    - the final kinetic energy;
    - deviations of the tracked speed from the reference.
  - No argument bounding these differences over all admissible controllers has been
    derived.
- **What the study does show.** The recorded evidence is empirical and limited to the
  tested model, profiles and controllers:
  - the scheduled-minus-fixed differences were 0.000 % to +0.005 %
    (`artifacts/tables/primary_pairs.csv`);
  - the 41-member fixed-gain family spanned 0.28 % in energy
    (`artifacts/tables/fixed_family.csv`, as quoted in
    `docs/research-contribution-review.md` §5.1).
- **What the study does not establish.** It does not show whether a ≥ 1 % improvement is
  possible under a more physically complete model, for example one with SoH-dependent
  voltage, current or power limits, OCV(SoC), an efficiency map, or other profiles.
- **Limits of the estimate.**
  - It is first-order: it ignores the I² change, takes the 2.1 % maximum as applying at
    every SoH, and holds only for the unverified k_r0 and k_r1.
  - A literature-derived resistance-growth law could be larger. Pan2023's table suggests
    R0,EOL/R0,new ≈ 1.7 under a different SoH definition (needs checking).
  - Even then, the resistive share stays a few per cent of supplied energy unless the pack
    resistance itself is much higher.

> **Correction, 2026-10-24.** The version of §4.3 written earlier on 2026-10-24 was headed
> "Upper bound on what SoH-scheduling could affect in this model". It contained these
> sentences, now withdrawn:
>
> - "This bounds the *SoH-specific* share a controller tracking the same trace could act
>   on, even if it removed the ageing penalty entirely, which it cannot."
> - "The bound is below the pre-registered ±1 % margin. So within this model and parameter
>   set, H1 (ΔE ≤ −1 %) was unreachable by construction for any SoH-scheduled controller
>   tracking the same profile."
>
> They treated a first-order loss estimate as an upper bound on controller differences.
> The reason for the withdrawal is in `docs/battery-data-feasibility-audit.md` §7. The same
> correction narrowed the "Energy decomposition" row of §2, the methodological and
> empirical rows of the §3 table, and the §9 recommendation.

## 5. Narrowest defensible research question

> In a documented, dimensionally consistent, torque-controlled longitudinal model of a
> hypothetical 48 V micro-EV in which battery SoH (70–100 %, known exactly) changes only
> battery resistance and capacity, and in which no actuator or battery limit is reached on
> the synthetic profiles S1 and S2, does scheduling the LQR weights on SoH according to the
> thesis's law (Eqs. 4.39–4.42, mapped as in the pre-registration) change model-computed
> battery energy per km or speed-tracking RMSE relative to (a) a fixed LQR designed at
> SoH = 100 % and (b) the best member of a pre-declared fixed-gain family? Are any
> differences resolvable above the numerical error of two independent implementations?

The answer on record:

- the difference is resolvable numerically: +0.003 % at S1, SoH 0.8, against numerical
  errors ≤ 4.3 × 10⁻⁹ percentage points;
- it is practically negligible under the ±1 % decision margin;
- (b) beats the schedule on both metrics.

The decision margin is **not** an equivalence bound [Lakens2017], so "equivalent" must not
be claimed.

## 6. Thesis claims to remove, narrow, or support

Locations refer to `data/processed/report/report.md`. The original `.docx` is unchanged.
This table complements the withdrawal list in `docs/research-contribution-review.md` §6. It
does not repeat items already withdrawn there (C01–C40) except where the literature adds a
reason.

| Claim (location) | Action | Reason or evidence needed |
|---|---|---|
| "adaptive LQR … with battery aging compensation" (L3, title of Contribution 1 at L788, journal title at L6588) | **Narrow** to "SoH-scheduled LQR weights" | No compensation was demonstrated. SoH does not change the controlled dynamics (§4.1) |
| O1: gains "compensate for battery aging effects on powertrain dynamics" (L609); "compensating for changes in vehicle dynamics due to battery aging" (L3174) | **Remove** | Contradicted by the documented model structure (§4.1) |
| "reduced control authority due to increased battery internal resistance" (L3328, L6112) | **Remove**, or support with Option B | Requires battery voltage, current or power limits that bind and depend on SoH. Absent from the model; headroom ≥ 7.8× in power (§4.2 item 4) |
| O4 and the target "battery lifetime extension ≥ 10 %" (L621, L673) | **Remove** | No ageing model was run. Lifetime claims in the literature need a degradation model, and for credibility independent ageing tests [Anselma2021] |
| "novel adaptive LQR framework" (L790); research-gap claims (L2590, L2608) | **Remove** | Gain scheduling and health-aware control are established (§1). Novelty was not established by a database search (review §1.2) |
| Assumption 5: LFP cells with parameters "identified from Huria et al." (L750) | **Correct** | Huria et al. (2012 IEVC, not 2018 TIA) used NMC/graphite cells (review §6, §9). The parameters have no LFP source |
| "SEI growth theory … (Huria 2018, J. Power Sources)" (L5998) | **Remove** or replace | Wrong venue and year. By its abstract the source is an electrical/thermal ECM paper with no SEI model |
| Literature Table 6 (L2560–2584) and the cited percentages 23.5 %, 18.2 %, 15.7 % (L2328–2332) | **Remove** or replace with verified studies | Refs. 7–9 were not found as cited; Table 6 entries cannot be identified (review §9) |
| Declaration: "validated parameters from published datasheets" (L5980) | **Remove** | `configs/parameters.yaml`: parameters are `report_unverified` or `assumed`; none measured |
| "Journal Paper 1 … (Under Review)" (L6588) | **Author to confirm or remove** | Not verifiable from the project. The title restates a claim (aging compensation) that the evidence does not support |
| Any statement that adaptive or SoH-aware control is ineffective in general | **Do not add** | Only one law, one model, in the unconstrained regime |
| "Python and Modelica results validate the model" | **Rephrase** as "reproduced in two independent implementations to within numerical error" | Agreement is verification, not validation [Roache1997; Roache2002]. Also report the unresolved S1 accumulator discrepancy |
| "SoH-aware control may matter when power limits bind" | **Keep only as a hypothesis**, with citations | The mechanism is supported [Etxandi2024; Plett2004]. It is untested here |

---

## 7. Option A: close out as a bounded comparative and reproducibility study

**Research question:** as in §5.

**Hypotheses.**

- H1, H0, H_W and H_C were tested in the pre-registration, and the decisions stand.
- The remaining falsifiable statements concern reproducibility:
  - **A-R1 (independent replication):** a person other than the author, running
    `scripts/setup.ps1`, `scripts/verify.ps1` and `scripts/reproduce_all.ps1` on a clean
    machine, reproduces `artifacts/reports/primary_results.json`. The criterion is
    hash-identical outputs, or ΔE within the recorded Python step error of 2.3 × 10⁻⁸
    percentage points. It is falsified by any larger deviation.
  - **A-N1 (symmetric numerics, optional):** under the protocol §8.1 rule, every one of
    the 16 cases passes with its *own* step and tolerance evidence (integrity review §4.4).
  - **A-N2 (S1 accumulator discrepancy, optional):** the −8.4 × 10⁻⁷ m S1 end-distance
    deficit disappears when the controller `sample()` is replaced by a drift-free
    time-event formulation (integrity review §3). This needs a dated amendment.

**Fair baselines.** Already in the record:

- the fixed LQR at SoH 1;
- the fixed-gain family c ∈ [0.1, 10] (S-C).

No new controller is needed to close A.

**Scenarios and controlled variables.** Unchanged: S1 and S2; SoH ∈ {1.0, 0.9, 0.8, 0.7};
the same plant, gains, profiles and noise seeds.

**Metrics.** Unchanged:

- primary: ΔE in energy per km;
- secondary: RMSE ratio, max |e|, RMS and peak current, and the energy split.

**Numerical verification.**

- Done: Python step refinement, Modelica DASSL tolerance refinement, and paired-difference
  error against the effect size.
- Remaining:
  - equalise the evidence across SoH levels (~25 min of compute; integrity review §4.4);
  - state the S1 discrepancy as unresolved and bounded.

**Evidence before claiming practical benefit.** Not applicable. Option A claims no benefit.
It must state the scope limits:

- unconstrained regime;
- synthetic profiles;
- unverified parameters;
- exact SoH;
- no ageing model;
- no vehicle data.

**What remains to be validated** (cannot be done inside A):

- physical validity of every parameter;
- standard cycles (UN GTR 15 / WLTC tables from the official text);
- a measured efficiency map;
- a sourced resistance-growth law;
- any HIL or vehicle test.

**Effort (estimates):**

- thesis revision per §6: 2–4 days of author time;
- A-R1: 0.5–1 day for a supervisor or peer;
- A-N1: under 1 hour of compute plus a write-up;
- A-N2: 0.5–1 day including the amendment.

---

## 8. Option B: extend the plant with SoH-dependent battery and powertrain limits

### 8.1 Is the source support adequate today?

**No, not for a defensible reference vehicle.**

- **Available sources:**
  - cell-level LFP resistance-growth data [Severson2019; Naumann2020; Pan2023];
  - a manufacturer-recommended voltage window for one cell, given in a peer-reviewed
    paper: 2.0–3.6 V for the A123 APR18650M1A [Severson2019];
  - the mechanism [Plett2004; Etxandi2024].
- **Missing:**
  - an official datasheet with continuous and peak (duration-specified) discharge and
    charge current limits for the same cell. The copies found were on third-party forums,
    so they are not authoritative and are not used;
  - an LFP OCV(SoC) table;
  - aged R1 and C1 for LFP;
  - any sourced 48 V micro-EV pack topology, BMS derating policy, or motor/inverter
    torque–speed data versus DC voltage;
  - sourced vehicle parameters.

**Recommendation:** do **not** implement B until the parameters marked *missing* in §8.2
are obtained from authoritative sources.

**Key point [review, from recorded data].** S1 already draws a peak of 274–275 A (≈ 2.7C on
the 100 Ah pack) and regenerates −171 A (≈ 1.7C) (`review_constraint_headroom.json`).

- Whether a limit binds therefore depends mainly on the chosen cell's **C-rate rating**,
  which is usually SoH-independent unless the BMS derates it.
- The SoH-dependent **voltage-floor** pathway is far from binding with the model's R0. The
  minimum terminal voltage is 46.35 V at SoH 0.7, a 3.4 % sag.
- If the binding constraint is an SoH-independent current limit, it applies identically to
  both controllers, and SoH still has no pathway.
- The cell must therefore be chosen to represent the intended vehicle. **It must not be
  chosen because its limits make an effect appear.**

### 8.2 Parameters required, their sources, and how they enter

Status values: **sourced** (an authoritative primary source has been read), **candidate**
(a source has been identified but not read in full, or is not for the target cell), or
**missing**. No values are proposed. Ranges must come from the sources.

| # | Parameter (unit) | How it enters the equations | Candidate authoritative source(s) | Status |
|---|---|---|---|---|
| 1 | Cell identity; pack topology N_s, N_p (–) | V_pack = N_s·V_cell; Q_pack = N_p·Q_cell; R_pack = (N_s/N_p)·R_cell; per-cell current I/N_p | Datasheet of the chosen cell, plus a declared micro-EV pack design | **missing** (topology would be a declared assumption) |
| 2 | OCV(SoC) per cell (V) | V_oc in V_t = V_oc(SoC) − V1 − R0·I; replaces the constant 48 V | Measured OCV table for the same cell; Pan2023 Fig. 4 is for a Lishen 20 Ah cell, figure only | **missing** |
| 3 | V_min, V_max per cell (V) | Voltage floor and ceiling: I_Vmin = (V_oc − V1 − V_min)/R0; regen I_Vmax = (V_max − V_oc + V1)/R0 | A123 APR18650M1A: 2.0 / 3.6 V "recommended by the manufacturer" [Severson2019]; Lishen 20 Ah: charge 3.65 ± 0.05 V [Pan2023] | **sourced** at cell test level for A123. The **BMS operating window** is a separate design choice (to declare) |
| 4 | I_dis,max continuous and peak, with pulse duration (A) | I_lim,dis = min(N_p·I_dis,max, I_Vmin); P_bat,lim = V_t(I_lim)·I_lim | Official manufacturer datasheet | **missing** (only non-authoritative copies seen) |
| 5 | I_chg,max for regen pulses (A) | I_lim,chg = min(N_p·I_chg,max, I_Vmax); regen beyond it goes to the friction brake | Official datasheet | **missing** |
| 6 | R0(SoH, T, SoC) (Ω) | Replaces R0_new(1 + k_r0(1 − SoH)); enters losses, V_t and both limits | Severson2019 per-cycle IR (30 ms pulses, 80 % SoC, 30 °C; 124 cells) gives R0 against capacity for the A123 cell; Naumann2020 resistance-increase model; Pan2023 linear R–Q relation | **candidate**. Fit with provenance and a cross-cell spread; do not reuse k_r0 = 0.5 |
| 7 | R1, C1 (SoH) (Ω, F) | V1 dynamics; slow sag over τ = R1·C1 | No aged LFP 1RC parameters were read. Seger2022 has aged 2RC tables for NMC+LMO (wrong chemistry) | **missing**. Keep R1 scaling as a declared assumption with a sensitivity range |
| 8 | SoH definition (–) | Q = SoH·Q_new and the mapping to R0 | Must match the data source: Severson capacity ratio vs Pan2023 normalised between new and EoL | **design decision**; must be declared |
| 9 | Cell temperature (°C) | R0(T); limits | Fix at the source's test temperature (30 °C for Severson2019); Etxandi2024 shows cold raises R | **design decision** |
| 10 | Power-limit (state-of-power) policy | How P_lim(SoH) is computed (instantaneous vs N-second pulse) and passed to the controller and anti-windup | Method [Plett2004]; review [Farmann2016]; pulse definitions in INL manuals [INL2015; INL2017] (full text not retrieved) | **candidate** (method); horizon is a design choice |
| 11 | Motor/inverter T_max(V_dc), P_max(V_dc), base speed; efficiency map (N·m, W, rad/s, –) | T_lim(ω, V_dc) = min(T_max(V_dc), P_max(V_dc)/ω, η·P_bat,lim/ω) | Datasheet of a real 48 V PMSM and inverter | **missing**. Without it, only the battery-power cap couples SoH to torque (acceptable as a declared first step) |
| 12 | Vehicle parameters (M, C_d, A_f, C_rr, r_w, G) | Road load, and therefore the demand that meets the limits | Homologation or manufacturer data for a real micro-EV | **missing** (all `report_unverified`) |
| 13 | Demand profiles | Whether limits are reached | Official WLTC tables (UN GTR 15 text); a declared full-acceleration manoeuvre | **missing** (an earlier reconstruction failed its acceptance check, pre-registration §6) |

**Extended equations** (a sketch of how items 3–6 and 10–11 would enter; not implemented):

- **Discharge current cap:**
  I_lim,dis(t) = min( N_p·I_dis,max , (V_oc(SoC) − V1 − V_min,pack)/R0(SoH) ).
- **Discharge power cap:** P_bat,lim = (V_oc − V1 − R0·I_lim,dis)·I_lim,dis.
- **Regeneration current cap:**
  I_lim,chg(t) = min( N_p·I_chg,max , (V_max,pack − V_oc + V1)/R0(SoH) ).
- **Regeneration power cap:** P_chg,lim = (V_oc − V1 + R0·I_lim,chg)·I_lim,chg.
- **Torque limits:**
  - motoring: T_lim+(ω) = min( T_max , P_max/ω , η_mi·P_bat,lim/ω );
  - regenerating: T_lim−(ω) = min( T_max , P_max/ω , P_chg,lim/(η_mi·ω) ).
- **Friction brake:** braking demand beyond T_lim− goes to the friction brake, as now.
- **Energy balance:** the closure check gains no new terms, but clipped regeneration moves
  energy from "recovered" to "friction-brake loss". This is the main channel through which
  SoH could change energy per km.

### 8.3 Research question and hypotheses (to pre-register as a dated amendment)

**Research question.** When battery current, voltage or power limits that depend on SoH
through a sourced R0(SoH) are reached, does:

- (i) scheduling the LQR weights on SoH, or
- (ii) informing the controller's saturation and anti-windup of the SoH-derated limit,

change energy per km, tracking error or unmet demand relative to fixed-gain baselines?

**Hypotheses.** The thresholds below are proposals for the author to fix before any run.

- **H_B0 (pathway gate; model property; run first):** on at least one pre-declared
  realistic profile, time-at-limit or unmet demand differs between SoH 1.0 and SoH 0.7 by
  more than the numerical error.
  - If false, SoH has no constrained pathway for the chosen cell and vehicle, B reduces to
    A, and the study stops.
- **H_B1 (scheduled vs fixed, constrained):**
  - null: |ΔE| < 1 % and the change in unmet demand is below a pre-declared threshold;
  - falsified if the scheduled law improves either beyond the threshold.
- **H_B2 (information vs scheduling):**
  - claim: an SoH-*informed* saturation and anti-windup on a *fixed* LQR achieves at least
    the benefit of weight scheduling;
  - falsified if weight scheduling beats the SoH-informed fixed LQR by more than the
    threshold.
  - Purpose: this separates "knowing the limit" from "re-weighting the cost".
- **H_B3 (H_C analogue):** the best member of the pre-declared fixed family, with the same
  anti-windup, is not worse than the scheduled law across SoH.

### 8.4 Fair baselines

1. **F0:** fixed LQR designed at SoH 1, saturation at the SoH-1 limit (SoH-unaware).
2. **F0-I:** the same gains, with saturation and anti-windup using P_lim(SoH) (SoH-informed).
3. **S:** the thesis's scheduled law, in both saturation variants.
4. **F\*:** the best fixed gain from a pre-declared family (selection rule as in S-C).
5. **E (optional):** energy-aware LQR with an added R-weight ∝ R0(SoH)·ω0²/(η·V_oc)²
   (§4.2 item 3; Hattori2020-style loss in the cost). This is the strong adaptive
   candidate the earlier review found missing.
6. **SoH-estimation-error variants** for S, F0-I and E, with SoH perturbed by a declared
   error, because exact SoH favours the scheduled designs.

### 8.5 Scenarios and controlled variables

- **Profiles.** S1 and S2 (unconstrained reference); official WLTC tables once retrieved;
  one declared full-demand acceleration and regeneration manoeuvre.
  - The manoeuvre is defined by driver demand (e.g. maximum torque request), **not** tuned
    to make a limit bind.
- **SoH** ∈ {1.0, 0.9, 0.8, 0.7}. **Temperature** fixed at the source temperature.
  **Initial SoC** fixed and declared.
- **Held identical across controllers:** plant, parameters, noise seeds, friction-brake
  logic and anti-windup structure. Gains are designed only on P-TUNE.

### 8.6 Metrics

- **Primary:**
  - energy per km (the existing definition);
  - tracking RMSE;
  - **unmet demand**: the integral of max(0, v_ref − v) dt, and the distance deficit at
    the end;
  - time-at-limit.
- **Secondary:**
  - friction-brake energy and clipped-regeneration energy;
  - minimum per-cell terminal voltage and peak per-cell C-rate;
  - max |e| and the number of saturation episodes;
  - Ah throughput, reported **only as a stress proxy**. No lifetime claim without an
    ageing model.

### 8.7 Numerical-verification requirements

- **Energy balance** closure in every run, including clipped regeneration and the friction
  brake. Same tolerance as now (≤ 5.4 × 10⁻¹⁰ achieved previously).
- **Step and tolerance refinement for every case**, each with its own evidence:
  - Python dt ∈ {1e-3, 5e-4, 2.5e-4, 1e-4};
  - Modelica DASSL at 1e-8, 1e-10 and 1e-12;
  - no borrowed tolerances (integrity review §4.4).
- **Non-smooth limits:**
  - count limit-switching events against step size;
  - check for chattering at min() boundaries;
  - confirm event detection in Modelica, using the existing guard and the DASSL-only rule.
- **Error budget.** The numerical error of each *paired difference* must be at most 1/10
  of any effect reported as resolved.
- **Consistency check.** Compare accumulated distance and energy with the integral of the
  saved speed and current, as in integrity review §3, to catch accumulator bias.

### 8.8 Evidence needed before claiming practical benefit

1. Sourced parameters for one identified cell and pack, and for the motor and inverter
   (items 1–7 and 10–12 in §8.2). No assumed limit values.
2. An effect larger than numerical error, robust across parameter ranges **derived from
   the sources**, e.g. the cross-cell R0 spread in Severson2019.
3. Robustness to realistic SoH-estimation error.
4. Outperformance of F0-I, so that any gain is attributed to scheduling rather than to
   knowing the limit.
5. For any real-world statement, HIL with a real BMS or inverter, or a dynamometer test.
6. For any lifetime statement, a validated ageing model and preferably ageing tests
   [Anselma2021].
7. Independent replication.

### 8.9 Scope and effort (estimates)

| Step | Effort |
|---|---|
| Source acquisition (datasheets; Severson2019 dataset; full texts of Naumann2020 and Plett2004) | 1–4 weeks, depending on access; external dependency |
| Parameter-provenance file and R0(SoH) fit with uncertainty | 2–4 days |
| Protocol amendment (dated, before runs) | 1–2 days |
| Plant extension and unit tests (limits, energy balance, regen clipping) | 1–2 weeks |
| Python runs (4 SoH × 3–4 profiles × 6–8 controllers) | hours |
| Modelica port and per-case cross-check | about 1 week (based on the previous cross-check) |
| Analysis and write-up | 1 week |

---

## 9. Recommendation

**Most defensible contribution.**

- A pre-registered, two-implementation-verified **negative result**: the thesis's
  SoH-scheduled LQR weights give no practical energy benefit, and a retuned fixed gain does
  better.
- An **explanation within the tested model**: SoH has no pathway into the controlled
  dynamics, and the first-order ageing-induced change in resistive loss is ≈ 0.3 % of
  supplied energy. This is not an upper bound on controller differences (§4.3).
- Presented as a **reproducibility case study**, not as an applied-control advance.

**Evidence gap.** The literature supports a mechanism the model does not contain:

- ageing raises resistance;
- voltage, current and power limits then bind, first in small packs.

There is no sourced, cell-consistent parameter set (current limits, R0(SoH), OCV, pack
topology, motor V_dc dependence) with which to test it.

**Single recommended next technical action.** Run the **Option B pathway gate (H_B0) as a
sourcing and headroom exercise, before any model change**:

1. Obtain the official manufacturer datasheet for one LFP cell with published
   resistance-growth data. The A123 APR18650M1A pairs with the Severson2019 dataset.
   Choose by representativeness of the intended vehicle, not by expected outcome.
2. Record V_min and V_max, continuous and peak (with duration) discharge and charge current,
   and R0 against capacity, with provenance, in a new parameter-provenance file.
3. Compute, from the **already-saved** S1 and S2 traces, whether SoH-dependent capability
   falls below the recorded demand (274 A and −171 A peak at pack level) for SoH 0.7–1.0,
   under a declared pack topology. No new simulation is needed.

**Decision:**

- **If no SoH-dependent limit binds**, close the study as Option A, adding the sourced
  statement "limits do not bind for this cell and these profiles".
- **If one binds**, write the dated protocol amendment for Option B (§8.3–§8.7) before any
  run.

**In parallel (author work, no computation):** revise the thesis according to §6 and the
citation corrections in the literature review §9.
