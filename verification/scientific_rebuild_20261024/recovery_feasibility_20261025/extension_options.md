# Candidate research extensions (Phase 2)

**Date:** 2026-10-25. **Nothing here was implemented.** Quantitative expectations come from the
Phase 1 ledger (`attainable_improvement_assessment.md`); everything else is reasoning, labelled.

**Not treated as facts:** the 100 Ah capacity, the 48 V/16-cell pack, the 3.2 V/100 Ah "CATL"
cell, and the rule "current limit ∝ SoH". Each is an unverified thesis value or an assumption
(R1 class C; owner item OC-1).

---

## 1. Candidate open data and published parameter sources

**Verification level.** *Metadata verified* = DOI resolved through Crossref or DataCite on
2026-10-25 and title, authors, venue, year, licence read. Chemistry, cell format and measured
quantities marked **[M]** are from my memory of the literature, **not** checked in this session
and must be confirmed from the primary text or the dataset README before any use. Nothing was
downloaded and no full text was read here.

| Source | Metadata verified | Chemistry / format | Measured quantities | Relevance | Mismatch to the thesis pack |
|---|---|---|---|---|---|
| Severson et al., *Nature Energy* 2019, 10.1038/s41560-019-0356-8 (data via data.matr.io) | Yes (article). Dataset host was unreachable in the 2026-10-24 audit; file list, size and licence **unverified** | LFP/graphite, A123 APR18650M1A, 1.1 Ah cylindrical high-power (verified in `docs/battery-data-feasibility-audit.md`) | V, I, T, Q per cycle; internal resistance at 80 % SoC by 30 ms pulses | Only LFP data with run-to-failure fade vs. charge protocol and C-rate; shows fade/resistance trends | Cell is 1.1 Ah power cell, 72 fast-charge policies, 30 °C chamber; not a 100 Ah prismatic cell; **not** validation for any specific pack |
| Attia et al., *Nature* 2020, 10.1038/s41586-020-1994-5 | Yes (article) | Same A123 cell family **[M]** | Cycle-life under optimised fast-charge protocols | Same as above | Same |
| Wang et al., *J. Power Sources* 196:3942–3948, 2011, 10.1016/j.jpowsour.2010.11.134 ("Cycle-life model for graphite-LiFePO4 cells") | Yes (title, authors, pages) | LFP/graphite; cell format and parameter values **[M] not read** | Published empirical fade law in Ah throughput, C-rate and temperature | Closest published LFP fade law with a C-rate term | Fitted on a different (A123-type) cell; parameters must be read from the paper; extrapolation to a 100 Ah cell is unvalidated |
| Naumann et al., *J. Energy Storage* 2018, 10.1016/j.est.2018.01.019 (calendar) and *J. Power Sources* 2020, 10.1016/j.jpowsour.2019.227666 (cycle) | Yes (titles, venue, year) | Commercial LFP/graphite cell **[M]** 26650 format; parameters **not read** | Published calendar and cycle fade laws vs. SoC, temperature, DoD and C-rate | Most complete published LFP calendar plus cycle models | Different cell, small format; temperature controlled |
| Oxford Battery Degradation Dataset 1, 10.5287/bodleian:KO2kdmYGg | Yes (DataCite; ODC-ODbL, share-alike) | Small pouch cells **[M]** (not LFP) | Ageing under a drive-cycle current profile; characterisation | Only item using a drive-derived load | Not LFP; 40 °C; sub-Ah pouch |
| Kollmeyer, LG 18650HG2, 10.17632/cp3473x7xv.3 | Yes (DataCite; CC BY 4.0) | NMC-type 18650, 3 Ah **[M]** | Drive-cycle (UDDS, US06, etc.) V, I, T at several temperatures **[M]** | Useful for **ECM identification method** under real drive load | NMC, not LFP; fresh cell, no ageing |
| Kollmeyer, Panasonic 18650PF, 10.17632/wykht8y7tg.1 | Yes (DataCite; CC BY 4.0) | NCA-type 18650, 2.9 Ah **[M]** | Same style | Same | Same |
| NASA PCoE Li-ion ageing set, CALCE cell datasets | **Not checked** | 18650 / prismatic **[M]** | Cycling with capacity and impedance **[M]** | Candidate only | Chemistry/format must be confirmed; likely not LFP |

**Rule that follows.** An NMC or NCA dataset may demonstrate *how to identify* an equivalent-circuit
model; it must not be presented as validation of LFP behaviour. An A123 LFP power-cell dataset
informs the *form* of a fade law; it does not validate a 100 Ah CATL pack. **No source above
characterises the thesis's cell**, because the cell has no part number (owner item OC-1). Until the
author supplies the part number and datasheet, every parameter from these sources is an
assumption with a stated provenance, never a measured property of the modelled vehicle.

