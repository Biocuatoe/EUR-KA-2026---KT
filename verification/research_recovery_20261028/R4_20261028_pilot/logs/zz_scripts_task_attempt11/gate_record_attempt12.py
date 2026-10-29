"""Write GATE_RECORD_attempt12.json inside the attempt-12 directory (refuses to overwrite). All hashes are computed here
from the files; nothing is typed in except paths, the fixed expected values that are checked, and the review outcome
transcribed from the saved review report (whose summary line is asserted and whose hash is recorded).
Usage: gate_record_attempt12.py <RR dir>"""
import hashlib, json, sys, time, xml.etree.ElementTree as ET
from pathlib import Path

RR = Path(sys.argv[1]).resolve()
C = RR / "R4_20261028_campaign"
RA = C / "release_attempts"
A = RA / "attempt12_final_owner_decisions"
P = RR / "R4_20261028_pilot"
out = A / "GATE_RECORD_attempt12.json"
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
              rev13="7f06dd1f1a825c55280fa220b740d617baf4fab1899300a4a31958f345d9759b",
              a3_manifest="e33cdcb9b9ff6c9e50d34ab00acdc53a21dac4fe87c20e79c41158f84f5da9d3",
              a4_manifest="0727aa086b3da7639c680a0bdd4f84ce58f7fe11133e64526727841cbcb91c89",
              a5_manifest="c32601c33365dc5c06f563d0ccec01c483208809499d87f3f2d7d944a4f3ca00",
              a6_manifest="b19ddce7373aff8e02ae854986f3107355ea244a05e0a4b62831623b96ad4c3a",
              a7_manifest="42e8c88f35edd49e206354173a79925050eae395a52b04a5fba7675f32a1f933",
              a8_manifest="2ea8714f3f492e8ceaa5cf345182ce243ef8dab51415f55413fc45bf5300a617",
              a9_manifest="0e317eef0a0a7ab54af9c2c69aee4af619693dabcf5ca441d2a7c386f5766ffc",
              a10_manifest="9af4b502cbc01fb1ee657ac0f509f71a59b87f8467d7e7e5a8dfc0b9aa6c84a8",
              a11_manifest="b62952650d79381ebb3c309dfe17049e03f08cbf7b3e8b929b6f83d3e5ef5768")
ATT = {3: "attempt3_amendment2", 4: "attempt4_owner_rulings", 5: "attempt5_owner_rulings", 6: "attempt6_review_fixes",
       7: "attempt7_final_review", 8: "attempt8_final_owner_decisions", 9: "attempt9_review_fixes", 10: "attempt10_review_fixes", 11: "attempt11_final_owner_decisions"}
got = dict(protocol=sha(RR / "R4_20261028_preflight" / "03_R4_protocol_v1.md"),
           a1=sha(C / "release/03_R4_protocol_v1_amendment_1.md"), a1_approval=sha(C / "release/amendment_1_approval.json"),
           root_manifest=sha(C / "zz_sha256_manifest_release.csv"), root_gate=sha(C / "logs/pre_run_hashes.txt"),
           root_gate_record=sha(C / "GATE_RECORD_release.json"), rev3=sha(P / "03_protocol_v1_amendment_2_DRAFT.md"),
           **{f"rev{n}": sha(P / f"03_protocol_v1_amendment_2_rev{n}_CANDIDATE.md") for n in (4, 5, 6, 7, 8, 9, 10, 11, 12, 13)},
           **{f"a{n}_manifest": sha(RA / d / f"zz_sha256_manifest_attempt{n}.csv") for n, d in ATT.items()})
assert got == EXPECT, {k: (got[k], EXPECT[k]) for k in got if got[k] != EXPECT[k]}
dry = sorted(A.glob("dry_run_*"))[-1]
pre = json.loads((A / "logs/preconditions_attempt12.json").read_text(encoding="utf-8"))
cp = json.loads((A / "logs/copy_verification_attempt12_summary.json").read_text(encoding="utf-8"))
dj = json.loads((dry / "dry_run.json").read_text(encoding="utf-8"))
val = json.loads((A / "logs/release_validation_attempt12.json").read_text(encoding="utf-8"))
v8 = json.loads((RA / "attempt11_final_owner_decisions/logs/release_validation_attempt11.json").read_text(encoding="utf-8"))
same_legacy = ([(h["file"], h["text"]) for h in val["legacy_numbers"]["hits_in_code"]]
               == [(h["file"], h["text"]) for h in v8["legacy_numbers"]["hits_in_code"]])
