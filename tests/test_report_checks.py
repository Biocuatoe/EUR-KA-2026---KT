"""Expected outcomes of the report consistency checks (recomputed, not asserted from memory)."""

import pytest

from eureka.audit import report_checks as rc
from eureka.audit.dimensional import audit_report_a_matrix


def test_energy_saving_is_10_2_percent():
    r = rc.chk_energy_pct()
    assert r.computed["relative_pct"] == pytest.approx(10.21, abs=0.01)
    assert not r.consistent


def test_vuc_statistics_are_mutually_impossible():
    assert rc.chk_vuc_speed().computed["avg_speed_kmh"] == pytest.approx(34.8)
    assert rc.chk_vuc_idle().computed["idle_pct"] == pytest.approx(62.3)
    assert not rc.chk_vuc_speed().consistent
    assert not rc.chk_vuc_idle().consistent


def test_cycle_speed_check_distinguishes_consistent_rows():
    r = rc.chk_cycle_speeds()
    assert r.computed["consistent_per_cycle"] == {"NEDC": True, "WLTP": False, "CLTC": True}


def test_bonferroni_threshold_rejects_reported_significance():
    r = rc.chk_bonferroni()
    assert r.computed["threshold_all_18"] == pytest.approx(0.05 / 18, rel=1e-3)
    assert r.computed["n_not_significant_all_18"] == 9
    assert r.computed["n_not_significant_per_metric"] == 6


def test_rmse_reduction_is_38_percent():
    assert rc.chk_rmse_pct().computed["reduction_pct"] == pytest.approx(38.2)


def test_bryson_rule_check():
    r = rc.chk_bryson()
    assert r.computed["u_max_implied_by_R_Nm"] == 1.0
    assert not r.consistent


def test_dimensional_audit_flags_only_the_traction_term():
    bad = [r["term"] for r in audit_report_a_matrix() if not r["consistent"]]
    assert bad == ["A[v,w] * w"]


def test_every_check_runs_and_serialises():
    for r in rc.run_all():
        d = r.as_dict()
        assert d["id"].startswith("CHK-")
        assert isinstance(d["consistent"], bool)
