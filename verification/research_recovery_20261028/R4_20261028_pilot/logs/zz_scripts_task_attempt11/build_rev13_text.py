"""Build the rev13 candidate template (a2_rev13_text.md) from the rev12 template (a2_rev12_text.md, read only). Whole
lines are replaced by a unique prefix; substrings must match exactly once; section 12 is replaced. Refuses to overwrite."""
from pathlib import Path

D = Path(__file__).resolve().parent
src, dst = D / "a2_rev12_text.md", D / "a2_rev13_text.md"
if dst.exists():
    raise SystemExit(f"refused: {dst} exists")
lines = (D / "a2_rev12_text.md").read_text(encoding="utf-8").split("\n")
REV12, REV11, REV10 = ("ac376c0b362c2e99a9d3777fa849205844487e0be50a41dd1c5f1b2410b5ae1b",
                       "162b688d2a1665831705bc3a1bc68273f5ede15cc87b0d226837cf4f015998e9",
                       "5479f0e81b981c7977ea5a416762972d2a332d4fdb75beee7ad8379ade399804")


def one(prefix):
    idx = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    assert len(idx) == 1, (prefix[:60], idx)
    return idx[0]


def set_line(prefix, new):
    lines[one(prefix)] = new


old10 = lines[one("| Supersedes (as the text proposed for review) |")]
earlier = old10[old10.index("Earlier drafts, all kept unchanged: rev9"):]
set_line("**Status: CANDIDATE rev12", "**Status: CANDIDATE rev13 — DRAFT — NOT APPROVED FOR RELEASE.** This candidate is not issued, frozen or approved, and has no force. Every owner ruling on its content has been made: I-1 to I-6, and the owner's decisions of 2026-10-29 (§1, §9). Issuing and approving it are the owner's separate decisions (§15). Rev13 corrects the findings of the review of release attempt 11: one MAJOR finding (R11-1, the wording of the machine block, not the code), three MINOR findings and five notes (§12). That review confirmed that the code implements the owner's decisions of 2026-10-29 (§1.15, §1.16).")
set_line("| Supersedes (as the text proposed for review) |",
         f"| Supersedes (as the text proposed for review) | candidate rev12, `03_protocol_v1_amendment_2_rev12_CANDIDATE.md`, SHA-256 `{REV12}`, the text reviewed in release attempt 11, kept unchanged. Before it: candidate rev11, `03_protocol_v1_amendment_2_rev11_CANDIDATE.md`, SHA-256 `{REV11}`, kept unchanged but never tested or reviewed (superseded by rev12 in the same task); candidate rev10, `03_protocol_v1_amendment_2_rev10_CANDIDATE.md`, SHA-256 `{REV10}`, the text reviewed in release attempt 10. " + earlier)
set_line("| Review |", "| Review | `review/R5_attempt5_review_agent_report_20261028.md`, `review/V6_attempt6_verification_agent_report_20261028.md`, `review/R7_attempt7_review_agent_report_20261028.md`, `review/R8_attempt8_review_agent_report_20261028.md`, `review/R9_attempt9_review_agent_report_20261028.md`, `review/R10_attempt10_review_agent_report_20261029.md` and `review/R11_attempt11_review_agent_report_20261029.md`: separate AI review agents (read-only; not a human audit). Rev13 and the rev15 code correct the findings of R11 (§12) |")
set_line("- **As applied.**", "- **As applied.** A pair with an exception in one of its runs or their evaluation, whose label would otherwise be `NOT_APPLICABLE_QS_INFEASIBLE`, `NOT_APPLICABLE_PROFILE_UNAVAILABLE`, PASS, REPORTED_ONLY or FAIL (review R8-1), is `NOT_EVALUABLE_CONDITION_ERROR` (AMB-29(d)). After a failure of the separate recomputation or its fold, three rules apply (AMB-31, I-4, §1.12, §1.16):\n  - a `NOT_APPLICABLE_*` pair with an executed run is `NOT_EVALUABLE_CONDITION_ERROR`;\n  - a `NOT_APPLICABLE_*` pair none of whose runs was executed keeps its label;\n  - a PASS, FAIL or REPORTED_ONLY that used energy the separate recomputation did not confirm is `NOT_EVALUABLE_RUN_INVALID`.\n\n  `NOT_EVALUABLE_RUN_MISSING` (AMB-29(b)), `NOT_EVALUABLE_QS_UNDEFINED` (AMB-29(c)) and `NOT_EVALUABLE_RUN_INVALID` (AMB-31) remain applicable under their own rules. After an exception no pair becomes `NOT_APPLICABLE_*` or PASS. Four things are reported separately (review R11-9):\n  - QS applicability: `qs_vs_dyn_applicability`;\n  - execution validity: protocol §8.2, the condition status and `energy_roles.csv` → `arm_8_2_valid`;\n  - recomputation validity: `energy_roles.csv` → `recomputation_confirmed`, and `conditions.csv` → `separate_recomputation`;\n  - the final pair outcome: `qs_vs_dyn_pair_status`.")
i = one("- **Implementer reading (not an owner ruling), for the owner's confirmation.**")
assert lines[i + 1].startswith("  - (a) every recorded stage") and lines[i + 2].startswith("  - (b) after an exception")
lines[i:i + 3] = [
    "- **Implementer reading (not an owner ruling), for the owner's confirmation.** In three parts (review R11-1, R11-3):",
    "  - (a) every recorded stage of a pair counts as \"a run or evaluation\": `run`, `run_report`, `qs_screen` with its per-piece diagnosis (review R9-1), `classify`, `qs_vs_dynamic`, `condition_report` and the condition-level stage. **This part can change an outcome.** An exception in a reporting stage or in the QS-screen diagnosis makes a pair that would otherwise be PASS or `NOT_APPLICABLE_*` `NOT_EVALUABLE_CONDITION_ERROR`, so the M0/M1 criterion becomes INCONCLUSIVE.",
    "  - (b) after an exception at a stage other than one of its runs, a pair already `NOT_EVALUABLE_RUN_MISSING`, `NOT_EVALUABLE_QS_UNDEFINED` or `NOT_EVALUABLE_RUN_INVALID` keeps that label. No outcome effect: it is NOT_EVALUABLE either way.",
    "  - (c) the owner's \"genuinely absent run\" (I-6b, §1.15) is read as the AMB-29(b) case of an arm without a finite dynamic energy: an executed run whose simulator energy is not finite, with no exception. It stays `NOT_EVALUABLE_RUN_MISSING`. No outcome effect."]
