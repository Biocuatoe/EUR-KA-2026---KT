# DRAFT — NOT ISSUED, NOT FROZEN, NOT REVIEWED
# Proposed amendment 1 to R4 protocol v1 (H3)

**Applies to:** `../R4_20261028_preflight/03_R4_protocol_v1.md` (SHA-256 `f9826318…2dab`). The protocol itself is unchanged.
**Prepared by:** AI assistant, 2026-10-28. It is a proposal for the owner to review.

**To issue it:**
1. Copy the reviewed text to `../R4_20261028_preflight/03_R4_protocol_v1_amendment_1.md`, or to a new versioned location the owner chooses.
2. Record its SHA-256 before any run it affects (protocol header).

Until then, it has no force. Item numbers refer to `02_protocol_ambiguity_register.md`.

## A1-1 Reference (AMB-01, clarification)
"Reference", "reference rest interval", "stop" and "segment" in §5, §6, §8 and §9 mean the cycle **sampled at h = 1 s** (§3). They do not mean the YAML profile.

The YAML profiles last 324.911 s (S1) and 213.278 s (S2) and have knots off the 1 s grid. The sampled task drops 0.911 s and 0.278 s of final idle, and its rest intervals are up to about 1 s shorter. This is recorded, not corrected. R3 v1 §3.2's statement that the knots lie on whole seconds does not hold for S1 or S2.

## A1-2 Extra stops (AMB-02, substantive). Owner to choose:
- **(a), recommended:** an S-eco profile must not come to rest between its departure and its arrival within a segment. A profile violating this is invalid, and the scenario is "profile unavailable". It is never replaced.
- **(b):** extra stops are allowed, counted and reported.

Reason for (a): an extra stop is a stop the task does not contain, i.e. a different driving task.

## A1-3 I_over (AMB-03, clarification)
- §8.2 I_over uses the C-rate limit of the active set (c_dis·Q for discharge, c_ch·Q for charge, nominal Q).
- The voltage floor is checked separately.
- The `r3_lib` window-limited exceedance is reported as a secondary diagnostic.

## A1-4 Baseline at P3 (AMB-04, substantive)
- For each evaluated plant state, v_b is computed on that state's plant.
- Whether v_b equals v_ref is recorded per state.
- The B3 profile remains the P1-designed S-eco profile (§8.1).

## A1-5 Limit sets (AMB-05, editorial)
In §2.4, replace "as implemented in `r3_lib`" by "as defined in R3 `code/run_gates.py` (LIMS) and `code/r3_pilot.py` (LIM)", which are identical.

## A1-6 Stop-arrival timing (AMB-06). Owner to confirm one:
- **(a) keep v1:** arrival no later than the reference arrival; waiting until the reference departure. This is the current frozen rule.
- **(b) exact arrival:** t_k = T_k within 1e-9 s. The planner would minimise energy subject to equality, which needs a change to §5.2.

The task brief of 2026-10-28 can be read as (b), so the owner's confirmation is needed.

## A1-7 M2 coefficient (AMB-07, editorial)
k_c = 18000·(1/0.874 − 1)/85² = 0.35917… (ledger MOT-07). The value 0.3592 in §2.3 is rounded.

## A1-8 Smoke test (AMB-09, substantive)
- The implementation smoke test is two runs: S1, M0, L-R1, P1, B0 and B3, at 1 ms.
- Its traces are retained. Its runs **are repeated** inside the campaign rather than reused, so that every campaign run is produced from the same gate record.
- No energy difference from the smoke test is reported.

## A1-9 RMSE sampling (AMB-11, clarification)
RMSE and max |e| are computed at the control instants k·Ts, k = 0…steps, as in R1–R3.

## A1-10 P3 feasibility (AMB-13, substantive)
- If the P1-designed S-eco profile has QS-infeasible pieces on the P3 plant, this is recorded.
- The dynamic run is still executed.
- Comparability is decided by §8.2 alone.
