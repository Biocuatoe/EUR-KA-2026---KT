"""Write parameter_registry.csv from configs/parameters.yaml plus the rebuild's battery-window parameters."""

import csv

import yaml

from eureka import REPO_DIR
from rebuild.run import HERE

STATUS = {
    "report_unverified": "value printed in the thesis without primary source; not verified",
    "assumed": "chosen by the project; sensitivity-relevant",
    "standard": "physical constant / definition",
    "literature": "cited primary source",
    "measured": "measured",
}

NEW = [
    ("rebuild.v_min_ratio", 0.78125, "dimensionless", "assumed",
     "thesis LFP cell range 2.5-3.65 V per 3.2 V nominal (L1211-1213), itself unsourced", "", "V_min = 37.5 V at V_oc 48 V"),
    ("rebuild.v_max_ratio", 1.140625, "dimensionless", "assumed", "as above (3.65/3.2)", "", "V_max = 54.75 V"),
    ("rebuild.c_dis", 3.0, "1/h", "assumed", "generic LFP discharge-current limit; no datasheet (owner item OC-1)", "2.0", "BCS, BCN; 2.0 in BCS2"),
    ("rebuild.c_ch", 1.0, "1/h", "assumed", "generic LFP charge-current limit; no datasheet", "0.5", "BCS, BCN; 0.5 in BCS2"),
    ("rebuild.soh_scaled", 1.0, "boolean", "assumed", "BMS policy: limits as C-rate of actual capacity", "0 (BCN)", "tested both ways"),
    ("rebuild.k_r0_sensitivity", 2.0, "dimensionless", "assumed", "high resistance-growth sensitivity case (thesis: 0.5)", "", "BV-k2, BCS-k2"),
]


def main():
    cfg = yaml.safe_load((REPO_DIR / "configs" / "parameters.yaml").read_text(encoding="utf-8"))
    rows = []
    for group, items in cfg.items():
        if not isinstance(items, dict):
            continue
        for name, s in items.items():
            if not isinstance(s, dict) or "value" not in s:
                continue
            u = s.get("uncertainty") or {}
            rows.append({"parameter": f"{group}.{name}", "value": s["value"], "unit": s["unit"],
                         "provenance": s["provenance"], "source": s["source"], "source_location": s["source_location"],
                         "uncertainty_low": u.get("low", ""), "uncertainty_high": u.get("high", ""),
                         "evidence_status": STATUS[s["provenance"]], "used_for": s["used_for"]})
    for p, v, unit, prov, src, alt, used in NEW:
        rows.append({"parameter": p, "value": v, "unit": unit, "provenance": prov, "source": src,
                     "source_location": "verification/scientific_rebuild_20261024/configs/R1.yaml",
                     "uncertainty_low": alt, "uncertainty_high": "", "evidence_status": STATUS[prov], "used_for": used})
    with (HERE / "parameter_registry.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(len(rows), "parameters")


if __name__ == "__main__":
    main()
