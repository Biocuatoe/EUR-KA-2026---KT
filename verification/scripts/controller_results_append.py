"""Append the preliminary-check and solver-study rows to verification/controller-crosscheck-results.csv (run after controller_eval.py).
usage: python controller_results_append.py <root>"""
import csv, json, pathlib, sys
root = pathlib.Path(sys.argv[1]); V = root / "verification"
sys.path.insert(0, str(V / "scripts")); import controller_series as cs
p = V / "controller-crosscheck-results.csv"
rows = list(csv.DictReader(open(p, encoding="utf-8"))); cols = list(rows[0].keys())
rows = [r for r in rows if not r["group"].startswith(("preliminary", "solver study"))]
def add(**kw):
    r = {c: "" for c in cols}; r.update({k: (f"{v:.17g}" if isinstance(v, float) else v) for k, v in kw.items()}); rows.append(r)
pc = json.loads((V / "controller-crosscheck-runs/preliminary_checks.json").read_text(encoding="utf-8"))
art = pc["result_file"].replace("\\", "/")
add(check_id="P1", group="preliminary checks", case="U_unit", quantity="controller arithmetic with ramp inputs (max |u| error vs independent evaluation)", status="PASS" if pc["P1"]["P1_pass"] else "FAIL",
    abs_diff=pc["P1"]["u"], tolerance=1e-9, note=f"coverage: {pc['P1']['coverage_samples_sat_and_e_negative']} samples saturated with e<0, {pc['P1']['coverage_samples_sat_and_e_positive']} saturated with e>0, {pc['P1']['coverage_samples_not_sat']} unsaturated; sat mismatches {pc['P1']['sat_k_mismatches']}",
    simulation_status=pc["simulation_status"], artifact_path=art, artifact_sha256=pc["result_sha256"])
add(check_id="P2", group="preliminary checks", case="U_unit", quantity="controller update times vs k*Ts", status="PASS" if pc["P2"]["P2_pass"] else "FAIL", abs_diff=pc["P2"]["max_event_time_deviation_s"], tolerance=1e-9,
    note=f"updates {pc['P2']['controller_updates']} of {pc['P2']['expected_updates']}", artifact_path=art, artifact_sha256=pc["result_sha256"])
add(check_id="P4", group="preliminary checks", case="Cases.mo", quantity="gains in Cases.mo equal controller_gains.json (bitwise)", status="PASS" if pc["P4"]["P4_pass"] else "FAIL", note=f"{pc['P4']['models_checked']} models",
    artifact_path="verification/modelica/EurekaController/Cases.mo", artifact_sha256=cs.sha256(V / "modelica/EurekaController/Cases.mo"))
st = json.loads((V / "controller-crosscheck-runs/step_input_tests.json").read_text(encoding="utf-8"))
a = st["A_original_method_on_original_test"]
add(check_id="P1b-original-failure", group="preliminary checks", case="U_step_original", quantity="RECORDED FAILURE reproduced: original evaluation method on the step-input test", status="INFO", abs_diff=a["max_abs_u"],
    note=f"max|u| diff {a['max_abs_u']!r}, max|e_k| diff {a['max_abs_e_k']!r}, sat mismatches {a['sat_mismatches']}: {a['note']}", artifact_path="verification/modelica-build/cases_ctl/U_step_original/U_step_original_res.csv", artifact_sha256=a["file_sha256"])
for k in ("B_U_step_original", "B_U_step_semantics"):
    b = st[k]
    add(check_id=f"P1b-{k[2:]}", group="preliminary checks", case=k[2:], quantity="piecewise-constant inputs, defined semantics (update at event time t_e uses the input current at t_e)", status="PASS" if b["pass_defined_semantics"] else "FAIL",
        abs_diff=max(b["max_abs_u"], b["max_abs_e_k"], b["max_abs_z"]), tolerance=1e-9, simulation_status=b["simulation_status"],
        note="; ".join(f"step {s['step_time']}: update nearest to the step at event time {s['event_time_minus_step_time_s']:+.3e} s from the step" for s in b["steps"]), artifact_path=f"verification/modelica-build/cases_ctl/{k[2:]}/{k[2:]}_res.csv", artifact_sha256=b["file_sha256"])
sel = json.loads((V / "references/controller_solver_selection.json").read_text(encoding="utf-8"))
study = {(r["solver"], float(r["tol"])): r for r in csv.DictReader(open(V / "controller-crosscheck-runs/ptune_solver_study.csv", encoding="utf-8"))}
for n, r in sel["runs"].items():
    q = study.get((r["solver"], r["tol"]))
    add(check_id=f"SS-{n}", group="solver study (P-TUNE)", case=n, quantity=f"{r['solver']} tol {r['tol']:g}: admissible / qualifies", status="PASS" if (q and q["qualifies"] == "True") else ("INFO" if r["admissible"] else "FAIL"),
        value_modelica=(r["sim_time_s"] if r["sim_time_s"] == r["sim_time_s"] else ""), abs_diff=(r.get("kin_resid_max_m") or ""), tolerance=("1e-3 (criterion K)" if r["admissible"] is not None else ""),
        simulation_status=r["status"], note=f"admissible={r['admissible']}; kinematic residual {r.get('kin_resid_max_m')}; qualifies={q['qualifies'] if q else 'n/a'}; max err/allow={q['max_err_over_allow'][:8] if q else 'n/a'}; selected={sel['selected']}" )
with open(p, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
print(len(rows), "rows")
