# Controller cross-check run log (append-only)

Each entry is written by `verification/scripts/runlog_record.py` at the time stated (local clock of the machine).

## 2026-10-23 22:49:14 +0700 - Pre-freeze preparation record (written retrospectively in one entry)
Before the protocol freeze, in this order: (1) inspection of the Python controller, simulation loop, plant, metrics, preregistration, saved manifests; (2) controller_gain_design.py run once (gains frozen; comparison with saved gains max 3.1e-13 relative); (3) python_reference_runs.py started (Python only; still running at the time of this entry); (4) compile-only checkModel of the Modelica controller models with unit checking (6 models, no warning after the discrete start values were added); (5) ControllerUnit simulated three times. Run 1 (step-change inputs) FAILED the P1 comparison: u diff 105.3, e_k diff 0.35, 1 sat mismatch; cause: the test design, not the controller. OpenModelica's sample() times drift from k*Ts (1.7e-13 s by t = 10 s), so a sample can land a few 1e-13 s before an input step that is scheduled at exactly k*Ts, and my row grouping merged two events 1.7e-13 s apart. Run 2 (same model after adding start values to discrete variables; same defect). Run 3 (inputs changed to continuous ramps, controller rows taken as the first row with k_ctrl = k+1) PASSED: u diff 1.1e-12, z 4e-15, sat mismatches 0, coverage: 441 samples saturated with e<0, 366 saturated with e>0, 194 unsaturated; updates 1001 of 1001; max update-time deviation 1.7e-13 s. The failed run-1 result file was overwritten by run 3 (not preserved); the numbers above are copied from its console output. No S1, S2 or P-TUNE closed-loop case has been simulated at the time of this entry.

## 2026-10-23 22:49:22 +0700 - Correction to the previous entry
Run 2 of ControllerUnit (after adding start values) was only checked for the initialisation warning (gone) and was NOT evaluated against the P1 criteria; only runs 1 (fail) and 3 (pass) were evaluated.

## 2026-10-23 23:25:06 +0700 - Python step-size study complete; step-input tests
Python refinement study finished (S1, S2, P-TUNE; dt 1e-3, 5e-4, 2.5e-4, 1e-4): reproduction of the saved series bit-identical, convergent (verdict in protocol 8.2). Step-input tests (P1b) run on the reconstructed original test and the defined-semantics test: the original failing evaluation was REPRODUCED with identical numbers (max |u| diff 105.28091142582139, e_k diff 0.35, 1 sat mismatch); both tests pass under the defined semantics (max u diff 1.4e-14 and 5.7e-14). Finding: for a step exactly at an update instant (t = 4.0 and 8.0) the Modelica update occurred at 3.999999999999959 and 7.999999999999874, i.e. BEFORE the step, so it saw the old input, whereas Python semantics (t_k >= t_step) would give the new one. Documented in protocol 6.1; no step input exists in the primary grid.

## 2026-10-23 23:25:22 +0700 - PROTOCOL FREEZE (v1.0) - before any P-TUNE or S1/S2 closed-loop simulation
Protocol finalised with the actual Python discretisation-error estimates (8.2), the verified meaning of the +/-1 % threshold (10), the P1b step-input semantics (6.1), the exact run matrix (2.1) and the stopping rules (12). Hashes of the protocol and of everything that defines the runs are below. The P-TUNE solver study starts after this entry.

