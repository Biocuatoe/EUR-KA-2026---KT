within EurekaController;
model ClosedLoop "Sampled-data state-feedback LQR on the independent Modelica plant (design: verification/controller-port-design.md)"
  extends EurekaPlant.Plant;
  // controller configuration (gains are frozen artifacts: verification/references/controller_gains.json)
  parameter Real Ts(unit = "s") = 0.01 "controller sample time (zero-order hold)";
  parameter Real K_e(unit = "N.m.s/m") = 0 "gain on the velocity error e = v - v_ref";
  parameter Real K_T(unit = "1") = 0 "gain on the delivered torque state";
  parameter Real K_z(unit = "N.m/m") = 0 "gain on the integral of the velocity error";
  // reference profile (same representation as EurekaPlant.InverseTracking)
  parameter Integer n = 1 "number of profile segments";
  parameter Integer kind[n] = {1};
  parameter Real p[n] = {1.0};
  parameter Real target[n] = {0.0};
  parameter Real tk[n + 1] = EurekaPlant.Profiles.knotTimes(n, kind, p, target) "knot times";
  parameter Real vk[n + 1] = EurekaPlant.Profiles.knotSpeeds(n, kind, p, target) "knot speeds";
  Integer seg "current profile segment (time events at the knots)";
  Real v_ref(unit = "m/s") "reference speed, linear interpolation, held at its last value after the last knot (np.interp behaviour)";
  Real a_ref(unit = "m/s2");
  SampledLqr ctrl(Ts = Ts, K_e = K_e, K_T = K_T, K_z = K_z, T_max = T_max, P_max = P_max, gr = gr, eps_w = eps_w);
  Real P_batt(unit = "W") "battery-side chemical power V_oc*I";
equation
  seg = 1 + sum(if time >= tk[i] then 1 else 0 for i in 2:n);
  a_ref = (vk[seg + 1] - vk[seg])/(tk[seg + 1] - tk[seg]);
  v_ref = vk[seg] + a_ref*(min(time, tk[n + 1]) - tk[seg]);
  ctrl.v = v;
  ctrl.T = T;
  ctrl.v_ref = v_ref;
  T_ref = ctrl.u;
  P_batt = V_oc*I;
end ClosedLoop;
