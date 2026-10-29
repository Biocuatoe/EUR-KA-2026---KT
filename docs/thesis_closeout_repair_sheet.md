# Thesis close-out repair sheet

Date: 2026-10-24. Scope: the thesis of the EV longitudinal-dynamics project in
`D:\EURÉKA 2026 - KT`.

**How to use.**

- This sheet lists exact, targeted repairs for the thesis DOCX. The DOCX was **not**
  edited.
- **Search strings** are short fragments chosen to survive DOCX formatting. Search the
  DOCX with each one.
- **Line numbers** refer to the in-project conversion `data/processed/report/report.md`.
  They locate the passage there; they are not DOCX page numbers.
- **Owner verification.** Items marked **[OWNER]** need the author's personal
  confirmation. Each has a conservative default that avoids a false claim if the
  confirmation is not available. All owner items are collected in §5.

**This sheet completes** the claim table of
`docs/final_contribution_and_thesis_revision_plan.md` §4 (R1–R14) for four items:

- §1: references 7–10 and Tables 6–7;
- §2: battery configuration;
- §3: publication status;
- §4: validation and replication wording.

---

## 1. References [7]–[10] and Tables 6–7

**Finding.**

- Exact-title and author queries against Crossref (2026-10-24,
  `docs/literature_review_soh_scheduled_lqr.md` §9) found **no reliable matching record**
  for references 7–10 as cited.
- This does not show that no similar work exists. It shows only that these
  author/year/title/venue combinations have no reliable provenance.
- They must not be kept in any form, including partial author/year mentions, unless the
  author supplies a DOI that resolves to the cited record **[OWNER, OV4]**.

| # | Search string | report.md | Current text (abridged) | Action |
|---|---|---|---|---|
| 1a | `Qiao et al.` | L2328, L2570, L2596 | "proposed an LQR-based fuzzy logic controller … 23.5% energy recovery improvement" | **Delete** the sentence, the table rows and the "23.5%" figure |
| 1b | `Wang et al. [8]` / `four-wheel-drive EVs` | L2330 | "… 18.2% improvement in energy recovery efficiency" | **Delete** |
| 1c | `Lin et al. [9]` / `explicit battery state constraints` | L2332 | "… 15.7% energy recovery improvement" | **Delete** |
| 1d | `Lqr-based fuzzy logic controller for regenerative braking` | L6014 (ref. 7) | Qiao, Zhang, Wang, Liu, *IETE J. Res.* 70(2):1124–1136, 2023 | **Delete** the reference |
| 1e | `Energy recovery strategy for four-wheel-drive` | L6016 (ref. 8) | Wang, Li, Chen, Zhang, *IET ITS* 18(3):456–469, 2024 | **Delete** |
| 1f | `Model predictive control for regenerative braking with battery state` | L6018 (ref. 9) | Lin, Huang, Wu, Chen, *Control Eng. Pract.* 142:105789, 2024. Article number 105789 resolves to an unrelated paper | **Delete** |
| 1g | `Solid-electrolyte interphase in lithium-ion batteries` | L6020 (ref. 10) | Smith & Wang, *J. Power Sources* 161(1):595–599, 2006 | **Delete**. Ref. 10 is also the only source for "Calendar aging coefficient γ0 = 3 × 10⁻³ Ah⁻¹ᐟ²" in Table 9 (the ageing-parameter table, around L3029). Table 9 belongs to the withdrawn ageing model (C05), so **remove Table 9** and every result that depends on it |
| 1h | `Comprehensive Literature Review: EV Powertrain` | Table 6, rows L2568–2584; caption L2586; intro L2566 "comparing 15 research papers" | 15 entries given only as "Author et al., year", e.g. "Huang et al. 2023, LQR, SoH-based, Aging compensation" | **Delete the whole table** and its introduction. The entries cannot be identified |
| 1i | `Research Gap Analysis: Comparison with Prior Work` | Table 7, L2592–2602; text L2588–2608 | Six unidentifiable rows, plus a "Proposed" row claiming "Real-time / Pareto / Explicit / 1000 cycles / t-test, ANOVA" | **Delete** the table and the paragraphs at L2588–2590 and L2604–2608. Every "Proposed" cell is withdrawn (C02, C04–C06, C10–C14, C31) |

