# Thesis audit summary

**Thesis:** "Multi-objective adaptive LQR with battery aging compensation for urban micro-EV
powertrain systems" (`EURÉKA 2026 - KT.docx`, SHA-256 `01363a06…eddff8c`).

**Date:** 2026-10-24.

**Full record:** `docs/thesis_full_scientific_audit.md`. Its sections are:
- §2 material defects;
- §3 equations;
- §4 results traceability;
- §5 the claim table;
- §6 the bibliography;
- §7 owner items;
- appendices A (derivations) and B (lookups).

**Coverage.** The whole thesis was read: `report.md` L1–L6612 and the 194 text-box paragraphs
that pandoc did not convert. No range is unreviewed.

**Limits:**
- the 17 figures carry no data;
- 5 garbled equations cannot be fully reconstructed;
- paywalled standards and the EUR-Lex text of Regulation 2023/1542 were not accessed;
- the novelty assessment rests on a limited search.

The DOCX, `report.md`, the models, scripts, protocols, saved results, the claim registry, the
preservation inventory and the baseline hashes were **not modified**. Nothing was simulated
or installed.

## 1. Counts

### Claims (295 rows, §5)

| Verdict | Count | Share |
|---|---|---|
| CONTRADICTED | 115 | 39 % |
| NOT VERIFIED | 91 | 31 % |
| VERIFIED WITH CONDITIONS | 44 | 15 % |
| INVALID DERIVATION | 27 | 9 % |
| VERIFIED | 11 | 4 % |
| OWNER CONFIRMATION REQUIRED | 7 | 2 % |

**Can the claim stay without overstatement?**
- Yes as written: **15**.
- Only after correction or conditioning: **110**.
- No (remove or replace): **170**.

### By part of the thesis

| Part | Rows | CONTRADICTED | INVALID DERIVATION | NOT VERIFIED | VERIFIED (± conditions) | Owner |
|---|---|---|---|---|---|---|
| Abstract | 17 | 10 | 1 | 6 | 0 | 0 |
| Ch. 1 Introduction | 30 | 13 | 2 | 12 | 3 | 0 |
| Ch. 2 Literature and theory | 65 | 11 | 8 | 23 | 23 | 0 |
| Ch. 3 System design | 65 | 16 | 13 | 17 | 17 | 2 |
| Ch. 4 Simulation setup | 29 | 15 | 2 | 9 | 2 | 1 |
| Ch. 5 Results | 24 | 17 | 1 | 5 | 1 | 0 |
| Ch. 6 Deployment | 34 | 19 | 0 | 10 | 4 | 1 |
| Declaration and limitations | 6 | 3 | 0 | 0 | 3 | 0 |
| Appendices A–J | 25 | 11 | 0 | 9 | 2 | 3 |

### Other audits

- **Equations (35 items, §3):**
  - 19 INVALID DERIVATION;
  - 2 CONTRADICTED;
  - 3 NOT VERIFIED;
  - 9 VERIFIED WITH CONDITIONS;
  - 2 VERIFIED.
- **Bibliography (25 entries, §6):**
  - 3 CONTRADICTED: Huria [3], Lin [9], and UL 1973 [24] as used;
  - 10 NOT VERIFIED;
  - 11 VERIFIED WITH CONDITIONS;
  - 1 VERIFIED;
  - the duplicate printed reference list is also CONTRADICTED.
- **New derivations from the thesis's own numbers (58, Appendix A):** 45 inconsistent,
  13 consistent.
- **Existing executed checks:** all 17 are `consistent: false`
  (`artifacts/reports/report-consistency-checks.json`).

## 2. The most serious errors and unsupported results

Ordered by how much of the thesis each one removes.

1. **The central results have no originating data.** The reproducible experiment
   contradicts them.
   - There is no run, log or dataset behind 12.5 % energy, 15.3 % fade, 85.3 vs 95 Wh/km,
     the 98.2 % success rate, any benchmark comparison, Monte Carlo statistic, Morris table,
     worst case or ANOVA.
   - The thesis's own numbers conflict: 10.2 % vs 9.7 % vs 12.5 %, and 15.3 % vs 14 %.
   - The pre-registered experiment in the documented model gives:
     - ΔE = +0.000 to +0.005 %;
     - RMSE 0.4–2.0 % worse;
     - a retuned fixed gain that beats the scheduled controller.
2. **The Chapter 3 plant model is dimensionally invalid** (CHK-AMATRIX-DIM).
   - Its PMSM parameters cannot run on a 48 V bus: the back-EMF at base speed is 37.1·p V,
     against a 27.7 V limit, and 85 N·m is available only below 0.46 m/s (A-05, A-06).
3. **The ageing model cannot be implemented and is dimensionally inconsistent.**
   - Its citations do not support it: Huria is NMC, from 2012, with no ageing model;
     Ramadass describes a different model; [10] does not exist as cited.
   - Its temperature law has the wrong sign.
   - Every lifetime, warranty and replacement figure depends on it.
