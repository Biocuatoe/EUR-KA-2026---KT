# Full scientific-content audit of the thesis

**Thesis:** "Multi-objective adaptive LQR with battery aging compensation for urban micro-EV
powertrain systems" (`EURÉKA 2026 - KT.docx`).

**Date:** 2026-10-24. **Status:** audit complete for the whole text; see §1.4 for the parts
that could not be checked.

**Companion:** `docs/thesis_audit_summary.md` (verdict counts, priorities, conclusion).

The original DOCX, `report.md`, the source models, scripts, protocols, saved results, the
claim registry, the preservation inventory and the baseline hash records were **not
modified**. No simulation was run and nothing was installed.

---

## 1. Method and coverage

### 1.1 Sources

**Thesis text**
- `EURÉKA 2026 - KT.docx`: SHA-256 `01363a06…eddff8c`. It is byte-identical to
  `data/raw/report/EUREKA-2026-KT.docx`.
- `data/processed/report/report.md`: a pandoc 3.11 conversion of that file (SHA-256
  `cbd2e74a…a26dca66`; `data/processed/report/MANIFEST.json`).
- Locations are given as `L####` (line in `report.md`) and as page numbers (p.). Page numbers
  come from the thesis's own table of contents, list of figures and list of tables. Where a
  page is not listed there, the nearest listed section page is given with "≈".

**Conversion limits** (checked with a read-only parse of `word/document.xml`)
- The DOCX is evidently a PDF-to-Word conversion.
  - It has no Word equation objects.
  - Fraction bars, integrals and sub- or superscripts are scattered over 534 text boxes, and
    194 distinct text-box paragraphs are not in `report.md`.
- All text-box text was extracted and read.
  - It holds figure labels, equation fragments, the ISO 26262 V-model boxes and the FTTI
    requirements.
- Where an equation is garbled, the reading used is stated. If the fragments do not
  determine an equation, it is marked as such.
- The 17 figures are vector drawings or placeholders.
  - The embedded images are 112–380-byte placeholders.
  - None carries data, so **no figure can be verified as a data plot**; only its axes and
    legend text can be read.

**Project evidence** (all read-only)

| Tag | Path | What it is |
|---|---|---|
| REG Cxx / Nxx | `evidence/claim_registry.yaml`; `evidence/evidence_matrix_2026-10-24.yaml` (dated corrected matrix) | 40 registered thesis claims and 4 restated claims, with executed checks |
| CHK-… | `artifacts/reports/report-consistency-checks.json` | 17 executed arithmetic/dimensional checks; **all 17 report `consistent: false`** |
| PRIM, PAIRS | `artifacts/reports/primary_results.json`, `artifacts/tables/primary_pairs.csv` | pre-registered primary experiment (16 runs, 16 valid) |
| GAMMA, FAM, ROB | `artifacts/reports/{gamma_sweep,fixed_family,robustness}_results.json` | S-B, S-C, S-D experiments |
| EB | `artifacts/tables/energy_breakdown.csv` | energy decomposition, closure ≤ 5.4e-10 |
| PARAMS | `configs/parameters.yaml` | every thesis parameter with provenance (20 `report_unverified`, 11 `assumed`, 2 `standard`) |
| MODEL | `docs/model.md`, `src/eureka/plant.py`, `src/eureka/controllers.py` | documented replacement model and controllers |
| XCHK | `verification/controller-crosscheck-report.md` | Python vs OpenModelica controller cross-implementation |
| A-nn | Appendix A of this document | 58 new read-only derivations from the thesis's own numbers (code and output included) |
| CR / OA / WEB | Appendix B | Crossref and OpenAlex lookups and targeted web sources, 2026-10-24, with access status |

### 1.2 Verdicts

| Verdict | Meaning in this audit |
|---|---|
| VERIFIED | Traced to primary evidence or reproduced by an explicit derivation; no qualification needed |
| VERIFIED WITH CONDITIONS | True only under a stated condition, or correct in substance with a minor defect that must be fixed |
| NOT VERIFIED | No primary evidence or source found, or the source could not be accessed. Also used for unexecuted plans stated as done when nothing contradicts them |
| CONTRADICTED | Primary evidence, an executed check, the thesis's own numbers or a verified source show the claim is false or internally inconsistent |
| INVALID DERIVATION | The mathematics or reasoning is wrong (dimension, sign, shape, logic), whatever the truth of its conclusion |
| OWNER CONFIRMATION REQUIRED | Only the author can resolve it (a receipt, an agreement, an intended configuration, an unpublished repository) |

**Rules followed:**
- A claim is not marked VERIFIED because another project document repeats it.
- A number in a table or figure counts only if its originating data and procedure exist.
- Python/OpenModelica agreement is cross-implementation evidence only; it is not physical
  validation.
- No independent human replication has been performed.

### 1.3 Categories (column "Cat.")

| Code | Category |
|---|---|
| LIT | literature |
| MATH | mathematical derivation |
| PARAM | parameter assumption |
| IMPL | model implementation |
| SIM | simulation result |
| STAT | statistical claim |
| PHYS | physical/engineering claim |
| SAFE | safety/compliance |
| ECON | economic or environmental projection |
| PLAN | future plan or design intent |
| — | editorial (structure of the document; one row, C1-30) |

### 1.4 Coverage, and what could not be checked

**Read in full:**
- `report.md` L1–L6612:
  - abstract;
  - Chapters 1–6;
  - declaration and limitations;
  - both reference lists;
  - Appendices A–J;
- all 194 text-box paragraphs.

No range of the thesis is unreviewed.

**What could not be checked, and why:**
1. **Figures 1–17** carry no data, so none of their curves can be verified.
2. **Garbled equations whose fragments do not determine the formula.** These are marked
   individually:
   - Eq. 2.7 rotor term;
   - Eq. 2.19;
   - Eq. 4.26 (a possible lost "1 +");
   - Eq. 4.36;
   - Eq. 4.58.
3. **Paywalled or blocked sources** (marked "not accessed"):
   - ISO 26262-3, ISO 14044, SAE J1979, MIL-HDBK-217F, UN GTR 15 and IEC/UL texts were not
     opened. Statements about them rest on standard reference knowledge.
   - EUR-Lex returns an empty page to automated fetches, so the Annex XII targets of
     Regulation (EU) 2023/1542 could not be read.
   - The full texts of Huria 2012 and Ramadass 2004 were not read; only their abstracts were.
4. **External-file provenance remarks** (`D:\EUREKA\…`) remain EXTERNAL_UNVERIFIED
   (`docs/research-contribution-review.md` §3.2). This audit does not rely on them; see
   C2-59, C3-29 and AP-03 for the in-project basis.
5. **Manufacturer data for Table 3** (four vehicles), Table 4 and Table 5 ranges were not
   looked up; the rows are NOT VERIFIED because the thesis cites no source.
   - This audit did not run an open literature search; novelty statements rest on
     `docs/literature_review_soh_scheduled_lqr.md` (a limited search), which does not prove
     that no prior work exists.

---

## 2. Material defects, ordered by scientific risk

Each item is a defect that changes what the thesis can claim. Claim IDs refer to §5.

### D1. The headline results have no originating data and are contradicted by the only reproducible experiment

- **What the thesis says:**
  - 12.5 % ± 2.1 % energy improvement (L9);
  - 15.3 % ± 2.8 % less capacity fade (L9);
  - 85.3 vs 95 Wh/km (L5468);
  - 98.2 % vs 72.4 % success (L5053);
  - fade of 16.5 vs 14.2 %/1000 cycles (L5476).
- **What exists:**
  - No run, log, script or dataset in the project produces any number in Chapter 5,
    Appendices D–F or Table 35.
  - Every figure is a vector drawing without data (§1.1).
  - The thesis's own figures are mutually inconsistent:
    - 85.3/95 Wh/km is a 10.2 % saving, not 9.7 % or 12.5 % (CHK-ENERGY-PCT);
    - fade reduction appears as 15.3 % and as 14 % (CHK-FADE-PCT);
    - the knee point is 122 Wh/km and 14 %/1000 cycles (L3593), outside Figure 9's 1–5 %
      axis.
- **The reproducible experiment** (pre-registered; documented 48 V model; synthetic S1/S2
  profiles; SoH 0.7–1.0; SoH known):
  - SoH scheduling changes energy per km by +0.000 to +0.005 % (PRIM, PAIRS; N01);
  - it worsens tracking RMSE by 0.4–2.0 %;
  - a single retuned fixed gain does better than the scheduled controller (FAM; N02);
  - peak current differs by 0.002 A (274.794 vs 274.793 A at S1, SoH 0.8), so there is no
    current-moderation mechanism for reduced fade (PAIRS).
- **Consequence:** C01–C04, C10–C16, C30, C31 and C39 cannot be retained. The defensible
  result is N01–N04, with their conditions.

### D2. The plant model in Chapter 3 is dimensionally invalid, and the motor parameters cannot work on a 48 V bus

- **Eq. 4.3–4.4 (L2654–2706):**
  - The traction coupling term has units rad/(kg·m·s), not m/s² (CHK-AMATRIX-DIM).
  - Battery current is modelled as an inductive state, with R_int/L_eq.
  - Motor speed is not kinematically tied to vehicle speed.
  - No road load acts on the shaft.
  - L_eq and K_e have no values.
- **Motor parameters (Table 8, L2728–2733):**
  - λ_m = 0.175 Wb gives a back-EMF amplitude of 37.1·p V at the base speed implied by
    18 kW/85 N·m (212 rad/s), for any pole-pair count p ≥ 1.
  - The largest phase voltage a 48 V bus can apply under SVPWM is 27.7 V.
  - With L_q = 8 mH, the inductive voltage alone exhausts the bus at 85 N·m above
    10.7 rad/s motor speed, i.e. 0.46 m/s vehicle speed (A-05, A-06).
  - The stated "≈20 ms" electrical time constant contradicts L/R = 400 ms from the same
    table (A-07).
- **Consequence:** results "from" this model cannot be physical. The documented replacement
  model (MODEL) is a torque-controlled point mass with an assumed 20 ms torque lag. It does
  not inherit these parameters. Any thesis text that keeps the Chapter 3 model must say it is
  dimensionally invalid; better, replace it with the documented model.

### D3. The battery-ageing model cannot be implemented, is dimensionally inconsistent, and is not supported by its citations

- **Eq. 4.21–4.26:**
  - k_c and k_cal have no values (C05).
  - Q_loss,0 is in % but is added to terms in Ah.
  - γ₀√t has units Ah^-1/2·time^1/2.
- **Eq. 2.54:**
  - It labels a term proportional to Ah throughput as "calendar ageing".
  - The parabolic diffusion law is in √t, not √Ah.
- **Eq. 4.35, 4.36 and 5.32 are dimensionally wrong** (A-58; §3).
- **Eq. 2.15:** the temperature law gives resistance *rising* with temperature, with the TCR
  of copper (0.004/°C); Li-ion cell resistance falls as temperature rises.
- **Sources:**
  - Huria et al. (L750, L5998) is a 2012 IEVC paper on NMC cells with no ageing model
    (REG C37; CR).
  - Ramadass 2004 [6] is a first-principles side-reaction model (OA abstract); its abstract
    does not describe the cited empirical law or LFP coefficients.
  - [10] (Smith & Wang 2006) is not found.
- **No validation data exist**, yet L3170 claims "agreement within 5 %", while L5998 says the
  model "requires experimental validation".
- **Consequence:** every ageing, lifetime, warranty and battery-replacement figure falls.

### D4. The SoH estimator cannot estimate SoH as specified

- The EKF state is [SoC, V_RC, R0], with capacity fixed at Q_nom (Eq. 4.52).
- Yet Eq. 4.63 takes SoH from "the estimated capacity state Q̂_k", and Eq. 4.64 takes its
  uncertainty from P₁,₁, which is the SoC variance.
- The abstract and §2.8 instead name Coulomb counting with voltage correction (L5, L2046).
- No estimator exists in the project (REG C29).
- Figure 13's text says "500 hours"; its axis runs to 1,000 hours.
- **Consequence:** C29 and Contribution 5 fall. A correct formulation is in §3, M-21.

### D5. The stability proofs are invalid

- **Time-varying LQR proof (L3218–3300):**
  - Condition 3 assumes the existence of the Lyapunov function that the proof should
    construct.
  - The K̇ bound (Eq. 4.50) is not derived from Eq. 4.49.
  - Continuous-time "Hurwitz" is used for a discrete-time controller.
  - "Region of attraction" is meaningless for a linear system.
- **MRAC proof (L3989–4087):**
  - The update law has the wrong matrix shape: K̂̇ = −Γ e xᵀ P B₀ is n×m, while K is m×n.
  - LaSalle's principle is applied to a non-autonomous error system.
  - It concludes K̃ → 0 without persistent excitation.
- **LQR robustness (Eq. 2.51–2.53):**
  - Eq. 2.51 is mislabelled as the return-difference inequality.
  - Eq. 2.53 is vacuous.
- What *is* supported:
  - frozen-time closed-loop stability of the documented design over SoH ∈ [0.5, 1] and
    γ ∈ [0, 10] (gate tests; REG C26);
  - the slow-variation argument, given in §3 (M-11).

### D6. The optimisation objectives are dimensionally invalid, and the Pareto study was never run

- Eq. 2.69 calls an average power (W) "energy consumption per kilometre".
- Eq. 2.70 equates a rate (ΔSoH/Δt) with an Ah-based quantity.
- No NSGA-II run, population or front exists (REG C31).
- Across fixed LQR weights in the documented model, energy and tracking do not conflict
  (FAM), so the trade-off that motivates the Pareto study was not observed.

### D7. The statistical claims are invalid or internally inconsistent

- The Monte Carlo count is given as both 100 per configuration and N = 1,000 (CHK-MC-COUNT).
- The matrix "6 × 4 × 100 = 2,400" omits the seventh controller (A-57).
- Tables 16 and 18 disagree, and "all samples < 0.6 m/s" conflicts with a 0.4 % failure
  rate (CHK-MC-TABLES).
- 9 of 18 p-values fail the stated Bonferroni threshold (CHK-BONFERRONI).
- The 95 % CI half-width is 0.005 m/s, not 0.008 (A-20).
- Cohen's d for tracking recomputes to 1.32, not 0.78 (A-23).
- The Morris statistics are identical in a 10- and a 12-parameter design (CHK-MORRIS-DUP).
- The worst-case sets conflict (CHK-WORSTCASE).
- Significance testing of model outputs under *assumed* distributions says nothing about
  real vehicles.

### D8. The drive-cycle evidence is fabricated-looking or physically impossible for the thesis's own vehicle

- **VUC:**
  - It is said to be "derived from real-world measurements" (L810, L4429), but the
    limitations say "not real measured data" (L5996).
  - Its distance/time implies 34.8, not 28.5 km/h (CHK-VUC-SPEED).
  - Its idle time cannot be under 62.3 % given 17 stops × 22 s (CHK-VUC-IDLE).
- **Table 13:**
  - It gives 95 kJ of positive wheel work on the VUC.
  - Rolling resistance alone needs 387 kJ, and the road load at least 643 kJ (A-13, A-14).
- **Table 12** gives a VUC "kinetic energy" of 1.5 kWh, which is 66 full stops from 50 km/h
  and nearly three times the 0.55 kWh the battery supplies over the cycle at 95 Wh/km
  (A-16, A-17).
- **Random cycles** violate the thesis's own ±5 % validation rule (A-18).
- **Other cycle errors:**
  - CLTC's average speed is 37.8 km/h in the text and 29.0 in the table (A-56);
  - WLTP's distance is wrong (CHK-CYCLE-SPEEDS);
  - "Class 3 is most representative" contradicts the vehicle's power-to-mass ratio of
    21–26 W/kg, which is Class 1–2 (A-12).

### D9. Benchmarks and comparative claims have no implementations

- P, PID, fuzzy LQR, MPC and DDPG exist only as descriptions.
- Defects in the descriptions:
  - the Ziegler–Nichols procedure cannot be applied to the stated plant and mixes PI and
    PID constants;
  - the DDPG agent has no reference speed or tracking error in its state;
  - its 10,000 episodes over 1 million steps last 1 s each, against 600–1,800 s cycles
    (A-19).
- Table 35 credits the adaptive LQR with the highest regeneration. In the documented runs,
  regenerated energy is identical within 0.01 Wh between fixed and scheduled LQR (REG C30).

### D10. Safety, compliance and hardware statements describe things that do not exist, and some are wrong in themselves

- **ISO 26262:**
  - ASIL B with 94 % diagnostic coverage is claimed without an FMEDA or hardware (REG C17).
  - The ASIL target appears as B, C and "C or D" (CHK-ASIL-LEVEL).
  - Table 24's own S3/E3/C3 maps to **ASIL C** in the ISO 26262-3 risk graph (A-52).
- **Regulations misapplied:**
  - UN R100 applies to M/N vehicles (L-category: R136); R13/R13-H cover braking of M/N/O
    vehicles and passenger cars.
  - "UN ECE 10" is the electromagnetic-compatibility regulation, not an emissions
    regulation (WEB).
- **Hardware:**
  - 0.40 ms in a 1 ms loop vs 1.2 ms in a 10 ms loop (CHK-SAMPLING);
  - the footprint is 86 KB, < 50 KB or 5 KB in different places (A-26);
  - the S32K144 and TMS570 are called "16-bit"; the thesis's own L5339 says 32-bit.
- **Sensing (Appendix B.1):**
  - the 11:1 divider puts 60 V at 5.45 V on the ADC;
  - the shunt amplifier outputs 10 V at 200 A;
  - ±200 A is below the ≈426 A that 18 kW needs at 48 V (A-27 to A-29).

### D11. Economics, LCA, reliability and manufacturing rest on contradicted inputs and contain arithmetic and method errors

- **Payback:** the arithmetic reproduces (A-31), but its inputs are C03/C04.
- **BOM:**
  - the lines sum to 12,580 USD, not 9,300, with the cells counted twice (A-35);
  - the cells cost 562 USD/kWh against the thesis's own 80–100 USD/kWh (A-37).
- **LCA:**
  - Table 27 totals 14.3 t, not 25 t;
  - it uses 0.6 kg/kWh, not 0.45;
  - it implies 130 Wh/km;
  - it lists a 2,500 kg body for an 850 kg vehicle (A-39 to A-44);
  - none of the ISO 14040/14044 elements are present.
- **Reliability:**
  - the component rates sum to 15.3 or 7.9, not 12.5;
  - "12.5 FIT" should be 12,500 FIT;
  - MTBF 9.1 years gives R(10 y) = 0.33, not "high confidence";
  - the "Ground benign" environment is wrong for a vehicle (A-47 to A-49).
- **Warranty:** the reserve should be 1,889 M VND, not 850 M VND (A-51).
- **Manufacturing:** yields "achieved in production" and field data from 1,000 vehicles
  over 2 years describe a product and a fleet that do not exist (Declaration L5980).

### D12. The literature base does not support the novelty claim, and the bibliography is unreliable

- **Duplicate lists:** the printed "References" section (L5948–5976) is a renumbered copy
  of entries 11–25. Its [1] is BloombergNEF, while the in-text [1] is the IEA.
- **Refs [7]–[10]:** none matches as printed (CR).
  - [9]'s article number belongs to a marine-vessel paper.
  - [7] has a topically similar but different record (Saxena et al. 2023).
- **Table 6:** 12 of its 15 studies have no bibliography entry.
- **Novelty is undercut by the thesis itself:**
  - Table 6 lists "Huang et al. 2023 | LQR | SoH-based | ageing: Yes | Aging compensation"
    and "Chen et al. 2024 | LQR + ANN | ageing | NSGA-II".
  - Yet L2608 says these elements were "explored in isolation".
- **Huria:** wrong venue, year and chemistry (REG C37).
- **Ramadass [6]:** an author is missing, and its abstract does not describe the law it is
  cited for.
- **Missing citations:** NSGA-II (Deb), DDPG (Lillicrap), Morris and SIMC are uncited.

### D13. The battery and vehicle configuration is undefined

- The model is a generic 48 V, 100 Ah pack.
- The BOM lists 16 × 3.2 V cells, which is 51.2 V, with no part number (A-38;
  `docs/battery-data-feasibility-audit.md`).
