# Literature review: fixed vs SoH-scheduled LQR for EV longitudinal control

Date: 2026-10-24. Scope: the EV longitudinal-dynamics project in `D:\EURÉKA 2026 - KT` only.
This document answers the literature questions LQ1–LQ4 left open in
`docs/research-contribution-review.md` §9, and adds a fifth theme (reproducibility and
numerical verification). It adds no simulations, results or model changes. The research-gap
assessment and the next-step design are in `docs/research_gap_and_next_experiments.md`.

**Independence.** The review was compiled by an AI research assistant working in the
author's repository. The same assistant built the model and ran the earlier evaluations. No
person has checked the source readings below. Spot-check the full-text (FT) entries before
quoting them in the thesis.

---

## 1. Method and its limits

### 1.1 How sources were found and verified

- **Search (2026-10-24).** General web search, then targeted look-ups. Queries covered:
  - gain-scheduled LQR and EV longitudinal or speed control, with energy;
  - battery SoH-aware or degradation-aware EV energy management and cruise control;
  - LQR, SoH and gain scheduling for battery ageing;
  - state of power, internal resistance and SoH;
  - LFP resistance increase with ageing;
  - eco-driving optimal control;
  - EV torque or power derating with an aged battery;
  - LQR cost with an energy-loss term;
  - reproducibility in control research;
  - cross-validation of vehicle simulators.
- **Verification.** Every bibliographic record below was resolved against the Crossref REST
  API (`api.crossref.org`) by DOI or by title query. Titles, authors, venue, volume and
  pages come from Crossref, not from search snippets. Abstracts came from OpenAlex or
  Semantic Scholar. Full texts were read only where an open-access copy could be retrieved.
  The helper scripts are in this session's scratchpad, not in the project.
- **Access label, given for every source:**
  - **FT**: full text read in this session (the version is stated when it is a preprint or
    an accepted manuscript);
  - **AB**: abstract read;
  - **MD**: bibliographic metadata only. No substantive claim is drawn from an MD source;
    it is listed for orientation or follow-up only;
  - **SEC**: content known only through a secondary summary. These are flagged and not
    relied on.

### 1.2 Limits of this review

- **Not a systematic review.** Scopus, Web of Science and IEEE Xplore could not be queried
  directly.
  - Several publishers blocked automated retrieval: MDPI and ScienceDirect HTML, HAL,
    OSTI, and the TUM repository.
  - Paywalled full texts (Elsevier, IEEE, ASME, Springer) were not read.
- **Absence of evidence is not evidence of absence.** No paper was found that schedules
  LQR *weights* on battery SoH for EV speed tracking. That is the result of the searches
  listed above, not proof that no such paper exists. Read §8 with this in mind.
- **Search-engine summaries were used only to locate papers.** Every number quoted below
  comes from an FT or AB source unless it is labelled SEC.

---

## 2. Summary of what the literature shows

1. **Energy savings in EV longitudinal control come mainly from freedom to change the speed
   trajectory**: eco-driving, car-following spacing, or arrival-time slack.
   - Han et al. [Han2019] formulate eco-driving as optimal control and find that for EVs
     energy use depends quadratically on the control input.
   - Hattori et al. [Hattori2020] put the energy loss into an LQR cost. They state that a
     standard cycle such as JC08 cannot be used for evaluation, "because these methods
     change the velocity trajectory" (FT).
   - Every degradation-aware BEV motion controller found [Pan2023; Jia2022; Zhang2022;
     Shao2019; Wang2024] optimises or adapts the speed or spacing trajectory.

   In this thesis the trajectory is fixed by the reference profile.
2. **In the literature, battery health enters vehicle control mostly as an objective term,
   not through physical constraints.** The term is a capacity-fade cost on Ah throughput,
   C-rate, SoC or DoD:
   - in HEV/PHEV energy management [Serrao2011; Ebbesen2012; Moura2013; Xie2019;
     DePascali2020; Anselma2021];
   - in BEV speed control [Pan2023; Jia2022; Zhang2022; Wang2024].

   One study adds regenerative-braking limits to an ageing-aware speed controller
   [Shao2019, AB]. A 2026 systematic review of 60 Eco-ACC studies found that "fewer than
   10%" consider SoH or thermal effects [Mahdy2026, FT].
3. **SoH reduces available battery power through resistance growth and a voltage floor.**
   - The pulse-power capability depends on impedance, which depends on SoC, temperature,
     current and history [Waag2013, SEC abstract].
   - Pack power estimation must respect voltage, current and power limits [Plett2004, AB].
   - In a degradation-aware electro-thermal simulation, small packs (< 40 kWh) reached
     their end of life through minimum-voltage power constraints before capacity
     constraints [Etxandi2024, FT].

   The micro-EV pack in this thesis is nominally 48 V × 100 Ah ≈ 4.8 kWh, far below that
   threshold.
4. **No study compares a fixed LQR with an SoH-scheduled LQR on a fixed speed trace.** That
   is the result of the searches above. The closest comparison is Pan et al. [Pan2023, FT]:
   - it compares a fixed-weight, degradation-aware MPC ("MPC2") with a fuzzily
     weight-adapted MPC ("AMPC");
   - it reports the fixed-weight controller better at medium and low speeds (NEDC);
   - on WLTC the two differ in capacity loss in the fourth significant digit.

   Most of their gains over PID and SMC come from the controller class, not from
   adaptation. This agrees in direction with H_C in this project, but on a different
   problem.
5. **Reproducibility is weak in control research, and two simulators agreeing is not
   validation.**
   - Only 2.6 % of CDC 2021 papers had code [CDC2023ws, grey literature].
   - IEEE Control Systems Magazine called for a reproducibility challenge in 2018 [How2018,
     FT].
   - More than 73 % of Eco-ACC studies validate in simulation only, and 10 % with
     real-world experiments [Mahdy2026].
   - The verification and validation literature separates *verification* (is the model
     solved correctly) from *validation* (is it the right model) [Roache1997; Roache2002].
   - No peer-reviewed study was found that cross-checks the same EV controller study in two
     independent simulators (Python and Modelica, or similar).

---

## 3. Theme 1: Energy-aware and gain-scheduled LQR in EV longitudinal control

**Gain-scheduling theory.**

- Linearisation-based scheduling designs controllers at frozen operating points of a
  scheduling variable, then interpolates between them. It is motivated by plant dynamics
  that vary with that variable [Rugh2000, AB; Leith2000, AB].
- Classical practice is "limited to slow variations in the scheduling variable"
  [Shamma1992, AB]. SoH varies over months, so the slow-variation hazard does not arise
  here, and frozen-time analysis is appropriate. This is review reasoning.
- The theory also implies a precondition: scheduling compensates a *plant* change. In this
  project's plant the controlled dynamics, from torque command to speed, do not depend on
  SoH (`docs/model.md` §3). The scheduling has nothing to compensate. Analysis is in
  `research_gap_and_next_experiments.md` §4.

**Physically motivated scheduling in vehicle speed control.**

- Tran et al. [Tran2022, AB] design an LMI-based polytopic LQR cruise controller. The
  scheduling parameters are functions of vehicle mass and speed, both of which enter the
  longitudinal dynamics.