4. **The SoH estimator cannot produce SoH as written.**
   - Capacity is not an EKF state.
   - The uncertainty is taken from the SoC variance.
   - The abstract names a different estimator.
5. **The stability proofs are invalid.**
   - The time-varying LQR proof is circular.
   - The MRAC proof has matrix-shape errors and misuses LaSalle's principle.
   - The LQR robustness bounds are mislabelled or vacuous.
   - Only frozen-time stability is supported.
6. **The optimisation objectives are dimensionally wrong**, and no Pareto study was ever run.
7. **The drive-cycle evidence is impossible for the thesis's own vehicle.**
   - The VUC is "real-world" in Chapter 1 and "not real measured data" in the Limitations.
   - VUC positive work (95 kJ) is below the rolling-resistance energy (387 kJ).
   - VUC "kinetic energy" (1.5 kWh) exceeds the 0.55 kWh the battery supplies.
   - The WLTP class and CLTC speed are wrong.
8. **The statistics are invalid.**
   - 9 of 18 p-values fail Bonferroni.
   - The confidence interval is wrong by a factor of 1.6.
   - Cohen's d is inconsistent.
   - The Monte Carlo count and two worst-case sets conflict.
   - The Morris tables are duplicated across two designs.
9. **Safety and compliance are claimed without any artefact.**
   - The thesis's own S3/E3/C3 rating means ASIL C, not B.
   - R100, R13 and R10 are misidentified or misapplied.
   - Manufacturing yields and field reliability are reported for a product and fleet that do
     not exist.
10. **The literature and novelty base is unreliable.**
    - References [7]–[10] are not found as printed; [9]'s locator belongs to another paper.
    - 12 of the 15 Table 6 studies are unreferenced.
    - The thesis's own Table 6 lists prior LQR + SoH-ageing work, contradicting "explored in
      isolation".
    - The reference list is duplicated with conflicting numbering.
11. **Economics and LCA rest on contradicted inputs.**
    - The BOM sums to 12,580 USD, not 9,300 USD.
    - The LCA table totals 14.3 t, not 25 t.
    - The reliability sum, the FIT unit and the warranty reserve are wrong.
12. **The configuration is undefined.**
    - The model is a generic 48 V pack; the BOM lists 16 × 3.2 V = 51.2 V cells with no part
      number.
    - The vehicles named are inconsistent.

## 3. What cannot be retained without correction

**Remove or replace entirely:**
- the Abstract's results sentences;
- Contributions 2–5;
- §2.10 Tables 6–7 and the novelty paragraph;
- §3.2 state-space model (Eq. 4.1–4.7) and the motor parameters of Table 8;
- §3.3 ageing model, Table 9 and Figure 11;
- §3.4 stability proof;
- §3.5 EKF SoH derivation and Figure 13;
- §3.6 Pareto results;
- §3.7.4–3.7.6 MRAC and RLS derivations;
- §3.8 Eq. 4.35, 4.36 and 5.32;
- §4.2 VUC and Tables 12–13 (VUC and random columns);
- §4.3 benchmark tuning results, Tables 14–15;
- **all Chapter 5 results** (§5.1–§4.9, Tables 16–21) and the hardware timing and footprint
  figures; keep the hardware, CAN and FTTI material only as a labelled proposed design;
- in Chapter 6: TCO and payback (Tables 25, 37), the LCA (Tables 26–27, 41), the
  manufacturing metrics, the reliability and warranty figures, the compliance statements and
  the chapter summary;
- Appendices B (Table 33, B.1 circuit), C (code claims), D (Tables 35–36, D.3–D.6), E
  (Table 38, effect sizes), F (Table 39) and G (BOM total and shares);
- the duplicate reference list;
- refs [7]–[10].

**Correct and keep:**
- Chapter 1 context sentences (IEA figure narrowed, CAGR corrected, L6e/L7e source
  corrected);
- Chapter 2 theory, after the specific fixes in §3 of the full audit: Eq. 2.15, 2.38,
  2.46–2.53, 2.54, 2.69–2.70 and 2.7;
- the citation details of [3], [4], [6], [24] and [25];
- Assumption 1, after deleting the > 10 % scenarios;
- the Declaration, after deleting "validated parameters".

## 4. What can safely be retained, and on what conditions

**Results** (SIMULATION_SUPPORTED within the documented model only):

| Result | Conditions |
|---|---|
| **N01** null result: SoH-scheduled LQR changes model energy per km by ≤ 0.005 %, with 0.4–2.0 % worse RMSE | 48 V documented model, flat road, synthetic S1/S2 ≤ 50 km/h, SoH 0.7–1.0 known, γ = 1; constraints essentially inactive |
| **N02** a retuned single fixed gain beats the scheduled controller | best member at the edge of the tested family |
| **N03** paired robustness, mean ΔE −0.054 % [−0.058, −0.050] | assumed parameter ranges; no inference about vehicles |
| **N04** resistive losses are 1.1–2.1 % of supplied energy | a decomposition of the tested runs, not a bound |
| **Python–OpenModelica cross-implementation** (554/570 checks) | cross-implementation only; DASSL only; S1 distance FAIL unresolved; same author; not physical validation |
| Frozen-time closed-loop stability of the documented design | over SoH 0.5–1.0 and γ 0–10 |

