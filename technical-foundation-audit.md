# Technical foundation audit: EV longitudinal dynamics and fixed vs SoH-scheduled LQR

- **Date:** 2026-10-23
- **Auditor:** Claude (AI assistant acting as independent technical reviewer), working read-only in the project.
- **Companion file:** `technical-claim-matrix.csv`, with 58 claims, exact locations, evidence paths and verdicts.

This audit does not prove the thesis or the evaluation correct. It separates what is
mathematically sound, what holds only under stated assumptions, what is unverified, and
what is wrong. Nothing here establishes physical vehicle performance.

---

## 0. Audit record (pre-investigation)

| Item | Value |
|---|---|
| Working directory = Git root | `D:\EURÉKA 2026 - KT` (`git rev-parse --show-toplevel` → `D:/EURÉKA 2026 - KT`) |
| Branch / commit | `master` / `f264eca354d67dcdf786063ca36ae246466217d2` |
| Git status at start and after every check | clean (no tracked or untracked changes, before these two files) |
| Remotes | none configured (`git remote -v` empty) |
| Final thesis | `EURÉKA 2026 - KT.docx` (project root). Identical copy `data/raw/report/EUREKA-2026-KT.docx` (both SHA-256 `01363a06…eddff8c`). Text read via `data/processed/report/report.md` (pandoc 3.11 conversion, `data/processed/report/MANIFEST.json`). |
| Final research documents | `docs/evaluation-report.md`, `docs/model.md`, `protocol/preregistration.md`, `docs/research-contribution-review.md`, `docs/optional-components.md`, `docs/lineage.md`, `evidence/claim_registry.yaml`, `evidence/evidence_matrix.{yaml,csv,json}`, `evidence/artifact_hashes.json` |
| Test command | `python -m pytest` (README); gate: `python scripts/run_gate.py` |
| Experiment commands | `python scripts/run_experiment.py {primary,gamma_sweep,fixed_family,robustness}`; analysis `scripts/analyze.py`; full chain `scripts/reproduce_all.ps1` (**not run**) |
| Environment | CPython 3.14.7 (`.venv`), numpy 2.5.4, scipy 1.18.1, python-control 0.10.2, sympy 1.14.0, pint 0.26.2, pydantic 2.14.1, hypothesis 6.170.8, pytest 9.1.1 |
| Installs | none |
| External browsing | available; used for 5 sources (section 8) |

---

## 1. Executive assessment

1. **The project's replacement model and controller (`docs/model.md`, `src/eureka/`) are
   mathematically and dimensionally sound within their stated assumptions.** Independent
   re-derivations and an independent DARE implementation reproduce the force balance,
   operating points, linearisation, controllability, LQR gains, closed-loop stability and
   saved results. The agreement ranges from machine precision (e.g. a 5.2e-12 relative
   difference in the gains) to exact (0.0 difference in ΔE).
2. **The thesis's core technical foundations do not hold.** Eq. 4.3 is dimensionally
   invalid however its garbled layout is read. The drivetrain-efficiency treatment
   (Eq. 2.23-2.24) puts motor and inverter losses on the torque path. The Lyapunov proof
   (Eq. 4.43-4.50) is a continuous-time argument for a discrete controller and does not
   derive its own bound. The MRAC stability conclusion misuses LaSalle's principle. The
   claimed gain trend (Table 33) is the opposite of what the stated weight laws produce.
3. **The pre-registered null result is reproduced and is structurally explained.** On the
   documented model, the SoH-scheduled LQR changes energy per km by +0.0030 % (S1,
   SoH 0.8). A new deduction (PM-23) shows that, under the model's assumptions,
   identical speed trajectories imply identical energy. The closed-loop runs sit only
   0.14-0.20 % above ideal-tracking energy. A controller that tracks the reference can
   therefore not produce a 12.5 % saving in this model.
4. **New positive result (bounded to the linear design model):** one common quadratic
   Lyapunov function certifies stability of the scheduled closed loop under *arbitrarily
   fast* SoH variation in [0.5, 1] for all tested γ. This replaces the thesis's defective
   proof with a correct, narrower statement.
5. **Corrections needed in the project's own documents (none invalidates a conclusion):**
   - N04's "resistive losses bound the saving" logic is not a valid bound.
   - "Never activated the traction limit or friction brake" is false for the S-D runs,
     which had momentary, noise-driven activations.
   - The energy-decomposition sentence omits shaft friction (3.1 %).
   - Exact measurement of the torque state is an unlisted assumption.
   - The implemented integrator differs (negligibly) from the designed one.
   - The 0.1 % closure threshold is only a gross-error screen.
6. **What remains unestablished:** physical validity (no measured vehicle, synthetic
   profiles, unsourced parameters), stability of the nonlinear saturated plant beyond
   simulation, the S-D noise mechanism, and any novelty claim (no literature review).

**Highest-priority corrective task:** rewrite the thesis's technical core (Ch. 2 Eq.
2.23-2.24 and Ch. 3 Eq. 4.1-4.4, 4.37-4.50, Table 33, §3.7) around the documented model,
the trajectory-determinism argument (PM-23) and the discrete-time stability result (PM-13),
and withdraw the contradicted equations. Without that, the thesis's methodology chapter
contradicts its own (corrected) results.

