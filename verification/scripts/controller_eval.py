"""Evaluation of the Modelica controller cross-check (protocol: verification/controller-crosscheck-protocol.md).

Reads saved files only: the Modelica result CSVs of the primary grid and the sensitivity runs, the saved Python series
(artifacts/raw/primary), the Python refinement series (verification/controller-crosscheck-runs/python_reference), the frozen gains,
the solver selection and the launcher logs. Calls no plant or controller code (no eureka import). Tolerances come from
controller_tolerances.py (the rule of protocol section 8); nothing here is set from a Modelica-versus-Python difference.

Writes verification/controller-crosscheck-results.csv, verification/controller-crosscheck-runs/evaluation_summary.json and the
gzip archive of every raw Modelica CSV under verification/controller-crosscheck-runs/raw/.
usage: python controller_eval.py <project root>
"""
import csv
import gzip
import json
import pathlib
import re
import sys

import numpy as np

root = pathlib.Path(sys.argv[1])
sys.path.insert(0, str(root / "verification/scripts"))
import controller_metrics as cm  # noqa: E402
import controller_series as cs  # noqa: E402
from controller_tolerances import FLOOR_REL, SAFETY, tol as tol_rule  # noqa: E402

VER = root / "verification"
RUNS = VER / "controller-crosscheck-runs"
STEPS = {"S1": 32491, "S2": 21328}
STATES = ["v", "T", "V1", "SoC", "E_chem", "E_rr", "E_aero", "E_fb", "E_gear", "E_visc", "E_mi", "E_R0", "E_R1", "dist", "Ah", "E_regen"]
IXY = {n: i for i, n in enumerate(STATES)}
TS, VOC = 0.01, 48.0
gains = json.loads((VER / "references/controller_gains.json").read_text(encoding="utf-8"))["gains"]
sel = json.loads((VER / "references/controller_solver_selection.json").read_text(encoding="utf-8"))["selected"]
cases = json.loads((VER / "modelica/scripts/controller_cases.json").read_text(encoding="utf-8"))
ROWS = []


def K_of(kind, soh):
    return gains["fixed_soh1.00" if kind == "fixed" else f"scheduled_soh{soh:.2f}"]["K"]


# ---------------------------------------------------------------- Python side
def py_saved(prof, kind, soh):
    man = json.loads((root / f"artifacts/raw/primary/{prof}/manifest.json").read_text(encoding="utf-8"))
    j = next(i for i, r in enumerate(man["runs"]) if r["controller"] == kind and abs(r["soh"] - soh) < 1e-9)
    with np.load(root / f"artifacts/raw/primary/{prof}/timeseries.npz") as z:
        a = {k: z[k] for k in z.files}
    y1, y0 = a["y_end"][j], a["y0"][j]
    s = {"v": a["v"][:, j], "v_ref": a["v_ref"], "T": a["T"][:, j], "u": a["t_ref"][:, j], "T_lim": a["t_lim"][:, j], "sat": a["sat"][:, j],
         "z": a["z"][:, j], "I": a["i"][:, j], "E_chem_t": a["E_chem"][:, j], "dist_t": a["dist"][:, j], "SoC": a["SoC"][:, j]}
    for nm in ("E_chem", "dist", "E_fb", "E_regen", "E_R0", "E_R1", "Ah"):
        s[nm] = float(y1[IXY[nm]] - y0[IXY[nm]])
    s["i"] = s["I"]
    return s


def py_refined(prof, kind, soh):
    p = RUNS / f"python_reference/{prof}_{kind}_soh{soh:.2f}_dt0.0001.npz"
    if not p.exists():
        return None
    z = np.load(p)
    s = {k: z[k] for k in z.files}
    s["T_lim"], s["I"], s["E_chem_t"], s["dist_t"] = s["t_lim"], s["i"], s.pop("E_chem_t"), s.pop("dist_t")
    for nm in ("E_chem", "dist", "E_fb", "E_regen", "E_R0", "E_R1", "Ah"):
        s[nm] = float(s[nm])
    return s


