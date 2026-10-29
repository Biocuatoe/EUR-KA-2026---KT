# Final read-only inspection of `D:\EUREKA`: provenance of the 12.5 % and 15.3 % claims

**Date:** 2026-10-25. Inspection window 12:13:26–12:18:35 +07:00 (system clock).
**Authorisation:** the owner's instruction of 2026-10-25, which allows a read-only inspection of `D:\EUREKA` only.
**Manifest:** `source_candidate_manifest_20261025.csv` (70 rows covering all 439 files).
**Supporting outputs:**
- `outputs/eureka_hashes_pre.csv` and `outputs/eureka_hashes_post.csv` (SHA-256 of every file);
- `outputs/eureka_kt01_lineage.csv` (feature matrix of 51 KT01 files).

**Tools:**
- `tools/eureka_manifest.py` (hash snapshot and verify);
- `tools/eureka_lineage.py` (text scan);
- `tools/eureka_candidate_manifest.py` (manifest).

Each tool ran with `python -I` from this folder and exited 0.

**What was not done:**
- nothing in `D:\EUREKA` was executed, written, moved or renamed;
- nothing was installed or downloaded, and no Git operation was performed;
- no other directory was searched;
- the thesis DOCX and all earlier records are untouched.

---

## 1. Did `D:\EUREKA` exist, and was it accessible?

**Yes.**

| Check | Result |
|---|---|
| Exact path | `D:\EUREKA` (normalised `D:\EUREKA`), directory, mtime 2026-09-10 13:23 |
| Separate from the project? | Yes. It is neither contained in nor containing `D:\EURÉKA 2026 - KT`; the inodes differ; it is not a symlink or junction |
| Contents | 439 files, 337,039,645 bytes, no directory links |
| Pre-inspection hashes | All 439 files, taken 12:14:05, **before** any content was read |
| Post-inspection hashes | All 439 files, taken 12:18:34. **0 added, 0 removed, 0 changed** (SHA-256, size and mtime all equal). `eureka_manifest.py verify` exit 0 |

Three PDFs were copied to the session scratchpad (`cp -p`) and their text was extracted there with MinGW `pdftotext` and MiKTeX `pdfinfo`, which are not tools from `D:\EUREKA`:
- `KT01_FINAL_REPORT.pdf`;
- `KT01_FINAL_REPORT_v2.pdf`;
- `KT01_FINAL_REPORT_v8.pdf`.

---

## 2. Which files were inspected (full list with hashes in the manifest)

| Depth of inspection | Files |
|---|---|
| **Read in full as text** | `scripts\render_kt01_figures.py`, `KT01_MicroEV\DATA_AND_COLAB_PROMPTS.md`, `AUDIT_REPORT.md` |
| **Read in part** (stated line ranges) | `KT01_FINAL_REPORT_v8.tex` (Figure 9, lines 1843–1885; Figure 11, lines 2678–2706), `V8_CHANGELOG.md`, `V8_FINAL_REPORT.md`, `readme.md` |
| **Regex context extraction** | v1 and v2 `.tex`, `v2_clean.tex`, `v8.tex`, `BLUEPRINT_200TRANG.md`, `PROMPTS_KT01.md`, `final_blueprint_KT01.md`, `CHANGELOG_v4.md`, `FIX_SUMMARY_v4.md`, `OPUS5_STRESS_TEST_REPORT.md`, `PHIEU_DANG_KY_EUREKA_2026.md`, both `.bib` files |
| **Text scan for 19 features** | 51 KT01 files (`eureka_lineage.py`): every KT01 `.tex` version and backup, the KT01 chapter and extension fragments, posters, and the KT01 planning notes |
| **PDF text from copies** | v1 build (92 pages), v2 build (177 pages), v8 build (155 pages) |
| **Metadata and hash only (not opened)** | 173 CNTT02 files (a separate thesis); 93 page-render PNG/PPM images (classified by file name: `style_p*`, `resizebox_p*`, `verify_p*`, …); 30 LaTeX build by-products; 5 pandoc distribution files; 73 other notes, templates, fix scripts and test files. The other notes were covered only by the folder-wide search for 12.5 %, 15.3 % and ± |