- Vahidi et al. [Vahidi2005, AB] estimate mass and road grade online by recursive least
  squares. Mass was estimated "within 5 %" in experiments, given persistent excitation.
- In both cases the adapted quantity is a **plant parameter that changes the controlled
  dynamics**. Battery SoH is not such a parameter in a torque-controlled drive.

**Energy-aware LQ designs.**

- **[Hattori2020, FT]** LQR with energy loss in the cost:
  - the loss is motor copper loss plus driving resistance; iron loss and battery losses
    are not included;
  - an approximate LPV model of vehicle and motor leaves one tuning parameter;
  - the vehicle is the in-wheel-motor research car FPEV2-Kanon;
  - the controller runs at a 10 kHz sampling rate;
  - it was compared with DP and with an LTI variant in simulation, on a chassis
    dynamometer bench and in field tests.

  Results:
  - in simulation (30 km/h to stop in 40 m), DP, LTI and LPV all regenerate more than 3 %
    more than constant-acceleration control;
  - the field-test regenerated energies (Fig. 16 caption, labels and units as printed) are
    "DP: 21.55 ± 0.16, LTI: 19.54 ± 0.08, LTI: 20.05 ± 0.13".

  This is the clearest precedent for an **energy-aware LQR**, the strong baseline missing
  from this project. It works by changing the deceleration trajectory.
- **[Pusztai2025, AB]** LTV-LQG tracking of a pre-optimised trajectory, with a Kalman
  filter estimating wind:
  - the nonlinear vehicle model deviates < 2 % in energy from measurements;
  - the controller uses up to 15.4 % less energy than a rule-based "human-like" switching
    controller in tailwind cases.

  The baseline is not a tuned LQ controller, so the 15.4 % reflects the baseline more than
  the LQ structure.
- **[Razi2021, FT, arXiv version]** Linear-quadratic tracking versus adaptive ECMS for HEV
  power split:
  - the performance is "a trade-off" between torque delivery, fuel and SoC tracking;
  - the adaptive ECMS depends strongly on its reference equivalence factor;
  - the LQT needs only a reference SoC.

  This is an example of a fixed-structure LQ controller being competitive with an adaptive
  one.
- **Eco-driving as optimal control.**
  - [Han2019, AB] For EVs, a "quadratic rather than linear dependence of energy use on
    control input" changes the optimal driving pattern.
  - [Sciarretta2015, AB] An IEEE CSM tutorial on eco-driving as optimal control.
  - [Han2018, AB] An analytical state-constrained eco-driving controller.
  - [Dib2014, MD] EV eco-driving energy management.

**Critical assessment.**

- The LQ literature with an energy objective puts **energy into the cost**: it penalises
  losses such as copper loss, proportional to current squared, together with road load.
- The thesis's law (report Eqs. 4.39–4.42) instead **rescales the existing Bryson weights
  with SoH**. No loss term is added, and no optimality argument links SoH to those weights.
- No source was found that motivates the specific direction of that law: softening the
  torque-state weight and raising R as SoH falls.

---

## 4. Theme 2: Fixed vs adaptive or gain-scheduled comparisons

- **[Pan2023, FT] Fixed-weight versus adapted-weight MPC, both degradation-aware.** This is
  the closest analogue to this project's H_C.
  - At SoH_ini = 1 on WLTC (Table 7), capacity loss is:
    - PID 3.8063, SMC 3.6463 and MPC1 (degradation-unaware) 3.1877;
    - MPC2 (fixed weights) 3.0822 and AMPC (fuzzy-adapted weights) 3.0835;
    - final SoC is 0.6841 for MPC2 and 0.6846 for AMPC.
  - The authors: the AMPC reduced capacity attenuation by 18.99 %, 15.43 %, 3.27 % and
    −0.04 % relative to PID, SMC, MPC1 and MPC2. That is, it was **slightly worse than the
    fixed-weight MPC2**.
  - At SoH_ini = 0.9 (Table 8), capacity loss is 3.0984 for MPC2 and 3.0967 for AMPC.
  - On NEDC, "the MPC2 controller has advantages in life optimization and energy
    consumption as most of the NEDC working conditions are medium- and low-speed".
  - **Internal inconsistency.** In the text extraction, Table 9 (UDDS) and Table 10 (NEDC)
    report identical capacity-loss values: PID 1.9921, SMC 1.8604, MPC1 1.8418,
    MPC2 1.7978 and AMPC 1.7940. Table 10 therefore favours AMPC by about 0.2 %, which
    contradicts the NEDC sentence above. Check against the PDF before citing either
    number.
  - The large improvements come from MPC versus PID or SMC (controller class), not from
    adapting the weights.
  - Limitations:
    - the result is simulation, plus HIL used only to show real-time feasibility; HIL
      capacity loss differed from model-in-the-loop by 0.688 in the paper's units;
    - capacity loss is evaluated with the same semi-empirical model the controller
      optimises;
    - the following vehicle has spacing freedom.
- **[Hattori2020, FT]** The LPV-scheduled LQR regenerates more than the LTI LQR in
  simulation and in the field (see §3). Here the scheduling variable (speed) changes the
  linearised plant, which is the situation gain-scheduling theory addresses.
- **[Razi2021, FT]** The fixed-structure LQT is competitive with adaptive ECMS (see §3).
- **[Mahdy2026, FT] Systematic review (PRISMA) of 60 Eco-ACC studies, 2021–2025.**
  - Methods: MPC 41.7 %, RL 33.3 %, hybrid MPC–AI 16.7 %.
  - Validation: HIL 16.7 %, real-world 10.0 %.
  - "fewer than 10%" consider SoH or thermal effects.
  - "around 70%" focus only on short-term energy.

**Assessment.**

- The literature has fixed-versus-adaptive comparisons in which the adaptation tracks a
  plant change (speed, mass) or an objective weighting (Pan2023).
- In Pan2023, which has the most similar comparison, adapted weights did not beat a
  well-chosen fixed weighting in all regimes, and differences were in the third or fourth
  significant digit of the degradation metric.
- This project's finding that a single retuned fixed gain beats the SoH schedule (N02) fits
  this pattern. It is a bounded result for one law and one model, not a general statement
  about adaptive LQR.

---

## 5. Theme 3: SoH-aware vehicle control and energy management

### 5.1 HEV and PHEV energy management (the established core)

- **Control degree of freedom.** The supervisory controller chooses the engine/battery power
  split. Battery wear enters the cost through:
  - a severity-factor map solved with Pontryagin's principle [Serrao2011, AB];
  - a control-oriented SoH model penalising instantaneous battery use [Ebbesen2012, AB];
  - electrochemical SEI and Ah-processed degradation models with stochastic DP
    [Moura2013, AB];
  - electrochemical degradation dynamics in a large NLP [DePascali2020, AB].
- **[Anselma2021, AB] Experimentally validated lifetime prediction.**
  - Cells were aged with profiles predicted by a multi-objective DP.
  - The resulting control approach allows "the battery pack may be downsized by 35% with no
    impact on battery lifetime and a fuel consumption increase of just 1.1%".
  - It is one of the few studies with **experimental ageing validation** of the lifetime
    prediction. The vehicle-level results remain simulation.
