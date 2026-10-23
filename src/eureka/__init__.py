"""EURÉKA 2026 KT: reproducible evaluation of fixed-gain vs SoH-scheduled LQR for an EV."""

import os
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[2]
# The Git root is the project root (artifacts/, data/ and logs/ sit beside src/).
ROOT_DIR = Path(os.environ.get("EUREKA_ROOT", REPO_DIR))
REPORT_MD = ROOT_DIR / "data" / "processed" / "report" / "report.md"
