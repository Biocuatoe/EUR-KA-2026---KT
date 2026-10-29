"""Build the rev11 candidate template (a2_rev11_text.md) from the rev10 template (a2_rev10_text.md, read only): targeted
replacements, each of which must match exactly once, plus the new sections 1.15 and 1.16 (the owner's decisions of
2026-10-29, verbatim) and the new section 12. Refuses if the output exists."""
from pathlib import Path

D = Path(__file__).resolve().parent
src, dst = D / "a2_rev10_text.md", D / "a2_rev11_text.md"
if dst.exists():
    raise SystemExit(f"refused: {dst} exists")
t = src.read_text(encoding="utf-8")
assert "CANDIDATE rev10" in t

I6B_WORDS = ("The specific unresolved case is a QS-eligible pair whose run was attempted but raised an exception. For that "
             "case, the pair-level status must be: `NOT_EVALUABLE_CONDITION_ERROR`. It must not be labelled "
             "`NOT_EVALUABLE_RUN_MISSING`, because the run was attempted and an exception occurred. Keep the semantic "
             "distinction explicit: A genuinely absent run follows the existing missing-run path. An attempted run that "
             "raises follows the condition-error path. Either case remains NOT_EVALUABLE / INCONCLUSIVE as applicable. "
             "Neither may count as PASS. An exception must override a prior PASS when the standing I-6 rules require it. "
             "Do not retry silently, replace the original evidence, or change unrelated valid outcomes.")
SCOPE_WORDS = ("Apply this owner decision to a failure of the separate recomputation or its fold: Only a pair currently "
               "classified as `NOT_APPLICABLE_*` with an actually executed run is eligible for the I-6 relabelling described "
               "here. Such a pair must not retain N/A when the relevant execution/evaluation exception requires a "
               "NOT_EVALUABLE classification. Preserve the existing handling of a genuinely missing run; do not conflate it "
               "with an executed run. Preserve the applicable `RUN_INVALID` and NOT_EVALUABLE classifications when required "
               "by the existing rules. Do not silently convert either to N/A or PASS. Both separate recomputations must "
               "confirm a run before its energy is usable for the QS check. Do not invent replacement energy values, use "
               "invalid energy as confirmatory evidence, or change unrelated statuses.")
NEW_SECS = f"""### 1.15 I-6b: an attempted run that raised (owner decision 2026-10-29)
Owner's words: "{I6B_WORDS}"
- A QS-eligible pair one of whose runs was attempted and raised (stage `run`) is `NOT_EVALUABLE_CONDITION_ERROR`, never `NOT_EVALUABLE_RUN_MISSING`. The pair evaluation's earlier label (`NOT_EVALUABLE_RUN_MISSING`, or a FAIL of the other, valid arm) is kept in `qs_vs_dyn_pair_status_before_error`, and a measured failure in `qs_vs_dyn_fail_arms` (§1.14).
- The missing-run path is unchanged: an eligible pair whose arm was executed but has no finite simulator energy, with no exception, is `NOT_EVALUABLE_RUN_MISSING` (AMB-29(b), §1.4). An arm not executed because its profile is missing stays on the profile path (`NOT_APPLICABLE_PROFILE_UNAVAILABLE`, AMB-29(a), §1.2).
- Both labels are NOT_EVALUABLE, so the M0/M1 criterion is INCONCLUSIVE; neither counts as PASS. The run is not retried, and its error, trace and run ID are kept (§1.6).
- This replaces the implementer reading of rev9 and rev10, which kept `NOT_EVALUABLE_RUN_MISSING` for this case. The decision answers the optional sub-question of `18_owner_decision_matrix_I1_I6.md` §3.5 in line with that matrix's I-6b column (headed "always `NOT_EVALUABLE_CONDITION_ERROR`").

### 1.16 I-6: scope after a failure of the separate recomputation or its fold (owner decision 2026-10-29)
Owner's words: "{SCOPE_WORDS}"
- After a failure of the separate recomputation (an exit other than 0 or 1, a launch failure, a missing or unreadable output) or of its fold, a `NOT_APPLICABLE_*` pair with an actually executed run becomes `NOT_EVALUABLE_CONDITION_ERROR` (its N/A label kept in `qs_vs_dyn_pair_status_before_error`). A `NOT_APPLICABLE_*` pair none of whose runs was executed keeps its label (`_na_pair_not_evaluable`, called from `fold_separate_recomputation` and `fold_failed`).
- A PASS, FAIL or REPORTED_ONLY that used energy the separate recomputation did not confirm becomes `NOT_EVALUABLE_RUN_INVALID` (AMB-31, I-4, §1.12), with its earlier label in `qs_vs_dyn_pair_status_before_error`. `NOT_EVALUABLE_RUN_MISSING`, `NOT_EVALUABLE_QS_UNDEFINED`, `NOT_EVALUABLE_RUN_INVALID` and `NOT_EVALUABLE_CONDITION_ERROR` stay. No label becomes `NOT_APPLICABLE_*` or PASS.
- Both recomputations must confirm a run before the QS check uses its energy: the in-process one (`run_condition`) and the separate one (the fold) (I-4, §1.12). No energy value is replaced or invented.
- Implementation: the executor passes the run IDs it executed. A direct call of the folds without them treats every N/A pair as executed, which fails closed; the executor never makes such a call.

"""