| file | sha256 |
|---|---|
| `verification/controller-crosscheck-protocol.md` | c7951936eb162ab5326711d537fe7f8438f76a2ac25df4a80126267237e9725d |
| `verification/controller-port-design.md` | ed83526da47f8ecf6899a12f037da415961e46c6a0c12266409065ea5470b3b1 |
| `verification/references/controller_gains.json` | 29c4df2048aaea177f0e7876af4138b7ac1a917665dcc54f536400cda495a310 |
| `verification/references/python_dt_study.json` | 82f485e1aab09004b4be8d81835f4a17c6aa4809e345cb019083fd91fc471516 |
| `verification/modelica/controller_generated_inputs.json` | 99533ed498957434482f970366f95528b3daba1896487cbdf06754cfe699a54c |
| `verification/Invoke-OpenModelica.ps1` | e69f16113e8f690df6f5fc309fe2ad11fe1f4dd5c315687b5991f6ad948d88e3 |
| `verification\modelica\EurekaPlant\InverseS1.mo` | af2ef1590e72f6bdd119fbadb91ba9d9538ff913cc10b69d69794c548dbb75f5 |
| `verification\modelica\EurekaPlant\InverseS2.mo` | cad74dd65a9691442ce9ca1b6b5bc61962d5da6d5566cc68443cbe5f42ee1400 |
| `verification\modelica\EurekaPlant\InverseTracking.mo` | 1e56ff93fc0ed7a243d5f3ae72dc61574b07600d86a9905b06e1cc980e9b1da2 |
| `verification\modelica\EurekaPlant\Parameters.mo` | 806f6600bba08b9da8d1a5dd37100fe13fab1fc37c496b9f62b66fa8745a9463 |
| `verification\modelica\EurekaPlant\Plant.mo` | 41e6b28e2bb7f24dc962dcdf7a4517fb290cdc58ceb1330cc643c60ce00e3bab |
| `verification\modelica\EurekaPlant\Profiles.mo` | 26357ad31d9834a1503f14789cfa50ba09b21e1242c9203a0ed3003c58aa2021 |
| `verification\modelica\EurekaPlant\Tests\CoastDown.mo` | 4720472751afd100acfbd31cf51995033a2af1352e44113a9ce7095a1c701bdf |
| `verification\modelica\EurekaPlant\Tests\OpenLoop66.mo` | 5c968b3529fa79cdae37433301dc777023b696ec4ee8435734f22c4b025003c0 |
| `verification\modelica\EurekaPlant\Tests\StaticPoint.mo` | 469a2b06248a382d052d87bcd40e088f69cbb8c2c26c33c7f04f4a88d2aaab5d |
| `verification\modelica\EurekaPlant\Tests\package.mo` | fc25a474c0dc8db1ee125b73ae11b845bad405f293a0c690c83219aaa2a46471 |
| `verification\modelica\EurekaPlant\package.mo` | 4ad7486acb4b0302808101a8b7d9ac9ff55dc77e01782b152dbbce6e64905bc1 |
| `verification\modelica\EurekaController\Cases.mo` | b27ad368620219b96c0ab7eab5e141bcafbf52ff45196b57a02037d1e8d9374d |
| `verification\modelica\EurekaController\ClosedLoop.mo` | b9c8ce3f609c25b02a6728fa00323ea4601e1c68c3f75f3cd293947bed9c7be2 |
| `verification\modelica\EurekaController\ControllerProfiles.mo` | db3f4c1fda4bebcc6ca7456e3604096bda3df59b1cfc3701175fddb96a3547b3 |
| `verification\modelica\EurekaController\SampledLqr.mo` | 7e4d78c970fc1ba46fa6681d6d53302345934e5dd247a7a5070be2afcd9992d9 |
| `verification\modelica\EurekaController\Tests\ControllerStepSemantics.mo` | 71cf163a09aeb7f45dc1c453596d466e29850dcb7bfedaa352439a3838e12280 |
| `verification\modelica\EurekaController\Tests\ControllerUnit.mo` | 5349098a1ab551fc42fe39e8761a3b0bee9dc29bd2c4df140693ee611116608b |
| `verification\modelica\EurekaController\Tests\ControllerUnitStepOriginal.mo` | 6d2000260d521e2696a4c3af4425295726d194d81021e8f37cbb7f1f2a070cad |
| `verification\modelica\EurekaController\Tests\package.mo` | d8f9fea785471910472d1b413b56ba9f09dc27927440b8a239b6cc6259e627c0 |
| `verification\modelica\EurekaController\package.mo` | 96a7506d23d03b9fe7cb20a8245d24ed43021800b1fdf9adf8e5426bd2396b3e |
| `verification\scripts\controller_eval.py` | 6155009089039a2f422a372787b5799c0c9fccd3c79fd55634601db2fb0287ea |
| `verification\scripts\controller_gain_design.py` | 422081ee19282212077897e95f7cd8b1a548970bc72a4ab625228f4485abd5f4 |
| `verification\scripts\controller_metrics.py` | c320fbb67ea4eb01dee30875238b3227d45f1d68b12d0a95c837c12dac817c69 |
| `verification\scripts\controller_prelim_checks.py` | 08b13e6bfa802e2e0f3251079f646c6840fab84966981a50bebf7ccd17391c85 |
| `verification\scripts\controller_ptune_study.py` | 44711c6490ac1b3a4349f1084fbf226e68a347d160db1b2eddad1cec023a1674 |
| `verification\scripts\controller_series.py` | 43c2bd017ae97e629038ce47a7483b0596fb2ee8d276dca8472cf50aab32573f |
| `verification\scripts\controller_step_tests.py` | 43500b40d52244937c8af0341a008c0261770f3cb9f43342d4ba73f66e79f342 |
| `verification\scripts\controller_tolerances.py` | 3429485cb7ea9d28049c9a26ff5cafa2ef26f0f0f6a96a73ba151f80c5c79fc3 |
| `verification/scripts/python_reference_runs.py` | d0cc743fac5d649e873a4b347402122ebcb5a01831f6eb7e32b89a7ef5f4d2df |
| `verification/scripts/generate_controller_models.py` | 6336047cfd7b4c48723302cd7c2e7f45cd3ba066534db5839d2a596c35cef474 |
| `verification/scripts/generate_controller_case_scripts.py` | d01e4dfa164cf306246eb502c6e659b3eafbe841826349d10c3ebb485594cd7d |

