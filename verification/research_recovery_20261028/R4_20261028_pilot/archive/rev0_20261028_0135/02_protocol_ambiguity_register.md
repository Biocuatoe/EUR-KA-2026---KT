# R4 H3 pilot: protocol ambiguity register

**Date:** 2026-10-28. **Prepared by:** AI assistant; no human review.
**Protocol:** `../R4_20261028_preflight/03_R4_protocol_v1.md`, SHA-256 `f9826318…2dab` (verified; not edited).

**Classification:**
- **DETERMINED:** the frozen text decides the question, possibly by its explicit numbers; any wording problem is editorial.
- **OPEN:** the frozen text does not decide it.
- **Slice:** whether the item could change the validity of the one vertical slice.
- **Campaign:** whether it must be resolved before the 170-run campaign.

Proposed wording for every OPEN item, and clarifications for the DETERMINED ones, is collected in `03_protocol_v1_amendment_1_DRAFT.md`. That file is **DRAFT — not issued, not frozen, not reviewed.**

| ID | Question | Evidence | Class | Implementation choice | Slice | Campaign |
|---|---|---|---|---|---|---|
| **AMB-01** | Is the H3 "reference" the 1 s-sampled cycle or the YAML profile? | S1's YAML profile lasts 324.911 s (2161.047 m); S2's lasts 213.278 s (531.678 m). Knots sit up to 0.5 s off the 1 s grid. The sampled versions are 324 s / 2161.027 m and 213 s / 531.574 m: the last 0.911 s and 0.278 s of idle are dropped, and each sampled rest interval is up to ≈ 1 s shorter (e.g. S2 stop 24.598–36.598 s becomes 25–36 s). R3 v1 §3.2 says the cycles have knots "on whole seconds"; for S1 and S2 that is **incorrect** | **DETERMINED** by protocol §3 ("sampled at h = 1 s", d_ref and T_ref printed as the sampled values) and §5.1 (segments of the sampled reference) | Task = the sampled reference. Its rest intervals define stop compliance. Both arms use the same task | no (both arms identical) | clarification recommended (A1-1) |
| **AMB-02** | May an S-eco profile come to rest *inside* a segment (an extra stop)? | §5.2 allows speed 0 at interior grid points; §5.3, §6 and §9 never mention extra stops | **OPEN** | The validator applies the strictest reading: an extra stop makes the profile **invalid** | **no.** The slice runs only if the profile has no extra stop, so it is valid under either reading | **yes** (A1-2) |
| **AMB-03** | Which current limit defines I_over in §8.2? | §8.2: "\|i\| − I_lim, where I_lim is the discharge or charge limit of the active set". `r3_lib` integrates exceedance of min(C-rate limit, voltage-window limit, max-power current) | **DETERMINED** (literal C-rate limit) | The decision uses the literal definition `I_over_protocol_As`. The window variant `I_over_window_As` is reported and used only for evaluator-simulator agreement. The voltage floor is checked separately (§8.2) | no | clarification (A1-3) |
| **AMB-04** | On which plant state is v_b computed for P3 runs? | §4 and §8.1 do not say. On S2 the reference was feasible in every R3 state, so v_b = v_ref is expected either way | **OPEN** | not implemented (P3 is not in the slice) | no | yes (A1-4) |
| **AMB-05** | §2.4 says the limit sets are "as implemented in `r3_lib`" | They are defined in R3 `run_gates.py` (LIMS) and `r3_pilot.py` (LIM), not in `r3_lib`. Both are frozen-unchanged and identical to each other and to the protocol table | **DETERMINED**, editorial | `config.LIMITS` copies those values; a test asserts them | no | clarification (A1-5) |
| **AMB-06** | The task brief says a trajectory "that reaches a stop at the wrong time" must be rejected | The frozen protocol explicitly allows arrival **no later than** the reference arrival (t_k ≤ T_k, §5.2), with departure at the reference time and waiting in between (§5.3). Total time, stop locations and every reference rest interval are preserved | **DETERMINED** by the protocol, but it **conflicts with one reading of the brief** | Follows the frozen protocol. Early arrival is accepted and reported per stop (`early_arrival_s`). Late arrival, early departure, late departure and motion during a rest interval are rejected | no (follows the governing protocol) | **owner confirmation needed**. Requiring exact arrival would change §5.2 (t_k = T_k) and needs an amendment (A1-6) |
| **AMB-07** | M2 coefficient | §2.3 prints k_c = 0.3592. Ledger MOT-07 and `r3_lib` use 18000·(1/0.874 − 1)/85² = 0.35917… | **DETERMINED**, editorial (rounding) | The exact derivation, in both simulator and evaluator | no | clarification (A1-7) |
| **AMB-08** | §9(a): "at rest at every reference-rest sample and knot" | "Knot" is not qualified | **DETERMINED** in substance | Exact check: v = 0 at both ends of every task rest interval and at every profile knot inside it. This implies v = 0 throughout, for piecewise-linear profiles | no | none |
| **AMB-09** | The protocol does not define a smoke test | The two slice runs (S1, M0, L-R1, P1, B0/B3, 1 ms) are 2 of the 12 planned S1 in-sample runs | **OPEN** | Labelled "implementation smoke test"; no ΔE computed; S2 untouched | no | yes: state whether these runs count toward the campaign or are repeated (A1-8) |
| **AMB-10** | Friction-energy recomputation (§9 names no tolerance for friction) | Friction power depends on the zero-order-hold command, which jumps at control instants; a plain trapezoid then disagrees with the integrator (first test run, `logs/pytest_run1.txt`) | implementation detail | The evaluator integrates each interval with the command held over it, recomputing the end value independently. Tolerance 1e-6 Wh (implementation choice, unchanged after the failure) | no | none |
| **AMB-11** | RMSE sampling (§8.2) | Not stated | **DETERMINED by inheritance** (R1–R3 definition: control instants k·Ts, k = 0…steps) | as R1–R3; the evaluator recomputes on the same instants | no | clarification (A1-9) |
| **AMB-12** | Speed domain | §5.2 caps speed at each segment's reference maximum. The 0–50 km/h domain comes from `02_model_basis.md`, not the protocol | **DETERMINED** (§5.2); the domain check is extra | both checked | no | none |
| **AMB-13** | P3 runs: what if the P1-designed S-eco profile is QS-infeasible on the P3 plant? | §8.1 says "P1-designed profile evaluated on P3". The validator's feasibility check uses the evaluated plant | **OPEN** | not exercised (P3 is not in the slice) | no | yes (A1-10): record the infeasibility, still run the dynamic case, and let §8.2 decide comparability |

## Decision on the vertical slice

None of the OPEN items (AMB-02, -04, -09, -13) can change the validity of the slice as specified:
- AMB-04 and AMB-13 concern P3 only;
- AMB-09 concerns labelling only;
- AMB-02 is neutralised by applying the strictest reading. The slice runs only if both trajectories are valid under it.

AMB-06 is decided by the frozen protocol, and the implementation follows the protocol. **The 170-run campaign must not start** until the owner has reviewed and issued an amendment covering at least AMB-02, AMB-04, AMB-06, AMB-09 and AMB-13.
