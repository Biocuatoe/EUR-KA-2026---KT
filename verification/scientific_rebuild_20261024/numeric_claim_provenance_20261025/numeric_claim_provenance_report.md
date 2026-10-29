# Forensic provenance audit of the thesis headline numbers (12.5 % energy, 15.3 % capacity fade)

**Date:** 2026-10-25.
**Scope:** the project root `D:\EURÉKA 2026 - KT`, plus the open-access full text of one external paper.
**Status:** complete for everything inside the root. Leads outside the root are listed, not checked (§4.4).

**What this audit did not do:**
- It did not modify the thesis DOCX. SHA-256 `01363a06…ddff8c` is unchanged before and after (§9).
- It did not change any R1, R2 or earlier record, protocol, raw output or verdict.
- It ran no simulation, tuned no parameter and reconstructed no number.
- It performed no Git operation. The only Git-related step was a plain-text read of `.git/logs/HEAD`.

**Naming used here.**
- "R1" is the scientific rebuild of 2026-10-24 (`../analysis_report_20261024.md`).
- "R2" is taken to mean the pre-registered P2 pilot of 2026-10-25 (`../research_recovery_20261025/pilot_results.md`). The project's own records reserve the label "R2" for a possible future study, so the mapping is stated here explicitly.

---

## 1. Findings in brief

1. **Each headline number occurs exactly once in the submitted DOCX, in the Abstract.**
   - Location: para 5, `report.md` L9.
   - The search covered all 7,731 paragraphs, including tables and the 782 text-box paragraphs.
   - No chapter, table, figure, equation or appendix reports 12.5 %, 15.3 %, ±2.1 % or ±2.8 %.
   - The Abstract does not define the metric, drive cycle, SoH, sample count, or the statistic behind "±".
2. **The thesis body contains different numbers for the same comparison.**
   - Its only fixed-vs-adaptive pairs are 95 → 85.3 Wh/km and 16.5 → 14.2 %/1000 cycles.
   - These give **10.2 %** and **13.9 %**. The body itself labels them "9.7 %" and "14 %".
   - Figure 11's plotted curves give a third value: **16.7 % at 1000 cycles**.
3. **No original computational provenance exists inside the project root.**
   - All 189,409 files were walked.
   - Outside third-party software trees, the only files that predate the audit (2026-10-23) are the thesis DOCX and its byte-identical copy.
   - None of the 16 code modules named in Appendix C exists. There are no MATLAB/Simulink files, and the Git repository the thesis refers to is absent.
   - Every file that contains the headline strings is an audit record written on 2026-10-23 or later.
4. **The DOCX is a PDF-to-Word conversion.**
   - `docProps/custom.xml` records the producer as iLovePDF, dated 2026-09-21.
   - The native source document is not in the project.
5. **Figures 9 and 11 still carry their plotted geometry as vector shapes, which earlier text-based audits could not see.**
   - The Figure 11 curves equal round-coefficient quadratics (e.g. fixed: 0.002·N + 1×10⁻⁶·N²) to within drawing resolution.
   - That convex shape is not the functional form of the thesis's own ageing equation (Eq. 4.22).
   - Figure 9's Pareto front sits on exact 5 Wh/km × 0.1 grid values. The knee point given in the text lies outside its axis.
   - These are descriptions of what was drawn. They are not evidence of how the numbers were produced.
6. **Tawfik, Ali and Asfoor (2024) is not cited anywhere in the thesis.**
   - Its full text reports 13 % lower energy and 15.8 % lower capacity loss, for a different vehicle, lever, baseline and horizon.
   - Both thesis numbers sit exactly 0.5 pp below Tawfik's. This is recorded as an observation, not as evidence of transcription.
   - Whether the thesis values were adapted from literature **cannot be determined from in-project evidence**.
7. **Verdicts (§8).**

   | Item | Verdict |
   |---|---|
   | 12.5 % | UNTRACEABLE, INTERNALLY INCONSISTENT, and (unchanged) CONTRADICTED within the R1/R2 scope |
   | 15.3 % | UNTRACEABLE, INTERNALLY INCONSISTENT, and (unchanged) UNRESOLVED as a physical question |
   | SoH-aware rationale | Defensible as motivation |
   | R1/R2 null results | Valid within their tested scope |
   | Gains from a different formulation | Plausible in the literature, not demonstrated here |

---

## 2. Method and coverage

**Tools.** All tools are in `tools/` and run with the project venv (Python 3.14.7, numpy 2.5.4) as `python -I tools/<name>.py` from this folder. All exited 0.