## 2026-10-23 23:37:54 +0700 - Amendment A1 (resource guard) after first P-TUNE launch
First P-TUNE launch: 8 DASSL runs completed; run 9 (PT_fixed_cvode_tol1e-06) went into a CVODE 'Desired step to small' loop (16.8 M rows, 10 GB, stuck at t=17.99 s); killed by hand, omc crashed, 15 runs not started. Protocol amended (A1, 500 MB guard, one case per omc call). Protocol sha256 after the amendment: 4b9df14b2e135f783e9d7f71db974ab20857fd8b4f66cfe49a4a9a8f8a6b7a9c. No P-TUNE result had been evaluated or inspected beyond file/row counts and the CVODE log.

## 2026-10-23 23:49:33 +0700 - P-TUNE solver study finished; amendments A1-A3; SELECTION: DASSL tol 1e-12
P-TUNE ladder: DASSL 4/4 tolerances x 2 controllers completed (about 2-3 s each); IDA 8/8 completed but its state reverts at every event after t=17.99 s (inadmissible under A2 criterion K: 1.1e-1 m vs 1.2e-5 m for DASSL); CVODE 8/8 failed (runaway). The frozen rule alone would have selected the defective IDA@1e-12; amendments A2/A3 (post P-TUNE result, pre S1/S2) are in protocol section 14. Selected: DASSL 1e-12. Protocol sha256 now b4ed35eb819f307b0746f3a1ee96f3ff435905c9cfee4987177a825e5566586d.

