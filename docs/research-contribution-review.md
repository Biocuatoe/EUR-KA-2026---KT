# Research contribution review: fixed-gain vs SoH-scheduled LQR

Date: 2026-10-23. Scope: the EV longitudinal-dynamics project in `D:\EURÉKA 2026 - KT`
only. This review reads the existing records and adds no new experiments, analyses or
results.

**Sources.** Every number below is copied from a saved artifact named next to it. Each
statement is labelled by source:

- **[record]**: the project's evidence documents or saved results.
- **[thesis]**: the in-project copy of the thesis, `data/processed/report/report.md`.
- **[review]**: reasoning added in this review, which is not a project result.

No external literature was consulted, so nothing here is prior-art evidence (see §9).

**Independence.** The model, the experiments, the evaluation report and this review were
all produced by the same AI research assistant, working in the author's repository. No
person has independently re-run or re-derived them yet. Treat that as an open limitation,
not a formality.

---

## 1. Executive assessment

- **The original headline result does not survive scrutiny.**
  - The thesis claims the SoH-scheduled ("adaptive") LQR is 12.5 % ± 2.1 % more energy
    efficient than a fixed-gain LQR. Nothing behind that number exists in the project.
  - The thesis's own body implies a different figure, and its vehicle model is
    dimensionally inconsistent.
  - In a pre-registered test on a corrected model, the scheduling law changed energy use
    by +0.003 %.
- **What the project can defend is a careful, narrow negative result**, plus an
  explanation of why it is negative. On a documented simulation model, under stated
  conditions, scheduling LQR weights on battery health:
  - gave no practical energy benefit;
  - tracked speed slightly worse;
  - was beaten on both energy and tracking by a single fixed gain, retuned once.
- **The explanation [record + review]:**
  - In a torque-controlled drive, battery ageing changes battery resistance, not the
    vehicle dynamics the controller acts on.
  - For a given speed profile, energy use is mostly fixed by the profile itself.
  - The part a tracking controller can shape, battery resistive loss, was only
    1.1–2.1 % of the energy supplied.
- **What the contribution is not:**
  - not a new control method;
  - not evidence about real vehicles;
  - not yet shown to be new relative to published work (§9).
- **The open regime:** the conclusion is silent where battery health is most likely to
  matter, when actuator and battery power limits are active. Those limits were not
  reached in the tested profiles.
- **Can the work be presented?** Yes, as a reproducible, pre-registered simulation
  finding with explicit scope, provided every withdrawn claim (§6) is removed from the
  thesis.

## 2. Main research question

The question as fixed before implementation (`protocol/preregistration.md` §2, commit
`126750a`) [record]:

> On a documented, dimensionally consistent longitudinal model of a 48 V micro-EV with
> SoH-dependent battery resistance, does the report's SoH-scheduled LQR (Eqs. 4.39-4.42)
> change model-computed battery energy per km and velocity tracking error relative to a
> fixed-gain LQR designed at SoH = 100 %? Conditions: flat road, 0-50 km/h synthetic
> urban profiles, SoH 70-100 %, SoH known exactly.

**Hypotheses [record]:**

- **H1 (from the thesis):** ΔE ≤ −1 % with RMSE ratio ≤ 1.10, at SoH 80 % on profile S1.
- **H0:** |ΔE| < 1 %.
- **H_W:** ΔE ≥ +1 %.
- **H_C:** a single, non-scheduled fixed gain can match the schedule across battery life.

**Precise reading [review]:**

- The study tests **the thesis's specific scheduling law**, mapped onto a consistent
  model. Two mappings were forced by the thesis itself (deviations (a)–(d), §4).
- It does **not** test SoH-aware control in general, nor the best possible adaptive
  design.
- At any fixed SoH, the scheduled controller is itself a fixed-gain LQR with different
  weights. So the question is whether *re-weighting with SoH* helps, compared with
  *choosing one good weighting*.

## 3. Evidence-backed findings

### 3.1 Findings confirmed against the saved artifacts