REPL = [
    # header (R10-3: no "six of its notes")
    ("**Status: CANDIDATE rev10 — DRAFT — NOT APPROVED FOR RELEASE.** This candidate is not issued, frozen or approved, and has no force. Every owner ruling on its content has been made, I-1 to I-6 included (§1, §9). Issuing and approving it are the owner's separate decisions (§15). Rev10 fixes the findings of the review of release attempt 9: one MAJOR (R9-1), two MINOR and six of its notes (§12). The review of release attempt 9 verified the rev9 fixes of the attempt-8 findings.",
     "**Status: CANDIDATE rev11 — DRAFT — NOT APPROVED FOR RELEASE.** This candidate is not issued, frozen or approved, and has no force. Every owner ruling on its content has been made: I-1 to I-6, and the owner's decisions of 2026-10-29 (§1, §9). Issuing and approving it are the owner's separate decisions (§15). Rev11 implements the decisions of 2026-10-29 (§1.15, §1.16). It also fixes, from the review of release attempt 10 (one MINOR finding and three notes): the MINOR finding R10-1 and the notes R10-3 and R10-4, and it addresses the note R10-2 with tests (§12). That review verified the rev10 fixes of the attempt-9 findings."),
    ("| Basis | the owner's rulings of 2026-10-28: N-A2; AMB-29(a) and AMB-31; AMB-29(b), AMB-29(c), AMB-29(d), AMB-30 and AMB-32; I-1; I-2 to I-6 |",
     "| Basis | the owner's rulings of 2026-10-28: N-A2; AMB-29(a) and AMB-31; AMB-29(b), AMB-29(c), AMB-29(d), AMB-30 and AMB-32; I-1; I-2 to I-6. The owner's decisions of 2026-10-29: I-6b, and the scope of the I-6 relabelling after a failure of the separate recomputation or its fold |"),
    ("| Supersedes (as the text proposed for review) | candidate rev9, `03_protocol_v1_amendment_2_rev9_CANDIDATE.md`, SHA-256 `cdeea032c520f408f1f300a53cf1bc8b1ec4582d80340d3df2c2c94fa5d45719`, kept unchanged. Earlier drafts, all kept unchanged: rev8",
     "| Supersedes (as the text proposed for review) | candidate rev10, `03_protocol_v1_amendment_2_rev10_CANDIDATE.md`, SHA-256 `5479f0e81b981c7977ea5a416762972d2a332d4fdb75beee7ad8379ade399804`, kept unchanged. Earlier drafts, all kept unchanged: rev9 `cdeea032c520f408f1f300a53cf1bc8b1ec4582d80340d3df2c2c94fa5d45719`; rev8"),
    ("`20_attempt8_final_owner_decisions_report.md` (the owner's rulings on I-2 to I-6, and release attempts 8 to 10) |",
     "`20_attempt8_final_owner_decisions_report.md` (the owner's rulings on I-2 to I-6, and release attempts 8 to 10); `21_attempt11_final_owner_decisions_report.md` (the owner's decisions of 2026-10-29, and release attempt 11) |"),
    ("`review/R8_attempt8_review_agent_report_20261028.md` and `review/R9_attempt9_review_agent_report_20261028.md`: separate AI review agents (read-only; not a human audit). Rev10 and the rev13 code fix the findings of R9 (§12) |",
     "`review/R8_attempt8_review_agent_report_20261028.md`, `review/R9_attempt9_review_agent_report_20261028.md` and `review/R10_attempt10_review_agent_report_20261029.md`: separate AI review agents (read-only; not a human audit). Rev11 and the rev14 code fix R10-1, R10-3 and R10-4 and address R10-2 (§12) |"),
    ("recorded in `03_protocol_v1_amendment_2_rev10_CANDIDATE.sha256.txt`.", "recorded in `03_protocol_v1_amendment_2_rev11_CANDIDATE.sha256.txt`."),
    # 1.1 to 1.3 headings and the rev10 sentence (R10-3)
    ("### 1.1 N-A2 (unchanged from rev3)", "### 1.1 N-A2 (owner ruling 2026-10-28; first stated in rev3)"),
    (" The profile, plant, LQR gain, limits and task are never modified. If the diagnosis of a failing piece raises, the piece says so, the exception goes to `errors.csv`, and the pair is `NOT_EVALUABLE_CONDITION_ERROR` (§1.6, §1.14; review R9-1).\n",
     " The profile, plant, LQR gain, limits and task are never modified.\n\nImplementation note (added in rev10, review R9-1; not part of the ruling): if the diagnosis of a failing piece raises, the piece says so, the exception goes to `errors.csv`, and the pair is `NOT_EVALUABLE_CONDITION_ERROR` (§1.6, §1.14).\n"),
    ("### 1.2 AMB-29(a): missing profile (unchanged from rev4)", "### 1.2 AMB-29(a): missing profile (owner ruling 2026-10-28; first stated in rev4)"),
    ("### 1.3 AMB-31: energy from a run failing §8.2 (unchanged from rev4, made precise in §4)",
     "### 1.3 AMB-31: energy from a run failing §8.2 (owner ruling 2026-10-28; first stated in rev4, made precise in §4)"),
    # 1.4
    ("- A QS-eligible pair with an arm without a finite dynamic energy is `NOT_EVALUABLE_RUN_MISSING`;",
     "- A QS-eligible pair with an arm that was executed but has no finite dynamic energy, with no exception, is `NOT_EVALUABLE_RUN_MISSING` (an attempted run that raised is `NOT_EVALUABLE_CONDITION_ERROR`, owner decision I-6b, §1.15);"),
    # 1.6
    ("For a QS-eligible pair it makes the pair `NOT_EVALUABLE_RUN_MISSING` (AMB-29(b)), also when the other, valid arm FAILs; that measured FAIL is kept (§1.14).",
     "For a QS-eligible pair it makes the pair `NOT_EVALUABLE_CONDITION_ERROR` (owner decision I-6b, §1.15), also when the other, valid arm FAILs; that measured FAIL is kept (§1.14)."),
    # 1.12
    ("A `NOT_APPLICABLE_*` pair with an executed run then becomes `NOT_EVALUABLE_CONDITION_ERROR` (I-6, §1.14; reviews R8-9, R9-6); a pair none of whose runs was executed keeps its label, because no run of it was evaluated (an implementer reading, §9).",
     "A `NOT_APPLICABLE_*` pair with an actually executed run then becomes `NOT_EVALUABLE_CONDITION_ERROR`; a pair none of whose runs was executed keeps its label (owner decision of 2026-10-29, §1.16; reviews R8-9, R9-6)."),
    # 1.14 (R10-1)
    ("- **Precedence.** An exception recorded for a pair's runs or their evaluation makes the pair NOT_EVALUABLE, whatever its label would otherwise be: `NOT_APPLICABLE_QS_INFEASIBLE`, `NOT_APPLICABLE_PROFILE_UNAVAILABLE`, PASS, REPORTED_ONLY or FAIL (review R8-1). This holds at every stage of the pair (`run`, `run_report`, `qs_screen` with its per-piece diagnosis (review R9-1), `classify`, `qs_vs_dynamic`, `condition_report`) and, for a pair with an executed run, after a failure of the separate recomputation or its fold (§1.12):\n  - a QS-eligible pair one of whose runs raised (stage `run`) has an arm without dynamic energy: `NOT_EVALUABLE_RUN_MISSING`, the AMB-29(b) label, whose operative wording since draft rev3 includes \"an exception\";\n  - after a failure of the separate recomputation or its fold, a result that used unconfirmed energy is `NOT_EVALUABLE_RUN_INVALID` (I-4, §1.12);\n  - any other pair is `NOT_EVALUABLE_CONDITION_ERROR` (AMB-29(d));\n  - a `NOT_EVALUABLE_*` label stays.\n- **Label reading, for the owner's confirmation.** The ruling requires the NOT_EVALUABLE class. Which label an eligible pair whose run raised gets (`NOT_EVALUABLE_RUN_MISSING` or `NOT_EVALUABLE_CONDITION_ERROR`) was an optional sub-question of `18_owner_decision_matrix_I1_I6.md` §3.5 that the ruling does not answer. That matrix's I-6b column, headed \"always `NOT_EVALUABLE_CONDITION_ERROR`\", listed `NOT_EVALUABLE_CONDITION_ERROR` for this case (review R9-5). This candidate keeps `NOT_EVALUABLE_RUN_MISSING`, following the standing AMB-29(b) ruling. Both labels lead to the same outcome. The owner may confirm or change the label when issuing; it is not an open decision (§9).",
     "- **Owner rulings and decisions.** I-6 (above) requires the NOT_EVALUABLE class and keeps the exception, stage, run ID and process log. The owner decided the optional sub-question of `18_owner_decision_matrix_I1_I6.md` §3.5 on 2026-10-29 in line with that matrix's I-6b column, headed \"always `NOT_EVALUABLE_CONDITION_ERROR`\": an attempted run that raised gives `NOT_EVALUABLE_CONDITION_ERROR` (§1.15). The owner also decided the scope after a failure of the separate recomputation or its fold (§1.16).\n- **As applied.** A pair with an exception whose label would otherwise be `NOT_APPLICABLE_QS_INFEASIBLE`, `NOT_APPLICABLE_PROFILE_UNAVAILABLE`, PASS, REPORTED_ONLY or FAIL (review R8-1) is `NOT_EVALUABLE_CONDITION_ERROR` (AMB-29(d)). There is one exception: after a failure of the separate recomputation or its fold, a PASS, FAIL or REPORTED_ONLY that used energy the separate recomputation did not confirm is `NOT_EVALUABLE_RUN_INVALID` (AMB-31, I-4, §1.12). `NOT_EVALUABLE_RUN_MISSING` (AMB-29(b)), `NOT_EVALUABLE_QS_UNDEFINED` (AMB-29(c)) and `NOT_EVALUABLE_RUN_INVALID` (AMB-31) remain applicable under their own rules. After an exception no pair becomes `NOT_APPLICABLE_*` or PASS.\n- **Implementer reading (not an owner ruling), for the owner's confirmation.** It changes no branch outcome, which is INCONCLUSIVE either way:\n  - (a) every recorded stage of a pair counts as \"a run or evaluation\": `run`, `run_report`, `qs_screen` with its per-piece diagnosis (review R9-1), `classify`, `qs_vs_dynamic`, `condition_report` and the condition-level stage;\n  - (b) after an exception at a stage other than one of its runs, a pair already `NOT_EVALUABLE_RUN_MISSING`, `NOT_EVALUABLE_QS_UNDEFINED` or `NOT_EVALUABLE_RUN_INVALID` keeps that label."),
    ("- **A measured failure is never hidden.** The label the pair would otherwise have is kept in `qs_vs_dyn_pair_status_before_error`,",
     "- **A measured failure is never hidden.** The label before the exception rule is kept in `qs_vs_dyn_pair_status_before_error`,"),
    ("- **Records.** The exception, its stage, the run ID or IDs and, for the separate recomputation, the process log are kept (§7). Nothing is retried or replaced.\n",
     "- **Records.** The exception, its stage, the run ID or IDs and, for the separate recomputation, the process log are kept (§7). Nothing is retried or replaced.\n\n" + NEW_SECS.rstrip("\n") + "\n"),
    # 2
    ("| NOT_EVALUABLE | `NOT_EVALUABLE_RUN_MISSING` | eligible; an arm has no finite simulator energy (the run raised, or its simulator energy is not finite). A run that raised gives this label whatever the other arm shows, a FAIL included (I-6) | INCONCLUSIVE (AMB-29(b)) |",
     "| NOT_EVALUABLE | `NOT_EVALUABLE_RUN_MISSING` | eligible; an arm was executed but its simulator energy is not finite, with no exception (the missing-run path). An attempted run that raised is `NOT_EVALUABLE_CONDITION_ERROR` (owner decision I-6b, §1.15) | INCONCLUSIVE (AMB-29(b)) |"),
    ("or an exception in a run or its evaluation of a pair that is not QS-eligible, whose label would otherwise be `NOT_APPLICABLE_*`, or whose result would otherwise be PASS, REPORTED_ONLY or FAIL (I-6); or a `NOT_APPLICABLE_*` pair with an executed run after a failure of the separate recomputation or its fold.",
     "or an exception in a run or its evaluation of a pair whose label would otherwise be `NOT_APPLICABLE_*`, PASS, REPORTED_ONLY or FAIL (I-6); or a QS-eligible pair one of whose runs was attempted and raised (owner decision I-6b, §1.15); or a `NOT_APPLICABLE_*` pair with an actually executed run after a failure of the separate recomputation or its fold (owner decision of 2026-10-29, §1.16)."),
    # 3
    ("| QS-eligible pair; one run raised and the other, valid arm FAILs | `NOT_EVALUABLE_RUN_MISSING` (AMB-29(b), I-6); the FAIL is kept in `qs_vs_dyn_pair_status_before_error` and `qs_vs_dyn_fail_arms` |",
     "| QS-eligible pair; one attempted run raised (the other arm valid, a FAIL included) | `NOT_EVALUABLE_CONDITION_ERROR` (owner decision I-6b, §1.15); the earlier label (`NOT_EVALUABLE_RUN_MISSING`, or the FAIL) is kept in `qs_vs_dyn_pair_status_before_error`, a FAIL also in `qs_vs_dyn_fail_arms` |"),
    ("| `NOT_EVALUABLE_CONDITION_ERROR` (I-6) if the pair has an executed run; otherwise its N/A label (§1.12) |",
     "| `NOT_EVALUABLE_CONDITION_ERROR` (I-6) if the pair has an actually executed run; otherwise its N/A label (owner decision of 2026-10-29, §1.16) |"),
    # 7.8
    ("After a process failure or a fold exception, a `NOT_APPLICABLE_*` pair with an executed run becomes `NOT_EVALUABLE_CONDITION_ERROR` (I-6; reviews R8-9, R9-6),",
     "After a process failure or a fold exception, a `NOT_APPLICABLE_*` pair with an actually executed run becomes `NOT_EVALUABLE_CONDITION_ERROR` (I-6; owner decision of 2026-10-29, §1.16),"),
    # 9
    ("All six points are decided by the owner (§1.9 to §1.14).", "All six points are decided by the owner (§1.9 to §1.14), and so are the two questions of 2026-10-29 (§1.15, §1.16)."),
    ("and `config/code_review_status_v11.json` → `open_owner_decisions` is empty.", "and `config/code_review_status_v12.json` → `open_owner_decisions` is empty."),
    ("Two implementer readings are listed for the owner's confirmation (`implementer_readings_for_owner_confirmation`): the label of an eligible pair whose run raised (§1.14), and the scope of I-6 after a failure of the separate recomputation or its fold (§1.12). Neither changes an outcome.",
     "The two implementer readings that rev10 listed were decided by the owner on 2026-10-29: the label became `NOT_EVALUABLE_CONDITION_ERROR` (§1.15), and the scope was confirmed (§1.16). One implementer reading remains for the owner's confirmation (`implementer_readings_for_owner_confirmation`): which stages count as \"a run or evaluation\", and that an existing NOT_EVALUABLE label stays after an exception at a later stage (§1.14). It changes no outcome."),
    ("| I-6 | an exception makes the pair NOT_EVALUABLE whatever its label would otherwise be, NOT_APPLICABLE and FAIL included (§1.14) | the pair label when a run or its evaluation raised | `campaign.run_condition`, `fold_separate_recomputation`, `fold_failed`; `qs_vs_dyn_applicability`; `checks.qs_dynamic_accounting` (§2, §3, §7.2) |",
     "| I-6 | an exception makes the pair NOT_EVALUABLE even if its QS check would otherwise be NOT_APPLICABLE (§1.14) | the pair label when a run or its evaluation raised | `campaign.run_condition`, `fold_separate_recomputation`, `fold_failed`; `qs_vs_dyn_applicability`; `checks.qs_dynamic_accounting` (§2, §3, §7.2) |\n| I-6b | an attempted run that raised gives `NOT_EVALUABLE_CONDITION_ERROR`, never `NOT_EVALUABLE_RUN_MISSING` (owner decision 2026-10-29, §1.15) | the label of a QS-eligible pair whose run raised | `campaign.run_condition` (§2, §3) |\n| I-6 scope | after a failure of the separate recomputation or its fold only a `NOT_APPLICABLE_*` pair with an actually executed run is relabelled (owner decision 2026-10-29, §1.16) | which N/A pairs become NOT_EVALUABLE after such a failure | `campaign._na_pair_not_evaluable`, `fold_separate_recomputation`, `fold_failed`, `execute_schedule` (§2, §3, §7.8) |"),
    ("I-3 can change whether a percentage exists. The other five change only a QS-versus-dynamic label, its per-status count, or the branch outcome.",
     "I-3 can change whether a percentage exists. The others change only a QS-versus-dynamic label, its per-status count, or the branch outcome."),
    # 13
    ("1. The rev7 to rev13 changes pass an independent review, and the owner accepts the closure. R5-1 and R5-2 (MAJOR) were verified fixed by AI-agent reviews, and R8-1 to R8-3 (MAJOR) by the AI-agent review of release attempt 9, which found one more MAJOR finding (R9-1), fixed in rev13. The review of release attempt 10 and the owner's acceptance are pending: `config/code_review_status_v11.json` keeps `open_major` 6 and a `reviews_pending` item until then, and each blocks.",
     "1. The rev7 to rev14 changes pass an independent review, and the owner accepts the closure. The six MAJOR findings R5-1, R5-2, R8-1, R8-2, R8-3 and R9-1 are verified fixed by AI-agent reviews (R9-1 by the review of release attempt 10); the owner's acceptance is not recorded. The review of release attempt 11 and the owner's acceptance are pending: `config/code_review_status_v12.json` keeps `open_major` 6 and a `reviews_pending` item until then, and each blocks."),
    # 15
    ("the owner may confirm the two implementer readings (§1.12, §1.14).", "the owner may confirm the implementer reading of §1.14."),
]
for a, b in REPL:
    assert t.count(a) == 1, ("not exactly once", a[:110], t.count(a))
    t = t.replace(a, b)

S12_START, S12_END = "### 12.1 Since rev9 (complete list)", "## 13. Blockers retained"
i, j = t.index(S12_START), t.index(S12_END)
t = t[:i] + (D / "a2_rev11_sec12.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + t[j:]
for bad in ("rev10 —", "status_v11.json", "six of its notes", "unchanged from rev3", "unchanged from rev4",
            "This candidate keeps `NOT_EVALUABLE_RUN_MISSING`", "two implementer readings (§1.12, §1.14)"):
    assert bad not in t, bad
assert t.count(I6B_WORDS) == 1 and t.count(SCOPE_WORDS) == 1
assert t.count("{{BLOCK}}") == 1 and "|\n\n|" not in t
dst.write_text(t, encoding="utf-8", newline="\n")
print("ok", t.count("\n"), "lines")
