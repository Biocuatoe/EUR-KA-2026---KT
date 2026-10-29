"""Copy the 2022 Renault Zoe YAML that FASTSim 3.1.0 embeds in its compiled module, and the
ElectricMachine documentation, into R3 for the motor-curve audit (R3_motor_curve_audit.md).

    <verification/python-env python> -I extract_fastsim_source.py

Read-only on the FASTSim install. Writes:
    ../data/fastsim_2022_Renault_Zoe_ZE50_R135.yaml   (verbatim text of the embedded resource)
    ../data/fastsim_source_record.json                (module path, SHA-256, offsets, copies identical?, docs)
"""

import hashlib
import json
import re
import sys
from importlib import metadata
from pathlib import Path

import fastsim as fsim

DATA = Path(__file__).resolve().parent.parent / "data"
NAME = "vehicles/2022_Renault_Zoe_ZE50_R135.yaml"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    pyd = next(Path(fsim.__file__).parent.glob("fastsim*.pyd"))
    b = pyd.read_bytes()
    starts = [m.end() for m in re.finditer(re.escape(NAME.encode()), b)]
    texts = []
    for s in starts:
        if not b[s:s + 3] == b"---":
            continue
        e = s
        # the resource is followed by the next embedded file name or a non-text byte
        while e < len(b) and (b[e] in (9, 10, 13) or 32 <= b[e] < 127):
            e += 1
        t = b[s:e].decode("ascii")
        nxt = re.search(r"(vehicles|cycles|resources)/[\w.\-]+\.(yaml|csv|json)", t[3:])
        texts.append(t[: 3 + nxt.start()] if nxt else t)
    if not texts:
        sys.exit("embedded Zoe resource not found")
    uniq = sorted(set(texts), key=len)
    DATA.mkdir(exist_ok=True)
    out = DATA / "fastsim_2022_Renault_Zoe_ZE50_R135.yaml"
    out.write_text(uniq[0], encoding="utf-8", newline="\n")
    docs = {}
    for cls in ("ElectricMachine", "Vehicle", "BEV", "ReversibleEnergyStorage"):
        obj = getattr(fsim, cls, None)
        if obj is not None:
            docs[cls] = obj.__doc__
            for attr in ("eff_interp_achieved", "eff_interp_at_max_input", "pwr_out_max_watts", "eff_max", "eff_min", "eff_range"):
                a = getattr(obj, attr, None)
                if a is not None and getattr(a, "__doc__", None):
                    docs[f"{cls}.{attr}"] = a.__doc__
    rec = {
        "fastsim_version": metadata.version("fastsim"),
        "module": str(pyd), "module_sha256": hashlib.sha256(b).hexdigest(), "module_bytes": len(b),
        "resource": NAME, "copies_found": len(texts), "distinct_texts": len(uniq),
        "distinct_lengths": [len(t) for t in uniq], "offsets": starts,
        "extracted_file": out.name, "extracted_sha256": hashlib.sha256(uniq[0].encode()).hexdigest(),
        "docs": docs,
    }
    (DATA / "fastsim_source_record.json").write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in rec.items() if k != "docs"}, indent=1))
    for k, v in docs.items():
        print("DOC", k, ":", (v or "")[:600].replace("\n", " | "))


if __name__ == "__main__":
    main()
