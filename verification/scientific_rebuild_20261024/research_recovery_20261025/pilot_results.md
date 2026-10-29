# P2 pilot results: SoH scheduling × battery-constraint supervisory layer

**Date:** 2026-10-25. **Protocol:** `pilot_protocol.md`, frozen before any run (SHA-256
`ebebc1570704b26f01290e34f6206c8980c41445e7d6f322c585b34fbd112b5a`). It was not amended, and the
deviation log (§10) is empty.

**Status of every number below:** simulation result under an **assumed scenario**. It is not
behaviour of the thesis vehicle, not real-vehicle validation, and not a capacity-fade result.

**Sources:**
- `pilot/out/{tune,eval,conv}/` (runs and manifests);
- `pilot/out/analysis/verification.json` (`verify_pilot.py`);
- `decisions.json`, `contrasts.csv`, `branch_runs.csv` and `pilot_tables.md` (`analyze_pilot.py`, pre-registered rules);
- `posthoc.json` (`posthoc_checks.py`, **post-hoc, not pre-registered**, labelled wherever used).

---

## 1. Run accounting and integrity

| Stage | Planned | Present | Missing | Duplicates | Invalid | Max energy-closure error | Exit code | Runtime |
|---|---|---|---|---|---|---|---|---|
| tune (4 branches × 24 LHS × T1, T2; S1) | 192 | 192 | 0 | 0 | 0 | 3.2e-10 | 0 | 134 s |
| eval (3 cycles × 5 conditions × 4 branches + 1 R1 check) | 61 | 61 | 0 | 0 | 0 | 8.7e-10 | 0 | 2,110 s |
| conv (UDDS E3 × 4 branches, dt = 0.5 ms) | 4 | 4 | 0 | 0 | 0 | 2.8e-11 | 0 | 979 s |
| **Total** | **257** | **257** | **0** | **0** | **0** | | | |

**Checks** (`verification.json`; no problems recorded):
- Every manifest records the frozen protocol hash, and the protocol file on disk still has it.
- Every recorded source-file hash (pilot code, R1 `src/rebuild`, `src/eureka`, parameters) matches
  the file on disk.
- All 257 gains, recomputed from the recorded tuning parameters, equal the stored gains
  (maximum difference 0.0).
- All 61 evaluation rows use exactly the gains selected in `tune/selected.json`.
- A scheduled gain at SoH 1.0 equals its fixed base gain (maximum difference 0.0).
- **R1 reproduction:** the layer-off branch with R1's F gain on S2/BCN/SoH 1.0 reproduces R1's
  saved run with difference **0.0** in Wh/km, RMSE, net energy and friction energy. The tolerance
  is 1e-9.
- No traceback in any stage log.

**Recorded discrepancies (preserved):**
1. The `conv` manifest has no `n_invalid` field (a coding omission). Its 4 runs were checked valid
   directly.
2. Pilot runs store metrics only, not the final state vectors that R1 saved. Energy is checked
   through the per-run closure error, not by recomputation from raw states.
3. Terminal voltage was not recorded per run. The voltage window cannot bind here: R0 at most
   1.7 × 5 mΩ = 8.5 mΩ, against a binding threshold of 16.4 mΩ on UDDS (`../results/precheck_cycles.csv`).
4. A stray `python -` process from an earlier malformed command of mine ran concurrently and
   competed for CPU. Stopping it was refused by the session's permission policy. It affected
   runtime only; it shares no files with the pilot.

**Tuning outcome** (`tune/selected.json`):
- All four branches found feasible candidates: F 24/24, S 23/24.
- F0 and F1 selected the same gain (σ = 0.298, c = 0.0145); S0 and S1 selected the same gain
  (σ = 0.318, c = 0.0411, γ_v = 9.27, γ_u = 1.99).
- **Reason:** in the training scenarios (S1, 3C/1C) the battery *drive* limit never bound (0 % of
  steps; the governor was never active). The layer therefore could not influence tuning. This
  follows from the pre-registered design and was not changed.

## 2. Conventions

