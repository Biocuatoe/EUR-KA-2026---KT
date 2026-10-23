"""Import every direct dependency and compare installed versions with uv.lock.

Prints a JSON report to stdout; exits 1 if any import fails, any installed version
differs from the lock, or any installed distribution is absent from the lock.
"""

import importlib
import json
import re
import sys
import tomllib
from importlib import metadata
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def canonicalize_name(name: str) -> str:
    """PEP 503 normalisation, as used by uv.lock."""
    return re.sub(r"[-_.]+", "-", name).lower()


# distribution name -> import name
DIRECT = {
    "numpy": "numpy",
    "scipy": "scipy",
    "pandas": "pandas",
    "matplotlib": "matplotlib",
    "sympy": "sympy",
    "control": "control",
    "pint": "pint",
    "pyyaml": "yaml",
    "pydantic": "pydantic",
    "statsmodels": "statsmodels",
    "pytest": "pytest",
    "pytest-cov": "pytest_cov",
    "hypothesis": "hypothesis",
    "ruff": "ruff",
    "pip": "pip",
    "ipykernel": "ipykernel",
}


def main() -> int:
    lock = tomllib.loads((REPO / "uv.lock").read_text(encoding="utf-8"))
    locked = {canonicalize_name(p["name"]): p["version"] for p in lock["package"] if "version" in p}

    imports, failures = {}, []
    for dist, mod_name in DIRECT.items():
        try:
            mod = importlib.import_module(mod_name)
        except Exception as exc:  # report every failure, not just the first
            failures.append(f"import {mod_name}: {exc!r}")
            continue
        imports[dist] = {
            "import": mod_name,
            "installed": metadata.version(dist),
            "locked": locked.get(canonicalize_name(dist)),
            "file": getattr(mod, "__file__", None),
        }

    installed = {canonicalize_name(d.metadata["Name"]): d.version for d in metadata.distributions()}
    mismatched = {
        n: {"installed": v, "locked": locked[n]}
        for n, v in installed.items()
        if n in locked and locked[n] != v
    }
    not_in_lock = sorted(n for n in installed if n not in locked)

    ok = not failures and not mismatched and not not_in_lock
    print(
        json.dumps(
            {
                "ok": ok,
                "python": sys.version,
                "executable": sys.executable,
                "direct_imports": imports,
                "import_failures": failures,
                "installed_count": len(installed),
                "version_mismatches": mismatched,
                "installed_but_not_locked": not_in_lock,
            },
            indent=2,
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