---

## 2. File inventory and research scope

Files inspected (all paths relative to the project root). Caches, `.venv/`, `tools/`,
`cache/` and `logs/` were not inspected.

| Path | Technical role |
|---|---|
| `EURÉKA 2026 - KT.docx` | Original thesis (read-only; hash checked) |
| `data/processed/report/report.md`, `MANIFEST.json` | Text conversion used for line references |
| `docs/model.md` | Plant and design-model equations, assumptions table |
| `configs/parameters.yaml` | 33 parameters with units, provenance, ranges |
| `configs/experiments.yaml`, `configs/cycles/profiles.yaml` | Experiment design; synthetic speed profiles |
| `protocol/preregistration.md` | Hypotheses, metrics, decision rules (locked) |
| `docs/evaluation-report.md` | Reported results |
| `docs/research-contribution-review.md` (headings and §9), `docs/optional-components.md` (opening) | Contribution/limitation framing; excluded components |
| `docs/lineage.md`, `evidence/artifact_hashes.json` | Provenance chain and hashes |
| `evidence/claim_registry.yaml` (structure, C01-C40 locations), `evidence/evidence_matrix.csv` | Existing claim register (40 + 4 rows) |
| `src/eureka/plant.py` | Nonlinear plant, RK4, energy closure |
| `src/eureka/controllers.py` | Design model, ZOH, Bryson weights, schedule, DARE |
| `src/eureka/simulate.py` | Closed-loop simulation, anti-windup |
| `src/eureka/metrics.py`, `scripts/analyze.py`, `scripts/energy_breakdown.py` (key lines) | Validity rules, metrics, preregistered analyses |
| `src/eureka/params.py`, `cycles.py`, `experiment.py`, `lineage.py`, `__init__.py` | Parameter loading, profiles, run specs, provenance |
| `tests/conftest.py`, `test_plant.py`, `test_controllers.py`, `test_pipeline.py`, `test_cycles_params.py`; side-effect lines of `test_environment.py` | Verification suite |
| `artifacts/raw/{primary/S1,primary/S2,gamma_sweep/S1,fixed_family/S1,robustness/draws-0000-0049}/{manifest.json,timeseries.npz}` | Saved raw outputs (read only) |
| `artifacts/tables/primary_pairs.csv`, `energy_breakdown.csv` | Saved derived tables |
| `pyproject.toml`, `project.env`, `README.md` | Environment and commands |

**Scope actually present in the project:** point-mass longitudinal dynamics, first-order
torque actuator with torque/power limits, friction brake, 1-RC battery with SoH-dependent
R0/R1, discrete LQR with integral action (fixed and SoH-weight-scheduled), synthetic
profiles, energy accounting. **Not present and not evaluated as implemented:** grade,
efficiency maps, DC-link voltage limits, ageing model, EKF, MRAC, NSGA-II, hardware.

---

## 3. Verdict definitions

| Verdict | Meaning |
|---|---|
| MATHEMATICALLY_VERIFIED_WITHIN_ASSUMPTIONS | Re-derived independently (analytically or with an independent numerical method), and true under the listed assumptions |
| IMPLEMENTATION_VERIFIED_FOR_TESTED_CASES | The code does what the documentation states, confirmed by an independent check on the cases examined. Says nothing about physical truth |
| SIMULATION_SUPPORTED | A model-computed result, independently recomputed from saved raw outputs. Valid for the model, profiles and parameters used |
| CONDITIONALLY_VALID | Correct only with an explicit qualification, or correct with a defect that does not change the conclusion |
| CONTRADICTED | Shown false by derivation, arithmetic or reproducible evidence |
| NOT_VERIFIED | Could not be checked (missing data or parameters), or the supporting argument is defective |
| REQUIRES_EXTERNAL_EVIDENCE | Needs measurements, datasheets, literature or hardware outside the project |
| REQUIRES_HUMAN_EXPERT_REVIEW | A judgement a qualified reviewer should confirm |

Passing unit tests never by itself earned a VERIFIED verdict. Each verified claim has an
independent check (IC-xx below), and the CSV states how independent that check is.

---

## 4. Technical claims reviewed

The CSV lists every claim. Summary by group:

| Group | IDs | Verdicts |
|---|---|---|
| Thesis vehicle physics | TF-01 to TF-05 | 1 verified, 1 conditional, 3 contradicted |
| Thesis state space, discretisation, LQR | TF-06 to TF-12 | 1 verified, 2 conditional, 3 contradicted, 1 not verified |
| Thesis battery and SoH | TF-13 to TF-15 | 1 not verified, 1 external evidence, 1 contradicted |
| Thesis adaptive law and stability | TF-16 to TF-24 | 3 conditional, 4 contradicted, 1 not verified, 1 expert review |
| Thesis results and applicability | TF-25 to TF-30 | 3 contradicted, 3 external evidence |
| Project model and controller | PM-01 to PM-13 | 7 verified, 3 implementation-verified, 3 conditional |
| Project experimental evidence | PM-14 to PM-23 | 4 simulation-supported, 1 implementation-verified, 1 verified (new deduction), 3 conditional, 1 not verified |
| Project provenance and software | PM-24 to PM-28 | 3 implementation-verified, 1 conditional, 1 external evidence |

