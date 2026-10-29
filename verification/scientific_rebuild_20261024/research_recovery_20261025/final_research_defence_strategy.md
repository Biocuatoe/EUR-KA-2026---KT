# Final research-defence strategy

**Project:** *Design and Optimization of an Adaptive LQR Controller with Battery Aging Compensation
for a Micro-EV Powertrain* (EURÉKA 2026). **Date:** 2026-10-25.

**Basis:**
- R1 (348 runs, frozen protocol `d80b5b4f…479c`);
- Phase-1 energy ledger;
- literature review (48-source matrix, 89-row search log);
- the pre-registered P2 pilot (257 runs, frozen protocol `ebebc157…2b5a`, all predictions held).

Claim-by-claim status is in `claim_status_matrix.csv`.

**Labels.** Every statement below is an analytical derivation, a numerical verification or a
simulation result in a documented model, or an assumed scenario. **Nothing is real-vehicle or
real-battery validation.**

---

## 1. Position to defend

> The thesis asked whether scheduling LQR weights on battery state of health improves the energy
> efficiency and battery longevity of a micro-EV. The question was turned into a falsifiable
> test:
> - a documented, numerically verified plant;
> - pre-registered protocols;
> - a matched comparison against an equally tuned fixed-gain LQR;
> - a factorial test that separates SoH scheduling from battery-constraint management.
>
> In this model, with the tested scenarios and battery-limit brackets, **SoH scheduling gives no
> practical energy or tracking benefit**, with or without battery-constraint supervision.
>
> The energy that any feedback gain can influence on a fixed reference is bounded by the gap to
> exact tracking: 0.11–0.20 % here.
>
> The submitted 12.5 % energy figure is therefore contradicted within the tested model. The 15.3 %
> capacity-fade figure is unresolved, because no justified fade model exists.

This defends the **direction** (LQR, battery SoH, micro-EV) and the **method**. It does not defend
the original percentages.

## 2. Claims by category

### A. Supported by current evidence (keep, with scope)

| ID | Claim | Label |
|---|---|---|
| A1 | Documented, reproducible micro-EV model with closed energy accounting (≤ 1e-9) and a cross-simulator check (class A) | numerical verification |
| A2 | Thesis SoH weight law: no practical benefit over fixed LQR (R1: ΔE −0.0019 % to +0.034 %, 112 pairs) | simulation result |
| A3 | A single retuned fixed gain matches or beats the scheduled controller (28/28) | simulation result |
| A4 | Resistance growth alone raises energy 0.16–1.1 % at SoH 0.7 and does not change tracking | simulation result + analytical derivation |
| A5 | On a fixed reference a feedback gain acts on energy only through the realised trajectory and the brake split; the gap to exact tracking is 0.11–0.20 % | analytical derivation + simulation result |
| A6 | Frozen-SoH LQR designs are stable for the design model | numerical verification |
| A7 | Equal-budget factorial: no practical scheduling effect, no practical supervision effect, no interaction (\|ΔE\| ≤ 0.025 %, interaction ≤ 0.0033 pp) | simulation result under assumed scenario |

### B. Keep only with explicit conditions

| ID | Claim | Condition |
|---|---|---|
| B1 | Ageing changes the controlled behaviour | only if battery current limits shrink with SoH, an assumed law with no source |
| B2 | Title: "Adaptive LQR … with Battery Aging Compensation" | as the *hypothesis tested*, not an achieved compensation |
| B3 | Equally tuned fixed LQR as the reference baseline | state that the pilot's fixed search box excluded the most aggressive gains |
| B4 | Scheduled LQR tracks better when aged (RMSE 0.017 vs 0.023 m/s on S2 at SoH 0.8) | it reverses at SoH 1.0; post-hoc analysis attributes it to gain magnitude, which a fixed gain can reproduce; not SoH compensation |
| B5 | A battery-constraint supervisory layer is a sound design element | it showed no practical effect in the tested brackets; claim only "does no harm" |

### C. Conflict with completed simulations (remove or restate)

| ID | Claim | Finding |
|---|---|---|
| C1 | 12.5 % ± 2.1 % energy improvement | largest observed difference 0.034 % (R1) and 0.025 % (pilot); contradicted within the tested model and scenarios |
| C2 | Ageing changes the powertrain dynamics through ΔA(SoH) = ΔR_int/L_eq, compensated by the gains | not physical behind a current-controlled inverter; SoH does not enter the speed dynamics |
| C3 | Reduced control authority from increased internal resistance | the voltage window would bind only for R0 > 3.3–3.8 × new; never reached |
| C4 | Integral gain rises as SoH falls (Table 33) | computed gains fall |
| C5 | Adaptive control slows fade by moderating peak currents | peak current differs ≤ 0.044 % between controllers; Keil2015 found more regeneration generally *reduced* ageing |

### D. Unresolved: a model, dataset or source is missing

| ID | Claim | What is missing |
|---|---|---|
| D1 | 15.3 % ± 2.8 % less capacity fade | a fade law for an identified cell, with its parameter uncertainty |
| D2 | NSGA-II energy–longevity Pareto | the fade model; also not novel (Tawfik2024) |
| D3 | EKF/Coulomb-counting SoH estimation accuracy | an implemented estimator; the EKF as specified has no capacity state |
| D4 | Results on NEDC/WLTP/CLTC/VUC and against PID/fuzzy/MPC/DDPG | reproducible implementations |
| D5 | Novelty of SoH-scheduled LQR | IEEE Xplore and Scopus searches |
| D6 | "Validated" parameters | primary sources; the cell part number (16 × 3.2 V ≠ 48 V) |

