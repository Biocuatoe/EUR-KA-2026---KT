"""Environment verification tests.

These confirm that the installed stack computes correctly and that runtime paths
resolve under D:\\EUREKA-2026. They are not research results: the LQR case is the
textbook double integrator, chosen because its Riccati solution is known in closed form.
"""

import math
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path

import control
import numpy as np
import pandas as pd
import pint
import pytest
import scipy
import sympy as sp
import yaml
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import BaseModel, PositiveFloat, ValidationError

SQRT3 = math.sqrt(3.0)
A = np.array([[0.0, 1.0], [0.0, 0.0]])
B = np.array([[0.0], [1.0]])


def is_under(path: str | Path, parent: str | Path) -> bool:
    p = os.path.normcase(os.path.realpath(path))
    q = os.path.normcase(os.path.realpath(parent))
    return os.path.commonpath([p, q]) == q


def double_integrator_lqr_closed_form(q1: float, q2: float, r: float) -> np.ndarray:
    """K for x'' = u with Q = diag(q1, q2), R = r (derived from the 2x2 ARE)."""
    p2 = math.sqrt(q1 * r)
    p3 = math.sqrt(r * (q2 + 2.0 * p2))
    return np.array([[p2 / r, p3 / r]])


# --- interpreter -------------------------------------------------------------


def test_interpreter_is_project_venv(project_root):
    expected = (project_root / "repo" / ".python-version").read_text().strip()
    assert platform.python_version() == expected
    assert sys.prefix != sys.base_prefix, "not running inside a virtual environment"
    assert os.path.normcase(sys.prefix) == os.path.normcase(str(project_root / ".venv"))
    assert is_under(sys.base_prefix, project_root / "tools" / "python")
    assert is_under(sys.executable, project_root / ".venv")


# --- numerics ----------------------------------------------------------------


def test_numpy_linear_solve_residual():
    rng = np.random.default_rng(20261023)
    m = rng.standard_normal((50, 50)) + 50.0 * np.eye(50)
    b = rng.standard_normal(50)
    x = np.linalg.solve(m, b)
    assert np.linalg.norm(m @ x - b) < 1e-10


def test_scipy_ode_quadrature_and_expm():
    t = np.linspace(0.0, 5.0, 51)
    sol = scipy.integrate.solve_ivp(
        lambda _t, x: -x, (0.0, 5.0), [1.0], t_eval=t, rtol=1e-10, atol=1e-12
    )
    assert sol.success
    np.testing.assert_allclose(sol.y[0], np.exp(-t), rtol=0, atol=1e-8)

    value, _ = scipy.integrate.quad(lambda x: math.exp(-x * x), -math.inf, math.inf)
    assert value == pytest.approx(math.sqrt(math.pi), abs=1e-10)

    np.testing.assert_allclose(scipy.linalg.expm(A * 2.5), [[1.0, 2.5], [0.0, 1.0]], atol=1e-12)


# --- python-control ----------------------------------------------------------


def test_lqr_double_integrator_matches_closed_form():
    K, S, E = control.lqr(A, B, np.eye(2), np.array([[1.0]]), method="scipy")
    np.testing.assert_allclose(K, [[1.0, SQRT3]], rtol=1e-10)
    np.testing.assert_allclose(S, [[SQRT3, 1.0], [1.0, SQRT3]], rtol=1e-10)
    np.testing.assert_allclose(
        np.sort_complex(E), [-SQRT3 / 2 - 0.5j, -SQRT3 / 2 + 0.5j], rtol=1e-10
    )

    # Independent route through SciPy's Riccati solver
    P = scipy.linalg.solve_continuous_are(A, B, np.eye(2), np.array([[1.0]]))
    np.testing.assert_allclose(P, S, rtol=1e-10)
    assert np.linalg.matrix_rank(control.ctrb(A, B)) == 2