Totals: 14 CONTRADICTED, 13 CONDITIONALLY_VALID, 10 MATHEMATICALLY_VERIFIED, 7
IMPLEMENTATION_VERIFIED, 4 SIMULATION_SUPPORTED, 4 NOT_VERIFIED, 5
REQUIRES_EXTERNAL_EVIDENCE, 1 REQUIRES_HUMAN_EXPERT_REVIEW.

---

## 5. Mathematical and physical verification

All checks below were executed in this audit. Scripts were run from the session scratchpad
(outside the project), with parameter values read directly from `configs/parameters.yaml`
by PyYAML rather than through `eureka.params`. `eureka` was imported only to compare
against.

### 5.1 Vehicle dynamics (IC-01, IC-02, IC-03)

- **Force balance and signs.** The plant has M_eff dv/dt = F_w − F_rr − F_aero − F_fb,
  with resistances opposing positive motion. This is the same form as the Linköping
  University TSFS02 lecture (m dV/dt = F − R_r − R_g − R_a, with R_a = ρ/2 C_D A_f V_r²);
  the project has no grade term (R_g = 0).
- **Dimensions (independent Pint expressions, IC-03).** Every project term is
  dimensionally consistent: traction, drag, shaft friction, linearisation coefficients a
  [1/s] and b·T [m/s²], and battery current [A]. Negative control: F_aero declared as
  watts is rejected.
- **Limiting cases.**
  - *Constant-speed equilibrium:* hand-computed steady torques are 3.74, 4.61 and
    7.32 N·m at 20, 30 and 50 km/h. The project's derivative gives |dv/dt| ≤ 2.4e-17 m/s²
    at those points.
  - *Zero speed:* the holding brake blocks reversing, and tanh(v/0.05) removes
    rolling resistance continuously.
  - *Zero acceleration:* reduces to the equilibrium case above.
- **Effective mass.** M_eff = 850 + 0.05·6.5²/0.28² = 876.945 kg. Strictly, rotor-inertia
  torque passes through the gearbox loss, so the reflected inertia should carry
  η_g^{±1}. The difference is about 0.8 kg (0.09 %), and the energy closure is consistent
  with the model's own definition (PM-05, TF-05).
- **Actuator limits.** Base speed is ω = 18000/85 = 211.76 rad/s, i.e. 9.122 m/s
  (32.84 km/h). Along the *reference* trajectories (independent inverse dynamics, IC-02),
  the minimum torque headroom is 21.2 N·m in traction and 31.5 N·m in regeneration on
  S1, and 57.5 / 62.1 N·m on S2. The references never require saturation or friction
  braking.
- **Thesis Eq. 4.3 (TF-07).** The coefficient Gη/(M r_w) has units 1/(kg·m). Multiplied
  by *any* state in Eq. 4.1 (v [m/s], i_batt [A], ω_m [rad/s]) it does not give m/s²;
  only a torque would. The verdict therefore does not depend on how the garbled matrix
  is read. The other six terms (R/L, K_e/L, K_t/J, B_m/J) are consistent. Additionally:
  - v and ω_m are kinematically tied under the thesis's own rigid, no-slip assumption,
    so they are not independent states (TF-06);
  - the "battery current" equation is a DC-motor armature equation.
- **Thesis Eq. 2.24 (TF-02).** Motor and inverter efficiencies act on the
  electrical-to-mechanical power conversion, not on the torque-to-force conversion. Using
  η_dt = 0.848 in F_trac under-states traction by 12.6 % relative to the gear and bearing
  efficiency of 0.970. The thesis's η_dt = 0.88 (Table 8) is also inconsistent with the
  product of its own components, 0.848 (TF-03).

### 5.2 State-space formulation (IC-04, IC-05)

- **Design model.** x = [e, T, z], u = T_ref, with
  A = [[−a, b, 0], [0, −1/τ, 0], [1, 0, 0]] and B = [0, 1/τ, 0]ᵀ. The dimensions agree
  (3×3, 3×1). Units: e [m/s], T [N·m], z [m]; a [1/s], b [m/(s²·N·m)].
- **Symbolic Jacobian (SymPy) of the nonlinear force equation at v0 = 8.333 m/s.**
  - a = 0.0095596 s⁻¹ and b = 0.025683; relative errors against the project are
    1.8e-16 and 1.4e-16.
  - In the regeneration branch, b is 6.2 % larger (1/η_g²).
  - The rolling-resistance tanh term contributes 0 at v0, but up to 0.64 s⁻¹ at
    0.05 m/s. Both effects are covered by the frozen-speed sweep (5.3).
- **Continuous-to-discrete.** An independent Van Loan exponential matches the project's
  ZOH. The thesis's truncated series (Eq. 4.9-4.10) has a remainder of about 0.26 % at
  ‖A·Ts‖ = 0.5. The project uses the exact exponential (TF-09).
- **Validity conditions.** The linearisation holds near cruise at v0 in the motoring
  branch. The reference acceleration and the constant load enter as disturbances
  rejected by integral action. There is no feedforward, so ramps produce a bounded lag:
  observed max |e| is 0.399 m/s on S1 and 0.256 m/s on S2.