- **ΔE % = 100·(E_a − E_b)/E_b.** The denominator is always the comparison branch b: F for the
  scheduling contrasts, the layer-off branch for the layer contrasts. Negative = a uses less.
- **Primary energy:** net battery energy per **reference** km (protocol §6). Energy per **actual**
  km is also reported. Over all held-out contrasts its largest magnitude is 0.0228 %
  (`posthoc.json`).
- **Interaction** = ΔE(S1 vs F1) − ΔE(S0 vs F0), in percentage points. It is the scheduling effect
  with the layer minus the scheduling effect without it.
- **"Complete"** = distance shortfall ≤ 1 % in both runs. Every run lasts the full cycle
  (S2 213 s, UDDS 1,369 s), so travel time is equal by construction and any tracking deficit
  appears as a distance shortfall.

## 3. Feasibility first (held-out cycles; values are ranges over the four branches)

| Cycle / condition | Shortfall % | RMSE m/s | max \|e\| m/s | Battery-limited % of steps | Current-limit exceedance A·s | Friction Wh | Regen Wh | Meets the tuning tracking requirement (RMSE ≤ 0.10, max \|e\| ≤ 1.0)? |
|---|---|---|---|---|---|---|---|---|
| S2 E1 nominal | −0.03 | 0.023–0.025 | 0.088–0.095 | 0 | 0 | 0 | 13.79 | yes |
| S2 E2 aged (R0 × 1.7) | −0.03 to −0.02 | 0.017–0.023 | 0.068–0.088 | 0 | 0 | 0 | 13.79 | yes |
| S2 E2b aged (R0 × 1.1) | −0.03 to −0.02 | 0.017–0.023 | 0.068–0.088 | 0 | 0 | 0 | 13.79 | yes |
| S2 E3 constraint (2C/0.5C) | −0.03 to −0.02 | 0.017–0.023 | 0.068–0.088 | 0 (only the charge limit acts) | 0 | 0.26 | 13.56–13.57 | yes |
| S2 E4 SoH-scaled (exploratory) | −0.03 to −0.02 | 0.017–0.023 | 0.068–0.088 | 0 | 0 | 1.11 | 12.84–12.85 | yes |
| UDDS E1 nominal | 0.26 | 0.180 | 2.13 | 3.96–4.02 | 10.8–10.9 | 71.4–71.5 | 234.1 | **no** (all branches) |
| UDDS E2 aged | 0.30 | 0.193–0.195 | 2.27–2.28 | 4.45–4.49 | 12.1–12.2 | 70.5 | 234.7–234.9 | **no** |
| UDDS E2b aged | 0.27 | 0.180–0.182 | 2.15 | 3.94–4.08 | 10.7–11.1 | 71.3–71.4 | 234.0–234.2 | **no** |
| UDDS E3 constraint | **2.29–2.30 (INCOMPLETE)** | 0.74 | **4.73–4.74** | 12.8–12.9 | 31.0–31.4 | 169.3–169.4 | 149.9 | **no: tracking failure** |
| UDDS E4 SoH-scaled | **4.42–4.43 (INCOMPLETE)** | 1.20 | **6.06** | 19.4–19.5 | 41.9–42.2 | 197.2–197.4 | 124.9 | **no: tracking failure** |

**Flags.**
- On UDDS no branch meets the tracking requirement, even at E1. The causes are the 18 kW motor
  limit (the reference exceeds it 0.29 % of the time) and the assumed 3C battery limit (about 4 % of
  steps).
- UDDS E3 and E4 are incomplete cycles with maximum errors of 4.7–6.1 m/s. Their energy per km is
  **not interpretable as efficiency**. Energy per actual km is 2.3–2.4 % (E3) and 4.4–4.6 % (E4)
  above energy per reference km. Lower energy per *reference* km there reflects distance not
  driven.
- The current-limit exceedance comes from the 20 ms torque lag (as in R1). It is present in all
  branches and differs between branches by at most 0.41 A·s.

## 4. Matched comparisons (held-out cycles)

