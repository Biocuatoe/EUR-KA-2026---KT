# R3: implications for the thesis claims, and final decision

**Date:** 2026-10-25.
**Basis:**
- `R3_motor_curve_audit.md`
- `R3_test_report.md`
- `R3_optimizer_validity.md`
- `R3_gate_results.md`
- `R3_pilot_results.md`
- frozen `R3_protocol_v1.md` with `R3_protocol_v1_amendment_1.md`

**Status of every number below.** Each is a **new R3 simulation result for a defined reference plant**. It is not recovered original evidence, not the thesis's (unidentified) battery or motor, and not validated against a vehicle. Prepared by the AI assistant that built R1–R3; not reviewed by a person.

## 1. Final decision (the seven questions)

**1. Which model branches are physically justified, illustrative, or unavailable?**
- **M0** (constant η = 0.874) is the baseline. Its structure is the thesis's, and its value is unverified.
- **M1** (FASTSim 3.1.0 generic e-machine curve) is **illustrative**. It is a template shape for a 39–100 kW machine, not a Zoe measurement and not the thesis motor. It has no torque or speed axis, no no-load loss, and the source has no regeneration curve.
- **M2** (all-copper loss) is an **illustrative stress model**, favourable to the hypothesis by design.
- **No branch is physically justified for the thesis motor.** A measured 15–20 kW map is unavailable.
- **Battery limits:** L-R1 is assumed; L-EVE is a generic-cell SEC summary; L-EVE-s is exploratory.

**2. Does the current energy model support a reliable attainable-improvement bound?**
- **Only on the discretised quasi-static problem.** There, the dual bounds are certified (weak duality; DP exactness checked against enumeration), and duality gaps are ≤ 0.08 pp at the gate rows.
- Grid refinement moved H by 0.010 pp and S by ≤ 0.14 pp.
- The bounds do **not** extend to the continuous problem or the dynamic plant.
- The pre-specified QS-vs-dynamic check holds to about 0.3 % on S2 for M0 and M1. It is marginal on UDDS baselines (M0 +1.05 %) and **fails for M2** (+6 to +14 %, explained by holding torque at standstill under the stall-loss model).
- The gates are therefore reliable as screening results for M0 and M1, and only coarse for M2.

**3. Did a pilot pass the pre-specified gate and actually run?**
- **G-A** (SoH information) FAILED, certified on the grid, in every branch, so **R3-A was not run**.
- **G-B** (same-task headroom) PASSED in every branch, and still passes with the stop-respecting correction of amendment A1.1, so **R3-B ran**: F0/S0/F1/S1, three branches, 768 runs.
- **G-C** (eco-driving) PASSED, so **R3-C ran**: 51 rows.

**4. Did SoH scheduling add benefit beyond a fair fixed-gain baseline?**
- **No.** The best case for SoH information is VSI ≤ 0.086 % on held-out cycles (certified ≤ 0.09 % on the grid). Even the exploratory SoH-scaled limits give ≤ 0.29 %.
- In closed loop with equal budgets and a fixed box covering the scheduled gains, scheduling changed energy by ≤ 0.04 % under M0 and M1. Under M2 it was **+0.4 % worse**.
- "Improves" is met in no condition of any branch.
- The only SoH effect found is on *feasibility*: on UDDS under L-EVE, the aged pack cannot follow the SoH-1.0-optimal trajectory. That is not an energy benefit.

**5. Did any apparent energy improvement come instead from motor modelling, supervisory control, or eco-driving?**
- **Motor modelling.** It changes absolute energy: M1 is about 9 % lower than M0 by its higher peak efficiency. It also changes the size of the trajectory levers (H 4.3 vs 6.4 %). It does not create a SoH benefit.
- **Supervisory layer.** < 0.01 % effect.
- **Trajectory tolerance.** The real same-task lever: about 1 % per 0.05 m/s of allowed deviation, independent of SoH. It is not captured by any tested LQR, because they track closely.
- **Eco-driving.** The large numbers come from here, and from nowhere else:
  - about 1.5–2.9 % at equal trip time on S2;
  - about 25–29 % on UDDS at equal time;
  - about 10–14 % (S2) and 31–34 % (UDDS) with 5 % more time.

  These are realised in closed loop by a fixed LQR. They result from changing the driving task and are an energy-time trade-off. They are not SoH-aware control.

**6. Is there any evidence for the original 12.5 % energy or 15.3 % capacity-fade claims?**
- **No.** No R3 result supports 12.5 % as an effect of SoH-aware LQR. Only eco-driving, a different task, produces savings of that size, and their magnitude depends on the cycle and the time allowance.
- **No fade result exists.** No defensible ageing law is available for the reference pack. Ah throughput (about −25 %) and ∫i²dt (about −48 %) under eco-driving are stress indicators, not capacity fade, and they come from eco-driving, not SoH scheduling.
- **The provenance audit stands:** the original figures are untraceable (`../../numeric_claim_provenance_20261025/`).

**7. Is a larger experiment scientifically justified?**
- **Not for SoH-scheduled LQR energy savings on this plant class.** The certified grid bound on SoH information (< 0.1 %) is an order of magnitude below the threshold. More runs of the same comparison would only re-measure a null. It would reopen only with:
  - a measured cell whose current limits fall with SoH;
  - a real motor map with no-load losses;
  - temperature effects.
- **A different question is justified,** if the thesis direction can change: battery-aware **eco-driving** or **energy-optimal trajectory planning within a tracking tolerance**. Before any larger study it needs:
  - a jerk-limited, causal (preview-horizon) formulation;
  - a measured motor map;
  - the real battery datasheet;
  - honest labelling as an energy-time trade-off.

## 2. Suggested wording for the defence (consistent with Version B of `../../numeric_claim_provenance_20261025/defence_wording_options.md`)

> "A post-submission re-analysis (R1–R3), in simulation of a reference plant with documented assumptions, found no practical energy benefit from SoH scheduling of the LQR. The value of SoH information on the same tracking task is below 0.1 % even as a perfect-preview bound. The originally reported 12.5 % and 15.3 % cannot be traced to any retained computation and are withdrawn. The same re-analysis shows that the energy lever in such a drivetrain is the speed trajectory itself: eco-driving re-planning saves a few per cent at equal trip time on a smooth urban profile and much more on UDDS. This is a different research question, which I propose as future work."

## 3. What would reopen the SoH-scheduling question

1. The actual cell's datasheet: DCR(SoC, T) and current limits versus SoH and temperature (owner item OC-1). VSI can become material only if the limits depend on SoH.
2. A measured motor/inverter map including no-load and iron loss, and the holding-torque behaviour at standstill.
3. A same-cell ageing law or dataset, for any fade statement.

## 4. Boundaries

- No change was made to the thesis DOCX, R1/R2 code or outputs, frozen protocols, provenance reports, or historical evidence.
- All new work is under this directory.
- No Git operation was performed. Nothing was downloaded or installed.
