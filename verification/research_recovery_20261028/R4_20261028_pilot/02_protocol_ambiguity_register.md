# R4 H3 pilot: protocol ambiguity register (rev1)

**Date:** 2026-10-28.
**Prepared by:** AI assistant; no human review.
**Protocol:** `../R4_20261028_preflight/03_R4_protocol_v1.md`, SHA-256 `f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab` (verified; not edited).
**Revision:** rev1 replaces rev0 (01:35). Rev0 is archived unchanged as `archive/rev0_20261028_0135/02_protocol_ambiguity_register.md`; its hash is in that folder's `ARCHIVE_INDEX.csv`. Rev1 changes the status of AMB-02, -04, -06, -09 and -13 after the owner's decisions D1–D5, and adds AMB-14 to AMB-28 from the readiness work and the code review.

**Status values:**
- **DETERMINED:** the frozen text decides the question.
- **DECIDED (Dx):** settled by owner decision Dx; still to be issued in the amendment.
- **OPEN:** an owner decision is required.
- **NOTE:** recorded for the owner; no amendment is proposed.

Proposed wording for every item is in `03_protocol_v1_amendment_1_DRAFT.md`, which is **DRAFT — NOT APPROVED FOR CAMPAIGN EXECUTION**.

| ID | Question | Status | Resolution or implementation | Amendment item | Blocks |
|---|---|---|---|---|---|
| AMB-01 | Is the reference the 1 s-sampled cycle or the YAML profile? | DETERMINED (§3) | The canonical sampled tasks are established and hashed (`05_cycle_input_provenance.md`). R3 v1 §3.2's "whole seconds" statement is wrong for S1 and S2 | A1-1 | — |
| AMB-02 | May an S-eco profile stop inside a segment? | **DECIDED (D1)**: no | Validator rejects any knot with v ≤ 1e-9 m/s (the frozen §5.1 rule) strictly between departure and arrival. The profile is then "unavailable" (VC-01) | D1 | — |
| AMB-03 | Which current limit defines I_over? | DETERMINED | C-rate limit of the active set. Now also compared against the simulator side (VC-05) | A1-3 | — |
| AMB-04 | Which plant is v_b designed on for P3 runs? | **DECIDED (D2)** | v_b and S-eco are both designed on P1 and both run on P3, with the P1 gain. Rev0 A1-4 is withdrawn | D2 | — |
| AMB-05 | "Limit sets as implemented in r3_lib" | DETERMINED, editorial | as rev0 | A1-5 | — |
| AMB-06 | Early arrival versus exact arrival | **DECIDED (D3)**: keep v1 | Arrive no later than the reference; depart exactly at the reference; at rest while waiting; exact time comparisons | D3 | — |
| AMB-07 | M2 coefficient 0.3592 versus 0.35917… | DETERMINED, editorial | exact derivation | A1-7 | — |
| AMB-08 | §9(a) "knot" | DETERMINED | as rev0 | — | — |
| AMB-09 | Do the smoke-test runs count? | **DECIDED (D4)**: no | Development only; official IDs never equal the smoke IDs (dry-run check); the configuration is re-run as `R4H3-INS-S1-M0-LR1-P1-B0/B3-dt1ms` | D4 | — |
| AMB-10 | Friction recomputation tolerance | implementation detail | Now a diagnostic that never decides crediting (VC-04) | A1-12 | — |
| AMB-11 | RMSE sampling | DETERMINED by inheritance | control instants | A1-9 | — |
| AMB-12 | Speed domain | DETERMINED | as rev0 | — | — |
| AMB-13 | A P1-designed profile infeasible on P3 | **DECIDED (D5)**, except the meaning of "infeasible" (AMB-24) | Both arms run and retained; classify; no paired difference unless COMPARABLE; denominators kept | D5 | — |
| **AMB-14** | Sensitivity draws: is the LQR gain designed on nominal P1 or on the draw's P1 plant? `gain()` depends on M, A_f, C_d and r_w, which §8.4 varies; §4 says "design-fixed"; §8.4 lists only v_b and S-eco as recomputed | **OPEN** | Both implemented; `sensitivity.gain_for_draw` refuses to choose | A1-11 | SEN (128 runs) |
| **AMB-15** | Campaign directory and gate record. §10.1 prescribes a new directory and `logs/pre_run_hashes.txt`; this pilot already holds the smoke-test gate and development outputs | **OPEN** | `run_campaign` runs only from a fresh directory named in the issued amendment, under its own gate record | A1-13 | the whole campaign |
| AMB-16 | Does a draw with no comparable pair count toward "≥ 29 of 32"? | DETERMINED (literal) | It does not give ΔE_rel ≤ −1 %; denominator 32 | A1-14 | — |
| AMB-17 | QS energy used for the QS-versus-dynamic check | DETERMINED (R3 definition) | QS energy of the tracked knots on the dynamic run's plant; 100·(e_dyn − e_QS)/e_QS | A1-15 | — |
| AMB-18 | The readiness brief's stop condition 6 asks the grid, QS/dynamic and 0.5 ms checks to pass before the campaign. Protocol §9 defines them on S2 campaign data and on failure states a resolution, not refusal to run | **NOTE / owner interpretation** | Implemented, and validated on S1 development data only (DEV-2, -3, -4) | — | readiness statement |
| AMB-19 | Does v_b have to meet the S-eco (§5.2) constraints? | DETERMINED (§9 "baseline sanity": reported) | v_b is validated and reported, not rejected; B0 always runs when v_b exists | A1-16 | — |
| AMB-20 | "pip freeze" in §10.2 | editorial | Installed-distribution list from `importlib.metadata` | A1-18 | — |
| AMB-21 | Definition of the battery-limited time fraction (§7.2) | DETERMINED by inheritance | R1–R3 definition at control instants (VC-03) | A1-17 | — |
| AMB-22 | Recomputation gate: which quantities decide crediting, and three tolerances §9 does not state (trip time, I_over, RMSE) | DETERMINED (set), tolerances **need acceptance** | Protocol group versus diagnostics (VC-04) | A1-12 | crediting rule |
| AMB-23 | Rev0 A1-4 (v_b on each state's plant) conflicts with D2 | resolved by D2 | withdrawn | D2 | — |
| **AMB-24** | What does "infeasible on P3" mean in D5: QS step-infeasible on the P3 plant, or failing §8.2 dynamically? | **OPEN** | Both implemented; `classify_pair` refuses P3 without an issued rule (review CR-A2) | D5 / A1-10 | P3 (12 runs) |
| AMB-25 | §7.3 braking work: does motor viscous drag while coasting count as motor braking? | DETERMINED by the implemented term, stated for confirmation | W_brake = ∫(max(−f_w·v, 0) + P_friction) dt, recomputed by the evaluator (VC-05) | A1-17 | — |
| AMB-26 | Stationarity of the dynamic run during the planned early-arrival wait, before t_a + 1 s | NOTE | §8.2 governs the dynamic run; a new check would be a new criterion | — | — |
| AMB-27 | M2 S-eco is designed on the M2 QS model, which §2.3 calls non-representative | NOTE (§5.2 literal) | as frozen | — | — |
| AMB-28 | Exact arrival comparison and floating-point rounding (planner sum versus knot cumulative sum) | NOTE (D3: no timing tolerance) | A spurious "unavailable" is possible but conservative; smoke-test margins are ≥ 0.076 s | D3 | — |

## Gate consequence

The campaign must not start until all of the following hold:
1. The amendment is approved and issued.
2. AMB-14, AMB-15 and AMB-24 are decided in it.
3. The A1-12 tolerances are accepted.
4. Review findings CR-A2 and CR-A6 are ruled on.

`code/r4h3/campaign.py` enforces every one of these: `preconditions()` and `read_amendment()`.
