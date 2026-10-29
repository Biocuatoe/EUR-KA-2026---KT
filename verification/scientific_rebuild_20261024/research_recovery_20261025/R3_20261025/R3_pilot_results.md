# R3 pilot results (Steps 7–8)

**What this is:** deterministic closed-loop simulations of the R3 **reference plant**:
- R1 plant, RK4 at 1 ms, ZOH at 10 ms;
- motor-loss branch M0, M1 or M2 (`R3_motor_curve_audit.md`);
- thesis-printed vehicle values;
- a generic 48 V, 100 Ah LFP reference pack.

It is not the thesis vehicle, not a real vehicle and not recovered original evidence. The thesis's 12.5 % and 15.3 % were not targets.

**Which pilots ran.** They follow the frozen gates (`R3_gate_results.md`):
- G-A FAIL-certified-on-grid → **R3-A not run**;
- G-B PASS → **R3-B ran**;
- G-C PASS → **R3-C ran**.

Pilot details are fixed in `R3_protocol_v1_amendment_1.md` (SHA-256 recorded before the runs).

**Raw outputs:**
- `outputs/pilot_B/<M>/` (`tune_candidates.csv`, `tune_selected.json`, `eval_runs.csv`, `conv_dt0.5ms.csv`, `manifest.json`);
- `outputs/pilot_C/<M>/runs.csv` and `manifest.json`.

**Analysis:** `code/analyse_pilots.py` → `outputs/pilot_summary.json` and `outputs/pilot_summary_tables.txt`. The tables there hold every run; this file summarises them.

## 0. Pre-conditions and run record

| Item | Result |
|---|---|
| R3-B port of R2's closed loop vs R2's `sim.py`, M0, S2, 8 runs (A1.3 pre-condition) | relative difference **0.0** in energy, distance and RMSE: pass (`outputs/pilot_B/precheck/`) |
| Same, where limits bind: S1, L-EVE and L-EVE-s, governor active 2.4–5.7 % of the time (added check) | **0.0**: pass (`precheck2.csv`) |
| R3-B runs | per branch: 192 tuning + 60 evaluation + 4 runs at dt 0.5 ms. All 768 runs valid. Unstable candidates: none |
| R3-C runs | per branch: 17 rows (11 at 1 ms, 5 at 0.5 ms, 1 "profile unavailable"). All valid |
| Failure during R3-C | all three processes crashed **after** writing `runs.csv`, at the manifest step: a 1 × 3 gain was passed to `float()` (`logs/pilot_C_*.err.txt`). No simulation was affected or rerun. The manifests were written afterwards by `code/write_pilot_C_manifests.py`, and are marked as such. The bug is fixed in `r3_pilot.py` |
| Wall time | R3-B: 4,500–6,300 s per branch. R3-C: about 2.5 h per branch (6 processes in parallel) |

## 1. R3-B: fixed vs SoH-scheduled LQR, with and without the supervisory layer

### Tuning

The tuning used equal budgets: 24 Latin-hypercube candidates per branch, on S1 at T1 (P1) and T2 (P3) under L-R1. The fixed box was widened to cover the scheduled gain range.

- **Fixed (F0/F1):** candidate 17 (σ 0.266, c 0.044, q_T 0.569) in **all three** motor branches. 21 of 24 candidates were feasible.
- **Scheduled (S0/S1):** candidate 22 (σ 0.318, c 0.041, γ_v 9.27, γ_u 1.99) under M0 and M1, and candidate 6 (σ 0.263, c 1.12, γ_v 6.3, γ_u 0.95) under M2. 23 of 24 candidates were feasible.

### Effects on held-out cycles (S2, UDDS), % of energy per reference km

Each value is the largest absolute effect over the complete and valid held-out conditions: 8 per branch.

| Branch | Scheduling, S0−F0 and S1−F1 | Layer, F1−F0 and S1−S0 | Interaction | Scheduling "improves" (v1 §5.1)? |
|---|---|---|---|---|
| M0 | ≤ 0.038 % (sign mixed, mostly +) | ≤ 0.004 % | ≤ 0.001 pp | **no**, in no condition |
| M1 | ≤ 0.033 % (S2 −0.015 to −0.020; UDDS +0.010 to +0.033) | ≤ 0.004 % | ≤ 0.001 pp | **no** |
| M2 (stress model) | **+0.35 to +0.40 % on UDDS** (the scheduled controller uses *more*); +0.05 % on S2 | ≤ 0.006 % | ≤ 0.004 pp | **no** |

