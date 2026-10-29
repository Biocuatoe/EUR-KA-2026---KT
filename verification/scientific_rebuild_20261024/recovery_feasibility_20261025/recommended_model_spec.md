# Recommendation, minimal model specification and evidence gates

**Date:** 2026-10-25. **Status:** proposal. Nothing here is frozen, run or committed.
The completed R1 study, its frozen protocol (SHA-256 `d80b5b4f…479c`) and the pre-registered
348-run study are unchanged and are not revisited.

**Independence.** Written by the same AI assistant that produced R1; no person has reviewed it.

---

## 1. Recommendation

**Stop expansion: the evidence does not justify developing a battery-aware constrained controller,
a degradation-aware objective, or an eco-driving framework as an extension of this study.**

This is one of the four options offered, and not a hedge between them. The reasons, each
traceable to a computed number:

1. **Same-cycle comparison (continue as is): already answered.** Controller-attributable energy
   differences are 0.04–0.28 % across F, S and F01 (assessment §4.2), the gap of the best tested
   controller to exact tracking is 0.11–0.20 % (§5.1), and R1 found no practical difference in 112
   of 112 pairs. Nothing remains to run.
2. **Battery-aware constrained controller: headroom is below the pre-registered margin and rests on
   unsourced limits.** The indicative sum of the gap to exact tracking and the avoidable friction
   braking is ≲ 0.8 % of energy (§6 of the assessment), against a 1 % practical-difference margin.
   The friction part exists only under assumed charge-current limits; the tracking part is zero if
   the limits are higher. The tracking *failures* under tightened limits are caused by the discharge
   limit and no controller recovers them without changing the reference.
3. **Degradation-aware objective: no justified fade model and a negligible lever.** Stress
   indicators differ by ≤ 0.23 % (Ah), ≤ 0.48 % (RMS current) and ≤ 0.044 % (peak current) across
   the tested controllers, and the only LFP fade laws found are for other, small cells.
4. **Eco-driving / speed-reference layer: large effect, wrong question.** Slowing the reference by
   5–10 % changes energy per km by 4–10 % (§5.4), but the saving is bought with trip time, exists
   whether or not the battery ages, and is an established field whose literature was not reviewed
   here. A battery-aware increment over a battery-agnostic eco layer exists only where limits bind,
   i.e. again only through the unsourced limit law.
5. **The Phase 4 stop rules are met.** (a) The only proposed gains depend on parameters nobody has
   sourced (charge/discharge limits and their derating with SoH). (b) The completed comparison has
   an unequal tuning budget (S used γ = 1 untuned, F01 was tuned once on S1), which a new study
   must remove. (c) The gain does not clear the practical margin even on the favourable
   assumptions. A pilot would therefore consume effort to confirm a number the accounting already
   brackets.

**Consequences.**
- `pilot_protocol.md` was **not** written, because the instruction was to write it only if the
  extension is justified. The conditional pilot and its go/no-go criteria are in §5 and §6 below.
- No small deterministic pilot of a new controller was run. The predicted-versus-actual accounting
  check of Phase 4 was done on existing runs instead (assessment §2: reference-only wheel energy
  against simulated wheel energy, agreement within 0.12–0.22 %).
- The thesis claims of 12.5 % and 15.3 % remain unsupported (R1 report §6). Nothing in this
  assessment is evidence for either.

**What would reopen the question (any one of these, from the owner, not from the model):**
- the cell part number and a datasheet with DCR vs. SoC/T, voltage window and current limits
  (owner item OC-1), and a pack topology that reconciles the 48 V figure;
- or a change of research question to eco-driving or to an energy-time-wear trade study, with its
  own literature gap check.

---

## 2. Smallest parameter set that materially affects the question

Ranked by R1's measured pathway effects (UDDS, SoH 0.7, controller F;
`analysis_report_20261024.md` §4):

