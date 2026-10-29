"""Frozen inputs of the H3 pilot and their hash checks (protocol v1 sections 2.1, 2.3, 10.1).

Nothing here writes. `load_r3_lib()` imports the R3 physics only after its SHA-256 matches the value
frozen in the protocol; any mismatch raises FrozenInputError and the caller must stop.
"""

from __future__ import annotations

import hashlib
import importlib
import sys
from pathlib import Path

PILOT = Path(__file__).resolve().parents[2]                 # the directory holding this code/ (pilot or a release copy)


def _find_repo(start: Path) -> Path:
    """The project root: the nearest ancestor holding src/eureka and the R4 preflight directory. Location-independent,
    so a release attempt can be tested from a versioned sub-directory (separate issue SI-1, amendment-2 task); from
    the pilot or the campaign root it resolves to the same directory as the former PILOT.parents[2]."""
    for p in start.parents:
        if (p / "src" / "eureka").is_dir() and (p / "verification" / "research_recovery_20261028"
                                                / "R4_20261028_preflight").is_dir():
            return p
    raise RuntimeError(f"project root not found above {start}")


REPO = _find_repo(PILOT)                                     # D:\EURÉKA 2026 - KT
RR = REPO / "verification" / "research_recovery_20261028"    # holds the preflight, pilot and campaign directories
PREFLIGHT = RR / "R4_20261028_preflight"
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

# Upstream code and data that r3_lib and the pilot import (plant, gain, parameters, cycles). Values as recorded by
# R1 (verification/scientific_rebuild_20261024/runs/R1_US06/manifest.json) and unchanged in the R4 preflight
# snapshot. Checked before r3_lib is imported (change VC-07, review finding CR-A7).
R1_DIR = REPO / "verification" / "scientific_rebuild_20261024"
UPSTREAM_SHA256 = {
    REPO / "src" / "eureka" / "plant.py": "e5701bce018f37bebba525dfc58d0e347c63cc1a5b385badf74fe6d0ea772907",
    REPO / "src" / "eureka" / "controllers.py": "2d57b757407dac725891219aa93102ce8be20294a97723fb35ea862ac76d8660",
    REPO / "src" / "eureka" / "params.py": "192ad65933b2786910104f3755601938758a161f603e2cce02d9eaa74907369e",
    REPO / "src" / "eureka" / "cycles.py": "f09ed877efe3aece1d4990c79d55c4902999758ef67ab2603591703ae49b8cec",
    R1_DIR / "src" / "rebuild" / "model.py": "2050111b0860d1552c180b25ffbfbdb16c098c0e262632be6ecdb95d876003de",
    R1_DIR / "src" / "rebuild" / "run.py": "7336a295f407134f6d7aa38ba1749edcb3aea9cdbddf7114c2f8a7bbdb185001",
    R1_DIR / "configs" / "R1.yaml": "b33d9667dacd69884c6443f7f71c229972eabb7a99eec6ae0649dfebbb980858",
    REPO / "configs" / "parameters.yaml": "0efe2d1a413a51d425043691c857807b021d62908935adfda9b757de6f9f374f",
    PROFILES_YAML: "90a496a36c618e216693a3d819b84739f10e6c35167c23a91b63478ef28be0a6",
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
    """Import the frozen R3 library (read-only) after the hash check of it and of everything it imports."""
    verify_frozen({R3_LIB: FROZEN_SHA256[R3_LIB], M1_CURVE: FROZEN_SHA256[M1_CURVE], **UPSTREAM_SHA256})
    sys.dont_write_bytecode = True
    code_dir = str(R3_LIB.parent)
    if code_dir not in sys.path:
        sys.path.insert(0, code_dir)
    return importlib.import_module("r3_lib")
