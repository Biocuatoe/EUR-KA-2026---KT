# Numerical validation (rebuild 2026-10-24)

| Check | Command or artefact | Result |
|---|---|---|
| Project test suite (activated environment) | `python -m pytest -q` | 155 passed |
| Project test suite (unactivated Git Bash, first attempt) | same | 16 failed (all in `test_environment.py`; environment variables not set); 139 passed. Kept as a record |
| Rebuild tests | `python -m pytest -q verification/scientific_rebuild_20261024/tests` (`logs/pytest_rebuild_run1.txt`) | 9 passed |
| Limits off ≡ documented plant | `test_derivatives_equal_base_plant_when_limits_disabled` | derivatives bit-identical |
| Limits off ≡ documented simulator | `test_simulate_reproduces_eureka_simulate_without_limits` | final states within 1e-9; RMSE within 1e-12 relative |
| Closed-form battery limits | `test_battery_limits_match_brute_force` | within 1e-4 of a brute-force search |
| Energy closure with limits active | test plus grid | ≤ 1e-6 in the test; ≤ 5.9e-10 across the 336-run grid |
| Reproduction of the saved pre-registered runs | `results/sanity_checks.csv` | 16/16 identical (relative 0.0) |
| Identities S ≡ F at SoH 1.0; BCS ≡ BCN at SoH 1.0 | `results/sanity_checks.csv` | 40/40 exact |
| Timestep convergence | `results/convergence.csv` | UDDS: ΔE changes 2.9e-8 and −2.8e-9 pp; E relative change ≤ 2.8e-10. US06: 4.1e-8 and −1.2e-8 pp; ≤ 5.5e-10. All 4 steps pass (< 0.01 pp, < 1e-4) |
| Recorded gains vs recomputation | `results/analysis_run_accounting.csv` | 0 mismatches |
| Source hashes recorded at run start vs files now | same | 0 mismatches |
| Independent implementation | `verification/controller-crosscheck-report.md` | class A only (OpenModelica, 554/570 checks, S1 distance FAIL unresolved); none for the battery window |
| Stochastic repetition | — | not applicable (deterministic model, no noise in R1) |

**Scope.** These checks establish implementation correctness and numerical accuracy only.
They do not establish that the model represents a real vehicle or battery.
