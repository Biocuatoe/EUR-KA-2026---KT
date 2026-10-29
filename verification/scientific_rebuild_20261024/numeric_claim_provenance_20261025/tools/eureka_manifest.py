"""Hash every file under D:\\EUREKA before and after the read-only inspection.

    python -I tools/eureka_manifest.py snapshot  -> outputs/eureka_hashes_pre.csv
    python -I tools/eureka_manifest.py verify    -> outputs/eureka_hashes_post.csv and a comparison

Only os.lstat and binary reads (open(..., "rb")) touch D:\\EUREKA. Symlinks are not followed.
Nothing in D:\\EUREKA is executed, written, renamed or moved.
"""

import csv
import hashlib
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

SRC = r"D:\EUREKA"
OUT = Path(__file__).resolve().parent.parent / "outputs"
TZ = timezone(timedelta(hours=7))
FIELDS = ["relpath", "size", "mtime", "ctime", "sha256"]


def iso(ts):
    return datetime.fromtimestamp(ts, TZ).isoformat(timespec="seconds")


def snapshot():
    rows = []
    for dp, dn, fn in os.walk(SRC, followlinks=False):
        dn.sort()
        for f in sorted(fn):
            p = os.path.join(dp, f)
            st = os.lstat(p)
            h = hashlib.sha256()
            with open(p, "rb") as fh:
                for block in iter(lambda: fh.read(1 << 20), b""):
                    h.update(block)
            rows.append({"relpath": os.path.relpath(p, SRC), "size": st.st_size, "mtime": iso(st.st_mtime),
                         "ctime": iso(st.st_ctime), "sha256": h.hexdigest()})
    return rows


def write(rows, name):
    OUT.mkdir(exist_ok=True)
    with open(OUT / name, "w", encoding="utf-8", newline="") as f:
        f.write(f"# source={SRC} taken={datetime.now(TZ).isoformat(timespec='seconds')} files={len(rows)}\n")
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def read(name):
    with open(OUT / name, encoding="utf-8") as f:
        next(f)
        return {r["relpath"]: r for r in csv.DictReader(f)}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "snapshot":
        if (OUT / "eureka_hashes_pre.csv").exists():
            raise SystemExit("pre-inspection snapshot already exists; refusing to overwrite it")
        rows = snapshot()
        write(rows, "eureka_hashes_pre.csv")
        print(f"pre snapshot: {len(rows)} files, {sum(r['size'] for r in rows)} bytes")
    elif mode == "verify":
        pre = read("eureka_hashes_pre.csv")
        rows = snapshot()
        write(rows, "eureka_hashes_post.csv")
        post = {r["relpath"]: r for r in rows}
        added = sorted(set(post) - set(pre))
        removed = sorted(set(pre) - set(post))
        changed = sorted(k for k in set(pre) & set(post)
                         if (pre[k]["sha256"], str(pre[k]["size"]), pre[k]["mtime"])
                         != (post[k]["sha256"], str(post[k]["size"]), post[k]["mtime"]))
        print(f"post snapshot: {len(rows)} files; added {len(added)}, removed {len(removed)}, changed {len(changed)}")
        for k in added + removed + changed:
            print("  DISCREPANCY:", k)
        sys.exit(1 if (added or removed or changed) else 0)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