**Hashes of the key files.** For each file the hash before inspection equals the hash after it.

| File | SHA-256 |
|---|---|
| `KT01_FINAL_REPORT.tex` | `5ea971a19f67dc2b6d026cb872690177cbc86abe0673cb111b789b4bdc901b75` |
| `KT01_FINAL_REPORT_v2.tex` | `b239db82f93785e14ff0192611111c6dbee1eb2c8a02f7b8e70fdf9e0824a7dd` |
| `KT01_FINAL_REPORT_v2_clean.tex` | `97aa23b3b0f0dad25f23ee1d56f9da64884daf699e9b06ccef487cd39ed1939f` |
| `KT01_FINAL_REPORT_v8.tex` | `586b06951c2bceb9ff5b92f48a6755e7f69e4ef2350f838aa0ab648475050732` |
| `KT01_FINAL_REPORT_v8.pdf` | `d93abac2219e355c77163375f111efeb3909fbf7bf1e4801fbc0ac27579a1a16` |
| `scripts\render_kt01_figures.py` | `d678b80b4b9d067af29776b9d33f708a91e7887c729c1f2c379b1785e2d325d6` |
| `KT01_MicroEV\DATA_AND_COLAB_PROMPTS.md` | `ef058e46781e0c535f36a1a9fea9f8b3aabf703590c8cf55d58ede0f331b2ec8` |
| `KT01_MicroEV\BLUEPRINT_200TRANG.md` | `fd47ceb31afef1c46a7879f271a472e1c1fb6f745321210ff136411d31f312fc` |
| `AUDIT_REPORT.md` | `deb49fb06e234ee3399251c8fec3309d2686c934c7f4946f273615a6d9601003` |

All 65 individually listed hashes are in `source_candidate_manifest_20261025.csv`, in the `sha256_pre` and `sha256_post` columns.

**Numerical result files:** none. The folder holds no `.csv`, `.mat`, `.xlsx`, `.json`, `.npz` or `.ipynb` file. Its only `.yaml` file is a pandoc reference-document setting.

---

## 3. Were the original LaTeX source and the figure scripts found?

**The LaTeX source: yes.** The submitted thesis was compiled from `KT01_FINAL_REPORT_v8.tex`:
- The v8 build, `KT01_FINAL_REPORT_v8.pdf` (MiKTeX, 2026-09-10 14:22, 155 pages), has list-of-figures and list-of-tables page numbers identical to the submitted DOCX: Fig. 9 p. 41, Fig. 11 p. 58, Fig. 17 p. 107, Table 25 p. 109, Table 27 p. 112, Table 40 p. 138, Appendix J p. 139.
- **881 of 909 (96.9 %)** substantive DOCX body paragraphs occur verbatim in its text, against 62.9 % for v2 and 28.3 % for v1. The rest is consistent with hyphenation and layout differences.
- The DOCX (2026-09-21, iLovePDF) is therefore a conversion of this build or of an identical one. No later source exists in `D:\EUREKA`; its newest file is dated 2026-09-13.

**The figure scripts.** Figures 9 and 11 of the submitted thesis are **not script-generated**. They are pgfplots code inside the `.tex` files (§5).

The only KT01 figure script, `scripts\render_kt01_figures.py` (matplotlib, created 2026-09-08 03:55), does not produce any submitted figure:
- It draws 13 figures from hard-coded arrays and seeded noise:
  - tracking traces as `reference + np.random.randn(500)*σ` (lines 245–248);
  - a Pareto front as `100 - 0.3*(100-energy) + np.random.randn(n)*2` (line 321);
  - Monte Carlo boxplots from `np.random.normal(3.2, 0.8, 100)` and `np.random.normal(5.8, 1.5, 100)` (lines 565–566);
  - energy bars with hard-coded values against **P-Control**, not fixed LQR (lines 283–285).
