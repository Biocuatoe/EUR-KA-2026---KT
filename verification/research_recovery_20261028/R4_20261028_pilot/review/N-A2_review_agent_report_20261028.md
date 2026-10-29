# Independent read-only review of the N-A2 change and the amendment 2 draft: final report (verbatim)

**Provenance.**
- **Who:** a separate AI review agent ("Plan" agent type, with no Edit/Write tools), 2026-10-28, about 09:44–09:57 local time.
- **Instructions:** Read, Grep and Glob only.
- **What it reviewed:** the state archived in `../archive/rev4a_reviewed_20261028_0957/`, including amendment 2 draft SHA-256 `c3e1ddfce7dca7909bb1cd2a6186f4d5044b5dfe81eeed43df0b9fcf215957d4`. Run 16 was in progress while it read; it later completed with 201 passed.
- **Format:** the text below is the agent's final message. The only edit is removing the indentation that the message relay adds. File references are as given by the reviewer.
- **Author's responses:** `../14_amendment2_release_readiness_report.md`.

---

Independent review of the N-A2 change and the amendment 2 draft, read-only

I used Read, Grep and Glob only. I ran no command, hashed nothing and wrote nothing.

**File legend.** Short names below mean these files:
- PIL = `D:\EURÉKA 2026 - KT\verification\research_recovery_20261028\R4_20261028_pilot`
- `checks.py` = `PIL\code\r4h3\checks.py`
- `campaign.py` = `PIL\code\r4h3\campaign.py`
- `frozen.py` = `PIL\code\r4h3\frozen.py`
- `evaluator.py` = `PIL\code\r4h3\evaluator.py`
- `T_A2` = `PIL\code\tests\test_amendment2.py`
- `T_C` = `PIL\code\tests\test_campaign.py`
- `T_R2` = `PIL\code\tests\test_rev2.py`
- `DRAFT2` = `PIL\03_protocol_v1_amendment_2_DRAFT.md`
- `A1` = `D:\EURÉKA 2026 - KT\verification\research_recovery_20261028\R4_20261028_campaign\release\03_R4_protocol_v1_amendment_1.md`
- `PROT` = `D:\EURÉKA 2026 - KT\verification\research_recovery_20261028\R4_20261028_preflight\03_R4_protocol_v1.md`
- `r3_lib` = `D:\EURÉKA 2026 - KT\verification\scientific_rebuild_20261024\research_recovery_20261025\R3_20261025\code\r3_lib.py`
- `model.py` = `D:\EURÉKA 2026 - KT\verification\scientific_rebuild_20261024\src\rebuild\model.py`
- ARCH = `PIL\archive\rev3_20261028_0928\code`

**What I compared against the archive (ARCH):**
- Line by line, identical: `evaluator.py`, `closedloop.py`, `sensitivity.py`, `recompute_from_traces.py`, `record_gate.py`, `record_readiness_gate.py`, `run_campaign.py`.
- Changed: `checks.py` (new lines 42-124), `campaign.py`, `frozen.py`, and `test_rev2.py` (stricter authorisation test).
- New: `test_amendment2.py`.
- The campaign root's `code\r4h3\frozen.py` is still the old version (depth-based paths).

## Verdicts
- **N-A2 implementation: DEFECTS FOUND.** The core rule is correct. The defects are MINOR: wrong buckets and undocumented ambiguities. None lets an M0/M1 branch pass when it should not, except the undocumented "usable energy" question in R3-4.
- **Amendment 2 draft: INACCURATE.** The machine-readable block matches `IMPLEMENTED_2` exactly. Several prose statements do not match the code (R3-1, R3-6).
- **CR-A2: CLOSED.**
- **CR-A6: MITIGATED-RESIDUAL-ACCEPTED.**
- **Torque limits: INDEPENDENT-EQUIVALENT.**
- **Fail-closed: NO, for one condition only.** The "campaign root" location check compares the directory name, not the path (R3-1). Every other listed precondition is enforced, and no code writes an owner document.

## Findings

