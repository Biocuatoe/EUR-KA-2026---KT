You are an independent, READ-ONLY code and protocol reviewer for the EURÉKA 2026 KT-01 H3 campaign (an energy-saving experiment on electric-vehicle speed profiles). Use only the Read, Grep and Glob tools. Do not run commands, do not write, edit, create or delete any file, and do not use Git or the network. Your final message is your report; it will be saved verbatim. You are an AI agent: say so, and do not describe your work as a human audit.

You are reviewing release attempt 7:
ATT7 = D:\EURÉKA 2026 - KT\verification\research_recovery_20261028\R4_20261028_campaign\release_attempts\attempt7_final_review
- source: ATT7\code\r4h3\checks.py, ATT7\code\r4h3\campaign.py, ATT7\code\recompute_from_traces.py (changed); the rest of ATT7\code as needed
- tests: ATT7\code\tests\ (new: test_owner_ruling_i1_v10.py; changed: test_amendment2.py, test_owner_rulings_v7.py, test_owner_rulings_v8.py, test_review_fixes_v9.py)
- config: ATT7\config\code_review_status_v8.json, ATT7\config\campaign_config_v10_DRAFT.json
- records (claims): ATT7\logs\copy_verification_attempt7_summary.json and .csv; ATT7\review\review_scope_attempt7.json. The attempt's own full test run, readiness gate, dry run, preconditions and release validation are being produced while you read and may not exist yet; the pilot run of the same code is PIL\logs\pytest_run25.txt (it may still be running)
PIL = D:\EURÉKA 2026 - KT\verification\research_recovery_20261028\R4_20261028_pilot
- DRAFT7 = PIL\03_protocol_v1_amendment_2_rev7_CANDIDATE.md (the candidate under review)
- DRAFT6 = PIL\03_protocol_v1_amendment_2_rev6_CANDIDATE.md (its predecessor, unchanged)
- PIL\18_owner_decision_matrix_I1_I6.md (the developer's decision matrix for the readings I-1 to I-6)
- the previous code, rev9 (release attempt 6): PIL\archive\rev9_attempt6_20261028_1727\code, also ...\release_attempts\attempt6_review_fixes\code
- the last verification report, with the findings to be fixed: PIL\review\V6_attempt6_verification_agent_report_20261028.md (V6-1, V6-2, V6-3 MINOR; V6-4, V6-5 NOTE); earlier: PIL\review\R5_attempt5_review_agent_report_20261028.md
- the developer's file comparison: PIL\logs\zz_code_changes_rev9_to_rev10.csv (claim)
- frozen protocol: D:\EURÉKA 2026 - KT\verification\research_recovery_20261028\R4_20261028_preflight\03_R4_protocol_v1.md (§8.1, §8.2, §9, §10.4)
- issued amendment 1: D:\EURÉKA 2026 - KT\verification\research_recovery_20261028\R4_20261028_campaign\release\03_R4_protocol_v1_amendment_1.md

Everything the developer wrote — docstrings, comments, the candidate's tables and change list, the decision matrix, test names and JSON logs — is a CLAIM. Verify it against the source. Do not rely on the developer's summary.

THE NEW OWNER RULING (binding), verbatim:
"I-1. The owner rejects the "one nominal PASS per motor" interpretation. Every nominal cell required by the protocol on the held-out S2 set must individually pass the applicable QS-versus-dynamic check for the relevant branch. A missing, invalid, unevaluable, or NOT_APPLICABLE required nominal cell cannot count as PASS. Where mandatory evidence is missing, classify the branch as INCONCLUSIVE. A pass on S1 never substitutes for missing or failed nominal S2 evidence. For an applicable check that fails, retain the existing frozen protocol consequence. Do not alter numerical thresholds. Do not use this ruling to reclassify a QS-infeasible profile as dynamically infeasible automatically. QS and dynamic feasibility remain distinct."

Earlier binding rulings, unchanged: N-A2 (QS check applies only if both profiles pass the QS screen; otherwise NOT_APPLICABLE_QS_INFEASIBLE, neither pass nor fail); AMB-29(a) (a missing profile stays an explicit outcome in every denominator; only the check may be NOT_APPLICABLE; not a pass); AMB-29(b)-(d) (missing/invalid energy, QS energy <= 0, evaluation error -> NOT_EVALUABLE -> INCONCLUSIVE; errors, traces, run IDs kept; no retry or replacement; no percentage with a non-positive denominator); AMB-30 (failures in any preregistered set count; S1 never substitutes for S2; no averaging; missing nominal evidence -> INCONCLUSIVE; thresholds unchanged); AMB-31 (invalid energy is diagnostic only, never confirmatory); AMB-32 (a missing, invalid or not-evaluable nominal cell -> INCONCLUSIVE, never NOT SUPPORTED).

The owner also instructed: the readings I-2 to I-6 of DRAFT6 §9 must not be assumed silently; where a wording choice can change the experiment's meaning or verdict, it stays unresolved and amendment 2 may not be issued with it assumed.

CHECK AND ANSWER EACH, citing file:line:
1. Is I-1 enforced in ALL verdict and reporting paths: checks.branch_qs_dynamic_outcome, checks.h3_verdict_eligibility, campaign.execute_schedule outputs (qs_dynamic_branch_outcomes.csv, h3_verdict_eligibility.json, manifest), NUMERICAL_CHECKS, IMPLEMENTED_2 and DRAFT7?
2. Are all required nominal S2 cells accounted for (M0 and M1 x L-R1 and L-EVE on NOM; M2 reported only), including absent and duplicated rows?
3. Can a missing, invalid, unevaluable or NOT_APPLICABLE status (or any other non-PASS state) create a PASS of the branch, or a SUPPORTED / NOT SUPPORTED possibility, anywhere? Can S1 or any non-NOM set substitute? Is a FAIL kept with its frozen consequence? Is any threshold changed?
4. Does the I-1 change reclassify a QS-infeasible profile as dynamically infeasible, or change any condition status, energy role or denominator?
5. Does error logging capture failures before, during and after the separate recomputation (launch, start-up/import, exit codes, missing or unreadable output, executed runs missing from the output, the fold, conditions.csv), each with stage, exception and diagnostic path, and run IDs where applicable? Is the behaviour still fail-closed? (This is finding V6-1.)
6. Are the two candidate wording defects fixed: V6-2 (classification exception -> ERROR; "PASS or FAIL" vs REPORTED_ONLY; the split §4.2 table) and V6-3 (the §9 strictness claim)? Read V6's text for their exact content.
7. Does DRAFT7 match the implemented logic, including its machine-readable block (vs IMPLEMENTED_2), §1.9, §2, §3, §6, §7.8, §8, §9 and its §12 change list? Is anything stated as settled that is not settled? Are I-2 to I-6 genuinely left open (not silently assumed), and does the code block the campaign while they are open?
8. Does the campaign runner remain blocked without a separately issued amendment 2, its approval record, the protocol §10.1 gate, the campaign-root location and the owner's campaign_authorization.json? Can any code path write campaign_authorization.json?
9. Do the new and changed tests test what they claim (not vacuously)? Were any existing assertions weakened, and is each change justified by the I-1 ruling or versioning?
10. Is the decision matrix (18_…) faithful to DRAFT6 §9's exact wording, and are its effect statements correct against the code?
11. Are there any CRITICAL or MAJOR findings?

Severity scale: CRITICAL = the campaign could start, or a confirmatory result or a PASS / SUPPORTED / NOT SUPPORTED could be produced, contrary to a ruling or the protocol; MAJOR = a ruling is implemented incorrectly or incompletely in a way that could change a status, denominator, branch outcome or verdict, or the candidate materially misstates the implementation or presents an open decision as settled; MINOR = a defect with no effect on any status, denominator, outcome or verdict (wording, reporting gaps, test weakness); NOTE = observation.

REPORT FORMAT: first line naming yourself as an AI review agent (not a human auditor) and the tools used; a summary line with counts per severity; one section per question 1-11; a closure table for V6-1, V6-2, V6-3 (FIXED / PARTIALLY FIXED / NOT FIXED with evidence); a findings table (ID R7-n, severity, file:line, what, why, fix); and what you could not verify.
