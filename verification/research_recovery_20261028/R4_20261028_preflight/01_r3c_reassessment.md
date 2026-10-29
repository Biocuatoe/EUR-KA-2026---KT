# R4 preflight — Phase 1: R3-C eco-driving results reassessed under a stops-respected reading

**Date:** 2026-10-28. **Prepared by:** AI assistant; no human review. **No simulation was run.** Everything below is from inspecting retained R3 files, plus arithmetic and descriptive statistics on them.

**Tools and outputs (this directory):**

| Tool | Output |
|---|---|
| `tools/describe_r3c_stop_compliance.py` | `01_r3c_eco_stop_compliance.csv` (136 eco profiles); `01_r3_baseline_stop_compliance.csv` (81 baselines) |
| `tools/recompute_r3c.py` | `01_r3c_qs_recomputed.csv` (144 QS rows); `01_r3c_dynamic_recomputed.csv` (51 pilot rows) |

All exit codes were 0.

**R3 sources** (relative to `verification\scientific_rebuild_20261024\research_recovery_20261025\R3_20261025\`):
- `R3_protocol_v1.md` §3.7, §5.3, §7, §10 (SHA-256 `d9e82f89…`, verified);
- `R3_protocol_v1_amendment_1.md` A1.1 and A1.4 (`51a2e93b…`, verified);
- `outputs/gates/eco_rows.csv`, `eco_vsi_rows.csv`, `paths/eco_*.npz`, `paths/band_*.npz`;
- `outputs/pilot_C/M{0,1,2}/runs.csv` and `manifest.json`;
- `code/r3_lib.py` (`segments`, `eco_segment_solve`, `eco_for_time`, `eco_profile`);
- the reports `R3_gate_results.md` §5 and `R3_pilot_results.md` §2.

---

## 1. Which protocol each R3-C result belongs to

**Main correction to the premise.** R3's stop-respecting amendment (A1.1) was applied to the **same-task band DP** (gates G-B′ and G-A′). It was **never** applied to the eco DP or to the R3-C pilot. A1.1 forced v = v_b at every sample where the baseline is at rest. **R3 contains no stop-respecting version of any eco-driving result.** [D: amendment text, `run_gates_a1.py` produces only band and VSI rows]

| Result set | Governing text | Run | Affected by A1.1? |
|---|---|---|---|
| G-C gate: QS eco savings S_found, S_max for A ∈ {0, 2.5, 5, 10} % | v1 §3.7, §4 | frozen run, 2026-10-25 15:32–15:44 | **no** |
| VSI_eco (SoH value of the eco plan at A = 0) | v1 §3.7 | same frozen run | no |
| R3-C pilot: fixed R1 LQR tracking v_b, eco A = 0, eco A = 5 % | v1 §5.3 + A1.4 (profiles, distance basis, exclusion rule, checks) | about 16:01–19:23 | no (A1.4 only fixed pilot details) |
| G-B′ / G-A′ (stop-respecting band, same task) | A1.1 | 15:48–15:59 | yes, but this is **not** eco-driving. It is the tracking-tolerance lever and is outside R3-C |

**What the eco DP does at stops, by construction** (`r3_lib.py`, `segments`, `eco_profile`) [D]:
- Each moving segment between reference standstills is re-planned from rest to rest over the reference segment's distance.
- Speed stays at or below that segment's reference maximum. Acceleration stays within the whole cycle's reference extremes.
- Idle intervals keep their durations and order.
- **The travel time of each segment is free.** A single λ trades energy against total time across all segments.

So stop *locations* and *dwell durations* are preserved, but stop *arrival times* are not.

## 2. Were the reported numbers computed from retained data?

| Reported quantity | Retained raw artefact | Recomputed in this run [A] | Result |
|---|---|---|---|
| QS S_found (all cycles, branches, limits, P1/P3, A) | `outputs/gates/eco_rows.csv` (144 rows), with E_eco and E_b per row | S = 100·(1 − E_eco/E_b) | equal to the recorded value in all 144 rows, max difference 1.4e-14 pp |
| Dynamic ΔE vs baseline (R3-C pilot) | `outputs/pilot_C/M*/runs.csv` (17 rows each), with Wh per reference km per run | ΔE = 100·(E_eco − E_base)/E_base per reference km, paired by cycle, limits, dt | every value in `R3_pilot_results.md` §2 reproduced to the printed digits |
| Trajectories behind the QS numbers | `outputs/gates/paths/eco_*.npz`, `band_*.npz` (knots or 1 s samples) | used for §3 | retained and hashed (`run_manifest.json`) |
| Per-sample dynamic traces (speed, torque, current, voltage) of R3-C | **not retained**: the pilot wrote aggregate rows only | — | energy cannot be independently recomputed from samples; only from aggregates |
| Code as run for R3-C | `r3_lib.py` retained (frozen-unchanged). The driver `r3_pilot.py` as run (`cec5f70b…`) is **not retained**; the current file is the post-fix `7fd01aca…` (`00_baseline_audit.md` §5.1) | — | outputs retained; generating driver not retained |

## 3. Comparability: distance, time, stops, terminal state, energy boundary

Held-out cycles S2 and UDDS, P1. Values come from `01_r3c_eco_stop_compliance.csv`, `01_r3_baseline_stop_compliance.csv` and `01_r3c_dynamic_recomputed.csv`.

| Aspect | Baseline task v_b | Eco A = 0 | Eco A = 5 % | Comparable? |
|---|---|---|---|---|
| Distance (QS, against d_ref) | S2: exact. UDDS L-R1: −7.7 to −16.7 m (≤ 0.14 %). UDDS L-EVE: −104 to −194 m (0.86–1.62 %) | exact (error < 1e-9 m) | exact | yes. Where the baseline falls short, the metric (per reference km) is *conservative* for eco |
| Distance (dynamic) | shortfall S2 −0.03 %; UDDS L-R1 0.06–0.14 %; UDDS L-EVE 0.88–1.63 % (M0, M1 incomplete) | complete in every run | complete in every run | yes, except UDDS L-EVE M0/M1 (baseline incomplete; R3 excluded these) |
| Total trip time | = T_ref | S2 212.91–212.97 s vs 213; UDDS 1367.6–1368.9 s vs 1369 | +4.9 to +5.0 % | A = 0 matched; A = 5 % is an energy-time trade-off by design |
| Stop locations | S2 exact; UDDS shifted up to 16.7 m (L-R1) and 194 m (L-EVE), because the reference's accelerations are infeasible | exact | exact | yes |
| Dwell at each stop | equal (one UDDS L-EVE M0 sample differs) | exact | exact | yes |
| **Stop arrival time vs reference** | equal | **S2: ≤ 0.32 s. UDDS: up to 84–89 s late and about 10 s early (mean \|shift\| 41–44 s)** | S2: ≤ 10.6 s late. UDDS: ≤ 121–127 s late | **S2 A = 0 only** |
| **Moving while the reference is at rest** (A1.1's criterion, on the 1 s reference grid) | 0 of 65 (S2); 0 of 259 (UDDS L-R1); 1 of 259 at 0.55 m/s (UDDS M0 L-EVE) | **S2: 5 of 65 samples, ≤ 0.18 m/s. UDDS: 156–168 of 259 samples, up to 13.6 m/s** | S2: 27–28 of 65, ≤ 4.6 m/s. UDDS: 144–169 of 259 | **S2 A = 0 only, and only within a tolerance** |
| Speed envelope | = reference (UDDS peak 25.35 m/s = 91.2 km/h; 15.1 % of time above 50 km/h) | UDDS peak 13.6 m/s (49 km/h) | UDDS peak 12.4 m/s | UDDS eco removes the high-speed part of the cycle |
| Initial and terminal state | rest; SoC 0.8; V1 = 0; ends at rest | same | same | yes. With constant OCV the energy integral needs no SoC terminal correction |
| Energy boundary | net ∫V_oc·i dt (OCV-referenced battery energy, regeneration netted, no auxiliary load, friction-brake energy lost) | same | same | yes, identical in every arm |
| Controller | R1 fixed Bryson LQR, same gain | same gain | same gain | yes |
| Plant | R3 reference plant: thesis-printed vehicle values, generic 48 V / 100 Ah LFP pack, motor-loss bracket M0/M1/M2. **Not the KT-01 vehicle** | same | same | yes (within the plant) |

**Domain finding.** UDDS reaches 91.2 km/h, against the thesis's declared 0–50 km/h micro-EV domain. Its peak power demand exceeds the 18 kW motor rating (20.96 kW [H]). UDDS is therefore an out-of-domain cycle for this plant. The 25–34 % UDDS savings combine three things:
- removing the >50 km/h excursion (the eco profile never exceeds 49 km/h);
- avoiding 70–81 Wh of baseline friction braking that the assumed 1C charge limit forces;
- rescheduling stops by up to about 1.5 min.

None of the three is an eco-driving effect at a comparable task.

## 4. Attribution: trajectory, LQR, SoH

| Source | Size in R3-C | Evidence |
|---|---|---|
| **Changed trajectory / driving task** | All of the measured ΔE. Both arms use the same LQR gain and plant state, so the only difference between them is the profile | design (v1 §5.3) [D] |
| **Low-level LQR** | Contributes no saving by design. Its *interaction* with the profile is the gap between the dynamic ΔE and the QS prediction: S2 A = 0 is +0.02 pp (M0) and −0.02 pp (M1), but **−2.10 pp under M2**, where the dynamic saving is 2.24 % against a QS 4.34 %. On UDDS the gap is ≤ 0.53 pp (M0, M1) and up to 3.04 pp (M2). The M2 gap comes from the LQR holding torque at standstill (R3's post-hoc diagnostic [H]) | `01_r3c_dynamic_recomputed.csv` [A] |
| **SoH-aware logic** | **Not tested in R3-C**: the pilot ran P1 (SoH 1.0) only. QS VSI_eco at A = 0 is 0–0.075 % on S2 and 0.011–0.024 % on UDDS. In UDDS M0 L-R1 the P1 eco trip is infeasible on P3, i.e. SoH changes feasibility, not energy | `eco_vsi_rows.csv` [D] |
| Numerical resolution of VSI_eco | On S1/M1 (in-sample), the P3-optimised trip is **0.40 % worse** on P3 than the P1-designed trip (87.33 vs 86.99 Wh). The λ-bisection eco DP can therefore miss its optimum by about 0.4 %, which is more than every VSI_eco value | `eco_vsi_rows.csv` [A] |
| Battery charge-limit assumption | UDDS baseline friction 70–81 Wh (8–10 % of energy) under a 1C charge limit (class C/D, not datasheet-based) | `eco_rows.csv` base_fric_Wh [D] |

## 5. Classification of R3-C results

Validity labels are relative to R4's stops-respected reading. In that reading the vehicle is at rest at every reference stop location, for at least the reference dwell, over the reference's time intervals, and distance and total time are matched.

| ID | Result (as reported in R3) | Protocol | Raw artefact | Comparability | Validity for R4 | Limitations |
|---|---|---|---|---|---|---|
| RC-1 | QS S_found, S2 A = 0: M0 2.85 %, M1 1.48 %, M2 4.34 % | v1 §3.7 | `eco_rows.csv`; `paths/eco_S2_*.npz` | distance and dwell exact; time −0.03 to −0.09 s; arrivals ≤ 0.32 s; 5/65 rest samples at ≤ 0.18 m/s | **VALID-CONDITIONAL**: stops-respected only within a ≈ 0.3 s arrival tolerance that was never pre-registered | QS. Reference plant. M2 QS is not representative (QS vs dynamic +6–14 %). Single held-out cycle of 0.53 km. L-R1 and L-EVE are identical on S2 (limits never bind), so they are not two observations |
| RC-2 | Dynamic ΔE, S2 A = 0: M0 −2.87 %, M1 −1.46 %, M2 −2.24 % | v1 §5.3 + A1.4 | `pilot_C/M*/runs.csv` | as RC-1; complete; RMSE ≤ 0.047 m/s | **VALID-CONDITIONAL** (as RC-1) | As RC-1. Aggregates only, no per-sample traces. Driver code as run not retained. P1 only. These are the only R3-C numbers carried forward, and only as a reference-plant observation |
| RC-3 | S2 A = 2.5 / 5 / 10 %: QS 6.4–20.0 %; dynamic A = 5 %: −14.25 / −9.67 / −10.90 % | v1 §3.7, §5.3 | as above | trip time +2.5 to +10 %; arrivals up to 21 s late | **VALID ONLY AS AN ENERGY-TIME TRADE-OFF**. Not a matched-task saving | Do not report it without the time increase. It is not comparable to a matched-time controller result |
| RC-4 | QS S_found, UDDS L-R1 A = 0: 27.8 / 28.5 / 28.1 % | v1 §3.7 | `eco_rows.csv`; `paths/eco_UDDS_*.npz` | arrivals shifted up to 89 s; moving during 60–65 % of reference rest samples; peak 49 vs 91 km/h | **INVALID** under the stops-respected reading; out of domain | Valid only under the weaker definition (same stop locations and dwell, equal total time), and only for the reference plant on an out-of-domain cycle |
| RC-5 | Dynamic ΔE, UDDS L-R1 A = 0: −28.28 / −28.99 / −25.26 % | v1 §5.3 + A1.4 | `pilot_C/M*/runs.csv` | as RC-4 | **INVALID** | as RC-4 |
| RC-6 | UDDS L-R1 A = 5 %: QS 33.7–33.8 %; dynamic −34.30 / −34.34 / −30.66 % | v1 | as above | as RC-4 plus +5 % time | **INVALID** | as RC-4 |
| RC-7 | UDDS L-EVE A = 5 %: dynamic M0 −29.50 %, M1 −31.00 % (excluded by R3), M2 −28.07 % | v1 + A1.4 | as above | baselines M0/M1 incomplete (1.64 / 1.14 % shortfall) | **INVALID** (stops; and M0/M1 baselines incomplete) | — |
| RC-8 | UDDS L-EVE A = 0 | v1 + A1.4 | "profile unavailable" rows | — | **NO RESULT**: the time budget is infeasible under 2C | Correctly recorded by R3, not replaced |
| RC-9 | VSI_eco at A = 0 ≤ 0.08 % | v1 §3.7 | `eco_vsi_rows.csv` | P3 vs P1 design | **VALID AS "BELOW RESOLUTION"**: smaller than the demonstrated ≈ 0.4 % DP optimality gap (§4) | UDDS rows inherit RC-4's stop problem |
| RC-10 | Stress indicators, UDDS: Ah −25 %, ∫i²dt −47 to −50 % | v1 §6 | `pilot_C/M*/runs.csv` | as RC-4 | **INVALID** (stops, domain). In any case not capacity fade | No ageing model |
| RC-11 | Summary wording "eco 2–29 %" and "≈ 25–29 % on UDDS at equal time" | `R3_pilot_results.md` §4; earlier session notes | — | — | **Upper end withdrawn**. Only "≈ 1.5–2.9 % on S2 at A = 0, reference plant, ≈ 0.3 s stop tolerance" survives | — |

## 6. Unfinished, invalid or incomparable tests

1. **No stops-respected eco result exists** for any cycle with nonzero arrival shift (all UDDS rows, and S2 at A > 0).
2. UDDS L-EVE A = 0: no eco profile (infeasible time budget).
3. UDDS L-EVE baselines for M0 and M1 are incomplete (> 1 % shortfall). R3 excluded them correctly.
4. QS vs dynamic checks failed in places:
   - M2 fails everywhere (+6.0 to +13.6 %);
   - M0 UDDS baselines fail marginally (+1.05 / +1.01 %);
   - so M2 QS numbers (RC-1 for M2) do not represent the dynamic plant.
5. S1 results are in-sample only. S2 is the only held-out cycle within the 0–50 km/h domain.
6. The pilot covered P1 only. No SoH variation was tested dynamically.
7. No jerk limit. No parameter-uncertainty draws. No per-sample traces retained.
8. A completeness tolerance of 1 % of distance equals the 1 % practical threshold, so a borderline-incomplete run could carry up to about 1 pp of artificial saving. No R3-C credited run is affected: the credited runs' shortfalls are ≤ 0.14 %. The rule is still unsafe and is tightened in the R4 protocol.

## 7. Smallest future test needed

To turn RC-1/RC-2 into an unconditional stops-respected result, and to obtain any eco result on a second cycle:

- **Planner "S-eco" (stops fixed in time):** the R3 eco DP per segment with its own time budget. Each segment's travel time must be ≤ the reference segment's travel time, and departure from each stop happens at the reference departure time. The vehicle waits if it arrives early, so it is at rest whenever the reference is at rest. Speed and acceleration bounds are as in R3. Full definition: `03_R4_protocol_v1.md` §5.2.
- **Runs:** S2 (held out) and S1 (in-sample) × M0/M1/M2 × L-R1/L-EVE × P1; fixed R1 LQR tracking v_b and the S-eco profile; dt 1 ms, with a 0.5 ms convergence repeat on S2 L-EVE; per-sample traces retained.
- **UDDS:** not part of the minimal test. It lies outside the micro-EV domain. If it is ever used, it is a separately labelled out-of-domain stress case.

## Gate G1 — PASS (classification complete; no stops-respected eco magnitude established beyond S2 A = 0)

**Why it passes.** The retained evidence is sufficient to classify every R3-C claim:
- the protocol each result belongs to is identified;
- every reported number is reproduced from retained raw rows;
- distance, time, stop, terminal, boundary and attribution comparability were measured from the saved trajectories.

**What the classification says:**
- Only S2 at A = 0 is near-stops-respected (≤ 0.32 s arrival shift). Its dynamic savings are 1.46–2.87 % on the reference plant.
- Every UDDS eco result is invalid under a stops-respected reading and is out of domain.
- Results with A > 0 are energy-time trade-offs.
- None of these results is attributable to the LQR or to SoH.

**What G1 does not establish.** It does **not** establish a stops-respected eco-driving benefit on any cycle other than S2, or one that is independent of the unregistered 0.3 s tolerance. That requires the minimal test in §7, which is not run here. Dependent work (H3 in the protocol) is therefore not given any prior effect size from R3-C.