def test_lqr_initial_response_matches_analytic_solution():
    K, _, _ = control.lqr(A, B, np.eye(2), np.array([[1.0]]), method="scipy")
    closed_loop = control.ss(A - B @ K, B, [[1.0, 0.0]], [[0.0]])
    t = np.linspace(0.0, 12.0, 601)
    resp = control.initial_response(closed_loop, T=t, X0=[1.0, 0.0])
    # x'' + sqrt(3) x' + x = 0, x(0) = 1, x'(0) = 0
    analytic = np.exp(-SQRT3 / 2 * t) * (np.cos(t / 2) + SQRT3 * np.sin(t / 2))
    np.testing.assert_allclose(np.squeeze(resp.outputs), analytic, rtol=0, atol=1e-8)


weights = st.floats(min_value=1e-3, max_value=1e3, allow_nan=False, allow_infinity=False)


@settings(max_examples=60, deadline=None)
@given(q1=weights, q2=weights, r=weights)
def test_lqr_gain_matches_closed_form_for_positive_weights(q1, q2, r):
    K, S, E = control.lqr(A, B, np.diag([q1, q2]), np.array([[r]]), method="scipy")
    np.testing.assert_allclose(K, double_integrator_lqr_closed_form(q1, q2, r), rtol=1e-6)
    assert np.all(E.real < 0)
    np.testing.assert_allclose(S, S.T, rtol=1e-9, atol=1e-12)
    assert np.all(np.linalg.eigvalsh(S) > 0)


def test_sympy_characteristic_roots_match_lqr_poles():
    s = sp.symbols("s")
    roots = sp.solve(s**2 + sp.sqrt(3) * s + 1, s)
    assert set(roots) == {-sp.sqrt(3) / 2 + sp.I / 2, -sp.sqrt(3) / 2 - sp.I / 2}
    _, _, E = control.lqr(A, B, np.eye(2), np.array([[1.0]]), method="scipy")
    symbolic = np.sort_complex(np.array([complex(r) for r in roots]))
    np.testing.assert_allclose(np.sort_complex(E), symbolic, rtol=1e-10)


# --- units, configuration, analysis -------------------------------------------


def test_pint_unit_conversions_and_dimension_checks():
    ureg = pint.UnitRegistry()
    assert (50 * ureg.km / ureg.hour).to("m/s").magnitude == pytest.approx(125 / 9)
    assert (1 * ureg.kWh).to("J").magnitude == pytest.approx(3.6e6)
    assert (120 * ureg.Wh / ureg.km).to("J/m").magnitude == pytest.approx(432.0)
    with pytest.raises(pint.DimensionalityError):
        _ = 1 * ureg.m + 1 * ureg.s


class _ExampleConfig(BaseModel):
    mass_kg: PositiveFloat
    wheel_radius_m: PositiveFloat


def test_yaml_config_validated_by_pydantic():
    good = yaml.safe_load("mass_kg: 1000.0\nwheel_radius_m: 0.3\n")
    assert _ExampleConfig.model_validate(good).mass_kg == 1000.0
    with pytest.raises(ValidationError, match="greater than 0"):
        _ExampleConfig.model_validate(yaml.safe_load("mass_kg: -1\nwheel_radius_m: 0.3\n"))


def test_pandas_statsmodels_regression_and_bonferroni():
    import statsmodels.formula.api as smf
    from statsmodels.stats.multitest import multipletests

    rng = np.random.default_rng(7)
    x = np.linspace(0.0, 10.0, 200)
    df = pd.DataFrame({"x": x, "y": 2.0 + 3.0 * x + rng.normal(0.0, 0.1, x.size)})
    fit = smf.ols("y ~ x", data=df).fit()
    assert fit.params["Intercept"] == pytest.approx(2.0, abs=0.05)
    assert fit.params["x"] == pytest.approx(3.0, abs=0.01)

    reject, corrected, _, _ = multipletests([0.01, 0.04, 0.03], alpha=0.05, method="bonferroni")
    np.testing.assert_allclose(corrected, [0.03, 0.12, 0.09])
    assert reject.tolist() == [True, False, False]


# --- output on D: --------------------------------------------------------------


