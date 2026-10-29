"""Spot-check of the inherited transcript findings on the GATE1 snapshot copies (R4 preflight, Phase 0). Read-only.

For each JSONL line, report: line number, record type/role, tool names used, and whether the line contains the
strings of interest (12.5 / 15.3 with a percent sign, the +-2.1 / +-2.8 / +-3.2 terms). Prints short context only.

    python -I spot_check_transcripts.py <snapshot transcripts dir>
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
PATTERNS = {
    "12.5%": re.compile(r"12\.5\s*\\?\\?%"),
    "15.3%": re.compile(r"15\.3\s*\\?\\?%"),
    "pm2.1": re.compile(r"(\\\\pm|±|\$\\\\pm\$)\s*2\.1"),
    "pm2.8": re.compile(r"(\\\\pm|±|\$\\\\pm\$)\s*2\.8"),
    "pm3.2": re.compile(r"(\\\\pm|±|\$\\\\pm\$)\s*3\.2"),
}


def tools(obj, acc):
    if isinstance(obj, dict):
        if obj.get("type") == "tool_use" and "name" in obj:
            acc.append(obj["name"])
        for v in obj.values():
            tools(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            tools(v, acc)
    return acc


def main():
    root = Path(sys.argv[1]) / "d0683093-fc16-4c61-b854-5a6fac9195be" / "subagents"
    for name in ("b1d68760-d763-4213-b7fc-ed17bae0b679.jsonl", "df2405df-7fa9-4f2b-ae89-4b506027b6a0.jsonl"):
        print("==", name)
        for i, line in enumerate((root / name).read_text(encoding="utf-8").splitlines(), 1):
            hits = [k for k, p in PATTERNS.items() if p.search(line)]
            if not hits:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                rec = {}
            role = rec.get("role") or rec.get("type") or (rec.get("message") or {}).get("role")
            print(f"line {i}: role={role} tools={sorted(set(tools(rec, [])))} hits={hits} bytes={len(line)}")


if __name__ == "__main__":
    main()
