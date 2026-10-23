# Software purpose and justification

> Recorded on 2026-10-23 when the project lived in `D:\EUREKA-2026` (Git repo in `repo\`). Since the move that day the project root is `D:\EURÉKA 2026 - KT`; see `migration-2026-10-23.md`.

Why each component is in the environment, or why it is not yet.

Rule applied: a package is installed only when a task that is already defined needs it.
Optional tools are compatibility-checked, so adding one later is a single command, but they
stay out of `uv.lock` until a research decision justifies them. Exact versions are in
`repo\uv.lock`.

## 1. Platform choices

| Choice | Decision | Justification |
|---|---|---|
| Python version | **3.14.7** | Newest stable CPython on 2026-10-23: uv's download list offers 3.15 only as `3.15.0rc2`. Every candidate package, including the deferred ones (PyBaMM + casadi, pymoo, SALib, mypy, JupyterLab), resolved to binary `win_amd64` wheels for 3.12, 3.13 and 3.14 (`logs\phaseB-compat-check.log`). Compatibility therefore did not force an older version. |
| Interpreter location | `D:\EUREKA-2026\tools\python` | Installed with `uv python install 3.14.7 --install-dir … --no-bin --no-registry`: nothing goes on PATH and no Windows registry entry is created. |
| Environment manager | uv 0.12.15 (already installed) | It installs a managed interpreter into a chosen folder, writes a universal lockfile with hashes (`uv.lock`), syncs the venv exactly to it, and checks consistency (`uv lock --check`, `uv sync --check`). |
| pip | 26.2.2, pinned in the `dev` group | uv venvs do not include pip. It is kept for `pip check` and so `requirements-lock.txt` can be installed with plain pip. |
| `requires-python` | `==3.14.*` | Keeps the lock tied to one minor version, for reproducibility. |
| Project mode | `package = false` | No research package exists yet. When code is added under `repo\src\`, switch to a packaged project. |

## 2. Installed packages

### Core scientific computing (`[project].dependencies`)

| Package | Version | Role in this study |
|---|---|---|
| NumPy | 2.5.4 | Arrays and linear algebra for vehicle and battery state models. Use seeded `np.random.default_rng` Generators for Monte Carlo runs; Ruff rule `NPY002` flags the legacy global `np.random.*` calls. |
| SciPy | 1.18.1 | ODE integration (`solve_ivp`) for longitudinal dynamics and battery states; Riccati solvers (`solve_continuous_are`) as an independent check on LQR gains; optimisation; basic tests (`ttest_ind`, `f_oneway`). |
| pandas | 3.1.0 | Drive-cycle time series, run logs and result tables written to `artifacts\tables`. Note: pandas 3 makes copy-on-write and the string dtype the default, so pandas-2 code may need changes. |
| Matplotlib | 3.11.2 | Figures in `artifacts\figures`, generated only from saved run outputs. |
| SymPy | 1.14.0 | Symbolic linearisation of the vehicle model and closed-form results used as test oracles, such as the double-integrator Riccati solution in `tests\`. |
| python-control | 0.10.2 | State-space models, `lqr`, closed-loop simulation. `lqr(..., method="scipy")` is used because Slycot is not installed (section 3). |
| Pint | 0.26.2 | Unit-aware parameters and conversions (km/h↔m/s, Wh/km↔J/m, kWh↔J), raising `DimensionalityError` on unit mistakes. Convert to plain floats at model boundaries; Pint is not meant for inner loops. |
| PyYAML | 6.0.3 | Human-readable experiment configuration files. |
| Pydantic | 2.14.1 | Typed validation of those configurations, so a run cannot start with, say, a negative mass or a missing parameter source. |

### Statistical analysis

| Package | Version | Justification |
|---|---|---|
| statsmodels | 0.15.0 | The draft's evaluation compares several controllers across several drive cycles, with t-tests, ANOVA and Bonferroni correction over Monte Carlo trials. A two-factor design (controller × cycle) needs a linear-model ANOVA (`ols` + `anova_lm`); SciPy only provides one-way `f_oneway`. `multipletests` provides Bonferroni and Holm corrections. Power analysis (`TTestIndPower`) can justify the number of trials instead of fixing it at 100 in advance. **Condition:** specify the tests, factors and correction before generating results. If the redesigned study drops these comparisons, remove the package. |

### Testing and code quality (`dev` group)

| Package | Version | Role |
|---|---|---|
| pytest | 9.1.1 | Test runner. Cache redirected to `cache\pytest` (`cache_dir` in `pyproject.toml`). |
| pytest-cov | 7.1.0 | Coverage. Data file `cache\coverage\.coverage` (via `COVERAGE_FILE`). Coverage becomes meaningful once a source package exists. |
| Hypothesis | 6.170.8 | Property-based tests. Already used to check python-control's LQR gain against the closed form over random positive weights. Database in `cache\hypothesis`. |
| Ruff | 0.17.2 | Lint (rules E, F, W, I, B, UP, NPY, PT) and formatting. Cache in `cache\ruff`. |

### Notebooks (`notebook` group)

| Package | Version | Role |
|---|---|---|
| ipykernel | 7.4.0 | Registers kernel `eureka-2026` inside the venv (`--sys-prefix`), with `MPLCONFIGDIR`, `IPYTHONDIR`, `TEMP` and `TMP` pinned to D: in `kernel.json`. VS Code's Jupyter extension can use it directly. |

## 3. Deferred: checked, not installed

| Package | Checked version | Why deferred | Install when | Command (in an activated shell, in `repo\`) |
|---|---|---|---|---|
| JupyterLab | 4.6.4 | VS Code with the Jupyter extension already covers notebooks through ipykernel. JupyterLab would grow the Windows environment from 65 to 128 packages (Jupyter server, web and templating stack; measured with `uv pip compile`). | You want browser-based notebooks. | `uv add --group notebook jupyterlab` |
| mypy | 2.4.0 | There is no project code yet. Numerical code is mostly NumPy arrays, and Pint `Quantity` typing is weak, so static typing would mean annotation work with little return. Runtime validation (Pydantic) and Ruff cover the immediate risks. | The model and controller package has stable interfaces (configuration and result classes) that are worth checking statically. | `uv add --dev mypy` |
| SALib | 1.6.0 | The draft's "±30 % parameter variation" is a one-at-a-time sweep, which NumPy handles. Global methods (Sobol, Morris, FAST) are defensible only with a written design: the uncertain parameters, sourced ranges or distributions, the output metrics and an affordable sample budget. None exists yet. | That sensitivity design is written down in `docs\`. | `uv add salib` |
| pymoo | 0.6.2 | NSGA-II is contribution (2) of the draft, but its "battery longevity" objective requires a degradation model that does not yet exist with provenance (see PyBaMM). The research question is not yet approved in its current form. | The objectives are approved and each can be computed from a validated model. | `uv add pymoo` |
| PyBaMM | 26.10.1.1 (+ casadi 3.8.1) | See section 4. | All prerequisites in section 4 are met. | `uv add --group battery pybamm` (adds `battery` to `[dependency-groups]`; also add it to `default-groups` if it should install by default) |
| Slycot | n/a | python-control's `lqr` works through SciPy without it, and the tests pin `method="scipy"`. It is only needed for some advanced routines (e.g. H∞ synthesis, balanced reduction). | One of those routines is needed. | Check wheel availability first: `uv add slycot` |
| seaborn | n/a | Only the old figure script in `D:\EUREKA` uses it; Matplotlib is enough. | n/a | n/a |

After any `uv add`, rerun
`powershell -File D:\EUREKA-2026\repo\scripts\verify.ps1` and update this file.

## 4. PyBaMM: what was investigated

- **Compatibility.** PyBaMM 26.10.1.1 and casadi 3.8.1 have Windows wheels for Python 3.14.
  The official installation page says PyBaMM supports Python 3.10–3.15 on Linux, macOS and
  Windows, and recommends a virtual environment (`pip`/`uv pip install pybamm`, or conda-forge).
- **Parameter sets.** In PyBaMM's built-in parameter-set documentation, **Prada2013** is the
  only LFP set, and its description does not mention SEI or degradation parameters. The SEI
  parameters in most other sets are labelled "example parameters" that "do not claim to be
  representative of the true parameter values". OKane2022 was fitted to experimental ageing
  data, but for an LG M50 NMC811 cell, not LFP.
- **The draft** assumes LFP cells and an empirical Arrhenius SEI-growth law with parameters
  attributed to "Huria et al.". Whether that reference provides degradation parameters, as
  opposed to electrical or thermal cell parameters, still has to be checked against the source.
- **Conclusion.** Installing PyBaMM would not support a claim about capacity fade over 1000
  cycles. It would only make an unvalidated model available. Prerequisites before installing:
  1. Battery degradation is confirmed to be in scope for the approved research question.
  2. The cell (chemistry, manufacturer and model) is fixed.
  3. A parameter set, including degradation parameters, has documented provenance.
  4. Measured ageing or cycling data for that chemistry is available, and its source and
     licence are recorded in `docs\` and the raw files stored in `data\raw\`.
  5. A validation criterion is chosen, such as an error bound on capacity fade against that
     data, together with the cycling protocol.

## 5. Not part of the Python environment

| Tool | Status |
|---|---|
| MATLAB/Simulink | Not installed. The draft says it was used, but no models exist on this machine. The study will be (re)implemented in Python in `repo\`. |
| MiKTeX, Pandoc | Pre-existing on C:, used for earlier report builds. Unchanged. |
| Node.js/npm | Pre-existing. Not needed by this project. |