| Tool | Reads | Writes |
|---|---|---|
| `thesis_trace.py` | thesis DOCX (zip, read mode; refuses to run if the SHA-256 differs) | `outputs/docx_package.json`, `outputs/thesis_paragraphs.tsv` (every `w:p` with chapter/section/caption context), `outputs/thesis_occurrences.csv` (202 pattern hits, 20 patterns) |
| `figure_geometry.py` | DOCX DrawingML shapes of Figures 9 and 11 | `outputs/figure11_curves.csv`, `outputs/figure9_points.csv`, `outputs/figure_geometry_summary.json` |
| `provenance_inventory.py` | `os.stat` of every file under the root; text of non-third-party text files; `.git/logs/HEAD` | `outputs/inventory_summary.json`, `outputs/inventory_type_files.csv`, `outputs/inventory_claim_string_hits.csv`, console log `outputs/_inventory_console.txt` |
| `arithmetic_checks.py` | printed numbers and the figure readout | `outputs/arithmetic_checks.csv` (16 checks) |

**External retrieval.** The Tawfik et al. 2024 PDF was downloaded once on 2026-10-25:
- Source: `https://www.nature.com/articles/s41598-024-71711-w.pdf`.
- Response: HTTP 200, `application/pdf`, 2,229,149 bytes, 16 pages.
- SHA-256: `5bb89362afaf139a115ab4fd1911e711d24b92fc93d46d2e4ddc7e812c532114`.
- Storage: kept in the session scratchpad, outside the project. Attributed excerpts (CC BY 4.0) are in `outputs/tawfik2024_fulltext_excerpts.txt`.

**Checked:**
- Every file in the root, including `.git`, `.venv`, `tools`, `cache` and `verification`, for modification time and file name.
- Every text-type file outside third-party trees for the strings `12.5 %`, `15.3 %`, `±2.1` and `±2.8`.
- File types searched: `.m`, `.mlx`, `.slx`, `.mdl`, `.sldd`, `.mat`, `.fig`, `.xls*`, `.csv`, `.npz`, `.npy`, `.pkl`, `.h5`, `.parquet`, `.ipynb`, `.tex`, `.bib`, `.docx`, `.doc`, `.pdf`, `.py`, `.yaml`, `.json`, `.log`, `.c`, `.h`.

**Not checked (so the search is exhaustive only for the project root):**
- Anything outside the root. In particular `D:\EUREKA`, which the owner forbade opening on 2026-10-23.
- The contents of compressed Git objects (no git command was run).
- Binary files, for the claim strings.
- Figure-by-figure visual inspection of the Tawfik PDF. Its text, tables and captions were read via `pdftotext`.

---

## 3. Task 1: the numbers in the submitted thesis

### 3.1 The headline claims

The only occurrence is Abstract, p. i, para 5, `report.md` L9:

> "Simulation results show that the adaptive LQR achieves up to 12.5% ± 2.1% improvement in
> energy efficiency and 15.3% ± 2.8% reduction in battery capacity fade over 1000 operational
> cycles compared to the fixed-gain LQR baseline."

| Element the claim needs | Stated in the thesis? |
|---|---|
| Baseline | fixed-gain LQR, defined in para 4861 as weights for SoH = 100 %, Q = diag(10, 1, 1, 0.5), R = 1 |
| Energy metric and denominator | no. "Energy efficiency" is not defined; the body uses Wh/km |
| Drive cycle | no. The Abstract lists NEDC, WLTP, CLTC and VUC without tying the number to one |
| SoH at which the comparison holds | no |
| Meaning of "up to" | a maximum, which is incompatible with a ± interval |
| Sample count | contradictory: "100 trials per configuration" (para 10, para 524, Table 11) vs "N = 1000" (Tables 16 and 18) |
| Statistic behind ± | not stated (SD, SE or CI) |
| "Operational cycle" and fade metric | not defined |
| Script, dataset, batch, seed or calculation producing the values | **none identified** (§3.3) |

### 3.2 Related figures in the body (none equals the headline)