# ---------------------------------------------------------------- Modelica side
def mod_series(case, prof, kind, soh):
    c = cases[case]
    path = root / c["result_file"]
    sd, info = cs.load_modelica(path, STEPS[prof])
    k = K_of(kind, soh)
    n = STEPS[prof]
    if not info["final_update_present"]:  # reconstruct the final sample's controller quantities from saved states (protocol P2)
        e = sd["v"][n] - sd["v_ref"][n]
        zu = sd["z"][n - 1]
        tl = min(85.0, 18000.0 / max(6.5 / 0.28 * max(sd["v"][n], 0.0), 1e-6))
        u = -(k[0] * e + k[1] * sd["T"][n] + k[2] * zu)
        sd["e_k"][n], sd["z_used"][n], sd["T_lim_k"][n], sd["u"][n], sd["sat_k"][n] = e, zu, tl, u, float(u > tl)
        info["final_sample_reconstructed"] = True
    s = {"v": sd["v"], "v_ref": sd["v_ref"], "T": sd["T"], "u": sd["u"], "T_lim": sd["T_lim_k"], "sat": sd["sat_k"], "z": sd["z_used"], "I": sd["I"],
         "i": sd["I"], "v_upd": sd["v_upd"], "T_upd": sd["T_upd"], "v_ref_upd": sd["v_ref_upd"], "E_chem_t": sd["E_chem"], "dist_t": sd["dist"], "SoC": sd["SoC"], "e_k": sd["e_k"], "z_next": sd["z"], "se2": sd["se2"]}
    for nm in ("E_chem", "dist", "E_fb", "E_regen", "E_R0", "E_R1", "Ah"):
        s[nm] = float(sd[nm][-1])
    s["closure_end"] = float(sd["closure"][-1])
    s["vmin"] = float(np.min(sd["v"]))
    s["F_fb"] = sd["F_fb"]
    return s, info, path


def acc(v):
    return np.diff(v) / TS


def add(**kw):
    row = {k: "" for k in ("check_id", "group", "case", "quantity", "status", "value_modelica", "value_python", "abs_diff", "rel_diff", "tolerance", "u_py", "u_mod",
                           "margin_tol_over_diff", "borrowed", "note", "simulation_status", "artifact_path", "artifact_sha256")}
    row.update({k: (f"{v:.17g}" if isinstance(v, (float, np.floating)) else v) for k, v in kw.items()})
    ROWS.append(row)
    return row


# ---------------------------------------------------------------- load everything
GRID = [(p, k, s) for p in ("S1", "S2") for s in (1.0, 0.9, 0.8, 0.7) for k in ("fixed", "scheduled")]
MOD, PYS, PYR, INFO, ART = {}, {}, {}, {}, {}
for prof, kind, soh in GRID:
    case = f"A_{prof}_{kind}_soh{round(soh * 100):03d}"
    if case not in cases:
        continue
    try:
        MOD[(prof, kind, soh)], INFO[(prof, kind, soh)], ART[(prof, kind, soh)] = mod_series(case, prof, kind, soh)
    except Exception as ex:  # noqa: BLE001
        add(check_id=f"V-{case}", group="validity", case=case, quantity="load", status="FAIL", note=f"cannot be loaded: {ex!r}", simulation_status=cs.sim_status(root, case))
        continue
    PYS[(prof, kind, soh)] = py_saved(prof, kind, soh)
    PYR[(prof, kind, soh)] = py_refined(prof, kind, soh)

# sensitivity variants (SoH 0.8): {(prof, kind): {(solver, tol): series}}
VAR = {}
for name, c in cases.items():
    m = re.match(r"N_(S1|S2)_(fixed|scheduled)_soh080_(\w+)_tol([\d.e+-]+)$", name)
    if not m or c["stage"] != "sens":
        continue
    prof, kind, solver, tol = m.group(1), m.group(2), m.group(3), float(m.group(4))
    st = cs.sim_status(root, name)
    if st != "finished successfully" or not (root / c["result_file"]).exists():
        add(check_id=f"S-{name}", group="sensitivity", case=name, quantity="completion", status="INFO", note=f"variant not admissible: {st}", simulation_status=st)
        continue
    try:
        VAR.setdefault((prof, kind), {})[(solver, tol)] = mod_series(name, prof, kind, 0.8)[0]
    except Exception as ex:  # noqa: BLE001
        add(check_id=f"S-{name}", group="sensitivity", case=name, quantity="load", status="INFO", note=f"variant not usable: {ex!r}", simulation_status=st)


