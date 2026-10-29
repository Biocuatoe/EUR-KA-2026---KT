# Pilot protocol P2-pilot: does SoH gain scheduling add anything once a battery-constraint supervisor exists?

**Status:** frozen 2026-10-25 before any pilot run. Its SHA-256 is written to
`pilot/protocol_sha256_at_freeze.txt` and into every pilot manifest. Later changes go to §10 as
dated deviations; this text is not edited.

**Relation to earlier work.** R1 (`../experimental_protocol.md`, frozen SHA-256 `d80b5b4f…479c`)
and its 348 runs are untouched and are not rerun. This pilot reuses R1's plant code by import
(`src/rebuild/model.py`, unmodified) and adds, in a separate module, a supervisory layer and an
equal-budget tuning procedure. Gate assessment: `evidence_gates.md`.

**Labels.** Every result of this pilot is a **simulation result under an assumed scenario**. No
parameter below is a datasheet value of the thesis's (unidentified) cell. Nothing here is
real-vehicle validation.

---

## 1. Questions (fixed before running)

- **Q-A (scheduling main effect):** averaged over supervisor on/off, does SoH scheduling (S) change
  energy per km or tracking compared with an equally tuned fixed gain (F)?
- **Q-B (supervisor main effect):** averaged over F/S, does the common supervisory layer change them?
- **Q-C (the decisive comparison, F1 vs S1):** with the supervisory layer present in both, does
  scheduling add a practical benefit?
- **Q-D (interaction):** is (S1 − F1) different from (S0 − F0)?

## 2. Branches

| Branch | Gain | Supervisory layer |
|---|---|---|
| F0 | fixed LQR, tuned (§4) | off |
| S0 | SoH-scheduled LQR (thesis Eqs. 4.39–4.41 form), tuned (§4) | off |
| F1 | fixed LQR, tuned (§4) with layer on | on |
| S1 | SoH-scheduled LQR, tuned (§4) with layer on | on |

**Layer off (F0, S0).** The battery management system still limits torque in the plant (exactly as
R1: drive torque ≤ η_mi·P_dis/ω, regen ≤ P_ch/(η_mi·ω), excess braking to friction). The controller
is *unaware* of the battery limit: its conditional anti-windup uses only the motor envelope
min(T_max, P_max/ω).

