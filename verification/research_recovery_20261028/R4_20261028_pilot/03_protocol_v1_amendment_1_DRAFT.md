# Proposed amendment 1 to R4 protocol v1 (H3)

**Status: DRAFT — NOT APPROVED FOR CAMPAIGN EXECUTION.** It is not frozen and not issued, and has had no human review. It has no force until the owner issues it (§10).

| Item | Value |
|---|---|
| Applies to | `../R4_20261028_preflight/03_R4_protocol_v1.md`, SHA-256 `f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab` (re-verified 2026-10-28; the protocol is unchanged) |
| Revision | rev1, 2026-10-28. It replaces rev0 (01:35), which is archived unchanged as `archive/rev0_20261028_0135/03_protocol_v1_amendment_1_DRAFT.md`, SHA-256 `faf25d80391d15ffc6dc54167b25bff0f931b61fd85e863a662f7902556d5f7f` (also in `archive/rev0_20261028_0135/ARCHIVE_INDEX.csv`) |
| Prepared by | AI assistant, from the owner's decisions D1–D5 of 2026-10-28 and the independent code review (`04_independent_code_review.md`) |
| Draft integrity identifier | The SHA-256 of this file is in `03_protocol_v1_amendment_1_DRAFT.sha256.txt` and in `zz_sha256_manifest_v2.csv`. It identifies this draft text only and does not mean the text is frozen or approved |

Section and item numbers below refer to protocol v1 (§) and to `02_protocol_ambiguity_register.md` (AMB-xx).

---

## 1. What changed from rev0

| Item | rev0 | rev1 |
|---|---|---|
| A1-2 extra stops | owner to choose (a) reject or (b) allow | **D1 adopted:** reject |
| A1-4 baseline at P3 | v_b computed on each state's plant | **D2 adopted:** v_b and S-eco both designed on P1, both run on P3. Rev0's proposal is withdrawn |
| A1-6 arrival timing | owner to choose (a) keep v1 or (b) exact arrival | **D3 adopted:** keep v1 (arrive no later, then wait at rest) |
| A1-8 smoke test | "repeated in the campaign" | **D4 adopted:** development only |
| A1-10 P3 feasibility | record QS infeasibility; §8.2 alone decides | **D5 adopted.** The meaning of "infeasible" is open (AMB-24) |
| A1-1 cycles | clarification | adds the canonical sampled inputs and their hashes |
| New | — | A1-11 to A1-18: review findings and open items |

---

## 2. Decisions D1–D5 (adopted by the owner, 2026-10-28)

### D1 — No stops other than the reference task's (amends §5.2–5.3 and §9(a); resolves AMB-02)

**Requirement clarified.** §5.2 allows the planner's speed grid to include 0 at any interior distance step. §5.3, §6 and §9 never say whether an S-eco profile may come to rest inside a segment.

**Decision.**
- An S-eco trajectory is **invalid** if it is at rest at any knot strictly between a segment's departure and its arrival.
- The only rest periods allowed are the segment endpoints and the reference rest intervals.
- An invalid trajectory makes that scenario's profile **unavailable**. It is recorded and never replaced or re-planned (as for a time-infeasible segment, §5.2).

**"At rest".** It means v ≤ 1e-9 m/s. This is the frozen moving/rest rule of §5.1 (`r3_lib.segments`: moving if v > 1e-9 m/s). No other near-zero threshold is used. The planner's speeds are exactly 0 or at least one speed step (0.1 or 0.05 m/s), so any threshold below the step would classify a planner profile the same way.

**Independence.**
- The validator decides from the profile knots alone.
- `validate_trajectory(task, t, v, plant, label)` takes no planner status, and a planner "ok" cannot make an invalid profile valid (tests `test_validator_cannot_be_satisfied_by_a_planner_flag`, `test_classification_ignores_any_planner_flag`).

**Rationale.** An extra stop changes the driving task. A matched comparison (§1, §6) then no longer holds.

**Scope.** D1 applies to the planned trajectory. Whether the dynamic run comes to rest inside a segment is not a validity criterion: §8.2 tracking governs (see AMB-26).

**Implementation.** `code/r4h3/validator.py` (VC-01).

### D2 — P3 comparisons (amends §4 and §8.1 "Secondary"; resolves AMB-04; withdraws rev0 A1-4)

**Requirement clarified.** §8.1 says "P1-designed profile evaluated on P3". The protocol does not say which baseline profile B0 tracks at P3.

