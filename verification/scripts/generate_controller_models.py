"""Generate the case wrapper models and the profile constants of the Modelica controller cross-check.

Inputs : verification/references/controller_gains.json (frozen gains), configs/cycles/profiles.yaml (segment data).
Outputs: verification/modelica/EurekaController/ControllerProfiles.mo   (P-TUNE, S1, S2 constants in the EurekaPlant.Profiles format)
         verification/modelica/EurekaController/Cases.mo               (one wrapper model per profile x controller x SoH, gains as float64 literals)
         verification/modelica/EurekaController/package.order
         verification/modelica/controller_generated_inputs.json        (hashes of inputs and outputs)
Gains are written with repr() (17 significant digits, exact float64 round trip). Nothing is read from any simulation output.
usage: python generate_controller_models.py <project root>
"""
import hashlib
import json
import pathlib
import sys

import yaml

root = pathlib.Path(sys.argv[1])
pkg = root / "verification/modelica/EurekaController"
sha = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
gains = json.loads((root / "verification/references/controller_gains.json").read_text(encoding="utf-8"))["gains"]
cfile = root / "configs/cycles/profiles.yaml"
prof = yaml.safe_load(cfile.read_text(encoding="utf-8"))
PROFILES = {"PTUNE": "P-TUNE", "S1": "S1", "S2": "S2"}

P = ["within EurekaController;", 'package ControllerProfiles "GENERATED from configs/cycles/profiles.yaml (same encoding as EurekaPlant.Profiles): P-TUNE, S1, S2"']
for mname, yname in PROFILES.items():
    kind, par, tgt = [], [], []
    for sg in prof[yname]["segments"]:
        if "idle" in sg or "cruise" in sg:
            kind.append(1)
            par.append(repr(float(sg.get("idle", sg.get("cruise")))))
            tgt.append("0.0")
        else:
            kind.append(2)
            par.append(repr(float(sg["accel"])))
            tgt.append(f'{float(sg["to_kmh"])!r}/3.6')
    n = len(kind)
    P.append(f"  constant Integer {mname}_n = {n};")
    P.append(f'  constant Integer {mname}_kind[{mname}_n] = {{{", ".join(map(str, kind))}}};')
    P.append(f'  constant Real {mname}_p[{mname}_n] = {{{", ".join(par)}}};')
    P.append(f'  constant Real {mname}_target[{mname}_n] = {{{", ".join(tgt)}}};')
P.append("end ControllerProfiles;")
(pkg / "ControllerProfiles.mo").write_text("\n".join(P) + "\n", encoding="ascii")

CASES = []  # (model name, profile key, kind, soh)
for mname in PROFILES:
    sohs = (1.0, 0.9, 0.8, 0.7) if mname in ("S1", "S2") else (0.8,)
    for soh in sohs:
        for kind in ("fixed", "scheduled"):
            CASES.append((f"{mname}_{kind}_soh{round(soh * 100):03d}", mname, kind, soh))
C = ["within EurekaController;", 'package Cases "GENERATED from verification/references/controller_gains.json: one wrapper model per (profile, controller, SoH)"']
for name, mname, kind, soh in CASES:
    g = gains["fixed_soh1.00" if kind == "fixed" else f"scheduled_soh{soh:.2f}"]["K"]
    C.append(f'  model {name} "{PROFILES[mname]}, {kind} LQR, SoH {soh}"')
    C.append(f"    extends EurekaController.ClosedLoop(SoH = {soh!r}, K_e = {g[0]!r}, K_T = {g[1]!r}, K_z = {g[2]!r},")
    C.append(f"      n = EurekaController.ControllerProfiles.{mname}_n, kind = EurekaController.ControllerProfiles.{mname}_kind,")
    C.append(f"      p = EurekaController.ControllerProfiles.{mname}_p, target = EurekaController.ControllerProfiles.{mname}_target);")
    C.append(f"  end {name};")
C.append("end Cases;")
(pkg / "Cases.mo").write_text("\n".join(C) + "\n", encoding="ascii")
(pkg / "package.order").write_text("ControllerProfiles\nSampledLqr\nClosedLoop\nCases\nTests\n", encoding="ascii")

meta = {"generator": "verification/scripts/generate_controller_models.py",
        "inputs": {"verification/references/controller_gains.json": sha(root / "verification/references/controller_gains.json"),
                   "configs/cycles/profiles.yaml": sha(cfile)},
        "outputs": {f: sha(pkg / f) for f in ("ControllerProfiles.mo", "Cases.mo", "ClosedLoop.mo", "SampledLqr.mo", "package.mo", "package.order", "Tests/ControllerUnit.mo", "Tests/ControllerUnitStepOriginal.mo", "Tests/ControllerStepSemantics.mo")},
        "cases": [c[0] for c in CASES]}
(root / "verification/modelica/controller_generated_inputs.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
print(len(CASES), "case models;", json.dumps(meta["outputs"], indent=1))
