# Path decision matrix (Phase 3)

**Date:** 2026-10-25. **Inputs:** `baseline_scientific_position.md`,
`literature_gap_assessment.md`, `evidence_gates.md`, the R1 record, the Phase-1 energy ledger
(`../recovery_feasibility_20261025/`) and the P2 pilot (`pilot_results.md`).

**Relation to the 2026-10-25 "stop expansion" recommendation**
(`../recovery_feasibility_20261025/recommended_model_spec.md`):

- Its reasons remain binding unless resolved:
  1. no sourced cell limits;
  2. controller headroom below 1 % on a fixed reference;
  3. no fade model;
  4. unequal tuning budgets.
- New evidence since then:
  - (i) The literature now shows the *named* lines and their counter-evidence (Phase 2).
  - (ii) Secondary (retailer) ratings for generic 100 Ah LFP cells are 1C continuous and 2C
    30-s pulse. That is far below the 3C assumed in R1. At 48 V this means about 4.8–9.6 kW against
    an 18 kW motor, so a battery-limited regime is *plausible* for this powertrain, not an edge
    case. The rating is not a source for the thesis cell.
  - (iii) A fair, equal-budget factorial (F0/S0/F1/S1) can be run with existing verified code.
- Reason 4 is now resolved for the pilot. Reason 1 is bracketed, not resolved. Reasons 2 and 3
  stand.

---

## 1. Path P1: retain SoH-scheduled LQR as the core method

**Why R1 found nothing.** Each candidate explanation was examined:

| Candidate explanation | Verdict | Evidence |
|---|---|---|
| Inherent lack of benefit for a fixed-reference tracking task | **Main cause** | Analytical derivation: on a fixed reference, every energy-ledger line is a functional of the realised trajectory. A feedback gain can change energy only through the tracking error and the brake split. The measured gap to exact tracking is 0.11–0.20 % on S1/S2 (ledger §5.1). |
| No SoH-dependent mechanism in the controlled channel | **Main cause** | In the documented plant, SoH enters R0, R1 and the SoC rate. None appears in the velocity or torque dynamics. The thesis's ΔA = ΔR_int/L_eq treats battery current as an inductive state, which is not physical behind a current-controlled inverter (audit M-16). |
| Inadequate scheduling law | Contributing, not decisive | The thesis law lowers the torque weight and raises R as SoH falls, i.e. it is less aggressive, with no physical target. A γ sweep (0–10) changed energy by ≤ 0.04 % (R1 S-B). No scheduling law can exceed the gap to exact tracking without worse tracking. |
| Inadequate plant (missing efficiency map, thermal state, OCV(SoC)) | Possible but unquantifiable | With a constant η_mi the motor-loss lever is absent. A real efficiency map adds a lever only through the torque profile, which the trajectory fixes for a single motor. No source for the thesis motor's map was found. |
| Confounding by tuning | **Real in R1; repaired in the pilot** | R1: fixed family 164 runs with the best at the range edge; S untuned (γ = 1). Pilot: 24 LHS candidates each, same objective and seed. |
| Confounding by saturation | Not the cause | When limits bind, F and S sit on the same limit (R1 Fig. `udds_bcs_soh07_timeseries.png`). The pilot tests whether constraint awareness changes this (F1 vs S1). |

**Defensible way to evaluate the marginal contribution of scheduling without changing the task.**
Yes:
1. an equal-budget comparison on the same fixed reference (pilot S0 vs F0); and
2. the gap-to-exact-tracking bound as the ceiling for any feedback-gain benefit under a
   tracking guard.

Both keep the research problem unchanged.

## 2. Path P2: common battery-constraint supervisory layer, LQR for tracking

The layer (identical in F1 and S1) is constraint-aware anti-windup plus a feasible-reference
governor. Braking is unchanged. Friction blending is hardware in all branches. Its value is
judged by the factorial in `pilot_results.md`.

**Pilot outcome** (`pilot_results.md`; 257/257 runs valid; frozen protocol; convergence passed).
All five pre-registered predictions held, and all 40 held-out contrasts are NO PRACTICAL
DIFFERENCE:

| Effect | Size | Practical? |
|---|---|---|
| Scheduling given the layer (S1 vs F1) | −0.025 % to +0.013 % energy per reference km | no |
| Scheduling without the layer (S0 vs F0) | −0.025 % to +0.014 % | no |
| Layer (F1 vs F0; S1 vs S0) | 0 (S2, inert) to −0.016 % (UDDS); max \|e\| ratio 1.000 | no |
| Interaction | ≤ 0.0033 pp | no |

- The scheduled branch's lower RMSE at SoH 0.8 (ratio 0.741 on S2) is, by a post-hoc analysis, a
  gain-magnitude effect. Tracking here is SoH-invariant to 3.4e-6 m/s, and the fixed search box
  excluded the most aggressive gains. It is not SoH compensation.
- P2 is therefore **answered**: in this plant and these bracketed scenarios, neither SoH
  scheduling nor the constraint layer, nor their combination, gives a practical benefit.

