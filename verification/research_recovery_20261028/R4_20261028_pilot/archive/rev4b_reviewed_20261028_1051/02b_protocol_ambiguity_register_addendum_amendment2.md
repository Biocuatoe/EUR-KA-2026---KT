# R4 H3: ambiguity register, addendum for amendment 2 (N-A2)

**Date:** 2026-10-28.

This addendum extends `02_protocol_ambiguity_register.md`, which stays unchanged; its entries AMB-01 to AMB-28 still apply. The entries below were found while implementing the owner's N-A2 ruling, or by the independent review (`review/N-A2_review_agent_report_20261028.md`). Each one is stated in `03_protocol_v1_amendment_2_DRAFT.md` §6 and carried as a machine-readable key in its block, so the owner's decision is checked by code.

| ID | Question | Handling proposed in the amendment 2 draft | Direction | Status |
|---|---|---|---|---|
| AMB-29(a) | A pair whose B0 or B3 profile does not exist | `NOT_APPLICABLE_PROFILE_UNAVAILABLE`; no effect on the branch | can be favourable: it removes the B0-only failure path the amendment-1 implementation had | **owner to confirm** |
| AMB-29(b) | A QS-eligible pair with an arm that has no finite dynamic energy | `NOT_EVALUABLE_RUN_MISSING`; branch INCONCLUSIVE | conservative | owner to confirm |
| AMB-29(c) | A QS-eligible pair whose QS energy is ≤ 0 (ratio undefined) | `NOT_EVALUABLE_QS_UNDEFINED`; branch INCONCLUSIVE | conservative | owner to confirm |
| AMB-29(d) | An exception before or during the pair evaluation | `NOT_EVALUABLE_CONDITION_ERROR`; eligibility unknown; branch INCONCLUSIVE | conservative | owner to confirm |
| AMB-30 | Scope of the motor-branch outcome | all planned pairs of the motor across all sets (the literal §9 reading); per-set counts reported | mostly conservative; a non-decisive set can supply the one PASS that avoids vacuity | **owner to confirm** |
| AMB-31 | Which dynamic energy is "usable" for an eligible pair | any executed run with a finite simulator energy, whatever its §8.2 verdict; dynamic-valid PASS counts reported separately | **can be favourable**; the stricter alternative would require §8.2 validity for a PASS to count | **owner to choose** |
