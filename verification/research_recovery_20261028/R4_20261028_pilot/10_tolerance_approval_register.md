# R4 H3: tolerance approval register (amendment item A1-12)

**Date:** 2026-10-28. **Prepared by:** AI assistant, as auditor.

**Status:** all three tolerances are **justified by evidence and proposed for owner approval**. None is left unresolved. None is approved until the owner issues the amendment, with `approved_tolerances` in the approval record equal to the values below.

## Scope

**What §9 fixes.** Protocol §9 "Independent recomputation" requires that E_chem, E_DC, distance, trip time, stop compliance, I_over and RMSE agree with `runs.csv`. It sets tolerances for only some of them:
- energies within 1e-4 relative;
- distance within 1e-6 relative;
- flags identical.

**What this register covers.** The three quantities §9 names without a tolerance: trip time, I_over and RMSE.

**What it does not cover:**
- The 1e-4 relative energy tolerance, and the measured E_chem agreement of about 6e-7, apply to that check only. They were **not** transferred to these three.
- No value below was chosen from an energy difference between arms, or because it makes a test pass.

**Evidence sources:**
- analytic bounds;
- tests in `code/tests/test_rev2.py` (log `logs/pytest_run10.*`);
- the rev2 development checks R2-3 (`outputs/dev_rev2_20261028_071112/devchecks_rev2.json`);
- the recomputation records of the smoke test, DEV-4 and R2-2.

## T1 — Trip time

| Item | Content |
|---|---|
| Quantity | trip time from the trace, t_last − t_first of the 1 ms samples, against the simulator's `trip_time_s` (the tracked profile's duration, equal to T_ref) |
| Units and comparison | seconds: \|t_eval − t_sim\| ≤ tol |
| Existing tolerance | none in the protocol; rev1 used 1e-9 s as an implementation choice |
| Analytic evidence | **Construction.** Each sample time is computed in one multiplication, t = step·dt, with step an exact integer (T_ref/Ts·Ts/dt; T_ref is 213 or 324 s and an exact multiple of Ts = 0.01 s). **Error terms.** The error comes from dt's binary representation (relative ≤ 1.1e-16, so ≤ 4e-14 s over 324 s) plus one rounding of the product (≤ ½ ulp(324) = 2.8e-14 s). **Bound:** ≤ 7e-14 s |
| Measured | Exactly 0 for T_ref ∈ {213, 324} s × dt ∈ {1, 0.5} ms (`test_trip_time_float_error_bound`; R2-3). 0 on the two smoke runs, DEV-4 (S1, 0.5 ms) and R2-2 (S1, M1) |
| Smallest structural error to detect | one missing or extra trace sample, 1e-3 s; a wrong duration is at least one control period, 1e-2 s |
| **Proposed value** | **1e-9 s**: 1.4·10⁴ times the float bound, and 10⁻⁶ of the smallest structural error |
| Affects | implementation validity only. Task duration itself is checked exactly by the validator (D3), and completeness by §8.2 shortfall |
| If exceeded | the run is RECOMPUTATION_DISAGREEMENT: flagged and not credited until resolved by amendment (§9) |
| Evidence justifies freezing? | **Yes**: an analytic bound, with measured values at the bound's floor (0) |

## T2 — Protocol §8.2 I_over (C-rate)

| Item | Content |
|---|---|
| Quantity | I_over = ∫ max(0, \|i\| − I_lim) dt over the 1 ms samples, with I_lim = c_dis·Q (discharge) or c_ch·Q (charge), nominal Q. Simulator side: from the traced r3_lib current. Evaluator side: from its own recomputed current. Both by the trapezoid rule on the same samples |
| Units and comparison | A·s: \|I_over_eval − I_over_sim\| ≤ tol |
| Existing tolerance | none in the protocol. Rev1 proposed 1e-4 A·s without a derivation; this register replaces that proposal |
| Analytic evidence | **Lipschitz bound.** max(0, ·) is 1-Lipschitz, so \|ΔI_over\| ≤ ∫\|i_eval − i_sim\| dt ≤ T·max\|Δi\|. **Current difference.** Both sides evaluate the same quadratic i = (v_o − √(v_o² − 4R0·p_e))/(2R0) from the same traced T, ω and V1. Where \|i\| exceeds the limit (≥ 30 A), rounding gives \|Δi\| ≲ 300 A × 1e-15 ≈ 3e-13 A. **Bound:** ≤ 324 s × 3e-13 A ≈ 1e-10 A·s |
| Measured | **Forced exceedances.** A 6 s synthetic ramp on a 15 Ah pack exceeds the limit for all 6 combinations of M0/M1/M2 × L-R1/L-EVE: I_over 0.94–1.30 A·s, far above the 0.01 A·s threshold. Simulator and evaluator agree **exactly** (0.0 A·s) and the constraint flags agree (`test_forced_overcurrent_i_over_agrees_far_inside_the_tolerance`; R2-3). **S1 runs:** 0 (no exceedance) on the smoke runs, DEV-4 and R2-2 |
| Smallest structural error to detect | **No useful lower bound:** an exceedance can be arbitrarily small near the limit. The smallest per-sample exceedance in the forced cases was 0.018 A, which is 1.8e-5 A·s over one sample. The tolerance is therefore set by decision relevance rather than by error size |
| **Proposed value** | **1e-6 A·s**: 10⁻⁴ of the §8.2 decision threshold (0.01 A·s) and about 10⁴ times the float bound. Decision identity is checked separately and exactly (`constraint_ok_equal`), so a disagreement inside the tolerance cannot hide a different §8.2 verdict |
| Affects | implementation validity; indirectly constraint compliance, through the flag check |
| If exceeded | RECOMPUTATION_DISAGREEMENT: not credited until resolved by amendment (§9) |
| Evidence justifies freezing? | **Yes**: an analytic bound plus exact agreement on non-zero exceedances |

