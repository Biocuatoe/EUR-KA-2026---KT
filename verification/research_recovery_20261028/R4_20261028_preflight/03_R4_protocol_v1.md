# R4 protocol v1: stops-respected eco-driving and SoH-aware control on a declared reference plant

**Status:** FROZEN on 2026-10-28 before any R4 simulation, implementation or outcome. The SHA-256 of this file is recorded in `03_R4_protocol_v1_freeze_record.md`. This text is never edited after freezing. Changes go into separately named amendment files (`03_R4_protocol_v1_amendment_N.md`). Each amendment's SHA-256 is recorded before any run it affects.

**Executable scope of v1:**
- **H3** (primary) and **H1** (defined, not scheduled), both on branch **RP-E** only (`02_model_basis.md` §5).
- **H2, H4 and H5 are BLOCKED.** Their designs are given so that they can be activated by amendment once the named gaps (`02_model_gaps.md`) are closed. They are not executable under v1.

**Preconditions met:** G0 PASS, G1 PASS (classification), G2 PASS for RP-E only (`04_gate_status_summary.md`).

**Integrity rules:**
- The thesis's 12.5 %, 15.3 %, ± 2.1 %, ± 2.8 % and every other legacy number are not targets, thresholds, tuning objectives or ground truth. They appear here only in this sentence.
- Every result is a simulation result for a hypothetical reference plant. None is a result for the KT-01 vehicle, a hardware test or a validation.
- **Prepared by:** AI assistant; no human review at freezing.

---

## 1. Questions

- **Q3 (H3):** On a declared reference micro-EV plant, does a generic eco-driving planner reduce energy per reference km relative to tracking the baseline task when the comparison is matched? Matched means: same stop locations, same stop time intervals, same total time, same distance, same controller.
- **Q1 (H1, not scheduled):** On the same plant, does an SoH-scheduled LQR use less energy than an equally tuned fixed-gain LQR on the same task?

## 2. Plant: branch RP-E

All values are declared reference-plant assumptions. IDs refer to `02_parameter_ledger.csv`.

### 2.1 Physics code
- The equations, QS plant and dynamic plant are those of R3 `code/r3_lib.py`, with SHA-256 `c2403adc2c7ef7a7ecc662f0dcfd3c107a43204ee73c28bd46f782b73cba1c97`. This value is recorded in R3's freeze record and in `R3_hash_manifest.csv`, and was re-verified on 2026-10-28.
- The implementation must check this hash at start and refuse to run on a mismatch.
- The implementation must not modify the R3 file. It may import it read-only, or copy it into the R4 code directory with the hash checked.
- Controller gains and profiles come from the R1 package `eureka` (`eureka.controllers.gain(p, "fixed")`, `eureka.cycles.Profile`), as used by R3 §5.3.

### 2.2 Nominal values

| Group | Values (ledger ID) |
|---|---|
| Vehicle | M 850 kg (VEH-01), A_f 2.2 m² (VEH-03), C_d 0.35 (VEH-04), C_rr 0.008 (VEH-05), r_w 0.28 m (VEH-06), ρ 1.225 kg/m³, g 9.81 m/s², grade 0 |
| Drivetrain | G 6.5, η_g 0.9702, J_m 0.05 kg·m², b_m 0.001 N·m·s, T_max 85 N·m, P_max 18 kW, ω_max 837 rad/s, τ_T 0.02 s |
| Battery | V_oc 48 V constant, Q 100 Ah, R0 5 mΩ, R1 3 mΩ, C1 50 kF, voltage window 37.5–54.75 V; initial state SoC 0.8, V1 = 0, at rest |

### 2.3 Motor-loss bracket (reported separately, never pooled or averaged)

| Branch | Definition |
|---|---|
| M0 | constant η = 0.874 |
| M1 | the FASTSim generic template curve, `R3_20261025/data/motor_curve_m1_derived.json`, SHA-256 `f872faa0ff96d12d26eb5c935bb145062c3ac649e4eb327136f0fa9a0868d1d9` (label "illustrative") |
| M2 | L = 0.3592·T² (stress model) |

M2 is evaluated from dynamic runs only, because its QS energy is not representative (R3: +6–14 %).

### 2.4 Battery limit sets and plant states

