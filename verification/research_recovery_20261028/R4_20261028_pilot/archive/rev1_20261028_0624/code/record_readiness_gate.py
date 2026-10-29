"""Write the readiness gate record logs/readiness_gate_v2.json after a clean test run (versioned; review CR-A14).

    python -I -B code/record_readiness_gate.py logs/<junit>.xml

This is not the protocol 10.1 campaign gate (logs/pre_run_hashes.txt of the campaign directory). It binds the
readiness test run to the SHA-256 of every code and config file, the protocol and the frozen and upstream inputs.
Refuses if the record exists, if the junit run had failures or errors, or if any frozen input differs.
"""

import json
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout.reconfigure(encoding="utf-8")

from r4h3 import campaign, frozen, inputs, slice as sl  # noqa: E402

if __name__ == "__main__":
    junit = (frozen.PILOT / sys.argv[1]).resolve()
    if campaign.READINESS_GATE.exists():
        sys.exit(f"refusing: {campaign.READINESS_GATE} already exists")
    s = sl.junit_summary(junit)
    if s["tests"] == 0 or s["failures"] or s["errors"]:
        sys.exit(f"refusing: test run not clean {s}")
    rec = {"written": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "kind": "readiness gate (not the campaign gate)",
           "protocol": str(frozen.PROTOCOL), "protocol_sha256": frozen.FROZEN_SHA256[frozen.PROTOCOL],
           "frozen_and_upstream_inputs": frozen.verify_frozen({**frozen.FROZEN_SHA256, **frozen.UPSTREAM_SHA256}),
           "canonical_cycle_inputs": inputs.verify_all(),
           "junit_xml": junit.relative_to(frozen.PILOT).as_posix(), "junit_sha256": frozen.sha256(junit), "junit": s,
           "code_sha256": sl.code_hashes()}
    campaign.READINESS_GATE.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print(json.dumps({k: rec[k] for k in ("written", "protocol_sha256", "junit")}, indent=1))
