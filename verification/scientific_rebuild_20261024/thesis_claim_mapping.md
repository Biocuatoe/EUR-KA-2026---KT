# Thesis claim mapping (rebuild 2026-10-24)

This maps each thesis claim to the evidence produced here. Detail: `analysis_report_20261024.md`
and `claims_and_evidence.csv`. Thesis line numbers refer to
`data/processed/report/report.md`.

| Thesis claim | Location | Evidence in this study | Verdict | Wording the thesis can use |
|---|---|---|---|---|
| 12.5 % energy improvement | Abstract L9 | 112 matched S-vs-F pairs: ΔE from −0.0019 % to +0.034 % | Contradicted by the tested evidence | "In a documented simulation model, scheduling LQR weights on SoH changed energy per km by less than 0.04 %, which is no practical difference." |
| 15.3 % lower capacity fade | Abstract L9 | No fade model exists | Unresolved (not established) | Remove; state that no capacity-fade model was implemented |
| The adaptive LQR outperforms the fixed LQR as the battery ages | L790 | No improvement in any scenario; the retuned fixed gain F01 better in 28/28 | Contradicted by the tested evidence | "A single retuned fixed gain performed at least as well as the SoH-scheduled controller in every tested scenario." |
| Ageing degrades powertrain behaviour; fixed controllers become suboptimal | L575, L587 | Behaviour changes only with assumed SoH-proportional current limits, and equally for both controllers | Supported only under explicit assumptions (the behaviour change); contradicted (scheduling as the remedy) | "If the battery's current limits fall with SoH (an assumption), tracking and regeneration degrade; weight scheduling does not compensate." |
| Integral gain rises as SoH falls | L3328, Table 33 | The gains computed from the thesis's own weight laws fall (REG C28) | Contradicted | Publish the computed schedule |
| Stability under time-varying gains | L3218–3300 | Frozen-time stability verified for each SoH; no time-varying proof | Proof invalid; frozen-time result supported | "Each frozen-SoH design is stable; SoH varies over months, which is slow relative to the closed-loop dynamics (condition stated, not quantified)." |
| Six-benchmark comparison, Monte Carlo, ANOVA | Ch. 5, App. E | Not run here; only F, S and F01 compared | Unresolved (not reproduced) | Remove |
