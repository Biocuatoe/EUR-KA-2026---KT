# R3 protocol: can a physically richer plant give SoH-aware or battery-aware control a measurable energy benefit?

**Status:** frozen before any gate or pilot computation. The SHA-256 of this file at freezing is
written to `logs/protocol_sha256_at_freeze.txt` and into every output manifest. Later changes go
to §11 as dated deviations; this text is not edited after freezing.

**What may have run before freezing:** only the implementation tests in `code/test_r3.py`
(equality with R1's plant, inverse maps, DP self-consistency, closure) and the extraction of the
published motor-efficiency curve (`data/motor_curve_fastsim.json`). Neither computes any outcome
defined below.

**Relation to earlier work.** R1 (`../../experimental_protocol.md`, SHA-256 `d80b5b4f…479c`), the
R2 P2 pilot (`../pilot_protocol.md`, SHA-256 `ebebc157…2b5a`), their code and outputs are imported
or read only, never modified or rerun.

**Labels.** Every number R3 produces is a **simulation result for a defined reference plant**. The
thesis's battery is unidentified (owner item OC-1), so no parameter here is presented as that
battery's. Nothing is real-vehicle validation. The thesis's 12.5 % and 15.3 % are not targets and
are not used anywhere in this protocol.

---

## 1. Questions

- **Q-A (R3-A, SoH scheduling, same task).** With the reference plant's motor-loss and battery
  mechanisms, can knowing SoH change achievable energy per km by ≥ 1 % while the vehicle performs
  the same tracking task?
- **Q-B (R3-B, battery-aware supervision, same task).** Can *any* controller that keeps the same
  tracking task, with or without a supervisory layer, save ≥ 1 % against exact tracking?
- **Q-C (R3-C, eco-driving, different task).** How does energy per km change when the speed
  trajectory is optimised between the reference's stops at matched distance and stated
  travel-time allowances?
- **Q-D (degradation).** Does any available, defensible ageing law permit a quantitative
  capacity-fade comparison?

## 2. Reference plant (`R3_model_basis.md`; code `code/r3_lib.py`)

**Longitudinal dynamics, drivetrain, battery ECM, actuator lag and torque saturation.** These are
R1's, with R1's parameter values (`../../parameter_registry.csv`; thesis values,
`report_unverified`).

**Motor/inverter loss L(P_m, T, ω) ≥ 0 with P_e = P_m + L.** Three structurally different models
are used, so that the conclusion does not rest on one loss assumption:

| Code | Model | Basis |
|---|---|---|
| M-const | constant η = 0.874 both directions | R1 (thesis value) |
| M-curve | η(\|P_m\|/18 kW) from the e-machine efficiency curve of the FASTSim 3.1.0 bundled vehicle `2022_Renault_Zoe_ZE50_R135.yaml`, as a function of output-power fraction, applied to both directions | published model data (NREL FASTSim), a generic shape from a different, larger vehicle |
| M-copper | L = k_c·T², k_c = 18 000·(1/0.874 − 1)/85² W/(N·m)² (same efficiency as M-const at rated torque and base speed; all loss is copper loss) | assumed **stress** model. It favours controllers that smooth torque, and is therefore favourable to the hypothesis |

**Battery limits** (current limits as C-rate × 100 Ah; voltage window 2.5–3.65 V per 3.2 V, as in
R1):

| Code | Discharge / charge | Basis |
|---|---|---|
| L-R1 | 3C / 1C | R1 assumption (BCN) |
| L-EVE | 2C / 1C | retailer summaries of EVE LF100 100 Ah LFP cells: 1C continuous, 2C 30-s pulse (SEC grade). A generic cell, not the thesis's |
| L-EVE-s | 2C / 1C scaled by SoH | exploratory BMS law; reported, never decisive |

**Plant states:**
- P1: SoH 1.0.
- P2: SoH 0.8, k_r0 = 0.5 (thesis law, R0 × 1.10).
- P3: SoH 0.8, k_r0 = 3.5 (R0 × 1.70, the Pan 2023 end-of-life ratio used in R2).

Isothermal (no temperature model; none sourced). Constant OCV (LFP plateau; the SoC swing per
cycle is below 2 %).

**Cycles.**
- S1 (in-sample in R2) and S2 (held-out in R2): R1 synthetic profiles.
- UDDS: EPA, provenance recorded in R1.
- US06 is excluded (beyond motor capability in every R1 class).

"Held-out" for gate purposes means S2 and UDDS.

## 3. Quasi-static evaluation and the two dynamic-programming bounds

**Quasi-static evaluation.** Constant acceleration per step, 3-point Gauss in time, V1 = 0.
- The friction brake absorbs braking beyond the regeneration limit.
- A step whose drive torque exceeds the motor/battery envelope is infeasible.
- Energy is net chemical energy ∫V_oc·I dt, the R1 definition.

**Band DP (same task).** Over all sampled trajectories with:
- |v_k − v_ref,k| ≤ δ at every sample (step h = 1 s, speed resolution 0.01 m/s on a grid centred on v_ref);
- equal duration;
- start and end equal to the reference;
- distance ≥ the reference's;

minimise energy (Lagrange multiplier on distance, bisection). Exact tracking is a feasible member, so the DP result is never worse.

**Headroom.** H(δ) = 1 − (E*/d*)/(E_b/d_b) per km:
- b = exact tracking where it is feasible;
- otherwise the band DP at the smallest feasible δ in {0.02, 0.05, 0.10} m/s, which is reported.

Bands: δ ∈ {0.05, 0.10, 0.25, 0.50} m/s. **δ = 0.25 m/s is the pre-registered same-task band for the gates.** It is deliberately generous: R2's tuned LQRs had RMSE < 0.10 m/s.

**Value of SoH information (VSI).** At δ = 0.25:
- VSI = 1 − (E*_P/d)/(E[traj*_P1 evaluated on P]/d) for P ∈ {P2, P3}.
- This is the most any SoH-informed controller could gain over the best SoH-1.0-designed trajectory performing the same task. It is an upper bound on the scheduling benefit (non-causal, perfect preview).
- If traj*_P1 is infeasible on P, that is reported.

**Eco DP (different task).** Distance domain, per moving segment between the reference's
standstills:
- start and end at rest;
- speed ≤ that segment's maximum reference speed;
- acceleration within [min, max] of the reference's acceleration over the whole cycle;
- motor torque/power and battery limits as above;
- distance step 2 m and speed step 0.1 m/s;
- idle durations as in the reference.

Minimise E + λ·t; λ is found by bisection so that total trip time ≤ (1 + A)·T_ref for **A ∈ {0, 2.5, 5, 10} %**.
- Saving S(A) = 1 − (E_eco/d)/(E_b/d_b), with b as for the band DP.
- **A = 0 is the matched-time case.**
- VSI is computed for eco at A = 0 as for the band DP.

**Scenario grid.**
- Band DP and VSI: 3 cycles × 3 motor models × {L-R1, L-EVE} × {P1, P2, P3}, plus L-EVE-s on P2/P3 (exploratory).
- Eco DP: 3 cycles × 3 motor models × {L-R1, L-EVE} × {P1, P3}.

## 4. Gates (decide which pilots run)

| Gate | Passes if | Then |
|---|---|---|
| G-A | VSI ≥ 1 % on a held-out cycle in any non-exploratory scenario | Run R3-A LQR pilot (§5.1) |
| G-B | H(0.25) ≥ 1 % on a held-out cycle in any non-exploratory scenario | Run R3-B factorial pilot (§5.2) |
| G-C | S(0) ≥ 1 % or S(5 %) ≥ 1 % on a held-out cycle | Run R3-C dynamic tracking pilot (§5.3) |

If a gate fails, its pilot is **not run** and the bound is the result.

## 5. Pilots (small, deterministic; dynamic plant `r3_lib.simulate`, RK4 1 ms, ZOH 10 ms)

### 5.1 R3-A (only if G-A)

F vs S on the R3 plant with R2's equal-budget tuning (24 Latin-hypercube candidates per branch,
seed 20261025, same parameter boxes and feasibility requirement: shortfall ≤ 1 %, RMSE ≤ 0.10 m/s,
max |e| ≤ 1.0 m/s on the tuning scenarios). Tuning on S1 (P1 and P3); evaluation on S2 and UDDS (P1,
P2, P3) under the motor model and limits that passed G-A.

