"""Canonical cycle inputs (brief section 2) and the sensitivity-draw design (protocol 8.4)."""

import shutil

import numpy as np
import pytest

from r4h3 import config, inputs, sensitivity, task as taskmod


# ---- canonical sampled cycles
def test_canonical_cycle_inputs_verify_and_equal_load_task():
    found = inputs.verify_all()
    assert found["S1_sampled_h1.csv"] == inputs.CANONICAL_SAMPLED_SHA256["S1"]
    for c, (n, T, d) in {"S1": (325, 324.0, 2161.027), "S2": (214, 213.0, 531.574)}.items():
        t, v = inputs.read_sampled(c)
        assert len(t) == n and t[0] == 0.0 and t[-1] == T and np.all(np.diff(t) == 1.0)
        assert v[0] == 0.0 and v[-1] == 0.0
        assert round(taskmod.task_from_samples(c, t, v).d_ref, 3) == d


def test_tampered_cycle_input_is_refused(tmp_path, monkeypatch):
    for f in inputs.CYCLE_DIR.iterdir():
        shutil.copy2(f, tmp_path / f.name)
    p = tmp_path / "S1_sampled_h1.csv"
    p.write_text(p.read_text(encoding="utf-8").replace("\n1.0,", "\n1.0000000001,", 1), encoding="utf-8")
    monkeypatch.setattr(inputs, "CYCLE_DIR", tmp_path)
    with pytest.raises(inputs.CycleInputError):
        inputs.read_sampled("S1")
    with pytest.raises(inputs.CycleInputError):
        inputs.read_sampled("UDDS")


# ---- sensitivity design
def test_draws_follow_protocol_8_4():
    u = sensitivity.unit_draws()
    assert u.shape == (32, 7) and np.array_equal(u, sensitivity.unit_draws())          # deterministic
    for j in range(7):                                                                 # Latin hypercube strata
        assert sorted(np.floor(u[:, j] * 32).astype(int)) == list(range(32))
    x = sensitivity.draws()
    want = {1: (722.5, 977.5), 2: (2.0, 2.4), 3: (0.315, 0.385), 4: (0.008, 0.012), 5: (0.265, 0.285), 6: (0.004, 0.006),
            7: (0.83, 0.918)}
    for c in sensitivity.COLUMNS:
        lo, hi = want[c["col"]]
        assert (c["lo"], c["hi"]) == (lo, hi)
        assert np.all(x[:, c["col"] - 1] >= lo) and np.all(x[:, c["col"] - 1] <= hi)
    assert [c["ledger"] for c in sensitivity.COLUMNS] == ["VEH-01", "VEH-03", "VEH-04", "VEH-05", "VEH-06", "BAT-07",
                                                          "MOT-05"]


def test_ranges_equal_the_preflight_ledger():
    import csv
    from r4h3 import frozen
    led = {r["param_id"]: r["uncertainty_range"]
           for r in csv.DictReader((frozen.PREFLIGHT / "02_parameter_ledger.csv").open(encoding="utf-8"))}
    for c in sensitivity.COLUMNS:
        lo, hi = led[c["ledger"]].split(" ")[0].split("-")
        scale = 1.0
        assert (float(lo) * scale, float(hi) * scale) == (c["lo"], c["hi"]), c["ledger"]


def test_draw_plant_and_motor():
    row = sensitivity.draws()[0]
    p = sensitivity.draw_params(row)
    assert (p.M, p.A_f, p.Cd, p.Crr, p.r_w, p.R0_new) == tuple(float(x) for x in row[:6])
    assert p.k_r0 == config.PSTATES["P1"]["k_r0"] and p.G == config.params_for("P1").G
    m0 = sensitivity.draw_motor(row, "M0")
    assert m0.kind == "const" and m0.eta == float(row[6])
    assert sensitivity.draw_motor(row, "M1") == config.motor_model("M1")                # column 7 ignored by M1
    assert sensitivity.draw_eval_motor_spec(row, "M0", None)["eta"] == float(row[6])
    with pytest.raises(ValueError):
        sensitivity.draw_motor(row, "M2")


def test_gain_basis_is_never_chosen_by_the_code():
    row = sensitivity.draws()[0]
    with pytest.raises(RuntimeError, match="AMB-14"):
        sensitivity.gain_for_draw(row, None)
    from r4h3.closedloop import fixed_gain
    nominal = sensitivity.gain_for_draw(row, "nominal_P1")
    assert np.array_equal(nominal, fixed_gain(config.params_for("P1")))
    assert not np.array_equal(sensitivity.gain_for_draw(row, "draw_P1"), nominal)       # the readings differ
    with pytest.raises(ValueError):
        sensitivity.gain_for_draw(row, "tuned")


def test_design_record():
    rec = sensitivity.design_record()
    assert rec["seed"] == 20261028 and rec["n_draws"] == 32 and rec["runs"] == 128
    assert "AMB-14" in rec["open_items"] and "not a probability statement" in rec["interpretation"]
    assert len(sensitivity.table_rows()) == 32
