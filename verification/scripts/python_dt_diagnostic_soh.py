"""Diagnostic (protocol section 12, numerics only; written after the grid results): Python dt = 1e-4 for SoH 0.9 and 0.7, S1 and S2, fixed and scheduled,
so that u_py need not be borrowed from SoH 0.8. Same storage layout as python_reference_runs.py. usage: python python_dt_diagnostic_soh.py <root> <profile>"""
import sys, pathlib, time
import numpy as np
root = pathlib.Path(sys.argv[1]); prof = sys.argv[2]
from eureka.controllers import gain
from eureka.cycles import load_profiles
from eureka.params import load_params
from eureka.plant import IX
from eureka.simulate import simulate
P = load_params(); dt = 1e-4
cases = [(k, s) for s in (0.9, 0.7) for k in ("fixed", "scheduled")]
out = simulate(load_profiles()[prof], [P.with_overrides(dt=dt)] * 4, np.vstack([gain(P, k, s) for k, s in cases]), np.array([s for _, s in cases]))
for j, (kind, soh) in enumerate(cases):
    y1, y0 = out["y_end"][j], out["y0"][j]
    d = {nm: float(y1[IX[nm]] - y0[IX[nm]]) for nm in ("E_chem", "dist", "E_fb", "E_regen", "E_R0", "E_R1", "Ah")}
    np.savez_compressed(root / f"verification/controller-crosscheck-runs/python_reference/{prof}_{kind}_soh{soh:.2f}_dt0.0001.npz", t=out["t"][:, j], gains=out["gains"][j],
        v=out["v"][:, j], v_ref=out["v_ref"][:, j], T=out["T"][:, j], u=out["t_ref"][:, j], t_lim=out["t_lim"][:, j], sat=out["sat"][:, j], z=out["z"][:, j], i=out["i"][:, j],
        E_chem_t=out["E_chem"][:, j], dist_t=out["dist"][:, j], **d)
print("done", prof)