| # | Reported finding | Confirmed from | Status |
|---|---|---|---|
| F1 | Headline numbers not reproducible from the original thesis | `evidence/claim_registry.yaml`: no code, run output or dataset for C01–C04, C10–C16. All 17 checks in `artifacts/reports/report-consistency-checks.json` find an inconsistency; the checks were written after reading the thesis, so selection bias is acknowledged in `docs/evaluation-report.md` | Confirmed |
| F2 | Original state-space model dimensionally inconsistent | `src/eureka/audit/dimensional.py`, claim C24, CHK-AMATRIX-DIM. See §3.2 for its dependence on an external source file | Confirmed from in-project sources |
| F3 | Replacement model passed the independent checks | `artifacts/reports/verification-gate.json`: 152 tests, 0 failures, clean tree at `38f443a`. `artifacts/reports/tuning-acceptance.json`: accepted on attempt 1, overshoot 3.7 %, max \|λ\| 0.989 | Confirmed. Tests prove the tested properties only, not physical accuracy |
| F4 | +0.003 % energy, 1.1 % worse tracking at SoH 80 % | `artifacts/reports/primary_results.json`: ΔE = +0.0030 % (49.9025 → 49.9040 Wh/km); RMSE ratio 1.011 (0.0504 → 0.0509 m/s) | Confirmed |
| F5 | Pre-registered verdict: no practical difference | Same file: `decision_H1 = NO PRACTICAL DIFFERENCE`. All 8 profile × SoH pairs: ΔE 0.000 to +0.005 %, RMSE ratio 1.000–1.020. The sanity control (SoH 100 %) was bit-identical | Confirmed |
| F6 | A retuned fixed controller performed better | `artifacts/reports/fixed_family_results.json`, SoH-averaged: R × 0.1 gives 49.854 Wh/km and 0.038 m/s vs scheduled 49.881 Wh/km and 0.051 m/s; `H_C_holds = true`. In `artifacts/tables/fixed_family.csv`, even the pre-registered fixed gain (R × 1: 49.880 Wh/km, 0.050 m/s) is below the schedule on both | Confirmed. The best member is at the edge of the tested range |
| F7 | Robustness: small differences under assumed ranges | `artifacts/reports/robustness_results.json`: 50 paired draws (100 runs). Mean ΔE −0.054 %, bootstrap 95 % [−0.058, −0.050] for the Monte Carlo mean. All 50 draws had lower energy for the schedule and all were inside ±1 %. Median RMSE ratio 1.011; 0 tracking failures | Confirmed. The sign differs from F4, still far inside the margin |
| F8 | Speed profiles synthetic | `configs/cycles/profiles.yaml`, header "SYNTHETIC … not standard cycles, not measured traffic" | Confirmed |
| F9 | Constant motor efficiency; limits not reached; SoH known | `docs/model.md` §3; `configs/parameters.yaml` (`motor_inverter_efficiency` constant 0.874). In `data/processed/*/runs.csv`, `traction_limited_frac` = 0 and `friction_brake_Wh` = 0 in all 196 primary, S-B and S-C runs. The 100 S-D runs reached at most 0.028 % of time and 0.003 Wh | Confirmed, with a precision: in S-D the limits were briefly, negligibly active |
| F10 | No real-vehicle validation | `docs/model.md` "External validity: none"; C38 (the thesis's own declaration of no physical experiments) is CONSISTENT_WITH_RECORD | Confirmed |

The "precision" for F9 is a wording difference, not a change to the record.
`docs/evaluation-report.md` Phase 10 says the profiles "never activated" the limits, while
evidence row N01 says "essentially never". N01 is the precise statement; F9 states the
numbers behind it.

**Other recorded results used below [record]:**

- **S-B (γ sweep, 15 settings):** ΔE from −0.019 % to +0.040 %, all no practical
  difference (`artifacts/tables/gamma_sweep.csv`).
- **Energy split (S1, SoH 80 %):** road load 68.2 %, motor/inverter 22.0 %, gear 4.7 %,
  battery resistive 2.0 %, friction brake 0 %. Battery resistive share across S1 and S2:
  1.1–2.1 % (`artifacts/tables/energy_breakdown.csv`).
- **Run validity:** all 296 runs valid. Largest tracking RMSE 0.104 m/s; largest |error|
  0.686 m/s (R × 10 fixed gain).

### 3.2 Which conclusions rest on files outside the project

Several provenance remarks cite files that are **not in this project**. Their entries are
read here as written in this project's metadata; the files were not opened for this
review.

| External reference (as written in project files) | Cited in | What depends on it | Conclusion without it |
|---|---|---|---|
| `D:\EUREKA\AUDIT_REPORT.md` L28, L195, L196 | `evidence/claim_registry.yaml` C01, C02 (`provenance_notes`); `evidence/evidence_matrix.yaml` C01; `docs/evaluation-report.md` Summary | The remark that the ± intervals were "added as an editorial fix" | C01 and C02 stay CONTRADICTED on in-project evidence: the thesis body gives 10.2 % and 14 %, the pre-registered experiment gives +0.003 %, and the ageing model is underspecified. The ± intervals have no calculation in the project either way |
| `D:\EUREKA\scripts\render_kt01_figures.py` | claim registry C36, C40; evidence matrix C36, C40; evaluation report Summary | The statement that the thesis's result figures were drawn from random noise around hard-coded values | C40 stays withdrawn because no code or data in the project can regenerate those figures. The specific allegation of noise generation is **not verifiable here** |
| `D:\EUREKA\KT01_MicroEV\DATA_AND_COLAB_PROMPTS.md` | claim registry C07, C40 | Stated intent to add noise; VUC background | C07 stays CONTRADICTED on the thesis itself: L5996 says "not real measured data", against "derived from real-world measurements" |
| `KT01_FINAL_REPORT_v8.tex` (no path given) | claim registry C24 `definition` | The column layout of the transcribed A matrix, because the docx rendering is garbled | See below |

**C24 does not depend on the `.tex` file [thesis + review]:**

- The in-project thesis copy (`report.md` around L2640–2690) shows the state vector
  x = [v, i_batt, ω_m] and, in the v̇ row of A, the entry Gη/(M_tot r_w). Only the column
  layout is garbled.
- Gη/(M r_w) has units 1/(kg·m). Multiplying it by any state (m/s, A or rad/s) never gives
  m/s².
- So the v̇ row is dimensionally inconsistent wherever that entry sits, and F2 holds on
  in-project evidence alone.

**Status of all external references: EXTERNAL_UNVERIFIED.**

- They were recorded earlier in this project's history and could not be re-checked within
  the authorized project root.
- They cannot support a current conclusion unless their relevance is established through
  an authorized source. For example, the author confirms how the figures and intervals
  were produced, or deliberately supplies the files to the project with provenance.
- This review does not infer which project any of those files belongs to, and finds no
  evidence of project mixing.
- **For presentations, use the in-project wording:** "the figures and ± intervals cannot
  be reproduced from any code or data in the project." Do not repeat the noise-generation
  or editorial-fix statements to judges unless they have been verified that way.

## 4. Actual contribution and limitations

### 4.1 What is not a contribution

The following are standard techniques; implementing them, or running many tests on them,
is not a research contribution:

- LQR and DARE design, Bryson's rule and ZOH discretisation;
- gain scheduling;
- a Thevenin 1-RC battery and a point-mass longitudinal model;
- Monte Carlo robustness checks.

### 4.2 What can be claimed, in decreasing order of strength

1. **A pre-registered negative result for a specific proposed law [record].** The
   thesis's SoH-scheduled LQR gives no practical energy benefit over fixed-gain LQR in a
   documented model; a once-retuned fixed gain does better (N01–N03).
2. **A model-class explanation, with a bound [record + review].** Two properties of this
   model, together with the recorded energy split, explain the null result:
   - under torque control, SoH enters only through battery resistance, not through the
     controlled vehicle dynamics (`docs/model.md` §3);
   - for a fixed speed trace with constant efficiencies, road load, drivetrain and
     motor/inverter losses are set by the trace.

   The share a tracking controller can shape is the battery resistive loss, 1.1–2.1 %
   (N04). A 12.5 % saving would need removing about six times the entire resistive loss.
   This argument holds for this model class; it is not a theorem about real drives.
3. **A corrected, documented, reproducible model and pipeline [record].**
   - Model parameters carry stated provenance (20 unverified from the thesis, 11 assumed,
     2 standard; none measured).
   - The energy balance closes to ≤ 5.4 × 10⁻¹⁰.
   - Lineage, hashes and one-command regeneration are in place.

   This is good practice, not novelty.
4. **An audit of the original claims [record].** This includes a dimensional error in the
   original state-space model and internal numerical contradictions. It is a
   research-integrity contribution; it matters for the thesis but is not a scientific
   finding about EVs.

**Novelty status:** unknown. Whether item 1 or 2 is new relative to published work
requires the literature check in §9. Until then, describe them as findings of this study,
not as first-of-their-kind.

### 4.3 Is the comparison fair and technically sound? (Question 3)

**In favour [record]:**

- Hypotheses, metrics, decision margin and tuning were fixed in a commit before any plant
  or controller code existed.
- Both controllers share the implementation, limits, anti-windup and friction-brake
  logic, and run on identical plants, profiles and noise realisations.
- Tuning used a separate profile (P-TUNE) and was accepted on the first attempt, so there
  was no tuning on evaluation data.
- A sanity control (SoH 100 %) produced bit-identical runs.
- No runs were excluded.
- Exact SoH knowledge favours the scheduled controller.

**Weaknesses [record + review]:**

- **The scheduled law is only partly defined by the thesis.**
  - γ_v and γ_u are not given, so γ = 1 was assumed and swept over 0–5.
  - α_v had to be moved from a "battery current" state to motor torque, and ΔA set to 0
    (deviations (a)–(c)).
  - The test therefore answers "does this law, mapped consistently, help?", not "does the
    author's intended controller help?".
- **No strong adaptive baseline was tested.** A controller whose cost explicitly includes
  SoH-dependent resistive loss (energy-aware LQR or MPC) is a fairer test of whether
  SoH-awareness *can* help. Its absence limits what the null result says about adaptation
  in general.
- **SoH only scales resistance, and is not varied in robustness.** The SoH→resistance law
  (k_r0 = 0.5, k_r1 = 0.3, so R0 is +15 % at SoH 70 %) is taken from the thesis as
  unverified and was not perturbed in S-D. A stronger resistance growth would raise the
  resistive share [review: probably still far below 12.5 %, untested].
- **The decision rule is energy-centred.** "No practical difference" is decided on |ΔE|
  alone. Three S-B settings had RMSE ratios of 1.11–1.19 and were still classified as no
  practical difference. That follows the pre-registered rule, but it should be stated when
  quoting S-B.
- **The best fixed gain is at the edge of the tested range** (R × 0.1). The optimum may lie
  beyond it, which can only strengthen H_C, not reverse it.
- **The S-D sign flip is unexplained.** Under parameter draws and measurement noise the
  schedule uses slightly *less* energy (−0.054 %), against +0.003 % without noise. The
  recorded hypothesis (less noise amplification at lower gains) was not tested. Both
  values are far inside the ±1 % margin.

**Verdict [review]:**

- **Sound** for the question as pre-registered.
- **Fair** in implementation.
- **Narrow** in what "adaptive" means.

## 5. What the negative result establishes, and what it does not

### 5.1 Establishes (within the model, profiles and parameter values used)

- **The thesis's scheduling law has no practical energy effect.** Differences were 0.000
  to +0.005 % without noise, all 15 γ settings were within ±0.04 %, and the robustness
  mean was −0.054 %. The largest of these is still about 18 times smaller than the ±1 %
  margin.
- **It slightly worsens tracking** (RMSE ratio up to 1.020), increasingly as SoH falls.
  This is because the law softens the controller as the battery ages.
- **Retuning a single fixed gain beats scheduling** on both SoH-averaged energy and
  tracking. In this model energy and tracking error fall *together* as R decreases, so
  there is no trade-off for scheduling to exploit (`fixed_family.csv`: the whole family
  spans 0.28 % in energy).
- **The claimed 12.5 % is unreachable by any controller tracking the same profile in this
  model class** (N04 and §4.2, item 2).

### 5.2 Does not establish (Question 5)

- Anything about real vehicles, a specific micro-EV model, Vietnamese traffic, or standard
  cycles (WLTC, NEDC, CLTC).
- That SoH-aware control is useless in general. Other designs (energy-aware cost, MPC,
  battery-limit-aware control) were not tested.
- Behaviour when torque, power, battery-current or voltage limits are active. That regime
  was not exercised, and it is where ageing most plausibly couples into control (§5.3).
- Anything about battery capacity fade or lifetime. No ageing model was run; C02 and C04
  are withdrawn, not tested.
- Statistical inference about a vehicle population. The parameter ranges are assumed, and
  no p-values are reported, correctly.
- Effects of SoH estimation error, grades, temperature, auxiliary loads or driveline
  compliance.

### 5.3 How each assumption limits the conclusions (Question 6)

| Assumption | How it constrains the conclusion |
|---|---|
| Synthetic profiles (S1 ≤ 50 km/h, 0.5–1.0 m/s²; S2 ≤ 25 km/h) | Mild demands keep every run in the unconstrained regime. Results cannot be quoted for standard or measured cycles, and do not show what happens in aggressive or hilly driving. |
| Assumed parameter ranges (uniform; about ±2 % to ±20 %, and 0.008–0.012 for rolling resistance; mostly from thesis text without sources) | The S-D interval is Monte Carlo precision over an assumption, not uncertainty about vehicles. The SoH→resistance coefficients were not varied. |
| Constant motor/inverter efficiency (0.874) | Energy becomes a function of the mechanical trajectory, hiding part-load efficiency differences. [review: for a single-gear drive following the same speed trace, the motor operating point (speed, torque) is largely set by the trace, so a measured map is expected to widen controller differences only modestly. This is an untested expectation; the record (N04) lists the efficiency map as a limitation that could enlarge the controllable share.] |
| Actuator limits not reached; constant V_oc; fixed P_max | Ageing cannot reduce available power in this model. In a real pack, higher resistance causes voltage sag and battery power derating, which would make SoH change the *constraints*. That is the most credible route by which SoH-aware control could matter, and it is untested. |
| SoH known exactly | Favours the scheduled controller, so this assumption cannot explain its failure to outperform. |
| No physical validation | Every number is a property of the model. |

## 6. Claims that must remain withdrawn (Question 7)

Taken from the `final_reporting_recommendation` and `disposition` fields in
`evidence/evidence_matrix.yaml` and `evidence/claim_registry.yaml` [record]. Nothing here
changes a status.

**Withdraw (must not appear in a revised thesis):**

- **Energy and ageing headline**
  - C01: 12.5 % ± 2.1 % energy improvement
  - C02: 15.3 % ± 2.8 % less capacity fade
  - C03: 95 → 85.3 Wh/km
  - C04: fade 2.3 % per 1000 cycles
  - C05: SEI model "calibrated for LFP"
  - C06: ageing model "validated against experimental data"
  - C36: capacity-fade figure
- **Drive cycle and statistics**
  - C08: VUC statistics
  - C10–C12: Monte Carlo counts, sample bounds and success rates
  - C13: Bonferroni significance
  - C14: normality and LHS power
  - C15: Morris ranking
  - C16: all worst cases pass
- **Safety and hardware**
  - C17: 94 % diagnostic coverage
  - C18: ASIL target
  - C20: SIL/PIL
  - C21: field-data reliability
- **Validation and software**
  - C22: within 5 % / 2 % of published or experimental data
  - C23: MATLAB/Simulink and version-controlled scripts
- **Model**
  - C24: the original state-space model
  - C28: the printed gain table
- **Benchmarks and optimisation**
  - C30: benchmark ranking and regen efficiency
  - C31: NSGA-II knee point
- **Figures**
  - C40: the result figures presented as simulation output

C01, C03, C10, C12 and C16 are recorded as WITHDRAW_PENDING_RETEST. The pre-registered
retest of C01 has been done and contradicts it. Any further retest would be new,
separately pre-registered work.

**Relabel, do not present as stated:**

- C07: the VUC is assumed or synthetic, not measured.
- C32–C34: parameters are unverified or assumed, not "validated" or "wind tunnel".
- C19: hardware becomes future work.

**Revise:**

- C09: cycle table.
- C25, C26: restate for the documented model, using frozen-time stability.
- C27: Bryson weights.
- C35: Monte Carlo distributions.

**Keep, after checking the citation:** C37 (Huria 2018 reference) and C38 (no physical
experiments).

**Out of scope:** C29 (EKF accuracy) and C39 (life-cycle CO₂ and payback).

## 7. Claims supported only by simulation (Question 8)

**SIMULATION_SUPPORTED, with their stated conditions [record]:**

- **N01:** no practical energy difference; 0.4–2.0 % higher RMSE.
- **N02:** a single retuned fixed gain is better on both metrics (H_C).
- **N03:** robustness mean −0.054 % under assumed ranges.
- **N04:** resistive losses of 1.1–2.1 % bound the controllable share.

**IMPLEMENTED_NOT_VALIDATED (properties of the documented design model only):**

- **C25:** controllability, rank 3.
- **C26:** frozen-time closed-loop stability over SoH ∈ [0.5, 1] and γ ∈ [0, 10].

None of these is REQUIRES_PHYSICAL_VALIDATION-cleared. All are claims about the model.

## 8. Defensible wording of the main negative finding

> In a documented, dimensionally consistent simulation of a hypothetical 48 V micro-EV
> (flat road; synthetic urban speed profiles up to 50 km/h; battery state of health
> 70–100 %, assumed known), scheduling the LQR weights on battery health as proposed
> changed model-computed battery energy per kilometre by between 0.000 % and +0.005 %
> relative to a fixed-gain LQR, while increasing speed-tracking RMSE by 0.4–2.0 %. Under
> the pre-registered ±1 % margin this is no practical difference. A single fixed gain,
> retuned once, used less energy and tracked better when averaged over battery health. In
> this model, battery resistive losses, the only part of the energy a tracking controller
> can shape, were 1.1–2.1 % of the energy supplied. These are properties of the model;
> they have not been validated on a vehicle.

**Shorter form:**

> Battery-health scheduling of LQR weights gave no practical energy benefit in our
> pre-registered simulation (+0.003 % at 80 % SoH); a retuned fixed gain did better.

**Avoid these phrasings:**

- "adaptive LQR is ineffective" (too general);
- "proved" (simulation only);
- "first study to show" (novelty not checked);
- any percentage without its conditions.

## 9. Literature needed to judge novelty (not yet consulted)

The project contains no literature review, and this review added none.

**Questions to answer before claiming novelty:**

- **LQ1.** Which published studies schedule or adapt LQR (or MPC) speed or traction
  control on battery SoH or ageing in EVs? What energy effect do they report, with which
  model, cycle and validation level (simulation, HIL, vehicle)?
- **LQ2.** For EVs following a fixed speed trace, what share of energy have published
  studies found to be controller-addressable? How does this compare with eco-driving or
  speed-planning approaches that change the trace? What battery I²R share is reported for
  small EVs on standard cycles?
- **LQ3.** What internal-resistance growth versus SoH has been measured for LFP cells,
  to set a defensible range for k_r0 and k_r1?
- **LQ4.** How do SoH-dependent battery power and current limits (derating) affect
  vehicle-level control? This is the regime left untested here.

**Source requirements:**

- **Acceptable sources:** peer-reviewed journal or conference papers, official
  standards, or measured datasets with documented provenance.
  - Journals such as IEEE Transactions on Vehicular Technology, Transportation
    Electrification, or Control Systems Technology; Applied Energy; Journal of Power
    Sources; Energy.
  - Standards such as UN GTR No. 15 / WLTP and UNECE Regulations 83 and 101.
- **What to record:** for each source, the full citation and DOI, model fidelity, test
  cycle, validation level and the exact number quoted.
- **Keep separate:** prior art goes in its own section of the thesis, never mixed with
  this project's simulation results.
- **Not acceptable:** other local research folders.

## 10. Likely judge questions and evidence-based answer outlines

**Q1. Why did the adaptive method not outperform the fixed controller? (Question 10)**

- In a torque-controlled drive, ageing raises battery resistance, but it does not change
  the vehicle dynamics the LQR controls (`docs/model.md` §3). At any given SoH, the
  "adaptive" controller is just a fixed LQR with different weights.
- Following the same speed profile, energy is mostly fixed by the profile: road load
  68 %, motor/inverter 22 %, gear 5 % (S1, SoH 80 %). Only battery resistive loss
  (1.1–2.1 %) depends on how current is shaped.
- The proposed law softens the controller as SoH falls. In this model that slightly
  raises tracking error and energy (+0.003 %).
- One well-chosen fixed gain was better on both metrics. The gain, if any, comes from
  *tuning*, not from *adaptation*.
- Where adaptation might matter (battery-power derating, active limits) is untested; that
  is the next study.

**Q2. Isn't the null result built into your model?**

- Partly, and that is the finding.
- The model uses standard physics for a torque-controlled drive. Its structure was fixed
  and pre-registered before any results existed.
- The result says the claimed benefit cannot come from this mechanism. It does not rule
  out other mechanisms (limits, voltage sag), which are named as untested.

**Q3. Why trust a simulator with unverified parameters?**

- Trust it only for what was verified:
  - 152 gate tests against independent references;
  - energy closure ≤ 5.4 × 10⁻¹⁰;
  - a bit-identical sanity control.
- Parameters are labelled unverified or assumed. Absolute Wh/km is not claimed to match
  any vehicle; only the paired *difference* is the outcome.

**Q4. Why not WLTC/NEDC or real Hanoi data?**

- The official tables could not be retrieved, and a reconstruction from memory failed
  its ±1 % acceptance check (`protocol/preregistration.md` §6).
- No measured Hanoi time series exists in the project (C07, C08).
- The pipeline accepts sourced cycle files without code changes.

**Q5. LQR is textbook. What is your contribution?**

- A pre-registered, reproducible test of a specific proposed benefit, which turned out
  negative.
- An explanation that bounds what any tracking controller can save in this model class.
- Not a new controller.

**Q6. Your earlier draft claimed 12.5 %. What happened?**

- Those numbers could not be reproduced from any code or data. The thesis's own body
  contradicts them (it implies 10.2 %), and the original model had a dimensional error.
- They were withdrawn and replaced by the pre-registered result.
- *State this openly. Do not cite the external-file provenance remarks (§3.2) unless
  they have been verified.*

**Q7. Why ±1 %? Why no p-values?**

- The ±1 % margin was fixed in advance, as the resolution at which a model with constant
  efficiencies can rank energy use.
- The simulations are deterministic given their inputs, so significance tests would
  describe the random-number generator, not vehicles.

**Q8. Your best fixed gain is at the edge of the range. Did you stop too early?**

- The range was pre-registered and not extended after seeing results.
- Extending it could only make the fixed gain look better, so H_C would still hold.

**Q9. Why does the robustness result have the opposite sign?**

- With measurement noise and perturbed plants, the schedule is −0.054 %, against +0.003 %
  without noise.
- Both are far inside the margin: the larger, 0.054 %, is about 18 times smaller than 1 %.
- A plausible cause (less noise amplification at lower gain) is recorded but untested.

**Q10. Would an efficiency map, MPC or a real ageing model change the answer?**

- Possibly. Each is listed as a limitation.
- A measured efficiency map could widen controller differences somewhat. [review: it is
  probably modest, since the speed trace fixes the operating point.]
- An energy-aware MPC or LQR is a stronger adaptive candidate that was not tested.
- Ageing effects on capacity were not modelled at all.

**Q11. Is it safe? What about ASIL?**

- No safety analysis was performed: no item definition, HARA or FMEDA.
- Stability and tracking-failure checks are controller-design checks, not ISO 26262
  evidence. The ASIL claims are withdrawn (C17, C18).

**Q12. Who did the work, and how?**

- Disclose the use of an AI research assistant as the competition rules require.
- Be ready to explain every step: the model, the pre-registration, the decision rule and
  the energy decomposition.
- Point to the commit history and the regeneration command (`docs/lineage.md`).

## 11. Gaps that block stronger conclusions

1. **Constrained regime untested.** No run had active torque or power limits beyond
   0.03 % of time; there is no battery power derating or voltage sag (V_oc constant).
2. **No strong adaptive baseline**, such as an energy-aware LQR or MPC with SoH-dependent
   loss in the cost.
3. **No measured or standard driving data.**
4. **No measured component data**: motor efficiency map, resistance-versus-SoH law
   (k_r0, k_r1), vehicle parameters.
5. **No literature positioning** (§9), so novelty is unknown.
6. **No independent human replication** of the pipeline or of this review.
7. **No physical validation** (HIL, dynamometer or vehicle). This is required before any
   real-world statement.
8. **External provenance remarks unverified** (§3.2). This does not affect any status,
   but it limits what may be said about how the original figures and intervals were
   made.
9. **No ageing model.** Nothing can be said about capacity fade.

## 12. Prioritised next steps (none started)

1. **Revise the thesis around the evidence.** This is author work and needs no new
   computation.
   - Remove every withdrawn claim (§6) and all non-reproducible figures.
   - Present the null result with its conditions (§8 and the abstract below).
   - State the simulation-only status and disclose the AI assistance.
2. **Answer LQ1–LQ4 from peer-reviewed sources** before using words such as "novel" or
   "first". Keep prior art separate from project results.
3. **Independent replication.** A supervisor or peer runs `scripts/setup.ps1`, then
   `scripts/verify.ps1` and `scripts/reproduce_all.ps1`, from the repository, and checks
   `evidence/artifact_hashes.json`.
4. **New pre-registered study for the constrained regime.** This would be a new protocol
   entry and new commits, leaving the existing records untouched.
   - Model changes: V_oc(SoC), voltage sag, a battery power and current limit that
     tightens with SoH, and k_r0/k_r1 ranges from LQ3.
   - Profiles: aggressive and graded ones that saturate the limits.
   - A third controller: an energy-aware LQR or MPC with SoH-dependent loss in its cost.
5. **Sourced standard cycles**, using official WLTC/NEDC tables with recorded provenance,
   and measured traffic traces if available.
6. **A measured motor/inverter efficiency map** with provenance.
7. **Physical validation** (HIL or dynamometer). This is outside the current scope, and is
   the only route to claims about real vehicles.

## 13. Potential abstract consistent with the evidence

> Battery ageing increases internal resistance, and scheduling a vehicle speed
> controller on battery state of health (SoH) has been proposed as a way to reduce
> energy use in ageing electric vehicles. We tested one such proposal—an LQR whose
> weights are scheduled on SoH—against a fixed-gain LQR on a documented, dimensionally
> consistent longitudinal model of a hypothetical 48 V micro-EV with an SoH-dependent
> Thevenin battery. Hypotheses, metrics, tuning and a ±1 % decision margin were
> pre-registered before implementation. On synthetic urban speed profiles (up to
> 50 km/h, flat road, SoH 70–100 % assumed known), scheduling changed model-computed
> battery energy per kilometre by 0.000 % to +0.005 %, with 0.4–2.0 % higher tracking
> error: no practical difference. A single fixed gain, retuned once, gave lower energy
> and lower tracking error averaged over SoH. Across 50 paired draws from assumed
> parameter ranges with velocity-measurement noise, the mean difference was −0.054 %, and
> every draw stayed within ±1 %. An energy decomposition explains the result: when the
> speed profile is fixed, energy is dominated by road load and drivetrain losses, and
> battery resistive loss—the part a tracking controller can shape—was 1.1–2.1 % of the
> energy supplied. Actuator and battery power limits were not reached, motor efficiency
> was constant, and no result has been validated on a vehicle. Whether SoH-aware control
> helps when ageing tightens power limits remains open.

## Appendix: files reviewed

Read inside `D:\EURÉKA 2026 - KT`, without modifying any of them:

- **Documents:** `docs/evaluation-report.md`, `protocol/preregistration.md`,
  `docs/model.md`, `docs/optional-components.md`, `docs/lineage.md`,
  `docs/migration-2026-10-23.md`, `README.md`; `docs/environment-inventory.md` (lines
  77–101 only).
- **Evidence:** `evidence/claim_registry.yaml` (all entries tabulated; C01, C02, C24, C25
  and C40 read in full), `evidence/evidence_matrix.yaml` (all rows tabulated; C01, C25,
  C26, C40 and N01–N04 read in full).
- **Configuration:** `configs/experiments.yaml`, `configs/parameters.yaml`,
  `configs/cycles/profiles.yaml` (header and P-TUNE).
- **Reports** (`artifacts/reports/`): `primary_results.json`, `robustness_results.json`,
  `robustness-sample-size.json`, `fixed_family_results.json`, `verification-gate.json`,
  `tuning-acceptance.json`, `report-consistency-checks.json` (check IDs and outcomes).
- **Tables** (`artifacts/tables/`): `primary_pairs.csv`, `gamma_sweep.csv`,
  `primary_metrics.csv`, `energy_breakdown.csv`, `fixed_family.csv`.
- **Processed data:** `data/processed/{primary,gamma_sweep,fixed_family,robustness}/runs.csv`
  (validity, limit, brake and tracking columns); `data/processed/report/report.md`
  (L2640–2700).
- **Code:** `src/eureka/audit/report_checks.py` (A-matrix check),
  `src/eureka/audit/dimensional.py` (header and symbol units).

Not opened: any file outside the project root, including the external references in
§3.2, and the thesis `.docx` itself.
