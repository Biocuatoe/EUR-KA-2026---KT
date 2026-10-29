# R4 H3: provenance of the S1 and S2 cycle inputs

**Date:** 2026-10-28.
**Question (readiness brief §2):** what exactly is the 1 s-sampled task that protocol v1 §3 prescribes? Where does it come from, and how does it differ from the YAML cycle definition?
**Answer:** the sampled tasks are established, reproduced bit for bit from three independent routes, and hashed. **No blocker.** No value was inferred by rounding, and no replacement cycle was made.

## 1. Sources and code, all hash-checked

| Role | File | SHA-256 | Earlier record of the same hash |
|---|---|---|---|
| Cycle definition (YAML segments) | `configs/cycles/profiles.yaml` | `90a496a36c618e216693a3d819b84739f10e6c35167c23a91b63478ef28be0a6` | R1 run manifests (e.g. `runs/R1_US06/manifest.json`), the R4 preflight project hash, Git-tracked unchanged |
| YAML → knots | `src/eureka/cycles.py` (`build`, `Profile.sample` = `np.interp`) | `f09ed877efe3aece1d4990c79d55c4902999758ef67ab2603591703ae49b8cec` | R1 run manifests |
| Cycle loader | `verification/scientific_rebuild_20261024/src/rebuild/run.py` (`load_cycle`) | `7336a295f407134f6d7aa38ba1749edcb3aea9cdbddf7114c2f8a7bbdb185001` | R1 run manifests |
| Sampling at h = 1 s | R3 `code/run_gates.py`, `reference(cyc, h=1.0)`: `t = np.arange(0, duration + 1e-9, h)`, `v = Profile.sample(t)` | `d870e096cbad828661c65682dfbd4e18ecc00bdace989af084e10def465ca85a` | `R3_hash_manifest.csv` ("frozen-unchanged") |
| R4 task | `code/r4h3/task.py`, `load_task()` (the same construction) | pilot code, hashed in `logs/readiness_gate_v2.json` | — |

**How the YAML becomes a task.**
- The YAML holds segment specifications (`idle`, `cruise`, `accel` to a target speed), not knots.
- `eureka.cycles.build` places a knot at the end of each segment. An acceleration from v₀ to v₁ at a lasts (v₁ − v₀)/a, which is generally not a whole number of seconds. For example, S2's first acceleration, 0 → 10 km/h at 0.6 m/s², lasts 4.630 s.
- This is why the knots lie off the 1 s grid.

## 2. Retained output

R3 saved the sampled reference it used in every path file: arrays `t` and `v_ref` in `outputs/gates/paths/*.npz` and `outputs/gates_a1/paths/*.npz`. There are 24 files per cycle, covering the band and eco paths for M0, M1 and M2 and their limit sets.

For each file:
1. its SHA-256 was checked against `R3_hash_manifest.csv`: 48 of 48 match;
2. only `t` and `v_ref` were read.

## 3. Bit-for-bit checks (`code/build_cycle_inputs.py`, log `logs/build_cycle_inputs.txt`)

| Check | S1 | S2 |
|---|---|---|
| R4 `task.load_task()` t and v equal R3 `run_gates.reference()` | yes | yes |
| All 24 R3-retained `t` and `v_ref` arrays equal R3 `run_gates.reference()` | yes | yes |
| Uniform 1 s grid starting at 0 | yes | yes |
| Starts and ends at rest | yes | yes |
| d_ref to 3 decimals equals the protocol §3 value | 2161.027 | 531.574 |
| T_ref equals the protocol §3 value | 324 s | 213 s |
| Canonical CSV reads back bit for bit | yes | yes |

The script stops before writing a sampled artefact if any check fails. None failed.

## 4. The two objects compared

| | S1 YAML profile | S1 sampled task | S2 YAML profile | S2 sampled task |
|---|---|---|---|---|
| Knots or samples | 24 knots (22 off whole seconds) | 325 samples, t = 0, 1, …, 324 | 26 knots (24 off whole seconds) | 214 samples, t = 0, 1, …, 213 |
| Duration | 324.911 s | **T_ref = 324 s** | 213.278 s | **T_ref = 213 s** |
| Distance | 2161.047 m | **d_ref = 2161.0270 m** | 531.678 m | **d_ref = 531.5735 m** |
| Acceleration bounds | ±1.0 m/s² | a_lo = −1.0, a_hi = 1.0 | −0.7 / +0.6 m/s² | a_lo = −0.7, a_hi = 0.6 (to float rounding) |
| Maximum speed | 13.889 m/s | 13.889 m/s | 6.944 m/s | 6.944 m/s |

**Why they differ.**
- The final partial second (0.911 s for S1, 0.278 s for S2) lies beyond the last whole-second sample: `np.arange(0, duration + 1e-9, 1)` ends at 324 and 213.
- Between samples, the sampled task is the straight line through the profile's values at whole seconds. Near every off-grid knot this differs slightly from the profile.

## 5. Stops: locations and times of the sampled task

A rest interval is a maximal run of samples with v ≤ 1e-9 m/s (protocol §5.1). "Position" is the trapezoidal distance travelled when the stop begins. "YAML rest" is the profile's own standstill interval, shown for comparison only.

**S1.** 5 rest intervals and 4 segments.

