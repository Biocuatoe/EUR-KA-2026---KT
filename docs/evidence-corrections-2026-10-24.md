# Evidence corrections, 2026-10-24

This is a dated, reviewable record of the corrections made on 2026-10-24 to the evidence
matrix and to `docs/research-contribution-review.md`. The YAML schema
(`src/eureka/evidence.py`, `MatrixRow`, `extra="forbid"`) has no history field. This file
therefore holds the verbatim previous values, and each changed row carries a comment
pointing here.

**Where the corrections live (updated 2026-10-24, after the amendment decision below):**

- The corrected matrix is **`evidence/evidence_matrix_2026-10-24.yaml`**, a dated amendment.
  Its dated comments, one per correction (K1, K2, K3, K1 for N04), are inside it.
- The original **`evidence/evidence_matrix.yaml` is restored byte for byte** to the
  committed version (SHA-256 `c4626b80…dee8d`, 27,459 bytes, equal to the preservation
  inventory). Sentences below that say "the YAML" was edited refer to the amendment.
- Dated exports: `evidence/exports/2026-10-24/` (see its README).

## Procedure followed

1. **Registry untouched.** `evidence/claim_registry.yaml` was **not** edited. Its header
   says it "records what the report CLAIMS. It is never edited to fit new results: test
   outcomes go into evidence_matrix.yaml". C37's registered disposition
   (`KEEP_WITH_CITATION_CHECK`) and note ("Verify against the primary source …") therefore
   stay as registered. The check's outcome is recorded in the matrix.
2. **Status vocabulary and precedence.** Statuses come from `src/eureka/evidence.py`
   (`STATUS_DEFINITIONS`, `PRECEDENCE`). No status value was changed. C01 and C37 remain
   `CONTRADICTED`; N04 remains `SIMULATION_SUPPORTED`.
3. **Validation (executed 2026-10-24):**
   - `python -m pytest tests/test_evidence_matrix.py tests/test_claim_registry.py -q` →
     **88 passed**, exit 0;
   - a dry replica of the checks in `scripts/build_evidence.py` (one row per claim, no
     duplicates, every supporting artifact exists) → 44 rows, no problems.

   Status counts are unchanged: CONTRADICTED 25, NOT_TESTED 8, REQUIRES_PHYSICAL_VALIDATION
   4, IMPLEMENTED_NOT_VALIDATED 2, CONSISTENT_WITH_RECORD 1, SIMULATION_SUPPORTED 4.
4. **Not run: `scripts/build_evidence.py`.** It rewrites `evidence/evidence_matrix.{csv,json}`,
   the copies in `artifacts/tables/`, and `evidence/artifact_hashes.json` with a new run
   context. The last of these is the baseline hash record; see "Write-scope check" below.
   **Consequence:** the baseline exports `evidence/evidence_matrix.csv` and `.json`, and
   their `artifacts/tables/` copies, keep the **previous** text below (K1–K3) by design.
   The corrected text is published separately; see "Resolution: dated amendment snapshot".
5. **Nothing else changed.** No protocol, model, script, raw run or saved result was
   changed.

## K1: universal-bound wording withdrawn

**Reason.** The resistive share (1.1–2.1 %) and the later ≈0.3 % estimate are not
mathematical bounds on energy differences between controllers.

- Controllers can also differ through:
  - motor/inverter and gear loss asymmetry (motoring vs regeneration);
  - R1 loss;
  - regenerated energy;
  - friction braking;
  - final kinetic energy;
  - tracking deviations.
- No argument bounding these over all controllers has been made.
- Sources: `docs/battery-data-feasibility-audit.md` §7; `docs/research-contribution-review.md`
  §14, K1.

**C01, field `contradictory_or_negative_evidence`, one sentence replaced:**

- **Previous:** "Battery resistive losses are only 1.1-2.1 % of supplied energy, so no
  controller tracking the same profile can save 12.5 % in this model."
- **Now:** "Battery resistive losses were 1.1-2.1 % of supplied energy in the tested runs,
  which explains the small tested differences; this is not a bound on what other
  controllers or a more complete plant could achieve (corrected 2026-10-24)."
- **Unchanged:** the rest of the field, including the external, unverified
  `D:\EUREKA\AUDIT_REPORT.md` remark; see "Pre-existing items not changed". The status
  stays `CONTRADICTED`; it rests on +0.003 %, the 10.2 % implied by the thesis body, and the
  absence of source data.

