"""Dimensional audit of the report's state-space model (Eqs. 4.1-4.4).

For x_dot = A x + B u, every term A_ij * x_j and B_i * u must carry the units of x_dot_i.
Symbols are given their physical units (values are irrelevant to the audit), so the check
does not depend on the report's missing numerical values for L_eq, K_e, K_t or v0.
"""

from __future__ import annotations

import pint

ureg = pint.UnitRegistry()
Q_ = ureg.Quantity

# Physical units of the symbols in Eq. 4.3 (report Table 8 / nomenclature)
SYM = {
    "rho": Q_(1, "kg/m^3"),
    "Cd": Q_(1, ""),
    "Af": Q_(1, "m^2"),
    "v0": Q_(1, "m/s"),
    "M": Q_(1, "kg"),
    "G": Q_(1, ""),
    "eta": Q_(1, ""),
    "r_w": Q_(1, "m"),
    "R_int": Q_(1, "ohm"),
    "L_eq": Q_(1, "H"),
    "K_e": Q_(1, "V*s/rad"),
    "K_t": Q_(1, "N*m/A"),
    "J_m": Q_(1, "kg*m^2"),
    "B_m": Q_(1, "N*m*s"),
}
# Units of states, derivatives and input (Pint treats rad as dimensionless).
STATE = {"v": Q_(1, "m/s"), "i": Q_(1, "A"), "w": Q_(1, "rad/s")}
DERIV = {k: v / Q_(1, "s") for k, v in STATE.items()}
INPUT = Q_(1, "N*m")  # T_ref, motor torque reference

s = SYM
A_REPORT = {
    ("v", "v"): -s["rho"] * s["Cd"] * s["Af"] * s["v0"] / s["M"],
    ("v", "w"): s["G"] * s["eta"] / (s["M"] * s["r_w"]),
    ("i", "i"): -s["R_int"] / s["L_eq"],
    ("i", "w"): s["K_e"] / s["L_eq"],
    ("w", "i"): -s["K_t"] / s["J_m"],
    ("w", "w"): -s["B_m"] / s["J_m"],
}
B_REPORT = {"w": 1 / s["J_m"]}


def _same(a: pint.Quantity, b: pint.Quantity) -> bool:
    return a.dimensionality == b.dimensionality


def audit_report_a_matrix() -> list[dict]:
    """Return one record per non-zero term with its units and the expected units."""
    out = []
    for (row, col), coef in A_REPORT.items():
        term = coef * STATE[col]
        out.append(
            {
                "term": f"A[{row},{col}] * {col}",
                "term_units": f"{term.units:~}",
                "expected_units": f"{DERIV[row].units:~}",
                "consistent": _same(term, DERIV[row]),
            }
        )
    for row, coef in B_REPORT.items():
        term = coef * INPUT
        out.append(
            {
                "term": f"B[{row}] * T_ref",
                "term_units": f"{term.units:~}",
                "expected_units": f"{DERIV[row].units:~}",
                "consistent": _same(term, DERIV[row]),
            }
        )
    return out
