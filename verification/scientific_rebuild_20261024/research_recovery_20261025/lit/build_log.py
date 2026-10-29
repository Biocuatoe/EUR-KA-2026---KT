"""Build ../literature_search_log.csv from search_runs.csv, search_hits.csv, the manual searches below and
../related_work_matrix.csv (to count how many hits of each query were retained). Also validates the matrix CSV."""

import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
RR = HERE.parent

with (RR / "related_work_matrix.csv").open(encoding="utf-8") as f:
    matrix = list(csv.DictReader(f))
ncol = len(matrix[0])
assert all(len(r) == ncol and None not in r for r in matrix), "matrix row with wrong column count"
kept = {r["doi"].lower() for r in matrix if r["doi"] and r["doi"] != "none"}

with (HERE / "search_hits.csv").open(encoding="utf-8") as f:
    hits = list(csv.DictReader(f))
with (HERE / "search_runs.csv").open(encoding="utf-8") as f:
    runs = list(csv.DictReader(f))

rows = []
for r in runs:
    h = [x for x in hits if x["qid"] == r["qid"] and x["engine"] == r["engine"]]
    k = sorted({x["doi"].lower() for x in h if x["doi"].lower() in kept})
    rows.append({"search_id": f"{r['qid']}-{r['engine']}", "date_utc": r["utc"], "engine": r["engine"],
                 "concept_group": r["group"], "query": r["query"], "http_status": r["http_status"],
                 "total_results_reported": r["total_count"], "screened": r["returned"],
                 "retained_in_matrix": len(k), "retained_dois": " ".join(k),
                 "raw_file": f"lit/raw/{r['engine']}_{r['qid']}.json"})

MANUAL = [
    ("W1", "web search (extended)", "A", '"state of health" LQR speed tracking electric vehicle gain scheduling battery aging compensation',
     "no paper combining LQR speed tracking + SoH gain scheduling; returned Jia2022 and SoH-estimation papers", "Jia2022"),
    ("W2", "web search", "C", "state of power battery limit aware longitudinal speed control electric vehicle LQR anti-windup reference governor",
     "closest: Samada2023 MPC reference governor with LQR inner loop (racing, SoC); arXiv 2601.19340 eco-driving with SoC-dependent current limits (not screened further)", "Samada2023"),
    ("W3", "web search", "E", "LiFePO4 100Ah prismatic cell datasheet maximum continuous charge current discharge current pulse 3.2V",
     "retailer listings only (EVE LF100MA/LA: 1C continuous, 2C 30 s pulse); no manufacturer datasheet", "EVE_LF100_listing"),
    ("W4", "web search", "B", 'Butcher 2026 "battery degradation effects on optimized torque splitting" ...', "thesis not found by web search; found via OpenAlex (C05)", ""),
    ("W5", "web search", "E", "EVE Energy LF100LA product specification pdf official maximum continuous charge current 1C pulse 2C",
     "official EVE specification hosted by NKON located; contents not visible in search", "EVE_LF100_listing"),
    ("F1", "fetch (WebFetch)", "B", "https://researchrepository.wvu.edu/cgi/viewcontent.cgi?article=14185&context=etd", "HTTP 403: Butcher2026 full text not read", ""),
    ("F2", "fetch (WebFetch)", "E", "https://www.nkon.nl/es/amfile/file/download/file/346/product/5702", "HTTP 403: EVE LF100LA specification not read", ""),
    ("F3", "fetch (PowerShell Invoke-WebRequest)", "E", "same NKON URL", "HTTP 403; empty download folder removed", ""),
    ("P0", "prior session 2026-10-24 (docs/literature_review_soh_scheduled_lqr.md §1.1)", "A-E",
     "10 query themes (gain-scheduled LQR EV energy; SoH-aware EMS/cruise; SoP; LFP resistance; eco-driving; derating; reproducibility)",
     "~55 Crossref-verified sources; reused here with their access labels", "Pan2023 Jia2022 Zhang2022 Shao2019 Wang2024 Hattori2020 Anselma2021 Mahdy2026 Etxandi2024 Severson2019 Naumann2020 Plett2004"),
]
for sid, eng, grp, q, note, ids in MANUAL:
    rows.append({"search_id": sid, "date_utc": "2026-10-25" if sid != "P0" else "2026-10-24", "engine": eng, "concept_group": grp,
                 "query": q, "http_status": "", "total_results_reported": "", "screened": "", "retained_in_matrix": len(ids.split()),
                 "retained_dois": ids, "raw_file": "", "notes": note})

keys = []
for r in rows:
    keys += [k for k in r if k not in keys]
with (RR / "literature_search_log.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=keys)
    w.writeheader()
    w.writerows(rows)
print("matrix rows:", len(matrix), "| log rows:", len(rows), "| API queries:", len(runs),
      "| unique API hits:", len({x['doi'].lower() for x in hits if x['doi']}),
      "| matrix DOIs found by API:", len(kept & {x['doi'].lower() for x in hits}))
