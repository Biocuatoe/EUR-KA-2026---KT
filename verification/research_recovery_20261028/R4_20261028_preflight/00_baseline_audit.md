# R4 preflight — Phase 0: baseline inventory and evidence integrity

**Date:** 2026-10-28, from 00:30 local time (UTC+7).
**Prepared by:** the AI assistant (Claude) in a Claude Code session. No person has reviewed it. Earlier R1–R3 work was done by the same kind of assistant, so this audit is not independent of that work.
**Mode:** read-only for everything outside this directory. Every check below was executed. The scripts are in `tools/` and their outputs sit next to this file.
**Scope:** KT-01 (micro-EV, fixed vs SoH-scheduled LQR) only. CNTT-02 is excluded (§7).

Evidence labels used throughout:
- **[D] direct:** the artefact was opened or hashed in this run.
- **[A] arithmetic:** recomputed in this run from retained numbers.
- **[I] inference:** reasoned from direct evidence, but not observed.
- **[H] inherited:** stated in an earlier report and not re-checked here.
- **[U] unknown.**

---

## 1. Project roots and boundaries

| Path | Exists | Role | Access in this run |
|---|---|---|---|
| `D:\EURÉKA 2026 - KT` | yes [D] | Main KT-01 research root. Holds the thesis DOCX copy, R1–R3, the Modelica cross-check and the earlier audits | read; writes only inside the R4 directory below |
| `D:\EURÉKA 2026 - KT\verification\research_recovery_20261028\R4_20261028_preflight` | created 2026-10-28 00:32 [D] | **R4 output directory.** Its parent did not exist before this run, and no other R4 directory exists in the project (a search for `*R4*` found only unrelated Modelica library images) | write (only place written) |
| `D:\EURÉKA 2026 - KT\verification\scientific_rebuild_20261024\` | yes [D] | R1 root, containing R2 (`research_recovery_20261025\`) and R3 (`research_recovery_20261025\R3_20261025\`) | read |
| `D:\EUREKA` | yes [D] | Legacy workspace: KT-01 and CNTT-02 thesis sources, AI audit notes | **files re-hashed only** (§2.3); no file content was read from this tree |
| `C:\Users\HLC\EUREKA_EVIDENCE\GATE1_20261028` | yes [D] | Evidence snapshot, created 2026-10-28 00:27 (folder time), 5 min before this run | read and hashed |
| `C:\Users\HLC\.cursor\projects\d-EUREKA` | yes [D] | Source of the 131 Cursor transcript files in the snapshot | file walk (names, sizes) and re-hash of the 131 snapshotted files |
| `D:\EUREKA-2026` | **no** [D] | Earlier project location, deleted 2026-10-23 (`docs/migration-2026-10-23.md`) [H] | — |

**Write probe.** The R4 directory accepted a create, read and delete of a test file (exit 0) before any deliverable was written [D].

**Access note on `D:\EUREKA`.** Earlier session records say the owner restricted opening `D:\EUREKA` to explicitly authorised, read-only inspections. This run's instructions name the folder and ask for a read-only source-to-snapshot hash comparison. I took that as authorisation for hashing only. Every file was opened in binary read mode. Reading can update last-access times on that volume, and an earlier audit found that access times there carry no evidential value [H]. No modification time, content or file was changed (§9).

**Path ambiguity.** None remains. The three generations are distinct and identified:
- `D:\EUREKA` holds the September 2026 thesis-writing workspace;
- `D:\EUREKA-2026` is the deleted October 2026 project folder;
- `D:\EURÉKA 2026 - KT` is the current research root.

R1–R3 exist only in the current root. Nothing with R1–R3 content was found in, or is expected in, `D:\EUREKA`.

## 2. Evidence snapshot and manifest

### 2.1 What the snapshot is

| Item | Value |
|---|---|
| Manifest | `MANIFEST.sha256.csv`, 570 rows; columns: source_path, snapshot_path, source_size_bytes, source_sha256, source_sha256_end, snapshot_sha256, verified, error |
| Manifest SHA-256 (recorded here as an external anchor) | `A93EB44FC128DAC30E754C6EA996D67AB381B78A708A999C8BE1DE7600D4F279` |
| Bytes covered | 345,749,891 |
| Contents | `workspace\` = 439 files from `D:\EUREKA` (the whole tree); `transcripts\` = 131 files from `C:\Users\HLC\.cursor\projects\d-EUREKA\agent-transcripts` (all of them) |
| Scope statement, README or creation script inside the snapshot | **none** [D]. The scope is implied by the rows only. Who created the snapshot, and with which tool, is not recorded in it [U] |

### 2.2 Internal consistency and snapshot integrity (all 570 rows)

Command: `tools/check_snapshot_manifest.py` (exit 0). Per-row results are in `00_snapshot_integrity_rows.csv` and the summary in `00_snapshot_integrity_summary.json`.

| Check | Result |
|---|---|
| S1 snapshot file exists | 570 / 570 |
| S2 size equals recorded source size | 570 / 570 |
| S3 SHA-256 of snapshot file equals recorded snapshot hash | 570 / 570 |
| S4 recorded source hash = source hash at end of copy = snapshot hash | 570 / 570 |
| S5 `verified = True` and no error | 570 / 570 |
| Files in the snapshot that the manifest does not list | 0 |

### 2.3 Source-to-snapshot comparison (read-only)

| Check | Result |
|---|---|
| R1 source file still exists | 570 / 570 |
| R2 SHA-256 of source file now equals recorded source hash | 570 / 570. `D:\EUREKA` and the transcripts are byte-identical to the snapshot as of this run |
| `D:\EUREKA` files not covered by the manifest | 0 of 439 walked |
| `C:\Users\HLC\.cursor\projects\d-EUREKA` files not covered | 192 of 323. None of them are agent transcripts: 94 canvases, 65 MCP descriptors, 32 assets, 1 terminal log |

### 2.4 Integrity checks not performed

- Cursor workspace storage (`AppData\Roaming\Cursor\User\workspaceStorage\…`, `state.vscdb`), Google Colab/Drive, other machines and cloud accounts are **not in the snapshot and were not inspected**. They are named as open leads in the earlier external-search report [H].
- The 192 uncovered Cursor files were not hashed.
- The manifest's own hash had no earlier external record. The value in §2.1 anchors it from now on.

## 3. KT-01 thesis and version lineage

| Item | Evidence | Status |
|---|---|---|
| Thesis DOCX in the research root: `EURÉKA 2026 - KT.docx` and its copy `data/raw/report/EUREKA-2026-KT.docx` | SHA-256 `01363a06…eddff8c` for both. This equals the hash recorded in the R1 parameter registry | [D] |
| Submitted DOCX is an iLovePDF conversion of the v8 PDF build `KT01_FINAL_REPORT_v8.pdf` (96.9 % paragraph match) | `numeric_claim_provenance_20261025/final_source_inspection_20261025.md` | [H] |
| KT-01 source versions v1–v8 with backups and pre-checks (`KT01_FINAL_REPORT*.tex/pdf`, `KT01_*_backup*.tex`, `KT01_V8_EXTENDED_*.tex`) | present in the snapshot `workspace\` | [D] (listing) |
| v8 source states "12.5 % ± 2.1 %" energy-efficiency improvement and "15.3 % ± 2.8 %" fade reduction | snapshot `workspace\KT01_FINAL_REPORT_v8.tex` line 157 | [D] |
| v8 payback section: 95 → 85.3 Wh/km printed as "9.7 Wh/km = 9.7 %"; fade 16.5 → 14.2 %/1000 cycles printed as "2.3 %/1000 cycles = 14 % reduction" | same file, lines 5470–5482 | [D] |
| (95 − 85.3)/95 = **10.21 %** (the absolute difference is 9.7 Wh/km); (16.5 − 14.2)/16.5 = **13.94 %** | recomputed | [A] |
| Fig. 11 curves are typed pgfplots formulas: fixed `100 − 0.002x − 0.000001x²`, adaptive `100 − 0.0017x − 0.0000008x²`. At x = 1000 these give 3.0 and 2.5 pp, a relative reduction of **16.67 %** | v8 lines 2690–2692 | [D] + [A] |
| v1 tables give 15.0 → 14.2 fade = 5.33 % | `EARLIEST_CLAIM_PROVENANCE_AUDIT.md` | [H] |
| v8 line 2706: "validated against experimental data from accelerated aging tests, … within 5 %" | text present [D]. No such data exists in any inspected location [H] | claim unsupported |

**Three incompatible fade definitions exist in the legacy text:** 13.94 %, 16.67 % and 5.33 %, besides the 15.3 % headline. None is tied to an executed calculation.

**Transcript spot-check** (`tools/spot_check_transcripts.py` → `00_transcript_spot_check.txt`, run on the snapshot copies) [D]:
- Sub-agent `b1d68760` line 5 is an assistant `Write` whose payload contains both "12.5 %" and "15.3 %".
- Sub-agent `df2405df` line 11 is a `Write` recommending "± 2.1" and "± 3.2". Its line 18 is a `StrReplace` that inserts "± 2.1" and "± 2.8".

This agrees, at line level, with the inherited finding that the four figures were AI-generated text and not computed results. I did **not** re-run the full search for the earliest occurrence across all 131 transcripts; that part remains [H].

## 4. R1–R3 artefacts located

| Phase | Location (under `verification\scientific_rebuild_20261024\`) | Protocol and freeze record | Raw outputs located [D] |
|---|---|---|---|
| R1 scientific rebuild (2026-10-24) | `.` | `experimental_protocol.md`, SHA-256 `d80b5b4f…` = freeze record `logs/protocol_sha256_at_freeze.txt` [D] | `runs/R1_{S1,S2,UDDS,US06}/` (84 rows each = 336), `runs/CONV_*` (6 × 2 = 12); per-run `series.npz`, `metrics.csv`, `manifest.json`; `results/` |
| R2 feasibility ledger | `recovery_feasibility_20261025/` | none (analysis of R1 outputs) | `ledger_*.csv` |
| R2 pre-registered factorial pilot F0/S0/F1/S1 | `research_recovery_20261025/pilot/` | `../pilot_protocol.md`, SHA-256 `ebebc157…` = `pilot/protocol_sha256_at_freeze.txt` [D] | `pilot/out/tune` (192), `eval` (61), `conv` (4) = 257 rows; `analysis/` |
| R3 gates and pilots | `research_recovery_20261025/R3_20261025/` | `R3_protocol_v1.md`, SHA-256 `d9e82f89…` = freeze record; `R3_protocol_v1_amendment_1.md`, SHA-256 `51a2e93b…` = `logs/amendment_1_sha256.txt` [D] | `outputs/gates/` (47 tasks), `outputs/gates_a1/` (27 tasks), `outputs/gates/paths/*.npz` (45 trajectory files), `outputs/pilot_B/M{0,1,2}/` (768 runs), `outputs/pilot_C/M{0,1,2}/runs.csv` (17 rows each), `outputs/checks/` |
| Forensic provenance audits (2026-10-25) | `numeric_claim_provenance_20261025/`; `R3_20261025/earliest_claim_provenance_20261025/`, `final_external_provenance_search_20261025/`, `cursor_pre_v1_evidence_20261025/` | — | reports, hash lists of `D:\EUREKA` (pre/post), candidate manifest |
| Other KT records (outside the R1 root) | `docs/` (thesis audit, battery feasibility audit, literature review), `evidence/`, `protocol/preregistration.md`, `verification/controller-crosscheck-*` (Modelica) | — | not re-verified in this run, except as cited |

**Naming used in this report:** R1 = scientific rebuild; R2 = the pilot in `research_recovery_20261025/pilot` (R3 documents call its code "R2's `sim.py`"); R3 = `R3_20261025`; R3-C = R3's eco-driving gate and pilot.

## 5. Verification of the R1–R3 hash records

Command: `tools/verify_r1_r3_records.py` (exit 0). There are 713 checks; per-row results are in `00_r1_r3_record_verification.csv`.

| Record | Checks | Match | Not matching, and why |
|---|---|---|---|
| R1 protocol freeze | 1 | 1 | — |
| R2 protocol freeze | 1 | 1 | — |
| R3 freeze record + amendment record | 22 | 21 | `R3_literature_and_parameter_sources.csv` changed after freeze. R3 itself discloses this (`R3_hash_manifest.csv` status `changed-after-freeze`). The frozen version is **not retained**, so the change cannot be inspected [D] |
| `R3_hash_manifest.csv` (end-of-R3 state) | 202 | 201 | `logs/build_hash_manifest.txt` is recorded as the empty-file hash `e3b0c442…` because it was hashed while being written (the file is 20 ms newer than the manifest). This is benign self-reference [D] |
| Per-run manifests (R1, R2, R3) | 487 | 483 | `code/r3_pilot.py` in the four R3-B manifests (§5.1) |

### 5.1 `r3_pilot.py` version used for R3-C [D + I]

- The four R3-B manifests, written at 16:00:37, 17:52, 18:08 and 18:28 on 2026-10-25, all record `r3_pilot.py` = `cec5f70b…`.
- The file was edited at 18:38:34 (the "one-line manifest fix"). Its current hash is `7fd01aca…`.
- The three R3-C processes were started at about 16:01 (`R3_execution_manifest.csv` seq 24). M2 finished at 18:34, before the edit; M0 and M1 finished at 18:55 and 19:23, after it.
- A Python process uses the code it loaded at start. **Inference:** all three R3-C runs executed `cec5f70b…`, because the file had that hash both before (16:00) and after (18:28) the start.
- The R3-C manifests were written afterwards and record `7fd01aca…`. They say the as-run hash "is not recoverable". It is recoverable as above, **but the `cec5f70b…` file content is not retained.**
- The physics module `r3_lib.py` is frozen-unchanged (`c2403adc…`).

**Consequence:** the R3-C raw rows are retained and recomputable (Phase 1). The exact driver code that produced them is not retained. Its difference from the current file is stated to be one line in the manifest step only, and that statement cannot be checked.

## 6. Headline results re-derived from retained tables

All arithmetic is on saved outputs. No simulation was re-run. Command: `tools/recheck_soh_headlines.py` → `00_soh_headline_recheck.txt`; R3-C via `tools/recompute_r3c.py` (Phase 1).

| Inherited headline | Re-derived [A] | Status |
|---|---|---|
| R1: S vs F ΔE between −0.0019 % and +0.034 % in all 112 pairs | n = 112, min −0.0019 %, max +0.0340 % | **reproduced from retained R1 tables** |
| R2: every held-out scheduling contrast \|ΔE\| ≤ 0.025 % | n = 20, max 0.0252 %; all "NO PRACTICAL DIFFERENCE" (some flagged incomplete-cycle) | reproduced |
| R3-B: scheduling ≤ 0.04 % (M0, M1); +0.35 to +0.40 % worse (M2, UDDS) | complete held-out S − F: M0 [−0.006, +0.038] %, M1 [−0.020, +0.033] %, M2 [+0.045, +0.396] % | reproduced |
| R3 gates G-A, G-B, G-C, G-B′ | decision JSON files present and hashed; not recomputed in this run | located, not re-derived |
| R3-C eco savings | every reported value reproduced (Phase 1) | reproduced; see `01_r3c_reassessment.md` for validity |

"Reproduced" means re-derived from retained raw tables by independent arithmetic. It does **not** mean the simulations were re-executed or independently replicated. All of R1–R3 share one model, one parameter set and one author.

## 7. KT-01 and CNTT-02 separation

The snapshot `workspace\` mixes both theses. Classified by file name [D]:

| Class | Files | Treatment in R4 |
|---|---|---|
| KT-01 (`KT01*`, `KT01_MicroEV\`, `render_kt01_figures.py`) | 96 | lineage evidence only (§3) |
| CNTT-02 (`CNTT02*`, `cntt02*`, `CNTT02_STGNN\`, `figures_cntt02\`, `render_*cntt02*`) | 173 | **excluded.** Nothing from them enters R4. Earlier audits found the 12.5 / 15.3 strings in CNTT-02 to be coincidental [H] |
| Shared or unlabelled (preambles, build logs, page renders, `AUDIT_REPORT.md`, changelogs, `refs.bib`, pandoc) | 170 | not used, except `AUDIT_REPORT.md` as cited by the inherited provenance finding |
| Cursor transcripts | 131 | spot-check only (§3) |

No CNTT-02 number, figure or parameter appears in any R4 file.

## 8. Missing, inaccessible, conflicting or unverified records

| # | Item | Status |
|---|---|---|
| M1 | Any executed calculation behind 12.5 %, 15.3 %, ± 2.1 %, ± 2.8 % | none in the project, `D:\EUREKA` or the transcripts inspected [H]. Colab/Drive, Cursor `state.vscdb` and other machines not inspected [U] |
| M2 | `r3_pilot.py` as run for R3-C (`cec5f70b…`) | not retained (§5.1) |
| M3 | Frozen version of `R3_literature_and_parameter_sources.csv` | not retained (§5) |
| M4 | Per-sample traces of the R3-C dynamic runs | **not retained**: only aggregate rows in `pilot_C/*/runs.csv` (Phase 1) |
| M5 | Cell part number and datasheet (owner item OC-1); pack series/parallel arrangement | absent; the BOM's 16 × 3.2 V conflicts with 48 V [H, see Phase 2] |
| M6 | Motor/inverter efficiency map for the KT-01 motor | absent [H, see Phase 2] |
| M7 | Applicable ageing law or same-cell ageing data | absent [H, see Phase 2] |
| M8 | Snapshot scope statement and creator | not recorded (§2.1) |
| M9 | Human review or independent replication of R1–R3 | none |
| M10 | Git history of R1–R3 | not inspected (this run's instructions exclude Git). Earlier records describe R1–R3 as uncommitted [H] |

## 9. Statement on legacy material

- No file outside the R4 directory was created, modified, renamed or deleted by this run. That covers legacy thesis files, posters, figures, audit reports, transcripts, backups, R1–R3 and the snapshot.
- **Executed proof:**
  - Pre-run hashes of 24,884 project files outside the R4 directory: `zz_pre_hash_project.csv`, taken 00:35.
  - These are compared with post-run hashes, sizes and modification times in `04_gate_status_summary.md` §6.
  - The snapshot and `D:\EUREKA` are re-checked against the manifest at the end of the run.
- One caveat: the pre-hash was taken about 3 minutes after the run began. Before it, this run had only created the R4 directory and read files.

## Gate G0 — PASS

| Criterion | Evidence |
|---|---|
| Project identity | KT-01; root `D:\EURÉKA 2026 - KT`; thesis DOCX hash matches the R1 record (§1, §3) |
| Output boundary | new R4 directory, absent before, the only place written (§1, §9) |
| Required source locations | R1, R2, R3, the R3-C protocol, amendment, raw outputs and forensic audits all located and hash-checked (§4, §5) |
| No unresolved path ambiguity | three generations distinguished; CNTT-02 separated (§1, §7) |

The defects in §5 and §8 (M2–M4 in particular) limit what can be claimed from R3-C. They do not create any risk of working in the wrong project. They are carried into Phase 1.
