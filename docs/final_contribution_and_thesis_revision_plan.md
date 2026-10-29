# Final contribution and thesis revision plan (Option A close-out)

Date: 2026-10-24. Scope: the EV longitudinal-dynamics project in `D:\EURÉKA 2026 - KT` only.

**Decision recorded.** The study is closed as **Option A**: a bounded comparative and
reproducibility study. No further search for a configuration that favours the adaptive
controller is to be made. Option B (SoH-dependent physical limits) is deferred under the
reopening criteria in §9.

**What this plan is.**

- It is a plan and a set of proposed wording for the author.
- The thesis `.docx` is **not** edited.
- Line numbers refer to the in-project Markdown copy `data/processed/report/report.md`.
  They do not map one-to-one onto the DOCX, so locate each passage by its quoted text.
- No simulation was run. No model, script, protocol or saved result was changed.

**Source labels for numbers:**

- **[Py]**: the saved Python result file named next to it;
- **[OM]**: the saved OpenModelica cross-check file;
- **[X]**: a cross-implementation comparison file;
- **[audit-quoted]**: a value quoted from an existing review document, not re-derived here.

**Integrity of the cited files** (checked 2026-10-24, read-only):

- The ten Python result files cited below match their SHA-256 values in the tracked
  `evidence/artifact_hashes.json`.
- The five OpenModelica and cross-check files match
  `verification/controller-crosscheck-artifact-manifest.csv`.
- `artifacts/` and `data/` are git-ignored. Their integrity rests on those hash records.

**Independence.** All analyses and reviews were produced by one AI research assistant. No
independent human replication has been done (§10, item 12).

**Inputs read:**

- `docs/literature_review_soh_scheduled_lqr.md`;
- `docs/research_gap_and_next_experiments.md`, with §4.3 corrected 2026-10-24;
- `docs/battery-data-feasibility-audit.md`;
- `docs/research-contribution-review.md`;
- `protocol/preregistration.md` (frozen);
- `evidence/claim_registry.yaml`;
- `verification/controller-crosscheck-report.md` and
  `verification/controller-crosscheck-integrity-review.md`;
- the saved results listed in §3.

---

## 1. Final research question

> In a documented, dimensionally consistent, torque-controlled longitudinal simulation
> model of a hypothetical 48 V micro-EV, battery SoH is assumed known exactly and
> affects only the battery's resistances and capacity. On the synthetic urban speed
> profiles S1 and S2 (flat road, up to 50 km/h), no actuator or battery limit is reached.
> Under these conditions, does scheduling the LQR weights on SoH according to the
> thesis's law (report Eqs. 4.39–4.42, mapped as fixed in `protocol/preregistration.md`)
> change model-computed battery energy per kilometre or speed-tracking RMSE relative to:
>
> - (a) a fixed LQR designed at SoH = 100 %, and
> - (b) the best member of a pre-declared fixed-gain family?
>
> Are any differences resolvable above the numerical error of two independent
> implementations (Python RK4 and OpenModelica/DASSL)?

The question excludes:

- SoH-dependent current, voltage or power limits;
- estimated rather than known SoH;
- capacity fade or lifetime;
- standard or measured drive cycles;
- any physical vehicle.

## 2. Defensible contribution statement

> This thesis contributes a pre-registered, reproducible simulation comparison of a fixed-gain
> LQR and an SoH-scheduled LQR for EV speed tracking, together with a cross-implementation
> numerical verification. Hypotheses, metrics, tuning and a ±1 % decision margin were fixed
> before implementation. On the documented model the SoH schedule produced no practical
> energy difference. A single fixed gain, retuned once from a pre-declared family, was
> better on both SoH-averaged energy and tracking. An energy decomposition shows why the
> tested schedule had little to act on: battery resistive loss was 1.1–2.1 % of supplied
> energy, and SoH does not enter the controlled dynamics of the model. The main
> difference was reproduced in an independent OpenModelica implementation, and the
> numerical error of the paired energy difference was quantified. The thesis does not
> propose a new or superior controller, and its results are properties of the model,
> not of a vehicle.

The contribution is **not**:

- a new control method;
- evidence that adaptive or SoH-aware control is ineffective in general;
- evidence about real vehicles, battery ageing or lifetime;
- a first-of-its-kind study (§8).

## 3. Results that can be reported

All values come from saved files. Rounding is for presentation; the cited file holds the
full value.

### 3.1 Primary comparison (pre-registered S-A) [Py]

