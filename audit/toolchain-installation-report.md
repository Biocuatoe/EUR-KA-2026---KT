# Independent verification toolchain: installation report

- **Date:** 2026-10-23
- **Scope:** setup only. No vehicle model was written, no existing result, claim verdict, preregistration or the thesis was touched, the 296-run batch was not rerun, nothing was committed or pushed.
- **Project root and Git:** `D:\EURÉKA 2026 - KT`, branch `master`, `HEAD` `f264eca354d67dcdf786063ca36ae246466217d2`.

## 1. Summary

| Item | Result |
|---|---|
| Isolated Python environment | Created and working: `verification\python-env` (CPython 3.14.7) |
| FASTSim | Installed (3.1.0). Minimal BEV simulation on UDDS and HWFET **passed** |
| OpenModelica | Installed (1.27.1), program and data on D:. Minimal model compiled and simulated **only after working around a non-ASCII-path defect** (section 5) |
| PyBaMM | **Not installed.** Deferred on purpose (section 6) |
| EPA cycles | UDDS, HWFET, US06 downloaded from epa.gov and validated |
| Preserved scripts | Both found and copied byte-for-byte |
| Installer side effects outside D: | Yes: three, listed in section 4. They were **not** undone |

## 2. Installation paths

| Component | Path |
|---|---|
| Verification interpreter | `D:\EURÉKA 2026 - KT\verification\python-env\Scripts\python.exe`, a venv whose base is the existing uv-managed `D:\EURÉKA 2026 - KT\tools\python\cpython-3.14.7-windows-x86_64-none` |
| FASTSim | `verification\python-env\Lib\site-packages\fastsim\` (compiled `fastsim.cp314-win_amd64.pyd`, vehicle and cycle data embedded in it) |
| OpenModelica | `D:\EURÉKA 2026 - KT\tools\OpenModelica\`, with `bin\omc.exe`, `bin\OMEdit.exe` (present, **not launched**), and bundled MSYS2/UCRT64 `tools\msys\ucrt64\bin\gcc.exe` |
| OpenModelica installer and checksum | `tools\downloads\openmodelica-1.27.1\` (1.5 GB) |
| OpenModelica per-user data (redirected) | `verification\omc-userdata\` (124 MB of cached Modelica libraries) |
| EPA originals | `data\raw\drive_cycles\epa\{uddscol,hwycol,us06col}.txt` and `_headers\` |
| EPA processed | `data\processed\drive_cycles\epa\` |
| Smoke-test outputs | `verification\fastsim-smoke\`, `verification\openmodelica-smoke\` |
| Logs | `verification\logs\` |

`uv` itself (0.12.15) is a pre-existing WinGet binary on C:. It was already installed, and I installed nothing there.

## 3. Versions and verification commands

| Package | Version | How verified |
|---|---|---|
| CPython | 3.14.7 | `uv venv … --python 3.14.7`, `pyvenv.cfg` |
| fastsim | 3.1.0 | `import fastsim`; `importlib.metadata`; `fastsim.__file__` is inside the new venv; Summary "Tool for modeling vehicle powertrains", homepage `https://www.nlr.gov/transportation/fastsim`; requires Python `>=3.10,<3.16` |
| numpy / pandas / polars / plotly / pyyaml | 2.5.4 / 3.1.0 / 1.44.2 / 6.9.0 / 6.0.3 | `uv pip freeze` → `verification\requirements-verification.txt` |
| pip | 26.2.2 | seeded by uv |
| OpenModelica `omc` | v1.27.1 (64-bit) | `omc.exe --version` |
| NSIS (installer engine) | 3.12 | byte signature in the installer |