| file | sha256 |
|---|---|
| `verification/controller-crosscheck-protocol.md` | b4ed35eb819f307b0746f3a1ee96f3ff435905c9cfee4987177a825e5566586d |
| `verification/controller-port-design.md` | ed83526da47f8ecf6899a12f037da415961e46c6a0c12266409065ea5470b3b1 |
| `verification/references/controller_gains.json` | 29c4df2048aaea177f0e7876af4138b7ac1a917665dcc54f536400cda495a310 |
| `verification/references/python_dt_study.json` | 82f485e1aab09004b4be8d81835f4a17c6aa4809e345cb019083fd91fc471516 |
| `verification/modelica/controller_generated_inputs.json` | 99533ed498957434482f970366f95528b3daba1896487cbdf06754cfe699a54c |
| `verification/Invoke-OpenModelica.ps1` | e69f16113e8f690df6f5fc309fe2ad11fe1f4dd5c315687b5991f6ad948d88e3 |
| `verification\modelica\EurekaPlant\InverseS1.mo` | af2ef1590e72f6bdd119fbadb91ba9d9538ff913cc10b69d69794c548dbb75f5 |
| `verification\modelica\EurekaPlant\InverseS2.mo` | cad74dd65a9691442ce9ca1b6b5bc61962d5da6d5566cc68443cbe5f42ee1400 |
| `verification\modelica\EurekaPlant\InverseTracking.mo` | 1e56ff93fc0ed7a243d5f3ae72dc61574b07600d86a9905b06e1cc980e9b1da2 |
| `verification\modelica\EurekaPlant\Parameters.mo` | 806f6600bba08b9da8d1a5dd37100fe13fab1fc37c496b9f62b66fa8745a9463 |
| `verification\modelica\EurekaPlant\Plant.mo` | 41e6b28e2bb7f24dc962dcdf7a4517fb290cdc58ceb1330cc643c60ce00e3bab |
| `verification\modelica\EurekaPlant\Profiles.mo` | 26357ad31d9834a1503f14789cfa50ba09b21e1242c9203a0ed3003c58aa2021 |
| `verification\modelica\EurekaPlant\Tests\CoastDown.mo` | 4720472751afd100acfbd31cf51995033a2af1352e44113a9ce7095a1c701bdf |
| `verification\modelica\EurekaPlant\Tests\OpenLoop66.mo` | 5c968b3529fa79cdae37433301dc777023b696ec4ee8435734f22c4b025003c0 |
| `verification\modelica\EurekaPlant\Tests\StaticPoint.mo` | 469a2b06248a382d052d87bcd40e088f69cbb8c2c26c33c7f04f4a88d2aaab5d |
| `verification\modelica\EurekaPlant\Tests\package.mo` | fc25a474c0dc8db1ee125b73ae11b845bad405f293a0c690c83219aaa2a46471 |
| `verification\modelica\EurekaPlant\package.mo` | 4ad7486acb4b0302808101a8b7d9ac9ff55dc77e01782b152dbbce6e64905bc1 |
| `verification\modelica\EurekaController\Cases.mo` | b27ad368620219b96c0ab7eab5e141bcafbf52ff45196b57a02037d1e8d9374d |
| `verification\modelica\EurekaController\ClosedLoop.mo` | b9c8ce3f609c25b02a6728fa00323ea4601e1c68c3f75f3cd293947bed9c7be2 |
| `verification\modelica\EurekaController\ControllerProfiles.mo` | db3f4c1fda4bebcc6ca7456e3604096bda3df59b1cfc3701175fddb96a3547b3 |
| `verification\modelica\EurekaController\SampledLqr.mo` | 7e4d78c970fc1ba46fa6681d6d53302345934e5dd247a7a5070be2afcd9992d9 |
| `verification\modelica\EurekaController\Tests\ControllerStepSemantics.mo` | 71cf163a09aeb7f45dc1c453596d466e29850dcb7bfedaa352439a3838e12280 |
| `verification\modelica\EurekaController\Tests\ControllerUnit.mo` | 5349098a1ab551fc42fe39e8761a3b0bee9dc29bd2c4df140693ee611116608b |
| `verification\modelica\EurekaController\Tests\ControllerUnitStepOriginal.mo` | 6d2000260d521e2696a4c3af4425295726d194d81021e8f37cbb7f1f2a070cad |
| `verification\modelica\EurekaController\Tests\package.mo` | d8f9fea785471910472d1b413b56ba9f09dc27927440b8a239b6cc6259e627c0 |
| `verification\modelica\EurekaController\package.mo` | 96a7506d23d03b9fe7cb20a8245d24ed43021800b1fdf9adf8e5426bd2396b3e |
| `verification\scripts\controller_eval.py` | 257bd92d93c49d6feccd8ef55bdb6bc9ec9eb36e6ba78daf3b4252141f105401 |
| `verification\scripts\controller_gain_design.py` | 422081ee19282212077897e95f7cd8b1a548970bc72a4ab625228f4485abd5f4 |
| `verification\scripts\controller_metrics.py` | c320fbb67ea4eb01dee30875238b3227d45f1d68b12d0a95c837c12dac817c69 |
| `verification\scripts\controller_prelim_checks.py` | 08b13e6bfa802e2e0f3251079f646c6840fab84966981a50bebf7ccd17391c85 |
| `verification\scripts\controller_ptune_study.py` | e3331ad2391219a0c136c9e2dd4b37143eae618d77ff758729b7e8d97efed6fb |
| `verification\scripts\controller_series.py` | 43c2bd017ae97e629038ce47a7483b0596fb2ee8d276dca8472cf50aab32573f |
| `verification\scripts\controller_step_tests.py` | 43500b40d52244937c8af0341a008c0261770f3cb9f43342d4ba73f66e79f342 |
| `verification\scripts\controller_tolerances.py` | 3429485cb7ea9d28049c9a26ff5cafa2ef26f0f0f6a96a73ba151f80c5c79fc3 |
| `verification/scripts/python_reference_runs.py` | d0cc743fac5d649e873a4b347402122ebcb5a01831f6eb7e32b89a7ef5f4d2df |
| `verification/scripts/generate_controller_models.py` | 6336047cfd7b4c48723302cd7c2e7f45cd3ba066534db5839d2a596c35cef474 |
| `verification/scripts/generate_controller_case_scripts.py` | 77625e17de453757fa7bd03392db8ff4e2b38b9a8fa630228480bc941fc96624 |
| `verification/references/controller_solver_selection.json` | 5d46973e1fe5c23fdece84c4e773e28c5fff49eba7f0a13181644d26e1c4fb01 |
| `verification/modelica/scripts/controller_cases.json` | 31c858476c7a6de3e201db07a2d7fbf79dacbde901d34903aa150c7d2bbc3821 |