| # | Sampled rest [t_a, t_d] (s) | Length (s) | Position (m) | YAML rest (s) | Tested by §8.2 |
|---|---|---|---|---|---|
| 0 | 0 – 10 | 10 | 0.000 | 0.000 – 10.000 | yes |
| 1 | 39 – 53 | 14 | 121.911 | 38.889 – 53.889 | yes |
| 2 | 118 – 137 | 19 | 576.406 | 117.500 – 137.500 | yes |
| 3 | 275 – 289 | 14 | 2037.354 | 274.286 – 289.286 | yes |
| 4 | 315 – 324 | 9 | 2161.027 | 314.911 – 324.911 | yes |

| Segment | ks–ke (s) | D_k (m) | T_k (s) | v_lim (m/s) |
|---|---|---|---|---|
| 0 | 10–39 | 121.911 | 29 | 5.5556 |
| 1 | 53–118 | 454.494 | 65 | 9.7222 |
| 2 | 137–275 | 1460.948 | 138 | 13.8889 |
| 3 | 289–315 | 123.673 | 26 | 6.9444 |

**S2 (held-out).** 7 rest intervals and 6 segments.

| # | Sampled rest [t_a, t_d] (s) | Length (s) | Position (m) | YAML rest (s) | Tested by §8.2 |
|---|---|---|---|---|---|
| 0 | 0 – 8 | 8 | 0.000 | 0.000 – 8.000 | yes |
| 1 | 25 – 36 | 11 | 34.096 | 24.598 – 36.598 | yes |
| 2 | 62 – 66 | 4 | 110.963 | 61.495 – 66.495 | yes |
| 3 | 90 – 99 | 9 | 192.092 | 89.690 – 99.690 | yes |
| 4 | 137 – 151 | 14 | 370.883 | 136.185 – 151.185 | yes |
| 5 | 175 – 180 | 5 | 439.416 | 174.082 – 180.082 | yes |
| 6 | 206 – 213 | 7 | 531.574 | 205.278 – 213.278 | yes |

| Segment | ks–ke (s) | D_k (m) | T_k (s) | v_lim (m/s) |
|---|---|---|---|---|
| 0 | 8–25 | 34.096 | 17 | 2.7778 |
| 1 | 36–62 | 76.867 | 26 | 4.1667 |
| 2 | 66–90 | 81.129 | 24 | 5.5556 |
| 3 | 99–137 | 178.792 | 38 | 6.9444 |
| 4 | 151–175 | 68.533 | 24 | 4.1667 |
| 5 | 180–206 | 92.157 | 26 | 5.5556 |

**What this means.**
- Every sampled rest interval lies inside the corresponding YAML standstill.
- Each sampled interval is up to about 1 s shorter than the YAML one.
- Stop compliance (§8.2) is tested on the sampled intervals, which is the protocol's definition (§3, §5.1).
- R3 v1 §3.2's statement that the S1 and S2 knots lie on whole seconds is **incorrect**. This is recorded here, not corrected in R3.

## 6. Canonical artefacts

The YAML source and the sampled task are kept as separate files under `inputs/cycles/`, written once and refusing overwrite.

| File | What it is | SHA-256 |
|---|---|---|
| `S1_source_segments.json` | S1 YAML definition, verbatim, with the YAML file's hash | `88a04c905fdd6a3b109e0189af0347c8d6525347ae4812228e7838162cb8d6fd` |
| `S1_knots_from_yaml.csv` | S1 knots from `eureka.cycles.build` | `e0cdb1f4a4627838a8e691d4516492e604b01be85c2afa34c1ec98be8fd120ec` |
| **`S1_sampled_h1.csv`** | **canonical S1 task** (t_s, v_mps; shortest round-trip floats) | **`87151e5c30c02f5f6784732a5dd619fc6c39e90913d4afcf06292de2c1f2b7da`** |
| `S2_source_segments.json` | S2 YAML definition, verbatim | `49093326473eb4d33dde34400a6dc741949d192e48fe25c81f1467683a0f2d13` |
| `S2_knots_from_yaml.csv` | S2 knots | `4bf394980e928f075f7f82135aa11beba1b97b95a2d1e18ae030ea3c448dde6c` |
| **`S2_sampled_h1.csv`** | **canonical S2 task** | **`def9d757dc0923afe20a91dca487c84527daff2bef5421c34aef1a61f0a6e990`** |
| `cycle_inputs_manifest.json` | every check above, every hash, segments and rest intervals | `3d3d6e93d19842141691d041e2363dd8f3f9fef73b362ebcd6ae2ef8b6de7ea5` |

**Where these hashes are used.**
- They are recorded in draft amendment A1-1 and in `config/campaign_config_v1_DRAFT.json`.
- `r4h3/inputs.py` holds them as constants.
- `inputs.verify_all()` re-hashes every artefact and checks that `task.load_task()` still reproduces the canonical tasks bit for bit. It runs in the readiness gate, in the dry run and at the start of every official campaign run set.
- A tampered file is refused (test `test_tampered_cycle_input_is_refused`).

## 7. S2 protection

S2 was used only as an input definition: hashed, sampled, and its d_ref and T_ref checked against the protocol.
- No S2 planner, QS-energy, baseline-task or dynamic computation was run in R4.
- No setting was chosen with reference to S2.
- The planner numerics are the frozen §5.2 constants, which the dry run asserts.
- Every development check in this task used S1 or toy tasks.