| Limit set | Discharge | Charge |
|---|---|---|
| L-R1 | 3C | 1C |
| L-EVE | 2C | 1C |

Both are as implemented in `r3_lib`. L-EVE-s and any SoH-dependent limit are not used.

| Plant state | SoH | k_r0 |
|---|---|---|
| P1 | 1.0 | 0.5 |
| P3 | 0.8 | 3.5 |

P2 (SoH 0.8, k_r0 0.5) is used only by H1. k_r1 = 0.3 throughout.

### 2.5 Exclusions (declared)
- temperature and thermal effects;
- OCV(SoC);
- motor no-load, iron and switching losses;
- auxiliary loads (0 W);
- capacity fade;
- road grade.

## 3. Cycles

| Cycle | Role | Definition |
|---|---|---|
| S2 | **primary held-out** | `configs/cycles/profiles.yaml` S2; d_ref = 531.574 m, T_ref = 213 s |
| S1 | in-sample: planner and solver checks, H1 tuning | same file; d_ref = 2161.027 m, T_ref = 324 s |
| P-TUNE | H1 tuning acceptance only | same file |

The reference is sampled at h = 1 s. d_ref is the trapezoidal distance of the sampled reference.

UDDS, US06 and HWFET are outside the plant's 0–50 km/h domain and are **not used** in v1. A second in-domain held-out cycle requires gap G-CYC-1 to be closed and an amendment.

## 4. Branches

| Branch | Controller | Tracked profile | Status in v1 |
|---|---|---|---|
| **B0** | R1 fixed Bryson LQR gain `eureka.controllers.gain(p, "fixed")` computed for plant state P1 (gain is design-fixed; not retuned per state) | v_b: the baseline task = closest feasible trajectory (`r3_lib.track_dp`, R3 v1 §3.3). On S2, v_b = v_ref is expected; this is checked and recorded | executable |
| **B1** | SoH-scheduled LQR, R3 amendment A1.3 family and tuning procedure, equal budget against a widened fixed family | v_b | defined (H1); not scheduled |
| **B2** | B0 plus SoH-dependent feasibility compensation | v_b | **blocked** (G-BAT-2) |
| **B3** | same gain as B0 | **S-eco profile** (§5), designed on P1 with no SoH information | executable |
| **B4** | same gain as B0 | S-eco designed on the actual plant state | **blocked** (G-BAT-2) |

B0 and B3 use the identical, untuned controller. Their tuning budgets are equal (zero), and any energy difference is attributable to the tracked profile alone.

## 5. The S-eco planner (stops fixed in time)

### 5.1 Segments
- Use `r3_lib.segments(v_ref, h)` (moving if v_ref > 1e-9 m/s), giving segments k = 1..K with sample indices (ks_k, ke_k).
- For each segment:
  - D_k = trapezoidal distance of v_ref over [ks_k, ke_k];
  - T_k = (ke_k − ks_k)·h, the reference travel time;
  - v_lim,k = max v_ref over the segment.
- Acceleration bounds a_lo and a_hi are the minimum and maximum of the reference acceleration over the whole cycle (as R3 v1 §3.7).

### 5.2 Per-segment problem
- Minimise Σ_i E_i over a speed sequence on N_k = max(round(D_k / 2 m), 2) equal distance steps.
- Speed grid: `numpy.linspace(0, v_lim,k, round(v_lim,k / 0.1) + 1)`.
- Constraints:
  - start and end at rest;
  - constant acceleration within each step, between a_lo and a_hi;
  - every step feasible per `QSPlant.step`;
  - **total segment time t_k ≤ T_k**.
- Transition tables come from `r3_lib.eco_segment_tables`, evaluated on plant P1 with the scenario's motor branch and limit set.
- **Solution method:**
  - Minimise Σ(E_i + λ_k·t_i) with `r3_lib.eco_segment_solve`.
  - λ_k is found by bisection on log₁₀λ_k ∈ [−3, 6] with 40 iterations. Keep the feasible solution with the smallest λ_k that satisfies t_k ≤ T_k.
  - If t_k > T_k even at λ_k = 10⁶, the segment is **time-infeasible**. The scenario's profile is then "unavailable", recorded and not replaced.