## 2026-10-23 23:53:32 +0700 - Primary grid (16) and sensitivity (8) runs executed
Selected configuration DASSL 1e-12; primary grid A_* 16 runs and sensitivity N_* 8 runs (DASSL 1e-10 and 1e-8) all launched by guarded_run.py; no guard trigger; launcher exit 0 for all (simulation status is read from the omc record by controller_eval.py). Evaluation not yet run at the time of this entry.

| file | sha256 |
|---|---|
| `verification/controller-crosscheck-protocol.md` | b4ed35eb819f307b0746f3a1ee96f3ff435905c9cfee4987177a825e5566586d |
| `verification/controller-port-design.md` | ed83526da47f8ecf6899a12f037da415961e46c6a0c12266409065ea5470b3b1 |
| `verification/references/controller_gains.json` | 29c4df2048aaea177f0e7876af4138b7ac1a917665dcc54f536400cda495a310 |
| `verification/references/python_dt_study.json` | 82f485e1aab09004b4be8d81835f4a17c6aa4809e345cb019083fd91fc471516 |
| `verification/modelica/controller_generated_inputs.json` | 99533ed498957434482f970366f95528b3daba1896487cbdf06754cfe699a54c |
| `verification/Invoke-OpenModelica.ps1` | e69f16113e8f690df6f5fc309fe2ad11fe1f4dd5c315687b5991f6ad948d88e3 |
| `verification\modelica\EurekaPlant\InverseS1.mo` | af2ef1590e72f6bdd119fbadb91ba9d9538ff913cc10b69d69794c548dbb75f5 |
| `verification\modelica\EurekaPlant\InverseS2.mo` | cad74dd65a9691442ce9ca1b6b5bc61962d5da6d5566cc68443cbe5f42ee1400 |
| `verification\modelica\EurekaPlant\InverseTracking.mo` | 1e56ff93fc0ed7a243d5f3ae72dc61574b07600d86a9905b06e1cc980e9b1da2 |
| `verification\modelica\EurekaPlant\Parameters.mo` | 806f6600bba08b9da8d1a5dd37100fe13fab1fc37c496b9f62b66fa8745a9463 |
| `verification\modelica\EurekaPlant\Plant.mo` | 41e6b28e2bb7f24dc962dcdf7a4517fb290cdc58ceb1330cc643c60ce00e3bab |
| `verification\modelica\EurekaPlant\Profiles.mo` | 26357ad31d9834a1503f14789cfa50ba09b21e1242c9203a0ed3003c58aa2021 |
| `verification\modelica\EurekaPlant\Tests\CoastDown.mo` | 4720472751afd100acfbd31cf51995033a2af1352e44113a9ce7095a1c701bdf |
| `verification\modelica\EurekaPlant\Tests\OpenLoop66.mo` | 5c968b3529fa79cdae37433301dc777023b696ec4ee8435734f22c4b025003c0 |
| `verification\modelica\EurekaPlant\Tests\StaticPoint.mo` | 469a2b06248a382d052d87bcd40e088f69cbb8c2c26c33c7f04f4a88d2aaab5d |
| `verification\modelica\EurekaPlant\Tests\package.mo` | fc25a474c0dc8db1ee125b73ae11b845bad405f293a0c690c83219aaa2a46471 |
| `verification\modelica\EurekaPlant\package.mo` | 4ad7486acb4b0302808101a8b7d9ac9ff55dc77e01782b152dbbce6e64905bc1 |
| `verification\modelica\EurekaController\Cases.mo` | b27ad368620219b96c0ab7eab5e141bcafbf52ff45196b57a02037d1e8d9374d |
| `verification\modelica\EurekaController\ClosedLoop.mo` | b9c8ce3f609c25b02a6728fa00323ea4601e1c68c3f75f3cd293947bed9c7be2 |
| `verification\modelica\EurekaController\ControllerProfiles.mo` | db3f4c1fda4bebcc6ca7456e3604096bda3df59b1cfc3701175fddb96a3547b3 |
| `verification\modelica\EurekaController\SampledLqr.mo` | 7e4d78c970fc1ba46fa6681d6d53302345934e5dd247a7a5070be2afcd9992d9 |
| `verification\modelica\EurekaController\Tests\ControllerStepSemantics.mo` | 71cf163a09aeb7f45dc1c453596d466e29850dcb7bfedaa352439a3838e12280 |
| `verification\modelica\EurekaController\Tests\ControllerUnit.mo` | 5349098a1ab551fc42fe39e8761a3b0bee9dc29bd2c4df140693ee611116608b |
| `verification\modelica\EurekaController\Tests\ControllerUnitStepOriginal.mo` | 6d2000260d521e2696a4c3af4425295726d194d81021e8f37cbb7f1f2a070cad |
| `verification\modelica\EurekaController\Tests\package.mo` | d8f9fea785471910472d1b413b56ba9f09dc27927440b8a239b6cc6259e627c0 |
| `verification\modelica\EurekaController\package.mo` | 96a7506d23d03b9fe7cb20a8245d24ed43021800b1fdf9adf8e5426bd2396b3e |
| `verification\scripts\controller_eval.py` | dab84150984be1f47dd249dab3f5e6af4cbd755a2b3be4a4e627887789425e6e |
| `verification\scripts\controller_gain_design.py` | 422081ee19282212077897e95f7cd8b1a548970bc72a4ab625228f4485abd5f4 |
| `verification\scripts\controller_metrics.py` | c320fbb67ea4eb01dee30875238b3227d45f1d68b12d0a95c837c12dac817c69 |
| `verification\scripts\controller_prelim_checks.py` | 08b13e6bfa802e2e0f3251079f646c6840fab84966981a50bebf7ccd17391c85 |
| `verification\scripts\controller_ptune_study.py` | e3331ad2391219a0c136c9e2dd4b37143eae618d77ff758729b7e8d97efed6fb |
| `verification\scripts\controller_series.py` | 43c2bd017ae97e629038ce47a7483b0596fb2ee8d276dca8472cf50aab32573f |
| `verification\scripts\controller_step_tests.py` | 43500b40d52244937c8af0341a008c0261770f3cb9f43342d4ba73f66e79f342 |
| `verification\scripts\controller_tolerances.py` | 3429485cb7ea9d28049c9a26ff5cafa2ef26f0f0f6a96a73ba151f80c5c79fc3 |
| `verification/scripts/python_reference_runs.py` | d0cc743fac5d649e873a4b347402122ebcb5a01831f6eb7e32b89a7ef5f4d2df |
| `verification/scripts/generate_controller_models.py` | 6336047cfd7b4c48723302cd7c2e7f45cd3ba066534db5839d2a596c35cef474 |
| `verification/scripts/generate_controller_case_scripts.py` | 77625e17de453757fa7bd03392db8ff4e2b38b9a8fa630228480bc941fc96624 |
| `verification/references/controller_solver_selection.json` | 5d46973e1fe5c23fdece84c4e773e28c5fff49eba7f0a13181644d26e1c4fb01 |
| `verification/modelica/scripts/controller_cases.json` | 31c858476c7a6de3e201db07a2d7fbf79dacbde901d34903aa150c7d2bbc3821 |

