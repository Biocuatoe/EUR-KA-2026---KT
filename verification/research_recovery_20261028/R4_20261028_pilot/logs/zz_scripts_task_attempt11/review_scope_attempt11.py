"""Record the scope of the attempt-11 review before it starts: copy the brief as sent into review/, hash every code and
config file of the attempt and the candidate under review. Refuses to overwrite.
Usage: review_scope_attempt11.py <attempt_dir> <pilot_dir> <brief>"""
import hashlib, json, shutil, sys, time
from pathlib import Path

att, pilot, brief = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve()
rv = att / "review"
sent, scope = rv / "review_brief_attempt11_as_sent.md", rv / "review_scope_attempt11.json"
for p in (sent, scope):
    if p.exists():
        sys.exit(f"refused: {p} exists")
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rv.mkdir(exist_ok=True)
shutil.copy2(brief, sent)
cand = pilot / "03_protocol_v1_amendment_2_rev12_CANDIDATE.md"
files = {p.relative_to(att).as_posix(): sha(p) for d in ("code", "config") for p in sorted((att / d).rglob("*"))
         if p.is_file()}
rec = dict(review_started=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
           reviewer="a new, separate AI review agent ('Plan' agent type: no Edit or Write tools), instructed to use Read, "
                    "Grep and Glob only",
           not_a_human_audit=True,
           kind="review of rev14 (owner decisions of 2026-10-29; fixes of R10-1..R10-4 of the attempt-10 review) and candidate rev12",
           brief=sent.relative_to(att).as_posix(), brief_sha256=sha(sent),
           amendment_2_candidate_rev12=dict(path=str(cand), sha256=sha(cand)),
           attempt_code_and_config_sha256=files, n_files=len(files))
assert rec["amendment_2_candidate_rev12"]["sha256"] == "ac376c0b362c2e99a9d3777fa849205844487e0be50a41dd1c5f1b2410b5ae1b"
scope.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
print(rec["review_started"], rec["n_files"], rec["brief_sha256"])
