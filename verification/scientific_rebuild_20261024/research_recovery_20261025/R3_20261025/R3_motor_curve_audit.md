# R3 motor-curve audit and loss-model branches (Steps 1–2)

**Date:** 2026-10-25. Written before any gate output was inspected. The gate run started at 15:32 under the frozen `R3_protocol_v1.md`; this file records facts fixed before then, and the post-freeze probe in §2.3 that only re-documents them.
**Prepared by:** the AI assistant that built R1 and R2. Not reviewed by a person.

## 1. The source actually used

| Item | Value | Evidence |
|---|---|---|
| Package | NREL FASTSim 3.1.0, installed 2026-10-23 in `verification/python-env` (Python 3.14.7). Nothing was downloaded in R3 | `data/fastsim_source_record.json` |
| Where the data lives | No separate file is installed. The vehicle YAML is compiled into `fastsim.cp314-win_amd64.pyd` (46,264,832 bytes, SHA-256 `18da0cec61c78d1be690fbdfcbd5881d3b610fae57cddc377e26bd9a72c2ce40`) | `code/extract_fastsim_source.py` |
| Resource | `vehicles/2022_Renault_Zoe_ZE50_R135.yaml`: 9 embedded copies, all byte-identical (5,380 characters) | same |
| Verbatim copy | `data/fastsim_2022_Renault_Zoe_ZE50_R135.yaml`, SHA-256 `ed882ffab297a02f1558a6c89a0f0c6fd0fca1ff40d98b64c858a9d6d8180141` | same |
| Field | `pt_type/BEV/em/eff_interp_achieved`: 11 grid points x = 0, 0.02, 0.04, 0.06, 0.08, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0. Values 0.84, 0.86, 0.88, 0.90, 0.91, 0.92, 0.94, 0.95, 0.95, 0.94, 0.93. `strategy: Linear`, `extrapolate: Error`. `pwr_out_max_watts: 100000` | YAML lines 43–116; `data/motor_curve_fastsim.json` |
| Provenance in the file | `doc: ~`, `make: ~`, `model: ~`. The file states no source, test or reference | YAML lines 4–8 |

## 2. What the curve physically represents

### 2.1 Component

The FASTSim class docstring for `ElectricMachine` reads: *"Struct for modeling electric machines. This lumps performance and efficiency of motor and power electronics."* (`data/fastsim_source_record.json`, `docs`).

The curve is therefore a **combined motor + inverter** efficiency. It does not cover the whole powertrain: the same vehicle has a separate transmission (`eff_interp: 0.92`) and battery (`eff_interp: Constant 0.9849`).

### 2.2 Axes and units

The quantity is efficiency (dimensionless) as a function of **one** variable, x = P_mech,out / pwr_out_max. The source machine is rated at 100 kW.

- There is **no torque or speed axis**: the same power at any torque/speed split has the same efficiency.
- There is **no voltage or temperature dependence**.
- The second field, `eff_interp_at_max_input`, has grid x/η (e.g. 0.02/0.86 = 0.02326 and 1/0.93 = 1.0753) and the same values. It is the input-power-fraction view of the same curve, not independent data.
- **Valid range:** x ∈ [0, 1]. FASTSim raises an error outside it.

### 2.3 How FASTSim applies it (executed check)

The Zoe was simulated on FASTSim's bundled UDDS: 1,370 steps, 768 motoring and 359 regenerating. Scripts are `code/probe_fastsim_regen.py` and `code/probe_fastsim_regen_rule.py`; outputs are in `data/fastsim_em_probe.json` and `logs/probe_fastsim_regen_rule.txt`.

- **Motoring.** The recorded efficiency equals curve(P_mech/100 kW) to 2.2e-16, and P_elec = P_mech/η to 1.1e-16.
- **Regeneration** appears as negative `pwr_mech_prop_out` (the `dyn_brake` channels are zero), with P_elec = η·P_mech exactly. However, η is **0.84 at every regen step**: curve(max(P_mech, 0)/P_max) matches exactly, while curve(|P_mech|/P_max) differs by up to 0.103. FASTSim 3.1.0 therefore applies the zero-power value of the curve throughout regeneration. Whether that is intended, it means the source provides **no regeneration efficiency curve**.
- The first probe run used the wrong sign for braking and found no regen samples. It is preserved and superseded by the second.

### 2.4 Is it a Zoe measurement?

No evidence says so, and two observations say it is a template:

1. Only three of the package's six embedded vehicles have an e-machine. All three use the same 11-point grid and the same shape (rising to a 40–60 % plateau, falling to x = 1):
   - 2016 Prius, 53 kW: 0.85, 0.85, 0.87 … 0.92;
   - 2021 Sonata Hybrid, 39 kW: 0.8211 … 0.9244;
   - the Zoe, 100 kW.

   Source: `data/fastsim_embedded_em_curves.json`.
2. The Zoe values at indices 1–10 equal the Prius values + 0.01 exactly in floating point. The stored `0.9400000000000001` is the double-precision result of 0.93 + 0.01, whereas a literal 0.94 is stored as `0.94`. The values were **computed by offsetting a template**, not entered from a measured map. The x = 0 point (0.84) is the only one that does not follow the offset (Prius 0.85).

**Conclusion:**
- The curve is a FASTSim modelling template for a large automotive e-machine, offset to a 0.95 peak.
- It is not a measured map of the Renault Zoe machine, and still less of the thesis's unidentified 18 kW motor.
- It is not cited anywhere as evidence of the thesis motor's efficiency.

## 3. Is rescaling to 18 kW defensible?

R3 uses x = |P_m| / 18 kW, keeping the values unchanged.

