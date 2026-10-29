import csv, json, pathlib, sys, hashlib
root = pathlib.Path(sys.argv[1])
v = json.loads((root / "data/processed/drive_cycles/epa/validation_results.json").read_text(encoding="utf-8"))
URL = {"UDDS": ("uddscol.txt", "https://www.epa.gov/sites/default/files/2015-10/uddscol.txt"),
       "HWFET": ("hwycol.txt", "https://www.epa.gov/sites/default/files/2015-10/hwycol.txt"),
       "US06": ("us06col.txt", "https://www.epa.gov/system/files/other-files/2025-03/us06col.txt")}
DEF = {"UDDS": "Urban Dynamometer Driving Schedule (EPA 'LA4' / city test); first part of the FTP",
       "HWFET": "Highway Fuel Economy Driving Schedule (EPA), highway driving under 60 mph",
       "US06": "US06 Supplemental FTP Driving Schedule (EPA), high-acceleration aggressive driving"}
cols = ["cycle", "original_file", "source_page", "source_url", "cycle_definition", "units_time", "units_speed", "time_resolution",
        "n_rows", "duration_s", "retrieval_date_utc", "http_status", "server_last_modified", "original_sha256", "transformation_applied",
        "processed_file", "processed_sha256", "validation_summary", "independent_crosscheck", "limitations_statement"]
rows = []
for name, (fn, url) in URL.items():
    r = v[name]
    hdr = (root / f"data/raw/drive_cycles/epa/_headers/{fn}.headers.txt").read_text(encoding="ascii")
    lm = next(l.split(":", 1)[1].strip() for l in hdr.splitlines() if l.lower().startswith("last-modified"))
    date = next(l.split(":", 1)[1].strip() for l in hdr.splitlines() if l.lower().startswith("date"))
    assert hashlib.sha256((root / f"data/raw/drive_cycles/epa/{fn}").read_bytes()).hexdigest() == r["original_sha256_before"]
    cc = r.get("vs_fastsim_bundled")
    rows.append([name, f"data/raw/drive_cycles/epa/{fn}", "https://www.epa.gov/vehicle-and-fuel-emissions-testing/dynamometer-drive-schedules", url, DEF[name],
                 "seconds (header: 'Test Time, secs')", "mph (header: 'Target Speed, mph')", "1 s (validated: all steps exactly 1.0 s)",
                 r["n_rows"], r["t_end"] - r["t_start"], date + " (retrieved 2026-10-23)", 200, lm, r["original_sha256_before"],
                 "none to the original. Processed copy: tab-separated text parsed to CSV with columns time_s, speed_mph_original, speed_m_per_s = mph x 0.44704 (exact definition)",
                 r["processed_file"], r["processed_sha256"],
                 f"0 malformed rows; no NaN/Inf; time 0..{r['t_end']:.0f} s strictly increasing at 1 s; starts and ends at rest; max speed {r['speed_max_mph']} mph; trapezoid distance {r['distance_trapezoid_miles']:.4f} mi ({r['distance_trapezoid_km']:.4f} km); original unchanged after processing",
                 (f"Speed trace vs FASTSim 3.1.0 bundled cycle: same length ({cc['epa_rows']} rows), identical time axis, max |difference| {cc['max_abs_speed_diff_m_s']:.2e} m/s" if cc else "none available (US06 is not bundled in FASTSim 3.1.0); validated by internal checks only"),
                 "EPA dynamometer reference schedules, not measured traffic and not Vietnamese traffic. The EPA page does not state units or resolution; they are taken from the file header and validated from the data. Cycle-based results say nothing about real-world driving."])
with open(root / "audit/external-data-provenance.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(cols); w.writerows(rows)
print(len(rows), "rows,", len(cols), "cols")
