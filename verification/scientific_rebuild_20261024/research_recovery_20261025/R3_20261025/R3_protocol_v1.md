# R3 protocol v1: attainable-improvement gates and evidence-gated pilots

**Status:** FROZEN 2026-10-25 before any gate, pilot or comparative outcome was computed. The SHA-256 of this file and of every code and data file is in `logs/protocol_v1_sha256_at_freeze.txt`. `code/run_gates.py` refuses to run if this file's hash differs. This text is never edited after freezing. Changes go into separately named amendment files (`R3_protocol_v1_amendment_N.md`), issued before any run they affect.

**Supersedes** the unfrozen draft `R3_protocol.md` (kept unchanged). The draft had three faults:
1. It called dynamic-programming results "bounds" without the qualifications in §3.5.
2. Its exact-tracking baseline does not exist on UDDS (§3.3).
3. Its R3-A fixed-gain box did not cover the scheduled gain range (§5.1).

**What ran before freezing** (logs in `logs/`, none computes an outcome defined here):
- the FASTSim source extraction and audit (`R3_motor_curve_audit.md`);
- the implementation tests `code/test_r3.py`, `code/test_r3_supplementary.py` and `code/test_r3_v1_additions.py`;
- a feasibility count of exact tracking per scenario (`outputs/precheck_feasibility.csv`, infeasible-step counts only, no energy);
- a smoke run of `run_gates.py` on a synthetic profile (scratchpad, not retained as evidence).

One pre-existing test, `test_r3.py::test_band_dp_zero_band_is_reference`, internally runs the band DP on S2 at δ = 0.10 under M2. It asserts only an inequality and prints no value.

**Labels.**
- Every number is a simulation result for the R3 **reference plant** (`R3_model_basis.md` §3), not the thesis vehicle, whose battery is unidentified.
- The thesis's 12.5 % and 15.3 % are not targets and appear nowhere below.
- Prepared by the AI assistant that built R1 and R2; no human review.

---

## 1. Questions

- **Q-A, SoH scheduling on the same task.** Is the value of SoH information (VSI, §3.6) ≥ 1 % of energy per reference km on a held-out cycle?
- **Q-B, any same-task controller or supervisory layer.** Is there a feasible trajectory performing the same task (§3.4) that uses ≥ 1 % less energy per reference km than the baseline task trajectory?
- **Q-C, eco-driving (a different task).** How does energy per reference km change when the speed trajectory is re-planned between the reference's stops at equal distance, for travel-time allowances A ∈ {0, 2.5, 5, 10} %?
- **Q-D, degradation.** Not computed (§9).

## 2. Plant branches (fixed)

**Motor/inverter loss** (`r3_lib.motor_models()`, `R3_motor_curve_audit.md`). The branches are reported separately, never averaged or pooled:

| Branch | Model | Status |
|---|---|---|
| M0 | constant η = 0.874 (thesis), P_e = P_m/η motoring, P_m·η regenerating | baseline; thesis value unverified |
| M1 | η(\|P_m\|/18 kW) by linear interpolation of the FASTSim 3.1.0 generic e-machine curve (`data/motor_curve_m1_derived.json`), same rule both directions | illustrative (generic template shape) |
| M2 | L = k_c·T², k_c = 0.3592 W/(N·m)² | illustrative stress model, deliberately favourable to torque-smoothing control |

**Battery limits** (C-rate × 100 Ah; voltage window 2.5–3.65 V per 3.2 V):

| Limit set | Discharge / charge | Status |
|---|---|---|
| L-R1 | 3C / 1C | R1 assumption |
| L-EVE | 2C / 1C | generic EVE LF100 retailer summary (SEC), not the thesis cell |
| L-EVE-s | 2C / 1C × SoH | **exploratory**; never decides a gate |

**Plant states:**
- P1: SoH 1.0, k_r0 = 0.5.
- P2: SoH 0.8, k_r0 = 0.5 (R0 × 1.10).
- P3: SoH 0.8, k_r0 = 3.5 (R0 × 1.70).