Sources: `artifacts/reports/primary_results.json`; `artifacts/tables/primary_pairs.csv`.

| Result | Value |
|---|---|
| Runs | 16 attempted, 16 valid |
| Primary condition | S1, SoH 0.80, γ_v = γ_u = 1 |
| Energy, fixed / scheduled | 49.9025 / 49.9040 Wh/km |
| ΔE | **+0.0030 %** |
| RMSE, fixed / scheduled | 0.05038 / 0.05094 m/s |
| RMSE ratio | **1.0110** |
| Pre-registered decision | **NO PRACTICAL DIFFERENCE** |
| All 8 profile × SoH pairs | ΔE 0.0000 % to +0.0052 % (largest at S1, SoH 0.7); RMSE ratio 1.000–1.020; every pair NO PRACTICAL DIFFERENCE |
| Sanity control | SoH 1.0 runs identical (`sanity_soh1_identical: true`) |

### 3.2 Secondary analyses [Py]

| Analysis | Source | Value |
|---|---|---|
| γ sweep (S-B), S1, SoH 0.8, 15 settings | `artifacts/reports/gamma_sweep_results.json` | ΔE −0.019 % to +0.040 %. RMSE ratio 0.893–1.194; three settings exceed 1.10 (1.111, 1.167, 1.194). All are classified NO PRACTICAL DIFFERENCE under the **energy-only** pre-registered rule, and that must be stated when quoting S-B |
| Fixed-gain family (S-C, tests H_C) | `artifacts/reports/fixed_family_results.json`; `artifacts/tables/fixed_family.csv` | 41 members (R scale 0.1–10), 164 runs valid. SoH-averaged results: best member R × 0.1 gives 49.8544 Wh/km and 0.0379 m/s; scheduled gives 49.8810 Wh/km and 0.0508 m/s; the pre-registered fixed gain (R × 1) gives 49.8798 Wh/km and 0.0504 m/s. `H_C_holds: true`. The family spans 0.276 % in energy. The best member lies **at the edge** of the pre-registered range |
| Robustness (S-D) | `artifacts/reports/robustness_results.json` | 50 paired draws (100 runs). Mean ΔE −0.0539 %, bootstrap 95 % interval of the mean [−0.0580, −0.0500] %. All 50 draws NO PRACTICAL DIFFERENCE; median RMSE ratio 1.0107; 0 tracking failures. File's own limit: the interval is "Monte Carlo uncertainty of the mean over an ASSUMED uniform parameter distribution; not an inference about vehicles". The sign differs from §3.1, for a reason not tested |
| Energy split, S1, SoH 0.8, fixed | `artifacts/tables/energy_breakdown.csv` | road load 68.18 %, motor/inverter 21.99 %, gear 4.67 %, shaft friction 3.11 %, battery resistive (R0 + R1) 2.02 %, friction brake 0 %. Battery resistive share over all 16 primary runs: 1.10–2.11 % |
| Run validity and verification gate | the four experiment reports; `artifacts/reports/verification-gate.json`; `artifacts/reports/tuning-acceptance.json` | 296 of 296 runs valid. Gate: 152 tests, 0 failures, clean tree. Tuning accepted on attempt 1 (P-TUNE): overshoot 3.71 %, max \|λ\| 0.989 |
| Unconstrained regime | `data/processed/primary/runs.csv`; saved traces (audit §5.2) | Peak battery current 273.95–275.22 A (S1) and 106.90–107.08 A (S2). Maximum torque request / limit 0.619 (S1). No saturation; `traction_limited_frac` and `friction_brake_Wh` 0 |

### 3.3 OpenModelica cross-implementation [OM], [X]

| Result | Source | Value |
|---|---|---|
| ΔE at S1, SoH 0.8 | `verification/controller-crosscheck-runs/evaluation_summary.json` | OpenModelica (DASSL, tolerance 1e-12): +0.0030138 %. Python dt = 1e-4 s: +0.0030138 %. Saved Python (dt = 1e-3 s): +0.0030138 % |
| RMSE ratio at S1, SoH 0.8 | same | 1.0110215 in all three |
| Decision labels | same | NO PRACTICAL DIFFERENCE for all 8 profile × SoH pairs (16 runs), in both implementations |
| Largest bias in ΔE from the accumulator discrepancy | `verification/controller-crosscheck-runs/review_dE_bias_bound.json` | ≤ 4.3 × 10⁻⁹ percentage points (maximum \|value\| 4.25 × 10⁻⁹, S2, SoH 0.8) |
| Check status | `verification/controller-crosscheck-results.csv` | 561 PASS, 191 INFO, 32 FAIL rows. **FAIL** rows: 16 for S1 accumulated distance (8 traces, 8 scalars; §6) and 16 for the inadmissible CVODE/IDA P-TUNE solver-study runs |
| Admissible solver | `verification/controller-crosscheck-report.md` §1 [audit-quoted] | DASSL only. CVODE and IDA failed. Solver-selection amendments A2/A3 were post-result rule changes (`controller-crosscheck-integrity-review.md` §4) |

