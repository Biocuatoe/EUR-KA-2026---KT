"""Evaluate the Modelica plant against the analytic references and the Python plant.

Applies the pass criteria of verification/modelica-plant-specification.md section 10, fixed BEFORE any result existed
(the tolerance table below is copied from there). Reads only saved files: Modelica result CSVs, hand_references.json,
the Python-plant reference CSVs, the reference-scheme convergence JSON and the launcher logs. Calls no plant code.

Writes verification/modelica-check-results.csv, verification/cross-implementation-comparison.csv and
verification/modelica-build/check_summary.json.   usage: python modelica_checks.py <project root>
"""
import csv
import glob
import hashlib
import json
import math
import pathlib
import re
import sys

import numpy as np
import pandas as pd

root = pathlib.Path(sys.argv[1])
VER = root / "verification"
BUILD = VER / "modelica-build"
sha = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
rel = lambda p: str(pathlib.Path(p).resolve().relative_to(root.resolve())).replace("\\", "/")

# ---- tolerances: copied from the specification, section 10 (do not edit after seeing results)
TOL = {
    "B1_accel": 1e-9, "B1_Fnet": 1e-6, "B1_v": 1e-9, "B2_rel": 1e-9, "B3_rel": 1e-9,
    "C1_floor": 1e-7, "C1_repro_frac": 0.20, "C2_abs": 1e-7,
    "D1_rel": 1e-7, "D2_rel": 1e-7, "D3_rel": 3e-4,
    "F1": {"v": 1e-5, "T": 1e-4, "V1": 1e-6, "SoC": 1e-8, "dist": 1e-4, "F": 5e-3, "a": 1e-5, "P": 0.1, "I": 5e-3, "E_rel": 1e-6, "E_floor": 1e-3},
    "E_factor": 10.0,
}
SWITCH_T = [10.0, 20.0, 30.0, 38.0, 46.0, 56.0]

model_files = sorted(glob.glob(str(VER / "modelica/EurekaPlant/**/*.mo"), recursive=True))
MODEL_SHA = hashlib.sha256("".join(sha(f) for f in model_files).encode()).hexdigest()[:16]
MODEL_VER = "EurekaPlant 0.1.1 (sources sha256-of-hashes " + MODEL_SHA + ")"
PARAM_SRC = "configs/parameters.yaml sha256 " + sha(root / "configs/parameters.yaml")[:16] + " via verification/modelica/generated_inputs.json"

ref = json.loads((VER / "references/hand_references.json").read_text(encoding="utf-8"))
cases = json.loads((VER / "modelica/scripts/cases.json").read_text(encoding="utf-8"))
conv = json.loads((VER / "references/ideal_reference_convergence.json").read_text(encoding="utf-8"))


def latest(pattern):
    fs = sorted(glob.glob(str(BUILD / "logs" / pattern)))
    return fs[-1]


launcher = json.loads(open(latest("*-v011-launcher.json"), encoding="utf-8-sig").read())
step_exit = {s["name"]: s["exit_code"] for s in launcher["steps"]}
solver_launcher = json.loads(open(latest("*-diagsolvers-launcher.json"), encoding="utf-8-sig").read())
solver_exit = {s["name"]: s["exit_code"] for s in solver_launcher["steps"]}


def load(case):
    p = root / cases[case]["result_file"]
    df = pd.read_csv(p)
    return df, p


def command_for(case):
    c = cases[case]
    return (f"powershell -File verification\\Invoke-OpenModelica.ps1 -Mos verification\\modelica\\scripts\\{c['script']}.mos  [simulate({c['model']}, "
            f"stopTime={c['stop_time']}, numberOfIntervals={c['intervals']}, tolerance={c['tolerance']}, dassl, simflags='{c['simflags']}')]")


RESULTS = []
_LOGS = {}


def sim_status(case):
    """omc exits 0 even when a simulation fails, so read the simulation record itself."""
    logs = glob.glob(str(BUILD / "logs" / "*-v011-*.out.txt")) + glob.glob(str(BUILD / "logs" / "*-diagsolvers-*.out.txt"))
    for lp in logs:
        if lp not in _LOGS:
            _LOGS[lp] = open(lp, encoding="utf-8", errors="replace").read()
        for blk in re.split(r"(?m)^record SimulationResult", _LOGS[lp])[1:]:
            if f"fileNamePrefix = '{case}'" in blk:
                return "finished successfully" if "The simulation finished successfully" in blk else "FAILED (see log)"
    return "no record found"


def add(check_id, description, status, metric, value, reference, abs_err, rel_err, tolerance, justification, case=None, notes="", artifact=None, exit_code=None):
    art = artifact if artifact else (root / cases[case]["result_file"] if case else None)
    RESULTS.append({
        "simulation_status": sim_status(case) if case else "",
        "check_id": check_id, "description": description, "status": status, "metric": metric, "value": value, "reference": reference,
        "abs_error": abs_err, "rel_error": rel_err, "tolerance": tolerance, "tolerance_justification": justification,
        "model_version": MODEL_VER, "parameters": PARAM_SRC,
        "source_data": ("configs/parameters.yaml; " + ("configs/cycles/profiles.yaml; " if check_id.startswith(("D", "E_D")) else "") + "verification/references/hand_references.json"),
        "command": command_for(case) if case else "verification/scripts/modelica_checks.py",
        "exit_code": (step_exit.get(cases[case]["script"]) if case and exit_code is None else exit_code),
        "artifact_path": rel(art) if art else "", "artifact_sha256": sha(art) if art and pathlib.Path(art).exists() else "", "notes": notes})


