# Reproducibility and limitation statement

**Date:** 2026-10-25. **Scope:** the research-recovery work in this directory, and the records it
builds on. **Independence:** all of this was produced by one AI assistant working in the author's
repository. No person has replicated or reviewed it. AI-generated reports are not independent
verification.

## 1. What can be reproduced, and how

| Item | Command (activated environment: `. scripts\activate.ps1`) | Inputs | Outputs | Check |
|---|---|---|---|---|
| R1 (348 runs) | unchanged; see `../README.md` | frozen R1 protocol | `../runs/`, `../results/` | not rerun here; R1 manifests carry file hashes |
| Energy ledger | `python energy_ledger.py`, `python summarise_ledger.py` in `../recovery_feasibility_20261025/` | R1 saved final states | `ledger_*.csv` | closure 2.2e-7 Wh |
| Literature search | `python -I lit/search.py` (appends; rerun gives today's index state, not the 2026-10-25 state) | public APIs | `lit/raw/*.json` (verbatim 2026-10-25 responses), `lit/search_*.csv` | raw responses preserved |
| Abstracts, log, bibliography | `python -I lit/abstracts.py`, `lit/build_log.py`, `lit/make_bib.py` | `lit/raw/abstracts.json` | `literature_search_log.csv`, `references.bib` | matrix CSV validated by `build_log.py` |
| P2 pilot | `python -X utf8 pilot/smoke_test.py`, then `pilot/run_pilot.py tune`, `eval`, `conv` (2026-10-25: exit 0 each; 257/257 runs valid), then `pilot/verify_pilot.py` (integrity; no problems), `pilot/analyze_pilot.py` (pre-registered rules) and `pilot/posthoc_checks.py` (post-hoc, labelled) | `pilot_protocol.md` (frozen SHA-256 `ebebc157…2b5a`), R1 plant code, EPA cycle CSVs | `pilot/out/{tune,eval,conv,analysis}/` with manifests | manifests record protocol hash, every source-file hash, Python and package versions; each stage refuses to overwrite an existing output directory |

**Determinism.** The plant, controllers and tuning are deterministic. The LHS uses a fixed seed
(20261025). Repeating a stage on the same machine and environment should give identical numbers.
Cross-platform bit-identity is not claimed.

**External state that can drift.** Search-engine and API indexes change over time. The verbatim
responses are therefore saved in `lit/raw/`.

## 2. Labels used for every result

| Label | Meaning | Examples here |
|---|---|---|
| Analytical derivation | follows from the model equations | for a fixed trajectory every energy-ledger line is fixed; the controller acts only through the trajectory and the brake split |
| Numerical verification | the equations are solved correctly | energy closure, dt halving, R1 reproduction by the pilot code (relative difference 0.0) |
| Simulation result | output of the verified model | R1 ΔE range; pilot contrasts |
| Source-grounded parameterisation | value traced to a cited source read at the stated access level | R0 ratio 1.7 from Pan2023 (FT, table layout to be confirmed); 2C pulse from retailer summaries (SEC, weaker) |
| Assumed scenario | value chosen by the project to bracket uncertainty | 3C/1C limits; SoH-scaled limits (E4); voltage window ratios |
| Unverified physical behaviour | asserted about real hardware without evidence | anything about the thesis's CATL cell, the real micro-EV, or capacity fade |

**No result in this directory is real-vehicle or real-battery validation.**

## 3. Limitations

**Model.**
- One hypothetical vehicle; thesis parameters without primary sources (20 of 39), plus project
  assumptions (17 of 39).
- Flat road; constant OCV; constant motor/inverter efficiency (no efficiency map); no thermal
  state; no auxiliaries.
- 1-RC battery, R0/R1 linear in (1 − SoH); oracle SoH, constant within a run.
- No capacity-fade model.

**Battery limits.**
- Bracketed, not measured. The thesis cell is unidentified.
- The only located 100 Ah LFP ratings are retailer summaries (SEC). The manufacturer specification
  was blocked (HTTP 403).
- The proportionality of current limits to SoH has no source and appears only in an exploratory
  arm.

**Pilot design.**
- Tuning used S1 only. In the training scenarios the battery *drive* limit never bound (0 % of
  steps; only the charge limit acted, through friction), so the supervisory layer could not
  influence tuning. F0 and F1 therefore selected the same gain, as did S0 and S1. This was a
  property of the pre-registered design and was not changed after it was seen.
- The fixed-gain search box excluded the most aggressive gains that the scheduled family reached
  through γ_v. The selected fixed gain lay at the box edge (found post hoc). This explains the
  scheduled branch's small tracking edge at SoH 0.8 and changes no energy verdict.
- Pilot runs saved metrics, not final state vectors, and did not record terminal voltage. The
  voltage window cannot bind in these scenarios (R0 ≤ 8.5 mΩ against a threshold of ≥ 16.4 mΩ).
- Two held-out cycles (S2, UDDS). US06 was excluded because it exceeds motor capability. UDDS does
  not meet the tracking requirement for any branch, and UDDS E3/E4 are incomplete cycles.
- Deterministic runs: no confidence intervals or p-values.

**Literature.**
- No Scopus, Web of Science or IEEE Xplore access. Abstracts only for this session's additions.
- Several full texts were blocked. One screener.
- "Not found" ≠ "does not exist".

**Independence.** The same assistant designed the model, the protocol, the pilot and the analysis.
The OpenModelica cross-check covers R1 class A only. No second implementation of the battery
window or the supervisory layer exists.

## 4. What would strengthen the evidence

1. Cell part number and manufacturer datasheet (owner item OC-1). This would turn assumed
   scenarios into a source-grounded reference vehicle.
2. A second implementation (e.g. Modelica) of the battery window and the supervisory layer.
3. Human replication of the pilot from the commands in §1.
4. A database literature search (IEEE Xplore, Scopus) before any novelty statement.
5. Full-text reading of Naumann2020, Prada2013 and Pan2023 Table 2 before using their values.