def test_plot_is_saved_under_project_artifacts(project_root):
    import matplotlib.image as mpimg
    import matplotlib.pyplot as plt

    K, _, _ = control.lqr(A, B, np.eye(2), np.array([[1.0]]), method="scipy")
    closed_loop = control.ss(A - B @ K, B, [[1.0, 0.0]], [[0.0]])
    t = np.linspace(0.0, 12.0, 601)
    y = np.squeeze(control.initial_response(closed_loop, T=t, X0=[1.0, 0.0]).outputs)

    surface, ink, ink_2, grid = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
    fig, ax = plt.subplots(figsize=(6.4, 3.6), dpi=150, facecolor=surface)
    ax.set_facecolor(surface)
    ax.plot(t, y, color="#2a78d6", linewidth=2)
    ax.axhline(0.0, color=ink_2, linewidth=0.8)
    ax.set_title(
        "Double integrator under LQR (Q = I, R = 1): position from x0 = [1, 0]",
        color=ink,
        fontsize=10,
        loc="left",
    )
    ax.set_xlabel("Time (s)", color=ink_2)
    ax.set_ylabel("Position x1 (dimensionless)", color=ink_2)
    ax.grid(axis="y", color=grid, linewidth=0.6)
    ax.tick_params(colors=ink_2)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(grid)
    fig.tight_layout()

    out = project_root / "artifacts" / "figures" / "environment-check" / "lqr_double_integrator.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, facecolor=surface)
    plt.close(fig)

    assert is_under(out, project_root)
    assert out.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    assert mpimg.imread(out).shape[:2] == (540, 960)


# --- cache and runtime locations ------------------------------------------------

PROJECT_ENV_VARS = [
    "UV_PROJECT_ENVIRONMENT",
    "UV_CACHE_DIR",
    "UV_PYTHON_INSTALL_DIR",
    "PIP_CACHE_DIR",
    "MPLCONFIGDIR",
    "JUPYTER_CONFIG_DIR",
    "JUPYTER_DATA_DIR",
    "JUPYTER_RUNTIME_DIR",
    "IPYTHONDIR",
    "RUFF_CACHE_DIR",
    "COVERAGE_FILE",
    "HYPOTHESIS_STORAGE_DIRECTORY",
    "TEMP",
    "TMP",
]


@pytest.mark.env_paths
@pytest.mark.parametrize("name", PROJECT_ENV_VARS)
def test_project_env_var_points_under_root(name, project_root):
    value = os.environ.get(name)
    assert value, f"{name} is not set: activate with scripts\\activate.ps1 (or VS Code envFile)"
    assert is_under(value, project_root), f"{name}={value} is outside {project_root}"


@pytest.mark.env_paths
def test_library_runtime_dirs_resolve_under_root(project_root, pytestconfig, tmp_path):
    import matplotlib
    from hypothesis.configuration import storage_directory
    from IPython.paths import get_ipython_dir
    from jupyter_core import paths as jpaths

    resolved = {
        "matplotlib config": matplotlib.get_configdir(),
        "matplotlib cache": matplotlib.get_cachedir(),
        "jupyter config": jpaths.jupyter_config_dir(),
        "jupyter data": jpaths.jupyter_data_dir(),
        "jupyter runtime": jpaths.jupyter_runtime_dir(),
        "ipython": get_ipython_dir(),
        "tempfile": tempfile.gettempdir(),
        "pytest tmp_path": str(tmp_path),
        "pytest cache": str(pytestconfig.cache.mkdir("eureka-env-check")),
        "hypothesis": str(storage_directory("examples", intent_to_write=False).path),
    }
    outside = {k: v for k, v in resolved.items() if not is_under(v, project_root)}
    assert not outside, f"resolved outside {project_root}: {outside}"


@pytest.mark.env_paths
def test_pip_cache_dir_under_root(project_root):
    out = subprocess.run(
        [sys.executable, "-m", "pip", "cache", "dir"], capture_output=True, text=True, check=True
    ).stdout.strip()
    assert is_under(out, project_root / "cache"), out