| Location | Printed | Arithmetic (`arithmetic_checks.csv`) |
|---|---|---|
| Ch. 6 Payback Period Analysis, paras 5971–5977 (L5468–L5472); repeated in App. D.6, paras 7179–7185 | 95 Wh/km (fixed) → 85.3 Wh/km (adaptive), "9.7 Wh/km = 9.7 %" | 9.7/95 = **10.21 %** (E1). 12.5 % would need a 97.5 Wh/km baseline or an 83.1 Wh/km adaptive value; neither is printed (E2, E3) |
| Ch. 6, paras 5980–5984 (L5476–L5480); App. D.6, paras 7188–7192 | 16.5 → 14.2 %/1000 cycles, "2.3 % = 14 % improvement" | 2.3/16.5 = **13.94 %** (F1). 15.3 % would need 16.77 %/1000 cycles (F2) |
| Ch. 6 summary, para 6489; LCA, paras 6064 and 6066 | 9.7 % energy, 14 % longer battery life | Same inputs. Para 6489 attributes them to "BloombergNEF data [11] and industry teardown reports [12]", which are a price survey and a BMS teardown |
| Ch. 5 Tables 16 and 18 (L5034, L5166); App. D Table 36 | Adaptive LQR only: 85.3 ± 4.2 Wh/km; SoH fade 14.2 ± 1.5 %/1000 cycles; N = 1000 | No fixed-LQR energy or fade distribution is printed anywhere. Tables 16 and 18 give the same mean and SD but different 5th/95th percentiles (78.5/92.8 vs 75.2/97.5) |
| App. E Table 38; paras 7275–7281 | p(Energy, LQR-fix) = 0.002; Cohen's d (energy) = 0.89 | If the pooled SD is taken as the printed 4.2 Wh/km, d = 0.89 implies a ≈3.7 Wh/km gap; 9.7 Wh/km would give d ≈ 2.3 (E5, assumption stated) |
| Ch. 3, para 3638 (L3593) | Pareto knee "≈122 Wh/km and 14.0 %/1000 cycle fade" | Outside the 1–5 %/1000 cycles axis of the Figure 9 it describes (F5) |
| Figure 11 (Ch. 3, caption para 3211, L3166) | Fade curves for fixed, adaptive and Pareto over **1500** cycles | Plotted geometry gives 3.0 / 2.5 / 2.0 pp at 1000 cycles, i.e. **16.7 %** (F3), and 5.5× less fixed-LQR fade than the 16.5 % of Ch. 6 (F4); see §5 |

### 3.3 Provenance statements inside the thesis

None of these is linked to the headline values.

| Statement | Location | Status in the project |
|---|---|---|
| "simulation studies … using MATLAB/Simulink and Python" | Abstract para 4; Ch. 4 paras 4256–4274 (MATLAB R2023a, Simulink 10.6, Python 3.10, NumPy 1.24) | No `.m`, `.slx`, `.mdl`, `.mlx`, `.sldd` or `.mat` file outside third-party trees |
| Random seed 42, `randn('seed',42)` | Table 11 and para 4330 (L4343–L4349) | No configuration, log or output that uses it |
| "100 Monte Carlo trials"; "6 controllers × 4 drive cycles × 100 trials = 2400 simulations" | Table 11; para 4363 (L4375) | No outputs. Conflicts with N = 1000 (Ch. 5) and with the 7 controllers of Table 35 |
| "All simulation scripts, models, and data are version-controlled using Git, enabling complete traceability of results" | para 4332 (L4351) | No URL or commit is given. This project's repository begins 2026-10-23T13:45+07:00 (first reflog entry), after the thesis file date of 2026-09-21 |
| 16 modules plus `config.yaml`; C excerpt `adaptive_lqr.c` / `gain_table.h`; "available upon reasonable request" | App. C, paras 6817–6889 (L6149–L6181) | None of the names exists anywhere in the root |
| "aging model is validated against experimental data … within 5 % … over 1000 cycles" | para 3214 (L3170) | No dataset named. The model lacks k_c and k_cal (earlier record C05) |
| Publications (IEEE TTE under review; VPPC 2025; ICSM 2025) | App. J, paras 7715–7717 (L6590) | No record found by title (earlier audit, 2026-10-24); owner item OC-3 |

### 3.4 What the DOCX package itself shows (`outputs/docx_package.json`)

**Producer.** `docProps/custom.xml` records `Producer = iLovePDF` and `Converter = StructuredOutput v12.0.20182.1`. `core.xml` records created = modified = 2026-09-21T05:18:41Z. The DOCX is therefore a conversion of a PDF, made the day the file is dated.

**Contents of the package:**
- There are no embedded charts, workbooks or OLE objects.
- The nine images are 112–380-byte glyphs of at most 48 px. None is a figure.
- The figures exist as DrawingML and VML vector shapes produced by the converter.

**Styling of the figures:**
- Lines are 0.797 pt wide.
- Colours are pure `#0000FF`, `#FF0000` and `#009900`, with a `#BFBFBF` grid.
- These are the pgfplots/TikZ defaults, which is consistent with a LaTeX-compiled PDF. Earlier project records say LaTeX sources existed outside the root (§4.4). This is an inference from styling, not a verified fact.

