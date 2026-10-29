"""How FASTSim 3.1.0 applies the e-machine curve (motoring vs regeneration, input vs output fraction).

    <verification/python-env python> -I probe_fastsim_regen.py   -> ../data/fastsim_em_probe.json

Simulates the bundled 2022 Renault Zoe on FASTSim's bundled UDDS (local, nothing downloaded) and
compares the recorded e-machine efficiency with the curve evaluated at |P_mech_out| / P_max.
Used only to interpret the source curve (R3_motor_curve_audit.md); no R3 outcome is computed.
"""

import json
import sys
from pathlib import Path

import numpy as np
import fastsim as fsim

OUT = Path(__file__).resolve().parent.parent / "data" / "fastsim_em_probe.json"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    veh = fsim.Vehicle.from_resource("2022_Renault_Zoe_ZE50_R135.yaml")
    veh.set_save_interval(1)
    cyc = fsim.Cycle.from_resource("udds.csv")
    sd = fsim.SimDrive(veh, cyc)
    sd.walk()
    d = sd.to_dict()
    em = d["veh"]["pt_type"]["BEV"]["em"]
    hist = em["history"]
    keys = sorted(hist.keys())
    pmax = em["pwr_out_max_watts"]
    grid = em["eff_interp_achieved"]["data"]["grid"][0]["data"]
    vals = em["eff_interp_achieved"]["data"]["values"]["data"]
    pm = np.array(hist["pwr_mech_prop_out_watts"])
    pe = np.array(hist["pwr_elec_prop_in_watts"])
    pmr = np.array(hist["pwr_mech_dyn_brake_watts"])
    per = np.array(hist["pwr_elec_dyn_brake_watts"])
    eff = np.array(hist["eff"])
    pl = np.array(hist["pwr_loss_watts"])
    fwd = pm > 1.0
    reg = pmr < -1.0          # FASTSim stores dynamic-brake power as negative
    curve_fwd = np.interp(pm[fwd] / pmax, grid, vals)
    curve_reg = np.interp(-pmr[reg] / pmax, grid, vals)
    rec = {
        "history_keys": keys,
        "n_steps": int(len(pm)), "n_motoring": int(fwd.sum()), "n_regen": int(reg.sum()),
        "motoring_max_abs(eff - curve(Pmech/Pmax))": float(np.max(np.abs(eff[fwd] - curve_fwd))) if fwd.any() else None,
        "motoring_max_abs(Pmech/Pelec - eff)": float(np.max(np.abs(pm[fwd] / pe[fwd] - eff[fwd]))) if fwd.any() else None,
        "regen_max_abs(eff - curve(Pmech_brake/Pmax))": float(np.max(np.abs(eff[reg] - curve_reg))) if reg.any() else None,
        "regen_max_abs(Pelec_brake/Pmech_brake - eff)": float(np.max(np.abs(per[reg] / pmr[reg] - eff[reg]))) if reg.any() else None,
        "regen_max_abs(loss - (Pmech_brake - Pelec_brake))": float(np.max(np.abs(pl[reg] - (pmr[reg] - per[reg])))) if reg.any() else None,
        "max_Pmech_frac": float(np.max(pm) / pmax), "max_Pbrake_frac": float(np.max(-pmr) / pmax),
        "sample_regen_rows": [[float(a), float(b), float(c)] for a, b, c in zip(pmr[reg][:8], per[reg][:8], eff[reg][:8])],
    }
    OUT.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print(json.dumps(rec, indent=1))


if __name__ == "__main__":
    main()
