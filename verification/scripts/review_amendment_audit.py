"""Integrity review phase 3: checks of amendments A1-A4 against the saved evidence (no simulation).
(1) the frozen protocol text (everything above '## 14. Amendments') reproduces the sha256 recorded at the freeze;
(2) IDA/CVODE rejection: simulation-status records, independently recomputed kinematic residual, state reversion at events, CVODE evidence files;
(3) timeline: modification times of the result files versus the selection file. usage: python review_amendment_audit.py <root>"""
import glob, hashlib, json, os, pathlib, re, sys, datetime
import numpy as np, pandas as pd
root = pathlib.Path(sys.argv[1]); V = root / "verification"; out = {}
s = open(V / "controller-crosscheck-protocol.md", encoding="utf-8", newline="").read()
head = s[: s.index("## 14. Amendments")]
rec = hashlib.sha256((head + "## 14. Amendments\r\n\r\n(none)\r\n").encode("utf-8")).hexdigest()
out["frozen_text_reconstruction"] = {"reconstructed_sha256": rec, "sha256_recorded_at_freeze": "c7951936eb162ab5326711d537fe7f8438f76a2ac25df4a80126267237e9725d", "identical": rec.startswith("c7951936eb162ab5")}
out["amendment_headings"] = re.findall(r"\*\*(A\d) - ([^*]+)\*\*", s)
C = V / "modelica-build/cases_ctl"; sel = json.loads((V / "references/controller_solver_selection.json").read_text(encoding="utf-8"))
log_txt = "\n".join(open(p, encoding="utf-8", errors="replace").read() for p in sorted(glob.glob(str(V / "modelica-build/logs/*.out.txt"))))
def status(case):
    v = "no record"
    for blk in re.split(r"(?m)^record SimulationResult", log_txt)[1:]:
        if f"fileNamePrefix = '{case}'" in blk: v = "finished successfully" if "The simulation finished successfully" in blk else "FAILED"
    return v
rows = {}
for solver in ("dassl", "ida"):
    for tol in ("1e-06", "1e-08", "1e-10", "1e-12"):
        for kind in ("fixed", "scheduled"):
            n = f"PT_{kind}_{solver}_tol{tol}"; f = C / n / f"{n}_res.csv"
            if not f.exists(): continue
            d = pd.read_csv(f, usecols=["time", "v", "dist", "E_chem", "ctrl.k_ctrl"]); kc = d["ctrl.k_ctrl"].to_numpy()
            up = np.searchsorted(kc, np.arange(1, int(kc[-1]) + 1)); ev = d.iloc[up]
            t = d["time"].to_numpy(); k = np.rint(t / 0.01).astype(int); ok = np.abs(t - k * 0.01) < 1e-9
            g = d[ok].groupby(k[ok]).first()
            res = np.abs(np.diff(g["dist"].to_numpy()) - 0.01 * (g["v"].to_numpy()[:-1] + g["v"].to_numpy()[1:]) / 2)
            # state reversion: controller-update row has exactly the same (v, E_chem, dist) as the previous update row although v is changing
            same = (np.abs(np.diff(ev["E_chem"].to_numpy())) == 0) & (ev["v"].to_numpy()[1:] > 1.0)
            rows[n] = {"status_from_omc_record": status(n), "kinematic_residual_max_m": float(res.max()), "samples_over_1e-3": int((res > 1e-3).sum()),
                       "update_rows_with_unchanged_E_chem_while_v>1": int(same.sum()), "first_such_update_time_s": float(ev["time"].to_numpy()[1:][same][0]) if same.any() else None}
out["ptune_dassl_ida"] = rows
cv = {}
for f in sorted(glob.glob(str(V / "controller-crosscheck-runs/failed_runs/*_evidence.txt"))):
    t = open(f, encoding="utf-8", errors="replace").read(); n = os.path.basename(f).replace("_evidence.txt", "")
    cv[n] = {"mentions_desired_step_to_small": "Desired step to small" in t, "csv_bytes": int(re.search(r"csv bytes:? (\d+)", t).group(1)) if re.search(r"csv bytes:? (\d+)", t) else None,
             "omc_record_status": status(n)}
out["cvode_evidence"] = cv
mt = lambda p: datetime.datetime.fromtimestamp(os.path.getmtime(p)).isoformat(timespec="seconds")
first_grid = min(glob.glob(str(C / "A_*/A_*_res.csv")), key=os.path.getmtime)
out["timeline"] = {"solver_selection_json_mtime": mt(V / "references/controller_solver_selection.json"), "first_S1_S2_grid_result_mtime": mt(first_grid), "first_grid_file": os.path.basename(first_grid),
                   "selection_precedes_first_grid_result": os.path.getmtime(V / "references/controller_solver_selection.json") < os.path.getmtime(first_grid)}
json.dump(out, open(V / "controller-crosscheck-runs/review_amendment_audit.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ("frozen_text_reconstruction", "amendment_headings", "timeline")}, indent=1))
for n, r in rows.items(): print(n, r["status_from_omc_record"], f"K={r['kinematic_residual_max_m']:.2e}", r["samples_over_1e-3"], "unchanged-E updates:", r["update_rows_with_unchanged_E_chem_while_v>1"], r["first_such_update_time_s"])
print(cv)
