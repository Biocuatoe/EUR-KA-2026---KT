# Scientific rebuild 2026-10-24: does battery SoH matter for LQR speed control?

## What this is

An isolated, dated study.

**What it does.** It tests the thesis hypothesis ("an SoH-scheduled LQR outperforms a
fixed-gain LQR as the battery ages") in a transparent simulation model where SoH can actually
reach the controlled behaviour.

**What it leaves unchanged.** It modifies nothing outside this directory except three
documentation files in `docs/scientific_rebuild/`. Specifically:
- the thesis DOCX is untouched;
- `src/eureka` is untouched;
- `configs/` and the saved runs in `artifacts/` are untouched;
- `protocol/` and the evidence baselines are untouched.

**What it does not do.**
- It does not reproduce the thesis's 12.5 % or 15.3 % figures, and does not try to.
- It contains no capacity-fade model, so it makes no battery-life claim.

## Contents

| Path | Content |
|---|---|
| `experimental_protocol.md` | Questions, factors, outcomes and decision rules, frozen before any comparative run (SHA-256 at freeze: `logs/protocol_sha256_at_freeze.txt`) |
| `model_equations.md` | Plant, battery window, controllers, metrics |
| `parameter_registry.csv` | All 39 parameters, with unit, provenance, source and evidence status |
| `configs/R1.yaml` | Machine-readable experiment definition |
| `src/rebuild/` | `model.py` (extended plant and simulator), `run.py` (grid and convergence), `precheck.py` (analytical pre-check), `analyze.py` (tables and figures), `registry.py` |
| `tests/test_rebuild.py` | 9 tests: equality with the documented plant, closed-form limits vs brute force, closure, monotonicity |
| `runs/<batch>/` | `manifest.json` (file hashes, environment, gains, status), `metrics.csv` (per run), `series.npz` (1 s samples and final states), `log.txt` |
| `results/` | CSV tables derived only from `runs/` |
| `figures/` | Figures drawn only from `runs/` |
| `logs/` | Test, pre-check and run console logs, including failures |
| `claims_and_evidence.csv`, `numerical_validation.md`, `results_and_limitations.md`, `thesis_claim_mapping.md` | Evidence and interpretation |

## How to reproduce

From PowerShell:

```powershell
cd 'D:\EURÉKA 2026 - KT'
. .\scripts\activate.ps1
$env:PYTHONPATH = "$PWD\verification\scientific_rebuild_20261024\src"
python -m pytest -q verification/scientific_rebuild_20261024/tests   # ≈ 3 min
python -m rebuild.precheck                                            # seconds
python -m rebuild.run grid                                            # 336 runs; refuses to overwrite runs/R1_*
python -m rebuild.run convergence                                     # dt = 1, 0.5, 0.25 ms
python -m rebuild.analyze                                             # tables and figures
python -m rebuild.registry                                            # parameter_registry.csv
```

**To re-run into fresh directories,** move or rename the existing `runs/R1_*` and `runs/CONV_*`
first. `run.py` never overwrites a batch.

**Environment.** This uses the project's locked environment (`uv.lock`; Python 3.14.7,
numpy 2.5.4, scipy 1.18.1). Nothing was installed for this study.