ΔE per reference km in %; "S/F" = RMSE ratio of scheduled to fixed; "layer" = max |e| ratio of
layer-on to layer-off.

| Cycle / condition | S0 vs F0 | S1 vs F1 | F1 vs F0 | S1 vs S0 | Interaction (pp) | RMSE S/F (both layers) | max \|e\| layer-on/off | Complete | Pre-registered verdict (all four) |
|---|---|---|---|---|---|---|---|---|---|
| S2 E1 | +0.0040 | +0.0040 | 0.0000 | 0.0000 | 0.0000 | 1.054 | 1.000 | yes | NO PRACTICAL DIFFERENCE |
| S2 E2 | −0.0252 | −0.0252 | 0.0000 | 0.0000 | 0.0000 | 0.741 | 1.000 | yes | NO PRACTICAL DIFFERENCE |
| S2 E2b | −0.0243 | −0.0243 | 0.0000 | 0.0000 | 0.0000 | 0.741 | 1.000 | yes | NO PRACTICAL DIFFERENCE |
| S2 E3 | −0.0066 | −0.0066 | 0.0000 | 0.0000 | 0.0000 | 0.741 | 1.000 | yes | NO PRACTICAL DIFFERENCE |
| S2 E4 | +0.0018 | +0.0018 | 0.0000 | 0.0000 | 0.0000 | 0.742 | 1.000 | yes | NO PRACTICAL DIFFERENCE |
| UDDS E1 | +0.0138 | +0.0133 | −0.0034 | −0.0039 | −0.0005 | 1.002 | 1.000 | yes | NO PRACTICAL DIFFERENCE |
| UDDS E2 | −0.0128 | −0.0120 | −0.0042 | −0.0034 | +0.0008 | 0.991 | 1.000 | yes | NO PRACTICAL DIFFERENCE |
| UDDS E2b | −0.0125 | −0.0117 | −0.0037 | −0.0029 | +0.0008 | 0.990 | 1.000 | yes | NO PRACTICAL DIFFERENCE |
| UDDS E3 | −0.0164 | −0.0131 | −0.0138 | −0.0105 | +0.0033 | 0.998–0.999 | 1.000 | **no** | NO PRACTICAL DIFFERENCE / INCOMPLETE-CYCLE |
| UDDS E4 | −0.0130 | −0.0098 | −0.0160 | −0.0127 | +0.0033 | 0.999 | 1.000 | **no** | NO PRACTICAL DIFFERENCE / INCOMPLETE-CYCLE |

The in-sample S1 rows, kept separate, lie between −0.0131 % and +0.0095 %
(`pilot/out/analysis/pilot_tables.md`).

**Pre-registered predictions** (`decisions.json`). None was falsified:

| ID | Prediction | Outcome |
|---|---|---|
| P1 | S1 vs F1: no practical difference on held-out conditions | held (0 of 10 falsifying) |
| P2 | layer changes energy < 1 % on complete runs | held |
| P3 | layer does not raise max \|e\| > 10 % where battery-limited > 1 % | held (10 contrasts tested, 0 falsifying; max \|e\| ratio 1.000) |
| P4 | \|interaction\| < 0.5 pp | held (largest 0.0033 pp) |
| P5 | all branch differences < 1 % on complete runs | held (largest 0.0252 %) |

## 5. What the differences consist of

**Scheduling (S vs F).**
- *Energy:* the differences are ≤ 0.025 % and change sign with conditions. Examples: S2 E3
  −0.0066 % vs S2 E4 +0.0018 %; S2/UDDS E1 at SoH 1.0 positive, E2 at SoH 0.8 negative.
- *Tracking:* at SoH 0.8 the scheduled branch tracks better on S2 (RMSE 0.0173 vs 0.0234 m/s,
  ratio 0.741; max |e| ratio 0.771). At SoH 1.0 it tracks worse (ratio 1.054). On UDDS the ratios
  are 0.990–1.002.
