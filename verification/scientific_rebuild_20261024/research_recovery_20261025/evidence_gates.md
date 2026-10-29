# Evidence gates (Phase 4)

**Date:** 2026-10-25. The P2 gate decisions below were made **before** any pilot run; the pilot
protocol was then frozen (SHA-256 `ebebc157…2b5a`, `pilot/protocol_sha256_at_freeze.txt`).

Verdicts: **PASS**; **PASS (scenario)** = passes only for an explicitly labelled assumed scenario,
not for the thesis vehicle; **FAIL**; **n/a**.

## 1. Gate table

| # | Gate | P1 (scheduling alone, existing plant) | P2 bounded pilot (F0/S0/F1/S1) | P3 (eco-driving + health) |
|---|---|---|---|---|
| 1 | Traceable source or explicit uncertainty range for every influential parameter | PASS for what P1 needs (R1 plant; nothing new) | **PASS (scenario):** current limits bracketed 3C/1C (R1 assumption) and 2C/0.5C (2C = 30-s pulse rating in *retailer* summaries of EVE 100 Ah LFP cells, SEC); R0 at SoH 0.8 bracketed ×1.1 (thesis law) and ×1.7 (Pan2023 Lishen LFP end of life, FT, table to be confirmed); SoH-scaled limits only as an exploratory arm. **No datasheet for the thesis cell** | **FAIL:** fade law for the cell, value of time and trip constraints are all unsourced |
| 2 | Units, signs, energy accounting | PASS (R1: closure ≤ 5.9e-10; ledger identity 2.2e-7 Wh) | PASS (same plant; closure checked per run; smoke test reproduces R1 exactly) | n/a until built |
| 3 | SoH, SoC, capacity, resistance and power limits separated | PASS | PASS: SoH enters R0, R1, SoC rate; capacity enters limits only in E4 (exploratory); limits as separate parameters | FAIL: fade (SoH evolution) would need a model |
| 4 | Physical and mathematical feasibility | PASS (US06 infeasible, excluded; UDDS 0.29 % over P_max, reported) | PASS: same; per-run battery-solution feasibility; unstable gains rejected | n/a |
| 5 | Tracking and travel-time requirement defined | PASS (same reference, R1 rules) | PASS: same reference and trip time for all branches; tuning feasibility shortfall ≤ 1 %, RMSE ≤ 0.10 m/s, max \|e\| ≤ 1.0 m/s | **FAIL:** the trip-time budget decides the result (Lot2025: −21 % energy at −7 % speed) and has no project basis |
| 6 | Equal tuning budgets, matched initial conditions | **FAIL in R1** (fixed family 164 runs, best at range edge; S γ = 1 untuned) | PASS by design: 24 LHS candidates per branch, same seed, objective and training set | n/a |
| 7 | Metric cannot reward failed tracking | PASS (per-reference-km + shortfall flag) | PASS: energy per **reference** km, completion guard, Pareto reporting | at risk: needs equal-time comparison |
| 8 | Pre-set pilot protocol and falsification criteria | n/a (analysis) | PASS: `pilot_protocol.md` §6 frozen before running | FAIL (not written; gates 1, 3, 5 fail first) |
| 9 | Raw-output reproducibility and convergence | PASS (R1) | PASS (planned): manifests with file hashes; dt halving on UDDS E3 | n/a |
| 10 | Mapping of outcomes to thesis claims | PASS | PASS (`pilot_protocol.md` §9) | partial: P3 does not test the thesis claim |

## 2. Decisions

- **P1 as a standalone new experiment: no pilot.** The question "does the thesis law help in this
  plant?" is answered by R1. The open part of P1 is the unequal tuning budget (gate 6), which the
  P2 pilot repairs for the scheduled branches as a by-product (S0 vs F0 is P1 with equal budgets).
- **P2 bounded pilot: gates pass in "scenario" form, so a small deterministic pilot is
  justified.** Every result is labelled an assumed-scenario simulation result. It cannot be
  reported as behaviour of the thesis vehicle, because gate 1 passes only through bracketing.
- **P3: gates 1, 3, 5 and 8 fail. No pilot.** What would resolve them is in §3.

## 3. What would resolve the failing gates

| Gate | Missing information | Could a different reference model resolve it without misrepresenting the vehicle? |
|---|---|---|
| 1 (P2 → beyond scenario) | Cell part number and manufacturer datasheet: continuous and peak current vs SoC/T, DCR, voltage window; pack topology reconciling 16 × 3.2 V with 48 V | Yes, **if relabelled**: a documented reference cell (e.g. a manufacturer-specified 100 Ah LFP prismatic cell, once its official specification is actually read) defines a *reference micro-EV*. It is not the thesis vehicle and must not be called so |
| 1, 3 (P3, any fade claim) | A fade law with stated provenance for the chosen cell, with its parameter uncertainty | Partly: Naumann2020/Schimpe2018 (Sony/Murata LFP) or Wang2011 (A123 LFP) give laws for *other* LFP cells; results would be conditional on that cell and must carry its uncertainty |
| 5 (P3) | A justified trip-time or speed-preference requirement | Yes, as a declared scenario (e.g. equal trip time), but the result then answers an eco-driving question, not the thesis question |
| 6 (R1) | Equal-budget tuning of F and S | Done in the P2 pilot (S0 vs F0, S1 vs F1) |