def near(d):
    """Protocol A3: u_mod uses only the variant closest in tolerance (the 100x looser neighbour); the 1e4x variant is a convergence check."""
    if not d:
        return {}
    k0 = min(d, key=lambda k: abs(np.log10(k[1]) - np.log10(sel["tolerance"])))
    return {k0: d[k0]}


def u_mod_trace(prof, kind, key, fn):
    vs = near(VAR.get((prof, kind), {}))
    if not vs:
        return 0.0, "no variants"
    ref = fn(MOD[(prof, kind, 0.8)])
    return float(max(np.max(np.abs(ref - fn(v))) for v in vs.values())), f"{len(vs)} variants"


def u_py_trace(prof, kind, soh, fn):
    """|Q(dt=1e-3) - Q(dt=1e-4)|; SoH 0.9 / 0.7 borrow the SoH 0.8 value of the same profile and controller."""
    borrowed = PYR.get((prof, kind, soh)) is None
    s0 = 0.8 if borrowed else soh
    a, b = PYS.get((prof, kind, s0)), PYR.get((prof, kind, s0))
    if a is None or b is None:
        return 0.0, True
    try:
        return float(np.max(np.abs(fn(a) - fn(b)))), borrowed
    except KeyError:  # SoC is not stored in the refined Python series
        return None, borrowed


