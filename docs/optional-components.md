# Optional research components: inclusion decisions (Phase 8)

Decision date: 2026-10-23, after the pre-registered experiments. None of these decisions
changed the pre-registered design; they record why each component stays out and what
would have to exist first.

## NSGA-II multi-objective optimisation (report contribution 2, claim C31): **excluded**

**Requirements** (protocol §8): defensible objectives, decision variables, constraints, a
Pareto analysis, and a meaningful comparison with the existing approach.

**Evidence:**

- The report's second objective, capacity fade per 1000 cycles, depends on an ageing
  model that cannot be evaluated: k_c and k_cal are missing and the units are inconsistent (C05).
- In the documented model, energy and tracking are **not** in conflict over the LQR weight
  family. The fixed-gain sweep (S-C, `artifacts/tables/fixed_family.csv`) shows energy and
  RMSE decreasing *together* as R falls (0.1× to 10× R spans only 0.28 % in energy). A
  Pareto front between them would degenerate to a single corner, so NSGA-II has no real
  trade-off to resolve in this model.

**To reconsider:** two objectives that are both computable from validated models and
shown, by a preliminary sweep, to actually conflict; then compare NSGA-II against the
grid-search baseline that already exists here.

## Battery-ageing analysis (claims C02, C04-C06, C36): **excluded**

**Requirements:** a degradation model and parameters appropriate for the chemistry and
for the conclusion being claimed.

**Evidence:**

- The report's model is underspecified (C05).
- The only built-in LFP parameter set in PyBaMM (Prada2013) carries no degradation
  parameters, and the other SEI sets are labelled "example parameters"
  (`docs/software-purpose-and-justification.md` at the project root).
- The existing fade figure is generated from hard-coded curves (C36, C40).

**What the experiment can say without an ageing model:** the scheduled controller
changes battery-current metrics negligibly. On S1 at SoH 0.8, peak current is
274.794 A (fixed) vs 274.793 A (scheduled), and resistive loss is 2.1807 vs 2.1814 Wh
(`primary_pairs.csv`).
That is **not** evidence about capacity fade, and no fade claim is made. A simulated ageing
curve would in any case need validation against measured cycling data for the same cell
before supporting a real-battery claim.

## Safety and certification (claims C17, C18): **excluded; claims to be withdrawn**

**Requirements:** limit safety claims to the analysis performed. Ordinary simulation tests
do not support ASIL compliance.

**Performed here:** closed-loop stability of every frozen-SoH design over SoH ∈ [0.5, 1]
and γ ∈ [0, 10] (property test), plus tracking-failure screening (RMSE > 1.5 m/s or
|e| > 3 m/s): 0 failures in 296 runs (largest RMSE 0.104 m/s, largest |e| 0.686 m/s). These are controller-design checks, **not** safety
analyses. There is no item definition, HARA, FMEDA, hardware metric or safety case, so no
ISO 26262 statement can be made.

## Other benchmarks (P, PID, fuzzy LQR, MPC, DDPG; claim C30): **excluded from the minimum study**

They can be added later against the same plant, profiles and metrics. Any benchmark has
to be tuned by a procedure documented before evaluation, as was done for the fixed LQR.
