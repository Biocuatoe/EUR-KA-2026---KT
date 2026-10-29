"""Verify R1-R3 hash records against the current files (R4 preflight, Phase 0). Read-only.

Sources of recorded hashes:
  - protocol freeze records of R1, R2 and R3 (and R3 amendment 1);
  - R3_hash_manifest.csv (every R3 file at the end of R3);
  - every manifest.json / run_manifest.json under the R1-R3 tree: each (key, 64-hex value) pair whose key
    names a file is resolved against the manifest's directory, its parents up to the repo root, and the
    R3 code directory; the first base where the file exists is used.

    python -I verify_r1_r3_records.py <repo root> <out.csv>
"""
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HEX = re.compile(r"^[0-9a-fA-F]{64}$")


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def walk(obj, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk(v, k)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk(v, prefix)
    elif isinstance(obj, str) and HEX.match(obj):
        yield prefix, obj


def main():
    repo, out = Path(sys.argv[1]), sys.argv[2]
    sr = repo / "verification" / "scientific_rebuild_20261024"
    rr = sr / "research_recovery_20261025"
    r3 = rr / "R3_20261025"
    rows = []

    def add(source, path, recorded, base_note=""):
        p = Path(path)
        if p.is_file():
            now = sha(p)
            status = "match" if now.lower() == recorded.lower() else "MISMATCH"
        else:
            now, status = "", "unresolved"
        rows.append({"record": str(source.relative_to(repo)), "file": str(p.relative_to(repo)) if p.is_file() else str(path),
                     "recorded_sha256": recorded.lower(), "current_sha256": now, "status": status, "note": base_note})

    # protocol freeze records
    add(sr / "logs" / "protocol_sha256_at_freeze.txt", sr / "experimental_protocol.md",
        (sr / "logs" / "protocol_sha256_at_freeze.txt").read_text().split()[0], "R1 protocol")
    add(rr / "pilot" / "protocol_sha256_at_freeze.txt", rr / "pilot_protocol.md",
        (rr / "pilot" / "protocol_sha256_at_freeze.txt").read_text().split()[0], "R2 pilot protocol")
    for line in (r3 / "logs" / "protocol_v1_sha256_at_freeze.txt").read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            h, rel = line.split(None, 1)
            add(r3 / "logs" / "protocol_v1_sha256_at_freeze.txt", r3 / rel.strip(), h, "R3 freeze record")
    for line in (r3 / "logs" / "amendment_1_sha256.txt").read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            h, rel = line.split(None, 1)
            add(r3 / "logs" / "amendment_1_sha256.txt", r3 / rel.strip().lstrip("*"), h, "R3 amendment record")

    # R3 final hash manifest
    with open(r3 / "R3_hash_manifest.csv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            add(r3 / "R3_hash_manifest.csv", r3 / r["path"], r["sha256"], f"R3_hash_manifest {r['freeze_status']}")

    # per-run manifests
    for m in sorted(list(sr.rglob("manifest.json")) + list(sr.rglob("run_manifest.json"))):
        try:
            data = json.loads(m.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            rows.append({"record": str(m.relative_to(repo)), "file": "", "recorded_sha256": "", "current_sha256": "",
                         "status": "unreadable", "note": repr(e)})
            continue
        for key, h in walk(data):
            if "sha256" in key.lower() and "." not in key and "/" not in key and "\\" not in key:
                in_r3 = r3 in m.parents
                key_path = {"protocol_sha256": "R3_protocol_v1.md" if in_r3 else ("pilot_protocol.md" if rr / "pilot" in m.parents
                                                                                  else "experimental_protocol.md"),
                            "amendment_1_sha256": "R3_protocol_v1_amendment_1.md"}.get(key)
                if key_path is None:
                    continue
                key = key_path
            bases = [m.parent, *m.parents[: len(m.relative_to(repo).parts)], r3 / "code", r3 / "data", r3, rr / "pilot", rr, sr]
            target = next((b / key for b in bases if (b / key).is_file()), None)
            add(m, target if target else key, h, "per-run manifest")

    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    c = Counter((r["note"].split()[0] if r["note"] else "", r["status"]) for r in rows)
    for k, v in sorted(c.items()):
        print(v, k)
    for r in rows:
        if r["status"] != "match":
            print(r["status"], r["record"], r["file"])


if __name__ == "__main__":
    main()