---

## 4. Task 2: search of the project for original provenance

### 4.1 Results (`outputs/inventory_summary.json`)

| Area | Files | Files older than 2026-10-23 00:00 +07 | Nature |
|---|---|---|---|
| Root files | 11 | 1: the thesis DOCX (2026-09-21 12:20) | The DOCX plus audit-era configuration |
| `data/` | 21 | 1: `data/raw/report/EUREKA-2026-KT.docx`, a read-only copy with the same SHA-256 | Audit inputs and outputs |
| `tools/` | 122,559 | 118,119, all under `tools/OpenModelica/` | Installer-preserved timestamps of third-party software. Its `.mat`/`.tex` files are scipy test data and automake `texinfo.tex` |
| `.venv`, `cache`, `.git` | 20,868 / 20,855 / 467 | 0 | Created 2026-10-23 or later |
| `verification/`, `docs/`, `evidence/`, `artifacts/`, `src/`, `scripts/`, `tests/`, `configs/`, `protocol/`, `logs/`, `audit/` | 24,449 and fewer | 0 | Audit and rebuild work, 2026-10-23 onward |

**Other results:**
- **Name search.** None of the 16 module names from Appendix C exists anywhere, nor do `adaptive_lqr.c`, `gain_table.h`, `render_kt01*`, `KT01*`, `DATA_AND_COLAB_PROMPTS*` or `AUDIT_REPORT.md`.
  - The only matches are false positives: scipy's `_sensitivity_analysis.py`, mpmath's `visualization.py`, and the audit's own `scripts/audit_report.py`.
- **Claim strings.** 41 text files contain the headline strings, and all are audit records.
  - The earliest is the pandoc export `data/processed/report/report.md` (2026-10-23 13:28). Then come `evidence/claim_registry.yaml` (13:37) and later reports.
  - No file containing the strings predates the audit (`outputs/inventory_claim_string_hits.csv`).
- **Data-type files outside third-party trees.** These are all R1, R2, Modelica cross-check, pre-registered evaluation or literature-review products created from 2026-10-23 on. They were generated by the audit's own code and are *new* evidence, not recovered originals:
  - 2 `.docx`, 186 `.csv`, 456 `.json`, 60 `.npz`, 100 `.py`;
  - 2,478 `.c` and 944 `.h` (OpenModelica-generated build files);
  - 1 `.bib`.

### 4.2 Candidate artifacts and whether they generate the claim

| Artifact | Modified | Relevant content | Generates 12.5 % or 15.3 %? |
|---|---|---|---|
| `EURÉKA 2026 - KT.docx` (434,945 B, SHA-256 `01363a06…`) | 2026-09-21 12:20 | The claims and the body numbers of §3 | No. It states them; it contains no calculation that yields them |
| `data/raw/report/EUREKA-2026-KT.docx` | 2026-09-21 12:20 (copy) | Identical bytes | No |
| Figure 11 and 9 vector shapes inside the DOCX | as DOCX | Plotted curves and points (§5) | No. The geometry gives 16.7 %, not 15.3 %, and contains no energy comparison |
| `data/processed/report/report.md` | 2026-10-23 13:28 | Pandoc text export (MANIFEST records the command) | No. Derived from the DOCX |
| `evidence/claim_registry.yaml` C01/C02 and later audit records | 2026-10-23 onward | Audit assessments | No. They record the claims as untraceable |
| R1 runs (`../runs/`), R2 pilot (`../research_recovery_20261025/pilot/`), 2026-10-23 evaluation (`artifacts/raw/`) | 2026-10-23 to 2026-10-25 | New simulations of the documented model | No. They are not the original computation. R1 found ΔE between −0.0019 % and +0.034 %; R2 found ≤ 0.025 % |

### 4.3 Missing evidence

The original provenance would need the following. **Not one item is present in the project root:**

1. The native thesis source (LaTeX `.tex` or Word original) from which the PDF was compiled.
2. The figure-generation code or data for Figures 9 and 11 (and the other result figures).
3. The MATLAB/Simulink model and scripts described in Ch. 4 (R2023a / Simulink 10.6).
4. The Python modules and `config.yaml` listed in Appendix C, and `adaptive_lqr.c` / `gain_table.h`.
5. The Git repository the thesis cites in para 4332.
6. Raw per-run outputs for **both** controllers:
   - energy per run, with drive cycle, SoH and seed;
   - fade per run over 1000 cycles.
   Without these neither ratio nor either ± interval can be computed.
