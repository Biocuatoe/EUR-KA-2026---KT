"""Mutation check: run tests of the live pilot against an archived version of r4h3.checks and r4h3.campaign, swapped into
sys.modules before collection. Every other module is the live pilot code. Reads the archive only; writes nothing there
(python -B; outputs go to pytest's tmp dirs). The archived campaign's DRAFT_AMENDMENT_2 name must equal <expected_draft>.
Usage (cwd = pilot): python -I -B run_tests_on_archived.py <pilot_dir> <archived code dir> <expected_draft> [pytest args]"""
import importlib.util
import sys
from pathlib import Path

pilot, arch, expected = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), sys.argv[3]
sys.dont_write_bytecode = True
sys.path.insert(0, str(pilot / "code"))
import r4h3  # noqa: E402

for name in ("checks", "campaign"):
    spec = importlib.util.spec_from_file_location(f"r4h3.{name}", arch / "r4h3" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[f"r4h3.{name}"] = mod
    spec.loader.exec_module(mod)
    setattr(r4h3, name, mod)
    print(f"r4h3.{name} <- {mod.__file__}")
assert r4h3.campaign.DRAFT_AMENDMENT_2.name == expected, r4h3.campaign.DRAFT_AMENDMENT_2.name

import pytest  # noqa: E402

sys.exit(pytest.main(["-c", "code/pytest.ini", "--rootdir", "code", "-p", "no:cacheprovider", *sys.argv[4:]]))
