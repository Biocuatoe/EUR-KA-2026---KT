"""Append a timestamped, hash-stamped entry to verification/controller-crosscheck-runlog.md.

usage: python runlog_record.py <project root> "<heading>" "<free text>" [--hash-set freeze|selection|evaluation]
The hash sets list the files whose state matters at that moment (protocol, models, scripts, gains, ...), so any later edit is visible.
"""
import datetime
import glob
import hashlib
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
heading, text = sys.argv[2], sys.argv[3]
hs = sys.argv[sys.argv.index("--hash-set") + 1] if "--hash-set" in sys.argv else ""
V = root / "verification"
sha = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
files = []
if hs in ("freeze", "selection", "evaluation"):
    files += ["verification/controller-crosscheck-protocol.md", "verification/controller-port-design.md", "verification/references/controller_gains.json",
              "verification/references/python_dt_study.json", "verification/modelica/controller_generated_inputs.json", "verification/Invoke-OpenModelica.ps1"]
    files += sorted(str(pathlib.Path(p).relative_to(root)) for p in glob.glob(str(V / "modelica/EurekaPlant/**/*.mo"), recursive=True))
    files += sorted(str(pathlib.Path(p).relative_to(root)) for p in glob.glob(str(V / "modelica/EurekaController/**/*.mo"), recursive=True))
    files += sorted(str(pathlib.Path(p).relative_to(root)) for p in glob.glob(str(V / "scripts/controller_*.py")))
    files += ["verification/scripts/python_reference_runs.py", "verification/scripts/generate_controller_models.py", "verification/scripts/generate_controller_case_scripts.py"]
if hs in ("selection", "evaluation"):
    files += ["verification/references/controller_solver_selection.json", "verification/modelica/scripts/controller_cases.json"]
log = V / "controller-crosscheck-runlog.md"
if not log.exists():
    log.write_text("# Controller cross-check run log (append-only)\n\nEach entry is written by `verification/scripts/runlog_record.py` at the time stated (local clock of the machine).\n", encoding="utf-8")
now = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
lines = [f"\n## {now} - {heading}\n", text + "\n"]
if files:
    lines.append("\n| file | sha256 |\n|---|---|\n")
    for f in dict.fromkeys(files):
        p = root / f
        lines.append(f"| `{f}` | {sha(p)[:64] if p.exists() else 'MISSING'} |\n")
with open(log, "a", encoding="utf-8") as fh:
    fh.writelines(lines)
print("logged:", heading)