## 2026-10-24 00:38:52 +0700 - Evaluation of the primary grid; amendment A4
controller_eval.py run several times: (1) 16 P5a FAIL (3.9e-9 > 1e-9; evaluator used grid rows), fixed by using the update rows (A4.1); (2) pair rows had a borrowing bug; after fixing, S1 SoH 0.7 dE% and one metric failed marginally, so Python dt=1e-4 refinements for SoH 0.9/0.7 were run (A4.2); (3) S1 dist(t)/distance_km FAIL remains (8.4e-7 m = 3.9e-10 relative), traced to Modelica's accumulated distance (report section 4). Diagnostics run: DASSL with -maxStepSize=1e-3 (no change in the dist deficit), IDA event log, Python dt=2e-5 (still running at the time of this entry). Final protocol sha256 367f0c8364f4b7f68524cdff4ce38625c6d8a4f26becf18aa465afdff5f6a8f0.

## 2026-10-24 00:47:31 +0700 - Diagnostic result: Python dt=2e-5 (S1 fixed SoH 0.8)
dist_end py1e-3 2161.2843813718, py1e-4 2161.2843812220, py2e-5 2161.2843811638, Modelica(DASSL 1e-12) 2161.2843803824. Python moves by 5.8e-8 m from 1e-4 to 2e-5; Modelica is 7.8e-7 m below the 2e-5 value; Modelica speed within 1.4e-10 m/s of py2e-5; E_chem Modelica - py2e-5 = -1.45e-4 J. Conclusion: S1 distance FAIL is on the Modelica accumulator side; mechanism not established.