def ok(cond):
    return "PASS" if cond else "FAIL"


# =============================================================== A. structural / unit checks
chk = (latest("*-v011-00_check_models.out.txt"))
t = open(chk, encoding="utf-8").read()
eq = re.findall(r"has (\d+) equation\(s\) and (\d+) variable\(s\)", t)
n_ok = all(a == b for a, b in eq) and len(eq) == 5
warn = len(re.findall(r"Warning", t))
add("A1", "authoritative models compile with unit checking on; equations equal variables; no unit warning", ok(n_ok and warn == 0), "models checked / unit warnings",
    f"{len(eq)} models, equation=variable counts {[a + '=' + b for a, b in eq]}, warnings {warn}", "5 models, 0 warnings", "", "", "no unit warning", "omc --unitChecking",
    artifact=chk, exit_code=step_exit["00_check_models"],
    notes="Limit: the two equations containing the bare literal 3600 (der(Ah), der(SoC)) pass omc's checker because a numeric literal is accepted as any unit; the 3600 s/h factor is confirmed instead by the Pint check in verification/references/spec_derivation_checks.txt")
un = latest("*-v011-50_unit_negative.out.txt")
tu = open(un, encoding="utf-8").read()
det = {n: ("INCONSISTENT due to specified unit information" in seg) for n, seg in
       ((n, tu.split("Check of " + n)[1].split("Check of")[0] if ("Check of " + n) in tu else "") for n in ("WrongUnitForce", "WrongTractionUnits", "WrongUnitChargeIntegral", "NegCoastDownWrongBranch"))}
flagged = [n for n in ("WrongUnitForce", "WrongTractionUnits", "WrongUnitChargeIntegral") if det[n]]
add("E_A1", "negative controls for the unit check: three wrong-unit fixtures must be flagged; the physics-direction fixture is not a unit error and must not be",
    ok(len(flagged) == 3 and not det["NegCoastDownWrongBranch"]), "fixtures flagged", f"flagged {flagged}; NegCoastDownWrongBranch flagged={det['NegCoastDownWrongBranch']}",
    "3 flagged, wrong-branch fixture not flagged", "", "", "all detected", "the unit check can fail, so the clean A1 result is meaningful",
    artifact=un, exit_code=step_exit["50_unit_negative"])

# ---- A3: the values in the generated Modelica parameter file equal the YAML (transcription and staleness)
import yaml as _yaml
_cfg = _yaml.safe_load((root / "configs/parameters.yaml").read_text(encoding="utf-8"))
_gen = json.loads((VER / "modelica/generated_inputs.json").read_text(encoding="utf-8"))
_mo = (VER / "modelica/EurekaPlant/Parameters.mo").read_text(encoding="ascii")
_bad = []
for _name, _info in _gen["parameters"].items():
    _g, _k = _info["yaml_key"].split(".")
    _m = re.search(r"parameter Real " + re.escape(_name) + r"\(unit = \"[^\"]*\"\) = ([^ ]+) ", _mo)
    if not _m or float(_m.group(1)) != float(_cfg[_g][_k]["value"]):
        _bad.append(_name)
_stale = [f for f, h in _gen["sources"].items() if sha(root / f) != h]
add("A3", "every parameter in Parameters.mo equals configs/parameters.yaml, and the generated inputs are not stale", ok(not _bad and not _stale), "mismatching parameters; stale sources",
    f"{len(_gen['parameters']) - len(_bad)} of {len(_gen['parameters'])} equal; stale sources: {_stale or 'none'}", "all equal", "", "", "exact equality", "values are copied by a generator that reads the YAML",
    artifact=VER / "modelica/EurekaPlant/Parameters.mo", exit_code=0, notes="mismatches: " + (str(_bad) if _bad else "none"))

# =============================================================== B1 equilibrium
for kmh in (20, 30, 50):
    case = f"B1_eq_{kmh}kmh"
    df, p = load(case)
    e = ref["equilibrium"][f"{kmh}kmh"]
    amax, fmax = df["a"].abs().max(), df["F_net"].abs().max()
    dv = abs(df["v"].iloc[-1] - e["v_m_s"])
    f_tot = (df["F_rr"] + df["F_aero"]).iloc[0]
    add(f"B1_{kmh}", f"equilibrium at {kmh} km/h from (v_eq, T_eq): acceleration, net force, speed drift over 1 s",
        ok(amax <= TOL["B1_accel"] and fmax <= TOL["B1_Fnet"] and dv <= TOL["B1_v"]), "max|a| [m/s2]; max|F_net| [N]; |v(1)-v_eq| [m/s]",
        f"{amax:.3e}; {fmax:.3e}; {dv:.3e}", "0; 0; 0 (hand-calculated T_eq = %.9f N m)" % e["T_eq_Nm"], f"{amax:.3e}", "",
        f"a {TOL['B1_accel']:g}; F_net {TOL['B1_Fnet']:g}; v {TOL['B1_v']:g}", "double-precision round-off of a balance of terms of size ~100 N, DASSL tolerance 1e-10", case=case,
        notes=f"road load F_rr+F_aero in the model = {f_tot:.9f} N against hand value {e['F_total_N']:.9f} N (relative difference {abs(f_tot - e['F_total_N']) / e['F_total_N']:.2e})")

