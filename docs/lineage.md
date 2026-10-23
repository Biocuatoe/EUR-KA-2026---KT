# Data lineage and regeneration commands

All commands run from the project root `D:\EURÉKA 2026 - KT` in an activated shell
(`. .\scripts\activate.ps1`). Before 2026-10-23 the same commands ran from
`D:\EUREKA-2026\repo`; the raw outputs below were produced there (see
`docs/migration-2026-10-23.md`).

| Step | Command | Inputs | Outputs |
|---|---|---|---|
| Report audit | `python scripts/audit_report.py` | `data/raw/report/*.docx` → `data/processed/report/report.md`, `evidence/claim_registry.yaml` | `artifacts/reports/report-consistency-checks.json`, `artifacts/tables/claim_registry.csv`, `data/processed/report/MANIFEST.json` |
| Tuning acceptance | `python scripts/tuning_acceptance.py` | `configs/parameters.yaml`, P-TUNE | `artifacts/reports/tuning-acceptance.json` |
| Verification gate | `python scripts/run_gate.py` | the full test suite, clean tree | `artifacts/reports/verification-gate.json` |
| Experiments | `python scripts/run_experiment.py {primary,gamma_sweep,fixed_family}`, `... robustness --stage pilot`, then `--stage main` | `configs/*.yaml` | `artifacts/raw/<exp>/<batch>/{manifest.json,timeseries.npz}` |
| Validation and metrics | `python scripts/analyze.py <exp>` (and `robustness --pilot` before `--stage main`) | raw outputs only | `data/processed/<exp>/runs.csv`, `artifacts/tables/<exp>_*.csv`, `artifacts/reports/<exp>_results.json` |
| Energy decomposition | `python scripts/energy_breakdown.py` | `artifacts/raw/primary` | `artifacts/tables/energy_breakdown.csv` |
| Figures | `python scripts/make_figures.py` | tables and raw primary S1 | `artifacts/figures/evaluation/*.png` |
| Evidence | `python scripts/build_evidence.py` | registry, matrix, all artifacts | `evidence/evidence_matrix.{csv,json}`, `evidence/artifact_hashes.json` |

`scripts/reproduce_all.ps1` runs the analysis chain from existing raw outputs, and with
`-Rerun -Force` the whole chain including the simulations.

**Determinism:**

- The simulations are deterministic given configuration, seeds and the locked
  environment (`uv.lock`).
- The only random inputs are the S-D draws and noise, seeded with 20261023 + draw. The
  same seed is used for both controllers of a pair.

Raw evaluation outputs in this record were produced at commit
`38f443aa5cabd51dc7c429a49962f12e9e273884`, after the gate passed at that commit.
