"""Write config/code_review_status_v14.json from v13 (kept unchanged): the R11 findings of the attempt-11 review,
open_major 7 (R11-1 added: fixed in rev15, not yet verified; nothing lowered; no owner acceptance recorded), the corrected
records of R10-1, R10-2 and R8-1, and the three-part implementer reading. Refuses to overwrite.
Usage: write_status_v14.py <pilot_dir>"""
import json, sys
from pathlib import Path

P = Path(sys.argv[1])
src, dst = P / "config/code_review_status_v13.json", P / "config/code_review_status_v14.json"
if dst.exists():
    sys.exit(f"refused: {dst} exists")
raw = src.read_text(encoding="utf-8")
d = json.loads(raw.replace("candidate rev12 section", "candidate rev13 section"))
assert d["open_major"] == 6 and d["owner_acceptance_of_major_closures"].startswith("not recorded")
d["review"] += (" + review/R11_attempt11_review_agent_report_20261029.md (review of release attempt 11: R11-1 MAJOR, "
                "R11-2..R11-4 MINOR, R11-5..R11-9 NOTE; an AI review agent, not a human audit)")
d["supersedes"] = "config/code_review_status_v13.json (kept unchanged)"
d["open_major"] = 7
d["basis_for_counts"] = (
    "open_critical 0: no review found a CRITICAL finding. open_major 7: R5-1 and R5-2 (verified FIXED by the AI-agent "
    "verification of attempt 6), R8-1, R8-2 and R8-3 (verified FIXED by the AI-agent review of attempt 9), R9-1 (verified "
    "FIXED by the AI-agent review of attempt 10) and R11-1 (review of attempt 11; fixed in rev15 and candidate rev13, not "
    "yet verified). All are pending the owner's acceptance; no owner acceptance is recorded, so none is closed or lowered "
    "here. An AI-agent review is not a human audit and not the owner's acceptance")
d["owner_acceptance_of_major_closures"] = ("not recorded (2026-10-29): R5-1, R5-2, R8-1, R8-2, R8-3, R9-1 and R11-1 stay "
                                           "counted in open_major until a later status file records the owner's explicit "
                                           "acceptance")
mf = d["major_findings"]
mf["R8-1"] += ("; note (review R11-8): since rev14 (owner decision I-6b, 2026-10-29) a QS-eligible pair whose attempted run "
               "raised is NOT_EVALUABLE_CONDITION_ERROR, not NOT_EVALUABLE_RUN_MISSING as described above")
mf["R11-1"] = ("the machine block stated, under 'Owner decision I-6b', that a genuinely absent run energy is 'an executed run "
               "without a finite simulator energy, no exception' (an interpretation presented as an owner decision; no "
               "outcome effect); rev15 and candidate rev13: the I-6b clause holds only the owner's sentences, and the mapping "
               "is part (c) of the labelled implementer reading (tests/test_owner_decisions_v15.py); verification pending "
               "(review of attempt 12); owner acceptance pending")
m = d["minor_findings"]
m["R10-1"] = ("machine-block wording; partly fixed in rev14 (review R11: the I-6 ruling clause and the readings (a), (b) were "
              "corrected, but the I-6b clause carried an unlabelled gloss, R11-1, and reading (a) was called outcome-free, "
              "R11-3); completed in rev15 and candidate rev13")
m["R10-2 (NOTE)"] = ("addressed in rev14 and rev15 by tests whose first call works on the old code, with mutation runs "
                     "(logs/zz_mutation_check_*): behavioural for R9-6 in the executor (separate-recomputation failure: "
                     "rev12; fold failure: rev12, rev15 test), R9-4(b) (rev12), I-6b (rev13), R3-9 (rev11) and, since rev15, "
                     "I6FL (rev13 and rev11, standalone test). The rev14 record claimed I6FL evidence that did not exist "
                     "(review R11-4); corrected here")