**Theory, parameters and citations:**
- **Standard theory, verified:**
  - the longitudinal force balance;
  - the 1-RC ECM;
  - discrete LQR with ZOH and DARE;
  - integral augmentation;
  - EKF update equations;
  - Pareto definitions;
  - LHS and Morris definitions.
- **Parameter values:** retain only as "assumed" or "taken from the draft without primary
  source", with the provenance labels in `configs/parameters.yaml`.
- **Verified citations:** BNEF 2023 ($139/kWh, −14 %); IEA GEVO 2024 (14 M, +35 %); the
  TRL definition.
- **Statements of what was not done:** no physical experiments; VUC not real data; the
  ageing model unvalidated.
- **Statements to add:** no independent human replication; no physical vehicle, bench or HIL
  validation.

## 5. Prioritised repair plan, ordered by scientific risk

1. **Replace the claimed results with the evidence that exists.**
   - Rewrite the Abstract, Chapter 5 and the conclusions around N01–N04 and the
     cross-implementation, with all conditions.
   - Withdraw 12.5 %, 15.3 % and every number derived from them.
   - Template wording is in `docs/final_contribution_and_thesis_revision_plan.md`.
2. **Replace the plant model.**
   - Present the documented model (`docs/model.md`) instead of Eq. 4.1–4.7.
   - Delete the PMSM parameter set, or replace it with a consistent 48 V motor plus a source.
3. **Withdraw the ageing model and every ageing-dependent claim:**
   - Contribution 4's lifetime aspect;
   - O4;
   - Figure 11;
   - the fade numbers;
   - warranty and replacement savings.
   - Keep only "SoH enters the model through R0/R1 scaling (assumed coefficients)".
4. **Remove the SoH estimator and the stability proofs, or correct them.**
   - State that SoH is assumed known.
   - Replace the proof with the frozen-time result and the slow-variation condition (full
     audit M-11).
5. **Remove the unexecuted studies:** benchmarks, Monte Carlo, Morris, worst cases, ANOVA,
   Pareto, DDPG/MPC/fuzzy/PID tuning and the drive-cycle tables for VUC and the random
   cycles.
6. **Remove the safety, compliance, hardware, manufacturing and reliability claims.**
   - At most keep a labelled preliminary hazard list. Correct its ASIL determination to C.
   - Keep the hardware sections only as a proposed design.
7. **Repair the literature.**
   - Delete the duplicate reference list.
   - Correct [3], [4], [6], [24] and [25]; remove [7]–[10] and Tables 6–7 unless DOIs are
     supplied.
   - Remove the novelty claims.
   - Add sources for the uncited theory, chosen by the author.
8. **Fix the remaining derivations in Chapter 2** (M-05, M-08, M-10, M-12, M-13, M-17,
   M-23, M-24), and the regulatory identifications (R129/R136/R10, L6e/L7e, 876/QĐ-TTg).
9. **Rebuild or delete Chapter 6 economics and LCA.**
   - Any retained economic analysis must use sourced inputs and must not depend on the
     withdrawn savings.
10. **Resolve the owner items:**
    - OC-1, the pack and cell;
    - OC-2 and OC-3, the publications;
    - OC-4, the refs [7]–[10] DOIs;
    - OC-5, the Table 1 source;
    - OC-6, the original code;
    - OC-7, named partners and suppliers;
    - OC-8, AI disclosure.
    - Each has a conservative default in §7 of the full audit.

Each step is itemised with search strings and replacement wording in
`docs/thesis_closeout_repair_sheet.md`. This audit's §5 adds the claims that the repair sheet
does not yet list.

## 6. Conclusion

**The thesis does not support its central claims.**
- The claimed energy and battery-lifetime benefits of SoH-scheduled LQR have no originating
  data.
- They are internally inconsistent.
- They are contradicted by the only reproducible experiment.
- The models used to justify them are dimensionally invalid, physically infeasible or
  unimplementable.

**What the project can support** is a narrower, honest result, valid in a documented
simulation model only. In that model:
- SoH scheduling of LQR weights made no practical difference to energy or tracking;
- a single retuned fixed gain did better;
- the outcome follows from SoH having no pathway into the controlled dynamics, given that
  resistive losses were about 1–2 % of supplied energy.

That result has been cross-implemented in OpenModelica. It has not been validated against a
vehicle, and it has not been independently replicated by a person. Writing the thesis around
that result requires removing or rewriting most of Chapters 3–6 and the Abstract.