# ---------------------------------------------------------------- validity / convergence / internal recomputation
for (prof, kind, soh), s in MOD.items():
    case = f"A_{prof}_{kind}_soh{round(soh * 100):03d}"
    st, info, path = cs.sim_status(root, case), INFO[(prof, kind, soh)], ART[(prof, kind, soh)]
    base = dict(case=case, simulation_status=st, artifact_path=str(path.relative_to(root)))
    thr = VOC * 3600.0 * s["Ah"]
    n = STEPS[prof]
    kin = float(np.max(np.abs(np.diff(s["dist_t"]) - TS * (s["v"][:-1] + s["v"][1:]) / 2)))  # criterion K, amendment A2
    ok = st == "finished successfully" and info["nan_cells"] == 0 and info["updates"] >= n and abs(s["closure_end"]) / thr <= 1e-3 and s["vmin"] >= -1e-6 and kin <= 1e-3
    add(check_id=f"V1-{case}", group="validity", quantity="simulation finished, no NaN, updates complete, prereg closure<=1e-3, v>=-1e-6", status="PASS" if ok else "FAIL",
        value_modelica=abs(s["closure_end"]) / thr, tolerance=1e-3, note=f"closure_rel={abs(s['closure_end']) / thr:.3e}; vmin={s['vmin']:.3e}; updates={info['updates']} of {n + 1}; nan_cells={info['nan_cells']}; "
        f"final update present={info['final_update_present']}; kinematic residual K={kin:.2e} m (<=1e-3)", **base)
    add(check_id=f"V2-{case}", group="timing", quantity="controller update rows within 1e-9 s of k*Ts", status="PASS" if info["update_row_time_max_dev_from_kTs"] <= 1e-9 else "FAIL",
        value_modelica=info["update_row_time_max_dev_from_kTs"], tolerance=1e-9, note=f"max event rows per grid time={info['n_event_rows_per_grid_time_max']}; rows={info['rows']}", **base)
    # P5: recomputation of the law from saved states
    k_ = K_of(kind, soh)
    # amendment A4: the recomputation uses the states the controller saw (rows of the update events), not the grid rows, whose times differ from the update times by the sample() drift
    nu = min(info["updates"], n + 1)
    vu, Tu, vru = s["v_upd"][:nu], s["T_upd"][:nu], s["v_ref_upd"][:nu]
    e = vu - vru
    zu = s["z"][:nu]
    ucalc = -(k_[0] * e + k_[1] * Tu + k_[2] * zu)
    tl_c = np.minimum(85.0, 18000.0 / np.maximum(6.5 / 0.28 * np.maximum(vu, 0.0), 1e-6))
    sat_c = ucalc > tl_c
    znext = np.where(sat_c & (e < 0), zu, zu + TS * e)
    d_u = float(np.max(np.abs(ucalc - s["u"][:nu])))
    # flags may legitimately differ only where |u - T_lim| is below the recomputation error
    marg = np.abs(s["u"][:nu] - s["T_lim"][:nu])
    flag_bad = int(np.sum((sat_c != (s["sat"][:nu] > 0.5)) & (marg > 1e-9)))
    d_z = float(np.max(np.abs(znext[:-1] - zu[1:])))
    d_se2 = abs(float(np.sqrt(s["se2"][-1 if info["final_update_present"] else -2] / (n + 1 if info["final_update_present"] else n))) - float(np.sqrt(np.mean(e[: (n + 1 if info["final_update_present"] else n)] ** 2))))
    d_e = float(np.max(np.abs(e - s["e_k"][:nu])))
    add(check_id=f"P5a-{case}", group="controller-logic", quantity="u_k = -K.[e,T,z_used] recomputed from saved states", status="PASS" if d_u <= 1e-9 else "FAIL", abs_diff=d_u, tolerance=1e-9, **base)
    add(check_id=f"P5b-{case}", group="controller-logic", quantity="sat flag and T_lim recomputed", status="PASS" if flag_bad == 0 else "FAIL", abs_diff=float(flag_bad), tolerance=0.0, **base)
    add(check_id=f"P5c-{case}", group="controller-logic", quantity="z recursion (anti-windup rule) recomputed", status="PASS" if d_z <= 1e-12 else "FAIL", abs_diff=d_z, tolerance=1e-12, **base)
    add(check_id=f"P5d-{case}", group="controller-logic", quantity="RMSE from running sum se2 vs from saved series; e_k vs v-v_ref", status="PASS" if (d_se2 <= 1e-12 and d_e <= 1e-9) else "FAIL",
        abs_diff=max(d_se2, d_e), tolerance=1e-12, note=f"d_se2={d_se2:.2e}, d_e={d_e:.2e}", **base)
    # P6: reference profile vs the saved profile
    d_vr = float(np.max(np.abs(s["v_ref"] - PYS[(prof, kind, soh)]["v_ref"])))
    add(check_id=f"P6-{case}", group="profile", quantity="v_ref(t_k) vs saved v_ref", status="PASS" if d_vr <= 1e-9 else "FAIL", abs_diff=d_vr, tolerance=1e-9,
        note="sample times drift from k*Ts by <=1e-9 s (OpenModelica sample()); 1e-9 m/s allows slope 1 m/s^2 x 1e-9 s", **base)

# ---------------------------------------------------------------- agreement with the Python baseline
TRACES = [("v", lambda s: s["v"]), ("acceleration", lambda s: acc(s["v"])), ("T", lambda s: s["T"]), ("u", lambda s: s["u"]), ("T_lim", lambda s: s["T_lim"]),
          ("z_used", lambda s: s["z"]), ("I", lambda s: s["I"]), ("E_chem(t)", lambda s: s["E_chem_t"]), ("dist(t)", lambda s: s["dist_t"]), ("SoC", lambda s: s["SoC"])]
