// NEGATIVE CONTROLS. Deliberately wrong models, kept apart from the authoritative package EurekaPlant.
// Each must be detected by the corresponding check (see verification/independent-model-report.md).
// This file never modifies EurekaPlant; it only extends its parameter model.

model WrongUnitForce "Unit error: a power assigned to a force"
  parameter Real P(unit = "W") = 1000;
  Real F(unit = "N");
equation
  F = P;
end WrongUnitForce;

model WrongTractionUnits "Unit error: traction built from motor speed instead of a torque-to-force relationship"
  extends EurekaPlant.Parameters;
  parameter Real T(unit = "N.m") = 10;
  parameter Real omega(unit = "1/s") = 100;
  Real F(unit = "N");
equation
  F = G*T*omega/r_w;
end WrongTractionUnits;

model NegCoastDownWrongBranch "Coast-down with the gear efficiency applied as a multiplier while regenerating (wrong direction of power flow)"
  extends EurekaPlant.Parameters;
  final parameter Real M_eff(unit = "kg") = M + J_m*G^2/r_w^2;
  final parameter Real gr(unit = "1/m") = G/r_w;
  Real v(unit = "m/s", start = 13.0, fixed = true);
  Real omega(unit = "1/s");
  Real F_w(unit = "N");
  Real F_rr(unit = "N");
  Real F_aero(unit = "N");
equation
  omega = gr*v;
  F_w = gr*eta_g*(0 - B_m*omega) "wrong: t_s < 0 here, so the efficiency must divide";
  F_rr = C_rr*M*g*tanh(v/v_eps);
  F_aero = 0.5*rho*C_d*A_f*v*v;
  M_eff*der(v) = F_w - F_rr - F_aero;
end NegCoastDownWrongBranch;

model WrongUnitChargeIntegral "Probe: does omc check an equation involving the unit A.h? der(q) with q in A.h and I in A is dimensionally inconsistent (A.h/s versus A)"
  parameter Real I(unit = "A") = 1;
  Real q(unit = "A.h", start = 0, fixed = true);
equation
  der(q) = I;
end WrongUnitChargeIntegral;
