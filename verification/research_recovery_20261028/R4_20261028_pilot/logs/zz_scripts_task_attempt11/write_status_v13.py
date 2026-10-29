"""Write config/code_review_status_v13.json from v12 (kept unchanged; superseded before use because it named candidate
rev11, itself superseded before use by rev12). Only the candidate references and the R10-3 entry change. Refuses to
overwrite. Usage: write_status_v13.py <pilot_dir>"""
import json, sys
from pathlib import Path

P = Path(sys.argv[1])
src, dst = P / "config/code_review_status_v12.json", P / "config/code_review_status_v13.json"
if dst.exists():
    sys.exit(f"refused: {dst} exists")
raw = src.read_text(encoding="utf-8")
n = raw.count("candidate rev11") + raw.count("Candidate rev11")
assert n >= 4, n
d = json.loads(raw.replace("candidate rev11", "candidate rev12").replace("Candidate rev11", "Candidate rev12"))
d["supersedes"] = ("config/code_review_status_v12.json (kept unchanged; superseded before any test, gate or review "
                   "because it named candidate rev11, which was superseded the same way)")
m = d["minor_findings"]
assert "first stated in rev3/rev4" in m["R10-3 (NOTE)"]
m["R10-3 (NOTE)"] = ("fixed in candidate rev12: no 'six of its notes'; the headings of sections 1.1 to 1.3 say 'first stated "
                     "in rev0' (N-A2: the section 'The owner's ruling (N-A2)' is in the first amendment-2 draft) and "
                     "'first stated in rev4' (AMB-29(a), AMB-31) instead of 'unchanged from'; the rev10 diagnosis sentence "
                     "is a separate implementation note outside the N-A2 ruling paragraph. Candidate rev11 had 'first "
                     "stated in rev3' and was superseded before use")
assert d["open_major"] == 6 and d["owner_acceptance_of_major_closures"].startswith("not recorded")
dst.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
print(dst, n, "references updated", d["open_major"])
