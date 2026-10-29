"""FASTSim 3.1.0 e-machine sign convention and regeneration-efficiency rule (post-freeze documentation probe).

    <verification/python-env python> -I probe_fastsim_regen_rule.py

Copied unchanged (below this docstring) from the session temp script that established the rule;
it reads FASTSim only and computes no R3 outcome. Output: ../logs/probe_fastsim_regen_rule.txt"""
import sys, numpy as np, fastsim as fsim
veh = fsim.Vehicle.from_resource("2022_Renault_Zoe_ZE50_R135.yaml"); veh.set_save_interval(1)
sd = fsim.SimDrive(veh, fsim.Cycle.from_resource("udds.csv")); sd.run()
d = sd.to_dict(); em = d["veh"]["pt_type"]["BEV"]["em"]; h = em["history"]
g = em["eff_interp_achieved"]["data"]["grid"][0]["data"]; vv = em["eff_interp_achieved"]["data"]["values"]["data"]
pm, pe, eff, pl = (np.array(h[k]) for k in ("pwr_mech_prop_out_watts","pwr_elec_prop_in_watts","eff","pwr_loss_watts"))
pmr, per = np.array(h["pwr_mech_dyn_brake_watts"]), np.array(h["pwr_elec_dyn_brake_watts"])
print("pm min/max", pm.min(), pm.max(), "pe min/max", pe.min(), pe.max(), "dynbrake min/max", pmr.min(), pmr.max(), per.min(), per.max())
r = pm < -1
print("n neg pm", r.sum())
if r.any():
    c = np.interp(-pm[r]/em["pwr_out_max_watts"], g, vv)
    print("regen max|eff-curve(|Pm|/Pmax)|", np.max(np.abs(eff[r]-c)))
    print("regen max|Pe/Pm - eff|", np.max(np.abs(pe[r]/pm[r]-eff[r])), " max|Pm/Pe - eff|", np.max(np.abs(pm[r]/pe[r]-eff[r])))
    print("regen loss check |pl-(pe-pm)| max", np.max(np.abs(pl[r]-(pe[r]-pm[r]))), " |pl-(pm-pe)|", np.max(np.abs(pl[r]-(pm[r]-pe[r]))))
    print("max regen frac", (-pm[r]).max()/em["pwr_out_max_watts"])
    for a,b,e in list(zip(pm[r],pe[r],eff[r]))[:5]: print(a,b,e)
P = em["pwr_out_max_watts"]
req = np.array(h["pwr_out_req_watts"])
cands = {
 "curve(|pm|/P)": np.interp(np.abs(pm)/P, g, vv),
 "curve(|pe|/P)": np.interp(np.abs(pe)/P, g, vv),
 "curve(|pm_prev|/P)": np.interp(np.abs(np.r_[0, pm[:-1]])/P, g, vv),
 "curve(|req|/P)": np.interp(np.abs(req)/P, g, vv),
 "curve(max(pm,0)/P)": np.interp(np.maximum(pm,0)/P, g, vv),
}
for k, c in cands.items():
    print(k, "regen max abs diff", np.max(np.abs(eff[r]-c[r])), " frac exact", np.mean(np.abs(eff[r]-c[r])<1e-9))
print("distinct regen eff values", np.unique(np.round(eff[r],6))[:20])
