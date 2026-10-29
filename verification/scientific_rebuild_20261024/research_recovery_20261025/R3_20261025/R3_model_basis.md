# R3 model basis: which missing mechanisms could matter, and the reference plant used

**Date:** 2026-10-25.
**Scope:** Phase 1 of R3, covering model and source inspection only. No R3 outcome had been computed when this was written.
**Parameter sources:** `R3_literature_and_parameter_sources.csv` (one row per quantity).
**Code:** `code/r3_lib.py`. **Protocol:** `R3_protocol.md`.
**Independence:** prepared by the same AI assistant that built R1 and R2. No person has reviewed it.

---

## 1. What R1 and R2 already contain

Sources: `../../model_equations.md`, `../../src/rebuild/model.py`, `../pilot_protocol.md`, `../pilot/sim.py`.

| Mechanism | R1 | R2 | Comment |
|---|---|---|---|
| Longitudinal dynamics, road load, effective mass | yes | yes | thesis values, `report_unverified` |
| Torque saturation T_max, P_max/ω | yes | yes | |
| Actuator dynamics (torque lag τ_T = 20 ms) | yes | yes | |
| Battery ECM: R0 and one RC branch (R1, C1) | yes | yes | thesis values, `report_unverified` |
| SoH → capacity (SoC bookkeeping), SoH → R0, R1 | yes | yes | k_r0 0.5 (thesis) and 3.5 (Pan 2023 ratio, R2) |
| Battery current and voltage window → drive and regeneration torque limits | yes (assumed limits) | yes | limits unsourced (3C/1C, 2C/0.5C, SoH-scaled variant) |
| Regeneration beyond the charge limit → friction brake | yes | yes | |
| Supervisory layer (aware anti-windup and feasible-reference governor) | — | yes | inert or negligible in R2 |
| **Motor/inverter efficiency vs torque and speed** | **no** (constant 0.874) | **no** | the largest gap (§2) |
| OCV(SoC) | no (constant 48 V) | no | |
| Temperature (R0, limits, OCV) | no | no | |
| Capacity fade | no | no | |

## 2. Assessment of each candidate mechanism

The governing fact, derived in `../../recovery_feasibility_20261025/attainable_improvement_assessment.md` §4.1, holds for any loss model of a single-motor, fixed-gear drive:

> At a given realised speed trajectory v(t), the wheel force, motor operating point (T, ω),
> electrical power and battery current are all fixed. A controller therefore changes energy
> only through (i) how far the trajectory departs from the reference and (ii) the
> regeneration/friction split where a limit binds.

A richer loss model changes **how much a given trajectory deviation is worth**. It does not create a new control lever. R3 can therefore bound every controller's benefit by optimising over trajectories directly (`R3_protocol.md` §3), without first having to design the best controller.

| Mechanism | Could it plausibly matter? | Source status | R3 treatment |
|---|---|---|---|
| Motor/inverter efficiency vs (T, ω) | **Yes, most plausible.** The motor/inverter loss is 15–31 % of energy in R1. With part-load efficiency drop or copper loss ∝ T², smoother torque and different operating points change losses, which a constant η hides | No map exists for the thesis motor (Roshandel 2021 is a review only). A published, generic efficiency-vs-power-fraction curve exists locally in FASTSim 3.1.0 (2022 Renault Zoe, about 100 kW) | Three structural variants: M-const (R1), M-curve (FASTSim shape, scaled to 18 kW), M-copper (all loss ∝ T², an assumed *stress* model favourable to the hypothesis) |
| Battery ECM and polarisation | Small. R0 loss is 1–3 % of energy and R1 loss 0.02–0.36 % in R1 | Thesis values unverified | R1 values kept. The DP bounds use V1 = 0, while the dynamic plant keeps V1 |
| SoC dependence (OCV, R0) | Negligible within one cycle: the SoC swing is < 2 % on the LFP plateau | No OCV table for any applicable cell | Constant OCV, stated |
| Temperature dependence | Unknown | Nothing sourced for an applicable cell | Not modelled; isothermal assumption stated |
| SoH → capacity, R0, available power | This is the only route by which SoH can reach the energy result. R0 alone raises losses by 0.2–1.1 % of energy in R1 at fixed trajectory, and no controller can avoid that share without changing the trajectory | R0 growth: thesis 0.5 (unsourced) and Pan 2023's 1.7 at end of life (different 20 Ah cell). SoH-scaling of current limits: no source | P2/P3 plant states; SoH-scaled limits reported as exploratory only |
| Charge acceptance and regeneration limits | **Yes, first-order.** R1 assessment §5.2: limit-forced friction braking is 91–98 % of friction energy. Qamar 2026 finds regeneration-limit assumptions change losses by 3–12 % | Only a retailer summary for a generic EVE 100 Ah LFP cell (1C continuous, 2C 30-s pulse; SEC grade) | L-R1 (3C/1C, R1) and L-EVE (2C/1C). At 48 V, 2C is about 9.6 kW against an 18 kW motor, so drive limits bind on hard accelerations |
| Torque saturation and actuator dynamics | Already in the model. They matter only for tracking feasibility (UDDS needs 20.96 kW peak against 18 kW) | Thesis values | Unchanged |
| Capacity fade | Cannot be quantified (§4) | No law for an applicable cell | Not computed |

## 3. The reference plant

The thesis battery cannot be identified: its BOM lists 16 × 3.2 V/100 Ah CATL with no part number, and 16 × 3.2 V ≠ 48 V. R3 therefore defines a **reference plant** and never presents it as the thesis vehicle's pack:

- **Vehicle and drivetrain:** the thesis-printed values exactly as in R1, so that R3 is comparable with R1 and R2.
- **Pack:** a generic 48 V, 100 Ah LFP reference pack.
  - R0, R1 and C1 are thesis-printed values.
  - Current limits come from either the R1 assumption or the generic EVE 100 Ah retailer summary.
  - It is not a CATL cell and not a measured pack.
- **Motor/inverter:** three loss structures that bracket the plausible behaviour. None is a measured map of the thesis motor. Conclusions are claimed only where they hold across the three.

## 4. Degradation

| Candidate | Cell | Why not used |
|---|---|---|
| Wang 2011 Ah-throughput law (form and E_a = 31,500 J/mol, z = 0.57 as stated in Tawfik 2024) | A123 2.3 Ah 26650 cylindrical | different cell, format and test duty; primary coefficients not read |
| Naumann 2020 capacity and resistance law | Sony/Murata 3 Ah 18650 LFP | different cell; coefficients not read |
| Schimpe 2018 | commercial LFP, stationary storage | different cell and duty |
| Pan 2023 semi-empirical | Lishen 20 Ah LFP | different cell |
| Datasets (Severson 2019, Chung 2021, NMC sets) | small cylindrical LFP or NMC | none is a 100 Ah prismatic LFP. Not downloaded, since approval is required and relevance is not established |

**Conclusion.** No fade law with parameters defensible for the reference pack is available. A 1000-cycle fade figure would rest on borrowed coefficients from a different cell, so none is computed. Ah throughput and ∫i²dt are reported as stress indicators. These are not fade, and Keil 2015 shows that lower current peaks need not mean slower ageing.

## 5. What would change this basis

- A measured motor/inverter efficiency map for a 15–20 kW micro-EV machine.
- The datasheet of the actual cell: DCR(SoC, T), current limits versus SoC and T, and the voltage window (owner item OC-1).
- An ageing dataset or law for the same cell.

Each would replace one bracketing assumption above. None is available today.