TOLS = {}  # (prof, kind, soh, trace) -> tol
for (prof, kind, soh), s in MOD.items():
    case = f"A_{prof}_{kind}_soh{round(soh * 100):03d}"
    py = PYS[(prof, kind, soh)]
    base = dict(case=case, simulation_status=cs.sim_status(root, case), artifact_path=str(ART[(prof, kind, soh)].relative_to(root)))
    for tname, fn in TRACES:
        a, b = fn(s), fn(py)
        diff = float(np.max(np.abs(a - b)))
        upy, borrowed = u_py_trace(prof, kind, soh, fn)
        umod, nv = u_mod_trace(prof, kind, soh, fn)
        if upy is None:
            add(check_id=f"C1-{case}-{tname}", group="trace agreement vs saved Python (dt=1e-3)", quantity=f"max|{tname}_mod - {tname}_py|", status="INFO", abs_diff=diff, u_mod=umod,
                note="u_py unavailable (quantity not stored in the refined Python series): no tolerance, informational", **base)
            continue
        t = tol_rule(upy, umod, float(np.max(np.abs(b))))
        TOLS[(prof, kind, soh, tname)] = t
        add(check_id=f"C1-{case}-{tname}", group="trace agreement vs saved Python (dt=1e-3)", quantity=f"max|{tname}_mod - {tname}_py|", status="PASS" if diff <= t else "FAIL",
            abs_diff=diff, tolerance=t, u_py=upy, u_mod=umod, margin_tol_over_diff=(t / diff if diff > 0 else float("inf")), borrowed=("u_py borrowed from SoH 0.8; " if borrowed else "") + ("u_mod borrowed from SoH 0.8" if soh != 0.8 else ""),
            note=nv, **base)
        ref = PYR.get((prof, kind, soh))
        if ref is not None:
            d4 = float(np.max(np.abs(a - fn(ref))))
            u4 = 0.0
            t4 = tol_rule(u4, umod, float(np.max(np.abs(b))))
            add(check_id=f"C2-{case}-{tname}", group="trace agreement vs refined Python (dt=1e-4)", quantity=f"max|{tname}_mod - {tname}_py(1e-4)|", status="INFO",
                abs_diff=d4, tolerance=t4, u_mod=umod, note="tolerance without u_py (the Python error of the refined run is not estimated); informational", **base)

# scalars
SCAL = ["energy_Wh_per_km", "rmse_ms", "max_abs_err_ms", "distance_km", "energy_Wh", "rms_current_A", "peak_current_A", "ah_throughput", "resistive_loss_Wh", "friction_brake_Wh",
        "regen_recovered_Wh", "traction_limited_frac", "rms_jerk_ms3", "rms_torque_cmd_Nm"]


def msr(s):
    return cm.metrics({"v": s["v"], "v_ref": s["v_ref"], "i": s["I"], "sat": np.nan_to_num(s["sat"]), "u": s["u"], "E_chem": s["E_chem"], "dist": s["dist"],
                       "E_fb": s["E_fb"], "E_regen": s["E_regen"], "E_R0": s["E_R0"], "E_R1": s["E_R1"], "Ah": s["Ah"]})


M_MOD, M_PYS, M_PYR = {}, {}, {}
for key in MOD:
    M_MOD[key] = msr(MOD[key])
    M_PYS[key] = msr(PYS[key])
    if PYR.get(key) is not None:
        M_PYR[key] = msr(PYR[key])
M_VAR = {k: {v_: msr(sv) for v_, sv in d.items()} for k, d in VAR.items()}


def u_metric(prof, kind, soh, name):
    borrowed = (prof, kind, soh) not in M_PYR
    s0 = 0.8 if borrowed else soh
    up = abs(M_PYS[(prof, kind, s0)][name] - M_PYR[(prof, kind, s0)][name]) if (prof, kind, s0) in M_PYR else 0.0
    vs = near(M_VAR.get((prof, kind), {}))
    um = max((abs(M_MOD[(prof, kind, 0.8)][name] - m[name]) for m in vs.values()), default=0.0)
    return up, um, borrowed


