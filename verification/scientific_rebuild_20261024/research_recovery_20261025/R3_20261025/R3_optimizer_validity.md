# R3 optimiser validity (Step 4)

**Code:** `code/r3_lib.py` (frozen SHA-256 `c2403adc…1c97`). **Protocol:** `R3_protocol_v1.md` §3. **Tests:** `R3_test_report.md` rows 10–12.

## 1. Common evaluation model

Every optimiser scores a trajectory with `QSPlant.step` and nothing else:
- constant acceleration per step;
- 3-point Gauss-Legendre in time;
- V1 = 0;
- the same force, torque, loss, current and limit equations as the dynamic plant (`test_qs_and_dynamic_share_equations`: identical current, acceleration to 1e-16);
- energy = net chemical ∫V_oc·i dt, where positive means discharge and regeneration is negative.

A step is **infeasible** (cost +∞) if, at any of its three nodes:
- the drive torque exceeds min(T_max, P_max/ω, the battery-derived limit, which is the discharge-current or voltage-window limit mapped through the motor model);
- the discharge current exceeds i_d;
- the battery quadratic has no real root.

Braking beyond min(T_max, P_max/ω, the charge-current/voltage limit) is never infeasible: the excess goes to the friction brake, and its energy is recorded.

**Not represented** in any optimiser:
- the torque lag τ_T = 20 ms and the RC voltage V1 (both present in the dynamic pilot);
- **jerk** (no optimiser constrains it);
- temperature;
- OCV(SoC).

## 2. The three optimisers

| | `track_dp`: baseline task | `band_*`: same-task band DP | `eco_*` and `EcoSolver`: eco DP |
|---|---|---|---|
| Decision variables | v_1..v_{N−1} on the reference time grid (h = 1 s), v_k = v_ref,k + j·0.05 m/s | v_1..v_{N−1}, v_k = v_b,k + j·0.01 m/s | per moving segment, speeds at N + 1 equally spaced distance points (Δs ≈ 2 m), on a 0.1 m/s grid |
| Objective | Σ_k (v_k − v_ref,k)² | min E subject to distance; solved as min Σ(E_k − μ s_k) | min E subject to time; solved as min Σ(E + λ t) with one λ for all segments |
| Feasible set | \|v_k − v_ref,k\| ≤ W (W = 3, 6 or 12 m/s; widened if the path touches the edge); v ≥ 0; every step feasible (§1) | \|v_k − v_b,k\| ≤ δ at samples (and so between them, both being linear); v ≥ 0; every step feasible | 0 ≤ v ≤ segment max reference speed; (v_b² − v_a²)/(2Δs) within the reference's [a_min, a_max]; every step feasible; no 0 → 0 step |
| Initial / terminal | v_0, v_N equal to the reference (rest) | v_0, v_N equal to v_b | v = 0 at both ends of every segment |
| Time | equal to the reference by construction | equal to the reference by construction | T_total = Σ t + idle ≤ (1 + A)·T_ref; idle time as the reference |
| Distance | not constrained (catch-up arises from minimising error); shortfall reported, and a baseline with > 1 % shortfall does not qualify for a gate | Σ s ≥ d_b (distance of v_b) | each segment exactly its reference distance D |
| Tracking tolerance | none (W only bounds the grid) | δ ∈ {0.05, 0.10, 0.25, 0.50}; gate δ = 0.25 | none: a different task. RMS and maximum deviation from v_ref are reported |
| Torque, power, current, voltage, regeneration | §1 | §1 | §1 |
| Speed / acceleration limits | through the envelope only | band plus envelope; braking harder than the reference is allowed (friction absorbs it) | explicit, as above |
| Solver | exact backward-indexed DP on the grid (`argmin` per stage) | exact DP for fixed μ; μ by bracketing (×4 from 1 until distance ≥ d_b, abort at 1e6) and then 40 bisection steps; keeps the smallest μ satisfying distance | exact DP per segment for fixed λ; log₁₀λ ∈ [−3, 4] by 30 bisection steps; keeps the smallest λ meeting the time budget |
| Stopping | single pass | fixed iteration count | fixed iteration count |
| Feasibility check | path re-evaluated by `evaluate` (feasible flag reported) | the returned path is re-evaluated; distance asserted | the trip time is checked against the budget; time-domain profile reconstructed by `eco_profile` |
| Certified on the grid? | **yes**: global optimum of its grid problem (tested by enumeration) | the DP for fixed μ is a global optimum (tested). The **distance-constrained** result is a supported point of the Lagrangian, not necessarily the constrained grid optimum (test: found 1210.5 J vs exact 1199.7 J) | the DP for fixed λ is a global optimum (tested). The time-constrained result is a supported point (same caveat) |

