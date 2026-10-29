"""H3 configuration: plant states, limit sets, the three motor-loss scenarios, numerics and validity rules.

Every value cites protocol v1 (section) or the preflight parameter ledger (ID). Nothing here is tuned.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from r4h3 import frozen

L = frozen.load_r3_lib()                                     # also puts eureka and rebuild on sys.path

from eureka.params import load_params  # noqa: E402
from rebuild.model import BatteryLimits  # noqa: E402

# --------------------------------------------------------------------------- plant states (protocol 2.4)
PSTATES = {"P1": dict(soh=1.0, k_r0=0.5), "P3": dict(soh=0.8, k_r0=3.5)}   # P2 is H1-only, not defined here

# --------------------------------------------------------------------------- limit sets (protocol 2.4; AMB-05)
# Identical to LIMS in R3 code/run_gates.py and LIM in code/r3_pilot.py (both frozen-unchanged).
_WIN = dict(v_min_ratio=0.78125, v_max_ratio=1.140625)
LIMITS = {"L-R1": BatteryLimits(c_dis=3.0, c_ch=1.0, **_WIN), "L-EVE": BatteryLimits(c_dis=2.0, c_ch=1.0, **_WIN)}


# --------------------------------------------------------------------------- motor-loss scenarios (protocol 2.3)
@dataclass(frozen=True)
class MotorScenario:
    sid: str
    kind: str
    ledger_id: str
    provenance_class: str
    label: str
    assumptions: str
    validity_limits: str
    qs_usable: bool          # protocol 2.3: M2 is evaluated from dynamic runs only


SCENARIOS = {
    "M0": MotorScenario(
        "M0", "const", "MOT-05", "C (as reference-plant assumption); D as a KT-01 value",
        "M0 constant combined motor+inverter efficiency 0.874",
        "Thesis peak motor 0.92 x inverter 0.95 used as a constant in both directions; zero loss at zero power",
        "Overstates part-load efficiency; no no-load, iron or switching loss; not a KT-01 measurement", True),
    "M1": MotorScenario(
        "M1", "curve", "MOT-06", "D (illustrative structural bracket member)",
        "M1 FASTSim 3.1.0 generic e-machine template curve scaled to 18 kW (illustrative)",
        "Efficiency vs |P_m|/18 kW by linear interpolation, same rule both directions",
        "Package template, not a measurement; NOT a Renault Zoe map and NOT the KT-01 motor", True),
    "M2": MotorScenario(
        "M2", "copper", "MOT-07", "C (transparent stress model)",
        "M2 copper-loss stress model L = k_c T^2, k_c = 18000 (1/0.874 - 1) / 85^2",
        "All loss as copper loss; charges stall loss at standstill",
        "Deliberately favourable to torque smoothing; QS energy not representative; dynamic results only", False),
}


def motor_model(sid: str):
    """The frozen r3_lib motor model for one scenario (never pooled, never substituted)."""
    if sid not in SCENARIOS:
        raise KeyError(f"unknown motor scenario {sid!r}; approved: {sorted(SCENARIOS)}")
    mm = L.motor_models()[sid]
    if mm.kind != SCENARIOS[sid].kind:
        raise RuntimeError(f"r3_lib motor model {sid} has kind {mm.kind}, expected {SCENARIOS[sid].kind}")
    return mm


def params_for(pstate: str):
    """Nominal RP-E parameters (protocol 2.2) with the plant state's k_r0."""
    return load_params().with_overrides(k_r0=PSTATES[pstate]["k_r0"])


# --------------------------------------------------------------------------- numerics (protocol 3, 5, 9)
H = 1.0                                   # reference sampling step [s]
TRACK_W = (3.0, 6.0, 12.0)                # baseline-task window sequence [m/s] (R3 v1 3.3)
TRACK_DV = 0.05                           # baseline-task speed step [m/s]
ECO_DS, ECO_DV = 2.0, 0.1                 # planner distance and speed steps (protocol 5.2)
LAMBDA_LOG10 = (-3.0, 6.0)                # bisection range of log10 lambda (protocol 5.2)
LAMBDA_ITERS = 40
SPEED_DOMAIN_MAX = 50.0 / 3.6             # 0-50 km/h micro-EV domain (02_model_basis.md)

# --------------------------------------------------------------------------- validity rules (protocol 8.2)
RULES = dict(
    shortfall_max_pct=0.1, rmse_max_ms=0.10, max_abs_err_ms=1.0,
    stop_min_duration_s=2.0, stop_settle_s=1.0, stop_speed_max_ms=0.05, stop_distance_max_m=0.10,
    i_over_max_As=0.01, v_min_tol_V=0.01, closure_max_rel=1e-3,
    recompute_energy_rel=1e-4, recompute_distance_rel=1e-6,
)


def scenario_record() -> dict:
    """Machine-readable record of the H3 configuration (config/scenarios_v1.json)."""
    p = load_params()
    return {
        "protocol": str(frozen.PROTOCOL), "protocol_sha256": frozen.FROZEN_SHA256[frozen.PROTOCOL],
        "hypothesis": "H3 only", "plant_branch": "RP-E (declared reference plant; not the KT-01 vehicle)",
        "nominal_params": p.as_dict(),
        "pstates": PSTATES,
        "limits": {k: dict(c_dis=v.c_dis, c_ch=v.c_ch, soh_scaled=v.soh_scaled, v_min_ratio=v.v_min_ratio,
                           v_max_ratio=v.v_max_ratio) for k, v in LIMITS.items()},
        "motor_scenarios": {k: dict(vars(s), r3_lib_label=L.motor_models()[k].label) for k, s in SCENARIOS.items()},
        "numerics": dict(H=H, TRACK_W=TRACK_W, TRACK_DV=TRACK_DV, ECO_DS=ECO_DS, ECO_DV=ECO_DV,
                         LAMBDA_LOG10=LAMBDA_LOG10, LAMBDA_ITERS=LAMBDA_ITERS, dt=p.dt, Ts=p.Ts,
                         SPEED_DOMAIN_MAX=SPEED_DOMAIN_MAX),
        "rules": RULES,
        "controller": "R1 fixed Bryson LQR, eureka.controllers.gain(p_P1, 'fixed'); identical for B0 and B3",
        "excluded": ["SoH-dependent gains", "SoH-dependent limits", "ageing / capacity fade", "retuning",
                     "supervisory layer", "out-of-domain cycles"],
    }


def write_scenario_record(path: Path) -> None:
    Path(path).write_text(json.dumps(scenario_record(), indent=1, default=str), encoding="utf-8")
