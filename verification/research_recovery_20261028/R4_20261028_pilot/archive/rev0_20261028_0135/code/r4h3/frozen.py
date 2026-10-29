"""Frozen inputs of the H3 pilot and their hash checks (protocol v1 sections 2.1, 2.3, 10.1).

Nothing here writes. `load_r3_lib()` imports the R3 physics only after its SHA-256 matches the value
frozen in the protocol; any mismatch raises FrozenInputError and the caller must stop.
"""

from __future__ import annotations

import hashlib
import importlib
import sys
from pathlib import Path

PILOT = Path(__file__).resolve().parents[2]                 # R4_20261028_pilot
REPO = PILOT.parents[2]                                      # D:\EURÉKA 2026 - KT
PREFLIGHT = PILOT.parent / "R4_20261028_preflight"
R3 = REPO / "verification" / "scientific_rebuild_20261024" / "research_recovery_20261025" / "R3_20261025"

PROTOCOL = PREFLIGHT / "03_R4_protocol_v1.md"
R3_LIB = R3 / "code" / "r3_lib.py"
M1_CURVE = R3 / "data" / "motor_curve_m1_derived.json"
PROFILES_YAML = REPO / "configs" / "cycles" / "profiles.yaml"

FROZEN_SHA256 = {
    PROTOCOL: "f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab",   # freeze record
    R3_LIB: "c2403adc2c7ef7a7ecc662f0dcfd3c107a43204ee73c28bd46f782b73cba1c97",     # protocol 2.1
    M1_CURVE: "f872faa0ff96d12d26eb5c935bb145062c3ac649e4eb327136f0fa9a0868d1d9",   # protocol 2.3
}


class FrozenInputError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_frozen(expected: dict | None = None) -> dict:
    """Hash every frozen input; raise on the first mismatch. Returns {path: sha256}."""
    expected = FROZEN_SHA256 if expected is None else expected
    found = {}
    for path, want in expected.items():
        if not Path(path).is_file():
            raise FrozenInputError(f"missing frozen input: {path}")
        got = sha256(path)
        if got != want:
            raise FrozenInputError(f"hash mismatch for {path}: {got} != frozen {want}")
        found[str(path)] = got
    return found


def load_r3_lib():
    """Import the frozen R3 library (read-only) after the hash check."""
    verify_frozen({R3_LIB: FROZEN_SHA256[R3_LIB], M1_CURVE: FROZEN_SHA256[M1_CURVE]})
    sys.dont_write_bytecode = True
    code_dir = str(R3_LIB.parent)
    if code_dir not in sys.path:
        sys.path.insert(0, code_dir)
    return importlib.import_module("r3_lib")