**Decision.** For every P3 condition:
- **Plant.** Both arms run on the same P3 plant (SoH 0.8, k_r0 3.5), with the same motor branch and limit set. Initial conditions are the same: SoC 0.8, V1 = 0, at rest, integrator 0.
- **Controller.** The fixed LQR gain is the one designed on P1, unchanged.
- **B0** tracks the baseline task v_b determined on P1 for the same cycle, motor branch and limit set. On S2 and S1 at P1 this is expected to equal v_ref exactly (§9 baseline sanity).
- **B3** tracks the S-eco profile designed on P1.
- Nothing is redesigned at P3.

**Rationale.** P3 is a transfer and robustness assessment of P1-designed inputs. Redesigning either arm at P3 would be B4 (blocked) or an unregistered variant.

**Fact recorded.** `eureka.controllers.gain(p, "fixed")` does not depend on SoH, k_r0, R0, the limit set or the motor. So the P1 gain equals a P3 gain bit for bit (`test_gain_is_identical_at_p1_and_p3`).

**Implementation.** `campaign.execute_schedule` / `run_condition`.

### D3 — Early arrival and waiting (confirms §5.2–5.3; resolves AMB-06)

**Requirement clarified.** §5.2 allows t_k ≤ T_k, and §5.3 departs each segment at the reference time. The task brief of 2026-10-28 could be read as requiring exact arrival.

**Decision.** Keep v1, with these rules:
- Arrival is no later than the reference arrival ke·h.
- Departure is exactly at the reference departure ks·h.
- After an early arrival the trajectory stays at rest (v ≤ 1e-9 m/s) until the next reference departure.
- The trajectory starts at t = 0 and ends at exactly T_ref, at rest. Its total and per-segment distances meet §9(b).
- **No timing tolerance:** time comparisons are exact.

A late arrival, an early or late departure, or motion during a wait or a reference rest interval makes the trajectory invalid.

**Rationale.** Early arrival preserves stop locations, rest intervals, total time and distance (§6). Exact arrival would change §5.2 (t_k = T_k) and is not needed for a matched comparison.

**Consequence noted (AMB-28).** With exact comparisons, a planned arrival within a few floating-point units of T_k (planner sum versus knot cumulative sum) would be rejected, and the profile would be "unavailable". This is conservative and has not occurred: the S1 smoke-test margins are 0.076–0.483 s.

**Implementation.** `validator.py` (VC-01). Tests: `test_arrival_one_tenth_of_a_nanosecond_late_is_rejected`, `test_departure_one_tenth_of_a_nanosecond_early_is_rejected`, `test_moving_again_after_an_early_arrival_is_rejected`.

### D4 — Smoke tests are development tests (resolves AMB-09)

**Decision.**
- The two runs `H3-slice-S1-M0-L-R1-P1-B0-dt1ms` and `…-B3-dt1ms` (`outputs/slice_S1_M0_L-R1_P1/`) are development and engineering tests only.
- They do not count toward the 170 runs and are preserved unchanged.
- The equivalent configuration is in the campaign as `R4H3-INS-S1-M0-LR1-P1-B0-dt1ms` and `…-B3-dt1ms`. Those runs are executed afresh, under official run IDs, after approval and campaign release.
- No energy difference is computed, published or optimised from the smoke-test pair.
- The same applies to every readiness development check (`outputs/dev_readiness_*`).

**Implementation.** `campaign.validate_schedule` checks that no official run ID equals a smoke-test ID.

### D5 — A P1-designed profile infeasible on P3 (amends §8.1/§8.2 handling; resolves AMB-13 except AMB-24)

**Decision.**
- **Infeasibility is a result.** It does not permit revising the controller, changing profile parameters, relaxing constraints or changing the task.
- **The record is kept.** Both arms of the prescribed P3 condition are run and retained whatever their feasibility on P3, along with every attempted run and error.
- **No paired energy difference** is computed when either arm is invalid or the task is incomplete.
- **Baseline infeasible on P3:** the condition is non-comparable for energy. The plant is never changed for one arm only.
- **Denominators** report every status (`checks.denominator`).

**Classification order** (`checks.classify_pair`):