# =============================================================== B2 instantaneous points (t = 0 row)
MAP = {"F_w": "F_w", "F_rr": "F_rr", "F_aero": "F_aero", "F_fb": "F_fb", "F_net": "net_force_N", "a": "accel_m_s2", "P_m": "P_mech_W", "P_e": "P_elec_W", "I": "I_A"}
for name, pt in ref["instantaneous_points"].items():
    case = f"B2_{name}"
    df, p = load(case)
    r0 = df.iloc[0]
    # relative error; where the hand value is exactly zero (friction brake inactive) the absolute error is used
    errs = {k: (abs(r0[k] - pt[h]) / abs(pt[h]) if pt[h] != 0 else abs(r0[k])) for k, h in MAP.items()}
    worst = max(errs, key=errs.get)
    add(f"B2_{name}", f"instantaneous values at (v={pt['v']}, T={pt['T']}) against hand calculation", ok(errs[worst] <= TOL["B2_rel"]),
        "max relative error over F_w, F_rr, F_aero, F_net, a, P_m, P_e, I", f"{errs[worst]:.3e} ({worst})", "hand_references.json instantaneous_points", "", f"{errs[worst]:.3e}",
        TOL["B2_rel"], "same formulas evaluated in double precision; CSV carries 16 digits", case=case,
        notes="; ".join(f"{k}: model {r0[k]:.10g} vs hand {pt[h]:.10g}" for k, h in MAP.items()))

# =============================================================== B3 actuator limits
for v, case in ((13.0, "B3_limit_v13"), (2.0, "B3_limit_v2")):
    df, p = load(case)
    r0 = df.iloc[0]
    tl = ref[f"T_lim_at_v{v:g}_Nm"]
    dT_ref = tl / 0.02
    e1, e2 = abs(r0["T_lim"] - tl) / tl, abs(r0["dTdt"] - dT_ref) / dT_ref
    add(f"B3_v{v:g}", f"torque limit and torque slew at v = {v} m/s (T_ref = 1000 N m, T = 0)", ok(max(e1, e2) <= TOL["B3_rel"]), "relative error of T_lim and dT/dt",
        f"T_lim {r0['T_lim']:.10g} (hand {tl:.10g}); dT/dt {r0['dTdt']:.10g} (hand {dT_ref:.10g})", "hand: T_lim = min(85, 18000/omega); dT/dt = T_lim/tau_T", "", f"{max(e1, e2):.3e}", TOL["B3_rel"],
        "algebraic quantities, double precision", case=case)

# =============================================================== C. coast-down
toy, p_toy = load("C1_toy_linear_drag")
exact = 10.0 * np.exp(-25.0 * toy["time"] / 850.0)
e_toy = (toy["v"] - exact).abs()
prev = json.loads((VER / "openmodelica-smoke/openmodelica_smoke_results.json").read_text(encoding="utf-8"))["max_abs_error_vs_closed_form_m_s"]
frac = abs(e_toy.max() - prev) / prev
add("C1", "toy linear-drag coast-down m v' = -c v (m = 850 kg, c = 25 N s/m, v0 = 10 m/s), 20 s, DASSL tol 1e-10, 2001 output points, metric max |v - v0 exp(-c t/m)|",
    ok(e_toy.max() <= TOL["C1_floor"] and frac <= TOL["C1_repro_frac"]), "max abs error [m/s]; max relative error", f"{e_toy.max():.4e}; {(e_toy / exact).max():.4e}",
    f"earlier reported {prev:.4e}", f"{e_toy.max():.4e}", f"{(e_toy / exact).max():.4e}", f"< {TOL['C1_floor']:g} and within {TOL['C1_repro_frac']:.0%} of the earlier value",
    "earlier global-error / tolerance ratio about 36; margin about 30", case="C1_toy_linear_drag",
    notes=(f"deviation from the earlier value: {frac:.2%}. WHAT THE NUMBER IS: the toy has linear drag and no rolling resistance, so it is not the project's coast-down; the error is the DASSL global "
           "error at tolerance 1e-10 sampled at the output grid, not an exact-arithmetic error; comparison uses a closed form evaluated in double precision"))

cd = ref["coastdown"]
al, be, ga = cd["alpha"], cd["beta"], cd["gamma"]
s_ = math.sqrt(4 * al * ga - be**2)
th0 = math.atan((2 * ga * cd["v0"] + be) / s_)
C2 = {}
for tol in (1e-6, 1e-8, 1e-10, 1e-12):
    case = f"C2_project_tol{tol:g}"
    df, p = load(case)
    ex = (s_ * np.tan(th0 - s_ * df["time"] / 2) - be) / (2 * ga)
    err = (df["v"] - ex).abs()
    C2[tol] = (err.max(), (err / ex).max(), df["v"].iloc[-1], ex.iloc[-1], case, len(df))
a10 = C2[1e-10]
add("C2", "project coast-down (T_ref = 0, regeneration-branch shaft friction, quadratic drag, rolling resistance), v0 = 13 m/s, 20 s, tol 1e-10, 2001 points vs closed form",
    ok(a10[0] <= TOL["C2_abs"]), "max abs error [m/s]; max relative error", f"{a10[0]:.4e}; {a10[1]:.4e}", f"closed form v(20) = {a10[3]:.12f}", f"{a10[0]:.4e}", f"{a10[1]:.4e}", TOL["C2_abs"],
    "global error of DASSL at tol 1e-10 was about 36x tol for the toy; margin about 30", case=a10[4],
    notes=f"Modelica v(20) = {a10[2]:.12f}; closed form verified symbolically (residual exactly 0) in spec_derivation_checks.txt")
