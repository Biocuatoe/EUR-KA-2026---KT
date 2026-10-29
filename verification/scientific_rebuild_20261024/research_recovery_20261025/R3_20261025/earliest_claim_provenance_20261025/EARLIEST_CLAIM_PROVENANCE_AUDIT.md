# Earliest-origin provenance audit: 12.5 % ± 2.1 % energy and 15.3 % ± 2.8 % capacity-fade claims

**Date:** 2026-10-25. Inspection window 19:55:59–20:06:41 +07:00 (system clock).
**Evidence source:** `D:\EUREKA`, read-only. It holds 439 files (337,039,645 bytes) from two projects.
**Scope:** an independent second pass. The first pass is `../../../numeric_claim_provenance_20261025/final_source_inspection_20261025.md`. It hashed the Project B (CNTT02) files but did not open them, and it searched only literal values. This pass:
- searches **both** projects;
- covers number variants, decimals and related values;
- reads DOCX XML, PDF text and PNG metadata;
- re-derives the chronology and recalculates whatever can be recalculated.

**This file is the only file written to the project.** Working scripts and intermediate outputs live in the session scratchpad, which is temporary. Their hashes are listed in §8.

---

## 1. Executive verdict

| Claim | Verdict (brief's categories) | One-line basis |
|---|---|---|
| **12.5 %** energy improvement vs fixed-gain LQR | **Present but unsubstantiated** | First occurs as typed prose in the v1 Abstract (`KT01_FINAL_REPORT.tex` line 162, saved 2026-09-07 04:22). There is no derivation. The **same file's own energy table** gives fixed→adaptive reductions of 8.57–12.07 % (mean 10.29 %), so its "up to 12.5 %" cannot be reproduced even from the thesis's own typed numbers |
| **± 2.1 %** | **Present but unsubstantiated** | First occurs on 2026-09-08 at 00:41:35 in `KT01_FINAL_REPORT_v2.tex`, 93 s after an AI-generated audit note recommended exactly "e.g., '12.5 ± 2.1%'". No runs, sample size or definition exist anywhere |
| **15.3 %** capacity-fade reduction over 1000 cycles | **Contradicted by a reproducible calculation** (and otherwise present but unsubstantiated) | First occurs in the same v1 Abstract sentence. The same v1 file's typed aging table (LQR-fix 15.0 vs Adapt 14.2 %/1000 cycles) gives **5.33 %**, and the table itself prints "Improvement vs LQR … 5.3 %". The file's two typed figure formulas give 20.69 % and 16.67 %. No ageing model with parameter values exists anywhere |
| **± 2.8 %** | **Present but unsubstantiated** | First occurs in the same 00:41:35 save as ±2.1, after the note had recommended **±3.2 %**. No file explains 2.8. The only earlier "2.8" in an ageing context is a different quantity (§5.2) |

None of the four values qualifies as **directly reproducible** or **partially traceable**. None depends on Project B. **Attribution ambiguous** applies to no file that carries the claims.

---

## 2. Project separation

| Class | Files | Identifying evidence |
|---|---|---|
| **Project A: KT01, EURÉKA micro-EV / adaptive LQR / battery ageing** | 102 (96 by `KT01` filename; 6 by content: the 4 `chapter6_*.tex`, `V8_CHANGELOG.md`, `compile_log.txt`) | Thesis title "multi-objective adaptive LQR … battery aging compensation for urban micro-EV" (v1 line 158); terms LQR, SoH, capacity fade, Wh/km, drive cycle, VinFast; 38–40 A-terms and 0 B-terms in each `chapter6_*` file |
| **Project B: CNTT02, STGNN traffic anomaly detection (ITS)** | 173 (`CNTT02`/`cntt02`/`STGNN` in filename, `figures_cntt02\`, `scripts\render_cntt02_figures.py`; 4 by content: `CHANGELOG_v6.md`, `TOC_FULL_OUTLINE.tex`, `compile_output*.txt`) | METR-LA, PEMS-BAY, graph neural network, MAE/RMSE traffic metrics, ITS architecture |
| **Shared / both** | 38 | Cover both theses or neither: `AUDIT_REPORT.md` (audits KT01 v2 *and* CNTT02 v2), `OPUS5_STRESS_TEST_REPORT.md`, `readme.md`, `QUICKSTART_30PH.md`, `PHIEU_DANG_KY_EUREKA_2026.md`, a **single shared** `refs.bib` (6 A-terms / 24 B-terms), changelogs, build logs, LaTeX style rules |
| **Shared tool** | 5 | `pandoc\pandoc-3.1.13\*` (2024 distribution), `pandoc.zip` |
| **Ambiguous / unclassified** | 121 | 118 PNG and 4 PPM page renders and figures with no project term in their metadata; generic helper scripts (`fix_*.py`, `detect_blank.py`, `latex_to_docx.py` …); templates; `test.tex`. They stay ambiguous. None contains a target value in readable form (images were not OCR-read; see §7) |

**Project B result.** Every match of 12.5 / 15.3 / 2.1 / 2.8 in Project B is a **coincidental match**:
- a METR-LA dataset table cell (`… & 0.028 & 12.5 & 446 & …`);
- "MAE increase of 12.5 % during Tet";
- "12-hour gap: 12.5 % MAE increase";
- ambulance response "12.5 minutes to 9.2 minutes";
- a traffic-forecast "+15.3 %" improvement;
- table-of-contents section numbers 12.5 / 15.3;
- `ax.text(12.5, …)` plot coordinates;
- `(15,30)` inside a pgfplots coordinate list, caught by the comma-decimal variant.

No Project B file carries an energy or fade claim, and no Project B occurrence precedes the KT01 v1 save in a related context.

---

## 3. Chronological provenance ledger

Times are +07:00. "created" is the NTFS creation time and "modified" the last-write time. Line numbers count LF (`sed`/`awk` convention). Hashes are SHA-256, identical before and after inspection.

| # | Artifact (class) | Locator | Context (brief) | Kind of number | created → modified | Derivation? |
|---|---|---|---|---|---|---|
| L0 | `KT01_MicroEV\BLUEPRINT_200TRANG.md` (A) | line 24 | SoH-adapted K "tăng tuổi thọ pin thêm 15-20%" ("raises battery life by 15–20 %"); line 25 plans a Monte Carlo of 100 cycles, fixed vs adaptive K | **Target / expectation** | 09-07 02:37 → **09-08 03:48** | No |
| L0′ | `final_blueprint_KT01.md` (A) | line 280 | "Phải có số liệu cụ thể — 'Adaptive K giảm aging 15% so với fixed K'. Cite Peterson 2024 nếu có." ("Must have a concrete figure: 'Adaptive K reduces aging by 15 % vs fixed K'. Cite Peterson 2024 if available.") No "Peterson 2024" exists locally; `refs.bib` has only `peterson2010kinetic` | **Prescribed target wording** | 09-07 02:45 → **09-08 03:48** | No |
| L0″ | `KT01_MicroEV\DATA_AND_COLAB_PROMPTS.md` (A) | line 3; line 709 | Intent: use published numbers as "ground truth" plus "noise hợp lý" ("reasonable noise") so results are "không thể phân biệt với thực nghiệm" ("indistinguishable from experiment"). Expected result "LQR cải thiện ~8-15% so với P-control" ("LQR improves ~8–15 % over P-control") | Target, **against P-control** | 09-07 02:30 → **09-13 17:03** | No; declared outputs (`KT01_energy_results.csv`, `results\`) do not exist |
| **L1** | **`KT01_FINAL_REPORT.tex` (A), v1** | **line 162** (Abstract) | "…achieves up to 12.5\% improvement in energy efficiency and 15.3\% reduction in battery capacity fade over 1000 operational cycles compared to the fixed-gain LQR baseline." **No ±.** Only occurrence of either value in v1 | **Manually entered prose** | **09-07 04:03:59 → 04:22:23** | **No** |
| L1a | same file | lines 2654–2668 | Typed energy table (Wh/km): LQR-fix 132/155/140/116, avg 136; Adapt 118/138/128/102, avg 122. Text line 2675: "10.3 % improvement compared to the Fixed LQR" | Manually entered table | same | Typed only. It **conflicts** with L1 (§5.1) |
| L1b | same file | lines 2852–2871 | Typed aging table: fade rate LQR-fix 15.0, Adapt 14.2 %/1000 cycles; "Improvement vs LQR … 5.3 %"; EOL 938→1012 cycles ("7.9 %"); text line 2727: "simulates 1000 charge-discharge cycles … approximately 48 hours of computation time" | Manually entered table | same | Typed only. It **contradicts** L1 (§5.1) |
| L1c | same file | lines 945–949; 2742–2830 | pgfplots formulas `100-0.002*x-0.000001*x^2` (fixed), `100-0.0017*x-0.0000008*x^2` (adaptive); seven further formulas per controller in the aging figure | Typed figure formula | same | Formulas only, with no data link |
| L1d | same file | lines 2133–2140 | `randn('seed', 42)`; "All simulation scripts, models, and data are version-controlled using Git" | Typed statement | same | No repository or script exists in `D:\EUREKA` |
| L2 | `KT01_FINAL_REPORT.pdf` (A) | PDF text line 93 | Same sentence; embedded `CreationDate` Mon Sep 7 **04:23:23** 2026 (dvipdfmx), 92 pages | Typeset copy of L1 | 09-07 04:22 → 04:23 | — |
| L3 | `KT01_FINAL_REPORT_v2.pdf`, `KT01_FINAL_REPORT_v2_clean.tex` (A) | v2_clean lines 164, 5792, 5825, 5831 | Abstract and conclusions repeated, still **no ±**. New objectives table: O1 "Error reduction ≥5 % vs fixed LQR → **12.5 % reduction**" (tracking error, not energy); O4 "Battery lifetime extension ≥10 % → **15.3 % extension**" (lifetime, not fade). Also new: Monte Carlo box (line 8030) "Battery Aging Rate (%/1000 cycles) & 2.8 & 0.3 & 2.3 & 3.3" | Manual copies, **relabelled** | PDF CreationDate 09-07 05:38:08; tex 05:40:54 | No |
| L4 | `KT01_FINAL_REPORT.docx` (A) | document.xml paragraph 60 | Same Abstract, no ±. python-docx template metadata (2013 dates: meaningless) | Converted copy | 09-07 05:41 | — |
| **L5** | **`AUDIT_REPORT.md` (Shared)** | lines 24–28, 195–196, 279 | Audits KT01 v2 ("Line 164, 5792"): "C2: Fabricated-Perfect Numbers … Fix: Add realistic uncertainty ranges (e.g., '12.5 ± 2.1%')". Table: "Add ±2.1%" / "Add **±3.2%**". Signed "Report generated by AI Audit System" | **Recommendation text** | **09-08 00:40:02** | No; the values are suggestions |
| **L6** | **`KT01_FINAL_REPORT_v2.tex` (A)** | **line 164** | "12.5\% $\pm$ 2.1\% … 15.3\% $\pm$ 2.8\% …" — **first ± anywhere**. The same save also applies the audit's other fixes (duplicate acronyms removed, mojibake bullets repaired, BOM removed; 147 differing lines vs v2_clean) | Manually entered | 09-07 04:51 → **09-08 00:41:35** | No |
| L7 | `CHANGELOG_v4.md`, `OPUS5_STRESS_TEST_REPORT.md` (Shared) | v4 line 20; stress test lines 29, 149–152 | "Already had uncertainty bounds (12.5 % ± 2.1 %) – no change needed"; values judged "Realistic" only against web-searched literature ranges (IGWO-LQR 17.6 %, OACC 9.7 %) | Post-hoc commentary | 09-08 00:56; 01:41 | No |
| L8 | v3 → v7, v8 lineage (A), 40 `.tex` versions and backups | Abstract line 149–168 | Identical claim sentence carried forward. From v6 on, only the Abstract occurrence remains | Copies | 09-08 00:43 → 09-10 14:21 | No |
| L9 | `KT01_FINAL_REPORT_v8.tex` / `.pdf` (A) | tex line 157; pdf text line 124 | Final source of the submitted thesis (prior pass: 96.9 % paragraph match to the submitted DOCX). New body values: lines 5471–5481 "Baseline energy: 95 Wh/km (fixed LQR) … 85.3 … Savings: 9.7 Wh/km = 9.7 %"; "Baseline SoH fade: 16.5 %/1000 cycles (fixed LQR) … 14.2 … 14 % reduction" | Typed | pdf CreationDate 09-10 14:22:26 | No (§5.3) |
| L10 | Posters, `PHIEU_DANG_KY_EUREKA_2026.md` (A/Shared) | e.g. registration form line 53, "12,5% … 15,3%" | Vietnamese comma-decimal copies, no ± | Copies | 09-09 18:17 → 09-10 13:23 | No |

### Earliest occurrences, as the brief requires

| Question | 12.5 % | 15.3 % | ±2.1 % | ±2.8 % |
|---|---|---|---|---|
| Earliest **surviving** occurrence (claim context) | L1, v1 tex line 162 (≤ 09-07 04:22:23) | L1, same line | L5 as a *recommendation* (09-08 00:40:02); L6 as a *claim* (00:41:35) | L6 (09-08 00:41:35) |
| Earliest occurrence **with a verifiable derivation** | **None** | **None** | **None** | **None** |
| Earliest in a **EURÉKA-specific** artifact | L1 | L1 | L6 | L6 |
| Earliest in **any** artifact, Project B included | L1. The earliest Project B "12.5" is a ToC section number in `CNTT02_FINAL_REPORT_v2.pdf`, 09-07 05:37 (coincidental) | L1. The CNTT02 v1 `(15,30)` coordinate match (≤ 04:23:34) is a false positive | L5 | L6 |
| Occurrence whose **timing is unknown** | Planning notes L0–L0″: content created before v1 but rewritten later; their pre-v1 text cannot be known | Same. L0′ ("15 %") and L0 ("15–20 %") are near-values whose pre-v1 wording is unknown | — | — |

---

## 4. Evidence chain

```
[planning notes, created 09-07 02:30–02:45, last rewritten 09-08 / 09-13]
  targets: "15-20 %" life (L0), "Adaptive K giảm aging 15 %" (L0'), "~8-15 % vs P-control" (L0'')
        │  (no data, no code output, no file reference links these to L1)
        ▼
L1  v1 Abstract, typed prose: 12.5 % / 15.3 %      ◄── no formula, no input, no run, no table feeding it
        │         └── same file's own typed tables give 10.29 % (max 12.07 %) and 5.33 % → conflict
        ▼
L2  v1 PDF (04:23) ─► L3 v2 / v2_clean (05:38–05:40, + relabelled objectives table) ─► L4 DOCX (05:41)
        ▼
L5  AI audit note (09-08 00:40:02): "add e.g. ±2.1 %", "±3.2 %"
        ▼
L6  v2.tex (00:41:35): "12.5 % ± 2.1 %", "15.3 % ± 2.8 %"   ◄── no runs, no definition, no n
        ▼
L7  changelog / stress test treat the ± as pre-existing ─► L8 v3…v8 copies ─► L9 v8 build (09-10 14:22)
        ▼
submitted DOCX (2026-09-21 iLovePDF conversion of the v8 build; prior pass) ─► Abstract only
```

**The chain is a text-copy chain only.** At no link does a formula, code, input dataset or raw output connect to the headline numbers.

**Searched for and not found** anywhere in the 439 files:
- any `.csv`, `.json`, `.mat`, `.xlsx`, `.npz` or `.ipynb`;
- any simulation log or run identifier;
- any script that computes energy or capacity fade for a fixed-gain LQR against an SoH-scheduled LQR.

`scripts\render_kt01_figures.py` (created 09-08 03:55, after L1):
- draws hard-coded arrays and seeded noise;
- uses **P-control** as its energy baseline;
- writes to `figures_kt01\`, which is empty.

The v1 tables and figures (L1a–L1c) sit in the same file as the claim but do not feed it.

---

## 5. Recalculation records

All inputs below are **typed literals transcribed from the cited lines**; no project code was executed. Formula: relative reduction `r = (baseline − proposed) / baseline × 100 %`. Arithmetic is exact to the printed decimals (tolerance ±0.005 pp).

### 5.1 From v1 (`KT01_FINAL_REPORT.tex`), the same file that introduces both claims

| Quantity | Inputs (line) | Result | Claim | Outcome |
|---|---|---|---|---|
| Energy, Adapt vs LQR-fix, NEDC / WLTP / CLTC / VUC | 132→118, 155→138, 140→128, 116→102 Wh/km (2658–2664) | 10.61 / 10.97 / 8.57 / **12.07** % | "up to 12.5 %" | Not reproduced; maximum 12.07 % |
| Energy, Adapt vs LQR-fix, Avg row | 136→122 (2666) | **10.29 %** (file text: "10.3 %") | 12.5 % | Not reproduced |
| Energy, Adapt vs P, Avg row | 148→122 | 17.57 % (file text: "17.6 %") | — | Internally consistent |
| Fade rate, Adapt vs LQR-fix | 15.0→14.2 %/1000 cycles (2860) | **5.33 %** (table prints "5.3 %") | 15.3 % | **Contradicted** (×2.9 gap) |
| Capacity loss from final SoH | 100−85.0 → 100−85.8 (2858) | 5.33 % | 15.3 % | Contradicted |
| Cycles to 80 % SoH | 938→1012 (2862) | +7.89 % (file text: "7.9 %") | — | Internally consistent |
| Aging-figure formulas L(1000) = a·N + b·N² | LQR-fix (0.0020, 0.9e-6) → 2.90 pp; Adapt (0.00165, 0.65e-6) → 2.30 pp (2742–2830) | 20.69 %; retention 97.1 / 97.7 %, while the table gives 85.0 / 85.8 % | 15.3 % | Contradicted; the formulas also disagree with the table by about 12 pp of SoH |
| Ch. 2 capacity-fade formulas | fixed (0.002, 1e-6) → 3.00 pp; adaptive (0.0017, 0.8e-6) → 2.50 pp (945–947) | 16.67 % | 15.3 % | Not reproduced. The same formulas appear in the submitted Fig. 11 |

The table's own "Improvement" rows are partly inconsistent with its fade-rate row (recomputed vs printed):

| Row | Recomputed | Printed |
|---|---|---|
| PID vs P | 4.24 % | 5.3 % |
| MPC vs P | 12.12 % | 12.7 % |
| DDPG vs P | 6.06 % | 7.7 % |
| Adapt vs P | 13.94 % | 16.5 % |
| MPC vs LQR | 3.33 % | 3.9 % |
| DDPG vs LQR | −3.33 % | +3.6 % |

**Coincidence scan.** All ordered cell pairs in the same row were checked against the targets (±0.05 pp):
- **12.5 %** arises only for P→MPC on WLTP (168→147) and P→Fuzzy on VUC (128→112). Neither compares fixed LQR with adaptive LQR. They are **numerical coincidences, not evidence of derivation**.
- **15.3 %** arises from no pair.
- ~2.1 and ~2.8 arise from several unrelated pairs (e.g. P→PID on NEDC, 2.82 %) and carry no meaning.

### 5.2 Uncertainty terms

There is nothing to recalculate. No artifact contains repeated runs, a sample size, seeds actually used, or a definition (SD, SE, CI, sensitivity) of ±2.1 or ±2.8.

**Resemblances, which are not origins:**
- (a) `AUDIT_REPORT.md` line 28 contains the literal string "12.5 ± 2.1%". This is the closest documented antecedent of ±2.1, and it is a suggestion, not a measurement.
- (b) `v2_clean.tex` line 8030 (09-07 05:40, before any ±): "Battery Aging Rate (%/1000 cycles): mean **2.8**, SD 0.3". This is a **mean aging rate in percentage points**, not a spread of a percentage reduction. It is also about 5× below v1's own fade rates (14.2–16.5). Whether it influenced the choice of 2.8 is **undeterminable**.
- (c) The same box lists "Regen Efficiency … SD 2.1": a different quantity.
- (d) The later v8 Monte Carlo tables (lines 4505, 4654–4658) give one-arm values only: energy SD 4.2 Wh/km, fade SD 1.5 %/1000 cycles. With no paired baseline arm, no SD of a percentage difference can be formed from them.

### 5.3 Later artifacts (cross-check only)

| Artifact | Inputs | Result | Printed | Note |
|---|---|---|---|---|
| `render_kt01_figures.py` lines 283–284 | P-control 18.5/22.3/20.1/16.8 → adaptive 16.2/19.5/17.5/14.5 | 12.43 / 12.56 / 12.94 / 13.69 % (mean 12.90) | — | Created after L1; baseline is **P-control**; figure not in the thesis |
| v8 lines 5471–5473 | 95 → 85.3 Wh/km | **10.21 %** | "9.7 Wh/km = 9.7 %" | Arithmetic error in the source |
| v8 lines 5479–5481 | 16.5 → 14.2 %/1000 cycles | 13.94 % | "14 % reduction" | 16.5 was the **P controller's** fade in v1 (fixed LQR was 15.0); relabelled "fixed LQR" in v8 |

None of these reproduces 12.5 % or 15.3 % against a fixed-gain LQR.

### 5.4 Same-task and ageing checks, as the brief requires

**Energy.** No early artifact records completed distance, trip time, a speed-reference definition, initial SoC/SoH, constraint or tolerance settings, or a battery-side energy accounting convention (traction minus regen) for any pair of runs. The only numbers are typed Wh/km table cells. **A same-task comparison is therefore not demonstrated.**

**Capacity fade.** No early artifact:
- identifies a cell or chemistry with parameters (v1 names SEI growth and an Arrhenius term, and `J_aging` at line 1253 uses α, β, E_a with no values);
- gives fitted coefficients or their test conditions;
- defines the cycle (charge–discharge cycle vs drive-cycle repetition);
- gives an extrapolation procedure.

The "1000 cycles" exists as prose, as typed table cells and as pgfplots formulas. **Modelled capacity loss is not demonstrated.** Neither Ah-throughput nor an ∫i²dt proxy is computed anywhere either.

---

## 6. Missing links needed to substantiate either claim

1. Code or notebook, dated before 2026-09-07 04:22, that simulates **fixed-gain LQR vs SoH-scheduled LQR** on the stated drive cycles.
2. Its inputs: vehicle and powertrain parameters, cell/pack model, drive-cycle files, the SoH trajectory or schedule.
3. Raw outputs per run (energy drawn, energy regenerated, distance, time, tracking error) and the accounting convention.
4. A sourced ageing model with parameter values and fitting conditions, plus the 1000-cycle procedure and the fade definition.
5. The repeated-run design behind ±2.1 / ±2.8: n, seeds, variability source, statistic.
6. The "Git" repository claimed at v1 line 2140. No `.git` or exported history exists in `D:\EUREKA`.
7. Original pre-v1 content of the planning notes (L0–L0″). Their current text is a later rewrite.

---

## 7. Conflicts and caveats

**Internal contradiction in the first artifact.** v1 states 15.3 % in its Abstract and prints 5.3 % in its own results table, and states "up to 12.5 %" against a table maximum of 12.07 %. The earlier pass reported that the body values 16.5 / 14.2 were "added in the v8 page-extension work". **That needs correcting:** both numbers already exist in v1's aging table, there as the P controller's and the adaptive controller's fade rates.

**Relabelling over time.** The same 12.5 / 15.3 appear in v2 as:
- a tracking-*error* reduction (O1);
- a *lifetime extension* (O4).

The same 16.5 is v1's **P-controller** fade but v8's "fixed LQR" fade.

**Planning-note timestamps.** Every planning note created before v1 was last written at exactly **2026-09-08 03:48:40** or **2026-09-13 17:03:27**, in batches with identical timestamps. Their current content therefore does not show what existed before L1. The absence of 12.5 / 15.3 in them, and the presence of "15–20 %" and "15 %", describe **later** text.

**Timestamp reliability.**
- NTFS creation and modification times can be preserved or reset by copy or sync tools. The many backups with created > modified are copies made later.
- The ordering L1 < L5 < L6 is supported independently by the build's embedded PDF `CreationDate` (v1 04:23:23, v2 05:38:08) and by content: the ± are absent from v2_clean and the v2 PDF, and the audit note quotes v2 lines 164 and 5792 *without* ±.
- Timestamps cannot exclude a computation done outside this folder.

**Literature.**
- No local bibliographic record, PDF, DOI or note links 12.5 / 15.3 / 2.1 / 2.8 to any publication. "Tawfik", "BMW i3", "171.3" and "149.2" occur nowhere locally.
- The resemblance to Tawfik et al. 2024 (13 % / 15.8 %) recorded in the earlier pass was not re-examined here, because there was no network access. It remains an **observation of numerical similarity, not evidence of origin**.
- "Peterson 2024" (L0′) is not in either `.bib`.
- The genuineness of `peterson2010kinetic` was not checked offline.

**Unreadable or partly read files.**
- `KT01_FINAL_REPORT_v3.pdf` and `KT01_BACKUP_v9.pdf` are truncated builds with no xref or trailer. Raw stream inflation recovered no text (XeLaTeX glyph IDs). Their `.tex` sources were searched.
- 118 PNG and 4 PPM images were checked for embedded text chunks only. No OCR engine is installed and none was installed. All images were created ≥ 09-08 03:16, after L1. One KT01 page render (`fig11_capacity_fade_page75.png`) was viewed: a typeset page with no plotted curves.
- `pandoc.exe` was not inspected (third-party binary).

**Authorship and intent.** Nothing here establishes who typed any value or why. The AI-signed audit note and the prompt-style planning notes are reported as content only.

---

## 8. Integrity information

**Hash snapshots of all 439 files** were taken at 19:55:59 (pre, before any content was read) and 20:06:41 (post):
- path, size, NTFS creation time, modification time and SHA-256 are **identical** for 439/439 files;
- the pre snapshot also equals the earlier pass's 12:14:05 snapshot (path, size, SHA-256).

**Last-access times, stated plainly.** `fsutil` reports `DisableLastAccess = 2 (System Managed, Disabled)`, yet reads do update last-access times on this volume:
- before this pass began they already showed 2026-10-25 for 433 files, i.e. they had been overwritten by the earlier inspection and by this pass's first hash read;
- this pass updated them again;
- the 6 zero-byte files, never opened, keep their original values;
- last-access times therefore carry **no** evidential value. They were not reset, because resetting would itself be a write.

**Access method.**
- Nothing in `D:\EUREKA` was written, renamed, moved, executed or compiled.
- Files were read in binary mode (`open('rb')`, `zipfile`).
- The 40 PDFs were copied (`shutil.copy2`) to the scratchpad and read there with MinGW `pdftotext` and MiKTeX `pdfinfo`.
- No network, no installs, no Git commands.
- No thesis, LaTeX, code, protocol, audit, R1/R2/R3 output or earlier record was modified.

| Key artifact | Size | Created → Modified | SHA-256 |
|---|---|---|---|
| `KT01_FINAL_REPORT.tex` (v1) | 163536 | 09-07 04:03:59 → 04:22:23 | `5ea971a19f67dc2b6d026cb872690177cbc86abe0673cb111b789b4bdc901b75` |
| `KT01_FINAL_REPORT.pdf` (v1) | 360627 | 09-07 04:22:06 → 04:23:23 | `5a5d5e842848f0ba7bef83baaae1b56b074ff623a5f5689d421095716ee063ff` |
| `KT01_FINAL_REPORT_v2_clean.tex` | 402595 | 09-07 05:40:54 | `97aa23b3b0f0dad25f23ee1d56f9da64884daf699e9b06ccef487cd39ed1939f` |
| `KT01_FINAL_REPORT_v2.pdf` | 597741 | 09-07 04:53:26 → 05:38:08 | `8ce9daf5110c8e29eba6475f674214aefa380a2c108ec037892a278ff62d1b30` |
| `KT01_FINAL_REPORT.docx` | 73000 | 09-07 05:41:59 | `20d98235f2179ad1e811d0b1969bcc8e30a9b04ed176ee579ff17defbf35a633` |
| `AUDIT_REPORT.md` | 8984 | 09-08 00:40:02 | `deb49fb06e234ee3399251c8fec3309d2686c934c7f4946f273615a6d9601003` |
| `KT01_FINAL_REPORT_v2.tex` | 402331 | 09-07 04:51:49 → 09-08 00:41:35 | `b239db82f93785e14ff0192611111c6dbee1eb2c8a02f7b8e70fdf9e0824a7dd` |
| `CHANGELOG_v4.md` | 4457 | 09-08 00:56:40 | `ed11712aafcb880817e458cc9a47511ce602bf872d0255be8bc6503e0c788d80` |
| `OPUS5_STRESS_TEST_REPORT.md` | 16869 | 09-08 01:40:24 → 01:41:28 | `d82d0019dd62274dc6b0660abbdb435e512474daf41d759e78d2c377d1c3e4a2` |
| `KT01_FINAL_REPORT_v8.tex` | 251660 | 09-09 06:26:52 → 09-10 14:21:47 | `586b06951c2bceb9ff5b92f48a6755e7f69e4ef2350f838aa0ab648475050732` |
| `KT01_FINAL_REPORT_v8.pdf` | 588336 | 09-09 09:19:00 → 09-10 14:22:26 | `d93abac2219e355c77163375f111efeb3909fbf7bf1e4801fbc0ac27579a1a16` |
| `final_blueprint_KT01.md` | 35402 | 09-07 02:45:33 → 09-08 03:48:40 | `8bdf66b66671080b0f4dc10a426d78faca52bac8d194df4e6ba07c7cd345f0c8` |
| `KT01_MicroEV\BLUEPRINT_200TRANG.md` | 22475 | 09-07 02:37:33 → 09-08 03:48:40 | `fd47ceb31afef1c46a7879f271a472e1c1fb6f745321210ff136411d31f312fc` |
| `KT01_MicroEV\DATA_AND_COLAB_PROMPTS.md` | 27796 | 09-07 02:30:12 → 09-13 17:03:27 | `ef058e46781e0c535f36a1a9fea9f8b3aabf703590c8cf55d58ede0f331b2ec8` |
| `scripts\render_kt01_figures.py` | 24186 | 09-08 03:55:11 | `d678b80b4b9d067af29776b9d33f708a91e7887c729c1f2c379b1785e2d325d6` |
| `PHIEU_DANG_KY_EUREKA_2026.md` | 5933 | 09-10 13:23:26 | `ac54abb2232803272c07727a88530353fd550c710e2c711dc621f5a49abfddd0` |
| `refs.bib` (shared) | 16632 | 09-07 03:56:07 → 09-09 05:45:02 | `dbd01a134f11fdd37f76a5c025f0a38167e2ced5ab5adfa3838e197cb2431275` |
| `CNTT02_FINAL_REPORT.tex` (Project B v1) | 117086 | 09-07 04:09:24 → 04:23:34 | `6d1d5bffdbf8f45588ad81d9d8513924d952106a2bcad90d517036d49c751dbd` |
| `KT01_FINAL_REPORT_v3.pdf` (truncated) | 63912 | 09-08 00:43:25 → 00:44:43 | `3d0e084dcc3f544785bb44a472b73d59592bbcc4fe19e585145db4ecba662c98` |
| `KT01_BACKUP_v9.pdf` (truncated) | 6605 | 09-08 14:30:22 | `6cfacee39a298e75c87bb26466589019ac9c519685d6a1808c28f3187bcd13ba` |

**Scratchpad working files** (temporary, outside the project):
- `pre.csv` / `post.csv`: full 439-file manifests;
- `hits.csv`: 2,421 variant matches;
- `classification.csv`;
- `recalc_v1.py` / `recalc_later.py` and their outputs.

SHA-256 of the main working files:
- `pre.csv` `712aa81a…6935`;
- `post.csv` `45690ca3…5d19`;
- `recalc_v1.py` `731e4707…e31185`;
- `recalc_v1.out` `8fccf791…7ad4d`;
- `recalc_later.py` `7d2c94c1…b5f`.

**Search patterns.**
- Targets: 12.5 / 15.3 with `.` or `,` and optional trailing 0; ±/`\pm`/`+/-` 2.1 and 2.8; 2.1 % and 2.8 %.
- Decimals and complements: .125, .153, .021, .028, .875, .847.
- Related values: 85.3, 16.5, 14.2, 9.7 %, "1000 cycles" variants, 15–20 %, 8–15 %.
- 0.153, 0.875 and 0.847 occur nowhere. 0.125 occurs only in CSS and pgfplots styling. 0.021 and 0.028 occur only in unrelated tables (e.g. METR-LA missing-data rate 0.028).

---

## 9. Recommended next step per claim

| Claim | Status | Next step |
|---|---|---|
| 12.5 % | **Unsupported by the current surviving evidence** | Do not present it as a result. Recovery would need **new independent validation**: a same-task fixed vs SoH-scheduled LQR comparison. The R3 study in this folder ran one, and SoH scheduling gave ≤ 0.04 % (`../R3_claim_implications.md`) |
| ± 2.1 % | **Unsupported**; not recoverable | No variability design exists. Withdraw it; it is not estimable without new repeated runs of a defined experiment |
| 15.3 % | **Unsupported, and contradicted by the earliest artifact's own typed values** (5.33 %) | Withdraw. Any fade claim needs a sourced, parameterised ageing model and a defined cycle procedure (R3 computed no fade, for lack of a cell datasheet) |
| ± 2.8 % | **Unsupported**; not recoverable | Withdraw, as for ±2.1 |

The only thing that could legitimately change these verdicts is **external** evidence: code, inputs, run logs and outputs created before 2026-09-07 04:22 that compute both ratios against a fixed-gain LQR. Examples are a Colab notebook in a cloud account or a chat-session export. Nothing in `D:\EUREKA` qualifies.

---

## 10. Confidence statement

**High confidence**, from direct, hash-verified reading:
- The earliest surviving occurrence of both 12.5 % and 15.3 % in a claim context is `KT01_FINAL_REPORT.tex` line 162, saved ≤ 2026-09-07 04:22:23, as typed Abstract prose with no derivation.
- The ±2.1 % / ±2.8 % terms first appear at 2026-09-08 00:41:35, after an AI audit note suggested "±2.1 %" and "±3.2 %".
- No computational artifact for any of the four values exists in `D:\EUREKA`.
- v1's own typed tables give 10.29 % (max 12.07 %) energy and 5.33 % fade reductions vs fixed LQR.
- All Project B matches are coincidental, and no claim-bearing file is attributable to Project B.

**Moderate confidence:**
- The ± insertion was part of a batch of audit-driven edits. The same save applies the note's other fixes, but no file says so explicitly.
- The planning notes' targets (15–20 %, 15 %, 8–15 % vs P-control) are near the claimed values. Whether their wording before v1 matched is unknown, because the notes were rewritten later.

**Cannot be determined from the available evidence:**
- whether a calculation was performed outside `D:\EUREKA` before 04:22 on 2026-09-07;
- why 2.8 was used instead of the recommended 3.2;
- whether the v2_clean "2.8" mean aging rate played any role;
- whether any external publication inspired the numbers;
- who entered any value, and with what intent.

"Not found in the surviving local evidence" here does not mean "never existed".
