within EurekaPlant.Tests;
model CoastDown "Coast-down from 13 m/s with zero torque request (project coast-down case)"
  extends Plant(v_init = 13.0, T_init = 0.0);
equation
  T_ref = 0;
end CoastDown;