7. Simulation logs, seeds actually used, and configuration snapshots for the Monte Carlo study (100 or 1000 samples).
8. The fixed-LQR source values 95 Wh/km and 16.5 %/1000 cycles. No table or figure produces them.
9. The accelerated-ageing dataset behind "validated … within 5 %" (para 3214), and values for k_c and k_cal.
10. Any record (manuscript, acceptance, DOI) of the Appendix J publications.

### 4.4 Leads outside the root (EXTERNAL_UNVERIFIED; not opened)

Project records written on 2026-10-23, before the owner's instruction not to open `D:\EUREKA`, describe external files. This audit read only the in-project descriptions (`docs/environment-inventory.md` §5; `evidence/claim_registry.yaml` C01, C02, C36, C40; `docs/research-contribution-review.md` §3.2) and could not re-check any of them.

| Lead (as recorded) | What it would decide if verified |
|---|---|
| `D:\EUREKA` holds "LaTeX sources and PDF builds (CNTT02, KT01)" | The native source of the thesis (missing item 1) |
| `KT01_FINAL_REPORT.tex`, first version 2026-09-07, "already contains the value" | When the number entered the text |
| `scripts\render_kt01_figures.py` lines 245–248, 321, 565–566 reportedly draw `np.random` noise around hard-coded values | Whether the result figures were computed at all |
| `AUDIT_REPORT.md` L28, L195, L196 ("Add ±2.1 %", "Add ±3.2 %") | Whether the ± intervals were added editorially |
| `KT01_MicroEV\DATA_AND_COLAB_PROMPTS.md` line 3: use published numbers from papers/datasheets as "ground truth" and simulate "with reasonable noise" | Whether the headline values were adapted from literature |

These leads are the most specific provenance information that exists. Every one of them points away from an original computation, but none is verified. They are reported here so that the owner can decide whether to authorise a read-only, hashed inspection of `D:\EUREKA`. They are **not** used as evidence for any verdict below.

---

## 5. Figure geometry: what the figures actually draw

This is a readout of drawn lines, calibrated against each figure's own grid and tick labels.
- It is not raw data and not recovered computational evidence.
- It shows what the author plotted, not how the values were obtained.
- Calibration and fits are in `outputs/figure_geometry_summary.json`. One EMU of drawing resolution corresponds to 1.5×10⁻⁵ pp.

### 5.1 Figure 11, "Capacity Fade Comparison Over 1500 Cycles" (Ch. 3, described as "predicted by the aging model")

**Geometry and legend.**
- The figure has three curves of 52 vertices each, on a shared abscissa with a spacing of 30.15 cycles.
- The x axis ends at exactly 1500 cycles.
- The legend mapping is unambiguous from stroke colour and dash, cross-checked against the stacked legend samples:
  - blue solid = Fixed Controller;
  - red dashed = Adaptive LQR;
  - green dashed = Pareto Optimal.

**Readout.**

| Fade (pp of capacity) | 500 cycles | 1000 cycles | 1500 cycles |
|---|---|---|---|
| Fixed Controller | 1.250 | **3.000** | 5.250 |
| Adaptive LQR | 1.050 | **2.500** | 4.350 |
| Pareto Optimal | 0.875 | 2.000 | 3.375 |
| Adaptive vs fixed reduction | 16.0 % | **16.7 %** | 17.1 % |

**Shape of the curves.** Each curve equals a quadratic with round coefficients to within ≤ 2×10⁻⁵ pp, which is about one drawing unit:

| Curve | Fade |
|---|---|
| Fixed | 0.0020·N + 1.0×10⁻⁶·N² |
| Adaptive | 0.0017·N + 0.8×10⁻⁶·N² |
| Pareto | 0.0015·N + 0.5×10⁻⁶·N² |

**Consequences:**
- The plotted reduction runs from 15.07 % to 17.14 % over 10–1500 cycles. It equals 15.3 % only near N ≈ 126 cycles, not at 1000.
- The fixed-controller fade at 1000 cycles (3.0 pp) is 5.5 times smaller than the 16.5 %/1000 cycles used in Ch. 6. The adaptive curve's 2.5 pp is 5.7 times smaller than the adaptive Table 18 mean (14.2 %/1000 cycles).
- The curves are convex (fade accelerates). The thesis's cycle-ageing law, Eq. 4.22 (f_c = α√Ah + β·Ah with α, β > 0), is concave under constant throughput per cycle. A fit of the form a√N + b·N needs a < 0.
- So the drawn curves do not have the functional form of the model they are said to come from. Exact round-coefficient polynomials are consistent with curves specified by formula. They are not proof of how they were made.

