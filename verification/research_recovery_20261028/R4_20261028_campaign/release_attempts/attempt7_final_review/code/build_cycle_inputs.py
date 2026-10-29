"""Canonical H3 cycle inputs for S1 and S2 (readiness brief section 2; draft amendment 1, item A1-1).

    python -I -B code/build_cycle_inputs.py

Writes three separate artefacts per cycle under inputs/cycles/ (refuses to overwrite):
    <C>_source_segments.json   the YAML segment definition, verbatim (source of the cycle)
    <C>_knots_from_yaml.csv    knots built from it by eureka.cycles.build (the un-sampled profile)
    <C>_sampled_h1.csv         the protocol task: the profile sampled at h = 1 s (protocol v1 section 3)
and cycle_inputs_manifest.json with every hash and check.

The sampled task is produced by R3's frozen run_gates.reference() (np.interp of the knots at
t = 0, 1, ..., floor(duration)); nothing is rounded or edited. It is checked bit for bit against
(a) R4 task.load_task() and (b) every sampled reference R3 retained in outputs/gates*/paths/*.npz,
whose file hashes are first checked against R3_hash_manifest.csv. Only the `t` and `v_ref` arrays of
those files are read. Any mismatch stops the script without writing the sampled artefacts.
"""

from __future__ import annotations

import csv
import hashlib
import importlib
import json
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402

from r4h3 import config, frozen  # noqa: E402
from r4h3 import task as taskmod  # noqa: E402

OUT = frozen.PILOT / "inputs" / "cycles"
CYCLES = ("S1", "S2")
R3_MANIFEST = frozen.R3 / "R3_hash_manifest.csv"
R3_RUN_GATES = frozen.R3 / "code" / "run_gates.py"
EUREKA_CYCLES = frozen.REPO / "src" / "eureka" / "cycles.py"
REBUILD_RUN = frozen.REPO / "verification" / "scientific_rebuild_20261024" / "src" / "rebuild" / "run.py"

# Hashes recorded before R4 (R1 run manifests, e.g. runs/R1_US06/manifest.json; R3_hash_manifest.csv
# 'frozen-unchanged'; R4 preflight zz_pre_hash_project.csv). A difference stops the script.
RECORDED = {
    frozen.PROFILES_YAML: "90a496a36c618e216693a3d819b84739f10e6c35167c23a91b63478ef28be0a6",
    EUREKA_CYCLES: "f09ed877efe3aece1d4990c79d55c4902999758ef67ab2603591703ae49b8cec",
    REBUILD_RUN: "7336a295f407134f6d7aa38ba1749edcb3aea9cdbddf7114c2f8a7bbdb185001",
    R3_RUN_GATES: "d870e096cbad828661c65682dfbd4e18ecc00bdace989af084e10def465ca85a",
}
PROTOCOL_PRINTED = {"S1": (2161.027, 324.0), "S2": (531.574, 213.0)}       # protocol v1 section 3 (d_ref m, T_ref s)


def fmt(x: float) -> str:
    return repr(float(x))                                     # shortest round-trip representation


def write_new(path: Path, text: str) -> str:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    path.write_text(text, encoding="utf-8", newline="\n")
    return frozen.sha256(path)


def csv_text(header, cols) -> str:
    lines = [",".join(header)] + [",".join(fmt(c[i]) for c in cols) for i in range(len(cols[0]))]
    return "\n".join(lines) + "\n"


def read_csv_cols(path: Path):
    rows = list(csv.reader(path.read_text(encoding="utf-8").splitlines()))
    return rows[0], [np.array([float(r[j]) for r in rows[1:]]) for j in range(len(rows[0]))]


def r3_retained(cycle: str):
    """Every R3-retained sampled reference for the cycle, with its recorded and actual hash."""
    rec = {r["path"]: r["sha256"] for r in csv.DictReader(R3_MANIFEST.open(encoding="utf-8"))}
    out = []
    for rel, want in sorted(rec.items()):
        name = rel.rsplit("/", 1)[-1]
        if "/paths/" in rel and name.endswith(".npz") and f"_{cycle}_" in name:
            p = frozen.R3 / rel
            got = frozen.sha256(p)
            with np.load(p, allow_pickle=False) as z:
                t, v = np.array(z["t"]), np.array(z["v_ref"])
            out.append(dict(path=rel, sha256_recorded=want, sha256_now=got, hash_ok=got == want, t=t, v=v))
    return out


def stop_table(task, knots_t, knots_v):
    """Rest intervals of the sampled task, with position along the route and the un-sampled rest interval."""
    x = np.concatenate([[0.0], np.cumsum(0.5 * (task.v_ref[1:] + task.v_ref[:-1]) * task.h)])
    kz = (knots_v[1:] == 0) & (knots_v[:-1] == 0)
    src = [(float(knots_t[i]), float(knots_t[i + 1])) for i in np.flatnonzero(kz)]
    rows = []
    for j, (a, b) in enumerate(task.rest):
        ia = int(round(a / task.h))
        s = next(((sa, sb) for sa, sb in src if sa <= b and sb >= a), (float("nan"), float("nan")))
        rows.append(dict(index=j, t_a_s=a, t_d_s=b, duration_s=b - a, position_m=float(x[ia]),
                         tested_by_8_2=(b - a) >= config.RULES["stop_min_duration_s"],
                         yaml_rest_from_s=s[0], yaml_rest_to_s=s[1]))
    return rows