---

## 2. Option A: more complete battery equivalent-circuit model

**Mathematical change.** Replace constant V_oc, R0, R1, C1 by
V_oc(SoC, T), R0(SoC, T, SoH), (R1, C1)(SoC, T, SoH); add a capacity state Q(SoH); replace the
assumed limits with physical ones: a voltage window per cell and a current limit I_max(SoC, T,
SoH) taken from a datasheet. Optionally add a first-order thermal state C_th·dT/dt = R0·I² − hA·(T − T_amb).

**Required parameters.** Cell part number and datasheet (OCV curve, DCR table, continuous and
peak current vs. SoC and T, voltage window); series/parallel count; interconnect resistance; BMS
derating rules. Thermal: C_th, hA.

**Source availability.** Unavailable for the stated cell. For a *substitute* cell, a datasheet plus
a characterisation dataset (e.g. the Kollmeyer sets for the method, a manufacturer datasheet for
values) is available but would redefine the vehicle.

**Implementation cost.** Moderate: new states and tables, a second independent implementation
(R1 has none for the battery window), regression against the legacy model. Data sourcing is the
real cost.

**Principal bias risk.** Choosing a convenient cell or fitting limits so that SoH matters
(R1 showed SoH matters only through the I_max ∝ SoH assumption). Fidelity can be mistaken for
validity: adding states with unmeasured parameters adds tuning freedom, not truth.

**Expected measurable outcomes (from Phase 1).** By itself A is a *plant* improvement, not a
controller improvement; it changes absolute energy and the size of the charge-limit friction floor
(§5.2 of the assessment) and nothing else. It cannot show a controller benefit; it can only reveal
whether the headroom is larger or smaller than 0.2–0.8 %.

**Fairness.** Apply the same plant to every controller; freeze it before tuning.

**Value for the research question: indispensable as a precondition for B or C, no value on its own.**

---

## 3. Option B: battery-aware constrained / gain-scheduled LQR with regeneration coordination and reference governor

**Mathematical change.** Constrained LQR / MPC on x = [e, T, z] with input and state constraints
T ∈ [−T_neg(SoC, SoH, T), T_pos(...)], I ∈ [−I_ch, I_dis], and a reference governor that
modifies the setpoint r → r' within |r' − r| ≤ ε and a distance-lag budget, so that the
constrained trajectory remains feasible. Gain scheduling on the *available limits* instead of on
SoH weights directly.

**Required parameters.** Everything in option A that defines the limits, plus the governor
tolerances ε and lag budget, plus the horizon and weights.

**Source availability.** Limits unavailable (see A). ε is a design choice that decides the result.

**Implementation cost.** High: online optimisation or explicit MPC, governor logic, tuning budget.

**Principal bias risk.** The governor tolerance buys energy by slowing the vehicle (assessment
§5.4), i.e. tracking-for-energy trades; the limit model is assumed; a more flexible controller is
tuned harder than the baselines (R1 already has this asymmetry: F01 tuned, S not).

**Expected measurable outcomes.** The only controller-attributable headroom Phase 1 supports is
(i) the gap to exact tracking, 0.11–0.20 % on S1 and S2; (ii) friction excess above the forced floor,
0.2–0.6 % of energy on S1 and UDDS, both **assumption-dependent**; rough sum **≲ 0.8 %**. Tracking
*feasibility* under tightened limits (UDDS under 2 C) is set by the discharge limit and cannot be
recovered by any controller without relaxing the reference. A governor makes the failure graceful;
it does not create energy. Expected effect on Ah throughput and peak current: at most a few tenths
of a percent (assessment §5.3) unless the governor deliberately slows the vehicle.

**Fairness.** Same plant, reference, actuator limits and initial state; fixed-gain LQR tuned with
the same procedure and budget; all controllers (not only B) receive the same limit information, or
the comparison is labelled "informed vs. uninformed". Report Pareto of (energy/km, RMSE, completion).

**Verdict (Phase 1 evidence):** headroom below the pre-registered 1 % margin on the data in hand;
no controller design can exceed it in this plant unless the limits turn out to be much tighter than
assumed, which only a datasheet can tell.

---

## 4. Option C: degradation-aware objective with a transparent capacity-fade model

**Mathematical change.** Add a wear term to the cost, J = ∫(e'Qe + u'Ru) dt + λ·ΔQ_loss, with a
fade rate such as dQ_loss/dAh = f(C-rate, T, SoC, Q_loss) (form: published empirical LFP laws,
e.g. Wang 2011, Naumann 2018/2020; **parameters not read here**). Fade feeds back into capacity,
resistance and limits, closing the loop between control and ageing.

