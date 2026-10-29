# Independent read-only re-review of CR-A2 and CR-A6: final report (verbatim)

**Provenance.**
- **Who:** a separate AI review agent (the "Plan" agent type, with no Edit/Write tools), started on 2026-10-28 at about 07:48 local time.
- **Instructions:** use only Read, Grep and Glob; run nothing and write nothing.
- **What it reviewed:** the current source, the tests and the archived code states. A test run (run 11) was in progress while it worked, and the VC-14 change (campaign authorisation) had been made just before it started.
- **Format:** the text below is its final message. The only edit is removing the uniform indentation that the message relay adds. File references are relative to the pilot directory.
- **Author's responses** are in `../13_owner_approval_and_release_report.md`.

---

Independent re-review of CR-A2 and CR-A6

**Bottom line**
- **CR-A2 is CLOSED** in the campaign code path. The P3 regression evidence is incomplete: no test runs a profile that fails the QS screen but passes §8.2 dynamically.
- **CR-A6 is CLOSED only as "mitigated, with the residual accepted"** (AMB decision in force). Two remedy items were not done literally: an independent spec file, and crediting decided by the separate script. Some document wording is stale or slightly overstated.
- I found no CRITICAL or MAJOR issue. The new findings below are MINOR or NOTE.

Method: Read, Grep and Glob only. I ran nothing.

---

## CR-A2

**Original finding (MAJOR):** "QS feasibility on the P3 plant decides the outcome before §8.2." `slice.py` stopped before the dynamic run, and `checks.py:104-110` classified P3 conditions from QS flags ahead of the §8.2 flags.

**Where it is fixed (current code)**
- `code/r4h3/checks.py:22-26` – `P3_RULE = "dynamic_8_2_decides; QS screen diagnostic only"`.
- `checks.py:30-39` – `qs_energy` records the exact failing pieces (index, t0, t1, v0, v1).
- `checks.py:96-106` – `arm_comparable` and `failed_criteria` read only evaluator and simulator §8.2 flags.
- `checks.py:109-127` – `classify_pair` has no QS argument. Its order: availability → ERROR → B0 §8.2 → B3 §8.2 → recomputation → COMPARABLE.
- `checks.py:130-136` – `paired_delta` raises unless the status is COMPARABLE.
- `code/r4h3/campaign.py:530-542` – `plan_design` validates only on the P1 design plant. `baseline_ok` depends only on v_b existing.
- `campaign.py:611-667` – `run_condition`:
  - The QS screen on the evaluated plant (621-623) is computed but only recorded.
  - Both arms run whenever `ok[b]` is true; `ok` comes from the P1 design (620, 625-651).
  - The status comes from `classify_pair` (652).
  - The exact pieces go to `b*_qs_screen_warning` and the §8.2 failures to `b*_failed_8_2` (654-663).
- `run_condition` is the same in rev2 (`archive/rev2_20261028_0744/code/r4h3/campaign.py:568-624`); VC-14 did not touch it.

**Answers**

**Q1 – Can a QS result change a P3 status or block a run?** No. `classify_pair` has no QS input, and its only caller is `campaign.py:652`; the tests also call it. No branch of `run_condition` reads `qs_feasible`. The only other QS gate is the validator on the P1 design plant (`campaign.py:538,541`), which follows D1/D3 and is not a P3 screen. Failures are recorded exactly, with the piece index, times and speeds.

**Q2 – Are both arms always run, and are failures kept?**
- Both arms run whenever their profile exists, including when the P3 QS screen fails.
- Arms that were not executed or that raised get `runs.csv` rows (`campaign.py:628-631, 647-651`).
- Non-finite runs keep their raw trace (`campaign.py:584-593`).
- `denominator()` counts every status (`campaign.py:756`).
- Caveat: see N-A5.

**Q3 – Any path to a paired ΔE for a non-COMPARABLE condition?** No. `paired_delta` is not called anywhere in the executor, and it refuses non-COMPARABLE statuses. The ordering matches §8.1 and AMB-24 for the main cases. Details are in N-A3 and N-A4.

