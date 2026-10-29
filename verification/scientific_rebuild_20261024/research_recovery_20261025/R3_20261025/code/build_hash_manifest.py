"""Final SHA-256 manifest of every R3 file, with its status against the freeze record.

    python -I build_hash_manifest.py      -> ../R3_hash_manifest.csv

status: frozen-unchanged | changed-after-freeze | new-after-freeze. Excludes the manifest itself.
"""

import csv
import hashlib
import time
from pathlib import Path

R3 = Path(__file__).resolve().parent.parent
OUT = R3 / "R3_hash_manifest.csv"


def main():
    frozen = {}
    for line in (R3 / "logs" / "protocol_v1_sha256_at_freeze.txt").read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            h, p = line.split(None, 1)
            frozen[p.strip()] = h
    rows = []
    for f in sorted(R3.rglob("*")):
        if not f.is_file() or f == OUT or "__pycache__" in f.parts:
            continue
        rel = f.relative_to(R3).as_posix()
        h = hashlib.sha256(f.read_bytes()).hexdigest()
        st = ("frozen-unchanged" if frozen[rel] == h else "changed-after-freeze") if rel in frozen else "new-after-freeze"
        rows.append(dict(path=rel, bytes=f.stat().st_size, modified=time.strftime("%Y-%m-%dT%H:%M:%S",
                         time.localtime(f.stat().st_mtime)), sha256=h, freeze_status=st,
                         frozen_sha256=frozen.get(rel, "")))
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        if r["freeze_status"] != "new-after-freeze":
            print(r["freeze_status"], r["path"])
    print(len(rows), "files")


if __name__ == "__main__":
    main()
