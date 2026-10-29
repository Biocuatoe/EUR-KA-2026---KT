"""Write config/code_review_status_v12.json from v11 (kept unchanged): the R10 findings of the attempt-10 review, the
owner's decisions of 2026-10-29 (I-6b; the scope of the I-6 relabelling after a separate-recomputation or fold
failure), the remaining implementer reading, and the pending review of attempt 11. open_major stays 6: no owner
acceptance of any MAJOR closure is recorded. Refuses to overwrite. Usage: write_status_v12.py <pilot_dir>"""
import json, sys
from pathlib import Path

P = Path(sys.argv[1])
src, dst = P / "config/code_review_status_v11.json", P / "config/code_review_status_v12.json"
if dst.exists():
    sys.exit(f"refused: {dst} exists")
d = json.loads(src.read_text(encoding="utf-8"))
assert d["open_major"] == 6 and d["open_owner_decisions"] == []
d["review"] += (" + review/R10_attempt10_review_agent_report_20261029.md (review of release attempt 10: no CRITICAL or "
                "MAJOR; R10-1 MINOR, R10-2..R10-4 NOTE; an AI review agent, not a human audit)")
d["supersedes"] = "config/code_review_status_v11.json (kept unchanged)"
d["date"] = "2026-10-29"
d["open_major"] = 6
d["basis_for_counts"] = (
    "open_critical 0: no review found a CRITICAL finding. open_major 6: R5-1 and R5-2 (verified FIXED by the AI-agent "
    "verification of attempt 6), R8-1, R8-2 and R8-3 (verified FIXED by the AI-agent review of attempt 9) and R9-1 "
    "(verified FIXED by the AI-agent review of attempt 10). All six are AI-verified fixes pending the owner's acceptance; "
    "no owner acceptance is recorded, so none is closed or lowered here. An AI-agent review is not a human audit and not "
    "the owner's acceptance")
d["owner_acceptance_of_major_closures"] = ("not recorded (2026-10-29): R5-1, R5-2, R8-1, R8-2, R8-3 and R9-1 stay counted in "
                                           "open_major until a later status file records the owner's explicit acceptance")
mf = d["major_findings"]
assert "verification pending (review of attempt 10)" in mf["R9-1"]
mf["R9-1"] = mf["R9-1"].replace("verification pending (review of attempt 10); owner acceptance pending",
                                "verified FIXED by the AI-agent review of attempt 10 (R10 report); owner acceptance pending")
assert "verified FIXED by the AI-agent review of attempt 10" in mf["R9-1"]
d["minor_findings"].update({
    "R10-1": "machine-block wording; fixed in rev14 and candidate rev11: AMB_29_condition_error separates the owner's I-6 "
             "ruling (its own words), the owner's decisions of 2026-10-29 (I-6b; the relabelling scope after a "
             "separate-recomputation or fold failure), the rules as applied (closing clause: RUN_INVALID after such a "
             "failure; RUN_MISSING, QS_UNDEFINED and RUN_INVALID remain applicable under their own rules) and one "
             "sentence labelled 'Implementer reading (not an owner ruling)' (tests/test_owner_decisions_v14.py)",
    "R10-2 (NOTE)": "addressed in rev14: standalone tests whose first call works on the old code "
                    "(tests/test_owner_decisions_v14.py); mutation runs of these tests against the rev12 and rev13 "
                    "modules, and of I6FL and R3-9 against the modules before their change, are in logs/zz_mutation_check_*",
    "R10-3 (NOTE)": "fixed in candidate rev11: no 'six of its notes'; the headings of sections 1.1 to 1.3 say 'first "
                    "stated in rev3/rev4' instead of 'unchanged from', and the rev10 diagnosis sentence is a separate "
                    "implementation note outside the N-A2 ruling paragraph",
    "R10-4 (NOTE)": "fixed in rev14: fold_failed indexes conds only within its length (a row without a matching condition "
                    "is treated as executed, fail-closed), so the fallback cannot raise on the indexing; regression test "
                    "in tests/test_owner_decisions_v14.py"})
r = d["owner_rulings_implemented"]
for k in list(r):
    r[k] = r[k].replace("candidate rev10 section", "candidate rev11 section")
r["I-6b"] = ("2026-10-29: a QS-eligible pair one of whose runs was attempted and raised an exception is "
             "NOT_EVALUABLE_CONDITION_ERROR, not NOT_EVALUABLE_RUN_MISSING; a genuinely absent run energy follows the "
             "missing-run path (candidate rev11 section 1.15)")
r["I-6 recomputation or fold failure scope"] = (
    "2026-10-29: after a failure of the separate recomputation or its fold, only a NOT_APPLICABLE_* pair with an "
    "actually executed run becomes NOT_EVALUABLE_CONDITION_ERROR; missing runs keep the existing handling; RUN_INVALID "
    "and NOT_EVALUABLE classifications are preserved (candidate rev11 section 1.16)")
d["implementer_readings_decided_by_owner"] = [
    "2026-10-29, owner decision I-6b: the label of a QS-eligible pair whose run raised is NOT_EVALUABLE_CONDITION_ERROR "
    "(the earlier implementer reading NOT_EVALUABLE_RUN_MISSING is replaced; rev14)",
    "2026-10-29, owner decision on the relabelling scope after a separate-recomputation or fold failure: only a "
    "NOT_APPLICABLE_* pair with an actually executed run (the earlier implementer reading is confirmed)"]
d["implementer_readings_for_owner_confirmation"] = [
    "I-6 application (not an owner ruling; no effect on any branch outcome, which is INCONCLUSIVE either way): (a) every "
    "recorded stage of a pair (run, run_report, qs_screen with its per-piece diagnosis, classify, qs_vs_dynamic, "
    "condition_report, condition) counts as 'a run or evaluation'; (b) after an exception at a stage other than one of "
    "its runs, a pair already NOT_EVALUABLE_RUN_MISSING, NOT_EVALUABLE_QS_UNDEFINED or NOT_EVALUABLE_RUN_INVALID keeps "
    "that label (it is already NOT_EVALUABLE). Candidate rev11 section 1.14 and the machine block state it as an "
    "implementer reading. Not an open decision; the owner may confirm or change it when issuing amendment 2"]
d["decided_through_amendment_2_approval_rule"] = (
    "Reviews R7-2, R8, R9, R10: no owner ruling on the content of amendment 2 is open; every one is listed in "
    "owner_rulings_implemented (N-A2, AMB-29(a)-(d), AMB-30, AMB-31, AMB-32, I-1 to I-6, and the owner's decisions of "
    "2026-10-29). One implementer reading is listed for confirmation; it changes no outcome. What remains are release "
    "steps, listed in pending_release_steps; they are not content decisions")
d["pending_release_steps"][0] = ("independent read-only AI review of rev14 on release attempt 11 (pending at the time "
                                 "this file was written)")
d["pending_release_steps"][1] = ("owner's acceptance of the closure of the AI-agent reviews (R5-1, R5-2, R8-1 to R8-3 "
                                 "and R9-1 counted in open_major until then); an AI-agent review is not a human audit")
d["reviews_pending"] = [
    "independent read-only AI review of rev14 (owner decisions I-6b and the relabelling scope of 2026-10-29, fixes of "
    "R10-1 to R10-4, candidate rev11) on release attempt 11, and the owner's acceptance of the closure of the rev7 to "
    "rev14 review (an AI-agent review is not a human independent audit)"]
dst.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
print(dst, d["open_major"], sorted(d["major_findings"]), len(d["implementer_readings_for_owner_confirmation"]))