**Q4 – Do the tests exercise P3 on real executor paths?** Only partly (N-A1).
- `test_campaign.py::test_p3_profile_infeasible_on_the_evaluated_plant_is_run_and_classified` runs the real `run_condition`. But with `T_max=2` both the QS screen and the dynamic §8.2 checks fail, so the test cannot tell the two rules apart.
- The only "QS fails, not labelled infeasible" test uses a synthetic dict (`test_checks.py::test_amb24_qs_screen_is_not_an_input_to_the_feasibility_verdict`), and its assertion holds trivially.

**Q5 – Any critical correctness issue?** None found.

**Regression tests:**
- `test_checks.py::test_classification[kwargs0..11]`, `::test_amb24_qs_screen_is_not_an_input_to_the_feasibility_verdict`, `::test_qs_screen_records_the_exact_failing_pieces`, `::test_paired_delta_only_for_comparable_conditions`, `::test_classification_ignores_any_planner_flag`.
- `test_checks.py::test_denominator_keeps_every_status`: in the current file; not among the names I searched for in the run-10 XML.
- `test_campaign.py::test_p3_profile_infeasible_on_the_evaluated_plant_is_run_and_classified`, `::test_classification_is_reproduced_from_the_written_rows`, `::test_time_infeasible_profile_is_unavailable_and_b0_still_runs`, `::test_an_exception_is_recorded_not_retried`.

**Logs:**
- `logs/pytest_run10.xml` (2026-10-28T07:26) lists these test names: tests=179, failures=0, errors=0.
- `logs/pytest_run11.txt` says "181 passed" but has no XML, so I could not verify which tests or which code version it covered.
- I did not verify that run 10's code hash equals the current code. The CR-A2-relevant code is the same in rev2 and current, by direct comparison of `run_condition` and of the `checks.py` lines I searched in both.

**Verdict: CLOSED** for the campaign path. Test evidence for the discriminating P3 case is missing (N-A1).

**New findings**
- **N-A1 MINOR (test gap).** No executor-level test of a profile that fails the QS screen on P3 but passes §8.2. If someone re-added a QS gate in `run_condition`, for example by skipping arms when `qs_feasible` is False, the current tests would not catch it. This scenario is realistic at P3: R0 is about 1.7×, so the drive limit is lower, while closed-loop RMSE ≤ 0.10 m/s tolerates brief saturation.
- **N-A2 MINOR (AMB-24 vs §9 check 7, not addressed).** `campaign.py:637-640` computes the protocol-9 QS-vs-dynamic check for P3 runs from `qs_energy` on the P3 plant, even when the screen failed.
  - `r3_lib.QSPlant.point` (`r3_lib.py:298-311`) still returns a finite energy for unclipped, over-limit drive torque.
  - So a QS-screen failure can produce `qs_vs_dyn_status = "FAIL (branch INCONCLUSIVE, protocol 9)"` for M0/M1. Under §8.1 ("Every check in §9 passes") that could turn the H3 verdict INCONCLUSIVE.
  - No aggregator applies this in code yet. Neither the row nor the amendment says whether QS-vs-dynamic is decisive on profiles that fail the screen. Candidate §5 is titled "QS checks are diagnostic", while §10 check 7 says a failure makes the branch INCONCLUSIVE. This needs an owner ruling or an explicit statement.
- **N-A3 NOTE (ordering).** `checks.py:119-126` checks ERROR before the B0 §8.2 failure, and puts §8.2 failures before RECOMPUTATION_DISAGREEMENT.
  - If B0 fails §8.2 and B3 raised, the status is ERROR, not B0_INVALID_EXCLUDED as §8.1 would have it.
  - If the evaluator and simulator disagree on a deciding flag (for example `constraint_ok` near 0.01 A·s), the condition gets the formal `ECO_INFEASIBLE_ON_P3` or `INVALID_COMPARISON` rather than RECOMPUTATION_DISAGREEMENT.
  - Neither path can produce a ΔE. The order is what candidate §5's table says, so it is a NOTE for the owner.
