within EurekaPlant;
model InverseS1 "Ideal tracking of the synthetic profile S1"
  extends InverseTracking(n = Profiles.S1_n, kind = Profiles.S1_kind, p = Profiles.S1_p, target = Profiles.S1_target);
end InverseS1;
