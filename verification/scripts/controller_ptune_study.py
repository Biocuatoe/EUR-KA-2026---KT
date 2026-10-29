"""Solver study on P-TUNE (protocol section 7). Applies the frozen selection rule; writes
verification/references/controller_solver_selection.json and verification/controller-crosscheck-runs/ptune_solver_study.csv.
usage: python controller_ptune_study.py <project root>
"""
import csv
import glob
import json
import pathlib
import re
import sys

import numpy as np

root = pathlib.Path(sys.argv[1])
sys.path.insert(0, str(root / "verification/scripts"))
import controller_metrics as cm  # noqa: E402
import controller_series as cs  # noqa: E402
from controller_tolerances import FLOOR_REL  # noqa: E402

STEPS = 12231
TS_ = 0.01
cases = {k: v for k, v in json.loads((root / "verification/modelica/scripts/controller_cases.json").read_text(encoding="utf-8")).items() if v["stage"] == "ptune"}
PYDIR = root / "verification/controller-crosscheck-runs/python_reference"
VO = 48.0


def acc(sd):
    return {"v": sd["v"], "T": sd["T"], "u": sd["u"]}


def py_series(kind, dt):
    z = np.load(PYDIR / f"P-TUNE_{kind}_soh0.80_dt{dt:g}.npz")
    return {k: z[k] for k in z.files}


def sim_time(case):
    for lp in sorted(glob.glob(str(root / "verification/modelica-build/logs/*.out.txt"))):
        txt = open(lp, encoding="utf-8", errors="replace").read()
        for blk in re.split(r"(?m)^record SimulationResult", txt)[1:]:
            if f"fileNamePrefix = '{case}'" in blk:
                m = re.search(r"timeSimulation = ([\d.eE+-]+)", blk)
                return float(m.group(1)) if m else float("nan")
    return float("nan")


def quantities(sd_f, sd_s):
    mf, ms = cm.metrics(sd_f), cm.metrics(sd_s)
    p = cm.pair(mf, ms)
    q = {"E_fixed": mf["energy_Wh_per_km"], "E_sched": ms["energy_Wh_per_km"], "rmse_fixed": mf["rmse_ms"], "rmse_sched": ms["rmse_ms"],
         "dE_pct": p["dE_pct"], "rmse_ratio": p["rmse_ratio"]}
    return q


def series_for(sd):
    return {"v": sd["v"], "T": sd["T"], "u": sd["u"]}


def complete(sd):
    """Fill the final-sample discrete quantities (control law, protocol P2) if the final update was not written; not needed for the rule's quantities."""
    return sd


# ---- Python u_py
pyf3, pyf4 = py_series("fixed", 1e-3), py_series("fixed", 1e-4)
pys3, pys4 = py_series("scheduled", 1e-3), py_series("scheduled", 1e-4)


def py_metric_series(z):
    return {"v": z["v"], "v_ref": z["v_ref"], "i": z["i"], "sat": z["sat"], "u": z["u"], "E_chem": float(z["E_chem"]), "dist": float(z["dist"]),
            "E_fb": float(z["E_fb"]), "E_regen": float(z["E_regen"]), "E_R0": float(z["E_R0"]), "E_R1": float(z["E_R1"]), "Ah": float(z["Ah"])}


q3 = quantities(py_metric_series(pyf3), py_metric_series(pys3))
q4 = quantities(py_metric_series(pyf4), py_metric_series(pys4))
u_py = {k: abs(q3[k] - q4[k]) for k in q3}
for kind, a, b in (("fixed", pyf3, pyf4), ("sched", pys3, pys4)):
    for tr in ("v", "T", "u"):
        u_py[f"{tr}_{kind}_trace"] = float(np.max(np.abs(a[tr] - b[tr])))
scale = {k: abs(q4[k]) for k in q4}

