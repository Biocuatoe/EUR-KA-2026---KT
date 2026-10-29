"""Generate the OpenModelica .mos scripts for every verification case.

Initial conditions and durations come from verification/references/hand_references.json (written by
hand_references.py), never typed by hand. All paths in the scripts are RELATIVE to verification/modelica-build,
the working directory the launcher uses, so the scripts do not depend on the alias drive letter.
Also writes verification/modelica/scripts/cases.json describing every case (model, overrides, tolerance, grid).
"""
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
ref = json.loads((root / "verification/references/hand_references.json").read_text(encoding="utf-8"))
out = root / "verification/modelica/scripts"
out.mkdir(parents=True, exist_ok=True)
LOAD = 'loadFile("../modelica/EurekaPlant/package.mo"); getErrorString();'
CASES = {}


def sim(script, case, model, stop, n, tol, overrides=None, filt=None, stats=False, extra_load=None):
    ov = ",".join(f"{k}={v!r}" for k, v in (overrides or {}).items())
    flags = []
    if ov:
        flags.append(f"-override={ov}")
    if stats:
        flags.append("-lv=LOG_STATS")
    CASES[case] = {"script": script, "model": model, "stop_time": stop, "intervals": n, "tolerance": tol, "overrides": overrides or {},
                   "result_file": f"verification/modelica-build/cases/{case}/{case}_res.csv", "simflags": " ".join(flags)}
    lines = [f'mkdir("cases/{case}"); cd("cases/{case}");']
    flt = f', variableFilter = "{filt}"' if filt else ""
    lines.append(f'simulate({model}, startTime = 0, stopTime = {stop!r}, numberOfIntervals = {n}, tolerance = {tol!r}, method = "dassl", '
                 f'outputFormat = "csv", fileNamePrefix = "{case}"{flt}, simflags = "{" ".join(flags)}"); getErrorString();')
    lines.append('cd("../..");')
    return lines


scripts = {}

# ---- 10: static points (B1 equilibrium, B2 instantaneous, B3 limits) + negative control
s = [LOAD, 'mkdir("cases"); getErrorString();']
for kmh in (20, 30, 50):
    e = ref["equilibrium"][f"{kmh}kmh"]
    s += sim("10_static", f"B1_eq_{kmh}kmh", "EurekaPlant.Tests.StaticPoint", 1.0, 100, 1e-10,
             {"v_init": e["v_m_s"], "T_init": e["T_eq_Nm"], "T_hold": e["T_eq_Nm"]})
for name, p in ref["instantaneous_points"].items():
    s += sim("10_static", f"B2_{name}", "EurekaPlant.Tests.StaticPoint", 0.01, 1, 1e-10, {"v_init": p["v"], "T_init": p["T"], "T_hold": p["T"]})
s += sim("10_static", "B3_limit_v13", "EurekaPlant.Tests.StaticPoint", 0.01, 1, 1e-10, {"v_init": 13.0, "T_init": 0.0, "T_hold": 1000.0})
s += sim("10_static", "B3_limit_v2", "EurekaPlant.Tests.StaticPoint", 0.01, 1, 1e-10, {"v_init": 2.0, "T_init": 0.0, "T_hold": 1000.0})
e = ref["equilibrium"]["30kmh"]   # negative control: wrong gear efficiency (0.98 instead of 0.9702) at the 30 km/h equilibrium
s += sim("10_static", "E_B1_eq_30kmh_wrong_eta_g", "EurekaPlant.Tests.StaticPoint", 1.0, 100, 1e-10,
         {"v_init": e["v_m_s"], "T_init": e["T_eq_Nm"], "T_hold": e["T_eq_Nm"], "eta_g": 0.98})
scripts["10_static"] = s

# ---- 20: coast-down
cd = ref["coastdown"]
s = [LOAD, 'loadFile("../openmodelica-smoke/CoastDown.mo"); getErrorString();', 'loadFile("../modelica/negative_fixtures/NegativeFixtures.mo"); getErrorString();',
     'mkdir("cases"); getErrorString();']
