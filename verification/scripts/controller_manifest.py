"""Artifact manifest for the controller cross-check integrity review. Hashes files in place (nothing is moved, deleted or modified).
Writes verification/controller-crosscheck-artifact-manifest.csv: path, size, sha256, category, role, git_state (tracked / untracked / ignored-by-rule).
usage: python controller_manifest.py <root>"""
import csv, fnmatch, hashlib, pathlib, subprocess, sys
root = pathlib.Path(sys.argv[1]); V = root / "verification"
items = []   # (path, category, role)
def add(pattern, cat, role, base=root):
    for p in sorted(base.glob(pattern)):
        if p.is_file(): items.append((p, cat, role))
add("verification/controller-crosscheck-protocol.md", "protocol", "frozen protocol v1.0 + amendments A1-A4 (appended)")
add("verification/controller-crosscheck-runlog.md", "protocol", "append-only run log with frozen hashes and timestamps")
add("verification/controller-port-design.md", "protocol", "controller reconstruction and port design")
add("verification/controller-crosscheck-report.md", "report", "final cross-check report (original record, unmodified by the review)")
add("verification/controller-crosscheck-results.csv", "results", "aggregated check table (784 rows)")
add("verification/references/controller_gains.json", "gains", "frozen gains (independent 50-digit design) and comparison with saved gains")
add("verification/references/controller_solver_selection.json", "solver", "P-TUNE solver-study outcome and selection")
add("verification/references/python_dt_*.json", "python-reference", "Python step-size study summaries")
add("verification/controller-crosscheck-runs/*.json", "results", "evaluation summary / preliminary / step-input tests")
add("verification/controller-crosscheck-runs/*.csv", "results", "P-TUNE solver-study table")
add("verification/controller-crosscheck-runs/raw/*", "modelica-raw-gz", "gzip of each Modelica result CSV (mtime=0)")
add("verification/controller-crosscheck-runs/python_reference/*", "python-reference", "Python reference series at refined dt (npz)")
add("verification/controller-crosscheck-runs/failed_runs/*", "solver", "evidence for runs stopped by the output guard / by hand")
add("verification/modelica/EurekaController/**/*.mo", "source", "controller Modelica sources", )
for p in sorted((V / "modelica/EurekaController").rglob("*")):
    if p.is_file() and p.suffix in (".mo", ".order"): items.append((p, "source", "controller Modelica source"))
for p in sorted((V / "modelica/EurekaPlant").rglob("*")):
    if p.is_file() and p.suffix in (".mo", ".order"): items.append((p, "source", "plant Modelica source (unchanged)"))
add("verification/modelica/scripts/*.mos", "source", "OpenModelica scripts (generated + diagnostics)")
add("verification/modelica/scripts/controller_cases.json", "source", "case table")
add("verification/modelica/controller_generated_inputs.json", "source", "hashes of generator inputs/outputs")
for n in ("controller_*.py", "python_reference_runs.py", "python_dt_*.py", "guarded_run.py", "runlog_record.py", "generate_controller_*.py"):
    add(f"verification/scripts/{n}", "source", "script used in the cross-check")
add("verification/Invoke-OpenModelica.ps1", "source", "launcher")
add("verification/scripts/review_*.py", "source", "integrity-review script (saved-record calculations only)")
add("verification/scripts/controller_manifest.py", "source", "manifest generator")
add("verification/controller-crosscheck-integrity-review.md", "report", "integrity review")
# simulation-status records and omc logs of the controller phase (in the git-ignored modelica-build tree)
for p in sorted((V / "modelica-build/logs").glob("*")):
    if p.is_file() and p.name >= "20261023-2239" and any(t in p.name for t in ("ctl", "diag_ida", "diag_maxstep")): items.append((p, "sim-status-log", "launcher stdout / summary: contains the omc SimulationResult records"))
add("verification/modelica-build/python_reference_runs.log", "python-reference", "log of the Python step-size study")
add("verification/modelica-build/guarded_*.log", "sim-status-log", "guarded_run.py console logs")
add("verification/modelica-build/ctl_ptune.console.txt", "sim-status-log", "first P-TUNE launch console (crashed after the CVODE runaway)")
for d in sorted((V / "modelica-build/cases_ctl").glob("*")):
    for p in sorted(d.glob("*")):
        if p.suffix in (".csv", ".log"): items.append((p, "modelica-raw-uncompressed" if p.suffix == ".csv" else "sim-status-log", "uncompressed result / solver log of case " + d.name))
# baseline Python artifacts (read only) and preregistration
for r in ("artifacts/raw/primary/S1/manifest.json", "artifacts/raw/primary/S1/timeseries.npz", "artifacts/raw/primary/S2/manifest.json", "artifacts/raw/primary/S2/timeseries.npz",
          "artifacts/tables/primary_metrics.csv", "artifacts/tables/primary_pairs.csv", "artifacts/reports/primary_results.json", "protocol/preregistration.md", "configs/parameters.yaml", "configs/cycles/profiles.yaml"):
    items.append((root / r, "baseline-readonly", "saved Python baseline / preregistration / configuration"))
seen = set(); rows = []
tracked = set(subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True, encoding="utf-8").stdout.splitlines())
rels = [str(p.relative_to(root)).replace("\\", "/") for p, _, _ in items]
ign = set(subprocess.run(["git", "check-ignore", "--stdin"], cwd=root, input=(("\n").join(rels) + "\n").encode("utf-8"), capture_output=True).stdout.decode("utf-8").splitlines())  # bytes: text mode would send CRLF and git would read CR as part of the path
for (p, cat, role), rel in zip(items, rels):
    if rel in seen or not p.exists(): continue
    seen.add(rel)
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 24), b""): h.update(chunk)
    rows.append({"path": rel, "size_bytes": p.stat().st_size, "sha256": h.hexdigest(), "category": cat, "role": role,
                 "git_state": "tracked" if rel in tracked else ("ignored-by-rule" if rel in ign else "untracked")})
with open(V / "controller-crosscheck-artifact-manifest.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
from collections import Counter
print(len(rows), "files;", sum(r["size_bytes"] for r in rows) / 1e6, "MB"); print(Counter((r["category"], r["git_state"]) for r in rows))
