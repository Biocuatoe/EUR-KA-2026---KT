# Amendment 1 to R4 protocol v1 (H3): final candidate, rev2

**Status: APPROVED by the project owner, 2026-10-28 07:46:23 +0700 (local system time) — protocol amendment only.** This approval does not authorise campaign execution. The official campaign remains BLOCKED until the release gate is complete and the owner writes a separate campaign authorisation (`release/campaign_authorization.json`).

Issued from candidate `../../R4_20261028_pilot/03_protocol_v1_amendment_1_rev2_CANDIDATE.md` (SHA-256 `42a7a9f51afae7c059373b9048ed9b09c6b87c975705e54c485f2f6bfc133369`). The text is otherwise identical; the differences are in `release/amendment_issue_diff.txt`.

| Item | Value |
|---|---|
| Applies to | `../R4_20261028_preflight/03_R4_protocol_v1.md`, SHA-256 `f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab` (re-verified 2026-10-28; unchanged; not edited) |
| Revision | **rev2**, 2026-10-28. It replaces as a candidate, without modifying: rev1 `03_protocol_v1_amendment_1_DRAFT.md` (SHA-256 `f4ffc4b752e93dc3eedd6efc8b1bb03f490bc12d65ade36ce17cb2b3e84cb69e`) and rev0 `archive/rev0_20261028_0135/03_protocol_v1_amendment_1_DRAFT.md` (SHA-256 `faf25d80391d15ffc6dc54167b25bff0f931b61fd85e863a662f7902556d5f7f`) |
| Basis | the owner's decisions D1–D5 (2026-10-28, readiness task) and AMB-14, AMB-15, AMB-24 and the S2 gate rule (2026-10-28, this task), recorded in `09_owner_decision_record.md` |
| Integrity identifier | this file's SHA-256 is in `03_protocol_v1_amendment_1_rev2_CANDIDATE.sha256.txt` and in `zz_sha256_manifest_v3.csv`. It identifies the text only; it is not an approval |

The owner's decisions approve the methodological choices below. They are **not** an approval of this text. Approval requires the owner to review this candidate and issue it (§12).

---

## 1. D1 — No unregistered interior stops (§5.2, §5.3, §9(a))

- An S-eco trajectory is invalid if it is at rest at any knot strictly between a segment's departure and its arrival.
- Rest is allowed only at the segment endpoints and in the reference rest intervals.
- "At rest" means v ≤ 1e-9 m/s, the frozen §5.1 rule (`r3_lib.segments`); no other near-zero threshold is used.
- An invalid trajectory makes the scenario's profile **unavailable**. It is recorded and never replaced or re-planned.
- The validator decides from the knots alone; no planner status enters it.

D1 applies to planned trajectories. In the dynamic run, §8.2 decides.

## 2. D2 — Matched P3 plant; fixed P1-designed LQR gain (§4, §8.1)

For every P3 condition:
- Both arms run on the same P3 plant (SoH 0.8, k_r0 3.5), with the same motor branch, limit set and initial state (SoC 0.8, V1 = 0, at rest, integrator 0).
- Both use the R1 fixed Bryson gain designed on P1, unchanged.
- B0 tracks the baseline task v_b determined on P1; B3 tracks the S-eco profile designed on P1. Nothing is redesigned at P3.
- The gain does not depend on SoH, k_r0, R0, the limit set or the motor, so the P1 and P3 designs coincide bit for bit.

## 3. D3 — Early arrival and waiting only at registered stops (§5.2, §5.3)

- Each segment departs exactly at its reference departure ks·h.
- It arrives no later than its reference arrival ke·h.
- After an early arrival it stays at rest, at the registered stop, until the next reference departure.
- The trajectory starts at t = 0 and ends at exactly T_ref, at rest. The per-segment and total distances meet §9(b).
- Time comparisons are exact: **no timing tolerance**.
- Late arrival, early or late departure, or motion while waiting makes the trajectory invalid.

## 4. D4 — Development tests excluded from the 170 runs

- The smoke-test pair (`H3-slice-S1-M0-L-R1-P1-B0-dt1ms`, `…-B3-dt1ms`) and every readiness development check (`outputs/dev_readiness_*`, `outputs/dev_rev2_*`, pytest toy runs) are development tests.
- They never count toward the 170 official runs and are preserved unchanged.
- The equivalent configuration is executed afresh as `R4H3-INS-S1-M0-LR1-P1-B0-dt1ms` and `…-B3-dt1ms`.
- No energy difference is computed from any development test.

