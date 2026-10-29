"""SHA-256, size and mtime of every file under one or more roots (read-only), excluding one directory.

    python -I hash_tree.py <out.csv> <exclude_dir> <root> [<root> ...]
    python -I hash_tree.py --compare <before.csv> <after.csv>
"""
import csv
import hashlib
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot(out, exclude, roots):
    ex = os.path.normcase(os.path.abspath(exclude))
    rows = []
    for root in roots:
        if os.path.isfile(root):
            st = os.stat(root)
            rows.append({"path": root, "bytes": st.st_size, "mtime_ns": st.st_mtime_ns, "sha256": sha256(root)})
            continue
        for dp, dns, fns in os.walk(root):
            dns[:] = [d for d in dns if os.path.normcase(os.path.abspath(os.path.join(dp, d))) != ex]
            for fn in fns:
                p = os.path.join(dp, fn)
                st = os.stat(p)
                rows.append({"path": p, "bytes": st.st_size, "mtime_ns": st.st_mtime_ns, "sha256": sha256(p)})
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["path", "bytes", "mtime_ns", "sha256"])
        w.writeheader()
        w.writerows(rows)
    print(len(rows), "files hashed")


def compare(a, b):
    load = lambda p: {r["path"]: r for r in csv.DictReader(open(p, encoding="utf-8"))}
    A, B = load(a), load(b)
    added, removed = sorted(B.keys() - A.keys()), sorted(A.keys() - B.keys())
    changed = sorted(p for p in A.keys() & B.keys()
                     if (A[p]["sha256"], A[p]["bytes"], A[p]["mtime_ns"]) != (B[p]["sha256"], B[p]["bytes"], B[p]["mtime_ns"]))
    print(f"before {len(A)} after {len(B)} added {len(added)} removed {len(removed)} changed {len(changed)}")
    for tag, lst in (("ADDED", added), ("REMOVED", removed), ("CHANGED", changed)):
        for p in lst:
            print(tag, p)
    return 1 if (added or removed or changed) else 0


if __name__ == "__main__":
    if sys.argv[1] == "--compare":
        sys.exit(compare(sys.argv[2], sys.argv[3]))
    snapshot(sys.argv[1], sys.argv[2], sys.argv[3:])