### 5.2 R3-B (only if G-B)

F0/S0/F1/S1 exactly as R2 (`../pilot_protocol.md` §2, §4), on the R3 plant, under the scenario that
passed G-B. Main effects and the interaction reported separately; scheduling credited only with
(S1 − F1) and (S0 − F0).

### 5.3 R3-C (only if G-C)

- **Controller.** The R1 fixed LQR gain (Bryson design) tracks three profiles:
  1. the original reference;
  2. the eco profile for A = 0;
  3. the eco profile for A = 5 %.
- **Scenarios.** S2 and UDDS; M-const, M-curve and M-copper; L-R1 and L-EVE; P1. That is 36 runs.
- **Convergence.** UDDS, L-EVE, the three profiles, M-copper, at dt = 0.5 ms (3 runs).
- **Requirements per run:**
  - valid (closure ≤ 1e-3 of ∫|V_oc·I|, finite, battery solution feasible);
  - RMSE ≤ 0.10 m/s against the profile it tracks;
  - distance shortfall ≤ 1 % against the reference distance.

## 6. Outcomes and denominators

**Outcomes:**
- **Primary:** energy per actual km, net chemical V_oc·I.
- **Relative differences:** ΔE % = 100·(E_a/d_a − E_b/d_b)/(E_b/d_b), with b the comparison case named in each table.
- **Secondary:** distance, trip time, RMSE and max |e| (pilots), friction-brake energy, terminal regeneration, Ah throughput, ∫i²dt, peak current, battery-limited time fraction.