**Report as:**

- "reproduced in two independent implementations to within numerical error";
- **not** "validated".

**Do not report:**

- "practical equivalence" (the ±1 % is a decision margin, not an equivalence bound);
- any value from the original thesis figures or tables that the claim registry lists as
  withdrawn.

## 4. Claims to remove or narrow

Locations are in `report.md`. Claim IDs are from `evidence/claim_registry.yaml`, and those
statuses are unchanged.

| # | Claim (location; quote) | Action | Evidence |
|---|---|---|---|
| R1 | "adaptive LQR … with battery aging compensation" (L3 abstract; Contribution 1 heading L788; L5012 "effectiveness of the proposed adaptive LQR controller with battery aging compensation") | **Narrow** to "SoH-scheduled LQR weights"; remove "compensation" | No compensation shown (§3.1). SoH does not enter the controlled dynamics (`research_gap…` §4.1) |
| R2 | "compensate for battery aging effects on powertrain dynamics" (L609, O1); "compensating for changes in vehicle dynamics due to battery aging" (L3174) | **Remove** | Contradicted by the documented model structure (`docs/model.md` §1–§3) |
| R3 | "reduced control authority due to increased battery internal resistance" (L3328, L6112) | **Remove** | The model has no battery-side limit. Peak torque request ≤ 0.619 of the limit; no saturation (§3.2). The CATL cell-specific limits needed to model it are unavailable (§7) |
| R4 | Lifetime and ageing: O4 (L621); "Battery lifetime extension ≥ 10 %" (L673); capacity-fade results (L3168; C02, C04, C05, C06 at L3170; C36/C40 figures); L3076 | **Remove** | No ageing model was run. C02, C04, C05, C06 and C40 are already WITHDRAW in the registry |
| R5 | Headline energy claims: "12.5 % ± 2.1 %" (L9, C01); 95 → 85.3 Wh/km (L5468, C03; also L5039, L5171, L5470, L6299, L6337, L6383) | **Remove** | Contradicted by §3.1. C01 and C03 are WITHDRAW_PENDING_RETEST, and the pre-registered retest contradicted them |
| R6 | Novelty: "novel adaptive LQR framework" (L790); "novel contributions" (L2590); "comprehensive integration … represents" a research gap (L2608) | **Remove** | Literature review §1.2 and §2: gain scheduling and health-aware control are established; no database search was done |
| R7 | Validated parameters: "validated parameters from published datasheets and benchmark papers" (L5980, C32); "validated against" (L5982); "derived from published experimental data" (L752); "Wind tunnel data" (Table 8 L2718, C33); Citroën Ami / Wuling datasheets (L5994, C34); "validated against published data" (L4353–4355, C22) | **Remove or relabel** as `report_unverified` / `assumed` | `configs/parameters.yaml`: 20 `report_unverified`, 11 `assumed`, 2 `standard`, none measured (`research-contribution-review.md` §4.2 [audit-quoted]) |
| R8 | Battery source: Assumption 5, "LFP … parameters identified from Huria et al." (L750); "SEI growth theory … (Huria 2018, J. Power Sources)" (L5998); ref. 3 printed as IEEE TIA 2018 (L6006) | **Correct** the citation to 2012 IEEE IEVC, [10.1109/IEVC.2012.6183271](https://doi.org/10.1109/IEVC.2012.6183271). **Withdraw** the LFP and SEI attributions | The paper's abstract describes NMC cells and a 1RC model without ageing (literature review §9). Evidence row C37 was updated 2026-10-24 (status still CONTRADICTED; recommendation now "correct and withdraw"); see review §14 (K2) and `docs/evidence-corrections-2026-10-24.md` |
| R9 | Literature claims: Qiao (L2328, 23.5 %), Wang (18.2 %), Lin (15.7 %) (L2330–2332); refs 7–10; Table 6 (L2560–2584) | **Remove** unless the author supplies DOIs that resolve | Not found as cited (literature review §9) |
| R10 | Pack: "48V/100Ah" (Table 8 L2725–2726) vs BOM 16 × "3.2V/100Ah" CATL (L6509–6510) | **State as hypothetical and resolve** the 16S (51.2 V) vs 48 V conflict, or remove the BOM cell line | `battery-data-feasibility-audit.md` §4 |
| R11 | "Journal Paper 1 … (Under Review)" (L6588) | **Author to confirm or remove**. Its title repeats R1 | Not verifiable from the project |
| R12 | Supporting-document overclaim: "H1 (ΔE ≤ −1 %) was unreachable by construction for any SoH-scheduled controller" (`research_gap_and_next_experiments.md` §4.3, original wording) | **Corrected 2026-10-24.** The original is preserved in the §4.3 correction note | `battery-data-feasibility-audit.md` §7. The thesis must not contain any form of this claim |
| R13 | Supporting-document related wording: "The claimed 12.5 % is unreachable by any controller tracking the same profile in this model class" (`research-contribution-review.md` §5.1), with the same idea in that review's §4.2, §7, §8, §10 and §13, in `docs/evaluation-report.md` Summary, and in evidence rows C01 and N04 | **Corrected 2026-10-24** with inline markers, review §14 (K1), an evaluation-report correction section, and `docs/evidence-corrections-2026-10-24.md` | Same reasoning as R12: the resistive-share argument is an explanation, not a theorem |
| R14 | Software and validation infrastructure: MATLAB/Simulink (L7, C23); SIL/PIL (C20); ASIL and diagnostic coverage (C17, C18) | **Remove** (already WITHDRAW) | Claim registry |

## 5. Replacement wording (thesis-ready drafts)

The author should adapt the language, but must keep the conditions attached to every
number.

**Research gap.**

> Battery health has been incorporated into vehicle control mainly as a cost on battery
> wear in hybrid-vehicle energy management, and as a degradation objective in speed
> planning for battery-electric vehicles, where the controller is free to change the speed
> trajectory. In the reviewed literature we did not identify a study that schedules the
> weights of a speed-tracking LQR on battery state of health while the speed profile is
> fixed, nor one that compares such a schedule with a retuned fixed-gain controller under
> pre-registered conditions. This review was not a systematic database search, so we do
> not claim that no such study exists.

**Contributions.**

> (i) A pre-registered simulation comparison of a fixed-gain and an SoH-scheduled LQR for
> speed tracking, including a competing fixed-gain explanation. (ii) An energy
> decomposition that explains why the tested schedule had little effect in this model.
> (iii) A cross-implementation verification in Python and OpenModelica, with the numerical
> error of the paired energy difference quantified. No new controller is proposed.

**Methodology.**

> The plant is a documented point-mass longitudinal model with a torque-controlled drive and
> a first-order Thevenin battery whose resistances increase linearly as SoH decreases. SoH
> is constant within each run and assumed known. All parameters are taken from the thesis
> draft without primary sources, or are assumed. None is measured. Hypotheses, metrics,
> tuning and a ±1 % decision margin were fixed before implementation. Gains were tuned on a
> separate profile. Results were regenerated in an independent OpenModelica implementation.

**Results.**

> On profile S1 at 80 % SoH, the SoH-scheduled controller changed battery energy per
> kilometre by +0.0030 % (49.9025 → 49.9040 Wh/km) and increased tracking RMSE by a factor
> of 1.011. Across both profiles and SoH 70–100 % the change ranged from 0.000 % to
> +0.005 %, which is no practical difference under the pre-registered margin. A single fixed
> gain from a pre-declared family used less energy (49.854 vs 49.881 Wh/km) and tracked
> better (0.038 vs 0.051 m/s), averaged over SoH. OpenModelica reproduced the primary
> difference (+0.0030138 %) and the decision labels for all eight profile and SoH
> combinations.

**Limitations.**

> All results are properties of a simulation model with unverified or assumed parameters,
> constant motor efficiency and constant open-circuit voltage, on synthetic profiles, with
> SoH known exactly. No actuator or battery limit was reached, and the model contains no
> SoH-dependent voltage, current or power limit. Such limits could not be parameterised for
> the stated CATL cell, whose part number and datasheet are unavailable. No ageing model was
> run, so nothing is claimed about capacity fade or lifetime. In the cross-implementation
> check, the accumulated distance on profile S1 failed its pre-declared tolerance by a
> relative amount of about 4 × 10⁻¹⁰. The cause is unresolved. Its effect on the energy
> difference is below 4.3 × 10⁻⁹ percentage points. No physical vehicle, bench or HIL
> validation was performed.

**Conclusion.**

> In this documented model and under the tested conditions, scheduling LQR weights on battery
> state of health as proposed gave no practical energy benefit, and a once-retuned fixed gain
> did better. The first-order ageing-induced change in battery resistive loss was about 0.3 %
> of supplied energy under the model's assumed resistance growth. This is an estimate for the
> tested runs, not an upper bound on what other controllers or a more complete battery model
> could achieve. Whether SoH-aware control helps when ageing tightens battery power limits
> remains open and requires sourced cell-level data.

## 6. Unresolved numerical issue: the S1 accumulated distance

This item **stays FAILED and unresolved**. Do not describe it as fixed.

- **What failed.** The S1 accumulated distance failed its pre-declared tolerance in the
  OpenModelica comparison: 16 FAIL rows (8 trace, 8 scalar) in
  `verification/controller-crosscheck-results.csv`. S2 passes.
- **Size [audit-quoted]** (`controller-crosscheck-report.md` §4.3;
  `controller-crosscheck-integrity-review.md` §3):
  - the maximum trace difference is 0.99–1.05 × 10⁻⁶ m, against tolerances of
    4.8–6.5 × 10⁻⁷ m;
  - the end distance is 8.4 × 10⁻⁷ m short of 2,161.3 m (3.9 × 10⁻¹⁰ relative) against the
    0.1 ms Python run;
  - the shortfall is identical for both controllers and all SoH levels, and independent of
    solver tolerance.
- **Bounded effect [X].** The induced bias in ΔE is ≤ 4.3 × 10⁻⁹ percentage points
  (`review_dE_bias_bound.json`), against effects of 10⁻³ to 5 × 10⁻³ %. The decision labels
  cannot change.
- **Mechanism.** Not established. A sample-time-drift explanation was partly supported and
  then falsified (integrity review §3, item 6).
- **Optional future test, not run:** a drift-free time-event formulation, under a dated
  amendment.

## 7. Physical-validation limitations

- **No validation of any kind:** no physical vehicle, dynamometer, bench or HIL validation.
  Every number is a property of the model (C38 is consistent with the record).
- **Parameters:** none measured. The vehicle is hypothetical.
- **Battery:** the thesis BOM names 16 CATL "3.2V/100Ah" cells with **no part number**.
  - No applicable datasheet, OCV–SoC curve, resistance against SoC, temperature and SoH,
    current rating or voltage floor is available
    (`battery-data-feasibility-audit.md` §4–§6).
  - CATL cell-specific constraints are therefore **unsupported** and were not modelled.
- **Proxy cell rejected:** the Severson et al. A123 APR18650M1A dataset was not used. It is
  a different cell (1.1 Ah cylindrical, high power), and it is a cell cycling dataset, not a
  vehicle validation dataset.
- **Profiles:** synthetic. No standard (WLTC) or measured cycles were used.

## 8. Literature positioning

- **Permitted wording:** "In the reviewed literature (`docs/literature_review_soh_scheduled_lqr.md`,
  2026-10-24) we did not identify a study that …".
