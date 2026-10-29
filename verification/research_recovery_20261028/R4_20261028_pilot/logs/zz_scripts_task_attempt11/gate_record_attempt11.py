"""Write GATE_RECORD_attempt11.json inside the attempt-11 directory (refuses to overwrite). All hashes are computed here
from the files; nothing is typed in except paths, the fixed expected values that are checked, and the review outcome
transcribed from the saved review report (whose summary line is asserted and whose hash is recorded).
Usage: gate_record_attempt11.py <RR dir>"""
import hashlib, json, sys, time, xml.etree.ElementTree as ET
from pathlib import Path

RR = Path(sys.argv[1]).resolve()
C = RR / "R4_20261028_campaign"
RA = C / "release_attempts"
A = RA / "attempt11_final_owner_decisions"
P = RR / "R4_20261028_pilot"
out = A / "GATE_RECORD_attempt11.json"
if out.exists():
    sys.exit(f"refused: {out} exists")
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def junit(p):
    r = ET.parse(p).getroot()
    s = [r] if r.tag == "testsuite" else list(r.iter("testsuite"))
    return {k: sum(int(x.get(k, 0)) for x in s) for k in ("tests", "failures", "errors", "skipped")}


EXPECT = dict(protocol="f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab",
              a1="7720fed75bb678e47a229d00aff154e0aa14607c051f4a1163cc9bf67b6abee2",
              a1_approval="03f835e9311410095e4447840ecb2b02d95c50279527df5fdf2f6d334e15eecd",
              root_manifest="eae902275b363357674be7aed8a8b37162b687cd72ced0033dbfb84dfaff32e4",
              root_gate="b4108d85c2bc35937e7c067aa922cca44e9b24f8d0a3e0a0286cf07fd7d69759",
              root_gate_record="c25b2cfcd899f9ea7ce1bc2e4583c6879007a5b1a9cd71e2f9cf0f790b41f8e8",
              rev3="fdaf193de510488733f0e0899d50def86cbeafabdbecdd3bc7a144099b6f492c",
              rev4="c726560d1e87036cbd94fe58724cafdc1e4746647f6cfacbb320f3e14ed143ab",
              rev5="e7ba73c11784b3cf38f48e32b69a7a7c21b070d039118547d638bc1bf06d4f5f",
              rev6="0dcb767e97e19f40c00735d9efaecf8d21c396c23952b70e60ccb21a3f711e1f",
              rev7="0e3ef3112c979237e7079f176b21dd4f2ce682c7ab435f36f33321ffe67a5996",
              rev8="f6430bf5512cb56065a2465bcfda1c4c42e244b80f73fcd3e88d985ac8811f7c",
              rev9="cdeea032c520f408f1f300a53cf1bc8b1ec4582d80340d3df2c2c94fa5d45719",
              rev10="5479f0e81b981c7977ea5a416762972d2a332d4fdb75beee7ad8379ade399804",
              rev11="162b688d2a1665831705bc3a1bc68273f5ede15cc87b0d226837cf4f015998e9",
              rev12="ac376c0b362c2e99a9d3777fa849205844487e0be50a41dd1c5f1b2410b5ae1b",
              a3_manifest="e33cdcb9b9ff6c9e50d34ab00acdc53a21dac4fe87c20e79c41158f84f5da9d3",
              a4_manifest="0727aa086b3da7639c680a0bdd4f84ce58f7fe11133e64526727841cbcb91c89",
              a5_manifest="c32601c33365dc5c06f563d0ccec01c483208809499d87f3f2d7d944a4f3ca00",
              a6_manifest="b19ddce7373aff8e02ae854986f3107355ea244a05e0a4b62831623b96ad4c3a",
              a7_manifest="42e8c88f35edd49e206354173a79925050eae395a52b04a5fba7675f32a1f933",
              a8_manifest="2ea8714f3f492e8ceaa5cf345182ce243ef8dab51415f55413fc45bf5300a617",
              a9_manifest="0e317eef0a0a7ab54af9c2c69aee4af619693dabcf5ca441d2a7c386f5766ffc",
              a10_manifest="9af4b502cbc01fb1ee657ac0f509f71a59b87f8467d7e7e5a8dfc0b9aa6c84a8")
