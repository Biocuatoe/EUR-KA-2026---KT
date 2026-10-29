# Battery-data feasibility audit for Option B (SoH-dependent battery limits)

Date: 2026-10-24. Scope: the EV longitudinal-dynamics project in `D:\EURÉKA 2026 - KT` only.

**What this audit is.** It decides whether Option B in
`docs/research_gap_and_next_experiments.md` §8 (adding SoH-dependent battery or powertrain
limits) can be parameterised defensibly for the thesis's stated vehicle.

**What was done.**

- No simulations were run. No model, script, protocol, result or thesis file was changed.
- All trace numbers come from saved files, through a read-only post-processing script kept
  in the session scratchpad. It uses only algebraic relations of the existing plant
  (§5.1).
- The Severson et al. raw dataset was **not** downloaded (§2.4).

**Labels used throughout:**

- **[verified]**: read in a primary or project source;
- **[derived]**: computed here from verified inputs;
- **[unsourced]**: stated somewhere without a traceable source;
- **[extrapolation]**: goes beyond the conditions of the data;
- **[review]**: reasoning added by this audit.

**Independence.** This audit was prepared by the same AI research assistant that built the
model and wrote the earlier reviews. No person has checked it.

---

## 1. Decision

**Option B is not currently supportable.** Recommendation: **close the study as Option A**,
a bounded comparative and reproducibility study.

The reasons, each detailed below:

1. **The thesis's own cell is not the cell with ageing data.**
   - The thesis bill of materials specifies the pack as 48 V/100 Ah, built from **16 cells
     of "3.2V/100Ah", supplier "CATL"**, with no part number (report.md L6509–6510)
     [verified, but itself unsourced].
   - No datasheet or ageing data exist for that unidentified large-format cell.
   - The Severson et al. dataset concerns a **1.1 Ah cylindrical high-power A123 cell**
     (§2).
   - Using it would mean picking a convenient proxy, not parameterising the stated
     vehicle.
2. **The A123 cell's current ratings are not traceable to a document I could read.** Only
   nominal voltage and capacity, and the voltage window, are traceable (§3).
3. **The pack definition is internally inconsistent.**
   - 16 cells × 3.2 V = 51.2 V, but the model uses 48 V. Numerically 48 V equals
     15 × 3.2 V, but the model specifies no cell count (clarified 2026-10-24).
   - The series count is therefore unresolved, so per-cell voltage and any voltage floor
     cannot be mapped (§4).
4. **The voltage-limit pathway is missing indispensable inputs:** OCV–SoC, R(SoC, T, SoH),
   R1/C1, the cell and inverter voltage floors, and interconnect resistance (§6).
5. **A screen on saved traces shows a limit could be made to bind only by choosing
   unsourced values.**
   - For example, with the thesis's own unsourced 2.5 V/cell floor, R0 would have to be
     about 5–6 times its new-cell value at the S1 peak (§6.2).
   - The decision rests on whether the parameterisation is defensible, not on whether a
     constraint can be made to activate.

---

## 2. Severson et al. 2019 dataset (A123 APR18650M1A)

### 2.1 Sources