def main() -> int:
    t0 = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    found = frozen.verify_frozen()
    for p, want in RECORDED.items():
        got = frozen.sha256(p)
        if got != want:
            raise SystemExit(f"STOP: {p} hash {got} differs from the recorded {want}")
    import yaml
    from eureka.cycles import load_profiles
    sys.path.insert(0, str(R3_RUN_GATES.parent))
    run_gates = importlib.import_module("run_gates")           # frozen R3 module; import has no side effects
    raw = yaml.safe_load(frozen.PROFILES_YAML.read_text(encoding="utf-8"))
    profiles = load_profiles()

    OUT.mkdir(parents=True, exist_ok=True)
    man = {"generated": t0, "tool": "code/build_cycle_inputs.py", "python": sys.version, "numpy": np.__version__,
           "frozen_inputs": found, "recorded_input_hashes": {str(k): v for k, v in RECORDED.items()},
           "method": "sampled task = R3 run_gates.reference(cycle): t = np.arange(0, duration + 1e-9, 1.0), "
                     "v = np.interp(t, knots_t, knots_v); knots = eureka.cycles.build(YAML segments)",
           "cycles": {}}
    for c in CYCLES:
        prof = profiles[c]
        t_r3, v_r3 = run_gates.reference(c)
        tk = taskmod.load_task(c)
        retained = r3_retained(c)
        checks = {
            "r4_load_task_t_bitwise": bool(np.array_equal(tk.t, t_r3)),
            "r4_load_task_v_bitwise": bool(np.array_equal(tk.v_ref, v_r3)),
            "n_r3_retained_files": len(retained),
            "r3_retained_hashes_ok": all(r["hash_ok"] for r in retained),
            "r3_retained_t_bitwise": all(np.array_equal(r["t"], t_r3) for r in retained),
            "r3_retained_v_bitwise": all(np.array_equal(r["v"], v_r3) for r in retained),
            "uniform_1s_grid": bool(np.all(np.diff(t_r3) == 1.0) and t_r3[0] == 0.0),
            "starts_and_ends_at_rest": bool(v_r3[0] == 0.0 and v_r3[-1] == 0.0),
            "d_ref_matches_protocol_3dp": round(tk.d_ref, 3) == PROTOCOL_PRINTED[c][0],
            "T_ref_matches_protocol": tk.T_ref == PROTOCOL_PRINTED[c][1],
        }
        bad = [k for k, v in checks.items() if v is False or (k == "n_r3_retained_files" and v == 0)]
        if bad:
            raise SystemExit(f"STOP: {c}: failed checks {bad}; no sampled artefact written")

        src = {"cycle": c, "source_file": "configs/cycles/profiles.yaml", "source_sha256": RECORDED[frozen.PROFILES_YAML],
               "definition": raw[c], "builder": "eureka.cycles.build (src/eureka/cycles.py)",
               "builder_sha256": RECORDED[EUREKA_CYCLES]}
        h_src = write_new(OUT / f"{c}_source_segments.json", json.dumps(src, indent=1) + "\n")
        h_knots = write_new(OUT / f"{c}_knots_from_yaml.csv", csv_text(["t_s", "v_mps"], [prof.knots_t, prof.knots_v]))
        p_samp = OUT / f"{c}_sampled_h1.csv"
        h_samp = write_new(p_samp, csv_text(["t_s", "v_mps"], [t_r3, v_r3]))
        _, (t_back, v_back) = read_csv_cols(p_samp)
        if not (np.array_equal(t_back, t_r3) and np.array_equal(v_back, v_r3)):
            raise SystemExit(f"STOP: {c}: sampled CSV does not round-trip bit for bit")
        stops = stop_table(tk, prof.knots_t, prof.knots_v)
        man["cycles"][c] = {
            "role": "primary held-out (protocol 3, 8.1)" if c == "S2" else "in-sample (protocol 3)",
            "artefacts": {f"{c}_source_segments.json": h_src, f"{c}_knots_from_yaml.csv": h_knots,
                          f"{c}_sampled_h1.csv": h_samp},
            "canonical_sampled_sha256": h_samp,
            "yaml_profile": {"n_knots": int(len(prof.knots_t)), "duration_s": prof.duration,
                             "distance_m": float(prof.stats()["distance_m"]),
                             "n_knots_off_whole_seconds": int(np.sum(prof.knots_t != np.round(prof.knots_t)))},
            "sampled_task": {"n_samples": int(len(t_r3)), "t_first_s": float(t_r3[0]), "t_last_s": float(t_r3[-1]),
                             "h_s": 1.0, "T_ref_s": tk.T_ref, "d_ref_m": tk.d_ref, "a_lo": tk.a_lo, "a_hi": tk.a_hi,
                             "v_max_ms": float(v_r3.max()), "n_rest_intervals": len(tk.rest),
                             "n_segments": len(tk.segs),
                             "segments": [dict(k=k, ks=ks, ke=ke, D_k_m=D, T_k_s=T, v_lim_ms=vl)
                                          for k, ((ks, ke), D, T, vl) in enumerate(zip(tk.segs, tk.D, tk.T_seg, tk.v_lim))],
                             "rest_intervals": stops},
            "checks": checks,
            "r3_retained_files": [{k: r[k] for k in ("path", "sha256_recorded", "sha256_now", "hash_ok")} for r in retained],
        }
        print(c, "ok:", {k: v for k, v in checks.items()}, "sampled sha256", h_samp)
    h_man = write_new(OUT / "cycle_inputs_manifest.json", json.dumps(man, indent=1, default=float) + "\n")
    print("cycle_inputs_manifest.json", h_man)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