**Replacement text** for L2326–2332, the regenerative-braking and related-work paragraph.

Only sources marked FT or AB in literature review §8 are used. Cite them with the DOIs
given there.

> Battery health has been incorporated into vehicle control mainly in hybrid-vehicle energy
> management, where battery wear is added to the cost of the engine/battery power split
> [Ebbesen et al. 2012; Moura et al. 2013; Anselma et al. 2021]. For battery-electric
> vehicles, degradation-aware speed and cruise controllers obtain energy or ageing benefits
> by changing the speed trajectory [Pan et al. 2023; Jia et al. 2022; Zhang et al. 2022]. An
> LQR with an energy-loss term in its cost has been evaluated in simulation, on a
> dynamometer bench and in field tests [Hattori et al. 2020]. Studies of battery power
> capability show that resistance growth and voltage limits reduce available power,
> particularly in small packs [Plett 2004; Etxandi-Santolaya et al. 2024]. In the reviewed
> literature we did not identify a study that schedules speed-tracking LQR weights on
> battery state of health while the speed profile is fixed. This review was not a
> systematic database search.

**Replacement for Table 6** ("Selected verified related work"). Optional; it replaces the
deleted table.

| Study (DOI) | Control | How battery health enters | Validation |
|---|---|---|---|
| Hattori et al. 2020, [10.1541/ieejjia.9.358](https://doi.org/10.1541/ieejjia.9.358) | LQR with energy-loss cost, LPV model | not at all (motor and road losses) | simulation, bench, field |
| Pan et al. 2023, [10.3390/app13074553](https://doi.org/10.3390/app13074553) | ACC: fixed-weight and adapted-weight MPC | resistance updated from capacity; degradation cost | simulation; HIL for real-time only |
| Jia et al. 2022, [10.1016/j.geits.2022.100030](https://doi.org/10.1016/j.geits.2022.100030) | MPC speed trajectory | ageing objective | simulation |
| Zhang et al. 2022, [10.1109/TTE.2022.3147214](https://doi.org/10.1109/TTE.2022.3147214) | ADMM-based MPC eco-driving | ageing evaluated via Ah throughput | simulation |
| Ebbesen et al. 2012, [10.1109/TVT.2012.2203836](https://doi.org/10.1109/TVT.2012.2203836) | HEV energy management | wear penalty in cost | simulation |
| Anselma et al. 2021, [10.1016/j.apenergy.2021.116440](https://doi.org/10.1016/j.apenergy.2021.116440) | HEV energy management (DP) | multi-objective lifetime cost | simulation plus cell ageing tests |
| Etxandi-Santolaya et al. 2024, [10.1016/j.heliyon.2024.e26066](https://doi.org/10.1016/j.heliyon.2024.e26066) | none (end-of-life analysis) | resistance growth, voltage floor | simulation |
| **This thesis** | fixed vs SoH-scheduled LQR, fixed speed profile | controller weights only; plant resistance and capacity, but no limits | simulation in two independent implementations; no physical validation |

**Table 7.** No replacement. The "this thesis" row above states the study's position
without a comparative superiority claim.

**Related references.**

- **Ref. 3, Huria.** Correct it to the 2012 IEVC record,
  [10.1109/IEVC.2012.6183271](https://doi.org/10.1109/IEVC.2012.6183271). Remove its use
  for LFP parameters (Assumption 5, L750; search `parameters identified from Huria`) and
  for the SEI ageing model (L5998; search `Huria 2018, J. Power Sources`). See C37 in
  `evidence/evidence_matrix_2026-10-24.yaml` (the original `evidence_matrix.yaml` is
  preserved unchanged).
- **Ref. 6, Ramadass et al.** It is cited only in Table 9. If Table 9 is removed, remove
  ref. 6 as well. If it is kept elsewhere, add the missing author P. M. Gomadam
  ([10.1149/1.1634273](https://doi.org/10.1149/1.1634273)).
  *[Corrected 2026-10-24: ref. 6 is also cited for the SEI capacity-loss law, Eq. 2.54
  (report.md L1938), not only in Table 9. Its abstract describes a first-principles
  side-reaction model and does not describe that law; see
  `docs/thesis_full_scientific_audit.md`, B-06 and C2-53.]*

## 2. Battery configuration consistency

**Project evidence** (`docs/battery-data-feasibility-audit.md` §4):

- **Simulation model:** a generic 48 V, 100 Ah pack with constant 48 V open-circuit voltage
  and pack resistances (`configs/parameters.yaml`: `assumed` or `report_unverified`). No
  cell, part number or series/parallel configuration is modelled.
- **Thesis BOM:** 16 × "3.2V/100Ah", supplier "CATL", with no part number.
  - If series-connected, the nominal sum is 16 × 3.2 V = **51.2 V**, not 48 V.
  - No document in the project validates the BOM pack as the simulated pack.

The model parameters and simulation results are **not** to be changed.

| # | Search string | report.md | Current | Replacement |
|---|---|---|---|---|
| 2a | `Battery Voltage (nom)` / `Battery Capacity` | Table 8, L2725–2727 | "48 V – Nominal voltage"; "100 Ah – Rated capacity"; "LFP" | Keep the values. Add a table note: "*Generic 48 V / 100 Ah reference battery model (constant open-circuit voltage, Thevenin 1-RC). The parameters are unverified or assumed and do not describe a specific cell or pack.*" |
| 2b | `3.2V/100Ah` | Table 40 (BOM), L6510 | "Battery Cells – 3.2V/100Ah – 16 – CATL" | Keep only as a cost item, with the note: "*Illustrative cost estimate. Cell part number not identified. The series/parallel configuration and its consistency with the 48 V simulation model have not been validated (16 × 3.2 V = 51.2 V nominal if series-connected).*" **[OWNER, OV1]** |
| 2c | `48V/100Ah` | Table 40, L6509 ("Battery Pack (LFP) 48V/100Ah – CATL/Faraday"); L2618 | pack label | As 2b: illustrative; not the validated simulated pack |
| 2d | `parameters identified from Huria` | L750 (Assumption 5) | LFP cells with parameters from Huria et al. | "*The battery is represented by a generic 48 V LFP-type Thevenin model whose parameters have no cell-specific source (see Limitations).*" |
| 2e | (Limitations section) | after L5998 | — | Add: "*Battery current, voltage and power limits that depend on state of health were not modelled. The cell-specific data needed to parameterise them (manufacturer, part number, datasheet, OCV and resistance against SoC, temperature and ageing) are unavailable for the stated CATL cell.*" |

**Conservative default if OV1 is not answered:** use the notes in 2a–2e as written. Do not
state a series count. Do not describe the BOM pack and the simulated pack as the same
design.

## 3. "Journal Paper 1 … (Under Review)"

**Evidence check (2026-10-24).**

- The project was searched for submission or review records (`submission`, `submitted`,
  `manuscript id`, `ScholarOne`, `under review`, `receipt`) in Markdown, text, YAML, JSON,
  CSV, e-mail and PDF files, excluding the environment folders.
- No submission receipt or manuscript-system record exists. The only hits are the thesis
  conversion itself and this project's review documents.

| # | Search string | report.md | Current | Action |
|---|---|---|---|---|
| 3a | `Journal Paper 1` / `(Under Review)` | L6588 | "Adaptive LQR Controller with Battery Aging Compensation for Micro-Electric Vehicles – IEEE Transactions on Transportation Electrification (Under Review)" | **[OWNER, OV2]** Keep "Under Review" **only** if the author holds a submission receipt or a manuscript-system record showing active review. Then cite the manuscript ID in the record, but not in the thesis if confidentiality requires. The title would still restate a withdrawn claim ("Battery Aging Compensation"). **Default:** remove the item. If the author confirms a manuscript is genuinely planned, replace it with: "*Planned manuscript (not submitted): Fixed versus state-of-health-scheduled LQR for EV speed tracking — a pre-registered simulation comparison with cross-implementation verification.*" |
| 3b | `Conference Paper 1` / `VPPC 2025`; `Conference Paper 2` / `ICSM 2025` | L6590, L6592 | NSGA-II Pareto optimisation; EKF SoH estimation | **[OWNER, OV3]** Same rule: keep only with an acceptance or publication record. Their topics rest on withdrawn or out-of-scope claims (C31 NSGA-II knee point withdrawn; C29 EKF out of scope). **Default:** remove |

No submission, acceptance or publication is asserted by this sheet.

## 4. Physical validation and independent human replication

Two separate things must not be confused:

| | Status | Evidence |
|---|---|---|
| **Two independently implemented simulation models** (Python RK4 and OpenModelica/DASSL) | **Performed.** The primary energy difference agrees (+0.0030138 % at S1, SoH 0.8), and the decision labels agree for all 8 profile × SoH pairs. One check failed and is unresolved: the S1 accumulated distance, effect on ΔE ≤ 4.3 × 10⁻⁹ percentage points | `verification/controller-crosscheck-runs/evaluation_summary.json`, `review_dE_bias_bound.json`, `verification/controller-crosscheck-results.csv` |
| **Independent human reproduction** (a different person runs `scripts/setup.ps1`, `scripts/verify.ps1` and `scripts/reproduce_all.ps1` and checks `evidence/artifact_hashes.json`) | **Not performed** | `docs/research-contribution-review.md` §11, item 6. Both implementations were produced by the same AI research assistant |
| **Physical validation** (vehicle, dynamometer, bench, HIL) | **Not performed** | C38 (CONSISTENT_WITH_RECORD); `docs/model.md` "External validity: none" |

| # | Search string | report.md | Current | Replacement |
|---|---|---|---|---|
| 4a | `validated through comprehensive testing` | L17 (abstract) | "The proposed framework is validated through comprehensive testing including Monte Carlo simulations …, statistical significance testing" | "*The comparison was tested in pre-registered simulations, including paired Monte Carlo runs over assumed parameter ranges, and reproduced in an independent OpenModelica implementation. No physical validation was performed.*" (C10–C14 are withdrawn) |
| 4b | `validated parameters from published datasheets` | L5980 | Declaration: "… using validated parameters from published datasheets and benchmark papers" | "*… using parameters taken from the thesis draft without primary sources, or assumed; none was measured or validated.*" Keep "No physical experiments were conducted." (C32, C38) |
| 4c | `The simulation parameters were validated against` | L5982 and the list after it | three "validated against" bullets | **Delete** |
| 4d | `validated against published data` | L4353–4355 | "within 5% of published values for WLTP …" | **Delete** (C22) |
| 4e | `validated against experimental data` | L3170 | ageing model "validated … within 5%" | **Delete** (C06) |
| 4f | `MATLAB/Simulink and Python` | L7 | simulations in MATLAB/Simulink and Python | "*Simulations were performed in Python, and the primary comparison was reproduced in OpenModelica.*" (C23) |
| 4g | `Real-world prototype validation will be conducted` | Limitations, L5992 | future-work statement | Keep as future work. Do not imply that it has been started |
| 4h | (new, Limitations) | — | — | "*The two implementations were written independently in Python and Modelica but by the same research workflow (an AI research assistant); no independent human reproduction of the pipeline has been performed.*" |

## 5. Owner-verification register

| ID | Item | What would confirm it | Conservative default if unconfirmed |
|---|---|---|---|
| OV1 | Identity and configuration of the battery cell in the BOM | Manufacturer, exact part number, applicable datasheet, intended series/parallel configuration | §2 notes as written. No series count; not the same design as the simulated pack |
| OV2 | "Journal Paper 1 … Under Review" | Submission receipt or manuscript-system record showing active review | Remove; or "Planned manuscript (not submitted)" with the bounded title, if a manuscript is genuinely planned |
| OV3 | Conference Papers 1 and 2 (VPPC 2025, ICSM 2025) | Acceptance letter or published-paper record | Remove |
| OV4 | References 7–10 | A DOI that resolves to each record exactly as cited | Remove (§1) |
| OV5 | Independent human reproduction | Name/role, date, commands and hash comparison, recorded in the project | State "not performed" |
| OV6 | Disclosure of AI assistance | The applicable competition or university rule | Disclose the assistant's role in modelling, analysis and review |
| OV7 | Corrected evidence exports | Cite the dated snapshot `evidence/exports/2026-10-24/` (source `evidence/evidence_matrix_2026-10-24.yaml`) with `docs/evidence-corrections-2026-10-24.md`. The original baseline is preserved and is not regenerated | The baseline `evidence_matrix.{csv,json}` keep the pre-correction C01, C37, N04 and C38 text by design. The default pipeline still reads the original YAML |

This sheet makes no assumption about the author's identity, the intended production
vehicle, the battery pack or any submission.