errs = [C2[t][0] for t in (1e-6, 1e-8, 1e-10, 1e-12)]
mono = all(errs[i + 1] <= 1.5 * errs[i] or errs[i + 1] < 1e-11 for i in range(3))
add("C3", "convergence of the coast-down error as the DASSL tolerance tightens (1e-6, 1e-8, 1e-10, 1e-12)", ok(mono), "max abs error at each tolerance [m/s]",
    "; ".join(f"{t:g}: {C2[t][0]:.3e}" for t in C2), "non-increasing (1.5x slack) down to a 1e-11 floor", "", "", "non-increasing", "a floor of 1e-11 m/s is about the double-precision limit of the closed form",
    case="C2_project_tol1e-10", notes="artifact is the 1e-10 run; the other three result files are in the same folder tree")

# =============================================================== D. ideal tracking energy
SAVED = {"S1_soh1.0": 49.714, "S1_soh0.8": 49.803, "S2_soh1.0": 36.951, "S2_soh0.8": 36.990}   # 3-decimal values quoted in technical-foundation-audit.md IC-11
fin = {}
for prof in ("S1", "S2"):
    for soh in (1.0, 0.8):
        case = f"D_{prof}_soh{soh}"
        df, p = load(case)
        fin[(prof, soh)] = (df, case)
hand = ref["profiles"]
for (prof, soh), (df, case) in fin.items():
    h = hand[prof]
    last = df.iloc[-1]
    errs = {"dist": abs(last["dist"] - h["distance_m"]) / h["distance_m"], "E_aero": abs(last["E_aero"] - h["E_aero_J_analytic"]) / h["E_aero_J_analytic"],
            "E_rr": abs(last["E_rr"] - h["E_rr_J_analytic"]) / h["E_rr_J_analytic"]}
    w = max(errs, key=errs.get)
    add(f"D1_{prof}_soh{soh}", f"{prof} (SoH {soh}): distance, aero and rolling energy against exact analytic integrals", ok(errs[w] <= TOL["D1_rel"]), "max relative error",
        f"{errs[w]:.3e} ({w})", "hand_references.json profiles (exact)", "", f"{errs[w]:.3e}", TOL["D1_rel"], "event-located knots plus DASSL tol 1e-10", case=case,
        notes=f"dist {last['dist']:.9f} vs {h['distance_m']:.9f}; E_aero {last['E_aero']:.6f} vs {h['E_aero_J_analytic']:.6f}; E_rr {last['E_rr']:.6f} vs {h['E_rr_J_analytic']:.6f} J "
              f"(without the tanh-smoothing correction of {h['rr_smoothing_correction_J']:.4f} J the analytic E_rr would be off by {h['rr_smoothing_correction_J'] / h['E_rr_J_analytic']:.1e})")
    clos = df["closure"].abs().max() / last["E_chem"]
    add(f"D2_{prof}_soh{soh}", f"{prof} (SoH {soh}): energy-balance closure of the inverse model", ok(clos <= TOL["D2_rel"]), "max |closure| / final E_chem", f"{clos:.3e}", "0", "", f"{clos:.3e}",
        TOL["D2_rel"], "conservation identity; DASSL tol 1e-10 on states of size 1e5 J", case=case,
        notes="a conservation identity: it would also hold with wrong coefficients, so it is not a test of the physical laws")

D3 = {}
for (prof, soh), (df, case) in fin.items():
    m = float(df.iloc[-1]["Wh_per_km"])
    key = f"{prof}_soh{soh}"
    series = {k: v["E_Wh_per_km"] for k, v in conv[key].items()}
    ref1 = series["h=0.001"]
    gap = abs(m - ref1) / ref1
    seq = [(float(k.split("=")[1]), abs(m - v) / v) for k, v in series.items()]
    seq.sort(reverse=True)                      # coarse to fine
    # pre-registered wording: "the gap must shrink when the reference scheme is rerun with a 10x finer step"
    # (finest run, h = 1e-4, against the saved h = 1e-3). The full series is reported but not required to be monotone.
    shrinks = seq[-1][1] < seq[0][1] and seq[-1][0] <= 1.0001e-4
    repro = abs(ref1 - SAVED[key])
    minmargin = float(df["limit_margin"].min())
    D3[key] = {"modelica": m, "ref_h1e-3": ref1, "gap_rel": gap, "series": seq, "shrinks": shrinks, "repro_vs_3dec": repro, "margin": minmargin}
    add(f"D3_{key}", f"{prof} (SoH {soh}): ideal-tracking energy per km against the saved reference", ok(gap <= TOL["D3_rel"] and shrinks), "Modelica Wh/km; reference Wh/km; relative gap",
        f"{m:.6f}; {ref1:.6f}; {gap:.3e}", f"saved value quoted as {SAVED[key]} (3 decimals); reference scheme rerun at h=1e-3 gives {ref1:.6f}", f"{abs(m - ref1):.6f}", f"{gap:.3e}",
        f"gap <= {TOL['D3_rel']:g} and gap shrinks with the reference step", "the reference misassigns up to h/2 of a power jump at each of about 14 slope changes (h = 1 ms)", case=case,
        notes=("gap to the reference at each step h: " + "; ".join(f"h={h:g}: {g:.2e}" for h, g in seq) + f". Reference reproduces the quoted 3-decimal value within {repro:.1e}. "
               f"Minimum T_lim-|T| along the trace: {minmargin:.2f} N m (positive: the ideal trace needs no friction braking and never exceeds the limit)."))
