"""Byte-aware comparison of the pilot's code/ and config/ against an archived state. For every changed or added file:
the CRLF / LF-only / bare-CR line counts before and after, the file's convention before and after, whether every added
line uses the convention of the original (for an added file: its own, which must not be mixed), and a unified diff in
which every line shows its ending ([CRLF] or [LF]). Refuses to overwrite. Exit 1 if a convention changed or a mixed file
appeared. Usage: eol_diff.py <pilot_dir> <archive_name> <out_csv> <out_diff_txt>"""
import csv, difflib, hashlib, sys
from pathlib import Path

pilot, arch, out_csv, out_txt = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4])
for p in (out_csv, out_txt):
    if p.exists():
        sys.exit(f"refused: {p} exists")
old_root = pilot / "archive" / arch
sha = lambda b: hashlib.sha256(b).hexdigest()


def counts(b):
    crlf = b.count(b"\r\n")
    return crlf, b.count(b"\n") - crlf, b.count(b"\r") - crlf


def conv(c):
    crlf, lf, cr = c
    return "CRLF" if crlf and not lf and not cr else "LF" if lf and not crlf and not cr else "EMPTY" if not (crlf or lf or cr) else "MIXED"


rows, diff_lines, bad = [], [], []
for new in sorted(p for d in ("code", "config") for p in (pilot / d).rglob("*") if p.is_file()):
    rel = new.relative_to(pilot).as_posix()
    old = old_root / rel
    nb = new.read_bytes()
    ob = old.read_bytes() if old.is_file() else None
    if ob is not None and sha(ob) == sha(nb):
        continue
    nc, oc = counts(nb), counts(ob) if ob is not None else None
    want = conv(oc) if oc else conv(nc)
    ol = ob.decode("utf-8").splitlines(True) if ob is not None else []
    nl = nb.decode("utf-8").splitlines(True)
    added = [l for l in difflib.ndiff(ol, nl) if l.startswith("+ ")]
    end = (lambda l: "CRLF" if l.endswith("\r\n") else "LF" if l.endswith("\n") else "NONE")
    added_ok = all(end(l[2:]) in (want, "NONE") for l in added) if want in ("CRLF", "LF") else False
    ok = conv(nc) == want and added_ok
    if not ok:
        bad.append(rel)
    rows.append(dict(path=rel, status="changed" if ob is not None else "added",
                     crlf_before=oc[0] if oc else "", lf_before=oc[1] if oc else "", cr_before=oc[2] if oc else "",
                     crlf_after=nc[0], lf_after=nc[1], cr_after=nc[2], convention_before=conv(oc) if oc else "",
                     convention_after=conv(nc), added_lines=len(added), added_lines_use_convention=added_ok, ok=ok))
    if ob is not None and rel.endswith(".py"):
        mark = lambda l: l.rstrip("\r\n") + (" [CRLF]" if l.endswith("\r\n") else " [LF]" if l.endswith("\n") else " [NONE]")
        diff_lines.append(f"=== {rel} ({conv(oc)} -> {conv(nc)})")
        for l in difflib.unified_diff([mark(x) for x in ol], [mark(x) for x in nl], f"rev-old/{rel}", f"rev-new/{rel}",
                                      lineterm="", n=1):
            diff_lines.append(l)
with open(out_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
out_txt.write_text("\n".join(diff_lines) + "\n", encoding="utf-8", newline="\n")
for r in rows:
    print(r["status"], r["path"], r["convention_before"], "->", r["convention_after"], "added", r["added_lines"], "ok", r["ok"])
print("not ok:", bad)
sys.exit(1 if bad else 0)
