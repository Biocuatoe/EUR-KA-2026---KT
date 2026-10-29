model CoastDown "Smoke test only: linear-drag coast-down, closed form v0*exp(-c*t/m). Not the project vehicle model."
  parameter Real m = 850 "kg";
  parameter Real c = 25 "N.s/m";
  parameter Real v0 = 10 "m/s";
  Real v(start = v0, fixed = true) "m/s";
  Real v_exact = v0*exp(-c*time/m) "m/s";
  Real err = v - v_exact "m/s";
equation
  m*der(v) = -c*v;
end CoastDown;
