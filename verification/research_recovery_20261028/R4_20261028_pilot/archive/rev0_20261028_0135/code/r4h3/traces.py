"""Component F: raw-trace schema r4h3-trace-v1, writer and reader (protocol v1 10.3).

A trace is one compressed .npz per run: one float64 array per channel (same length, finite), plus
`__schema__` (this channel table as JSON) and `__meta__` (run ID, scenario, configuration hash,
initial conditions, ...). The writer refuses incomplete, misaligned or non-finite data.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from r4h3 import SCHEMA_VERSION

# name: (unit, description, source)
CHANNELS = {
    "t_s": ("s", "time of the sample (integration-step grid)", "index * dt"),
    "v_ref_task_mps": ("m/s", "1 s-sampled task reference, linearly interpolated", "task"),
    "stop_ref_flag": ("1", "1 inside a task rest interval [t_a, t_d], else 0", "task"),
    "v_tracked_mps": ("m/s", "profile the controller tracks (v_b for B0, S-eco for B3)", "profile"),
    "v_mps": ("m/s", "vehicle speed state", "integrator"),
    "int_dist": ("m", "position (integrated distance state)", "integrator"),
    "u_cmd_Nm": ("N m", "LQR torque command held over the 10 ms control period", "controller"),
    "z_int_m": ("m", "LQR integral-of-error state used for u_cmd", "controller"),
    "t_cmd_eff_Nm": ("N m", "command after the instantaneous torque limits", "r3_lib"),
    "t_pos_Nm": ("N m", "drive torque limit", "r3_lib.torque_limits"),
    "t_neg_Nm": ("N m", "regeneration torque limit (magnitude)", "r3_lib.torque_limits"),
    "T_Nm": ("N m", "motor torque state", "integrator"),
    "w_radps": ("rad/s", "motor speed", "G/r_w v"),
    "p_mech_W": ("W", "motor mechanical power T w", "r3_lib.battery_current"),
    "p_elec_W": ("W", "electrical power at the motor/inverter input (= p_mech + loss)", "r3_lib.battery_current"),
    "i_A": ("A", "battery current, > 0 discharge", "r3_lib.battery_current"),
    "V1_V": ("V", "RC polarisation voltage state", "integrator"),
    "Vt_V": ("V", "battery terminal voltage V_oc - V1 - R0 i", "derived"),
    "SoC": ("1", "state of charge", "integrator"),
    "P_wheel_W": ("W", "motor force at the wheel times speed (f_w v), < 0 when motor brakes", "r3_lib.derivatives"),
    "P_regen_wheel_W": ("W", "motor-braking power at the wheel, max(-P_wheel, 0)", "derived"),
    "P_fric_W": ("W", "friction-brake power", "r3_lib.derivatives"),
    "batt_feasible": ("1", "1 if the battery power equation has a real solution", "r3_lib.battery_current"),
    "limit_active": ("1", "1 if u_cmd is outside [-t_neg, t_pos]", "derived"),
    "int_E_chem": ("J", "integrated V_oc i", "integrator"),
    "int_E_pos": ("J", "integrated max(V_oc i, 0)", "integrator"),
    "int_E_neg": ("J", "integrated min(V_oc i, 0)", "integrator"),
    "int_E_fb": ("J", "integrated friction-brake energy", "integrator"),
    "int_E_R0": ("J", "integrated R0 i^2", "integrator"),
    "int_E_R1": ("J", "integrated V1^2 / R1", "integrator"),
    "int_E_mi": ("J", "integrated motor/inverter loss", "integrator"),
    "int_I_over": ("A s", "integrated current above the r3_lib window limit (AMB-03)", "integrator"),
    "int_Ah": ("A h", "integrated |i| / 3600", "integrator"),
}
REQUIRED_META = ("run_id", "schema_version", "branch", "cycle", "motor_scenario", "limits", "pstate", "soh", "dt_s",
                 "Ts_s", "initial_conditions", "config_sha256", "gain", "d_ref_m", "T_ref_s")


class TraceError(ValueError):
    pass


def schema_record() -> dict:
    return {"schema_version": SCHEMA_VERSION,
            "channels": [dict(name=k, unit=u, description=d, source=s) for k, (u, d, s) in CHANNELS.items()],
            "required_meta": list(REQUIRED_META)}


def write_trace(path, arrays: dict, meta: dict) -> str:
    path = Path(path)
    if path.exists():
        raise TraceError(f"refusing to overwrite {path}")
    missing = [k for k in CHANNELS if k not in arrays]
    extra = [k for k in arrays if k not in CHANNELS]
    if missing or extra:
        raise TraceError(f"channel mismatch: missing {missing}, unexpected {extra}")
    n = {len(np.asarray(arrays[k])) for k in CHANNELS}
    if len(n) != 1 or n == {0}:
        raise TraceError(f"channels differ in length or are empty: {sorted(n)}")
    for k in CHANNELS:
        a = np.asarray(arrays[k], dtype=float)
        if not np.all(np.isfinite(a)):
            raise TraceError(f"non-finite values in channel {k}")
    mm = [k for k in REQUIRED_META if k not in meta]
    if mm:
        raise TraceError(f"missing meta fields: {mm}")
    if meta["schema_version"] != SCHEMA_VERSION:
        raise TraceError("schema version mismatch")
    np.savez_compressed(path, __schema__=np.array(json.dumps(schema_record())),
                        __meta__=np.array(json.dumps(meta, default=str)),
                        **{k: np.asarray(arrays[k], dtype=np.float64) for k in CHANNELS})
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_trace(path):
    with np.load(path, allow_pickle=False) as z:
        schema = json.loads(str(z["__schema__"]))
        meta = json.loads(str(z["__meta__"]))
        if schema.get("schema_version") != SCHEMA_VERSION:
            raise TraceError(f"unsupported schema {schema.get('schema_version')}")
        arrays = {c["name"]: np.array(z[c["name"]]) for c in schema["channels"]}
    return arrays, meta, schema
