"""Load configs/parameters.yaml with provenance validation and unit checking."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from pathlib import Path
from typing import Literal

import pint
import yaml
from pydantic import BaseModel, ConfigDict, model_validator

from eureka import REPO_DIR

PARAMS_PATH = REPO_DIR / "configs" / "parameters.yaml"
ureg = pint.UnitRegistry()

Provenance = Literal["measured", "literature", "report_unverified", "assumed", "standard"]


class Uncertainty(BaseModel):
    model_config = ConfigDict(extra="forbid")
    low: float
    high: float
    justification: str


class Param(BaseModel):
    model_config = ConfigDict(extra="forbid")
    value: float
    unit: str
    provenance: Provenance
    source: str
    source_location: str
    valid_range: tuple[float, float]
    uncertainty: Uncertainty | None
    used_for: str

    @model_validator(mode="after")
    def _ranges(self) -> Param:
        lo, hi = self.valid_range
        if not lo <= self.value <= hi:
            raise ValueError(f"value {self.value} outside valid_range {self.valid_range}")
        if self.uncertainty is not None:
            u = self.uncertainty
            if not (lo <= u.low <= self.value <= u.high <= hi):
                raise ValueError("uncertainty range must bracket the value inside valid_range")
        ureg.Unit(self.unit)  # raises on an unknown unit
        return self


# Unit each parameter is converted to (also asserts its dimension) -> field of PlantParams.
TARGET = {
    "vehicle.mass": ("kg", "M"),
    "vehicle.frontal_area": ("m^2", "A_f"),
    "vehicle.drag_coefficient": ("dimensionless", "Cd"),
    "vehicle.rolling_resistance": ("dimensionless", "Crr"),
    "vehicle.wheel_radius": ("m", "r_w"),
    "vehicle.air_density": ("kg/m^3", "rho"),
    "vehicle.gravity": ("m/s^2", "g"),
    "drivetrain.gear_ratio": ("dimensionless", "G"),
    "drivetrain.gear_efficiency": ("dimensionless", "eta_g"),
    "drivetrain.motor_inertia": ("kg*m^2", "J_m"),
    "drivetrain.motor_viscous_friction": ("N*m*s", "B_m"),
    "drivetrain.motor_inverter_efficiency": ("dimensionless", "eta_mi"),
    "drivetrain.torque_max": ("N*m", "T_max"),
    "drivetrain.power_max": ("W", "P_max"),
    "drivetrain.speed_max": ("rad/s", "w_max"),
    "drivetrain.torque_time_constant": ("s", "tau_T"),
    "battery.open_circuit_voltage": ("V", "V_oc"),
    "battery.capacity": ("A*h", "Q_Ah"),
    "battery.r0_new": ("ohm", "R0_new"),
    "battery.r1_new": ("ohm", "R1_new"),
    "battery.c1": ("F", "C1"),
    "battery.k_r0": ("dimensionless", "k_r0"),
    "battery.k_r1": ("dimensionless", "k_r1"),
    "simulation.integration_step": ("s", "dt"),
    "simulation.speed_smoothing": ("m/s", "v_eps"),
    "simulation.velocity_noise_std": ("m/s", "noise_std"),
    "controller.sample_time": ("s", "Ts"),
    "controller.linearisation_speed": ("m/s", "v0"),
    "controller.bryson_velocity_error_max": ("m/s", "e_max"),
    "controller.bryson_torque_max": ("N*m", "T_bryson"),
    "controller.bryson_integral_error_max": ("m", "z_max"),
    "controller.gamma_v": ("dimensionless", "gamma_v"),
    "controller.gamma_u": ("dimensionless", "gamma_u"),
}


@dataclass(frozen=True)
class Params:
    """All model and controller parameters in SI (A*h for capacity)."""

    M: float
    A_f: float
    Cd: float
    Crr: float
    r_w: float
    rho: float
    g: float
    G: float
    eta_g: float
    J_m: float
    B_m: float
    eta_mi: float
    T_max: float
    P_max: float
    w_max: float
    tau_T: float
    V_oc: float
    Q_Ah: float
    R0_new: float
    R1_new: float
    C1: float
    k_r0: float
    k_r1: float
    dt: float
    v_eps: float
    noise_std: float
    Ts: float
    v0: float
    e_max: float
    T_bryson: float
    z_max: float
    gamma_v: float
    gamma_u: float

    @property
    def M_eff(self) -> float:
        return self.M + self.J_m * self.G**2 / self.r_w**2

    def with_overrides(self, **kw: float) -> Params:
        return replace(self, **kw)

    def as_dict(self) -> dict:
        return {f.name: getattr(self, f.name) for f in fields(self)}


def load_registry(path: Path = PARAMS_PATH) -> dict[str, Param]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    out = {}
    for group, items in raw.items():
        if not isinstance(items, dict):
            continue
        for name, spec in items.items():
            out[f"{group}.{name}"] = Param.model_validate(spec)
    return out


def load_params(path: Path = PARAMS_PATH) -> Params:
    reg = load_registry(path)
    missing = set(TARGET) - set(reg)
    extra = set(reg) - set(TARGET)
    if missing or extra:
        raise ValueError(f"parameter registry mismatch: missing={missing} extra={extra}")
    values = {}
    for key, (unit, field) in TARGET.items():
        p = reg[key]
        values[field] = ureg.Quantity(p.value, p.unit).to(unit).magnitude
    return Params(**values)


def uncertainty_ranges(path: Path = PARAMS_PATH) -> dict[str, tuple[float, float]]:
    """Field name -> (low, high) in target units, for parameters with an uncertainty range."""
    reg = load_registry(path)
    out = {}
    for key, (unit, field) in TARGET.items():
        u = reg[key].uncertainty
        if u is not None:
            q = [ureg.Quantity(x, reg[key].unit).to(unit).magnitude for x in (u.low, u.high)]
            out[field] = (q[0], q[1])
    return out
