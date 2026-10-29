# Defence wording options for the 12.5 % and 15.3 % claims

**Date:** 2026-10-25.
**Basis:** `numeric_claim_provenance_report.md` and `numeric_claim_traceability.csv` in this folder.

**Which version applies today: Version B.** The original numerical provenance has not been recovered. Version A becomes usable only after every gate in A.1 has been passed and documented.

**How to use this file.**
- The quoted statements are written to be said, or handed over, as they stand. Shortening them is fine. Making them stronger is not.
- The submitted thesis is not altered. A correction is made by an erratum or a defence statement, never by editing the submitted file.

---

## Version A: original provenance recovered *and* independently reproduced

### A.1 Gates that must all be passed before any Version A wording is used

1. **Original material recovered.** The original native source, model and scripts, configuration, seeds and raw per-run outputs for **both** controllers are recovered, with file dates that predate submission. These are report §4.3 items 1–7.
2. **Material recorded as found.** It is hashed and archived exactly as found, before anything is run.
3. **Independent rerun.** A person other than the author reruns it in a recorded environment **without changing any assumption, parameter or seed**.
4. **Same quantity reproduced.** The rerun reproduces 12.5 % and/or 15.3 % as the *same* quantity the Abstract states: the same metric, cycle, SoH, horizon and statistic behind ±.
5. **Internal inconsistencies explained.** The material explains the thesis's own conflicting figures:
   - 10.2 % (95 → 85.3 Wh/km);
   - 13.9 % / "14 %" (16.5 → 14.2 %/1000 cycles);
   - 16.7 % and the 5.5× lower fade level of Figure 11;
   - N = 100 vs N = 1000;
   - Cohen's d = 0.89.
6. **Relation to R1/R2 explained.** The material shows what its model contains that the documented model tested in R1/R2 does not, so it is clear why R1/R2 found no practical difference.
7. **Fade model specified.** For 15.3 %, the fade model is fully specified (including k_c and k_cal or their replacement) and its parameters are sourced.

If any gate fails, use Version B. A partial recovery permits only the narrower wording in A.3.

### A.2 What can be said (all gates passed)

> "The 12.5 % [and 15.3 %] figure[s] in the Abstract come from [named script/model, version, commit],
> run on [cycle] at SoH [value] with [N] paired runs. The ± values are [SD/SE/CI] over those runs.
> The original files have been recovered unchanged and independently re-run by [name] on [date],
> who obtained [value]. The archive and hashes are at [location]."

> "The figure applies only to that model and scenario. It is a simulation result, not a measured
> vehicle result."

> "The thesis body contains inconsistent restatements (10.2 %, 14 %, Figure 11). They are corrected
> in the erratum as follows: [list]."

> "Our later pre-registered re-implementations (R1, R2) found no practical difference on the
> documented model. The difference arises because the original model includes [mechanism], which the
> documented model does not. The result therefore depends on that modelling choice, and it is
> justified by [source]."

**Must not be said, even in Version A:**
- that the result holds for real vehicles;
- that it holds generally, beyond the reproduced model and scenario;
- that it is supported by Tawfik et al. (2024) or any other paper that did not study this controller;
- that the R1/R2 null results were wrong. They remain valid within their own scope.

### A.3 Partial recovery (some original files found, not independently reproduced)

> "Some original files have been located [list]. They have not yet been independently reproduced, so
> the 12.5 % and 15.3 % figures are not presented as verified results."

Then continue with Version B.

---

## Version B: original provenance not recovered (current state)

### B.1 Core statement to the examiner

> "The Abstract's figures of 12.5 % ± 2.1 % energy improvement and 15.3 % ± 2.8 % less capacity fade
> cannot be traced to any calculation, simulation output or code. I withdraw them."
>
> "The thesis body does not support them either. Its own comparison values give 10.2 % and 13.9 %,
> and Figure 11 as drawn implies a different value again. None of these is backed by retained data,
> so I do not rely on any of them."

> "After submission I rebuilt the study on a documented model and ran pre-registered comparisons:
> 348 runs in R1 and 257 in a second, pilot study. On that model, scheduling the LQR weights on
> battery state of health changed energy per kilometre by at most about 0.03 %, which is no practical
> difference under the rule I fixed in advance. A single well-tuned fixed gain did as well or better.
> No credible capacity-fade model was available, so I make no battery-life claim."

### B.2 What can be said, claim by claim

**SoH-aware control as motivation:**

> "There is good reason in the literature to expect battery ageing to matter for energy management.
> Ageing raises internal resistance and lowers capacity, and studies such as Tawfik et al. (2024)
> report lower modelled degradation when battery current is limited. That motivated the question.
> In my formulation, though, SoH only changes the LQR weights of a speed-tracking loop. In the
> documented model this has no pathway to change energy or current materially. That is what R1 and
> R2 found."

