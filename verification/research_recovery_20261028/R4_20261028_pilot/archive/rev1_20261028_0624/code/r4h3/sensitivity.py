"""Parameter-sensitivity draws of protocol v1 8.4 (H3): design, mapping and per-draw plant.

    32 draws from scipy.stats.qmc.LatinHypercube(d=7, rng=numpy.random.default_rng(20261028)), default
    scrambling, mapped uniformly onto the seven ranges below (all equal to the preflight ledger's
    uncertainty_range for the same ID). Per draw: v_b and the S-eco profile are recomputed on that draw's
    P1 plant; B0 and B3 run on S2, L-EVE, P1, for M0 and M1 (128 runs). The mapping is a coverage design,
    not a probability statement (protocol 8.4).

Open item AMB-14: the protocol does not say whether the fixed LQR gain of a draw is designed on the nominal
P1 plant or on the draw's P1 plant (eureka.controllers.gain depends on M, A_f, Cd and r_w). gain_for_draw()
refuses to choose: the basis must come from an issued amendment. Until then the 128 runs are BLOCKED.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from r4h3 import config

SEED = 20261028
N_DRAWS = 32
D = 7
COLUMNS = (
    dict(col=1, ledger="VEH-01", param="M", unit="kg", lo=722.5, hi=977.5, applies="all draws"),
    dict(col=2, ledger="VEH-03", param="A_f", unit="m^2", lo=2.0, hi=2.4, applies="all draws"),
    dict(col=3, ledger="VEH-04", param="Cd", unit="-", lo=0.315, hi=0.385, applies="all draws"),
    dict(col=4, ledger="VEH-05", param="Crr", unit="-", lo=0.008, hi=0.012, applies="all draws"),
    dict(col=5, ledger="VEH-06", param="r_w", unit="m", lo=0.265, hi=0.285, applies="all draws"),
    dict(col=6, ledger="BAT-07", param="R0_new", unit="ohm", lo=0.004, hi=0.006, applies="all draws"),
    dict(col=7, ledger="MOT-05", param="eta_M0", unit="-", lo=0.83, hi=0.918, applies="M0 only; ignored by M1"),
)
MOTORS = ("M0", "M1")
LIMITS = "L-EVE"
PSTATE = "P1"
CYCLE = "S2"
GAIN_BASES = ("nominal_P1", "draw_P1")          # the two readings of AMB-14; neither is chosen here
PURPOSE = ("coverage of the declared reference-plant ranges for the H3 sensitivity criterion of protocol 8.1 "
           "(at least 29 of 32 draws with dE_rel <= -1.0 % and none > 0, for M0 and M1 separately)")


def unit_draws() -> np.ndarray:
    from scipy.stats import qmc
    return qmc.LatinHypercube(d=D, rng=np.random.default_rng(SEED)).random(N_DRAWS)


def draws() -> np.ndarray:
    u = unit_draws()
    lo = np.array([c["lo"] for c in COLUMNS])
    hi = np.array([c["hi"] for c in COLUMNS])
    return lo + u * (hi - lo)


def draw_params(row):
    """The draw's plant parameters at P1 (SoH 1, k_r0 0.5): nominal RP-E with columns 1-6 overridden."""
    over = {c["param"]: float(row[c["col"] - 1]) for c in COLUMNS if c["param"] != "eta_M0"}
    return config.params_for(PSTATE).with_overrides(**over)


def draw_motor(row, motor: str):
    """r3_lib motor model for the draw: M0 with the drawn constant efficiency; M1 unchanged (column 7 ignored)."""
    if motor == "M0":
        return config.L.MotorModel("const", eta=float(row[6]), label=f"M0 constant {float(row[6])!r} (draw)")
    if motor == "M1":
        return config.motor_model("M1")
    raise ValueError(f"sensitivity draws use M0 and M1 only (protocol 8.4), not {motor!r}")


def draw_eval_motor_spec(row, motor: str, m1_curve_path: Path) -> dict:
    """The evaluator's independent motor specification for the draw."""
    from r4h3 import evaluator
    if motor == "M0":
        return {"sid": "M0", "kind": "const", "eta": float(row[6])}
    return evaluator.motor_spec_from_protocol(motor, m1_curve_path)


def gain_for_draw(row, basis: str | None):
    """Fixed LQR gain for a draw under an explicitly issued basis (AMB-14). Refuses when the basis is unset."""
    from r4h3.closedloop import fixed_gain
    if basis is None:
        raise RuntimeError("AMB-14 open: the gain basis for sensitivity draws is not set by an issued amendment")
    if basis == "nominal_P1":
        return fixed_gain(config.params_for(PSTATE))
    if basis == "draw_P1":
        return fixed_gain(draw_params(row))
    raise ValueError(f"unknown gain basis {basis!r}; allowed {GAIN_BASES}")


def table_rows() -> list[dict]:
    u, x = unit_draws(), draws()
    rows = []
    for i in range(N_DRAWS):
        r = {"draw": i + 1}
        for c in COLUMNS:
            r[f"u{c['col']}"] = repr(float(u[i, c["col"] - 1]))
            r[f"{c['ledger']}_{c['param']}_{c['unit']}"] = repr(float(x[i, c["col"] - 1]))
        rows.append(r)
    return rows


def design_record() -> dict:
    import scipy
    return {"protocol_section": "8.4", "seed": SEED, "n_draws": N_DRAWS, "d": D,
            "generator": "scipy.stats.qmc.LatinHypercube(d=7, rng=numpy.random.default_rng(20261028)).random(32)",
            "scrambling": "default (scramble=True)", "mapping": "uniform: lo + u (hi - lo)",
            "scipy": scipy.__version__, "numpy": np.__version__, "columns": list(COLUMNS),
            "per_draw": f"recompute v_b and S-eco on the draw's {PSTATE} plant; run B0 and B3 on {CYCLE}, {LIMITS}, "
                        f"{PSTATE}, for {', '.join(MOTORS)}",
            "runs": N_DRAWS * len(MOTORS) * 2, "purpose": PURPOSE,
            "interpretation": "coverage design, not a probability statement; the spread is a sensitivity range, "
                              "never a confidence interval (protocol 7.5)",
            "open_items": {"AMB-14": "gain basis per draw: one of " + " / ".join(GAIN_BASES)}}