| Rank | Parameter | Evidence of materiality | Source today |
|---|---|---|---|
| 1 | Discharge and charge current limits (magnitude, vs. SoC and T) | Existence of limits: +6.5 % energy, RMSE +168 % | Assumed (3 C/1 C, 2 C/0.5 C) |
| 2 | Whether and how those limits derate with SoH | SoH scaling: +1.2 % energy, RMSE +228 %; it is the only route by which SoH reaches the dynamics | Assumed, no source |
| 3 | R0 at SoH 1.0 and its growth (k_r0) | 4× growth: +1.5 % energy; ohmic share 1–3 % | Thesis, unverified |
| — | Voltage window | Never reached (on UDDS R0 would have to be at least 3.3× its new-cell value; more on S1, S2) | Immaterial at this fidelity |
| — | R1, C1, OCV curve, capacity | No effect on energy or tracking at this fidelity | Immaterial here |
| (C only) | Fade-law constants and the wear price λ | Defines the only quantity option C reports | Published laws exist for other cells |

Items 1–3 all require the datasheet of the actual cell. Everything else may stay as in the
legacy model.

---

## 3. Minimal model specification if the study is reopened

**Plant (unchanged from R1 where not listed).**
- Longitudinal dynamics, constant η_g, η_mi, motor torque limits as in `model_equations.md`.
- Battery limits from a datasheet, as a function of SoC, T and SoH: I_dis(·), I_ch(·), V_min,
  V_max; R0(SoC, T, SoH). SoH known exactly (best case, stated).
- No fade state in the first stage. No thermal state unless the datasheet current limit is
  temperature-dependent in the operating range.
- A second, independent implementation of the new plant elements (Modelica), agreeing to the R1
  criterion, before any comparison is run.

**Controllers (all share plant, reference, torque limits, anti-windup and initial state).**
1. **C1** fixed-gain LQR, gains chosen by the tuning procedure below.
2. **C2** SoH-scheduled LQR, with the weight-scheduling parameters (γ_v, γ_u) *and* the base
   weights treated as tuning variables under the same procedure and budget.
3. **C3** battery-aware constrained/supervisory variant, only if the headroom gate (§5, G1) passes.

**Tuning.** One documented procedure applied identically to C1–C3: a fixed number of deterministic
evaluations per controller (a grid or Latin hypercube, number stated in advance), on a *training*
set; selection by the same constrained objective:

    minimise energy per actual km  subject to  distance shortfall ≤ 1 %,  RMSE ≤ 1.10 · RMSE(F)

where F is the pre-registered fixed reference gain, so no controller can win by tracking worse.

**Scenarios.** Training: S1, S2 and the first part of UDDS. Held-out: the remainder of UDDS and at
least one additional official cycle added with recorded provenance (requires approval to fetch).
US06 only as a labelled capability stress case; it exceeds the vehicle in every class so energy
per km on it is not comparable.

**Metrics (per run).** Energy per actual km and per reference km; distance shortfall; RMSE; peak
|e|; limit exceedances (I_over, torque, voltage); regeneration at the terminals and its fraction of
wheel braking energy; friction-brake energy; Ah throughput, RMS and peak current as stress
indicators. Capacity fade is reported **only** if a fade law with stated provenance and
uncertainty exists; otherwise it is "not computed", as in R1.

**Reporting.** A table of (energy/km, RMSE, shortfall, stress indicators) for C1, C2, C3 per
scenario, with non-dominated entries marked. A controller is said to **improve** only if
ΔE ≤ −1 % with RMSE ratio ≤ 1.10 and shortfall ≤ 1 % against the tuned C1 on *held-out* scenarios.
Lower energy with worse tracking or incomplete cycles is a trade-off, reported as such.

**Versioning.** The new protocol is `R2`, separate from R1 and the pre-registered study, with its
own frozen text and SHA-256 recorded in every manifest. This document is a proposal, not R2.

---

## 4. Tests that can falsify the proposed extension

Each is fixed before any run and has a numeric kill criterion.

