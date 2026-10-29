# R4 H3 pilot: implementation and test report (Phases 4–5)

**Date:** 2026-10-28, 01:01–01:35 local time (UTC+7).
**Prepared by:** AI assistant (Claude); no human review.
**Directory:** `verification/research_recovery_20261028/R4_20261028_pilot/` (new; the name prescribed by protocol §10.1).
**Scope:** H3 only.
- No campaign run was started. The single vertical slice is an implementation smoke test, **not a result**.
- No energy difference between the arms was computed or reported.
- No claim is made about the thesis vehicle, SoH benefit or capacity fade.

## 1. Starting checks

| Check | Result |
|---|---|
| Protocol `03_R4_protocol_v1.md` SHA-256 vs freeze record | `f9826318…2dab` = `f9826318…2dab`: **match** (01:01, and again at gate and slice start) |
| Preflight file manifest (29 files) | 0 mismatches |
| Frozen code `r3_lib.py` | `c2403adc…1c97`: matches the value frozen in protocol §2.1 |
| M1 curve | `f872faa0…d1d9`: matches protocol §2.3 |
| Seven preflight tools | all auditors; none imported. `hash_tree.py` and `check_snapshot_manifest.py` were executed unchanged for the before/after checks |
| Pilot directory | absent before 01:02, then created |

## 2. Modules and provenance

All code lives in `code/r4h3/`. "Uses" lists what each module calls; nothing in R1–R3 was copied except where stated.

| Module | Component | Content | Provenance |
|---|---|---|---|
| `frozen.py` | — | paths and SHA-256 guard. `load_r3_lib()` imports the R3 physics only after its hash matches | new |
| `config.py` | D | P1/P3, L-R1/L-EVE, three labelled motor scenarios (ledger ID, provenance class, assumptions, validity limits, QS usability), numerics, §8.2 rules | Values from protocol §2.2–2.4, §5, §8.2. The limit sets equal R3 `run_gates.py`/`r3_pilot.py` (test-asserted). Motor models come from frozen `r3_lib.motor_models()`, never substituted |
| `task.py` | A (input) | the 1 s-sampled task: d_ref, T_ref, rest intervals, segments, D_k, T_k, v_lim,k, acceleration bounds | sampling as R3 `run_gates.reference()`; segments from `r3_lib.segments` |
| `validator.py` | A | exact checks on piecewise-linear trajectories: duration, start/end at rest, v ≥ 0, total and per-segment distance, rest-interval compliance, departure = reference departure, arrival ≤ reference arrival, extra stops (strict, AMB-02), segment and domain speed caps, acceleration bounds, QS feasibility of every piece | new |
| `planner.py` | B | baseline task v_b (`r3_lib.track_dp`, W 3/6/12, dv 0.05) and the S-eco planner (protocol §5): per-segment λ bisection on [−3, 6] (40 iterations), smallest λ with t_k ≤ T_k, Lagrangian bound, time-domain builder with departures at ks·h | DP kernels `r3_lib.eco_segment_tables` and `eco_segment_solve` (frozen); bisection and profile builder are new |
| `closedloop.py` | C | `simulate_traced`: a line-for-line port of `r3_lib.simulate` (n = 1) that records every 1 ms sample. Physics calls are the unmodified `r3_lib` functions. Gain: `eureka.controllers.gain(p_P1, "fixed")` for both arms | port of `r3_lib.py` lines 200–244; **bitwise-equal** to it in tests (§3) |
| `traces.py` | F | schema `r4h3-trace-v1`: 33 channels with units, descriptions and sources, plus required meta. Writer refuses missing or misaligned channels, NaN, missing meta and overwrites. Reader validates the schema | new; schema also in `config/trace_schema_v1.json` |
| `evaluator.py` | E | **no `r3_lib` or planner import.** Own loss (M0/M1/M2), current, window-limit and friction formulas from the protocol text. Trapezoid integration of the retained 1 ms trace; §7 metrics, §8.2 flags; comparison with simulator-side values; refusal to pool conditions | new |
| `slice.py`, `run_slice.py`, `record_gate.py` | — | slice driver with every stop condition of the brief; pre-run gate record (protocol §10.1) | new |