- **Tracking.** RMSE is 0.017–0.031 m/s on S2 and 0.12–0.19 m/s on UDDS E1/E2/E2b. The RMSE ratios between F and S lie between 0.97 and 1.8. Where S's RMSE is higher, its energy is not lower.
- **Completeness.** UDDS under E3 (L-EVE) and E4 (L-EVE-s) is **incomplete for every branch and every controller** (shortfall > 1 %; RMSE 0.54–1.20 m/s). The battery limit, not the controller, prevents completing the task. These two conditions are excluded from "improves" by rule. Even there, scheduling differences are ≤ 0.54 % and are positive, i.e. worse.
- **Time-step check** (UDDS E3, dt 1 → 0.5 ms): every reported difference changed by < 2e-7 pp. The criterion was < 0.01 pp: pass.
- **Exploratory E4** (SoH-scaled limits): nothing changes.

**Comparison with the gate.** G-B showed that a trajectory within ±0.25 m/s could save about 4–6 % on the same task. The tuned LQRs differ from each other by < 0.4 %, and the layer by < 0.01 %. Neither SoH scheduling nor R2's supervisory layer exploits that headroom. Both track the reference closely (S2 RMSE ≈ 0.02 m/s), so they never realise the tolerance-band trajectories the DP found. Capturing that headroom would need a controller that deliberately plans its deviations: an energy-optimal or preview controller, which is a different design question.

## 2. R3-C: fixed R1 LQR tracking the baseline and the eco profiles (P1)

The profiles are separate driving tasks. Every saving is an energy-time trade-off and is **not attributable to SoH scheduling**.

| Branch | Cycle, limits | Profile | ΔE vs baseline, dynamic | DP prediction S_found | Trip time | RMSE vs profile | Status |
|---|---|---|---|---|---|---|---|
| M0 | S2, L-R1 = L-EVE | eco A = 0 | **−2.87 %** | 2.85 % | 213.0 s (= ref) | 0.047 | ok |
| M0 | S2 | eco A = 5 % | **−14.25 %** | 14.21 % | 223.5 s (+4.9 %) | 0.045 | ok |
| M0 | UDDS, L-R1 | eco A = 0 | **−28.28 %** | 27.76 % | 1,367.6 s (−0.1 %) | 0.072 | ok |
| M0 | UDDS, L-R1 | eco A = 5 % | **−34.30 %** | 33.82 % | 1,437.4 s (+5.0 %) | 0.070 | ok |
| M0 | UDDS, L-EVE | eco A = 5 % | −29.50 % | 28.97 % | 1,437.4 s | 0.069 | **excluded**: the baseline run is incomplete (shortfall 1.64 %) |
| M1 | S2 | eco A = 0 / 5 % | **−1.46 / −9.67 %** | 1.48 / 9.66 % | 212.9 / 223.3 s | 0.047 / 0.046 | ok |
| M1 | UDDS, L-R1 | eco A = 0 / 5 % | **−28.99 / −34.34 %** | 28.48 / 33.83 % | 1,368.7 / 1,437.3 s | 0.071 / 0.069 | ok |
| M1 | UDDS, L-EVE | eco A = 5 % | −31.00 % | 30.49 % | 1,437.4 s | 0.069 | **excluded**: baseline shortfall 1.14 % |
| M2 | S2 | eco A = 0 / 5 % | −2.24 / −10.90 % | 4.34 / 13.46 % | 213.0 / 223.6 s | 0.045 / 0.042 | ok; A = 0 realises only 52 % of the DP value (falsification line: 50 %) |
| M2 | UDDS, L-R1 | eco A = 0 / 5 % | −25.26 / −30.66 % | 28.09 / 33.68 % | 1,368.9 / 1,437.1 s | 0.071 / 0.069 | ok |
| M2 | UDDS, L-EVE | eco A = 5 % | −28.07 % | 31.11 % | 1,437.1 s | 0.069 | ok (baseline shortfall 0.88 %) |

UDDS under L-EVE at A = 0 has no profile in any branch (time budget infeasible) and is recorded as "profile unavailable".

**Falsification test** (v1 §10: the simulated saving is opposite in sign or below half of S_found). It is **not met in any scenario**, so the DP eco result is not falsified. Under M0 and M1 the dynamic savings equal the DP predictions to within 0.5 pp. Under M2 they are 52–90 % of the prediction (§3).

