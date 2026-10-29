# Literature gap assessment (Phase 2)

**Date:** 2026-10-25. **Files:** `literature_search_log.csv` (89 rows: 80 logged API queries, 5 web
searches, 3 blocked fetches, 1 pointer to the 2026-10-24 review), `related_work_matrix.csv`
(48 sources), `references.bib`, raw API responses in `lit/raw/`, scripts in `lit/`.

**Independence.** One AI assistant did the searching, screening and classification; no second
screener. Classification errors are possible. Spot-check any source before quoting it.

---

## 1. Method and its limits

**Search.**
- 40 queries over the five required concept groups (A–E), the five named lines of work (K01–K05)
  and three deliberately critical queries (X01–X03).
- Each query was sent to OpenAlex (top 10) and Crossref (top 6). That is 80 API calls, all HTTP
  200, giving 629 hits and 537 unique DOIs, all screened by title.
- Five targeted web searches followed. The 2026-10-24 review (~55 Crossref-verified sources) is
  reused, not repeated.

**Depth.**
- Abstracts were read for 50 shortlisted records (OpenAlex; 38 had abstracts).
- No full text was read in this session. Three attempts were blocked (HTTP 403): the Butcher 2026
  thesis and the EVE LF100LA specification, twice.
- Full-text readings come only from the prior session (Pan2023, Zhang2022, Wang2024,
  Hattori2020, Etxandi2024, Mahdy2026, Severson2019).

**Not done.**
- No Scopus, Web of Science or IEEE Xplore search (no access).
- No forward-citation chaining beyond what OpenAlex ranking provides.
- Backward chaining was done only through the prior review.

**Consequence.** "No paper found" below means *not found by these searches*. It never means
"no such paper exists". Nothing here supports the words "first" or "novel".

**Window.** Publication years in the screened set run from 1961 to 2026. The matrix weights
2018–2026.

## 2. The five named lines of work: located and checked

| Required line | Located | Access | What it shows |
|---|---|---|---|
| Adaptive MPC for EV cruise control considering battery degradation | Pan2023 (Appl. Sci.); Xu2026 (J. Power Sources, HEV, RL) | FT / MD | Pan2023: adapting weights adds little over a fixed-weight degradation-aware MPC; the fixed weights are better at medium/low speed |
| Multi-objective trade-off: battery degradation, charge retention, driveability | Tawfik2024 (Sci. Rep.) | AB | NSGA-II Pareto over exactly these three objectives; battery life +25 %, range +8 %, driveability −0.6 % |
| Hierarchical urban eco-driving with battery lifetime and energy | LiB2024 (CCTA), LiB2023 (TTE), Cai2026 (HEV) | AB / MD | Battery life +26.6 % and energy −10.5 % against constant-speed strategies, with signal-timing freedom |
| Eco-driving optimal control with driver preferences | Fleming2020, Lot2025, Qamar2026 | AB | −21 % energy with −7 % average speed. The regen-limit assumption alone shifts energy losses by 3–12 % |
| Public ageing data with capacity and impedance | Luh2024 (NMC/C-SiO, 228 cells), Pozzato2022 (NMC, UDDS profile, HPPC+EIS), Zhang2020 (EIS), Severson2019 (LFP, IR), Chung2021 (repurposed LFP), catalogues Mayemba2024, dosReis2021 | AB / FT | Rich NMC data with driving profiles; LFP data only for small A123 cells or second-life LFP. **Nothing for a 100 Ah CATL cell** |

## 3. Classification

### 3.1 Directly comparable work

| Source | Relation to this project |
|---|---|
| **Pan2023** | Fixed vs adapted weights in degradation-aware longitudinal control. Its finding agrees in direction with R1 (adaptation ≈ no gain over a good fixed design). The degree of freedom differs (spacing in ACC), and so does the controller (MPC). |
| **Tawfik2024** | Multi-objective NSGA-II trade-off of degradation, charge retention and driveability. It overlaps the thesis's Contribution 2 (NSGA-II Pareto of energy, longevity and performance). |
| **Corno2019** | Ageing management by acting on the **maximum battery current** and the depth of discharge, with drivability and range constraints. Prior art for any "battery-current-limit-aware" layer. |
| **Xu2026** | Ageing-aware ACC co-optimised with HEV energy management (title only). |

**None of these schedules LQR gains on SoH for fixed-reference speed tracking.**

### 3.2 Related but materially different

These are grouped by what differs from this project:

- **The speed trajectory is free** (eco-driving or ACC): LiB2023, LiB2024, Cai2026, Lot2025,
  Qamar2026, Fleming2020, Jia2022, Zhang2022, Shao2019, Wang2024, Djeffal2026, Heuts2025,
  Stabile2023.
- **No SoH:** Hattori2020 (energy-aware LQR with a motor loss model), Tramacere2022 (adaptive LQR,
  lateral), Zhang2019S (weight adaptation on motion states), Komaee2024 (LQR gain adapted to avoid
  saturation), Ban2015.
- **Different powertrain or degree of freedom:** Butcher2026 (dual-motor torque split vs battery
  health), Anselma2021/2021b (HEV), Naseri2026 and Smith2009 (regen blending and current governors),
  Samada2023 (MPC reference governor with an LQR inner loop, battery SoC, racing).

### 3.3 Counter-evidence (sources that challenge the thesis's premises)

1. **A lower peak current is not evidence of slower fade.**
   - Keil2015, cell experiments: "A higher level of regenerative braking has generally led to
     reduced battery aging". Long low-current charging, not short high-rate recharge, promoted
     lithium plating.
   - SunC2026, review: "lower charging current alone does not establish a battery-life benefit".
   - Both contradict the thesis's mechanism for its fade claim (report.md L3168: "by moderating
     peak charge/discharge currents, achieves slower capacity fade").
