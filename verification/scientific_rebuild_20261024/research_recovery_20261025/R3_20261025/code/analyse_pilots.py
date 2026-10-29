"""Apply the pilot decision rules (protocol v1 sections 5, 7, 8; amendment 1 A1.3-A1.4) to the raw pilot outputs.

    python -I analyse_pilots.py      -> ../outputs/pilot_summary.json, ../outputs/pilot_summary_tables.txt

Reads outputs/pilot_B/<M>/{tune_selected.json, eval_runs.csv, conv_dt0.5ms.csv} and
outputs/pilot_C/<M>/runs.csv. Never edits them.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

R3 = Path(__file__).resolve().parent.parent
OB, OC = R3 / "outputs" / "pilot_B", R3 / "outputs" / "pilot_C"
HELD = ("S2", "UDDS")


def rd(p):
    if not p.exists():
        return None
    with p.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fl(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def tb(x):
    return str(x) == "True"


def dE(a, b):
    return 100 * (fl(a["Wh_per_ref_km"]) - fl(b["Wh_per_ref_km"])) / fl(b["Wh_per_ref_km"])


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    S, T = {"B": {}, "C": {}}, []
    P = T.append
    # ------------------------------------------------------------------ R3-B
    P("# R3-B (F0/S0/F1/S1), per motor branch\n")
    improve_branches = []
    for m in ("M0", "M1", "M2"):
        ev = rd(OB / m / "eval_runs.csv")
        if ev is None:
            S["B"][m] = "missing"
            P(f"## {m}: no outputs\n")
            continue
        sel = json.loads((OB / m / "tune_selected.json").read_text(encoding="utf-8"))
        cv = rd(OB / m / "conv_dt0.5ms.csv") or []
        P(f"## {m}\n\nSelected (cand, n_feasible/24, rule): " + "; ".join(
            f"{b} ({s['cand']}, {s['n_feasible']}/{s['n_evaluated']}, sigma {s['sigma']:.3g}, c {s['c']:.3g}, qT {s['qT']:.3g}, gv {s['gv']:.3g}, gu {s['gu']:.3g}, {s['rule']})"
            for b, s in sel.items()) + "\n")
        P("| Cycle | Cond | E F0 Wh/ref-km | S0−F0 % | S1−F1 % | F1−F0 % | S1−S0 % | interaction pp | RMSE F0/S0/F1/S1 | complete all | valid all | sched. improves? |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
        idx = {(r["cycle"], r["scen"], r["branch"]): r for r in ev}
        res = []
        for cyc in ("S1", "S2", "UDDS"):
            for sc in ("E1", "E2", "E2b", "E3", "E4"):
                g = {b: idx.get((cyc, sc, b)) for b in ("F0", "S0", "F1", "S1")}
                if any(v is None for v in g.values()):
                    continue
                s0f0, s1f1, f1f0, s1s0 = dE(g["S0"], g["F0"]), dE(g["S1"], g["F1"]), dE(g["F1"], g["F0"]), dE(g["S1"], g["S0"])
                comp = all(fl(v["shortfall_pct"]) <= 1.0 for v in g.values())
                val = all(tb(v["valid"]) for v in g.values())
                rr = lambda a, b: fl(g[a]["rmse_ms"]) / fl(g[b]["rmse_ms"])
                imp = [(d, ratio) for d, ratio in ((s0f0, rr("S0", "F0")), (s1f1, rr("S1", "F1")))]
                improves = cyc in HELD and comp and val and any(d <= -1.0 and ratio <= 1.10 for d, ratio in imp)
                res.append(dict(cycle=cyc, cond=sc, S0_F0=s0f0, S1_F1=s1f1, F1_F0=f1f0, S1_S0=s1s0, inter=s1f1 - s0f0,
                                complete=comp, valid=val, improves=improves))
                P(f"| {cyc} | {sc} | {fl(g['F0']['Wh_per_ref_km']):.3f} | {s0f0:+.3f} | {s1f1:+.3f} | {f1f0:+.3f} | {s1s0:+.3f} | {s1f1 - s0f0:+.3f} | "
                  + "/".join(f"{fl(g[b]['rmse_ms']):.3f}" for b in ("F0", "S0", "F1", "S1")) + f" | {comp} | {val} | {improves} |")
        held = [r for r in res if r["cycle"] in HELD]
        hc = [r for r in held if r["complete"] and r["valid"]]
        imp_nonexpl = [r for r in held if r["improves"] and r["cond"] != "E4"]
        if imp_nonexpl:
            improve_branches.append(m)
        conv_note = []
        if cv:
            cidx = {(r["branch"]): r for r in cv}
            base = {r["branch"]: r for r in ev if r["cycle"] == "UDDS" and r["scen"] == "E3"}
            for a, b in (("S0", "F0"), ("S1", "F1"), ("F1", "F0"), ("S1", "S0")):
                d1 = dE(base[a], base[b])
                d2 = dE(cidx[a], cidx[b])
                conv_note.append(dict(pair=f"{a}-{b}", dE_1ms=d1, dE_0p5ms=d2, change_pp=d2 - d1))
        S["B"][m] = dict(max_abs_sched_effect_heldout_pct=max((max(abs(r["S0_F0"]), abs(r["S1_F1"])) for r in hc), default=None),
                         max_abs_layer_effect_heldout_pct=max((max(abs(r["F1_F0"]), abs(r["S1_S0"])) for r in hc), default=None),
                         max_abs_interaction_heldout_pp=max((abs(r["inter"]) for r in hc), default=None),
                         n_heldout_conditions=len(held), n_heldout_complete_valid=len(hc),
                         scheduling_improves_conditions=[f"{r['cycle']} {r['cond']}" for r in held if r["improves"]],
                         conv=conv_note, n_invalid_eval=sum(not tb(r["valid"]) for r in ev))
        P(f"\nConvergence (UDDS E3, dt 1 -> 0.5 ms): " + "; ".join(f"{c['pair']} {c['dE_1ms']:+.4f} -> {c['dE_0p5ms']:+.4f} (Δ {c['change_pp']:+.4f} pp)" for c in conv_note) + "\n")
    S["B"]["scheduling_improves_in_more_than_one_branch"] = len(improve_branches) > 1
    S["B"]["branches_with_improvement"] = improve_branches
    # ------------------------------------------------------------------ R3-C
    P("\n# R3-C (fixed R1 LQR tracks baseline / eco profiles), P1\n")
    for m in ("M0", "M1", "M2"):
        rows = rd(OC / m / "runs.csv")
        if rows is None:
            S["C"][m] = "missing"
            P(f"## {m}: no outputs\n")
            continue
        P(f"## {m}\n\n| Cycle | Limits | Profile | dt ms | status | Wh/ref-km | ΔE vs baseline % | DP S_found % | trip time s | RMSE vs profile | max |e| | shortfall % | valid | QS vs dyn % | recompute rel |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        out = []
        for cyc in HELD:
            for lk in ("L-R1", "L-EVE"):
                rs = [r for r in rows if r["cycle"] == cyc and r["limits"] == lk]
                base = {fl(r.get("dt_s")): r for r in rs if r["profile"] == "baseline" and r["status"] == "ok"}
                for r in rs:
                    if r["status"] != "ok":
                        P(f"| {cyc} | {lk} | {r['profile']} | — | {r['status']} | | | | | | | | | | |")
                        out.append(dict(cycle=cyc, limits=lk, profile=r["profile"], status=r["status"]))
                        continue
                    dt = fl(r["dt_s"])
                    b = base.get(dt)
                    d = dE(r, b) if b is not None and r["profile"] != "baseline" else None
                    base_ok = b is not None and tb(b["valid"]) and tb(b["tracking_ok"]) and tb(b["complete"])
                    run_ok = tb(r["valid"]) and tb(r["tracking_ok"]) and tb(r["complete"])
                    s_dp = fl(r.get("DP_saving_pct"))
                    fals = None
                    if d is not None and s_dp is not None:
                        sim_saving = -d
                        fals = (not run_ok) or (sim_saving * s_dp < 0) or (sim_saving < 0.5 * s_dp)
                    out.append(dict(cycle=cyc, limits=lk, profile=r["profile"], dt=dt, dE_pct=d, dp_saving=s_dp,
                                    base_ok=base_ok, run_ok=run_ok, falsifies_dp=fals, qs_vs_dyn=fl(r["QS_vs_dyn_pct"]),
                                    trip_time=fl(r["trip_time_s"]), rmse=fl(r["rmse_ms"])))
                    P(f"| {cyc} | {lk} | {r['profile']} | {dt*1000:.1f} | {'ok' if run_ok else 'FAILS requirements'} | {fl(r['Wh_per_ref_km']):.3f} | "
                      + (f"{d:+.2f}" if d is not None else "—") + f" | {s_dp if s_dp is not None else '—'} | {fl(r['trip_time_s']):.1f} | {fl(r['rmse_ms']):.3f} | "
                      f"{fl(r['max_abs_err_ms']):.3f} | {fl(r['shortfall_pct']):.3f} | {r['valid']} | {fl(r['QS_vs_dyn_pct']):+.2f} | {fl(r['recompute_rel']):.1e} |")
        conv = []
        for o in out:
            if o.get("dt") == 0.0005 and o.get("dE_pct") is not None:
                o1 = next((x for x in out if x.get("dt") == 0.001 and (x["cycle"], x["limits"], x["profile"]) == (o["cycle"], o["limits"], o["profile"])), None)
                if o1:
                    conv.append(dict(case=f"{o['cycle']} {o['limits']} {o['profile']}", change_pp=o["dE_pct"] - o1["dE_pct"]))
        S["C"][m] = dict(runs=out, conv=conv)
        P("\nConvergence dt 1 -> 0.5 ms (ΔE change): " + "; ".join(f"{c['case']} {c['change_pp']:+.4f} pp" for c in conv) + "\n")
    (R3 / "outputs" / "pilot_summary.json").write_text(json.dumps(S, indent=1, default=str), encoding="utf-8")
    (R3 / "outputs" / "pilot_summary_tables.txt").write_text("\n".join(T), encoding="utf-8")
    print("\n".join(T))
    print(json.dumps({k: v for k, v in S["B"].items()}, indent=1, default=str))


if __name__ == "__main__":
    main()
