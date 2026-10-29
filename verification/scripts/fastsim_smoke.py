"""FASTSim 3.1.0 smoke test: bundled BEV x bundled UDDS/HWFET. Writes only under argv[1]."""
import json, pathlib, sys
import numpy as np
import fastsim as fsim

out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
VEH = "2022_Renault_Zoe_ZE50_R135.yaml"
res = {"fastsim_file": fsim.__file__, "vehicle": VEH, "runs": {}}
for cyc_name in ("udds.csv", "hwfet.csv"):
    veh = fsim.Vehicle.from_resource(VEH)
    cyc = fsim.Cycle.from_resource(cyc_name)
    sd = fsim.SimDrive(veh, cyc)
    sd.run()
    df = sd.to_dataframe()
    df.to_csv(out / f"zoe_{cyc_name.replace('.csv','')}_timeseries.csv", index=False)
    g = lambda s: df[s].to_numpy(dtype=float)
    P = "veh.pt_type.BEV."
    dist_km = g("veh.history.dist_meters")[-1] / 1000
    e_chem = g(P + "res.history.energy_out_chemical_joules")[-1]
    e_elec = g(P + "res.history.energy_out_electrical_joules")[-1]
    soc = g(P + "res.history.soc")
    v_ach, v_cyc = g("veh.history.speed_ach_meters_per_second"), g("cyc.speed_meters_per_second")
    parts = sum(g(f"veh.history.energy_{k}_joules")[-1] for k in ("drag", "rr", "accel", "ascent", "whl_inertia"))
    trac = g("veh.history.energy_tractive_joules")[-1]
    res["runs"][cyc_name] = {
        "n_rows": int(len(df)), "n_cols": int(df.shape[1]),
        "cycle_distance_km_(cyc.dist)": float(g("cyc.dist_meters")[-1] / 1000),
        "achieved_distance_km": float(dist_km),
        "battery_chemical_out_Wh": float(e_chem / 3600),
        "battery_chem_Wh_per_km": float(e_chem / 3600 / dist_km),
        "battery_electrical_out_Wh_per_km": float(e_elec / 3600 / dist_km),
        "soc_start": float(soc[0]), "soc_end": float(soc[-1]),
        "max_abs_speed_shortfall_m_s": float(np.max(np.abs(v_ach - v_cyc))),
        "rmse_speed_m_s": float(np.sqrt(np.mean((v_ach - v_cyc) ** 2))),
        "ledger_tractive_J": float(trac), "ledger_sum_of_road_load_terms_J": float(parts),
        "ledger_rel_gap_(tractive-vs-sum)": float(abs(trac - parts) / max(abs(trac), 1.0)),
        "all_finite": bool(np.isfinite(df.select_dtypes("number").to_numpy()).all()),
    }
(out / "fastsim_smoke_results.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
print(json.dumps(res, indent=2))