| Order | Status | Meaning |
|---|---|---|
| 1 | PROFILE_UNAVAILABLE | eco profile unavailable |
| 2 | BASELINE_UNAVAILABLE | baseline task unavailable |
| 3 | ERROR | an attempted run raised an exception |
| 4 | BASELINE_INFEASIBLE_ON_P3, then ECO_INFEASIBLE_ON_P3 | infeasible on P3, under the issued AMB-24 rule |
| 5 | B0_INVALID_EXCLUDED | B0 fails §8.2 (§8.1: excluded and reported) |
| 6 | INVALID_COMPARISON | B3 fails §8.2 |
| 7 | RECOMPUTATION_DISAGREEMENT | §9: not credited until resolved by amendment |
| 8 | COMPARABLE | the only status for which `checks.paired_delta` returns ΔE_abs and ΔE_rel, always with trip time |

**Open (AMB-24): what "infeasible on P3" means.** D5 does not define it. Two readings are implemented, and neither is chosen:

| Reading | Rule |
|---|---|
| (a) `qs_step_feasibility_on_P3` | Infeasible if any piece of the P1-designed profile fails `QSPlant.step` on the P3 plant (the §5.2 feasibility notion) |
| (b) `dynamic_8_2_only` | Only the dynamic run's §8.2 flags decide; the QS flag is reported |

Rev0 A1-10 proposed (b). The review (CR-A2) notes that the readiness implementation first applied (a). The campaign refuses every P3 condition until the issued amendment sets the rule.

---

## 3. Cycle definition and resampling (A1-1, rev1; AMB-01)

**Facts established on 2026-10-28** (`05_cycle_input_provenance.md`):

**The YAML source.** `configs/cycles/profiles.yaml` (SHA-256 `90a496a36c618e216693a3d819b84739f10e6c35167c23a91b63478ef28be0a6`) defines each cycle as segments: idle or cruise durations and accelerations to target speeds. `eureka.cycles.build` turns these into piecewise-linear knots. Accelerations end at non-integer times, so:

| Cycle | Knots off the 1 s grid | Duration | Distance |
|---|---|---|---|
| S1 | 22 of 24 | 324.911 s | 2161.047 m |
| S2 | 24 of 26 | 213.278 s | 531.678 m |

R3 v1 §3.2's statement that the knots lie on whole seconds is wrong for S1 and S2.

**The protocol task (§3).** It is the profile sampled at h = 1 s. It is produced by R3's frozen `run_gates.reference()` (SHA-256 `d870e096cbad828661c65682dfbd4e18ecc00bdace989af084e10def465ca85a`): `t = np.arange(0, duration + 1e-9, 1.0)` and `v = np.interp(t, knots)`. Nothing is rounded. The final partial second is not sampled, which is why T_ref is 324 s and 213 s.

| Cycle | Samples | Time span | T_ref | d_ref |
|---|---|---|---|---|
| S1 | 325 | 0–324 s | 324 s | 2161.0270 m |
| S2 | 214 | 0–213 s | 213 s | 531.5735 m |

Both equal the protocol's printed values. Rest intervals and segments: S1 has 5 and 4; S2 has 7 and 6 (listed in `inputs/cycles/cycle_inputs_manifest.json`).

**Provenance check, bit for bit:**
- R3's `run_gates.reference()` equals R4's `task.load_task()`.
- Both equal the `t` and `v_ref` arrays in all 24 sampled references per cycle that R3 retained (`outputs/gates*/paths/*.npz`). Each of those files' SHA-256 was first checked against `R3_hash_manifest.csv`.

**Canonical inputs (separate artefacts, hashed):**

| File | Content | SHA-256 |
|---|---|---|
| `inputs/cycles/S1_sampled_h1.csv` | canonical S1 task (t_s, v_mps; shortest round-trip floats) | `87151e5c30c02f5f6784732a5dd619fc6c39e90913d4afcf06292de2c1f2b7da` |
| `inputs/cycles/S2_sampled_h1.csv` | canonical S2 task | `def9d757dc0923afe20a91dca487c84527daff2bef5421c34aef1a61f0a6e990` |
| `inputs/cycles/S1_source_segments.json`, `S2_source_segments.json` | YAML definitions, verbatim | `88a04c90…d6fd`, `49093326…2d13` |
| `inputs/cycles/S1_knots_from_yaml.csv`, `S2_knots_from_yaml.csv` | knots from `eureka.cycles.build` | `e0cdb1f4…20ec`, `4bf39498…de6c` |
| `inputs/cycles/cycle_inputs_manifest.json` | all checks and hashes | `3d3d6e93d19842141691d041e2363dd8f3f9fef73b362ebcd6ae2ef8b6de7ea5` |

