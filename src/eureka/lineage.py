"""Run provenance: Git commit, software versions, configuration hashes, run identifiers."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import platform
import subprocess
import sys
from importlib import metadata

from eureka import REPO_DIR

TRACKED_PACKAGES = (
    "numpy",
    "scipy",
    "pandas",
    "matplotlib",
    "control",
    "pint",
    "pydantic",
    "pyyaml",
    "statsmodels",
    "sympy",
)


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO_DIR), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def git_state() -> dict:
    try:
        commit = _git("rev-parse", "HEAD")
    except subprocess.CalledProcessError:
        commit = None
    dirty = bool(_git("status", "--porcelain")) if commit else True
    return {"commit": commit, "dirty": dirty}


def software_versions() -> dict:
    v = {"python": platform.python_version(), "executable": sys.executable}
    for p in TRACKED_PACKAGES:
        v[p] = metadata.version(p)
    return v


def config_hash(obj) -> str:
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def run_context() -> dict:
    return {
        "utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "git": git_state(),
        "software": software_versions(),
        "machine": platform.node(),
    }
