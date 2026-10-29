# R4 H3 pilot: implementation plan (Phases 4–5)

**Date:** 2026-10-28, from 01:01 local time (UTC+7).
**Prepared by:** AI assistant (Claude); no human review.
**Governing protocol:** `../R4_20261028_preflight/03_R4_protocol_v1.md`. Its SHA-256 `f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab` was re-verified at 01:01 and matches the freeze record. The 29-file preflight manifest `zz_R4_file_manifest.csv` was re-verified with 0 mismatches.

**Scope:** H3 only. No campaign. At most one vertical slice (§7). H1 stays unscheduled; H2, H4 and H5 stay blocked. No legacy percentage is used anywhere.

## 1. Directory and write boundary

| Item | Value |
|---|---|
| Implementation directory | `verification/research_recovery_20261028/R4_20261028_pilot/`. This is the name protocol §10.1 prescribes; it did not exist before 01:02 (checked) |
| Written only there | `code/r4h3/` (package), `code/tests/`, `config/`, `logs/`, `outputs/` and the reports |
| Never written | the preflight directory, R1–R3, `src/`, the snapshot, the thesis and everything else. A pre-work hash of 24,914 project files (`logs/zz_pre_hash_project.csv`) is compared after the work |
| Bytecode | Every Python call uses `-B`, and the package sets `sys.dont_write_bytecode`. Importing `r3_lib` would otherwise create `__pycache__` inside the R3 tree, which has none today |
| pytest | run with a local `pytest.ini` (`-c`) and `-p no:cacheprovider`, so the project's `pyproject.toml` settings and `.pytest_cache` are not used |

## 2. The seven preflight tools

All seven are **auditors**: read-only checks of past artefacts. None is meant for implementation, and none is imported by the pilot. `hash_tree.py` is *executed* (unchanged) for the before/after file comparison.

| Tool | Role |
|---|---|
| `check_snapshot_manifest.py` | snapshot and source hash auditor |
| `hash_tree.py` | tree hash and comparison (re-used as a tool) |
| `verify_r1_r3_records.py` | R1–R3 hash-record auditor |
| `describe_r3c_stop_compliance.py` | descriptive stop analysis of saved R3 paths |
| `recompute_r3c.py` | arithmetic on R3-C raw rows |
| `recheck_soh_headlines.py` | arithmetic on R1/R2/R3-B tables |
| `spot_check_transcripts.py` | transcript line check |

## 3. H3 experiment extracted from the frozen protocol

### 3.1 Comparison
- **B0:** R1 fixed Bryson LQR `eureka.controllers.gain(p, "fixed")` with p at P1, tracking **v_b**, the closest feasible trajectory to the 1 s-sampled reference (`r3_lib.track_dp`, W ∈ {3, 6, 12} m/s, dv 0.05 m/s).
- **B3:** the identical gain, tracking the **S-eco** profile (§5).
- **Independent variable:** the tracked profile only. There is no SoH logic, no retuning and no layer (§4, §6).

### 3.2 Task constraints

