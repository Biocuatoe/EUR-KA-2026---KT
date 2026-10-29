"""Extract the e-machine efficiency curve of a FASTSim bundled vehicle (M-curve source data).

    <verification/python-env python> -I extract_motor_curve.py   -> ../data/motor_curve_fastsim.json

Runs in the separate FASTSim environment (verification/python-env, FASTSim 3.1.0, installed
2026-10-23; nothing is downloaded). Writes the raw dictionary path, the arrays found, and the
package version, so the curve used by R3 is traceable to the bundled resource.
"""

import json
import sys
from importlib import metadata
from pathlib import Path

import fastsim as fsim

OUT = Path(__file__).resolve().parent.parent / "data" / "motor_curve_fastsim.json"
VEH = "2022_Renault_Zoe_ZE50_R135.yaml"


def find(d, path=()):
    """Yield (path, value) for every leaf whose key mentions efficiency or power fraction."""
    if isinstance(d, dict):
        for k, v in d.items():
            yield from find(v, path + (k,))
    elif isinstance(d, list) and d and not isinstance(d[0], (dict, list)):
        yield path, d
    else:
        yield path, d


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    veh = fsim.Vehicle.from_resource(VEH)
    d = veh.to_pydict()
    hits = {}
    for path, val in find(d):
        key = "/".join(map(str, path))
        low = key.lower()
        if ("em" in low or "machine" in low or "motor" in low) and any(s in low for s in ("eff", "pwr_out_frac", "pwr_in_frac", "pwr_out_max", "frac")):
            hits[key] = val
    OUT.parent.mkdir(exist_ok=True)
    rec = {"fastsim_version": metadata.version("fastsim"), "vehicle_resource": VEH, "fields": hits,
           "top_level_keys": list(d.keys())}
    OUT.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    for k, v in hits.items():
        print(k, (str(v)[:300]))


if __name__ == "__main__":
    main()
