# Path exceptions and installation failures

> Recorded on 2026-10-23 when the project lived in `D:\EUREKA-2026` (Git repo in `repo\`). Since the move that day the project root is `D:\EURÉKA 2026 - KT`; see `migration-2026-10-23.md`.

What remains outside `D:\EUREKA-2026`, what went wrong during setup, and what is still open.
Status as of 2026-10-23 13:11 (+07:00).

## 1. Installation failures

**None outstanding.** All requested core, testing and notebook packages installed from binary
wheels, and the final verification passed 19/19 (see [installation-verification.md](installation-verification.md)).
Optional packages were deferred on purpose (see [software-purpose-and-justification.md](software-purpose-and-justification.md));
none of them failed.

Failures during setup, all fixed:

| When | Failure | Cause | Fix |
|---|---|---|---|
| 13:03:24 | `setup.ps1` exit 1 when run inside `repo\` | `uv python find 3.14.7` returns the project `.venv` interpreter when run inside the project | Changed to `uv python find --system` (verified from both working directories) |
| 13:04:04 | `ruff format --check` FAIL | Two new helper scripts were not formatted | `ruff format` |
| 13:04:47 | Stray `repo\.ruff_cache` | Ruff run without `RUFF_CACHE_DIR` | Removed (created 13:04:40, cache only); added `cache-dir` to `[tool.ruff]` |

## 2. Writes to C: caused by this setup

| Item | Size | Status |
|---|---|---|
| CPython 3.12.14 and 3.13.15 in `C:\Users\HLC\AppData\Roaming\uv\python` | about 120 MB | **Reverted.** uv downloaded them automatically during the compatibility check (`uv pip compile --python-version 3.12/3.13` with no local interpreter). Removed with `uv python uninstall` (`logs\phaseB-undo-autodownloaded-pythons.log`). The pre-existing 3.14.7 there (created 2026-10-15) was not touched. Prevented from now on by `UV_PYTHON_DOWNLOADS=manual` and `python-downloads = "manual"`. |
| `C:\Users\HLC\.matplotlib\fontlist-v3.11.0.json` | 149,500 bytes | **Reverted.** Written by an unactivated diagnostic command (`import control` builds Matplotlib's font cache). Removed; the pre-existing `fontlist-v390.json` was not touched. |
| `C:\Users\HLC\AppData\Local\npm-cache\_logs\2026-10-23T05_47_1*-debug-0.log` (3 files) | about 2.7 KB | Left in place. Written by `npm --version` / `npm config get` during the inventory; npm rotates these logs itself. |
| `C:\Users\HLC\AppData\Local\Temp\pytest-of-HLC\pytest-246\` | empty folders | Left in place. Created by the deliberately unactivated negative-control test run; pytest keeps only its 3 most recent folders. |
| This Claude Code session | n/a | The transcript and tool outputs are under `C:\Users\HLC\.claude\projects\d--EUR-KA-2026---KT\`; the scratch files (extracted thesis text, about 0.9 MB, and compatibility-check inputs) are under `C:\Users\HLC\AppData\Local\Temp\claude\`. Claude Code manages both. |

No registry entries were added (`--no-registry`). No user-level or machine-level environment
variables were changed. The HKCU entries `PythonCore\3.11` and `Astral\CPython3.14.7`
existed before this setup and are unchanged.

## 3. Components that stay on C: by design (pre-existing, reused, not reinstalled)

| Component | Location | Why it stays |
|---|---|---|
| uv 0.12.15 | `C:\Users\HLC\AppData\Local\Microsoft\WinGet\Packages\astral-sh.uv_…\uv.exe` | Working winget install; a single executable. Its caches and Python installs for this project go to D:. |
| Git 2.54 | `C:\Program Files\Git` | System install, shared |
| VS Code 1.143.1 and extensions | `C:\Users\HLC\AppData\Local\Programs\Microsoft VS Code`, `C:\Users\HLC\.vscode\extensions` | Per-user install. VS Code also keeps settings, workspace state and Pylance/Jupyter-extension caches under `%APPDATA%\Code` and `%LOCALAPPDATA%`; that location is not configurable per project. |
| Windows PowerShell 5.1, py launcher | `C:\Windows\…` | Part of Windows |
| Node.js / npm | `C:\Program Files\nodejs`; cache `C:\Users\HLC\AppData\Local\npm-cache` (3.5 GB) | Not used by this project; global npm config left unchanged |
| Claude Code | Extension binary under `C:\Users\HLC\.vscode\extensions\anthropic.claude-code-2.1.304-win32-x64\`; data in `C:\Users\HLC\.claude\` (1.3 GB), `C:\Users\HLC\.claude.json`, `C:\Users\HLC\AppData\Local\claude-cli-nodejs\` | Working; left as is |

## 4. Conditional exceptions (only if the project environment is bypassed)

`project.env` is loaded by `scripts\activate.ps1`, `setup.ps1` and `verify.ps1`, by VS Code
(`python.envFile`) and by the Jupyter kernel (`kernel.json` → `env`). Bypassing all of these
changes where files go:

| Action | Consequence | Mitigation in place |
|---|---|---|
| Running `.venv\Scripts\python.exe` from a plain shell | The Matplotlib font cache goes to `%USERPROFILE%\.matplotlib`; pytest `tmp_path` and `tempfile` go to `C:\Users\HLC\AppData\Local\Temp`; pip's cache goes to `D:\AI\Cache\Pip` (the user-level setting); IPython and Jupyter files go under `%USERPROFILE%` / `%APPDATA%` | Hypothesis storage is pinned in `tests\conftest.py`; the pytest cache is pinned in `pyproject.toml`; the 16 `env_paths` tests fail loudly; `verify.ps1` scans C: |
| Running `uv sync` / `uv add` in `repo\` from a plain shell | uv creates **`repo\.venv`** using a different 3.14 interpreter, because no config-file setting exists for the project-environment path | The uv cache stays on D: (`cache-dir` in `[tool.uv]`); no Python downloads (`python-downloads = "manual"`); `verify.ps1` check 18 flags `repo\.venv`; the README warns about it |

If you want unactivated runs to be safe too, one option is a small `sitecustomize.py` in
`.venv` that loads `project.env` defaults. It was **not** added, because it would silently
change the startup behaviour of every Python process in the venv.

## 5. Open items for you to decide

1. **C: free space (7.5 GB).** Large caches that predate this project: npm cache 3.5 GB,
   legacy pip cache `C:\Users\HLC\AppData\Local\pip\cache` 2.2 GB, uv cache
   `C:\Users\HLC\AppData\Local\uv\cache` 617 MB, and `C:\Users\HLC\.claude` 1.3 GB. They were
   not cleaned, as instructed. Clearing them is a decision for you.
2. **Provenance of existing results.** The figures in the current thesis draft come from
   random noise around hard-coded values (see the inventory, section 5). They must be
   replaced by regenerated results before any claim is made.
3. **Research decisions that gate the deferred packages:** whether battery degradation stays
   in scope (PyBaMM), approval of the multi-objective formulation (pymoo), a written
   sensitivity design (SALib), and the statistical analysis plan (statsmodels is installed
   on that assumption).
4. **`docs\` is outside the Git repository**, as the requested layout specifies, so these
   provenance documents are not version-controlled. Consider moving them into `repo\docs\`
   or tracking them another way.
5. **Git.** `repo\` is initialised with nothing committed. The first commit is yours to make.
6. **VS Code.** Your current window (`D:\EURÉKA 2026 - KT`) uses the C: Python 3.11, so
   Pylance reports the project's packages as missing there. Open `D:\EUREKA-2026\repo` to
   pick up `.vscode\settings.json`.
7. `C:\Users\HLC\Documents\gcc.bat` is ahead of MSYS2 `gcc.exe` on PATH. It doesn't matter
   for this wheels-only setup, but it would matter if a package ever needs a source build.
8. `C:\Users\HLC\AppData\Local\Programs\Python\Python314\` has no interpreter, but its
   `Lib\site-packages` holds 908 files (18.1 MB), probably left by an uninstalled Python 3.14.
   The project venv is isolated from it. It was not touched.