# ---- Modelica results
runs = {}
for name, c in cases.items():
    m = re.match(r"PT_(fixed|scheduled)_(\w+)_tol([\d.e+-]+)", name)
    kind, solver, tol = m.group(1), m.group(2), float(m.group(3))
    path = root / c["result_file"]
    rec = {"case": name, "kind": kind, "solver": solver, "tol": tol, "status": cs.sim_status(root, name), "file": str(path.relative_to(root)), "sim_time_s": sim_time(name)}
    ok = path.exists() and rec["status"] == "finished successfully"
    if ok:
        try:
            sd, info = cs.load_modelica(path, STEPS)
            rec["info"] = info
            rec["nan_cells"] = info["nan_cells"]
            ok = info["nan_cells"] == 0 and info["updates"] >= STEPS
            sdm = {"v": sd["v"], "v_ref": sd["v_ref"], "i": sd["I"], "sat": np.nan_to_num(sd["sat_k"], nan=0.0), "u": np.nan_to_num(sd["u"], nan=0.0),
                   "E_chem": float(sd["E_chem"][-1]), "dist": float(sd["dist"][-1]), "E_fb": float(sd["E_fb"][-1]), "E_regen": float(sd["E_regen"][-1]),
                   "E_R0": float(sd["E_R0"][-1]), "E_R1": float(sd["E_R1"][-1]), "Ah": float(sd["Ah"][-1])}
            rec["series"] = sdm
            rec["trace"] = {"v": sd["v"], "T": sd["T"], "u": np.nan_to_num(sd["u"], nan=0.0)}
            thr = VO * 3600.0 * sdm["Ah"]
            rec["closure_rel"] = float(abs(sd["closure"][-1]) / thr)
            rec["vmin"] = float(np.min(sd["v"]))
            rec["kin_resid_max_m"] = float(np.max(np.abs(np.diff(sd["dist"]) - TS_ * (sd["v"][:-1] + sd["v"][1:]) / 2)))  # amendment A2, criterion K
            rec["kin_violations"] = int(np.sum(np.abs(np.diff(sd["dist"]) - TS_ * (sd["v"][:-1] + sd["v"][1:]) / 2) > 1e-3))
            ok = ok and np.all(np.isfinite(sd["v"])) and rec["closure_rel"] <= 1e-3 and rec["vmin"] >= -1e-6 and rec["kin_resid_max_m"] <= 1e-3
        except Exception as ex:  # noqa: BLE001
            rec["error"] = repr(ex)
            ok = False
    rec["admissible"] = bool(ok)
    runs[name] = rec

configs = sorted({(r["solver"], r["tol"]) for r in runs.values()}, key=lambda x: (x[1], x[0]))
avail = {}
for (solver, tol) in configs:
    f, s = runs.get(f"PT_fixed_{solver}_tol{tol:g}"), runs.get(f"PT_scheduled_{solver}_tol{tol:g}")
    if f and s and f["admissible"] and s["admissible"]:
        q = quantities(f["series"], s["series"])
        avail[(solver, tol)] = {"q": q, "tr": {"fixed": f["trace"], "sched": s["trace"]}}

# ---- reference: smallest admissible tolerance, CVODE preferred, then IDA
ref_key = None
for tol in sorted({t for (_, t) in avail}):
    for solver in ("cvode", "ida", "dassl"):
        if (solver, tol) in avail:
            ref_key = (solver, tol)
            break
    if ref_key:
        break
out = {"admissible_configurations": [f"{s}@{t:g}" for (s, t) in sorted(avail, key=lambda x: (x[1], x[0]))],
       "failed_or_inadmissible": {n: (r["status"], r.get("error", ""), r.get("nan_cells")) for n, r in runs.items() if not r["admissible"]},
       "u_py_P-TUNE_dt1e-3_vs_1e-4": u_py}
rows = []
if ref_key is None:
    out["outcome"] = "inconclusive: no admissible reference configuration"
