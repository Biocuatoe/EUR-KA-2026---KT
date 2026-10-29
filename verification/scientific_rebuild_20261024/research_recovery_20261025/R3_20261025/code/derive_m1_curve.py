"""Derive the R3 M1 (M-curve) loss-model data from the extracted FASTSim e-machine curve.

    python -I derive_m1_curve.py      (any Python with the standard library)

Input : ../data/motor_curve_fastsim.json         (extract_motor_curve.py, FASTSim 3.1.0)
        ../data/fastsim_source_record.json       (extract_fastsim_source.py: module and YAML hashes)
Output: ../data/motor_curve_m1_derived.json      (the only curve r3_lib uses for M1)

Transformation (fixed before any R3 outcome was computed; R3_motor_curve_audit.md section 5):
    x   = |P_m| / 18 000 W           (P_m = motor shaft mechanical power; 18 kW = thesis P_max)
    eta = linear interpolation of the source values over the source grid x in [0, 1]
    motoring      P_e = P_m / eta(x)       (as FASTSim)
    regeneration  P_e = P_m * eta(x)       (R3 assumption; FASTSim 3.1.0 itself uses eta(0) = 0.84)
    x > 1 cannot occur in R3 (|T| <= min(85 N m, 18 kW / w)); r3_lib clamps to eta(1) and test_r3_supplementary checks x <= 1.
The efficiency values are used unchanged (no rescaling to the thesis's 0.874).
"""

import hashlib
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"


def main():
    src = DATA / "motor_curve_fastsim.json"
    rec = json.loads(src.read_text(encoding="utf-8"))
    f = rec["fields"]
    grid = f["pt_type/BEV/em/eff_interp_achieved/data/grid"][0]["data"]
    vals = f["pt_type/BEV/em/eff_interp_achieved/data/values/data"]
    assert f["pt_type/BEV/em/eff_interp_achieved/strategy"] == "Linear"
    assert len(grid) == len(vals) == 11 and grid[0] == 0.0 and grid[-1] == 1.0
    assert all(b > a for a, b in zip(grid, grid[1:]))
    assert all(0.0 < v < 1.0 for v in vals)
    srcrec = json.loads((DATA / "fastsim_source_record.json").read_text(encoding="utf-8"))
    out = {
        "branch": "M1 (M-curve)",
        "quantity": "combined motor + power-electronics efficiency vs mechanical output-power fraction (FASTSim ElectricMachine)",
        "frac": grid, "eff": vals,
        "p_rated_W": 18000.0,
        "source": {
            "package": f"fastsim {rec['fastsim_version']}", "resource": rec["vehicle_resource"],
            "field": "pt_type/BEV/em/eff_interp_achieved (strategy Linear, extrapolate Error)",
            "source_pwr_out_max_W": f["pt_type/BEV/em/pwr_out_max_watts"],
            "module_sha256": srcrec["module_sha256"], "embedded_yaml_sha256": srcrec["extracted_sha256"],
            "extraction_json": src.name, "extraction_json_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
        },
        "transformation": [
            "x = |P_m| / 18000 W (source normalises by its own 100 kW pwr_out_max)",
            "eta values unchanged; linear interpolation on the source grid",
            "motoring P_e = P_m / eta(x); regeneration P_e = P_m * eta(x) (R3 assumption; FASTSim 3.1.0 uses eta(0) in regeneration)",
            "x > 1 does not occur (torque/power envelope); clamped to eta(1) if it did",
        ],
        "status": "illustrative generic shape; not a measurement of the Zoe machine or of the thesis motor",
    }
    dst = DATA / "motor_curve_m1_derived.json"
    dst.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(dst.name, hashlib.sha256(dst.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
