"""Search the whole project root for original computational provenance of the thesis figures.

    python -I tools/provenance_inventory.py
        -> outputs/inventory_summary.json     per-folder counts and mtime ranges, pre-audit files,
                                              provenance-type files, name hits, .git reflog start
        -> outputs/inventory_type_files.csv   every provenance-type file outside third-party trees
        -> outputs/inventory_claim_string_hits.csv   text files containing the headline numbers

Read-only: only os.stat and file reads. No git command is executed; the .git directory is
counted and its plain-text reflog (.git/logs/HEAD) is read for the first commit time.
Scope is the project root only. D:\\EUREKA and every other folder outside the root are
deliberately not opened (owner instruction of 2026-10-23).
"""

import csv
import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
ROOT = HERE.parents[2]
OUT = HERE / "outputs"
AUDIT_START = datetime(2026, 10, 23, 0, 0, tzinfo=timezone(timedelta(hours=7))).timestamp()
THIRD_PARTY = {".venv", "tools", "cache", ".git"}
# third-party trees inside verification/ (OpenModelica user libraries, a separate Python env)
THIRD_PARTY_SUB = ("verification/omc-userdata/", "verification/python-env/")

PROVENANCE_EXT = {".m", ".mlx", ".slx", ".slxc", ".mdl", ".sldd", ".mat", ".fig", ".xlsx", ".xls",
                  ".xlsm", ".csv", ".npz", ".npy", ".pkl", ".pickle", ".h5", ".hdf5", ".parquet",
                  ".ipynb", ".tex", ".bib", ".docx", ".doc", ".pdf", ".py", ".yaml", ".yml", ".json",
                  ".log", ".c", ".h"}
# names given in thesis Appendix C (para 6821-6851, 6860-6863) and earlier project records
NAME_PATTERNS = [r"vehicle_params\.py", r"vehicle_dynamics\.py", r"battery_model\.py", r"lqr_baseline\.py",
                 r"adaptive_lqr\.(py|c|h)", r"ekf_soh_estimator\.py", r"soh_estimator\.py", r"regen_braking\.py",
                 r"pareto_optimization\.py", r"drive_cycles\.py", r"simulation_runner\.py", r"results_analysis\.py",
                 r"statistical_analysis\.py", r"sensitivity_analysis\.py", r"visualization\.py", r"gain_table\.h",
                 r"render_kt01", r"kt01", r"KT01_FINAL_REPORT", r"AUDIT_REPORT", r"DATA_AND_COLAB_PROMPTS"]
TEXT_EXT = {".md", ".csv", ".json", ".yaml", ".yml", ".txt", ".py", ".tex", ".bib", ".log", ".ps1",
            ".toml", ".html", ".tsv", ".mos", ".m", ".ipynb", ".xml", ".cfg", ".ini"}
CLAIM_RX = re.compile(rb"12[.,]5 ?%|15[.,]3 ?%|\xc2\xb1 ?2[.,]1|\xc2\xb1 ?2[.,]8")


def rel(p):
    return p.relative_to(ROOT).as_posix()


def iso(ts):
    return datetime.fromtimestamp(ts, timezone(timedelta(hours=7))).isoformat(timespec="seconds")


