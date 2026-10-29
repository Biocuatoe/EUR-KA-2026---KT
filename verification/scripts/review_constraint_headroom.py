"""Integrity review phase 5 (saved records only): how close do S1/S2 come to any constraint, and could SoH influence one in the CURRENT model?
From the Modelica primary-grid CSVs: peak current / electrical power, minimum terminal voltage V_t = V_oc - V1 - R0*I, battery power capability (V_oc-V1)^2/(4 R0),
and the headroom of the torque request u against +T_lim (traction limit) and -T_lim (friction-brake onset). usage: python review_constraint_headroom.py <root>"""
import json, pathlib, sys
import numpy as np, pandas as pd, yaml
root = pathlib.Path(sys.argv[1]); C = root / "verification/modelica-build/cases_ctl"
P = yaml.safe_load((root / "configs/parameters.yaml").read_text(encoding="utf-8"))
voc, r0n, k0 = P["battery"]["open_circuit_voltage"]["value"], P["battery"]["r0_new"]["value"], P["battery"]["k_r0"]["value"]
out = {}
for prof in ("S1", "S2"):
    for soh in (1.0, 0.9, 0.8, 0.7):
        for kind in ("fixed", "scheduled"):
            n = f"A_{prof}_{kind}_soh{round(soh*100):03d}"
            d = pd.read_csv(C / n / f"{n}_res.csv", usecols=["time", "v", "I", "V1", "P_e", "P_m", "T_lim", "T_ref", "T", "F_fb", "ctrl.u", "ctrl.T_lim_k"])
            r0 = r0n * (1 + k0 * (1 - soh)); vt = voc - d["V1"] - r0 * d["I"]; cap = (voc - d["V1"]) ** 2 / (4 * r0)
            u = d["ctrl.u"]; tl = d["ctrl.T_lim_k"]; pos = d["P_e"] > 0
            out[n] = {"R0_ohm": r0, "peak_I_A": float(d["I"].max()), "min_I_A": float(d["I"].min()), "peak_P_e_W": float(d["P_e"].max()), "peak_P_m_W": float(d["P_m"].max()),
                      "min_terminal_voltage_V": float(vt.min()), "min_terminal_voltage_frac_of_Voc": float(vt.min() / voc), "battery_power_capability_at_that_time_min_W": float(cap.min()),
                      "peak_Pe_over_capability": float((d["P_e"] / cap).max()), "max_u_over_Tlim": float((u / tl).max()), "max_T_over_Tlim": float((d["T"] / d["T_lim"]).max()),
                      "min_u_over_minus_Tlim": float((u / -tl).max()), "F_fb_max_N": float(d["F_fb"].max()), "T_lim_min_Nm": float(d["T_lim"].min()), "u_max_Nm": float(u.max()), "u_min_Nm": float(u.min())}
json.dump(out, open(root / "verification/controller-crosscheck-runs/review_constraint_headroom.json", "w"), indent=1)
for n, o in out.items():
    if "soh070" in n or "soh100" in n and "fixed" in n: print(n, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in o.items() if k in ("peak_I_A", "peak_P_e_W", "min_terminal_voltage_V", "peak_Pe_over_capability", "max_u_over_Tlim", "min_u_over_minus_Tlim", "T_lim_min_Nm", "u_max_Nm", "u_min_Nm", "F_fb_max_N")})
