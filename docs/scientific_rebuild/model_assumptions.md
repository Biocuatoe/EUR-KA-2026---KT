# Model assumptions and what they exclude

**Date:** 2026-10-24.

**Scope.** This applies to the documented model (`docs/model.md`) and to its battery-limited
extension (`verification/scientific_rebuild_20261024/model_equations.md`).

**Five separate questions.** Each assumption below is classified by the question it affects:

| Code | Question |
|---|---|
| Math | Is the derivation valid? |
| Impl | Does the code implement the equation? |
| Num | Has the numerical solution converged? |
| Model | Does the model represent the intended physics? |
| Real | Does it predict a real vehicle? |

The project can establish **Math**, **Impl** and **Num**. It can say little about **Model**
and nothing about **Real**.

## Vehicle and drivetrain

| Assumption | Value / form | Source | Affects | What it excludes |
|---|---|---|---|---|
| Hypothetical vehicle | 850 kg, C_d·A 0.77 m², C_rr 0.008, r_w 0.28 m, G 6.5 | thesis Table 8, **report_unverified** | Model, Real | Any specific real micro-EV |
| Flat road | grade 0 | assumed | Model | Grade-dependent loads |
| Torque-controlled drive | first-order lag τ_T = 20 ms | assumed (thesis L2802 states 20 ms, contradicting its own L/R = 400 ms) | Model | Current-loop and voltage-limit dynamics of a real PMSM |
| Motor limits | 85 N·m, 18 kW | report_unverified | Model | Field weakening, thermal derating |
| Constant efficiencies | η_g 0.9702; η_mi 0.874 (peak) | report_unverified; peak used as constant | Model | Part-load efficiency effects of control (absolute Wh/km optimistic) |
| No traction or tyre slip | µ not modelled | thesis Assumption 3 | Model | Wheel-slip events |

## Battery

| Assumption | Value / form | Source | Affects | What it excludes |
|---|---|---|---|---|
| Generic 48 V, 100 Ah pack | constant V_oc 48 V | assumed (flat LFP plateau) | Model | The BOM's 16 × 3.2 V cells (51.2 V); OCV–SoC variation; the specific cell is unknown (owner item OC-1) |
| 1-RC Thevenin | R0 5 mΩ, R1 3 mΩ, C1 50 kF | report_unverified | Model | Temperature, hysteresis, diffusion |
| Resistance growth with SoH | R = R_new(1 + k(1 − SoH)), k_r0 0.5, k_r1 0.3 | thesis Eq. 4.28–4.29, no source; k_r0 = 2.0 used as a sensitivity assumption | Model | Measured resistance-growth trajectories |
| **No capacity-fade model** | SoH is an input, constant within a run | — | — | Any claim about lifetime, fade rate or battery-life extension (thesis C02/C04 cannot be tested) |
| SoH known exactly | oracle | assumed (best case for scheduling) | Model | Estimator error; an EKF as specified cannot identify capacity |
| Battery window (rebuild only) | V_t ∈ [0.78125, 1.140625]·V_oc; I ≤ c_dis·Q·s, −I ≤ c_ch·Q·s | assumed: ratios from the thesis's LFP range (2.5/3.2, 3.65/3.2; no source); C-rates 2–3 C / 0.5–1 C | Model | Temperature- and SoC-dependent BMS limits; real cell datasheets |
| SoH-scaled current limits (rebuild) | s = SoH | assumed BMS policy (limits as C-rate of *actual* capacity); BCN tests s = 1 | Model | Whether a real BMS derates with SoH |

## Controller and evaluation

| Assumption | Source | Affects | Excludes |
|---|---|---|---|
| Design model linearised at 30 km/h; same gains on UDDS and US06 | pre-registered | Model | Gain re-design for highway speeds |
| γ_v = γ_u = 1 | assumed (thesis gives no value) | Model | Other scheduling laws (γ swept in S-B, 0–10) |
| Deterministic runs, no noise (except S-D) | protocol | Num | Sensor effects (S-D only) |
| Reference cycles | S1/S2 synthetic; UDDS/US06 official EPA | — | Vietnamese traffic (none exists in the project) |

## Explicitly not claimed

- Validation against any vehicle, battery or test bench.
- An electrochemical or validated ageing model.
- Any battery-life effect. Ah throughput and RMS current are stress indicators only.
- Independent human replication.
- That agreement between Python and OpenModelica shows physical validity.
