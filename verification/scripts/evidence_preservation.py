"""Evidence preservation tooling for the controller cross-verification (2026-10-24).

usage (from the project root, any Python with the standard library):
  python verification/scripts/evidence_preservation.py archive     copy-only: compress selected ignored/volatile files into verification/evidence-archive/
  python verification/scripts/evidence_preservation.py inventory   write verification/evidence-preservation-inventory.csv (plan and final inventory)
  python verification/scripts/evidence_preservation.py verify      re-hash everything the inventory lists, the archive, the raw gz archives and the baseline

Nothing here deletes, moves, rewrites or regenerates a scientific artifact. 'archive' only reads originals and writes new
.gz copies (mtime 0, so they are deterministic); each copy is decompressed and compared with the original hash before it is kept.
"""
import csv
import gzip
import hashlib
import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
os.chdir(ROOT)
ARCH = "verification/evidence-archive"
INV = "verification/evidence-preservation-inventory.csv"
OLD_MANIFEST = "verification/controller-crosscheck-artifact-manifest.csv"
BIG_LOG = 2_000_000  # solver-status logs above this size are archived compressed instead of tracked
BUILD_DIRS = ("cases", "cases_ctl", "cases_v0.1.0_when_pre")
NOISE_PREFIX = ("verification/python-env/", "verification/omc-userdata/", "verification/openmodelica-smoke/out/",
                "verification/modelica-build/launcher-smoke/", "verification/modelica-build/tmp/")
COLUMNS = ["path", "size_bytes", "sha256", "git_state_before", "ignore_rule", "tier", "action", "category", "run_id", "supports",
           "archive_path", "archive_size_bytes", "archive_sha256", "reason"]


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def sha_gz(path):
    h = hashlib.sha256()
    with gzip.open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def git(*args, inp=None):
    return subprocess.run(["git", "-c", "core.quotepath=off", *args], capture_output=True, input=inp, cwd=ROOT).stdout.decode("utf-8")


def walk(top):
    for dp, _, fn in os.walk(top):
        for f in fn:
            yield (dp + "/" + f).replace("\\", "/")


def ignore_rules(paths):
    out = git("check-ignore", "-v", "-n", "--stdin", inp=("\n".join(paths) + "\n").encode("utf-8"))
    res = {}
    for line in out.splitlines():
        meta, p = line.split("\t", 1)
        res[p] = meta if meta.strip(":") else ""
    return res


def run_id(p):
    parts = p.split("/")
    if "modelica-build" in parts:
        i = parts.index("modelica-build")
        if parts[i + 1] in BUILD_DIRS:
            return parts[i + 2]
        if parts[i + 1] == "logs":
            n = parts[-1]
            return n.split("-", 2)[-1] if n[:8].isdigit() else n
    n = os.path.basename(p)
    for suf in (".csv.gz", "_res.csv", ".npz", ".csv", ".json"):
        if n.endswith(suf):
            return n[: -len(suf)]
    return ""


def archive_candidates():
    """Files that exist only in ignored build folders and are evidence, not build output."""
    out = []
    for d in BUILD_DIRS:
        for p in walk(f"verification/modelica-build/{d}"):
            if p.endswith("_res.csv") or p.endswith(".log"):
                out.append(p)
    for p in walk("verification/modelica-build/logs"):
        if os.path.getsize(p) > BIG_LOG:
            out.append(p)
    out += [p for p in walk("verification/modelica-build/python_reference")]
    return sorted(set(out))


def covered_by_raw_gz():
    """sha256 of every uncompressed result CSV that a gz in controller-crosscheck-runs/raw reproduces exactly."""
    m = {}
    for p in walk("verification/controller-crosscheck-runs/raw"):
        if p.endswith(".gz"):
            m[sha_gz(p)] = p
    return m


