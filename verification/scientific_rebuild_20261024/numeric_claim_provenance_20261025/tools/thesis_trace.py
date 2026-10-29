"""Trace the headline numbers through the submitted thesis DOCX (read-only).

    python -I tools/thesis_trace.py
        -> outputs/docx_package.json          package parts, metadata, media sizes, SHA-256
        -> outputs/thesis_paragraphs.tsv      every w:p (body, tables, text boxes) with section context
        -> outputs/thesis_occurrences.csv     every paragraph matching a claim-related pattern

The DOCX is opened with zipfile in read mode only; nothing is written next to it.
Paragraph indices are document order of w:p elements, so they are stable for this file hash.
"report_md_line" maps a paragraph to data/processed/report/report.md (pandoc 3.11 export used
by the earlier audits) where an exact text match exists.
"""

import csv
import hashlib
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
ROOT = HERE.parents[2]
DOCX = ROOT / "EURÉKA 2026 - KT.docx"
REPORT_MD = ROOT / "data" / "processed" / "report" / "report.md"
EXPECTED_SHA256 = "01363a069eeb005851f6d62ac4b9da9e3fd13a742bebbfdfc14c802f0eddff8c"
OUT = HERE / "outputs"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# id, regex, what it is looking for
PATTERNS = [
    ("P-12.5", r"12[.,]\s?5\s?%", "headline energy figure"),
    ("P-15.3", r"15[.,]\s?3\s?%", "headline fade figure"),
    ("P-pm2.1", r"±\s?2[.,]1", "energy uncertainty"),
    ("P-pm2.8", r"±\s?2[.,]8", "fade uncertainty"),
    ("P-9.7", r"9[.,]7\s?(%|Wh)", "body energy saving"),
    ("P-14pct", r"\b14\s?%|14[.,]2\s?%|14[.,]0\s?%", "body fade figures"),
    ("P-16.5", r"16[.,]5\s?%", "fixed-LQR fade"),
    ("P-85.3", r"85[.,]3", "adaptive energy Wh/km"),
    ("P-95Wh", r"\b95 Wh", "fixed-LQR energy Wh/km"),
    ("P-1000cyc", r"1,?000 (operational )?cycles|/1000 cyc|per 1000 cycles|1000 cycle", "1000-cycle horizon"),
    ("P-1500cyc", r"1,?500 [Cc]ycles", "1500-cycle horizon"),
    ("P-fixedLQR", r"[Ff]ixed[- ]?(gain )?LQR|LQR-fix", "fixed-LQR baseline mention"),
    ("P-energy-imp", r"energy (efficiency )?improvement|energy savings?", "energy improvement wording"),
    ("P-fade", r"capacity fade|SoH [Ff]ade|fade rate|[Ff]ade reduction", "fade wording"),
    ("P-MC", r"Monte Carlo|\bN ?= ?1000\b|100 trials", "sample count"),
    ("P-stats", r"Cohen|t-test|ANOVA|Bonferroni|p-value|Tukey", "statistics"),
    ("P-seed", r"\bseed\b|random state|rng", "random seed"),
    ("P-code", r"\.py\b|\.m\b|\.slx|Simulink|MATLAB|config\.yaml|source code|repository|GitHub|dataset", "code/data provenance"),
    ("P-tawfik", r"Tawfik|Asfoor|Scientific Reports|71711", "Tawfik 2024"),
    ("P-13pct", r"\b13\s?%|15[.,]8\s?%", "Tawfik figures"),
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def paragraph_text(p):
    parts = []
    for t in p.iter():
        if t.tag == W + "t":
            parts.append(t.text or "")
        elif t.tag in (W + "tab", W + "br"):
            parts.append(" ")
    return "".join(parts)


def main():
    digest = sha256(DOCX)
    if digest != EXPECTED_SHA256:
        raise SystemExit(f"DOCX hash {digest} differs from the audited file {EXPECTED_SHA256}")
    OUT.mkdir(exist_ok=True)
    z = zipfile.ZipFile(DOCX, "r")

    package = {
        "file": str(DOCX),
        "sha256": digest,
        "size_bytes": DOCX.stat().st_size,
        "parts": [{"name": i.filename, "size": i.file_size, "zip_datetime": "%04d-%02d-%02d %02d:%02d:%02d" % i.date_time}
                  for i in z.infolist()],
        "docProps": {n: z.read(n).decode("utf-8") for n in z.namelist() if n.startswith("docProps/")},
    }
    (OUT / "docx_package.json").write_text(json.dumps(package, indent=1, ensure_ascii=False), encoding="utf-8")

    root = ET.fromstring(z.read("word/document.xml"))
    parent = {c: p for p in root.iter() for c in p}
    report_lines = REPORT_MD.read_text(encoding="utf-8").splitlines()
    norm = lambda s: re.sub(r"[\s*_\\]+", " ", s).strip()
    report_norm = [norm(l) for l in report_lines]

    rows, heading = [], {"1": "", "2": "", "3": ""}
    last_caption = ""
    for i, p in enumerate(root.iter(W + "p")):
        text = paragraph_text(p)
        style_el = p.find(f"{W}pPr/{W}pStyle")
        style = style_el.get(W + "val") if style_el is not None else ""
        anc, in_table, in_textbox = p, False, False
        while anc in parent:
            anc = parent[anc]
            in_table |= anc.tag == W + "tbl"
            in_textbox |= anc.tag == W + "txbxContent"
        m = re.match(r"Heading([123])", style)
        if m and text.strip():
            heading[m.group(1)] = text.strip()
            for lower in "123":
                if lower > m.group(1):
                    heading[lower] = ""
        if re.match(r"\s*(Table|Figure) \d+\.", text):
            last_caption = text.strip()
        context = "textbox" if in_textbox else ("table" if in_table else "body")
        rows.append({"para": i, "context": context, "style": style,
                     "chapter": heading["1"], "section": heading["2"], "subsection": heading["3"],
                     "last_caption": last_caption, "text": text})

    with open(OUT / "thesis_paragraphs.tsv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t")
        w.writeheader()
        w.writerows({**r, "text": r["text"].replace("\t", " ")} for r in rows)

    def report_line(text):
        key = norm(text)[:60]
        if len(key) < 12:
            return ""
        hits = [str(n + 1) for n, l in enumerate(report_norm) if key in l]
        return ";".join(hits[:3])

    occ = []
    for r in rows:
        for pid, rx, what in PATTERNS:
            for m in re.finditer(rx, r["text"]):
                s, e = max(0, m.start() - 160), min(len(r["text"]), m.end() + 160)
                occ.append({"pattern": pid, "looking_for": what, "match": m.group(0), "para": r["para"],
                            "context": r["context"], "chapter": r["chapter"], "section": r["section"],
                            "subsection": r["subsection"], "nearest_preceding_caption": r["last_caption"],
                            "report_md_line": report_line(r["text"]), "excerpt": r["text"][s:e].strip()})
    with open(OUT / "thesis_occurrences.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(occ[0]))
        w.writeheader()
        w.writerows(occ)

    counts = {}
    for o in occ:
        counts[o["pattern"]] = counts.get(o["pattern"], 0) + 1
    print(f"DOCX sha256 OK ({digest[:12]}...), {len(rows)} paragraphs, {len(occ)} pattern hits")
    for pid, _, what in PATTERNS:
        print(f"  {pid:12s} {counts.get(pid, 0):4d}  {what}")


if __name__ == "__main__":
    main()