for (prof, kind, soh), m in M_MOD.items():
    case = f"A_{prof}_{kind}_soh{round(soh * 100):03d}"
    base = dict(case=case, simulation_status=cs.sim_status(root, case), artifact_path=str(ART[(prof, kind, soh)].relative_to(root)))
    for name in SCAL:
        a, b = m[name], M_PYS[(prof, kind, soh)][name]
        up, um, borrowed = u_metric(prof, kind, soh, name)
        t = tol_rule(up, um, b)
        add(check_id=f"M1-{case}-{name}", group="metric agreement vs saved Python", quantity=name, status="PASS" if abs(a - b) <= t else "FAIL", value_modelica=a, value_python=b, abs_diff=abs(a - b),
            rel_diff=abs(a - b) / abs(b) if b else "", tolerance=t, u_py=up, u_mod=um, margin_tol_over_diff=(t / abs(a - b) if a != b else float("inf")),
            borrowed=("u_py borrowed from SoH 0.8; " if borrowed else "") + ("u_mod borrowed from SoH 0.8" if soh != 0.8 else ""), **base)
    add(check_id=f"M2-{case}-distance_normalisation", group="metric agreement vs saved Python", quantity="E_chem_end and dist_end separately", status="INFO",
        value_modelica=MOD[(prof, kind, soh)]["dist"], value_python=PYS[(prof, kind, soh)]["dist"], abs_diff=abs(MOD[(prof, kind, soh)]["dist"] - PYS[(prof, kind, soh)]["dist"]),
        note=f"E_chem end: Modelica {MOD[(prof, kind, soh)]['E_chem']:.9f} J vs Python {PYS[(prof, kind, soh)]['E_chem']:.9f} J (abs diff {abs(MOD[(prof, kind, soh)]['E_chem'] - PYS[(prof, kind, soh)]['E_chem']):.3e})", **base)

# constraint activation timing
for (prof, kind, soh), s in MOD.items():
    case = f"A_{prof}_{kind}_soh{round(soh * 100):03d}"
    py = PYS[(prof, kind, soh)]
    base = dict(case=case, simulation_status=cs.sim_status(root, case), artifact_path=str(ART[(prof, kind, soh)].relative_to(root)))
    tu, tl_, ti, tv = (TOLS[(prof, kind, soh, x)] for x in ("u", "T_lim", "I", "v"))
    flags = {
        "traction limit (u > T_lim)": ((s["sat"] > 0.5), py["sat"].astype(bool), np.abs(py["u"] - py["T_lim"]), tu + tl_),
        "friction brake (u < -T_lim)": ((s["u"] < -s["T_lim"]), (py["u"] < -py["T_lim"]), np.abs(py["u"] + py["T_lim"]), tu + tl_),
        "regeneration (I < 0)": ((s["I"] < 0), (py["I"] < 0), np.abs(py["I"]), ti),
        "standstill (|v| < 1e-9)": ((np.abs(s["v"]) < 1e-9), (np.abs(py["v"]) < 1e-9), np.abs(py["v"]), tv),
    }
    for fname, (fm, fp, margin, tolm) in flags.items():
        mis = np.nonzero(fm != fp)[0]
        unexplained = [int(i) for i in mis if margin[i] > tolm]
        add(check_id=f"K-{case}-{fname.split(' ')[0]}", group="constraint activation timing", quantity=fname, status="PASS" if not unexplained else "FAIL",
            value_modelica=float(fm.sum()), value_python=float(fp.sum()), abs_diff=float(len(mis)), tolerance=tolm,
            note=f"samples active: Modelica {int(fm.sum())}, Python {int(fp.sum())}; disagreeing samples {len(mis)}; unexplained (margin > tolerance) {len(unexplained)}"
                 + (f"; first unexplained k={unexplained[0]} (t={unexplained[0] * TS:.2f} s)" if unexplained else ""), **base)

# ---------------------------------------------------------------- pairs
def pair_of(ms):
    return cm.pair(ms["fixed"], ms["scheduled"])


def pair_py_refined(prof, soh):
    s0 = soh
    if (prof, "fixed", s0) in M_PYR and (prof, "scheduled", s0) in M_PYR:
        return cm.pair(M_PYR[(prof, "fixed", s0)], M_PYR[(prof, "scheduled", s0)])
    return None