## 5. D5 and AMB-24 — Feasibility on P3: dynamic §8.2 decides; QS checks are diagnostic

**Formal feasibility** of a P3 branch is decided by the dynamic run's frozen §8.2 checks: valid, complete, tracking, stop compliance, constraint compliance.

**The QS screen.** For each P1-designed profile, the quasi-static step check on the P3 plant (`QSPlant.step`, the §5.2 notion) is a **diagnostic screen**:
- If it fails, the warning and the exact failing pieces (piece index, time interval, start and end speed) are recorded.
- The branch is **not** labelled infeasible on that ground alone.

**Both arms are always run and retained** when their profile exists.

**Classification of a condition**, in order:

| Order | Status | When |
|---|---|---|
| 1 | PROFILE_UNAVAILABLE | eco profile unavailable or rejected (D1, D3) |
| 2 | BASELINE_UNAVAILABLE | no baseline task |
| 3 | ERROR | an attempted run raised an exception |
| 4 | BASELINE_INFEASIBLE_ON_P3 | on P3: B0 fails §8.2. The comparison is **non-comparable for energy** |
| 5 | ECO_INFEASIBLE_ON_P3 | on P3: B3 fails §8.2. The eco branch is infeasible |
| 4–5 (P1) | B0_INVALID_EXCLUDED, INVALID_COMPARISON | the same failures at P1 (§8.1 labels) |
| 6 | RECOMPUTATION_DISAGREEMENT | §9: not credited until resolved by amendment |
| 7 | COMPARABLE | none of the above |

**What follows from the classification:**
- A paired ΔE_abs and ΔE_rel, always reported with trip time, is computed **only** for COMPARABLE conditions.
- The failed §8.2 criteria are recorded per arm.
- Every attempt and error is retained. Exceptions go to `errors.csv` and are never retried.
- Denominators list every status.
- An infeasible or invalid profile is never repaired by changing gains, the task, constraints or profile parameters.

## 6. AMB-14 — P1 gain fixed across sensitivity draws (§8.4)

- All 32 draws use the nominal gain designed on P1.
- Within a draw, B0 and B3 use that gain on the same plant realisation; v_b and S-eco are re-planned on that plant, as §8.4 requires.
- No draw is retuned.

The sensitivity set therefore assesses **robustness to plant-parameter uncertainty under a fixed controller**, not the best achievable result after retuning each plant.

## 7. AMB-15 — Campaign directory

**The directory.**
- Official runs are produced only in `verification/research_recovery_20261028/R4_20261028_campaign/`. It was verified absent and then created, with a directory plan and a not-released gate record only.
- At release it receives a hash-identical copy of `code/`, `config/` and `inputs/` from this pilot, its own clean test run and its own `logs/pre_run_hashes.txt` (§10.1).
- `run_campaign` refuses to run from any other directory.

**The issued amendment.**
- Location: `R4_20261028_campaign/release/03_R4_protocol_v1_amendment_1.md`, so the preflight directory is never written to.
- Approval record: `R4_20261028_campaign/release/amendment_1_approval.json`.

## 8. Canonical S1 and S2 sampled inputs

The sampled tasks were produced by R3's frozen `run_gates.reference()` (`np.interp` of the YAML knots at t = 0, 1, …, floor(duration)). They match R4 `task.load_task()` and all 24 hash-checked R3-retained references per cycle bit for bit (`05_cycle_input_provenance.md`).

| Path (in this pilot; copied unchanged at release) | SHA-256 |
|---|---|
| `inputs/cycles/S1_sampled_h1.csv` (325 samples, T_ref 324 s, d_ref 2161.0270 m) | `87151e5c30c02f5f6784732a5dd619fc6c39e90913d4afcf06292de2c1f2b7da` |
| `inputs/cycles/S2_sampled_h1.csv` (214 samples, T_ref 213 s, d_ref 531.5735 m) | `def9d757dc0923afe20a91dca487c84527daff2bef5421c34aef1a61f0a6e990` |
| `inputs/cycles/S1_source_segments.json` | `88a04c905fdd6a3b109e0189af0347c8d6525347ae4812228e7838162cb8d6fd` |
| `inputs/cycles/S2_source_segments.json` | `49093326473eb4d33dde34400a6dc741949d192e48fe25c81f1467683a0f2d13` |
| `inputs/cycles/S1_knots_from_yaml.csv` | `e0cdb1f4a4627838a8e691d4516492e604b01be85c2afa34c1ec98be8fd120ec` |
| `inputs/cycles/S2_knots_from_yaml.csv` | `4bf394980e928f075f7f82135aa11beba1b97b95a2d1e18ae030ea3c448dde6c` |
| `inputs/cycles/cycle_inputs_manifest.json` | `3d3d6e93d19842141691d041e2363dd8f3f9fef73b362ebcd6ae2ef8b6de7ea5` |

