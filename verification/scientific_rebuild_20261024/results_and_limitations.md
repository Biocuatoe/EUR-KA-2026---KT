# Results and limitations (rebuild 2026-10-24)

The authoritative statement of results, mechanisms, sensitivity, verdicts and limitations is
`analysis_report_20261024.md`. In short:

1. **No practical difference.** In 112 matched comparisons, SoH-scheduled LQR vs fixed LQR
   changed energy per km by −0.0019 % to +0.034 %, with an RMSE ratio of 1.000–1.022. The
   pre-registered verdict is NO PRACTICAL DIFFERENCE in all 112. This holds for the legacy
   plant, for SoH-independent battery limits, and for assumed SoH-proportional current limits.
2. **A retuned fixed gain does better.** The fixed gain retuned once (F01) matched or beat the
   scheduled controller in all 28 cycle × case combinations.
3. **Ageing changes behaviour only under an assumption.** It changes vehicle behaviour
   materially only when the current limits are *assumed* to fall with SoH. Then tracking
   degrades, regeneration is lost and cycle distance falls short, equally for both
   controllers.
4. **Resistance growth cannot limit the drive.** With the thesis's resistance-growth law, the
   battery voltage window cannot limit the drive (analytical bound; confirmed in simulation).
5. **Headline claims:** 12.5 % energy is contradicted within the tested model; 15.3 % fade is
   unresolved, because no fade model exists.

**Limitations:**
- a hypothetical vehicle with assumed or unverified parameters;
- constant efficiencies and constant OCV;
- assumed battery window and C-rates;
- SoH known exactly;
- US06, and UDDS under the stricter class-C limits, exceed the vehicle's capability;
- no fade model;
- no physical validation;
- no independent human replication.

See §7 of the analysis report.
