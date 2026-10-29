"""Fetch OpenAlex records (abstract, authors, venue, OA status) for the screening shortlist.

    python -I abstracts.py   -> raw/abstracts.json and printed digest
Abstracts are reconstructed from OpenAlex's inverted index; they are what the label "AB" refers to.
"""

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
UA = {"User-Agent": "EUREKA-2026-literature-review/1.0 (research use)"}
SHORTLIST = """10.3390/app13074553 10.1016/j.jpowsour.2026.239432 10.1038/s41598-024-71711-w 10.1109/ccta60707.2024.10666572
10.1016/j.est.2026.124179 10.1016/j.treng.2025.100302 10.1016/j.treng.2026.100455 10.1109/tits.2020.2977882
10.1109/tvt.2019.2940033 10.3390/wevj7010041 10.3390/en16145303 10.3389/fmech.2026.2005334 10.3390/machines14040416
10.1109/tcst.2009.2027023 10.1016/j.conengprac.2023.105730 10.1016/j.energy.2019.03.176 10.3390/vehicles4010001
10.1149/2.053304jes 10.1149/2.1181714jes 10.1016/j.jpowsour.2017.01.133 10.1016/j.etran.2026.100595 10.1109/access.2025.3624875
10.1016/j.est.2023.106624 10.1038/s41597-024-03831-x 10.1016/j.est.2024.110560 10.1016/j.egyai.2021.100081
10.1016/j.dib.2022.107995 10.1038/s41467-020-15235-7 10.1038/s41597-021-00954-3 10.3390/en14227805 10.3390/en16031394
10.1109/tte.2023.3325403 10.1016/j.jfranklin.2015.06.005 10.1109/cdc56724.2024.10885881 10.1109/vppc55846.2022.10003308
10.3390/sym11121516 10.3390/wevj17100505 10.20944/preprints202601.2381.v1 10.2139/ssrn.7540532 10.33915/etd.13464
10.1109/iecon.2014.7049361 10.1016/j.geits.2022.100030 10.1109/tte.2022.3147214 10.1016/j.energy.2015.11.075
10.1016/j.apenergy.2025.125782 10.1016/j.energy.2019.02.017 10.1109/itec51675.2021.9490149 10.1016/j.nxener.2026.100791
10.1016/j.apenergy.2025.126375 10.1016/j.ifacol.2022.11.264""".split()


def abstract(inv):
    if not inv:
        return ""
    pos = sorted((p, w) for w, ps in inv.items() for p in ps)
    return " ".join(w for _, w in pos)


import sys

out = {}
if "--digest-only" in sys.argv:
    out = json.loads((HERE / "raw" / "abstracts.json").read_text(encoding="utf-8"))
    SHORTLIST = []
for doi in SHORTLIST:
    url = "https://api.openalex.org/works/doi:" + urllib.parse.quote(doi)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
            w = json.loads(r.read().decode("utf-8"))
    except Exception as e:  # noqa: BLE001
        out[doi] = {"error": repr(e)}
        print(doi, "ERROR", e)
        continue
    src = ((w.get("primary_location") or {}).get("source") or {})
    out[doi] = {
        "title": w.get("title"), "year": w.get("publication_year"), "venue": src.get("display_name"),
        "authors": [a["author"]["display_name"] for a in w.get("authorships", [])],
        "type": w.get("type"), "oa": (w.get("open_access") or {}).get("is_oa"),
        "oa_url": (w.get("open_access") or {}).get("oa_url"), "cited_by": w.get("cited_by_count"),
        "biblio": w.get("biblio"), "abstract": abstract(w.get("abstract_inverted_index")),
    }
    time.sleep(0.2)
if SHORTLIST:
    (HERE / "raw" / "abstracts.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
lines = []
for doi, d in out.items():
    if "error" in d:
        lines.append(f"{doi} ERROR {d['error']}")
        continue
    a = d["abstract"] or "(no abstract in OpenAlex)"
    lines.append(f"\n### {doi} | {d['year']} | {', '.join(d['authors'][:4])} | {d['venue']} | OA={d['oa']} {d['oa_url'] or ''}"
                 f"\n{d['title']}\n{a[:1000]}")
(HERE / "raw" / "abstracts_digest.txt").write_text("\n".join(lines), encoding="utf-8")
print(len(out), "records;", sum("error" in d for d in out.values()), "errors;",
      sum(bool(d.get("abstract")) for d in out.values()), "with abstract")