The other parameters are R1's (`../../parameter_registry.csv`, thesis values, `report_unverified`). The plant is isothermal, with constant OCV 48 V. Initial state: rest, SoC 0.8, V1 = 0.

**Cycles.** S1 is in-sample, used for the convergence checks and R3-A tuning. S2 and UDDS are held-out. US06 is excluded.

## 3. Quasi-static evaluation and optimisers (`code/r3_lib.py`, `code/run_gates.py`)

### 3.1 Trajectory energy

A trajectory is a speed sequence v_0..v_N on a time grid with step h and constant acceleration within each step.
- **Energy:** net chemical energy ∫V_oc·i dt, by 3-point Gauss-Legendre per step with V1 = 0. These are the same force, torque, loss and current equations as the dynamic plant (`test_r3_supplementary.py::test_qs_and_dynamic_share_equations`).
- **Infeasible steps:** a step is infeasible where drive torque exceeds min(T_max, P_max/ω, battery-derived limit) at any Gauss node, or the battery equation has no real solution.
- **Braking:** braking beyond the motor or charge envelope goes to the friction brake.
- **Primary metric:** energy per **reference km** = E / d_ref, where d_ref is the trapezoidal distance of the sampled reference. Energy per actual km is reported alongside.

### 3.2 Discretisation (fixed)

- **Gate grid:** h = 1 s (all three cycles are piecewise linear with knots on whole seconds). Band speed step 0.01 m/s.
- **Baseline-task grid:** speed step 0.05 m/s.
- **Eco grid:** distance step 2 m, speed step 0.1 m/s.

### 3.3 Baseline task trajectory v_b

The exact reference is infeasible on UDDS in every scenario and on S1 under L-EVE (`outputs/precheck_feasibility.csv`). The baseline is therefore the **closest feasible trajectory**:

- **Definition:** v_b = argmin Σ_k (v_k − v_ref,k)² over v_k = v_ref,k + j·0.05 m/s with |j·0.05| ≤ W, v_k ≥ 0, and ends equal to the reference, subject to step feasibility. This is `r3_lib.track_dp`, a global optimum on its grid.
- **Window:** W = 3 m/s. If the optimal path touches ±W, it is recomputed with W = 6 m/s, then 12 m/s. A path still on the boundary is flagged.
- **Feasible references:** where the reference is feasible, v_b = v_ref exactly.
- **Energy:** E_b = E(v_b). The baseline's shortfall against d_ref and its RMS and maximum deviation from v_ref are reported.

v_b is energy-agnostic. It is the reference task made feasible, and stands for what a tightly tracking controller does at best.

### 3.4 Same-task band DP (Q-B)

Minimise E over:
- |v_k − v_b,k| ≤ δ at every sample (between samples the difference is linear in time, hence also within δ);
- equal duration;
- ends equal to v_b;
- every step feasible;
- distance ≥ d_b.

**Method:** Lagrangian min Σ(E − μ·s) by exact DP on the grid (`band_tables` and `band_dp_tab`), with μ found by bisection. This uses 40 iterations after bracketing, and keeps the smallest μ found with distance ≥ d_b.

**Bands:** δ ∈ {0.05, 0.10, 0.25, 0.50} m/s. **δ = 0.25 m/s is the gate band.** It is generous, since R2's tuned LQRs had RMSE < 0.10 m/s.

**Reported per scenario and δ:**
- H_found = 1 − E*/E_b, where E* is the energy of the trajectory actually returned (feasible, distance ≥ d_b);
- H_max = 1 − LB/E_b, where LB = max over the evaluated μ of [min Σ(E − μ s) + μ·d_b];
- H per actual km;
- friction energy, Ah, ∫i²dt;
- maximum deviation from v_b and from v_ref.

### 3.5 What these numbers are, and are not

