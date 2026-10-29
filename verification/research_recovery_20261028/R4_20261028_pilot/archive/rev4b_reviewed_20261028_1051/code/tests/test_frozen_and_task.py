"""Frozen inputs, nominal parameters and the sampled task (protocol 2.1, 2.2, 2.4, 3)."""

import numpy as np
import pytest

from r4h3 import config, frozen, task as taskmod


def test_frozen_hashes_match():
    found = frozen.verify_frozen()
    assert set(found) == {str(p) for p in frozen.FROZEN_SHA256}


def test_wrong_hash_is_refused():
    with pytest.raises(frozen.FrozenInputError):
        frozen.verify_frozen({frozen.PROTOCOL: "0" * 64})


def test_nominal_parameters_equal_protocol_table(p1):
    want = dict(M=850.0, A_f=2.2, Cd=0.35, Crr=0.008, r_w=0.28, rho=1.225, g=9.81, G=6.5, eta_g=0.9702, J_m=0.05,
                B_m=0.001, T_max=85.0, P_max=18000.0, w_max=837.0, tau_T=0.02, V_oc=48.0, Q_Ah=100.0, R0_new=0.005,
                R1_new=0.003, C1=50000.0, k_r1=0.3, dt=0.001, Ts=0.01, k_r0=0.5)
    got = p1.as_dict()
    assert {k: got[k] for k in want} == want


def test_plant_states_and_limits_are_the_protocol_ones():
    assert config.PSTATES == {"P1": dict(soh=1.0, k_r0=0.5), "P3": dict(soh=0.8, k_r0=3.5)}
    r1, eve = config.LIMITS["L-R1"], config.LIMITS["L-EVE"]
    assert (r1.c_dis, r1.c_ch, eve.c_dis, eve.c_ch) == (3.0, 1.0, 2.0, 1.0)
    for lim in (r1, eve):
        assert not lim.soh_scaled
        assert lim.v_min_ratio * 48.0 == pytest.approx(37.5) and lim.v_max_ratio * 48.0 == pytest.approx(54.75)


@pytest.mark.parametrize("cycle,d_ref,T_ref", [("S2", 531.574, 213.0), ("S1", 2161.027, 324.0)])
def test_sampled_task_matches_protocol_section_3(cycle, d_ref, T_ref):
    tk = taskmod.load_task(cycle)
    assert tk.T_ref == T_ref
    assert tk.d_ref == pytest.approx(d_ref, abs=5e-4)
    assert sum(tk.D) == pytest.approx(tk.d_ref, abs=1e-9)
    # AMB-01: the cycle definition is longer than the sampled task; the sampled task is what protocol 3 fixes
    assert tk.profile_duration > tk.T_ref and tk.profile_duration - tk.T_ref < 1.0


def test_out_of_domain_cycles_are_refused():
    with pytest.raises(ValueError):
        taskmod.load_task("UDDS")


def test_rest_intervals_and_segments_are_consistent(toy2_task):
    tk = toy2_task
    assert tk.rest == ((0.0, 1.0), (7.0, 9.0), (15.0, 16.0))
    assert tk.segs == ((1, 7), (9, 15))
    assert tk.T_seg == (6.0, 6.0)
    assert tk.D == (6.0, 6.0)
    assert (tk.a_lo, tk.a_hi) == (-1.0, 1.0)
    assert np.isclose(tk.d_ref, 12.0)