**Energy accounting** (`evaluator.py` docstring):
- Current i > 0 on discharge.
- Primary metric: net E_chem = ∫V_oc·i dt (propulsion positive, regeneration negative), divided by d_ref for Wh per reference km.
- Also computed: E_DC = ∫V_t·i dt; E_pos and E_neg separately.
- Auxiliary load 0 W (not modelled).
- η_regen = returned chemical energy / wheel braking work, kept separate from Wh/km.
- An incomplete, invalid or non-compliant run is flagged `comparable = False` and is never credited.

**Configuration and schema:** `config/scenarios_v1.json`, `config/trace_schema_v1.json`, and per run `outputs/…/run_config.json` (its SHA-256 is in every trace's meta).

## 3. Tests

Run with `python -I -B -m pytest -c code/pytest.ini` (local configuration, no cache, no bytecode).

| File | Tests | Covers (brief item) |
|---|---|---|
| `test_validator.py` | 16 | 1 distance and duration; 2 stop timing (motion in a stop, late arrival, early or late departure, early arrival with waiting accepted per §5.3, extra stop); 3 speed, acceleration, negative speed, QS feasibility; malformed input |
| `test_evaluator.py` | 13 | 5 sign convention and analytic integrals; 6 independent current and window-limit formulas equal `r3_lib` for M0/M1/M2; 4 incomplete (0.2 % short), tracking, stop-window and current-limit breaches flagged; disagreement detected; 9 pooling refused |
| `test_closedloop.py` | 12 | port **bitwise-equal** to `r3_lib.simulate` for M0/M1/M2 × L-R1/L-EVE; trace end = integrator state; 8 repeatability bitwise; fixed gain = R1 design; 6 trace-based recomputation agrees with the simulator for M0/M1/M2 |
| `test_frozen_and_task.py` | 8 | frozen hashes; wrong hash refused; nominal parameters = protocol §2.2; P-states and limits = §2.4; S1/S2 sampled d_ref and T_ref = §3; UDDS refused; toy task structure |
| `test_planner.py` | 7 | §9(d) DP = exhaustive enumeration; t_k ≤ T_k and weak duality; monotone energy vs time budget; time-infeasible reported, not replaced; §9(a–c) on a two-segment toy; determinism; baseline equals feasible reference |
| `test_traces.py` | 5 | 7 schema completeness, round trip, refusals |
| `test_scope.py` | 6 | 9 three distinct scenarios with labels and provenance, different losses, unknown ID refused; 10 no SoH scheduling, ageing or benefit fields in config, outputs or slice code |
| **Total** | **67** | |

**Results:**
- **Run 1** (`logs/pytest_run1.*`, 01:16): **64 passed, 3 failed.** All three failures were in `test_evaluator_recomputes_simulator_metrics_from_trace[M0/M1/M2]`: friction energy differed by 3–4e-4 Wh against a 1e-6 Wh tolerance.
  - **Cause:** an evaluator defect. Friction power depends on the zero-order-hold torque command, which jumps at each 10 ms control instant. A plain trapezoid mixes the old and new commands at those instants. Battery energy was unaffected, because current depends only on the continuous torque state.
  - **Fix:** integrate each 1 ms interval with the command held over it. The end value is recomputed independently from (u, t_neg, v), and the traced start value is checked against the same law.
  - **No tolerance was changed.**
- **Run 2** (`logs/pytest_run2.*`, 01:18): **67 passed, 0 failed, 0 skipped.** The gate record `logs/pre_run_hashes.txt` (01:20) binds this junit file, the protocol hash, the frozen-input hashes and the SHA-256 of every code and config file.

**Test limitations:**
- Planner tests use toy tasks; S2 is deliberately not touched by any test.
- The port-equivalence test uses a 4 s profile, not a full cycle.
- The evaluator is independent in its formulas, but the motor-limit channels `t_pos`/`t_neg` it uses for friction come from the trace (computed by `r3_lib.torque_limits`).
- Everything is single-author code with no human review.

## 4. Vertical slice

**Configuration:** S1 (in-sample), M0, L-R1, P1; B0 and B3; dt 1 ms; deterministic, no seed. Output: `outputs/slice_S1_M0_L-R1_P1/`.

**Why it was allowed to run:**
- Protocol hash matched.
- Gate record present and code unchanged since the clean test run.
- The open ambiguities could not affect this slice (`02_protocol_ambiguity_register.md`).
- Both trajectories were valid under the strictest reading before any dynamic run.

| Demonstration item (brief §6) | Evidence | Outcome |
|---|---|---|
| 1. Baseline task and eco trajectory loaded | `profiles.npz`, `planner_rows.csv` | v_b = sampled reference exactly (W = 3 m/s, no boundary hit). S-eco: 4 segments, every one "ok" |
| 2. Both pass validation | `trajectory_validation.json` | **both valid, 0 failures.** S-eco distance error −2.5e-11 m; departures exactly at 10, 53, 137, 289 s; arrivals 0.076–0.483 s before the reference (protocol-permitted waiting); 0 extra stops; max 11.79 m/s ≤ segment caps; acceleration within ±0.998 m/s² (bounds ±1.0) |
| 3. Same fixed LQR tracks both | `run_config.json` gain; `evaluation.csv` | identical K for both runs; RMSE and max \|e\| within §8.2 limits for both |
| 4. Runs complete without invalidating the task | `evaluation.csv`, `stop_compliance.csv` | both: simulator-valid, complete (≤ 0.1 %), tracking ok, constraint ok, finite. 5 of 5 tested stop windows with max \|v\| = 0.0 and 0.0 m travelled |
| 5. Raw signals retained | `trace_…-B0-dt1ms.npz` (33.9 MB), `trace_…-B3-dt1ms.npz` (31.1 MB) | 324,001 samples × 33 channels each, schema `r4h3-trace-v1`; read back from disk before evaluation |
| 6. Independent recomputation | `recomputation.json` | all 12 checks pass for both runs. Simulator vs evaluator: E_chem 6.1e-7 and E_DC 6.1e-7 relative (tolerance 1e-4); distance 1.5e-11 and 8.4e-11 relative (1e-6); trip time exact; RMSE agreement ≤ 3e-15; recomputed battery current and friction power differ by 0.0 |
| 7. Manifest and hashes | `manifest.json` | status **PASS**; no stops; no errors; frozen-input hashes; gate-record hash; config SHA-256; trace SHA-256; per-file output hashes; Python 3.14.7, numpy 2.5.4, scipy 1.18.1; wall time 413 s |

**Not done in the slice** (required later by protocol §9 for the campaign):
- the QS-vs-dynamic comparison per profile;
- planner grid convergence (2 m/0.1 vs 1 m/0.05);
- scenario-level S_max − S_found reporting;
- the 0.5 ms time-step repeat;
- the campaign runner and the 32-draw sensitivity design.

These are **not implemented yet**. Per-segment bounds are already written to `planner_rows.csv`.

## 5. Integrity

| Check | Result |
|---|---|
| Project files outside the pilot directory, before (01:02) vs after (01:33): SHA-256, size, mtime | 24,914 → 24,914; **0 added, 0 removed, 0 changed** (`logs/zz_pre_post_comparison.txt`). This covers the frozen protocol, preflight reports and manifest, R1–R3, `src/` and the thesis |
| Evidence snapshot vs manifest | 570/570 consistent; manifest SHA-256 `A93EB44F…F279` unchanged |
| Bytecode | no `__pycache__` or `.pyc` created anywhere (checked in the pilot directory, `src/` and the R1–R3 tree) |
| Git, installs, network, CNTT-02 | none used |

## 6. Status of the work

| Status | Items |
|---|---|
| Implemented and tested | Components A–F, gate record, slice driver |
| Passed | 67/67 tests (run 2); the vertical slice (all checks) |
| Failed and retained | run 1: 3 tests (friction integration defect, fixed in the evaluator) |
| Blocked or not started | the 170-run campaign (needs owner review of `03_protocol_v1_amendment_1_DRAFT.md`, at least AMB-02/-04/-06/-09/-13); campaign-level §9 checks (§4 above); H1, H2, H4, H5 |
