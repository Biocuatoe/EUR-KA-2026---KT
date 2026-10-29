import sys

sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pytest  # noqa: E402

from r4h3 import config, task as taskmod  # noqa: E402

L = config.L


@pytest.fixture(scope="session")
def p1():
    return config.params_for("P1")


@pytest.fixture(scope="session")
def toy_task():
    """One segment: rest [0, 1], move 1..7 s over 6 m (peak 2 m/s, |a| <= 1), rest [7, 10]."""
    t = np.arange(0.0, 11.0)
    v = np.array([0, 0, 1, 2, 1, 1, 1, 0, 0, 0, 0], float)
    return taskmod.task_from_samples("TOY", t, v)


@pytest.fixture(scope="session")
def toy2_task():
    """Two segments separated by a stop: rest [0,1], seg 1..7, rest [7,9], seg 9..15, rest [15,16].
    Each segment covers 6 m in 6 s with a brief 2 m/s peak, so a faster schedule exists (time slack)."""
    t = np.arange(0.0, 17.0)
    v = np.array([0, 0, 1, 2, 1, 1, 1, 0, 0, 0, 1, 2, 1, 1, 1, 0, 0], float)
    return taskmod.task_from_samples("TOY2", t, v)


@pytest.fixture(scope="session")
def plant_m0(p1):
    return L.QSPlant(p1, 1.0, config.LIMITS["L-R1"], config.motor_model("M0"))


def short_profile():
    """4 s profile: rest, accelerate to 3 m/s, hold, brake to rest (exercises drive and regeneration)."""
    from r4h3.closedloop import profile_from_knots
    return profile_from_knots("short", [0.0, 0.5, 2.0, 3.0, 4.0], [0.0, 0.0, 3.0, 3.0, 0.0])