ATT = {3: "attempt3_amendment2", 4: "attempt4_owner_rulings", 5: "attempt5_owner_rulings", 6: "attempt6_review_fixes",
       7: "attempt7_final_review", 8: "attempt8_final_owner_decisions", 9: "attempt9_review_fixes", 10: "attempt10_review_fixes"}
got = dict(protocol=sha(RR / "R4_20261028_preflight" / "03_R4_protocol_v1.md"),
           a1=sha(C / "release/03_R4_protocol_v1_amendment_1.md"), a1_approval=sha(C / "release/amendment_1_approval.json"),
           root_manifest=sha(C / "zz_sha256_manifest_release.csv"), root_gate=sha(C / "logs/pre_run_hashes.txt"),
           root_gate_record=sha(C / "GATE_RECORD_release.json"), rev3=sha(P / "03_protocol_v1_amendment_2_DRAFT.md"),
           **{f"rev{n}": sha(P / f"03_protocol_v1_amendment_2_rev{n}_CANDIDATE.md") for n in (4, 5, 6, 7, 8, 9, 10, 11, 12)},
           **{f"a{n}_manifest": sha(RA / d / f"zz_sha256_manifest_attempt{n}.csv") for n, d in ATT.items()})
assert got == EXPECT, {k: (got[k], EXPECT[k]) for k in got if got[k] != EXPECT[k]}
dry = sorted(A.glob("dry_run_*"))[-1]
pre = json.loads((A / "logs/preconditions_attempt11.json").read_text(encoding="utf-8"))
cp = json.loads((A / "logs/copy_verification_attempt11_summary.json").read_text(encoding="utf-8"))
dj = json.loads((dry / "dry_run.json").read_text(encoding="utf-8"))
val = json.loads((A / "logs/release_validation_attempt11.json").read_text(encoding="utf-8"))
v8 = json.loads((RA / "attempt10_review_fixes/logs/release_validation_attempt10.json").read_text(encoding="utf-8"))
same_legacy = ([(h["file"], h["text"]) for h in val["legacy_numbers"]["hits_in_code"]]
               == [(h["file"], h["text"]) for h in v8["legacy_numbers"]["hits_in_code"]])