- **Bounds reported per segment:**
  - E*_k (found);
  - LB_k = max over the evaluated λ of [E(λ) + λ·(t(λ) − T_k)];
  - t_k and λ_k.

### 5.3 Time-domain profile
- Segment k departs at the reference departure time ks_k·h. It follows the DP speeds, which are piecewise linear in time with constant acceleration per distance step.
- The vehicle then stays at rest until ks_{k+1}·h. The initial idle and the final idle are as in the reference.
- **By construction, the profile is at rest whenever the reference is at rest.** An implementation test must assert that this holds on the 1 s grid and at every knot.

### 5.4 Planner outputs
- Profile knots (npz).
- `planner_rows.csv`: one row per segment with D_k, T_k, t_k, E*_k, LB_k, λ_k, N_k, v_lim,k and status.
- Scenario totals:
  - S_found = 1 − E_Seco/E(v_b);
  - S_max = 1 − ΣLB_k/E(v_b);
  - both on the QS plant.

## 6. Matched comparison (fairness)

All compared branches receive:

| Aspect | Rule |
|---|---|
| Plant | same vehicle and drivetrain parameters, same motor branch, same limit set, same plant state, same initial SoC 0.8, V1 = 0, SoH, payload (in M) and ambient (isothermal, no temperature input) |
| Task | the same cycle; the same reference distance d_ref; the same total duration T_ref; the same stop locations and stop time intervals (B3 by construction, §5.3; B0 tracks v_b) |
| Controller | identical gain and sample time for B0 and B3. For H1, equal tuning budgets per R3 A1.3 |
| Energy accounting | §7, identical boundary and sign convention |
| Numerics | RK4 at dt = 1 ms, ZOH at 10 ms for every run; the same convergence rules (§9) |
| Incomplete, violating or infeasible runs | not credited (§8.2). Reported separately |
| Held-out set | S2. Nothing about S2 outcomes is used to choose any setting |

A failure to travel the required distance is never counted as an energy saving.

## 7. Metrics (frozen definitions)

### 7.1 Primary energy metric
- **Energy boundary:** the battery's open-circuit (chemical) side. E_chem = ∫₀^T_ref V_oc·i dt, with i > 0 on discharge.
  - Regenerated energy enters with a negative sign (net energy).
  - The resistive losses R0 and R1 inside the battery are included; auxiliary load is 0 W.
  - This is the energy that must be restored to the cells, excluding charger losses.
- **Energy per reference km:** e = E_chem / d_ref, in Wh/km.
- **Reported separately, always both:**
  - ΔE_abs = e_X − e_B0 (Wh/km);
  - ΔE_rel = 100·(e_X − e_B0)/e_B0 (%).
- **Aggregation:** none. Results are reported per (cycle, motor branch, limit set, plant state) and are never pooled or averaged across these factors.

### 7.2 Secondary metrics (per run)
- E_DC = ∫V_t·i dt;
- energy per actual km;
- distance, and shortfall = 100·(d_ref − d)/d_ref;
- trip time;
- RMSE and max |e| against the tracked profile and against v_ref;
- friction-brake energy;
- Ah throughput ∫|i|dt; ∫i²dt; peak and RMS current;
- battery-limited time fraction; I_over (§8.2); minimum V_t;
- the stop-compliance metrics of §8.2.

### 7.3 Regenerative-braking efficiency (a separate metric, never mixed with Wh/km)
- η_regen = E_regen,chem / W_brake, where:
  - E_regen,chem = |∫ min(V_oc·i, 0) dt| is the energy returned to the cells;
  - W_brake = ∫ (P_regen,wheel + P_friction) dt is the braking work at the wheels, i.e. motor-braking power referred to the wheel plus friction-brake power, both taken positive.
- Reported per run.

### 7.4 Quantities not computed in v1
These are defined so that they are never conflated:
- capacity fade ΔQ_N = 1 − Q_N/Q_0 after N cycles;
- absolute SoH = Q/Q_0;
- relative fade reduction = 1 − ΔQ_N,X / ΔQ_N,B0;
- cycle-life extension = N_EOL,X / N_EOL,B0 − 1 at Q/Q_0 = 0.8.

All four require H5 and are blocked.