- **Post-hoc attribution** (`posthoc.json`; not pre-registered, does not change any verdict):
  - Where no drive limit binds, each fixed candidate's RMSE is the same at SoH 1.0 and 0.8 to
    within **3.4e-6 m/s**. The vehicle's tracking does not depend on SoH there.
  - The scheduled branch's lower RMSE at SoH 0.8 therefore comes from the *gain magnitude* it uses
    at SoH 0.8 (γ_v = 9.27 lowers the torque weight, giving a more aggressive gain). It does not
    come from compensating any SoH-dependent dynamics.
  - None of the 24 fixed candidates reached 0.0163 m/s. The most aggressive fixed candidate (the
    one selected, 0.0221 m/s) sits at the edge of the fixed search box, as in R1. The scheduled
    family can reach gains outside that box through γ_v.
  - **This is a search-space asymmetry in the pre-registered tuning, not evidence that SoH
    information helps.** A fixed gain equal to the scheduled gain at SoH 0.8 would, by the
    3.4e-6 m/s invariance, track equally well at every SoH. That is an analytical inference; no run
    was made to confirm it.
  - The absolute difference (0.006 m/s RMSE) is small against the 0.05 m/s velocity-noise level
    assumed in the parameter registry. That comparison is context, not a pre-registered criterion.

**Supervisory layer (layer-on vs layer-off).**
- On S2 the layer is inert: the drive limit never binds. All S2 layer contrasts are exactly 0.
- On UDDS it lowers energy per reference km by 0.003–0.016 % and current-limit exceedance by
  0.3–3.3 % (largest: S, E2b, 11.02 → 10.66 A·s; F, E3, 31.37 → 31.00 A·s). Battery-limited time
  falls by about 0.1 percentage points. It
  changes maximum overshoot by ≤ 0.004 m/s and maximum |e| by < 0.1 %.
- The governor was active on 4–19 % of UDDS steps but changed almost nothing, because the
  unaware anti-windup accumulated little integrator wind-up during the short battery-limited
  episodes.

**Interaction.** Largest magnitude 0.0033 pp (incomplete UDDS rows). On complete held-out rows it
is at most 0.0008 pp.

## 6. Convergence and parameter dependence

**Time step** (UDDS E3, dt 1 ms → 0.5 ms; `decisions.json`). Pairwise ΔE changed by:

| Contrast | ΔE at dt = 1 ms | ΔE at dt = 0.5 ms | Change | Criterion < 0.01 pp |
|---|---|---|---|---|
| S0 vs F0 | −0.0164045 % | −0.0164045 % | 2.0e-9 pp | pass |
| S1 vs F1 | −0.0131407 % | −0.0131407 % | −4.2e-8 pp | pass |
| F1 vs F0 | −0.0137714 % | −0.0137713 % | 2.6e-8 pp | pass |
| S1 vs S0 | −0.0105074 % | −0.0105074 % | −1.8e-8 pp | pass |

- The contrasts (≥ 0.0105 % on this condition) and the interaction (0.0033 pp) are 1e5 times or
  more above the numerical sensitivity. They are **real properties of the model, and practically
  negligible**: about 40 to 300 times smaller than the 1 % margin.
- Convergence was checked only on UDDS E3, an incomplete-cycle condition. The other conditions
  inherit R1's convergence evidence (same solver and dt).

**Parameter status and dependence.**

| Parameter | Status | Varied within the protocol | Effect on contrasts |
|---|---|---|---|
| R0 growth at SoH 0.8 | ×1.7: source-grounded but weak (Pan2023 Lishen 20 Ah LFP, FT, table layout unconfirmed); ×1.1: thesis law, unverified | E2 vs E2b | scheduling ΔE changes by ≤ 0.0009 pp; energy level +0.6–1.4 %; verdict unchanged |
| Current limits 3C/1C → 2C/0.5C | 3C/1C assumed (R1); 2C from retailer summaries of EVE 100 Ah LFP (SEC); 0.5C assumed | E2 vs E3 | UDDS becomes incomplete; energy +1.1 % (S2) to +2.4 % (UDDS); contrasts stay ≤ 0.017 % |
| Limits ∝ SoH | **unsupported assumption** (exploratory arm) | E3 vs E4 | adds shortfall (2.3 → 4.4 % on UDDS); the scheduling contrast on S2 flips sign (−0.0066 → +0.0018 %); no verdict changes |
| All vehicle parameters, η_mi, Q = 100 Ah | thesis values, unverified | not varied | — |

