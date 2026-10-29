within EurekaPlant;
model InverseS2 "Ideal tracking of the synthetic profile S2"
  extends InverseTracking(n = Profiles.S2_n, kind = Profiles.S2_kind, p = Profiles.S2_p, target = Profiles.S2_target);
end InverseS2;