| Source | Publisher / host | Access in this audit | Use |
|---|---|---|---|
| Severson et al., *Nature Energy* 4:383–391, 2019, [10.1038/s41560-019-0356-8](https://doi.org/10.1038/s41560-019-0356-8) | Springer Nature; accepted manuscript on [eScholarship](https://escholarship.org/uc/item/9532z8t0) | Accepted manuscript read in full. The nature.com page redirected to a login and was not read | Methods, test conditions |
| Supplementary Information (ESM 1) | Springer Nature, [static-content.springer.com](https://static-content.springer.com/esm/art%3A10.1038%2Fs41560-019-0356-8/MediaObjects/41560_2019_356_MOESM1_ESM.pdf) | Read in full (text extraction) | Feature definitions, rate capability, temperature |
| Data-processing repository [rdbraatz/data-driven-prediction-of-battery-cycle-life-before-capacity-degradation](https://github.com/rdbraatz/data-driven-prediction-of-battery-cycle-life-before-capacity-degradation) | Authors (GitHub); no licence file (API `license: null`); last push 2023-07-06 | `README.md`, `LoadData.m`, `BuildPkl_Batch1.ipynb` read | Field names, exclusions |
| Data portal [data.matr.io/1](https://data.matr.io/1/) | Toyota Research Institute platform | **Not accessible.** TCP connections from this machine timed out. A remote fetch returned only a JavaScript shell titled "Experimental Data Platform" | File list, sizes and licence **unverified** |
| Kaggle mirror ("MIT-Stanford Dataset") | third party | Page not readable (JavaScript). A search-engine summary says 2017-05-12 batch file ≈ 3.03 GB | **SEC**; size unverified |

### 2.2 Per-cycle and within-cycle data actually available

From the repository `README.md`, `LoadData.m` and `BuildPkl_Batch1.ipynb` [verified]:

- **Per-cell descriptors:** charging policy, cycle life, barcode and channel. Barcode and
  channel are "not available in the pkl files".
- **Per-cycle summary:** `cycle`, `QDischarge`, `QCharge`, `IR`, `Tmax`, `Tavg`, `Tmin`,
  `chargetime`.
- **Within-cycle:** `t`, `I`, `V`, `T`, `Qc`, `Qd`, plus the derived `Qdlin`, `Tdlin` and
  `discharge_dQdV`.
- **Format.** Three batch files, `2017-05-12_…`, `2017-06-30_…` and
  `2018-04-12_batchdata_updated_struct_errorcorrect.mat`. They are MATLAB v7.3 (HDF5),
  read with `h5py` in the notebook.
- **Exclusions in `LoadData.m`:**
  - five cells continue from batch 1 into batch 2 and are appended;
  - channel 46 of batch 3 is removed for "a problem with the data collection";
  - batch-3 cells with final capacity > 0.885 Ah are removed;
  - three "noisy" batch-3 cells are removed;
  - five unfinished batch-1 cells are optionally removed.

### 2.3 Resistance measurement: conditions and limits

**Conditions** (accepted manuscript, Methods) [verified]:

- "an internal resistance measurement was obtained during charging at 80 % SOC by averaging
  10 pulses of ±3.6C with a pulse width of 30 ms, where 1C is 1.1 A";
- Arbin LBT cycler with 4-point contacts;
- environmental chamber at 30 °C;
- all cells discharged identically: 4C CC-CV to 2.0 V, cutoff C/50;
- charged with 72 fast-charging policies, 0→80 % SoC in 9–13.3 min, then 1C CC-CV to
  3.6 V.

**Units.** The unit of `IR` is **not stated** in the paper, SI or repository text read.
Ohm is the likely unit but is **unverified**. It must be checked against the data magnitude
before any use.

**How the paper used it.** The SI uses IR only as early-life features: cycle 2, the
minimum over cycles 2–100, and cycle 100 minus cycle 2 (SI Table 1 and feature
definitions) [verified]. The paper and SI give **no IR-versus-ageing summary**.

**Temperature.**

- Cell average temperature varies by about 6 °C across cells (SI Fig. 3).
- It rises by "nearly 10 °C" during rapid steps (SI Fig. 4).
- So "30 °C" describes the chamber, not the cell.

**What can be quantified** (only after obtaining the batch files):

- A 30 ms pulse resistance at 80 % SoC during charge, ≈ 30 °C chamber, against measured
  discharge capacity, for each cell. That gives an empirical resistance-versus-capacity
  relation and its cell-to-cell spread for **this cell, under fast-charge cycling**.

**What cannot be inferred:**

- resistance against SoC, or against temperature as an independent variable;
- the RC branch (R1, C1) or longer-pulse (1–10 s) resistance, which matters for sustained
  acceleration;
- OCV–SoC: only 4C discharge V–Q curves exist, and they include IR drop;
- discharge resistance, since the pulses are taken during charge;
- behaviour under EV drive cycles or calendar ageing;
- current limits;
- pack-level resistance (interconnects, busbars);
- **anything about a 100 Ah prismatic cell.**

This is a **cell cycling dataset**. It is not a vehicle-battery or pack validation dataset.

### 2.4 Practical accessibility

- **No smaller author-published summary was found.**
  - The SI contains no IR trajectories.
  - The repository contains code only.
  - The portal is the authors' data location (README).
- Quantifying IR growth would require at least one multi-GB batch file (≈ 3 GB per the SEC
  mirror summary). The portal itself could not be reached from this machine.
- **Not downloaded**, because the result cannot change the decision: the cell does not
  apply to the thesis vehicle (§1, item 1).
- Third-party processed copies exist (e.g. the Kaggle mirror). Their provenance and
  processing are unknown, and they should not substitute for the portal files.

---

## 3. Datasheet traceability: issuing publisher versus current host

| Quantity (APR18650M1A) | Value | Issued by | Where the copy is hosted | Status |
|---|---|---|---|---|
| Nominal voltage / capacity / energy | 3.3 V / 1.1 Ah / 3.63 Wh | A123 Systems, LLC: *Battery Pack Design, Validation, and Assembly Guide using A123 Systems AMP20M1HD-A Nanophosphate Cells*, User Documentation 493005-002, 7 Feb 2014, Table 2 (copyright notice "© 2014 A123 Systems, LLC"; PDF author field "A123 Energy Solutions") | buya123products.com (relationship to A123 **not verified**) | **traceable** to manufacturer-issued text |
| Voltage window | 2.0 V (discharge) / 3.6 V (charge) | Stated by Severson et al. as "recommended by the manufacturer"; SI Fig. 27 rate test within 3.6/2.0 V | Nature Energy / eScholarship | **peer-reviewed second-hand attribution**, not a datasheet |
| Manufacturer fast-charge protocol | 3.6C CC-CV | Severson et al. (Methods) | as above | peer-reviewed second-hand attribution |
| Max continuous discharge; 10 s pulse discharge; charge limits; internal impedance | (30 A continuous and others appear only in search summaries) | An A123 datasheet, listed by a third party as "MD100009, 2009" | mikrocontroller.net (Cloudflare challenge / HTTP 403), alldatasheet.com (403), datasheet4u.com, teklib.com (zip on a third-party S3) | **NOT VERIFIED**: no copy could be read |
| Pack-scaling rules | string current = N_p × cell maximum (Eq. 8); string cutoff = N_s × cell cutoff (Eq. 9); pulses may go below the cutoff, never below 0.5 V | A123 493005-002 | buya123products.com | **traceable** (general A123 rules) |
| Current-limit tables against temperature and SoC (Appendix A, Tables 15–18) | — | A123 493005-002 | as above | apply to the **AMP20M1HD-A** cell only, not the APR18650M1A |

---

## 4. The modelled pack, from project sources

| Quantity | Value in project | Source and status |
|---|---|---|
| Pack open-circuit voltage | 48 V, constant | `configs/parameters.yaml` (`assumed`; from report Table 8 nominal) |
| Pack capacity | 100 Ah | `parameters.yaml` (`report_unverified`, Table 8) |
| Chemistry | LFP | Table 8 (L2727). The cited parameter source, Huria 2012, used NMC cells (literature review §9) |
| Cell | "3.2V/100Ah", quantity 16, supplier "CATL" | BOM, report.md L6510 (`report_unverified`; **no part number, no datasheet**) |
| Series / parallel | **not stated** | The BOM implies 1P (16 cells of 100 Ah give a 100 Ah pack only in series), hence 16S. But 16 × 3.2 V = **51.2 V ≠ 48 V** used in Table 8 and the model. **Series count UNRESOLVED** |
| Cell voltage window | "2.5–3.65 V" (generic LFP text, L1213) | **unsourced** |
| Pack R0_new / R1_new / C1 | 5 mΩ / 3 mΩ / 50 kF | `parameters.yaml` (`report_unverified`) |
| R0 growth | k_r0 = 0.5, so R0 × 1.15 at SoH 0.7 | `report_unverified` |
| Motor limits | T_max 85 N·m, P_max 18 kW, constant (no V_dc dependence) | `report_unverified` |
| Minimum bus / inverter voltage, BMS current limits | — | **missing** |

**Pack scaling.** Only the BOM configuration (1P) is explicit enough to compute.

- In 1P, cell current equals pack current, whatever the series count [derived].
- An APR18650M1A pack of 100 Ah would need 100/1.1 = 90.9 cells in parallel, which is not
  an integer. No such configuration appears anywhere in the project. **No A123 cell current
  is computed.** Inventing N_p would be an unsupported configuration.

---

## 5. Saved S1/S2 evidence

### 5.1 What the saved traces contain

Files: `artifacts/raw/primary/{S1,S2}/timeseries.npz` (8 runs each: fixed and scheduled ×
SoH 1.0/0.9/0.8/0.7), `manifest.json`, and `data/processed/primary/runs.csv`. Sampling is
every 10 ms: S1 has 32,492 samples over 324.9 s; S2 has 21,329 over 213.3 s [verified].

| Signal | Saved? | Note |
|---|---|---|
| Battery current `i` | yes | computed from the state at each sample (`simulate.py` L67–69) |
| SoC | yes | S1 0.765–0.800; S2 0.793–0.800 |
| Speed `v`; delivered torque `T`; torque request `t_ref`; available torque `t_lim`; saturation `sat`; `infeasible` | yes | |
| Electrical power P_e | no, but **exactly derivable** | P_e = T·ω/η_mi when motoring and T·ω·η_mi when regenerating, with ω = G·v/r_w (the plant's own relation) |
| Terminal voltage V_t; RC voltage V1 | no, but **exactly derivable** | V_t = P_e/I (|I| > 1 A); V1 = V_oc − V_t − R0·I |
| Cell temperature | no | no thermal model |
| Energy accumulators | `E_chem`, `dist` per sample; others only at start and end | |

**Check of the reconstruction [derived].** The algebraic V1 agrees with an independent
trapezoidal integration of dV1/dt = −V1/(R1·C1) + I/C1 from the saved current to
≤ 5.7 × 10⁻⁶ V in every run.

**Possible from saved files:**

- current-demand statistics;
- pack C-rate;
- moving-average currents;
- P_e, V_t and V1;
- torque headroom;
- breakeven resistance for a given voltage floor (§6.2).

**Not possible without re-simulation:**

- the *effect* of any limit on the trajectory, energy, tracking or regeneration clipping.
  Once a limit binds, the closed-loop trajectory changes, so these traces only show whether
  a limit **would have been reached**;
- per-cell voltage (series count unresolved);
- OCV-dependent V_t (the model has constant V_oc);
- temperature effects;
- standard cycles or other profiles.

### 5.2 Current demand [derived, verified against `runs.csv`]

| | S1, all 8 runs | S2, all 8 runs |
|---|---|---|
| Peak discharge current | 273.95–275.22 A (`runs.csv` `peak_current_A` identical) | 106.90–107.08 A |
| Peak regenerative current | −171.4 to −171.0 A | −67.1 A |
| RMS current | 64.66–64.81 A | 26.83–26.86 A |
| Maximum 10 s / 30 s / 60 s moving-mean discharge current | 195.8–196.5 / 107.9–108.2 / 79.9–80.1 A | 61.4 / 28.1 / 21.6 A |
| Fraction of time with \|I\| > 100 A / > 200 A | 0.106 / 0.019 | 0.003 / 0 |
| Peak P_e | 12.76 kW | 5.07 kW |
| Minimum V_t | 46.56 V (SoH 1.0) to 46.35 V (SoH 0.7) | 47.45–47.37 V |
| V1 at peak current | 0.066–0.067 V | 0.018–0.019 V |
| max \|t_ref\|/t_lim; saturation; infeasible samples | 0.619; 0; 0 | 0.380–0.381; 0; 0 |

**Pack-normalised C-rate.** I/Q_pack is 2.74–2.75C peak, 1.96C as a 10 s mean, and 1.71C
in regeneration (S1).

- For the BOM's 1P configuration this **is** the cell C-rate.
- It holds for any configuration only under equal current sharing between identical cells.

**Model ceiling [derived; model-internal, `report_unverified` inputs].** P_max = 18 kW
limits P_e to ≤ 20.6 kW. At V1 = 0 that is ≈ 450 A (4.50C) at SoH 1.0 and ≈ 454 A (4.54C)
at SoH 0.7, with V_t = 45.7 and 45.4 V. No profile in this model can demand more.

**Current-limit pathway: verdict.**

- **Cannot be assessed.** The thesis cell's continuous and pulse current ratings are
  missing (no part number), and the A123 ratings are unverified (§3).
- Even when obtained, a fixed C-rate limit is SoH-independent unless the BMS derates it
  with SoH. In that case it would apply identically to both controllers and give SoH no
  pathway. A sourced, SoH-dependent BMS derating policy would also be required. None is
  available.

---

## 6. Voltage-limit pathway

### 6.1 Missing inputs

| Input | Unit | Needed for | Candidate source | Applicability conditions | Status |
|---|---|---|---|---|---|
| Cell identity (part number) | — | everything below | thesis author or BOM supplier | must be the vehicle's cell | **missing** |
| OCV(SoC, T) | V per cell | V_t = V_oc(SoC) − V1 − R0·I; at least SoC 0.75–0.80 for S1/S2 | manufacturer OCV table, or a C/20 or GITT measurement of the same cell | same cell model; temperature stated | **missing** (the model's 48 V is `assumed`) |
| R0(SoC, T, SoH) and its pulse-duration definition | Ω per cell | sag and floor | same-cell datasheet or ageing test; Severson2019 for the A123 cell only (30 ms, 80 % SoC, charge, 30 °C) | duration must match the floor criterion (instantaneous vs 10 s) | **missing** for the thesis cell |
| R1, C1 (or 2RC) against SoH | Ω, F | sustained-acceleration sag (S1 10 s mean ≈ 196 A) | same-cell characterisation | | **missing** |
| Series count N_s | — | mapping a cell floor to the bus | BOM gives 16 cells, conflicting with 48 V | resolve with the author | **unresolved** |
| Cell discharge floor (continuous and pulse) and charge ceiling | V | V_min,pack = N_s·V_min,cell (A123 Eq. 9) | same-cell datasheet | pulses may go below the cutoff (A123 493005-002) | **missing** (2.5 V/cell is unsourced) |
| Inverter minimum DC-bus voltage | V | a second floor, possibly binding first | inverter datasheet | | **missing** |
| Interconnect and busbar resistance | Ω | pack R beyond N_s/N_p·R_cell | pack design | | **missing** |
| BMS state-of-power policy | — | how the floor becomes a current or power limit | design decision informed by [Plett2004] | must be declared | **missing** |
| SoH definition | — | maps the ageing data to SoH | data source | capacity ratio vs normalised (literature review §6) | **missing** |

### 6.2 Breakeven screen on saved traces [derived; inputs labelled]

**Method.**

- At the recorded peak electrical power P_e,pk with the reconstructed V1, the terminal
  voltage reaches a floor V_f when R0 ≥ R\* = (V_oc − V1 − V_f)·V_f / P_e,pk.
- V_oc = 48 V is the model's **assumed** constant, so the screen inherits that assumption.
- The floors below are a **sensitivity grid**. None is sourced.

| Pack floor V_f | S1: R\* (× R0_new = 5 mΩ) | S2: R\* (× R0_new) | Basis of V_f |
|---|---|---|---|
| 46 V | 7.0 mΩ (×1.39) | 18.0 mΩ (×3.59) | arbitrary (96 % of V_oc) |
| 44 V | 13.6 mΩ (×2.71) | 34.5 mΩ (×6.91) | arbitrary |
| 42 V | 19.5 mΩ (×3.91) | 49.5 mΩ (×9.91) | arbitrary |
| 40 V | 24.9 mΩ (×4.98) | 62.9 mΩ (×12.59) | 16 × 2.5 V: thesis BOM count × thesis generic floor (**unsourced**) |
| 37.5 V | 30.7 mΩ (×6.13) | — | 15 × 2.5 V: model-consistent count × the same unsourced floor |
| 36 V | 33.7 mΩ (×6.74) | 85.0 mΩ (×17.0) | arbitrary |

**Separating measured values from extrapolation.**

- **Model value at SoH 0.7:** R0 = 5.75 mΩ (×1.15), from `report_unverified` coefficients.
- **Only literature ageing ratio located:** R0,EOL/R0,new ≈ 1.7 for a Lishen 20 Ah LFP cell
  [Pan2023]. It was read from a scrambled table extraction, uses a different SoH
  definition and a different cell, and is unverified.
- **Severson IR growth:** not quantified (data not obtained).
- With the thesis's own unsourced floors, the S1 peak would need about 5–6× new-cell
  resistance. Reaching that from the model's 15 % growth, or from the unverified 1.7×
  ratio, would be an **[extrapolation]** with no supporting data.
- Choosing a 44–46 V floor would make the limit "bind" at ×1.4–2.7. That would be
  unsupported parameter selection.

**Uncertainty.**

- The breakeven values scale directly with the assumed V_oc and with the peak power. P_e
  is fixed by the S1 trace and the `report_unverified` vehicle and drivetrain parameters.
- A real LFP OCV, or a 16-cell pack at 51.2 V nominal, would raise V_oc − V_f and
  therefore R\*.
- Longer-pulse resistance (R0 + R1-type effects over 10 s) would lower the effective R\*.
  No source quantifies this for the thesis cell.
- **The direction of the net error is unknown.**

---

## 7. The "≈ 0.3 %" statement is not a universal bound

`docs/research_gap_and_next_experiments.md` §4.3 (written earlier in this project) says
the SoH-attributable resistive loss is ≈ 0.3 % of supplied energy. It concludes that
"within this model and parameter set, **H1 (ΔE ≤ −1 %) was unreachable by construction**
for any SoH-scheduled controller tracking the same profile".

**This audit flags that conclusion as an overreach [review].**

- **What the 0.3 % is.** It is first-order arithmetic: the 2.1 % resistive share times the
  15 % R0 increase from k_r0, which is `report_unverified`. It estimates how much ageing
  raises resistive loss in the tested runs.
- **Why it is not a bound on ΔE.** ΔE compares two controllers **at the same SoH**. Their
  energy can differ through every trajectory-dependent term, not only the ageing
  increment:
  - the motor/inverter loss asymmetry (÷η when motoring vs ×η when regenerating);
  - gear-efficiency asymmetry;
  - R1 losses;
  - friction braking;
  - the final kinetic energy;
  - tracking deviations from the trace.
- **What a bound would require.** A separate mathematical argument bounding the energy
  difference over all admissible torque trajectories that meet a stated tracking
  tolerance. That argument has not been made.
- **The same caution applies to N04** ("the resistive share bounds the controllable
  share"). `docs/research-contribution-review.md` already notes that it "is not a theorem".

**Narrowed wording to use instead:**

> In the tested model, profiles and controllers, the ageing-induced increase in battery
> resistive loss was of order 0.3 % of supplied energy (first-order estimate from recorded
> shares and the unverified resistance-growth coefficient). The observed scheduled-minus-
> fixed differences were 0.000 % to +0.005 %, and the 41-member fixed-gain family spanned
> 0.28 % in energy. No general bound on controller-induced energy differences has been
> derived.

The earlier document was not edited. This section supersedes its §4.3 conclusion sentence.

---

## 8. Limitations of this audit

- **Not read:**
  - the Nature article HTML (login redirect);
  - the data portal and its licence (unreachable or JavaScript-only);
  - every APR18650M1A datasheet copy (blocked).
- **Hosting.** The A123 pack guide's host (buya123products.com) was not verified as an A123
  property. Its content carries an A123 copyright notice.
- **IR unit** in the Severson data is unverified.
- **The screen in §5–§6** inherits every model assumption: constant V_oc, constant
  efficiencies, `report_unverified` vehicle parameters. It cannot show limit effects.
- **Pack configuration.** The project's pack configuration rests on an unsourced BOM entry
  that conflicts with the model voltage.

## 9. What would make Option B supportable

All of the following are needed:

1. The manufacturer part number and datasheet for the thesis vehicle's cell, with
   continuous and pulse current against temperature and SoC, and voltage limits.
2. Resistance-versus-ageing data for that cell, or for a cell whose applicability is
   documented.
3. OCV–SoC for that cell.
4. A resolved series/parallel configuration and pack voltage.
5. The inverter's minimum DC-bus voltage.
6. A declared, sourced BMS limit or derating policy that depends on SoH.

Only then should the model changes and protocol amendment in
`research_gap_and_next_experiments.md` §8.2–§8.7 be written, before any run.

## 10. Single recommended next action

**Close Option A now:** state the thesis result as a bounded comparative and
reproducibility finding, using the narrowed wording in §7 and the scope limits of
`research_gap_and_next_experiments.md` §7.

**Reopen Option B only if** the thesis author can supply the cell part number and its
manufacturer datasheet (item 1 of §9). That is the cheapest single input that could change
this decision, and nothing else in §9 can be sourced without it.