### 5.2 Figure 9, "Pareto Front: Energy Efficiency vs Battery Longevity" (Ch. 2, described as "a typical Pareto front")

**Readout:**
- The front has 12 vertices at exactly 120, 125, …, 175 Wh/km, with fade values exactly 4.2, 3.8, 3.4, 3.1, 2.8, 2.6, 2.4, 2.2, 2.1, 2.0, 1.9, 1.8 %/1000 cycles.
- Highlighted markers A and B sit at (130, 3.4) and (145, 2.6).

**Consequences:**
- The thesis presents this figure as an illustration in its literature/theory chapter.
- It cannot support the Ch. 3 knee of "≈122 Wh/km and 14.0 %/1000 cycles": 14.0 is outside the 1–5 axis.
- Its energy range (120–175 Wh/km) does not include the 85–95 Wh/km operating values used for the headline comparison.

**Relation to earlier records.** The earlier audit recorded Figure 11 as "figure has no data" (`docs/thesis_full_scientific_audit.md` C3-26) because the pandoc text export drops vector shapes. This readout refines that observation and does not change the earlier verdict (C36/C40: withdraw). That record is left as it is.

---

## 6. Task 3: literature relationship

### 6.1 Bibliography trace

The thesis has two reference lists:
- paras 6502–6518: standards, reports and industry sources;
- paras 6538–6563: numbered [1]–[26].

**Tawfik et al. 2024 is not cited.** There are 0 matches for "Tawfik", "Asfoor", "Scientific Reports" or "71711" in all 7,731 paragraphs.

**Sources tied to the ageing and energy figures:**
- Table 9 attributes α₀ and β₀ to [6] (Ramadass et al. 2004, *J. Electrochem. Soc.*) and γ₀ to [10] (Smith & Wang 2006, *J. Power Sources*). The earlier literature audit could not find [10] as cited.
- The Limitations section attributes the ageing model to "Huria 2018, J. Power Sources". The earlier audit established that this is a 2012 IEVC paper on NMC cells (C37).
- The body energy and fade figures are attributed (para 6489) to BloombergNEF [11] and a Munro teardown [12]. Neither contains controller results.
- Literature-review Tables 6 and 7 list "Chen et al. 2024 (Hybrid, Pareto, aging-aware)" with no matching bibliography entry. It cannot be identified.

**No cited source reports 12.5 % or 15.3 %** for an adaptive-vs-fixed LQR comparison.

### 6.2 What Tawfik et al. (2024) actually report (full text, open access)

**Study.** Tawfik M.I., Ali A.M., Asfoor M.Sh., "A combined trade-off strategy of battery degradation, charge retention, and driveability for electric vehicles", *Sci. Rep.* 14:21995, doi:10.1038/s41598-024-71711-w.

| Aspect | Tawfik et al. 2024 | Thesis (as written) |
|---|---|---|
| Vehicle | 2014 BMW i3 BEV model: 1,620 kg, 125 kW, 18.8 kWh. Validated against ANL D3 chassis-dynamometer data (Table 3; >95 % accuracy) | 48 V micro-EV, 850 kg, 18 kW, LFP 100 Ah (Table 8); no vehicle validation data |
| Battery chemistry and ageing model | A123 ANR26650 LiFePO₄ 2.3 Ah. Semi-empirical Ah-throughput law Q_loss = f(I_c, θ, SoC)·Ah^z, z = 0.57, E_a = 31,500 J/mol (Wang et al. 2011; Onori et al.). Checked against OSU CAR ageing data | "LFP", f_c = α√Ah + β·Ah (Eq. 4.22), E_a,α = 31.5 kJ/mol; k_c and k_cal never given |
| Control lever | NSGA-II over battery-current limit i_max and di/dt limit; chosen point i_max = 110 A, di/dt = 1000 A/s | LQR gains scheduled on SoH; NSGA-II over LQR weights |
| Objectives | J1 capacity loss, J2 SoC (charge retention), J3 driveability (RMSE of tractive vs battery power); normalised and equally weighted | J1 energy per km, J2 fade rate (Eq. 4.67) |
| Baseline | "Normal / not optimized model" (no current limitation) | Fixed-gain LQR |
| Drive cycle | 2×UDDS + US06 + HWFET = 53.27 km "one-day trip" (~80 min); 23–25 °C; SoC 20–90 % | NEDC, WLTP, CLTC, VUC (claim not tied to one) |
| **Energy result** | Table 5: 171.3 → 149.2 Wh/km, "13 %" (computes to 12.90 %) | 12.5 % ± 2.1 % (Abstract only); body 95 → 85.3 Wh/km (10.2 %) |
| **Degradation result** | Table 5: Q_loss 0.012 % → 0.0101 % after **one** daily trip, "15.8 %" (computes to 15.83 %). The authors note the absolute loss after one trip is "negligible" | 15.3 % ± 2.8 % "over 1000 operational cycles" |
| Long horizon | Repeated daily trips to EoL (~2,900 days): battery life 8 → 10 years (+25 %), range +8 % | 1000-cycle (Abstract) or 1500-cycle (Fig. 11) |
| Uncertainty | none reported (single deterministic scenario) | ± values with no stated statistic |
| Data availability | "available from the corresponding author on reasonable request" | code "available upon reasonable request" |