- **Not permitted:** "first", "novel", "no prior study exists", "to the best of our
  knowledge, the first".
- **Related prior work the thesis should cite** (verified entries in literature review §8):
  - gain-scheduling surveys [Rugh2000; Leith2000];
  - health-aware HEV energy management [Ebbesen2012; Moura2013; Anselma2021];
  - degradation-aware BEV speed control [Pan2023; Jia2022; Zhang2022];
  - an energy-aware LQR [Hattori2020];
  - SoH-dependent power limits [Plett2004; Etxandi2024];
  - reproducibility and verification [How2018; Roache2002; Nosek2018; Lakens2017].
- **Respect access labels:** do not quote numbers from sources marked MD or SEC in that
  review.

## 9. Reopening criteria for Option B

A physical constraint model may be developed **only if all** of the following are first
documented with provenance:

1. **The cell:** the actual manufacturer (CATL or another), the exact part number, and the
   applicable manufacturer-issued datasheet. The issuing publisher and the hosting site
   must be distinguished.
2. **Current ratings:** continuous and pulse discharge and charge currents, with pulse
   duration and their dependence on temperature and SoC.
3. **Voltage limits:** discharge floor and charge ceiling, continuous and pulse.
4. **OCV–SoC** for that cell, at the stated temperature.
5. **Resistance against SoC, temperature and ageing** for that cell, or for a cell whose
   applicability is documented, with the pulse duration defined.