def cmd_archive():
    cov = covered_by_raw_gz()
    done, skipped = 0, 0
    for p in archive_candidates():
        h = sha(p)
        if p.endswith("_res.csv") and h in cov:
            skipped += 1
            continue
        dst = pathlib.Path(ARCH) / (p[len("verification/"):] + ".gz")
        if dst.exists() and sha_gz(dst) == h:
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        tmp = dst.with_name(dst.name + ".partial")
        with open(p, "rb") as src, open(tmp, "wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as gz:
            for b in iter(lambda: src.read(1 << 22), b""):
                gz.write(b)
        if sha_gz(tmp) != h or sha(p) != h:  # hash of the copy and of the original, after the copy
            tmp.unlink()
            raise SystemExit(f"hash mismatch while archiving {p}")
        os.replace(tmp, dst)
        done += 1
    print(f"archived {done}; skipped {skipped} (result CSV reproduced exactly by a gz in controller-crosscheck-runs/raw)")


# ---------------------------------------------------------------- classification
CTRL_CASES = json.loads(pathlib.Path("verification/modelica/scripts/controller_cases.json").read_text(encoding="utf-8"))
STAGE_SUPPORT = {
    "primary": "controller-crosscheck-results.csv (primary S1/S2 grid rows); controller-crosscheck-report.md sec 4.1, 4.4",
    "ptune": "ptune_solver_study.csv; references/controller_solver_selection.json; protocol sec 7, A2, A3; report sec 4.2",
    "sens": "controller-crosscheck-results.csv (numerical-sensitivity rows); report sec 4.2",
    "step": "controller-crosscheck-runs/step_input_tests.json; protocol sec 6.1; report sec 4.6",
    "unit": "controller-crosscheck-runs/preliminary_checks.json; protocol sec 6; report sec 4.1",
}


def supports_for(p, rid):
    if rid in CTRL_CASES:
        return STAGE_SUPPORT[CTRL_CASES[rid]["stage"]]
    if rid.startswith("DIAG_S1_fixed_maxstep") or rid.startswith("DIAG_ida"):
        return "protocol A2 / A3 amendment evidence; report sec 3, 4.3, 5; integrity review sec 3, 4"
    if "/cases_v0.1.0_when_pre/" in p:
        return "superseded earlier plant-verification run (before the event-timing fix); independent-model-report.md; modelica-check-results.csv"
    if "/modelica-build/cases/" in p or "/modelica-build/python_reference/" in p:
        return "modelica-check-results.csv; independent-model-report.md; cross-implementation-comparison.csv"
    if "/modelica-build/logs/" in p:
        return "simulation-status record of one omc launch; controller-crosscheck-runlog.md; report sec 3, 5"
    return ""


def classify(p, state, in_raw_cov):
    """-> (tier, action, category, reason). state in tracked/untracked/ignored."""
    if state == "tracked":
        return "A", "tracked-unchanged", "already-tracked", "already in Git; not modified by this work"
    if p.startswith(("audit/", "technical-")):
        return "A", "track", "audit", "claim audit record (earlier phase); small text, untracked since it was written"
    if p.startswith("artifacts/"):
        return "B", "retain-in-place", "baseline-artifact", "Python baseline outputs; outside Git by project policy (.gitignore, docs/lineage.md); hashes tracked in evidence/artifact_hashes.json"
    if p.startswith("data/") or p.startswith("logs/") or p.endswith("EURÉKA 2026 - KT.docx"):
        return "B", "retain-in-place", "baseline-input", "baseline inputs/logs (incl. the frozen thesis copy); outside Git by project policy; never modify"
    if p.startswith(NOISE_PREFIX):
        return "C", "retain-ignored", "build-cache", "regenerable build/cache output"
    if p.startswith("verification/controller-crosscheck-runs/raw/"):
        return "B", "retain-in-place", "modelica-raw-gz", "primary raw evidence (compressed Modelica results); too large for ordinary Git history"
    if p.startswith("verification/controller-crosscheck-runs/python_reference/"):
        return "B", "retain-in-place", "python-reference", "Python reference series used for tolerances; 48 MB of .npz, not ordinary-Git material"
    if p.startswith("verification/evidence-archive/"):
        return "B", "archive-store", "evidence-archive", "compressed copies of evidence that exists only in ignored build folders"
    parts = p.split("/")
    if len(parts) > 2 and parts[1] == "modelica-build":
        d = parts[2]
        if d in BUILD_DIRS:
            if p.endswith("_res.csv"):
                if in_raw_cov:
                    return "B", "retain-in-place", "modelica-raw-uncompressed-redundant", "byte-identical to a gz in controller-crosscheck-runs/raw (hash-verified); kept, not deleted"
                return "B", "archive-copy", "modelica-raw-uncompressed", "result CSV that exists only here; compressed copy in evidence-archive"
            if p.endswith(".log"):
                return "B", "archive-copy", "case-solver-log", "per-case executable log (solver statistics); compressed copy in evidence-archive"
            return "C", "retain-ignored", "build-output", "compiler/linker output; regenerable from tracked sources and scripts"
        if d == "python_reference":
            return "B", "archive-copy", "plant-python-reference", "plant-phase Python reference series; compressed copy in evidence-archive"
        if d == "logs":
            if os.path.getsize(p) > BIG_LOG:
                return "B", "archive-copy", "sim-status-log-large", "solver-status log above 2 MB (CVODE output); compressed copy in evidence-archive, original kept"
            return "A", "track", "sim-status-log", "omc launch record incl. SimulationResult status blocks; not regenerable without rerun"
        return "A", "track", "build-record", "small failure/diagnostic record kept at its original path (names the first, defective runs)"
    if p.startswith("verification/fastsim-smoke/") and p.endswith(".csv"):
        return "A?", "defer-review", "smoke-output", "ancillary FASTSim smoke time series (2 MB); not a headline-result artifact; left untracked for owner review"
    if p.startswith("verification/logs/om-baseline-"):
        return "A?", "defer-review", "machine-state-log", "snapshot of the user PATH and profile folders (machine-specific); left untracked for owner review"
    if p.endswith((".pyc", ".pyo")) or "/__pycache__/" in p:
        return "C", "retain-ignored", "cache", "bytecode cache"
    return "A", "track", "source-or-record", "source, script, protocol, report, result table or JSON summary"


def cmd_inventory():
    old = {r["path"]: r for r in csv.DictReader(open(OLD_MANIFEST, encoding="utf-8"))}
    tracked = set(git("ls-files").splitlines())
    paths = set(old)
    for top in ("verification", "audit", "artifacts", "data", "logs", "protocol", "evidence"):
        paths.update(walk(top))
    paths.update(["technical-claim-matrix.csv", "technical-foundation-audit.md"])
    thesis = [f for f in os.listdir(".") if f.endswith(".docx")]
    paths.update(thesis)
    # the preservation layer itself (inventory, guide, report, .gitignore, .gitattributes) is hashed in the report, not in the inventory
    paths -= {INV, "verification/evidence-preservation-report.md", "verification/evidence-storage-guide.md"}
    paths = sorted(p for p in paths if not p.startswith(ARCH + "/") and not p.endswith(".partial"))
    ign = ignore_rules(paths)
    cov = covered_by_raw_gz()
    cov_paths = set()
    for p in paths:
        if p.endswith("_res.csv") and "/modelica-build/cases_ctl/" in p and sha(p) in cov:
            cov_paths.add(p)
    rows, groups = [], {}
    for p in paths:
        state = "tracked" if p in tracked else ("ignored" if ign.get(p) else "untracked")
        tier, action, cat, reason = classify(p, state, p in cov_paths)
        if tier == "C" or (tier == "B" and action == "retain-ignored"):
            key = next((n for n in NOISE_PREFIX if p.startswith(n)), None) or ("/".join(p.split("/")[:3]) if "/modelica-build/" in p else p.rsplit("/", 1)[0])
            g = groups.setdefault((key, cat, state, ign.get(p, "")), [0, 0, reason, tier, action])
            g[0] += 1
            g[1] += os.path.getsize(p)
            continue
        size = os.path.getsize(p)
        rid = run_id(p)
        arch_path = arch_size = arch_sha = ""
        if action == "archive-copy":
            ap = pathlib.Path(ARCH) / (p[len("verification/"):] + ".gz")
            if ap.exists():
                arch_path, arch_size, arch_sha = ap.as_posix(), ap.stat().st_size, sha(ap)
        rows.append({"path": p, "size_bytes": size, "sha256": sha(p), "git_state_before": state,
                     "ignore_rule": ign.get(p, ""), "tier": tier, "action": action, "category": cat, "run_id": rid, "supports": supports_for(p, rid),
                     "archive_path": arch_path, "archive_size_bytes": arch_size, "archive_sha256": arch_sha, "reason": reason})
    for (d, cat, state, rule), (n, size, reason, tier, action) in sorted(groups.items()):
        rows.append({"path": d.rstrip("/") + "/  [group]", "size_bytes": size, "sha256": "", "git_state_before": state, "ignore_rule": rule, "tier": tier, "action": action,
                     "category": cat, "run_id": "", "supports": "", "archive_path": "", "archive_size_bytes": "", "archive_sha256": "",
                     "reason": f"{n} files; {reason}"})
    with open(INV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {INV}: {len(rows)} rows")


def cmd_verify():
    rows = list(csv.DictReader(open(INV, encoding="utf-8")))
    bad = []
    n = 0
    for r in rows:
        if not r["sha256"]:
            continue
        p = r["path"]
        n += 1
        if not os.path.exists(p):
            bad.append(("missing", p)); continue
        if os.path.getsize(p) != int(r["size_bytes"]) or sha(p) != r["sha256"]:
            bad.append(("changed", p))
        if r["archive_path"]:
            if not os.path.exists(r["archive_path"]):
                bad.append(("archive missing", r["archive_path"]))
            elif sha(r["archive_path"]) != r["archive_sha256"] or sha_gz(r["archive_path"]) != r["sha256"]:
                bad.append(("archive differs", r["archive_path"]))
    unc = {r["sha256"]: r["path"] for r in rows if r["category"] == "modelica-raw-uncompressed-redundant"}
    for p in walk("verification/controller-crosscheck-runs/raw"):
        if p.endswith(".gz") and sha_gz(p) not in unc:
            bad.append(("raw gz not reproducing a listed CSV", p))
    base = json.loads(pathlib.Path("evidence/artifact_hashes.json").read_text(encoding="utf-8"))["sha256"]
    for p, h in base.items():
        if not os.path.exists(p) or sha(p) != h:
            bad.append(("baseline", p))
    print(f"checked {n} listed files, {len(base)} baseline hashes; problems: {len(bad)}")
    for b in bad:
        print("  ", b)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    {"archive": cmd_archive, "inventory": cmd_inventory, "verify": cmd_verify}[sys.argv[1]]()