### 7.5 Uncertainty
- **No "±" is reported unless it is defined here.** The deterministic nominal runs have no sampling error.
- The only spread reported is the **parameter-sensitivity range** of §8.4: minimum, median and maximum of the paired ΔE_rel over the declared draws, plus the count of draws meeting the threshold.
- This range is not a confidence interval and is never described as one.

## 8. Hypotheses

### 8.1 H3: generic eco-driving at a matched task (PRIMARY, executable)

| Item | Specification |
|---|---|
| Independent variable | tracked profile: v_b (B0) vs S-eco (B3); same controller |
| Required inputs | RP-E (§2); S2; planner §5 |
| Primary metric | ΔE_rel and ΔE_abs per reference km, dynamic runs, S2, P1 |
| Secondary | the same at P3 (P1-designed profile evaluated on P3); QS S_found and S_max; all §7.2 metrics |
| Raw output | §10 |
| Practical threshold | **ΔE_rel ≤ −1.0 %** (§8.3) |
| Held-out condition | S2. S1 is in-sample and reported, never decisive |

**Decision rules (applied mechanically):**
- **SUPPORTED** if all of the following hold:
  - In the nominal S2 P1 runs, every motor branch (M0, M1, M2) and both limit sets give a comparable pair (§8.2) with ΔE_rel ≤ −1.0 %.
  - In the sensitivity draws (§8.4), for M0 and M1 separately, at least 29 of the 32 draws give ΔE_rel ≤ −1.0 %, and no draw gives ΔE_rel > 0.
  - Every check in §9 passes.
- **NOT SUPPORTED** if ΔE_rel > −1.0 % in every motor branch for the nominal S2 P1 runs, with all checks passing.
- **INCONCLUSIVE** otherwise. Examples: branches disagree; the sensitivity criterion fails although the nominal runs meet the threshold; a §9 check fails, so the result is stated only at the demonstrated resolution.
- **INVALID COMPARISON** for a condition if either run of the pair fails §8.2. If the B0 run fails, the condition is excluded and reported, as in R3.

Any outcome is labelled "S2 only, one held-out cycle of 0.53 km, reference plant". A SUPPORTED outcome is labelled "not generalised" until G-CYC-1 is closed.

### 8.2 Run validity and comparability (all hypotheses)

A run is **comparable** only if every criterion below holds. Otherwise it is reported and not credited.

| Criterion | Rule |
|---|---|
| Valid | finite states; battery equation solvable at every step; energy closure ≤ 1e-3 of throughput (as R3) |
| Complete | shortfall ≤ **0.1 %** of d_ref. This is tightened from R3's 1 %: a 1 % shortfall could create up to about 1 pp of apparent saving, equal to the threshold |
| Tracking | RMSE against the tracked profile ≤ 0.10 m/s; max \|e\| ≤ 1.0 m/s |
| Stop compliance | for every reference standstill interval [t_a, t_d] with t_d − t_a ≥ 2 s: \|v\| ≤ 0.05 m/s on [t_a + 1 s, t_d], and distance travelled on [t_a + 1 s, t_d] ≤ 0.10 m. Shorter standstills are reported, not tested |
| Constraint compliance | I_over = ∫ max(0, \|i\| − I_lim) dt ≤ 0.01 A·s per run, where I_lim is the discharge or charge limit of the active set; and V_t ≥ V_min − 0.01 V at every sample |

### 8.3 Threshold justification (independent of legacy figures)

The threshold is 1.0 % of energy per reference km. It is the smallest effect this model can attribute with confidence:
- **Implementation resolution.** R3's dynamic-versus-QS agreement for M0/M1 was 0.2–0.3 % on S2 and about 1 % on long cycles. Time-step sensitivity was < 0.01 pp. Effects below about 1 % are therefore of the same order as known model-implementation differences.
- **Structural uncertainty.** The unknown motor-loss structure moves the same comparison by more than 1 pp between bracket members (R3 QS S2 A = 0: M0 2.85 % vs M1 1.48 %). An effect smaller than 1 % cannot be separated from that uncertainty. This is why the rule requires agreement across the bracket.

**Equivalence wording:** "no practical difference" may be used only if |ΔE_rel| < 0.5 % in every comparable held-out condition of every branch. Between 0.5 % and 1.0 % the wording is "below the practical threshold".