**No apparent advantage depends on an unsupported assumption, because there is no advantage to
lose.** The only effect that comes and goes with the assumptions is the *size* of the battery
limitation itself (shortfall, friction braking), which acts on every branch alike.

## 7. Verdicts

| Question | Answer | Basis |
|---|---|---|
| Does SoH scheduling add a measurable benefit beyond the common supervisory layer (S1 vs F1)? | **No practical benefit.** Energy differences are measurable numerically (≤ 0.025 %, sign varies) but 40× or more below the pre-registered 1 % margin. The tracking edge at SoH 0.8 is a gain-magnitude effect a fixed gain can reproduce (post-hoc) | §4, §5; P1 held |
| Does the supervisory layer help independently of scheduling (F1 vs F0, S1 vs S0)? | **No practical effect in these scenarios.** Inert where the drive limit does not bind (S2). On UDDS it reduces energy ≤ 0.016 %, current-limit exceedance ≤ 3.3 % (≤ 0.36 A·s), overshoot ≤ 0.004 m/s | §5; P2, P3 held |
| Is there an interaction? | **No.** Largest 0.0033 pp (incomplete rows); ≤ 0.0008 pp on complete rows | §5; P4 held |
| Are any effects practically meaningful under the predetermined criteria? | **No.** All 40 held-out contrasts are NO PRACTICAL DIFFERENCE; 8 of them also INCOMPLETE-CYCLE (UDDS E3, E4) | §4 |
| Does any result support the 12.5 % energy claim? | **No.** The largest held-out difference between any two branches is 0.025 %, about 500 times smaller | §4 |
| Does any result support the 15.3 % capacity-fade claim? | **No, and it cannot.** No fade model was used. Ah, current and exceedance differences are not fade evidence (Keil2015; SunC2026) | `pilot_protocol.md` §5 |
| Which claims remain unresolved for lack of a fade model? | The 15.3 % fade reduction; any lifetime-extension or "battery longevity" benefit; the NSGA-II energy–longevity Pareto results | `claim_status_matrix.csv` D1, D2 |

**Under §8 of the protocol, the pilot does not justify a larger SoH-scheduling study.** P1 was not
falsified in the direction of a benefit. P3 holds only in the weak sense that the layer does no
harm, so no constraint-management follow-up is justified by these data either.

## 8. Limitations

- **Assumed scenarios.** Limits and ageing are bracketed (§6), not datasheet values of the thesis
  cell (unidentified).
- **Tuning data.** Tuning was on S1 only, and the drive limit never bound there, so the layer did
  not shape the gains. The fixed search box excluded the most aggressive gains the scheduled family
  reached.
- **Held-out cycles.** Two held-out cycles. UDDS does not meet the tracking requirement for any
  branch, and two UDDS conditions are incomplete.
- **Missing elements.** Oracle SoH; constant η_mi; no thermal state; no OCV(SoC); no fade model.
- **Independence.** The protocol, code and analysis come from the same AI assistant. No second
  implementation of the supervisory layer exists, and no human has replicated the pilot.

## 9. Is further work warranted?

The only post-hoc uncertainty is whether a fixed gain set to the scheduled gain at SoH 0.8 matches
its tracking. It is already settled for the non-binding regime by the 3.4e-6 m/s SoH-invariance.
In the binding regime the S/F ratios are 0.998–1.002. A confirming run could not change any
verdict, so **no further run is recommended**.

The uncertainty that *could* change the conclusion is physical, not numerical: the real cell's
current and power limits and their dependence on SoH (owner item OC-1). Only a source-grounded
limit law much tighter than, or differently shaped from, the brackets tested here could alter the
picture. Even then, the pilot shows that both branches sit on the same limit.