| Constraint | Protocol source | Value / rule |
|---|---|---|
| Cycles | §3 | **S2 = primary held-out** (d_ref 531.574 m, T_ref 213 s; this is the "0.53 km" cycle); **S1 = in-sample** for planner and solver checks (2161.027 m, 324 s). One held-out plus one in-sample cycle. UDDS, US06 and HWFET are excluded |
| Reference | §3 | **the reference sampled at h = 1 s**; d_ref is the trapezoidal distance of the samples. See ambiguity AMB-01: the YAML profiles are 0.3–0.9 s longer and have off-grid knots |
| Distance | §5.1–5.2, §6 | eco covers D_k exactly in each segment (assert within 1e-9 m) |
| Total time | §6 | T_ref for both arms (departures fixed in time; final idle as in the reference) |
| Stop locations | §5.2–5.3 | the reference stop locations (follows from D_k per segment) |
| Stop times | §5.3 | **at rest throughout every reference rest interval.** Departure at exactly ks_k·h; arrival ≤ ke_k·h (t_k ≤ T_k). **Early arrival followed by waiting is permitted by the protocol.** No other tolerance exists; R3-C's ≈ 0.3 s tolerance is **not** used |
| Trajectory-level stop test | §9 (a) | at rest at every reference-rest sample and at every eco knot inside a reference rest interval (zero tolerance) |
| Run-level stop test | §8.2 | for every reference standstill of ≥ 2 s: \|v\| ≤ 0.05 m/s on [t_a + 1 s, t_d], and distance ≤ 0.10 m in that window |
| Speed | §5.2 | v ≤ v_lim,k (the segment's reference maximum) and v ≥ 0; the 0–50 km/h domain (`02_model_basis.md`) is also checked |
| Acceleration | §5.1 | within [min, max] of the 1 s differences of the sampled reference (R3 `eco_setup`) |
| Feasibility | §5.2 | every constant-acceleration piece feasible per `QSPlant.step` at P1 for the scenario's motor branch and limit set |
| Initial / terminal | §2.2 | rest, SoC 0.8, V1 = 0 at t = 0; at rest at T_ref |
| Extra intermediate stops | **not specified** | AMB-02. The validator applies the strictest reading (none allowed) |

### 3.3 Planner (§5)
- Distance step: N_k = max(round(D_k / 2 m), 2).
- Speed grid: `linspace(0, v_lim,k, round(v_lim,k / 0.1) + 1)`.
- Per segment: minimise Σ(E + λ_k·t), with λ_k bisected on log₁₀λ ∈ [−3, 6] over 40 iterations, keeping the smallest λ_k with t_k ≤ T_k. Infeasible at λ = 10⁶ → "profile unavailable".
- Per-segment Lagrangian bound: LB_k = max over evaluated λ of [E + λ(t − T_k)].

### 3.4 Energy accounting (§7)
- **Primary boundary:** E_chem = ∫V_oc·i dt, with i > 0 on discharge and regeneration netted; aux load 0 W.
- **Normalisation:** e = E_chem/d_ref (Wh/km), reporting ΔE_abs and ΔE_rel separately.
- **Secondary:** E_DC = ∫V_t·i dt and the §7.2 set.
- **Regenerative braking:** η_regen = |∫min(V_oc·i, 0)| / ∫(P_regen,wheel + P_friction), kept separate.
- **Not computed:** no fade quantity (§7.4).

### 3.5 Motor-loss scenarios (§2.3)
- M0: constant η 0.874.
- M1: FASTSim template curve (`motor_curve_m1_derived.json`, SHA-256 `f872faa0…d1d9`), labelled illustrative.
- M2: k_c·T² with k_c = 18000(1/0.874 − 1)/85², taken from dynamic runs only.

All three are built by `r3_lib.motor_models()` (frozen, SHA-256 `c2403adc…1c97`). They are kept separate everywhere.

### 3.6 Run design (§10.6, 170 dynamic runs; **none started in this task**)

| Set | Cycle | State | Motor × limits | Arms | dt | Runs |
|---|---|---|---|---|---|---|
| Nominal (decisive) | S2 | P1 | 3 × {L-R1, L-EVE} | B0, B3 | 1 ms | 12 |
| Secondary | S2 | P3 (P1-designed profile) | 3 × 2 | B0, B3 | 1 ms | 12 |
| In-sample | S1 | P1 | 3 × 2 | B0, B3 | 1 ms | 12 |
| Time-step check | S2 | P1 | 3 × L-EVE | B0, B3 | 0.5 ms | 6 |
| Sensitivity | S2 | P1 | {M0, M1} × L-EVE, 32 LHS draws | B0, B3 | 1 ms | 128 |

- **Seed:** `LatinHypercube(d=7, rng=default_rng(20261028))` for the draws only. Everything else is deterministic.
- **Raw output:** 1 ms traces for every run, `runs.csv`, `manifest.json`, planner knots and `planner_rows.csv`, `errors.csv`.

## 4. Module boundaries

| Module | Component | Responsibility | Uses |
|---|---|---|---|
| `r4h3/frozen.py` | — | locate and hash-check the protocol, `r3_lib.py` and the M1 curve; import `r3_lib` only after the check passes | hashlib |
| `r4h3/config.py` | D | P-states, limit sets, the three motor scenarios with provenance and validity notes, numerical settings, validity thresholds; writes `config/scenarios_v1.json` | `r3_lib.motor_models`, `rebuild.model.BatteryLimits` |
| `r4h3/task.py` | A (input) | the sampled reference task: samples, d_ref, T_ref, rest intervals, segments, D_k, T_k, v_lim,k, acceleration bounds | `rebuild.run.load_cycle`, `r3_lib.segments` |
| `r4h3/validator.py` | A | trajectory validity (§3.2) for v_b and S-eco knots; returns every failure, never repairs | `r3_lib.QSPlant.step` (feasibility only) |
| `r4h3/planner.py` | B | the baseline task v_b and the S-eco planner (§3.3); no SoH, no controller | `r3_lib.track_dp`, `eco_segment_tables`, `eco_segment_solve` |
| `r4h3/closedloop.py` | C | `simulate_traced`: a line-for-line port of `r3_lib.simulate` (n = 1) that records every 1 ms sample, using `r3_lib`'s unmodified `rk4_step`, `derivatives`, `torque_limits` and `battery_current`. Tested to equal `r3_lib.simulate` exactly | `r3_lib`, `eureka` |
| `r4h3/traces.py` | F | versioned schema `r4h3-trace-v1`, writer (refuses incomplete or non-finite data), reader | numpy |
| `r4h3/evaluator.py` | E | recomputes every metric from the trace using **its own** loss, current and battery-limit formulas (no `r3_lib` import), and compares with the simulator-side values | numpy, json |
| `r4h3/slice.py` | — | runs the vertical slice with every stop condition of the brief; never computes ΔE | all of the above |

## 5. Test strategy (before any execution)

`code/tests/`, run with pytest. Every test checks a general property; none asserts a savings value.

| # | Brief item | Tests |
|---|---|---|
| 1 | distance and duration | validator on synthetic tasks: exact copy passes; shortened distance, shortened or extended duration fail |
| 2 | stop time and duration | motion inside a rest interval fails; late arrival fails; early departure fails; early arrival with waiting passes (protocol §5.3); extra mid-segment stop flagged |
| 3 | speed and feasibility | speed above v_lim,k fails; acceleration outside bounds fails; negative speed fails; a QS-infeasible piece fails |
| 4 | invalid or incomplete rejection | evaluator: 0.2 % shortfall → not complete; RMSE breach; stop-window breach; I_over breach; non-comparable pair not credited |
| 5 | sign convention and integration | analytic constant, sign-changing and sinusoidal currents; trapezoid exactness on linear signals |
| 6 | evaluator agreement | evaluator's own current formula equals `r3_lib.battery_current` for M0/M1/M2 on random states; trace-based energy and distance agree with integrator states on a short closed-loop run (1e-4 / 1e-6) |
| 7 | schema completeness | writer rejects a missing channel, length mismatch or NaN; round-trip preserves schema and meta |
| 8 | repeatability | two identical short simulations are bitwise equal; planner output identical twice |
| 9 | scenario separation | three distinct scenario IDs and loss behaviours; evaluator dispatches by ID; pooling helper refuses mixed motors |
| 10 | no SoH or fade claims | H3 configs use P1/P3 only, the fixed gain only, no scheduled weights, no ageing keys; slice outputs contain no fade or SoH-benefit fields |
| — | frozen inputs | wrong protocol or `r3_lib` hash → refuse; nominal parameters equal protocol §2.2 |
| — | port equivalence | `simulate_traced` end state and accumulators equal `r3_lib.simulate` bitwise for M0/M1/M2 × L-R1/L-EVE on a short profile |
| — | planner DP | per-segment DP equals exhaustive enumeration on a toy grid (§9 d); S-eco at rest in every reference rest interval; D_k reproduced; t_k ≤ T_k |

Failed tests and their messages are kept in `logs/`.

## 6. Unresolved protocol questions

Details are in `02_protocol_ambiguity_register.md`.
- **AMB-01:** sampled vs exact reference.
- **AMB-02:** extra intermediate stops.
- **AMB-03:** definition of I_over.
- **AMB-04:** which plant state v_b uses at P3.
- **AMB-05:** "as implemented in `r3_lib`" for the limit sets (they are defined in the R3 scripts).
- **AMB-06:** the brief vs the protocol on early arrival.

Each is classified there as determined by the protocol text, or as open with a proposed addendum.

## 7. Vertical slice (only if every check passes)

**Choice: S1, M0, L-R1, P1, B0 + B3, dt 1 ms (two dynamic runs).**
- **S1, not S2:** S1 is the protocol's in-sample cycle for "planner and solver checks" (§3). Using it leaves the held-out S2 untouched before the campaign.
- **M0:** the simplest loss model.
- **L-R1:** the sampled S1 reference is feasible there (R3), so v_b should equal v_ref; this is checked, not assumed.
- **Status of the two runs:** they are 2 of the 12 planned in-sample runs. They are labelled a smoke test.

**Run only if all hold:**
- the protocol and code hashes are recorded in `logs/pre_run_hashes.txt` and still match at start;
- every test passes;
- both trajectories pass the validator under its strictest reading, so the open ambiguities AMB-02 and AMB-06 cannot change their validity;
- the output directory is new.

**Not done:** no ΔE, no saving percentage, no S_found discussion in any report. The planner's internal QS totals are stored as the protocol requires (§5.4), but not interpreted.