**N04 (restated claim):**

| Field | Previous | Now |
|---|---|---|
| `original_statement` | 'NEW. In this model, battery resistive losses are 1.1-2.1 % of supplied energy on S1/S2, bounding what any controller tracking the same profile can save by shaping current.' | 'NEW. In this model, battery resistive losses are 1.1-2.1 % of supplied energy on S1/S2 in the tested runs; this is the energy share that SoH changes directly. It explains the tested null result and is not a bound on what other controllers could save.' |
| `contradictory_or_negative_evidence` | 'Constant motor/inverter efficiency hides any part-load efficiency effect of control; a measured efficiency map could enlarge the controllable share.' | The previous text, followed by: '2026-10-24: energy can also differ between controllers through motor/inverter and gear loss asymmetry (motoring vs regeneration), R1 loss, regenerated energy, friction braking and tracking deviations; no bound over all controllers has been derived.' |
| `final_reporting_recommendation` | 'Report as a model-specific bound and name the efficiency-map limitation.' | 'Report as a model-specific energy decomposition of the tested runs, not as a bound; name the efficiency-map limitation.' |
| `verification_status` | SIMULATION_SUPPORTED | unchanged. The decomposition, with closure ≤ 5.4e-10, is reproduced; the "bound" interpretation was removed |

## K2: C37, Huria citation check completed

**Verified identity.**

