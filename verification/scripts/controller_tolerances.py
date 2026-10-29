"""Numerical-agreement tolerances of the controller cross-check, computed by the rule frozen in the protocol (section 8).

    tol(Q) = SAFETY * (u_py(Q) + u_mod(Q)) + floor(Q)

u_py  : discretisation error of the Python baseline, |Q(dt = 1e-3) - Q(dt = 1e-4)| from the Python-only refinement study
        (verification/references/python_dt_study.json and the stored series); for traces the maximum over the grid of the absolute
        difference of the two Python series.
u_mod : solver sensitivity of the Modelica result, max |Q(selected) - Q(variant)| over the sensitivity runs (tightened tolerance and
        the other solvers) of the same case.
floor : 1e-11 * (largest magnitude of Q), a round-off allowance that is orders of magnitude below any plausible discretisation error.
The rule uses no Modelica-versus-Python difference and no knowledge of the size of the energy effect.
"""
SAFETY = 3.0
FLOOR_REL = 1e-11


def tol(u_py: float, u_mod: float, scale: float) -> float:
    return SAFETY * (abs(u_py) + abs(u_mod)) + FLOOR_REL * abs(scale)
