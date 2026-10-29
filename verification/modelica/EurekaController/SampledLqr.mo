within EurekaController;
block SampledLqr "Zero-order-hold state-feedback law u = -(K_e e + K_T T + K_z z) with conditional anti-windup, executed at t_k = k*Ts"
  parameter Real Ts(unit = "s") = 0.01 "sample time";
  parameter Real K_e(unit = "N.m.s/m") = 0 "gain on e = v - v_ref";
  parameter Real K_T(unit = "1") = 0 "gain on the delivered torque state";
  parameter Real K_z(unit = "N.m/m") = 0 "gain on z = integral of e";
  parameter Real T_max(unit = "N.m") = 85 "torque ceiling";
  parameter Real P_max(unit = "W") = 18000 "power ceiling";
  parameter Real gr(unit = "1/m") = 1 "motor speed per vehicle speed, G/r_w";
  parameter Real eps_w(unit = "1/s") = 1e-6 "floor on motor speed in P_max/omega";
  input Real v(unit = "m/s") "measured speed (plant state, exact)";
  input Real T(unit = "N.m") "delivered torque (plant state, exact)";
  input Real v_ref(unit = "m/s") "reference speed";
  discrete Real u(unit = "N.m", start = 0, fixed = true) "held torque request";
  discrete Real z(unit = "m", start = 0, fixed = true) "integral state for the NEXT sample";
  discrete Real e_k(unit = "m/s", start = 0, fixed = true);
  discrete Real z_used(unit = "m", start = 0, fixed = true) "integral state used in u at this sample";
  discrete Real T_lim_k(unit = "N.m", start = 0, fixed = true);
  discrete Boolean sat_k(start = false, fixed = true) "u > T_lim_k";
  discrete Integer k_ctrl(start = 0, fixed = true) "updates executed";
  discrete Real se2(unit = "m2/s2", start = 0, fixed = true) "running sum of e_k^2";
equation
  when sample(0, Ts) then
    e_k = v - v_ref;
    z_used = pre(z);
    T_lim_k = min(T_max, P_max/max(gr*max(v, 0), eps_w));
    u = -(K_e*e_k + K_T*T + K_z*pre(z));
    sat_k = u > T_lim_k;
    z = if sat_k and e_k < 0 then pre(z) else pre(z) + Ts*e_k;
    k_ctrl = pre(k_ctrl) + 1;
    se2 = pre(se2) + e_k^2;
  end when;
end SampledLqr;
