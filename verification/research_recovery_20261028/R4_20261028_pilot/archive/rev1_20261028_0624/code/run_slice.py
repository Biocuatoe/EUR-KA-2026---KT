"""CLI for the H3 vertical slice. Run from the pilot directory:

    ..\\..\\..\\.venv\\Scripts\\python.exe -I -B code/run_slice.py --cycle S1 --motor M0 --limits L-R1 --pstate P1
"""

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout.reconfigure(encoding="utf-8")

from r4h3 import slice as sl  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycle", required=True, choices=["S1", "S2"])
    ap.add_argument("--motor", required=True, choices=["M0", "M1", "M2"])
    ap.add_argument("--limits", required=True, choices=["L-R1", "L-EVE"])
    ap.add_argument("--pstate", required=True, choices=["P1", "P3"])
    a = ap.parse_args()
    m = sl.run(a.cycle, a.motor, a.limits, a.pstate)
    print("status:", m["status"])
    sys.exit(0 if m["status"] == "PASS" else 1)
