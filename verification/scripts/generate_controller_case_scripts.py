"""Generate the OpenModelica .mos scripts and the case table for the controller cross-check.

usage: python generate_controller_case_scripts.py <project root> <stage> [--solver S --tol T]
stages: step      piecewise-constant input tests of the controller (original reconstructed failing test + defined-semantics test)
        unit      ControllerUnit (controller logic with prescribed inputs; no plant, no profile)
        ptune     solver x tolerance ladder on P-TUNE (fixed and scheduled, SoH 0.8): the solver-selection study of the protocol
        primary   S-A grid (S1, S2 x fixed, scheduled x SoH 1.0, 0.9, 0.8, 0.7) at the selected --solver/--tol
        sens      numerical-sensitivity runs on S1 and S2 (SoH 0.8): tightened tolerance and the other solvers, at the selected --solver/--tol
Case metadata are appended to verification/modelica/scripts/controller_cases.json. All paths inside the .mos files are relative to
verification/modelica-build, the working directory the launcher uses.  Stop time = steps*Ts, output grid = Ts (the control grid).
"""
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
stage = sys.argv[2]
opt = dict(zip(sys.argv[3::2], sys.argv[4::2]))
TS = 0.01
STEPS = {"PTUNE": 12231, "S1": 32491, "S2": 21328}  # round(duration/Ts), from eureka.cycles (checked in the protocol)
FILT = ("^(time|v|v_ref|T|T_ref|T_lim|T_cmd|a|F_fb|F_net|I|P_batt|P_e|P_m|SoC|V1|E_chem|E_rr|E_aero|E_fb|E_gear|E_visc|E_mi|E_R0|E_R1|E_regen|dist|Ah|closure"
        "|ctrl\\\\.u|ctrl\\\\.z|ctrl\\\\.z_used|ctrl\\\\.e_k|ctrl\\\\.T_lim_k|ctrl\\\\.sat_k|ctrl\\\\.k_ctrl|ctrl\\\\.se2)$")
SCRIPTS = root / "verification/modelica/scripts"
CASES_FILE = SCRIPTS / "controller_cases.json"
cases = json.loads(CASES_FILE.read_text(encoding="utf-8")) if CASES_FILE.exists() else {}
LOAD = ['setCommandLineOptions("--unitChecking"); getErrorString();', 'loadFile("../modelica/EurekaPlant/package.mo"); getErrorString();',
        'loadFile("../modelica/EurekaController/package.mo"); getErrorString();', 'mkdir("cases_ctl"); getErrorString();']


def sim(case, model, stop, n, solver, tol, stage_name, filt=FILT, stats=False):
    cases[case] = {"stage": stage_name, "model": model, "stop_time": stop, "intervals": n, "solver": solver, "tolerance": tol,
                   "result_file": f"verification/modelica-build/cases_ctl/{case}/{case}_res.csv", "simflags": "-lv=LOG_STATS" if stats else ""}
    flt = f', variableFilter = "{filt}"' if filt else ""
    return [f'mkdir("cases_ctl/{case}"); cd("cases_ctl/{case}");',
            f'simulate({model}, startTime = 0, stopTime = {stop!r}, numberOfIntervals = {n}, tolerance = {tol!r}, method = "{solver}", '
            f'outputFormat = "csv", fileNamePrefix = "{case}"{flt}, simflags = "{cases[case]["simflags"]}"); getErrorString();', 'cd("../..");']


lines = list(LOAD)
if stage == "unit":
    lines += sim("U_unit", "EurekaController.Tests.ControllerUnit", 10.0, 1000, "dassl", 1e-10, "unit", filt="")
    name = "70_controller_unit"
elif stage == "step":
    lines += sim("U_step_original", "EurekaController.Tests.ControllerUnitStepOriginal", 10.0, 1000, "dassl", 1e-10, "step", filt="")
    lines += sim("U_step_semantics", "EurekaController.Tests.ControllerStepSemantics", 12.0, 1200, "dassl", 1e-10, "step", filt="")
    name = "75_controller_step_inputs"
elif stage == "ptune":
    for solver in ("dassl", "cvode", "ida"):
        for tol in (1e-6, 1e-8, 1e-10, 1e-12):
            for kind in ("fixed", "scheduled"):
                lines += sim(f"PT_{kind}_{solver}_tol{tol:g}", f"EurekaController.Cases.PTUNE_{kind}_soh080", STEPS["PTUNE"] * TS, STEPS["PTUNE"], solver, tol, "ptune")
    name = "80_ptune_convergence"
elif stage == "primary":
    solver, tol = opt["--solver"], float(opt["--tol"])
    for prof in ("S1", "S2"):
        for soh in (1.0, 0.9, 0.8, 0.7):
            for kind in ("fixed", "scheduled"):
                c = f"{prof}_{kind}_soh{round(soh * 100):03d}"
                lines += sim(f"A_{c}", f"EurekaController.Cases.{c}", STEPS[prof] * TS, STEPS[prof], solver, tol, "primary", stats=True)
    name = "90_primary_grid"
elif stage == "sens":
    solver, tol = opt["--solver"], float(opt["--tol"])
    variants = [(solver, float(f"{tol * 100.0:.6g}")), (solver, float(f"{tol * 1e4:.6g}"))]  # protocol amendment A3: DASSL at 100x and 1e4x the selected tolerance (CVODE/IDA are inadmissible)
    for prof in ("S1", "S2"):
        for kind in ("fixed", "scheduled"):
            for s, t in variants:
                c = f"{prof}_{kind}_soh080"
                lines += sim(f"N_{c}_{s}_tol{t:g}", f"EurekaController.Cases.{c}", STEPS[prof] * TS, STEPS[prof], s, t, "sens")
    name = "95_numerical_sensitivity"
else:
    raise SystemExit("unknown stage")
(SCRIPTS / f"{name}.mos").write_text("\n".join(lines) + "\n", encoding="ascii")
CASES_FILE.write_text(json.dumps(cases, indent=1), encoding="utf-8")
print(name, "->", sum(1 for c in cases.values() if c["stage"] == stage), "cases")