**Where the savings come from** (UDDS, L-R1, M0; eco A = 0 vs baseline):
- friction braking falls from 73.5 to 0.44 Wh;
- motor/inverter loss falls from 173.4 to 130.9 Wh;
- the current-limit exceedance of the baseline (1.36 A·s; 6.5 A·s under L-EVE) disappears (0–0.002 A·s for the eco runs).

**Stress indicators (not capacity fade).** On UDDS with L-R1, eco A = 0 vs baseline:

| Branch | Ah throughput | ∫i² dt | Peak current |
|---|---|---|---|
| M0 | 28.5 → 21.3 Ah (−25 %) | −48 % | 301 → 295 A |
| M1 | 26.9 → 20.8 Ah | −47 % | — |
| M2 | 27.5 → 21.7 Ah | −50 % | — |

These are **not** converted into capacity fade. No defensible ageing law exists for the reference pack (protocol §9), and lower current peaks need not mean slower ageing (Keil 2015).

## 3. Numerical validity and reproduction (v1 §8, A1.4)

| Check | Result | Criterion → verdict |
|---|---|---|
| Time step 1 → 0.5 ms, R3-C (S2 and UDDS L-EVE, every available profile, every branch) | ΔE changed by **< 1e-4 pp** | < 0.01 pp: **pass** |
| Time step, R3-B | < 2e-7 pp | pass |
| Independent recomputation: E_pos + E_neg vs E_chem (every run) | ≤ 9e-14 relative | ≤ 1e-6: **pass** |
| Energy closure (every run) | valid, ≤ 1e-3 of throughput | pass |
| **QS vs dynamic, M0** | S2: +0.19 to +0.24 %. UDDS eco: +0.25 to +0.32 %. **UDDS baseline: +1.05 % (L-R1), +1.01 % (L-EVE)** | ≤ 1 %: **marginal fail on the two UDDS baselines** |
| **QS vs dynamic, M1** | S2: −0.21 to −0.18 %. UDDS: +0.21 to +0.29 % (eco), +0.94 / +1.00 % (baselines) | ≤ 1 %: pass (UDDS L-R1 baseline 0.999 %) |
| **QS vs dynamic, M2** | **+6.0 to +13.6 %** | ≤ 1 %: **FAIL** |

**Consequences.**
- Under M0 and M1, the DP gate values are stated to about 1 % resolution on UDDS and 0.3 % on S2.
- Under M2, the QS gate values (H, S, VSI) do not represent the dynamic plant better than about 6–14 %. M2's gate numbers are therefore stated only to that resolution, and M2's eco savings are quoted from the dynamic runs.

**Cause of the M2 gap.** This is a post-hoc diagnostic, `code/diagnose_m2_qs_gap.py` → `outputs/checks/m2_qs_gap.csv`, S2 baseline:
- R1's fixed LQR holds a mean |T| of **15.3 N·m at standstill** (58 s of S2).
- Under M0 and M1 that costs nothing, since the loss is zero at zero power. Under M2 the stall copper loss k_c T² costs **1.58 Wh**.
- Torque ripple and lag while moving add 0.32 Wh.
- In total that is 1.90 Wh, about 10.1 % of 18.8 Wh, matching the observed +10.3 %.

The gap is an interaction between the controller's holding torque and the stress model's stall loss. It is not an optimiser error. It also shows that M0 and M1 never charge for holding torque, a further simplification common to both.

**Not independent replication.** The QS model, the DP, the dynamic plant and the pilot share the same physics, parameters and author. The R2-port pre-checks show code equivalence, not independent confirmation.

## 4. What the pilots establish, and what they do not

- **Same task.** On this plant, SoH-scheduled LQR does not add energy benefit over an equal-budget fixed LQR. The widened fixed box covers the scheduled gain range. The result holds in all three loss branches: ≤ 0.04 % under M0 and M1, and 0.4 % *worse* under M2.
- **Supervisory layer.** R2's layer changes energy by < 0.01 %.
- **Eco-driving.** The fixed LQR can follow DP eco profiles closely (RMSE ≤ 0.072 m/s, complete, no current-limit violations). The predicted energy-time trade-off is realised: about 1.5–2.9 % at equal time on S2, about 25–29 % on UDDS at equal time, and more with 5 % extra time.
- **Not shown:**
  - that these magnitudes hold for a real vehicle, a real motor map with no-load losses, or a jerk-limited, causal eco controller;
  - anything about battery capacity fade.
