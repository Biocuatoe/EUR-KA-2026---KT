import fastsim as fsim
veh = fsim.Vehicle.from_resource("2022_Renault_Zoe_ZE50_R135.yaml")
cyc = fsim.Cycle.from_resource("udds.csv")
print("veh_type:", veh.veh_type, "| cycle len:", cyc.len())
sd = fsim.SimDrive(veh, cyc)
ok = sd.run()
print("run returned:", ok)
df = sd.to_dataframe()
print(type(df).__name__, df.shape)
cols = [c for c in df.columns if any(k in c.lower() for k in ("energy", "soc", "pwr_out", "dist", "speed", "time"))]
print(len(df.columns), "columns; relevant:")
for c in cols: print("  ", c)
