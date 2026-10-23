"""EURÉKA 2026 KT: reproducible evaluation of fixed-gain vs SoH-scheduled LQR for an EV."""

import os
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[2]
ROOT_DIR = Path(os.environ.get("EUREKA_ROOT", REPO_DIR.parent))
REPORT_MD = ROOT_DIR / "data" / "processed" / "report" / "report.md"
