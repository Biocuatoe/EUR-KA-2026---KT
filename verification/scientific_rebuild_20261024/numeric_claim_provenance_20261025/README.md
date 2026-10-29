# Numeric-claim provenance audit, 2026-10-25

**Question.** Can the computational origin of the thesis's 12.5 % ± 2.1 % energy and 15.3 % ± 2.8 % capacity-fade claims be recovered?

**Answer.** Not from anything inside the project root.

**Scope.** This is a read-only forensic audit:
- no simulation was run;
- nothing outside this folder was changed;
- no Git operation was performed;
- the thesis DOCX hash was verified unchanged.

| File | Content |
|---|---|
| `numeric_claim_provenance_report.md` | Findings, method, coverage, verdicts (start here) |
| `numeric_claim_traceability.csv` | 25 rows: each claim, body figure, provenance statement, literature lead and external lead, with status and evidence |
| `defence_wording_options.md` | Version A (provenance recovered and reproduced; gated) and Version B (current state) |
| `tools/thesis_trace.py` | Paragraph dump and pattern search of the DOCX (verifies SHA-256 first) |
| `tools/figure_geometry.py` | Readout of the vector geometry of Figures 9 and 11 |
| `tools/arithmetic_checks.py` | Ratios recomputed from printed numbers |
| `tools/provenance_inventory.py` | Walk of the whole root: dates, names, file types, claim strings |
| `outputs/` | Everything the tools write, plus attributed Tawfik et al. 2024 excerpts (CC BY 4.0) |

**To reproduce,** see report §9.