**What supports this:**
- FASTSim itself normalises its curves by rated power across 39–100 kW machines, so normalising by rated power is the tool's own convention.

**What does not:**
- 18 kW is outside the size range of the package's examples.
- No source states that the shape or level is size-invariant. Smaller machines and low-voltage (48 V) inverters typically have lower peak efficiency and higher relative conduction loss. The 0.95 peak is therefore probably optimistic for this plant; the thesis's own combined value is 0.874 (itself unverified).
- With no torque or speed axis, the curve cannot represent the operating-point effects that make real maps matter: high-torque/low-speed copper loss and high-speed iron loss.
- **No no-load loss.** At x → 0, η = 0.84 and loss → 0. Real drives have speed-dependent iron loss and inverter switching loss at zero output. The curve therefore understates light-load and coasting losses, which matters for pulse-and-glide-type eco strategies.

**Extrapolation:**
- In R3 the shaft power is bounded by |T| ≤ min(85 N·m, 18 kW/ω), so x ≤ 1 always (`test_r3_supplementary.py::test_grid_finite_and_constraints_enforced` asserts it on 5,751 operating points × 18 configurations).
- `r3_lib` clamps to η(1) = 0.93 if x > 1 ever occurred, and the inverse-map table extends to x = 1.5 with that clamp. No extrapolated value enters an energy.

**Verdict:** **M1 is illustrative.** It is a published, generic part-load shape, transferred by an assumption. It is usable as a sensitivity branch showing whether a power-dependent efficiency changes conclusions. It is not a physically validated representation of the R3 plant's motor.

## 4. The three branches (Step 2)

| | M0 constant | M1 FASTSim generic curve | M2 copper-loss stress |
|---|---|---|---|
| Equation | L = P_m(1/η − 1) motoring; \|P_m\|(1 − η) regenerating; η = 0.874 | same with η = η(x), x = \|P_m\|/18 kW, linear interpolation of 11 source points | L = k_c·T², k_c = 18 000·(1/0.874 − 1)/85² = 0.3592 W/(N·m)² |
| Parameters and source | thesis Appendix A (0.92 × 0.95), `report_unverified` | §1 above | derived so that L equals M0's at rated torque and power (85 N·m, 211.8 rad/s, 18 kW); not calibrated to any outcome |
| Efficiency range in R3 | 0.874 | 0.84–0.95 (tested on 100,001 points) | P/(P + k_c T²). Examples: 0.62 at 85 N·m, 50 rad/s; 0.874 at rated; 0.965 at 20 N·m, 200 rad/s; 0.994 at 5 N·m, 300 rad/s |
| Zero power | L = 0 | L = 0, continuous across P_m = 0 (\|L(±1e-9 W)\| < 1e-9 W) | L = k_c T² > 0 at stall (ω = 0); L = 0 at T = 0 |
| Regeneration | symmetric | symmetric by \|P_m\|: an **R3 assumption**, since FASTSim uses η(0) = 0.84 | at low speed, braking torque can cost battery energy (k_c T² > \|P_m\|), which is physical plugging. `pm_regen_max` handles it (returns ∞ where the return cannot be reached) |
| Smoothness | constant | piecewise linear in x, kinks at the 11 knots, no jumps (max \|ΔL\| 0.034 W per 0.18 W step) | smooth |
| Inverse maps (battery → torque limits) | closed form | table with 3,001 points; round trip ≤ 1.5e-5 relative | closed-form quadratic |
| Status | **baseline**; thesis value, structure unverified | **illustrative** generic shape | **illustrative stress model** |

### Why M2 is deliberately favourable to the hypothesis

M2 puts *all* loss into copper loss ∝ T².
- This makes loss strictly convex in torque. Smoothing torque, and avoiding high-torque/low-speed operation, then saves energy, which is exactly the lever an LQR weighting can pull.
- It omits iron, friction and switching losses, which grow with speed and do not reward smoothing.
- It gives efficiency approaching 1 at light load, which no real drive has.

**Interpretation:**
- A benefit seen only under M2 is labelled *stress-model only* (protocol §4 and §7).
- An absence of benefit under M2 is the strongest negative evidence R3 can produce for torque-smoothing benefits.
- M2's absolute energies are not realistic and are never compared with M0's or M1's.

### Independence of branches

Results are always reported per branch, and the gate is evaluated per branch (protocol §4). No branch is averaged with another or chosen post hoc. Absolute energies differ between branches by construction: M1's level (peak 0.95) is not the thesis's 0.874. Only within-branch relative differences are interpreted.

## 5. Transformation record (M1)

`code/derive_m1_curve.py` writes `data/motor_curve_m1_derived.json` (SHA-256 `f872faa0ff96d12d26eb5c935bb145062c3ac649e4eb327136f0fa9a0868d1d9`), with:
- frac and eff exactly as the source;
- p_rated 18,000 W;
- the source hashes;
- the four transformation rules above.

The original FASTSim install is untouched; it was only read.

## 6. Summary verdicts

- **M0:** reproduces R1's plant to 9.1e-14 (relative, 3,000 random states), and R1's independent exact-tracking ledger to 0.071 % worst case over 16 rows (limit 0.2 %). The constant η itself is an unverified thesis value.
- **M1:** **illustrative.** Generic template, combined motor + inverter, power-fraction only, no regen curve in the source, no no-load loss, 18 kW transfer assumed.
- **M2:** **illustrative stress model**, favourable to the hypothesis by design.
- **Physically justified for the thesis motor:** none of the three. No measured map of a 15–20 kW micro-EV drive is available locally (`R3_model_basis.md` §5).
