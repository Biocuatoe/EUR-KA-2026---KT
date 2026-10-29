"""Validate original EPA schedule files and write processed CSVs. Originals are only read."""
import hashlib, json, pathlib, re, sys
import numpy as np, pandas as pd

root = pathlib.Path(sys.argv[1])
raw = root / "data/raw/drive_cycles/epa"
proc = root / "data/processed/drive_cycles/epa"; proc.mkdir(parents=True, exist_ok=True)
MPH = 0.44704  # m/s per mph, exact by definition (1 mile = 1609.344 m)
sha = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
FILES = {"UDDS": "uddscol.txt", "HWFET": "hwycol.txt", "US06": "us06col.txt"}
fs_ref = {"UDDS": "zoe_udds_timeseries.csv", "HWFET": "zoe_hwfet_timeseries.csv"}
out = {}
for name, fn in FILES.items():
    p = raw / fn
    before = sha(p)
    text = p.read_bytes().decode("ascii")  # raises if any non-ASCII byte
    lines = text.split("\r\n")
    trailing_blank = lines[-1] == ""
    if trailing_blank: lines = lines[:-1]
    title, header, body = lines[0], lines[1], lines[2:]
    problems = []
    rows = []
    for i, ln in enumerate(body, start=3):
        parts = ln.split("\t")
        if len(parts) != 2: problems.append(f"line {i}: {len(parts)} fields: {ln!r}"); continue
        try: rows.append((float(parts[0]), float(parts[1])))
        except ValueError: problems.append(f"line {i}: non-numeric {ln!r}")
    a = np.array(rows)
    t, v = a[:, 0], a[:, 1]
    dt = np.diff(t)
    chk = {
        "title_line": title, "header_line": header.strip('"'),
        "header_declares_secs_and_mph": bool(re.search(r"secs", header, re.I) and re.search(r"mph", header, re.I)),
        "n_rows": int(len(a)), "malformed_rows": problems,
        "t_start": float(t[0]), "t_end": float(t[-1]),
        "t_integer_valued": bool(np.all(t == np.round(t))),
        "dt_min": float(dt.min()), "dt_max": float(dt.max()), "strictly_increasing_unit_step": bool(np.all(dt == 1.0)),
        "any_nan_or_inf": bool(~np.isfinite(a).all()), "speed_min_mph": float(v.min()), "speed_max_mph": float(v.max()),
        "starts_and_ends_at_rest": bool(v[0] == 0 and v[-1] == 0),
        "max_accel_mph_per_s": float(np.max(np.diff(v))), "max_decel_mph_per_s": float(np.min(np.diff(v))),
        "distance_trapezoid_miles": float(np.trapezoid(v, t) / 3600.0),
        "distance_trapezoid_km": float(np.trapezoid(v * MPH, t) / 1000.0),
        "mean_speed_mph": float(np.trapezoid(v, t) / (t[-1] - t[0])),
        "crlf_endings": True, "trailing_blank_after_last_row": trailing_blank,
        "original_sha256_before": before,
    }
    df = pd.DataFrame({"time_s": t, "speed_mph_original": v, "speed_m_per_s": v * MPH})
    pp = proc / f"epa_{name.lower()}_1hz.csv"
    df.to_csv(pp, index=False, float_format="%.10g", lineterminator="\n")
    chk["processed_file"] = str(pp.relative_to(root)).replace("\\", "/"); chk["processed_sha256"] = sha(pp)
    if name in fs_ref:  # independent cross-check against FASTSim's separately packaged cycle
        f = pd.read_csv(root / "verification/fastsim-smoke" / fs_ref[name])
        fv, ft = f["cyc.speed_meters_per_second"].to_numpy(), f["cyc.time_seconds"].to_numpy()
        n = min(len(fv), len(v))
        chk["vs_fastsim_bundled"] = {"fastsim_rows": int(len(fv)), "epa_rows": int(len(v)), "same_length": bool(len(fv) == len(v)),
                                     "max_abs_speed_diff_m_s": float(np.max(np.abs(fv[:n] - v[:n] * MPH))),
                                     "time_axes_identical": bool(np.array_equal(ft[:n], t[:n]))}
    chk["original_sha256_after"] = sha(p); chk["original_unchanged"] = chk["original_sha256_after"] == before
    out[name] = chk
(root / "data/processed/drive_cycles/epa/validation_results.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print(json.dumps(out, indent=2))
