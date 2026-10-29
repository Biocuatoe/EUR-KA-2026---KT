"""Piecewise-constant-input tests of the Modelica controller block (protocol section 6, P1b).
(A) U_step_original: the reconstructed original test, evaluated with the ORIGINAL (flawed) row grouping -> reproduces the recorded failure.
(B) U_step_original and U_step_semantics evaluated with the defined semantics: the sample at actual event time t_e uses the input value
    current at t_e (post-step iff t_e >= t_step). Mandatory outcome for steps >= 1e-6 s away from every update instant; for a step exactly
    at an update instant either outcome is accepted if it is consistent with the recorded event time, and which one occurred is reported.
usage: python controller_step_tests.py <root>   writes verification/controller-crosscheck-runs/step_input_tests.json"""
import json, pathlib, sys
import numpy as np, pandas as pd
root = pathlib.Path(sys.argv[1]); sys.path.insert(0, str(root / "verification/scripts"))
import controller_series as cs
TS, TMAX, PMAX, GR, EPSW = 0.01, 85.0, 18000.0, 6.5 / 0.28, 1e-6
K = (196.035338058519, 0.3506849472210603, 150.8545190065969)

def law_run(inputs):  # inputs: list of (v, T, vref) per sample -> expected dict of arrays
    z = 0.0; out = {k: [] for k in ("u", "z_used", "e_k", "T_lim_k", "sat_k", "z")}
    for v, T, vr in inputs:
        e = v - vr; tl = min(TMAX, PMAX / max(GR * max(v, 0.0), EPSW)); u = -(K[0] * e + K[1] * T + K[2] * z); sat = u > tl
        out["u"].append(u); out["z_used"].append(z); out["e_k"].append(e); out["T_lim_k"].append(tl); out["sat_k"].append(sat)
        z = z if (sat and e < 0) else z + TS * e; out["z"].append(z)
    return {k: np.array(v) for k, v in out.items()}

def compare(df, exp, rows):
    got = {c: df[f"ctrl.{c}"].to_numpy()[rows] for c in exp}
    return {"max_abs_u": float(np.max(np.abs(got["u"] - exp["u"]))), "max_abs_e_k": float(np.max(np.abs(got["e_k"] - exp["e_k"]))),
            "max_abs_z": float(np.max(np.abs(got["z"] - exp["z"]))), "sat_mismatches": int(np.sum(got["sat_k"].astype(bool) != exp["sat_k"])), "samples": int(len(rows))}

res = {}
# ---- (A) original evaluation method on the original test
p = root / "verification/modelica-build/cases_ctl/U_step_original/U_step_original_res.csv"
df = pd.read_csv(p); t = df["time"].to_numpy(); kk = np.rint(t / TS).astype(int); ok = np.abs(t - kk * TS) < 1e-9
last = {}
for i in np.nonzero(ok)[0]: last[kk[i]] = i                      # ORIGINAL grouping: last row within 1e-9 s of k*Ts
steps = max(last); rows = [last[k] for k in range(steps + 1)]
inputs = [(df.at[r, "v"], df.at[r, "T"], df.at[r, "v_ref"]) for r in rows]
res["A_original_method_on_original_test"] = {**compare(df, law_run(inputs), rows), "file_sha256": cs.sha256(p),
    "note": "reproduces the recorded first failure: input rows and controller rows disagree at the steps because two events lie 1e-13 s apart"}
# ---- (B) defined semantics
def staircase_original(te):
    return (13.0, (0.0 if te < 4 else (-300.0 if te < 8 else 0.0)), (13.3 if te < 4 else 12.95))
ts_, vr_, Tv_ = [2.005, 5.999999, 8.0, 10.000001], [13.3, 13.1, 12.9, 13.2, 12.95], [0, -50, -300, 0, -100]
def staircase_sem(te):
    i = sum(1 for x in ts_ if te >= x); return (13.0, float(Tv_[i]), vr_[i])
for name, fn, steps_t in (("U_step_original", staircase_original, [4.0, 8.0]), ("U_step_semantics", staircase_sem, ts_)):
    p = root / f"verification/modelica-build/cases_ctl/{name}/{name}_res.csv"; df = pd.read_csv(p); kc = df["ctrl.k_ctrl"].to_numpy(); t = df["time"].to_numpy()
    upd = np.searchsorted(kc, np.arange(1, int(kc[-1]) + 1), side="left"); te = t[upd]
    exp = law_run([fn(x) for x in te])
    r = compare(df, exp, upd)
    r["file_sha256"] = cs.sha256(p); r["simulation_status"] = cs.sim_status(root, name); r["updates"] = int(kc[-1]); r["max_event_time_dev_s"] = float(np.max(np.abs(te - np.arange(len(te)) * TS)))
    near = []
    for s in steps_t:
        k_near = int(round(s / TS)); k_pre, k_post = (int(np.floor(s / TS)), int(np.floor(s / TS)) + 1)
        info = {"step_time": s, "distance_to_nearest_update_s": float(abs(s - k_near * TS)), "event_time_of_update_k_near": float(te[k_near]), "event_time_minus_step_time_s": float(te[k_near] - s)}
        sample_after = [k for k in range(len(te)) if te[k] >= s][0]
        info["first_sample_that_saw_the_new_input"] = int(sample_after); info["its_event_time"] = float(te[sample_after])
        got_e = df["ctrl.e_k"].to_numpy()[upd]; 
        info["controller_used_new_input_at_first_sample_after_step"] = bool(abs(got_e[sample_after] - (13.0 - (vr_[ [i for i,x in enumerate(ts_) if x==s][0]+1 ] if name=="U_step_semantics" else 12.95))) < 1e-12) 
        info["controller_used_old_input_at_last_sample_before_step"] = bool(abs(got_e[sample_after - 1] - (13.0 - (vr_[ [i for i,x in enumerate(ts_) if x==s][0] ] if name=="U_step_semantics" else 13.3))) < 1e-12) if sample_after > 0 else None
        near.append(info)
    r["steps"] = near
    r["pass_defined_semantics"] = bool(r["max_abs_u"] <= 1e-9 and r["max_abs_e_k"] <= 1e-9 and r["max_abs_z"] <= 1e-9 and r["sat_mismatches"] == 0 and r["simulation_status"] == "finished successfully")
    res["B_" + name] = r
(root / "verification/controller-crosscheck-runs/step_input_tests.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
print(json.dumps(res, indent=1))