**The 12.5 % claim:**

> "Withdrawn. Its origin is not documented: I cannot produce the script, data or calculation behind
> it. On the documented model the measured difference is below 0.034 % in every tested case."

**The 15.3 % claim:**

> "Withdrawn. The thesis's ageing equations are incomplete: two coefficients are never given, and the
> units are inconsistent. No fade simulation can be shown to have been run with them. The fade curves
> in Figure 11 do not have the form of those equations. Whether SoH-aware control changes capacity
> fade remains an open question in this work."

**R1 and R2:**

> "Within their scope, the null results are sound. That scope is: my documented plant, the assumed
> battery parameters and limits, the thesis's SoH weight law, and the named drive cycles. The
> protocols were frozen before the runs, all runs passed integrity checks, and the time step was
> shown to be converged. They do not prove equivalence, and they say nothing about a real vehicle or
> about other controller formulations."

**Other formulations:**

> "Other formulations may well reduce energy use or degradation. Published simulation studies of
> current limiting or eco-driving report effects of this size, but on different vehicles, levers and
> baselines. My project has not demonstrated any such gain, and I do not claim one."

**If asked about Tawfik et al. (2024):**

> "That paper studies NSGA-II optimisation of battery-current limits on a BMW i3 model. It reports
> 13 % lower energy and 15.8 % lower capacity loss over one daily trip, compared with an
> unconstrained model. It is related work. It is not cited in the submitted thesis and should have
> been, because it overlaps my Pareto-optimisation contribution. Its results are not results for my
> controller, and I do not use them as support for my numbers."

**If asked where the numbers came from:**

> "I cannot document their origin. The project contains no code, data or logs that produce them, and
> I am not going to offer an explanation I cannot evidence."

This is the honest answer on in-project evidence. Before the defence, the owner should decide whether the external material listed in report §4.4 (`D:\EUREKA`) is to be inspected. Whatever that material shows, the answer must not go beyond it. It must never suggest a computation that cannot be produced.

**If you personally know how the numbers were produced,** for example that they were taken or adapted from published values, or entered as targets, say so plainly instead of the sentence above:

> "They were [how]. They are not results of my simulations."

"I cannot document their origin" is only honest if it is true. Examiners treat a candid account of a mistake far better than an answer that later turns out to be evasive.

### B.3 What must not be said in Version B

- That 12.5 % or 15.3 % is a result, an approximate result, or "within uncertainty" of a result.
- That the ± intervals are confidence intervals or derive from Monte Carlo runs.
- That 10.2 %, 9.7 %, 14 % or the Figure 11 curves are verified results. They share the same missing provenance.
- That Tawfik et al. (2024), or any other paper, confirms, validates or "is consistent with" the thesis's numbers for this controller.
- That the claims were "reproduced", "approximately reproduced" or "partially reproduced" by R1/R2. R1/R2 contradict 12.5 % within their scope and could not assess 15.3 %.
- That SoH-scheduled LQR is "novel" or "the first". The literature search did not cover Scopus or IEEE Xplore, and adjacent work exists.
- That the null result proves no SoH-aware controller can help. It covers one formulation on one documented model.
- Any reconstructed value presented as the original.

### B.4 What can be offered as the contribution instead

All of the following come from existing project records; nothing here is new evidence.
- A documented, test-verified longitudinal micro-EV model with fixed and SoH-scheduled LQR, cross-checked against an independent Modelica implementation.
- A pre-registered negative result:
  - SoH scheduling of LQR weights gives no practical energy difference on that model;
  - a single retuned fixed gain does as well or better;
  - SoH matters only if current limits are assumed to scale with SoH.
- A clear statement of what would be needed to test capacity-fade benefits:
  - a sourced fade law;
  - a cell datasheet (owner item OC-1);
  - a formulation in which SoH can affect current or power.

---

## Quick reference

| Question from the examiner | Version B answer in one line |
|---|---|
| Can you show the calculation for 12.5 %? | No. It is untraceable and withdrawn. |
| Then why does the body say 9.7 % / 14 %? | Those are inconsistent restatements, also without retained data. 95 → 85.3 Wh/km is in fact 10.2 %. |
| Is Figure 11 simulation output? | It cannot be shown to be. Its curves do not follow the thesis's own ageing equations. |
| Did you re-test the idea? | Yes, pre-registered: R1 348 runs, R2 257 runs. No practical difference (≤ 0.034 %). |
| Is the idea wrong? | Not shown. This formulation, on this model, gave no benefit. Other formulations remain open. |
| Is this from Tawfik et al. 2024? | I cannot establish where the numbers came from. That paper's results are for a different system and are not mine. |