**Disclosure of prior knowledge.** The author of this protocol knew R3's S2 results when fixing the threshold and the planner:
- R3's S2 eco runs at A = 0 gave dynamic savings of 1.46–2.87 %, with stop-arrival shifts of ≤ 0.32 s (`01_r3c_reassessment.md`).
- The 1.0 % threshold was not chosen from those results. It is the same threshold all frozen R1–R3 protocols used, with the justification given above.
- The S-eco planner was designed in response to R3-C's *stop-timing* defect, not to its energy values.
- No S-eco outcome exists at freezing.

### 8.4 Parameter-sensitivity draws (H3)
- **Design:** 32 draws from `scipy.stats.qmc.LatinHypercube(d=7, rng=numpy.random.default_rng(20261028))`, using the default scrambling, mapped uniformly onto:

  | Column | Parameter | Range |
  |---|---|---|
  | 1 | VEH-01 M | 722.5–977.5 kg |
  | 2 | VEH-03 A_f | 2.0–2.4 m² |
  | 3 | VEH-04 C_d | 0.315–0.385 |
  | 4 | VEH-05 C_rr | 0.008–0.012 |
  | 5 | VEH-06 r_w | 0.265–0.285 m |
  | 6 | BAT-07 R0 | 4–6 mΩ |
  | 7 | MOT-05 η | 0.83–0.918; M0 only, ignored by M1 |

- **Per draw:** recompute v_b and the S-eco profile on that draw's plant. Run B0 and B3 dynamically on S2, L-EVE, P1, for M0 and for M1. That is 128 runs.
- **Interpretation:** uniform mapping is a coverage design, not a probability statement.

### 8.5 H1: SoH-scheduled vs equally tuned fixed LQR (defined; NOT SCHEDULED in v1)

| Item | Specification |
|---|---|
| Independent variable | B1 vs B0′, where B0′ is the fixed gain tuned with the widened box of R3 A1.3 |
| Inputs | RP-E; P1, P2, P3; L-R1, L-EVE |
| Tuning | exactly R3 A1.3: 24 LHS candidates per family, seed as declared in an activating amendment; S1 at P1 and P3; feasibility RMSE ≤ 0.10, max \|e\| ≤ 1.0, shortfall ≤ 0.1 %; selection by minimum mean Wh per reference km |
| Metrics | ΔE_rel and ΔE_abs per reference km; RMSE ratio |
| Threshold | ΔE_rel ≤ −1.0 % with RMSE ratio ≤ 1.10, in every motor branch, held-out S2 |
| Prior evidence | null in R1, R2 and R3-B on this plant (`00_baseline_audit.md` §6) |
| Activation | only by amendment, and only after G-BAT-2 changes how SoH enters the plant. Otherwise a fourth run repeats known physics |

### 8.6 H2: SoH-dependent feasibility compensation (BLOCKED)
- **Design for later activation:** B2 vs B0 on a plant whose current and voltage limits depend on SoH according to a sourced law (G-BAT-2).
- **Primary metrics:** I_over, time below V_min, completion rate and RMSE at P3. **Secondary:** energy.
- **Threshold:** to be justified from the sourced limit law's uncertainty in the activating amendment, before any run.
- **Invalid** if the limit law is unsourced (class D).

### 8.7 H4: SoH-aware vs generic planner (BLOCKED)
- **Design:** B4 (S-eco designed on P3) vs B3 (S-eco designed on P1), both evaluated on P3, with identical constraints.
- **Threshold:** 1.0 %.
- **Blocked because:**
  - without G-BAT-2 the only SoH pathway is R0 growth;
  - its QS value (R3 VSI_eco 0–0.075 % on S2) is smaller than the eco DP's demonstrated optimality gap (≈ 0.4 %, `01_r3c_reassessment.md` §4);
  - so any result would be below resolution.

### 8.8 H5: capacity-fade benefit (BLOCKED)
- Requires G-AGE-1: an ageing law with sourced parameters for the pack, its validity domain, a cycle-resolved state history retained per run, and validation data.
- Until then no fade, fade-reduction, SoH-trajectory or cycle-life number may be produced or reported.
- Ah throughput and ∫i²dt are reported only as stress indicators, never as fade.

## 9. Numerical and validity checks (fixed before running)

