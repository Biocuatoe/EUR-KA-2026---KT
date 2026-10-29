"""The H3 reference task: the cycle sampled at h = 1 s (protocol v1 section 3; ambiguity AMB-01).

All task quantities (d_ref, T_ref, rest intervals, segments, D_k, T_k, v_lim_k, acceleration bounds)
come from the sampled reference, exactly as protocol 3 and 5.1 define them.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from r4h3 import config

L = config.L
from rebuild.run import load_cycle  # noqa: E402

REST_EPS = 1e-9                                              # r3_lib.segments threshold


@dataclass(frozen=True)
class Task:
    cycle: str
    h: float
    t: np.ndarray                 # sample times [s]
    v_ref: np.ndarray             # sampled reference [m/s]
    d_ref: float                  # trapezoidal distance of the samples [m]
    T_ref: float                  # duration of the sampled reference [s]
    rest: tuple                   # ((t_a, t_d), ...) maximal runs of v_ref <= REST_EPS on the grid
    segs: tuple                   # ((ks, ke), ...) r3_lib.segments
    D: tuple                      # per-segment reference distance [m]
    T_seg: tuple                  # per-segment reference travel time (ke - ks) h [s]
    v_lim: tuple                  # per-segment reference maximum speed [m/s]
    a_lo: float
    a_hi: float
    profile_duration: float       # duration of the un-sampled cycle definition (reported, not used)
    profile_distance: float


def rest_intervals(t, v, eps=REST_EPS):
    z = np.abs(v) <= eps
    out, k, n = [], 0, len(v)
    while k < n:
        if z[k]:
            a = k
            while k < n and z[k]:
                k += 1
            out.append((float(t[a]), float(t[k - 1])))
        else:
            k += 1
    return tuple(out)


def task_from_samples(cycle, t, v_ref, h=config.H, profile_duration=float("nan"), profile_distance=float("nan")):
    t = np.asarray(t, float)
    v_ref = np.asarray(v_ref, float)
    segs = tuple(L.segments(v_ref, h))
    D, Tk, vl = [], [], []
    for ks, ke in segs:
        seg = v_ref[ks:ke + 1]
        D.append(float(np.sum(0.5 * (seg[1:] + seg[:-1])) * h))
        Tk.append((ke - ks) * h)
        vl.append(float(seg.max()))
    acc = np.diff(v_ref) / h
    return Task(cycle=cycle, h=h, t=t, v_ref=v_ref, d_ref=float(np.sum(0.5 * (v_ref[1:] + v_ref[:-1])) * h),
                T_ref=float(t[-1]), rest=rest_intervals(t, v_ref), segs=segs, D=tuple(D), T_seg=tuple(Tk),
                v_lim=tuple(vl), a_lo=float(acc.min()), a_hi=float(acc.max()),
                profile_duration=profile_duration, profile_distance=profile_distance)


def load_task(cycle: str, h: float = config.H) -> Task:
    """Sample the cycle exactly as R3 run_gates.reference() does."""
    if cycle not in ("S1", "S2"):
        raise ValueError(f"cycle {cycle!r} is not part of H3 v1 (S2 held-out, S1 in-sample)")
    prof = load_cycle(cycle)
    t = np.arange(0.0, prof.duration + 1e-9, h)
    return task_from_samples(cycle, t, prof.sample(t), h, prof.duration, float(prof.stats()["distance_m"]))