- **Unlisted assumption (PM-08).** The controller feeds back the *true* delivered torque
  (`simulate.py:56`). Torque measurement or estimation error is not modelled, and the
  assumption is not in the `docs/model.md` §3 table.

### 5.3 LQR (IC-05, IC-06, IC-07, IC-16)

- **Objective and weights.** J = Σ xᵀQx + uᵀRu, with Q0 = diag(1/0.5², 1/85², 1/0.5²)
  in units (m/s)⁻², (N·m)⁻², m⁻², and R0 = 1/85² (N·m)⁻². These are correct Bryson
  normalisations. The thesis's R = 1 implies u_max = 1 N·m against an 85 N·m limit
  (TF-24).
- **Existence conditions.**
  - Controllability holds in closed form: det[B, AB, A²B] = −b²/τ³ ≠ 0 for every b,
    τ > 0.
  - The PBH rank is 3 at every eigenvalue of A_d.
  - The continuous eigenvalues (−a, −50, 0) are real and distinct, so ZOH sampling
    cannot lose controllability.
  - Q > 0 gives detectability, and R > 0. A stabilising DARE solution therefore exists
    at every SoH and γ ≥ 0.
- **Gains.** My own symplectic-pencil DARE gives K_fixed = [196.035, 0.35068, 150.855].
  The maximum relative difference from the project is 5.2e-12 and the Riccati residual
  is 8e-14. The gains in the run manifests match. This check is *partially* independent:
  it uses the same deflating-subspace principle as SciPy's QZ solver but a separate
  implementation, without balancing. The project's own value-iteration test is the
  algorithmically independent check, and it passes.
- **Closed-loop stability and margins (linear design model only).**
  - Nominal spectral radius is 0.9894.
  - The upper gain margin (by bisection) is 11.6× for the fixed gain. The lower limit is
    ≈ 0⁺ because the integrator makes the open loop marginal.
  - The minimum return difference of 0.914 guarantees gain in [0.52, 11.6] and phase
    ≥ 54°. The crossover phase margin is 94°.
  - Negative control: scaling K to 1.05 × GM gives ρ = 1.085, which is detected.
  - Frozen linearisations at 0-16 m/s, in both efficiency branches and including the
    tanh term near standstill, give worst ρ = 0.9938 (fixed) and 0.9960 (R × 10).
- **Design versus implementation (PM-12).** The design discretises ∫e exactly. The code
  uses z ← z + Ts·e (forward Euler, `simulate.py:77`). The implemented loop has
  ρ = 0.989310 against 0.989402 for the design, so the difference is negligible but
  undocumented. Conditional anti-windup lies outside LQR optimality.
- **What this does not show.** A numerically computed gain with |λ| < 1 is a property of
  the linear, unconstrained, frozen model. Stability of the nonlinear plant with
  saturation, piecewise efficiency and the holding brake is supported only by stable
  simulation traces on the tested profiles.

### 5.4 SoH-scheduled controller (IC-06, IC-08, IC-15)

- **What changes with SoH.** Only the LQR weights change: Q₂₂ is multiplied by
  α_v = 1/(1 + γ_v(1−SoH)) and R by (1 + γ_u(1−SoH)). The design model, and the plant
  dynamics, are independent of SoH.
- **Evidence that the dynamics are SoH-independent.** Fixed-gain speed trajectories are
  bit-identical at SoH 1.0 and 0.7 (maximum difference 0.0, IC-10).
- **Effect of the schedule.** With γ = 1 the gains *decrease* as SoH falls:
  - K_e: 196.04 → 189.91 → 184.30 → 179.17
  - K_z: 150.85 → 146.01 → 141.48 → 137.27
  - This contradicts the thesis claim that the integral gain increases (TF-22).
- **Specification.** The law is continuous and well defined for γ ≥ 0. The thesis gives
  no γ values, and it describes both an online DARE and a lookup table (TF-17). The SoH
  measurement is assumed exact, the best case for the schedule.
- **Thesis stability proof (TF-18).** It has four defects:
  1. It is a continuous-time Hurwitz argument for a 10 ms DARE controller.
  2. Condition 3 essentially assumes the conclusion and omits uniform bounds on P(t).
  3. The bound on K̇ in Eq. 4.50 does not follow from the preceding bound on Ṗ.
  4. It applies to the invalid Eq. 4.3 model.
- **Independent replacement, discrete time, on the linear design model:**
  - **Slow-variation bound (IC-08).** The DARE identity
    A_clᵀPA_cl − P = −(Q + KᵀRK) holds (residual 2e-13). It gives the sufficient
    condition |ΔSoH per step| ≤ 3.15e-10, only about 5× above a fast realistic drift of
    20 % per year. The bound is very conservative.
  - **Common quadratic Lyapunov function (IC-15).** P(SoH = 1) satisfies
    A_cl(s)ᵀP A_cl(s) − P < 0 for every s on a 1001-point grid over [0.5, 1], for
    γ pairs (1,1), (0,5), (5,0), (5,5), (1,5) and (5,1). The maximum eigenvalue is
    −1.26e-4 to −1.39e-4 (relative −2.2e-7 to −2.4e-7, far above floating-point error).
    So the linear closed loop is exponentially stable even under *arbitrarily fast* SoH
    changes within that range. Negative control: the identity matrix as candidate fails,
    as it should.
  - **Scope.** This is a numerical certificate on a grid, not a proof over the continuum,
    and it covers neither saturation nor the nonlinear plant. Because SoH is constant
    within each run, every simulated run is in any case a time-invariant closed loop.
