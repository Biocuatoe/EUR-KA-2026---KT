"""Canonical H3 cycle inputs and their hashes (readiness brief section 2; draft amendment 1, item A1-1).

The 1 s-sampled tasks were written once by code/build_cycle_inputs.py (log: logs/build_cycle_inputs.txt)
from R3's frozen run_gates.reference() and checked bit for bit against R4 task.load_task() and against
every sampled reference R3 retained (inputs/cycles/cycle_inputs_manifest.json). This module only reads
and verifies them; it never regenerates or edits a cycle.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from r4h3 import frozen

CYCLE_DIR = frozen.PILOT / "inputs" / "cycles"
CANONICAL_SAMPLED_SHA256 = {
    "S1": "87151e5c30c02f5f6784732a5dd619fc6c39e90913d4afcf06292de2c1f2b7da",
    "S2": "def9d757dc0923afe20a91dca487c84527daff2bef5421c34aef1a61f0a6e990",
}
SOURCE_SHA256 = {
    "S1_source_segments.json": "88a04c905fdd6a3b109e0189af0347c8d6525347ae4812228e7838162cb8d6fd",
    "S1_knots_from_yaml.csv": "e0cdb1f4a4627838a8e691d4516492e604b01be85c2afa34c1ec98be8fd120ec",
    "S2_source_segments.json": "49093326473eb4d33dde34400a6dc741949d192e48fe25c81f1467683a0f2d13",
    "S2_knots_from_yaml.csv": "4bf394980e928f075f7f82135aa11beba1b97b95a2d1e18ae030ea3c448dde6c",
}
MANIFEST_SHA256 = "3d3d6e93d19842141691d041e2363dd8f3f9fef73b362ebcd6ae2ef8b6de7ea5"


class CycleInputError(RuntimeError):
    pass


def sampled_path(cycle: str) -> Path:
    if cycle not in CANONICAL_SAMPLED_SHA256:
        raise CycleInputError(f"no canonical sampled task for {cycle!r}")
    return CYCLE_DIR / f"{cycle}_sampled_h1.csv"


def read_sampled(cycle: str):
    """(t, v) of the canonical sampled task, after its SHA-256 is checked."""
    p = sampled_path(cycle)
    if not p.is_file():
        raise CycleInputError(f"missing canonical cycle input {p}")
    got = frozen.sha256(p)
    if got != CANONICAL_SAMPLED_SHA256[cycle]:
        raise CycleInputError(f"{p.name}: SHA-256 {got} != recorded {CANONICAL_SAMPLED_SHA256[cycle]}")
    rows = list(csv.reader(p.read_text(encoding="utf-8").splitlines()))
    if rows[0] != ["t_s", "v_mps"]:
        raise CycleInputError(f"{p.name}: unexpected header {rows[0]}")
    t = np.array([float(r[0]) for r in rows[1:]])
    v = np.array([float(r[1]) for r in rows[1:]])
    return t, v


def verify_all() -> dict:
    """Hash every canonical cycle artefact and check that task.load_task() reproduces the sampled tasks
    bit for bit. Raises CycleInputError on any difference. Returns {file: sha256}."""
    from r4h3 import task as taskmod
    found = {}
    for name, want in {**SOURCE_SHA256, "cycle_inputs_manifest.json": MANIFEST_SHA256}.items():
        got = frozen.sha256(CYCLE_DIR / name)
        if got != want:
            raise CycleInputError(f"{name}: SHA-256 {got} != recorded {want}")
        found[name] = got
    for c in CANONICAL_SAMPLED_SHA256:
        t, v = read_sampled(c)
        tk = taskmod.load_task(c)
        if not (np.array_equal(t, tk.t) and np.array_equal(v, tk.v_ref)):
            raise CycleInputError(f"{c}: task.load_task() differs from the canonical sampled task")
        found[sampled_path(c).name] = CANONICAL_SAMPLED_SHA256[c]
    return found
