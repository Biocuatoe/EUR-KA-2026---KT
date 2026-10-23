"""Validate the evidence matrix and export it with artifact hashes.

    python scripts/build_evidence.py

Checks that every registered claim has exactly one matrix row and that every supporting
artifact exists. Writes evidence/evidence_matrix.{csv,json} (tracked) plus a copy in
artifacts/tables, and evidence/artifact_hashes.json (SHA-256 of every result file).
"""

import hashlib
import json
import sys
from collections import Counter

from eureka import REPO_DIR, ROOT_DIR
from eureka.evidence import PRECEDENCE, load_matrix, load_registry, write_matrix_exports
from eureka.lineage import run_context

RESULT_DIRS = [
    "artifacts/reports",
    "artifacts/tables",
    "artifacts/figures/evaluation",
    "data/processed",
]


def sha256(p) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    reg = load_registry()
    rows = load_matrix()
    ids = Counter(r.claim_id for r in rows)
    problems = [f"duplicate row {k}" for k, n in ids.items() if n > 1]
    problems += [f"claim {c.id} has no matrix row" for c in reg.claims if c.id not in ids]
    problems += [
        f"{r.claim_id}: missing artifact {a}"
        for r in rows
        for a in r.supporting_artifacts
        if not (ROOT_DIR / a).exists()
    ]
    if problems:
        print("\n".join(problems))
        return 1

    write_matrix_exports(rows, REPO_DIR / "evidence")
    write_matrix_exports(rows, ROOT_DIR / "artifacts" / "tables")

    files = sorted(p for d in RESULT_DIRS for p in (ROOT_DIR / d).rglob("*") if p.is_file())
    hashes = {str(p.relative_to(ROOT_DIR)).replace("\\", "/"): sha256(p) for p in files}
    raw_manifests = sorted((ROOT_DIR / "artifacts" / "raw").rglob("manifest.json"))
    for m in raw_manifests:
        for f in (m, m.parent / "timeseries.npz"):
            hashes[str(f.relative_to(ROOT_DIR)).replace("\\", "/")] = sha256(f)
    raw_commits = sorted(
        {
            json.loads(m.read_text(encoding="utf-8"))["context"]["git"]["commit"]
            for m in raw_manifests
        }
    )
    (REPO_DIR / "evidence" / "artifact_hashes.json").write_text(
        json.dumps(
            {
                "context": run_context(),
                "raw_run_commits": raw_commits,
                "precedence": PRECEDENCE,
                "sha256": hashes,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    status = Counter(r.verification_status.value for r in rows)
    print(
        json.dumps(
            {
                "rows": len(rows),
                "status_counts": dict(status),
                "artifacts_hashed": len(hashes),
                "raw_run_commits": raw_commits,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