Key commands (full outputs are in `verification\logs\`):

```
uv venv "D:\EURÉKA 2026 - KT\verification\python-env" --python 3.14.7 --no-config --seed
uv pip install --dry-run --python <venv python> --no-config fastsim     # resolved cleanly first
uv pip install --python <venv python> --no-config fastsim==3.1.0
uv pip check --python <venv python>                                      # "All installed packages are compatible"
OpenModelica-v1.27.1-64bit.exe /S /D=D:\EURÉKA 2026 - KT\tools\OpenModelica    # exit 0
omc.exe ..\test.mos                                                       # run from verification\openmodelica-smoke\out
```

Before each uv command, `project.env` was loaded into the process (so `UV_CACHE_DIR`, `UV_PYTHON_INSTALL_DIR`, `TEMP`
and `TMP` pointed at D:). `UV_PROJECT_ENVIRONMENT` was removed from the process and every command named the
target interpreter explicitly, so the locked `.venv` could not be targeted. `uv.lock` has the same SHA-256 as
at the start (`f830a6b3…bb8c0`).

Installer integrity: `OpenModelica-v1.27.1-64bit.exe` MD5 `d3852e01a89a49845e6be63a64462639` equals the published
`.md5sum`; SHA-256 `b7479c752e11648e7859341f986aa981a400ef3071e8e718101a8375037eaa8d`.

## 4. Where caches and data live, and what could not be on D:

**On D: (checked):** the interpreter, FASTSim, all package caches (`cache\uv`), temp files (`cache\tmp`), OpenModelica
program, its bundled compiler toolchain, its user library cache (`APPDATA`/`LOCALAPPDATA` were redirected for
the `omc` process), the Modelica build products and results, all downloaded data. C: free space was 7.7 GB before
the work and 7.68 GB after.

**Installer components that could not be placed on D: (observed by diffing before and after):**

| # | Change | Where it physically lives | Effect |
|---|---|---|---|
| 1 | `OPENMODELICAHOME` set as a **machine-wide** environment variable, value `D:\EURÉKA 2026 - KT\tools\OpenModelica\` | HKLM registry (C:) | Visible to every process started from now on, for all users |
| 2 | Add/Remove Programs entry `HKLM\SOFTWARE\WOW6432Node\…\Uninstall\OpenModelica…` | HKLM registry (C:) | Registers the uninstaller |
| 3 | Start Menu folder `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\OpenModelica` | C: | Shortcuts |

Not changed: the user and machine `PATH`, any user-level variable, `C:\Program Files`, `%APPDATA%\.openmodelica`.

Item 1 is a system setting. I did not choose it. The installer made it silently, and the uninstaller would
remove it. **I left all three in place** because undoing them means uninstalling, which was not authorised.
I also do not know how the registry writes succeeded: a separate PowerShell session reported
`IsInRole(Administrator) = False` shortly before the install, yet HKLM was written. The installer manifest asks for
"highestAvailable" rights.

Items 1-3 point at, but do not contain, the D: data. Decision for you: keep them, or run
`tools\OpenModelica\Uninstall.exe` and reinstall differently (see the readiness report).

## 5. OpenModelica minimal test

**Result: compiled and simulated successfully, but not with the project's real path.**

- `omc` starts and reports its version from the `É` path. When it initialises the compiler, though, it fails with
  *"We could not find some needed MINGW paths"*, although `tools\msys\ucrt64\bin\gcc.exe` exists. I tried
  `OPENMODELICAHOME` with and without a trailing backslash, and the 8.3 short path (this volume has no 8.3
  names, so the path was unchanged). All failed with the same message.
- Mapping the project root to an ASCII drive letter (`subst Y: "D:\EURÉKA 2026 - KT"`, then `OPENMODELICAHOME=Y:\tools\OpenModelica`,
  working directory `Y:\verification\openmodelica-smoke\out`) made the same run succeed: *"The simulation finished
  successfully"*, total 2.30 s.
- That identifies the non-ASCII path as the cause by an intervention, not by inspecting `omc`'s source.
  The `subst` mapping is session-level, and I **removed it** afterwards (`subst Y: /D`; `subst` lists nothing).
- Model: `verification\openmodelica-smoke\CoastDown.mo`, a library-free linear-drag coast-down m·v̇ = −c·v (m = 850 kg, c = 25 N·s/m, v₀ = 10 m/s),
  a smoke test only, not the project's vehicle model.
- Independent check: the saved `CoastDown_res.csv` (2002 rows, on D:, SHA-256 `501723fa…1273a`) was compared in Python with
  v₀·exp(−c·t/m): maximum absolute error 3.6×10⁻⁹ m/s (relative 5.1×10⁻¹⁰). Negative control: a deliberately wrong c = 26 gives
  0.129 m/s, so the check can fail. Results: `verification\openmodelica-smoke\openmodelica_smoke_results.json`.
- Library cache: `omc` unpacked the bundled Modelica libraries (3.2.3, 4.0.0, 4.1.0 and others) into
  `verification\omc-userdata\Roaming\.openmodelica\libraries\`. It also tried to download
  `https://libraries.openmodelica.org/index/v1/index.json` and timed out; this was harmless for the test, but it shows `omc` makes
  outbound network requests.
- OMEdit: `bin\OMEdit.exe` exists. It was not started, so the GUI is unverified.

## 6. FASTSim

**Result: passed its minimal EV check.** FASTSim is an independent powertrain and energy cross-check
(a backward-looking, cycle-following model). It is not an adaptive-LQR controller simulator, and nothing from it can stand in
for a fair controller comparison.

- Package identity checked (section 3). Bundled vehicles: 2012 Ford Fusion, 2016 Nissan Leaf 30 kWh, 2016 Toyota Prius Two,
  2020 Chevrolet Bolt EV, 2021 Hyundai Sonata Hybrid, 2022 Tesla Model 3 RWD, 2022 Renault Zoe ZE50 R135, 2026 Chrysler Pacifica Select.
  Bundled cycles: `hwfet.csv`, `udds.csv` only (no US06).
- Data and outputs: vehicle and cycle data are embedded in the compiled extension, and nothing was downloaded at run time.
  Outputs were written only under `verification\fastsim-smoke\`.
- Run (`verification\scripts\fastsim_smoke.py`): Renault Zoe ZE50 on UDDS and HWFET.

| Cycle | Rows | Distance | Battery chemical energy | Wh/km | Own ledger closure |
|---|---|---|---|---|---|
| UDDS | 1370 | 11.990 km | 1393.4 Wh | 116.2 | 1.1×10⁻¹⁵ |
| HWFET | 766 | 16.507 km | 2288.4 Wh | 138.6 | 1.1×10⁻¹⁵ |

- "Own ledger closure" means tractive energy against the sum of drag, rolling, acceleration, grade and wheel-inertia terms inside FASTSim.
  It is an internal consistency check, not validation against a measured vehicle.
- The first run reported `all_finite = false`. Cause: one non-finite cell per file (`veh.history.mass_kilograms`, first row);
  none of the columns used in the check.
- These Wh/km values belong to a Zoe preset. They must not be compared with the project's 49.9 Wh/km, which is for a different
  hypothetical vehicle.

## 7. PyBaMM (conditional): deferred

The project does not specify enough to run a defensible battery study: chemistry is only "LFP" at pack level
(48 V / 100 Ah, no cell), there are no degradation parameters (`docs/optional-components.md`: PyBaMM's only built-in LFP set,
Prada2013, has none), the SoH-to-resistance law (`k_r0 = 0.5`, `k_r1 = 0.3`) is unsourced, and
temperature is only an assumption (25 °C in `docs/model.md`). Installing a simulator would not support any capacity-fade claim.

## 8. EPA drive-cycle data

Source page `https://www.epa.gov/vehicle-and-fuel-emissions-testing/dynamometer-drive-schedules` (page states last update June 22, 2026).
All three downloads returned HTTP 200 on the first attempt; no substitute site was used.

| Cycle | File | Rows | Duration | Original SHA-256 | Validation |
|---|---|---|---|---|---|
| UDDS | `uddscol.txt` | 1370 | 1369 s | `cc9f3edf…687b6` | passed; trapezoid distance 7.4504 mi (11.9902 km) |
| HWFET | `hwycol.txt` | 766 | 765 s | `e48e278a…fb3e10a` | passed; 10.2567 mi (16.5065 km) |
| US06 | `us06col.txt` | 601 | 600 s | `84e9d8cc…725ad2` | passed; 8.0080 mi (12.8876 km) |

(Complete hashes, URLs, transformation and processed-file hashes are in `audit\external-data-provenance.csv`.)

- Checks: no malformed rows, no NaN or Inf, time 0..N s strictly increasing in exact 1 s steps, starts and ends at rest, header declares secs and mph.
  The EPA page does not state units or resolution; they come from the file header and the validated data.
- Originals are unchanged (hash recomputed after processing). The processed CSVs add `speed_m_per_s = mph × 0.44704` (exact definition).
- Independent cross-check: UDDS and HWFET speed traces equal FASTSim's separately packaged cycles (same length, same time axis,
  max difference 4.3×10⁻⁴ m/s). US06 has no second source, so it was validated by internal checks only. The US06 header line has a stray
  quotation mark and trailing tab; no row is affected.
