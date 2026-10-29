# R4 preflight: gate status summary

**Date:** 2026-10-28, 00:30–01:00 local time (UTC+7).
**Prepared by:** AI assistant (Claude); no human review.
**Scope:** Phases 0–3 only. No simulation, optimiser, sweep, installation, download, network access, Git command or legacy-file write was performed. Phases 4–6 were not started.

## 1. Gates

| Gate | Result | Why | Evidence |
|---|---|---|---|
| **G0** baseline and boundaries | **PASS** | Project root, R4 output boundary, R1–R3 locations and the snapshot are identified and hash-checked. The three project generations are distinguished, and CNTT-02 is separated. Snapshot: 570/570 rows consistent; source re-hash 570/570 unchanged | `00_baseline_audit.md`; `00_snapshot_integrity_*`; `00_r1_r3_record_verification.csv` |
| **G1** R3-C reassessment | **PASS (classification complete)** | Every R3-C number is reproduced from retained raw rows, and every claim is classified. **R3's stop-respecting amendment never covered eco-driving.** Under a stops-respected reading, only S2 at A = 0 survives: dynamic savings of 1.46–2.87 %, conditional on a ≈ 0.3 s arrival tolerance that was never pre-registered. All UDDS eco results are invalid: stops are shifted by up to 89 s, the vehicle moves during 60–65 % of reference rest samples, and the cycle is outside the 0–50 km/h domain. A > 0 results are energy-time trade-offs. No eco saving is attributable to the LQR or to SoH. **Not established:** any stops-respected eco magnitude beyond S2 A = 0. The smallest test that would establish one is specified | `01_r3c_reassessment.md`; `01_r3c_*.csv` |
| **G2** model basis | **PASS for branch RP-E only; FAIL for K, RP-S, AGE** | No KT-01 vehicle, motor, battery or ageing parameter has class A or B support. 51 of 64 ledger values are class D as KT-01 facts, and 10 specification conflicts are recorded. RP-E (declared hypothetical reference plant, motor-loss bracket M0/M1/M2, ranges swept, in-domain cycles) is executable with every input declared. That is **not** physical validation. K (the thesis vehicle), RP-S (SoH-dependent limits) and AGE (capacity fade) lack critical inputs | `02_model_basis.md`; `02_parameter_ledger.csv`; `02_model_gaps.md` |
| **G3** protocol | **PASS for the executable scope; FROZEN** | H3 (B0 vs B3 with the new stops-in-time S-eco planner, S2 held out, RP-E) is specified to the level of code entry points, hashes, grids, tolerances, decision rules, seeds, run budget and raw-output layout. H1 is fully defined but not scheduled. H2, H4 and H5 are written into v1 as **blocked**, with their activation conditions | `03_R4_protocol_v1.md`, SHA-256 `f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab`; `03_R4_protocol_v1_freeze_record.md` |

## 2. R1–R3 conclusions: reproduced or inherited

"Reproduced" means re-derived in this run, by independent arithmetic, from retained raw tables. No simulation was re-executed, and nothing has been independently replicated (same model, same author).

| Conclusion | Status |
|---|---|
| R1: SoH-scheduled vs fixed LQR ΔE between −0.0019 % and +0.034 % (112 pairs) | **reproduced** from `results/pairs.csv` |
| R2: held-out scheduling contrasts \|ΔE\| ≤ 0.025 % | **reproduced** from `pilot/out/analysis/contrasts.csv` (n = 20, max 0.0252 %) |
| R3-B: scheduling ≤ 0.04 % (M0, M1); up to +0.40 % worse (M2) | **reproduced** from `pilot_B/*/eval_runs.csv` |
| R3-C: eco savings (QS and dynamic) | **numbers reproduced** from `eco_rows.csv` and `pilot_C/*/runs.csv`. **Validity reclassified** (G1): UDDS withdrawn; S2 A = 0 conditional |
| R3 gate decisions G-A, G-B, G-B′ (VSI < 0.09 %; tracking-tolerance lever ≈ 4–6 %) | **inherited**: decision files located and hash-verified, values not recomputed |
| R3 QS-vs-dynamic and time-step checks; M2 holding-torque diagnosis | **inherited** |
| Legacy arithmetic: 95 → 85.3 Wh/km = 10.21 % (not 9.7 %); 16.5 → 14.2 = 13.94 %; Fig. 11 formulas give 16.67 % | **reproduced** from the snapshot v8 source (lines 2690–2692, 5470–5482) |
| 12.5 % / 15.3 % / ± 2.1 % / ± 2.8 % are AI-written text, not computed results | **partly re-checked**: transcript lines b1d68760:5 and df2405df:11/18 confirmed. The earliest-occurrence search and the Cursor-origin analysis are **inherited** |
| Modelica cross-check of the plant and controller | **inherited** (not re-examined) |

## 3. Branch ready for a small future pilot

**RP-E, H3: B0 (fixed R1 LQR tracking the baseline task) vs B3 (same LQR tracking the S-eco profile, stops fixed in time).**
- **Conditions:** S2 held out, S1 in-sample; M0/M1/M2 reported separately; L-R1 and L-EVE; P1 primary, P3 secondary.
- **Size:** 170 dynamic runs, as planned in protocol §10.6.

