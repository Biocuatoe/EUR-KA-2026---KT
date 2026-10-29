"""File-level comparison of code/ and config/ between an archive and the live pilot (or another archive).
Usage: code_changes.py <pilot_dir> <old_archive_name> <old_label> <new_label> <out_csv> [<new_archive_name>]
Refuses to overwrite out_csv."""
import csv, hashlib, sys
from pathlib import Path

pilot, old, ol, nl, out = Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4], Path(sys.argv[5])
new_root = pilot / "archive" / sys.argv[6] if len(sys.argv) > 6 else pilot
if out.exists():
    sys.exit(f"refused: {out} exists")


def files(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for d in ("code", "config") for p in (root / d).rglob("*")
            if p.is_file() and "__pycache__" not in p.parts and ".pytest_cache" not in p.parts}


a, b = files(pilot / "archive" / old), files(new_root)
rows = []
for k in sorted(set(a) | set(b)):
    st = "added" if k not in a else "removed" if k not in b else "unchanged" if a[k] == b[k] else "changed"
    rows.append((k, st, a.get(k, ""), b.get(k, "")))
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["path", "status", f"sha256_{ol}", f"sha256_{nl}"])
    w.writerows(rows)
for r in rows:
    if r[1] != "unchanged":
        print(r[1], r[0])
print(len(rows), "files compared")
