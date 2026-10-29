within EurekaController.Tests;
model ControllerStepSemantics "SampledLqr with piecewise-CONSTANT inputs whose steps lie mid-interval, 1e-6 s before an update, exactly at an update and 1e-6 s after an update"
  parameter Real K_e = 196.035338058519;
  parameter Real K_T = 0.3506849472210603;
  parameter Real K_z = 150.8545190065969;
  parameter Real ts[4] = {2.005, 5.999999, 8.0, 10.000001} "step times [s]: mid-interval; 1e-6 before the update at 6.00; exactly at the update at 8.00; 1e-6 after the update at 10.00";
  parameter Real vr[5] = {13.3, 13.1, 12.9, 13.2, 12.95} "reference speed after each step (first value before the first step)";
  parameter Real Tv[5] = {0, -50, -300, 0, -100} "delivered torque after each step";
  Integer idx "1 + number of steps already passed (time >= ts[i])";
  Real v(unit = "m/s");
  Real T(unit = "N.m");
  Real v_ref(unit = "m/s");
  SampledLqr ctrl(Ts = 0.01, K_e = K_e, K_T = K_T, K_z = K_z, T_max = 85, P_max = 18000, gr = 6.5/0.28);
equation
  idx = 1 + sum(if time >= ts[i] then 1 else 0 for i in 1:4);
  v = 13;
  v_ref = vr[idx];
  T = Tv[idx];
  ctrl.v = v;
  ctrl.T = T;
  ctrl.v_ref = v_ref;
end ControllerStepSemantics;
