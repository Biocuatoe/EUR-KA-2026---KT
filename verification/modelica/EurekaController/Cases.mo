within EurekaController;
package Cases "GENERATED from verification/references/controller_gains.json: one wrapper model per (profile, controller, SoH)"
  model PTUNE_fixed_soh080 "P-TUNE, fixed LQR, SoH 0.8"
    extends EurekaController.ClosedLoop(SoH = 0.8, K_e = 196.035338058519, K_T = 0.3506849472210603, K_z = 150.8545190065969,
      n = EurekaController.ControllerProfiles.PTUNE_n, kind = EurekaController.ControllerProfiles.PTUNE_kind,
      p = EurekaController.ControllerProfiles.PTUNE_p, target = EurekaController.ControllerProfiles.PTUNE_target);
  end PTUNE_fixed_soh080;
  model PTUNE_scheduled_soh080 "P-TUNE, scheduled LQR, SoH 0.8"
    extends EurekaController.ClosedLoop(SoH = 0.8, K_e = 184.3037169150638, K_T = 0.28187517263942446, K_z = 141.48409698840834,
      n = EurekaController.ControllerProfiles.PTUNE_n, kind = EurekaController.ControllerProfiles.PTUNE_kind,
      p = EurekaController.ControllerProfiles.PTUNE_p, target = EurekaController.ControllerProfiles.PTUNE_target);
  end PTUNE_scheduled_soh080;
  model S1_fixed_soh100 "S1, fixed LQR, SoH 1.0"
    extends EurekaController.ClosedLoop(SoH = 1.0, K_e = 196.035338058519, K_T = 0.3506849472210603, K_z = 150.8545190065969,
      n = EurekaController.ControllerProfiles.S1_n, kind = EurekaController.ControllerProfiles.S1_kind,
      p = EurekaController.ControllerProfiles.S1_p, target = EurekaController.ControllerProfiles.S1_target);
  end S1_fixed_soh100;
  model S1_scheduled_soh100 "S1, scheduled LQR, SoH 1.0"
    extends EurekaController.ClosedLoop(SoH = 1.0, K_e = 196.035338058519, K_T = 0.3506849472210603, K_z = 150.8545190065969,
      n = EurekaController.ControllerProfiles.S1_n, kind = EurekaController.ControllerProfiles.S1_kind,
      p = EurekaController.ControllerProfiles.S1_p, target = EurekaController.ControllerProfiles.S1_target);
  end S1_scheduled_soh100;
  model S1_fixed_soh090 "S1, fixed LQR, SoH 0.9"
    extends EurekaController.ClosedLoop(SoH = 0.9, K_e = 196.035338058519, K_T = 0.3506849472210603, K_z = 150.8545190065969,
      n = EurekaController.ControllerProfiles.S1_n, kind = EurekaController.ControllerProfiles.S1_kind,
      p = EurekaController.ControllerProfiles.S1_p, target = EurekaController.ControllerProfiles.S1_target);
  end S1_fixed_soh090;
  model S1_scheduled_soh090 "S1, scheduled LQR, SoH 0.9"
    extends EurekaController.ClosedLoop(SoH = 0.9, K_e = 189.906809498586, K_T = 0.31296528908150945, K_z = 146.00983572436985,
      n = EurekaController.ControllerProfiles.S1_n, kind = EurekaController.ControllerProfiles.S1_kind,
      p = EurekaController.ControllerProfiles.S1_p, target = EurekaController.ControllerProfiles.S1_target);
  end S1_scheduled_soh090;
  model S1_fixed_soh080 "S1, fixed LQR, SoH 0.8"
    extends EurekaController.ClosedLoop(SoH = 0.8, K_e = 196.035338058519, K_T = 0.3506849472210603, K_z = 150.8545190065969,
      n = EurekaController.ControllerProfiles.S1_n, kind = EurekaController.ControllerProfiles.S1_kind,
      p = EurekaController.ControllerProfiles.S1_p, target = EurekaController.ControllerProfiles.S1_target);
  end S1_fixed_soh080;
  model S1_scheduled_soh080 "S1, scheduled LQR, SoH 0.8"
    extends EurekaController.ClosedLoop(SoH = 0.8, K_e = 184.3037169150638, K_T = 0.28187517263942446, K_z = 141.48409698840834,
      n = EurekaController.ControllerProfiles.S1_n, kind = EurekaController.ControllerProfiles.S1_kind,
      p = EurekaController.ControllerProfiles.S1_p, target = EurekaController.ControllerProfiles.S1_target);
  end S1_scheduled_soh080;
  model S1_fixed_soh070 "S1, fixed LQR, SoH 0.7"
    extends EurekaController.ClosedLoop(SoH = 0.7, K_e = 196.035338058519, K_T = 0.3506849472210603, K_z = 150.8545190065969,
      n = EurekaController.ControllerProfiles.S1_n, kind = EurekaController.ControllerProfiles.S1_kind,
      p = EurekaController.ControllerProfiles.S1_p, target = EurekaController.ControllerProfiles.S1_target);
  end S1_fixed_soh070;
  model S1_scheduled_soh070 "S1, scheduled LQR, SoH 0.7"
    extends EurekaController.ClosedLoop(SoH = 0.7, K_e = 179.174299683759, K_T = 0.25598350090049127, K_z = 137.26847041089965,
      n = EurekaController.ControllerProfiles.S1_n, kind = EurekaController.ControllerProfiles.S1_kind,
      p = EurekaController.ControllerProfiles.S1_p, target = EurekaController.ControllerProfiles.S1_target);
  end S1_scheduled_soh070;
  model S2_fixed_soh100 "S2, fixed LQR, SoH 1.0"
    extends EurekaController.ClosedLoop(SoH = 1.0, K_e = 196.035338058519, K_T = 0.3506849472210603, K_z = 150.8545190065969,
      n = EurekaController.ControllerProfiles.S2_n, kind = EurekaController.ControllerProfiles.S2_kind,
      p = EurekaController.ControllerProfiles.S2_p, target = EurekaController.ControllerProfiles.S2_target);
  end S2_fixed_soh100;
  model S2_scheduled_soh100 "S2, scheduled LQR, SoH 1.0"
    extends EurekaController.ClosedLoop(SoH = 1.0, K_e = 196.035338058519, K_T = 0.3506849472210603, K_z = 150.8545190065969,
      n = EurekaController.ControllerProfiles.S2_n, kind = EurekaController.ControllerProfiles.S2_kind,
      p = EurekaController.ControllerProfiles.S2_p, target = EurekaController.ControllerProfiles.S2_target);
  end S2_scheduled_soh100;
  model S2_fixed_soh090 "S2, fixed LQR, SoH 0.9"
    extends EurekaController.ClosedLoop(SoH = 0.9, K_e = 196.035338058519, K_T = 0.3506849472210603, K_z = 150.8545190065969,
      n = EurekaController.ControllerProfiles.S2_n, kind = EurekaController.ControllerProfiles.S2_kind,
      p = EurekaController.ControllerProfiles.S2_p, target = EurekaController.ControllerProfiles.S2_target);
  end S2_fixed_soh090;
  model S2_scheduled_soh090 "S2, scheduled LQR, SoH 0.9"
    extends EurekaController.ClosedLoop(SoH = 0.9, K_e = 189.906809498586, K_T = 0.31296528908150945, K_z = 146.00983572436985,
      n = EurekaController.ControllerProfiles.S2_n, kind = EurekaController.ControllerProfiles.S2_kind,
      p = EurekaController.ControllerProfiles.S2_p, target = EurekaController.ControllerProfiles.S2_target);
  end S2_scheduled_soh090;
  model S2_fixed_soh080 "S2, fixed LQR, SoH 0.8"
    extends EurekaController.ClosedLoop(SoH = 0.8, K_e = 196.035338058519, K_T = 0.3506849472210603, K_z = 150.8545190065969,
      n = EurekaController.ControllerProfiles.S2_n, kind = EurekaController.ControllerProfiles.S2_kind,
      p = EurekaController.ControllerProfiles.S2_p, target = EurekaController.ControllerProfiles.S2_target);
  end S2_fixed_soh080;
  model S2_scheduled_soh080 "S2, scheduled LQR, SoH 0.8"
    extends EurekaController.ClosedLoop(SoH = 0.8, K_e = 184.3037169150638, K_T = 0.28187517263942446, K_z = 141.48409698840834,
      n = EurekaController.ControllerProfiles.S2_n, kind = EurekaController.ControllerProfiles.S2_kind,
      p = EurekaController.ControllerProfiles.S2_p, target = EurekaController.ControllerProfiles.S2_target);
  end S2_scheduled_soh080;
  model S2_fixed_soh070 "S2, fixed LQR, SoH 0.7"
    extends EurekaController.ClosedLoop(SoH = 0.7, K_e = 196.035338058519, K_T = 0.3506849472210603, K_z = 150.8545190065969,
      n = EurekaController.ControllerProfiles.S2_n, kind = EurekaController.ControllerProfiles.S2_kind,
      p = EurekaController.ControllerProfiles.S2_p, target = EurekaController.ControllerProfiles.S2_target);
  end S2_fixed_soh070;
  model S2_scheduled_soh070 "S2, scheduled LQR, SoH 0.7"
    extends EurekaController.ClosedLoop(SoH = 0.7, K_e = 179.174299683759, K_T = 0.25598350090049127, K_z = 137.26847041089965,
      n = EurekaController.ControllerProfiles.S2_n, kind = EurekaController.ControllerProfiles.S2_kind,
      p = EurekaController.ControllerProfiles.S2_p, target = EurekaController.ControllerProfiles.S2_target);
  end S2_scheduled_soh070;
end Cases;