dop = json.loads((VER / "references/ideal_reference_segmentwise_dop853.json").read_text(encoding="utf-8"))
for (prof, soh), (df, case) in fin.items():
    key = f"{prof}_soh{soh}"
    m = float(df.iloc[-1]["Wh_per_km"])
    rr = abs(m - dop[key]["E_Wh_per_km"]) / dop[key]["E_Wh_per_km"]
    RESULTS.append({"check_id": f"D4_{key}", "description": f"{prof} (SoH {soh}): ideal-tracking energy, Modelica against an adjudicating SciPy DOP853 calculation of the same equations (rtol 1e-13, restart at every knot, step capped at 0.01 s)",
                    "status": "INFO", "metric": "relative difference", "value": f"{m:.9f} (Modelica) vs {dop[key]['E_Wh_per_km']:.9f} (DOP853); relative {rr:.2e}", "reference": "verification/references/ideal_reference_segmentwise_dop853.json",
                    "abs_error": f"{abs(m - dop[key]['E_Wh_per_km']):.3e}", "rel_error": f"{rr:.3e}", "tolerance": "none pre-registered (adjudication, not a criterion)",
                    "tolerance_justification": "third calculation by a different integrator, used to say which side of the saved-reference gap Modelica lies on", "model_version": MODEL_VER, "parameters": PARAM_SRC,
                    "source_data": "configs/parameters.yaml; configs/cycles/profiles.yaml", "command": command_for(case) + "  vs  verification/scripts/segmentwise_ode_reference.py", "exit_code": step_exit["30_ideal"],
                    "simulation_status": sim_status(case), "artifact_path": rel(root / cases[case]["result_file"]), "artifact_sha256": sha(root / cases[case]["result_file"]), "notes": ""})
_first = BUILD / "ideal_reference_segmentwise_dop853_FIRST_RUN_free_step_DEFECTIVE.json"
RESULTS.append({"check_id": "FINDING_reference_defect", "description": "finding about the verification tooling: the first segment-wise DOP853 reference (free step) was defective and wrongly suggested a 6e-6 relative error in the Modelica S2 energy",
                "status": "FINDING", "metric": "energy lost by the defective reference", "value": "0.083 J per stop-from-motion (5 stops in S2: 0.415 J, relative 5.9e-6)", "reference": "", "abs_error": "", "rel_error": "",
                "tolerance": "none", "tolerance_justification": "", "model_version": MODEL_VER, "parameters": PARAM_SRC, "source_data": "verification/scripts/segmentwise_ode_reference.py",
                "command": "verification/scripts/segmentwise_ode_reference.py (first run, free step) and the diagnostics described in independent-model-report.md", "exit_code": 0, "simulation_status": "",
                "artifact_path": rel(_first), "artifact_sha256": sha(_first),
                "notes": ("Cause: the free-step integrator crosses the ~0.07 s rolling-resistance smoothing knee (tanh(v/0.05)) at each standstill in a few steps and never samples it. With a step cap the result converges (all caps from 0.5 s to 0.5 ms agree) and equals direct quadrature of the "
                          "specification integrand, Modelica's states, and the fixed-step reference's own integration of the stop ramp. The model was never wrong here; the tool was. The defective output is preserved in the artifact column.")})
add("D3_ref", "the saved reference is reproduced by its own algorithm (h = 1e-3) to its published precision", ok(all(v["repro_vs_3dec"] <= 5e-4 for v in D3.values())), "max |recomputed - quoted| [Wh/km]",
    f"{max(v['repro_vs_3dec'] for v in D3.values()):.2e}", "quoted values rounded to 3 decimals", "", "", 5e-4, "half a unit of the third decimal",
    artifact=VER / "references/ideal_reference_convergence.json", exit_code=0,
    notes="the reference is a saved numerical result of a fixed-step scheme, not an exact value; it exists as text in technical-foundation-audit.md and as an algorithm in audit/technical-verification/ind_checks_b.py")

# =============================================================== E. negative controls
df, _ = load("E_B1_eq_30kmh_wrong_eta_g")
e = ref["equilibrium"]["30kmh"]
fnet0 = float(df["F_net"].iloc[0])
w30 = 6.5 / 0.28 * e["v_m_s"]
pred = 6.5 / 0.28 * 0.98 * (e["T_eq_Nm"] - 0.001 * w30) - e["F_total_N"]
add("E_B1", "negative control: gear efficiency 0.98 instead of 0.9702 at the 30 km/h equilibrium must break the force balance", ok(abs(fnet0) >= TOL["E_factor"] * TOL["B1_Fnet"] and abs(fnet0 - pred) <= 1e-6 * abs(pred)),
    "F_net at t=0 [N]; analytic prediction [N]", f"{fnet0:.6f}; {pred:.6f}", f">= {TOL['E_factor'] * TOL['B1_Fnet']:g} N", f"{abs(fnet0):.6f}", "", f">= 10x the B1 force tolerance", "detection factor shown in notes",
    case="E_B1_eq_30kmh_wrong_eta_g", notes=f"detected by a factor {abs(fnet0) / TOL['B1_Fnet']:.1e} above the B1 tolerance; the model response equals the analytic prediction")
