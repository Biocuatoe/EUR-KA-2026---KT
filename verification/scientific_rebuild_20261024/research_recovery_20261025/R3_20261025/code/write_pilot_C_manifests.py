"""Write the R3-C manifests that the original runs failed to write (post-run repair; no simulation).

    python -I write_pilot_C_manifests.py

The three `r3_pilot.py C <M>` processes crashed after writing runs.csv, at the manifest step
(1 x 3 gain passed to float(); logs/pilot_C_*.err.txt). This writes manifest.json with the same fields,
marked as written afterwards, plus the runs.csv hash. Code hashes are those on disk now, i.e. after
the one-line fix in r3_pilot.py; the hash of r3_pilot.py as run is not recoverable and is stated so.
"""

import hashlib
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r3_pilot as P  # noqa: E402


def main():
    p = P.load_params().with_overrides(k_r0=0.5)
    K = np.ravel(P.r1_gain(p, "fixed"))
    for mk in ("M0", "M1", "M2"):
        root = P.OUTC / mk
        if (root / "manifest.json").exists():
            continue
        runs = root / "runs.csv"
        n = sum(1 for _ in runs.open(encoding="utf-8")) - 1
        P.manifest(root, "C", dict(motor=mk, n_runs=n, gain=[float(x) for x in K],
                                   runs_csv_sha256=hashlib.sha256(runs.read_bytes()).hexdigest(),
                                   note="written afterwards by write_pilot_C_manifests.py: the run crashed at its manifest "
                                        "step after runs.csv was complete (logs/pilot_C_%s.err.txt). r3_pilot.py hash below "
                                        "is after the one-line manifest fix; the simulation code was unchanged by it." % mk))
        print(mk, "manifest written", n, "runs")


if __name__ == "__main__":
    main()