2. **Moderate ageing barely changes vehicle-level performance.**
   - Anselma2021b: HEV fuel economy and acceleration "relatively unaffected until the battery
     loses more than 20 % of original capacity".
   - Butcher2026: "the range loss caused by capacity fade is larger than the range recovered
     through torque optimization".
   - Both agree with R1, where SoH mattered only through assumed current limits.
3. **Double-digit energy savings come from changing the speed profile.**
   - Djeffal2026: 13.06 % saving against a *tracking* baseline, by reshaping speed.
   - Lot2025: 21 % saving with a 7 % lower average speed.
   - LiB2024: 10.5 % saving against constant-speed strategies.
   - The thesis's 12.5 % is in the range typical of trajectory freedom, not of feedback-gain changes
     on a fixed reference. That agrees with R1's ledger (gap to exact tracking 0.11–0.20 %).
4. **Weight adaptation is not reliably better than good fixed weights** (Pan2023).
5. **Regen-limit assumptions alone move energy by several percent** (Qamar2026: 3–12 %). Any
   SoH effect that runs through assumed regen limits (R1 class C) is therefore of the same order
   as a modelling choice.

### 3.4 Apparent research gaps (not found by these searches)

| ID | Apparent gap | Why it is narrow | Counter-evidence to its value |
|---|---|---|---|
| G1 | A **fair, factorial** test of whether SoH gain scheduling adds anything *once a battery-constraint supervisor exists* (scheduling × constraint management, equal tuning budgets, held-out cycles) | Pan2023 compares adaptive vs fixed weights but not with a separate constraint layer, and without equal tuning budgets reported | The answer may simply be "no", as R1 and Pan2023 suggest. A negative result is publishable only as a careful methods/benchmark study |
| G2 | A **bound** on what any feedback gain can change in energy on a fixed reference (gap to exact tracking + forced friction), as an evaluation tool for "adaptive controller saves X %" claims | Hattori2020 notes qualitatively that standard cycles cannot evaluate trajectory-changing methods | The bound is model-specific and partly elementary; it is a contribution of method and clarity, not of new theory |
| G3 | SoH-dependent **state-of-power limits in micro-EV / low-voltage (48 V) LFP packs** for longitudinal control | Etxandi2024 shows small packs become power-limited first (NMC+LMO, ≥ 16 kWh). No 48 V LFP micro-EV study was found | It needs cell data (OC-1); without it, any result is an assumed scenario |
| G4 | **Reproducible negative-result benchmark** with an energy ledger and a cross-simulator check for an SoH-adaptive EV controller | The prior review found no cross-simulator check of an EV controller comparison | Methodological; journals in this area rarely publish null results |

### 3.5 Gaps that cannot be verified from the available sources

- **The novelty of "SoH-scheduled LQR" itself.** No paper scheduling LQR on SoH for speed tracking
  was found by OpenAlex, Crossref or web search. IEEE Xplore and Scopus were not searched, and the
  thesis's Table 6 lists an unidentifiable "Huang et al. 2023, LQR, SoH-based, Aging compensation"
  (prior review §9). **Not verifiable.** Do not claim it.
- **Whether battery-health-aware eco-driving for micro-EVs is unstudied.** Cai2026 and Xu2026 could
  only be read as titles, and the eco-driving literature is large. **Not verifiable.**
- **Any LFP 100 Ah resistance-growth or power-limit-vs-SoH law.** Prada2013, Naumann2020 and
  Schimpe2018 may contain usable relations, but their full texts were not read. **Not verifiable
  here.**
- **The thesis cell's current limits.** Only retailer summaries of EVE 100 Ah LFP cells (1C
  continuous, 2C 30-s pulse) were found, as secondary sources. CATL is unidentified. **Not
  verifiable.**

## 4. What follows for the three paths

| Path | Effect of the literature |
|---|---|
| **P1: retain SoH-scheduled LQR as the core** | The closest prior work (Pan2023) agrees with R1 that adaptation adds little. Counter-evidence weakens the thesis's fade mechanism. What remains defensible is G1/G2: a *fair evaluation* of SoH scheduling, not a claim that it works. |
| **P2: battery-constraint supervisory layer** | Constraint-aware regen blending (Naseri2026), current governors (Smith2009), current-limit ageing management (Corno2019) and MPC reference governors (Samada2023) already exist, so the layer itself is **not novel**. The open question is G1: the *marginal* value of SoH scheduling given such a layer. This is narrow, answerable with existing code, and the user's F1-vs-S1 comparison targets exactly that. |
| **P3: energy–time–health eco-driving layer** | Well established: Tawfik2024, LiB2024, Lot2025, Cai2026, Jia2022, Zhang2022, Wang2024. A defensible narrower contribution would need G3 (micro-EV 48 V LFP state-of-power limits), which is blocked by missing cell data. Novelty is not demonstrable from the sources reachable here. |

## 5. Comparison of percentages across studies

Reported gains are **not comparable** with each other or with the thesis's 12.5 %. They differ in:
- **baseline:** constant speed, a human or preceding vehicle, an IDM, a tracking controller, or a
  fixed-weight MPC;
- **speed freedom and trip time:** Lot2025 is 7 % slower;
- **energy definition:** battery, wheel, or total cost;
- **ageing model:** usually the same model inside the optimiser and the evaluation (circularity
  noted for Zhang2022 and Wang2024).

None is cited here as a benchmark the thesis should match.
