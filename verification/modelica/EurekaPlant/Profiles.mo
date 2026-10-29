within EurekaPlant;
package Profiles "GENERATED from configs/cycles/profiles.yaml: segment lists and a knot builder written in Modelica"
  constant Integer S1_n = 23;
  constant Integer S1_kind[S1_n] = {1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1} "1 = hold (idle or cruise), 2 = ramp to target";
  constant Real S1_p[S1_n] = {10.0, 0.8, 15.0, -0.8, 15.0, 1.0, 30.0, -0.6, 10.0, -0.9, 20.0, 0.7, 40.0, -0.5, 20.0, 0.5, 25.0, -1.0, 15.0, 1.0, 10.0, -0.8, 10.0} "hold: duration [s]; ramp: acceleration [m/s2]";
  constant Real S1_target[S1_n] = {0.0, 20.0/3.6, 0.0, 0.0/3.6, 0.0, 35.0/3.6, 0.0, 15.0/3.6, 0.0, 0.0/3.6, 0.0, 50.0/3.6, 0.0, 30.0/3.6, 0.0, 45.0/3.6, 0.0, 0.0/3.6, 0.0, 25.0/3.6, 0.0, 0.0/3.6, 0.0} "ramp: target speed [m/s]; hold: unused";
  constant Integer S2_n = 25;
  constant Integer S2_kind[S2_n] = {1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1} "1 = hold (idle or cruise), 2 = ramp to target";
  constant Real S2_p[S2_n] = {8.0, 0.6, 8.0, -0.7, 12.0, 0.6, 12.0, -0.7, 5.0, 0.6, 6.0, -0.7, 10.0, 0.6, 15.0, -0.7, 15.0, 0.6, 10.0, -0.7, 6.0, 0.6, 8.0, -0.7, 8.0} "hold: duration [s]; ramp: acceleration [m/s2]";
  constant Real S2_target[S2_n] = {0.0, 10.0/3.6, 0.0, 0.0/3.6, 0.0, 15.0/3.6, 0.0, 0.0/3.6, 0.0, 20.0/3.6, 0.0, 0.0/3.6, 0.0, 25.0/3.6, 0.0, 0.0/3.6, 0.0, 15.0/3.6, 0.0, 0.0/3.6, 0.0, 20.0/3.6, 0.0, 0.0/3.6, 0.0} "ramp: target speed [m/s]; hold: unused";
  function knotTimes "Knot times [s] of a piecewise-linear profile"
    input Integer n;
    input Integer kind[n];
    input Real p[n];
    input Real target[n];
    output Real t[n + 1];
  protected
    Real v;
  algorithm
    t[1] := 0.0;
    v := 0.0;
    for i in 1:n loop
      if kind[i] == 1 then
        t[i + 1] := t[i] + p[i];
      else
        t[i + 1] := t[i] + (target[i] - v)/p[i];
        v := target[i];
      end if;
    end for;
  end knotTimes;
  function knotSpeeds "Knot speeds [m/s] of a piecewise-linear profile"
    input Integer n;
    input Integer kind[n];
    input Real p[n];
    input Real target[n];
    output Real v[n + 1];
  algorithm
    v[1] := 0.0;
    for i in 1:n loop
      if kind[i] == 1 then
        v[i + 1] := v[i];
      else
        v[i + 1] := target[i];
      end if;
    end for;
  end knotSpeeds;
end Profiles;
