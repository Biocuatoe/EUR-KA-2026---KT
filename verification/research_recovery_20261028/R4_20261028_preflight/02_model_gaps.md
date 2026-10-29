# R4 preflight — Phase 2: model gaps and blocker register

**Date:** 2026-10-28. **Prepared by:** AI assistant; no human review.

Each gap names:
- what it blocks, by hypothesis and branch (see `03_R4_protocol_v1.md` for H1–H5 and B0–B4);
- the **exact evidence** that would resolve it;
- who can supply that evidence.

Parameter IDs refer to `02_parameter_ledger.csv`.

## 1. Register

| Gap | What is missing | Blocks | Evidence that would resolve it | Who |
|---|---|---|---|---|
| **G-BAT-1** | Identity and datasheet of the KT-01 cell (BAT-02) | branch K; any KT-01 battery statement; transfer of RP-E results to KT-01 | Manufacturer part number and datasheet: rated capacity; DCR or pulse resistance vs SoC and temperature; continuous and pulse charge/discharge current limits vs SoC and temperature; voltage window; OCV(SoC) | thesis owner (open item OC-1) |
| **G-BAT-2** | Any SoH dependence of power capability (BAT-14, BAT-15) | **H2/B2 entirely; the SoH mechanism of H4/B4**; any non-trivial SoH effect in H1 | For the same cell (or a documented equivalent): HPPC or pulse-power tests at ≥ 2 aged states; or a BMS derating specification as a function of SoH, with its source | owner or cell supplier; or a peer-reviewed dataset for the identified cell |
| **G-BAT-3** | Pack series/parallel arrangement and nominal voltage (BAT-03, BAT-04, BAT-05) | branch K; per-cell current and voltage mapping | Pack schematic or BMS configuration that resolves 16 × 3.2 V = 51.2 V against 48 V | owner |
| **G-BAT-4** | OCV(SoC) and temperature dependence (BAT-06, BAT-16, BAT-17) | multi-cycle or cold-condition studies; SoC-dependent charge acceptance | Same-cell datasheet curves or test data | owner or supplier |
| **G-MOT-1** | Motor/inverter efficiency map (MOT-10, MOT-11, MOT-12) | **any motor-specific benefit claim**; replacing the M0/M1/M2 bracket | Measured efficiency map over (T, ω) in both power directions, including no-load and inverter losses, for the KT-01 motor or a named 15–20 kW machine with a primary source | owner; manufacturer; or a peer-reviewed map for a named machine |
| **G-MOT-2** | A physically consistent motor specification (X-4, X-5) | branch K | Motor model, voltage class and torque-speed curve consistent with a 48 V bus (or the actual bus voltage) | owner |
| **G-VEH-1** | Actual vehicle road-load and mass (X-1, X-2, X-8) | branch K | Measured or homologated curb mass, coast-down coefficients (or C_d·A_f and C_rr) and tyre size | owner; or a named real vehicle's homologation data |
| **G-AGE-1** | An ageing model applicable to the pack (AGE-01 to AGE-06) | **H5 entirely**; any fade, fade-reduction or cycle-life number | An ageing law with parameters identified for the same cell (or same chemistry, format and capacity class), its validity domain (T, C-rate, SoC, DoD), calibration and validation data, and the state-update equation linking current and temperature histories to capacity | owner, supplier, or a peer-reviewed same-cell study; approval needed for any download |
| **G-CYC-1** | A second in-domain held-out cycle (CYC-07) | generalisation of H3 beyond S2; the second held-out condition required by protocol §8 | A standard low-speed schedule taken from its primary regulatory text (e.g. WLTC Class 1 per UN GTR No. 15, or the ECE-15 urban part), with retrieval hash and provenance record as for the EPA cycles | approval for a bounded download in a later phase |
| **G-RV-1** | A real reference vehicle with primary data | branch RV (a separately labelled real system) | G-MOT-1 + G-VEH-1 + G-BAT-1 for one named vehicle | owner or literature, with approval |
| **G-REP-1** | Independent replication of R1–R3 and of any R4 result | upgrading any result beyond "single-author simulation" | A second implementation by a different person, or a human review of the R4 pilot code against the protocol | owner or supervisor |
| **G-REP-2** | R3-C driver code as run (`r3_pilot.py` `cec5f70b…`) and R3-C per-sample traces | upgrading R3-C numbers (RC-2) from "reproduced from aggregates" to "independently recomputed" | Not recoverable from inspected sources. A rerun under the R4 protocol replaces it | — (superseded by the R4 pilot) |
| **G-PRV-1** | Unchecked legacy provenance leads (Cursor `state.vscdb` and workspace storage, Colab/Drive, other machines) | claims about the *origin* of 12.5 / 15.3 beyond "no underlying numerical evidence found in inspected sources" | Owner-authorised inspection of those locations | owner. **Does not block R4**: R4 does not depend on legacy figures |
| **G-LIT-1** | Database-level novelty search (Scopus, IEEE Xplore) | any "novel" or "first" wording | A documented database search | owner, with database access |

## 2. Effect on the R4 hypotheses

| Hypothesis | Blocking gaps | Status |
|---|---|---|
| H1: SoH-scheduled vs equally tuned fixed LQR, energy | none for RP-E. A non-trivial SoH mechanism needs G-BAT-2 | **Testable on RP-E.** Three earlier studies (R1, R2, R3-B) gave a null result on this plant. In the absence of G-BAT-2 a fourth run would repeat the same physics (SoH enters only through R0 and capacity bookkeeping). It is defined as an optional control arm, not as the pilot's purpose |
| H2: SoH-dependent feasibility compensation | G-BAT-2 (and G-BAT-1 for limit values) | **Blocked** |
| H3: generic eco-driving at a comparable task | none for S2 on RP-E; G-CYC-1 for a second held-out cycle; G-MOT-1 for motor-specific magnitude | **Testable on RP-E (S2 only).** This is the proposed small pilot |
| H4: SoH-aware vs generic planner | G-BAT-2 (no SoH mechanism other than R0 growth, whose QS value VSI_eco ≈ 0–0.08 % lies below the eco DP's ≈ 0.4 % demonstrated optimality gap) | **Blocked** |
| H5: capacity-fade benefit | G-AGE-1 | **Blocked**. No fade number may be reported |

## 3. Next critical blocker

- **For the thesis's central SoH question (H1 non-trivially, H2, H4):** G-BAT-2 together with G-BAT-1. The minimum is the cell datasheet and an SoH-dependent power-capability source for the same cell. Without them, every SoH effect in any model of this vehicle is either resistance growth (already shown negligible) or an assumption.
- **For the narrow R4 pilot (H3 on RP-E):**
  - nothing blocks a first S2 run once the planner is implemented and verified (Phase 4/5, not started);
  - G-CYC-1 blocks generalisation;
  - G-MOT-1 blocks any motor-specific magnitude.
- **For any capacity-fade statement:** G-AGE-1.
