"""Logged literature search (OpenAlex primary, Crossref secondary). Phase 2 of the research-recovery task.

    python -I search.py            # runs every query in QUERIES, appends to raw/ and writes search_hits.csv

Writes only inside this directory: raw/<engine>_<qid>.json (verbatim API responses), search_hits.csv
(one row per hit), search_runs.csv (one row per query: engine, timestamp, total count, HTTP status).
No API key, no e-mail address and no personal data are sent.
"""

from __future__ import annotations

import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
RAW.mkdir(exist_ok=True)
UA = {"User-Agent": "EUREKA-2026-literature-review/1.0 (research use)"}

# (qid, concept group, query). Groups: A core LQR/SoH, B ageing physics, C constraint-aware control,
# D energy-time-degradation trade-offs, E data/parameters, K named lines the task requires, X critical/challenge.
QUERIES = [
    ("A01", "A", '"gain-scheduled LQR" battery aging'),
    ("A02", "A", '"adaptive LQR" electric vehicle battery state of health'),
    ("A03", "A", "LQR state of health scheduling electric vehicle speed control"),
    ("A04", "A", "battery health aware longitudinal control electric vehicle"),
    ("A05", "A", "gain scheduling linear quadratic regulator actuator saturation stability"),
    ("A06", "A", "fixed gain versus gain scheduled controller comparison electric vehicle energy"),
    ("A07", "A", "battery degradation aware cruise control electric vehicle"),
    ("B01", "B", "state of health dependent power capability lithium-ion battery"),
    ("B02", "B", "state of power estimation lithium-ion battery aging"),
    ("B03", "B", "capacity fade and resistance increase LiFePO4 graphite cycle aging"),
    ("B04", "B", "semi-empirical aging model lithium iron phosphate battery"),
    ("B05", "B", "equivalent circuit model parameters aging state of health dependence"),
    ("B06", "B", "regenerative braking charge acceptance battery current limit electric vehicle"),
    ("B07", "B", "motor inverter efficiency map energy optimal torque control electric vehicle"),
    ("C01", "C", "constraint-aware LQR electric vehicle"),
    ("C02", "C", "reference governor electric vehicle battery constraints"),
    ("C03", "C", "supervisory control battery power limit electric vehicle traction"),
    ("C04", "C", "regenerative friction brake blending battery state of charge limit"),
    ("C05", "C", "aging-aware torque allocation electric vehicle"),
    ("C06", "C", "anti-windup gain scheduling input saturation vehicle"),
    ("D01", "D", "battery aging aware eco-driving electric vehicle"),
    ("D02", "D", "optimal speed trajectory electric vehicle energy battery degradation"),
    ("D03", "D", "energy time degradation Pareto optimization electric vehicle driving"),
    ("D04", "D", "drivability battery degradation trade-off electric vehicle"),
    ("D05", "D", "eco-driving low-power small electric vehicle"),
    ("D06", "D", "multi-objective energy efficiency battery lifetime electric vehicle control"),
    ("E01", "E", "open lithium-ion battery aging dataset capacity impedance"),
    ("E02", "E", "LFP cell aging dataset impedance capacity fade public"),
    ("E03", "E", "battery resistance growth with state of health data LiFePO4"),
    ("E04", "E", "battery model parameter identification public dataset drive cycle"),
    ("E05", "E", "low voltage 48 V electric vehicle battery power limit"),
    ("E06", "E", "large format prismatic LiFePO4 cell characterization internal resistance"),
    ("K01", "K", "adaptive model predictive control electric vehicle cruise control battery degradation"),
    ("K02", "K", "battery degradation charge sustenance drivability multi-objective"),
    ("K03", "K", "hierarchical eco-driving urban battery lifetime energy"),
    ("K04", "K", "eco-driving optimal control driver preference constraints"),
    ("K05", "K", "battery aging dataset impedance spectroscopy capacity public"),
    ("X01", "X", "battery aging negligible effect vehicle energy consumption"),
    ("X02", "X", "eco-driving travel time trade-off energy savings overestimated"),
    ("X03", "X", "gain scheduling no improvement over fixed gain robust controller"),
]


def get(url: str) -> tuple[int, dict]:
    req = urllib.request.Request(url, headers=UA)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.status, json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(5 * (attempt + 1))
                continue
            return e.code, {}
        except Exception as e:  # noqa: BLE001
            if attempt < 3:
                time.sleep(3)
                continue
            return -1, {"error": repr(e)}
    return -1, {}


def openalex(q: str) -> tuple[int, dict]:
    sel = "id,doi,title,publication_year,primary_location,authorships,cited_by_count,open_access,type"
    url = ("https://api.openalex.org/works?per-page=10&select=" + sel + "&search=" + urllib.parse.quote(q))
    return get(url)


def crossref(q: str) -> tuple[int, dict]:
    url = ("https://api.crossref.org/works?rows=6&select=DOI,title,container-title,issued,author,type"
           "&query.bibliographic=" + urllib.parse.quote(q.replace('"', "")))
    return get(url)


def main(ids: list[str]) -> None:
    runs_p, hits_p = HERE / "search_runs.csv", HERE / "search_hits.csv"
    new_runs = not runs_p.exists()
    with runs_p.open("a", newline="", encoding="utf-8") as fr, hits_p.open("a", newline="", encoding="utf-8") as fh:
        wr, wh = csv.writer(fr), csv.writer(fh)
        if new_runs:
            wr.writerow(["qid", "group", "engine", "query", "utc", "http_status", "total_count", "returned"])
            wh.writerow(["qid", "engine", "rank", "doi", "year", "title", "venue", "first_author", "cited_by", "oa_url"])
        for qid, grp, q in QUERIES:
            if ids and qid not in ids:
                continue
            for eng, fn in (("openalex", openalex), ("crossref", crossref)):
                st, js = fn(q)
                (RAW / f"{eng}_{qid}.json").write_text(json.dumps(js, ensure_ascii=False), encoding="utf-8")
                if eng == "openalex":
                    items = js.get("results", [])
                    total = js.get("meta", {}).get("count")
                    for i, w in enumerate(items, 1):
                        loc = (w.get("primary_location") or {}).get("source") or {}
                        au = (w.get("authorships") or [{}])[0].get("author", {}).get("display_name", "") if w.get("authorships") else ""
                        wh.writerow([qid, eng, i, (w.get("doi") or "").replace("https://doi.org/", ""), w.get("publication_year"),
                                     w.get("title"), loc.get("display_name", ""), au, w.get("cited_by_count"),
                                     (w.get("open_access") or {}).get("oa_url") or ""])
                else:
                    items = js.get("message", {}).get("items", [])
                    total = js.get("message", {}).get("total-results")
                    for i, w in enumerate(items, 1):
                        au = (w.get("author") or [{}])[0].get("family", "") if w.get("author") else ""
                        yr = ((w.get("issued") or {}).get("date-parts") or [[None]])[0][0]
                        wh.writerow([qid, eng, i, w.get("DOI", ""), yr, " ".join(w.get("title") or []),
                                     " ".join(w.get("container-title") or []), au, "", ""])
                wr.writerow([qid, grp, eng, q, datetime.now(timezone.utc).isoformat(timespec="seconds"), st, total, len(items)])
                time.sleep(1.2 if eng == "crossref" else 0.3)
            print(qid, "done", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
