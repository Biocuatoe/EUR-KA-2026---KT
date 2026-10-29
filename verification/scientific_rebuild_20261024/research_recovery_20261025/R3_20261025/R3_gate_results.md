# R3 gate results (Step 6)

**What this is:** quasi-static (QS) dynamic-programming results for the R3 **reference plant** (`R3_model_basis.md` §3). It is not the thesis vehicle, not a real vehicle, and not recovered original evidence. Each number belongs to one motor-loss branch; branches are never pooled.

**Runs:**
- **Frozen run.** `code/run_gates.py` under `R3_protocol_v1.md` (SHA-256 `d9e82f89…bae56`, frozen 15:32:14). It ran 2026-10-25 15:32–15:44: 47 tasks, **0 errors**, exit 0. Raw outputs are in `outputs/gates/`, with hashes in `outputs/gates/run_manifest.json`.
- **Amendment run.** `code/run_gates_a1.py` under `R3_protocol_v1_amendment_1.md` (SHA-256 `51a2e93b…1e64`, recorded 15:48:29, before the run). It ran 15:48–15:59: 27 tasks, 0 errors. Outputs are in `outputs/gates_a1/`.
- **Decisions** were applied mechanically by `code/evaluate_gates.py`: `outputs/gates/gate_decisions.json` and `outputs/gates_a1/gate_decisions.json`.
- **Tables** below come from `code/summarise_gates.py` (`outputs/gates/summary_tables.txt`).

**Reading the numbers** (`R3_optimizer_validity.md` §3):
- **found** is the saving of a feasible trajectory that was actually evaluated;
- **max** (in brackets) is a certified upper bound **for the discretised QS problem only**;
- neither bounds the continuous problem or the dynamic plant.

## 1. Decisions

| Gate | Quantity | M0 | M1 | M2 | Frozen rule outcome |
|---|---|---|---|---|---|
| G-A | VSI (same task, SoH information) | 0.011 % (max 0.084 %) | 0.086 % (max 0.086 %) | 0.004 % (max 0.009 %) | **FAIL-certified-on-grid**, all branches → no R3-A pilot |
| G-B | H(0.25), same task | 5.32 % | 6.70 % | 7.35 % | **PASS**, all branches → R3-B pilot |
| G-C | S(0) or S(5 %), eco | 34.3 % | 34.2 % | 34.0 % | **PASS**, all branches → R3-C pilot |
| G-A′ (A1.1) | VSI, stop-respecting band | 0.005 % (max 0.007 %) | 0.057 % (max 0.079 %) | 0.004 % (max 0.004 %) | FAIL-certified-on-grid |
| G-B′ (A1.1) | H(0.25), stop-respecting band | 4.93 % | 6.44 % | 5.20 % | PASS (interpretation only; the pilot was already triggered by G-B) |

Decision-robustness check (protocol §4): no deciding value lies in [0.5 %, 2 %], so it was not triggered.

## 2. Baseline task (protocol §3.3)

| Cycle | Limits | Exact reference feasible? | Baseline vs v_ref (RMS / max m/s), shortfall | Friction energy at baseline |
|---|---|---|---|---|
| S2 | L-R1, L-EVE | yes, all branches | 0 / 0, 0 % | 0 Wh |
| S1 (in-sample) | L-R1 / L-EVE | yes / no | 0 / 0 and ≤ 0.04 / ≤ 0.50, ≤ 0.04 % | 2.3–3.1 Wh |
| UDDS | L-R1 | no (7–41 infeasible steps) | 0.10–0.16 / 1.25–1.75, ≤ 0.14 % | 70–81 Wh (≈ 8–10 % of energy) |
| UDDS | L-EVE | no (93–120 steps) | 0.49–0.69 / 3.5–3.9, 0.86–1.62 % | 69–81 Wh |

UDDS L-EVE baselines for M0 (1.62 %) and M1 (1.13 %) exceed 1 % shortfall, so they **do not qualify** for gates (protocol §4); M2 (0.86 %) does. Full table: `summary_tables.txt` §Baselines.

## 3. R3-A: same trajectory task, and the value of SoH information

**VSI** is what knowing SoH 0.8, rather than designing for SoH 1.0, is worth on the same task, with perfect preview (protocol §3.6). The largest values were:

