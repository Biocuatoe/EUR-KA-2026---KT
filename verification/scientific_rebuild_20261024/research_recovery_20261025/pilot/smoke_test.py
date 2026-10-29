"""Smoke test before the pilot (not a pilot result): layer-off with R1's F gain must reproduce R1's saved S2 BCN run;
layer-on must run and close energy. Prints the comparison; writes nothing."""

import csv
import sys

import numpy as np

import run_pilot as rp  # sets sys.path
from eureka.params import load_params
from rebuild.model import BatteryLimits
from rebuild.run import load_cycle
from sim import metrics, simulate

p = load_params().with_overrides(k_r0=0.5)
lim = BatteryLimits(c_dis=3.0, c_ch=1.0, **rp.WIN)
K = rp.gain(p, "fixed", 1.0, 1.0, 1.0)
out = simulate(load_cycle("S2"), [p, p], np.array([K, K]), np.array([1.0, 1.0]), [lim, lim], [False, True], [False, True])
m0, m1 = metrics(out, 0, p), metrics(out, 1, p)
with (rp.R1 / "runs" / "R1_S2" / "metrics.csv").open(encoding="utf-8") as f:
    ref = next(r for r in csv.DictReader(f) if r["run_id"] == "R1_S2-BCN-soh1.00-F")
print("R1 saved  Wh/km", ref["Wh_per_km"], "rmse", ref["rmse_ms"])
print("layer off Wh/km", m0["Wh_per_km"], "rmse", m0["rmse_ms"], "closure", m0["closure_rel"], "valid", m0["valid"])
print("layer on  Wh/km", m1["Wh_per_km"], "rmse", m1["rmse_ms"], "closure", m1["closure_rel"], "valid", m1["valid"],
      "gov active", m1["governor_active_frac"])
rel = abs(m0["Wh_per_km"] - float(ref["Wh_per_km"])) / float(ref["Wh_per_km"])
print("relative difference vs R1:", rel)
sys.exit(0 if rel < 1e-9 else 1)