## 2026-10-24 00:47:31 +0700 - Final artifact hashes
Final state at report time.

| file | sha256 |
|---|---|
| `verification/controller-crosscheck-protocol.md` | 367f0c8364f4b7f68524cdff4ce38625c6d8a4f26becf18aa465afdff5f6a8f0 |
| `verification/controller-port-design.md` | ed83526da47f8ecf6899a12f037da415961e46c6a0c12266409065ea5470b3b1 |
| `verification/references/controller_gains.json` | 29c4df2048aaea177f0e7876af4138b7ac1a917665dcc54f536400cda495a310 |
| `verification/references/python_dt_study.json` | 82f485e1aab09004b4be8d81835f4a17c6aa4809e345cb019083fd91fc471516 |
| `verification/modelica/controller_generated_inputs.json` | 99533ed498957434482f970366f95528b3daba1896487cbdf06754cfe699a54c |
| `verification/Invoke-OpenModelica.ps1` | e69f16113e8f690df6f5fc309fe2ad11fe1f4dd5c315687b5991f6ad948d88e3 |
| `verification\modelica\EurekaPlant\InverseS1.mo` | af2ef1590e72f6bdd119fbadb91ba9d9538ff913cc10b69d69794c548dbb75f5 |
| `verification\modelica\EurekaPlant\InverseS2.mo` | cad74dd65a9691442ce9ca1b6b5bc61962d5da6d5566cc68443cbe5f42ee1400 |
| `verification\modelica\EurekaPlant\InverseTracking.mo` | 1e56ff93fc0ed7a243d5f3ae72dc61574b07600d86a9905b06e1cc980e9b1da2 |
| `verification\modelica\EurekaPlant\Parameters.mo` | 806f6600bba08b9da8d1a5dd37100fe13fab1fc37c496b9f62b66fa8745a9463 |
| `verification\modelica\EurekaPlant\Plant.mo` | 41e6b28e2bb7f24dc962dcdf7a4517fb290cdc58ceb1330cc643c60ce00e3bab |
| `verification\modelica\EurekaPlant\Profiles.mo` | 26357ad31d9834a1503f14789cfa50ba09b21e1242c9203a0ed3003c58aa2021 |
| `verification\modelica\EurekaPlant\Tests\CoastDown.mo` | 4720472751afd100acfbd31cf51995033a2af1352e44113a9ce7095a1c701bdf |
| `verification\modelica\EurekaPlant\Tests\OpenLoop66.mo` | 5c968b3529fa79cdae37433301dc777023b696ec4ee8435734f22c4b025003c0 |
| `verification\modelica\EurekaPlant\Tests\StaticPoint.mo` | 469a2b06248a382d052d87bcd40e088f69cbb8c2c26c33c7f04f4a88d2aaab5d |
| `verification\modelica\EurekaPlant\Tests\package.mo` | fc25a474c0dc8db1ee125b73ae11b845bad405f293a0c690c83219aaa2a46471 |
| `verification\modelica\EurekaPlant\package.mo` | 4ad7486acb4b0302808101a8b7d9ac9ff55dc77e01782b152dbbce6e64905bc1 |
| `verification\modelica\EurekaController\Cases.mo` | b27ad368620219b96c0ab7eab5e141bcafbf52ff45196b57a02037d1e8d9374d |
| `verification\modelica\EurekaController\ClosedLoop.mo` | b9c8ce3f609c25b02a6728fa00323ea4601e1c68c3f75f3cd293947bed9c7be2 |
| `verification\modelica\EurekaController\ControllerProfiles.mo` | db3f4c1fda4bebcc6ca7456e3604096bda3df59b1cfc3701175fddb96a3547b3 |
| `verification\modelica\EurekaController\SampledLqr.mo` | 7e4d78c970fc1ba46fa6681d6d53302345934e5dd247a7a5070be2afcd9992d9 |
| `verification\modelica\EurekaController\Tests\ControllerStepSemantics.mo` | 71cf163a09aeb7f45dc1c453596d466e29850dcb7bfedaa352439a3838e12280 |
| `verification\modelica\EurekaController\Tests\ControllerUnit.mo` | 5349098a1ab551fc42fe39e8761a3b0bee9dc29bd2c4df140693ee611116608b |
| `verification\modelica\EurekaController\Tests\ControllerUnitStepOriginal.mo` | 6d2000260d521e2696a4c3af4425295726d194d81021e8f37cbb7f1f2a070cad |
| `verification\modelica\EurekaController\Tests\package.mo` | d8f9fea785471910472d1b413b56ba9f09dc27927440b8a239b6cc6259e627c0 |
| `verification\modelica\EurekaController\package.mo` | 96a7506d23d03b9fe7cb20a8245d24ed43021800b1fdf9adf8e5426bd2396b3e |
| `verification\scripts\controller_eval.py` | 935276e5d1e59c5f6db6fcd0a55ef2fa374a51569633768f5398af0b2b0fd4a3 |
| `verification\scripts\controller_gain_design.py` | 422081ee19282212077897e95f7cd8b1a548970bc72a4ab625228f4485abd5f4 |
| `verification\scripts\controller_metrics.py` | c320fbb67ea4eb01dee30875238b3227d45f1d68b12d0a95c837c12dac817c69 |
| `verification\scripts\controller_prelim_checks.py` | 08b13e6bfa802e2e0f3251079f646c6840fab84966981a50bebf7ccd17391c85 |
| `verification\scripts\controller_ptune_study.py` | e3331ad2391219a0c136c9e2dd4b37143eae618d77ff758729b7e8d97efed6fb |
| `verification\scripts\controller_results_append.py` | fabebf3c414749b1d8dd8f77b58ef26eda7fc4d0c7c02f4ae408258b16efc3f7 |
| `verification\scripts\controller_series.py` | c70a12cb6cd54c81bfe84f4d49514ad7e22de5ba1fdc0ac5d52f77cc525e2995 |
| `verification\scripts\controller_step_tests.py` | 43500b40d52244937c8af0341a008c0261770f3cb9f43342d4ba73f66e79f342 |
| `verification\scripts\controller_tolerances.py` | 3429485cb7ea9d28049c9a26ff5cafa2ef26f0f0f6a96a73ba151f80c5c79fc3 |
| `verification/scripts/python_reference_runs.py` | d0cc743fac5d649e873a4b347402122ebcb5a01831f6eb7e32b89a7ef5f4d2df |
| `verification/scripts/generate_controller_models.py` | 6336047cfd7b4c48723302cd7c2e7f45cd3ba066534db5839d2a596c35cef474 |
| `verification/scripts/generate_controller_case_scripts.py` | 77625e17de453757fa7bd03392db8ff4e2b38b9a8fa630228480bc941fc96624 |
| `verification/references/controller_solver_selection.json` | 5d46973e1fe5c23fdece84c4e773e28c5fff49eba7f0a13181644d26e1c4fb01 |
| `verification/modelica/scripts/controller_cases.json` | 31c858476c7a6de3e201db07a2d7fbf79dacbde901d34903aa150c7d2bbc3821 |