summary = {"selected": sel, "pairs": {}}
for prof in ("S1", "S2"):
    for soh in (1.0, 0.9, 0.8, 0.7):
        if (prof, "fixed", soh) not in MOD or (prof, "scheduled", soh) not in MOD:
            continue
        pm = pair_of({"fixed": M_MOD[(prof, "fixed", soh)], "scheduled": M_MOD[(prof, "scheduled", soh)]})
        pp = pair_of({"fixed": M_PYS[(prof, "fixed", soh)], "scheduled": M_PYS[(prof, "scheduled", soh)]})
        borrowed = not ((prof, "fixed", soh) in M_PYR and (prof, "scheduled", soh) in M_PYR)
        s0 = 0.8 if borrowed else soh
        pr = pair_py_refined(prof, s0)
        # saved table check: the saved pair table value must equal the recomputation from the saved series
        sv = {}
        for r in csv.DictReader(open(root / "artifacts/tables/primary_pairs.csv", encoding="utf-8")):
            if r["profile"] == prof and abs(float(r["soh"]) - soh) < 1e-9:
                sv = {"dE_pct": float(r["dE_pct"]), "rmse_ratio": float(r["rmse_ratio"]), "decision": r["decision"]}
        # modelica sensitivity of the pair
        um = {"dE_pct": 0.0, "rmse_ratio": 0.0}
        signs = {"dE_pct": [np.sign(pm["dE_pct"])], "rmse_ratio": [np.sign(pm["rmse_ratio"] - 1)]}
        nvar = 0
        vf, vs_ = near(M_VAR.get((prof, "fixed"), {})), near(M_VAR.get((prof, "scheduled"), {}))
        for key in set(vf) & set(vs_):
            nvar += 1
            pv = cm.pair(vf[key], vs_[key])
            if soh == 0.8:
                for q in um:
                    um[q] = max(um[q], abs(pm[q] - pv[q]))
                signs["dE_pct"].append(np.sign(pv["dE_pct"]))
                signs["rmse_ratio"].append(np.sign(pv["rmse_ratio"] - 1))
        if soh != 0.8 and 0.8 in [0.8] and (prof, "fixed", 0.8) in M_MOD:  # borrow the SoH 0.8 sensitivity
            pm8 = cm.pair(M_MOD[(prof, "fixed", 0.8)], M_MOD[(prof, "scheduled", 0.8)])
            for key in set(vf) & set(vs_):
                pv = cm.pair(vf[key], vs_[key])
                for q in um:
                    um[q] = max(um[q], abs(pm8[q] - pv[q]))
        pp_s0 = pp if not borrowed else pair_of({"fixed": M_PYS[(prof, "fixed", s0)], "scheduled": M_PYS[(prof, "scheduled", s0)]})  # pair at the SoH whose refinement exists
        for q in ("dE_pct", "rmse_ratio"):
            up = abs(pp_s0[q] - pr[q]) if pr else 0.0
            t = tol_rule(up, um[q], pp[q])
            diff = abs(pm[q] - pp[q])
            dist_mod = abs(pm[q] - (0.0 if q == "dE_pct" else 1.0)) > SAFETY * um[q] and len(set(signs[q])) == 1 and nvar > 0 or (soh == 1.0 and pm[q] == (0.0 if q == "dE_pct" else 1.0))
            dist_py = abs(pp[q] - (0.0 if q == "dE_pct" else 1.0)) > SAFETY * up
            agree = diff <= t
            if soh == 1.0:
                cls = "identical by construction (sanity control)"
            elif agree and dist_mod and dist_py:
                cls = "agree; effect distinguishable from numerical error in both implementations"
            elif (not agree) and dist_mod and dist_py:
                cls = "MISMATCH"
            else:
                cls = "numerically inconclusive (" + ("Modelica effect not distinguishable from its numerical error; " if not dist_mod else "") + ("Python effect not distinguishable from its discretisation error; " if not dist_py else "") + ("agreement criterion " + ("met" if agree else "NOT met")) + ")"
            case = f"{prof}_soh{round(soh * 100):03d}"
            base = dict(case=case, simulation_status="finished successfully" if all(cs.sim_status(root, f'A_{prof}_{k}_soh{round(soh * 100):03d}') == 'finished successfully' for k in ("fixed", "scheduled")) else "see per-case rows")
            add(check_id=f"PR-{case}-{q}", group="pair (scheduled vs fixed)", quantity=q, status=("PASS" if agree else "FAIL"), value_modelica=pm[q], value_python=pp[q], abs_diff=diff,
                tolerance=t, u_py=up, u_mod=um[q], margin_tol_over_diff=(t / diff if diff > 0 else float("inf")), borrowed=("u_py borrowed from SoH 0.8; " if borrowed else "") + ("u_mod borrowed from SoH 0.8" if soh != 0.8 else ""),
                note=f"classification: {cls}; saved table value {sv.get(q)}; python dt=1e-4 value {pr[q] if pr else 'n/a'}; sensitivity variants used: {nvar}", **base)
        add(check_id=f"PR-{case}-decision", group="pair (scheduled vs fixed)", quantity="preregistration section 9 decision (decision-level comparison, not equivalence)",
            status="PASS" if pm["decision"] == pp["decision"] == sv.get("decision") else "FAIL", value_modelica=pm["decision"], value_python=pp["decision"],
            note=f"saved table decision: {sv.get('decision')}", case=case)
        if soh == 1.0:
            add(check_id=f"PR-{case}-sanity", group="pair (scheduled vs fixed)", quantity="SoH 1.0: dE == 0 and RMSE ratio == 1 exactly (prereg sanity control)",
                status="PASS" if (pm["dE_pct"] == 0.0 and pm["rmse_ratio"] == 1.0) else "FAIL", value_modelica=pm["dE_pct"], value_python=pp["dE_pct"],
                note=f"ratio Modelica {pm['rmse_ratio']!r}", case=case)
        summary["pairs"][f"{prof}_soh{soh}"] = {"modelica": pm, "python_saved_recomputed": pp, "python_dt1e-4": pr, "saved_table": sv, "U_mod": um}

