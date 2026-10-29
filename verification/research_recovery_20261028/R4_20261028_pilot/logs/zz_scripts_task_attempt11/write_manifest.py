"""Write a self-excluding SHA-256 manifest of a directory. Refuses to overwrite either output.
Usage: write_manifest.py <root> <manifest_rel> <sha_txt_abs> [<extra excluded rel path>...]
The manifest excludes itself, the sha txt (if inside root) and the extra paths, plus __pycache__/ and *.pyc."""
import csv, hashlib, sys, time
from pathlib import Path

root, man = Path(sys.argv[1]).resolve(), sys.argv[2]
txt = Path(sys.argv[3]).resolve()
extra = set(sys.argv[4:])
mp = root / man
for p in (mp, txt):
    if p.exists():
        sys.exit(f"refused: {p} exists")
excl = {man} | extra
try:
    excl.add(txt.relative_to(root).as_posix())
except ValueError:
    pass
pyc = [p for p in root.rglob("*") if p.is_file() and ("__pycache__" in p.parts or p.suffix == ".pyc")]
rows = []
for p in sorted(root.rglob("*"), key=lambda q: q.relative_to(root).as_posix()):
    rel = p.relative_to(root).as_posix()
    if not p.is_file() or rel in excl or "__pycache__" in p.parts or p.suffix == ".pyc":
        continue
    rows.append((rel, p.stat().st_size, hashlib.sha256(p.read_bytes()).hexdigest()))
with open(mp, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["path", "bytes", "sha256"])
    w.writerows(rows)
h = hashlib.sha256(mp.read_bytes()).hexdigest()
txt.write_text(f"{mp.name} SHA-256 {h}\n{len(rows)} files listed; written {time.strftime('%Y-%m-%d %H:%M:%S %z')}\n"
               f"root: {root}\nexcluded: {sorted(excl)}; __pycache__/ and *.pyc ({len(pyc)} present)\n",
               encoding="utf-8", newline="\n")
print(txt.read_text(encoding="utf-8"))