def main():
    OUT.mkdir(exist_ok=True)
    per_top = defaultdict(lambda: {"files": 0, "min_mtime": None, "max_mtime": None, "pre_audit": 0})
    pre_audit_outside, type_rows, name_hits, claim_hits = [], [], [], []
    tp_type_counts = Counter()
    pre_audit_tools = Counter()
    own = rel(HERE) + "/"
    for dirpath, dirnames, filenames in os.walk(ROOT):
        for fn in filenames:
            p = Path(dirpath) / fn
            try:
                st = p.stat()
            except OSError as e:
                per_top["<stat-error>"]["files"] += 1
                continue
            r = rel(p)
            top = r.split("/", 1)[0] if "/" in r else "<root files>"
            d = per_top[top]
            d["files"] += 1
            d["min_mtime"] = st.st_mtime if d["min_mtime"] is None else min(d["min_mtime"], st.st_mtime)
            d["max_mtime"] = st.st_mtime if d["max_mtime"] is None else max(d["max_mtime"], st.st_mtime)
            third = top in THIRD_PARTY or r.startswith(THIRD_PARTY_SUB)
            if st.st_mtime < AUDIT_START:
                d["pre_audit"] += 1
                if third:
                    pre_audit_tools["/".join(r.split("/")[:3])] += 1
                else:
                    pre_audit_outside.append({"path": r, "mtime": iso(st.st_mtime), "size": st.st_size})
            ext = p.suffix.lower()
            for rx in NAME_PATTERNS:
                if re.search(rx, fn, re.I):
                    name_hits.append({"pattern": rx, "path": r, "mtime": iso(st.st_mtime), "size": st.st_size})
            if ext in PROVENANCE_EXT:
                if third:
                    tp_type_counts[(top if top in THIRD_PARTY else "/".join(r.split("/")[:2]), ext)] += 1
                elif not r.startswith(own):
                    type_rows.append({"path": r, "ext": ext, "size": st.st_size, "mtime": iso(st.st_mtime),
                                      "pre_audit": st.st_mtime < AUDIT_START})
            if (not third and not r.startswith(own) and ext in TEXT_EXT and st.st_size < 50_000_000):
                try:
                    n = len(CLAIM_RX.findall(p.read_bytes()))
                except OSError:
                    n = -1
                if n:
                    claim_hits.append({"path": r, "hits": n, "mtime": iso(st.st_mtime),
                                       "pre_audit": st.st_mtime < AUDIT_START})

    reflog = (ROOT / ".git" / "logs" / "HEAD").read_text(encoding="utf-8", errors="replace").splitlines()
    first = reflog[0].split("\t")[0].split() if reflog else []
    first_commit = {"line": reflog[0] if reflog else None,
                    "time": iso(int(first[-2])) if len(first) >= 2 else None, "reflog_entries": len(reflog)}

    summary = {
        "root": str(ROOT),
        "audit_start_reference": iso(AUDIT_START),
        "per_top_level": {k: {**v, "min_mtime": v["min_mtime"] and iso(v["min_mtime"]),
                              "max_mtime": v["max_mtime"] and iso(v["max_mtime"])} for k, v in sorted(per_top.items())},
        "pre_audit_files_outside_third_party_trees": pre_audit_outside,
        "pre_audit_files_in_third_party_trees_by_prefix": dict(pre_audit_tools.most_common()),
        "provenance_type_counts_in_third_party_trees": {f"{a} {b}": n for (a, b), n in sorted(tp_type_counts.items())},
        "provenance_type_counts_outside": dict(Counter(r["ext"] for r in type_rows)),
        "provenance_type_files_outside_pre_audit": [r for r in type_rows if r["pre_audit"]],
        "name_pattern_hits": name_hits,
        "claim_string_files": len(claim_hits),
        "claim_string_files_pre_audit": [h for h in claim_hits if h["pre_audit"]],
        "git_first_reflog_entry": first_commit,
        "not_searched": ["anything outside the project root (D:\\EUREKA in particular, by owner instruction)",
                         "contents of compressed Git objects (no git command run)",
                         "binary files for the claim strings (only the TEXT_EXT types were read)"],
    }
    (OUT / "inventory_summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False), encoding="utf-8")
    with open(OUT / "inventory_type_files.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["path", "ext", "size", "mtime", "pre_audit"])
        w.writeheader()
        w.writerows(sorted(type_rows, key=lambda r: r["path"]))
    with open(OUT / "inventory_claim_string_hits.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["path", "hits", "mtime", "pre_audit"])
        w.writeheader()
        w.writerows(sorted(claim_hits, key=lambda r: r["path"]))

    total = sum(v["files"] for v in per_top.values())
    print(f"{total} files walked; pre-audit outside third-party trees: {len(pre_audit_outside)}")
    for x in pre_audit_outside:
        print("   ", x)
    print("pre-audit in third-party trees:", dict(pre_audit_tools.most_common(8)))
    print("name hits:", len(name_hits), sorted({h['path'] for h in name_hits})[:30])
    print("provenance-type files outside:", summary["provenance_type_counts_outside"])
    print("claim-string files:", len(claim_hits), "of which pre-audit:", len(summary["claim_string_files_pre_audit"]))
    print("first reflog entry:", first_commit["time"])


if __name__ == "__main__":
    main()
