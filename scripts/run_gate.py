"""Verification gate (preregistration section 11). Must pass before any evaluation run.

    python scripts/run_gate.py

Runs the full test suite on a clean working tree and checks the tuning acceptance record.
Writes artifacts/reports/verification-gate.json tied to the current Git commit.
"""

import json
import subprocess
import sys
import xml.etree.ElementTree as ET

from eureka import ROOT_DIR
from eureka.lineage import run_context
from eureka.params import load_params


def main() -> int:
    ctx = run_context()
    reports = ROOT_DIR / "artifacts" / "reports"
    junit = reports / f"gate-pytest-{(ctx['git']['commit'] or 'none')[:12]}.xml"
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", f"--junitxml={junit}"],
        capture_output=True,
        text=True,
        check=False,
    )
    suite = ET.parse(junit).getroot().find("testsuite")
    counts = {k: int(suite.get(k, 0)) for k in ("tests", "failures", "errors", "skipped")}

    tuning = json.loads((reports / "tuning-acceptance.json").read_text(encoding="utf-8"))
    tuning_ok = tuning["accepted_e_max"] == load_params().e_max

    passed = (
        proc.returncode == 0
        and counts["failures"] == 0
        and counts["errors"] == 0
        and tuning_ok
        and not ctx["git"]["dirty"]
    )
    gate = {
        "context": ctx,
        "pytest_exit": proc.returncode,
        "counts": counts,
        "junit": str(junit),
        "tuning_accepted": tuning_ok,
        "clean_tree": not ctx["git"]["dirty"],
        "passed": passed,
        "pytest_tail": proc.stdout.splitlines()[-3:],
    }
    (reports / "verification-gate.json").write_text(json.dumps(gate, indent=2), encoding="utf-8")
    print(json.dumps({k: gate[k] for k in ("counts", "tuning_accepted", "clean_tree", "passed")}))
    print("commit", ctx["git"]["commit"])
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
