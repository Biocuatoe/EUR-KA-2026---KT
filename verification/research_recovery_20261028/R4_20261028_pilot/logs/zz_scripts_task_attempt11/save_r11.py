"""Save the attempt-11 review report verbatim (the agent's hand-back text from the session transcript, unmodified) under a
provenance header, in attempt11/review/ and a copy in the pilot's review/. Refuses to overwrite.
Usage: save_r11.py <transcript.jsonl> <line_no> <attempt_dir> <pilot_dir>"""
import hashlib, json, shutil, sys
from pathlib import Path

src, n, att, pilot = sys.argv[1], int(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
name = "R11_attempt11_review_agent_report_20261029.md"
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
assert "**New findings: CRITICAL 0 · MAJOR 1 · MINOR 3 · NOTE 5.**" in body and d["timestamp"] == "2026-10-29T01:05:04.741Z"
header = f"""# Release attempt 11: independent read-only review report (verbatim)

**Provenance.**
- **Who:** a new, separate **AI review agent** ("Plan" agent type, which has no Edit or Write tools), instructed to use Read, Grep and Glob only. It is not the agent that reviewed attempts 5 to 10. **This is not a human independent audit.**
- **When:** 2026-10-29 (+0700):
  - `review_scope_attempt11.json` was written at 07:45:53, and the agent was launched right after;
  - it ran without interruption for 1,112.0 s (the agent's reported duration), so it started about 07:46:32;
  - it delivered this report at 08:05:04 (transcript timestamp 2026-10-29T01:05:04.741Z).
- **Brief:** `review_brief_attempt11_as_sent.md`.
- **State reviewed:**
  - this attempt's `code/` and `config/`: 76 files, SHA-256 in `review_scope_attempt11.json`;
  - amendment 2 candidate rev12, `R4_20261028_pilot/03_protocol_v1_amendment_2_rev12_CANDIDATE.md`, SHA-256 `ac376c0b362c2e99a9d3777fa849205844487e0be50a41dd1c5f1b2410b5ae1b`.
- **Format:** the text below the line is the agent's final message, copied programmatically from the session transcript ({len(body):,} characters), unmodified.
- **Outcome:**
  - **1 MAJOR finding (R11-1, wording of the machine block) is open in this attempt.** As required, it is corrected in a new attempt, `../attempt12_final_owner_decisions/`; this attempt is kept unchanged as reviewed.
  - The rev14 code changes are confirmed correct and narrow.

---

"""
out.parent.mkdir(exist_ok=True)
out.write_text(header + body + "\n", encoding="utf-8", newline="\n")
saved = out.read_text(encoding="utf-8").split("\n---\n\n", 1)[1].rstrip("\n")
assert saved == body.rstrip("\n")
shutil.copy2(out, cp)
print(hashlib.sha256(out.read_bytes()).hexdigest(), len(body))
