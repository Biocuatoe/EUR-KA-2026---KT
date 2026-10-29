within EurekaController;
package ControllerProfiles "GENERATED from configs/cycles/profiles.yaml (same encoding as EurekaPlant.Profiles): P-TUNE, S1, S2"
  constant Integer PTUNE_n = 11;
  constant Integer PTUNE_kind[PTUNE_n] = {1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1};
  constant Real PTUNE_p[PTUNE_n] = {5.0, 1.0, 20.0, 1.0, 20.0, -1.0, 8.0, 0.5, 15.0, -0.8, 5.0};
  constant Real PTUNE_target[PTUNE_n] = {0.0, 20.0/3.6, 0.0, 40.0/3.6, 0.0, 0.0/3.6, 0.0, 30.0/3.6, 0.0, 0.0/3.6, 0.0};
  constant Integer S1_n = 23;
  constant Integer S1_kind[S1_n] = {1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1};
  constant Real S1_p[S1_n] = {10.0, 0.8, 15.0, -0.8, 15.0, 1.0, 30.0, -0.6, 10.0, -0.9, 20.0, 0.7, 40.0, -0.5, 20.0, 0.5, 25.0, -1.0, 15.0, 1.0, 10.0, -0.8, 10.0};
  constant Real S1_target[S1_n] = {0.0, 20.0/3.6, 0.0, 0.0/3.6, 0.0, 35.0/3.6, 0.0, 15.0/3.6, 0.0, 0.0/3.6, 0.0, 50.0/3.6, 0.0, 30.0/3.6, 0.0, 45.0/3.6, 0.0, 0.0/3.6, 0.0, 25.0/3.6, 0.0, 0.0/3.6, 0.0};
  constant Integer S2_n = 25;
  constant Integer S2_kind[S2_n] = {1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1};
  constant Real S2_p[S2_n] = {8.0, 0.6, 8.0, -0.7, 12.0, 0.6, 12.0, -0.7, 5.0, 0.6, 6.0, -0.7, 10.0, 0.6, 15.0, -0.7, 15.0, 0.6, 10.0, -0.7, 6.0, 0.6, 8.0, -0.7, 8.0};
  constant Real S2_target[S2_n] = {0.0, 10.0/3.6, 0.0, 0.0/3.6, 0.0, 15.0/3.6, 0.0, 0.0/3.6, 0.0, 20.0/3.6, 0.0, 0.0/3.6, 0.0, 25.0/3.6, 0.0, 0.0/3.6, 0.0, 15.0/3.6, 0.0, 0.0/3.6, 0.0, 20.0/3.6, 0.0, 0.0/3.6, 0.0};
end ControllerProfiles;
