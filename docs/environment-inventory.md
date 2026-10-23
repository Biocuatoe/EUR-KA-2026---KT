# Environment inventory

Machine inspection (Phase A) and the resulting installed state.
Recorded 2026-10-23 on `DESKTOP-QF465MB`, Windows 10 Pro 10.0.19045, user `HLC`.
Every value below was read from the machine with a command during this session.

## 1. Disks

| Drive | Label | Size | Free at start | Free at end |
|---|---|---|---|---|
| C: | (none) | 237.85 GB | 7.75 GB | 7.52 GB |
| D: | GAME | 476.29 GB | 337.15 GB | 336.54 GB |

C: is nearly full, so keeping caches and temporary files off it matters here.
Other running applications also write to C:, which explains the 0.23 GB change. This
setup's net writes to C: are listed in [path-exceptions-and-failures.md](path-exceptions-and-failures.md).
On D:, the project uses about 0.6 GB of physical space. Explorer will show more, because uv
hard-links `.venv` files to `cache\uv`, so both folders count the same blocks.

## 2. Executables found (before any installation)

| Tool | Version | Path | Notes |
|---|---|---|---|
| Python | 3.11.9 | `C:\Users\HLC\AppData\Local\Programs\Python\Python311\python.exe` | First `python` on PATH; HKCU `PythonCore\3.11`; pip 24.0 |
| Python (uv-managed) | 3.14.7 | `D:\AI\Runtimes\Python\cpython-3.14.7-windows-x86_64-none\python.exe` | HKCU `Astral\CPython3.14.7`; base of `D:\AI\Envs\CareLens-VLM` |
| Python (uv-managed) | 3.14.7 | `C:\Users\HLC\AppData\Roaming\uv\python\cpython-3.14.7-windows-x86_64-none\python.exe` | uv's default install dir, created 2026-10-15 |
| (residue) | n/a | `C:\Users\HLC\AppData\Local\Programs\Python\Python314\` | No interpreter. `Lib\site-packages` holds 908 files (18.1 MB), probably left by an uninstalled Python 3.14. Not used: the project venv has `include-system-site-packages = false` |
| py launcher | n/a | `C:\Windows\py.exe` | |
| uv | 0.12.15 | `C:\Users\HLC\AppData\Local\Microsoft\WinGet\Packages\astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe\uv.exe` | winget install; reused |
| Git | 2.54.0.windows.1 | `C:\Program Files\Git\cmd\git.exe` | Global user.name/email configured |
| VS Code | 1.143.1 | `C:\Users\HLC\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd` | Extensions: ms-python.python 2026.10.0, Pylance 2026.4.1, python-envs 1.40.0, debugpy 2026.6.0, ms-toolsai.jupyter 2025.9.1 |
| Windows PowerShell | 5.1.19041.6456 | `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe` | PowerShell 7 (`pwsh`) not installed. Execution policy CurrentUser = RemoteSigned |
| Node.js / npm | v24.15.0 / 11.12.1 | `C:\Program Files\nodejs\node.exe`, `npm.cmd` | npm prefix `C:\Users\HLC\AppData\Roaming\npm` |
| winget | v1.29.380 | `C:\Users\HLC\AppData\Local\Microsoft\WindowsApps\winget.exe` | |
| gcc | n/a | `C:\Users\HLC\Documents\gcc.bat` (first on PATH), `C:\msys64\mingw64\bin\gcc.exe` | Not needed: every package installs from a binary wheel |
| LaTeX / Pandoc | n/a | `...\MiKTeX\miktex\bin\x64\xelatex.exe`, `C:\Users\HLC\AppData\Local\Pandoc\pandoc.exe` | Used by earlier report builds in `D:\EUREKA` |
| Not found | | | MATLAB, conda/mamba, pipx, pnpm, yarn, choco, scoop, cmake, MSVC `cl`, `jupyter`, `pwsh`, standalone `claude` CLI |

## 3. Claude Code installation (inspected, not modified)

| Item | Location | Size |
|---|---|---|
| Running binary (VS Code extension `anthropic.claude-code` 2.1.304) | `C:\Users\HLC\.vscode\extensions\anthropic.claude-code-2.1.304-win32-x64\resources\native-binary\claude.exe` | n/a |
| Settings, sessions, transcripts, plugins | `C:\Users\HLC\.claude\` | 1,321.7 MB |
| Account/config file | `C:\Users\HLC\.claude.json` | n/a |
| MCP logs cache | `C:\Users\HLC\AppData\Local\claude-cli-nodejs\` | 0.3 MB |
| Session scratchpad | `C:\Users\HLC\AppData\Local\Temp\claude\` | n/a |

A second extension, `andrepimenta.claude-code-chat` 2.3.1, is also installed. Claude Code
was working, so it was left as is.

## 4. Caches and environment variables found

| Item | Value at start | Size |
|---|---|---|
| `PIP_CACHE_DIR` (User) | `D:\AI\Cache\Pip` | 2,749.4 MB |
| Legacy pip cache | `C:\Users\HLC\AppData\Local\pip\cache` | 2,222.1 MB |
| uv cache (no `UV_CACHE_DIR` set) | `C:\Users\HLC\AppData\Local\uv\cache` | 617.0 MB (`D:\AI\Cache\uv` exists but is empty) |
| uv Python dir (default) | `C:\Users\HLC\AppData\Roaming\uv\python` | 60.2 MB |
| npm cache | `C:\Users\HLC\AppData\Local\npm-cache` | 3,507.7 MB |
| `HF_HOME` / `HF_HUB_CACHE` (User) | `D:\AI\Cache\HuggingFace[\hub]` | n/a |
| Matplotlib | `C:\Users\HLC\.matplotlib` (`fontlist-v390.json`) | 0.1 MB |
| Jupyter / IPython | none (`~\.jupyter`, `%APPDATA%\jupyter` and `~\.ipython` absent) | n/a |
| `TEMP` / `TMP` (User) | `C:\Users\HLC\AppData\Local\Temp` | n/a |

None of these user-level settings were changed. The project overrides them per process
through `repo\project.env` (section 7).

## 5. Existing project material

| Location | Contents | Relevance |
|---|---|---|
| `D:\EURÉKA 2026 - KT\EURÉKA 2026 - KT.docx` | Thesis draft, 434,945 bytes, modified 2026-09-21, SHA-256 `01363A069EEB005851F6D62AC4B9DA9E3FD13A742BEBBFDFC14C802F0EDDFF8C` | Defines the intended study (below) |
| `D:\EURÉKA 2026 - CNTT\` | A separate CNTT thesis draft | Out of scope |
| `D:\EUREKA\` | Earlier working folder: LaTeX sources and PDF builds (CNTT02, KT01), `scripts\render_kt01_figures.py` | See provenance finding |
| `D:\EUREKA\KT01_MicroEV\` | Three Markdown planning files only: `BLUEPRINT_200TRANG.md`, `DATA_AND_COLAB_PROMPTS.md`, `PROMPTS_KT01.md` | No code, data or models |
| `D:\AI\Envs\`, `D:\AI\Models\` | CareLens venvs; Ollama, Piper and CareLens-VLM models | Unrelated to KT |

**Not found anywhere inspected:** any simulation code, Simulink model, drive-cycle data file,
battery test data, notebook, `pyproject.toml`, requirements file or virtual environment for
the KT study. `data\raw\` therefore starts empty.

**Study as described in the draft:** an adaptive LQR whose gains follow battery state of
health, for a micro-EV powertrain. It compares the controller with P, PID, fixed-gain LQR,
fuzzy LQR, MPC and DDPG on NEDC, WLTP, CLTC and a custom Vietnam Urban Cycle. The
battery model is an LFP cell with empirical Arrhenius SEI-growth capacity fade, parameters
attributed to "Huria et al.". Other planned elements are NSGA-II Pareto optimisation of
energy against battery longevity, Monte Carlo runs (100 per configuration), t-test and ANOVA
with Bonferroni correction, and ±30 % parameter sensitivity. The draft says the vehicle model
was implemented in MATLAB/Simulink, but MATLAB is not installed on this machine.

### Provenance finding (affects every existing result)

- `D:\EUREKA\scripts\render_kt01_figures.py` draws the result figures from `np.random`
  around hard-coded values instead of simulation output. For example:
  - lines 245–248: `adaptive_lqr = reference + np.random.randn(500) * 1.5`, `fixed_lqr … * 3.0`, `pid … * 4.5`
  - line 321: the Pareto front is built as `longevity = 100 - 0.3 * (100 - energy) + noise`
  - lines 565–566: `adaptive_errors = np.random.normal(3.2, 0.8, 100)`, `fixed_errors = np.random.normal(5.8, 1.5, 100)`
- `D:\EUREKA\KT01_MicroEV\DATA_AND_COLAB_PROMPTS.md`, line 3, states the intent: *"Dùng số
  liệu công bố từ papers/datasheet làm "ground truth". Prompt Colab sẽ mô phỏng với noise hợp
  lý quanh ground truth, cho ra kết quả realistic không thể phân biệt với thực nghiệm."*
  In English: use published numbers as "ground truth", and simulate "with reasonable noise
  around ground truth" so the results are "realistic, indistinguishable from experiment".
- Consequently, none of the figures, tables or headline numbers in the draft can be treated
  as simulation or experimental evidence. That includes "12.5 % ± 2.1 % energy improvement"
  and "15.3 % ± 2.8 % less capacity fade over 1000 cycles". Every result must be regenerated
  from code in `repo\`, with inputs in `data\` and outputs in `artifacts\`.
- The draft is also internally inconsistent: the abstract says 1000 cycles, while a figure
  title says "Capacity Fade Comparison Over 1500 Cycles".

None of these files were modified.

## 6. Reuse assessment

| Candidate | Decision | Reason |
|---|---|---|
| uv 0.12.15 (C:) | Reused | Working, recent, single binary. Reinstalling it on D: brings no benefit |
| Git, VS Code + Python/Jupyter extensions, PowerShell 5.1 | Reused | Working; reinstalling would disrupt other projects |
| CPython 3.14.7 at `D:\AI\Runtimes\Python` | Not used as the base interpreter | Owned by another project's setup (`CareLens-VLM` depends on it) and not on uv's default search path. A project-owned copy cost a 21.7 MiB download and isolates EURÉKA from changes there |
| CPython 3.11.9 (C:) | Not used | Older, and on C: |
| uv cache on C: (617 MB) | Not used | Reusing it would keep project package data on C: |
| pip caches (D:\AI, C:) | Not usable | pip's HTTP cache format cannot be read by uv |
| `D:\AI\Envs\*` venvs | Not shared | Belong to other projects; sharing would break isolation |

## 7. Installed state (after setup)

```
D:\EUREKA-2026
├── .venv\                  Python 3.14.7 virtual environment (65 packages, 476.9 MB logical)
├── tools\python\           cpython-3.14.7-windows-x86_64-none (uv-managed, 60.3 MB; no PATH shim, no registry entry)
├── tools\jupyter\          JUPYTER_CONFIG_DIR, JUPYTER_DATA_DIR
├── cache\                  uv (436.5 MB), pip, matplotlib, ipython, jupyter\runtime, pytest, hypothesis, ruff, coverage, tmp
├── repo\                   Git repository (initialised, nothing committed)
│   ├── pyproject.toml      direct dependencies (lower bounds) and tool configuration
│   ├── uv.lock             exact, hashed, universal lock (71 entries; 65 apply on Windows)
│   ├── requirements-lock.txt  pip-compatible export of uv.lock with hashes
│   ├── .python-version     3.14.7
│   ├── project.env         every cache and runtime path (single source of truth)
│   ├── scripts\            setup.ps1, activate.ps1, verify.ps1, _common.ps1, check_imports.py, check_kernel.py
│   ├── tests\              environment verification tests (27)
│   └── .vscode\settings.json  interpreter = D:\EUREKA-2026\.venv, envFile = project.env
├── data\raw\, data\processed\           empty
├── artifacts\figures\environment-check\ verification plot
├── artifacts\reports\                   verification JSON and JUnit reports
├── logs\                                setup, verify, compatibility-check logs
└── docs\                                this documentation (outside the Git repository, per the requested layout)
```

Verified executable paths:

| Role | Path |
|---|---|
| Project interpreter | `D:\EUREKA-2026\.venv\Scripts\python.exe` (Python 3.14.7) |
| Base interpreter | `D:\EUREKA-2026\tools\python\cpython-3.14.7-windows-x86_64-none\python.exe` |
| pip | `D:\EUREKA-2026\.venv\Lib\site-packages\pip` (26.2.2, via `python -m pip`) |
| pytest / ruff / jupyter | `D:\EUREKA-2026\.venv\Scripts\{pytest,ruff,jupyter}.exe` |
| Jupyter kernel | `eureka-2026` at `D:\EUREKA-2026\.venv\share\jupyter\kernels\eureka-2026` |
| uv (reused) | `C:\Users\HLC\AppData\Local\Microsoft\WinGet\Packages\astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe\uv.exe` |