- **[Xie2019, AB] Ageing-aware MPC on a ~70 km city-bus route.** It lowered "total cost by
  1.65%, 1.29% and 1.38%" for 5, 10 and 15 s preview, compared with ageing-unaware MPC.
- **Relevance.** These studies establish that health-aware control is meaningful **when the
  controller has a real degree of freedom over how much battery power is used**. A
  single-source BEV following a fixed speed trace has no power split: the battery must
  supply whatever the trace demands, apart from resistive and controller-induced
  differences.

### 5.2 BEV speed control with battery degradation

| ID | Degree of freedom | Degradation model | Baseline | Reported benefit | Validation |
|---|---|---|---|---|---|
| Pan2023 | ACC spacing and speed | semi-empirical Q_loss(Ah, C-rate, T); R0 updated from capacity | PID, SMC, MPC1, MPC2 | see §4 | simulation; HIL real-time check |
| Jia2022 | speed trajectory (SQP-MPC) | "high-precision battery aging model" (AB) | baseline strategy; preceding vehicle | life +10.33 % (no traffic); ageing −33.02 % vs preceding vehicle | simulation |
| Zhang2022 | truck speed over terrain (ADMM-MPC) | Lam & Bauer capacity-fade rate on Ah processed (FT) | constant-speed cruise control at 85 km/h | energy −5.05 % (up to); life "more than 100%" | simulation |
| Zhang2023 | truck speed with topography and traffic | (MD only) | (MD only) | (not verified) | (MD) |
| Shao2019 | CAV speed and following | ageing plus regen limits (AB) | not stated in abstract | 9.1 % energy benefit (14.3 % with perfect prediction) | simulation |
| Wang2024 | speed through two signals (DP) | LFP Ah-throughput model from Wang2011 (FT) | "regular driving" | up to 49 % cost benefit | simulation plus field test of a simplified phone-app advisor; **preprint, not peer-reviewed** |

**Critical points.**

1. **Every benefit comes with trajectory freedom against a weak or non-optimised
   baseline:** cruise control, a preceding human-driven vehicle, or "regular driving".
2. **Circularity.** Lifetime gains are computed with the same empirical ageing model used
   inside the optimiser. That is a consistency check, not independent evidence.
3. **SoH as a plant change.** Only Pan2023 changes the plant with SoH: resistance R0 is
   updated from capacity through a linear capacity–resistance relation attributed to Xia
   et al.
4. **Validation.** None validates lifetime on hardware at the vehicle level.

### 5.3 What this means for the thesis

- The thesis's claims of "battery aging compensation" and "lifetime extension"
  (report.md L3, L609, L621, L673) would need what these papers have and the project
  lacks:
  - a degradation model inside the evaluation;
  - a controller degree of freedom that changes battery current;
  - and, for credibility, independent ageing validation [Anselma2021].
- The project ran no ageing model (C02 and C04 were withdrawn).

---

## 6. Theme 4: SoH-dependent battery capability limits

**Mechanism (supported).**

- **[Plett2004, AB]** Available pack power must be computed so that "the pack will not be
  damaged by over/under charge or voltage or by exceeding a design current or power limit".
  It is predicted with a dynamic cell model plus SoC.
- **[Farmann2016, MD]** Review of on-board state-of-available-power prediction (listed for
  follow-up).
- **[Waag2013, SEC]** Abstract seen only as summarised from the IDEAS/RePEc listing, so
  verify before quoting:
  - the power capability "is described by its impedance characteristic", which depends on
    SoC, temperature, current and history;
  - Kokam 40 Ah NMC cells were tested new and aged;
  - the high-efficiency SoC window narrows with significant ageing.
- **[Etxandi2024, FT] EV end of life by capacity, power or safety constraints.**
  - Model: degradation-aware 2RC electro-thermal model, with parameters from Seger et al.
    [Seger2022, MD] for a 2.1 Ah NMC+LMO cell.
  - **Small packs** (< 40 kWh) show power constraints (minimum voltage) **before** capacity
    constraints. Larger packs are capacity-limited.
  - On their SU50 cycle, the end-of-life SoH of small batteries ranged 79 %–56 %; on SH50,
    99 %–66 %.
  - Low temperature raises resistance and makes the voltage floor bind earlier.
  - The authors recommend "estimating the capacity fade and IR increase independently".
  - Limits: the chemistry differs from LFP; the work is simulation only; the cycles are
    synthetic.

**LFP resistance-growth data (candidate parameter sources).**

- **[Severson2019, FT, accepted manuscript]**
  - 124 commercial **A123 APR18650M1A** LFP/graphite cells, 1.1 Ah nominal and 3.3 V
    nominal, cycled at 30 °C under 72 fast-charging policies.
  - Discharge was 4C to 2.0 V. The voltage cut-offs (2.0 V and 3.6 V) "follow those
    recommended by the manufacturer".
  - **Internal resistance was measured every cycle**: the average of 10 pulses at ±3.6C,
    30 ms wide, at 80 % SoC during charge.
  - Cycle lives ranged from about 150 to 2,300 cycles.
  - The accepted manuscript gives the data location as "figshare repository at [DOI
    pending]". The final repository must be confirmed from the published version.
  - Caveats:
    - a 30 ms pulse resistance approximates the ohmic R0, not R1;
    - fast-charge ageing at 30 °C is not EV urban use;
    - 1.1 Ah high-power cells are not a 100 Ah pack.
- **[Naumann2020, AB; Naumann2018, MD]**
  - A commercial Sony/Murata LFP/graphite cell, from a 29-month study at 19 cycle-ageing
    test points.
  - A semi-empirical combined model of **capacity loss and resistance increase**, validated
    on two dynamic profiles. Errors were below 1 % for capacity loss and below 2 % for
    resistance increase.
  - "an unexpectedly strong, but partly reversible capacity loss" was seen with shallow
    cycles at medium SoC.
  - The cell model number and the fitted coefficients are in the full text, which was not
    accessed.
- **[Pan2023, FT]** Lishen 20 Ah LFP cell:
  - R0 is linked to capacity through R0,now = R0,EOL − (Q_now − Q_EOL)/(Q_new − Q_EOL) ·
    (R0,EOL − R0,new).
  - Table 2 appears to give R0,new = 0.0063 Ω and R0,EOL = 0.0107 Ω, a ratio of about 1.7
    at end of life. The extracted table layout is scrambled, so confirm these values
    against the PDF.
  - Their SoH is normalised between new and end-of-life capacity, not Q_now/Q_new, so it
    is not directly comparable with this project's SoH.
- **[Sarasketa2015; Sarasketa2014, MD]** LFP/graphite cycle and calendar ageing with
  dynamic validation (listed for follow-up).
- **[Wang2011, MD]** The widely used LFP cycle-life model is a capacity-fade model; no
  resistance claim is drawn from it.

**Cell model behind the thesis.**

- **[Huria2012, AB]** The parameter source cited by the thesis (report.md L750,
  "Assumption 5"). The abstract describes:
  - a 1RC equivalent circuit with dependence on SoC, current and temperature;
  - identified on "LiNi-CoMnO2 cathode and graphite-based anode" (NMC) cells;
  - voltage accuracy within 2 % on an independent drive cycle.

  It is **not an LFP source and not an ageing model**. See §9 for the citation errors.