for case, label in (("E_C2_wrong_branch_fixture", "efficiency applied as a multiplier while regenerating (equation-level fixture)"), ("E_C2_Crr_plus1pct", "C_rr increased by 1 % (parameter override)")):
    df, _ = load(case)
    ex = (s_ * np.tan(th0 - s_ * df["time"] / 2) - be) / (2 * ga)
    err = float((df["v"] - ex).abs().max())
    add(f"E_{case[2:4]}_{case.split('_')[-1]}", f"negative control: coast-down with {label}", ok(err >= TOL["E_factor"] * TOL["C2_abs"]), "max abs error vs the unperturbed closed form [m/s]", f"{err:.4e}",
        f">= {TOL['E_factor'] * TOL['C2_abs']:g}", f"{err:.4e}", "", ">= 10x C2 tolerance", "detection factor shown in notes", case=case, notes=f"detected by a factor {err / TOL['C2_abs']:.1e}")
base = float(fin[("S1", 1.0)][0].iloc[-1]["Wh_per_km"])
refs1 = D3["S1_soh1.0"]["ref_h1e-3"]
for case, label in (("E_D_S1_soh1.0_Cd_plus1pct", "C_d +1 %"), ("E_D_S1_soh1.0_etami_plus1pct", "eta_mi +1 %")):
    df, _ = load(case)
    m = float(df.iloc[-1]["Wh_per_km"])
    gap = abs(m - refs1) / refs1
    add(f"E_D_{label.split()[0]}", f"negative control: ideal-tracking energy with {label} must fail the D3 criterion", ok(gap >= TOL["E_factor"] * TOL["D3_rel"]), "relative gap to the saved reference",
        f"{gap:.3e} (energy {m:.6f} Wh/km against {refs1:.6f})", f">= {TOL['E_factor'] * TOL['D3_rel']:g}", f"{abs(m - refs1):.6f}", f"{gap:.3e}", ">= 10x D3 tolerance", "detection factor shown in notes",
        case=case, notes=f"detected by a factor {gap / TOL['D3_rel']:.1f} above the D3 tolerance")

# =============================================================== F1 cross-implementation comparison
mod_full, p_mod = load("F1_openloop66_tol1e-10")
# OpenModelica writes extra rows at event instants (pre- and post-event values at one time, plus state-event times).
# Take the first row at each 0.01 s grid time (the pre-event value; algebraic quantities at the six switch
# instants are excluded below, so the choice only matters for continuous states, which have no jump).
_t = mod_full["time"].to_numpy()
_idx = [int(np.searchsorted(_t, k * 0.01 - 1e-9, side="left")) for k in range(6601)]
assert all(abs(_t[i] - k * 0.01) < 1e-9 for k, i in enumerate(_idx))
mod = mod_full.iloc[_idx].reset_index(drop=True)
EXTRA_ROWS = len(mod_full) - len(mod)
py4 = pd.read_csv(BUILD / "python_reference/openloop66_python_h0.0001.csv")
py3 = pd.read_csv(BUILD / "python_reference/openloop66_python_h0.001.csv")
assert len(mod) == len(py4) == len(py3) and np.allclose(mod["time"], py4["time"], atol=1e-9)
t_ = mod["time"].to_numpy()
sw_mask = np.zeros(len(t_), bool)
for s in SWITCH_T:
    sw_mask |= np.abs(t_ - s) < 1e-6
F = TOL["F1"]
QUANT = [("v", "v", F["v"], "state"), ("T", "T", F["T"], "state"), ("V1", "V1", F["V1"], "state"), ("SoC", "SoC", F["SoC"], "state"), ("dist", "dist", F["dist"], "state")]
for e_ in ("E_chem", "E_rr", "E_aero", "E_fb", "E_gear", "E_visc", "E_mi", "E_R0", "E_R1", "E_regen"):
    QUANT.append((e_, e_, None, "energy"))
for f_ in ("F_w", "F_rr", "F_aero", "F_fb", "F_net"):
    QUANT.append((f_, f_, F["F"], "algebraic"))
QUANT += [("a", "a", F["a"], "algebraic"), ("P_m", "P_m", F["P"], "algebraic"), ("P_e", "P_e", F["P"], "algebraic"), ("I", "I", F["I"], "algebraic"), ("T_lim", "T_lim", F["T"], "algebraic")]
comp = []
all_pass = True
for name, col, tol, kind in QUANT:
    m_, a4, a3 = mod[col].to_numpy(float), py4[col].to_numpy(float), py3[col].to_numpy(float)
    mask = ~sw_mask if kind == "algebraic" else np.ones(len(t_), bool)
    final = max(abs(a4[-1]), 0.0)
    tol_eff = tol if tol is not None else max(F["E_rel"] * final, F["E_floor"])
    d4, d3, d43 = np.abs(m_ - a4)[mask], np.abs(m_ - a3)[mask], np.abs(a3 - a4)[mask]
    scale = max(np.abs(a4[mask]).max(), 1e-300)
    status = ok(d4.max() <= tol_eff)
    all_pass &= (status == "PASS")
    i4 = int(np.argmax(np.where(mask, np.abs(m_ - a4), -1)))
    comp.append({"quantity": name, "kind": kind, "samples_compared": int(mask.sum()), "excluded_switch_samples": int((~mask).sum()),
                 "max_abs_diff_modelica_vs_python_h1e-4": float(d4.max()), "time_of_max_s": float(t_[i4]), "rms_diff_h1e-4": float(np.sqrt(np.mean(d4**2))),
                 "max_abs_diff_modelica_vs_python_h1e-3": float(d3.max()), "max_abs_diff_python_h1e-3_vs_h1e-4": float(d43.max()),
                 "ratio_(modelica-vs-py1e-3)/(py1e-3-vs-py1e-4)": float(d3.max() / d43.max()) if d43.max() > 0 else float("nan"),
                 "scale_max_abs": float(scale), "relative_to_scale_h1e-4": float(d4.max() / scale), "tolerance": float(tol_eff), "status": status})