**R3-1 — MAJOR — SI-1 removed the implicit location lock; campaign mode only checks the directory name.**
- **Where:** `frozen.py:17-28` (marker-based `_find_repo`) together with `campaign.py:59` and `campaign.py:526-529` (the check is `frozen.PILOT.name != CAMPAIGN_DIR_NAME`).
- **Defect:** before SI-1, `REPO = PILOT.parents[2]` and `PREFLIGHT = PILOT.parent/…` (ARCH `frozen.py:14-16`). A copy at any other depth failed the frozen-input hash checks. Now the repository root is found from any depth, and the release files are read from the fixed real `CAMPAIGN_DIR\release`. `check_gate` (`slice.py:48-64`) checks only paths relative to the running copy.
- **Failure scenario:**
  1. After authorisation, a verbatim copy of the campaign root is placed in any directory named `R4_20261028_campaign` under the project root, for example `R4_20261028_campaign\release_attempts\R4_20261028_campaign\`.
  2. The copy has the same `logs\pre_run_hashes.txt`, so `pre_run_hashes_sha256` in the authorisation still matches.
  3. The copy has no `outputs\campaign`, so the "already run" check passes.
  4. The campaign can therefore run a second time, possibly in a different Python environment, which the gate does not pin.
- **Conflicts with:** `A1:95` ("`run_campaign` refuses to run from any other directory") and `DRAFT2:106` ("still runs only from the campaign root").
- **Remedy:** block unless `frozen.PILOT.resolve() == CAMPAIGN_DIR.resolve()`. Add a test that monkeypatches `PILOT` to a nested directory with the same name.

**R3-2 — MINOR — An applicable FAIL is hidden as NOT_EVALUABLE_RUN_MISSING.**
- **Where:** `checks.py:66-69` runs before `checks.py:73-75`.
- **Defect:** if one M0/M1 arm has `status = FAIL` and the other arm has no usable energy, the pair status is `NOT_EVALUABLE_RUN_MISSING`. `qs_check_fail` (`checks.py:121`) then undercounts. This contradicts `DRAFT2:34` ("FAIL if either M0/M1 arm fails").
- **Effect:** the branch is still INCONCLUSIVE, so this is not favourable to a positive result. The reported reason and the counts are wrong.
- **Remedy:** test for a FAIL among the available arm checks before the missing-energy test, or record both reasons. Add a test.

**R3-3 — MINOR — `NOT_EVALUABLE_RUN_MISSING` covers cases outside its documented definition, and the eligibility counts do not add up.**
- **Definition in the draft:** `DRAFT2:74` (AMB-29(b)) defines the label as a *QS-eligible* pair without usable dynamic energy, from an exception or non-finite states.
- **Case 1 (`campaign.py:819-822`):** a condition-level exception is given `qs_eligible_pair=False` and this label, although the screen never ran.
- **Case 2 (`checks.py:76-79`):** `"undefined (QS energy <= 0)"` is given the same label, although no run is missing.
- **Consequence:** `qs_eligible_pairs + qs_ineligible_pairs + not_evaluable_profile_unavailable` can be less than `planned_pairs`, and `not_evaluable_run_missing` mixes eligible pairs with pairs of unknown eligibility.
- **What still holds:** the six check-status classes are complete and mutually exclusive. Both cases are fail-closed: the branch is INCONCLUSIVE.
- **Remedy:** add separate labels (for example `NOT_EVALUABLE_CONDITION_ERROR` and `NOT_EVALUABLE_QS_UNDEFINED`), or record eligibility as unknown. Update AMB-29.

**R3-4 — MINOR — Undocumented ambiguity: which dynamic energy is "usable".**
- **Where:** `campaign.py:713-715`.
- **Defect:** "usable" means executed, no exception, and a finite simulator `E_net_Wh`. The code does not require §8.2 validity, crediting, or agreement with the separate recomputation. So a QS-eligible pair can give the branch its one required PASS even when its arms are:
  - battery-infeasible;
  - above the closure limit;
  - incomplete;
  - mistracked;
  - classified RECOMPUTATION_DISAGREEMENT.
- **Why it matters:** AMB-29(b)'s own reasoning ("a check that applied could not be shown to pass") would make such a pair not evaluable. Counting it as a PASS is the favourable direction.
- **Draft mismatch:** `DRAFT2:74` says "states became non-finite", but the code tests only whether `E_net_Wh` is finite.
- **Context:** per-run computation is unchanged from the amendment-1 implementation. In practice the P1 pairs should be §8.2-valid, so the impact is low, but it is not verified.
- **Remedy:** document this as a new ambiguity (AMB-31) for the owner, and report how many eligible PASS pairs are also dynamic-valid.

**R3-5 — MINOR — "Exact failed feasibility check" is silently read as "failed piece".**
- **Where:** `checks.py:35-39` and `campaign.py:724-725`.
- **Defect:** only the piece index, time interval and speeds are recorded. `QSPlant.step`'s `ok` combines three checks at three integration (Gauss) points: drive torque against `t_pos`, a non-negative battery discriminant, and current against `i_d` (`r3_lib:301`, `311`, `314`). Which check failed, and by how much, is not recorded.
- **Context:** the pieces are reproducible from the saved knots, so this is a documentation issue.
- **Remedy:** record which check failed, or list the interpretation as an ambiguity.

**R3-6 — MINOR — Draft prose that does not match the code or the files.**
- `DRAFT2:10`: `03_protocol_v1_amendment_2_DRAFT.sha256.txt` and `zz_sha256_manifest_v5.csv` do not exist.
- `DRAFT2:106`: see R3-1.
- `DRAFT2:108`, "No other behaviour changes". Unlisted changes:
  - the authorisation now needs the key `amendment_2_sha256` (`campaign.py:420-421`);
  - `REVIEW_STATUS` now points to `code_review_status_v4.json`, which is absent (`campaign.py:87`);
  - the `qs_E_J` column is renamed `qs_E_J_diagnostic` (`campaign.py:692`);
  - the `NUMERICAL_CHECKS` row 7 text changed (`campaign.py:252-256`);
  - `read_amendment` now compares JSON round-tripped values (`campaign.py:343`).
- `DRAFT2:34`: see R3-2. `DRAFT2:74`: see R3-3 and R3-4.
- `DRAFT2:71`: the header says no item is "a favourable choice". For AMB-29(a), the choice removes the B0-only failure path that the amendment-1 implementation had (ARCH `campaign.py:640-642`). This follows the ruling's "both profiles pass" wording and is disclosed, but the header's description is inaccurate.
- `DRAFT2:75`: "as already implied by amendment 1". `A1:180` says "every B0 and B3 run", but `A1:164` speaks of "QS-versus-dynamic on S2 profiles". Amendment 1 is itself ambiguous here.

**R3-7 — MINOR — Test evidence and test gaps.**
- **No clean run on the current tree:** `logs\pytest_run15.txt` shows 200 passed and 1 failed, before the `test_rev2` fix. `pytest_run16.txt` is incomplete (27 dots).
- **Untested:**
  - the branches of `preconditions` for an amendment 2 that exists but is DRAFT, has the wrong amendment-1 hash, or has a bad approval record (`campaign.py:489-500`);
  - SI-1 from a sub-directory, and refusal from a same-named directory;
  - the QS fields of a condition-level exception;
  - the FAIL-plus-missing ordering (R3-2).
- **Weak static check:** the regex at `T_C:116-117` does not match `ISSUED_AMENDMENT_2.write_text` or `APPROVAL_RECORD_2.write_text`. `open(...)` calls are caught by prefix.
- **Conditional asserts:** `T_A2:195-198` become vacuous once those files exist.

**R3-8 — NOTE — Authorisation scope and key name.**
- `AUTHORIZATION_SCOPE` (`campaign.py:70`) still reads "…of protocol v1 amendment 1".
- `DRAFT2:118` does not name the required key `amendment_2_sha256`.
- Both fail closed.

**R3-9 — NOTE — An exception in the new post-run code would relabel executed runs.**
- **Where:** `campaign.py:707-740` is outside the per-arm `try`. In ARCH, `qs_vs_dynamic` was inside it (ARCH `campaign.py:640`).
- **Effect:** an exception there turns executed runs into "condition-level exception, executed=False" rows (`campaign.py:817-826`). The runs would drop out of `runs.csv`, `evaluation.csv` and the separate recomputation, while their traces remain.
- **Likelihood:** low; the risk is of the same kind as N-A5.

**R3-10 — NOTE — Smaller consistency points.**
- `branch_qs_dynamic_outcome` ignores rows with an unknown status (`checks.py:87`). `denominator()` raises in the same situation (`checks.py:228-229`).
- `NOT_EVALUABLE_PROFILE_UNAVAILABLE` (no effect on the branch) and `NOT_EVALUABLE_RUN_MISSING` (branch INCONCLUSIVE) share a prefix but have opposite consequences.
- `P3_RULE` "QS screen diagnostic only" (`checks.py:26`) is now incomplete: the screen also decides §9 applicability.
- AMB-29 and AMB-30 are not in `02_protocol_ambiguity_register.md`. AMB-30 has no machine-readable key, so the owner's decision on it is not checked by code.

**R3-11 — NOTE — `read_amendment` comparison change.**
- The JSON round-trip comparison (`campaign.py:343`) is outside the ruling and not declared. It does not change behaviour for the current `IMPLEMENTED` values (no tuples, no non-string keys).

## Answers to questions 1-13

**1. Path through the code.**
- **Code path:**
  1. `run_condition` screens each existing profile on `eval_plant` (`campaign.py:672-677`).
  2. Eligibility means both screens are True (`campaign.py:708-709`).
  3. The per-arm check runs only if the pair is eligible and the energy is usable (`campaign.py:714-715`).
  4. The pair status comes from `pair_qs_dynamic` (`checks.py:52-79`).
  5. The branch outcome and the counts are computed after the separate recomputation is folded in (`campaign.py:864-872`).
- **Can QS ineligibility directly cause an M0/M1 failure?** No. An ineligible pair becomes `NOT_APPLICABLE_QS_INFEASIBLE` before the arm results are read (`checks.py:57-62`), and the branch rule ignores it (`checks.py:91-101`).
- **Is NOT_APPLICABLE ever counted as a pass?** No. Only `"PASS"` is counted (`checks.py:87`, `93`).
- **Can a branch pass by vacuity?** No. Zero PASS gives INCONCLUSIVE (`checks.py:93-95`).
- **Indirect route:** a branch whose pairs are all inapplicable is INCONCLUSIVE. That is what the ruling requires.

**2. Per-arm QS value for ineligible pairs.** It is never computed. `arm_checks` is filled only when the pair is eligible (`campaign.py:714`), and `qs_vs_dyn_pct` is left empty (`campaign.py:721`).
- **Preserved:**
  - per arm (`campaign.py:692-693`): `qs_E_J_diagnostic`, `qs_screen_feasible`, `qs_screen_n_failed`;
  - per condition (`campaign.py:724-729`): `b*_qs_feasible_on_eval_plant`, and `b*_qs_screen_warning` with the piece, interval and speeds at full precision.
- **Not preserved:** the structured `_qs_val` list is dropped (`campaign.py:827`); this is pre-existing. Which sub-check failed is not recorded (R3-5).

**3. "Same applicable conditions".** Yes.
- The screen uses `QSPlant(p_eval, soh_eval, lim, mm)` (`campaign.py:672`).
- `p_eval` is the P3 parameters for P3, or the draw's parameters for SEN (`campaign.py:810-811`).
- The limits are the condition's limit set; the motor is the condition's motor, or the drawn M0 efficiency for SEN (`campaign.py:796`, `813`).
- On P1 sets the evaluated plant equals the design plant.

**4. Independence of the §8.2 status.** Yes.
- `classify_pair` is byte-identical to ARCH (`checks.py:194-212`) and takes no QS input.
- Arms run whenever their profile exists (`campaign.py:679-685`).
- `paired_delta` refuses anything not COMPARABLE (`checks.py:217-218`), and only tests call it.
- The fold of the separate recomputation only ever downgrades a status (`campaign.py:765-766`).
- No paired energy difference is possible for an invalid or incomplete pair.

**5. Records and denominators.**
- `runs.csv` has a row for every scheduled run: executed, unavailable, or exception (`campaign.py:683`, `704`, `824`).
- `evaluation.csv` holds every executed arm without an exception.
- Traces are kept, and non-finite raw traces too.
- The status denominator is complete (`campaign.py:883`). The six QS check classes are complete and mutually exclusive.
- Wrong buckets: R3-2 (a FAIL hidden) and R3-3 (condition errors and undefined QS energy; the eligibility counts do not add up).

**6. AMB-29 and AMB-30.**
- **Documented?** Yes, for the owner, in `DRAFT2:69-75`. They are not in the ambiguity register.
- **AMB-29(a):** has no effect on the branch outcome. It does remove an earlier failure path; see R3-6.
- **AMB-29(b):** conservative.
- **AMB-30:** the literal reading, mostly conservative. It also lets non-decisive sets supply the one PASS needed against vacuity.
- **"Usable energy" condition:** reasonable as a minimum. Its lack of a §8.2 or recomputation requirement is undocumented and leans favourable (R3-4).

**7. Changes beyond the ruling, and SI-1.**
- No relaxing change beyond the ruling and SI-1, apart from the side effects listed in R3-6 and R3-11.
- **Paths from the pilot and the campaign root:** identical. Neither `verification\` nor `research_recovery_20261028\` contains `src\eureka`, so `REPO` = `D:\EURÉKA 2026 - KT` and `RR` = `PILOT.parent` (`frozen.py:28-30`, `campaign.py:53`, `59`).
- **From a sub-directory:** campaign mode is blocked only if that directory's name differs from `R4_20261028_campaign` (R3-1).

**8. Amendment 2 draft.**
- **Correct:**
  - complete hashes of protocol v1 and amendment 1 (`DRAFT2:7-8`);
  - the ruling stated exactly (`DRAFT2:14-21`);
  - the pair rule and unchanged thresholds and consequence (`DRAFT2:23-38`);
  - the definition of `NOT_APPLICABLE_QS_INFEASIBLE` (`DRAFT2:40-48`);
  - §8.2 independence (`DRAFT2:50-56`);
  - zero eligible pairs gives INCONCLUSIVE (`DRAFT2:64`);
  - denominators (`DRAFT2:77-94`);
  - no change to the 170 runs (`DRAFT2:96-98`);
  - blockers kept (`DRAFT2:110-118`);
  - the "DRAFT — NOT APPROVED FOR RELEASE" label (`DRAFT2:3`).
- **Machine block:** matches `IMPLEMENTED_2` key for key and value for value (`campaign.py:292-310` against `DRAFT2:132-169`; 15 keys plus `amendment`, `status` and `note`).
- **Inaccurate:** see R3-6.

**9. CR-A2.** CLOSED. The QS screen never decides P3 feasibility; it only gates whether the §9 check applies. Executor-level tests force a QS failure on P3 with dynamically valid runs: `T_A2:129-142` and `T_C:283-309`.

**10. CR-A6.** Intact.
- **Recomputation folded into crediting:** `campaign.py:748-766` and `858-864`, unchanged.
- **Evaluator's own torque limits used for friction and the battery-limited fraction:** `evaluator.py:168-189`.
- **Limit diagnostics are non-gating:** `evaluator.py:334`, `342-343`.
- **Residual accepted:** `A1:158` states it without claiming physical validation, and `release\amendment_1_approval.json` exists. Its contents were not checked.

**11. Torque limits.** `evaluator.py` is identical to ARCH and imports only `json`, `Path` and `numpy` (`evaluator.py:28-31`).
- **M2:** the formulas are rationalised forms algebraically identical to `r3_lib:78-95`.
- **M0:** the evaluator is unbounded where `r3_lib` returns INF above 1.5·p_rated. The motor-only limit (P_max = 18 kW) binds first, so the results agree, including for drawn efficiencies 0.83-0.918.
- **M1:** bisection with the same INF convention.
- **Battery limits:** the same as `model.py:44-62` for H3's limit sets, which are active, not SoH-scaled and have a finite V_max (`config.py:24-25`).
- **Not verified:** numerical agreement. I rely on the `test_rev2` limit tests passing in run15.

**12. Fail-closed.**
- **Each listed precondition blocks campaign mode:**
  - issued amendment 2 with status APPROVED (`campaign.py:486-492`);
  - its approval record (`campaign.py:495-500`);
  - the issued amendment 1 equal to the hash amendment 2 amends (`campaign.py:493-494`; in any case blocked if amendment 2 is absent);
  - the protocol §10.1 gate (`campaign.py:512-516`);
  - the authorisation carrying the amendment 1, amendment 2 and gate hashes (`campaign.py:414-430`, `518-525`);
  - the review status (`campaign.py:530-537`; v4 is absent, so this blocks).
- **Exception:** "in the campaign root" is checked by name only (R3-1).
- **Writes:** no code writes `campaign_authorization.json`, an issued amendment or an approval record. The only write sites are in output and config directories (grep), and `release\` holds only amendment 1, its approval and a diff.

**13. Vacuous tests or target values.** No test asserts a target energy-saving value. `test_checks.py:36` and `110` are arithmetic checks on synthetic numbers.
- **Conditional or forced:**
  - `T_A2:195-198`, `211-212`, `222` and `T_C:97-105` depend on the current state of the files;
  - `test_eligible_pair_is_evaluated_with_the_frozen_rule` accepts PASS or FAIL but checks it against the computed deviation, so it is not vacuous;
  - cases 6 and 10 force the screen result with a monkeypatch; `T_C:286` explains why.
- **Gaps:** see R3-7.
