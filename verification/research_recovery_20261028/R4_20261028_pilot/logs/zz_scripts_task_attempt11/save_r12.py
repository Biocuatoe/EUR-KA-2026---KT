"""Save the attempt-12 review report verbatim (the agent's hand-back text from the session transcript, unmodified) under a
provenance header, in attempt12/review/ and a copy in the pilot's review/. Refuses to overwrite.
Usage: save_r12.py <transcript.jsonl> <line_no> <attempt_dir> <pilot_dir>"""
import hashlib, json, shutil, sys
from pathlib import Path

src, n, att, pilot = sys.argv[1], int(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
name = "R12_attempt12_review_agent_report_20261029.md"
out, cp = att / "review" / name, pilot / "review" / name
for p in (out, cp):
    if p.exists():
        sys.exit(f"refused: {p} exists")
with open(src, encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i == n:
            d = json.loads(line)
            break
body = d["origin"]["handbackReportText"]
assert "**New findings: CRITICAL 0 · MAJOR 0 · MINOR 2 · NOTE 4.**" in body and d["timestamp"] == "2026-10-29T02:46:27.956Z"
header = f"""# Release attempt 12: independent read-only review report (verbatim)

**Provenance.**
- **Who:** a new, separate **AI review agent** ("Plan" agent type, which has no Edit or Write tools), instructed to use Read, Grep and Glob only. It is not the agent that reviewed attempts 5 to 11. **This is not a human independent audit.**
- **Deviation from the brief, disclosed by the agent and checked in its own transcript:**
  - besides 49 Read, 48 Grep and 25 Glob calls, it made one Bash call at 09:33:46 (+0700);
  - that call was `sed -n '34p' <attempt-11 review brief> | fold -w 400`, which prints one line of a file;
  - it wrote and changed nothing.
- **When:** 2026-10-29 (+0700):
  - `review_scope_attempt12.json` was written at 09:11:55, and the agent was launched right after;
  - it stopped on the account's session limit at 09:12:43 (HTTP 429);
  - it was resumed with its own context at about 09:32:22, told only that some of the attempt's outputs might now exist and are claims;
  - it delivered this report at 09:46:27 (transcript timestamp 2026-10-29T02:46:27.956Z), 846.0 s after resumption.
- **Brief:** `review_brief_attempt12_as_sent.md`.
- **State reviewed:**
  - this attempt's `code/` and `config/`: 79 files, SHA-256 in `review_scope_attempt12.json`;
  - amendment 2 candidate rev13, `R4_20261028_pilot/03_protocol_v1_amendment_2_rev13_CANDIDATE.md`, SHA-256 `7f06dd1f1a825c55280fa220b740d617baf4fab1899300a4a31958f345d9759b`.
- **Format:** the text below the line is the agent's final message, copied programmatically from the session transcript ({len(body):,} characters), unmodified.
- **Outcome:**
  - **no CRITICAL or MAJOR finding**; R11-1 (MAJOR) is verified FIXED;
  - two MINOR findings (R12-1, R12-2) and four notes are open and recorded for the owner.

---

"""
out.parent.mkdir(exist_ok=True)
out.write_text(header + body + "\n", encoding="utf-8", newline="\n")
saved = out.read_text(encoding="utf-8").split("\n---\n\n", 1)[1].rstrip("\n")
assert saved == body.rstrip("\n")
shutil.copy2(out, cp)
print(hashlib.sha256(out.read_bytes()).hexdigest(), len(body))
