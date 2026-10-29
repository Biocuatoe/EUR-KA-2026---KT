# Verification readiness: what the toolchain can and cannot yet check

- **Date:** 2026-10-23
- **Companion:** `audit\toolchain-installation-report.md` (what was installed and how it was verified)
- **Status:** the tools run, but the independent-model phase has **blockers that need your decisions** (section 2). No existing result, verdict or file was altered, and the independent vehicle model has not been started.

## 1. What is ready

| Capability | State | Evidence |
|---|---|---|
| Separate Python environment for verification tools | Ready | `verification\python-env`; locked `.venv` and `uv.lock` untouched |
| FASTSim 3.1.0 energy cross-check | Ready for **bundled** vehicles | Zoe on UDDS/HWFET ran; own ledger closes to 1e-15 |
| OpenModelica 1.27.1 compile and simulate | Ready **only through an ASCII path alias** | Coast-down matched the closed form to 3.6e-9 m/s |
| Authoritative cycles | UDDS, HWFET, US06 validated | `audit\external-data-provenance.csv` |
| Preserved audit scripts | Preserved (not rerun) | `audit\technical-verification\` |
| Battery/ageing simulator | Deliberately absent | PyBaMM deferred (no cell, no degradation data) |

## 2. Blockers and decisions needed

**B1. OpenModelica cannot compile from the project's real path.** `omc` fails at start-up with a "MINGW paths not found" error
whenever its install path contains `É`, though the compiler is present. A temporary drive-letter alias fixes it (`subst Y: "D:\EURÉKA 2026 - KT"`,
then use `Y:\…` for `OPENMODELICAHOME`, the working directory and all model paths). The alias is lost at logoff and has to be recreated each session.
Options, none taken yet:
(a) keep the alias and script it (no file changes; a per-session system mapping);
(b) reinstall OpenModelica to an ASCII path, which would be outside the project root, so needs your approval;
(c) rename the project folder: not proposed, since it breaks the path conventions recorded in the project.
Whichever you choose, generated models and results must be created through the ASCII path too.

**B2. The installer made machine-wide changes** (`OPENMODELICAHOME` in the HKLM environment, an uninstall entry, Start Menu shortcuts).
They are harmless to the study but they are system state outside the project. Keep, or uninstall with `tools\OpenModelica\Uninstall.exe` (which
also removes the 8.9 GB program) and reinstall under your chosen option for B1.

**B3. The project's hypothetical vehicle cannot follow all EPA schedules.** From `verification\scripts\cycle_feasibility_check.py`
(output in `verification\logs\cycle-feasibility.txt`; indicative, constant efficiencies, crude acceleration estimate):

| Cycle | Peak speed | Peak accel | Samples where required force exceeds available | Peak shaft power vs 18 kW |
|---|---|---|---|---|
| UDDS | 91.2 km/h | 1.48 m/s² | 2 of 1370 (0.1 %) | ≈ 19.9 kW |
| HWFET | 96.4 km/h | 1.43 m/s² | 0 of 766 | ≈ 16.2 kW |
| US06 | 129.2 km/h | 3.24 m/s² | **171 of 601 (28.5 %)** | ≈ 44.4 kW |

The vehicle's maximum acceleration is about 2.18 m/s² before road loads. US06 therefore cannot be followed (both for acceleration and power), UDDS is marginal for
two samples, and HWFET is feasible. The study's own profiles stop at 50 km/h (S1) and 25 km/h (S2), and its linear design point is 30 km/h, so every EPA cycle
lies partly or wholly outside the documented operating domain. Using them for the controller comparison would be a new, dated deviation to the locked preregistration,
with a re-justified design point, and it would exercise actuator saturation for the first time.

**B4. FASTSim has no model of the project's vehicle yet.** The bundled vehicles are real-vehicle presets. Building one from `configs/parameters.yaml`
(850 kg, C_d·A_f = 0.77 m², C_rr 0.008, G = 6.5, constant efficiencies 0.9702 and 0.874) has not been attempted, and how well FASTSim's efficiency-map structure
can reproduce constant efficiencies is untested. Until then, FASTSim numbers are about the Zoe preset only.

**B5. No independent implementation of the plant or controller exists.** This setup phase wrote none, as instructed.

## 3. What each tool can legitimately show

- **Modelica (once B1 is settled):** a second, independently coded implementation of the plant and the two LQR controllers, in a different
  language, with a different solver and a different discretisation path. That is the only tool here that can test the **controller comparison**
  (ΔE = +0.003 %, H_C, S-D). It should take its parameters from `configs/parameters.yaml` but its equations from `docs/model.md` and the audit's
  re-derivations, not from `src/eureka`.
- **FASTSim:** a cycle-following ("backward") powertrain energy model. Given a speed trace it computes the energy needed, so it can cross-check the
  **trajectory-determined energy** (the audit's ideal-tracking value, 49.714 Wh/km on S1 at SoH 1) for a matched vehicle. It cannot show anything about LQR,
  SoH scheduling, tracking error or saturation, and agreement would not validate the result against a real vehicle.
- **EPA cycles:** reference schedules for standardised comparison, not measured or Vietnamese traffic. See B3 before any use.

## 4. Other unmet prerequisites

1. Parameters are still all `report_unverified` or `assumed`, and no real vehicle or measured efficiency map exists, so even a perfect independent
   re-implementation checks the **model's** internal consistency, not physical truth.
2. No second source for the US06 trace (not bundled in FASTSim).
3. OMEdit (GUI) was not launched.
4. OpenModelica makes outbound network requests for its package index. It runs offline using the cached libraries, but this may matter on a restricted network.
5. The preserved audit scripts have not been rerun at the current commit.

## 5. Exact next steps for the independent-model phase

1. **Decide B1 and B2** (alias, reinstall to an ASCII path, or other). If the alias is kept, write a small script that creates it, sets the `omc` environment and removes it.
2. **Decide whether EPA cycles will be used at all**, and if so as a separate, dated deviation (B3). Without that decision, keep S1/S2 and the preregistered domain.
3. **Specify the Modelica model on paper first**, from `docs/model.md` and the audit's derivations: states, equations, limits, battery, energy ledger. Include a
   Modelica-side energy closure and the closed-form coast-down and equilibrium checks already used (IC-01).
4. **Implement the plant alone**, then reproduce the hand-computed equilibrium torques (3.74, 4.61, 7.32 N·m at 20, 30, 50 km/h) and the ideal-tracking energy of
   49.714 / 49.803 / 36.951 / 36.990 Wh/km (IC-11) with no controller.
5. **Implement both controllers with gains computed outside the project code** (the preserved `ind_checks_a.py` DARE routine is one route), then compare with the
   saved S1/S2 results (ΔE +0.003 %, RMSE ratio 1.011) as a check, without tuning anything to match.
6. **Build the matched FASTSim vehicle** (B4) and compare trajectory-determined energy only.
7. Record every comparison with its tolerance **before** looking at the result, and report disagreements as findings.
8. Only then consider a saturating-profile or noise-on/off experiment, each as an approved, dated deviation.

## 6. Git status at the end of this phase

See the final summary: untracked `audit/`, `verification/`, `technical-claim-matrix.csv`, `technical-foundation-audit.md`. `tools/`, `data/` and `cache/` are
git-ignored. No tracked file was modified, and nothing was committed.