- **E\* is a measured QS energy of a feasible trajectory.** H_found is a *lower* bound on the headroom of the discretised problem.
- **LB is a valid lower bound on the discretised problem's minimum**, by weak Lagrangian duality: for any μ ≥ 0 and any feasible grid trajectory with s ≥ d_b, E ≥ E − μ(s − d_b) ≥ min[Σ(E − μ s)] + μ d_b. The DP computes that minimum exactly (tested by exhaustive enumeration). H_max is therefore an *upper* bound on the discretised problem's headroom.
- **Neither number bounds the continuous problem.** Finer grids, other time steps and the dynamic plant (lag, V1) are not covered. Convergence (§8) is evidence, not proof.
- **A gate result is a screening result, not a theorem about all controllers.**

### 3.6 Value of SoH information (Q-A)

At δ = 0.25, for P ∈ {P2, P3}, on the band around v_b(P) with distance ≥ d_b(P):
- traj\*_P = the band DP result on plant P.
- traj\*_P1|P = the band DP result for the same band and distance, but on plant P1: the best SoH-1.0 design for the aged vehicle's task.

Then:
- **VSI_found** = 1 − min(E_P(traj\*_P), E_P(traj\*_P1|P)) / E_P(traj\*_P1|P).
- **VSI_max** = 1 − LB_P / E_P(traj\*_P1|P).

If traj\*_P1|P is infeasible on P, that is reported.

**Interpretation.** VSI is the energy value of knowing SoH when designing for the same task, with perfect preview, on the discretised QS problem. It is not a bound on the difference between two arbitrary controllers: a poorly tuned fixed controller can lose more. Fair tuning (§5.1) addresses that difference, and the band spread H bounds it from below.

### 3.7 Eco DP (Q-C; a different task)

Each moving segment between the reference's standstills (`r3_lib.segments`) is re-planned in the distance domain:
- **Ends:** start and end at rest.
- **Distance:** the segment's reference distance D, in N = round(D/2 m) equal steps.
- **Speed:** ≤ the segment's maximum reference speed.
- **Acceleration:** (v_b² − v_a²)/(2 Δs) within [min, max] of the reference's acceleration over the whole cycle.
- **Feasibility:** every step feasible as in §3.1.
- **Idle:** total idle time equals the reference's, with idle intervals kept in sequence.

**Method:** minimise Σ(E + λ t) with a common λ for all segments (exact DP per segment on the grid). λ is chosen by bisection on log₁₀λ ∈ [−3, 4] (30 iterations) for the lowest-energy supported trip with T_total ≤ (1 + A)·T_ref.

**Reported per allowance:**
- S_found = 1 − E_eco/E_b;
- S_max = 1 − LB/E_b, with LB = max over the evaluated λ of [E + λ(t − (T_target − idle))];
- trip time and its change, minimum achievable eco time;
- RMS and maximum deviation of the time-domain eco profile from v_ref;
- friction energy, Ah, ∫i²dt.

If no trip meets the time budget, that is reported as "time budget infeasible".

**VSI_eco at A = 0:** the P1-optimal trip's speed sequences are evaluated on P3 (same times), giving VSI_eco = 1 − min(E_P3*, E_P3(trip_P1))/E_P3(trip_P1).

### 3.8 Scenario grid

- **Band DP:** 3 cycles × {M0, M1, M2} × {L-R1, L-EVE, L-EVE-s} × {P1, P2, P3} × 4 δ.
- **VSI:** P2 and P3 for each (cycle, motor, limits).
- **Eco:** 3 cycles × {M0, M1, M2} × {L-R1, L-EVE} × {P1, P3} × 4 A, plus VSI_eco for P3.

Executed by `code/run_gates.py`, 6 worker processes. All rows are written, including infeasible ones.

## 4. Gates

Each gate is evaluated **per motor branch**, on held-out cycles (S2, UDDS) only. Only non-exploratory limit sets (L-R1, L-EVE) and states P1, P2 and P3 count.

