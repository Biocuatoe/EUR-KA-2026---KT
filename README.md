# EUREKA 2026 KT: research environment

Project folder and Git root for the micro-EV control study (fixed-gain vs SoH-scheduled
LQR): `D:\EURÉKA 2026 - KT`. Environment layout, provenance and verification records are in
`docs/` (`environment-inventory.md`, `software-purpose-and-justification.md`,
`installation-verification.md`, `path-exceptions-and-failures.md`). The project was moved
here from `D:\EUREKA-2026` on 2026-10-23; see `docs/migration-2026-10-23.md`.

## Evaluation of the report's claims

- `docs/evaluation-report.md`: phase-by-phase findings (start here)
- `protocol/preregistration.md`: hypotheses, metrics and decision rules, fixed before implementation
- `evidence/claim_registry.yaml`: what the report claims, with exact locations
- `evidence/evidence_matrix.{yaml,csv,json}`: what was tested, with status and artifacts
- `docs/model.md`, `configs/parameters.yaml`: plant model and parameter provenance
- `docs/lineage.md`, `scripts/reproduce_all.ps1`: how every result is regenerated

## Activate and test (PowerShell)

```powershell
cd 'D:\EURÉKA 2026 - KT'
. .\scripts\activate.ps1
python -m pytest
```

## Rebuild or check the environment

```powershell
cd 'D:\EURÉKA 2026 - KT'
powershell -NoProfile -ExecutionPolicy RemoteSigned -File .\scripts\setup.ps1   # safe to rerun
powershell -NoProfile -ExecutionPolicy RemoteSigned -File .\scripts\verify.ps1  # records every check
```

- Dependencies: `pyproject.toml` (direct, lower bounds) -> `uv.lock` (exact pins, universal)
  -> `requirements-lock.txt` (pip-compatible export with hashes).
- After changing dependencies: `setup.ps1 -Relock`.
- All cache and runtime paths come from `project.env`. Run `uv` commands only in an
  activated shell, otherwise uv may fall back to its C: cache for some operations.