- Crossref resolved the record as: T. Huria, M. Ceraolo, J. Gazzarri, R. Jackey, "High
  fidelity electrical model with thermal dependence for characterization and simulation of
  high power lithium battery cells", 2012 IEEE International Electric Vehicle Conference
  (IEVC), pp. 1–8, DOI [10.1109/IEVC.2012.6183271](https://doi.org/10.1109/IEVC.2012.6183271).
- The abstract, read via OpenAlex, describes a one-RC equivalent-circuit model identified
  on "LiNi-CoMnO2 cathode and graphite-based anode" cells. The full text was not accessed.
- Source: `docs/literature_review_soh_scheduled_lqr.md` §6, §8.1 and §9.

**Status transition.**

- `verification_status`: `CONTRADICTED` → `CONTRADICTED` (unchanged).
- `final_reporting_recommendation`: from "check pending" to "check completed; correct and
  withdraw".

| Field | Previous | Now |
|---|---|---|
| `implemented_experiment` | 'Citation comparison.' | 'Citation comparison. 2026-10-24: bibliographic identity resolved on Crossref (DOI 10.1109/IEVC.2012.6183271) and the abstract read via OpenAlex; full text not accessed.' |
| `supporting_artifacts` | [] | [docs/literature_review_soh_scheduled_lqr.md] |
| `contradictory_or_negative_evidence` | 'Two different publications cited for the same source; the listed reference is an equivalent-circuit model paper.' | The previous text, followed by the verified identity, and that the source supports neither LFP-specific parameters (Assumption 5, L750) nor the SEI ageing model (L5998) |
| `final_reporting_recommendation` | 'Check the primary source; correct the citation.' | 'Correct reference [3] to the 2012 IEVC record above. Withdraw its use as a source for LFP-specific parameters (L750) and for SEI ageing theory (L5998). No replacement provenance is known; do not substitute one without a verified source.' |

**Registry note.** The thesis's Assumption 5 (report.md L750: "LFP chemistry cells with
characteristics following the model parameters identified from Huria et al.") is **not a
registered location** of C37 or of any other claim. The registry was not extended here. If
the owner revises the registry, adding L750 as a C37 location is recommended. The registry
quote test would accept it, because the text is verbatim on that line.

## K3: C38, random-noise remark withdrawn from the recommendation

**Reason.** C38's recommendation told the thesis to "disclose that earlier figures were
generated from random noise".

- The basis is `D:\EUREKA\scripts\render_kt01_figures.py`. That file is outside the
  project and was never opened for this work. The registry's C38 `disposition_note` cites
  `docs/environment-inventory.md`, which only reports what that external file was said to
  contain.
- `docs/research-contribution-review.md` §3.2 classes the reference as
  EXTERNAL_UNVERIFIED: "The specific allegation of noise generation is not verifiable
  here".
- What the project does establish is weaker: no code or data in the project can
  regenerate the thesis's earlier result figures.

**Change (C38, `final_reporting_recommendation` only):**

- **Previous:** 'Keep; remove the contradicted statements and disclose that earlier figures
  were generated from random noise.'
- **Now:** 'Keep; remove the contradicted statements and state that earlier figures cannot
  be reproduced from any code or data currently available in the project.'

**Unchanged:**

- `verification_status` stays `CONSISTENT_WITH_RECORD`. The claim itself ("no physical
  experiments") is unaffected, and no new evidence bears on it.
- All other C38 fields are unchanged.
- The registry's C38 `disposition_note` still contains the remark. The registry was not
  edited (procedure item 1). The remark does not determine any status.
- C36 and C40 also cite the external figure script (matrix C40
  `contradictory_or_negative_evidence`; registry C01 `source_data` and C40 `source_data`).
  They are outside K3 and were not changed. This is flagged for owner review.

## Review document markers

In `docs/research-contribution-review.md`, the original 2026-10-23 sentences are
unchanged. Inline *[Corrected 2026-10-24 …]* markers were added after:

- the executive assessment;
- §4.2, item 2;
- §5.1;
- §6 (C37);
- §7 (N04);
- §8;
- §10, Q1 and Q5;
- §13.

A new §14 (K1, K2) and a header note were also added.

**Other documents corrected under K1 the same day:**

- `docs/evaluation-report.md`: an inline marker after the Summary sentence "In this model
  no controller tracking the same profile could save 12.5 %", which is left unchanged,
  plus a closing "Correction (2026-10-24)" section;
- `docs/battery-data-feasibility-audit.md` §1, item 3: a wording clarification. The model
  specifies no cell count; 48 V only equals 15 × 3.2 V numerically.

## Pre-existing items not changed (flagged for owner review)

- **C01 evidence text and C01 registry `provenance_notes`.** They cite
  `D:\EUREKA\AUDIT_REPORT.md`, which `docs/research-contribution-review.md` §3.2 classes as
  EXTERNAL_UNVERIFIED. It does not affect C01's status.
- **C38 `final_reporting_recommendation`.** Left unchanged under K1 and K2, because C38
  was outside their scope. It was corrected later the same day under K3 above.

## Write-scope check of `scripts/build_evidence.py` (2026-10-24, not run)

A read-only replica of the script's hashing step was run. It computed the hashes and wrote
nothing. The script was **not run**: its write scope is wider than the export corrections.

**Files it writes:**

| Path | Class | Recorded where |
|---|---|---|
| `evidence/evidence_matrix.csv`, `.json` | generated exports (intended) | preservation inventory, rows 87–88 |
| `artifacts/tables/evidence_matrix.csv`, `.json` | derived copies (intended), but also Python-baseline entries | `evidence/artifact_hashes.json`; inventory rows 48–49 |
| `evidence/artifact_hashes.json` | **baseline hash record** for raw runs (`artifacts/raw/*/{manifest.json,timeseries.npz}`), results, tables, figures and `data/processed` | inventory row 85; `verification/evidence-storage-guide.md` tier B: "hashes tracked in evidence/artifact_hashes.json; never modify"; checked by `evidence_preservation.py verify`; cited by `verification/controller-crosscheck-protocol.md` |

**What a run would change in `artifact_hashes.json`:**

- **Rewritten in full:**
  - `context`: commit 3640533 → current HEAD, `dirty`, UTC, and the interpreter path
    `D:\EUREKA-2026\.venv\…` → the current one;
  - `raw_run_commits` (recomputed; it would stay 38f443a).
- **Hash values:**
  - unchanged for 54 of the 56 entries;
  - changed for the 2 `artifacts/tables/evidence_matrix.*` entries.
- **Ten files newly enrolled as baseline**, none of them in `docs/lineage.md`:
  - six environment and pytest reports, `artifacts/reports/{environment-verification,pytest}-20261023-15{3335,3614,4018}.*`, written 2026-10-23 15:35–15:41;
  - four files in `data/processed/drive_cycles/epa/`, `epa_{udds,hwfet,us06}_1hz.csv` and `validation_results.json`, written 2026-10-23 17:57.

**Read-only `python verification/scripts/evidence_preservation.py verify` on 2026-10-24:**

- Before the restore below: 901 listed files and 56 baseline hashes checked; 1 problem,
  `('changed', 'evidence/evidence_matrix.yaml')`. That was the corrections edited in place.
  The guide (§4.1) says "Never edit a file in the inventory", while the registry header
  sends test outcomes to this matrix; the amendment workflow below follows §4.1.
- After the restore: the same command reports **0 problems**.
- A build run would add five more inventory mismatches: the four export files and
  `artifact_hashes.json`.

## Resolution: dated amendment snapshot (2026-10-24)

The owner chose to preserve the original baseline and publish the corrections separately.
`scripts/build_evidence.py` was not run, and no baseline hash record was changed.

| Step | Result |
|---|---|
| Original YAML recovered | `git show HEAD:evidence/evidence_matrix.yaml`: 27,459 bytes, SHA-256 `c4626b8077b1d11cd767e00414b17d0ffb32a061ce43bf7c13af77d7867dee8d`, equal to inventory row 89 |
| Original YAML restored | only that file, by writing the HEAD blob; no reset, checkout of other paths, clean or history operation. Hash and size re-verified after writing |
| Corrected YAML preserved | `evidence/evidence_matrix_2026-10-24.yaml`, byte copy taken before the restore, SHA-256 `a5ec75e3aa3644357b75fa105a18cdc054e2073d145e13c0575c4b3ba6b25557`; contains the four dated correction comments |
| Dated exports | `evidence/exports/2026-10-24/evidence_matrix.{csv,json}`, produced by `evidence/exports/2026-10-24/make_exports.py` (existing `load_matrix` and `write_matrix_exports`; writes only in that directory) |
| Checks | the amendment passes the `MatrixRow` schema and the registry checks (44 rows, one per claim, supporting artifacts exist); JSON and CSV equal the amendment for all 44 rows; only C01, C37, C38 and N04 differ from the original, and no status differs; the corrected wording is present in YAML, JSON and CSV |
| Baseline unchanged | `artifact_hashes.json`, `evidence/evidence_matrix.{csv,json}` and the `artifacts/tables/` copies have the same SHA-256 before and after; `evidence_preservation.py verify` reports 0 problems |

**What this does not resolve.**

- **Default tooling still reads the original.** `eureka.evidence.MATRIX_PATH`,
  `scripts/build_evidence.py` and the tests read `evidence/evidence_matrix.yaml`. They do not
  see the corrections. The amendment is published and reviewable but is not yet the
  authoritative input to the pipeline. Any future decision to make it so (for example by
  regenerating the baseline) needs its own dated decision.
- **Baseline exports are stale by design.** They still show the pre-correction C01, C37,
  N04 and C38 text. Cite the dated snapshot together with this record.
- **The conflict between the registry rule and the storage guide is handled for this
  instance only.** There is no general amendment procedure in `docs/lineage.md` or the
  guide beyond §4.1 ("new work gets new files and a dated amendment").
- **Ten files are unlisted in `docs/lineage.md`** and would be enrolled as baseline by any
  future `build_evidence.py` run (see the write-scope check above). Their provenance is
  unconfirmed.

## Follow-up evidence-review items (statuses not changed)

These remain unresolved. No status was changed, and none can be without new evidence.

1. **Registry C38 `disposition_note`** still says the existing figures "were generated from
   random noise (see docs/environment-inventory.md)". The basis is the external,
   unopened `D:\EUREKA\scripts\render_kt01_figures.py`. Unverified
   (`docs/research-contribution-review.md` §3.2). The registry is not edited by its own
   rule.
2. **C40**: the matrix evidence (`render_kt01_figures.py lines 245-248, 321, 565-566 draw
   np.random noise around hard-coded values; DATA_AND_COLAB_PROMPTS.md line 3 states the
   intent`) and registry C40 `source_data` cite the same external script.
3. **Registry C01 `source_data`** (line "D:\EUREKA contains only LaTeX/Markdown and a
   figure script that draws random noise") cites it too. C07 and C36 cite the other
   external files (§3.2).
4. **C01 `AUDIT_REPORT.md` remark** (see "Pre-existing items" above).
5. **The ten unlisted baseline-candidate files.**

For C40, the in-project fact stands: no code or data in the project can regenerate the
thesis's earlier result figures.