| Gate | PASS for branch m if, in some qualifying scenario | Then |
|---|---|---|
| G-A | VSI_found ≥ 1 % | R3-A pilot (§5.1) for branch m |
| G-B | H_found(0.25) ≥ 1 % | R3-B pilot (§5.2) for branch m |
| G-C | S_found(0) ≥ 1 % or S_found(0.05) ≥ 1 % | R3-C pilot (§5.3) for branch m |

**Classification per branch and gate:**
- **PASS:** some qualifying found value is ≥ 1 %.
- **FAIL-certified-on-grid:** every qualifying *max* value (H_max, VSI_max, S_max) is < 1 %.
- **INDETERMINATE:** otherwise.

Only PASS launches a pilot. INDETERMINATE is reported, and no "no opportunity" claim is made for it.

Further rules:
- A scenario whose baseline is flagged (`track_hit_boundary`), or whose baseline shortfall exceeds 1 %, is reported but does not qualify.
- If a gate passes only under M2, the pilot may run, but any finding is labelled "stress-model only".
- **Decision robustness.** If a qualifying found value deciding a gate lies in [0.5 %, 2 %], that scenario is recomputed one-at-a-time with M ∈ {722.5, 977.5} kg, C_rr = 0.012 and R0_new ∈ {4, 6} mΩ (R1 registry ranges). Whether the decision flips is reported, and the frozen decision is not changed.

## 5. Pilots (deterministic; dynamic plant `r3_lib.simulate`, RK4 1 ms, ZOH 10 ms)

General rules:
- Every run is written: valid, invalid or failed.
- A run is **invalid** for a non-finite state, an infeasible battery solution, or closure > 1e-3 of throughput.
- A run is **complete** if its distance shortfall against d_ref is ≤ 1 %.
- Tracking metrics are computed against the profile the controller tracks, and also against v_ref.
- Reported per run: E, Wh per reference km and per actual km, distance, trip time, RMSE, max |e|, battery-limited time fraction, I_over, friction energy, regeneration, Ah, ∫i²dt, peak and RMS current, closure.

### 5.1 R3-A (only on G-A PASS)

F vs S on the passing branch and limit set.
- **Scheduled family:** R2's (`../pilot_protocol.md` §4): log₁₀σ ∈ [−0.6, 0.3], log₁₀c ∈ [−2, 1], γ_v and γ_u ∈ [0, 10].
- **Fixed family:** widened so that it covers every gain the scheduled family can reach at SoH 0.8: log₁₀σ ∈ [−0.6, 0.3], log₁₀c ∈ [−2, 1.48], and a torque-weight multiplier q_T with log₁₀q_T ∈ [−0.48, 0]. Its Q is diag(1/(0.5σ)², q_T/85², 1/0.5²).
- **Budget:** 24 Latin-hypercube candidates per branch (scipy qmc, seed 20261025, scrambled).
- **Tuning:** S1 on P1 and P3. Feasibility requires shortfall ≤ 1 %, RMSE ≤ 0.10 m/s and max |e| ≤ 1.0 m/s in both runs. Selection is by minimum mean energy per reference km.
- **Evaluation:** S2 and UDDS × P1, P2, P3.
- **Improvement rule:** ΔE ≤ −1 % per reference km, RMSE ratio ≤ 1.10, both runs complete, on a held-out cycle, in more than one motor branch.

### 5.2 R3-B (only on G-B PASS)

F0/S0/F1/S1 exactly as R2 (`../pilot_protocol.md` §2 and §4), with the fixed family widened as in §5.1. The layer is identical for F1 and S1.
- **Effects:** the main effects (layer: F1−F0 and S1−S0; scheduling: S0−F0 and S1−F1) and the interaction (S1−F1) − (S0−F0) are reported separately.
- **Credit:** scheduling is credited only with S−F at equal layer.

### 5.3 R3-C (only on G-C PASS)

