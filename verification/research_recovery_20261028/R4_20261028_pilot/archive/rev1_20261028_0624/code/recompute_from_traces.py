"""Protocol v1 section 9 'independent recomputation' as a separate script reading only the saved traces.

    python -I -B code/recompute_from_traces.py <output dir>

For every executed run in <output dir>/runs.csv it reads traces/<run_id>.npz and traces/<run_id>.spec.json,
recomputes every metric with r4h3.evaluator in this process, and compares the result with the runs.csv row.
It imports no simulator code (r3_lib, eureka, rebuild, the planner or config); this is asserted before
anything is written. Writes <output dir>/recomputation_independent.csv and recomputation_independent.json
(refuses to overwrite). Exit status 1 if any run fails a protocol check.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

from r4h3 import evaluator, frozen, traces  # noqa: E402

FORBIDDEN = ("r3_lib", "eureka", "rebuild", "r4h3.config", "r4h3.planner", "r4h3.closedloop", "r4h3.campaign")


def _value(s: str):
    if s in ("True", "False"):
        return s == "True"
    try:
        return float(s)
    except ValueError:
        return s


def main(outdir: Path) -> int:
    rows = [{k: _value(v) for k, v in r.items()} for r in csv.DictReader((outdir / "runs.csv").open(encoding="utf-8"))]
    out, n_fail = [], 0
    for r in rows:
        if r.get("executed") is not True:
            out.append(dict(run_id=r["run_id"], recomputed=False, reason=r.get("reason", "not executed")))
            continue
        tpath = outdir / "traces" / f"{r['run_id']}.npz"
        if not tpath.is_file():
            out.append(dict(run_id=r["run_id"], recomputed=False, reason="no evaluable trace (see runs.csv note)"))
            continue
        spec_doc = json.loads((outdir / "traces" / f"{r['run_id']}.spec.json").read_text(encoding="utf-8"))
        a, meta, _ = traces.read_trace(tpath)
        ev = evaluator.evaluate_trace(a, spec_doc["spec"], spec_doc["rules"])
        cmp = evaluator.compare_with_simulator(ev, r, spec_doc["rules"])
        n_fail += not cmp["protocol_ok"]
        row = dict(run_id=r["run_id"], recomputed=True, trace_sha256=frozen.sha256(tpath),
                   spec_sha256=frozen.sha256(outdir / "traces" / f"{r['run_id']}.spec.json"),
                   protocol_ok=cmp["protocol_ok"], diagnostics_ok=cmp["diagnostics_ok"],
                   stop_ok=ev["stop_ok"], complete=ev["complete"], tracking_ok=ev["tracking_ok"],
                   constraint_ok=ev["constraint_ok"])
        row.update({f"{k}": v["value"] for k, v in cmp.items() if isinstance(v, dict)})
        out.append(row)
    leaked = sorted(m for m in sys.modules if m.split(".")[0] in ("r3_lib", "eureka", "rebuild") or m in FORBIDDEN)
    if leaked:
        raise SystemExit(f"STOP: simulator modules were imported: {leaked}")
    p_csv, p_json = outdir / "recomputation_independent.csv", outdir / "recomputation_independent.json"
    for p in (p_csv, p_json):
        if p.exists():
            raise SystemExit(f"refusing to overwrite {p}")
    keys = []
    for r in out:
        keys += [k for k in r if k not in keys]
    with open(p_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    summary = dict(n_rows=len(out), n_recomputed=sum(1 for r in out if r.get("recomputed")), n_protocol_fail=n_fail,
                   simulator_modules_imported=leaked, python=sys.version)
    p_json.write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(json.dumps(summary))
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(Path(sys.argv[1]).resolve()))