| ID | Test | Falsified (stop) if |
|---|---|---|
| F1 | **Headroom, no controller:** recompute the assessment's gap to exact tracking and forced-friction floor with sourced limits | (gap + avoidable friction) < 1 % of energy on every complete, in-capability scenario |
| F2 | **Equal-budget fixed baseline:** C1 tuned with the same budget as C2/C3 | C1 within 0.1 % of C2/C3 energy at no worse RMSE (R1 already shows this for an untuned S) |
| F3 | **Limit-law robustness:** repeat with limits SoH-scaled and not, and over the datasheet tolerance range | the sign or size (≥ 1 %) of the gain changes between variants |
| F4 | **Time- and distance-matched comparison** | the energy gain disappears when completion and trip time are enforced equal |
| F5 | **Held-out cycles** | gain on held-out scenarios < 1 %, or opposite in sign to training |
| F6 | **Battery-awareness increment** (option D only): battery-aware vs. battery-agnostic eco layer at equal trip time | increment < 1 % |
| F7 | **Numerical:** halve dt | ΔE changes by ≥ 0.01 percentage points |
| F8 | **Accounting:** predicted ledger vs. actual pilot ledger | any ledger line differs by > 0.1 % of energy, or closure > 1e-3 |

---

## 5. Conditional pilot (not authorised)

Run only if the owner supplies the inputs in §1 and G0–G2 below pass.

**Gate G0 (inputs).** Cell identified; datasheet limits, DCR and voltage window obtained; pack
topology reconciled with the plant voltage; units checked.
**Gate G1 (headroom, analysis only).** F1 survives: (gap + avoidable friction) ≥ 1 % of energy at
some complete, in-capability scenario with sourced limits.
**Gate G2 (baseline).** The tuning procedure of §3 is frozen in R2 and the plant extension passes
its independent-implementation check.

**Pilot P1 (small, deterministic).** Cycles S1 and UDDS (held-out part); SoH 1.0 and 0.7; limits
at nominal and at the bounds of the datasheet tolerance; controllers C1, C2, C3 (12 to 36 runs).
No parameter is tuned on the pilot scenarios.

---

## 6. Evidence that justifies moving from the pilot to a larger experiment

All of the following, on the pilot, are required. Deterministic runs carry no confidence
intervals; the sensitivity box replaces them.

1. **Accounting agreement (F8):** every ledger line of every pilot run within 0.1 % of energy of the
   pre-run prediction; energy closure ≤ 1e-3 of throughput; zero invalid runs.
2. **Effect size:** the candidate controller beats the equal-budget tuned fixed LQR by ≥ 1 % in
   energy per actual km, with RMSE ratio ≤ 1.10 and shortfall ≤ 1 %, on a held-out scenario.
3. **Robustness (F3):** that margin holds at every corner of the datasheet tolerance box and under
   both limit-law variants, not only the nominal one.
4. **Fairness (F2):** the margin survives doubling the tuning budget of the fixed baseline.
5. **Mechanism:** the energy difference is traced in the ledger to a named line (friction brake,
   regeneration, tracking gap) and matches the G1 prediction in sign and magnitude. A gain with no
   ledger explanation is a defect to find, not a result.
6. **No substitution of metrics:** if energy improves, Ah throughput, peak current and RMSE do not
   worsen beyond the pre-stated margins; otherwise the result is reported as a trade-off and does
   not justify scaling.
7. **Numerical (F7)** and an **independent implementation** of the new plant elements agree.
8. **Novelty check:** a literature search against IEEE/Scopus-class databases for the constrained
   variant, since the earlier review used only open indexes and so cannot support "novel".

If any one fails, the larger experiment is not run and the failure is reported. A large grid is
never launched to look for a margin the pilot did not show, and no result is tuned to 12.5 % or
15.3 %.

---

## 7. What this recommendation does not say

- It does not say that SoH-aware control can never help. It says that, in this model, with the
  parameters that exist, the evidence shows no practical controller benefit and no sourced reason to
  expect one.
- It does not validate or refute anything about a real vehicle or pack.
- It does not rank eco-driving as unpromising; it says that effect belongs to a different study.
