"""Phase 1 outputs: report consistency checks and a flat export of the claim registry.

    python scripts/audit_report.py

Writes
    artifacts/reports/report-consistency-checks.json
    artifacts/tables/claim_registry.csv
    data/processed/report/MANIFEST.json   (provenance of the derived report.md)
"""

import csv
import hashlib
import json
import subprocess

from eureka import REPORT_MD, ROOT_DIR
from eureka.audit.report_checks import run_all
from eureka.evidence import load_registry
from eureka.lineage import run_context


def sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    ctx = run_context()
    reg = load_registry()

    raw = ROOT_DIR / reg.report_file
    pandoc = subprocess.run(
        [r"C:\Users\HLC\AppData\Local\Pandoc\pandoc.exe", "--version"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.splitlines()[:1]
    manifest = {
        "source": str(raw),
        "source_sha256": sha256(raw),
        "derived": str(REPORT_MD),
        "derived_sha256": sha256(REPORT_MD),
        "command": f'pandoc "{raw}" -t gfm --wrap=none --extract-media=media -o report.md',
        "tool": pandoc,
    }
    (REPORT_MD.parent / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), "utf-8")

    checks = [r.as_dict() for r in run_all()]
    out = ROOT_DIR / "artifacts" / "reports" / "report-consistency-checks.json"
    out.write_text(json.dumps({"context": ctx, "checks": checks}, indent=2), encoding="utf-8")

    table = ROOT_DIR / "artifacts" / "tables" / "claim_registry.csv"
    fields = [
        "id",
        "title",
        "category",
        "locations",
        "units",
        "evidence_category",
        "reproducibility",
        "consistency_checks",
        "disposition",
    ]
    with table.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for c in reg.claims:
            w.writerow(
                {
                    "id": c.id,
                    "title": c.title,
                    "category": c.category,
                    "locations": "; ".join(f"L{loc.line}" for loc in c.locations),
                    "units": c.units,
                    "evidence_category": c.evidence_category.value,
                    "reproducibility": c.reproducibility.value,
                    "consistency_checks": "; ".join(c.consistency_checks),
                    "disposition": c.disposition.value,
                }
            )

    n_bad = sum(not c["consistent"] for c in checks)
    print(f"{len(reg.claims)} claims registered; {len(checks)} checks, {n_bad} inconsistent")
    print(f"wrote {out}\nwrote {table}")


if __name__ == "__main__":
    main()
