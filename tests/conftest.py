"""Shared pytest configuration for the EUREKA 2026 test suite."""

import os
from pathlib import Path

import matplotlib
import pytest
from hypothesis import configuration

# Headless backend: figures are only ever written to files.
matplotlib.use("Agg")

REPO = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("EUREKA_ROOT", REPO))

# project.env normally sets HYPOTHESIS_STORAGE_DIRECTORY; without it Hypothesis would
# create .hypothesis/ in the current directory, so pin it to the project cache.
if not os.environ.get("HYPOTHESIS_STORAGE_DIRECTORY"):
    configuration.set_hypothesis_home_dir(ROOT / "cache" / "hypothesis")


@pytest.fixture(scope="session")
def project_root() -> Path:
    return ROOT