### 6.3 Classification of the thesis values

| Possibility | Evidence | Assessment |
|---|---|---|
| Independent calculation by this project | No code, data, log or calculation exists. The body's own numbers give 10.2 % and 13.9 %; the figure gives 16.7 % | **Not demonstrated** |
| Separate result from a source-supported model | The described ageing model is not implementable (k_c, k_cal missing). The figure curves do not follow its functional form. No cited source supports the comparison | **Not supported** |
| Adapted, approximated or transcribed from prior literature | The thesis does not cite Tawfik 2024. Several things are consistent with, but do not establish, a literature origin: the methodological overlap (NSGA-II, LFP Ah-throughput ageing, E_a = 31.5 kJ/mol, energy-vs-degradation objective), the identical 0.5 pp offsets, and the unverified external planning note (§4.4). Many papers share these features, and E_a = 31.5 kJ/mol is the standard Wang 2011 value | **Neither demonstrated nor excluded** |
| Cannot be traced to origin | All of the above | **This is the supported finding** |

**Limits on this comparison:**
- **No accusation.** Nothing here states or implies that the project owner copied results. Proximity of two numbers to a published pair is not evidence of transcription.
- **Tawfik's results belong to their own study.** They measure a different quantity (one-trip capacity loss, not 1000-cycle fade), on a different vehicle, with a different lever (current limiting, not LQR gain scheduling) and against a different baseline (an unconstrained model, not a fixed LQR). They say nothing about the owner's LQR controller and cannot be assigned to it.

---

## 7. Task 4: could the claims be calculated?

| Requirement | 12.5 % energy | 15.3 % capacity fade |
|---|---|---|
| Numerator / denominator | (E_fixed − E_adaptive)/E_fixed in Wh/km on a stated cycle, SoH and battery state | (Fade_fixed − Fade_adaptive)/Fade_fixed after 1000 defined cycles, with temperature, DoD and initial SoH stated |
| Raw outcomes needed | Per-run energy for both controllers, paired by seed and cycle | Per-run capacity trajectories for both controllers |
| Model equations | Plant (Ch. 3) and controllers. The earlier audit found the documented plant inconsistent in places (e.g. C24 units); R1/R2 built a documented, corrected plant | Eq. 4.21–4.29: **not implementable** (k_c, k_cal absent; mixed % and Ah units; earlier record C05) |
| Baseline result exists? | Only the single number 95 Wh/km, with no source | Only 16.5 %/1000 cycles, with no source |
| Proposed-controller result exists? | Summary only (85.3 ± 4.2 Wh/km), with no samples | Summary only (14.2 ± 1.5 %/1000 cycles), with no samples |
| ± recomputable from independent samples? | **No** (E4) | **No** (F7) |
| Fade modelled across sufficient cycling conditions? | n/a | **No evidence.** No run exists, and the plotted curves are closed-form quadratics over a single condition |
| Reproducible from identified source code without changing assumptions? | **No.** No source code has been identified | **No** |

**Numerical reconstruction: not attempted.** The rule for this task allows a reconstruction only where a defensible equation and parameter set already exist. For fade, none exists. Choosing k_c, k_cal or a substitute law would be inventing a value. For energy, R1 and R2 already evaluated the documented model under frozen protocols. A further run would be a new study of the same model, not a recovery of the original number. The arithmetic in `outputs/arithmetic_checks.csv` uses only printed numbers and the figure readout, and is labelled as such.

---

## 8. Task 5: what can be defended

