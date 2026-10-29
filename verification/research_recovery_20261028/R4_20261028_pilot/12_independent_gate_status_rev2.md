# R4 H3: independent gate status, rev2 (after owner decisions)

**Date:** 2026-10-28, 07:35 (UTC+7). **Auditor:** AI assistant (reproducibility audit). It supersedes `08_gate_status_summary.md`, which is kept unchanged.

**Overall status: READY FOR OWNER APPROVAL.** Every methodological item is decided, implemented and tested. Every tolerance is justified. **The campaign stays blocked** until the owner approves and issues the amendment and the release steps of `11_campaign_release_checklist.md` are completed.

**Not done:**
- the campaign was not started, and campaign mode was never invoked;
- no energy difference between arms was computed;
- S2 was not used for tuning or anything else beyond its input hash.

## 1. Stop conditions

| # | Condition | Status | Evidence |
|---|---|---|---|
| 1 | Canonical S1/S2 sampled data with provenance and hashes | **MET** | `05_cycle_input_provenance.md`; hashes in candidate §8 |
| 2 | Amendment reviewed and explicitly approved | **NOT MET (owner action)** | candidate rev2 `42a7a9f51afae7c059373b9048ed9b09c6b87c975705e54c485f2f6bfc133369` is READY FOR OWNER APPROVAL: 0 reader errors, 0 open items. No issued file and no approval record exist |
| 3 | P3 comparison and infeasibility rules implemented and tested | **MET** | AMB-24 applied: dynamic §8.2 decides; QS failures recorded exactly as diagnostics. Tests in `test_checks.py`, `test_campaign.py` and `test_rev2.py` |
| 4 | Stop compliance independent of planner flags | **MET** | unchanged since rev1 (validator takes only knots; classification reads only evaluator and simulator flags) |
| 5 | Energy metrics recomputable with documented tolerances | **MET (values proposed for approval)** | `10_tolerance_approval_register.md`: trip time 1e-9 s, I_over 1e-6 A·s, RMSE 1e-9 relative, each justified analytically and by measurement. Separate-process recomputation, now with independently computed torque limits (R2-1, R2-2) |
| 6 | Grid, QS-versus-dynamic and 0.5 ms checks | **MET as redefined by the owner** | Release requires infrastructure readiness only (S1 and synthetic: DEV-2/3/4, R2-1/2). The S2 checks have predetermined consequences during the campaign (`campaign.NUMERICAL_CHECKS`; candidate §10); none is a release gate |
| 7 | Schedule, IDs, sensitivity design and S2 role validated without execution | **MET** | dry run `outputs/dry_run_20261028_073157`: 170 unique official IDs (12/12/12/6/128), 82 planner jobs, smoke IDs excluded. AMB-14 applied: nominal P1 gain for every draw |
| 8 | No unresolved critical review issue | **MET** | `config/code_review_status_v2.json`: 0 critical, 0 major. CR-A2 closed by AMB-24. CR-A6 remedies implemented; its residual scope is stated in candidate §9 and must be accepted in the approval record (enforced). These closures were not re-verified by the separate reviewer |
| 9 | No result selected or tuned to a legacy figure | **MET** | no outcome computed; no legacy figure in code, config or reports |

## 2. What changed in rev2

**Code changes.** The per-file record is `logs/zz_code_changes_rev1_to_rev2.csv` (9 changed, 4 added, 31 unchanged); rev1 is archived in `archive/rev1_20261028_0624/` (40 files, all matching manifest v2).