**Proposed wording.**
- "Reference", "reference rest interval", "stop" and "segment" in §5, §6, §8 and §9 mean the canonical 1 s-sampled task above. They do not mean the YAML profile.
- Every campaign process verifies both canonical hashes. It also verifies that `task.load_task()` reproduces them bit for bit (`inputs.verify_all`); any difference stops the campaign.
- No replacement cycle is made.

**S2 protection.**
- S2 has been used only as an input definition: hashed and sampled.
- No S2 planner, QS or dynamic run has been executed in R4.
- No setting has been chosen from S2.
- The planner numerics are the frozen §5.2 constants and are asserted by the dry run.

---

## 4. Clarifications and remaining items

**A1-3 I_over (AMB-03).**
- §8.2 I_over is integrated against the active set's C-rate limits (c_dis·Q, c_ch·Q, nominal Q).
- Protocol §9 "I_over agrees with runs.csv" compares this same quantity: simulator side from the traced r3_lib current, evaluator side from its own recomputed current (VC-05).
- The voltage-window exceedance from `r3_lib` is a diagnostic.

**A1-5 Limit sets (AMB-05), editorial.** "as implemented in `r3_lib`" should read "as defined in R3 `code/run_gates.py` (LIMS) and `code/r3_pilot.py` (LIM)".

**A1-7 M2 coefficient (AMB-07), editorial.** k_c = 18000·(1/0.874 − 1)/85² = 0.35917…; §2.3's 0.3592 is rounded.

**A1-9 RMSE sampling (AMB-11).** RMSE and max |e| are taken at the control instants k·Ts, k = 0…steps.

**A1-11 Sensitivity gain basis (AMB-14), OPEN.**
- `eureka.controllers.gain` depends on M, A_f, C_d and r_w, which §8.4 varies.
- §4 says the gain is "design-fixed"; §8.4 lists only v_b and S-eco as recomputed per draw. The owner must choose:

