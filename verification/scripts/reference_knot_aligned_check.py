"""Test the explanation for the saved reference's discretisation error: knot straddling.
Same midpoint scheme and exponential RC update as the saved reference (reference_scheme_convergence.py), but with the step
chosen per profile segment so that no step ever contains a knot (h_i = duration_i / round(duration_i / h)). If knot straddling
is the cause, this variant should agree with the converged answer far better than the fixed global step at the same h.
Plain math + PyYAML. Writes verification/references/ideal_reference_knot_aligned.json"""
import json, math, pathlib, sys, yaml
root = pathlib.Path(sys.argv[1])
cfg = yaml.safe_load((root / "configs/parameters.yaml").read_text(encoding="utf-8"))
V = {f"{g}.{k}": s["value"] for g, it in cfg.items() if isinstance(it, dict) for k, s in it.items()}
M, Af, Cd, Crr, rw, rho, g = (V[k] for k in ("vehicle.mass","vehicle.frontal_area","vehicle.drag_coefficient","vehicle.rolling_resistance","vehicle.wheel_radius","vehicle.air_density","vehicle.gravity"))
G, eg, Jm, Bm, emi = (V[k] for k in ("drivetrain.gear_ratio","drivetrain.gear_efficiency","drivetrain.motor_inertia","drivetrain.motor_viscous_friction","drivetrain.motor_inverter_efficiency"))
Voc, R0n, R1n, C1 = (V[k] for k in ("battery.open_circuit_voltage","battery.r0_new","battery.r1_new","battery.c1"))
kr0, kr1, veps = V["battery.k_r0"], V["battery.k_r1"], V["simulation.speed_smoothing"]
Meff = M + Jm*G**2/rw**2
prof = yaml.safe_load((root / "configs/cycles/profiles.yaml").read_text(encoding="utf-8"))
def knots(segs):
    t, v = [0.0], [0.0]
    for s in segs:
        if "idle" in s or "cruise" in s: t.append(t[-1] + float(s.get("idle", s.get("cruise")))); v.append(v[-1])
        else: tgt = s["to_kmh"]/3.6; t.append(t[-1] + (tgt - v[-1])/s["accel"]); v.append(tgt)
    return t, v
def aligned(name, soh, h):
    tk, vk = knots(prof[name]["segments"]); r0, r1 = R0n*(1+kr0*(1-soh)), R1n*(1+kr1*(1-soh))
    V1 = E = dist = 0.0
    for i in range(len(tk)-1):
        dur = tk[i+1]-tk[i]; n = max(1, round(dur/h)); hi = dur/n; tc = math.exp(-hi/(r1*C1)); a = (vk[i+1]-vk[i])/dur
        for k in range(n):
            v = vk[i] + a*((k+0.5)*hi)
            F = Meff*a + Crr*M*g*math.tanh(v/veps) + 0.5*rho*Cd*Af*v*v
            ts = F*rw/(G*eg) if F >= 0 else F*rw*eg/G; w = G*v/rw; T = ts + Bm*w; pm = T*w; pe = pm/emi if pm >= 0 else pm*emi
            vo = Voc - V1; i_ = (vo - math.sqrt(vo*vo - 4*r0*pe))/(2*r0); E += Voc*i_*hi; dist += v*hi; V1 = V1*tc + r1*(1-tc)*i_
    return E/3600/(dist/1000)
dop = json.load(open(root / "verification/references/ideal_reference_segmentwise_dop853.json"))
conv = json.load(open(root / "verification/references/ideal_reference_convergence.json"))
out = {}
for name, soh in (("S1", 1.0), ("S1", 0.8), ("S2", 1.0), ("S2", 0.8)):
    key = f"{name}_soh{soh}"; ref = dop[key]["E_Wh_per_km"]; out[key] = {"dop853_converged": ref}
    for h in (1e-3, 2.5e-4):
        e = aligned(name, soh, h); gf = conv[key][f"h={h:g}"]["E_Wh_per_km"]
        out[key][f"h={h:g}"] = {"knot_aligned": e, "rel_err_knot_aligned": abs(e-ref)/ref, "global_step": gf, "rel_err_global_step": abs(gf-ref)/ref}
        print(f"{key:10s} h={h:g}: knot-aligned error {abs(e-ref)/ref:.2e}   global-step (saved scheme) error {abs(gf-ref)/ref:.2e}")
(root / "verification/references/ideal_reference_knot_aligned.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