- The vehicle is variously Wuling Hongguang/VinFast VF3 (L780) and Citroën Ami/Wuling
  (L5994).
- Table 3's Wuling (20 kW, 665 kg) and VF3 (32 kW, 1,035 kg) exceed the thesis's own L7e
  limits of 15 kW and 600 kg.
- **Owner item:** the intended pack and vehicle. **Default:** describe a hypothetical generic
  vehicle with a generic 48 V pack, and treat the BOM as illustrative.

### D14. Validation and replication language overstates what was done

- "Validated parameters from published datasheets and benchmark papers" (L5980) is
  contradicted: of 33 parameters, 20 are report_unverified, 11 assumed and 2 standard
  (PARAMS).
- "Parameters validated against … manufacturer datasheets" (L7) likewise.
- What exists:
  - one model and its pre-registered simulations;
  - a Python vs OpenModelica cross-implementation of the controller and plant (XCHK).
- The cross-implementation's limits:
  - 554 of 570 checks pass, with DASSL as the only admissible solver;
  - the S1 accumulated-distance traces fail: 16 rows, relative size 3.9e-10–4.6e-10,
    mechanism not established;
  - the effect on ΔE is 1.6e-9 pp, because it cancels between the controllers.
- Not performed:
  - no physical vehicle, bench or HIL validation;
  - no independent human replication; both implementations were produced by the same AI
    research assistant.

## 3. Mathematical and dimensional audit

Equations are numbered as printed. Numbering is inconsistent: Chapter 2 contains Eq. 3.1–3.13,
Chapter 3 uses 4.x and 5.x, and Chapter 5 sections are numbered 4.6–4.9. These are renumbering
remnants. L3939 contains an unresolved cross-reference ("Equation **??**").

| ID | Topic | Eq. / location | Finding | Verdict | Defensible replacement |
|---|---|---|---|---|---|
| M-01 | Longitudinal force balance | 2.17–2.18, 2.20–2.22 (L1600–1650) | Correct; matches the documented plant (MODEL). The small-angle error is 0.1 % at an 8 % grade (computed) | VERIFIED | — |
| M-02 | Velocity-dependent rolling resistance | 2.19 (L1610–1618) | The garbled form cannot be read; the units of v are not stated; no source | NOT VERIFIED | State the formula, the units of v and a source, or delete |
| M-03 | Drivetrain and rotating mass | 2.23–2.25 (L1656–1682) | Dimensionally correct. 2.24 holds for traction only; in regeneration the efficiency acts on the other side. Appendix A's components multiply to 0.848, not Table 8's 0.88 (A-10) | VERIFIED WITH CONDITIONS | F = G·η·T/r_w (motoring); F = G·T/(η·r_w) (regenerating); use one η value consistently |
| M-04 | PMSM dq model and torque | 2.1–2.4 (L991–1027) | Standard model, correct after reading the fragments; [4] is real, but 1989 not 1988 | VERIFIED WITH CONDITIONS | Fix the citation year |
| M-05 | Induction-motor torque | 2.7 (L1095–1105) | Uses L_s + L_r (total self-inductances, as defined in 2.5–2.6); the steady-state equivalent-circuit formula needs the leakage inductances. The rotor equation 2.6 as rendered lacks the magnetising-current term (rendering uncertain) | INVALID DERIVATION | T_e = (3p/ω_s)·V_s²(R_r/s)/[(R_s+R_r/s)² + ω_s²(L_ls+L_lr)²] (per-phase rms, magnetising branch neglected), or remove; IM is not used |
| M-06 | Inverter power balance | 2.16 (L1580) | P_dc = (3/2)(v_d i_d + v_q i_q) holds for a lossless inverter with the amplitude-invariant Park transform | VERIFIED WITH CONDITIONS | State both conditions |
| M-07 | 1-RC Thevenin ECM | 2.11–2.12 (L1356–1364) | Correct; the same structure as the documented plant (R0, R1-C1) | VERIFIED | — |
| M-08 | Temperature law of R0 | 2.14–2.15 (L1522–1526) | With α_T = +0.004/°C, R0 rises with temperature. Li-ion ohmic and charge-transfer resistance fall with temperature (Arrhenius-type kinetics, electrolyte conductivity). 0.004/°C is the TCR of copper | CONTRADICTED | R0(T) = R0,ref·exp[(E_R/R_g)(1/T − 1/T_ref)], with E_R identified from the cell's HPPC data at several temperatures; the value cannot be determined from available information |
| M-09 | Continuous-time LQR | 2.31–2.35 (L1742–1770) | Correct. 2.33 omits x. P ≻ 0 requires (A, Q^1/2) observable; detectability gives only P ⪰ 0 | VERIFIED WITH CONDITIONS | Write u* = −R⁻¹BᵀPx; state the observability condition |
| M-10 | Lyapunov derivative for LQR | 2.38 (L1790) | Uses open-loop AᵀP + PA, which equals −Q + KᵀRK, not −(Q + KᵀRK). Strict negativity also needs Q + KᵀRK ≻ 0 | INVALID DERIVATION | V̇ = xᵀ[(A−BK)ᵀP + P(A−BK)]x = −xᵀ(Q + KᵀRK)x ≤ 0; asymptotic stability by detectability and LaSalle (LTI system) |
| M-11 | Time-varying LQR stability | 4.43–4.50 (L3218–3300); Contribution 1 (L792–798) | Condition 3 assumes the conclusion. 4.50 is not derived from 4.49. "‖K̇‖ < K_max, K_max any positive constant" is false in general: slow-variation results need the bound to be *sufficiently small* relative to the uniform decay rate. Continuous-time Hurwitz is used for a sampled controller | INVALID DERIVATION | Use the frozen-time Riccati solution P(SoH) as V. With p₁I ⪯ P ⪯ p₂I uniformly, V̇ ≤ −xᵀ[Q(SoH) + KᵀRK − Ṗ]x, so exponential stability holds if sup‖∂P/∂SoH‖·sup abs(dSoH/dt) < inf λ_min(Q + KᵀRK). For the discrete implementation, use the analogous condition on ‖P_{k+1} − P_k‖. SoH varies over months, so the margin is large, but no project artifact computes it. The documented project establishes **frozen-time** stability only (gate tests, REG C26) |
| M-12 | Hamiltonian derivation of the ARE | 2.46–2.50 (L1866–1898) | "At steady state (λ̇ = 0) the costate is proportional to the state" is wrong; λ̇ = 0 gives Qx = −Aᵀλ, not the ARE | INVALID DERIVATION | Assume λ(t) = P x(t) with constant P; substitute into λ̇ = −Qx − Aᵀλ and ẋ = (A − BR⁻¹BᵀP)x; equate coefficients to get the ARE |
| M-13 | LQR robustness | 2.51–2.53 (L1902–1918) | 2.51 is the value-function identity (equality ½x₀ᵀPx₀ for the optimal cost), not the return-difference inequality. 2.52 holds only at the plant input of a continuous-time full-state LQR loop with R = ρI. 2.53 is vacuous (singular values are ≥ 0). Discrete-time LQR has no guaranteed 60°/[½, ∞) margins | INVALID DERIVATION | Kalman inequality (I + L(jω))ᴴR(I + L(jω)) ⪰ R for L = K(jωI − A)⁻¹B, giving GM ∈ [½, ∞) and PM ≥ 60° for the continuous-time single-input loop; for the implemented discrete loop, compute the margins numerically |
| M-14 | Discrete LQR, ZOH, DARE, integral action | 2.39–2.45, 4.8–4.20 (L1796–1860, L2758–2910) | Correct; the documented controllers use exact ZOH (`zoh`) and DARE (`dlqr`). 4.9–4.10 are truncated series. "Schur method … iteratively" is inaccurate (the Schur method is direct). The state order differs between 4.1 and 4.14 | VERIFIED WITH CONDITIONS | — |
| M-15 | Sampling-time rules | L2800–2806 | "π/100 = 31.4 ms for a 10 Hz bandwidth": 10 Hz is 62.8 rad/s (A-09). "Time constants ≈20 ms ⇒ Ts ≤ 2 ms" is then violated by the chosen Ts = 10 ms (A-08); Table 8 gives L/R = 400 ms (A-07) | CONTRADICTED | Justify Ts from the closed-loop bandwidth of the actual design (documented model: 10 ms, tracking RMSE ≈ 0.05 m/s; PAIRS) |
| M-16 | Chapter 3 state-space model | 4.1–4.5 (L2630–2708) | Traction term has units rad/(kg·m·s) (CHK-AMATRIX-DIM); battery current treated as an inductive state; no v–ω_m kinematic coupling; L_eq, K_e undefined | INVALID DERIVATION | Documented model (MODEL): M_eff·v̇ = F_trac − F_rr − F_aero − F_brake, F_trac = G·η·T/r_w, ω_m = G·v/r_w, first-order torque lag, battery current algebraic from electrical power (V_t·I = P_e) |
| M-17 | Ageing law (theory) | 2.54 (L1938–1962) | The "calendar" term β·exp(−E_a/RT)·Ah is proportional to throughput, not time. The parabolic SEI law is √t, not √Ah. Units of α, β undefined. [6] does not describe this law (OA abstract) | INVALID DERIVATION | Separate laws: Q_cal = A_cal·exp(−E_cal/RT)·√t and Q_cyc = B·exp(−E_cyc/RT)·(Ah)^z, with every coefficient, unit and source stated; none is available in the project |
| M-18 | Stress factors | 2.55–2.60, 4.30–4.34 (L1964–2010, L3078–3126) | Forms are generic and dimensionally fine. 2.59 is not 1 at the reference unless C = 0, contradicting L1976. f_base and S_f are undefined. No coefficient has a source | NOT VERIFIED | — |
| M-19 | Implemented ageing model | 4.21–4.26 (L2916–2958) | k_c, k_cal have no values (not implementable; REG C05). Q_loss,0 = 2 % added to Ah terms. γ₀√t has units Ah^-1/2·time^1/2. As rendered, γ(SoC) = γ₀((SoC−0.5)/0.5)² vanishes at SoC = 0.5 (a text box holds a stray "1 +"; whether it belongs here cannot be determined) | INVALID DERIVATION | Cannot be determined from available information; withdraw |
| M-20 | SEI thickness and capacity | 4.35–4.36 (L3130–3148); 5.30–5.32 (L4223–4257) | 4.35: 2D·c₀·t/(zF) has units mol²/(m·C), not m² (A-58). 4.36 (as rendered) makes loss inversely proportional to thickness and is not in Ah. 5.30 and 5.31 are dimensionally consistent. 5.32 (2ρFMδ/M_Li) is not a charge | INVALID DERIVATION (4.35, 4.36, 5.32) | δ_SEI = √(2·D_SEI·c₀·M_SEI·t/ρ_SEI); Q_SEI = 2F·ρ_SEI·A_neg·δ_SEI/M_SEI [C] (÷3600 for Ah), with A_neg the active anode area and 2 electrons per SEI formula unit. Parameters are unavailable |
| M-21 | EKF for SoH | 4.52–4.64 (L3336–3446) | Filter equations correct (2.62–2.66, 4.56–4.62). Capacity is not a state, yet 4.63 reads SoH from "Q̂_k"; 4.64 uses P₁,₁ (SoC variance). "Optimal minimum-variance" holds for the linear Kalman filter, not the EKF | INVALID DERIVATION | Augment x = [SoC, V_RC, R0, Q]ᵀ with Q̇ = 0 + w_Q and dSoC/dt = −I/Q; then SoH = 100·Q̂/Q_initial and σ_SoH = 100·√P_QQ/Q_initial. Q is observable only with sufficient SoC excursion; call the EKF a first-order approximation |
| M-22 | Coulomb counting with voltage correction | 2.61 (L2046–2058) | "SoH_coulomb" undefined (Coulomb counting gives SoC, not capacity); gains not given | NOT VERIFIED | Define the capacity estimator or drop it |
| M-23 | Objective "energy per km" | 2.69 (L2190–2194) | (1/T)∫P dt is average power in W, not Wh/km | INVALID DERIVATION | J₁ = ∫P_batt dt / ∫v dt [J/m]; ×(1/3.6) for Wh/km. 4.66 (normalised energy) is acceptable |
| M-24 | Objective "ageing" | 2.70 (L2196–2212) | Equates ΔSoH/Δt (1/s) with an Ah-based quantity; SoH (fraction) vs Q_loss (Ah) | INVALID DERIVATION | J₂ = 100·Q_loss(Ah over 1,000 equivalent cycles)/Q_nom [% per 1,000 cycles] from a documented ageing model |
| M-25 | Optimisation constraints, knee curvature, crowding distance | 2.68, 2.71–2.74 (L2132–2238) | Correct definitions. For a sampled design, use Schur, not Hurwitz. 2.72 is trivial with integral action. Boundary points get infinite crowding distance (omitted) | VERIFIED WITH CONDITIONS | — |
| M-26 | Regenerative torque limits | L3613–3683, 4.69 | The road-friction limit M·g·µ·r_w is a *wheel* torque, compared inside min() with *motor* torques (a factor G apart), and uses total weight instead of driven-axle load | INVALID DERIVATION | T_road,motor = µ·F_z,driven·r_w/G (with the regeneration-direction efficiency if needed) |
| M-27 | Gain-scheduling interpolation bound | 5.2 (L3831–3841) | The bound h²/8·max‖K″‖ is standard; "< 1 % of gain magnitude" is not computed | VERIFIED WITH CONDITIONS | Compute max‖K″‖ from the schedule |
| M-28 | Certainty equivalence | 5.5–5.6 (L3943–3957) | "Optimal control law takes the same form" is not a theorem for unknown parameters (dual control); 5.6 uses nominal A₀, B₀, not estimates | INVALID DERIVATION | Present certainty equivalence as a heuristic design, with the separation principle only for known-parameter LQG |
| M-29 | MRAC | 5.9–5.13, 5.18–5.20 (L3989–4087) | 5.11: −Γ e xᵀ P B₀ is n×m while K is m×n; 5.19 has the same shape error. LaSalle is used on a non-autonomous system. (e, K̃) → 0 is claimed without persistent excitation. With σ-modification, V̇ ≤ 0 no longer holds | INVALID DERIVATION | For ẋ = Ax + Bu, u = −K̂x + K_r r, matching A − BK* = A_m: K̂̇ = Γ·BᵀP·e·xᵀ (sign of B known). Barbalat's lemma gives e → 0; K̃ → 0 needs persistent excitation; with σ-modification, only uniform ultimate boundedness |
| M-30 | Forgetting-factor RLS | 5.14–5.17 (L4013–4057) | 5.16 denominator must be λ + φᵀPφ (correct only for λ = 1). 5.17 makes λ *increase* with prediction error (the reverse of the intent) and exceed 1 when ρε²/ε₀² > 1 | INVALID DERIVATION | P(t) = (1/λ)[P − Pφφᵀ P/(λ + φᵀPφ)]; any variable-λ rule must decrease λ as error grows and clip λ ≤ 1 |
| M-31 | SPM, Butler–Volmer | 5.21–5.25 (L4093–4155) | Diffusion equation and boundary conditions correct. 5.24 equals the linearisation only if α_a + α_c = 1. 5.25 sign convention unspecified | VERIFIED WITH CONDITIONS | j ≈ j₀(α_a + α_c)Fη/(RT) |
| M-32 | DFN electrolyte balance | 5.27 (L4197) | Source term written with t₊; the standard DFN form uses (1 − t₊⁰) | INVALID DERIVATION | ε_e ∂c_e/∂t = ∇·(D_e,eff∇c_e) + (1 − t₊⁰)·a·j/F |
| M-33 | Lateral, tyre, NN, DDPG, MPC, Monte Carlo and sensitivity formulas | 2.26–2.30, 3.1–3.13 (L1708–1730, L2366–2564) | Standard forms. 2.29: the leading Burckhardt coefficient is not the peak friction. 3.3: the critic update lacks the factor −2 of the loss gradient. 3.10 assumes i.i.d. samples, which LHS samples are not | VERIFIED WITH CONDITIONS | Add citations (Deb 2002, Lillicrap 2016, Morris 1991, Pacejka, Burckhardt) |
| M-34 | Energy and regeneration conventions | 4.70 (L3771–3783), Table 13 work ratio (L4677) | 4.70 is a valid definition (ignores road load during braking). The work-ratio reading is reversed: negative/positive work near 1 means most traction work is later removed by braking | INVALID DERIVATION (interpretation) | State the convention and the terminal-state treatment; the documented model ends every run at rest (EB: kinetic_end_Wh = 0) |
| M-35 | Metric definitions | RMSE, success (L5047), ΔE | RMSE is undefined (sample period, interval, whether stops are included). "Energy improvement > 5 %" is undefined per sample (relative to what?). Specifications differ: 0.5, 0.6, 0.8 and 1.5 m/s | INVALID DERIVATION | Use the pre-registered definitions (`protocol/preregistration.md`; documented ΔE = 100·(E_sched − E_fixed)/E_fixed in Wh/km) |

**Energy conventions in the documented model** (relevant to any retained result)
- **Energy:** E is battery chemical energy per km, ∫V_oc·I dt / distance. It includes
  regenerated energy as negative supply.
- **Losses:**
  - battery losses are I²R0 and V1²/R1;
  - motor and inverter losses follow a constant η, applied asymmetrically between motoring
    and regeneration (MODEL).
- **Terminal state:** every run ends at rest (EB: kinetic_end_Wh = 0). The RC store at the
  end is ≤ 0.026 Wh.
- **Effect:** these terminal-state terms are about 1e-4 of the energy supplied, far below the
  ±1 % decision margin.

---

## 4. Quantitative results: traceability

"Origin" means a run, dataset and analysis procedure that produce the number.

| Thesis number | Location | Origin found? | Verdict | Evidence |
|---|---|---|---|---|
| 12.5 % ± 2.1 % energy improvement | L9 | No | CONTRADICTED | REG C01; CHK-ENERGY-PCT; PRIM ΔE = +0.003 % (S1, SoH 0.8) |
| 15.3 % ± 2.8 % less fade over 1,000 cycles | L9 | No | CONTRADICTED | REG C02; CHK-FADE-PCT; no ageing model can be run (M-19) |
| 95 → 85.3 Wh/km, "9.7 %" | L5468–5472, L6381–6385 | No | CONTRADICTED | CHK-ENERGY-PCT (10.2 %); model 49.9 Wh/km on S1 (PRIM) |
| Fade 16.5 → 14.2 %/1000 cycles, "14 %" | L5476–5480 | No | CONTRADICTED | REG C04 |
| Six-benchmark comparison; Table 35; Tables 38–39 | L7, L6247–6499 | No | NOT VERIFIED (benchmarks) / CONTRADICTED (adaptive vs fixed) | REG C30; PAIRS regeneration identical within 0.01 Wh |
| 1,000-cycle ageing; Figure 11 (1,500 cycles) | L621, L3152–3168 | No | CONTRADICTED | REG C02, C36; CHK-FIG-CYCLES |
| Monte Carlo 100/configuration vs N = 1,000 | L17, L4343, L5016 | No | CONTRADICTED | CHK-MC-COUNT; A-57 |
| Tables 16, 18, 36 | L5034, L5166, L6295 | No | CONTRADICTED | CHK-MC-TABLES; A-20 |
| Morris Tables 17, 19 | L5079, L5207 | No | CONTRADICTED | CHK-MORRIS-DUP |
| Worst cases (two sets), Table 20 | L5100–5290 | No | CONTRADICTED | CHK-WORSTCASE |
| ANOVA F = 45.67, Tukey, Table 38 | L6403–6440 | No | CONTRADICTED | CHK-BONFERRONI (9/18 fail) |
| Cohen's d 0.89/0.78/0.65 | L6450–6454 | No | CONTRADICTED | A-23 |
| Shapiro–Wilk W = 0.987, p = 0.342 | L5177 | No | NOT VERIFIED | REG C14 |
| Sensitivity Tables 21, 39; correlations D.3 | L5314, L6484, L6317 | No | NOT VERIFIED | no runs; R0 effects implausible beside a resistive share of 1.1–2.1 % (EB, documented model) |
| ASIL B, 94 % diagnostic coverage | L5422–5426 | No | CONTRADICTED | REG C17, C18; A-52 |
| S32K144 timings 0.40 ms / 1.2 ms; footprints | L3893–3917, L5353–5367 | No | CONTRADICTED | CHK-SAMPLING; A-26 |
| EKF 2 h convergence, within 1 % | L3503 | No | NOT VERIFIED | REG C29; M-21 |
| Knee point 122 Wh/km, 14.0 %/1000 cycles | L3593 | No | CONTRADICTED | REG C31; outside Figure 9's axis |
| Payback 3.86 / 3.09 years | L5490–5494 | Arithmetic only | CONTRADICTED | A-31 reproduces arithmetic; inputs are C03/C04 (REG C39) |
| TCO 4,750 USD | Table 25 | Arithmetic only | NOT VERIFIED | A-30 sums match; inputs unsourced |
| LCA 45 % / 25 t / Table 27 | L13, L5551–5583 | No | CONTRADICTED | A-39 to A-46 |
| MTBF 80,000 h; warranty 850 M VND | L5722–5758 | Partial | CONTRADICTED | A-47 to A-51 |
| VUC statistics; Tables 12–13 | L4453–4671 | No | CONTRADICTED | CHK-VUC-SPEED/IDLE; A-13 to A-18 |
| Parameters "validated against manufacturer data" | L7, L5980–5988 | No | CONTRADICTED | REG C32; PARAMS |