| Option | Gain used for every draw |
|---|---|
| `nominal_P1` | the nominal P1 gain (the controller is not redesigned for the perturbed plant) |
| `draw_P1` | `gain(p_draw, "fixed")` (the controller is redesigned for each draw's P1 plant) |

- Both are implemented. `sensitivity.gain_for_draw` refuses to choose.
- **The 128 SEN runs are blocked until this is set.**

**A1-12 Recomputation gate and tolerances (AMB-22).**
- **Credit-deciding checks** are the protocol §9 quantities:

| Check | Tolerance | Source |
|---|---|---|
| E_chem, E_DC | 1e-4 relative | §9 |
| distance | 1e-6 relative | §9 |
| trip time | 1e-9 s absolute | **not stated in §9**; implementation choice |
| §8.2 C-rate I_over | 1e-4 A·s absolute | **not stated in §9**; implementation choice |
| RMSE | 1e-9 relative | **not stated in §9**; implementation choice |
| stop, completion, tracking and constraint flags | identical | §9 |

  The owner is asked to accept the three implementation choices or replace them.
- **Diagnostics** never decide crediting (VC-04): E_pos, friction energy, max |e|, window I_over, min V_t, battery-limited fraction, current and friction-power recomputation, wheel braking power, tracked-profile check and energy closure.
- The recomputation is also run as a **separate process** that reads only the saved traces and per-run spec files (`code/recompute_from_traces.py`, CR-A6).

**A1-13 Campaign directory and gate record (AMB-15), OPEN.**
- §10.1 requires a new versioned directory and `logs/pre_run_hashes.txt` written before the first outcome-producing run.
- This pilot directory already holds the smoke-test gate record, which binds the rev0 code, plus development outputs.
- **Proposal:** the campaign runs from a fresh sibling directory named `R4_<campaign date>_pilot`, with a suffix if needed. It holds a hash-identical copy of `code/`, `config/` and `inputs/`, its own clean test run, and its own `logs/pre_run_hashes.txt`. The issued amendment names that directory, and `run_campaign` refuses any other.

**A1-14 Sensitivity counting (AMB-16), clarification.** In the §8.1 rule "at least 29 of the 32 draws give ΔE_rel ≤ −1.0 %", a draw with no comparable pair does not give such a ΔE_rel. The denominator stays 32.

**A1-15 QS vs dynamic (AMB-17), clarification.**
- e_QS is the QS energy of the tracked profile's knots on the plant of the dynamic run, per reference km.
- The criterion is 100·(e_dyn − e_QS)/e_QS, R3's definition. M0 and M1 must be within ±1 %; M2 is reported only.
- For P1 S-eco profiles e_QS equals the planner's DP sum (checked in DEV-2).

**A1-16 Baseline task validation (AMB-19), clarification.**
- v_b is validated and reported (protocol §9 "baseline sanity"), not rejected: equal to v_ref, maximum deviation, distance error, window and boundary hit.
- B0 runs whenever v_b exists; §8.2 decides its validity.
- The §5.2 planner constraints (segment speed caps, D_k equality) apply to S-eco only.

**A1-17 Secondary metric definitions (AMB-21, AMB-25), clarification.**
- **Battery-limited fraction** follows R1–R3: control instants at which the command exceeds the drive limit and that limit is below min(T_max, P_max/ω).
- **Braking work W_brake for η_regen** is ∫(max(−f_w·v, 0) + P_friction) dt. Here f_w is the drivetrain force at the wheel, so motor viscous drag while coasting counts as motor braking.

**A1-18 Environment record (AMB-20), editorial.** "pip freeze" is recorded as the installed-distribution list from `importlib.metadata` (same content, no subprocess).

**Owner notes, not amendments:**

| Item | Note |
|---|---|
| AMB-18 | The readiness brief's stop condition 6 ("grid, QS/dynamic and 0.5 ms checks pass") cannot be met before the campaign. Protocol §9 defines these checks on S2 campaign data, and on failure states a resolution or INCONCLUSIVE rather than refusing to run. Pre-campaign, they are implemented and validated on S1 development data only |
| AMB-26 | §8.2 tests stationarity only on [t_a + 1 s, t_d]. A dynamic check of the planned early-arrival wait would be a new criterion |
| AMB-27 | The M2 S-eco profile is designed on the M2 QS model, which §2.3 calls non-representative. This follows §5.2 literally |

---

## 5. Impact on the 170-run design and run IDs

**The run count is unchanged:** 170 dynamic runs (§10.6). D1–D5 change no run count. D5 keeps infeasible and invalid runs in the record.

| Set | Runs | Definition | Blocked by |
|---|---|---|---|
| NOM | 12 | S2, P1, M0/M1/M2 × L-R1/L-EVE × B0/B3, 1 ms | approval, AMB-15 |
| P3 | 12 | S2, evaluated on P3, P1-designed profiles (D2), 1 ms | approval, AMB-15, **AMB-24** |
| INS | 12 | S1, P1, 1 ms (includes the configuration of the D4 smoke test) | approval, AMB-15 |
| CNV | 6 | S2, L-EVE, P1, M0/M1/M2 × B0/B3 at 0.5 ms (traced at 1 ms) | approval, AMB-15 |
| SEN | 128 | 32 draws × M0/M1 × B0/B3, S2, L-EVE, P1 | approval, AMB-15, **AMB-14** |

- **Run ID format:** `R4H3-<set>-[D<nn>-]<cycle>-<motor>-<limits>-<pstate>-<branch>-dt<1|0.5>ms`, for example `R4H3-NOM-S2-M0-LR1-P1-B0-dt1ms`. All 170 IDs are listed in the dry run's `schedule_170.csv`; its SHA-256 is in `config/campaign_config_v1_DRAFT.json`.
- **Planner jobs (82, QS only, not runs):** 6 S2 P1, 6 S1 P1, 64 sensitivity designs and 6 S2 fine-grid jobs for the §9 grid convergence.

## 6. Development tests versus confirmatory runs

| | Development tests | Confirmatory runs |
|---|---|---|
| Examples | smoke-test pair; `outputs/dev_readiness_*`; pytest toy runs | the 170 official runs |
| IDs | `H3-slice-…`, `DEV-…` | `R4H3-…`, accepted only by `run_campaign` |
| Cycles | S1 or toy tasks only | S1 and S2 per §10.6 |
| Purpose | validate code and infrastructure | the H3 result |
| Counted toward the 170 | never | yes |
| Energy difference | never computed | computed only for COMPARABLE conditions, after the campaign |
| Directory | this pilot directory | a fresh campaign directory (A1-13) |

## 7. Unresolved items and gate status

| Item | Status | Blocks |
|---|---|---|
| Approval and issue of this amendment | not done | the whole campaign |
| AMB-15 campaign directory | open | the whole campaign |
| AMB-24 meaning of "infeasible on P3" | open | P3 set (12) |
| AMB-14 sensitivity gain basis | open | SEN set (128) |
| A1-12 three unstated recomputation tolerances | needs acceptance | crediting rule |
| Review MAJOR findings CR-A2 (= AMB-24) and CR-A6 residual (evaluator shares the model's equations and the traced torque limits) | open or need acceptance | campaign (`config/code_review_status_v1.json`) |
| AMB-18 brief stop condition 6 | owner interpretation | readiness statement only |

## 8. Machine-readable block

`code/r4h3/campaign.py` reads this block.
- A value that differs from what the code implements, or an unknown key, is an **error**, never an override.
- A `null` is an open item and blocks the campaign.
- The issued version must set `"status": "APPROVED"`, fill every `null`, live at `../R4_20261028_preflight/03_R4_protocol_v1_amendment_1.md`, and be accompanied by `approvals/amendment_1_approval.json`, which names the approver, the date and the issued file's SHA-256.

<!-- r4h3-amendment-block -->
```json
{
 "amendment": "R4 protocol v1 amendment 1 (draft rev1)",
 "status": "DRAFT",
 "applies_to_protocol_sha256": "f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab",
 "D1_extra_stop_rule": "reject",
 "D1_rest_threshold_ms": 1e-09,
 "D2_p3_profiles": "B0 tracks v_b designed on P1; B3 tracks S-eco designed on P1; both run on the P3 plant",
 "D2_gain_design_state": "P1",
 "D3_arrival_rule": "arrival no later than the reference arrival, then at rest until the reference departure",
 "D3_timing_tolerance_s": 0.0,
 "D4_smoke_runs_count_toward_campaign": false,
 "D5_p3_infeasible_rule": "run and retain both arms; classify the condition infeasible; no paired energy difference",
 "canonical_sampled_cycles_sha256": {
  "S1": "87151e5c30c02f5f6784732a5dd619fc6c39e90913d4afcf06292de2c1f2b7da",
  "S2": "def9d757dc0923afe20a91dca487c84527daff2bef5421c34aef1a61f0a6e990"
 },
 "recompute_gate": [
  "E_chem_rel",
  "E_DC_rel",
  "distance_rel",
  "trip_time_abs_s",
  "I_over_protocol_abs_As",
  "rmse_rel",
  "stop_ok_equal",
  "complete_equal",
  "tracking_ok_equal",
  "constraint_ok_equal"
 ],
 "recompute_tolerances": {
  "E_chem_rel": 0.0001,
  "E_DC_rel": 0.0001,
  "distance_rel": 1e-06,
  "trip_time_abs_s": 1e-09,
  "I_over_protocol_abs_As": 0.0001,
  "rmse_rel": 1e-09,
  "flags": "identical"
 },
 "planned_runs": {
  "NOM": 12,
  "P3": 12,
  "INS": 12,
  "CNV": 6,
  "SEN": 128,
  "total": 170
 },
 "AMB_14_sensitivity_gain_basis": null,
 "AMB_15_campaign_directory": null,
 "AMB_24_p3_infeasibility_rule": null,
 "note": "DRAFT - NOT APPROVED FOR CAMPAIGN EXECUTION. Values must equal the implementation; null = open."
}
```

## 9. Not changed by this amendment

These are unchanged:
- the protocol text;
- the plant, motor bracket, limit sets, P-states and cycles;
- the planner numerics (2 m, 0.1 m/s, λ ∈ [10⁻³, 10⁶], 40 bisection steps);
- the §8.2 criteria and the 1.0 % threshold;
- the §8.1 decision rules;
- the §9 checks;
- the 170-run budget.

No legacy figure is a target or criterion.

## 10. To issue (owner)

1. Review this text and decide AMB-14, AMB-15 and AMB-24. Accept or replace the A1-12 tolerances. Rule on review findings CR-A2 and CR-A6 (`04_independent_code_review.md`).
2. Copy the reviewed text to `../R4_20261028_preflight/03_R4_protocol_v1_amendment_1.md`, set `"status": "APPROVED"`, fill the `null` values, and record its SHA-256 before any affected run (protocol header).
3. Write `approvals/amendment_1_approval.json`: `{"approved_by": …, "date": …, "amendment_sha256": …}`.
4. Prepare the campaign directory (A1-13), run the tests there and record `logs/pre_run_hashes.txt`. Only then may `run_campaign.py --execute` pass its preconditions.