## T3 — RMSE

| Item | Content |
|---|---|
| Quantity | RMSE of v − v_tracked at the control instants k·Ts, k = 0…steps (A1-9). Simulator: sequential sum of e² over the steps. Evaluator: numpy (pairwise) mean of the same e values from the trace |
| Units and comparison | relative: \|rmse_eval − rmse_sim\| / rmse_sim ≤ tol |
| Existing tolerance | none in the protocol; rev1 used 1e-9 relative as an implementation choice |
| Analytic evidence | The e values are identical on both sides: the same states, and v_tracked recorded at the same instants. Only the summation order differs. For a sum of N non-negative terms, the relative error is ≤ (N − 1)·2⁻⁵³: about 2.4e-12 for S2 (N = 21,301) and 3.6e-12 for S1 (N = 32,401). The square root halves it |
| Measured | Summation-order difference on random data, N = 21,301 and 32,401: within the bound (`test_rmse_summation_order_error_bound`). On the real S1 trace (DEV-4): 2.5e-15. Runs: smoke 2.0e-15 and 2.8e-15; R2-2 4.8e-15 |
| Smallest structural error to detect | On the S1 trace (DEV-4): dropping one control instant changes RMSE by **1.5e-5** relative; misaligning by one 1 ms sample changes it by **4.2e-3** relative |
| **Proposed value** | **1e-9 relative**: about 280 times the worst-case float bound, and 1.5·10⁴ times smaller than the smallest structural error measured |
| Affects | implementation validity; the tracking verdict is checked separately and exactly (`tracking_ok_equal`) |
| If exceeded | RECOMPUTATION_DISAGREEMENT: not credited until resolved by amendment (§9) |
| Evidence justifies freezing? | **Yes**: an analytic bound, measured values and measured structural sensitivity. **Caveat:** a relative comparison is ill-conditioned if RMSE approaches 0, which cannot occur when a moving profile is tracked. If it did, the run would be flagged, not credited |

## Diagnostic tolerances (non-gating; listed for transparency, not for approval)

These never decide crediting; a failure is reported and flagged for investigation.

| Diagnostic | Tolerance | Basis |
|---|---|---|
| independent vs traced torque limits, M0 and M2 | 1e-9 N·m | closed forms on both sides; measured ≤ 2e-13 N·m over 240,000 operating points |
| independent vs traced torque limits, M1 | 1e-5 N·m | `r3_lib` inverts the curve through a 3001-point table, the evaluator by bisection. Measured table difference ≤ 9.7e-7 N·m (dense grid, P1/P3 × L-R1/L-EVE) and 9.7e-7 N·m on the full S1 run R2-2 |
| friction energy | 1e-6 Wh + gr·max\|Δt_neg\|·distance | bound of the friction difference caused by the measured limit difference |
| battery-limited fraction | fraction of instants within the limit difference of a boundary, + 1e-12 | the instants whose classification could flip |
| E_pos, max \|e\|, window I_over, min V_t, current, friction-law, wheel power, tracked profile, closure | as in `evaluator.compare_with_simulator` | bookkeeping checks; unchanged since rev1 except for the limit-derived bounds above |

## Owner action

Approve T1, T2 and T3 as proposed, or replace them with stated reasons, by issuing the amendment with `approved_tolerances` in `R4_20261028_campaign/release/amendment_1_approval.json`:

```json
{"E_chem_rel": 0.0001, "E_DC_rel": 0.0001, "distance_rel": 1e-06,
 "trip_time_abs_s": 1e-09, "I_over_protocol_abs_As": 1e-06, "rmse_rel": 1e-09, "flags": "identical"}
```

`campaign.approval_problems()` refuses any other set, unless the code and the amendment are changed together and re-tested.