- **N-A4 NOTE.** When both arms fail on P3, the status is BASELINE_INFEASIBLE_ON_P3 only. B3's infeasibility appears only in `b3_failed_8_2`, so the ECO_INFEASIBLE_ON_P3 count understates eco-arm failures.
- **N-A5 MINOR (accounting).** Exceptions outside `run_arm`'s try block abort `execute_schedule` before `runs.csv`, `errors.csv` and `manifest.json` are written; only per-condition JSON survives. This covers `plan_design`/planner (`campaign.py:706`), `checks.qs_energy` (621), `task_loader` and `sensitivity`. Those writes happen only at lines 742-762. Low likelihood; this is CR-A4/A5 territory.
- **N-A6 NOTE (residual old logic in a development path).** `slice.py:141,150,160,165-167` still validates both trajectories on the *evaluated* plant and stops before any dynamic run. `run_slice.py:21` accepts `--pstate P3`. This is smoke-test only, outside the campaign, but it is the original CR-A2 defect.
- **N-A7 NOTE (stale text).**
  - `test_campaign.py:264` docstring still says "under the QS rule the condition is infeasible".
  - `02_protocol_ambiguity_register.md:41` still lists AMB-24 as OPEN ("classify_pair refuses P3").
  - `04_independent_code_review.md:44` describes the rev1 two-rule implementation.

---

## CR-A6

**Original finding (MAJOR):** "the evaluator does not meet protocol §9's 'separate script reading only the saved traces'." It shared formulas and parameter objects, read r3_lib channels (`t_neg`, `t_pos`, `P_fric`, `P_regen_wheel`, `v_tracked`), and computed I_over and min V_t only once.

**Where it is fixed**
- `code/r4h3/evaluator.py:1-24` – scope docstring.
- `evaluator.py:86-144` – `battery_power_limits`, `mech_power_limits`, `torque_limits`.
- `evaluator.py:167-176` – its own limits drive the battery-limited fraction.
- `evaluator.py:179-189` – friction uses its own `t_neg`.
- `evaluator.py:197-199` – tracked-knots check.
- `evaluator.py:284-345` – protocol and diagnostic groups; `PROTOCOL_TOLERANCES`.
- `closedloop.py:147-157` – simulator-side C-rate I_over and min V_t from the traced r3_lib current.
- `campaign.py:509-519, 575-583` – per-run `spec.json`, whose hash becomes the meta `config_sha256`.
- `code/recompute_from_traces.py:23-25, 60-62` – separate process with an import-leak check.

**Q6 – Formulas compared term by term with `r3_lib.torque_limits` (`r3_lib.py:111-119`), `rebuild.model.battery_limits` (`model.py:44-62`) and `MotorModel.pm_*` (`r3_lib.py:78-95`).** The evaluator does not import `r3_lib`, `rebuild` or `eureka`; it imports only json, Path and numpy.

| Term | Result |
|---|---|
| Speed floor | `max(w, 1e-6)` on both sides; also inside the copper `a`. Same |
| Base limit | `min(T_max, P_max/w_pos)`. Same |
| Discharge current | `i_v`, `i_d = min(c_dis·Q, i_v, vo/2R0)`, `p_d = (vo − R0·i_d)·i_d`. Same |
| Charge current | `i_c = min(c_ch·Q, max((v_max − vo)/R0, 0))`, `p_c = (vo + R0·i_c)·i_c`. Same for finite `v_max` (H3: 1.140625) |
| C-rate basis | Nominal Q: both limit sets have `soh_scaled=False`. The evaluator ignores `soh_scaled` and `lim.active` (r3 returns base when inactive). Both limit sets in H3 are active and unscaled, so there is no effect. It would diverge only for an inactive or SoH-scaled set |
| M2 inverse | Rationalised but algebraically identical closed forms, with INF where disc < 0. r3 clamps `pe ≥ 0` and the evaluator does not; this matters only if `vo < 0`, which is non-physical |
| M0 inverse | r3 inverts through the 3001-point table with `right=INF` beyond 1.5·p_rated (about 30.9 kW drive / 23.6 kW regen at η 0.874). The evaluator's closed form is unbounded. No effect: P_max = 18 kW (`configs/parameters.yaml:134-136`) < 27 kW, so both sides return base there. Drawn η 0.83–0.918 does not change this |
| M1 inverse | Bisection on `[0, 1.5·p_rated]`, INF where target > f(hi) (same convention as r3 `right=INF`). Same clamped `np.interp` of η. The curve is monotone (`test_copper_and_curve_inverses_satisfy_the_forward_law`) |

- Discrepancies that could matter: none in the H3 configuration.