- **Held-out qualifying:** found ≤ 0.086 % and max ≤ 0.086 % in every branch.
- **Exploratory L-EVE-s:** up to 0.12 % (frozen) and 0.29 % (stop-respecting, max).
- **In-sample S1:** up to 0.60 %, under M1 with L-EVE-s (exploratory).

On the grid every qualifying upper bound is below 0.09 %, i.e. more than ten times below the 1 % threshold. Eco-VSI at A = 0 is ≤ 0.08 %.

**"P1 design infeasible on aged plant"** occurs in 4–8 UDDS L-EVE scenarios. The SoH-1.0-optimal trajectory demands discharge power that the aged pack's voltage window no longer allows: R0 is higher, so the voltage limit binds earlier. Here SoH changes **what is feasible**, not the energy of feasible trajectories. A SoH-aware controller could matter there for tracking or feasibility, but not for energy. That is not what the thesis claims.

**Why VSI is so small.** At SoH 0.8 the plant differs from SoH 1.0 only in R0 (× 1.10 or × 1.70) and capacity (SoC bookkeeping). The R0 loss is 1–3 % of energy, and the optimal trajectory hardly changes when it grows. The current limits under L-R1 and L-EVE do not depend on SoH. Only the exploratory L-EVE-s makes them depend on SoH, and even there VSI stays below 0.3 %.

### Separation required by Step 6 (same task)

| Component | Size on held-out cycles (QS) | Basis |
|---|---|---|
| Energy at the baseline task (unavoidable for that trajectory) | S2: 33.4–36.7 Wh per reference km; UDDS: 63.7–74.1 Wh per reference km, branch-dependent | `band_rows.csv` E_b |
| Variation from a different realised trajectory within ±δ | H(0.25) 4.3–6.4 % with stops respected; ≈ 0.9–1.8 % per 0.05 m/s; same in P1, P2, P3 within 0.4 pp | §4 |
| Variation from regeneration/friction allocation at a fixed trajectory | M0, M1: zero (maximal regeneration is optimal and already used). M2: ≤ 0.27 % (`check_m2_regen_split.py`, A1.2) | `outputs/checks/m2_regen_split.csv` |
| Losses a controller cannot change at fixed trajectory | all of them: aerodynamic, rolling, gear, viscous, motor/inverter and R0 losses are functions of the trajectory | `R3_model_basis.md` §2 |
| Not quantifiable here | motor no-load or iron loss, temperature, OCV(SoC), the cell's real limits versus SoC and temperature. Torque lag and V1 are absent in QS and present only in pilots | `R3_motor_curve_audit.md` §3; `R3_model_basis.md` §1 |

The constant-efficiency loss fraction (15–31 % of energy) was **not** used as a bound on controller savings anywhere.

## 4. R3-B: same task, any controller or supervisory layer

**Frozen G-B.** Some feasible trajectory within ±0.25 m/s of the baseline task, at equal time and distance ≥ the baseline's, uses 4.6–7.3 % less energy per reference km. The duality gaps are ≤ 0.08 pp.

**Material flaw (amendment A1.1).** The frozen band let the vehicle move at up to δ while the task is at rest. The DP did so at every such sample, covering 0.5–2.3 % of the distance there (`outputs/checks/band_path_description.csv`).

**Stop-respecting band.** With v = v_b enforced at standstill, H(0.25) is still:
- 4.3–4.9 % under M0;
- 5.4–6.4 % under M1;
- 4.7–5.2 % under M2.

The artefact explained about 0.3–2.5 pp, mostly under M2 on S2.

| H_found %, stop-respecting, P1, L-R1 | δ = 0.05 | 0.10 | 0.25 | 0.50 |
|---|---|---|---|---|
| S2 M0 / M1 / M2 | 0.91 / 1.80 / 1.16 | 1.79 / 3.13 / 2.20 | 4.34 / 6.44 / 4.72 | 8.24 / 10.79 / 7.09 |
| UDDS M0 / M1 / M2 | 1.31 / 1.46 / 1.30 | 2.36 / 2.67 / 2.41 | 4.86 / 5.37 / 5.07 | 8.35 / 9.02 / 8.57 |

**Mechanism** (from the saved paths):
- The optimal band trajectory runs about 0.06–0.09 m/s below the baseline on average while moving, with speed peaks 0.25 m/s lower.
- It recovers the distance by staying near the top of the band elsewhere. This cuts the kinetic-energy throughput under M0 and M2 by 6–10 %.
- Under M1 the throughput can rise while energy falls. M1's efficiency is lowest at low power fraction, so the optimum shifts operating points towards the 40–60 % plateau.