**What can be traced** (all SIMULATION_SUPPORTED in the dated matrix, within the
documented model only):

| Restated result | Evidence | Conditions that must accompany it |
|---|---|---|
| N01: SoH scheduling (γ = 1) changes energy per km by +0.000 to +0.005 % and tracking RMSE by +0.4 to +2.0 %; no practical difference (±1 % margin) | PRIM, PAIRS, GAMMA | 48 V documented model; flat road; synthetic S1/S2 up to 50 km/h; SoH 0.7–1.0 known; traction limit and friction brake essentially never active |
| N02: a single retuned fixed gain (R × 0.1) beats the scheduled controller on SoH-averaged energy (49.854 vs 49.881 Wh/km) and RMSE (0.038 vs 0.051 m/s) | FAM | best member at the edge of the tested family; the family spans only 0.28 % in energy |
| N03: over 50 paired draws from assumed ranges with velocity noise, mean ΔE = −0.054 % (bootstrap 95 % [−0.058, −0.050]) | ROB | distributions assumed; not an inference about vehicles; no p-values |
| N04: battery resistive losses are 1.1–2.1 % of supplied energy in the tested runs | EB | a decomposition of the tested runs, not a bound on other controllers or plants |
| Cross-implementation: the Modelica controller and plant reproduce the 16 saved runs | XCHK | 554 of 570 checks pass; DASSL only; S1 distance FAIL unresolved; same author; not physical validation |

---

## 5. Claim-by-claim traceability

