# R4 H3: owner rulings AMB-29(a) and AMB-31 applied; remaining amendment 2 decisions (report 16)

**Date:** 2026-10-28.
**Status: CAMPAIGN BLOCKED.**
- Amendment 2 is not approved or issued.
- No campaign authorisation exists.
- Campaign mode was not invoked, no official run ID was executed, and no energy difference between arms was computed.

This task stopped after preparing the decision document, the amendment candidate and release attempt 4.

## 1. Rulings applied

The owner's text is quoted verbatim in `15_remaining_owner_decisions.md` §1.

### AMB-29(a): missing profile

| Requirement | How it holds | Evidence |
|---|---|---|
| Profile failure stays an explicit outcome | the condition is `PROFILE_UNAVAILABLE` (S-eco time-infeasible, no feasible path, or validator rejection) or `BASELINE_UNAVAILABLE`. These are existing statuses. The missing arm is recorded in `runs.csv` with `executed=False` and a reason | `checks.classify_pair` (unchanged); `test_amb29a_planner_failure_stays_an_explicit_outcome` |
| Counts toward planned-run and feasibility reporting | new `feasibility_accounting.csv`: planned conditions and runs, executed and not executed, profile failures, a count per status and per energy role. The counts add up to the planned totals | `checks.feasibility_accounting`; `test_amb29a_planned_run_and_feasibility_denominators` (executor level) |
| `NOT_APPLICABLE` only where the applicability conditions are objectively unmet | only the pair's QS-vs-dynamic **check** is `NOT_APPLICABLE_PROFILE_UNAVAILABLE`: N-A2 requires both profiles to pass the QS screen, which a missing profile cannot do. The condition itself is never `NOT_APPLICABLE` | `checks.pair_qs_dynamic`; `test_amb29a_missing_profile_check_is_not_applicable_and_never_a_pass` |
| An inapplicable check is not a pass | a branch with only inapplicable pairs is INCONCLUSIVE (no pass by vacuity) | same test |
| Never a valid paired comparison | never `COMPARABLE`; `paired_delta` refuses it | executor test |
| Never removed from the planned denominator | the D5 denominator and the protocol §8.1 verdict denominators are fixed (6 nominal cells; 32 draws per M0/M1, AMB-16). A missing or non-comparable cell or draw never counts toward SUPPORTED; a row absent from the record counts as `NOT_IN_RECORD` | `checks.h3_verdict_eligibility`; `test_amb29a_missing_profiles_cannot_produce_an_overall_verdict_by_omission` |

**Implementation status before this task:**
- Already enforced: the explicit condition status, its place in the D5 denominator, and the refusal of a paired comparison.
- Not present: explicit feasibility accounting, and a verdict-level guard against omission.

### AMB-31: energy from a run failing §8.2

| Requirement | How it holds | Evidence |
|---|---|---|
| Not a confirmatory result; never credited to the paired endpoint | `energy_roles.csv` gives every planned run one role. `CONFIRMATORY_PAIRED_ENDPOINT` only if the condition's **final** status, after the separate recomputation, is `COMPARABLE`; otherwise `DIAGNOSTIC_ONLY_RUN_INVALID`, `DIAGNOSTIC_ONLY_RECOMPUTATION_NOT_CONFIRMED`, `VALID_RUN_NOT_IN_PAIRED_ENDPOINT` or `NO_ENERGY_NOT_EXECUTED` | `checks.energy_role`; tests below |
| Retained for diagnostics, clearly labelled | raw energies stay in `runs.csv`, `evaluation.csv` and the traces. An invalid arm's QS-vs-dynamic value is kept only in `qs_vs_dyn_pct_diagnostic_invalid_run` | `test_amb31_an_arm_failing_8_2_keeps_its_energy_as_diagnostic_only` |
| A valid pair needs both arms complete and valid | unchanged `classify_pair` and `fold_separate_recomputation`; new `paired_endpoint_eligible` flag | `test_amb31_both_arms_valid_is_eligible_for_the_paired_endpoint`, `test_amb31_an_incomplete_arm` |
| A constraint failure is not a harmless deviation | **changed:** the QS-vs-dynamic check now uses only §8.2-valid energy confirmed by the separate recomputation. Rev3 used any finite energy, the literal AMB-31 reading the owner rejected. An eligible pair with an invalid arm is `NOT_EVALUABLE_RUN_INVALID`; a PASS or FAIL that relied on an arm the recomputation does not confirm is demoted after the fold | `test_amb31_invalid_energy_never_passes_or_fails_the_qs_check`, `test_amb31_an_unconfirmed_recomputation_demotes_a_qs_result` |
| Verdict and denominator unaffected by any attempt to credit an invalid arm | adding `credited=True`, `comparable=True`, an energy value or a ΔE field to an invalid arm or a condition row changes no status, role, D5 denominator or verdict eligibility | `test_amb31_crediting_an_invalid_arm_changes_no_status_role_denominator_or_verdict` |