**Layer on (F1, S1).** Two elements, identical for F1 and S1:
1. *Constraint-aware anti-windup:* the integrator freezes when u > T_pos (battery-aware envelope) and
   e < 0 (R1's rule).
2. *Feasible-reference governor:* the controller tracks r_g instead of v_ref. At each control step,
   if v_ref(k) > r_g(k−1), r_g(k) = min(v_ref(k), r_g(k−1) + max(a_avail, 0)·T_s), with
   a_avail = (G·η_g·(T_pos − B_m·ω)/r_w − F_rr − F_aero)/M_eff at the current speed; otherwise
   r_g(k) = v_ref(k). It never slows the reference below what the battery can deliver and never
   changes braking. Tracking metrics are always computed against the **original** v_ref.

Friction-brake blending (braking beyond the regen limit) is vehicle hardware and is present in
all four branches.

## 3. Plant and scenarios

Plant: R1 plant (`model_equations.md`), RK4 dt = 1 ms, controller ZOH T_s = 10 ms, initial state
rest, SoC 0.8, V1 = 0. Current limits not SoH-scaled unless stated.

| Code | Use | SoH | R0 growth | Limits c_dis / c_ch [1/h × 100 Ah] | Basis |
|---|---|---|---|---|---|
| T1 | tuning | 1.0 | — | 3 / 1 | R1 BCN assumption |
| T2 | tuning | 0.8 | R0 × 1.7 (k_r0 = 3.5) | 3 / 1 | R0 ratio from Pan 2023 (Lishen 20 Ah LFP, end of life; FT, table to be confirmed) |
| E1 nominal | eval | 1.0 | — | 3 / 1 | as T1 |
| E2 aged | eval | 0.8 | R0 × 1.7 | 3 / 1 | as T2 |
| E2b aged (thesis law) | eval | 0.8 | R0 × 1.1 (k_r0 = 0.5) | 3 / 1 | thesis Eq. 4.28, unverified |
| E3 constraint-active | eval | 0.8 | R0 × 1.7 | 2 / 0.5 | 2C = 30-s pulse rating in retailer listings of EVE LF100 cells (SEC); 0.5C charge = R1 BCS2 assumption |
| E4 exploratory | eval | 0.8 | R0 × 1.7 | 2 / 0.5, **SoH-scaled** | assumed BMS law; exploratory only |

Voltage window 2.5–3.65 V per 3.2 V (R1). Cycles: **tuning on S1 only** (T1, T2). **Held-out:**
S2 and UDDS (EPA, provenance recorded in R1). S1 evaluation rows are reported as in-sample. US06 is
excluded (beyond motor capability in every R1 class).

## 4. Equal-budget tuning (identical for all four branches)

- Fixed family: Q = diag(1/(0.5·σ)², 1/85², 1/0.5²), R = c/85²; parameters log₁₀σ ∈ [−0.6, 0.3],
  log₁₀c ∈ [−2, 1].
- Scheduled family: the same two base parameters plus γ_v, γ_u ∈ [0, 10], applied as
  Q(SoH) = Q·diag(1, 1/(1+γ_v(1−SoH)), 1), R(SoH) = R·(1+γ_u(1−SoH)).
- **Budget: 24 candidates per branch**, Latin hypercube (scipy `qmc.LatinHypercube`, seed 20261025,
  scrambled), each evaluated on T1 and T2 (48 simulations per branch, 192 in total). Unstable designs
  (|eig| ≥ 1) are infeasible.
- **Tracking requirement (feasibility):** in both T1 and T2, shortfall ≤ 1 %, RMSE ≤ 0.10 m/s,
  max |e| ≤ 1.0 m/s.
- **Selection:** among feasible candidates, minimum mean energy per **reference** km over T1 and T2;
  ties (< 1e-6 relative) broken by mean RMSE. If no candidate is feasible, the minimum mean RMSE
  candidate is taken and this is reported.
- Each branch is tuned with its own layer setting. No tuning on S2 or UDDS.

## 5. Outcomes (per run, against the original v_ref)

Distance and shortfall; energy per actual km and per reference km (net V_oc·I); RMSE; max |e|;
max overshoot max(v − v_ref); battery-limited time fraction; friction-brake energy; terminal
regeneration; integrated current-limit exceedance; Ah; peak and RMS current; energy closure.
**Not computed:** capacity fade (no justified model).

## 6. Pre-registered predictions and decision rules

ΔE % = 100·(E_a − E_b)/E_b per reference km, b = comparison branch. "Complete" = shortfall ≤ 1 % in
both runs.

| ID | Prediction (from `../recovery_feasibility_20261025/attainable_improvement_assessment.md`) | Falsified if |
|---|---|---|
| P1 | **Q-C:** S1 vs F1 is NO PRACTICAL DIFFERENCE on every held-out condition | S1 has ΔE ≤ −1 % with RMSE ratio ≤ 1.10, both complete, on any held-out condition (this would *support* scheduling) |
| P2 | **Q-B:** the layer does not change energy by ≥ 1 % on complete runs | \|ΔE(F1 vs F0)\| ≥ 1 % or \|ΔE(S1 vs S0)\| ≥ 1 % on a complete held-out run |
| P3 | **Q-B tracking:** where the battery limit binds (> 1 % of time), the layer reduces max overshoot or max \|e\| | the layer increases max \|e\| by > 10 % on such a run |
| P4 | **Q-D:** \|(ΔE_S1/F1) − (ΔE_S0/F0)\| < 0.5 percentage points | interaction ≥ 0.5 pp on a held-out condition |
| P5 | **Accounting:** all branch-to-branch energy differences on complete runs are < 1 % (Phase-1 headroom) | any difference ≥ 1 % on a complete run, without a ledger explanation |

Scheduling is said to **improve** only under the R1 rule (ΔE ≤ −1 %, RMSE ratio ≤ 1.10) on a
**held-out**, complete condition, and in **both** E3 and E4 (it must not depend on the assumed
SoH-scaling law).

## 7. Validity and numerical checks

- Run invalid only for non-finite state, infeasible battery solution, closure > 1e-3 of ∫|V_oc·I|,
  or v < −1e-6. Tracking failure is an outcome.
- Sanity: at SoH 1.0 a scheduled gain equals its own base fixed gain (checked numerically);
  layer-off branches with the R1 F gain reproduce R1 BCN when the governor and unaware rule are not
  binding (spot check on S2 E1, where no limit binds).
- Convergence: UDDS E3, all four branches, dt = 1 and 0.5 ms; criterion: change of every pairwise ΔE
  < 0.01 percentage points.

## 8. What moves the work beyond the pilot

Only if P1 is falsified in the direction of a benefit on a held-out condition, in both E3 and E4,
with the convergence check passing, would a larger R2 study of SoH scheduling be justified. If only
P3 holds (layer improves tracking), the justified follow-up is a constraint-management study
(not an SoH-scheduling study), which must be labelled as such.

## 9. Mapping to thesis claims

Q-A/Q-C bear on the thesis's central hypothesis (adaptive vs fixed LQR) and on the 12.5 % energy
claim within this plant. Nothing here bears on the 15.3 % capacity-fade claim.

## 10. Deviations log

(empty at freezing)