| Change | What |
|---|---|
| VC-09 | Independent torque limits in the evaluator: battery power limits inverted through the loss law (closed forms for M0/M2, bisection for M1), used for friction and the battery-limited fraction. Traced limits are compared as diagnostics |
| VC-10 | AMB-24 in `checks.classify_pair`. QS screen warnings record the exact failing pieces |
| VC-11 | AMB-14 in `sensitivity.gain_for_draw` (nominal P1 gain) |
| VC-12 | AMB-15 in `campaign`: campaign directory, issued-amendment and approval-record locations, approval-record requirements (`approval_problems`), the numerical-check plan, readiness gate v4, review status v2 |
| VC-13 | Release fix. Pilot-only paths (smoke test, drafts, candidate) are named explicitly, and tests assert the rule for the state they find, so the suite can run from the released copy |
| Tolerances | `evaluator.PROTOCOL_TOLERANCES`; I_over tightened from rev1's 1e-4 to 1e-6 A·s with a derivation |

**Torque-limit check, D.**

| Evidence | Result |
|---|---|
| Tests | 6 analytic boundary cases (below, at and above the battery boundary and the motor corner speed; standstill), regeneration and voltage-window cases, and inverse residuals for M2 and M1 |
| Agreement with `r3_lib` | 12 tests (3 motors × 2 limit sets × 2 plant states) on 4,005 points each |
| Sensitivity | a wrong R0 is detected |
| Independence | the evaluator ignores tampered traced limits |
| Full S1 runs | M0 1.4e-14 N·m; M1 9.7e-7 N·m (table resolution of `r3_lib`; diagnostic tolerance 1e-5 N·m). Both pass every check in-process and in a separate process |

**Shared assumptions.** These are documented in candidate §9: the model equations, parameter values, speed floor, nominal-Q limits, the M1 curve and its domain, and the integrated states. **This is not physical validation.**

**Tests.**

| Run | Result | Notes |
|---|---|---|
| 6 | 176 passed, 2 failed | The candidate file did not exist yet. The synthetic trace carried impossible zero torque limits, which the new check correctly flagged; fixed by giving the synthetic trace simulator-like limit channels |
| 7 | 178 passed | gate v3 |
| 8 | 179 passed | after the release fix |
| 9 | 179 passed | gate v4 (`logs/readiness_gate_v4.json`, binds the current code). See the correction in `logs/pytest_run9_INTERRUPTED_NOTE.txt` |
| 10 | 179 passed | on the same code |

All logs are kept.

**Development checks** (S1 and synthetic only; not campaign runs): `outputs/dev_rev2_20261028_071112/`, with R2-1, R2-2 and R2-3.

**Campaign directory.** `R4_20261028_campaign/` holds only `00_DIRECTORY_PLAN.md`, `GATE_RECORD_not_released.json` (status NOT RELEASED; 0 official outputs) and its manifest.

## 3. Remaining blockers (all owner or release actions)

1. The owner reviews and approves the candidate. The owner issues it as `R4_20261028_campaign/release/03_R4_protocol_v1_amendment_1.md` with `"status": "APPROVED"`.
2. The owner writes the approval record. It must accept "CR-A6 residual" and approve exactly the tolerances in register 10.
3. Release package, release test run and §10.1 gate in the campaign directory (checklist C).

## 4. Integrity

| Check | Result |
|---|---|
| Protocol SHA-256 | `f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab`, unchanged |
| Preflight directory | not written to (no file added, removed or edited); manifest 29/29 |
| Project files outside the pilot, before (06:47) vs after (07:36) | 24,914 → 24,917: **3 added, 0 removed, 0 changed**. The 3 are the new `R4_20261028_campaign/` files (plan, gate record, manifest). Record: `logs/zz_pre_post_comparison_v3.txt` |
| Evidence snapshot | 570/570 |
| Earlier logs, smoke traces, review reports and manifests | `zz_sha256_manifest_v2.csv`: 138 of 147 entries unchanged in place. The other 9 are the superseded code and test files; each archived copy in `archive/rev1_20261028_0624/` carries exactly its v2 hash. All test logs from runs 1–10, both review reports, the v1 and v2 manifests, and rev0 and rev1 of the amendment are unchanged |
| Git, installs, network, CNTT-02 | none used |