- **Controller:** R1's fixed Bryson LQR gain (`eureka.controllers.gain(p, "fixed")`), with no tuning.
- **Profiles tracked:** (i) v_b, the baseline task; (ii) the eco profile for A = 0; (iii) the eco profile for A = 5 %. Profiles (ii) and (iii) come from `outputs/gates/paths/`.
- **Scenarios:** S2 and UDDS × {L-R1, L-EVE} × P1, for each passing branch. That is 12 runs per branch.
- **Requirements per run:** valid; RMSE ≤ 0.10 m/s against the tracked profile; complete.
- **Outcome:** ΔE = eco − baseline per reference km, always reported with the trip-time change, as an energy-time trade-off.
- **Scenario exclusion:** if the baseline run fails its requirements, the scenario is reported and excluded from the pilot conclusion.

## 6. Outcomes and denominators

- **Primary:** energy per reference km (net V_oc·i).
- **Relative change:** ΔE % = 100·(E_a − E_b)/E_b per reference km, with b named in each table.
- **Secondary:** per-actual-km energy, distance, trip time, tracking errors, friction energy, Ah, ∫i²dt, peak current and battery-limited fraction.
- **Stress indicators:** Ah and ∫i²dt are stress indicators, **not** capacity fade.

## 7. Practical threshold and attribution

- **Threshold:** 1 % of energy per reference km.
- **Credited gains:** a gain obtained by poorer tracking (outside the band or the requirements), shorter distance (below d_b or incomplete), or a violated constraint is not credited.
- **Eco attribution:** eco savings are attributed to the changed driving task (an energy-time trade-off), never to SoH scheduling. Only VSI_eco can be attributed to SoH.
- **Motor-model attribution:** an effect that appears in M1 or M2 but not M0 is attributed to the loss model, not to control.

## 8. Numerical validity (fixed before running)

| Check | Case | Criterion |
|---|---|---|
| Band discretisation | S1, M2, L-EVE, P3, δ = 0.25: (h 1 s, dv 0.01) vs (0.5 s, 0.005) | \|ΔH_found\| < 0.05 pp |
| Eco discretisation | S1, M2, L-EVE, P1, A = 0 and 5 %: (2 m, 0.1) vs (1 m, 0.05) | \|ΔS_found\| < 0.2 pp |
| Duality gap | every gate row | reported; it decides PASS / FAIL / INDETERMINATE (§4) |
| Pilot time step | per passing branch: UDDS (else S2), L-EVE, the three profiles at dt 0.5 ms | every reported ΔE changes by < 0.01 pp |
| QS vs dynamic | each pilot profile: QS energy of the profile vs the dynamic run tracking it | ≤ 1 % per reference km |
| Independent recomputation | each pilot run: E from the E_chem state vs ∫V_oc·i assembled from E_pos + E_neg | ≤ 1e-6 relative |

A failed criterion is reported, and the affected quantity is then stated only to the resolution demonstrated. Solver settings are not changed after results are seen, except by a dated amendment.

**Failed or missing runs.** A task that raises is written to `outputs/gates/errors.csv` with its traceback. It is not silently retried. A rerun requires an amendment stating the cause and the fix.

## 9. Degradation (Q-D)

No fade law is applied (`R3_model_basis.md` §4):
- every candidate law is for a different cell and format;
- no coefficients were read from primary full text;
- no dataset is downloaded.

Ah throughput and ∫i²dt are reported as stress indicators only.

## 10. Falsification statements (fixed)

- **H-A:** SoH information is worth ≥ 1 % on the same task. *Falsified on the grid* if G-A is FAIL-certified-on-grid for every branch. *Not supported* if it is FAIL or INDETERMINATE everywhere.
- **H-B:** some same-task trajectory saves ≥ 1 %. Same rule with G-B.
- **H-C:** re-planning saves ≥ 1 % at A ≤ 5 %. Falsified if S_max(0.05) < 1 % on every qualifying held-out scenario of every branch.
- **R3-C pilot:** falsifies the DP eco result for a scenario if the LQR cannot meet the requirements on the eco profile, or if the simulated saving is opposite in sign to S_found or less than half of it.

## 11. Amendments

None at freezing. Amendments are separate files (header of this document).
