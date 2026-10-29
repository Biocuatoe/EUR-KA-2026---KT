within EurekaPlant.Tests;
model StaticPoint "Constant torque request from a chosen initial (v, T); values are set per run with -override"
  extends Plant;
  parameter Real T_hold(unit = "N.m") = 0 "constant torque request";
equation
  T_ref = T_hold;
end StaticPoint;