s += sim("20_coastdown", "C1_toy_linear_drag", "CoastDown", 20.0, 2000, 1e-10)
for tol in (1e-6, 1e-8, 1e-10, 1e-12):
    s += sim("20_coastdown", f"C2_project_tol{tol:g}", "EurekaPlant.Tests.CoastDown", cd["t_end"], 2000, tol,
             filt="^(time|v|omega|F_w|F_rr|F_aero|F_net|a|T|closure)$")
s += sim("20_coastdown", "E_C2_wrong_branch_fixture", "NegCoastDownWrongBranch", cd["t_end"], 2000, 1e-10)
s += sim("20_coastdown", "E_C2_Crr_plus1pct", "EurekaPlant.Tests.CoastDown", cd["t_end"], 2000, 1e-10, {"C_rr": 0.008 * 1.01},
         filt="^(time|v)$")
scripts["20_coastdown"] = s

# ---- 30: ideal tracking energy (D) + negative controls
s = [LOAD, 'mkdir("cases"); getErrorString();']
FILT = "^(time|v_ref|a_ref|E_chem|E_rr|E_aero|E_gear|E_visc|E_mi|E_R0|E_R1|dist|V1|closure|Wh_per_km|limit_margin|T|I|F_req)$"
for prof, key in (("S1", "InverseS1"), ("S2", "InverseS2")):
    dur = ref["profiles"][prof]["duration_s"]
    for soh in (1.0, 0.8):
        s += sim("30_ideal", f"D_{prof}_soh{soh}", f"EurekaPlant.{key}", dur, int(round(dur / 0.02)), 1e-10, {"SoH": soh}, filt=FILT, stats=True)
dur = ref["profiles"]["S1"]["duration_s"]
s += sim("30_ideal", "E_D_S1_soh1.0_Cd_plus1pct", "EurekaPlant.InverseS1", dur, int(round(dur / 0.02)), 1e-10, {"C_d": 0.35 * 1.01}, filt=FILT)
s += sim("30_ideal", "E_D_S1_soh1.0_etami_plus1pct", "EurekaPlant.InverseS1", dur, int(round(dur / 0.02)), 1e-10, {"eta_mi": 0.874 * 1.01}, filt=FILT)
scripts["30_ideal"] = s

# ---- 40: forward open-loop trajectory (F1)
s = [LOAD, 'mkdir("cases"); getErrorString();']
for tol in (1e-8, 1e-10, 1e-12):
    s += sim("40_openloop", f"F1_openloop66_tol{tol:g}", "EurekaPlant.Tests.OpenLoop66", 66.0, 6600, tol, stats=(tol == 1e-10))
s += sim("40_openloop", "E_F1_openloop66_Crr_plus1pct", "EurekaPlant.Tests.OpenLoop66", 66.0, 6600, 1e-10, {"C_rr": 0.008 * 1.01})
scripts["40_openloop"] = s

# ---- 50: unit checking negative controls
scripts["50_unit_negative"] = ['setCommandLineOptions("--unitChecking"); getErrorString();', LOAD,
                               'loadFile("../modelica/negative_fixtures/NegativeFixtures.mo"); getErrorString();',
                               'checkModel(WrongUnitForce); getErrorString();', 'checkModel(WrongTractionUnits); getErrorString();',
                               'checkModel(NegCoastDownWrongBranch); getErrorString();']
for nm, lines in scripts.items():
    (out / f"{nm}.mos").write_text("\n".join(lines) + "\n", encoding="ascii")
(out / "cases.json").write_text(json.dumps(CASES, indent=2), encoding="utf-8")
print(len(CASES), "simulation cases;", ", ".join(f"{k}.mos ({len(v)} lines)" for k, v in scripts.items()))
