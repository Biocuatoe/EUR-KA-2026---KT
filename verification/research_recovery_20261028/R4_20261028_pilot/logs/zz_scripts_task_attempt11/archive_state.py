"""Copy the pilot's code/, config/ and the given top-level files into archive/<name>/ with an ARCHIVE_INDEX.csv.
Refuses if the target exists. Usage: archive_state.py <pilot_dir> <name> <top-level file>..."""
import csv, hashlib, shutil, sys
from pathlib import Path

pilot, name, tops = Path(sys.argv[1]), sys.argv[2], sys.argv[3:]
dst = pilot / "archive" / name
if dst.exists():
    sys.exit(f"refused: {dst} exists")
files = [p for d in ("code", "config") for p in sorted((pilot / d).rglob("*"))
         if p.is_file() and "__pycache__" not in p.parts and ".pytest_cache" not in p.parts]
files += [pilot / t for t in tops]
rows = []
for p in files:
    rel = p.relative_to(pilot)
    q = dst / rel
    q.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, q)
    h1 = hashlib.sha256(p.read_bytes()).hexdigest()
    h2 = hashlib.sha256(q.read_bytes()).hexdigest()
    if h1 != h2:
        sys.exit(f"copy mismatch {rel}")
    rows.append((q.relative_to(pilot).as_posix(), rel.as_posix(), h1))
with open(dst / "ARCHIVE_INDEX.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["archived_path", "original_path", "sha256"])
    w.writerows(rows)
print(len(rows), "files archived to", dst)