else:
    # reference's own uncertainty: the other independent integrator at the same tolerance, if admissible
    other = [(s, ref_key[1]) for s in ("cvode", "ida", "dassl") if s != ref_key[0] and (s, ref_key[1]) in avail]
    ref = avail[ref_key]
    u_ref = {}
    for k in ref["q"]:
        u_ref[k] = abs(ref["q"][k] - avail[other[0]]["q"][k]) if other else 0.0
    for kind in ("fixed", "sched"):
        for tr in ("v", "T", "u"):
            u_ref[f"{tr}_{kind}_trace"] = float(np.max(np.abs(ref["tr"][kind][tr] - avail[other[0]]["tr"][kind][tr]))) if other else 0.0
    out["reference"] = f"{ref_key[0]}@{ref_key[1]:g}"
    out["reference_second_integrator"] = f"{other[0][0]}@{other[0][1]:g}" if other else "none admissible at that tolerance (u_ref set to 0, flagged)"
    out["u_ref"] = u_ref
    qualifying = []
    for key, a in sorted(avail.items(), key=lambda x: (x[0][1], x[0][0])):
        err = {k: abs(a["q"][k] - ref["q"][k]) for k in a["q"]}
        for kind in ("fixed", "sched"):
            for tr in ("v", "T", "u"):
                err[f"{tr}_{kind}_trace"] = float(np.max(np.abs(a["tr"][kind][tr] - ref["tr"][kind][tr])))
        allow = {k: max(0.1 * u_py.get(k, 0.0), 3 * u_ref.get(k, 0.0), FLOOR_REL * scale.get(k, max(abs(ref["q"].get(k, 0.0)), 1.0))) for k in err}
        # trace floors use the signal magnitude
        for k in err:
            if k.endswith("_trace"):
                allow[k] = max(0.1 * u_py.get(k, 0.0), 3 * u_ref.get(k, 0.0), FLOOR_REL * 100.0)
        fail = [k for k in err if err[k] > allow[k]]
        q_ok = not fail
        rt = (runs[f"PT_fixed_{key[0]}_tol{key[1]:g}"]["sim_time_s"], runs[f"PT_scheduled_{key[0]}_tol{key[1]:g}"]["sim_time_s"])
        rows.append({"solver": key[0], "tol": key[1], "is_reference": key == ref_key, "qualifies": q_ok, "failing_quantities": ";".join(fail),
                     "max_err_over_allow": max(err[k] / allow[k] for k in err), **{f"err_{k}": err[k] for k in err}, **{f"allow_{k}": allow[k] for k in err},
                     "sim_time_fixed_s": rt[0], "sim_time_sched_s": rt[1]})
        if q_ok:
            qualifying.append(key)
    out["qualifying"] = [f"{s}@{t:g}" for s, t in qualifying]
    das = sorted([k for k in qualifying if k[0] == "dassl"], key=lambda x: -x[1])
    if das:
        sel = das[0]
        out["selected"] = {"solver": sel[0], "tolerance": sel[1], "rule": "loosest qualifying DASSL tolerance"}
    elif qualifying:
        sel = sorted(qualifying, key=lambda x: -x[1])[0]
        out["selected"] = {"solver": sel[0], "tolerance": sel[1], "rule": "no DASSL tolerance qualifies; loosest qualifying configuration of any solver"}
    else:
        out["selected"] = None
        out["outcome"] = "inconclusive: no configuration qualifies"
runs_summary = {n: {k: r.get(k) for k in ("kind", "solver", "tol", "status", "admissible", "sim_time_s", "closure_rel", "vmin", "error", "nan_cells", "kin_resid_max_m", "kin_violations")} for n, r in runs.items()}
out["runs"] = runs_summary
(root / "verification/references/controller_solver_selection.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
if rows:
    keys = sorted({k for r in rows for k in r})
    with open(root / "verification/controller-crosscheck-runs/ptune_solver_study.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
print(json.dumps({k: out.get(k) for k in ("admissible_configurations", "reference", "reference_second_integrator", "qualifying", "selected", "outcome")}, indent=1))
print("not admissible:", json.dumps(out["failed_or_inadmissible"], indent=1)[:1500])
for r in rows:
    print(f"{r['solver']:6s} {r['tol']:g}  qualifies={r['qualifies']}  max err/allow={r['max_err_over_allow']:.3g}  failing={r['failing_quantities']}  t={r['sim_time_fixed_s']:.1f}s")