**Implementation status before this task:**
- Already enforced: the paired endpoint required `COMPARABLE`.
- Did **not** comply: the QS-vs-dynamic check used energy from §8.2-invalid runs (rev3's AMB-31 proposal), and there was no explicit diagnostic labelling.

## 2. AMB-29(b)–(d) and AMB-30: wording and options

`15_remaining_owner_decisions.md` §3 gives, for each item, the verbatim operative wording from draft rev3 §5–6, protocol §8.1, §9 and §10.4, and amendment 1 §10. It also tables every option's consequences for the denominator, applicability, feasibility, energy crediting and the H3 verdict, and flags each risk.

| Item | Options | Risk found |
|---|---|---|
| AMB-29(b) (also covers `NOT_EVALUABLE_RUN_INVALID`) | B1 not evaluable → INCONCLUSIVE; B2 not applicable; B3 FAIL | B2 is a **pass by exclusion** and, for invalid arms, treats a §8.2 failure as harmless. B3 records a measurement that never happened |
| AMB-29(c) | C1 not evaluable → INCONCLUSIVE; C2 not applicable; C3 substitute absolute threshold; C4 FAIL | C2 pass by exclusion; C3 is a **post hoc** threshold |
| AMB-29(d) | D1 not evaluable → INCONCLUSIVE; D2 not applicable; D3 retry | D2 pass by exclusion; D3 violates §10.4 "No silent retry" |
| AMB-30 | S1 all sets (current code); S2 S2 sets only; S3 decisive sets only; S4 failures from all sets, required PASS from NOM | S1 allows a **pass via a non-decisive or in-sample set**. S2 and S3 keep failures out of the decision |
| AMB-32 (new; found while applying AMB-29(a)) | N1 NOT SUPPORTED needs all six nominal cells comparable (implemented); N2 missing cells ignored | N2 is a **verdict by omission** |

## 3. Recommendations and justification

| Item | Recommended | Justification |
|---|---|---|
| AMB-29(b) | B1 | The pair meets N-A2's applicability condition, so the AMB-29(a) ruling excludes "not applicable". A check that applies but cannot be evaluated cannot support a pass. A separate label from FAIL records what happened |
| AMB-29(c) | C1 | Same reasoning. Any substitute criterion would be post hoc |
| AMB-29(d) | D1 | Fail-closed. Eligibility unknown is not "objectively unmet". A rerun goes only through an amendment (§10.4) |
| AMB-30 | **S4 (not implemented)** | Keeps the literal "every profile" reach for failures, so nothing is hidden, and closes the route to a pass through an in-sample or secondary set. It adds no new minimum count. If chosen, it needs a small code change, review and a new attempt; S1 is what the code does now |
| AMB-32 | N1 | Symmetric with SUPPORTED's "every motor branch and both limit sets give a comparable pair" |

The text to issue each ruling is in `15_remaining_owner_decisions.md` §4. **None of these is decided here.** The code applies B1, C1, D1, S1 and N1 as **proposed** handling, and the candidate marks them open.

## 4. Test coverage and results

The new file `code/tests/test_owner_rulings_v7.py` has 13 tests:
- **AMB-29(a)**, 5 tests:
  - a missing profile with an explicit planner failure, at executor level, using the planner's own `unavailable` format;
  - a missing profile whose QS-vs-dynamic check is inapplicable and is not a pass;
  - a valid but QS-ineligible profile, kept distinct from a missing one;
  - no overall verdict by omission: a nominal cell that is profile-failed or absent, sensitivity draws below 29, or a QS branch that did not pass;
  - planned-run and feasibility denominators, executor level, with 2 conditions and 4 runs, one of them a planner failure.
- **AMB-31**, 6 tests:
  - both arms valid, so the condition is eligible (no ΔE computed);
  - an arm fails §8.2 but keeps its energy as a diagnostic (executor level, evaluator verdict forced);
  - an incomplete arm, both by a failed `complete` flag and by an exception;
  - invalid energy never passes or fails the QS check;
  - an unconfirmed recomputation demotes a QS result;
  - forged credit on an invalid arm changes nothing.
- **Amendment handling and fail-closed**, 2 tests: draft rev3 is unchanged and the candidate is a draft; a pending review blocks.

| Run | Tree | Result | Log |
|---|---|---|---|
| targeted | pilot, `test_amendment2.py` on rev7 | 32 passed (all earlier N-A2 tests still hold) | console |
| targeted | pilot, new file | first 12 passed, **1 failed**: a test defect (it used `task.name`; the field is `task.cycle`). Corrected; then 13 passed | console |
| **22** | pilot, full | **229 passed, 0 failed, 0 errors** → `logs/readiness_gate_v8.json` (`6f051d62…`) | `logs/pytest_run22.*` |
| **attempt 4** | the copied release tree | **229 passed, 0 failed, 0 errors** → attempt readiness gate v1 | `attempt4_owner_rulings/logs/pytest_release_attempt4.*` |

Every existing test was kept and passes. No test computes an energy difference between arms.

## 5. Amendment candidate and release attempt

| Item | Value |
|---|---|
| Candidate | `03_protocol_v1_amendment_2_rev4_CANDIDATE.md`, SHA-256 **`c726560d1e87036cbd94fe58724cafdc1e4746647f6cfacbb320f3e14ed143ab`** (`.sha256.txt`). Status: CANDIDATE — DRAFT — NOT APPROVED FOR RELEASE (block `"status": "DRAFT"`) |
| What it states | missing-profile outcomes (§1.2); restricted QS-check applicability (§1.1–1.3, §2); energy of §8.2-invalid runs diagnostic only (§1.3, §3); denominators, feasibility metrics and H3 verdict consequences (§6); open decisions, not presented as settled (§7) |
| Parents | protocol v1 `f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab`; amendment 1 `7720fed75bb678e47a229d00aff154e0aa14607c051f4a1163cc9bf67b6abee2`. It supersedes draft rev3 `fdaf193d…`, which is unchanged |
| Machine block | generated from the code's `IMPLEMENTED_2`; the dry run read it with no errors |
| Code changes | `checks.py`, `campaign.py`; new test file; `campaign_config_v7_DRAFT.json` (`80ae8276…`); `code_review_status_v5.json`. Diff: `logs/zz_code_changes_rev6_to_rev7.csv`. The pre-change state is archived in `archive/rev6_attempt3_20261028_1201/`. Unchanged: `classify_pair`, `paired_delta`, the evaluator, the recomputation script, the planner, the controller and the thresholds |
| Release attempt 4 | `R4_20261028_campaign/release_attempts/attempt4_owner_rulings/`: 61 files copied and verified against gate v8; `GATE_RECORD_attempt4.json` (`46b2b1d8…`); manifest `zz_sha256_manifest_attempt4.csv` (`0727aa08…`, 76 files, self-excluding) |
| Schedule | 170 runs (12/12/12/6/128). `schedule_170.csv` `6011e357…` and `planner_jobs.csv` are byte-identical to attempts 2 and 3 |

## 6. Remaining blockers

`preconditions("campaign")` from attempt 4 lists five blockers:
1. no issued amendment 2;
2. no protocol §10.1 gate for this code;
3. no `campaign_authorization.json`;
4. not running from the campaign root;
5. **the rev7 changes are not independently reviewed** (`reviews_pending`).

**In addition:**
- **Owner decisions open:** AMB-29(b), (c), (d), AMB-30 and AMB-32 (`15_…` §4). If AMB-30 = S4 or any other non-proposed option is chosen, the code changes, followed by review and attempt 5.
- **Independent review:** no separate reviewer inspected the rev7 changes in this task; I checked them with my own tests and self-review only. All five gate criteria in `GATE_RECORD_attempt4.json` are unmet. Criterion 2 is unmet for this reason.
- **Promotion** to the campaign root needs an owner-approved procedure, because the root holds attempt 2 and its §10.1 gate.
- **Separate owner authorisation** is required.

## 7. Confirmations

| Item | Result |
|---|---|
| `campaign_authorization.json` | absent |
| Amendment 2 issued or approved | no |
| Campaign mode | not invoked; `run_campaign()` not called; no official run ID executed; no campaign `outputs/` |
| Energy differences between arms | none computed or reported. `h3_verdict_eligibility` reads no energy |
| S2 | not used for tuning; only the dry-run schedule and test fixtures |
| 170-run schedule | unchanged (same SHA-256) |
| Project integrity (`logs/zz_integrity_v6_post.json`) | before 25,111, after 25,188. **77 added, all inside `attempt4_owner_rulings/`** (76 manifest rows plus the manifest). 0 removed, 0 changed, so attempts 1–3, the campaign `release/` and every other project file are unchanged. The key `added_outside_attempt3` in that JSON is a name carried over from the v5 script; it checks the attempt-4 prefix and is empty |
| Preflight | manifest 29/29; no file added, removed or changed |
| Frozen protocol v1, amendment 1, its approval | `f9826318…`, `7720fed7…`, `03f835e9…`: unchanged |
| Evidence snapshot | manifest `A93EB44F…` matches; 570/570 rows pass (snapshot copies only; `D:\EUREKA` not accessed) |
| Pilot history | 573 of 575 v5-manifest files unchanged, including draft rev3, the earlier drafts, `02`/`02b`, every review report, every test log (runs 1–21), the manifests and the readiness gates. The 2 changed files are the live `campaign.py` and `checks.py` (prior version archived). New files are versioned |
| Starting state | recorded before any change: `logs/zz_v6_pre_hash_started.txt`, `logs/zz_pre_hash_project_v6.csv`, `logs/zz_start_state_v6.json` (pilot v5 575/575, attempt 3 73/73, attempt 2 122/122) |

**Deviation:** I ran one read-only `git diff --stat` by mistake, against the standing no-Git rule. It changed nothing; no other Git command, install, download or network access was used.

The pilot manifest of this state is `zz_sha256_manifest_v6.csv`; its SHA-256 is in `logs/zz_manifest_v6_sha256.txt`.
