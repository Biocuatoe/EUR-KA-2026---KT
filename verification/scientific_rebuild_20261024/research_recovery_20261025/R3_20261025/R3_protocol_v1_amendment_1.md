# R3 protocol v1 — Amendment 1

**Issued:** 2026-10-25, after the frozen gate run (`outputs/gates/`, finished 15:44) and before any run this amendment affects. Its SHA-256 is recorded in `logs/amendment_1_sha256.txt` before those runs start.

**Status of v1:** `R3_protocol_v1.md` (SHA-256 `d9e82f89…bae56`) is unchanged and remains binding except where this amendment adds to it. The frozen gate decisions in `outputs/gates/gate_decisions.json` are **not changed**. Under §4 they are:

| Branch | G-A | G-B | G-C |
|---|---|---|---|
| M0, M1, M2 | FAIL-certified-on-grid | PASS | PASS |

The pilots they trigger (R3-B and R3-C, for all three branches) run as frozen.

## A1.1 Material flaw found after the gate run: motion while the baseline stands still

**Observation** (`code/describe_band_paths.py` → `outputs/checks/band_path_description.csv`, a description of the saved paths, not a new outcome):
- In every held-out scenario, the band DP keeps the vehicle moving at nearly every sample where v_b = 0: 63 samples on S2, 257 on UDDS.
- At δ = 0.25 m/s this covers 0.50–2.3 % of the trip distance.
- That distance lets the trajectory run slower while moving: mean offset −0.06 to −0.09 m/s, peak speed −0.25 m/s.

**Diagnosis.** The frozen definition (v1 §3.4) bounds |v − v_b| ≤ δ but does not require the vehicle to be at rest where the task is at rest. Creeping through stops and idle periods is not the same driving task. The frozen H(δ) therefore mixes two levers:
- motion at standstill, a task-definition artefact;
- tolerance-limited speed reduction while moving.

**Added analysis (G-B′).** Same as v1 §3.4, with one extra constraint: v_k = v_b,k at every sample where v_b,k = 0. It is implemented by setting band-table transitions to +∞ for nonzero offsets at those samples (`code/run_gates_a1.py`, function `stop_mask`).

- **Coverage:** the full v1 band scenario grid, all δ, and VSI′ on the same masked band.
- **Rules:** the v1 §4 classification is applied unchanged, giving the G-B′ and G-A′ decisions.
- **Use:** G-B′ is used for interpretation. It does not cancel the R3-B pilot that the frozen G-B PASS triggered, and it does not launch anything by itself.
- **Reporting:** both the frozen and the stop-respecting results are reported side by side.

## A1.2 Post-freeze check: regeneration/friction split under M2

As stated in `R3_optimizer_validity.md` §3:
- `code/check_m2_regen_split.py` recomputes the M2 baseline and band (δ = 0.25) trajectories with motor braking torque T′ = clamp(−ω/(2k_c), T_m, 0) and friction for the rest;
- it reports the energy difference;
- it is descriptive only, and no gate is recomputed with it.

## A1.3 R3-B pilot: details v1 left open

1. **Closed loop.** `code/r3_pilot.py` ports R2's `../pilot/sim.py` (R2's layer: aware anti-windup and feasible-reference governor) to `r3_lib`'s plant with the motor model as an argument. Logic is unchanged.
   - **Pre-condition:** with M0, the port must reproduce R2's `sim.py` on a fixed set of 8 runs (S2; the four branch settings × two limit sets) to ≤ 1e-9 relative energy and distance.
   - If that fails, the pilot does not run.
2. **Branches F0, S0, F1, S1**, as R2. The fixed family is widened per v1 §5.1:
   - Q = diag(1/(e_max σ)², q_T/T_bryson², 1/z_max²) and R = c/T_bryson²;
   - log₁₀σ ∈ [−0.6, 0.3], log₁₀c ∈ [−2, 1.48], log₁₀q_T ∈ [−0.48, 0];
   - a 3-dimensional Latin hypercube.

   The scheduled family is R2's: a 4-dimensional LHS over log₁₀σ, log₁₀c, γ_v and γ_u, with R2's boxes. Both use `scipy.stats.qmc.LatinHypercube(rng=default_rng(20261025))`, with 24 candidates each.
3. **Tuning on S1:**
   - T1 is P1 and T2 is P3, both under L-R1. This equals R2's T1/T2 and v1 §5.1 "S1 on P1 and P3".
   - Feasibility and selection follow R2 §4 exactly (shortfall ≤ 1 %, RMSE ≤ 0.10, max |e| ≤ 1.0 in both; minimum mean Wh per reference km; ties by RMSE).
   - Unstable designs are infeasible.
4. **Evaluation.** S2 and UDDS are held-out; S1 is in-sample and reported. The conditions are:

   | Condition | Plant state | Limits |
   |---|---|---|
   | E1 | P1 | L-R1 |
   | E2 | P3 | L-R1 |
   | E2b | P2 | L-R1 |
   | E3 | P3 | L-EVE |
   | E4 | P3 | L-EVE-s (exploratory) |

   R2's E3/E4 used a 0.5C charge limit. R3 uses its own L-EVE (1C), as v1 §2 defines.
5. **Runs.** Each motor branch M0, M1 and M2 (all passed G-B) is tuned and evaluated separately. That is 3 × 192 tuning runs and 3 × 60 evaluation runs.
6. **Effects.** Reported as in v1 §5.2:
   - layer: F1 − F0 and S1 − S0;
   - scheduling: S0 − F0 and S1 − F1;
   - interaction.

   Scheduling **improves** only under the v1 §5.1 rule: ΔE ≤ −1 % per reference km, RMSE ratio ≤ 1.10, both complete, held-out, in more than one motor branch, and not only in E4.
7. **Convergence.** UDDS E3, four branches, dt = 0.5 ms, per motor branch.

## A1.4 R3-C pilot: details v1 left open

1. **Profiles.** Each profile is a piecewise-linear `eureka.cycles.Profile` built from the saved knots (`outputs/gates/paths/`):
   - the baseline v_b, for P1 and the scenario's limit set, sampled at 1 s;
   - eco A = 0, if it exists;
   - eco A = 5 %.

   Where eco A = 0 is "time budget infeasible" (UDDS, L-EVE, every branch), that run is recorded as "profile unavailable" and not replaced.
2. **Distance.** Completion is judged against the original reference distance d_ref, not the profile's own distance.
3. **Exclusion.** A scenario whose baseline-profile run fails §5.3's requirements is reported and excluded from the pilot conclusion.
4. **Independent recomputation** (v1 §8): E_pos + E_neg vs E_chem from the final state. **QS check:** the QS energy of the profile (`QSPlant` at h = 1 s) vs the dynamic run.
5. **Time-step check:** S2 and UDDS, L-EVE, for each available profile, at dt = 0.5 ms, for each branch.

## A1.5 Nothing else changes

- Thresholds, denominators, falsification statements and the no-fade rule are as in v1.
- No gate value already computed is recomputed or replaced.
