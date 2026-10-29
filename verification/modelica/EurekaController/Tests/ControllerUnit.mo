within EurekaController.Tests;
model ControllerUnit "SampledLqr driven by prescribed signals: checks the control law, the integral update, saturation and the anti-windup rule against an independent evaluation"
  parameter Real K_e = 196.035338058519;
  parameter Real K_T = 0.3506849472210603;
  parameter Real K_z = 150.8545190065969;
  Real v(unit = "m/s");
  Real T(unit = "N.m");
  Real v_ref(unit = "m/s");
  SampledLqr ctrl(Ts = 0.01, K_e = K_e, K_T = K_T, K_z = K_z, T_max = 85, P_max = 18000, gr = 6.5/0.28);
equation
  // inputs are continuous in time (ramps), so the value a sample sees does not depend on whether the sample time lies a few 1e-13 s before or after a ramp corner
  // phase A (t < 4): e = -0.3, T = 0 -> request rises with |z| until the 59.6 N.m limit at 13 m/s is hit while e < 0 (frozen integral)
  // phase B (4.5 <= t < 8): e = +0.05, T = -300 -> request above the limit with e > 0 (integral must keep integrating)
  // phase C (t >= 9): e = +0.05, T = 0 -> request back below the limit
  v = 13;
  v_ref = 13.3 - 0.35*min(max((time - 4)/0.5, 0), 1);
  T = -300*min(max((time - 4)/0.5, 0), 1) + 300*min(max((time - 8)/1.0, 0), 1);
  ctrl.v = v;
  ctrl.T = T;
  ctrl.v_ref = v_ref;
end ControllerUnit;