### E. New hypotheses for a separate R2 (not claims of this thesis)

1. **E1:** SoH-dependent state-of-power limits of an identified 48 V LFP micro-EV pack and their
   effect on urban tracking.
2. **E2:** Scheduling on available power instead of SoH.
3. **E3:** An energy–time–health Pareto frontier with an LQR inner loop at declared trip times.
4. **E4:** A controller fade comparison with a sourced LFP fade law.
5. **E5:** A benchmark protocol for adaptive-controller energy claims (equal budgets,
   gap-to-exact-tracking bound, ledger, completion guard, cross-simulator check).

## 3. How to defend the direction without the percentages

1. **Keep the title.** There is no strong documented reason to change it. In the abstract and
   conclusion, define "battery aging compensation" as the *hypothesis* the work set out to test,
   and state the outcome plainly.
2. **Reframe the contribution as a rigorous evaluation** (A1–A7):
   - the hypothesis is made falsifiable;
   - it is tested with pre-registration, matched comparisons and equal tuning budgets;
   - the ledger explains *why* the result is null: a fixed-reference task leaves a feedback gain at
     most the gap to exact tracking, and SoH does not reach the speed dynamics except through
     battery limits.

   The literature supports the value of this framing:
   - Pan2023, the closest analogue, also found fixed weights ≥ adapted weights;
   - Mahdy2026 reports > 73 % simulation-only work and weak reproducibility in eco-ACC research;
   - Hattori2020 notes that trajectory-changing methods cannot be judged on standard cycles.
3. **State the thesis's original numbers once, as submitted, alongside what the verified model
   gives.** Do not average them or reconcile them:
   - 12.5 % → contradicted within the tested scope;
   - 15.3 % → not evaluated.
4. **Separate what SoH changes from what the controller changes.**
   - SoH raises resistive loss (+0.16–1.1 %) for every controller alike.
   - It changes the trajectory only through battery limits, which bind on every controller alike.
   - That is the physical explanation a defence panel will ask for.
5. **Show the trajectory-freedom distinction.**
   - Double-digit savings in the literature (Djeffal2026 13 %, Lot2025 21 %, LiB2024 10.5 %) come
     from changing the speed profile, often with longer trip time.
   - The ledger shows that a 5–10 % slower reference saves 4–10 % energy per km.
   - This is why a 12.5 % saving cannot come from the controller on a fixed reference, and why the
     thesis must not imply it can.
6. **Answer "why not a bigger study?"**
   - The pre-registered pilot's go criterion (a scheduling benefit on held-out data in both limit
     laws) was not met.
   - The only uncertainty that could change the conclusion is physical: the real cell's power
     limits (OC-1). More simulation sweeps do not resolve it.

## 4. Defence questions and evidence-backed answers

| Likely question | Answer | Where |
|---|---|---|
| Was the fixed baseline weaker than the adaptive one? | In R1 the fixed family had *more* tuning, and it won. In the pilot both had 24 candidates and the result was the same. Caveat: the fixed box excluded the most aggressive gains | `pilot_results.md` §1, §5 |
| Maybe the battery model is too simple? | Possibly for absolute energy. But the controller's lever is bounded by the trajectory: any battery model changes losses for every controller alike unless the controller changes the trajectory | `attainable_improvement_assessment.md` §4 |
| Would a real SoH estimator change this? | It can only degrade the oracle case, and the oracle case shows no benefit | `baseline_scientific_position.md` §4 |
| Is the 15.3 % fade claim wrong? | It is untested: no justified fade model. Current and energy proxies are not fade evidence | D1; Keil2015, SunC2026 |
| Is your method novel? | Not claimed. The evaluation methodology (ledger bound, factorial, cross-simulator check) is the contribution, and it is positioned against prior work | `literature_gap_assessment.md` |

## 5. Actions before the defence

1. **Thesis text.** Apply `claim_status_matrix.csv`: remove C1–C5, D2–D4 and the D1 number;
   qualify B1–B5; add A1–A7 with scope. Thesis repairs from 2026-10-24 remain valid
   (`docs/thesis_closeout_repair_sheet.md`). **The submitted DOCX is not modified by this work.**
2. **Owner items:**
   - OC-1: cell part number and datasheet;
   - the pack voltage conflict;
   - DOIs for thesis refs 7–10 (prior review §9).
3. **Optional, to strengthen the evidence without new claims:** human replication of the pilot
   from `reproducibility_and_limitation_statement.md` §1; full-text reading of Pan2023 Table 2 and
   Naumann2020; an IEEE Xplore/Scopus search before any novelty sentence.

## 6. What would reopen the quantitative question

- **Energy:** a source-grounded limit law for an identified cell that binds much more tightly or
  is shaped differently than the brackets tested, combined with a controller that uses that
  information (E1/E2). Even then, the pilot shows that both controllers sit on the same limit.
- **Fade:** a fade law for an identified cell with stated uncertainty (E4).
- **Neither** is reopened by tuning harder, by running larger grids, or by targeting 12.5 % or
  15.3 %.