**Q7 – Own limits used, and which traced channels are still read.**
- The evaluator's own `t_neg`/`t_pos` are used for friction and the battery-limited fraction (`evaluator.py:168, 173-174, 187-189`).
- `test_rev2.py::test_evaluator_uses_its_own_limits_not_the_traced_ones` confirms that tampering with the traced limits leaves both unchanged.
- r3-derived channels still read:
  - The states `v_mps`, `T_Nm`, `V1_V`. All credit-deciding quantities depend on them: E_chem, E_DC, distance/shortfall, stop, I_over, min V_t.
  - `v_tracked_mps`, used for RMSE and max|e|, which decide `tracking_ok`.
  - `u_cmd_Nm`, used for friction and the battery-limited fraction (not credit-deciding).
  - `limit_active`, a reported fraction.
- Comparison-only channels: `i_A`, `w_radps`, `P_fric_W`, `P_regen_wheel_W`, `t_pos_Nm`, `t_neg_Nm`, `int_*`.
- The own-vs-trace `v_tracked` check (`tracked_profile_abs_ms`) is a non-gating diagnostic, so `tracking_ok` rests on a simulator channel. The knots for the spec and for the profile come from the same in-process variable (`campaign.py:561, 575`), so an upstream wrong-profile error would be shared anyway.

**Q8 – Is the limit comparison non-gating, and are the tolerances reasonable?**
- Yes, it is non-gating: `torque_limit_*` is not in `PROTOCOL_CHECKS` (`evaluator.py:342-343`), and `protocol_ok` uses only that set (334).
- `TORQUE_LIMIT_TOL`: 1e-9 N·m for M0/M2 (closed forms on both sides) and 1e-5 N·m for M1 (measured table error 9.7e-7). Both are reasonable and documented in `evaluator.py:89-93` and the `10_` register.
- The friction bound (`1e-6 Wh + gr·dneg·d/3600`) and the battery-limited bound (ambiguous fraction) are dimensionally correct. They scale with the measured limit difference, so they cannot detect a limit error on their own; only the torque-limit diagnostic carries that signal. That is acceptable for diagnostics.
- The comment's "240 000 operating points" was not verified: the tests use 12 × 4,005 points.

**Q9 – Overclaims and owner wording**
- I found no claim of physical validation. Candidate §9 (line 156) says "does not validate the plant dynamics or the parameter values". `12_…:49` says "This is not physical validation". `09_…:19` says "without claiming physical validation". The evaluator docstring (lines 8-9, 23) says the same.
- Overstatements found:
  - (a) `evaluator.py:39` section header "formulas from the protocol text", and `01_implementation_and_test_report.md:35` "formulas from the protocol text". This is the exact wording CR-A6 objected to; the protocol has no such equations.
  - (b) Candidate §9 line 156 says the recomputation "verifies … the torque-limit calculation", although that check is non-gating.
  - (c) `code_review_status_v2.json` "closed_since_v1" says "all remedies the reviewer named are implemented". The reviewer's "frozen spec file written from the protocol and ledger" was not done: `eval_spec` is built from the same in-process `Params`/`BatteryLimits` objects (`campaign.py:509-516`).
- The candidate §9 list of shared assumptions (equations, parameters, 1e-6 floor, nominal-Q, M1 curve and domain, states) matches the owner's limitation in substance.
- I_over 1e-6 A·s:
  - Register T2 says it is "set by decision relevance rather than by error size", "10⁻⁴ of the §8.2 decision threshold", and "Affects implementation validity".
  - Candidate line 134 matches, and line 138 says "not task-feasibility or outcome criteria".
  - It is never described as a physical uncertainty. But neither document states explicitly that it is "not a measured physical uncertainty" or "not a change to the 0.01 A·s threshold".
  - `08_gate_status_summary.md:19` still says I_over 1e-4 A·s (stale).
  - `04_independent_code_review.md:63-69` still says t_neg/t_pos are not recomputed (stale since VC-09).