# sensitivity summary rows (S1/S2, SoH 0.8): spread of the key metrics over the variants
for (prof, kind), vs in M_VAR.items():
    for name in ("energy_Wh_per_km", "rmse_ms"):
        vals = {f"{k[0]}@{k[1]:g}": m[name] for k, m in vs.items()}
        base_v = M_MOD[(prof, kind, 0.8)][name]
        add(check_id=f"SENS-{prof}-{kind}-{name}", group="numerical sensitivity (Modelica)", quantity=name, status="INFO", value_modelica=base_v,
            abs_diff=max((abs(v - base_v) for v in vals.values()), default=0.0), note="variants: " + "; ".join(f"{k}: {v - base_v:+.3e}" for k, v in vals.items()))

# ---------------------------------------------------------------- archive raw Modelica CSVs and fill hashes
raw = RUNS / "raw"
raw.mkdir(parents=True, exist_ok=True)
sha_of_csv = {}
for name, c in cases.items():
    if c["stage"] not in ("primary", "sens", "ptune"):
        continue
    p = root / c["result_file"]
    if not p.exists():
        continue
    data = p.read_bytes()
    sha_of_csv[name] = cs.sha256(p)
    gz = raw / f"{name}.csv.gz"
    with open(gz, "wb") as f:
        with gzip.GzipFile(fileobj=f, mode="wb", compresslevel=9, mtime=0, filename="") as g:
            g.write(data)
for r in ROWS:
    pth = r["artifact_path"]
    if pth:
        r["artifact_sha256"] = cs.sha256(root / pth) if (root / pth).exists() else ""
        r["artifact_path"] = pth.replace("\\", "/")
cols = list(ROWS[0].keys())
with open(VER / "controller-crosscheck-results.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(ROWS)
nfail = sum(1 for r in ROWS if r["status"] == "FAIL")
summary["counts"] = {s: sum(1 for r in ROWS if r["status"] == s) for s in ("PASS", "FAIL", "INFO", "INCONCLUSIVE")}
summary["raw_csv_sha256_uncompressed"] = sha_of_csv
(RUNS / "evaluation_summary.json").write_text(json.dumps(summary, indent=1, default=float), encoding="utf-8")
print(summary["counts"], "rows:", len(ROWS))
for r in ROWS:
    if r["status"] == "FAIL":
        print("FAIL", r["check_id"], r["abs_diff"], r["tolerance"], r["note"][:160])