set_line("- The missing-run path is unchanged:", "- The missing-run path is unchanged. By implementer reading (c) (§1.14), the owner's \"genuinely absent run\" is the AMB-29(b) case of an arm without a finite dynamic energy (an executed run whose simulator energy is not finite, with no exception), which stays `NOT_EVALUABLE_RUN_MISSING` (§1.4). An arm not executed because its profile is missing stays on the profile path (`NOT_APPLICABLE_PROFILE_UNAVAILABLE`, AMB-29(a), §1.2).")
set_line("1. The rev7 to rev14 changes", "1. The rev7 to rev15 changes pass an independent review, and the owner accepts the closure. The MAJOR findings R5-1, R5-2, R8-1, R8-2, R8-3 and R9-1 are verified fixed by AI-agent reviews. R11-1, found by the review of release attempt 11, is fixed in rev13 and the rev15 code but not yet verified. The owner's acceptance of any of them is not recorded. The review of release attempt 12 and the owner's acceptance are pending: `config/code_review_status_v14.json` keeps `open_major` 7 and a `reviews_pending` item until then, and each blocks. An AI-agent review is not a human audit.")
t = "\n".join(lines)
REPL = [
    ("`21_attempt11_final_owner_decisions_report.md` (the owner's decisions of 2026-10-29, and release attempt 11) |",
     "`21_attempt11_final_owner_decisions_report.md` (the owner's decisions of 2026-10-29, and release attempts 11 and 12; written after the review of release attempt 12, review R11-5) |"),
    ("recorded in `03_protocol_v1_amendment_2_rev12_CANDIDATE.sha256.txt`.", "recorded in `03_protocol_v1_amendment_2_rev13_CANDIDATE.sha256.txt`."),
    ("or change unrelated valid outcomes.\"", "or change unrelated valid outcomes. Do not perform a broad label rewrite. Inspect the affected branch and its tests, then verify all exception paths retain their intended classification and reporting.\""),
    ("(the missing-run path).", "(the missing-run path; implementer reading (c), §1.14)."),
    ("and `config/code_review_status_v13.json` → `open_owner_decisions` is empty.", "and `config/code_review_status_v14.json` → `open_owner_decisions` is empty."),
    ("One implementer reading remains for the owner's confirmation (`implementer_readings_for_owner_confirmation`): which stages count as \"a run or evaluation\", and that an existing NOT_EVALUABLE label stays after an exception at a later stage (§1.14). It changes no outcome.",
     "One implementer reading, in three parts, remains for the owner's confirmation (`implementer_readings_for_owner_confirmation`; §1.14):\n- (a) which stages count as \"a run or evaluation\". This part can change an outcome;\n- (b) that an existing NOT_EVALUABLE label stays after an exception at a later stage;\n- (c) that the owner's \"genuinely absent run\" is the AMB-29(b) case of an executed run without a finite energy.\n\nParts (b) and (c) change no outcome."),
]
for a, b in REPL:
    assert t.count(a) == 1, ("not exactly once", a[:100], t.count(a))
    t = t.replace(a, b)
S12_START, S12_END = "### 12.1 Since rev10 (complete list)", "## 13. Blockers retained"
i, j = t.index(S12_START), t.index(S12_END)
t = t[:i] + (D / "a2_rev13_sec12.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + t[j:]
for bad in ("CANDIDATE rev12 —", "status_v13.json` →", "It changes no branch outcome, which is INCONCLUSIVE either way",
            "a genuinely absent run energy"):
    assert bad not in t, bad
assert t.count("{{BLOCK}}") == 1 and "|\n\n|" not in t
assert "Do not perform a broad label rewrite." in t[t.index("### 1.15 "):t.index("### 1.16 ")]
dst.write_text(t, encoding="utf-8", newline="\n")
print("ok", t.count("\n"), "lines")