- **Other adaptive-control statements in the thesis.**
  - "Gain scheduling guarantees stability at each operating point" (TF-19) is
    contradicted as a general statement. Frozen-point stability needs a slow-variation
    or common-Lyapunov argument, the caveat stated in the abstract of Shamma & Athans
    (1992).
  - The MRAC argument (TF-21) is contradicted. V̇ = −eᵀQe gives e → 0 via Barbalat, but
    not K̃ → 0, which requires persistent excitation; LaSalle does not apply directly to
    the non-autonomous loop; and σ-modification removes V̇ ≤ −eᵀQe.

### 5.5 Power and energy (IC-10, IC-11)

- **Power chain.** P_m = T·ω is mechanical power at the rotor. P_e = P_m/η_mi when
  motoring and P_m·η_mi when regenerating, on the DC side. The battery is a 1-RC
  Thevenin model with E_chem = ∫V_oc·I dt. Each loss term is non-negative in both power
  directions (PM-02).
- **Integration.** RK4 runs at 1 ms with the controller held at 10 ms.
- **Energy closure.** Recomputed independently from the saved end states, closure is at
  most 4.4e-10 (primary), 3.4e-10 (S-C) and 5.4e-10 (S-D).
  - Negative control: a 1 % error in the aero loss accumulator yields closure as low as
    3.65e-4, *inside* the 1e-3 exclusion threshold.
  - The threshold is therefore a gross-error screen. The accounting is supported by the
    achieved 1e-10 closure (PM-05).
- **Percentage formula.** ΔE = (E_s − E_f)/E_f × 100, with E in Wh/km and the fixed
  controller as denominator (`analyze.py:84`). It matches the preregistration. On a
  total-Wh basis the S1/0.8 value is +0.00314 % instead of +0.00301 %, because the
  trajectories differ by 2.8 mm. The decision is unaffected.
- **Trajectory determinism (PM-23, new).** The argument:
  1. Given v(t), the term M_eff·v̇ + loads fixes F_w.
  2. F_w is strictly increasing in shaft torque, so the delivered torque T(t) is unique.
  3. P_m, P_e, I(t), V1(t) and E_chem then follow uniquely.

  So, with constant efficiencies and no friction braking, equal speed trajectories imply
  equal energy. Any energy difference between controllers can only come from tracking
  differences.
- **Independent ideal-tracking reference (IC-11).** An independently coded inverse
  dynamics along the reference, including the RC branch, gives 49.714 Wh/km (S1,
  SoH 1.0), 49.803 (S1, 0.8), 36.951 (S2, 1.0) and 36.990 (S2, 0.8). The simulated
  closed-loop runs are 0.14-0.20 % above these values, and the two controllers differ by
  ≤ 0.005 %. The energy shares agree with `artifacts/tables/energy_breakdown.csv`: road
  68.2-68.4 %, motor/inverter 22.0 %, battery resistive 1.1-2.1 %.
- **Corrections to project wording.**
  - N04's claim that resistive losses bound what any controller can save does not follow
    (PM-20). With the same trajectory there is nothing to shape; with a different
    trajectory, road-load and motor losses change too. The 0.14-0.20 % gap to ideal
    tracking is the defensible model-specific statement.
  - The decomposition sentence in `docs/evaluation-report.md` L164-165 omits shaft
    friction (E_visc, 3.1 %) (PM-21).

---

## 6. Implementation and test assessment

**Test run (executed).**

- **Command:** `python -m pytest tests --ignore=tests/test_environment.py`, with the
  temp, Hypothesis and pytest cache directories redirected to the session scratchpad.
- **Result:** 128 passed in 40.4 s, exit 0.
- **Rationale for the redirection and skip:** to leave no files in the project.
- **First attempt:** used `-p no:cacheprovider`, which conflicted with `--strict-config`
  ("Unknown config option: cache_dir", exit 4, no tests ran); fixed by redirecting
  `cache_dir` instead.
- **Skipped:** `tests/test_environment.py` (24 tests). It overwrites
  `artifacts/figures/environment-check/lqr_double_integrator.png` and spawns `pip`. It
  checks the environment, not the science.

**What the tests actually establish:**

| Test file | Purpose | Independence |
|---|---|---|
| `test_plant.py` | Physics properties: hand-formula forces, equilibrium, closed-form coast-down, RK4 vs DOP853, limits, brake, no reversing, loss-rate signs and energy closure (Hypothesis) | Coast-down and hand formulas are independent. DOP853 checks only the integrator (same derivative function). Closure is a model-internal identity |
| `test_controllers.py` | Design model vs finite-difference linearisation; ZOH vs python-control; controllability; DARE vs value iteration and python-control; poles; schedule equations; frozen-time stability; anti-windup | Value iteration is algorithmically independent. The schedule tests restate the equations (regression) |
| `test_pipeline.py` | Run → save → validate → metrics lineage; gate refusal; pairing of robustness draws | Software behaviour |
| `test_cycles_params.py` | Profile arithmetic, parameter schema and unit rejection | Software behaviour plus a simple independent arithmetic case |
| `test_report_checks.py`, `test_claim_registry.py`, `test_evidence_matrix.py` | Arithmetic regressions on thesis numbers; verbatim quote locations; matrix completeness | Regression and documentation integrity, not physics |