**Capacity fade is not computed** (§9).

## 7. Practical-effect threshold and decision rules

- **Practical threshold: 1 % of energy per km**, as in R1 and R2.
- **A controller "improves" only under all of these conditions:** ΔE ≤ −1 % against the matched baseline, on a held-out cycle, with the tracking and completion requirements met, and in more than one motor-loss model. A result that holds only under M-copper is reported as "stress-model only".
- **An eco-driving saving is attributed to the changed driving task, never to SoH scheduling.** Only VSI(eco) can be attributed to SoH.

## 8. Numerical validity and convergence (pre-specified)

- **Band DP.** On S1, M-copper, L-EVE, P3, δ = 0.25: h 1 → 0.5 s and dv 0.01 → 0.005 m/s. Criterion: |ΔH| < 0.05 percentage points.
- **Eco DP.** On S1, M-copper, L-EVE, P1, A = 0 and 5 %: Δs 2 → 1 m and Δv 0.1 → 0.05 m/s. Criterion: |ΔS| < 0.2 percentage points.
- **Pilot.** dt 1 → 0.5 ms changes every reported ΔE by < 0.01 pp.
- **Accounting.**
  - Quasi-static energy of each tracked profile against the dynamic simulation of that profile: |difference| ≤ 1 % of energy per km.
  - Quasi-static exact tracking against R1's independent exact-tracking ledger (`../../recovery_feasibility_20261025/ledger_ideal.csv`): ≤ 0.2 %. This is a pre-freeze test.
- A failed criterion is reported. The affected quantity is then stated only to the resolution actually demonstrated.

## 9. Degradation (Q-D)

No fade law is used to compute capacity loss:
- The candidate LFP laws found (Wang 2011, Naumann 2020, Schimpe 2018, Pan 2023) are for other cells and formats.
- Their coefficients have not been read from primary full text in this project.
- No dataset is downloaded.

Ah throughput and ∫i²dt are reported as stress indicators only. Neither is converted into fade.

## 10. Falsification statements (fixed before running)

- **H-A** (SoH scheduling can add ≥ 1 % on the same task) is **falsified** if VSI < 1 % in every non-exploratory scenario.
- **H-B** (a same-task controller, including any supervisory layer, can save ≥ 1 %) is **falsified** if H(0.25) < 1 % on every held-out non-exploratory scenario.
- **H-C** (re-planning the speed trajectory saves ≥ 1 % at A ≤ 5 %) is **falsified** if S(5 %) < 1 % on every held-out scenario.
- **The R3-C pilot falsifies the DP eco result** if the LQR cannot track the eco profiles within the requirements, or if the simulated saving is opposite in sign or less than half of the DP prediction.

## 11. Deviations log

(empty at freezing)