assert same_legacy and val["all_checks_true"]
rpt = A / "review" / "R12_attempt12_review_agent_report_20261029.md"
assert "**New findings: CRITICAL 0 · MAJOR 0 · MINOR 2 · NOTE 4.**" in rpt.read_text(encoding="utf-8")
assert sha(P / "review" / rpt.name) == sha(rpt)
rec = {
    "record": "release attempt 12 gate record (the owner's decisions of 2026-10-29 and the fixes of review R11; amendment 2 "
              "candidate rev13). NOT a release, NOT the protocol 10.1 gate",
    "written": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    "campaign_status": "BLOCKED",
    "attempt_status": "REVIEWED - no CRITICAL or MAJOR finding (independent AI-agent review, not a human audit); 2 MINOR "
                      "(R12-1, R12-2) and 4 NOTE findings open and recorded for the owner. NOT RELEASED: amendment 2 not "
                      "issued or approved; open_major 7 awaits the owner's acceptance (code_review_status_v14.json blocks); "
                      "R12-2 (implementer extensions inside other owner-ruling clauses of the block) should be resolved "
                      "before the block is approved; no protocol 10.1 gate; no authorisation",
    "attempt_directory": "R4_20261028_campaign/release_attempts/attempt12_final_owner_decisions/",
    "protocol_v1": {"path": "R4_20261028_preflight/03_R4_protocol_v1.md", "sha256": got["protocol"]},
    "amendment_1": {"path": "R4_20261028_campaign/release/03_R4_protocol_v1_amendment_1.md", "sha256": got["a1"],
                    "status": "APPROVED (issued 2026-10-28; unchanged)", "approval_record_sha256": got["a1_approval"]},
    "amendment_2": {"draft_path": "R4_20261028_pilot/03_protocol_v1_amendment_2_rev13_CANDIDATE.md",
                    "draft_sha256": got["rev13"], "revision": "candidate rev13",
                    "status": "CANDIDATE - DRAFT - NOT APPROVED FOR RELEASE",
                    "earlier_drafts_unchanged": {k: got[k] for k in ("rev3", "rev4", "rev5", "rev6", "rev7", "rev8", "rev9",
                                                                     "rev10", "rev11", "rev12")},
                    "owner_decisions_2026_10_29_verbatim_record": {
                        "path": "R4_20261028_pilot/21a_owner_decisions_20261029_verbatim.md",
                        "sha256": sha(P / "21a_owner_decisions_20261029_verbatim.md"),
                        "note": "the owner's message copied programmatically from the session transcript; it is the source "
                                "of the sentence R12-1 found unrecorded; the rev13 §1.16 quote omits the last sentence of "
                                "the owner's §2.2 ('Add targeted regression tests covering each applicable branch and its "
                                "precedence.')"},
                    "text_to_correct_before_issue": [
                        "R12-2 (MINOR): implementer extensions remain inside owner-ruling clauses of the block (AMB-31 "
                        "'or not confirmed by its recomputation' / 'never used by the QS-vs-dynamic check', AMB-30, "
                        "AMB-29(a), AMB-29(d), the I-3 rule, the fold-scope qualifiers) and in candidate §1.16",
                        "R12-1 (MINOR): the source of the quoted sentence is now recorded (21a_...); the §1.16 quote should "
                        "also include the owner's last §2.2 sentence",
                        "R12-3 to R12-6 (NOTE): record wording, a code comment, the examples of reading (a), test cases"],
                    "dry_run_reading": {"status": dj["draft_amendment_2"].get("status"),
                                        "errors": dj["draft_amendment_2"].get("errors")},
                    "issued_copy_present": (C / "release/03_R4_protocol_v1_amendment_2.md").exists(),
                    "approval_record_present": (C / "release/amendment_2_approval.json").exists()},
    "source": {"pilot_readiness_gate": {"path": "R4_20261028_pilot/logs/readiness_gate_v16.json",
                                        "sha256": sha(P / "logs/readiness_gate_v16.json"),
                                        "junit": junit(P / "logs/pytest_run30.xml"),
                                        "junit_sha256": sha(P / "logs/pytest_run30.xml")},
               "copy_verification": {"files_copied": cp["files_copied"], "copy_mismatches": cp["copy_mismatches"],
                                     "gate_code_files": cp["gate_code_files"], "gate_mismatches": cp["gate_mismatches"],
                                     "not_in_gate": cp["copied_code_or_config_files_not_in_gate"],
                                     "summary_sha256": sha(A / "logs/copy_verification_attempt12_summary.json"),
                                     "rows_sha256": sha(A / "logs/copy_verification_attempt12.csv")},
               "line_endings": {"check": "R4_20261028_pilot/logs/zz_line_endings_rev14_to_rev15.csv",
                                "check_sha256": sha(P / "logs/zz_line_endings_rev14_to_rev15.csv"),
                                "byte_aware_diff": "R4_20261028_pilot/logs/zz_diff_rev14_to_rev15.txt",
                                "result": "every changed or added file keeps its convention (campaign.py CRLF, the tests "
                                          "and configs LF); no mixed file"},
               "mutation_checks": {"v15_tests_on_rev14": "behavioural for R11-6(b) and R11-8; text for R11-1, R11-2; "
                                                         "versioning for three tests",
                                   "r11_4_on_rev13_and_rev11": "behavioural (RUN_MISSING on rev13, FAIL on rev11)",
                                   "r11_7_fold_on_rev12": "behavioural (CONDITION_ERROR on rev12)"}},
    "attempt_tests": {"log": "logs/pytest_release_attempt12.txt", "junit": "logs/pytest_release_attempt12.xml",
                      **junit(A / "logs/pytest_release_attempt12.xml"),
                      "junit_sha256": sha(A / "logs/pytest_release_attempt12.xml"),
                      "attempt_readiness_gate": {"path": "logs/readiness_gate_v1.json",
                                                 "sha256": sha(A / "logs/readiness_gate_v1.json")}},
    "release_validation": {"path": "logs/release_validation_attempt12.json",
                           "sha256": sha(A / "logs/release_validation_attempt12.json"),
                           "all_checks_true": val["all_checks_true"],
                           "reporting_test_prefixes_all_found_and_passed": val["reporting_tests"]["every_prefix_found"]
                           and val["reporting_tests"]["all_passed"],
                           "legacy_number_hits": len(val["legacy_numbers"]["hits_in_code"]),
                           "legacy_number_hits_identical_to_attempt_11": same_legacy},
    "independent_review": {
        "reviewer": "a new, separate AI review agent ('Plan' agent type, no Edit or Write tools), instructed to use Read, Grep "
                    "and Glob only. NOT a human independent audit",
        "deviation": "the agent made one Bash call against the brief (disclosed in its report; checked in its transcript): "
                     "sed -n '34p' <attempt-11 review brief> | fold -w 400 at 09:33:46, which prints one line and writes "
                     "nothing; its other tool calls were 49 Read, 48 Grep and 25 Glob",
        "timing": "scope recorded 2026-10-29 09:11:55 (+0700); launched right after; stopped on the account's session limit "
                  "at 09:12:43; resumed with its own context at about 09:32:22; delivered 09:46:27 (846.0 s after "
                  "resumption). Saved programmatically from the session transcript and checked to equal the hand-back "
                  "text (22,238 characters)",
        "brief": {"path": "review/review_brief_attempt12_as_sent.md", "sha256": sha(A / "review/review_brief_attempt12_as_sent.md")},
        "scope_record": {"path": "review/review_scope_attempt12.json", "sha256": sha(A / "review/review_scope_attempt12.json")},
        "report": {"path": "review/R12_attempt12_review_agent_report_20261029.md", "sha256": sha(rpt),
                   "pilot_copy": "R4_20261028_pilot/review/R12_attempt12_review_agent_report_20261029.md (identical)"},
        "counts": {"CRITICAL": 0, "MAJOR": 0, "MINOR": 2, "NOTE": 4},
        "closure_of_R11": {"R11-1": "FIXED", "R11-2": "FIXED (the omission; see R12-1)", "R11-3": "FIXED", "R11-4": "FIXED",
                           "R11-5": "ADDRESSED", "R11-6": "PARTLY ADDRESSED", "R11-7": "ADDRESSED (mostly)",
                           "R11-8": "ADDRESSED", "R11-9": "PARTLY ADDRESSED (residual R12-2)"},
        "owner_decisions_2026_10_29": "unchanged in the code from rev14 (verified); the only rev15 behavioural changes are "
                                      "R11-6(b) and the R11-8 reason text",
        "open_minor": ["R12-1 the I-6b quote ends with a sentence the reviewer found in no recorded copy; it is the owner's "
                       "(21a_owner_decisions_20261029_verbatim.md); the §1.16 quote omits the owner's last §2.2 sentence",
                       "R12-2 implementer extensions inside other owner-ruling clauses of the block, candidate §1.16:129 and "
                       "the status file (stricter, cannot produce a PASS)"],
        "open_notes": ["R12-3 record wording (R11-6(b) partly fixed; R10-1 'completed'; 'rev12 state')",
                       "R12-4 a code comment still carries the R11-1 gloss", "R12-5 reading (a) examples omit classify",
                       "R12-6 test cases (non-finite other arm; rev13 mutation of M1, M2, unconfirmed arm)"],
        "critical_or_major_open": False,
        "formal_status": "code_review_status_v14.json counts open_major 7 (R5-1, R5-2, R8-1..R8-3, R9-1 AI-verified; R11-1 "
                         "now AI-verified by this review), records no owner acceptance, lists one implementer reading in "
                         "three parts and a reviews_pending item; each blocks until a later status file records the "
                         "owner's acceptance",
        "status_file_in_this_attempt": {"path": "config/code_review_status_v14.json",
                                        "sha256": sha(A / "config/code_review_status_v14.json")}},
    "dry_run": {"path": dry.name + "/", "dry_run_json_sha256": sha(dry / "dry_run.json"),
                "schedule_170_csv_sha256": sha(dry / "schedule_170.csv"), "counts_per_set": dj["schedule"]["counts_per_set"],
                "total_runs": sum(dj["schedule"]["counts_per_set"].values()), "schedule_passed": dj["schedule"]["passed"],
                "schedule_identical_to_attempt_2": sha(dry / "schedule_170.csv")
                == sha(C / "release/dry_run_20261028_083731/schedule_170.csv"),
                "planner_jobs_identical_to_attempt_2": sha(dry / "planner_jobs.csv")
                == sha(C / "release/dry_run_20261028_083731/planner_jobs.csv"),
                "config": dj["campaign_config"], "sensitivity_table_regenerates": dj["sensitivity"]["regenerates_identically"]},
    "schedule_validation": {k: val["schedule"][k] for k in (
        "runs", "counts_per_set", "run_ids_unique", "all_official_prefix", "every_condition_has_B0_and_B3",
        "smoke_runs_excluded", "s2_rows_all_held_out", "s1_only_in_INS", "every_profile_designed_on_P1",
        "sen_gain_equal_nominal_P1_for_all_32_draws", "sen_draws_checked")},
    "paired_endpoint": {k: val["paired_endpoint"][k] for k in (
        "confirmatory_only_if_executed_valid_confirmed_and_COMPARABLE", "paired_delta_refuses_every_non_COMPARABLE_status")},
    "preconditions": {"record": "logs/preconditions_attempt12.json", "sha256": sha(A / "logs/preconditions_attempt12.json"),
                      "readiness_blockers": pre["readiness_blockers"], "campaign_mode_blockers": pre["campaign_blockers"]},
    "gate_criteria": [
        {"criterion": "0. owner rulings and decisions implemented as ruled", "met": False,
         "evidence": "code: no CRITICAL or MAJOR finding (AI-agent review); text: R12-2 extensions inside owner clauses; the "
                     "implementer reading awaits the owner; the owner has not accepted the review closures"},
        {"criterion": "1. amendment 2 approved by the owner and issued", "met": False,
         "evidence": "no release/03_R4_protocol_v1_amendment_2.md and no release/amendment_2_approval.json"},
        {"criterion": "2. release attempt passes all mandatory tests and independent reviews", "met": False,
         "evidence": f"tests: {junit(A / 'logs/pytest_release_attempt12.xml')} from this copy; AI-agent review: no "
                     "CRITICAL or MAJOR; NOT met because the owner has not accepted the closure and the shipped status file "
                     "blocks (open_major 7, reviews_pending)"},
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
                            "status": "preserved unchanged" + ("; superseded by this attempt (1 MAJOR finding)"
                                                               if n == 11 else "")}
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