m.update({
    "R11-2": "candidate wording; fixed in candidate rev13: the I-6b owner's words are quoted in full, including 'Do not "
             "perform a broad label rewrite.'",
    "R11-3": "fixed in rev15 and candidate rev13: the implementer reading states that part (a) can change an outcome (an "
             "exception in a reporting stage or the QS-screen diagnosis makes a pair that would be PASS or NOT_APPLICABLE_* "
             "NOT_EVALUABLE_CONDITION_ERROR, so the M0/M1 criterion INCONCLUSIVE); parts (b) and (c) change none",
    "R11-4": "fixed in rev15: a standalone I6FL test (an eligible pair whose B3 run raised while B0 FAILs) whose first "
             "assertion uses only names every version has; mutation runs on rev13 and rev11 in logs/",
    "R11-5 (NOTE)": "fixed in candidate rev13: section 12 cites the final comparison logs; report 21 is stated to be written "
                    "after the review of release attempt 12",
    "R11-6 (NOTE)": "(b) fixed in rev15: fold_separate_recomputation raises on a length mismatch instead of truncating (the "
                    "executor then applies fold_failed); (a) the fallback without executed run IDs and the unguarded "
                    "fold_failed call are unchanged and documented (unreachable from the executor; fail-closed)",
    "R11-7 (NOTE)": "addressed in rev15: a forced-PASS override test; executor tests of I-6b for M1, M2 and an invalid other "
                    "arm; a fold-failure executor test for a pair without an executed run (mutation run on rev12); the stale "
                    "test comment corrected",
    "R11-8 (NOTE)": "fixed in rev15: the reason text cites owner decision I-6b only for a QS-eligible pair; the R8-1 entry "
                    "notes the rev14 label",
    "R11-9 (NOTE)": "addressed in rev15: the I-1 and I-4 owner-ruling clauses of the machine block hold the owner's words, "
                    "with the implementation details after 'As implemented'; the I-6 'As applied' clause names execution "
                    "validity and recomputation validity separately and resolves the case of a pair with no executed run"})
r = d["owner_rulings_implemented"]
r["I-6b"] = ("2026-10-29: a QS-eligible pair whose run was attempted but raised an exception is "
             "NOT_EVALUABLE_CONDITION_ERROR, not NOT_EVALUABLE_RUN_MISSING; a genuinely absent run follows the existing "
             "missing-run path (candidate rev13 section 1.15)")
d["implementer_readings_for_owner_confirmation"] = [
    "I-6 application (not an owner ruling; candidate rev13 section 1.14 and the machine block): (a) every recorded stage of "
    "a pair (run, run_report, qs_screen with its per-piece diagnosis, classify, qs_vs_dynamic, condition_report, "
    "condition) counts as 'a run or evaluation'; this CAN change an outcome: an exception in a reporting stage or in the "
    "QS-screen diagnosis makes a pair that would otherwise be PASS or NOT_APPLICABLE_* NOT_EVALUABLE_CONDITION_ERROR, so "
    "the M0/M1 criterion INCONCLUSIVE; (b) after an exception at a stage other than one of its runs, a pair already "
    "NOT_EVALUABLE_RUN_MISSING, NOT_EVALUABLE_QS_UNDEFINED or NOT_EVALUABLE_RUN_INVALID keeps that label (no outcome "
    "effect); (c) the owner's 'genuinely absent run' (I-6b) is read as the AMB-29(b) case of an arm without a finite "
    "dynamic energy: an executed run whose simulator energy is not finite, without an exception, stays "
    "NOT_EVALUABLE_RUN_MISSING (no outcome effect). Not an open decision; the owner may confirm or change it when "
    "issuing amendment 2"]
d["decided_through_amendment_2_approval_rule"] = d["decided_through_amendment_2_approval_rule"].replace(
    "Reviews R7-2, R8, R9, R10:", "Reviews R7-2, R8, R9, R10, R11:").replace(
    "One implementer reading is listed for confirmation; it changes no outcome.",
    "One implementer reading (three parts) is listed for confirmation; part (a) can change an outcome, parts (b) and (c) "
    "cannot.")
assert "R11:" in d["decided_through_amendment_2_approval_rule"] and "three parts" in d["decided_through_amendment_2_approval_rule"]
d["pending_release_steps"][0] = ("independent read-only AI review of rev15 on release attempt 12 (pending at the time "
                                 "this file was written)")
d["pending_release_steps"][1] = ("owner's acceptance of the closure of the AI-agent reviews (R5-1, R5-2, R8-1 to R8-3, "
                                 "R9-1 and R11-1 counted in open_major until then); an AI-agent review is not a human audit")
d["reviews_pending"] = [
    "independent read-only AI review of rev15 (fixes of R11-1 to R11-9, candidate rev13) on release attempt 12, and the "
    "owner's acceptance of the closure of the rev7 to rev15 review (an AI-agent review is not a human independent audit)"]
dst.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
print(dst, d["open_major"], sorted(d["major_findings"]))