**Software-quality findings:**

- No unit, sign or frame errors were found in the plant or controller.
- The thresholds in code match the preregistration: closure 1e-3 (`metrics.py:13`),
  tracking failure 1.5 / 3.0 m/s (`metrics.py:77`), margin 1 % and RMSE ratio 1.10
  (`analyze.py:29`), and H_C at +0.1 % (`analyze.py:150`).
- No configuration value is silently replaced by a default. `load_params` rejects
  missing or extra keys (`params.py:150-160`), and the only code default
  (`soc0 = 0.8`) equals preregistration §7.
- No metric is hard-coded: all are computed from saved arrays.
- **Undocumented design choices:** exact torque measurement (PM-08), and the Euler
  integrator versus the ZOH design (PM-12).
- **Reproducibility risks (minor):**
  - Hypothesis tests are not derandomised.
  - `pyproject.toml` contains an absolute machine path (documented as intentional).
  - Manifests record the historic interpreter path `D:\EUREKA-2026\.venv`, which is
    provenance only.
  - `evidence/artifact_hashes.json` records `dirty: true` at 3640533, while commit
    9aa883e says "from clean commit 3640533". It is probably dirty only because of the
    regenerated files themselves; this was not verified.
- **Artifact integrity.** All 56 recorded SHA-256 hashes match the files on disk (none
  missing or mismatched).

---

## 7. Existing experimental-evidence assessment

All values below were recomputed from `artifacts/raw/*/timeseries.npz` with independent
code. No simulation was rerun.

| Reported item | Recomputed | Status |
|---|---|---|
| H1: S1, SoH 0.8, ΔE +0.0030 %, 49.9025 → 49.9040 Wh/km, RMSE ratio 1.011 | +0.0030138 %, 49.90254 → 49.90405, 1.01102 (difference from saved = 0.0) | Reproduced |
| All 8 primary pairs within ±0.005 %, RMSE up to +2.0 % | max ΔE 0.00518 %, max ratio 1.0201 | Reproduced |
| Sanity control: bit-identical at SoH 1.0 | ΔE = 0.0 and ratio = 1.0 exactly (S1, S2) | Reproduced |
| 296 runs, all valid; worst closure 5.4e-10 | All examined runs finite, feasible, v ≥ 0, closure ≤ 5.4e-10 | Reproduced |
| S-B: ΔE −0.019 to +0.040 % | −0.0189 to +0.0398 %; corr(ΔE, RMSE ratio) 0.9987 | Reproduced |
| S-C: best R×0.1, 49.854 vs 49.881 Wh/km, RMSE 0.038 vs 0.051, H_C holds | 49.8544 vs 49.8810, 0.0379 vs 0.0508; 21/41 feasible; best at the range edge | Reproduced |
| S-D: mean −0.054 %, 95 % CI −0.058 to −0.050, N = 50, 50/50 negative | −0.0539 %, [−0.0580, −0.0501] with an independent bootstrap seed, N rule = 50, 50/50 | Reproduced |
| Energy decomposition | Matches the table; the sentence omits shaft friction 3.1 % | Wording fix |
| "Never activated traction limit or friction brake" | Primary runs: 0 saturation, 0 J brake, peak \|T_ref\|/T_lim = 0.62. S-D: 80/100 runs with momentary saturation (≤ 0.028 % of samples), 9/100 with brake energy (≤ 2.3e-5 of supply) | True for primary only |

**Equivalence of the comparison:**

- Within each pair, the plant, profile, initial state, integrator, limits, brake and
  anti-windup are identical.
- In S-D, parameter overrides, seeds and the noise arrays are identical within each pair
  (verified).
- Both controllers are designed on nominal parameters (`experiment.py:147`), as recorded
  in preregistration deviation 2.
- Exclusion rules are numerical only, as preregistered. No run was excluded.

**Robustness ranges.** All draws lie inside the `configs/parameters.yaml` uncertainty
ranges, which are labelled assumed (report-stated ±% values without sources).

**Known limitations, checked against the artifacts:**

| Limitation | Scope verified |
|---|---|
| Synthetic driving profiles | `profiles.yaml` header and preregistration §6. S1 is 2161.05 m in 324.91 s; S2 is 531.68 m in 213.28 s |
| Constant motor efficiency | `plant.py:117`, a single η_mi = 0.874 (a peak-derived value). Together with PM-23, this is *why* scheduling cannot matter: energy depends on the trajectory only |
| SoH treated as known | `experiment.py:146-150` passes the true SoH to `gain()`. No estimator exists |
| Actuator limits not exercised | Confirmed for the primary runs (21 N·m drive and 31 N·m brake headroom). S-D activations are momentary and noise-driven |
| No vehicle-level physical validation | No measured data anywhere in the project |
| No completed literature review | Confirmed (`docs/research-contribution-review.md` §9) |