The lever is **tracking tolerance**: how the vehicle deviates within a tolerance band. It does not depend on SoH (the values for P1, P2 and P3 agree within 0.4 pp), and nothing in it needs SoH information.

**What G-B does and does not show:**
- It shows a large same-task energy sensitivity to small, structured trajectory deviations in this QS model.
- It does **not** show that an LQR, a scheduled LQR, or R2's supervisory layer captures any of it. That is what the R3-B pilot tests.
- The bound is perfect-preview and non-causal. A tracking controller only follows the reference it is given.

## 5. R3-C: eco-driving (a different task)

| P1, S_found % [max], trip-time change % | A = 0 | A = 2.5 % | A = 5 % | A = 10 % |
|---|---|---|---|---|
| S2 M0 / M1 / M2 (L-R1 = L-EVE) | 2.85 / 1.48 / 4.34 | 9.98 / 6.43 / 9.86 | 14.21 / 9.66 / 13.46 | 20.01 / 14.13 / 18.64 |
| UDDS L-R1, M0 / M1 / M2 | 27.8 / 28.5 / 28.1 | 31.0 / 31.4 / 31.1 | 33.8 / 33.8 / 33.7 | 38.4 / 37.8 / 38.1 |
| UDDS L-EVE, M0 / M1 / M2 | infeasible / infeasible / infeasible | infeasible / 27.8 / 28.3 | 29.0 / 30.5 / 31.1 | 34.2 / 34.7 / 35.7 |

**Infeasible cells.** The fastest eco trip found is 3.8 % (M0), 1.6 % (M1) and 1.3 % (M2) longer than T_ref, because L-EVE's 2C limit cannot deliver the reference's accelerations.

**Deviation from the reference** (RMS, time domain):
- S2: 0.18–0.19 m/s at A = 0 and 1.1–2.5 m/s with allowances.
- UDDS: **6.2–7.0 m/s at every allowance**.

The UDDS eco profile is a different speed history. It cruises steadily, accelerates within the cycle's own extreme acceleration range, and redistributes time across the 17 segments.

**Where the UDDS saving comes from:**
- The baseline loses 70–81 Wh, about 8–10 %, to friction braking beyond the 1C charge limit. The eco profile loses 0–1.7 Wh.
- The rest comes from removing the reference's speed oscillations (a kinetic-energy round trip at η² ≈ 0.7–0.9).

**Interpretation:**
- Savings are a property of the changed driving task. They are an **energy-time trade-off** wherever A > 0, and never attributable to SoH scheduling (protocol §7).
- **Eco-VSI** at A = 0 is ≤ 0.08 %.
- **No jerk limit** is imposed (`R3_optimizer_validity.md` §5), so whether a controller can follow these profiles is tested only by the R3-C pilot.
- **H-C** is not falsified: S_max(5 %) is ≥ 1 % in every branch.

## 6. Numerical checks (protocol §8)

| Check | Result | Criterion |
|---|---|---|
| Band, S1 M2 L-EVE P3 δ 0.25: (1 s, 0.01) → (0.5 s, 0.005) | H_found 4.557 → 4.567 %, Δ = **0.010 pp** | < 0.05 pp: pass |
| Eco, S1 M2 L-EVE P1: (2 m, 0.1) → (1 m, 0.05) | A = 0: 12.40 → 12.54 % (Δ **0.14 pp**); A = 5 %: 18.60 → 18.62 % (Δ **0.02 pp**) | < 0.2 pp: pass |
| Duality gaps | ≤ 0.08 pp at qualifying gate rows (H, S); VSI max − found ≤ 0.08 pp | reported |
| Errors | 0 / 47 and 0 / 27 tasks | — |

The checks cover the stated cases only. Continuous-problem behaviour is inferred from them, not proved.

## 7. What would change these results

- **A measured 15–20 kW motor/inverter map with no-load losses.** It would replace M1 and M2, and could change H and S in either direction.
- **The real cell's current limits versus SoH, SoC and temperature.** If limits fall with SoH, a VSI mechanism could appear. The exploratory L-EVE-s gives < 0.3 % here.
- **A causal, jerk-limited eco formulation.** It would give a more realistic, smaller S.