## 3. Path P3: energy–time–health eco-driving layer with LQR tracking

- The literature establishes the line: Tawfik2024, LiB2024, Lot2025, Cai2026, Jia2022,
  Zhang2022, Wang2024, Djeffal2026.
- Ledger §5.4 shows that the leverage comes from trip time: 5 % slower gives 4.1–5.4 % less energy
  per km.
- A narrower contribution would be micro-EV, 48 V LFP state-of-power-limited eco-driving at equal
  trip time. It needs cell data and a fade law (gates 1, 3, 5 fail).
- It does not test the thesis's same-reference claim.

## 4. Decision table

| Criterion | P1 Retain SoH-scheduled LQR | P2 Constraint supervisor + LQR (F0/S0/F1/S1) | P3 Eco-driving + health layer |
|---|---|---|---|
| Preserves the submitted research direction (LQR + SoH + micro-EV) | **Yes, fully** | **Yes**: LQR and SoH stay; adds a layer the thesis lacks | Partly: LQR becomes an inner loop; the question changes to speed planning |
| R1 finding addressed | No benefit of S over F; unequal tuning | SoH matters only through limits; whether constraint handling, not scheduling, is what matters | Energy leverage lies in the speed profile (ledger §5.4) |
| Physical mechanisms required | None new (SoH → R0/R1 only) | Battery discharge/charge current limits, voltage window (SoP), torque lag, brake blending | Speed–time trade-off, SoP limits, a fade law |
| Required parameters | R1 set | current limits vs SoC/T/SoH; R0 growth; voltage window | the above + fade-law constants + time value or trip-time constraint |
| Source availability | R1 set (unverified thesis values) | **bracketed only:** retailer 1C/2C (SEC); Pan2023 R0 × 1.7 (FT); no thesis-cell datasheet | fade laws only for other LFP cells (Wang2011, Naumann2020; not read); time value has no basis |
| Evidence for novelty | No paper scheduling LQR on SoH for speed tracking was *found*; not verifiable (no IEEE/Scopus search) | The layer is not novel (Smith2009, Naseri2026, Corno2019, Samada2023). The *factorial question* (marginal value of scheduling given a layer) was not found | Weak: established line (§3) |
| Counter-evidence | Pan2023 (fixed ≥ adaptive weights); R1; ledger bound | Qamar2026: regen-limit assumptions alone move energy 3–12 %, so results depend on limit modelling | Keil2015, SunC2026 (current reduction ≠ life benefit); Lot2025, Djeffal2026 (savings bought with speed changes) |
| Complexity | Low | Low–moderate (done in the pilot with existing code) | High |
| Likely failure modes | Null result again | Layer helps tracking but not energy; scheduling still adds nothing; results hinge on assumed limits | Gains are time trades; fade results circular (same model in optimiser and evaluation) |
| What would falsify it | Equal-budget S0 vs F0 shows no practical difference (pilot P1/S0-F0) | Pilot predictions P1–P5 (`pilot_protocol.md` §6) | Equal-trip-time comparison shows < 1 % increment from battery awareness (F6 in `recommended_model_spec.md`) |
| Small pilot justified now? | No separate pilot (answered by R1 + the pilot's S0 vs F0) | **Yes, run** (gates pass in scenario form) | **No** (gates 1, 3, 5, 8 fail) |

## 5. Ranking by defensibility

Ranked by how well each path's claims can be defended with evidence that exists, not by expected
effect size.

| Rank | Path | Defensible claim it supports | What it cannot support |
|---|---|---|---|
| **1** | **P1 + P2 as an evaluation study** (retain SoH-scheduled LQR as the object of study; report R1, the pilot's equal-budget factorial and the gap-to-exact-tracking bound) | "In a documented, verified micro-EV model, SoH scheduling of LQR weights gives no practical energy or tracking benefit over an equally tuned fixed gain, with or without battery-constraint supervision. A fixed-reference task bounds any feedback-gain energy benefit to the gap to exact tracking (0.11–0.20 %)." | Any positive performance claim; any statement about the real vehicle or cell |
| 2 | P2 as a *constraint-management* contribution | Nothing practical in the tested brackets (layer effect ≤ 0.016 % energy, ≤ 3.3 % current-limit exceedance). Would become relevant only with source-grounded, much tighter limits | Novelty of the layer itself (Smith2009, Naseri2026, Corno2019, Samada2023) |
| 3 | P3 eco-driving + health | Nothing yet; gates fail; established field | Any test of the thesis's same-reference claim |

**Decision.** Pursue rank 1 as the defended contribution. Do not start a larger P2 sweep (the
pilot's §8 criterion was not met). Do not start P3 under this project. Reopen P2 only if
source-grounded limits for an identified cell become available (owner item OC-1). Reopen P3 only
as a separately scoped eco-driving study with its own gap check.

This **re-evaluates and refines** the earlier "stop expansion" decision rather than repeating it.
The new evidence (equal-budget factorial, interaction test, literature) did not resolve its
binding reasons in favour of a benefit, but it converts the negative result into a fair,
factorial, pre-registered one.
