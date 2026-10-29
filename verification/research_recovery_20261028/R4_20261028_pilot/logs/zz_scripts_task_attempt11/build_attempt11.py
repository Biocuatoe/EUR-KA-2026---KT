"""Copy code/, config/ and inputs/ from the pilot into a NEW release-attempt directory and verify every copy.
Usage: build_attempt11.py <pilot_dir> <attempt_dir> <readiness_gate_json>
Refuses if attempt_dir exists. Verifies: every copied file's SHA-256 equals its source; the copy's code and config
files equal the code_sha256 map of the readiness gate; nothing outside code/, config/, inputs/ is copied."""
import csv, hashlib, json, shutil, sys
from pathlib import Path

pilot, dst, gate = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve()
if dst.exists():
    sys.exit(f"refused: {dst} exists")
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
src = [p for d in ("code", "config", "inputs") for p in sorted((pilot / d).rglob("*"))
       if p.is_file() and "__pycache__" not in p.parts and ".pytest_cache" not in p.parts]
rows, bad = [], []
for p in src:
    rel = p.relative_to(pilot)
    q = dst / rel
    q.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, q)
    a, b = sha(p), sha(q)
    rows.append((rel.as_posix(), p.stat().st_size, a, b, a == b))
    if a != b:
        bad.append(rel.as_posix())
g = json.loads(gate.read_text(encoding="utf-8"))["code_sha256"]
gate_bad = [k for k, v in g.items() if not (dst / k).is_file() or sha(dst / k) != v]
extra = [r[0] for r in rows if (r[0].startswith(("code/", "config/")) and r[0] not in g)]
(dst / "logs").mkdir()
out = dst / "logs" / "copy_verification_attempt11.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["path", "bytes", "sha256_source_pilot", "sha256_copy", "equal"])
    w.writerows(rows)
summary = dict(source=str(pilot), target=str(dst), files_copied=len(rows), copy_mismatches=bad,
               readiness_gate=str(gate), readiness_gate_sha256=sha(gate), gate_code_files=len(g),
               gate_mismatches=gate_bad, copied_code_or_config_files_not_in_gate=extra)
(dst / "logs" / "copy_verification_attempt11_summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
print(json.dumps(summary, indent=1))
sys.exit(1 if bad or gate_bad else 0)