**Q10 – Does `recompute_from_traces.py` avoid simulator code?**
- Its imports are `r4h3/__init__` (sys only), `evaluator` (json, Path, numpy), `frozen` (hashlib, importlib, sys; `load_r3_lib` is not called) and `traces` (numpy, json). `np.load(..., allow_pickle=False)` is used (`traces.py:100`).
- The `sys.modules` check (`recompute_from_traces.py:60-62`) is meaningful for normal imports: `r3_lib` is loaded under the name "r3_lib" (`frozen.py:80`), and `config`/`validator`/`closedloop` would pull it in. It would miss only a module loaded under a different name or vendored code. No such path exists.
- It runs after evaluation and before writing, which is acceptable.
- It does not check that the spec SHA-256 equals the trace meta `config_sha256`, or that the trace SHA-256 equals the `evaluation.csv` value (NOTE).
- `test_campaign.py::test_independent_recomputation_runs_as_a_separate_process` runs it as a subprocess with `-I -B`.

**Q11 – Unresolved common mode that could let a wrong metric be credited.**
- Parameters in the spec come from the same objects. The R0 ageing law is duplicated (checked against BatchParams by `test_regressions_v2.py::test_evaluator_r0_at_p3_equals_batchparams`). The loss, current and friction laws, the M1 curve and the states are shared. These are inside the accepted residual.
- Beyond that: an `r3_lib` torque-limit error would be detected only by a non-gating diagnostic with no binding consequence ("flagged for investigation"), so the run would still be credited. The owner's wording ("reduces shared-code errors") arguably accepts this; it should be explicit.

**New findings**
- **N-B1 MINOR.** Crediting is decided by the in-process evaluation in the simulator process: `campaign.py:596-605` → `credited`, `recompute_protocol_ok` → `classify_pair`. The §9 separate script runs only as a manual post-run checklist step (`11_campaign_release_checklist.md:32`). Its result is not fed back into `conditions.csv` or the statuses. If it is skipped or exits 1, conditions remain COMPARABLE. Both paths use the same code on the same re-read trace, so a divergence is unlikely, but §9's "by a separate script … not credited" is not enforced.
- **N-B2 NOTE.** The wording issues listed in Q9 (a)-(c) and the stale `04_`/`08_` text.
- **N-B3 NOTE.** The evaluator assumes active, non-SoH-scaled limits without carrying `active` or `soh_scaled` in the spec. It is correct for H3, but nothing would catch it if the limits were reused outside H3.

**Regression tests:**
- `test_rev2.py::test_drive_limit_boundaries[6 cases]`, `::test_regen_limit_and_voltage_window_cases`, `::test_copper_and_curve_inverses_satisfy_the_forward_law`, `::test_independent_limits_agree_with_r3_lib_within_the_diagnostic_tolerance[12 cases]`, `::test_the_limit_check_detects_a_wrong_input`, `::test_evaluator_uses_its_own_limits_not_the_traced_ones`, `::test_forced_overcurrent_i_over_agrees_far_inside_the_tolerance[6 cases]`.
- `test_regressions_v2.py::test_diagnostic_disagreement_is_flagged_but_does_not_decide_crediting`, `::test_protocol_disagreement_decides`, `::test_evaluator_r0_at_p3_equals_batchparams`.
- `test_campaign.py::test_independent_recomputation_runs_as_a_separate_process`.
- `logs/pytest_run10.xml` lists the `test_rev2.py` and `test_campaign.py` names above as part of 179 tests with 0 failures and 0 errors. I did not search it for the three `test_regressions_v2.py` names.
- `pytest_run11.txt` (181 passed) cannot be tied to test names or a code version.
- The rev2 evaluator and `recompute_from_traces` match the current files at the key definitions (`TORQUE_LIMIT_TOL`, `torque_limits`, `PROTOCOL_TOLERANCES`, `FORBIDDEN`). I did not do a full diff.

**Verdict: CLOSED as "mitigated, with the residual accepted"**, conditional on that acceptance being recorded. `code_review_status_v2.json` still lists "CR-A6 residual" under `pending_owner_acceptance`. No approval record exists yet, and `approval_problems` (`campaign.py:405-407`) enforces that one is needed.

**Remaining limitations (as accepted):** no validation of the plant dynamics or parameters; shared equations, parameters and integrated states; `tracking_ok` relies on the traced `v_tracked`; the torque-limit cross-check does not decide crediting. In addition, N-B1: crediting comes from in-process recomputation rather than the separate script.