"Reference", "rest interval", "stop" and "segment" in §5, §6, §8 and §9 mean the canonical sampled task. Every campaign process re-verifies these hashes; any difference stops it.

## 9. Recomputation (§9): scope, gate, tolerances and the independent torque-limit check

**The gate** (decides crediting). Agreement between `runs.csv` and the evaluator for:

| Quantity | Tolerance | Source |
|---|---|---|
| E_chem, E_DC | 1e-4 relative | §9 |
| distance | 1e-6 relative | §9 |
| stop, completion, tracking and constraint flags | identical | §9 |
| **trip time** | **1e-9 s absolute** | proposed (A1-12) |
| **§8.2 C-rate I_over** | **1e-6 A·s absolute** | proposed (A1-12); rev1 proposed 1e-4 A·s, now tightened |
| **RMSE** | **1e-9 relative** | proposed (A1-12) |

The three proposed values are justified in `10_tolerance_approval_register.md`. Each is at least about 280 times its quantity's floating-point bound (derived and measured). Each is also far below the error it must detect:

| Quantity | Smallest structural error it must detect |
|---|---|
| Trip time | one trace sample, 1e-3 s: 10⁶ times the tolerance |
| RMSE | dropping one control instant, 1.5e-5 relative on S1: 1.5·10⁴ times the tolerance |
| I_over | a structural error can be arbitrarily small near zero exceedance, so the tolerance is set relative to the §8.2 decision threshold of 0.01 A·s: 1e-6 A·s is 10⁻⁴ of it. Decision identity is checked separately (`constraint_ok_equal`) |

None was chosen from an energy difference between arms or to make a test pass.

**Consequence if exceeded:** the run is flagged RECOMPUTATION_DISAGREEMENT and not credited until resolved by amendment (§9). The tolerances concern implementation validity only; they are not task-feasibility or outcome criteria.

**The recomputation process.** It runs in a separate process (`code/recompute_from_traces.py`) on the saved traces and per-run spec files only, and asserts that no simulator module was loaded.

**The independent torque-limit check** (`evaluator.torque_limits`):
- The evaluator computes the drive and regeneration torque limits itself: battery power limits at the C-rate, voltage-window and maximum-power currents, inverted through the loss law. Closed forms for M0 and M2; bisection on the forward law for M1.
- It uses its own limits for friction energy and the battery-limited fraction.
- Traced limits are only compared, as diagnostics: tolerance 1e-9 N·m for M0/M2 and 1e-5 N·m for M1, where `r3_lib` inverts the curve through a 3001-point table (measured table error ≤ 9.7e-7 N·m).

**Diagnostics never decide crediting.**

**Shared assumptions.** The simulator and the evaluator share:
- the declared model equations;
- the parameter values;
- the speed floor of 1e-6 rad/s;
- nominal-Q C-rate limits;
- the M1 curve file and its 1.5 × 18 kW domain.

They also share the integrated states (v, T, V1) read from the trace. **The recomputation verifies bookkeeping, integration, sampling, metric definitions and the torque-limit calculation; it does not validate the plant dynamics or the parameter values.** The owner accepts this scope by issuing this amendment (review item CR-A6 residual, `config/code_review_status_v2.json`).

## 10. S2's role and the ordered stop/go logic of the numerical checks

**S2 is used only for its preregistered purpose:**
- the held-out evaluation;
- the §9 checks that §9 places on S2 (grid convergence, the time step, and QS-versus-dynamic on S2 profiles).

S2 is never used to tune the planner, choose model parameters, select a tolerance, choose between planner designs or revise an acceptance criterion. Development checks use S1 or synthetic tasks only.

**Release** depends only on infrastructure. No S2 run is required before release.

**Ordered checks and their predetermined consequences:**

