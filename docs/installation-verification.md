# Installation verification

What was actually run to verify the environment, with exit codes and outputs.
A check is marked PASS only when its command's exit code and output meet the criterion stated below.

## 1. Final result

| Item | Value |
|---|---|
| Run | 2026-10-23 13:11:11 → 13:11:36 (+07:00), `DESKTOP-QF465MB` |
| Command | `powershell -NoProfile -ExecutionPolicy RemoteSigned -File D:\EUREKA-2026\repo\scripts\verify.ps1` |
| Exit code | **0** |
| Result | **19 / 19 checks PASS**; pytest 27 passed, 0 failed, 0 errors, 0 skipped |
| Full log | `D:\EUREKA-2026\logs\verify-20261023-131111.log` |
| Per-check JSON | `D:\EUREKA-2026\artifacts\reports\environment-verification-20261023-131111.json` |
| JUnit | `D:\EUREKA-2026\artifacts\reports\pytest-20261023-131111.xml` |
| Preceding setup run | `D:\EUREKA-2026\logs\setup-20261023-131109.log`, exit 0, "Would make no changes" |

## 2. Checks

Paths are shortened: `.venv\` = `D:\EUREKA-2026\.venv\`, `repo\` = `D:\EUREKA-2026\repo\`,
and `uv` = the winget `uv.exe` listed in the inventory.

| # | Check | Command | Exit | Result | Pass criterion |
|---|---|---|---|---|---|
| 1 | Python version | `.venv\Scripts\python.exe --version` | 0 | PASS: `Python 3.14.7` | Equals `repo\.python-version` |
| 2 | pip version | `.venv\Scripts\python.exe -m pip --version` | 0 | PASS: `pip 26.2.2 from D:\EUREKA-2026\.venv\Lib\site-packages\pip (python 3.14)` | Loaded from `.venv` |
| 3 | Interpreter and venv paths | `.venv\Scripts\python.exe -c "…sys.executable, sys.prefix, sys.base_prefix…"` | 0 | PASS: prefix `D:\EUREKA-2026\.venv`; base_prefix `D:\EUREKA-2026\tools\python\cpython-3.14.7-windows-x86_64-none` | prefix is `.venv`; base is under `tools\python` |
| 4 | Lock matches metadata | `uv lock --check` | 0 | PASS: "Resolved 71 packages" | uv.lock up to date with pyproject.toml |
| 5 | venv matches lock exactly | `uv sync --check` | 0 | PASS: "Checked 65 packages … Would make no changes" | No missing, extra or different packages |
| 6 | Dependency consistency (uv) | `uv pip check --python .venv\Scripts\python.exe` | 0 | PASS: "All installed packages are compatible" | |
| 7 | Dependency consistency (pip) | `.venv\Scripts\python.exe -m pip check` | 0 | PASS: "No broken requirements found." | |
| 8 | Imports and versions vs lock | `.venv\Scripts\python.exe repo\scripts\check_imports.py` | 0 | PASS: 16 direct packages imported; 65 distributions, all equal to uv.lock, none unlocked | Every import succeeds; installed == locked |
| 9 | Test suite | `.venv\Scripts\python.exe -m pytest --junitxml … --cov=tests --cov-report=term` | 0 | PASS: 27 passed in 7.16 s | Exit 0 |
| 10 | Plot saved on D: | file check | n/a | PASS: `D:\EUREKA-2026\artifacts\figures\environment-check\lqr_double_integrator.png` (37,499 bytes), rewritten during the run | Exists, non-empty, newer than run start |
| 11 | Lint | `.venv\Scripts\ruff.exe check .` | 0 | PASS: "All checks passed!" | |
| 12 | Format | `.venv\Scripts\ruff.exe format --check .` | 0 | PASS | |
| 13 | Kernel registered | `.venv\Scripts\jupyter.exe kernelspec list --json` | 0 | PASS: `eureka-2026` at `.venv\share\jupyter\kernels\eureka-2026`, argv[0] = `.venv\Scripts\python.exe` | Resource dir and argv inside `.venv` |
| 14 | Kernel executes | `.venv\Scripts\python.exe repo\scripts\check_kernel.py` | 0 | PASS: kernel ran code; reported executable `.venv\Scripts\python.exe`, numpy 2.5.4, MPLCONFIGDIR `cache\matplotlib`, tempdir `cache\tmp`, IPYTHONDIR `cache\ipython` | Execute status ok; all reported paths under `D:\EUREKA-2026` |
| 15 | uv cache | `uv cache dir` | 0 | PASS: `D:\EUREKA-2026\cache\uv` | Under `cache\` |
| 16 | pip cache | `.venv\Scripts\python.exe -m pip cache dir` | 0 | PASS: `d:\eureka-2026\cache\pip` | Under `cache\` |
| 17 | Ruff cache | `.venv\Scripts\ruff.exe check --show-settings tests\conftest.py` | 0 | PASS: `cache_dir = "D:\EUREKA-2026\cache\ruff"` | Under `cache\` |
| 18 | No stray caches in repo | `Test-Path` on `.pytest_cache`, `.ruff_cache`, `.hypothesis`, `.coverage`, `.mypy_cache`, `.venv` | n/a | PASS: none present | None exist |
| 19 | No C: writes during the run | Recursive scan of 11 C: locations (below) for files modified after run start | n/a | PASS: 0 files | 0 files |

The locations scanned in check 19 were `%LOCALAPPDATA%\uv`, `%APPDATA%\uv`, `%LOCALAPPDATA%\pip`,
`~\.matplotlib`, `~\.jupyter`, `%APPDATA%\jupyter`, `%LOCALAPPDATA%\jupyter`, `~\.ipython`,
`~\.local\bin`, `~\.cache` and `%TEMP%(user)\pytest-of-HLC`. The run exercised pip, uv, pytest,
Hypothesis, Matplotlib (font cache and figure), IPython and a live Jupyter kernel.

## 3. What the 27 tests verify (`repo\tests\test_environment.py`)

| Test | Verifies |
|---|---|
| `test_interpreter_is_project_venv` | Python version equals `.python-version`; running inside `.venv`; base interpreter under `tools\python` |
| `test_numpy_linear_solve_residual` | 50×50 solve with a seeded Generator; residual < 1e-10 |
| `test_scipy_ode_quadrature_and_expm` | `solve_ivp` of ẋ = −x against e^(−t) (atol 1e-8); ∫e^(−x²) = √π (1e-10); `expm` of the double integrator matches the analytic result |
| `test_lqr_double_integrator_matches_closed_form` | `control.lqr` for ẍ = u with Q = I, R = 1 gives K = [1, √3], P = [[√3, 1], [1, √3]] and poles −√3/2 ± j/2 (rtol 1e-10); cross-checked against `scipy.linalg.solve_continuous_are`; controllability rank 2 |
| `test_lqr_initial_response_matches_analytic_solution` | `control.ss` + `initial_response` match x(t) = e^(−√3t/2)(cos(t/2) + √3 sin(t/2)) to 1e-8 |
| `test_lqr_gain_matches_closed_form_for_positive_weights` | Hypothesis, 60 examples, q₁, q₂, r ∈ [1e-3, 1e3]: K = [√(q₁/r), √((q₂ + 2√(q₁r))/r)] (rtol 1e-6); stable poles; P symmetric positive definite |
| `test_sympy_characteristic_roots_match_lqr_poles` | Symbolic roots of s² + √3 s + 1 equal the numerical LQR poles |
| `test_pint_unit_conversions_and_dimension_checks` | 50 km/h = 125/9 m/s; 1 kWh = 3.6e6 J; 120 Wh/km = 432 J/m; m + s raises `DimensionalityError` |
| `test_yaml_config_validated_by_pydantic` | YAML parsed and validated; a negative mass is rejected |
| `test_pandas_statsmodels_regression_and_bonferroni` | OLS formula fit recovers known coefficients; Bonferroni on [0.01, 0.04, 0.03] gives [0.03, 0.12, 0.09] |
| `test_plot_is_saved_under_project_artifacts` | Saves the LQR response figure under `artifacts\figures`; valid PNG, 960×540 px |
| `test_project_env_var_points_under_root[×14]` (`env_paths`) | Each variable from `project.env` is set and points under `D:\EUREKA-2026` |
| `test_library_runtime_dirs_resolve_under_root` (`env_paths`) | The directories Matplotlib, Jupyter, IPython, tempfile, pytest `tmp_path`, the pytest cache and Hypothesis actually resolve to are under `D:\EUREKA-2026` |
| `test_pip_cache_dir_under_root` (`env_paths`) | `pip cache dir` is under `cache\` |

The LQR cases are textbook checks with known solutions. They test the libraries, not the
research model, and no research algorithm has been implemented.

## 4. Negative controls (the checks can fail)

| Control | Command | Expected | Observed |
|---|---|---|---|
| Unactivated shell | `.venv\Scripts\python.exe -m pytest -m env_paths` without `project.env` | Path tests fail | 16 failed, exit 1; e.g. "PIP_CACHE_DIR=D:\AI\Cache\Pip is outside D:\EUREKA-2026" |
| Unlocked package in .venv | `uv pip install tomli-w`, then `setup.ps1` | Setup refuses to prune silently | Exit 1, listed `- tomli-w==1.2.0`, package left installed (`logs\setup-20261023-130357.log`) |
| Same state, `verify.ps1` | `verify.ps1` | Lock checks fail | 16/19, exit 1: `uv sync --check` FAIL, imports-vs-lock FAIL; `uv pip check` and `pip check` PASS, correctly, since tomli-w conflicts with nothing. Also caught a real defect: two unformatted scripts (`verify-20261023-130404.log`) |
| Prune on request | `setup.ps1 -AllowPrune` | Removes tomli-w | "Uninstalled 1 package", exit 0 (`setup-20261023-130440.log`) |
| Stray cache | `verify.ps1` after an unconfigured `ruff` call | Check 18 fails | FAIL on `repo\.ruff_cache`, exit 1 (`verify-20261023-130447.log`); fixed with `cache-dir` in `[tool.ruff]` |

## 5. Setup runs (rerun safety)

| Log | Working dir | Flags | Exit | Outcome |
|---|---|---|---|---|
| `setup-20261023-125644.log` | `D:\EURÉKA 2026 - KT` | none | 0 | First install: CPython 3.14.7 downloaded (21.7 MiB) into `tools\python`; `uv lock` resolved 71; installed 65 packages in 5.03 s; kernel registered; 36 s total |
| `setup-20261023-130324.log` | `repo\` | none | 1 | **Script defect:** run inside `repo\`, `uv python find` returned `.venv\Scripts\python.exe`, which failed the under-`tools\python` assertion. Fixed with `uv python find --system` |
| `setup-20261023-130331.log` | `D:\EURÉKA 2026 - KT` | none | 0 | No changes |
| `setup-20261023-130354.log` | `repo\` | none | 0 | After the fix: "Would make no changes" |
| `setup-20261023-130357.log` | `repo\` | none | 1 | Negative control (tomli-w), as intended |
| `setup-20261023-130440.log` | `repo\` | `-AllowPrune` | 0 | Removed tomli-w |
| `setup-20261023-131109.log` | `repo\` | none | 0 | Final configuration: "Would make no changes" |

The setup script only creates missing folders. It never deletes project data, refuses to
replace a `.venv` built from another interpreter, and never prunes packages without `-AllowPrune`.

## 6. Resolved versions

Direct dependencies, installed version = locked version (from check 8):

| numpy | scipy | pandas | matplotlib | sympy | control | pint | pyyaml |
|---|---|---|---|---|---|---|---|
| 2.5.4 | 1.18.1 | 3.1.0 | 3.11.2 | 1.14.0 | 0.10.2 | 0.26.2 | 6.0.3 |

| pydantic | statsmodels | pytest | pytest-cov | hypothesis | ruff | pip | ipykernel |
|---|---|---|---|---|---|---|---|
| 2.14.1 | 0.15.0 | 9.1.1 | 7.1.0 | 6.170.8 | 0.17.2 | 26.2.2 | 7.4.0 |

All 65 installed distributions:

annotated-types 0.8.0, asttokens 3.0.2, colorama 0.4.6, comm 0.2.3, contourpy 1.4.0,
control 0.10.2, coverage 7.17.0, cycler 0.12.1, debugpy 1.8.22, executing 2.3.0, flexcache 0.3,
flexparser 0.4, fonttools 4.67.0, formulaic 1.2.2, hypothesis 6.170.8, iniconfig 2.3.1,
interface-meta 2.0.1, ipykernel 7.4.0, ipython 9.17.1, ipython-pygments-lexers 1.1.1,
jedi 0.20.1, jupyter-client 8.10.0, jupyter-core 5.9.1, kiwisolver 1.5.1, matplotlib 3.11.2,
matplotlib-inline 0.2.2, mpmath 1.3.0, narwhals 2.27.1, nest-asyncio2 1.7.4, numpy 2.5.4,
packaging 26.3, pandas 3.1.0, parso 0.8.7, patsy 1.0.3, pillow 13.0.0, pint 0.26.2, pip 26.2.2,
platformdirs 4.13.5, pluggy 1.7.0, prompt-toolkit 3.0.53, psutil 7.2.2, pure-eval 0.2.4,
pydantic 2.14.1, pydantic-core 2.50.1, pygments 2.21.0, pyparsing 3.3.3, pytest 9.1.1,
pytest-cov 7.1.0, python-dateutil 3.0.0, pyyaml 6.0.3, pyzmq 27.2.0, ruff 0.17.2, scipy 1.18.1,
six 1.17.0, sortedcontainers 2.4.0, stack-data 0.6.3, statsmodels 0.15.0, sympy 1.14.0,
tornado 6.6, traitlets 5.16.1, typing-extensions 4.16.0, typing-inspection 0.4.4, tzdata 2026.5,
wcwidth 0.9.3, wrapt 2.5.1.

The authoritative pins, with hashes, are in `repo\uv.lock` and `repo\requirements-lock.txt`.

## 7. Known warnings (not failures)

Starting the kernel from a script prints two warnings. ipykernel notes that the local kernel
uses TCP without CurveZMQ encryption (the normal default for a local kernel), and pyzmq notes
that the Windows Proactor event loop is falling back to a selector thread. Neither affects
execution: check 14 passes.

## 8. Reproduce

```powershell
powershell -NoProfile -ExecutionPolicy RemoteSigned -File D:\EUREKA-2026\repo\scripts\setup.ps1
powershell -NoProfile -ExecutionPolicy RemoteSigned -File D:\EUREKA-2026\repo\scripts\verify.ps1
```

Without uv, on Windows with CPython 3.14 (fallback; **not executed in this session**):
`python -m venv D:\EUREKA-2026\.venv`, then
`D:\EUREKA-2026\.venv\Scripts\python.exe -m pip install --require-hashes -r D:\EUREKA-2026\repo\requirements-lock.txt`.