| # | Question | Verdict | Basis |
|---|---|---|---|
| 1 | Scientific rationale for SoH-aware control | **DEFENSIBLE AS MOTIVATION; NOT A DEMONSTRATED BENEFIT** | The wider literature supports two points: ageing changes resistance and capacity, and battery-current management can reduce *modelled* degradation (e.g. Tawfik 2024; Corno & Pozzato 2019, per `../research_recovery_20261025/related_work_matrix.csv`). In the thesis formulation, however, SoH changes only the LQR weights of a speed-tracking loop and has no pathway into the controlled dynamics. R1 found SoH effects only when current limits were *assumed* to shrink with SoH (exploratory class C) |
| 2 | Original 12.5 % energy claim | **UNTRACEABLE and INTERNALLY INCONSISTENT.** The earlier verdict (CONTRADICTED within the tested model and scenarios) stands unchanged | One occurrence, with no definition, no calculation, no data and no code. The body implies 10.2 %. R1 found −0.0019 % to +0.034 % over 112 matched pairs; R2 found ≤ 0.025 % |
| 3 | Original 15.3 % capacity-fade claim | **UNTRACEABLE and INTERNALLY INCONSISTENT.** The earlier verdict (UNRESOLVED: no credible fade model) stands unchanged | The body gives 13.9 % ("14 %") and the figure 16.7 %. The absolute fade levels of figure and text differ 5.5×. The described model cannot be run, and the plotted curves do not follow its form |
| 4 | R1/R2 negative findings | **VALID WITHIN THEIR TESTED SCOPE** | Frozen protocols (R1 `d80b5b4f…`, R2 `ebebc157…`); 348 R1 runs and 257 R2 runs, all valid; timestep convergence; R2 reproduces an R1 run exactly; an independent Modelica port of the 2026-10-23 evaluation plant and controllers agrees with the Python implementation (`verification/controller-crosscheck-report.md`). **Scope:** the documented plant, assumed battery parameters and limits, the thesis's SoH weight law and the named cycles. They are not real-vehicle results, not an equivalence proof (±1 % is a decision margin) and not a capacity-fade result. This audit reviewed their records; it did not rerun them |
| 5 | Similar improvements under a different, independently justified formulation | **PLAUSIBLE IN THE LITERATURE; NOT DEMONSTRATED BY THIS PROJECT** | Tawfik 2024 reports 13 % / 15.8 % for battery-current limiting on a BMW i3 model over one trip, against an unconstrained baseline. That is a different lever, baseline, vehicle and horizon, so its magnitudes cannot be transferred. This project has no sourced fade law and no cell datasheet (OC-1), and the P3 eco-driving path failed its gates. Any such gain would be a separate study's result, never this thesis's |

**Plausible versus verified.** That ~13–16 % improvements appear in published simulation studies of *other* formulations makes such magnitudes plausible in the field. It does not make the thesis's numbers generated or verified by this project. Neither number has been.

---

## 9. Reproduction and integrity

**Commands.** From PowerShell:

```powershell
cd 'D:\EURÉKA 2026 - KT\verification\scientific_rebuild_20261024\numeric_claim_provenance_20261025'
. 'D:\EURÉKA 2026 - KT\scripts\activate.ps1'
python -I tools/thesis_trace.py          # verifies the DOCX SHA-256 first
python -I tools/figure_geometry.py
python -I tools/arithmetic_checks.py     # needs figure_geometry output
python -I tools/provenance_inventory.py  # ~45 s; walks the whole root
```

**Integrity:**
- **DOCX unchanged.** SHA-256 `01363a069eeb005851f6d62ac4b9da9e3fd13a742bebbfdfc14c802f0eddff8c` was recorded before the first tool ran and again after all runs, for both copies. The original's mtime is still 2026-09-21 12:20:02.
- **Nothing outside this folder was written.** The tools write only to `outputs/`. Exploratory copies (an unzipped DOCX copy and the Tawfik PDF) are in the session scratchpad, outside the project.
- **Errors along the way, all fixed before the final runs:**
  - The first `figure_geometry.py` run failed with "curves are sampled at different abscissae", because one shape holds several paths.
  - A second run picked a marker circle as the Figure 9 front.
  - Two console listings failed on the Windows code page.
  - Final runs all exited 0.

---

## 10. What would change these verdicts

**What could move a claim to Version A** (`defence_wording_options.md`): the owner supplying items 1–7 of §4.3, plus either:
- an independent rerun that reproduces 12.5 % and/or 15.3 % from that material **without changing its assumptions**; and
- an explanation of the internal inconsistencies (10.2 %, 13.9 %, 16.7 %, the 5.5× fade level) and of why R1/R2 found no effect.

**What the owner may decide.**
- **Inspection of `D:\EUREKA`.** The owner may authorise a read-only, hash-recorded inspection of `D:\EUREKA`. If the recorded description of `render_kt01_figures.py` were confirmed, Version A would become impossible for the figures.
- **Publications.** The owner can confirm or withdraw the Appendix J publications (OC-3).
