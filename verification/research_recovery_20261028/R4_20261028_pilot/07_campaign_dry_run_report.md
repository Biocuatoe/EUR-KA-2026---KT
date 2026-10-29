# R4 H3: campaign dry run and plan validation

**Run:** 2026-10-28 06:14:40 +07:00, `python -I -B code/run_campaign.py --dry-run`.
- Console output: `logs/dry_run_console.txt`.
- Outputs: `outputs/dry_run_20261028_061440/`. File hashes are in `dry_run_outputs_sha256.json` there and in `zz_sha256_manifest_v2.csv`.

**What it did:**
- built and validated the 170-run schedule;
- re-hashed every frozen, upstream and canonical input;
- read the draft amendment;
- checked the campaign configuration and the sensitivity draw table;
- estimated runtime and disk use;
- listed every reason the campaign may not start.

**What it did not do:** run, plan or evaluate anything. No plant, planner, QS or dynamic computation took place, and campaign mode was not invoked.

## 1. Schedule (protocol §10.6): all 18 checks pass

| Check | Result |
|---|---|
| Total 170 runs; per set NOM 12, P3 12, INS 12, CNV 6, SEN 128 (equal to §10.6) | pass |
| Run IDs unique (170); condition IDs unique (85); every condition has exactly B0 and B3 | pass |
| Official ID format `R4H3-<set>-[D<nn>-]<cycle>-<motor>-<limits>-<pstate>-<branch>-dt<1\|0.5>ms` | pass |
| Cycles only S1 and S2; S1 only in INS; S2 in NOM, P3, CNV and SEN | pass |
| P3 only in the P3 set; every profile designed on P1 (D2) | pass |
| 0.5 ms only in CNV; CNV = S2, L-EVE, P1 × M0/M1/M2, each with a 1 ms counterpart in NOM | pass |
| SEN = draws 1–32 × M0/M1, S2, L-EVE, P1; no M2 | pass |
| Smoke-test run IDs (`H3-slice-S1-M0-L-R1-P1-B0-dt1ms`, `…-B3-dt1ms`) not in the schedule (D4) | pass |
| Planner numerics equal §5.2 (2 m, 0.1 m/s, log₁₀λ ∈ [−3, 6], 40 iterations, h = 1 s) | pass |
| No planner job selects a parameter: 82 QS jobs, all "profiles for set …" or "grid convergence" | pass |

**Files written:**
- `schedule_170.csv`, SHA-256 `5d5320a023bec0c7c683a8066f9c7298d262cc554a3b5df03330af77124e7068`: one row per run with sequence, IDs, set, cycle, motor, limits, evaluated and design plant state, branch, dt, trace step, draw, tracked-profile source, gain, held-out or in-sample role, and "counts toward 170".
- `planner_jobs.csv`, SHA-256 `0ccc0f626bf9c5c000f70e6307c70c7133c7eba482c8b7db521b90289d161df3`: 6 S2 P1, 6 S1 P1, 64 sensitivity designs, and 6 S2 fine-grid jobs for §9 grid convergence. None counts toward 170.

## 2. Inputs

| Input | Result |
|---|---|
| Protocol, `r3_lib`, M1 curve and 9 upstream files | all hashes match |
| Canonical cycle inputs (7 files) | match; `task.load_task()` reproduces S1 and S2 bit for bit |
| `config/campaign_config_v1_DRAFT.json` (SHA-256 `9f3043f023391ca55fb3c4b7f6849abd00dd756f60453c5a935264c74d75ad13`) | current: it rebuilds identically. The schedule hash inside it equals the dry-run `schedule_170.csv` |
| `config/sensitivity_draws_v1.csv` (SHA-256 `d1e42f31c5feb69c139b78fcdeb8d066be4aec8748708c539a210d24c008c703`) | regenerates identically from seed 20261028 |
| Draft amendment (SHA-256 at dry run `f4ffc4b752e93dc3eedd6efc8b1bb03f490bc12d65ade36ce17cb2b3e84cb69e`) | parses; status DRAFT; 0 errors; open items AMB_14, AMB_15, AMB_24 |
| Issued amendment at `../R4_20261028_preflight/03_R4_protocol_v1_amendment_1.md` | absent |

## 3. Sensitivity-draw specification (protocol §8.4)

| Item | Value |
|---|---|
| Generator | `scipy.stats.qmc.LatinHypercube(d=7, rng=numpy.random.default_rng(20261028)).random(32)`, default scrambling; SciPy 1.18.1, NumPy 2.5.4 |
| Mapping | uniform, lo + u·(hi − lo) |
| Checked in tests | one point per stratum in every column; deterministic; inside every range |

**Columns.** Each range equals the preflight ledger's `uncertainty_range` for the same ID (test `test_ranges_equal_the_preflight_ledger`).

| Column | Ledger ID | Parameter | Range |
|---|---|---|---|
| 1 | VEH-01 | M | 722.5–977.5 kg |
| 2 | VEH-03 | A_f | 2.0–2.4 m² |
| 3 | VEH-04 | C_d | 0.315–0.385 |
| 4 | VEH-05 | C_rr | 0.008–0.012 |
| 5 | VEH-06 | r_w | 0.265–0.285 m |
| 6 | BAT-07 | R0 | 4–6 mΩ |
| 7 | MOT-05 | η | 0.83–0.918 (M0 only; ignored by M1) |

**Purpose of each draw.** Each draw is one perturbed reference plant at P1:
- v_b and the S-eco profile are re-planned on that plant;
- B0 and B3 run on S2, L-EVE, P1, for M0 and M1.

This gives coverage for the §8.1 sensitivity criterion: at least 29 of 32 draws with ΔE_rel ≤ −1.0 %, and none above 0, for M0 and M1 separately. It is a coverage design, not a probability statement, and its spread is never a confidence interval (§7.5).

**Open:** the gain basis per draw (AMB-14). The 128 runs cannot start until it is issued.

## 4. Estimate

The basis is the two S1 smoke-test runs: mean runtime 203.5 s per 324 s run at 1 ms, scaled by cycle length and 1/dt.

| Item | Estimate |
|---|---|
| Dynamic runtime for the 170 runs | about 6.8 h, single process; planner jobs extra |
| Trace volume | about 3.8 GB (protocol §10.3 expected 3–4 GB) |
| Free space on D: | 348.8 GB |

## 5. Blockers reported

Readiness mode reported two blockers:
1. `no issued amendment at …/R4_20261028_preflight/03_R4_protocol_v1_amendment_1.md (the draft is not approved)`.
2. `code review: 0 critical and 2 major findings not resolved or accepted by the owner` (CR-A2 → AMB-24; CR-A6 residual).

The campaign-mode preconditions also require the following; tested in `test_preconditions_block_the_campaign_now`:
- a fresh campaign directory named by the issued amendment (AMB-15);
- that directory's own `logs/pre_run_hashes.txt` with a clean test run;
- an approval record naming the approver, the date and the issued amendment's SHA-256;
- no `null` in the issued block (AMB-14, AMB-24).

**`campaign_may_start`: false.** The campaign runner was never called in campaign mode.
