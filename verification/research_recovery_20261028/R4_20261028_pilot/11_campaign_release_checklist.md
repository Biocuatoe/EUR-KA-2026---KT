# R4 H3: campaign release checklist

Every box must be ticked, in order, by the person releasing the campaign. The code enforces each item marked **(enforced)**; `run_campaign.py --execute` refuses otherwise. Nothing on this list has been done beyond step A, and the campaign has not started.

## A. Before approval (done in this task)

- [x] Frozen protocol SHA-256 `f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab` verified unchanged.
- [x] Final candidate `03_protocol_v1_amendment_1_rev2_CANDIDATE.md` written; status READY FOR OWNER APPROVAL; machine block parses with 0 errors and 0 open items (dry run).
- [x] Owner decisions recorded (`09_owner_decision_record.md`); tolerance evidence recorded (`10_tolerance_approval_register.md`).
- [x] Readiness tests pass (run 10, gate `logs/readiness_gate_v4.json`); dry run validates 170 unique official runs.
- [x] `R4_20261028_campaign/` created empty of outputs: plan, not-released gate record and manifest only.

## B. Owner approval

1. [ ] Review the candidate, 09, 10 and `12_independent_gate_status_rev2.md`.
2. [ ] Accept the review item "CR-A6 residual" (recomputation scope; candidate §9), or require further work.
3. [ ] Copy the reviewed candidate text to `R4_20261028_campaign/release/03_R4_protocol_v1_amendment_1.md` and set `"status": "APPROVED"` in its block. Change nothing else, or re-run section C. **(enforced: block must equal the implementation)**
4. [ ] Record that file's SHA-256.
5. [ ] Write `R4_20261028_campaign/release/amendment_1_approval.json` with `approved_by`, `date`, `amendment_sha256`, `accepted_review_items: ["CR-A6 residual"]` and `approved_tolerances` (exact set in 10, "Owner action"). **(enforced: `approval_problems`)**

## C. Release package (in `R4_20261028_campaign/`)

6. [ ] Copy `code/`, `config/` and `inputs/` from the pilot unchanged. Verify every hash against `../R4_20261028_pilot/logs/readiness_gate_v4.json` (`code_sha256`) and `zz_sha256_manifest_v3.csv`. Do not copy `outputs/`, `logs/` or `archive/`.
7. [ ] In the campaign directory: `python -I -B -m pytest -c code/pytest.ini --rootdir code --junitxml=logs/pytest_release.xml code/tests > logs/pytest_release.txt`. All must pass (the tests are written to run from either directory). On any failure, stop; do not edit and retry without a recorded amendment.
8. [ ] `python -I -B code/record_gate.py logs/pytest_release.xml`, which writes `logs/pre_run_hashes.txt` (protocol §10.1). **(enforced: `check_gate`)**
9. [ ] `python -I -B code/run_campaign.py --dry-run` in the campaign directory (release documentation, not a run). The schedule must pass. Its readiness-mode blocker "readiness gate record missing" applies only to the pilot and is expected there. The campaign-mode preconditions are the ones `--execute` checks.
10. [ ] Write `zz_sha256_manifest_release.csv` for the directory (self-excluding).

## D. Execution (the official campaign; not started)

11. [ ] `python -I -B code/run_campaign.py --execute` from `R4_20261028_campaign/` only. **(enforced: directory name, no smoke-test folder, no existing `outputs/campaign`)**
12. [ ] After completion: run `python -I -B code/recompute_from_traces.py outputs/campaign` in a separate process, and write the post-run manifest (the executor writes `zz_post_run_sha256.csv`).
13. [ ] Apply the protocol §9 consequences in the order of `campaign.NUMERICAL_CHECKS` (candidate §10). None may change a setting, profile, tolerance, controller, task or the run list.
14. [ ] Only then compute paired ΔE_abs and ΔE_rel, with trip time, for COMPARABLE conditions, and apply §8.1 mechanically. Report all denominators.

## Never

- Run official IDs from the pilot directory.
- Use S2 to tune or select anything.
- Re-run a failed run without an amendment stating cause and fix (§10.4).
- Compute an energy difference from a development test.