## 3. Four different things, kept separate

| Quantity | What it is | Symbol in the outputs |
|---|---|---|
| A feasible trajectory and its simulated energy | any returned path, re-evaluated by `QSPlant`. It is a real member of the feasible set, and its energy is a measured QS value | `E_star_Wh`, `E_eco_Wh` |
| The best solution found | the same thing. Because of the supported-point issue, it can be worse than the grid optimum; it is never called the theoretical best | `H_found_pct`, `S_found_pct`, `VSI_found_pct` |
| A certified lower bound on achievable energy | **on the discretised QS problem only**. Weak duality gives, for any μ ≥ 0 and any feasible grid path with s ≥ d_b: E ≥ E − μ(s − d_b) ≥ min_grid Σ(E − μ s) + μ d_b. The minimum is computed exactly by the DP, and the bound is the maximum over every μ evaluated. The same argument with λ(t − τ) applies to the eco DP. Verified against enumeration in three tests | `lb_Wh` |
| A certified upper bound on savings | 1 − LB/E_b, again on the discretised QS problem only | `H_max_pct`, `S_max_pct`, `VSI_max_pct` |

**What is not certified:**
- **The continuous problem.** Arbitrary speeds, finer time steps, the dynamic plant with lag and V1, and controllers that change the trajectory between samples are not covered by LB. A finer grid can only lower the grid minimum: the coarse grid's speed set is contained in the finer one when the time step is unchanged and dv halves. So LB from a coarse grid is not a bound for the fine grid. The convergence checks (protocol §8) measure how much the found values move under refinement. That is evidence about the continuous problem, not proof.
- **Controllers outside the trajectory picture.** Under M0, M1 and M2, at a given realised speed trajectory the operating point (T, ω), the battery current and every loss are fixed, apart from the regeneration/friction split. Both the QS model and the dynamic plant use motor braking up to the limit and friction for the rest.
  - Under **M0 and M1** this is energy-optimal, because regeneration always returns η·|P_m| > 0.
  - Under **M2** it is not. The battery return Tω − k_c T² is maximised at T* = ω/(2k_c) (81 N·m at 2.5 m/s), so below about 2.5 m/s, blending in friction earlier would return more energy. Below about 0.5 m/s, motor braking at typical torques even costs battery energy. That split is a small lever the R3 optimisers do not search. Its size is checked after the gates as a labelled post-freeze check (`R3_gate_results.md`).
  - Apart from that lever, a controller can only change energy by changing the trajectory, so the trajectory picture covers every controller *within the QS model*.
  - Lag and V1 introduce small dynamic differences, which the pilot measures where it runs.
- **Value of information vs controller differences.** VSI bounds what SoH knowledge adds to an optimal same-task design. It does not bound the energy difference between two particular controllers, one of which may simply be tuned worse; that is what equal-budget tuning in a pilot addresses.

## 4. Interpretation rules (protocol §4, restated)

- **PASS** needs a found value ≥ 1 %, i.e. a demonstrated feasible trajectory.
- **FAIL-certified-on-grid** needs every max value < 1 %.
- **INDETERMINATE** otherwise. No "impossible" claim is made, and no pilot is launched.
- A saving obtained outside the band, below the required distance, or beyond a constraint is impossible by construction in the band DP. In the eco DP, a saving bought with longer trip time is always reported with that time.

## 5. Known limitations carried into the results

1. **No jerk limit.** Eco profiles may change acceleration abruptly. Only the R3-C pilot, with an LQR tracking through a 20 ms torque lag, tests whether they are realisable.
2. **Supported-point gap.** It can make found values pessimistic. The dual bound brackets it and decides INDETERMINATE.
3. **Eco "time budget infeasible"** is judged at the fastest trip found (λ = 10⁴ W, `t_min_eco_s`). A trip slightly faster than that could exist on the grid. This only matters if the budget lies between the two.
4. **The baseline for UDDS** is the closest feasible trajectory (an assumption about what "the task" is when the reference cannot be driven). It is reported with its deviation from the reference.
5. **Regeneration/friction split not optimised under M2** (§3).
6. **V1 = 0** in all optimisers. R1's RC loss is 0.02–0.36 % of energy, below the 1 % threshold but not negligible against small differences.
