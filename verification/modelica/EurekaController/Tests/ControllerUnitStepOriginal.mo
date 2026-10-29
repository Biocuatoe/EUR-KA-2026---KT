within EurekaController.Tests;
model ControllerUnitStepOriginal "RECONSTRUCTED original controller-logic test (step inputs at exactly 4 s and 8 s), kept because its first evaluation FAILED; see verification/controller-crosscheck-runlog.md"
  parameter Real K_e = 196.035338058519;
  parameter Real K_T = 0.3506849472210603;
  parameter Real K_z = 150.8545190065969;
  Real v(unit = "m/s");
  Real T(unit = "N.m");
  Real v_ref(unit = "m/s");
  SampledLqr ctrl(Ts = 0.01, K_e = K_e, K_T = K_T, K_z = K_z, T_max = 85, P_max = 18000, gr = 6.5/0.28);
equation
  v = 13;
  v_ref = if time < 4 then 13.3 else 12.95;
  T = if time < 4 then 0 elseif time < 8 then -300 else 0;
  ctrl.v = v;
  ctrl.T = T;
  ctrl.v_ref = v_ref;
end ControllerUnitStepOriginal;
