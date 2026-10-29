# Evidence storage guide (controller cross-verification)

Written 2026-10-24. Companion files: `evidence-preservation-inventory.csv` (every file, size, SHA-256, tier, action, run ID, supporting table), `evidence-preservation-report.md` (what was done and found), `controller-crosscheck-artifact-manifest.csv` (the 536-file manifest of the integrity review; unchanged, its `git_state` column is a snapshot of that day), `controller-crosscheck-integrity-review.md` section 2 (the strategy this implements).

## 1. Where things are

| Tier | What | Where | In Git? | Why there |
|---|---|---|---|---|
| A | Sources (`.mo`, `.mos`), scripts, launcher, frozen protocol and amendments, run log, report, integrity review, result tables, JSON summaries, frozen gains, solver selection, failure excerpts, claim audit, manifests, the inventory | `verification/`, `audit/`, `technical-*` | yes, explicit paths, 3.8 MB | small, text, needed to review the work |
| A | Solver-status records of every `omc` launch (`SimulationResult` blocks, launcher JSON) and the first, defective runs (`check_results_FIRST_RUN_with_B2_failure.csv`, `..._DEFECTIVE.json`) | `verification/modelica-build/logs/` and the top level of `verification/modelica-build/` | yes (309 + 15 small files) | not regenerable without rerunning; a blanket ignore rule used to hide them |
| B | 40 compressed Modelica result series (the data behind every table row) | `verification/controller-crosscheck-runs/raw/*.csv.gz` | no (ignored by exact path) | 241 MB; plain Git history cannot be rewritten or pruned, and there is no LFS remote |
| B | 45 Python reference series (`.npz`) | `verification/controller-crosscheck-runs/python_reference/` | no (ignored by exact path) | 48 MB binary |
| B | Compressed copies of evidence that existed only in the ignored build folders: 7 solver logs > 2 MB (CVODE), 5 diagnostic result CSVs, the 63 plant-phase result CSVs, 6 plant-phase Python reference files (3 CSV, 3 JSON), 108 per-case executable logs | `verification/evidence-archive/` (mirrors the original path under `verification/`, plus `.gz`) | no (ignored by exact path) | 497.7 MB of originals stored as 41.7 MB; originals are kept where they are |
| B | Python baseline (`artifacts/`, `data/`, `logs/`, frozen thesis copy) | unchanged | no (existing project policy) | hashes tracked in `evidence/artifact_hashes.json`; never modify |
| B (redundant) | 40 uncompressed Modelica CSVs (1.44 GB) | `verification/modelica-build/cases_ctl/*/*_res.csv` | no | each is byte-identical to a `.gz` in `raw/` (hash-verified); kept, not deleted |
| C | Compiler and linker output, per-case generated C, objects, executables, launcher smoke output, `omc` library cache, `verification/python-env`, bytecode caches | `verification/modelica-build/cases*/`, `launcher-smoke/`, `verification/omc-userdata/`, `python-env/` | no (ignored) | regenerable from tracked sources and scripts (`Invoke-OpenModelica.ps1`, `generate_*case_scripts.py`); 23,231 files, 637 MB |
| defer | `verification/fastsim-smoke/*.csv` (2.1 MB), `verification/logs/om-baseline-*.txt` (machine PATH and profile folder snapshot) | in place | untracked, undecided | ancillary or machine-specific; left for the owner |

Ignore rules (`.gitignore`) now name exact paths. The blanket `/verification/modelica-build/` rule is gone. `.gitattributes` has `-text` for `verification/**`, `audit/**` and the two `technical-*` files, so Git stores them byte for byte: the frozen-protocol hash and every hash in the inventory stay valid on any checkout (with the repository's `* text=auto`, LF files would otherwise be rewritten to CRLF on Windows).

## 2. Chain from configuration to claim

`configs/parameters.yaml` -> `verification/modelica/EurekaPlant|EurekaController/*.mo` (values generated into `generated_inputs.json` / `controller_generated_inputs.json`) -> `verification/scripts/generate_controller_case_scripts.py` -> `verification/modelica/scripts/*.mos` and `controller_cases.json` -> `Invoke-OpenModelica.ps1` / `guarded_run.py` -> raw run (`raw/<case>.csv.gz`, status in `modelica-build/logs/*.out.txt`) -> `controller_eval.py`, `controller_metrics.py` -> `controller-crosscheck-results.csv` (each row carries `artifact_path` and `artifact_sha256`) and `controller-crosscheck-runs/evaluation_summary.json` -> `controller-crosscheck-report.md` -> `controller-crosscheck-integrity-review.md`. The inventory column `supports` names the table and report section each raw file backs; `run_id` is the case name used in `controller_cases.json`.

## 3. Verify (read-only; about 10 s)

```
python verification/scripts/evidence_preservation.py verify
```

It re-hashes every file the inventory lists (901 files, 2.39 GB), decompresses every archive copy and compares it with the original hash, checks that each `raw/*.csv.gz` reproduces a listed result CSV, and checks the 56 hashes in `evidence/artifact_hashes.json`. Exit code 0 means no problem. A missing or altered file is reported, never rebuilt.

If only Git is available: `git status` must show no change under `verification/` apart from ignored paths, and `git ls-files --eol verification audit` must show `attr/-text` with the same line-ending class in the index (`i/`) and the working tree (`w/`).

## 4. Updating the evidence later

1. Never edit a file in the inventory. New work gets new files and a dated amendment (protocol section 14 style).
2. Run `verify` first. Investigate anything it reports before adding more.
3. Add new small records with explicit paths: `git add -- <path> <path>`. Never `git add .` or `-A`.
4. New files above about 2 MB, or any raw time series, go to Tier B: keep them outside Git, extend the archive with `python verification/scripts/evidence_preservation.py archive` only if they exist solely in an ignored folder, then rerun `inventory`.
5. `inventory` rewrites the CSV; its `git_state_before` and `ignore_rule` columns describe the state on 2026-10-24 and will differ on later runs. Keep the 2026-10-24 version in Git history.
6. The inventory does not list itself, this guide, the report, `.gitignore` or `.gitattributes`; Git tracks those. Their SHA-256 values are in the report.
7. Before deleting or relocating any Tier B or redundant file, copy it to a second medium and confirm the hash there.

## 5. Limits

- The archive and the raw files sit on the same disk as the repository. They are preserved in the project, not backed up. Copy `verification/controller-crosscheck-runs/raw/`, `.../python_reference/` and `verification/evidence-archive/` (about 330 MB) to a second medium to protect against disk loss.
- Items that exist only as descriptions in the run log, protocol or report (the first failing controller-logic run, the first 16-failure evaluation CSV, the original IDA-choosing selection output; integrity review section 2) were never saved as files and cannot be preserved now.
- The 10 GB and 0.5 GB CVODE result files deleted under amendment A1 remain gone; only their header, tail, size and hash excerpts exist (`failed_runs/`).
- Git LFS 3.7.1 is installed but was not used: with no remote, LFS objects would sit only in `.git/lfs`, and enabling it rewrites hooks and attributes for the whole repository.
