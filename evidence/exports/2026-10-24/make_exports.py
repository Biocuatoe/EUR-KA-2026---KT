"""Export the dated evidence matrix amendment to this directory only.

    python evidence/exports/2026-10-24/make_exports.py

Reads evidence/evidence_matrix_2026-10-24.yaml and writes evidence_matrix.{csv,json} next to
this script, using the project's own serializer (eureka.evidence.write_matrix_exports).
It applies the same checks as scripts/build_evidence.py (one row per registered claim, no
duplicates, every supporting artifact exists) but writes nothing else: it does not touch
evidence/artifact_hashes.json, evidence/evidence_matrix.{csv,json} or artifacts/tables.
"""

import sys
from collections import Counter
from pathlib import Path

from eureka import REPO_DIR, ROOT_DIR
from eureka.evidence import load_matrix, load_registry, write_matrix_exports

HERE = Path(__file__).resolve().parent
SOURCE = REPO_DIR / "evidence" / "evidence_matrix_2026-10-24.yaml"


def main() -> int:
    reg = load_registry()
    rows = load_matrix(SOURCE)  # pydantic schema check, extra="forbid"
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
    for p in write_matrix_exports(rows, HERE):
        print("wrote", p.relative_to(REPO_DIR))
    print(f"{len(rows)} rows from {SOURCE.relative_to(REPO_DIR)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