with open(VER / "cross-implementation-comparison.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(comp[0].keys()) + ["model_version", "parameters", "modelica_artifact", "modelica_sha256", "python_artifacts", "command", "exit_code"])
    w.writeheader()
    for c in comp:
        c.update({"model_version": MODEL_VER, "parameters": "SoH 0.8; " + PARAM_SRC, "modelica_artifact": rel(p_mod), "modelica_sha256": sha(p_mod),
                  "python_artifacts": "verification/modelica-build/python_reference/openloop66_python_h0.0001.csv; ..._h0.001.csv", "command": command_for("F1_openloop66_tol1e-10") + "  vs  scripts/run_python_plant_openloop.py <root> 1e-4 and 1e-3",
                  "exit_code": step_exit[cases["F1_openloop66_tol1e-10"]["script"]]})
        w.writerow(c)
bad = [c["quantity"] for c in comp if c["status"] == "FAIL"]
worst_lines = sorted(comp, key=lambda c: -c["relative_to_scale_h1e-4"])[:3]
add("F1", "forward plant, 66 s open-loop schedule, SoH 0.8: Modelica (DASSL 1e-10) against the Python plant at h = 1e-4 s, all quantities of spec section 10", ok(not bad),
    "quantities passing", f"{len(comp) - len(bad)} of {len(comp)}; failing: {bad if bad else 'none'}", "pre-registered per-quantity tolerances", "", "", "see cross-implementation-comparison.csv",
    "Python RK4 at h = 1e-4 is 10x finer than the project's step; tolerances derived from the largest step-dependent effects", case="F1_openloop66_tol1e-10",
    notes="largest relative-to-scale differences: " + "; ".join(f"{c['quantity']} {c['relative_to_scale_h1e-4']:.2e} at t={c['time_of_max_s']:.2f}" for c in worst_lines))
pyc, _ = None, None
negp = pd.read_csv(BUILD / "python_reference/openloop66_python_h0.001_Crr1.01.csv")
dv = float(np.abs(mod["v"].to_numpy() - negp["v"].to_numpy()).max())
add("E_F1", "negative control: Python plant with C_rr +1 % against the unperturbed Modelica run must fail the F1 speed tolerance", ok(dv >= TOL["E_factor"] * F["v"]), "max |dv| [m/s]", f"{dv:.4e}", f">= {TOL['E_factor'] * F['v']:g}",
    f"{dv:.4e}", "", ">= 10x F1 speed tolerance", "detection factor shown in notes", case="F1_openloop66_tol1e-10", notes=f"detected by a factor {dv / F['v']:.1e}")

# ---- solver independence (informational): same model, other solvers / tolerances, final values
solv = {}
for case, label in (("F1_openloop66_tol1e-08", "DASSL 1e-8"), ("F1_openloop66_tol1e-10", "DASSL 1e-10"), ("DIAG_dassl_tol1e-11", "DASSL 1e-11"), ("DIAG_dassl_tol3e-12", "DASSL 3e-12"),
                    ("DIAG_cvode_tol1e-10", "CVODE 1e-10"), ("DIAG_cvode_tol1e-12", "CVODE 1e-12"), ("DIAG_ida_tol1e-12", "IDA 1e-12"), ("DIAG_rk4_h1e-4", "RK4 (Modelica) 1e-4")):
    pth = BUILD / "cases" / case / f"{case}_res.csv"
    if pth.exists():
        d = pd.read_csv(pth)
        solv[label] = (float(d["E_chem"].iloc[-1]), float(d["v"].iloc[-1]), float(d["T"].iloc[-1]), float(d["closure"].abs().max()) if "closure" in d else float("nan"))
ref_e = solv["CVODE 1e-12"][0] if "CVODE 1e-12" in solv else mod["E_chem"].iloc[-1]
summ = {"solver_final_E_chem_J": {k: v[0] for k, v in solv.items()}, "solver_rel_to_CVODE1e-12": {k: abs(v[0] - ref_e) / ref_e for k, v in solv.items()},
        "python_h1e-4_final_E_chem_J": float(py4["E_chem"].iloc[-1]), "python_h1e-3_final_E_chem_J": float(py3["E_chem"].iloc[-1]), "modelica_dassl1e-10_final_E_chem_J": float(mod["E_chem"].iloc[-1]),
        "C2": {str(k): v[0] for k, v in C2.items()}, "D3": {k: {kk: vv for kk, vv in v.items() if kk != "series"} | {"series": v["series"]} for k, v in D3.items()}, "failing_quantities_F1": bad}
for lab, (E, vf, Tf, cl) in solv.items():
    rr = abs(E - ref_e) / ref_e
    case_map = {"DASSL 1e-8": "F1_openloop66_tol1e-08", "DASSL 1e-10": "F1_openloop66_tol1e-10", "DASSL 1e-11": "DIAG_dassl_tol1e-11", "DASSL 3e-12": "DIAG_dassl_tol3e-12",
                "CVODE 1e-10": "DIAG_cvode_tol1e-10", "CVODE 1e-12": "DIAG_cvode_tol1e-12", "IDA 1e-12": "DIAG_ida_tol1e-12", "RK4 (Modelica) 1e-4": "DIAG_rk4_h1e-4"}
    cs = case_map[lab]
    pth = BUILD / "cases" / cs / f"{cs}_res.csv"
    RESULTS.append({"check_id": "INFO_solver_" + lab.replace(" ", "_"), "description": f"informational: same forward trajectory, {lab}; final E_chem against CVODE 1e-12 (not a pass/fail criterion)", "status": "INFO",
                    "metric": "relative difference of final E_chem", "value": f"{E:.6f} J; relative {rr:.3e}", "reference": f"CVODE 1e-12: {ref_e:.6f} J", "abs_error": f"{abs(E - ref_e):.6f}", "rel_error": f"{rr:.3e}",
                    "tolerance": "none (informational)", "tolerance_justification": "solver-independence evidence, not pre-registered as pass/fail", "model_version": MODEL_VER, "parameters": PARAM_SRC,
                    "source_data": "verification/modelica/EurekaPlant/Tests/OpenLoop66.mo", "command": "powershell -File verification\\Invoke-OpenModelica.ps1 -Mos verification\\modelica\\scripts\\" + ("40_openloop" if cs.startswith("F1") else "diag_openloop_solvers") + ".mos",
                    "exit_code": solver_exit.get("diag_openloop_solvers") if cs.startswith("DIAG") else step_exit["40_openloop"], "simulation_status": sim_status(cs),
                    "artifact_path": rel(pth), "artifact_sha256": sha(pth), "notes": "RK4 (Modelica) is OpenModelica's deprecated fixed-step method; its larger error is reported as observed and not explained" if "RK4" in lab else ""})
_dl = BUILD / "cases/DIAG_tol1e-12/DIAG_tol1e-12_res.csv"
RESULTS.append({"check_id": "FINDING_dassl_1e-12", "description": "finding (outside the pass criteria): DASSL at tolerance 1e-12 and 1e-13 terminates with NaN right after the state event at t = 30 s; tolerances >= 3e-12 and CVODE/IDA at 1e-12 complete",
                "status": "FINDING", "metric": "simulation outcome", "value": "DASSL 1e-12: failed; DASSL 1e-13: failed; DASSL 3e-12 and 1e-11: finished; CVODE 1e-12: finished; IDA 1e-12: finished", "reference": "", "abs_error": "", "rel_error": "",
                "tolerance": "none", "tolerance_justification": "not a pre-registered criterion", "model_version": MODEL_VER, "parameters": PARAM_SRC, "source_data": "verification/modelica/EurekaPlant/Tests/OpenLoop66.mo",
                "command": "powershell -File verification\\Invoke-OpenModelica.ps1 -Mos verification\\modelica\\scripts\\diag_openloop_tol1e-12.mos and diag_openloop_solvers.mos", "exit_code": 0,
                "simulation_status": sim_status("DIAG_tol1e-12"), "artifact_path": rel(sorted(glob.glob(str(BUILD / "logs" / "*-v011-diag_openloop_tol1e-12.out.txt")))[-1]), "artifact_sha256": sha(sorted(glob.glob(str(BUILD / "logs" / "*-v011-diag_openloop_tol1e-12.out.txt")))[-1]),
                "notes": "omc exits 0 even though the simulation failed. The mechanism is not established: the log shows a located state event at t = 30 s followed by NaN; the same model completes with other solvers and looser DASSL tolerances, so it is a DASSL-at-extreme-tolerance limitation, not a model equation problem (hypothesis, not proven)"})
(BUILD / "check_summary.json").write_text(json.dumps(summ, indent=2, default=float), encoding="utf-8")

cols = ["check_id", "description", "status", "metric", "value", "reference", "abs_error", "rel_error", "tolerance", "tolerance_justification", "model_version", "parameters", "source_data", "command", "exit_code",
        "simulation_status", "artifact_path", "artifact_sha256", "notes"]
with open(VER / "modelica-check-results.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for r in RESULTS:
        w.writerow({c: r.get(c, "") for c in cols})
n_pass = sum(r["status"] == "PASS" for r in RESULTS)
n_fail = sum(r["status"] == "FAIL" for r in RESULTS)
print(f"{len(RESULTS)} rows: {n_pass} PASS, {n_fail} FAIL, {sum(r['status'] == 'INFO' for r in RESULTS)} INFO, {sum(r['status'] == 'FINDING' for r in RESULTS)} FINDING")
for r in RESULTS:
    print(f"{r['status']:4s} {r['check_id']:28s} {str(r['value'])[:130]}")
print("cross-implementation: ", sum(c["status"] == "PASS" for c in comp), "of", len(comp), "quantities pass")
