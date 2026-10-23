# EUREKA 2026 KT: research environment

Source repository for the micro-EV control study. Project layout, provenance and
verification records live outside this folder in `D:\EUREKA-2026\docs`.

## Evaluation of the report's claims

- `docs/evaluation-report.md`: phase-by-phase findings (start here)
- `protocol/preregistration.md`: hypotheses, metrics and decision rules, fixed before implementation
- `evidence/claim_registry.yaml`: what the report claims, with exact locations
- `evidence/evidence_matrix.{yaml,csv,json}`: what was tested, with status and artifacts
- `docs/model.md`, `configs/parameters.yaml`: plant model and parameter provenance
- `docs/lineage.md`, `scripts/reproduce_all.ps1`: how every result is regenerated

## Activate and test (PowerShell)

```powershell
. D:\EUREKA-2026\repo\scripts\activate.ps1
cd D:\EUREKA-2026\repo
python -m pytest
```

## Rebuild or check the environment

```powershell
powershell -NoProfile -ExecutionPolicy RemoteSigned -File D:\EUREKA-2026\repo\scripts\setup.ps1   # safe to rerun
powershell -NoProfile -ExecutionPolicy RemoteSigned -File D:\EUREKA-2026\repo\scripts\verify.ps1  # records every check
```

- Dependencies: `pyproject.toml` (direct, lower bounds) -> `uv.lock` (exact pins, universal)
  -> `requirements-lock.txt` (pip-compatible export with hashes).
- After changing dependencies: `setup.ps1 -Relock`.
- All cache and runtime paths come from `project.env`. Run `uv` commands only in an
  activated shell, otherwise uv would create `repo\.venv` and use its C: cache.
