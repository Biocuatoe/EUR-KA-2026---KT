"""Print the tail of saved OpenAlex abstracts (chars 1000+) for the DOIs given on the command line."""
import json
import sys
from pathlib import Path

d = json.loads((Path(__file__).resolve().parent / "raw" / "abstracts.json").read_text(encoding="utf-8"))
sys.stdout.reconfigure(encoding="utf-8")
for doi in sys.argv[1:]:
    a = d.get(doi, {}).get("abstract", "")
    print(f"### {doi}\n{a[950:]}\n")
