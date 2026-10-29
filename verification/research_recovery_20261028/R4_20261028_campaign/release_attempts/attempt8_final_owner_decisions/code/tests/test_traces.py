"""Component F: raw-trace schema completeness and round trip (brief test 7)."""

import json

import numpy as np
import pytest

from r4h3 import SCHEMA_VERSION, traces

META = dict(run_id="T-1", schema_version=SCHEMA_VERSION, branch="B0", cycle="TOY", motor_scenario="M0", limits="L-R1",
            pstate="P1", soh=1.0, dt_s=0.001, Ts_s=0.01, initial_conditions=dict(v=0.0, SoC=0.8), config_sha256="0" * 64,
            gain=[1.0, 2.0, 3.0], d_ref_m=1.0, T_ref_s=1.0)


def full(n=11):
    return {k: np.linspace(0.0, 1.0, n) for k in traces.CHANNELS}


def test_every_channel_has_a_unit_and_description():
    for name, (unit, desc, src) in traces.CHANNELS.items():
        assert unit and desc and src, name
    rec = traces.schema_record()
    assert rec["schema_version"] == SCHEMA_VERSION and len(rec["channels"]) == len(traces.CHANNELS)


def test_round_trip_preserves_data_schema_and_meta(tmp_path):
    a = full()
    sha = traces.write_trace(tmp_path / "t.npz", a, META)
    assert len(sha) == 64
    b, meta, schema = traces.read_trace(tmp_path / "t.npz")
    assert meta == json.loads(json.dumps(META)) and schema["schema_version"] == SCHEMA_VERSION
    for k in traces.CHANNELS:
        assert np.array_equal(a[k], b[k])


def test_missing_channel_is_refused(tmp_path):
    a = full()
    a.pop("i_A")
    with pytest.raises(traces.TraceError, match="missing"):
        traces.write_trace(tmp_path / "t.npz", a, META)


def test_length_mismatch_nan_and_missing_meta_are_refused(tmp_path):
    a = full()
    a["v_mps"] = a["v_mps"][:-1]
    with pytest.raises(traces.TraceError, match="length"):
        traces.write_trace(tmp_path / "a.npz", a, META)
    a = full()
    a["T_Nm"][3] = np.nan
    with pytest.raises(traces.TraceError, match="non-finite"):
        traces.write_trace(tmp_path / "b.npz", a, META)
    meta = dict(META)
    meta.pop("config_sha256")
    with pytest.raises(traces.TraceError, match="meta"):
        traces.write_trace(tmp_path / "c.npz", full(), meta)


def test_existing_trace_is_never_overwritten(tmp_path):
    traces.write_trace(tmp_path / "t.npz", full(), META)
    with pytest.raises(traces.TraceError, match="overwrite"):
        traces.write_trace(tmp_path / "t.npz", full(), META)