**Required parameters.** The fade-law constants for the actual cell; the SoH-to-resistance and
SoH-to-limit mappings; λ (a price on wear, which is a value judgement, not a physical constant).

**Source availability.** Published laws exist for A123- and Sony/Murata-type LFP cells (metadata
verified above). None is for the CATL 100 Ah cell, and a one-cycle simulation sees about 1e-5 of
the lifetime fade, so every conclusion is an extrapolation over many cycles.

**Implementation cost.** High: long-horizon (multi-cycle) simulation or averaged wear rates;
uncertainty propagation over fade-law parameters.

**Principal bias risk.** Selecting a fade law and λ that reward the proposed controller; extrapolating
a small-cell law; reporting a percentage fade reduction that is smaller than the law's own parameter
uncertainty. The thesis's 15.3 % is not a target and no value is tuned to it.

**Expected measurable outcomes.** In the tested family the stress indicators differ by ≤ 0.23 %
(Ah), ≤ 0.48 % (RMS current), ≤ 0.044 % (peak current). For a fade law that is sublinear in Ah and
not extraordinarily sensitive to peak current, the controller-attributable fade difference is of the
same size, i.e. **well under 1 %**, a conditional statement, not an estimate. A larger effect would
need the controller to change the current profile materially (which means changing the trajectory:
option D).

**Fairness.** Same fade law, parameters (nominal and bounds) and λ for all controllers; report fade
with its parameter-uncertainty interval, not as a point value; wear-cost weight swept, not tuned.

**Verdict:** premature. It needs option A's cell identity first, and with the current controller
family the effect size is below any plausible fade-law uncertainty.

---

## 5. Option D: eco-driving / speed-reference optimisation layer

**Mathematical change.** The reference becomes a decision variable: minimise
E(v(·)) + μ·t_trip + λ·wear subject to the plant dynamics, battery limits and speed bounds, with
the tracking controller as an inner loop. This is an optimal-control problem (dynamic programming
or direct collocation), no longer a same-cycle tracking experiment.

**Required parameters.** Everything in A; the value of time μ (or a trip-time/distance
constraint); traffic and speed-limit constraints; optionally a fade model (C).

**Source availability.** The physics is in the existing model; μ and traffic constraints are
scenario choices.

**Implementation cost.** Moderate for a model-only solver (1-D speed-time DP); high for coupling
with battery limits and wear.

**Principal bias risk.** The largest of the four. Leverage is large (assessment §5.4: 2 %, 5 %,
10 % slower gives 1.7–2.3 %, 4.1–5.4 %, 7.7–10.1 % less energy per km) and is bought with trip time,
so "energy saved" is not a free improvement and is easily inflated by an unstated time budget. It is
independent of SoH: **a battery-aware layer matters only where battery limits bind, i.e. only through
the unsourced limit law**. Eco-driving is an established field; no literature search for it has been
done in this project (the earlier review covered SoH-scheduled LQR), so novelty is unassessed.

**Expected measurable outcomes.** Energy per km changes of several percent at equal distance, with a
Pareto frontier against trip time; the battery-aware increment over a battery-agnostic eco layer
is expected to be small unless limits are tight, and that increment is the only new scientific
content.

**Fairness.** Compare at **equal trip time and distance** (or report the full energy-time
frontier); give every controller and baseline the same eco layer; separate the eco-layer gain from
any battery-aware increment; keep the original same-cycle comparison unchanged and separate.

---

## 6. Side-by-side

| | A | B | C | D |
|---|---|---|---|---|
| What changes | plant fidelity | controller | objective + ageing | the task |
| New unsourced inputs | cell identity, limits | limits, ε | fade law, λ | μ, constraints |
| Controller-attributable energy headroom (Phase 1) | none by itself | ≲ 0.8 %, assumption-dependent | ≲ 0.25 % in stress indicators | several %, paid in trip time |
| Depends on the unsourced I_max ∝ SoH rule? | defines it | yes | yes | for the battery-aware part, yes |
| Can be validated without a prototype? | only against datasheet/cell data | no | no (fade over many cycles) | partly (physics), not the limits |
| Dominant bias risk | convenient cell choice | tolerance and tuning asymmetry | fade-law and λ choice | stated or hidden time budget |

**Reading.** No option yields a meaningful, defensible controller-attributable improvement on the
present evidence. D has a large effect, but it is an effect of the reference, and it exists
whether or not the battery ages.
