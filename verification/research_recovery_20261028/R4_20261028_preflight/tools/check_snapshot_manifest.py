"""Read-only integrity check of the GATE1_20261028 evidence snapshot (R4 preflight, Phase 0).

Checks, for every manifest row:
  S1 snapshot file exists
  S2 snapshot size == recorded source_size_bytes
  S3 sha256(snapshot file) == recorded snapshot_sha256
  S4 recorded source_sha256 == source_sha256_end == snapshot_sha256 (manifest internal consistency)
  S5 verified == "True" and error is empty
and, with --source, for every manifest row:
  R1 source file exists
  R2 sha256(source file, read now) == recorded source_sha256
It also lists snapshot files that are not in the manifest and, with --source, files under each
source root (directory walk, metadata only) that the manifest does not cover.

All files are opened with mode "rb". Nothing is written except the two output files given on
the command line, which must lie outside both trees.
"""
import argparse
import csv
import hashlib
import json
import os
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def norm(p):
    return os.path.normcase(os.path.normpath(p))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("snapshot_root")
    ap.add_argument("out_csv")
    ap.add_argument("out_json")
    ap.add_argument("--source", action="store_true", help="also re-hash source files read-only")
    ap.add_argument("--source-root", action="append", default=[],
                    help="source root to walk (metadata only) for uncovered files")
    a = ap.parse_args()

    manifest = os.path.join(a.snapshot_root, "MANIFEST.sha256.csv")
    for out in (a.out_csv, a.out_json):
        for root in [a.snapshot_root] + a.source_root:
            if norm(out).startswith(norm(root)):
                sys.exit(f"refusing to write inside a checked tree: {out}")

    with open(manifest, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    results = []
    fail = Counter()
    for r in rows:
        snap = r["snapshot_path"]
        res = {"source_path": r["source_path"], "snapshot_path": snap}
        res["S1_exists"] = os.path.isfile(snap)
        if res["S1_exists"]:
            res["S2_size"] = os.path.getsize(snap) == int(r["source_size_bytes"])
            h = sha256(snap)
            res["S3_snapshot_hash"] = h == r["snapshot_sha256"].upper()
        else:
            res["S2_size"] = res["S3_snapshot_hash"] = False
        res["S4_manifest_consistent"] = (
            r["source_sha256"].upper() == r["source_sha256_end"].upper() == r["snapshot_sha256"].upper())
        res["S5_flag"] = r["verified"] == "True" and r["error"] == ""
        if a.source:
            src = r["source_path"]
            res["R1_source_exists"] = os.path.isfile(src)
            res["R2_source_hash_now"] = (sha256(src) == r["source_sha256"].upper()) if res["R1_source_exists"] else False
        for k, v in res.items():
            if isinstance(v, bool) and not v:
                fail[k] += 1
        results.append(res)

    listed = {norm(r["snapshot_path"]) for r in rows}
    unlisted_snapshot = []
    for dp, _, fns in os.walk(a.snapshot_root):
        for fn in fns:
            p = os.path.join(dp, fn)
            if norm(p) != norm(manifest) and norm(p) not in listed:
                unlisted_snapshot.append(p)

    uncovered_source = {}
    listed_src = {norm(r["source_path"]) for r in rows}
    for root in a.source_root:
        files = []
        for dp, _, fns in os.walk(root):
            for fn in fns:
                files.append(os.path.join(dp, fn))
        unc = [p for p in files if norm(p) not in listed_src]
        uncovered_source[root] = {"files_walked": len(files), "not_in_manifest": len(unc),
                                  "not_in_manifest_examples": sorted(unc)[:200]}

    with open(a.out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)

    summary = {
        "manifest": manifest,
        "manifest_sha256": sha256(manifest),
        "rows": len(rows),
        "total_bytes_recorded": sum(int(r["source_size_bytes"]) for r in rows),
        "source_prefix_counts": dict(Counter("\\".join(r["source_path"].split("\\")[:4]) for r in rows)),
        "failures_by_check": dict(fail),
        "unlisted_snapshot_files": unlisted_snapshot,
        "source_hash_check_run": a.source,
        "uncovered_source": uncovered_source,
    }
    with open(a.out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(json.dumps({k: v for k, v in summary.items() if k != "uncovered_source"}, indent=2, ensure_ascii=False))
    for root, u in uncovered_source.items():
        print(root, u["files_walked"], "walked,", u["not_in_manifest"], "not in manifest")


if __name__ == "__main__":
    main()