**Context and standards.**

- **INL test manuals [INL2015; INL2017, AB]** define characterisation and life-test
  procedures, including one for 48 V systems.
- **UN GTR No. 22 [GTR22, SEC]** sets in-vehicle battery durability minimum-performance
  requirements. A secondary summary gives 80 % state of certified energy at 5 years or
  100,000 km and 70 % at 8 years or 160,000 km (passenger category). The official text was
  not retrieved; verify before citing.
- **Reviews** for background only: [Vetter2005, MD], [Barre2013, MD], and [Birkl2017, AB]
  on degradation modes and OCV-based diagnostics.

**What follows for this thesis (review reasoning).**

- The literature supports the *mechanism*: resistance rises with ageing, a voltage floor
  then caps current and power, and small packs are affected first.
- It does **not** supply a ready, sourced R0(SoH) law for a 48 V, 100 Ah LFP micro-EV pack.
  The values depend on the cell, temperature, protocol and SoH definition.
- The thesis's coefficients k_r0 = 0.5 and k_r1 = 0.3 have no traceable source (they are
  `report_unverified`). Their cited cell source is NMC.

---

## 7. Theme 5: Reproducibility, cross-simulator and numerical verification

**State of practice in control research.**

- **[How2018, FT]** The IEEE CSM editor:
  - reports the HSCC repeatability evaluation, in which authors submit a repeatability
    package and receive a rating;
  - quotes that computational results become "nonreproducible—even by the research group
    that originally produced them";
  - recommends a "Control Systems Reproducibility Challenge".
- **[CDC2023ws, web page, grey literature]** "only 2.6% of publications had code" at
  CDC 2021, against about 5 % at ICRA and over 60 % at NeurIPS.
- **[Mahdy2026, FT]** Reproducibility (availability of parameters, datasets, code) was a
  quality criterion. More than 73 % of studies were simulation-only.

**General guidance.**

- [Vandewalle2009, AB] and [Bjornson2019, AB] (signal processing): document code and data
  and make them available.
- [Sandve2013, AB] Ten rules for reproducible computational research.
- [Wilkinson2016, MD] FAIR data principles.
- [Nosek2018, AB] Preregistration separates prediction from postdiction. This is the
  rationale behind the project's `protocol/preregistration.md`.
- [Lakens2017, AB] An equivalence claim needs pre-specified equivalence bounds
  ("smallest effect size of interest") and a test such as TOST. This supports the project's
  position that its ±1 % *decision margin* is **not** an equivalence threshold
  (`verification/controller-crosscheck-integrity-review.md` §5).

**Verification versus validation.**

- [Roache1997, AB] reviews verification, validation and error estimation.
- [Roache2002, AB] "Verification is a purely mathematical exercise". The method of
  manufactured solutions with systematic refinement gives code verification "with a
  theorem-like quality".
- [Oberkampf2002, MD] V&V in CFD (report).
- The project's Python–Modelica agreement and its step and tolerance refinement are
  **solution and code verification**. They are not physical validation.

**Vehicle-simulation tools.**

- [Wipke1999, AB] ADVISOR combines backward- and forward-facing simulation. It is validated
  to within 0.7 % on acceleration time and 0.6 % on US06 energy for one vehicle, which
  shows what validation against measurement looks like.
- [Gao2007, AB] Survey of EV and HEV modelling tools; it notes numerical oscillations with
  power electronics.
- Solver documentation: [Hindmarsh2005, AB] SUNDIALS (CVODE and IDA, used by OpenModelica)
  and [Fritzson2020, AB] OpenModelica.

**Gap.**

- No peer-reviewed vehicle-control paper was found that ports a controller comparison to a
  second, independent simulator. None was found that reports the numerical error of the
  *paired difference* against the effect size, as this project's cross-check does.
- This is a small methodological contribution. It is not new verification methodology:
  step and tolerance refinement and cross-code comparison are standard [Roache1997].

---

## 8. Literature matrix

### 8.1 Bibliographic part

DOIs and metadata were verified on Crossref on 2026-10-24. Links are DOI resolvers unless an
open-access copy is given. Type: **P** primary research, **R** review or survey,
**T** tutorial or editorial, **S** standard, report or dataset, **G** grey literature,
**PP** preprint.