**Interpretation boundary.** The results are properties of a hypothetical, parameterised,
flat-road model under synthetic profiles. Nothing extends to real vehicles, grades,
efficiency maps, standard cycles or SoH-estimation error.

---

## 8. External source checks

| Source | What was examined | Claim it supports | Used as |
|---|---|---|---|
| SciPy, `scipy.linalg.solve_discrete_are` documentation, https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.solve_discrete_are.html | Page opened. It states the DARE solved, the QZ symplectic-pencil method (van Dooren 1981, Laub, Benner 2001 for balancing) and conditions | TF-11, and the partial independence of IC-06 | Corroboration |
| Linköping University, TSFS02 *Vehicle Dynamics and Control*, Lecture 2 slides, https://fs.isy.liu.se/courses/TSFS02/Lectures/Lecture2.pdf (no date on the slides read) | Slides 5-7 read: m dV/dt = F − R_r − R_g − R_a; R_a = ρ/2 C_D A_f V_r²; ρ = 1.225 kg/m³ | TF-01, PM-01 | Corroboration |
| J. S. Shamma and M. Athans, "Gain scheduling: potential hazards and possible remedies," *IEEE Control Systems*, 12(3):101-107, June 1992, DOI 10.1109/37.165527 | Bibliographic records and abstract only (University of Illinois experts page, via search). Full text **not** read | TF-19 (the "schedule on a slow variable" caveat) | Corroboration of a deduction; full text needed before citing it in the thesis |
| C. A. Desoer, "Slowly varying system ẋ = A(t)x," *IEEE Trans. Automatic Control*, 14:780-781, 1969 | Bibliographic records only, via citing works (search). Volume/page reported inconsistently across sources. Full text **not** read | The slow-variation framework behind TF-18 and IC-08 | Context only |
| Discrete-time LQR lacks the continuous-time guaranteed margins (NASA technical report 19830011732, via search snippet) | Search snippet only. Shaked (1986) was **not** found | PM-11 (why the margins were computed rather than assumed) | Context only; IC-07 computes the margins directly |

**Not examined, though needed for citation:** Ioannou & Sun, *Robust Adaptive Control*
(1996), for TF-20 and TF-21; Guzzella & Sciarretta, *Vehicle Propulsion Systems*, for the
efficiency-direction convention. Every critical conclusion in this audit rests on
derivations and computations run here, not on search snippets.

**Provenance categories used in this report:**

- *Project facts:* sections 2, 6 and 7.
- *Independent deductions:* PM-23, TF-06/07/18/21.
- *Checked against external sources:* TF-01 and TF-11.
- *Unverified assumptions:* all report_unverified and assumed parameters; the DC-link
  decoupling.
- *Hypotheses needing new experiments:* PM-19 (noise mechanism); behaviour under
  saturation.

---

## 9. Contradictions and unresolved assumptions

**Contradicted (thesis):**

- TF-02: efficiency placement.
- TF-03, TF-04: parameter inconsistencies.
- TF-06, TF-07: state choice and Eq. 4.3.
- TF-10: sampling rationale.
- TF-15: ΔA mechanism.
- TF-19: gain-scheduling guarantee.
- TF-21: MRAC convergence.
- TF-22: gain trend.
- TF-24: Bryson weights.
- TF-25, TF-26, TF-28: results and statistics.

**Internal wording issues in project documents (none changes a conclusion):**

- PM-20: N04 bound logic.
- PM-21: decomposition omits shaft friction.
- PM-22: "never activated".
- PM-27: dirty flag in the hash record.

**Unresolved assumptions that could change conclusions:**

1. **Constant efficiency.** It makes energy a pure function of the trajectory (PM-23). A
   measured efficiency map could let the controller shape part-load efficiency.
2. **No DC-link voltage limit.** This is the only identified physical mechanism through
   which battery SoH could affect drivetrain dynamics (PM-06, TF-15).
3. **Exact torque measurement** (PM-08).
4. **SoH known exactly.**
5. **Synthetic, non-saturating profiles.** Behaviour under the power limit and friction
   braking is untested.
6. **Unsourced parameters** (PM-24).

---

## 10. Claims supported within explicit assumptions

- **Plant equations and implementation** (PM-01 to PM-04, PM-06): flat road, rigid
  drivetrain, constant efficiencies, constant V_oc.
- **Design-model linearisation, controllability, DARE gains and closed-loop stability,
  with gain and phase margins** (PM-07, PM-09 to PM-11): linear, frozen, unconstrained
  model.
- **Scheduled controller exponentially stable under arbitrary SoH variation in
  [0.5, 1]** (PM-13): linear design model, tested γ grid, numerical certificate.
- **Pre-registered results** (PM-14 to PM-18): reproduced from raw outputs, for the
  documented model only.
- **Equal trajectories imply equal energy** (PM-23): constant efficiencies, no friction
  braking.

## 11. Claims not supported by current evidence

- **Any energy saving or capacity-fade reduction from SoH scheduling** (TF-25, TF-26).
- **Thesis state-space model, controllability claim, stability proof, gain table,
  gain-scheduling guarantee and MRAC convergence** (TF-06 to TF-08, TF-18, TF-19, TF-21,
  TF-22).
