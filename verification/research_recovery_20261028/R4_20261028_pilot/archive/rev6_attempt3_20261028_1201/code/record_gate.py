"""Write the pre-run gate record logs/pre_run_hashes.txt (protocol v1 10.1) after a clean test run.

    python -I -B code/record_gate.py logs/<junit>.xml

Refuses if the record already exists, if the junit run had failures or errors, or if frozen inputs differ.
"""

import json
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout.reconfigure(encoding="utf-8")

from r4h3 import frozen, slice as sl  # noqa: E402

if __name__ == "__main__":
    junit = (frozen.PILOT / sys.argv[1]).resolve()
    if sl.GATE_FILE.exists():
        sys.exit(f"refusing: {sl.GATE_FILE} already exists")
    s = sl.junit_summary(junit)
    if s["tests"] == 0 or s["failures"] or s["errors"]:
        sys.exit(f"refusing: test run not clean {s}")
    rec = {"written": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
           "protocol": str(frozen.PROTOCOL), "protocol_sha256": frozen.FROZEN_SHA256[frozen.PROTOCOL],
           "frozen_inputs": frozen.verify_frozen(),
           "junit_xml": junit.relative_to(frozen.PILOT).as_posix(), "junit_sha256": frozen.sha256(junit), "junit": s,
           "code_sha256": sl.code_hashes()}
    sl.GATE_FILE.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print(json.dumps({k: rec[k] for k in ("written", "protocol_sha256", "junit")}, indent=1))
