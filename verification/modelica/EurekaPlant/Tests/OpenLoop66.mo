within EurekaPlant.Tests;
model OpenLoop66 "Deterministic 66 s open-loop torque schedule exercising the limits, regeneration, friction braking and standstill (SoH 0.8)"
  extends Plant(SoH = 0.8);
  parameter Integer nS = 7;
  parameter Real tsw[nS] = {0, 10, 20, 30, 38, 46, 56} "interval start times [s]";
  parameter Real Tval[nS] = {85, 20, 0, -40, -200, -20, 10} "torque request in each interval [N.m]";
  Integer k "current interval: 1 + number of switch times already passed (time events)";
equation
  k = 1 + sum(if time >= tsw[i] then 1 else 0 for i in 2:nS);
  T_ref = Tval[k];
end OpenLoop66;
