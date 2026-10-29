# OpenModelica launcher and the Unicode-path workaround

Launcher: `verification/Invoke-OpenModelica.ps1` (ASCII-only, Windows PowerShell 5.1). Written and tested 2026-10-23.

## 1. Why a launcher is needed

- OpenModelica 1.27.1 is installed at `D:\EURÉKA 2026 - KT\tools\OpenModelica` (installed in an earlier phase; not reinstalled, not uninstalled).
- `omc.exe --version` works from that path. Anything that initialises the compiler fails with *"We could not find some needed MINGW paths in $OPENMODELICAHOME or $OMDEV"*, although `tools\msys\ucrt64\bin\gcc.exe` exists.
- Tried without success: `OPENMODELICAHOME` with and without a trailing backslash, and the 8.3 short name (this volume has no 8.3 names, so the path did not change).
- Mapping the project root to an ASCII drive letter fixes it. The non-ASCII path is therefore the cause *by intervention*; the mechanism inside `omc` was not investigated.
- The installer also set `OPENMODELICAHOME` machine-wide (value contains the `É`). That setting is **left alone**: this task does not remove registry entries or Start Menu shortcuts. The launcher overrides it inside its own process only.

## 2. What the launcher does

| # | Behaviour | How |
|---|---|---|
| 1 | Finds the project root from its own location | `$PSScriptRoot\..`, checked for `project.env`, `.git`, `configs\parameters.yaml`, and for its own folder being named `verification` |
| 2 | Verifies the installation | `tools\OpenModelica\bin\omc.exe` and `tools\msys\ucrt64\bin\gcc.exe` must exist, otherwise it stops with exit code 2 |
| 3-4 | Chooses an unused letter | first free of Y, X, W, V, U, T, S, R, Q, P (not in `subst`, not a drive, not a PSDrive, not existing); with `-DriveLetter` it **refuses** a letter already in use and changes nothing |
| 5 | Creates the alias | `subst X: <project root>`, then proves the alias is the project root by hashing this very script through both paths |
| 6 | Uses alias paths | compiler, working directory, scripts; the `.mos` files use paths relative to `verification\modelica-build`, so they do not depend on the letter |
| 7-8 | Process-scoped environment | saves, then sets `OPENMODELICAHOME`, `APPDATA`, `LOCALAPPDATA`, `TEMP`, `TMP`, `PATH` for this process only, all pointing at D: (`omc-userdata`, `modelica-build\tmp`); child processes inherit them |
| 9 | Smoke test | `omc --version`, then compiles and simulates the linear-drag coast-down `verification/openmodelica-smoke/CoastDown.mo` and checks the end value against its closed form (limit 1e-6 m/s) |
| 10 | Restores the environment | in `finally`; values that were unset are removed again |
| 11-12 | Removes only its own alias | `subst X: /D` only if this invocation created X; afterwards verifies the letter is unmapped and that every other mapping is unchanged |

It writes per-step logs and a summary JSON to `verification\modelica-build\logs\`, and prints each step's exit code, the artifact paths and a cleanup line. Exit code 0 only if every step passed; 2 for a setup error; 3 if cleanup could not be confirmed.

Usage:

```powershell
& 'D:\EURÉKA 2026 - KT\verification\Invoke-OpenModelica.ps1'                       # version + smoke test
& 'D:\EURÉKA 2026 - KT\verification\Invoke-OpenModelica.ps1' -Label x -Mos verification\modelica\scripts\10_static.mos
```

## 3. Evidence that it works (all executed)

| Test | Result |
|---|---|
| First run | alias created, verified and removed, environment restored, **but reported failure (exit 1)**: `Start-Process -PassThru` returned a null `ExitCode`. Fixed by touching the process handle and treating a null code as failure (-998). The cleanup path had worked even in the failing run |
| Second run | `omc` v1.27.1, smoke simulation finished, end-point error 2.84e-9 m/s, exit 0, alias removed, `subst` empty afterwards, process `OPENMODELICAHOME` empty again |
| Requested letter already mapped (a test mapping of my own, `Z:`) | refused with exit 2, "Nothing was changed"; `Z:` still mapped and readable |
| Auto-selection while `Z:` mapped | chose `Y:`, passed, removed `Y:` only; `other_mappings_unchanged=True`; `Z:` still present |
| My test mapping `Z:` | removed by me afterwards; `subst` listed nothing at the end of the task |
| Used for every Modelica run in this task | 11 invocations wrote a summary file (`verification\modelica-build\logs\*-launcher.json`); in all 11 the alias was removed and the environment restored; exit codes: one 1 (the first run, the `ExitCode` bug above) and ten 0. One further invocation (the refused `-DriveLetter Z`) wrote no summary |

## 4. Limits and cautions

- **`omc` exits 0 even when a simulation fails** (it did for the DASSL 1e-12 diagnostic). A launcher exit code 0 means omc ran; whether each simulation succeeded has to be read from the simulation record. `modelica_checks.py` does that (column `simulation_status`).
- The alias is a per-logon-session DOS device mapping visible to every process of the same user while it exists. A launcher killed before its `finally` block leaves it in place until `subst X: /D` or logoff.
- Two launchers started at the same moment could pick the same letter; the second would then fail at `subst` and clean up nothing.
- The launcher assumes the layout of this project (`tools\OpenModelica`, `verification\omc-userdata`). It does not search for anything.
- `omc` made one outbound request in an earlier phase (a library index download that timed out). It runs offline from the cached libraries in `verification\omc-userdata`.
- The launcher does **not** make `OPENMODELICAHOME` correct outside itself: a plain `omc` started from a normal shell still fails on any compile.
- Nothing was written to the user or machine environment or registry by the launcher.