- These are EPA reference schedules, not measured traffic and not Vietnamese traffic. They were **not** used in any controller experiment.

## 9. Preserved scripts

`ind_checks_a.py` (SHA-256 `c5cad625019ecceb3f352c63574c51d93f928f7018709e2e7cc846a8a57fd0db`) and `ind_checks_b.py`
(`5e98b430deefbf4977e8f9d594b362abc2cc8df35583c4c36c8fe61135ff2080`) both existed at the two named paths and were copied to
`audit\technical-verification\` with identical hashes. Details, run order and what is not preserved: `audit\technical-verification\README.md`.

## 10. Departures from the instructions, and other things you should know

1. **Two directory listings outside the project root** during a pre-install check: the top level of `D:\` (`ls /d | grep -c openmodelica`)
   and `C:\Program Files` (`ls … | grep -i openmodelica`). Both returned only "no match". They went against the "no scanning D:" and
   "nothing outside the root" rules.
2. **Deliberate reads outside the root for the installer audit:** registry keys and environment variables, and `Test-Path` on specific `C:` paths
   (before and after install). They changed nothing.
3. **Machine-wide changes made by the installer** (section 4). I could not avoid them in a silent install, and I did not undo them.
4. **A temporary `subst Y:` mapping** was created and removed (section 5).
5. **`omc` attempted one outbound request** to libraries.openmodelica.org (timed out).
6. **Process-level environment only:** `OPENMODELICAHOME`, `APPDATA`, `LOCALAPPDATA` and `TEMP` were set per process for `omc` runs, never persistently.
7. Mistakes in my own steps: a first `New-Item -LiteralPath` call failed under PowerShell 5.1, so the script copy was repeated with `-Path` (nothing was
   written by the failed call); two non-ASCII print errors in throwaway Python commands.
8. Git hygiene: `verification\python-env` is safe, since uv wrote a `.gitignore` containing `*` inside it. `verification\omc-userdata`
   (9,763 files, 124 MB of cached Modelica libraries) is **untracked and not ignored**, and `verification\openmodelica-smoke\out`
   holds about 60 generated build files. A careless `git add .` would stage them. I did not edit `.gitignore`.
   (An earlier draft of this report wrongly named `python-env` as the unignored folder.)
