"""Pre-registered tuning acceptance (preregistration section 5), on P-TUNE only.

    python scripts/tuning_acceptance.py

Criteria: closed-loop |eig| < 1, overshoot after every ramp < 10 % of the speed change,
and error zero-crossing rate during holds (after 2 s settling, deadband 0.01 m/s) < 0.5 Hz.
On failure the velocity-error maximum is doubled (at most 3 times) and each attempt is
recorded. Writes artifacts/reports/tuning-acceptance.json. Does not touch S1/S2.
"""

import json
import sys

import numpy as np

from eureka import ROOT_DIR
from eureka.controllers import bryson_weights, design_model, dlqr, zoh
from eureka.cycles import load_profiles
from eureka.lineage import run_context
from eureka.params import load_params
from eureka.simulate import simulate


def hold_metrics(prof, t, v):
    over, rates = [], []
    kt, kv = prof.knots_t, prof.knots_v
    for i in range(1, len(kt) - 1):
        dv_in = kv[i] - kv[i - 1]
        is_hold = kv[i + 1] == kv[i]
        if not is_hold or dv_in == 0:
            continue
        m = (t >= kt[i]) & (t <= kt[i + 1])
        over.append(max(0.0, float(np.max((v[m] - kv[i]) * np.sign(dv_in)) / abs(dv_in) * 100)))
        settle = (t >= kt[i] + 2.0) & (t <= kt[i + 1])
        e = v[settle] - kv[i]
        state = np.where(e > 0.01, 1, np.where(e < -0.01, -1, 0))
        state = state[state != 0]
        crossings = int(np.sum(state[1:] != state[:-1]))
        dur = kt[i + 1] - kt[i] - 2.0
        rates.append(crossings / dur if dur > 0 else 0.0)
    return over, rates


def main() -> int:
    p = load_params()
    prof = load_profiles()["P-TUNE"]
    attempts = []
    for attempt in range(4):
        pa = p.with_overrides(e_max=p.e_max * 2**attempt)
        Ad, Bd = zoh(*design_model(pa), pa.Ts)
        K, _, eig = dlqr(Ad, Bd, *bryson_weights(pa))
        out = simulate(prof, [pa], K, np.array([1.0]))
        over, rates = hold_metrics(prof, out["t"][:, 0], out["v"][:, 0])
        res = {
            "attempt": attempt + 1,
            "e_max": pa.e_max,
            "K": K.tolist(),
            "max_abs_eig": float(np.max(np.abs(eig))),
            "max_overshoot_pct": max(over),
            "max_zero_crossing_rate_hz": max(rates),
        }
        res["accepted"] = bool(
            res["max_abs_eig"] < 1
            and res["max_overshoot_pct"] < 10
            and res["max_zero_crossing_rate_hz"] < 0.5
        )
        attempts.append(res)
        print(json.dumps(res))
        if res["accepted"]:
            break
    report = {
        "context": run_context(),
        "profile": "P-TUNE",
        "attempts": attempts,
        "accepted_e_max": attempts[-1]["e_max"] if attempts[-1]["accepted"] else None,
    }
    out_path = ROOT_DIR / "artifacts" / "reports" / "tuning-acceptance.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"wrote {out_path}")
    return 0 if attempts[-1]["accepted"] else 1


if __name__ == "__main__":
    sys.exit(main())
