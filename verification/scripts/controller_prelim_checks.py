"""Preliminary checks P1, P2, P4 of the controller protocol (verification/controller-crosscheck-protocol.md section 6).

P1/P2: ControllerUnit result (prescribed inputs) against an independent Python evaluation of the control law (inputs are taken from
       the saved rows of the same result, the law and the integral recursion are re-implemented here from the specification text).
P4   : the gains written into Cases.mo equal controller_gains.json (bitwise after parsing).
Writes verification/controller-crosscheck-runs/preliminary_checks.json.  usage: python controller_prelim_checks.py <project root>
"""
import json
import pathlib
import re
import sys

import numpy as np
import pandas as pd

root = pathlib.Path(sys.argv[1])
sys.path.insert(0, str(root / "verification/scripts"))
import controller_series as cs  # noqa: E402

TS, TMAX, PMAX, GR, EPSW = 0.01, 85.0, 18000.0, 6.5 / 0.28, 1e-6
K = (196.035338058519, 0.3506849472210603, 150.8545190065969)
res_path = root / "verification/modelica-build/cases_ctl/U_unit/U_unit_res.csv"
df = pd.read_csv(res_path)
t = df["time"].to_numpy()
kc = df["ctrl.k_ctrl"].to_numpy()
# the row of the m-th controller update is the first row with k_ctrl == m (post-event values of that sample)
last = {m - 1: int(np.nonzero(kc >= m)[0][0]) for m in range(1, int(kc[-1]) + 1)}
steps = max(last)
out = {"result_file": str(res_path.relative_to(root)), "result_sha256": cs.sha256(res_path), "steps_found": int(steps),
       "simulation_status": cs.sim_status(root, "U_unit")}

# independent evaluation of the law on the inputs the sample actually saw (last row at t_k = post-event input values)
z = 0.0
exp = {"u": [], "z_used": [], "e_k": [], "T_lim_k": [], "sat_k": [], "z_next": []}
for k in range(steps + 1):
    r = last[k]
    v, T, vref = df.at[r, "v"], df.at[r, "T"], df.at[r, "v_ref"]
    e = v - vref
    tl = min(TMAX, PMAX / max(GR * max(v, 0.0), EPSW))
    u = -(K[0] * e + K[1] * T + K[2] * z)
    sat = u > tl
    exp["u"].append(u); exp["z_used"].append(z); exp["e_k"].append(e); exp["T_lim_k"].append(tl); exp["sat_k"].append(sat)
    z = z if (sat and e < 0) else z + TS * e
    exp["z_next"].append(z)
got = {c: np.array([df.at[last[k], f"ctrl.{c}"] for k in range(steps + 1)]) for c in ("u", "z_used", "e_k", "T_lim_k", "sat_k", "z")}
d = {"u": float(np.max(np.abs(got["u"] - exp["u"]))), "z_used": float(np.max(np.abs(got["z_used"] - exp["z_used"]))),
     "e_k": float(np.max(np.abs(got["e_k"] - exp["e_k"]))), "T_lim_k": float(np.max(np.abs(got["T_lim_k"] - exp["T_lim_k"]))),
     "z_next": float(np.max(np.abs(got["z"] - exp["z_next"]))), "sat_k_mismatches": int(np.sum(got["sat_k"].astype(bool) != np.array(exp["sat_k"])))}
sat = np.array(exp["sat_k"]); eneg = np.array(exp["e_k"]) < 0
frozen = sat & eneg
zn, zu = np.array(exp["z_next"]), np.array(exp["z_used"])
d["coverage_samples_sat_and_e_negative"] = int(frozen.sum())
d["coverage_samples_sat_and_e_positive"] = int((sat & ~eneg).sum())
d["coverage_samples_not_sat"] = int((~sat).sum())
d["integral_frozen_exactly_when_sat_and_e_neg"] = bool(np.all(got["z"][frozen] == got["z_used"][frozen]))
d["max_dz_error_when_integrating"] = float(np.max(np.abs((got["z"] - got["z_used"])[~frozen] - TS * np.array(exp["e_k"])[~frozen])))
d["P1_pass"] = bool(max(d["u"], d["z_used"], d["e_k"], d["T_lim_k"], d["z_next"]) <= 1e-9 and d["sat_k_mismatches"] == 0
                    and frozen.sum() > 0 and (sat & ~eneg).sum() > 0 and (~sat).sum() > 0 and d["integral_frozen_exactly_when_sat_and_e_neg"])
out["P1"] = d
# P2 timing
inc = np.nonzero(np.diff(kc) > 0)[0] + 1
et = t[inc]
out["P2"] = {"controller_updates": int(kc[-1]), "expected_updates": int(steps + 1), "max_event_time_deviation_s": float(np.max(np.abs(et - np.rint(et / TS) * TS))),
             "first_event_time": float(et[0]) if len(et) else None, "update_at_final_instant_present": bool(kc[-1] == steps + 1)}
out["P2"]["P2_pass"] = bool(out["P2"]["max_event_time_deviation_s"] <= 1e-9 and kc[-1] in (steps, steps + 1))
# P4 gains in Cases.mo
cases = (root / "verification/modelica/EurekaController/Cases.mo").read_text(encoding="ascii")
gj = json.loads((root / "verification/references/controller_gains.json").read_text(encoding="utf-8"))["gains"]
bad = []
n = 0
for m in re.finditer(r"model (\w+) \"[^\"]*\"\s+extends EurekaController.ClosedLoop\(SoH = ([\d.]+), K_e = ([\d.e+-]+), K_T = ([\d.e+-]+), K_z = ([\d.e+-]+),", cases):
    name, soh = m.group(1), float(m.group(2))
    if name.startswith("PTUNE") and soh != 0.8:
        continue
    kind = "fixed" if "_fixed_" in name else "scheduled"
    key = "fixed_soh1.00" if kind == "fixed" else f"scheduled_soh{soh:.2f}"
    n += 1
    if [float(m.group(i)) for i in (3, 4, 5)] != gj[key]["K"]:
        bad.append(name)
out["P4"] = {"models_checked": n, "mismatching": bad, "P4_pass": bool(n == 18 and not bad)}
(root / "verification/controller-crosscheck-runs").mkdir(parents=True, exist_ok=True)
(root / "verification/controller-crosscheck-runs/preliminary_checks.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print(json.dumps(out, indent=1))
