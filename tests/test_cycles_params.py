"""Reference profile construction and parameter-registry validation."""

import pint
import pytest
import yaml

from eureka.cycles import build, load_profiles
from eureka.params import PARAMS_PATH, load_params, load_registry


def test_profile_statistics_match_segment_arithmetic():
    prof = build(
        "x",
        [
            {"idle": 5},
            {"accel": 1.0, "to_kmh": 36},
            {"cruise": 10},
            {"accel": -0.5, "to_kmh": 0},
            {"idle": 3},
        ],
    )
    s = prof.stats()
    # 0 -> 10 m/s at 1 m/s^2: 10 s, 50 m; cruise 100 m; 10 -> 0 at 0.5 m/s^2: 20 s, 100 m
    assert s["duration_s"] == pytest.approx(5 + 10 + 10 + 20 + 3)
    assert s["distance_m"] == pytest.approx(250.0)
    assert s["idle_s"] == pytest.approx(8.0)
    assert s["stops"] == 1
    assert prof.sample(prof.knots_t).tolist() == prof.knots_v.tolist()


@pytest.mark.parametrize(
    "bad", [[{"accel": -1.0, "to_kmh": 20}], [{"accel": 1.0, "to_kmh": 20}, {"idle": 3}]]
)
def test_profile_builder_rejects_inconsistent_segments(bad):
    with pytest.raises(ValueError, match=r"acceleration sign|idle segment"):
        build("bad", bad)


def test_registered_profiles_stay_in_operating_domain():
    prof = load_profiles()
    assert set(prof) == {"P-TUNE", "S1", "S2"}
    assert prof["S1"].stats()["max_speed_kmh"] == pytest.approx(50.0)
    assert prof["S2"].stats()["max_speed_kmh"] == pytest.approx(25.0)
    for p in prof.values():
        assert p.stats()["max_accel"] <= 1.0 + 1e-12


def test_every_parameter_has_provenance_and_valid_unit():
    reg = load_registry()
    assert len(reg) == 33
    for key, p in reg.items():
        assert p.source.strip(), key
        assert p.source_location.strip(), key
    load_params()  # converts every value to its target unit


def test_wrong_dimension_is_rejected(tmp_path):
    raw = yaml.safe_load(PARAMS_PATH.read_text(encoding="utf-8"))
    raw["vehicle"]["mass"]["unit"] = "m"
    bad = tmp_path / "parameters.yaml"
    bad.write_text(yaml.safe_dump(raw), encoding="utf-8")
    with pytest.raises(pint.DimensionalityError):
        load_params(bad)


def test_value_outside_valid_range_is_rejected(tmp_path):
    raw = yaml.safe_load(PARAMS_PATH.read_text(encoding="utf-8"))
    raw["vehicle"]["mass"]["value"] = 5000.0
    bad = tmp_path / "parameters.yaml"
    bad.write_text(yaml.safe_dump(raw), encoding="utf-8")
    with pytest.raises(ValueError, match="outside valid_range"):
        load_params(bad)