Column key:
- **Loc.** gives the page (from the thesis's own contents lists) and the `report.md` line.
- **Retain?** answers whether the claim can stay in the final thesis without overstatement:
  - **Yes** — keep as written;
  - **Cond.** — only after the stated correction or conditioning;
  - **No** — remove or replace.
- **Disposition** values: retain, narrow, recalculate, correct citation, remove, seek owner
  confirmation.

### 5.1 Abstract (p. i, L1–L23)

| ID | Loc. | Claim | Cat. | Verdict | Evidence | Method → outcome | Gap | Disposition | Retain? |
|---|---|---|---|---|---|---|---|---|---|
| AB-01 | p. i, L3, L5 | Design **and implementation** of a multi-objective adaptive LQR | IMPL | NOT VERIFIED | REG C23; MODEL | Project search → no thesis code or model; the project re-implemented only the SoH-scheduled weights (`controllers.py`) | Original implementation absent | Narrow: "a controller was specified; a re-implementation of its weight schedule was evaluated" | No |
| AB-02 | p. i, L5 | Pareto optimisation with NSGA-II as contribution 2 | SIM | NOT VERIFIED | REG C31; M-23, M-24 | No run, front or code; objectives dimensionally invalid | Entire study missing | Remove | No |
| AB-03 | p. i, L5 | Ageing model with SEI growth following the Arrhenius law | MATH | INVALID DERIVATION | M-17 to M-20; REG C05 | Dimensional and implementability review → coefficients missing, units mixed | No usable model | Remove or replace with a fully sourced model | No |
| AB-04 | p. i, L5 | SoH estimator = Coulomb counting with voltage correction | IMPL | CONTRADICTED | L2622, L3318 (EKF); REG C29 | Internal comparison → two different estimators called "the" estimator; neither exists | No estimator | Remove; state "SoH assumed known" | No |
| AB-05 | p. i, L7 | Simulations in MATLAB/Simulink and Python | IMPL | NOT VERIFIED | REG C20, C23 | No Simulink models, logs or Python package of the thesis in the project | — | Replace with the project's Python model and commit hash | No |
| AB-06 | p. i, L7 | NEDC, WLTP, CLTC and VUC (600 s, max 50 km/h) | SIM | NOT VERIFIED | REG C07–C09; L5996 | No run on any of these cycles exists; VUC not real | — | Remove; the evaluated profiles are synthetic S1/S2 | No |
| AB-07 | p. i, L7 | Parameters validated against published benchmarks and manufacturer datasheets | PARAM | CONTRADICTED | REG C32; PARAMS | Provenance audit → 20 report_unverified, 11 assumed, 2 standard | — | Remove; say "parameters assumed or taken from the draft without primary source" | No |
| AB-08 | p. i, L7–9 | Significant improvements vs six benchmarks | SIM | NOT VERIFIED | REG C30 | No benchmark implementation except fixed LQR (in the project) | 5 of 6 benchmarks absent | Remove | No |
| AB-09 | p. i, L9 | Up to 12.5 % ± 2.1 % better energy efficiency vs fixed LQR | SIM | CONTRADICTED | REG C01; CHK-ENERGY-PCT; PRIM | Pre-registered experiment → ΔE = +0.003 % (S1, SoH 0.8); the thesis body itself implies 10.2 % | Original conditions undefined | Remove; report N01 with its conditions | No |
| AB-10 | p. i, L9 | 15.3 % ± 2.8 % less capacity fade over 1,000 cycles | SIM | CONTRADICTED | REG C02; CHK-FADE-PCT; PAIRS | Fade stated as 15.3 % and 14 %; no runnable ageing model; peak current equal within 0.002 A | — | Remove | No |
| AB-11 | p. i, L13 | BOM with 18 component categories, supplier assessment, supply-chain risk matrix | ECON | CONTRADICTED | A-35 to A-38 | BOM lines sum to 12,580 USD, not 9,300; cells counted twice; no risk matrix beyond one column | — | Recalculate or remove | No |
| AB-12 | p. i, L13 | Compliance with ECE R100/R13 safety standards | SAFE | CONTRADICTED | L5980 (no experiments); REG C17 | No test of any kind; R100 and R13 address M/N(/O) categories, not L-category micro-EVs (reference knowledge; texts not accessed) | — | Remove | No |
| AB-13 | p. i, L13 | LCA: 45 % less CO₂ than ICE over 150,000 km | ECON | CONTRADICTED | A-39 to A-46; REG C39 | Table 27 totals 14.3 t (text 25 t); grid factor inconsistent; depends on C03/C04 | No sourced LCA | Remove or redo as a sourced LCA | No |
| AB-14 | p. i, L17 | Monte Carlo with 100 trials per configuration | STAT | CONTRADICTED | CHK-MC-COUNT; REG C10 | Also "N = 1,000" (L5016) | No run logs | Remove | No |
| AB-15 | p. i, L17 | t-test and ANOVA with Bonferroni correction | STAT | CONTRADICTED | CHK-BONFERRONI; REG C13 | 9 of 18 reported p-values exceed 0.05/18 | — | Remove | No |
| AB-16 | p. i, L17–19 | Sensitivity across ±30 % variations | STAT | NOT VERIFIED | Tables 21, 39 | No runs or data | — | Remove | No |
| AB-17 | p. i, L19–21 | Failure-mode analysis "ensures safe operation under degraded conditions" | SAFE | CONTRADICTED | L5278 (WC-5 FAIL) | The thesis's own worst case fails; no FMEA/FMEDA exists | — | Remove | No |

### 5.2 Chapter 1 (pp. 1–12, L551–L901)

| ID | Loc. | Claim | Cat. | Verdict | Evidence | Method → outcome | Gap | Disposition | Retain? |
|---|---|---|---|---|---|---|---|---|---|
| C1-01 | p. 1, L555 | IEA GEVO 2024: 14 M EV sales in 2023, +35 %, "over 40 %" of sales by 2030 | LIT | VERIFIED WITH CONDITIONS | WEB: IEA GEVO 2024 outlook page; CleanTechnica summary | 14 M and +35 % match; IEA STEPS gives "almost 40 %" in 2030 (APS ≈ 45 %) | Overstated "over 40 %" | Narrow: "almost 40 % under the stated-policies scenario" | Cond. |
| C1-02 | p. 1, L557 | Micro-EVs defined by "UN Regulations L6e and L7e", < 45 km/h, < 4 kW (L6e) or < 15 kW (L7e) | LIT | CONTRADICTED | WEB: ZEMO summary of Reg. (EU) 168/2013; UK DfT Annex B | L6e/L7e are EU (Reg. 168/2013) categories, not UN regulations; the 45 km/h limit applies to L6e only | EUR-Lex text not accessed | Correct citation and definitions | Cond. |
| C1-03 | p. 1, L559 | Hanoi and HCMC rank among the most polluted cities per the WHO database [2] | LIT | NOT VERIFIED | B-02 | [2] is a global exposure assessment (not opened); no ranking source cited | Source for ranking | Cite a ranking source or remove | Cond. |
| C1-04 | p. 2, L561–571 | Table 1: Vietnam EV sales 2020–2024 ("VAMA Report") | LIT | NOT VERIFIED | A-02 | YoY arithmetic consistent; no bibliographic reference for the data | Source | Seek owner confirmation of the VAMA document; else remove | Cond. |
| C1-05 | p. 2, L561 | CAGR "exceeding 200 %" 2020–2024 | MATH | CONTRADICTED | A-01 | (248,000/3,200)^(1/4) − 1 = 196.7 % | — | Correct to ≈ 197 % (if Table 1 is kept) | Cond. |
| C1-06 | p. 1–3, L575, L587 | Fixed-gain controllers become suboptimal as the battery ages (worse efficiency, faster degradation) | PHYS | NOT VERIFIED | N01, N02 (PRIM, FAM) | Stated as fact without source; in the documented model scheduling did not help and a retuned fixed gain was better | General claim untested beyond one model | Narrow to a hypothesis | Cond. |
| C1-07 | p. 3, L591 | Energy efficiency inherently conflicts with battery longevity | PHYS | NOT VERIFIED | FAM; REG C31 | No source; across LQR weights in the documented model energy and tracking did not conflict | — | Narrow to hypothesis with source | Cond. |
| C1-08 | p. 4, L609 | O1: gains compensate battery-ageing effects on powertrain dynamics | PHYS | NOT VERIFIED | M-16; MODEL; N04 | In the thesis model ΔA alters only the (invalid) battery-current row; in the documented model SoH has no pathway into the velocity dynamics | Mechanism not shown | Narrow | Cond. |
| C1-09 | p. 6, Table 2 | O1 KPI: tracking error reduction ≥ 5 % vs fixed LQR (implied as met) | SIM | CONTRADICTED | PAIRS; REG C12 | Documented model: scheduled RMSE 0.4–2.0 % worse; thesis's 50 % claim contradicted | — | Report the KPI as not met | No |
| C1-10 | p. 6, Table 2 | O2: Pareto front with ≥ 50 solutions | SIM | NOT VERIFIED | REG C31 | Not run | — | Remove or mark unmet | No |
| C1-11 | p. 6, Table 2 | O3: win rate ≥ 4/6 benchmarks | SIM | NOT VERIFIED | REG C30 | Not run | — | Remove or mark unmet | No |
| C1-12 | p. 6, Table 2 | O4: battery lifetime extension ≥ 10 % | SIM | CONTRADICTED | REG C02 | No ageing result exists | — | Mark unmet | No |
| C1-13 | p. 5, L623 | Ageing simulation "must use validated electrochemical models" | MATH | CONTRADICTED | L5998; M-17 to M-20 | The thesis's own model is unvalidated (Limitations) and not implementable | — | Remove requirement or state unmet | No |
| C1-14 | p. 6–7, L688–708 | In-scope: standard cycles, NSGA-II, EKF, Monte Carlo, ANOVA | PLAN | NOT VERIFIED | §4 | None performed in any retrievable form | — | Rescope to what was done | No |
| C1-15 | p. 7, L720 vs L5337, L3919 | HIL out of scope, yet hardware implementation and SIL/PIL are reported | PLAN | CONTRADICTED | REG C19, C20 | Internal comparison | — | Remove hardware/PIL claims | No |
| C1-16 | p. 7, L724 vs §6.4 | Manufacturing out of scope, yet a manufacturing section reports results | PLAN | CONTRADICTED | L5591–5675 | Internal comparison | — | Remove manufacturing results | No |
| C1-17 | p. 7, L732–734 | Assumption 1: grades ≤ 10 %, linearised model valid | PARAM | VERIFIED WITH CONDITIONS | MODEL (flat road); L5258, L6347, Figure 6 | A legitimate assumption, but violated by WC-3 (15 %), D.4 (15 %) and Figure 6 (10° = 17.6 %); the documented model is flat-road only | — | Retain; delete the > 10 % scenarios | Cond. |
| C1-18 | p. 7, L736 | Assumption 2: thermal effects captured through the ageing model | PARAM | NOT VERIFIED | M-19 | No thermal model; ageing model not implementable | — | Remove clause | Cond. |
| C1-19 | p. 7, L742 | Micro-EVs rarely exceed traction limits | PHYS | VERIFIED WITH CONDITIONS | A-11; N01 | Peak wheel force 1,736 N < µ·m·g for any plausible driven-axle share at µ = 0.8; traction limit essentially never active in the documented runs | Dry road, flat, Table 8 values | Retain with conditions | Cond. |
| C1-20 | p. 8, L746 | Typical sensor rates and accuracies | PARAM | NOT VERIFIED | PARAMS (velocity_noise_std) | No source | — | Label as assumption | Cond. |
| C1-21 | p. 8, L750–752 | Assumption 5: LFP cells with parameters identified by Huria et al. [3] from published LFP data | LIT | CONTRADICTED | REG C37; CR | [3] is a 2012 IEVC paper; abstract: NMC/graphite cells | Full text not read | Correct citation; withdraw LFP attribution | No |
| C1-22 | p. 8, L780 | Model calibrated against the Wuling Hongguang Mini EV and VinFast VF3 | PARAM | CONTRADICTED | REG C34; L5994 | Limitations name the Citroën Ami and Wuling instead; no datasheet cited; VF3 (1,035 kg) ≠ model 850 kg | — | Describe the vehicle as hypothetical | No |
| C1-23 | p. 9, L790 | Contribution 1 is novel | LIT | NOT VERIFIED | `docs/literature_review_soh_scheduled_lqr.md`; Table 6 row "Huang et al. 2023" | A limited search found no direct prior work, but the thesis's own Table 6 lists an LQR with SoH-based ageing compensation | Exhaustive search not done | Remove "novel"; position against verified related work | No |
| C1-24 | p. 9, L790 | Re-tuning with SoH maintains optimal performance as R rises and capacity falls | PHYS | CONTRADICTED | N01, N02 | Documented model: no benefit; a retuned fixed gain does better | Other plants untested | Narrow | No |
| C1-25 | p. 9, L792–798 | Exponential stability if ‖K̇‖ < K_max and A − BK(t) Hurwitz | MATH | INVALID DERIVATION | M-11 | K_max must be sufficiently small; Hurwitz wrong for a discrete controller | — | Replace with frozen-time result and slow-variation condition | No |
| C1-26 | p. 9, L802–804 | Contribution 2 reveals fundamental energy–longevity trade-offs | SIM | NOT VERIFIED | REG C31; M-23, M-24 | Not run; objectives invalid | — | Remove | No |
| C1-27 | p. 10, L808–810 | Contribution 3: VUC from traffic-flow data and real-world measurements | LIT | CONTRADICTED | REG C07; L5996 | The thesis itself says "not real measured data" | — | Remove | No |
| C1-28 | p. 10, L816–820 | Contribution 4: robustness framework (100 trials, ±30 %, t-test/ANOVA/Bonferroni) | STAT | CONTRADICTED | REG C10, C13 | — | — | Remove | No |
| C1-29 | p. 10, L824 | Contribution 5: EKF gives optimal minimum-variance SoH estimates, superior to Coulomb counting | MATH | INVALID DERIVATION | M-21; REG C29 | Capacity not a state; EKF not optimal; no implementation | — | Remove | No |
| C1-30 | p. 11, L828 | Thesis organised into seven chapters | — | CONTRADICTED | TOC | There are six chapters | — | Correct | Cond. |

### 5.3 Chapter 2 (pp. 13–49, L903–L2608)

| ID | Loc. | Claim | Cat. | Verdict | Evidence | Method → outcome | Gap | Disposition | Retain? |
|---|---|---|---|---|---|---|---|---|---|
| C2-01 | p. 13, L909 | UNECE Regulations No. 129 (L6e) and No. 136 (L7e) define micro-EVs | LIT | CONTRADICTED | WEB: UN treaty record XI-B-16-136; EUR-Lex Reg. 2014/129 listing | R129 = enhanced child restraint systems; R136 = electric power train safety of L-category vehicles | — | Cite Reg. (EU) 168/2013 for categories | Cond. |
| C2-02 | p. 13, L911–923 | L6e: 350 kg (excl. battery), 4 kW, 45 km/h; L7e: 600 kg (450 kg goods), 15 kW, no speed limit | LIT | CONTRADICTED | WEB: ZEMO; UK DfT Annex B | Under 168/2013: L6e ≤ 425 kg; 4 kW (L6e-A)/6 kW (L6e-B); L7e passenger ≤ 450 kg, utility ≤ 600 kg (reversed in thesis); sub-types have speed limits | Secondary sources; EUR-Lex not accessed | Correct with primary citation | Cond. |
| C2-03 | p. 13, L927 | Wuling Hongguang Mini EV: world's best-selling EV in 2022, > 550,000 units | LIT | NOT VERIFIED | — | No citation; not checked | Source | Cite or remove | Cond. |
| C2-04 | p. 14, L933–947 | Table 3 micro-EV specifications | LIT | NOT VERIFIED | A-12 context; C2-01 | No sources. Internal: Wuling (20 kW, 665 kg, 100 km/h) and VF3 (32 kW, 1,035 kg) exceed the thesis's own L7e limits, so are not micro-EVs by its definition; "Range (WLTP)" unsourced | Manufacturer data | Cite each value or remove; define the category consistently | Cond. |
| C2-05 | p. 14, L949 | VAMA: urban trips 8–12 km; peak speeds rarely > 25 km/h | LIT | NOT VERIFIED | — | No reference | Source | Cite or remove | Cond. |
| C2-06 | p. 14, L951 | Decision 876/QĐ-TTg gives registration-tax exemptions through 2025 | LIT | CONTRADICTED | WEB: luatvietnam (Binh Thuan plan implementing 876); diendandoanhnghiep | 876/QĐ-TTg (22 Jul 2022) is the transport green-energy transition programme; registration fees are set by separate decrees (not verified here) | Exact fee instrument | Correct citation | Cond. |
| C2-07 | p. 14, L951 | Ministry of Transport proposed reduced licensing for L6e/L7e | LIT | NOT VERIFIED | — | No source | — | Cite or remove | Cond. |
| C2-08 | pp. 15–18, L967, L1053, Table 4 | Motor efficiencies, power and torque densities, cost and speed ranges | LIT | NOT VERIFIED | — | Uncited generic ranges | Sources | Cite or remove | Cond. |
| C2-09 | p. 15, L989–1033 | PMSM dq model and torque, Eq. 2.1–2.4 [4] | MATH | VERIFIED WITH CONDITIONS | M-04; CR 10.1109/28.25541 | Standard model; [4] exists but is dated 1989, not 1988 | — | Correct year | Cond. |
| C2-10 | p. 16, L1063–1109 | IM model and slip torque, Eq. 2.5–2.7 | MATH | INVALID DERIVATION | M-05 | Self- instead of leakage inductances | Rendering partly uncertain | Correct or remove (IM unused) | No |
| C2-11 | p. 17, L1139–1147 | SRM torque ½ i² dL/dθ | MATH | VERIFIED WITH CONDITIONS | — | Standard, linear magnetics only | — | State condition | Cond. |
| C2-12 | p. 19, L1177 | Cathode typically a transition-metal oxide, e.g. LiFePO₄ | PHYS | CONTRADICTED | — | LiFePO₄ is a phosphate (olivine), not an oxide | — | Correct wording | Cond. |
| C2-13 | p. 19, L1185 | Typical cell voltages range from 2.5 V (LFP) to 4.2 V (NMC) | PHYS | NOT VERIFIED | — | Mixes cut-off and maximum voltages; uncited | — | Narrow | Cond. |
| C2-14 | p. 19, L1187–1203 | SoC and SoH (capacity) definitions, Eq. 2.9–2.10 | MATH | VERIFIED WITH CONDITIONS | M-19 | Correct definitions; inconsistent with Eq. 4.27, where SoH(0) = 98 % because Q_loss,0 = 2 % | — | Use one definition | Cond. |
| C2-15 | p. 20, L1211–1221 | LFP: 3.2 V, 2.5–3.65 V, 120–160 Wh/kg, 3000+ cycles, stable to 270 °C, 80–100 $/kWh | LIT | NOT VERIFIED | A-37; L5476 | Uncited. Internally contradicted by the BOM cell price (562 USD/kWh) and by fade of 14–16.5 %/1000 cycles (EOL ≈ 1,200–1,400 cycles) | Sources | Cite; remove the contradictions | Cond. |
| C2-16 | p. 20, L1231 vs L1241 | The flat plateau "simplifies" and "complicates" SoC estimation | PHYS | CONTRADICTED | — | Internal contradiction | — | Keep "complicates" only | Cond. |
| C2-17 | pp. 21–23, L1249–1346 | NMC "dominant chemistry"; NMC/LTO/solid-state properties; Table 5 | LIT | NOT VERIFIED | — | Uncited; time-dependent market statement | Sources | Cite or shorten | Cond. |
| C2-18 | p. 23, L1354–1374 | 1-RC Thevenin model, Eq. 2.11–2.12 | MATH | VERIFIED | M-07; MODEL | Matches the documented plant | Uncited | Retain; add a citation | Yes |
| C2-19 | p. 24, L1376–1378 | 6th-order OCV(SoC) polynomial | PARAM | NOT VERIFIED | PARAMS (constant OCV assumed) | No coefficients | — | Remove or supply coefficients and source | Cond. |
| C2-20 | p. 24, L1496–1518; Fig. 4 | LFP plateau 20–80 % SoC motivates Coulomb counting | LIT | NOT VERIFIED | §1.1 (figures) | Uncited; figure carries no data | — | Cite | Cond. |
| C2-21 | p. 25, L1520–1528 | R0(T) = R0,ref(1 + α_T(T − T_ref)), α_T ≈ 0.004/°C for Li-ion | PHYS | CONTRADICTED | M-08 | Wrong sign of the dependence; copper's TCR | — | Replace with an Arrhenius form and identified parameters, or remove | No |
| C2-22 | p. 25, L1536–1556 | Packs 15–100 kWh; drivetrain efficiency 85–95 % vs ICE 20–35 % | LIT | NOT VERIFIED | — | Uncited; 15–100 kWh does not fit micro-EVs (4.8–9.2 kWh in this thesis) | — | Narrow or cite | Cond. |
| C2-23 | p. 27, L1578–1588 | Inverter power balance Eq. 2.16; switching at 5–20 kHz | MATH | VERIFIED WITH CONDITIONS | M-06 | Lossless, amplitude-invariant; switching range uncited | — | State conditions | Cond. |
| C2-24 | p. 27, L1596–1608 | Force balance, rolling resistance, Eq. 2.17–2.18; Crr 0.008–0.015 | MATH | VERIFIED | M-01; MODEL | Correct; Crr range uncited | — | Retain | Yes |
| C2-25 | p. 28, L1608–1620 | Velocity-dependent Crr, Eq. 2.19 | MATH | NOT VERIFIED | M-02 | Unreadable form; no units, no source | — | Remove or rewrite | No |
| C2-26 | p. 28, L1622–1652 | Aero and grade forces; small-angle error negligible for 5–8 % grades | MATH | VERIFIED | M-01 | 0.1 % at 8 % (computed) | — | Retain | Yes |
| C2-27 | p. 28, L1654–1682 | Drivetrain efficiency, traction force, effective mass, Eq. 2.23–2.25 | MATH | VERIFIED WITH CONDITIONS | M-03; A-10 | Regeneration direction; 0.848 vs 0.88 | — | Correct | Cond. |
| C2-28 | p. 29, L1684–1700; Fig. 6 | Force components incl. "Gradient (10°)"; motor meets any demand up to its power limit | SIM | NOT VERIFIED | §1.1 | No data; 10° = 17.6 % grade exceeds Assumption 1 | — | Remove or redraw from the model | No |
| C2-29 | p. 30, L1702–1718 | Lateral bicycle model, Eq. 2.26–2.28 | MATH | VERIFIED | M-33 | Standard; outside scope | — | Optional: remove (unused) | Yes |
| C2-30 | p. 30, L1720–1734 | Burckhardt and Pacejka models; µ = 0.8 dry asphalt | MATH | VERIFIED WITH CONDITIONS | M-33 | Burckhardt leading coefficient ≠ peak; µ uncited | — | Correct wording; cite | Cond. |
| C2-31 | p. 31, L1740–1770 | CT-LQR and ARE; P unique and positive definite; closed loop asymptotically stable | MATH | VERIFIED WITH CONDITIONS | M-09 | P ≻ 0 needs observability | — | Correct | Cond. |
| C2-32 | p. 32, L1772–1782 | Bryson's rule [5] | MATH | VERIFIED | B-05 | Rule correct as stated; its application (C27) is contradicted | — | Retain | Yes |
| C2-33 | p. 32, L1784–1792 | Lyapunov derivative Eq. 2.38 | MATH | INVALID DERIVATION | M-10 | Open-loop matrix used | — | Replace | No |
| C2-34 | p. 32–33, L1794–1830 | DT-LQR, ZOH, DARE and gain, Eq. 2.39–2.42 | MATH | VERIFIED | M-14; `controllers.py` (`zoh`, `dlqr`) | Matches the implementation used in the project | — | Retain | Yes |
| C2-35 | p. 33, L1834–1844 | Ts ≤ π/ω_bw; Ts = 10 ms adequate | MATH | VERIFIED WITH CONDITIONS | M-15; PAIRS | Theoretical limit only; 10 ms adequate in the documented model (RMSE ≈ 0.05 m/s) | — | Narrow | Cond. |
| C2-36 | p. 33, L1846–1862 | Integral augmentation, Eq. 2.43–2.45 | MATH | VERIFIED | M-14 | Standard | — | Retain | Yes |
| C2-37 | p. 34, L1864–1900 | Hamiltonian derivation of the ARE; LQR optimal and stabilising | MATH | INVALID DERIVATION | M-12 | "λ̇ = 0 ⇒ λ = Px" invalid; conclusion standard | — | Replace derivation | No |
| C2-38 | p. 34, L1902–1920 | Return-difference inequality and robustness bounds, Eq. 2.51–2.53 | MATH | INVALID DERIVATION | M-13 | Mislabelled; vacuous; DT margins not guaranteed | — | Replace or remove | No |
| C2-39 | p. 35, L1926–1936 | Ageing mechanisms; SEI dominates calendar ageing and contributes to cycle ageing for LFP | LIT | NOT VERIFIED | — | Uncited (standard content) | Citation | Cite a review chosen by the author | Cond. |
| C2-40 | p. 35–36, L1938–1962 | Parabolic SEI law Eq. 2.54 from [6]; Ea = 31.5 kJ/mol for LFP | MATH | INVALID DERIVATION | M-17; OA abstract of [6] | Calendar term proportional to Ah; √Ah not √t; [6] describes a first-principles model; Ea unsourced | Full text of [6] not read | Remove or replace with sourced laws | No |
| C2-41 | pp. 36–37, L1964–2010 | Stress-factor model; k_SoC 0.5, k_C 0.1, n_C 0.5, n_DoD 1.2 | PARAM | NOT VERIFIED | M-18 | No sources; f_C ≠ 1 at the reference | — | Remove or source | No |
| C2-42 | p. 38, L2012; Fig. 7 | Figure 7 shows a capacity-loss surface over time, temperature and SoC | SIM | CONTRADICTED | §1.1 | The figure shows three temperature curves against time; no data | — | Remove | No |
| C2-43 | pp. 38–39, L2014–2058 | SoH method taxonomy; thesis uses Coulomb counting with PI voltage correction (Eq. 2.61) | MATH | NOT VERIFIED | M-22; REG C29 | Estimator undefined and not implemented | — | Remove or define | No |
| C2-44 | p. 39, L2060–2080 | EKF equations, Eq. 2.62–2.66 | MATH | VERIFIED | M-21 | Standard | — | Retain if the EKF is kept | Yes |
| C2-45 | p. 39, L2082 | EKF gives optimal minimum-variance estimates under Gaussian noise | MATH | INVALID DERIVATION | M-21 | True of the linear KF only | — | Correct | No |
| C2-46 | p. 40, L2084–2112; Fig. 8 | EKF superior, bounded divergence; Coulomb counting drifts | SIM | NOT VERIFIED | REG C29; §1.1 | No implementation, no data | — | Remove | No |
| C2-47 | pp. 40–41, L2088–2152 | Multi-objective optimisation, Pareto dominance, crowding distance Eq. 2.67–2.68 | MATH | VERIFIED WITH CONDITIONS | M-25 | Correct; boundary rule omitted; NSGA-II (Deb et al. 2002) uncited | Citation | Add citation | Cond. |
| C2-48 | p. 41, L2156–2176; Fig. 9 | Typical Pareto front 100–180 Wh/km, 1–5 %/1000 cycles | SIM | NOT VERIFIED | §1.1; L3593 | Illustrative, no data; inconsistent with the knee point at 14 %/1000 cycles | — | Remove or label "schematic" | Cond. |
| C2-49 | p. 41, L2178–2186 | NSGA-II components (sorting, crowding, tournament, SBX, polynomial mutation) | LIT | VERIFIED WITH CONDITIONS | — | Correct description of NSGA-II; uncited | Citation | Add citation | Cond. |
| C2-50 | p. 41, L2190–2212 | Objectives f1 (energy/km), f2 (ageing rate), Eq. 2.69–2.70 | MATH | INVALID DERIVATION | M-23, M-24 | Units | — | Replace | No |
| C2-51 | p. 42, L2214–2238 | Constraints Eq. 2.71–2.73; knee curvature Eq. 2.74 | MATH | VERIFIED WITH CONDITIONS | M-25 | Schur vs Hurwitz; 2.72 trivial | — | Correct | Cond. |
| C2-52 | p. 42, L2242 | "A comprehensive literature review covering 15+ research papers" | LIT | CONTRADICTED | Table 6; B-07 to B-10 | 12 of 15 Table 6 studies have no reference; refs 7–9 not found as cited | — | Remove claim | No |
| C2-53 | p. 42, L2244–2324 | Algorithm 1 NSGA-II for LQR weights | IMPL | NOT VERIFIED | REG C31 | No code, no run | — | Remove or label as proposed method | No |
| C2-54 | p. 43, L2328 | Qiao et al. [7]: LQR-based fuzzy controller, 23.5 % energy recovery gain, PSO-tuned | LIT | NOT VERIFIED | B-07; CR | Printed reference not found; a topically similar paper with different authors, title and pages exists (Saxena et al. 2023) | Intended source unknown | Seek owner confirmation; else remove | No |
| C2-55 | p. 43, L2330 | Wang et al. [8]: DP braking distribution, 18.2 % | LIT | NOT VERIFIED | B-08; CR | Not found | — | Remove unless a DOI is supplied | No |
| C2-56 | p. 43, L2332 | Lin et al. [9]: MPC with battery constraints, 15.7 % | LIT | CONTRADICTED | B-09; CR | Printed locator (Control Eng. Pract. 105789) is a marine-vessel paper in vol. 143 | — | Remove | No |
| C2-57 | p. 43, L2334–2362 | EMS categories; fuzzy-logic structure; fuzzy LQR concept | LIT | VERIFIED WITH CONDITIONS | — | Standard descriptions; uncited | Citations | Cite | Cond. |
| C2-58 | p. 44, L2364–2380 | NN approximation (Eq. 3.1); NN adaptive control gives stability guarantees if the error is bounded | MATH | VERIFIED WITH CONDITIONS | M-33 | Guarantees need specific adaptive laws and robustification; uncited | — | Narrow; cite | Cond. |
| C2-59 | pp. 44–45, L2382–2478 | DDPG update rules (Eq. 3.2–3.3, 3.6); MPC formulation (3.4–3.5), complexity O(Hn³) | MATH | VERIFIED WITH CONDITIONS | M-33 | 3.3 sign/factor; complexity for structured solvers only; DDPG (Lillicrap 2016) uncited | — | Correct; cite | Cond. |
| C2-60 | p. 46, L2480–2564 | Monte Carlo mean, variance, CI (3.8–3.10); sensitivity and Morris EE (3.11–3.13) | MATH | VERIFIED WITH CONDITIONS | M-33 | i.i.d. assumption (not LHS); Morris (1991) uncited | — | Correct; cite | Cond. |
| C2-61 | p. 48, L2566–2586 | Table 6: 15 studies of EV powertrain control | LIT | NOT VERIFIED | B-07 to B-10 | 12 rows have no reference entry; 3 references not found as cited | Sources | Remove (`docs/thesis_closeout_repair_sheet.md` §1) | No |
| C2-62 | p. 49, L2592–2602 | Table 7: proposed work has "1000 cycles" verification and "t-test, ANOVA" | LIT | CONTRADICTED | REG C02, C13 | — | — | Remove | No |
| C2-63 | p. 49, L2590, L2608 | Integration "explored in isolation" before; "significant advance in the state of the art" | LIT | CONTRADICTED | Table 6 rows Chen 2024, Huang 2023 | Internal: the thesis's own table lists LQR + ageing + NSGA-II and LQR with SoH-based compensation | External novelty not established | Remove | No |
| C2-64 | p. 49, L2604 | Significance testing ensures improvements are not due to random variation | STAT | INVALID DERIVATION | REG C13 | Model outputs under assumed distributions; tests do not establish real-world effects | — | Remove | No |
| C2-65 | p. 49, L2606 | EKF + Coulomb counting gives accurate tracking and robust degradation monitoring | SIM | NOT VERIFIED | REG C29 | Not implemented | — | Remove | No |

### 5.4 Chapter 3 (pp. 50–81, L2610–L4283)

| ID | Loc. | Claim | Cat. | Verdict | Evidence | Method → outcome | Gap | Disposition | Retain? |
|---|---|---|---|---|---|---|---|---|---|
| C3-01 | p. 50, L2618 | Architecture with an "LFP 48V/100Ah" pack | PARAM | OWNER CONFIRMATION REQUIRED | A-38; `docs/battery-data-feasibility-audit.md` | Matches Table 8; BOM gives 16 × 3.2 V = 51.2 V with no cell part number | Intended pack | Default: "generic 48 V, 100 Ah model pack; BOM illustrative, not the same pack" | Cond. |
| C3-02 | p. 50, L2622 | An EKF-based SoH estimator supplies the adaptive gain | IMPL | CONTRADICTED | L5 (Coulomb counting); REG C29 | Internal conflict; nothing implemented | — | State "SoH assumed known" | No |
| C3-03 | p. 50, L2624 | Sampling period 10 ms | PARAM | VERIFIED WITH CONDITIONS | PARAMS (`sample_time` 0.01 s); CHK-SAMPLING | Used by the documented controllers; the thesis elsewhere says a 1 ms loop (L5357) | — | Use 10 ms throughout | Cond. |
| C3-04 | pp. 50–51, L2628–2708 | State-space model Eq. 4.1–4.5 | MATH | INVALID DERIVATION | M-16; CHK-AMATRIX-DIM; REG C24 | Dimensional audit with Pint → traction entry has wrong units; structure not physical | — | Replace with the documented model | No |
| C3-05 | p. 53, L2740–2756 | Controllability and observability matrices have full rank | MATH | NOT VERIFIED | REG C25; tests/test_controllers.py | Thesis matrices lack L_eq, K_e (rank symbolic only); documented design model has rank 3 (tested) | — | Restate for the documented model | Cond. |
| C3-06 | p. 52, L2716 | Mass 850 kg = curb + 150 kg payload | PARAM | NOT VERIFIED | PARAMS (report_unverified); REG C35 | No source; Monte Carlo centres on curb + 75 kg | — | Label as assumed | Cond. |
| C3-07 | p. 52, L2717 | Frontal area 2.2 m² ("micro-EV typical") | PARAM | NOT VERIFIED | PARAMS; L6059 | Appendix A says "design specification" | — | Label as assumed | Cond. |
| C3-08 | p. 52, L2718 | C_d = 0.35 from wind-tunnel data | PARAM | CONTRADICTED | REG C33; L6058 | Appendix A: "Micro-EV average" | — | Label as assumed | Cond. |
| C3-09 | p. 52, L2719 | r_w = 0.28 m = 13″ wheel diameter / 2 | PARAM | CONTRADICTED | A-04 | 13″/2 = 0.165 m (rim only) | — | Keep 0.28 m as assumed tyre radius; delete the note | Cond. |
| C3-10 | p. 52, L2720–2724 | G 6.5; 18 kW peak; 85 N·m; 837 rad/s = 8000 rpm | PARAM | VERIFIED WITH CONDITIONS | A-03; PARAMS | Unit conversion correct; values unsourced (report_unverified) | Source | Label as assumed | Cond. |
| C3-11 | p. 52, L2721 | η_dt = 0.88 combined | PARAM | CONTRADICTED | A-10; PARAMS (`gear_efficiency`, `motor_inverter_efficiency`) | Appendix A components multiply to 0.848 | — | Use one consistent set | Cond. |
| C3-12 | p. 52, L2725–2727 | Battery 48 V nominal, 100 Ah, LFP | PARAM | OWNER CONFIRMATION REQUIRED | A-38; repair sheet §2 | Generic model pack; BOM pack differs (51.2 V) | Cell part number, series/parallel configuration | Default as C3-01 | Cond. |
| C3-13 | p. 52, L2728–2733 | PMSM parameters R_s 0.02 Ω, L_d = L_q 8 mH, λ_m 0.175 Wb, J_m 0.05, B_m 0.001 | PHYS | CONTRADICTED | A-05 to A-07 | On a 48 V bus: back-EMF at base speed 37.1·p V > 27.7 V; 85 N·m only below 0.46 m/s; L/R = 400 ms, not "≈20 ms" | — | Remove the motor model or supply a consistent 48 V motor; the documented model does not use these values | No |
| C3-14 | p. 53, L2758–2796 | ZOH discretisation, truncated series Eq. 4.9–4.10 | MATH | VERIFIED WITH CONDITIONS | M-14 | Series truncation; exact `expm` used in the project | — | State truncation | Cond. |
| C3-15 | p. 54, L2800 | "Ts ≤ π/ω_max = π/100 = 31.4 ms for a 10 Hz bandwidth" | MATH | CONTRADICTED | A-09 | 10 Hz = 62.8 rad/s | — | Correct | Cond. |
| C3-16 | p. 54, L2802–2806 | Motor electrical time constant ≈ 20 ms needs Ts ≤ 2 ms; Ts = 10 ms chosen | MATH | CONTRADICTED | A-07, A-08 | Self-contradictory; also 400 ms from Table 8 | — | Rewrite the sampling rationale | No |
| C3-17 | p. 54, L2820–2828 | DARE solved "iteratively using the Schur method"; gain Eq. 4.12 | MATH | VERIFIED WITH CONDITIONS | M-14 | The Schur method is direct | — | Correct wording | Cond. |
| C3-18 | pp. 54–55, L2830–2912 | Augmented model with integral action Eq. 4.13–4.20 | MATH | VERIFIED WITH CONDITIONS | M-14 | Correct structure; state order differs from 4.1; symbol "C_d" reused | — | Correct notation | Cond. |
| C3-19 | p. 55, L2916–2942 | Ageing model 4.21–4.24 "calibrated for LFP"; α₀ 5.10e-4 Ah^1/2, β₀ 4.56e-4 [6]; E_a 31.5/20 kJ/mol | MATH | INVALID DERIVATION | M-19; REG C05; B-06 | k_c, k_cal missing; unit mixing; [6] abstract does not describe these coefficients | Full text of [6] | Withdraw | No |
| C3-20 | p. 56, L2944–2958 | Calendar term γ(SoC)√t with γ₀ = 3e-3 Ah^-1/2 [10] | MATH | INVALID DERIVATION | M-19; B-10 | Units; vanishes at SoC 0.5 as rendered; [10] not found | Possible lost "1 +" | Withdraw | No |
| C3-21 | p. 56, L2960–2968 | SoH from capacity loss Eq. 4.27; EOL at 80 % SoH | MATH | VERIFIED WITH CONDITIONS | C2-14 | Definitions fine; SoH(0) = 98 %; EOL convention uncited | — | Correct | Cond. |
| C3-22 | p. 56, L2970–2976 | R0(SoH), R1(SoH) with k_R 0.5, k_R1 0.3 "for LFP" | PARAM | NOT VERIFIED | PARAMS (report_unverified) | No source; used as-is in the documented model | Source | Label as assumed (already in PARAMS) | Cond. |
| C3-23 | p. 56, L2978–3074 | Table 9 ageing parameters with references [6], [10] | LIT | NOT VERIFIED | B-06, B-10 | [6] does not describe them (abstract); [10] not found | — | Remove (repair sheet §1) | No |
| C3-24 | p. 57, L3076–3128 | Ageing model supports warranty calculations; stress model "enables accurate prediction" | SIM | NOT VERIFIED | M-18 | No implementation, no validation | — | Remove | No |
| C3-25 | p. 57, L3130–3150 | SEI parabolic growth Eq. 4.35; capacity loss Eq. 4.36 | MATH | INVALID DERIVATION | M-20; A-58 | Units | — | Replace (M-20) or remove | No |
| C3-26 | p. 58, L3152–3168; Fig. 11 | Adaptive LQR slows fade by moderating peak currents; Pareto controller ages least | SIM | CONTRADICTED | REG C36; PAIRS | Peak current 274.794 vs 274.793 A (S1, SoH 0.8); figure has no data; horizon 1,500 vs 1,000 cycles | — | Remove | No |
| C3-27 | p. 58, L3170 | Ageing model validated against accelerated-ageing data within 5 % over 1,000 cycles | SIM | CONTRADICTED | REG C06; L5998 | No dataset; the Limitations say validation is still required | — | Remove | No |
| C3-28 | p. 58, L3174–3194 | A(t) = A₀ + ΔA(SoH) compensates ageing-induced dynamics changes | MATH | NOT VERIFIED | M-16; MODEL | ΔA alters only the invalid battery-current row | — | Remove | No |
| C3-29 | p. 59, L3196–3210 | Q(SoH), α_v, R(SoH) laws Eq. 4.39–4.41 | MATH | VERIFIED WITH CONDITIONS | `controllers.py` `scheduled_weights`; PARAMS (γ_v = γ_u = 1 assumed) | Implemented as written (α_v on the second state); γ values not given in the thesis | γ values | Retain with γ stated as assumed | Cond. |
| C3-30 | p. 59, L3212–3216 | Gain recomputed from the Riccati equation at each sampling instant | MATH | VERIFIED WITH CONDITIONS | M-14 | Writes A, B for A_d, B_d; elsewhere lookup tables (L3318, L3825) | — | Unify | Cond. |
| C3-31 | pp. 59–60, L3218–3300 | Lyapunov proof: exponential stability under Conditions 1–3 | MATH | INVALID DERIVATION | M-11; REG C26 | Circular Condition 3; underived bound | — | Replace (M-11) | No |
| C3-32 | p. 61, L3302–3308 | SoH estimator's low-pass filtering limits gain variation | IMPL | NOT VERIFIED | — | No estimator | — | Remove | No |
| C3-33 | p. 61, L3328; Appendix B | Integral gain increases as SoH decreases | SIM | CONTRADICTED | REG C28; PRIM | With the thesis's weight laws on a consistent model the gains fall (K_e 196.0 → 184.3 at SoH 0.8); the thesis's own laws (Q down, R up) make control less aggressive | — | Remove | No |
| C3-34 | p. 62, L3332–3362 | Battery state model for the EKF, Eq. 4.52–4.53 | MATH | VERIFIED WITH CONDITIONS | M-21 | Standard ECM-EKF states; no capacity state | — | See C3-35 | Cond. |
| C3-35 | pp. 63–64, L3422–3446 | SoH from estimated capacity Q̂_k; σ_SoH from P₁,₁ | MATH | INVALID DERIVATION | M-21 | Capacity not a state; P₁,₁ is SoC variance | — | Replace (M-21) or remove | No |
| C3-36 | p. 64, L3450–3479 | EKF advantages; 10 Hz update; Table 10 accuracies (5–10/3–5/1–3 %) | LIT | NOT VERIFIED | — | Uncited; not implemented | — | Remove numbers or cite | Cond. |
| C3-37 | p. 64, L3481–3507; Fig. 13 | EKF converges in ≈ 2 h to within 1 %; Coulomb counting 5–8 % after 500 h; "this demonstration validates the EKF" | SIM | NOT VERIFIED | REG C29; §1.1 | No data. Internal: "500 h" vs a 0–1,000 h axis; SoH falling toward ≈ 75–80 % in ≈ 1,000 h conflicts with "3000+ cycles" | — | Remove | No |
| C3-38 | p. 65, L3513–3533 | Weight parameterisation (5 variables); normalised objectives Eq. 4.66–4.67 | MATH | VERIFIED WITH CONDITIONS | M-23 | Dimensionless and acceptable; inconsistent with Eq. 2.69–2.70 | — | Unify | Cond. |
| C3-39 | p. 66, L3535–3559, L3605–3607 | NSGA-II settings; "converges after 200 generations" | SIM | NOT VERIFIED | REG C31 | No run (20,000 lifetime evaluations claimed) | — | Remove the result statement | No |
| C3-40 | p. 66, L3593 | Knee point ≈ 122 Wh/km and 14.0 %/1000 cycles | SIM | CONTRADICTED | REG C31; PRIM | Outside Figure 9's 1–5 % axis; vs 85.3–95 Wh/km elsewhere and 49.9 Wh/km in the documented model | — | Remove | No |
| C3-41 | p. 67–68, L3613–3683 | Regenerative torque limits, Eq. 4.69 | MATH | INVALID DERIVATION | M-26 | Wheel vs motor torque mixed; total vs axle load | — | Correct | Cond. |
| C3-42 | p. 68–69, L3685–3769; Algorithm 3 | SoC/SoH-aware regeneration limits, incl. 80 % regeneration cut below 15 % SoC | PHYS | NOT VERIFIED | — | No rationale for limiting charging at low SoC; thresholds unsourced; not implemented | — | Justify or remove | Cond. |
| C3-43 | p. 69, L3771–3785 | Recovery efficiency Eq. 4.70 | MATH | VERIFIED WITH CONDITIONS | M-34 | Ignores road load during braking | — | State condition | Cond. |
| C3-44 | p. 69, L3787 | Regeneration recovers 20–40 % of braking energy, i.e. 10–20 % overall efficiency gain | LIT | NOT VERIFIED | — | Uncited | — | Cite or remove | Cond. |
| C3-45 | p. 69, L3789 | Adaptive LQR maximises time spent in regeneration | SIM | CONTRADICTED | REG C30; PAIRS | Regenerated energy identical within 0.01 Wh between controllers | — | Remove | No |
| C3-46 | p. 69, L3791–3809 | Brake-blending law Eq. 4.71 | MATH | VERIFIED | — | Definition | — | Retain (if regeneration kept) | Yes |
| C3-47 | p. 70, L3815–3829 | Three-layer architecture; 11 gain matrices on a 100–50 % SoH grid | IMPL | CONTRADICTED | L6199–6219 | The C code has a 7-entry table (1.00–0.70) and clamps SoH at 0.70 | — | Unify | No |
| C3-48 | p. 71, L3831–3841 | Interpolation error bound; "< 1 % of gain magnitude" | MATH | VERIFIED WITH CONDITIONS | M-27 | Bound correct; percentage not computed | — | Compute or remove the number | Cond. |
| C3-49 | p. 71, L3843–3857 | Memory footprint; deployable on "16-bit" MCUs such as NXP S32K144 or TI TMS570 | IMPL | CONTRADICTED | L5339; A-26 | Both are 32-bit Arm devices (the thesis's own L5339 says so); footprints conflict | — | Correct; drop footprint figures without a build | No |
| C3-50 | p. 71, L3859 | Integration via the "standard OBD-II/CAN messaging format" for control | IMPL | CONTRADICTED | — | OBD-II (SAE J1979) is a diagnostic protocol, not a control-message format (reference knowledge; standard not accessed) | — | Correct wording | Cond. |
| C3-51 | pp. 71–72, L3861–3889 | CAN message set; safety functions (watchdog, plausibility, 200 N·m/s rate limit, fallback P controller) | PLAN | NOT VERIFIED | — | Design intent; nothing implemented | — | Retain only as a proposed design | Cond. |
| C3-52 | p. 72, L3891–3917 | Compute cost 1.2 ms per 10 ms cycle and 3.1 ms EKF; 15 % CPU | IMPL | CONTRADICTED | A-24, A-25; CHK-SAMPLING; REG C19 | Sums correct; no hardware; conflicts with 0.40 ms in a 1 ms loop | — | Remove | No |
| C3-53 | p. 72, L3919 | Verified through SIL and PIL testing | IMPL | NOT VERIFIED | REG C20 | No artefacts | — | Remove | No |
| C3-54 | p. 73–74, L3921–3939 | Parametric-uncertainty formulation Eq. 5.3–5.4 | MATH | VERIFIED WITH CONDITIONS | M-28 | Correct formulation; "Equation ??" broken reference | — | Fix reference | Cond. |
| C3-55 | p. 74, L3941–3957 | Certainty equivalence gives the optimal adaptive law | MATH | INVALID DERIVATION | M-28 | — | — | Rephrase as heuristic | No |
| C3-56 | p. 75, L3959–3985 | Gain scheduling offers guaranteed stability at each operating point and robustness to estimation errors | MATH | VERIFIED WITH CONDITIONS | M-11 | Frozen-point stability only; robustness unshown | — | Narrow | Cond. |
| C3-57 | pp. 75–76, L3987–4009 | MRAC law Eq. 5.11 and σ-modification Eq. 5.13 | MATH | INVALID DERIVATION | M-29 | Matrix shape and sign | — | Replace or remove (MRAC unused) | No |
| C3-58 | p. 76, L4011–4057 | FF-RLS Eq. 5.14–5.16; λ choices; adaptive λ Eq. 5.17 | MATH | INVALID DERIVATION | M-30 | Denominator; reversed λ adaptation | — | Correct or remove | No |
| C3-59 | p. 77, L4059–4087 | MRAC Lyapunov proof; LaSalle ⇒ asymptotic stability of (e, K̃) = (0, 0) | MATH | INVALID DERIVATION | M-29 | Non-autonomous; no persistent excitation | — | Remove | No |
| C3-60 | p. 78, L4093–4159 | SPM, Butler–Volmer, terminal voltage; SPM within 5 % for C/3–1C | MATH | VERIFIED WITH CONDITIONS | M-31 | Equations standard with conditions; 5 % accuracy uncited | — | Cite or remove the accuracy | Cond. |
| C3-61 | p. 79, L4161–4203 | DFN electrolyte equation 5.27; "12 coupled PDEs"; 10–100× real time; GITT/EIS/DVA | MATH | INVALID DERIVATION | M-32 | t₊ vs (1 − t₊); PDE count and speed uncited | — | Correct or remove | No |
| C3-62 | p. 79, L4205–4215 | Coupled ECM–electrochemical model within 2 % of experimental data across all conditions; HIL-ready | SIM | NOT VERIFIED | REG C22 | No experimental data; no model | — | Remove | No |
| C3-63 | p. 80, L4217–4247 | SEI growth rate and resistance, Eq. 5.30–5.31 | MATH | VERIFIED WITH CONDITIONS | M-20 | Dimensionally consistent; uncited | — | Cite | Cond. |
| C3-64 | p. 80, L4249–4257 | Capacity fade from SEI, Eq. 5.32 | MATH | INVALID DERIVATION | M-20 | Units | — | Replace (M-20) | No |
| C3-65 | p. 81, L4259–4283 | E_a = 22.0 kJ/mol (graphite–LiCoO₂); empirical calendar and cycle laws | LIT | NOT VERIFIED | — | Uncited; LCO, not LFP; conflicts with 31.5/20 kJ/mol | — | Remove or source | Cond. |

### 5.5 Chapter 4 (pp. 82–97, L4285–L5008)

| ID | Loc. | Claim | Cat. | Verdict | Evidence | Method → outcome | Gap | Disposition | Retain? |
|---|---|---|---|---|---|---|---|---|---|
| C4-01 | p. 82, L4289–4313 | MATLAB R2023a/Simulink 10.6, Python 3.10 environment | IMPL | NOT VERIFIED | REG C23 | No artefacts; version pairing not checked | — | Replace with project environment (`uv.lock`, commit) | No |
| C4-02 | p. 82–83, L4315–4343 | Fixed-step Euler plant + backward-Euler controller; Table 11 with rtol 1e-6/atol 1e-8 | IMPL | CONTRADICTED | — | Tolerances have no meaning for a fixed-step Euler solver; "backward Euler" is undefined for a discrete controller | — | Replace with the documented solver (RK4, 1 ms) | No |
| C4-03 | p. 83, L4325 | SIL mode with Embedded Coder verifies code generation | IMPL | NOT VERIFIED | REG C20 | No artefacts | — | Remove | No |
| C4-04 | p. 83, L4342–4349 | Seed 42; 100 Monte Carlo trials | STAT | CONTRADICTED | CHK-MC-COUNT | Conflicts with N = 1,000 | — | Remove | No |
| C4-05 | p. 83, L4351 | All scripts, models and data are version-controlled with Git | IMPL | OWNER CONFIRMATION REQUIRED | REG C23 | No such repository in the project | Repository outside the project? | Default: replace with this project's repository and commit hash | Cond. |
| C4-06 | p. 84, L4353–4359 | Platform validated: energy within 5 % of WLTP, tracking within 3 %, SoC within 2 % | SIM | NOT VERIFIED | REG C22 | No reference data named | — | Remove; state "not validated against a vehicle" | No |
| C4-07 | p. 84, L4373–4375 | Test matrix 6 controllers × 4 cycles × 100 = 2,400 | STAT | CONTRADICTED | A-57; L6407 (μ₁…μ₇) | Seven controllers are compared | — | Remove | No |
| C4-08 | pp. 84–85, L4381–4395 | NEDC: 11 km, 1,180 s (780 + 400), 120 km/h, 33.6 km/h, 1.04 m/s² | LIT | VERIFIED WITH CONDITIONS | CHK-CYCLE-SPEEDS | Internally consistent; matches the commonly published UN R83 profile (reference knowledge; not accessed); uncited | Citation | Cite | Cond. |
| C4-09 | p. 85, L4397–4409 | WLTP: 23.6 km, 1,800 s, 131 km/h, 46.5 km/h, 1.67 m/s² | LIT | CONTRADICTED | CHK-CYCLE-SPEEDS | 23.6 km/1,800 s = 47.2 km/h; the official class 3b distance is ≈ 23.27 km (UN GTR 15; not accessed) | — | Correct with citation | Cond. |
| C4-10 | p. 85, L4411 | WLTP Class 3 most representative of micro-EV operation | PHYS | CONTRADICTED | A-12 | PMR 21.2–25.7 W/kg → Class 1–2 (class limits 22 and 34 W/kg, UN GTR 15; not accessed) | — | Correct | Cond. |
| C4-11 | p. 85, L4413–4427 | CLTC: 14.5 km, 1,800 s, 114 km/h, average 37.8 km/h | LIT | CONTRADICTED | A-56 | 14.5 km/1,800 s = 29.0 km/h (as in Table 12) | — | Correct | Cond. |
| C4-12 | pp. 86–87, L4429–4467 | VUC derived from GTMC and 2023 HCMC survey traffic data; its statistics | SIM | CONTRADICTED | REG C07, C08; CHK-VUC-SPEED/IDLE; L5996 | Not real data; distance/time and idle statistics impossible together | — | Remove | No |
| C4-13 | p. 86, L4441–4451 | Features of Vietnamese urban driving (4–6 intersections/km, 15–20 % signal time, 25–35 km/h) | LIT | NOT VERIFIED | — | No references | — | Cite or remove | Cond. |
| C4-14 | p. 88, L4497–4501 | VUC: highest stop frequency; "high kinetic energy density (5.8 km covered in 600 s)" | SIM | CONTRADICTED | CHK-VUC-SPEED | 5.8 km in 600 s is 34.8 km/h, not 28.5 | — | Remove | No |
| C4-15 | p. 88, L4503–4516 | Table 12 cycle metrics (accelerations, stops, idle, kinetic energy, regeneration potential) | SIM | CONTRADICTED | A-15 to A-17; CHK-VUC-IDLE | VUC "kinetic energy" 1.5 kWh = 66 full stops from 50 km/h and > 0.55 kWh supplied; no time series | — | Remove VUC column; cite the official cycles | No |
| C4-16 | pp. 89–90, L4518–4534; Algorithm 4 | Markov-chain random cycles validated against VUC (±5 % speed, ±20 % stops, KS p > 0.05) | SIM | CONTRADICTED | A-18; L4602 | Random cycles average 34.1–35.5 km/h vs 28.5 (+20–25 %); Random 3's −1.52 m/s² breaks the ±1.5 m/s² limit; no VUC series to train on | — | Remove | No |
| C4-17 | p. 90, L4536–4620 | Drive-cycle library includes 100 Markov cycles and real-world traces | SIM | CONTRADICTED | L5996 | No traces exist | — | Remove | No |
| C4-18 | p. 91, L4654–4671 | Table 13 work, work ratio, regeneration potential, RMS acceleration (7 cycles) | SIM | CONTRADICTED | A-13, A-14 | VUC positive work 95 kJ < rolling work 387 kJ < road-load bound 643 kJ | — | Remove | No |
| C4-19 | p. 91, L4673–4681 | VUC regeneration potential highest because motor efficiency is high at low speed; random cycles validate the Markov approach | SIM | NOT VERIFIED | MODEL | No efficiency map; no data | — | Remove | No |
| C4-20 | p. 91, L4677 | Work ratio near 1 indicates efficient driving with minimal braking | PHYS | INVALID DERIVATION | M-34 | Reversed interpretation | — | Remove or correct | No |
| C4-21 | p. 91, L4683–4699 | Six benchmarks implemented and each tuned to its best | SIM | NOT VERIFIED | REG C30 | Only fixed LQR exists (project) | — | Remove | No |
| C4-22 | p. 92, L4701–4715 | P controller tuned by Ziegler–Nichols ultimate gain for 2 % overshoot; K_p = 150 | MATH | INVALID DERIVATION | — | A plant without delay of order ≤ 2 never oscillates under P control; constants mix the PI rule (0.45, 0.54) with a non-standard K_d (0.113); ZN targets quarter-decay (≈ 25 % overshoot), not 2 % | — | Remove | No |
| C4-23 | p. 92, L4717–4741 | PID by SIMC; gains 100/20/15 | MATH | VERIFIED WITH CONDITIONS | — | K_c, τ_I match SIMC with τ_c = 0.5τ_p; the τ_D rule is not SIMC; gains not traceable (no identified plant) | Plant identification | Remove gains or show identification | Cond. |
| C4-24 | p. 93, L4743–4755 | Fixed LQR Q = diag(10, 1, 1, 0.5), R = 1 by Bryson; settling < 1.5 s, overshoot < 5 % | MATH | CONTRADICTED | REG C27; CHK-BRYSON; A-55 | R = 1 implies u_max = 1 N·m (limit 85); Table 14 lists a different Q; LQR does not "place" poles; K₁ = 3.16 alone implies a 13 s velocity time constant (indicative only; other gain terms ignored) | — | Use documented Bryson weights (PARAMS) | No |
| C4-25 | p. 93, L4757–4777 | Fuzzy LQR rules, PSO-optimised | IMPL | NOT VERIFIED | — | Not implemented | — | Remove | No |
| C4-26 | p. 94, L4779–4809 | MPC: 50-step horizon, constraints, FORCES NLP at 0.8 ms on automotive hardware | IMPL | NOT VERIFIED | REG C19 | No implementation or hardware; a rate limit of 50 N·m/s vs the 200 N·m/s safety limit (L3883) | — | Remove | No |
| C4-27 | pp. 94–95, L4811–4855 | DDPG design: 5-state actor, 10,000 episodes = 1 M steps, reward terms | IMPL | CONTRADICTED | A-19 | 1 s episodes vs 600–1,800 s cycles; actor state has no reference speed or tracking error; SoH penalty constant within an episode | — | Remove | No |
| C4-28 | p. 95–96, L4857–4876; Table 14 | Equivalent budgets; memory figures; adaptive LQR 5 KB ROM "between PID and fuzzy LQR"; "near-MPC performance" | IMPL | CONTRADICTED | A-26; REG C30 | 5 KB < PID 8 KB < fixed LQR 15 KB; no performance data | — | Remove | No |
| C4-29 | p. 96–97, L4878–5008; Table 15 | Systematic tuning (fmincon, multi-objective, robustness) and tuned gains | IMPL | NOT VERIFIED | REG C27 | No artefacts; Q differs from Table 14 | — | Remove | No |

### 5.6 Chapter 5 (pp. 97–107, L5010–L5426)

| ID | Loc. | Claim | Cat. | Verdict | Evidence | Method → outcome | Gap | Disposition | Retain? |
|---|---|---|---|---|---|---|---|---|---|
| C5-01 | p. 97, L5012 | Results "demonstrate the effectiveness" of the adaptive LQR across cycles and conditions | SIM | CONTRADICTED | N01–N03 | The only reproducible experiment shows no practical difference | — | Replace with N01–N04 | No |
| C5-02 | p. 97, L5016 | Monte Carlo with 1,000 samples | STAT | CONTRADICTED | CHK-MC-COUNT | Conflicts with 100 per configuration | — | Remove | No |
| C5-03 | p. 97, L5018–5032 | Uncertainty bounds from manufacturer specifications and experimental data | PARAM | CONTRADICTED | REG C32, C35 | No source; η_dt ±3 % vs LHS range [0.92, 0.98] around 0.88 | — | Label as assumed | No |
| C5-04 | p. 98, L5034–5043; Table 16 | RMSE 0.42 ± 0.08; "all samples" below 0.6 m/s; 95th percentile 0.56 vs 0.8 m/s target | STAT | CONTRADICTED | REG C11; CHK-MC-TABLES | Conflicts with Table 18 (0.62/0.78) and 0.4 % failures; two different specifications | — | Remove | No |
| C5-05 | p. 98, L5045–5053 | Success 98.2 %, partial 1.4 %, failure 0.4 % | STAT | CONTRADICTED | M-35 | Sums to 100 %, but "energy improvement > 5 %" per sample is undefined and contradicted by N01 | — | Remove | No |
| C5-06 | p. 98, L5055–5063 | Fixed LQR success 72.4 %, RMSE 0.68 m/s; "25.8 pp" higher; "50 % lower" tracking error | STAT | CONTRADICTED | REG C12; CHK-RMSE-PCT; A-22; ROB | 25.8 pp arithmetic correct; 0.42 vs 0.68 is 38 %; S-D: scheduled tracks slightly worse (median RMSE ratio 1.011), 0 failures in 100 runs | — | Remove | No |
| C5-07 | p. 99, L5065–5094; Table 17 | Morris (10 parameters): R0, Crr, Q most influential, "validating" ageing compensation | STAT | CONTRADICTED | REG C15; CHK-MORRIS-DUP; N04 | Identical μ, σ to Table 19; circular inference; R0 has no pathway into tracking in the documented model | — | Remove | No |
| C5-08 | p. 99–100, L5096–5140 | WC-1…WC-5 all pass the 1.5 m/s specification | STAT | CONTRADICTED | REG C16; CHK-WORSTCASE | WC-5 fails in §4.8 | — | Remove | No |
| C5-09 | p. 100, L5142–5164 | LHS distributions; 1,000 LHS samples ≈ 10,000 random samples | STAT | CONTRADICTED | REG C14, C35 | Centres conflict with Table 8 (r_w 0.265 vs 0.28; mass; η_dt); efficiency factor unsupported | — | Remove | No |
| C5-10 | p. 101, L5166–5173; Table 18 | Extended Monte Carlo summary incl. SoH fade 14.2 %/1000 cycles | STAT | CONTRADICTED | REG C11, C02 | — | — | Remove | No |
| C5-11 | p. 101, L5175–5177 | Shapiro–Wilk W = 0.987, p = 0.342 | STAT | NOT VERIFIED | REG C14 | No data | — | Remove | No |
| C5-12 | p. 101, L5179 | 95 % CI for mean RMSE [0.412, 0.428] | STAT | CONTRADICTED | A-20 | 1.96 × 0.08/√1000 = 0.005 → [0.415, 0.425] (i.i.d.); the LHS CI needs another method | — | Remove | No |
| C5-13 | p. 101, L5181–5189 | Success 98.2 % vs 72.4 % (repeated) | STAT | CONTRADICTED | as C5-05/06 | — | — | Remove | No |
| C5-14 | p. 102, L5191–5205 | Morris design r(k + 1) = 260 samples vs 16.7 M full factorial (k = 12, p = 4, r = 20) | MATH | VERIFIED WITH CONDITIONS | A-21 | Arithmetic correct (4¹² = 16,777,216); no runs exist | — | Keep only as a design statement | Cond. |
| C5-15 | p. 102, L5207–5224; Table 19 | Morris (12 parameters); rank stability 94.2 % | STAT | CONTRADICTED | REG C15 | — | — | Remove | No |
| C5-16 | p. 102, L5228–5236 | BFGS with 50 restarts and differential evolution "ensure global optima" | STAT | INVALID DERIVATION | — | Neither guarantees a global optimum | — | Remove | No |
| C5-17 | pp. 102–104, L5238–5290; Table 20 | Second worst-case set; WC-5 fails by 0.02 m/s; WC-3 at a 15 % grade | STAT | CONTRADICTED | REG C16; C1-17 | Conflicts with §5.3; WC-3 outside Assumption 1 | — | Remove | No |
| C5-18 | p. 104, L5292–5333; Table 21 | ±30 % sensitivity matrix and design priorities | STAT | NOT VERIFIED | — | No runs; "Stability" metric undefined | — | Remove | No |
| C5-19 | p. 105, L5337–5351 | S32K144: Cortex-M4F 112 MHz, FPU, 512 KB flash, 64 KB SRAM, 2 × 12-bit ADC, CAN FD, AEC-Q100; 4.50 USD at 10k units | PHYS | NOT VERIFIED | — | Datasheet and price not accessed (the core specifications match reference knowledge) | Datasheet citation | Cite the datasheet; drop the price or cite a quote | Cond. |
| C5-20 | p. 105, L5351–5369 | Footprint 86 KB/12 KB; 1 ms loop with 0.40 ms compute | IMPL | CONTRADICTED | REG C19; CHK-SAMPLING; A-26 | No hardware; conflicts with 10 ms/1.2 ms and with < 50 KB and 5 KB | — | Remove | No |
| C5-21 | p. 106, L5371–5380; Table 22 | CAN message definitions | PLAN | NOT VERIFIED | — | Design intent | — | Retain only as a proposed design | Cond. |
| C5-22 | p. 106, L5382–5401; Table 23 | OBD-II PIDs; "custom PIDs (0x61, 0x62)" | SAFE | CONTRADICTED | — | 0x61/0x62 are standard SAE J1979 mode-01 PIDs (engine percent torque); coolant, fuel-level and oil PIDs do not apply to this EV controller (reference knowledge; J1979 not accessed) | — | Correct or remove | No |
| C5-23 | p. 106, L5405–5426; Table 24; Fig. 16–17 | ISO 26262 ASIL B; unintended acceleration rated ASIL B; all mechanisms implemented; DC 94 % | SAFE | CONTRADICTED | REG C17, C18; A-52 | Own S3/E3/C3 maps to ASIL C (ISO 26262-3 risk graph; not accessed); no FMEDA, hardware or safety case; "stranding" and "battery damage" are not injury harms (S-class misuse) | — | Remove; at most "preliminary hazard list" | No |
| C5-24 | p. 107, text boxes | FTTI: detection ≤ 100 ms, reaction ≤ 50 ms, total ≤ 200 ms; required mechanisms listed | SAFE | NOT VERIFIED | — | Requirement statement; internally consistent (150 ≤ 200 ms); no derivation from a hazard | — | Retain only as a proposed requirement | Cond. |

### 5.7 Chapter 6 (pp. 108–121, L5428–L5944)

| ID | Loc. | Claim | Cat. | Verdict | Evidence | Method → outcome | Gap | Disposition | Retain? |
|---|---|---|---|---|---|---|---|---|---|
| C6-01 | p. 108, L5432 | All numerical estimates in the chapter rest on industry references, literature and datasheets | ECON | CONTRADICTED | C6-04 to C6-28 | Many values have no reference; several rest on contradicted results (C01, C03, C04) | — | Remove the statement | No |
| C6-02 | p. 108, L5440 | BNEF 2023: pack prices fell 14 % to 139 USD/kWh [11] | LIT | VERIFIED | WEB: BNEF press release (about.bnef.com, 27 Nov 2023) | Matches | — | Retain | Yes |
| C6-03 | p. 109, L5446 | CATL/BYD BMS BOM 45–80 USD per unit from teardown reports [12] | LIT | NOT VERIFIED | B-12 | [12] is a Tesla Model Y BMS teardown with a generic URL; it cannot plausibly support CATL/BYD costs | — | Remove or cite a matching source | No |
| C6-04 | p. 109, L5448–5460; Table 25 | 5-year TCO 4,750 USD; 0.063 USD/km; 950 USD/year | ECON | NOT VERIFIED | A-30, A-33 | Sums correct; inputs unsourced ([11], [12] do not contain them); replacement 800 USD here vs 1,200 USD in the payback | — | Remove or source each line | No |
| C6-05 | p. 109, L5462 | Battery 34.4 %, motor 19.4 %, chassis 12.9 % of BOM | ECON | CONTRADICTED | A-35, A-36 | Shares computed on 9,300 USD, but the BOM lines sum to 12,580 USD | — | Recalculate | No |
| C6-06 | p. 109, L5464–5494 | Payback 3.86 years (3.09 with subsidy) | ECON | CONTRADICTED | REG C39; A-31, A-32, A-34 | Arithmetic reproduces; inputs contradicted (C03, C04); 9.7 % is 10.2 %; 120 USD vs 168 USD | — | Remove | No |
| C6-07 | p. 110, L5494–5498 | 19 % learning rate ⇒ 45–55 USD/unit at 100,000 units; payback range 2.8–5.2 years | ECON | NOT VERIFIED | — | No derivation; a pack learning rate is applied to BMS hardware | — | Remove | No |
| C6-08 | p. 110, L5504 | LCA follows ISO 14040/14044 | ECON | CONTRADICTED | — | No inventory, impact method, interpretation or critical review (needed for a published comparative assertion, ISO 14044; not accessed) | — | Remove | No |
| C6-09 | p. 110, L5520–5522 | Functional unit 150,000 km; GREET: 65–95 kg CO₂e/kWh pack [13] | LIT | NOT VERIFIED | B-13; A-42 | GREET not accessed; Table 27 implies 250 kg/kWh and the text uses 50 kg/kWh | — | Source or remove | No |
| C6-10 | p. 111, L5528 | Vietnam grid factor 0.45 kg CO₂/kWh [14] | LIT | CONTRADICTED | WEB: VietnamNews (2025 HUST/ministry study: 0.681 t/MWh in 2024, +3.2 % on 2023); A-40 | [14] is a Swedish battery LCA, not a grid source; reported national factors are ≈ 0.66–0.68 t/MWh; Table 27 itself uses 0.60 | Official MONRE value not accessed | Correct with the official factor | No |
| C6-11 | p. 111, L5530–5536 | Gasoline 2.31 kg/L; battery 50 kg/kWh; vehicle 8 t; recycling credit −15 % | ECON | CONTRADICTED | A-42, A-43 | Table 27: production 2.6 t (not 8 t); battery 250 kg/kWh; credit −1.8 t (69 %); [14] is not a fuel-factor source | — | Remove | No |
| C6-12 | p. 111, L5538 | Romare & Dahllöf: cell manufacturing 32–86 kWh/kWh, median 47 | LIT | NOT VERIFIED | B-14 | Report not accessed; secondary sources confirm only its 150–200 kg CO₂e/kWh headline | — | Check against the report or remove | Cond. |
| C6-13 | p. 111, L5540–5547; Table 26 | Chemistry CO₂ factors (GREET 2023, Romare 2017) | LIT | NOT VERIFIED | B-13, B-14 | Not accessed | — | Source or remove | Cond. |
| C6-14 | p. 112, L5549–5563 | ICE 45 t, fixed 28 t, adaptive 25 t; 38 %, 45 %, "additional 7 %" | ECON | CONTRADICTED | A-39, A-45, A-46 | 44.4 % rounds to 45 % only generously; 7 % is 7 pp (relative 10.7 %); Table 27 gives 14.3 t; rests on C03/C04 | — | Remove | No |
| C6-15 | p. 112, L5565–5583; Table 27 | Detailed LCA (body 2,500 kg, 19,500 kWh, totals 2.6/13.3/−1.6/14.3 t) | ECON | CONTRADICTED | A-40 to A-44 | Sums correct; 2,500 kg body > 850 kg vehicle; 0.6 kg/kWh used; 130 Wh/km implied | — | Remove | No |
| C6-16 | p. 112, L5585 | EU 2023/1542: 65 % recycling efficiency by weight for Co, Cu, Pb, Ni by 2025, 80 % by 2030 | LIT | NOT VERIFIED | B-15 | EUR-Lex text not retrievable; the wording appears to conflate the battery-level recycling-efficiency target with metal recovery targets | Annex XII text | Check against Annex XII and correct | Cond. |
| C6-17 | p. 113, L5587 | ±12 % uncertainty on lifecycle emissions | ECON | NOT VERIFIED | — | No analysis | — | Remove | No |
| C6-18 | p. 113, L5597–5621 | IPC-A-610 Class 3 PCB; FPY 98.5 % "achieved in production" [16], < 100 DPMO, ICT 99.2 %; then FPY "projected 92–97 %" | PHYS | CONTRADICTED | L5980; B-16 | No production exists; achieved and projected yields conflict; IPC-A-610 is an acceptability standard and reports no yields | — | Remove the results; keep as a proposed process | No |
| C6-19 | p. 114, L5623–5655 | Assembly process; reflow peak 245 ± 5 °C; IATF 16949; cycle time 45 min; yield 99.2 % | PHYS | CONTRADICTED | L5980 | Production metrics without production; process steps are generic | — | Remove metrics | No |
| C6-20 | p. 114–115, L5657–5675 | Tests incl. 24 h "burn-in" at 85 °C/85 % RH; test coverage 99.8 %; 1.2 % warranty claims over 2 years | PHYS | CONTRADICTED | L5980 | No field units; 85/85 THB is a qualification stress (typically 1,000 h), not a 24 h production burn-in (reference knowledge) | — | Remove | No |
| C6-21 | p. 115, L5679–5681 | Reliability from field data and accelerated life testing | PHYS | CONTRADICTED | REG C21 | No such data | — | Remove | No |
| C6-22 | p. 115, L5685–5691 | Parts count at 40 °C, environment Ground Benign (G_B) | PHYS | CONTRADICTED | B-18 | G_B is for non-mobile controlled environments; a vehicle ECU needs Ground Mobile (G_M) (handbook not accessed) | — | Correct if kept | Cond. |
| C6-23 | p. 115, L5693–5703 | Field data, 1,000 vehicles × 2 years: MTBF 28,500 h, MTTR 2.5 h, availability 99.97 %, Weibull β 1.2 | PHYS | CONTRADICTED | L5980; A-50 | No fleet; availability from its own numbers is 99.991 % | — | Remove | No |
| C6-24 | p. 116, L5705–5718; Table 28 | Component failure rates (STM32F407, LTC6811, …) | PHYS | NOT VERIFIED | B-18 | Not computed per the handbook; STM32F407 conflicts with the S32K144 selection (L5337) | — | Recalculate per the handbook or remove | No |
| C6-25 | p. 116, L5720–5744 | λ = 12.5 per 10⁶ h = "12.5 FIT"; MTBF 80,000 h ≈ 9.1 years meets 10 years "with high confidence" | PHYS | CONTRADICTED | A-47 to A-49 | Table sums 15.3 or 7.9; 12,500 FIT; R(10 y) = 0.33 | — | Remove | No |
| C6-26 | p. 116–117, L5746–5758 | Warranty reserve 850 M VND per 10,000 units | ECON | CONTRADICTED | A-51 | From its own rates: 1,889 M VND | — | Remove | No |
| C6-27 | p. 117, L5760–5772 | DfR measures implemented (derating, 85 °C, redundant monitoring, CISPR 25) | PLAN | NOT VERIFIED | — | No hardware | — | Restate as proposed | Cond. |
| C6-28 | p. 117, L5778, L5796; Table 29 | Current TRL 3 (NASA definition [19]) | PLAN | VERIFIED WITH CONDITIONS | B-19 | Definition matches Mankins 1995 (not opened); simulation-only work covers only the analytical part of TRL 3 | — | Narrow: "analytical proof of concept (TRL 2–3)" | Cond. |
| C6-29 | pp. 117–118, L5782–5832 | Roadmap: Table 29 (TRL 9 in 2034–36) vs phases (pilot of 100 vehicles 2026–27, mass adoption 2028–30, 15 % market share by 2030) | PLAN | CONTRADICTED | — | Internal timeline conflict; pilot sizes conflict (100 vs 5–10 vehicles) | — | Keep one consistent, labelled projection | Cond. |
| C6-30 | p. 118, L5802, L5814; L6512 | Partnership with and motor supply by TMT Motors | PLAN | OWNER CONFIRMATION REQUIRED | — | A real company is named; no agreement or quote in the project | Agreement | Default: remove the name or mark "hypothetical partner" | Cond. |
| C6-31 | p. 119, L5840–5856; Table 30 | Applicable standards and scopes | LIT | VERIFIED WITH CONDITIONS | B-20 to B-25 | Titles largely correct; UL 1973 covers stationary and motive *auxiliary* power, not EV propulsion; R100 applies to M/N (L-category: R136); "ASIL-C target" conflicts with ASIL B | — | Correct scopes | Cond. |
| C6-32 | p. 119–120, L5858–5868 | The controller *meets* ISO 26262 (ASIL B), ECE R100, IEC 62660-1, UL 2580, TCVN 7612; DC 94 % | SAFE | CONTRADICTED | REG C17; L5980 | No test of any kind; UL 2580 is cited to [24] (UL 1973); IEC 62660 is a cell standard; TCVN 7612 identity not verified | — | Remove | No |
| C6-33 | p. 120–121, L5870–5922 | Future work: prototype (STM32F407), lab tests, pilot, certification (ASIL C or D), scale-up | PLAN | VERIFIED WITH CONDITIONS | — | Legitimate plans; MCU and ASIL inconsistent with earlier sections | — | Retain; unify MCU and ASIL | Cond. |
| C6-34 | p. 121, L5924–5944 | Chapter summary "confirms the technical and economic viability … for commercial deployment" | ECON | CONTRADICTED | C6-01 to C6-32 | Inherits the contradicted items | — | Remove | No |

### 5.8 Declaration and limitations (pp. ≈ 122–124, L5978–L5998)

| ID | Loc. | Claim | Cat. | Verdict | Evidence | Method → outcome | Gap | Disposition | Retain? |
|---|---|---|---|---|---|---|---|---|---|
| DL-01 | L5980 | "No physical experiments were conducted" | PLAN | VERIFIED WITH CONDITIONS | REG C38 (CONSISTENT_WITH_RECORD) | Consistent with all project evidence; contradicts C06, C17, C19–C22 and the Chapter 6 "achieved"/"field" statements | Absence shown on the record only | Retain; remove every contradicting statement | Yes |
| DL-02 | L5980–5988 | Results use validated parameters from datasheets, benchmark datasets and peer-reviewed papers | PARAM | CONTRADICTED | REG C32; PARAMS | No per-parameter source | — | Replace (repair sheet §4b) | No |
| DL-03 | L5992 | All results based on numerical simulation; prototype validation is future work | PLAN | VERIFIED WITH CONDITIONS | REG C38 | — | — | Retain; add "no independent human replication" | Yes |
| DL-04 | L5994 | Vehicle parameters from Citroën Ami and Wuling Mini EV datasheets | PARAM | CONTRADICTED | REG C34 | L780 names other vehicles; no datasheet cited | — | Describe the vehicle as hypothetical | No |
| DL-05 | L5996 | VUC is simplified, not real measured data | LIT | VERIFIED WITH CONDITIONS | REG C07 | Consistent with the project record; contradicts L810 and L4429 | — | Retain; remove the contrary statements | Yes |
| DL-06 | L5998 | Ageing model from SEI theory (Huria 2018, J. Power Sources); needs experimental validation | LIT | CONTRADICTED | REG C37; CR | Wrong source and venue; "needs validation" is correct | — | Correct citation; withdraw the attribution | Cond. |

### 5.9 Appendices A–J (pp. 127–140, L6052–L6612)

| ID | Loc. | Claim | Cat. | Verdict | Evidence | Method → outcome | Gap | Disposition | Retain? |
|---|---|---|---|---|---|---|---|---|---|
| AP-01 | p. 127, L6054–6069; Table 31 | Vehicle parameters with sources ("Micro-EV average", "Design specification", component efficiencies) | PARAM | CONTRADICTED | REG C33; A-10 | Sources conflict with Table 8; efficiencies multiply to 0.848 | — | Unify with PARAMS provenance labels | Cond. |
| AP-02 | p. 127, L6071–6088; Table 32 | R0 5 mΩ, R1 3 mΩ, C1 50,000 F, etc. | PARAM | NOT VERIFIED | PARAMS | No source (report_unverified); τ = R1·C1 = 150 s | — | Label as assumed | Cond. |
| AP-03 | p. 128, L6090–6112; Table 33 | Gains at 11 SoH values; K_i rises as SoH falls | SIM | CONTRADICTED | REG C28; A-54 | Not reproducible (L_eq, K_e, K_t, γ missing); gains fall in the documented computation; K₁(100 %) = √(Q₁₁/R) = √10 (scalar-integrator value, an observation only); grid 50–100 % vs code 70–100 % | — | Replace with the computed schedule and its inputs | No |
| AP-04 | p. 128, L6118–6128 | BMS interface: 11:1 divider for 0–60 V; 0.5 mΩ shunt with INA199 (100×) for ±200 A; 2.5 kV isolation | PHYS | CONTRADICTED | A-27 to A-29 | 60 V → 5.45 V at the ADC; 200 A → 10 V amplifier output; ±200 A < ≈ 426 A peak (and < 274 A in the documented runs) | — | Redesign or remove | No |
| AP-05 | p. 129, L6130–6143; Table 34 | Motor-driver interface signals | PLAN | NOT VERIFIED | — | Design intent | — | Retain only as a proposed design | Cond. |
| AP-06 | p. 129, L6145–6181 | Python module list; complete code available on request | IMPL | OWNER CONFIRMATION REQUIRED | REG C23 | None of the modules exists in the project | Code location | Default: replace with this project's repository | Cond. |
| AP-07 | p. 130, L6183–6241 | C implementation excerpt of the adaptive LQR | IMPL | NOT VERIFIED | C3-47 | Incomplete, uncompiled; table conflicts with the 11-point grid | — | Remove or provide a compiled source | No |
| AP-08 | p. 131, L6243–6261; Table 35 | Regeneration efficiency by cycle; adaptive LQR highest through SoH-aware allocation | SIM | CONTRADICTED | REG C30; PAIRS | Adaptive vs fixed: identical within 0.01 Wh; other controllers not implemented | — | Remove | No |
| AP-09 | p. 132, L6263–6289 | Calibration procedure; targets RMSE < 0.5 m/s, > 5 % energy improvement | PLAN | NOT VERIFIED | N01 | Not executed; the energy target is not attained in the documented model | — | Retain only as a proposed procedure | Cond. |
| AP-10 | p. 133, L6291–6305; Table 36 | LHS summary incl. temperature and efficiency columns | STAT | NOT VERIFIED | REG C11 | No data; minimum equals the 5th percentile (0.28) and maximum equals Table 18's 99th percentile (0.78), implausible for N = 1,000; temperature is not modelled | — | Remove | No |
| AP-11 | p. 133, L6307–6311 | LHS divides each range into 1,000 strata | MATH | VERIFIED | — | Correct definition | — | Retain | Yes |
| AP-12 | p. 133, L6313–6325 | Correlations (R0–energy ρ = +0.68, etc.) | STAT | NOT VERIFIED | EB; N04 | No data; in the documented model resistive losses are 1.1–2.1 % of energy, so R0 cannot dominate the energy variance (indicative) | — | Remove | No |
| AP-13 | p. 133, L6327–6351 | Per-cycle RMSE/energy; all RMSE < 0.5 m/s; −10 °C, 45 °C, 15 % grade and overload effects | SIM | NOT VERIFIED | C1-17 | No data; 15 % grade outside Assumption 1; specification varies (0.5/0.6/0.8/1.5 m/s) | — | Remove | No |
| AP-14 | pp. 134–135, L6353–6399 | Repeated TCO and payback (Tables 37, D.6) | ECON | CONTRADICTED | C6-04, C6-06 | Duplicates | — | Remove | No |
| AP-15 | p. 135, L6401–6427 | ANOVA H₀: μ₁ = … = μ₇; F = 45.67, p < 0.0001; Tukey HSD | STAT | NOT VERIFIED | — | No data; degrees of freedom unspecified; seven controllers (contradicts 6 × 4 × 100) | — | Remove | No |
| AP-16 | p. 136, L6429–6440; Table 38 | All 18 comparisons significant; Bonferroni keeps FWER at 0.05 | STAT | CONTRADICTED | REG C13; CHK-BONFERRONI | 9 of 18 above 0.00278 | — | Remove | No |
| AP-17 | p. 136, L6442–6458 | Cohen's d = 0.89/0.78/0.65 | STAT | CONTRADICTED | A-23 | Tracking d from the reported means, SD and 95th percentile is 1.32 (normal approximation) | — | Remove | No |
| AP-18 | p. 137, L6460–6478 | Applicable standards incl. ECE R13-H and "UN ECE 10: emissions" | LIT | CONTRADICTED | WEB: UN R10 (EMC) listings | UN R10 is electromagnetic compatibility; R13-H covers passenger-car braking (M1/N1) | — | Correct | Cond. |
| AP-19 | p. 137, L6480–6499; Table 39 | ±30 % sensitivity per controller; adaptive LQR least sensitive | STAT | NOT VERIFIED | EB | No data; an R0 +30 % effect of +3.8 to +7.8 % on energy is implausible beside a resistive share of 1.1–2.1 % (documented model; indicative) | — | Remove | No |
| AP-20 | p. 138, L6501–6530; Table 40 | BOM of 18 components, total 9,300 USD, 45 % local; named suppliers | ECON | CONTRADICTED | A-35, A-37, A-38 | Lines sum to 12,580 USD; cells counted twice; 562 USD/kWh cells; 16 × 3.2 V = 51.2 V; "45 % local" not reproducible; real suppliers named without quotes | Supplier quotes | Recalculate as an illustrative BOM; seek owner confirmation of suppliers | No |
| AP-21 | p. 138, L6532–6554; Table 41 | Detailed LCA (duplicate of Table 27); 45 % lower emissions | ECON | CONTRADICTED | C6-15 | — | — | Remove | No |
| AP-22 | p. 139, L6556–6582 | Deployment roadmap (duplicate) | PLAN | CONTRADICTED | C6-29 | — | — | Remove duplicate | Cond. |
| AP-23 | p. 139, L6588 | Journal Paper 1, IEEE Trans. Transp. Electrif., "Under Review" | PLAN | OWNER CONFIRMATION REQUIRED | CR (no match; uninformative for unpublished work) | No submission record in the project | Submission receipt | Default: remove, or "Planned manuscript (not submitted)" | Cond. |
| AP-24 | p. 139, L6590–6592 | Conference papers at VPPC 2025 and ICSM 2025 | PLAN | OWNER CONFIRMATION REQUIRED | CR (no record by title, 2026-10-24) | No acceptance or DOI in the project | Acceptance letter or DOI | Default: remove | Cond. |
| AP-25 | p. 140, L6594–6612 | Future research directions | PLAN | VERIFIED WITH CONDITIONS | — | Plans; consistent with the stated limitations | — | Retain | Yes |

---

## 6. Bibliography audit

**Structure.** The thesis has two numbered lists.
- **Printed list.** The "References" section (p. 125 per the TOC; L5948–5976) numbers
  1–15. It is a renumbered copy of main-list entries 11–25.
- **Main list.** The 25-entry list that in-text numbers point to (bookmarks, L6002–6050)
  follows the Limitations.
- **Conflict.** In the text, [1] = IEA, but in the printed list 1 = BloombergNEF.
- **Verdict:** **CONTRADICTED** (B-00). **Disposition:** delete the duplicate list.

| ID | Entry as printed | Exists? | Bibliographic accuracy | Supports the attached sentence? | Verdict | Disposition |
|---|---|---|---|---|---|---|
| B-01 | IEA, "Global EV Outlook 2024" | Yes (WEB, iea.org) | Adequate (add URL) | 14 M and +35 % yes; "over 40 % by 2030" overstated (STEPS: almost 40 %) | VERIFIED WITH CONDITIONS | Narrow the sentence |
| B-02 | WHO, "Ambient air pollution: a global assessment…", 2016 | Yes (reference knowledge; not opened) | Adequate | A city ranking is not this report's content | NOT VERIFIED | Cite a ranking source or remove the sentence |
| B-03 | Huria, Ceraolo, Gazzarri, Jackey, IEEE Trans. Ind. Appl. 54(6):6514–6526, 2018 | Only as 2012 IEVC, pp. 1–8, DOI 10.1109/IEVC.2012.6183271 (CR) | Wrong venue, year, volume, pages | No: NMC cells (OA abstract); no ageing or SEI model; not LFP | CONTRADICTED | Correct to the IEVC record; withdraw L750 and L5998 uses |
| B-04 | Pillay & Krishnan, IEEE Trans. Ind. Appl. 25(2):265–273, 1988 | Yes, DOI 10.1109/28.25541 (CR) | Year is 1989; title truncated ("… Part I") | Yes for the dq model (standard) | VERIFIED WITH CONDITIONS | Correct the year |
| B-05 | Bryson & Ho, *Applied Optimal Control*, Washington, D.C., 1975 | Yes (book; not opened) | Publisher missing (Hemisphere) | Bryson's rule: conventionally attributed | VERIFIED WITH CONDITIONS | Add publisher |
| B-06 | Ramadass, Haran, White, Popov, J. Electrochem. Soc. 151(2):A196–A203, 2004 | Yes, DOI 10.1149/1.1634273 (CR) | Omits co-author P. M. Gomadam | Abstract: first-principles CC-CV side-reaction model; it does not describe Eq. 2.54 or the α₀, β₀ values; not LFP (full text not read) | NOT VERIFIED | Add author; remove from L1938 and Table 9 unless the author shows the page |
| B-07 | Qiao, Zhang, Wang, Liu, IETE J. Res. 70(2):1124–1136, 2023 | Not found as printed (CR) | — | Unknown. A different paper exists in the same issue (Saxena et al., "Design of LQR-based FLC for the Optimal Regenerative Braking Controlling of Solar PV-based Electric Vehicle System", 70(2):1923–1936, DOI 10.1080/03772063.2023.2171916) | NOT VERIFIED | Seek owner confirmation; do not substitute; else remove |
| B-08 | Wang, Li, Chen, Zhang, IET Intell. Transp. Syst. 18(3):456–469, 2024 | Not found (CR) | — | — | NOT VERIFIED | Remove unless a DOI is supplied |
| B-09 | Lin, Huang, Wu, Chen, Control Eng. Pract. 142:105789, 2024 | Not found; article 105789 is a marine-vessel paper in vol. 143 (DOI 10.1016/j.conengprac.2023.105789) (CR) | Locator belongs to another paper | — | CONTRADICTED | Remove |
| B-10 | Smith & Wang, "Solid-electrolyte interphase…: a molecular dynamics perspective", J. Power Sources 161(1):595–599, 2006 | Not found (CR) | — | — | NOT VERIFIED | Remove; Table 9's γ₀ has no source |
| B-11 | BloombergNEF, Lithium-ion battery price survey 2023 | Yes (WEB press release, 27 Nov 2023) | Adequate | Yes: 139 USD/kWh, −14 % | VERIFIED | Retain |
| B-12 | Munro Live, "Tesla Model Y BMS Teardown Report", 2022, munroev.com | Not verified (generic URL) | Incomplete | A Tesla teardown cannot support CATL/BYD BMS costs | NOT VERIFIED | Remove or replace with a matching source |
| B-13 | Argonne GREET model, 2023 | Yes (greet.es.anl.gov; not opened) | Adequate | 65–95 kg/kWh and Table 26 values not checked | NOT VERIFIED | Cite the specific GREET table |
| B-14 | Romare & Dahllöf, IVL Report C 243, 2017 | Yes (WEB secondary) | Adequate | 32–86 kWh/kWh not checked; it is not a source for the Vietnam grid factor (L5528) | NOT VERIFIED | Check the figures; remove from L5528 |
| B-15 | Regulation (EU) 2023/1542 | Yes | Adequate | Annex XII not accessible (EUR-Lex blocked); the sentence appears to conflate targets | NOT VERIFIED | Check Annex XII and correct |
| B-16 | IPC-A-610, 2017 | Yes (revision G, 2017) | Adequate | Does not report yields | NOT VERIFIED (as used) | Cite only for acceptability criteria |
| B-17 | IATF 16949:2016 | Yes | Adequate | QMS requirement description is generic | VERIFIED WITH CONDITIONS | Retain as a standards reference |
| B-18 | MIL-HDBK-217F, 1991 | Yes (Notice 2, 1995, not mentioned) | Adequate | Parts-count method yes; G_B environment misapplied | VERIFIED WITH CONDITIONS | Use G_M; cite the notice |
| B-19 | Mankins, "Technology Readiness Levels", NASA, 1995 | Yes (reference knowledge) | Adequate | TRL 3 wording consistent | VERIFIED WITH CONDITIONS | Retain |
| B-20 | UN Regulation No. 100, 2015 | Yes | Adequate | Applies to M/N; L-category electric safety is R136 | VERIFIED WITH CONDITIONS | Cite R136 for an L-category micro-EV |
| B-21 | ISO 6469, 2018 | Yes (multi-part) | Part numbers missing | Generic | VERIFIED WITH CONDITIONS | Cite parts |
| B-22 | ISO 26262, 2018 | Yes | Part numbers missing | No compliance demonstrated | VERIFIED WITH CONDITIONS (existence) | Cite part 3 for the hazard analysis |
| B-23 | UN Manual of Tests and Criteria, §38.3, 2015 | Yes | Revision not stated | Generic | VERIFIED WITH CONDITIONS | Retain |
| B-24 | UL 1973, 2018 | Yes | Title is "… Stationary and Motive Auxiliary Power Applications" | Also cited for UL 2580 (L5866), which it is not | CONTRADICTED (as used for UL 2580) | Add UL 2580 separately or remove |
| B-25 | IEC 62660, 2011 | Yes (parts 1–3; first editions 2010) | Year imprecise; part numbers missing | Cell standard; not applicable to a controller | VERIFIED WITH CONDITIONS | Cite parts and editions |

**Uncited material that needs a source:**
- NSGA-II (Deb et al., 2002);
- DDPG (Lillicrap et al., 2016);
- the Morris method (1991);
- SIMC (Skogestad, 2003);
- the Pacejka and Burckhardt tyre models;
- the Thevenin ECM;
- Tables 1, 3, 4 and 5;
- the motor efficiency ranges;
- the VAMA statements.

This audit does not supply these references. The author should choose sources they have
read.

---

## 7. Owner-confirmation register

These are only items that project evidence cannot resolve. Each has a conservative default.

| ID | Question | Where | Conservative default |
|---|---|---|---|
| OC-1 | Which cell (part number, datasheet) and series/parallel layout is intended? | C3-01, C3-12, AP-20 | "Generic 48 V, 100 Ah model pack; the BOM is illustrative and not validated as the same pack" |
| OC-2 | Is there a submission receipt for Journal Paper 1? | AP-23 | Remove, or "Planned manuscript (not submitted)" |
| OC-3 | Acceptance letters or DOIs for the VPPC 2025 and ICSM 2025 papers? | AP-24 | Remove |
| OC-4 | DOIs for refs [7], [8], [10]; is Saxena et al. 2023 the intended [7]? | B-07, B-08, B-10 | Remove the references and every sentence or number attributed to them |
| OC-5 | Source document for Table 1 ("VAMA Report") | C1-04 | Remove Table 1 |
| OC-6 | Does a Git repository or Python package of the original study exist outside this project? | C4-05, AP-06 | Replace with this project's repository, commit and `uv.lock` |
| OC-7 | Any agreement or quote involving TMT Motors or the named suppliers | C6-30, AP-20 | Remove names, or mark them "hypothetical" |
| OC-8 | Disclosure of AI assistance under the applicable rules | — | Disclose |

Not owner items (already decided by evidence):
- physical validation was not performed;
- independent human replication was not performed;
- the 12.5 %/15.3 % results are not reproducible.

---

## 8. Corrections to earlier project documents found during this audit

- `docs/thesis_closeout_repair_sheet.md` §1 said ref. 6 is "cited only in Table 9". It is
  also cited for Eq. 2.54 (L1938). A dated correction was added there on 2026-10-24.
- No other conflict was found between this audit and:
  - `docs/final_contribution_and_thesis_revision_plan.md`;
  - `docs/research-contribution-review.md`;
  - `docs/literature_review_soh_scheduled_lqr.md`;
  - `docs/battery-data-feasibility-audit.md`;
  - the dated matrix snapshot.
- This audit adds many findings those documents did not cover:
  - D2 (motor infeasibility);
  - M-08, M-10 to M-13, M-20, M-21 and M-26 to M-32;
  - A-01 to A-58;
  - the regulatory misidentifications;
  - the Chapter 6 arithmetic.
- These findings do not change any registered status. The claim registry and the matrix
  were not edited.

---

## Appendix A. Derivations from the thesis's own numbers (read-only)

**Method.**
- Every input is a value printed in `report.md`, at the line given in the code.
- The script performs closed-form arithmetic only; nothing is simulated.
- It was run with the project interpreter in isolated mode (`python -I`) on 2026-10-24.
- The script was kept outside the project; its full text is below so that anyone can rerun
  it.

```python
import math
out = []
def rec(cid, desc, computed, reported, ok):
    out.append((cid, desc, computed, reported, "consistent" if ok else "INCONSISTENT"))

cagr = (248000 / 3200) ** (1 / 4) - 1                                            # Table 1, L561-571
rec("A-01", "Table 1 CAGR", f"{100*cagr:.1f} %", "> 200 %", cagr > 2.0)
yoy = [8600/3200-1, 34700/8600-1, 95200/34700-1, 248000/95200-1]
rec("A-02", "Table 1 YoY", ", ".join(f"{100*y:.1f} %" for y in yoy), "168.8, 303.5, 174.4, 160.5 %", True)
M, A, Cd, rw, G, eta, Tmax, Pmax = 850, 2.2, 0.35, 0.28, 6.5, 0.88, 85.0, 18000.0   # Table 8, L2716-2736
Rs, L, lam, Vdc, Crr, rho, g = 0.02, 0.008, 0.175, 48.0, 0.008, 1.225, 9.81
rec("A-03", "8000 rpm", f"{8000*2*math.pi/60:.1f} rad/s", "837 rad/s", True)
rec("A-04", "13 in / 2", f"{13*0.0254/2:.3f} m", "0.28 m", False)
wb = Pmax / Tmax; vph = Vdc / math.sqrt(3); iq_p1 = Tmax / (1.5 * lam)
rec("A-05", "back-EMF at base speed vs SVPWM limit", f"{wb*lam:.1f}*p V vs {vph:.1f} V", "-", wb*lam < vph)
w_lim = vph / (L * iq_p1)
rec("A-06", "speed where w_e*Lq*iq(85 N m) = limit", f"{w_lim:.1f} rad/s = {w_lim*rw/G:.2f} m/s", "-", w_lim >= wb)
rec("A-07", "L/R", f"{L/Rs*1000:.0f} ms", "~20 ms (L2802)", False)
rec("A-08", "Ts 10 ms vs own rule Ts <= 2 ms", "10 ms", "<= 2 ms", False)
rec("A-09", "10 Hz in rad/s", f"{2*math.pi*10:.1f}", "100 rad/s (L2800)", False)
rec("A-10", "0.95*0.92*0.98*0.99", f"{0.95*0.92*0.98*0.99:.3f}", "0.88", False)
rec("A-11", "peak wheel force", f"{Tmax*G*eta/rw:.0f} N", "-", True)
for m in (700, 850):                                                              # UN GTR 15 classes: <=22, 22-34, >34 W/kg
    pmr = Pmax / m; rec(f"A-12/{m}", "PMR", f"{pmr:.1f} W/kg -> class {1 if pmr <= 22 else 2 if pmr <= 34 else 3}", "Class 3", False)
d, T = 5800.0, 600.0                                                              # VUC, L4453-4455
E_rr = Crr*M*g*d; E_aero = 0.5*rho*Cd*A*(d/T)**2*d                                # Jensen lower bound for aero
rec("A-13", "VUC rolling work", f"{E_rr/1e3:.0f} kJ", "95 kJ (Table 13)", False)
rec("A-14", "VUC road-load lower bound", f"{(E_rr+E_aero)/1e3:.0f} kJ", "95 kJ", False)
ke = 0.5*M*(50/3.6)**2
rec("A-15", "KE at 50 km/h", f"{ke/1e3:.1f} kJ", "-", True)
rec("A-16", "stops for 1.5 kWh", f"{1.5*3.6e6/ke:.0f}", "17", False)
rec("A-17", "VUC battery energy at 95 Wh/km", f"{95*5.8/1000:.2f} kWh", "KE 1.5 kWh", False)
rec("A-18", "random cycle speeds vs 28.5 +-5 %", "34.2, 34.1, 35.5", "27.1-29.9", False)
rec("A-19", "DDPG episode length", f"{1e6/1e4*0.01:.0f} s", "600-1800 s cycles", False)
hw = 1.96*0.08/math.sqrt(1000)
rec("A-20", "95 % CI half-width", f"{hw:.4f}", "0.008", False)
rec("A-21", "Morris r(k+1); 4^12", f"{20*13}; {4**12:,}", "260; 16.7 M", True)
rec("A-22", "98.2-72.4", f"{98.2-72.4:.1f} pp", "25.8 pp", True)
sd_fix = (1.12-0.68)/1.645; sp = math.sqrt((0.08**2+sd_fix**2)/2)
rec("A-23", "Cohen d tracking (normal approx.)", f"{(0.68-0.42)/sp:.2f}", "0.78", False)
rec("A-24", "loop budget", f"{0.2+0.1+0.3+0.1+0.5:.1f} ms", "1.2 ms", True)
rec("A-25", "EKF budget", f"{0.5+1.0+0.8+0.3+0.5:.1f} ms", "3.1 ms", True)
rec("A-26", "ROM figures", "86 KB / <50 KB / ~5 KB", "one value", False)
rec("A-27", "11:1 divider at 60 V", f"{60/11:.2f} V", "<= 5 V", False)
rec("A-28", "0.5 mOhm x 100 at 200 A", f"{200*0.0005*100:.1f} V", "<= 5 V", False)
rec("A-29", "battery current at 18 kW", f"{Pmax/(eta*Vdc):.0f} A", "+-200 A range", False)
rec("A-30", "Table 25 total", f"{2150+450+1250+450+450}", "4,750", True)
pay = 200/(0.00345*15000)
rec("A-31", "payback", f"{pay:.2f} / {0.8*200/(0.00345*15000):.2f} y", "3.86 / 3.09", True)
rec("A-32", "95 -> 85.3 Wh/km", f"{100*(95-85.3)/95:.1f} %", "9.7 %", False)
rec("A-33", "battery replacement", "800 vs 1,200 USD", "one value", False)
rec("A-34", "14 % of 1,200 USD", f"{0.14*1200:.0f}", "120", False)
bom = [3200, 2880, 320, 1800, 650, 180, 120, 1200, 170, 150, 130, 130, 90, 70, 220, 300, 120, 350, 500]
rec("A-35", "BOM sum", f"{sum(bom):,} ({sum(bom)-2880:,} without cells)", "9,300", False)
rec("A-36", "shares on 9,300", f"{100*3200/9300:.1f}, {100*1800/9300:.1f}, {100*1200/9300:.1f} %", "34.4, 19.4, 12.9", True)
rec("A-37", "cell cost", f"{180/0.32:.0f} USD/kWh", "80-100", False)
rec("A-38", "16 x 3.2 V", f"{16*3.2:.1f} V", "48 V", False)
rec("A-39", "Table 27 total vs text", "14.3 t", "25 t", False)
rec("A-40", "19,500 kWh x 0.45", f"{19500*0.45:,.0f} kg ({11700/19500:.2f} kg/kWh used)", "11,700 kg", False)
rec("A-41", "Wh/km implied", f"{19500/150:.0f}", "85.3-95", False)
rec("A-42", "battery CO2 per kWh", f"{1200/4.8:.0f}", "50-95", False)
rec("A-43", "15 % of 2,600 kg", f"{0.15*2600:.0f} kg", "1,800 kg", False)
rec("A-44", "body mass", "2,500 kg", "vehicle 850 kg", False)
rec("A-45", "28 -> 25 t relative", f"{100*3/28:.1f} %", "7 %", False)
rec("A-46", "reductions vs 45 t", f"{100*17/45:.1f}, {100*20/45:.1f} %", "38, 45 %", True)
lam_q = 0.5+1.2+2.5+0.3+4*1.0+30*0.1+2*1.5+0.8; lam_1 = 0.5+1.2+2.5+0.3+1.0+0.1+1.5+0.8
rec("A-47", "Table 28 sum", f"{lam_q:.1f} / {lam_1:.1f}", "12.5", False)
rec("A-48", "12.5 per 1e6 h in FIT", "12,500 FIT", "12.5 FIT", False)
rec("A-49", "R(10 y), MTBF 80,000 h", f"{math.exp(-87600/80000):.2f}", "high confidence", False)
rec("A-50", "availability", f"{100*28500/28502.5:.3f} %", "99.97 %", False)
war = 10000*(0.005*2.5+0.008*2.8+0.012*3.0+0.015*3.2+0.02*3.5)
rec("A-51", "warranty reserve (M VND)", f"{war:,.0f}", "850", False)
rec("A-52", "ASIL (ISO 26262-3 risk graph)", "S3E3C3=C, S2E3C2=A, S2E2C2=QM, S3E2C3=B", "ASIL B", False)
p = [0.001,0.001,0.002,0.015,0.048,0.001,0.001,0.001,0.003,0.012,0.035,0.001,0.001,0.002,0.008,0.025,0.042,0.003]
rec("A-53", "p > 0.05/18", f"{sum(x > 0.05/18 for x in p)} of 18", "0", False)
rec("A-54", "sqrt(Q11/R)", f"{math.sqrt(10):.3f}", "K1 = 3.16", True)
rec("A-55", "velocity time constant from K1 alone", f"{M/(3.16*G*eta/rw):.1f} s", "settling < 1.5 s", False)
rec("A-56", "CLTC 14.5 km / 1800 s", f"{14.5/0.5:.1f} km/h", "37.8 (text) / 29.0 (table)", False)
rec("A-57", "7 x 4 x 100", f"{7*4*100}", "2,400", False)
rec("A-58", "units of 2 D c0 t/(zF)", "mol^2/(m C)", "m^2", False)
for r in out: print(" | ".join(map(str, r)))
```

**Output** (2026-10-24; script `audit_calcs.py`, identical arithmetic):

| ID | Check | Computed | Thesis | Result |
|---|---|---|---|---|
| A-01 | Table 1 CAGR 2020–2024 | 196.7 % | > 200 % | INCONSISTENT |
| A-02 | Table 1 YoY growth | 168.8, 303.5, 174.4, 160.5 % | same | consistent |
| A-03 | 8000 rpm | 837.8 rad/s | 837 rad/s | consistent |
| A-04 | 13″ diameter / 2 | 0.165 m | 0.28 m | INCONSISTENT |
| A-05 | Back-EMF at base speed (212 rad/s) | 37.1·p V vs 27.7 V limit | motor runs on 48 V | INCONSISTENT |
| A-06 | Speed where ω_e·L_q·i_q(85 N·m) reaches the limit | 10.7 rad/s = 0.46 m/s | 85 N·m to base speed | INCONSISTENT |
| A-07 | L/R | 400 ms | ≈ 20 ms | INCONSISTENT |
| A-08 | Ts vs own rule | 10 ms | ≤ 2 ms | INCONSISTENT |
| A-09 | 10 Hz | 62.8 rad/s | 100 rad/s | INCONSISTENT |
| A-10 | η product (Appendix A) | 0.848 | 0.88 | INCONSISTENT |
| A-11 | Peak wheel force / acceleration | 1,736 N; 2.04 m/s² | — | consistent |
| A-12 | PMR at 700 / 850 kg | 25.7 / 21.2 W/kg → class 2 / 1 | Class 3 | INCONSISTENT |
| A-13 | VUC rolling work | 387 kJ | positive work 95 kJ | INCONSISTENT |
| A-14 | VUC road-load lower bound | 643 kJ | 95 kJ | INCONSISTENT |
| A-15 | KE at 50 km/h | 82.0 kJ (22.8 Wh) | — | consistent |
| A-16 | 50 km/h stops for 1.5 kWh | 66 | 17 stops | INCONSISTENT |
| A-17 | VUC supplied energy at 95 Wh/km | 0.55 kWh | KE 1.5 kWh | INCONSISTENT |
| A-18 | Random-cycle speeds | 34.2, 34.1, 35.5 km/h | 28.5 ± 5 % | INCONSISTENT |
| A-19 | DDPG episode length | 100 steps = 1 s | 600–1,800 s cycles | INCONSISTENT |
| A-20 | 95 % CI half-width | 0.0050 m/s → [0.415, 0.425] | [0.412, 0.428] | INCONSISTENT |
| A-21 | Morris samples; 4¹² | 260; 16,777,216 | 260; 16.7 M | consistent |
| A-22 | 98.2 − 72.4 | 25.8 pp | 25.8 pp | consistent |
| A-23 | Cohen's d (tracking) | 1.32 | 0.78 | INCONSISTENT |
| A-24 | Loop budget | 1.2 ms | 1.2 ms | consistent |
| A-25 | EKF budget | 3.1 ms | 3.1 ms | consistent |
| A-26 | ROM figures | 86 KB / < 50 KB / ≈ 5 KB | one footprint | INCONSISTENT |
| A-27 | 11:1 divider at 60 V | 5.45 V | ≤ 3.3/5 V ADC | INCONSISTENT |
| A-28 | Shunt × gain at 200 A | 10.0 V | ≤ 3.3/5 V | INCONSISTENT |
| A-29 | Battery current at 18 kW | 426 A | ±200 A sensor | INCONSISTENT |
| A-30 | Table 25 totals | 4,750 USD | 4,750 USD | consistent |
| A-31 | Payback | 3.86 y; 3.09 y | 3.86; 3.09 | consistent |
| A-32 | 95 → 85.3 Wh/km | 10.2 % | 9.7 % | INCONSISTENT |
| A-33 | Battery replacement cost | 800 vs 1,200 USD | one value | INCONSISTENT |
| A-34 | 14 % of 1,200 USD | 168 USD | 120 USD | INCONSISTENT |
| A-35 | BOM sum | 12,580 (9,700 without cells) USD | 9,300 USD | INCONSISTENT |
| A-36 | Shares on 9,300 USD | 34.4, 19.4, 12.9 % | same | consistent |
| A-37 | Cell cost | 562 USD/kWh | 80–100 USD/kWh | INCONSISTENT |
| A-38 | 16 × 3.2 V | 51.2 V | 48 V | INCONSISTENT |
| A-39 | Table 27 total vs text | 14.3 t | 25 t | INCONSISTENT |
| A-40 | 19,500 kWh × 0.45 | 8,775 kg (table uses 0.60 kg/kWh) | 11,700 kg | INCONSISTENT |
| A-41 | Implied consumption | 130 Wh/km | 85.3–95 Wh/km | INCONSISTENT |
| A-42 | Battery CO₂ per kWh | 250 kg/kWh | 50–95 kg/kWh | INCONSISTENT |
| A-43 | 15 % of 2,600 kg | 390 kg | 1,800 kg | INCONSISTENT |
| A-44 | Body mass | 2,500 kg | vehicle 850 kg | INCONSISTENT |
| A-45 | 28 → 25 t | 10.7 % (7 pp of 45 t) | "additional 7 %" | INCONSISTENT |
| A-46 | Reductions vs 45 t | 37.8, 44.4 % | 38, 45 % | consistent |
| A-47 | Table 28 sum | 15.3 / 7.9 per 10⁶ h | 12.5 | INCONSISTENT |
| A-48 | 12.5 per 10⁶ h | 12,500 FIT | 12.5 FIT | INCONSISTENT |
| A-49 | R(10 y) at MTBF 80,000 h | 0.33 | "high confidence" | INCONSISTENT |
| A-50 | Availability | 99.991 % | 99.97 % | INCONSISTENT |
| A-51 | Warranty reserve | 1,889 M VND | 850 M VND | INCONSISTENT |
| A-52 | ASIL for Table 24 rows | C, A, QM, B | "ASIL B" | INCONSISTENT |
| A-53 | p > 0.05/18 | 9 of 18 | all significant | INCONSISTENT |
| A-54 | √(Q₁₁/R) | 3.162 | K₁ = 3.16 | consistent (observation) |
| A-55 | Velocity time constant from K₁ alone | 13.2 s | settling < 1.5 s | INCONSISTENT (indicative) |
| A-56 | CLTC average speed | 29.0 km/h | 37.8 (text) / 29.0 | INCONSISTENT |
| A-57 | Test matrix with 7 controllers | 2,800 | 2,400 | INCONSISTENT |
| A-58 | Units of Eq. 4.35 | mol²/(m·C) | m² | INCONSISTENT |

**Conditions on the less direct derivations:**
- **A-05/A-06:** these assume the amplitude-invariant dq convention, λ_m as a peak flux
  linkage, SVPWM in the linear range (V_ph,max = V_dc/√3), and R_s neglected. The result
  holds for any pole-pair count.
- **A-14:** uses the mean speed in the aero term. This is a lower bound, because the mean of
  v² is at least the square of the mean v.
- **A-23:** assumes normal distributions.
- **A-55:** ignores the K₂, K₃ and K_i terms, so it is indicative only and is not used as a
  verdict basis.
- **A-52:** uses the ISO 26262-3 risk graph from reference knowledge; the standard was not
  accessed.

---

## Appendix B. Citation and source lookups (2026-10-24)

| Query | Source | Result |
|---|---|---|
| DOI 10.1109/28.25541 | Crossref API | Pillay & Krishnan, IEEE TIA 25(2):265–273, **1989** |
| DOI 10.1149/1.1634273 | Crossref; OpenAlex abstract | Ramadass, Haran, **Gomadam**, White, Popov, JES 151(2):A196, 2004; abstract: first-principles CC-CV solvent-reduction model |
| DOI 10.1109/IEVC.2012.6183271 | Crossref | Huria et al., 2012 IEEE IEVC, pp. 1–8 |
| Titles of refs [7]–[10] | Crossref `query.bibliographic` | No match for any; IETE J. Res. 70(2) contains Saxena et al., DOI 10.1080/03772063.2023.2171916; Control Eng. Pract. 105789 = DOI 10.1016/j.conengprac.2023.105789 (vol. 143, marine vessels) |
| Publication-list titles (J1, C1, C2) | Crossref | No match (uninformative for unpublished or unindexed work) |
| UN R136 scope | [UN Treaty Collection XI-B-16-136](https://treaties.un.org/doc/Publication/MTDSG/Volume%20I/Chapter%20XI/XI-B-16-136.en.pdf); [MLIT UN R136](https://www.mlit.go.jp/jidosha/un/UN_R136.pdf) | Electric power train of L-category vehicles |
| UN R129 | [EUR-Lex Reg. 2014/129 listing](https://eur-lex.europa.eu/eli/reg/2014/129/oj); [Lexaris R129](https://lexaris.de/library/tableofcontents/2047921) | Enhanced child restraint systems |
| UN R10 | [EUR-Lex UN R10](https://eur-lex.europa.eu/eli/reg/2012/10/oj/eng); [MLIT UN R010](https://www.mlit.go.jp/jidosha/un/UN_R010.pdf) | Electromagnetic compatibility |
| Reg. (EU) 168/2013 L6e/L7e | [ZEMO presentation](https://www.zemo.org.uk/assets/presentations/EU%20Regulation%20on%20the%20Approval%20of%20L-Category%20Vehicles.pdf); [UK DfT Annex B](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1088182/annex-b-l-category-vehicle-classification.pdf) | Secondary; EUR-Lex not accessed |
| Reg. (EU) 2023/1542 Annex XII | [EUR-Lex](https://eur-lex.europa.eu/eli/reg/2023/1542/oj/eng) | **Not accessed** (empty page to automated fetch) |
| IEA GEVO 2024 | [IEA outlook](https://www.iea.org/reports/global-ev-outlook-2024/outlook-for-electric-mobility); [CleanTechnica](https://cleantechnica.com/2024/04/23/iea-2024-global-ev-outlook-sees-sunny-skies-ahead-for-electric-transportation/) | ≈ 14 M (2023), +35 %; STEPS almost 40 % in 2030 |
| BNEF 2023 survey | [BNEF press release](https://about.bnef.com/blog/lithium-ion-battery-pack-prices-hit-record-low-of-139-kwh/) | 139 USD/kWh, −14 % |
| Vietnam grid factor | [VietnamNews 2025](https://vietnamnews.vn/environment/1716087/study-shows-coal-power-dominant-as-viet-nam-s-grid-emissions-climbed-in-2024.html) | 0.681 tCO₂e/MWh (2024), +3.2 % on 2023 (secondary; official MONRE value not accessed) |
| Decision 876/QĐ-TTg | [LuatVietnam (Binh Thuan implementation plan)](https://static.luatvietnam.vn/tai-file-ke-hoach-2104-kh-ubnd-binh-thuan-2023-trien-khai-thuc-hien-quyet-dinh-876-qd-ttg-255425-d2/uploaded/VIETLAWFILE/2023/6/2104_KH-UBND_130623141643.pdf.aspx); [Diễn đàn Doanh nghiệp](https://diendandoanhnghiep.vn/uu-dai-giam-o-to-dien-khong-con-hap-dan-10146727.html) | Transport green-energy transition programme (22 Jul 2022) |
| Romare & Dahllöf 2017 | [IVL summary (Swedish)](https://kunskap.ivl.se/download/18.72fab6cc1761c7ad2941daf/1608124869907/190318%20Batteriers%20milj%C3%B6p%C3%A5verkan_small.pdf); [elektroauto-news](https://www.elektroauto-news.net/news/emissionen-lithium-ionen-batterie-produktion-gesunken) | Report exists; 150–200 kg CO₂e/kWh headline; 32–86 kWh/kWh not found |