- **Validation, safety, hardware and novelty claims** (TF-27, TF-29, TF-30).
- **The S-D noise explanation** (PM-19): hypothesis only.
- **Stability of the nonlinear saturated closed loop**: simulation evidence only.

---

## 12. Recommended independent checks (not run; would need approval where noted)

1. **Noise mechanism (PM-19).** Run paired noise-on and noise-off simulations at the S-D
   draws. This is a new simulation batch, so it needs approval.
2. **Saturating profile.** Use a profile that exercises the power limit and friction
   brake, to test anti-windup and the PM-23 assumptions. This needs a deviation entry
   and approval.
3. **DC-link coupling.** Add a voltage-dependent torque envelope and repeat the
   comparison, to test whether SoH can matter at all. This needs approval.
4. **Common-Lyapunov proof over the continuum.** Use an LMI over a polytopic SoH
   parameterisation; this needs a solver not installed here.
5. **Hand-check of the closure exclusion rule.** A tighter, per-term closure tolerance
   could be added as a reporting diagnostic.
6. **Primary sources.** Read the full texts of Shamma & Athans, Desoer, Ioannou & Sun and
   a vehicle-propulsion text before citing them.

## 13. Prioritised remediation plan

| Priority | Task | Affects |
|---|---|---|
| 1 | Rewrite the thesis's technical core: withdraw Eq. 4.1-4.4, 4.37-4.38, 4.43-4.50, §3.7.6 and Table 33; correct Eq. 2.23-2.24; present `docs/model.md`, PM-13 and PM-23 | TF-02, TF-06/07, TF-15, TF-18, TF-21, TF-22 |
| 2 | Correct project wording: N04 (use PM-23 and the 0.14-0.20 % gap); "never activated" → "not in the primary runs"; add shaft friction to the decomposition; add "torque measured exactly" to `docs/model.md` §3; document the Euler integrator | PM-08, PM-12, PM-20, PM-21, PM-22 |
| 3 | Source or label every parameter, starting with mass, C_d·A, C_rr, η_mi (a map) and R0 | PM-24, TF-03/04, TF-14 |
| 4 | Literature review for novelty and for each cited theorem | TF-30, section 8 |
| 5 | With approval: the experiments in section 12, items 1-3, as dated deviations, without overwriting raw outputs | PM-19, unresolved assumptions 1-5 |
| 6 | Reproducibility hygiene: derandomise Hypothesis for the gate; clarify the dirty flag; keep this audit's check scripts in the project if desired (they are currently outside it) | PM-27, PM-28 |

---

## Appendix A: independent checks executed

| ID | Check | Result |
|---|---|---|
| IC-01 | Hand operating points vs plant derivative | M_eff 876.945 kg; v_base 32.84 km/h; residual ≤ 2.4e-17 |
| IC-02 | Actuator headroom along references (inverse dynamics) | S1 drive 21.2 N·m, regen 31.5 N·m; S2 57.5 / 62.1 N·m |
| IC-03 | Pint dimensional analysis (project and thesis) | Project all consistent; thesis traction term fails for all 3 states; negative control rejected |
| IC-04 | SymPy Jacobian vs design model | Relative error ~1e-16; regen b +6.2 % |
| IC-05 | Controllability closed form, PBH, ZOH | det = −b²/τ³; ranks 3; ZOH matches |
| IC-06 | Symplectic-pencil DARE vs project and manifests | ≤ 5.2e-12; residual ≤ 8e-14 |
| IC-07 | Margins, gain bisection, frozen-speed sweep, negative control | GM 11.6×, disk [0.52, 11.6] / 54°; worst ρ 0.9938; control ρ 1.085 |
| IC-08 | Discrete slow-variation bound | 3.15e-10 per step (×5 over 20 %/yr) |
| IC-09 | Thesis arithmetic | η_dt 0.848 ≠ 0.88; 13″/2 = 0.165 m; 10 Hz → 50 ms |
| IC-10 | Primary metrics, closure, actuator use, SoH-invariance from raw | Exact reproduction; closure ≤ 4.4e-10; aero 1 % control 3.65e-4 |
| IC-11 | Inverse-dynamics ideal-tracking energy | S1 49.714 / 49.803 Wh/km; simulated runs +0.14-0.20 % |
| IC-12 | S-C recomputation | H_C holds; best at edge |
| IC-13 | S-B recomputation | −0.019 to +0.040 % |
| IC-14 | S-D recomputation, pairing, ranges | −0.0539 % [−0.0580, −0.0501]; pairs identical |
| IC-15 | Common quadratic Lyapunov function, 6 γ pairs × 1001 SoH | All negative definite; identity control fails |
| IC-16 | Integrator mismatch; peak/RMS current; S-D jitter and limit activation | Δρ < 1e-4; ΔI_peak 0.003 A; jitter ratio 0.927 vs K_e ratio 0.940, per-draw r = 0.10 |

**Where the check scripts are.** `ind_checks_a.py` (IC-01 to IC-09), `ind_checks_b.py`
(IC-10 to IC-15) and `make_matrix.py` are in the session scratchpad, outside the project.
IC-16 and the γ-grid extension of IC-15 ran as inline commands. They are not part of the
project; copying them in would be a separate, approved change.
