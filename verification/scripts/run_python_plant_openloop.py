"""Run the project's corrected PYTHON plant (eureka.plant, RK4) on the open-loop torque schedule of
verification/modelica-plant-specification.md section 11, for comparison with the Modelica plant.

Run with the project's locked .venv (read-only use of the project code). Output is written under
verification/modelica-build/python_reference/ (git-ignored generated output). The Modelica side never reads
these files while it runs, and this script never reads any Modelica output: the comparison is made afterwards.

usage: python run_python_plant_openloop.py <project root> <h seconds> [C_rr multiplier]
"""
import hashlib
import json
import pathlib
import sys
import time

import numpy as np

from eureka.params import load_params
from eureka.plant import IX, BatchParams, derivatives, initial_state, rk4_step

root = pathlib.Path(sys.argv[1])
h = float(sys.argv[2])
crr_mult = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
SOH = 0.8
TSW = [0, 10, 20, 30, 38, 46, 56]
TVAL = [85.0, 20.0, 0.0, -40.0, -200.0, -20.0, 10.0]
T_END = 66.0
REC = 0.01

P = load_params()
if crr_mult != 1.0:
    P = P.with_overrides(Crr=P.Crr * crr_mult)
bp = BatchParams.from_params([P], np.array([SOH]))
n_steps = round(T_END / h)
rec_every = round(REC / h)
sw_steps = [round(t / h) for t in TSW]          # switches fall exactly on step boundaries
assert all(abs(s * h - t) < 1e-9 for s, t in zip(sw_steps, TSW))


def t_ref_at(step):
    k = 0
    for i, s in enumerate(sw_steps):
        if step >= s:
            k = i
    return TVAL[k]


STATES = ["v", "T", "V1", "SoC", "E_chem", "E_rr", "E_aero", "E_fb", "E_gear", "E_visc", "E_mi", "E_R0", "E_R1", "E_regen", "dist", "Ah"]
rows = []
y = initial_state(1)
y0 = y.copy()
gr = bp.G / bp.r_w
t0 = time.time()
for k in range(n_steps + 1):
    tr = t_ref_at(k)
    if k % rec_every == 0:
        arr = np.array([tr])
        dy, aux = derivatives(y, arr, bp)
        v = max(float(y[0, IX["v"]]), 0.0)
        T = float(y[0, IX["T"]])
        w = float(gr[0]) * v
        ts = T - float(bp.B_m[0]) * w
        f_w = float(gr[0]) * ts * float(bp.eta_g[0]) if ts >= 0 else float(gr[0]) * ts / float(bp.eta_g[0])
        f_rr = float(bp.Crr[0] * bp.M[0] * bp.g[0]) * np.tanh(v / float(bp.v_eps[0]))
        f_aero = 0.5 * float(bp.rho[0] * bp.Cd[0] * bp.A_f[0]) * v * v
        f_fb = float(aux["f_fb"][0])
        p_m = T * w
        p_e = p_m / float(bp.eta_mi[0]) if p_m >= 0 else p_m * float(bp.eta_mi[0])
        ke = 0.5 * float(bp.M_eff[0]) * (float(y[0, IX["v"]]) ** 2 - float(y0[0, IX["v"]]) ** 2)
        ec1 = 0.5 * float(bp.C1[0]) * (float(y[0, IX["V1"]]) ** 2 - float(y0[0, IX["V1"]]) ** 2)
        sinks = ke + ec1 + sum(float(y[0, IX[x]] - y0[0, IX[x]]) for x in ("E_rr", "E_aero", "E_fb", "E_gear", "E_visc", "E_mi", "E_R0", "E_R1"))
        row = {"time": k * h, "T_ref": tr}
        row.update({s: float(y[0, IX[s]]) for s in STATES})
        row.update({"F_w": f_w, "F_rr": float(f_rr), "F_aero": f_aero, "F_fb": f_fb, "F_net": f_w - float(f_rr) - f_aero - f_fb,
                    "a": float(dy[0, IX["v"]]), "P_m": p_m, "P_e": p_e, "I": float(aux["i"][0]), "T_lim": float(aux["t_lim"][0]),
                    "closure": float(y[0, IX["E_chem"]] - y0[0, IX["E_chem"]]) - sinks})
        rows.append(row)
    if k < n_steps:
        y, feasible = rk4_step(y, np.array([tr]), bp, h)
        assert bool(feasible[0]), f"battery power infeasible at step {k}"
elapsed = time.time() - t0

out = root / "verification/modelica-build/python_reference"
out.mkdir(parents=True, exist_ok=True)
tag = f"h{h:g}" + (f"_Crr{crr_mult:g}" if crr_mult != 1.0 else "")
path = out / f"openloop66_python_{tag}.csv"
cols = list(rows[0].keys())
with open(path, "w", encoding="ascii", newline="") as f:
    f.write(",".join(cols) + "\n")
    for r in rows:
        f.write(",".join(repr(float(r[c])) for c in cols) + "\n")
meta = {"file": str(path.relative_to(root)).replace("\\", "/"), "step_s": h, "rows": len(rows), "elapsed_s": round(elapsed, 1), "SoH": SOH,
        "schedule": {"t": TSW, "T_ref": TVAL}, "Crr_multiplier": crr_mult, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "plant": "eureka.plant.rk4_step (fixed-step RK4), parameters from eureka.params.load_params()"}
(out / f"openloop66_python_{tag}.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
print(json.dumps(meta, indent=2))
