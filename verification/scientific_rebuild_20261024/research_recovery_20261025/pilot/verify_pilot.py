"""Completion and integrity checks on the finished pilot (read-only). Writes out/analysis/verification.json.

Checks: planned vs present runs per stage; duplicates; manifest status fields; protocol hash vs freeze;
every recorded source-file hash vs the file on disk now; gains recomputed from the recorded tuning parameters;
eval gains vs selected.json; validity and energy closure; R1 reproduction against R1's 1e-9 tolerance;
stdout files scanned for tracebacks.
"""

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

import run_pilot as rp  # sets sys.path
from eureka.params import load_params

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
(OUT / "analysis").mkdir(exist_ok=True)


def rd(p):
    with p.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


res = {"stages": {}, "problems": []}
freeze = (HERE / "protocol_sha256_at_freeze.txt").read_text().split()[0]
plan = {"tune": 4 * rp.N_CAND * 2, "eval": 3 * 5 * 4 + 1, "conv": 4}
files = {"tune": "candidates.csv", "eval": "runs.csv", "conv": "runs_dt0.5ms.csv"}
base = load_params()
sel = json.loads((OUT / "tune" / "selected.json").read_text(encoding="utf-8"))

for st in ("tune", "eval", "conv"):
    m = json.loads((OUT / st / "manifest.json").read_text(encoding="utf-8"))
    rows = rd(OUT / st / files[st])
    keyf = (lambda r: (r["branch"], r["cand"], r["scen"])) if st == "tune" else (lambda r: (r["cycle"], r["scen"], r["branch"]))
    keys = [keyf(r) for r in rows]
    hash_mism = [f for f, h in m["file_sha256"].items() if not (rp.REPO / f).exists() or sha(rp.REPO / f) != h]
    # gains recomputed from recorded parameters
    kmax = 0.0
    for r in rows:
        kind = "fixed" if r["branch"] in ("F0", "F1", "SANITY_R1_F") else "scheduled"
        p = base.with_overrides(k_r0=float(r["k_r0"]))
        K = rp.gain(p, kind, float(r["sigma"]), float(r["c"]), float(r["soh"]), float(r["gv"]), float(r["gu"]))
        kmax = max(kmax, float(np.max(np.abs(np.array(json.loads(r["K"])) - K))))
    sel_mism = 0
    if st != "tune":
        for r in rows:
            if r["branch"] in sel:
                s = sel[r["branch"]]
                sel_mism += any(abs(float(r[k]) - float(s[k])) > 0 for k in ("sigma", "c", "gv", "gu"))
    stage = {
        "planned": plan[st], "present": len(rows), "missing": plan[st] - len(rows) if len(rows) < plan[st] else 0,
        "duplicates": len(keys) - len(set(keys)), "invalid": sum(r["valid"] != "True" for r in rows),
        "max_closure_rel": max(float(r["closure_rel"]) for r in rows),
        "manifest_n_runs": m.get("n_runs"), "manifest_n_invalid": m.get("n_invalid"), "runtime_s": m.get("runtime_s"),
        "protocol_hash_matches_freeze": m["protocol_sha256"] == freeze == m["protocol_sha256_at_freeze"],
        "protocol_file_unchanged_now": sha(rp.RR / "pilot_protocol.md") == freeze,
        "source_hash_mismatches_now": hash_mism, "max_abs_gain_recompute_diff": kmax,
        "eval_rows_not_matching_selected_tuning": sel_mism, "dt_s": sorted({r["dt_s"] for r in rows}),
    }
    for k, bad in (("missing", stage["missing"]), ("duplicates", stage["duplicates"]), ("invalid", stage["invalid"]),
                   ("hash", len(hash_mism)), ("selected", sel_mism)):
        if bad:
            res["problems"].append(f"{st}: {k} = {bad}")
    if not stage["protocol_hash_matches_freeze"] or kmax > 1e-9 or stage["max_closure_rel"] > 1e-3:
        res["problems"].append(f"{st}: protocol/gain/closure check failed")
    res["stages"][st] = stage

ev = rd(OUT / "eval" / "runs.csv")
san = next(r for r in ev if r["branch"] == "SANITY_R1_F")
r1 = next(r for r in rd(rp.R1 / "runs" / "R1_S2" / "metrics.csv") if r["run_id"] == "R1_S2-BCN-soh1.00-F")
rel = {}
for k in ("Wh_per_km", "rmse_ms", "E_net_Wh", "friction_brake_Wh"):
    a, b = float(san[k]), float(r1[k])
    rel[k] = abs(a - b) / abs(b) if b != 0 else abs(a - b)  # absolute difference where R1's value is exactly 0
res["R1_reproduction"] = {"diff_relative_or_absolute_if_ref_zero": rel, "tolerance": 1e-9,
                          "pass": all(v <= 1e-9 for v in rel.values())}
if not res["R1_reproduction"]["pass"]:
    res["problems"].append("R1 reproduction outside 1e-9")
res["sched_equals_fixed_at_soh1_maxabs"] = json.loads((OUT / "eval" / "manifest.json").read_text())["sched_equals_fixed_at_soh1_maxabs"]
res["stdout_tracebacks"] = {f.name: ("Traceback" in f.read_text(encoding="utf-8", errors="replace"))
                            for f in HERE.glob("out_*_stdout.txt")}
(OUT / "analysis" / "verification.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
print(json.dumps(res, indent=1, default=str))