**Before it can run, Phase 4/5 must happen under the frozen protocol:**
- implement the S-eco planner and the profile builder;
- implement the trace writer and the independent recomputation script;
- pass the planner unit tests of protocol §9.

None of this was started.

**Expectation management:**
- Whatever the outcome, it is a statement about one 0.53 km synthetic cycle on a hypothetical plant.
- It says nothing about KT-01, about SoH, or about capacity fade.
- H1 is runnable but would repeat known null physics unless G-BAT-2 is closed.

## 4. Next critical blockers

1. **G-BAT-2 + G-BAT-1**: the KT-01 cell datasheet (owner item OC-1) and any sourced SoH dependence of power capability. Without them, SoH reaches this vehicle model only through resistance growth, already shown negligible three times. H2 and H4 stay blocked, and H1 cannot produce a non-trivial answer.
2. **G-AGE-1**: a same-cell ageing law with domain and validation data. Without it, no fade number of any kind (H5).
3. **G-CYC-1**: a second in-domain held-out cycle, sourced from its regulation text. Without it, H3 cannot be generalised beyond S2.
4. **G-MOT-1**: a measured motor/inverter map. Without it, no motor-specific magnitude can be claimed.

## 5. Files created (all in this directory)

| File | Content |
|---|---|
| `00_baseline_audit.md` | Phase 0 report, gate G0 |
| `00_snapshot_integrity_rows.csv`, `00_snapshot_integrity_summary.json` | start-of-run snapshot and source check |
| `00_r1_r3_record_verification.csv` | 713 hash-record checks |
| `00_soh_headline_recheck.txt` | R1/R2/R3-B headline re-derivation |
| `00_transcript_spot_check.txt` | transcript line check |
| `01_r3c_reassessment.md` | Phase 1 report, gate G1 |
| `01_r3c_eco_stop_compliance.csv`, `01_r3_baseline_stop_compliance.csv` | stop-compliance description of saved trajectories |
| `01_r3c_qs_recomputed.csv`, `01_r3c_dynamic_recomputed.csv` | R3-C recomputation |
| `02_model_basis.md`, `02_parameter_ledger.csv`, `02_model_gaps.md` | Phase 2, gate G2 |
| `03_R4_protocol_v1.md` (read-only), `03_R4_protocol_v1_freeze_record.md` | Phase 3, gate G3 |
| `04_gate_status_summary.md` | this file |
| `tools/check_snapshot_manifest.py`, `tools/hash_tree.py`, `tools/verify_r1_r3_records.py`, `tools/describe_r3c_stop_compliance.py`, `tools/recompute_r3c.py`, `tools/recheck_soh_headlines.py`, `tools/spot_check_transcripts.py` | read-only analysis scripts used above |
| `zz_pre_hash_project.csv`, `zz_post_hash_project.csv`, `zz_pre_post_comparison.txt` | before/after hashes of every project file outside this directory |
| `zz_post_snapshot_integrity_rows.csv`, `zz_post_snapshot_integrity_summary.json` | end-of-run snapshot and source check |
| `zz_R4_file_manifest.csv` | SHA-256 of every file above, written last |

## 6. Statement that no legacy files or snapshots were modified

| Check (executed) | Result |
|---|---|
| Project files outside this directory: SHA-256, size and modification time before (00:35) and after (≈ 00:57) | 24,884 → 24,884 files; **0 added, 0 removed, 0 changed** (`zz_pre_post_comparison.txt`) |
| Evidence snapshot vs its manifest, at start and at end | 570/570 identical both times; 0 unlisted files; manifest SHA-256 `A93EB44F…F279` unchanged |
| `D:\EUREKA` and the 131 Cursor transcripts vs the manifest, at start and at end | all 570 sources re-hashed both times, 570/570 matched both times. Byte-identical |
| Thesis DOCX | hash `01363a06…` unchanged (included in the 24,884) |

**Not covered by the before/after comparison:**
- `.venv`, `cache`, `tools` (interpreter) and `.git` were excluded.
- Last-access times on `D:\EUREKA` and the snapshot may have been updated by reading. This is a known property of that volume and is recorded without evidential value.

## 7. Exceptions and self-caused issues

- Two ad-hoc one-line Python commands failed with `SyntaxError` (Bash collapsed a backslash). They had no effect and were redone through script files.
- `verify_r1_r3_records.py` first ran with two resolver bugs:
  - R2 manifests' `protocol_sha256` was compared against R3's protocol;
  - R3 `data/` was missing from the search bases.

  Its first output (in this directory) was overwritten by the corrected rerun. The remaining mismatches are real and are explained in `00_baseline_audit.md` §5.
- `describe_r3c_stop_compliance.py` was rerun once with an added time-indexed column. Its first outputs, in this directory, were overwritten.
- The pre-run project hash was taken about 3 minutes after the run began. Before that, the run had only created this directory and read files.
- The protocol was edited four times before freezing (`03_R4_protocol_v1_freeze_record.md`), and not after.
- `D:\EUREKA` had been restricted by the owner in earlier sessions. This run's instructions named it for a read-only hash comparison, and only hashing was done (§6).
