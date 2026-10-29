"""Diagnostic (protocol section 12, numerics only): Python plant at a finer step for one traced case. usage: python python_dt_diagnostic.py <root> <profile> <kind> <soh> <dt>"""
import sys, pathlib, time, json
import numpy as np
root = pathlib.Path(sys.argv[1]); prof, kind, soh, dt = sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5])
from eureka.controllers import gain
from eureka.cycles import load_profiles
from eureka.params import load_params
from eureka.plant import IX
from eureka.simulate import simulate
P = load_params(); t0 = time.time()
out = simulate(load_profiles()[prof], [P.with_overrides(dt=dt)], gain(P, kind, soh)[None, :], np.array([soh]))
y1 = out["y_end"][0]
np.savez_compressed(root / f"verification/controller-crosscheck-runs/python_reference/DIAG_{prof}_{kind}_soh{soh:.2f}_dt{dt:g}.npz", v=out["v"][:, 0], T=out["T"][:, 0], u=out["t_ref"][:, 0], dist_t=out["dist"][:, 0], E_chem_t=out["E_chem"][:, 0], i=out["i"][:, 0], dist=y1[IX["dist"]], E_chem=y1[IX["E_chem"]])
print(json.dumps({"dt": dt, "runtime_s": time.time() - t0, "dist_end": float(y1[IX["dist"]]), "E_chem_end": float(y1[IX["E_chem"]])}))