6. **Pack topology:** a resolved series/parallel configuration consistent with the stated
   pack voltage, and interconnect resistance.
7. **Inverter:** its minimum DC-bus voltage.
8. **BMS policy:** a sourced or explicitly declared limit or derating policy that depends
   on SoH. Without it, a fixed current limit gives SoH no pathway.
9. **Protocol:** a dated protocol amendment written before any run, as specified in
   `research_gap_and_next_experiments.md` §8.3–§8.7.

Reopening must not be motivated by, or designed around, whether the adaptive controller
would then look better.

## 10. Consistency checklist

Tick each item before finalising. "Docs" means the supporting research documents in
`docs/` and `verification/`.

| # | Check | Thesis | Supporting docs: current state |
|---|---|---|---|
| 1 | The research question matches §1 (fixed profile, unconstrained model, known SoH) | ☐ | ✔ `research_gap…` §5 |
| 2 | Every quantitative result traces to a §3 file; no withdrawn number remains (R5, R14) | ☐ | ✔ this plan §3 |
| 3 | Wording: "no practical difference", never "equivalent" or "ineffective in general" | ☐ | ✔ |
| 4 | Python, OpenModelica and cross-implementation values are labelled separately; "reproduced", not "validated" | ☐ | ✔ |
| 5 | The S1 distance FAIL is reported as unresolved and bounded (§6) | ☐ | ✔ cross-check report §5, integrity review §3 |
| 6 | No claim of ageing compensation, reduced control authority, lifetime extension or capacity-fade benefit (R1–R4) | ☐ | ✔ |
| 7 | The 0.3 % is stated only as a first-order estimate for the tested runs, never as a bound (R12, R13) | ☐ | ✔ corrected 2026-10-24 in `research_gap…` §4.3, review §14 (K1), `evaluation-report.md` and evidence rows C01 and N04. The tracked CSV/JSON exports still need regenerating (item 18) |
| 8 | No novelty claim; literature positioning as in §8 | ☐ | ✔ |
| 9 | Parameters labelled unverified or assumed; no "validated parameters" (R7) | ☐ | ✔ |
| 10 | Huria citation corrected; LFP and SEI attributions withdrawn (R8) | ☐ | ✔ evidence row C37 and review §14 (K2), 2026-10-24. The registry disposition stays as registered, by the registry's rule; the outcome lives in the matrix |
| 11 | Unresolved references 7–10 and Table 6 removed or given DOIs (R9) | ☐ | ✔ listed in literature review §9 |
| 12 | Independent human replication (setup, verify, reproduce, hash check), stated as done or as not done | ☐ | ✘ not done (`research-contribution-review.md` §11, item 6) |
| 13 | Pack definition consistent (48 V vs 16 × 3.2 V) or explicitly hypothetical (R10) | ☐ | ✔ flagged in audit §4 |
| 14 | No physical validation and no CATL cell-specific constraints (§7) | ☐ | ✔ |
| 15 | Option B appears only as future work with the §9 criteria | ☐ | ✔ |
| 16 | AI-assistance disclosure as required by competition or university rules | ☐ | — |
| 17 | Solver caveat stated: DASSL was the only admissible OpenModelica solver; A2/A3 were post-result amendments | ☐ | ✔ integrity review §4 |
| 18 | Corrected evidence matrix published without rewriting the baseline | — | ✔ as a dated snapshot (2026-10-24): `evidence/evidence_matrix_2026-10-24.yaml` and `evidence/exports/2026-10-24/`. The baseline (`evidence_matrix.{yaml,csv,json}`, `artifacts/tables/` copies, `artifact_hashes.json`) is preserved unchanged and still shows the pre-correction C01, C37, N04 and C38 text. `build_evidence.py` was not run. The default pipeline still reads the original YAML. See `docs/evidence-corrections-2026-10-24.md`, "Resolution" |

**Update 2026-10-24 (later the same day).** Items 7 and 10 were resolved in the supporting
record (`docs/evidence-corrections-2026-10-24.md`). Thesis-side repairs are itemised in
`docs/thesis_closeout_repair_sheet.md`.

**Still open:**

- item 12: no independent human replication;
- follow-up evidence-review items (C38 registry note, C40 and the other registry entries
  citing the unverified external figure script, ten unlisted baseline-candidate files):
  see `docs/evidence-corrections-2026-10-24.md`. Item 18 is done as a dated snapshot
  (2026-10-24), not by regenerating the baseline.
