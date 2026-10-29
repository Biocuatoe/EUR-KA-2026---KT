"""Build the rev12 candidate template (a2_rev12_text.md) from the rev11 template (a2_rev11_text.md, read only). Rev11 was
written and superseded before any test or review: its section 1.1 heading said "first stated in rev3", but the N-A2
ruling section exists since the first amendment-2 draft (rev0). Every replacement must match exactly once."""
from pathlib import Path

D = Path(__file__).resolve().parent
src, dst = D / "a2_rev11_text.md", D / "a2_rev12_text.md"
if dst.exists():
    raise SystemExit(f"refused: {dst} exists")
t = src.read_text(encoding="utf-8")
REV11 = "162b688d2a1665831705bc3a1bc68273f5ede15cc87b0d226837cf4f015998e9"
REPL = [
    ("**Status: CANDIDATE rev11 — DRAFT — NOT APPROVED FOR RELEASE.**", "**Status: CANDIDATE rev12 — DRAFT — NOT APPROVED FOR RELEASE.**"),
    ("Rev11 implements the decisions of 2026-10-29 (§1.15, §1.16).",
     "Rev12 implements the decisions of 2026-10-29 (§1.15, §1.16)."),
    ("That review verified the rev10 fixes of the attempt-9 findings.",
     "That review verified the rev10 fixes of the attempt-9 findings. Rev12 replaces candidate rev11, which was superseded before any test or review because its §1.1 heading named the wrong first draft (§12)."),
    ("| Supersedes (as the text proposed for review) | candidate rev10, `03_protocol_v1_amendment_2_rev10_CANDIDATE.md`, SHA-256 `5479f0e81b981c7977ea5a416762972d2a332d4fdb75beee7ad8379ade399804`, kept unchanged. Earlier drafts, all kept unchanged: rev9",
     f"| Supersedes (as the text proposed for review) | candidate rev11, `03_protocol_v1_amendment_2_rev11_CANDIDATE.md`, SHA-256 `{REV11}`, kept unchanged but never tested or reviewed (superseded in the same task, §12). Before it, candidate rev10, `03_protocol_v1_amendment_2_rev10_CANDIDATE.md`, SHA-256 `5479f0e81b981c7977ea5a416762972d2a332d4fdb75beee7ad8379ade399804`, the text reviewed in release attempt 10. Earlier drafts, all kept unchanged: rev9"),
    ("Rev11 and the rev14 code fix R10-1, R10-3 and R10-4 and address R10-2 (§12) |",
     "Rev12 and the rev14 code fix R10-1, R10-3 and R10-4 and address R10-2 (§12) |"),
    ("recorded in `03_protocol_v1_amendment_2_rev11_CANDIDATE.sha256.txt`.", "recorded in `03_protocol_v1_amendment_2_rev12_CANDIDATE.sha256.txt`."),
    ("### 1.1 N-A2 (owner ruling 2026-10-28; first stated in rev3)", "### 1.1 N-A2 (owner ruling 2026-10-28; first stated in rev0)"),
    ("and `config/code_review_status_v12.json` → `open_owner_decisions` is empty.", "and `config/code_review_status_v13.json` → `open_owner_decisions` is empty."),
    ("| `config/code_review_status_v12.json`: the R10 findings;",
     "| `config/code_review_status_v13.json` (v12, written first, was superseded before use because it named candidate rev11): the R10 findings;"),
    ("`REVIEW_STATUS` → `code_review_status_v12.json` | versioning | — |",
     "`REVIEW_STATUS` → `code_review_status_v13.json` | versioning | — |\n"
     f"| Candidate rev11 (`{REV11[:8]}…`) was written and superseded before any test or review. Its §1.1 heading said \"first stated in rev3\". The section \"The owner's ruling (N-A2)\" is already in the first amendment-2 draft, rev0 (`archive/rev4a_reviewed_20261028_0957/03_protocol_v1_amendment_2_DRAFT.md`, SHA-256 `c3e1ddfce7dca7909bb1cd2a6186f4d5044b5dfe81eeed43df0b9fcf215957d4`), so rev12 says \"first stated in rev0\". §1.2 and §1.3 first appear as owner rulings in rev4, as their headings say. Both rev11 and status v12 are kept unchanged | review R10-3 (checking the new headings) | wording |"),
    ("pending: `config/code_review_status_v12.json` keeps `open_major` 6", "pending: `config/code_review_status_v13.json` keeps `open_major` 6"),
]
for a, b in REPL:
    assert t.count(a) == 1, ("not exactly once", a[:110], t.count(a))
    t = t.replace(a, b)
for bad in ("CANDIDATE rev11 —", "status_v12.json` →", "Rev11 implements", "Rev11 and the rev14",
            "### 1.1 N-A2 (owner ruling 2026-10-28; first stated in rev3)"):
    assert bad not in t, bad
assert t.count("first stated in rev3") == 1                      # only the quotation in section 12
assert t.count("{{BLOCK}}") == 1 and "|\n\n|" not in t
dst.write_text(t, encoding="utf-8", newline="\n")
print("ok", t.count("\n"), "lines")
