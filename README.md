# EUREKA 2026 KT: research environment

Source repository for the micro-EV control study. Project layout, provenance and
verification records live outside this folder in `D:\EUREKA-2026\docs`.

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
