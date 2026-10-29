"""Run selected cases of a generated .mos script one per launcher invocation, with an output-size guard (protocol amendment A1).

usage: python guarded_run.py <root> <mos file (relative)> <label> <max_MB> <case1> [case2 ...]
For each case: extract its 3 lines from the .mos, run the launcher on a one-case script, poll the result CSV size every 3 s, and if it exceeds
max_MB terminate the case's simulation executable (omc then crashes; the launcher still removes its alias) and write an evidence file
under verification/controller-crosscheck-runs/failed_runs/, deleting the oversized CSV/log. Simulation status stays read from the omc record.
"""
import hashlib, pathlib, subprocess, sys, time
root = pathlib.Path(sys.argv[1]); mos = root / sys.argv[2]; label = sys.argv[3]; max_b = float(sys.argv[4]) * 1e6; cases = sys.argv[5:]
lines = mos.read_text(encoding="ascii").splitlines()
head = [l for l in lines[:4]]
out_dir = root / "verification/controller-crosscheck-runs/failed_runs"; out_dir.mkdir(parents=True, exist_ok=True)
for c in cases:
    i = next(k for k, l in enumerate(lines) if l.startswith(f'mkdir("cases_ctl/{c}")'))
    one = root / f"verification/modelica/scripts/_single_{c}.mos"
    one.write_text("\n".join(head + lines[i:i + 3]) + "\n", encoding="ascii")
    res = root / f"verification/modelica-build/cases_ctl/{c}/{c}_res.csv"
    p = subprocess.Popen(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(root / "verification/Invoke-OpenModelica.ps1"), "-Label", f"{label}_{c}", "-Mos", str(one.relative_to(root))],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
    killed = False
    t0 = time.time()
    while p.poll() is None:
        time.sleep(3)
        if res.exists() and res.stat().st_size > max_b and not killed:
            subprocess.run(["taskkill", "/F", "/IM", f"{c}.exe"], capture_output=True)
            killed = True
    outp = p.stdout.read()
    size = res.stat().st_size if res.exists() else 0
    msg = f"{c}: launcher exit {p.returncode}, {time.time() - t0:.0f} s, csv {size / 1e6:.1f} MB, guard_triggered={killed}"
    if killed or size > max_b:
        ev = out_dir / f"{c}_evidence.txt"
        sha = hashlib.sha256(res.read_bytes()).hexdigest() if size < 2e10 else "n/a"
        with open(ev, "w", encoding="utf-8") as f:
            f.write(f"# {c}: output-size guard triggered at {max_b / 1e6:.0f} MB; csv bytes {size}; sha256 {sha}\n--- csv header+first rows\n")
            with open(res, encoding="utf-8") as r:
                for _ in range(4): f.write(r.readline())
            f.write("--- csv last bytes\n"); r = open(res, "rb"); r.seek(max(0, size - 1500)); f.write(r.read().decode("utf-8", "replace")); r.close()
            lg = res.with_suffix("").with_name(f"{c}.log")
            if lg.exists():
                f.write(f"\n--- log: {lg.stat().st_size} bytes; first lines\n"); f.write("".join(open(lg, encoding="utf-8", errors="replace").readlines()[:5]))
        res.unlink(); 
        if lg.exists(): lg.unlink()
        msg += f" -> evidence {ev.name}, big files deleted"
    one.unlink()
    print(msg, flush=True)