assert same_legacy and val["all_checks_true"]
rpt = A / "review" / "R11_attempt11_review_agent_report_20261029.md"
assert "**New findings: CRITICAL 0 · MAJOR 1 · MINOR 3 · NOTE 5.**" in rpt.read_text(encoding="utf-8")
assert sha(P / "review" / rpt.name) == sha(rpt)
rec = {
    "record": "release attempt 11 gate record (owner decisions of 2026-10-29: I-6b and the relabelling scope after a "
              "separate-recomputation or fold failure; fixes of review R10; amendment 2 candidate rev12). NOT a release, "
              "NOT the protocol 10.1 gate",
    "written": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    "campaign_status": "BLOCKED",
    "attempt_status": "REVIEWED - 1 MAJOR finding open (R11-1: an implementer gloss inside the owner decision I-6b clause "
                      "of the machine block; wording, no outcome effect; independent AI-agent review, not a human audit). "
                      "NOT RELEASABLE. Preserved unchanged as reviewed; the corrections go into a new attempt, "
                      "release_attempts/attempt12_final_owner_decisions/ (a CRITICAL or MAJOR finding is never downgraded)",
    "superseded_by": "release_attempts/attempt12_final_owner_decisions/",
    "built_from": "the unchanged attempt-10 state: at the start of the task the pilot's code/ and config/ equalled attempt 10's "
                  "copy file by file (logs/zz_start_state_v10.json, baseline_pilot_equals_attempt10)",
    "attempt_directory": "R4_20261028_campaign/release_attempts/attempt11_final_owner_decisions/",
    "protocol_v1": {"path": "R4_20261028_preflight/03_R4_protocol_v1.md", "sha256": got["protocol"]},
    "amendment_1": {"path": "R4_20261028_campaign/release/03_R4_protocol_v1_amendment_1.md", "sha256": got["a1"],
                    "status": "APPROVED (issued 2026-10-28; unchanged)", "approval_record_sha256": got["a1_approval"]},
    "amendment_2": {"draft_path": "R4_20261028_pilot/03_protocol_v1_amendment_2_rev12_CANDIDATE.md",
                    "draft_sha256": got["rev12"], "revision": "candidate rev12",
                    "status": "CANDIDATE - DRAFT - NOT APPROVED FOR RELEASE",
                    "superseded_unused": {"rev11": got["rev11"],
                                          "why": "its section 1.1 heading said 'first stated in rev3'; the N-A2 section is "
                                                 "in rev0. Written and superseded before any test or review"},
                    "earlier_drafts_unchanged": {k: got[k] for k in ("rev3", "rev4", "rev5", "rev6", "rev7", "rev8", "rev9",
                                                                     "rev10")},
                    "owner_decisions_2026_10_29": ["I-6b: a QS-eligible pair whose run was attempted and raised is "
                                                   "NOT_EVALUABLE_CONDITION_ERROR, not NOT_EVALUABLE_RUN_MISSING",
                                                   "after a separate-recomputation or fold failure only a NOT_APPLICABLE_* "
                                                   "pair with an actually executed run is relabelled"],
                    "dry_run_reading": {"status": dj["draft_amendment_2"].get("status"),
                                        "errors": dj["draft_amendment_2"].get("errors")},
                    "issued_copy_present": (C / "release/03_R4_protocol_v1_amendment_2.md").exists(),
                    "approval_record_present": (C / "release/amendment_2_approval.json").exists()},
    "source": {"pilot_readiness_gate": {"path": "R4_20261028_pilot/logs/readiness_gate_v15.json",
                                        "sha256": sha(P / "logs/readiness_gate_v15.json"),
                                        "junit": junit(P / "logs/pytest_run29.xml"),
                                        "junit_sha256": sha(P / "logs/pytest_run29.xml")},
               "copy_verification": {"files_copied": cp["files_copied"], "copy_mismatches": cp["copy_mismatches"],
                                     "gate_code_files": cp["gate_code_files"], "gate_mismatches": cp["gate_mismatches"],
                                     "not_in_gate": cp["copied_code_or_config_files_not_in_gate"],
                                     "summary_sha256": sha(A / "logs/copy_verification_attempt11_summary.json"),
                                     "rows_sha256": sha(A / "logs/copy_verification_attempt11.csv")},
               "line_endings": {"baseline": "R4_20261028_pilot/logs/zz_line_endings_rev13_baseline.csv",
                                "final_check": "R4_20261028_pilot/logs/zz_line_endings_rev13_to_rev14_final.csv",
                                "final_check_sha256": sha(P / "logs/zz_line_endings_rev13_to_rev14_final.csv"),
                                "byte_aware_diff": "R4_20261028_pilot/logs/zz_diff_rev13_to_rev14_final.txt",
                                "result": "every changed or added file keeps its convention (campaign.py CRLF, the tests "
                                          "and configs LF); no mixed file; closedloop.py's historical mixed endings "
                                          "untouched"},
               "mutation_checks": {
                   "first_invocation_failed": "zz_mutation_check_{v14_tests_on_rev13,v14_r10_2_tests_on_rev12,"
                                              "v11_i6_tests_on_rev13,a2_r3_9_test_on_rev11}.txt: ModuleNotFoundError before "
                                              "any test ran (an unquoted path split into several arguments); kept",
                   "run2_and_later": "behavioural on the old modules: I-6b and R10-4 (rev13), I6EL (rev13), R10-2's "
                                     "executor and unknown-status tests (rev12), R3-9 through the new test (rev11); "
                                     "API-level only: the old R3-9 assertion (rev11). Reviewer R11: I6FL was never "
                                     "reached in these runs"}},
    "attempt_tests": {"log": "logs/pytest_release_attempt11.txt", "junit": "logs/pytest_release_attempt11.xml",
                      **junit(A / "logs/pytest_release_attempt11.xml"),
                      "junit_sha256": sha(A / "logs/pytest_release_attempt11.xml"),
                      "attempt_readiness_gate": {"path": "logs/readiness_gate_v1.json",
                                                 "sha256": sha(A / "logs/readiness_gate_v1.json")}},
    "release_validation": {"path": "logs/release_validation_attempt11.json",
                           "sha256": sha(A / "logs/release_validation_attempt11.json"),
                           "all_checks_true": val["all_checks_true"],
                           "reporting_test_prefixes_all_found_and_passed": val["reporting_tests"]["every_prefix_found"]
                           and val["reporting_tests"]["all_passed"],
                           "legacy_number_hits": len(val["legacy_numbers"]["hits_in_code"]),
                           "legacy_number_hits_identical_to_attempt_10": same_legacy},
    "independent_review": {
        "reviewer": "a new, separate AI review agent ('Plan' agent type, no Edit or Write tools; Read, Grep and Glob only). "
                    "NOT a human independent audit",
        "timing": "scope recorded 2026-10-29 07:45:53 (+0700); agent launched right after (before 07:46:36); ran without "
                  "interruption for 1,112.0 s; delivered 08:05:04. Saved programmatically from the session transcript and "
                  "checked to equal the hand-back text (26,143 characters)",
        "brief": {"path": "review/review_brief_attempt11_as_sent.md", "sha256": sha(A / "review/review_brief_attempt11_as_sent.md")},
        "scope_record": {"path": "review/review_scope_attempt11.json", "sha256": sha(A / "review/review_scope_attempt11.json")},
        "report": {"path": "review/R11_attempt11_review_agent_report_20261029.md", "sha256": sha(rpt),
                   "pilot_copy": "R4_20261028_pilot/review/R11_attempt11_review_agent_report_20261029.md (identical)"},
        "counts": {"CRITICAL": 0, "MAJOR": 1, "MINOR": 3, "NOTE": 5},
        "owner_decisions_verdict": {"I-6b": "implemented correctly and narrowly in the code (text: R11-1, R11-2)",
                                    "relabelling scope": "implemented (behaviour unchanged from rev13; docstrings cite "
                                                         "the decision)"},
        "closure_of_R10": {"R10-1": "PARTLY FIXED (residuals R11-1, R11-3)", "R10-2": "PARTLY ADDRESSED (I6FL, fold_failed)",
                           "R10-3": "FIXED", "R10-4": "FIXED"},
        "open_major": ["R11-1 under 'Owner decision I-6b' the block glossed the owner's 'genuinely absent run' as 'an "
                       "executed run without a finite simulator energy, no exception' without labelling it as an "
                       "implementer reading (no outcome effect)"],
        "open_minor": ["R11-2 the I-6b owner quote in the candidate omits 'Do not perform a broad label rewrite.'",
                       "R11-3 implementer reading (a) is called outcome-free; it is not",
                       "R11-4 the status file claims I6FL mutation evidence that does not exist"],
        "open_notes": ["R11-5 pointers to non-final logs and to report 21", "R11-6 fold fallback without executed IDs; "
                       "zip truncation; unguarded fold_failed", "R11-7 test gaps (forced PASS, other motors and arms, "
                       "fold_failed mutation, stale comment)", "R11-8 R8-1 record and the I-6b reason text",
                       "R11-9 implementer additions inside other owner-ruling clauses (I-1, I-4)"],
        "critical_or_major_open": True,
        "formal_status": "code_review_status_v13.json (in this attempt, written before the review) counts open_major 6, "
                         "records no owner acceptance, lists one implementer reading and a reviews_pending item; each "
                         "blocks",
        "status_file_in_this_attempt": {"path": "config/code_review_status_v13.json",
                                        "sha256": sha(A / "config/code_review_status_v13.json")}},
    "dry_run": {"path": dry.name + "/", "dry_run_json_sha256": sha(dry / "dry_run.json"),
                "schedule_170_csv_sha256": sha(dry / "schedule_170.csv"), "counts_per_set": dj["schedule"]["counts_per_set"],
                "total_runs": sum(dj["schedule"]["counts_per_set"].values()), "schedule_passed": dj["schedule"]["passed"],
                "schedule_identical_to_attempt_2": sha(dry / "schedule_170.csv")
                == sha(C / "release/dry_run_20261028_083731/schedule_170.csv"),
                "planner_jobs_identical_to_attempt_2": sha(dry / "planner_jobs.csv")
                == sha(C / "release/dry_run_20261028_083731/planner_jobs.csv"),
                "config": dj["campaign_config"], "sensitivity_table_regenerates": dj["sensitivity"]["regenerates_identically"]},
    "schedule_validation": {k: val["schedule"][k] for k in (
        "runs", "counts_per_set", "run_ids_unique", "all_official_prefix", "smoke_runs_excluded", "s2_rows_all_held_out",
        "s1_only_in_INS", "every_profile_designed_on_P1", "sen_gain_equal_nominal_P1_for_all_32_draws", "sen_draws_checked")},
    "preconditions": {"record": "logs/preconditions_attempt11.json", "sha256": sha(A / "logs/preconditions_attempt11.json"),
                      "readiness_blockers": pre["readiness_blockers"], "campaign_mode_blockers": pre["campaign_blockers"]},
    "gate_criteria": [
        {"criterion": "0. owner rulings and decisions implemented as ruled", "met": False,
         "evidence": "the code is confirmed correct; the machine block's I-6b clause carries an unlabelled interpretation "
                     "(R11-1, MAJOR)"},
        {"criterion": "1. amendment 2 approved by the owner and issued", "met": False,
         "evidence": "no release/03_R4_protocol_v1_amendment_2.md and no release/amendment_2_approval.json"},
        {"criterion": "2. release attempt passes all mandatory tests and independent reviews", "met": False,
         "evidence": f"tests: {junit(A / 'logs/pytest_release_attempt11.xml')} from this copy; AI-agent review: 1 MAJOR open"},
        {"criterion": "3. final release manifest and protocol hashes verified", "met": False,
         "evidence": "this attempt's manifest and the protocol, amendment 1 and draft hashes are verified; the FINAL release "
                     "manifest only exists after promotion to the campaign root"},
        {"criterion": "4. promotion to the campaign root with its own protocol 10.1 gate", "met": False,
         "evidence": "not promoted; the campaign root still holds release attempt 2 (amendment 1 only), unchanged"},
        {"criterion": "5. separate explicit owner authorisation (release/campaign_authorization.json)", "met": False,
         "evidence": "absent; no code path writes it"}],
    "prior_attempts": {
        "attempt_1": "release_attempts/attempt1/ (preserved)",
        "attempt_2": {"location": "campaign root", "manifest_sha256": got["root_manifest"],
                      "pre_run_hashes_sha256": got["root_gate"], "gate_record_sha256": got["root_gate_record"],
                      "status": "preserved unchanged (amendment 1 only)"},
        **{f"attempt_{n}": {"location": f"release_attempts/{d}/", "manifest_sha256": got[f"a{n}_manifest"],
                            "status": "preserved unchanged" + ("; superseded by this attempt (reviewed with no CRITICAL or "
                                                               "MAJOR finding)" if n == 10 else "")}
           for n, d in ATT.items()}},
    "official_outputs_present": (C / "outputs").exists() or (A / "outputs").exists(),
    "campaign_mode_invoked": False,
    "campaign_authorization_created": False,
    "arm_to_arm_energy_differences_computed": False,
}
out.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
print(out, sha(out))
print(rec["schedule_validation"], rec["dry_run"]["schedule_identical_to_attempt_2"], rec["dry_run"]["planner_jobs_identical_to_attempt_2"],
      rec["attempt_tests"]["tests"], rec["attempt_tests"]["failures"], len(pre["campaign_blockers"]),
      rec["official_outputs_present"])
