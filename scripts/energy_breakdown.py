"""Energy decomposition of the primary runs, from saved raw outputs.

    python scripts/energy_breakdown.py

Splits the chemical energy supplied over each primary run into the model's sinks, to show
which share a controller tracking the same reference could possibly influence.
Writes artifacts/tables/energy_breakdown.csv.
"""

import pandas as pd

from eureka import ROOT_DIR
from eureka.experiment import RAW_DIR
from eureka.metrics import load_batch, run_params
from eureka.plant import IX, LOSS_TERMS


def main() -> None:
    rows = []
    for batch in sorted((RAW_DIR / "primary").iterdir()):
        m, arr = load_batch(batch)
        for j, run in enumerate(m["runs"]):
            p = run_params(m, j)
            d = {k: (arr["y_end"][j, IX[k]] - arr["y0"][j, IX[k]]) / 3600 for k in LOSS_TERMS}
            ke = 0.5 * p.M_eff * (arr["y_end"][j, IX["v"]] ** 2) / 3600
            ec1 = 0.5 * p.C1 * arr["y_end"][j, IX["V1"]] ** 2 / 3600
            supplied = (arr["y_end"][j, IX["E_chem"]] - arr["y0"][j, IX["E_chem"]]) / 3600
            row = {
                "run_id": run["run_id"],
                "supplied_Wh": supplied,
                "kinetic_end_Wh": ke,
                "rc_store_end_Wh": ec1,
                **{f"{k}_Wh": v for k, v in d.items()},
            }
            row.update({f"{k}_share_pct": v / supplied * 100 for k, v in d.items()})
            road = d["E_rr"] + d["E_aero"]
            row["road_load_share_pct"] = road / supplied * 100
            row["battery_resistive_share_pct"] = (d["E_R0"] + d["E_R1"]) / supplied * 100
            rows.append(row)
    df = pd.DataFrame(rows)
    out = ROOT_DIR / "artifacts" / "tables" / "energy_breakdown.csv"
    df.to_csv(out, index=False)
    cols = [
        "run_id",
        "supplied_Wh",
        "road_load_share_pct",
        "E_mi_share_pct",
        "E_gear_share_pct",
        "battery_resistive_share_pct",
        "E_fb_share_pct",
    ]
    print(df[cols].round(3).to_string(index=False))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