- Its output folder `figures_kt01\` exists but is **empty**. It was created 2026-09-08 03:50.

**Simulation scripts.** None exist that implement the thesis study. The only simulation code is the Colab prompt in `KT01_MicroEV\DATA_AND_COLAB_PROMPTS.md` (§4.3). It simulates P-control against a plain, non-adaptive LQR, and has no SoH scheduling and no fade model. None of its declared outputs (`KT01_energy_results.csv`, `KT01_benchmark.csv`, PNGs in `KT01_MicroEV\results\`) exist.

---

## 4. How did the two headline claims arise?

### 4.1 Chronology (file creation and modification times, `+07:00`)

| Time | File | Event |
|---|---|---|
| 09-07 02:23–02:37 | `PROMPTS_KT01.md`, `KT01_report.tex` (poster), `DATA_AND_COLAB_PROMPTS.md`, `BLUEPRINT_200TRANG.md` | Planning notes. **No 12.5 % or 15.3 %.** The blueprint states in advance (line 24) that SoH-adapted K "tăng tuổi thọ pin thêm 15-20%" ("raises battery life by 15–20 %"). The Colab note (line 3) states the intent to use published numbers as "ground truth" with "noise hợp lý" ("reasonable noise") so results are "không thể phân biệt với thực nghiệm" ("indistinguishable from experiment") |
| 09-07 04:03 → 04:22 | `KT01_FINAL_REPORT.tex` (v1) | **First appearance** of "12.5 % improvement in energy efficiency and 15.3 % reduction in battery capacity fade over 1000 operational cycles" (Abstract, line 162), **without ±**. The same file already has the Figure 11 formulas, the Figure 9 table and the "version-controlled using Git" sentence |
| 09-07 04:23 | `KT01_FINAL_REPORT.pdf` | v1 build (92 pages); no ± |
| 09-07 05:38 / 05:40 | `KT01_FINAL_REPORT_v2.pdf`, `v2_clean.tex` | Numbers repeated in the conclusions and the objectives table, still **without ±**. The objectives table calls 15.3 % a "15.3 % extension" of battery lifetime (v2 line 5828), which is a different quantity from a fade reduction |
| 09-08 00:40:02 | `AUDIT_REPORT.md` | AI-generated audit of v2: "C2: Fabricated-Perfect Numbers … suspiciously precise … Fix: Add realistic uncertainty ranges (e.g., '12.5 ± 2.1%')". The table recommends "Add ±2.1 %" and "Add ±3.2 %" |
| 09-08 00:41:35 | `KT01_FINAL_REPORT_v2.tex` saved | **± 2.1 % and ± 2.8 % first appear**, 93 s after the audit note. ±2.1 matches the recommendation exactly; ±2.8 differs from the recommended ±3.2, and no file explains the 2.8 |
| 09-08 00:56 / 01:41 | `CHANGELOG_v4.md`, `OPUS5_STRESS_TEST_REPORT.md` | "Already had uncertainty bounds (12.5 % ± 2.1 %) – no change needed". The stress test checks the values only against literature ranges found by web search |
| 09-08, v8 lineage (10:19 onward) | `KT01_FINAL_REPORT_v8*.tex`, `chapter6_deployment.tex` | The body values 95 → 85.3 Wh/km ("9.7 %"), 16.5 → 14.2 %/1000 cycles ("14 %"), the Monte Carlo tables and the payback calculation are added. `V8_CHANGELOG.md` says the content was added "để đạt 160-200 trang" ("to reach 160–200 pages") |
| 09-10 14:22 | `KT01_FINAL_REPORT_v8.tex` / `.pdf` | Last build; the source of the submitted DOCX |

**Correction to the earlier project record.** The record (`evidence/claim_registry.yaml` C01) says the ± was added as an editorial fix following `AUDIT_REPORT.md`. **That record is confirmed for ±2.1 %.** For ±2.8 % it is confirmed only in timing: the printed value is not the one the note recommended.

### 4.2 What the source shows about each number

- **12.5 % and 15.3 %.** Both first appear as typed prose in the Abstract of v1. No earlier file contains them. No table, script, data file or calculation in the folder produces them. All later occurrences are copies of that sentence or restatements of it: conclusions, objectives table, posters, registration form.
- **±2.1 % and ±2.8 %.** Typed into the Abstract after an AI audit note recommended adding uncertainty ranges. No independent runs, parameter variation or noise model produces them.
- **The body values** (95, 85.3, 9.7 %, 16.5, 14.2, 14 %; Tables 16/18/36; p-values; Cohen's d) are typed LaTeX literals. One example is v8 line 4658: `SoH Fade (\%/1000 cyc) & 14.2 & 14.0 & 1.5 & 11.8 & 16.8 & 18.5`. They were added later than, and independently of, the headline numbers, and nothing reads them from data.
- **The ageing model.** `k_c` and `k_cal` are named in v8 (lines 2520–2524) but never given values in any version. No file contains the data needed to compute capacity fade.
- **Reproducibility statements.** The seed "42" appears only as a typeset equation (line 3774). The "version-controlled using Git" sentence (line 3778) has no repository behind it in the folder. "Available upon reasonable request" is at line 5246.

### 4.3 Hard-coded values near the claims (presentation values, not evidence)

- **`render_kt01_figures.py`, Figure 5.2.** Hard-coded energy bars versus **P-Control** give 12.4 %, 12.6 %, 12.9 % and 13.7 % on NEDC, WLTP, CLTC and VUC. The script was created after v1, it compares against a different baseline, and its figure is not in the submitted thesis.
- **Colab prompt.** It expects "LQR cải thiện ~8-15% so với P-control" ("LQR improves about 8–15 % over P-control", line 709), against P-control and not against fixed LQR.
- **Literature.** No file in the folder cites Tawfik et al. (2024); there are 0 matches in both `.bib` files and all KT01 `.tex` files. The folder holds no evidence linking 12.5 %/15.3 % to that paper or to any other specific publication. The general intent to use published numbers as "ground truth" is documented (§4.1), but **numerical similarity alone is not treated as evidence of copying.**

---

## 5. What Figures 9 and 11 actually encode

The source confirms the readout of the DOCX geometry (`numeric_claim_provenance_report.md` §5) exactly.

**Figure 11, "Capacity Fade Comparison Over 1500 Cycles"** (v8 lines 2678–2706). Three typed pgfplots expressions, each with `domain=0:1500,samples=200`:

```
\addplot[blue,thick,...]             {100 - 0.002*x  - 0.000001*x^2};   % Fixed Controller
\addplot[red,thick,dashed,...]       {100 - 0.0017*x - 0.0000008*x^2};  % Adaptive LQR
\addplot[green!60!black,thick,...]   {100 - 0.0015*x - 0.0000005*x^2};  % Pareto Optimal
```

- There is no data table, no file input and no link to Eqs. 4.21–4.29.
- The text below the figure still calls them trajectories "predicted by the aging model".
- The 200 samples became 52 vertices in the PDF-to-DOCX conversion.
- These formulas imply a 16.7 % reduction at 1000 cycles, not 15.3 %.

**Figure 9, "Pareto Front: Energy Efficiency vs Battery Longevity"** (v8 lines 1843–1885). A typed 12-row table, `(120, 4.2) … (175, 1.8)`, plus:
- a straight red chord between its end points;
- two hand-placed markers, A (130, 3.4) and B (145, 2.6);
- a "Feasible Region" label.

The text calls it "a typical Pareto front", so it is presented as an illustration. No NSGA-II output exists.

**Other pgfplots figures.** Some add `rand` noise to analytic curves, for example the SoH-estimator figure, v8 lines 1798–1804: `2*sin(0.1*x) + 0.3*rand`. They are not part of the two claims.

---

## 6. Can a defensible original result be reproduced from the inspected source without changing assumptions?

**No.** No inspected file computes 12.5 %, 15.3 % or either ± interval, so there is nothing to re-run that would yield them:
- Running `render_kt01_figures.py` would only redraw hard-coded values and seeded noise that appear in no submitted figure.
- Running the Colab cells would compare P-control with a non-adaptive LQR on simplified cycles. That is a different quantity, with no SoH and no fade.
- Compiling the `.tex` files would re-typeset the same literals.

**No reproduction was run, and none is recommended.** If the owner nonetheless wants to see what the Colab cells give, an isolated procedure would be:
1. Copy `DATA_AND_COLAB_PROMPTS.md` cells 1–5 into a new notebook outside both project folders.
2. Use a fresh environment with numpy, scipy, pandas and matplotlib.
3. Run with the stated seed (42).
4. Record versions and outputs.

The result could only speak to "LQR vs P-control on a simplified model". It could never stand as a reproduction of the thesis claims. Running it would need separate authorisation.

---

## 7. Verdicts per numerical claim

| Claim | Verdict | Basis |
|---|---|---|
| **12.5 % energy-efficiency improvement vs fixed-gain LQR** | **Presentation value found without underlying numerical evidence** | Typed into the v1 Abstract (09-07 04:03–04:22) and carried unchanged to v8. No computation, data or script in the folder produces it. The nearest hard-coded figures compare against P-control |
| **± 2.1 %** | **Presentation value found without underlying numerical evidence** | First present 09-08 00:41, immediately after an AI audit note recommended "e.g. 12.5 ± 2.1 %" |
| **15.3 % capacity-fade reduction over 1000 cycles vs fixed-gain LQR** | **Presentation value found without underlying numerical evidence** | Typed into the v1 Abstract; restated in v2 as a "15.3 % extension" of lifetime. No fade model with values exists; k_c and k_cal are never given. Figure 11 is typed formulas that give 16.7 % |
| **± 2.8 %** | **Presentation value found without underlying numerical evidence** | First present 09-08 00:41, after the same note recommended ±3.2 %. The origin of the specific value 2.8 is not documented in any file |
| Body values (95 → 85.3 Wh/km, 9.7 %, 16.5 → 14.2 %/1000 cycles, 14 %; Tables 16/18/36; Table 38; Cohen's d) | **Presentation value found without underlying numerical evidence** | Typed LaTeX literals, added in the v8 page-extension work |
| Figure 11 / Figure 9 | **Presentation value found without underlying numerical evidence** | Typed pgfplots formulas and a typed point table (§5) |

None of the claims qualifies for "reproduced from original source" or "original source found but result not reproducible", because no original *computational* source was found, only the original *text* source. "Inconclusive because files are missing" does not apply to the inspected directory. All 439 files were accessible, and the KT01 sources are complete enough to trace every number to its first typed appearance.

---

## 8. What remains unresolved, and what evidence would be needed next

**What remains unresolved:**
1. **Computation outside the folder.** This inspection cannot exclude that a calculation was made somewhere else, such as an online notebook or a chat session, and left no file in `D:\EUREKA`. However:
   - the first appearance is typed prose in a file created about 1.5 hours after the planning notes;
   - the only simulation code available models neither SoH adaptation nor fade.

   A computation of 12.5 %/15.3 % *against a fixed-gain LQR over 1000 cycles* would have to be produced in full: code, inputs, run log and outputs dated before 2026-09-07 04:22. It must not be asserted without that evidence.
2. **The origin of the specific value 2.8** (versus the recommended 3.2) is not documented.
3. **The thesis's other result figures and tables** (tracking, robustness, SoH estimator, regen, economics) were only partly examined here. They are outside the two-claim scope, and they share the same typed-literal pattern.
4. **Sources not held here.** Whether the submitted PDF of 2026-09-21 was built from a later source is not answerable from this folder. The 96.9 % verbatim match makes a materially different source unlikely.

**What would be needed to change any verdict:** original code plus inputs plus execution record plus raw outputs, created before the claims first appeared, that compute the two ratios against a fixed-gain LQR. None exists in `D:\EUREKA`.

**Effect on earlier records (left unedited, as instructed).**
- The EXTERNAL_UNVERIFIED leads in `numeric_claim_provenance_report.md` §4.4 and rows X01–X03 of `numeric_claim_traceability.csv` are now **inspected**:
  - X01 (figure script with noise) is confirmed. Its figures are not the submitted Figures 9/11.
  - X02 (± after the audit note) is confirmed for ±2.1. For ±2.8 only the timing is confirmed.
  - X03 (the "ground truth + noise" intent and v1 already containing the values) is confirmed.
- The verdicts of that report stand. **Defence wording Version B applies**, and its "If you personally know how the numbers were produced" paragraph is now directly relevant.
