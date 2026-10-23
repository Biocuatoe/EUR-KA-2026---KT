"""End-to-end lineage: run -> saved raw outputs -> validation -> metrics (on P-TUNE only)."""

import json

import numpy as np
import pytest

from eureka import experiment as ex
from eureka.cycles import load_profiles
from eureka.metrics import batch_table, load_batch


@pytest.fixture(scope="module")
def ptune_batch(tmp_path_factory):
    raw = tmp_path_factory.mktemp("raw")
    orig = ex.RAW_DIR
    ex.RAW_DIR = raw
    try:
        specs = [
            ex.RunSpec("pipeline_test", "P-TUNE", "fixed", 0.8),
            ex.RunSpec("pipeline_test", "P-TUNE", "scheduled", 0.8),
        ]
        dest = ex.run_batch("pipeline_test", "P-TUNE", specs, "float64", allow_dirty=True)
    finally:
        ex.RAW_DIR = orig
    return dest


def test_saved_runs_validate_and_metrics_match_profile(ptune_batch):
    rows = batch_table(ptune_batch)
    dist = load_profiles()["P-TUNE"].stats()["distance_m"] / 1000
    for r in rows:
        assert r["valid"], r["reasons"]
        assert r["closure_rel"] < 1e-6
        assert r["distance_km"] == pytest.approx(dist, rel=5e-3)
        assert 0 < r["rmse_ms"] < 0.5
        assert r["energy_Wh_per_km"] > 0


def test_manifest_records_lineage(ptune_batch):
    m, arr = load_batch(ptune_batch)
    assert m["context"]["git"]["commit"]
    assert set(m["context"]["software"]) >= {"numpy", "scipy", "control"}
    assert len(m["runs"]) == arr["y_end"].shape[0] == 2
    assert m["runs"][1]["gain"] == arr["gains"][1].tolist()


def test_runner_refuses_without_passed_gate(tmp_path, monkeypatch):
    reports = tmp_path / "artifacts" / "reports"
    reports.mkdir(parents=True)
    (reports / "verification-gate.json").write_text(
        json.dumps({"passed": False, "context": {"git": {"commit": "x"}}}), encoding="utf-8"
    )
    monkeypatch.setattr(ex, "ROOT_DIR", tmp_path)
    spec = [ex.RunSpec("t", "P-TUNE", "fixed", 1.0)]
    with pytest.raises(RuntimeError, match="verification gate"):
        ex.run_batch("t", "P-TUNE", spec, "float64")


def test_robustness_pairs_share_parameters_and_noise():
    cfg = ex.load_experiments()
    specs = ex.specs_for("robustness", cfg, draws=range(3))
    assert len(specs) == 6
    for a, b in zip(specs[::2], specs[1::2], strict=True):
        assert (a.controller, b.controller) == ("fixed", "scheduled")
        assert a.overrides == b.overrides
        assert a.seed == b.seed
        p = ex.load_params()
        np.testing.assert_array_equal(ex._noise(a, p, 100), ex._noise(b, p, 100))
    assert specs[0].overrides != specs[2].overrides