| Check | Case | Criterion | On failure |
|---|---|---|---|
| r3_lib hash | start of every process | equals the frozen hash | refuse to run |
| Planner unit tests | before any outcome | (a) profile at rest at every reference-rest sample and knot; (b) segment distance = D_k within 1e-9 m; (c) t_k ≤ T_k; (d) per-segment DP equals exhaustive enumeration on a toy grid | do not run |
| Planner grid convergence | S2, each motor branch and limit set, P1: (2 m, 0.1 m/s) vs (1 m, 0.05 m/s) | \|ΔS_found\| < 0.2 pp | state results at the observed resolution |
| Planner optimality | every scenario | S_max − S_found reported; if > 0.2 pp, that gap is the stated resolution | as stated |
| Dynamic time step | S2, L-EVE, P1, each motor branch, B0 and B3: dt 1 ms vs 0.5 ms | every ΔE_rel changes by < 0.01 pp | as R3: stated resolution |
| QS vs dynamic | every B0 and B3 profile | M0, M1: ≤ 1 % per reference km. M2: reported only | M0/M1 failure → INCONCLUSIVE for that branch |
| Independent recomputation | every run, by a separate script reading only the saved traces | E_chem, E_DC, distance, trip time, stop compliance, I_over and RMSE agree with `runs.csv`: energies within 1e-4 relative, distance within 1e-6 relative, flags identical (all traces at 1 ms) | the run is flagged and not credited until resolved by amendment |
| Baseline sanity | S2 | v_b = v_ref exactly is checked and recorded. If not, the shortfall and deviation are reported | — |

## 10. Raw output, reproducibility and reporting

### 10.1 Directory and code
- **Directory:** a new versioned directory `verification/research_recovery_20261028/R4_<date>_pilot/`, never reusing or overwriting an existing one.
- **Code:** in `code/`, with tests. Every file is hashed in `logs/pre_run_hashes.txt` before the first outcome-producing run, together with this protocol's hash.

### 10.2 Environment manifest
Record, per run:
- the Python executable and version;
- `pip freeze` of the project `.venv`;
- numpy and scipy versions;
- the machine name and process start time.

### 10.3 Per-run files

| File | Content |
|---|---|
| `traces/<run_id>.npz` | t, v, v_tracked, v_ref, T_cmd, T, ω, i, V_t, V1, SoC, P_friction, P_regen_wheel and a limit-active flag. Sampled every 1 ms for every run (every integration step; every second step for the 0.5 ms convergence runs), float64, compressed (about 3–4 GB in total, on D:) |
| `runs.csv` | one row per run with every §7 metric and every §8.2 flag |
| `manifest.json` | code hashes, protocol and amendment hashes, input-file hashes, environment, start and end times |
| planner outputs | profile knots (npz) and `planner_rows.csv` |

### 10.4 Run accounting and deviations
- Every run is written, valid or not.
- Exceptions go to `errors.csv` with the traceback. **No silent retry.** A rerun needs an amendment that states the cause and the fix.
- A post-run SHA-256 manifest covers all outputs.
- **Protocol deviations:** any change after freezing is an amendment issued before the affected runs. A change made after outcomes are seen is labelled *post hoc* in every table that uses it.

### 10.5 Reporting rules
- No number goes into the thesis unless it traces from a table cell to a `runs.csv` row, to a traces file, to manifest hashes.
- ΔE_abs and ΔE_rel are always reported together.
- Trip time is always reported alongside energy.
- Completed, invalid, infeasible and excluded conditions are reported in separate rows.

### 10.6 Planned run budget (H3)

| Set | Runs |
|---|---|
| Nominal S2 P1 (3 motor branches × 2 limit sets × B0/B3) | 12 |
| S2 P3 | 12 |
| S1 P1 (in-sample) | 12 |
| Convergence | 6 |
| Sensitivity draws | 128 |
| **Total** | **170 dynamic runs** |

Planner runs are QS only. No optimiser other than the planner of §5, and no sweep beyond §8.4, is permitted under v1.

## 11. What v1 does not do

- No KT-01 vehicle claims.
- No motor-specific claims.
- No SoH-dependent limits.
- No fade.
- No UDDS or other out-of-domain cycles.
- No pooling across motor branches.
- No tuning to any target value.