| ID | Authors | Year | Title | Venue | DOI / link | Type | Access |
|---|---|---|---|---|---|---|---|
| Hattori2020 | Hattori, Fujimoto, Hori, Takeda, Sato | 2020 | Simple Tuning and Low-Computational-Cost Controller for Enhancing Energy Efficiency of Autonomous-Driving Electric Vehicles | IEEJ J. Ind. Appl. 9(4):358–365 | [10.1541/ieejjia.9.358](https://doi.org/10.1541/ieejjia.9.358) | P | FT |
| Tran2022 | Tran, Pham, Sename, Gáspár | 2022 | Design of an LMI-based Polytopic LQR Cruise Controller for an Autonomous Vehicle towards Riding Comfort | Periodica Polytechnica Transp. Eng. 51(1):1–7 | [10.3311/pptr.20075](https://doi.org/10.3311/pptr.20075) | P | AB |
| Pusztai2025 | Pusztai, Luspay, Friedler | 2025 | LTV-LQG Control for an Energy Efficient Electric Vehicle | Vehicles 7(4):113 | [10.3390/vehicles7040113](https://doi.org/10.3390/vehicles7040113) | P | AB |
| Razi2021 | Razi, Murgovski, McKelvey, Wik | 2021 | Design and Comparative Analyses of Optimal Feedback Controllers for Hybrid Electric Vehicles | IEEE TVT 70(4):2979–2993 | [10.1109/TVT.2021.3062313](https://doi.org/10.1109/TVT.2021.3062313); [arXiv:2004.01921](https://arxiv.org/abs/2004.01921) | P | FT (arXiv) |
| Han2019 | Han, Vahidi, Sciarretta | 2019 | Fundamentals of energy efficient driving for combustion engine and electric vehicles: An optimal control perspective | Automatica 103:558–572 | [10.1016/j.automatica.2019.02.031](https://doi.org/10.1016/j.automatica.2019.02.031) | P | AB |
| Han2018 | Han, Sciarretta, Ojeda, De Nunzio, Thibault | 2018 | Safe- and Eco-Driving Control for Connected and Automated Electric Vehicles Using Analytical State-Constrained Optimal Solution | IEEE T-IV 3(2):163–172 | [10.1109/TIV.2018.2804162](https://doi.org/10.1109/TIV.2018.2804162) | P | AB |
| Sciarretta2015 | (authors not returned by Crossref; HAL record hal-01252197 blocked) | 2015 | Optimal Ecodriving Control: Energy-Efficient Driving of Road Vehicles as an Optimal Control Problem | IEEE Control Systems 35(5):71–90 | [10.1109/MCS.2015.2449688](https://doi.org/10.1109/MCS.2015.2449688) | T | AB; **authors UNRESOLVED** |
| Dib2014 | Dib, Chasse, Moulin, Sciarretta, Corde | 2014 | Optimal energy management for an electric vehicle in eco-driving applications | Control Eng. Practice 29:299–307 | [10.1016/j.conengprac.2014.01.005](https://doi.org/10.1016/j.conengprac.2014.01.005) | P | MD |
| Rugh2000 | Rugh, Shamma | 2000 | Research on gain scheduling | Automatica 36(10):1401–1425 | [10.1016/S0005-1098(00)00058-3](https://doi.org/10.1016/S0005-1098(00)00058-3) | R | AB |
| Leith2000 | Leith, Leithead | 2000 | Survey of gain-scheduling analysis and design | Int. J. Control 73(11):1001–1025 | [10.1080/002071700411304](https://doi.org/10.1080/002071700411304) | R | AB |
| Shamma1992 | Shamma, Athans (authors from the ACC 1991 version; the CSM record lacks authors in Crossref) | 1992 | Gain scheduling: potential hazards and possible remedies | IEEE Control Systems 12(3):101–107 | [10.1109/37.165527](https://doi.org/10.1109/37.165527) | P | AB |
| Vahidi2005 | Vahidi, Stefanopoulou, Peng | 2005 | Recursive least squares with forgetting for online estimation of vehicle mass and road grade: theory and experiments | Vehicle System Dynamics 43(1):31–55 | [10.1080/00423110412331290446](https://doi.org/10.1080/00423110412331290446) | P | AB |
| Pan2023 | Pan, Zhang, Wang, Liu | 2023 | Adaptive Cruise Control Strategy for Electric Vehicles Considering Battery Degradation Characteristics | Applied Sciences 13(7):4553 | [10.3390/app13074553](https://doi.org/10.3390/app13074553) | P | FT |
| Jia2022 | Jia, Luo, Zhang | 2022 | Development of optimal speed trajectory control strategy for electric vehicles to suppress battery aging | Green Energy Intell. Transp. 1(2):100030 | [10.1016/j.geits.2022.100030](https://doi.org/10.1016/j.geits.2022.100030) | P | AB |
| Zhang2022 | Zhang, Qu, Tong | 2022 | Optimal Eco-Driving Control of Autonomous and Electric Trucks in Adaptation to Highway Topography: Energy Minimization and Battery Life Extension | IEEE TTE 8(2):2149–2163 | [10.1109/TTE.2022.3147214](https://doi.org/10.1109/TTE.2022.3147214); [arXiv:2009.04683](https://arxiv.org/abs/2009.04683) | P | FT (arXiv v3) |
| Zhang2023 | Zhang, Wang, Yu, Zheng | 2023 | Battery aging-minimal speed control of autonomous heavy-duty electric trucks in adaptation to highway topography and traffic | Sci. China Tech. Sci. 66(10):2942–2957 | [10.1007/s11431-022-2427-4](https://doi.org/10.1007/s11431-022-2427-4) | P | MD |
| Shao2019 | Shao, Sun | 2019 | Optimal Speed Control for a Connected and Autonomous Electric Vehicle Considering Battery Aging and Regenerative Braking Limits | ASME DSCC 2019, V001T08A005 | [10.1115/DSCC2019-9075](https://doi.org/10.1115/DSCC2019-9075) | P | AB |
| Wang2024 | Wang, Advani, Prasad | 2024 | Effects of eco-driving on energy consumption and battery degradation for electric vehicles at signalized intersections | arXiv preprint | [10.48550/arXiv.2410.01685](https://arxiv.org/abs/2410.01685) | PP | FT |
| Serrao2011 | Serrao, Onori, Sciarretta, Guezennec, Rizzoni | 2011 | Optimal energy management of hybrid electric vehicles including battery aging | Proc. ACC 2011, 2125–2130 | [10.1109/ACC.2011.5991576](https://doi.org/10.1109/ACC.2011.5991576) | P | AB |
| Ebbesen2012 | Ebbesen, Elbert, Guzzella | 2012 | Battery State-of-Health Perceptive Energy Management for Hybrid Electric Vehicles | IEEE TVT 61(7):2893–2900 | [10.1109/TVT.2012.2203836](https://doi.org/10.1109/TVT.2012.2203836) | P | AB |
| Moura2013 | Moura, Stein, Fathy | 2013 | Battery-Health Conscious Power Management in Plug-In Hybrid Electric Vehicles via Electrochemical Modeling and Stochastic Control | IEEE TCST 21(3):679–694 | [10.1109/TCST.2012.2189773](https://doi.org/10.1109/TCST.2012.2189773) | P | AB |
| Xie2019 | Xie, Hu, Qi, Tang, Lang, Xin, Brighton | 2019 | Model predictive energy management for plug-in hybrid electric vehicles considering optimal battery depth of discharge | Energy 173:667–678 | [10.1016/j.energy.2019.02.074](https://doi.org/10.1016/j.energy.2019.02.074) | P | AB |
| DePascali2020 | De Pascali, Biral, Onori | 2020 | Aging-Aware Optimal Energy Management Control for a Parallel Hybrid Vehicle Based on Electrochemical-Degradation Dynamics | IEEE TVT 69(10):10868–10878 | [10.1109/TVT.2020.3019241](https://doi.org/10.1109/TVT.2020.3019241) | P | AB |
| Anselma2021 | Anselma, Kollmeyer, Lempert, Zhao, Belingardi, Emadi | 2021 | Battery state-of-health sensitive energy management of hybrid electric vehicles: Lifetime prediction and ageing experimental validation | Applied Energy 285:116440 | [10.1016/j.apenergy.2021.116440](https://doi.org/10.1016/j.apenergy.2021.116440) | P | AB |
| Mahdy2026 | Mahdy, Abdellatif, El-Khatib | 2026 | A Systematic Review of Eco-Adaptive Cruise Control for Electric Vehicles: Control Strategies, Computational Challenges, and the Simulation-to-Reality Gap | Applied System Innovation 9(5):96 | [10.3390/asi9050096](https://doi.org/10.3390/asi9050096) | R | FT |
| Plett2004 | Plett | 2004 | High-Performance Battery-Pack Power Estimation Using a Dynamic Cell Model | IEEE TVT 53(5):1586–1593 | [10.1109/TVT.2004.832408](https://doi.org/10.1109/TVT.2004.832408) | P | AB |
| Farmann2016 | Farmann, Sauer | 2016 | A comprehensive review of on-board State-of-Available-Power prediction techniques for lithium-ion batteries in electric vehicles | J. Power Sources 329:123–137 | [10.1016/j.jpowsour.2016.08.031](https://doi.org/10.1016/j.jpowsour.2016.08.031) | R | MD |
| Waag2013 | Waag, Käbitz, Sauer | 2013 | Experimental investigation of the lithium-ion battery impedance characteristic at various conditions and aging states and its influence on the application | Applied Energy 102:885–897 | [10.1016/j.apenergy.2012.09.030](https://doi.org/10.1016/j.apenergy.2012.09.030) | P | SEC |
| Waag2014 | Waag, Fleischer, Sauer | 2014 | Critical review of the methods for monitoring of lithium-ion batteries in electric and hybrid vehicles | J. Power Sources 258:321–339 | [10.1016/j.jpowsour.2014.02.064](https://doi.org/10.1016/j.jpowsour.2014.02.064) | R | MD |
| Etxandi2024 | Etxandi-Santolaya, Canals Casals, Corchero | 2024 | Extending the electric vehicle battery first life: Performance beyond the current end of life threshold | Heliyon 10(4):e26066 | [10.1016/j.heliyon.2024.e26066](https://doi.org/10.1016/j.heliyon.2024.e26066) | P | FT (via Europe PMC) |
| Seger2022 | Seger, Coron, Thivel, Riu, Cugnet, Genies | 2022 | Open data model parameterization of a second-life Li-ion battery | J. Energy Storage 47:103546 | [10.1016/j.est.2021.103546](https://doi.org/10.1016/j.est.2021.103546) | P / S | MD |
| Severson2019 | Severson, Attia, Jin, Perkins, Jiang, Yang, Chen, Aykol, Herring, Fraggedakis, Bazant, Harris, Chueh, Braatz | 2019 | Data-driven prediction of battery cycle life before capacity degradation | Nature Energy 4(5):383–391 | [10.1038/s41560-019-0356-8](https://doi.org/10.1038/s41560-019-0356-8); [eScholarship](https://escholarship.org/uc/item/9532z8t0) | P / S | FT (accepted manuscript) |
| Naumann2020 | Naumann, Spingler, Jossen | 2020 | Analysis and modeling of cycle aging of a commercial LiFePO4/graphite cell | J. Power Sources 451:227666 | [10.1016/j.jpowsour.2019.227666](https://doi.org/10.1016/j.jpowsour.2019.227666) | P | AB |
| Naumann2018 | Naumann, Schimpe, Keil, Hesse, Jossen | 2018 | Analysis and modeling of calendar aging of a commercial LiFePO4/graphite cell | J. Energy Storage 17:153–169 | [10.1016/j.est.2018.01.019](https://doi.org/10.1016/j.est.2018.01.019) | P | MD |
| Sarasketa2015 | Sarasketa-Zabala, Gandiaga, Martinez-Laserna, Rodriguez-Martinez, Villarreal | 2015 | Cycle ageing analysis of a LiFePO4/graphite cell with dynamic model validations: Towards realistic lifetime predictions | J. Power Sources 275:573–587 | [10.1016/j.jpowsour.2014.10.153](https://doi.org/10.1016/j.jpowsour.2014.10.153) | P | MD |
| Sarasketa2014 | Sarasketa-Zabala, Gandiaga, Rodriguez-Martinez, Villarreal | 2014 | Calendar ageing analysis of a LiFePO4/graphite cell with dynamic model validations: Towards realistic lifetime predictions | J. Power Sources 272:45–57 | [10.1016/j.jpowsour.2014.08.051](https://doi.org/10.1016/j.jpowsour.2014.08.051) | P | MD |
| Wang2011 | Wang, Liu, Hicks-Garner, Sherman, Soukiazian, Verbrugge, Tataria, Musser, Finamore | 2011 | Cycle-life model for graphite-LiFePO4 cells | J. Power Sources 196(8):3942–3948 | [10.1016/j.jpowsour.2010.11.134](https://doi.org/10.1016/j.jpowsour.2010.11.134) | P | MD |
| Huria2012 | Huria, Ceraolo, Gazzarri, Jackey | 2012 | High fidelity electrical model with thermal dependence for characterization and simulation of high power lithium battery cells | 2012 IEEE Int. Electric Vehicle Conf. (IEVC), 1–8 | [10.1109/IEVC.2012.6183271](https://doi.org/10.1109/IEVC.2012.6183271) | P | AB |
| Vetter2005 | Vetter, Novák, Wagner, Veit, Möller, Besenhard, Winter, Wohlfahrt-Mehrens, Vogler, Hammouche | 2005 | Ageing mechanisms in lithium-ion batteries | J. Power Sources 147(1–2):269–281 | [10.1016/j.jpowsour.2005.01.006](https://doi.org/10.1016/j.jpowsour.2005.01.006) | R | MD |
| Barre2013 | Barré, Deguilhem, Grolleau, Gérard, Suard, Riu | 2013 | A review on lithium-ion battery ageing mechanisms and estimations for automotive applications | J. Power Sources 241:680–689 | [10.1016/j.jpowsour.2013.05.040](https://doi.org/10.1016/j.jpowsour.2013.05.040) | R | MD |
| Birkl2017 | Birkl, Roberts, McTurk, Bruce, Howey | 2017 | Degradation diagnostics for lithium ion cells | J. Power Sources 341:373–386 | [10.1016/j.jpowsour.2016.12.011](https://doi.org/10.1016/j.jpowsour.2016.12.011) | P | AB |
| INL2015 | Christophersen (ed.), Idaho National Laboratory | 2015 | Battery Test Manual For Electric Vehicles, Revision 3 | US DOE/INL report | [10.2172/1186745](https://doi.org/10.2172/1186745) | S | AB |
| INL2017 | Walker (ed.), Idaho National Laboratory | 2017 | Battery Test Manual For 48 Volt Mild Hybrid Electric Vehicles | US DOE/INL report | [10.2172/1389182](https://doi.org/10.2172/1389182) | S | AB |
| GTR22 | UNECE WP.29 | 2022 | UN GTR No. 22: In-vehicle battery durability for electrified vehicles | UN global technical regulation | official text not retrieved; secondary: [HORIBA summary](https://www.horiba.com/ind/mobility/applications/emissions-performance-and-durability/exhaust-emissions/gtr-no22) | S | SEC; **metadata UNRESOLVED** |
| How2018 | How | 2018 | Control Systems Reproducibility Challenge [From the Editor] | IEEE Control Systems 38(4):3–4 | [10.1109/MCS.2018.2829978](https://doi.org/10.1109/MCS.2018.2829978) | T | FT |
| CDC2023ws | Schoellig, How, Corke, Pappas, Hirche, et al. (organisers) | 2023 | Workshop on Benchmarking, Reproducibility, and Open-Source Code in Controls (CDC 2023) | workshop web page | [cdc2023.ieeecss.org/ws9](https://cdc2023.ieeecss.org/ws9/) | G | FT (web page) |
| Vandewalle2009 | Vandewalle, Kovacevic, Vetterli | 2009 | Reproducible research in signal processing | IEEE Signal Proc. Mag. 26(3):37–47 | [10.1109/MSP.2009.932122](https://doi.org/10.1109/MSP.2009.932122) | T | AB |
| Bjornson2019 | Björnson | 2019 | Reproducible Research: Best Practices and Potential Misuse [Perspectives] | IEEE Signal Proc. Mag. 36(3):106–123 | [10.1109/MSP.2019.2898421](https://doi.org/10.1109/MSP.2019.2898421) | T | AB |
| Sandve2013 | Sandve, Nekrutenko, Taylor, Hovig | 2013 | Ten Simple Rules for Reproducible Computational Research | PLoS Comput. Biol. 9(10):e1003285 | [10.1371/journal.pcbi.1003285](https://doi.org/10.1371/journal.pcbi.1003285) | T | AB |
| Wilkinson2016 | Wilkinson et al. | 2016 | The FAIR Guiding Principles for scientific data management and stewardship | Scientific Data 3:160018 | [10.1038/sdata.2016.18](https://doi.org/10.1038/sdata.2016.18) | T | MD |
| Nosek2018 | Nosek, Ebersole, DeHaven, Mellor | 2018 | The preregistration revolution | PNAS 115(11):2600–2606 | [10.1073/pnas.1708274114](https://doi.org/10.1073/pnas.1708274114) | T | AB |
| Lakens2017 | Lakens | 2017 | Equivalence Tests | Soc. Psychol. Personal. Sci. 8(4):355–362 | [10.1177/1948550617697177](https://doi.org/10.1177/1948550617697177) | T | AB |
| Roache1997 | Roache | 1997 | Quantification of uncertainty in computational fluid dynamics | Annu. Rev. Fluid Mech. 29:123–160 | [10.1146/annurev.fluid.29.1.123](https://doi.org/10.1146/annurev.fluid.29.1.123) | R | AB |
| Roache2002 | Roache | 2002 (online 2001) | Code Verification by the Method of Manufactured Solutions | J. Fluids Eng. 124(1):4–10 | [10.1115/1.1436090](https://doi.org/10.1115/1.1436090) | T | AB |
| Oberkampf2002 | Oberkampf, Trucano | 2002 | Verification and Validation in Computational Fluid Dynamics | Sandia report | [10.2172/793406](https://doi.org/10.2172/793406) | S | MD |
| Wipke1999 | Wipke, Cuddy, Burch | 1999 | ADVISOR 2.1: a user-friendly advanced powertrain simulation using a combined backward/forward approach | IEEE TVT 48(6):1751–1761 | [10.1109/25.806767](https://doi.org/10.1109/25.806767) | P | AB |
| Gao2007 | Gao, Mi, Emadi | 2007 | Modeling and Simulation of Electric and Hybrid Vehicles | Proc. IEEE 95(4):729–745 | [10.1109/JPROC.2006.890127](https://doi.org/10.1109/JPROC.2006.890127) | R | AB |
| Hindmarsh2005 | Hindmarsh, Brown, Grant, Lee, Serban, Shumaker, Woodward | 2005 | SUNDIALS: Suite of nonlinear and differential/algebraic equation solvers | ACM TOMS 31(3):363–396 | [10.1145/1089014.1089020](https://doi.org/10.1145/1089014.1089020) | P | AB |
| Fritzson2020 | Fritzson et al. | 2020 | The OpenModelica Integrated Environment for Modeling, Simulation, and Model-Based Development | Model. Identif. Control 41(4):241–295 | [10.4173/mic.2020.4.1](https://doi.org/10.4173/mic.2020.4.1) | T | AB |

### 8.2 Technical part (primary studies most relevant to the thesis)

Column key:
- **Fidelity**: vehicle and battery model fidelity.
- **Control and trigger**: control architecture and what triggers adaptation.
- **SoH: plant or controller?**: whether SoH changes the physical plant or only the
  controller or objective.
- **Constraints, energy and degradation**: constraints, energy model and degradation model.
- **Baselines, metrics**: baselines compared and evaluation metrics.
- **Valid.**: validation level (S simulation, HIL, bench, field).
- **Rel.**: relevance to this thesis.

| ID | Fidelity | Control and trigger | SoH: plant or controller? | Constraints, energy and degradation | Baselines, metrics | Valid. | Main finding | Limitations | Rel. |
|---|---|---|---|---|---|---|---|---|---|
| Hattori2020 | full vehicle model with tyre slip; 4 in-wheel PMSMs; motor equivalent circuit with copper and iron loss; no battery model | LQR on an approximate LPV model; re-linearised at each step on speed | no SoH | energy = motor input power; cost on copper loss plus driving resistance | DP; LTI-LQR; constant acceleration; regenerated energy | S, bench, field | LPV-LQR between DP and LTI; one tuning parameter; 10 kHz | one deceleration scenario; no battery; standard cycles unusable because the trajectory changes | template for an energy-aware LQR baseline; shows savings need trajectory freedom |
| Tran2022 | longitudinal model, parameter-dependent state space | polytopic (LMI) LQR scheduled on mass and speed | no SoH | comfort-oriented reference speed | not stated in abstract | S | scheduling on physical plant parameters | simulation only; no energy metric | contrast: scheduling on variables that change the dynamics |
| Pusztai2025 | structured nonlinear EV model (< 2 % energy deviation from measurement) | LTV-LQG along a pre-optimised trajectory; Kalman filter for wind | no SoH | time constraint; energy | rule-based switching ("human-like") controller | S | up to 15.4 % less energy in tailwind | weak baseline; simulation | energy-aware LQ tracking; baseline-quality caveat |
| Razi2021 | parallel-HEV powertrain; SoC constraints via barrier functions | LQT vs adaptive proportional ECMS; analytic sub-optimal solutions | no SoH | fuel, service brakes, SoC | controller-vs-controller trade-offs | S | trade-off; ECMS sensitive to equivalence factor; LQT needs only a SoC reference | HEV; simple noise model | fixed-structure LQ competitive with adaptive |
| Pan2023 | point-mass ACC; Rint battery, OCV(SoC) measured on a Lishen 20 Ah LFP cell; semi-empirical Q_loss(Ah, C-rate, T) | MPC1, MPC2 (fixed weights), AMPC (weights by fuzzy logic on speed and spacing); SoH updates the model | **both**: R0 updated from capacity (plant) and degradation cost (controller) | constraint set: SoC bounds, a ∈ [−5, 3] m/s², jerk ±2.5 m/s³, minimum gap 4 m; motor efficiency map; **no battery current, voltage or power limit** | PID, SMC, MPC1, MPC2; Q_loss, SoC; WLTC, UDDS, NEDC; SoH_ini 1 and 0.9 | S; HIL for real-time | on WLTC, adapted vs fixed weights differ ≤ 0.06 % in Q_loss; the text says fixed is better on NEDC | lifetime evaluated by the controller's own model; spacing freedom; HIL only for timing; Tables 9 and 10 identical (inconsistency) | **closest analogue to H_C**; shows how SoH can enter the plant |
| Jia2022 | vehicle speed, acceleration and SoC state space; "high-precision battery aging model" | SQP-solved MPC with an ageing objective | controller objective (from AB) | look-ahead; traffic | baseline strategy; preceding vehicle; battery ageing | S | life +10.33 %; ageing −33.02 % vs preceding vehicle | AB only; baseline is human or preceding vehicle | degradation objective with trajectory freedom |
| Zhang2022 | truck longitudinal model with grade; battery power via motor and gearbox efficiency; Lam & Bauer fade rate per Ah processed | ADMM-MPC with terrain and traffic preview | controller objective (energy); ageing evaluated afterwards | speed limits; topography | constant-speed CC at 85 km/h; energy, capacity fade | S | energy −5.05 %; life ">100%" | CC baseline; ageing evaluated with the same model class | energy–ageing link via Ah throughput; trajectory freedom |
| Shao2019 | CAV following a platoon; traffic-flow prediction | NLP-based MPC with ageing and **regen limits** | constraint (regen limit, e.g. no regen near full charge) plus ageing | 15 s horizon; 0.54 s average solve | prediction quality vs perfect prediction | S | 9.1 % energy benefit (14.3 % with perfect prediction) | AB only; baseline unclear | only BEV speed controller found with a battery-side regen constraint |
| Wang2024 | EV scaled from a Tesla Model 3; LFP Ah-throughput model (Wang2011) | DP eco-driving through signals | objective (energy plus degradation cost) | signal timing; acceleration bounds | regular driving | S plus field (phone-app advisor) | up to 49 % cost benefit | preprint; field test of a simplified rule-based version | degradation cost vs energy; LFP |
| Anselma2021 | HEV; empirical ageing model improved with temperature | multi-objective DP (offline) | objective | fuel, battery lifetime, pack size | ageing-unaware; pack sizes | S plus **cell ageing experiments** | 35 % downsizing at equal life, +1.1 % fuel | offline DP; HEV | example of independent ageing validation |
| Xie2019 | PHEV city bus; ageing model; optimal DoD | MPC tracking a reference SoC from an optimal DoD | objective (energy plus life-loss cost) | SoC bounds | ageing-unaware MPC, DP, PMP, rule-based | S (real-world cycles) | total cost −1.29 to −1.65 % | cost-weighted; PHEV | ageing-aware gains are small even with power-split freedom |
| Etxandi2024 | 2RC electro-thermal ECM, Seger2022 tables, 2.1 Ah NMC+LMO; capacity and IR degraded | no controller; EoL analysis | **plant capability** (voltage floor, capacity, temperature) | minimum voltage; capacity; temperature; 50 % SoH safety | battery sizes 16–100 kWh; two climates; four synthetic cycles | S | small packs power-limited first; EoL SoH 99–56 % depending on cycle | NMC+LMO; synthetic cycles | **evidence that SoH-driven power limits matter most in small packs** |
| Severson2019 | 124 A123 APR18650M1A LFP cells; measured capacity, IR, temperature | none (data-driven life prediction) | — | 2.0–3.6 V window; 4C discharge; 30 °C | — | lab data | IR measured per cycle; 150–2,300 cycle lives | fast-charge ageing; 1.1 Ah cell | **candidate source for an R0(SoH) curve of one LFP cell** |
| Naumann2020 | Sony/Murata LFP/graphite; 19 test points; 29 months | none | — | semi-empirical capacity-loss and resistance-increase model | two dynamic validation profiles | lab data | errors < 1 % (capacity), < 2 % (resistance) | coefficients not read here; stationary-storage focus | **candidate R0 growth model for LFP** |
| Huria2012 | 1RC ECM, SoC/current/T-dependent; **NMC** cells | none | — | — | independent drive cycle (2 % voltage accuracy) | lab data | ECM identification method | not LFP; no ageing | the thesis's cited source does not support its LFP claim (§9) |

---

## 9. Verification of the thesis's own citations

Checked against Crossref on 2026-10-24. Locations refer to `data/processed/report/report.md`,
the in-project copy of the thesis. The thesis itself was not modified.

| Thesis citation (as printed) | Finding | Status |
|---|---|---|
| Ref. 3: Huria, Ceraolo, Gazzarri, Jackey, IEEE Trans. Ind. Appl. 54(6):6514–6526, 2018 (L6006); "Huria 2018, J. Power Sources" (L5998) | The paper with this exact title and authors is **2012 IEEE IEVC, pp. 1–8, [10.1109/IEVC.2012.6183271](https://doi.org/10.1109/IEVC.2012.6183271)**. Its abstract describes **NMC/graphite** cells and a 1RC ECM with no ageing model. The two thesis citations disagree with each other and with Crossref. Assumption 5 (L750, "LFP … parameters identified from Huria et al.") and the "SEI growth theory" attribution (L5998) are **not supported by this source as abstracted**. | CORRECT the citation; WITHDRAW the LFP and SEI attributions |
| Ref. 6: Ramadass, Haran, White, Popov, J. Electrochem. Soc. 151(2):A196–A203, 2004 | Exists ([10.1149/1.1634273](https://doi.org/10.1149/1.1634273)). The author list omits P. M. Gomadam. | CORRECT the author list |
| Ref. 7: Qiao, Zhang, Wang, Liu, "LQR-based fuzzy logic controller for regenerative braking of electric vehicles", IETE J. Res. 70(2):1124–1136, 2023 | Not found by title or author query. A *different* paper, Saxena et al., "Design of LQR-based FLC for the Optimal Regenerative Braking Controlling of Solar PV-based Electric Vehicle System", IETE J. Res. 70(2):1923–1936 ([10.1080/03772063.2023.2171916](https://doi.org/10.1080/03772063.2023.2171916)), exists. The thesis's authors, title and pages do not match it. The "23.5 %" figure (L2328) is unverifiable. | UNRESOLVED: treat as unverifiable; remove unless the author supplies a DOI |
| Ref. 8: Wang, Li, Chen, Zhang, IET Intell. Transp. Syst. 18(3):456–469, 2024 | Not found by title or author query. | UNRESOLVED: remove unless a DOI is supplied |
| Ref. 9: Lin, Huang, Wu, Chen, Control Eng. Pract. 142:105789, 2024 | Not found. Article number 105789 in Control Engineering Practice resolves to an unrelated marine-vessel paper (vol. 143, [10.1016/j.conengprac.2023.105789](https://doi.org/10.1016/j.conengprac.2023.105789)). | UNRESOLVED: remove unless a DOI is supplied |
| Ref. 10: Smith, Wang, "Solid-electrolyte interphase in lithium-ion batteries: A molecular dynamics perspective", J. Power Sources 161(1):595–599, 2006 | Not found. J. Power Sources 161(1) contains Smith & Wang, "Solid-state diffusion limitations on pulse operation of a lithium ion cell for hybrid electric vehicles", pp. 628–639 ([10.1016/j.jpowsour.2006.03.050](https://doi.org/10.1016/j.jpowsour.2006.03.050)), a different paper. | UNRESOLVED: remove or replace |
| Table 6 (L2560–2584): 15 studies given only as "Author et al., year" with no titles | Cannot be identified or verified. The row "Huang et al. 2023, LQR, SoH-based, Aging compensation" would be the closest prior art if it exists; none was found in this review. | REMOVE, or replace with verified entries from §8 |

These are bibliographic findings only. They do not establish how the references were
produced. Do not speculate about that in the thesis.

---

## 10. Open items

- **Read the full texts** of Naumann2020, Waag2013, Farmann2016, Plett2004, Jia2022,
  Zhang2023 and Shao2019 through institutional access before quoting their numbers or
  coefficients.
- **Sciarretta2015** authors and **GTR22** official metadata are unresolved.
- **Severson2019:** confirm the final data repository and licence from the published
  version.
- **Pan2023:** confirm the Table 2 values (R0,new, R0,EOL, pack topology) from the PDF.
- **Coverage:** a database search (Scopus or IEEE Xplore) is needed before using "first" or
  "novel" in the thesis. Suggested strings:
  - ("state of health" OR SoH OR aging) AND (LQR OR "linear quadratic") AND (vehicle OR
    EV) AND (speed OR longitudinal OR cruise);
  - ("gain schedul*") AND ("state of health" OR "battery aging");
  - ("power limit" OR derating OR "state of power") AND ("speed control" OR "cruise
    control") AND electric vehicle.