| # | Check | When | Criterion | If it fails |
|---|---|---|---|---|
| 1 | frozen and input hashes | every process start | equal to the frozen values | **STOP**: refuse to run (§9) |
| 2 | planner unit tests | release gate | all pass | **STOP**: do not release (§9) |
| 3 | infrastructure readiness | release gate | tests pass; recomputation and the 0.5 ms path work (S1 / synthetic) | **STOP**: do not release |
| 4 | planner optimality | each official planner job | S_max − S_found ≤ 0.2 pp | GO: the gap is the stated resolution (§9) |
| 5 | planner grid convergence | after the 6 S2 fine-grid jobs | \|ΔS_found\| < 0.2 pp | GO: results stated at the observed resolution (§9) |
| 6 | independent recomputation | every run | §9 of this amendment | GO: run not credited until resolved by amendment (§9) |
| 7 | QS vs dynamic | every B0 and B3 run | M0, M1: ≤ 1 % per reference km; M2 reported | GO: that motor branch is INCONCLUSIVE (§9) |
| 8 | dynamic time step | after the NOM L-EVE and CNV runs | \|ΔE_rel(0.5 ms) − ΔE_rel(1 ms)\| < 0.01 pp | GO: stated resolution (§9) |
| 9 | baseline sanity | S2 designs | v_b = v_ref checked and recorded | GO: shortfall and deviation reported |

**Rules for checks 4–9:**
- They are evaluated on the official run data, as reached.
- Their outcomes are reported with the results.
- They never cause a change to a planner setting, profile, controller, task, tolerance or the run list.
- No acceptance threshold is added or altered: every threshold in the table is the frozen §9 value.

## 11. The planned matrix: exactly 170 unique official runs

| Set | Runs | Definition |
|---|---|---|
| NOM | 12 | S2, P1, M0/M1/M2 × L-R1/L-EVE × B0/B3, 1 ms |
| P3 | 12 | S2 on P3, P1-designed profiles |
| INS | 12 | S1, P1 |
| CNV | 6 | S2, L-EVE, P1 at 0.5 ms (traced at 1 ms) |
| SEN | 128 | 32 draws × M0/M1 × B0/B3, S2, L-EVE, P1, nominal P1 gain |

- IDs follow `R4H3-<set>-[D<nn>-]<cycle>-<motor>-<limits>-<pstate>-<branch>-dt<1|0.5>ms`.
- None of these decisions changes the count. The dry run validates 170 unique official IDs, none equal to a smoke-test ID.
- The 82 planner jobs are QS only and are not runs.

**Unchanged** (§9 of rev1 applies):
- the protocol text;
- plant, motor bracket, limit sets, P-states and cycles;
- planner numerics;
- §8.2 criteria and the 1.0 % threshold;
- §8.1 decision rules;
- §9 checks.

Rev1's clarifications A1-3, A1-5, A1-7, A1-9 and A1-14 to A1-18 are carried over unchanged.

## 12. To issue (owner)

1. Review this candidate, `09_owner_decision_record.md`, `10_tolerance_approval_register.md` and `12_independent_gate_status_rev2.md`.
2. Copy the reviewed text to `R4_20261028_campaign/release/03_R4_protocol_v1_amendment_1.md` and set `"status": "APPROVED"` in the block below. Record its SHA-256 before any run.
3. Write `R4_20261028_campaign/release/amendment_1_approval.json` with: `approved_by`, `date`, `amendment_sha256` (of the issued file), `accepted_review_items: ["CR-A6 residual"]`, and `approved_tolerances` equal to the `recompute_tolerances` below.
4. Complete `11_campaign_release_checklist.md`. Only then can `run_campaign.py --execute` pass its preconditions.

## 13. Machine-readable block

`code/r4h3/campaign.py` reads this block. Every value must equal what the code implements: a difference or an unknown key is an error, never an override. No item is left open.

<!-- r4h3-amendment-block -->
```json
{
 "amendment": "R4 protocol v1 amendment 1 (candidate rev2)",
 "status": "APPROVED",
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
  "I_over_protocol_abs_As": 1e-06,
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
 "AMB_14_sensitivity_gain_basis": "nominal_P1",
 "AMB_15_campaign_directory": "R4_20261028_campaign",
 "AMB_24_p3_feasibility": "dynamic_8_2_decides; QS screen diagnostic only",
 "numerical_check_order": [
  "frozen_and_input_hashes",
  "planner_unit_tests",
  "infrastructure_readiness",
  "planner_optimality",
  "planner_grid_convergence",
  "independent_recomputation",
  "qs_vs_dynamic",
  "dynamic_time_step",
  "baseline_sanity"
 ],
 "note": "Approved by the project owner 2026-10-28 07:46:23 +0700 (amendment only). Campaign execution additionally requires release/campaign_authorization.json."
}
```
