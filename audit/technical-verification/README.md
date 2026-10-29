# Preserved independent-check scripts (technical foundation audit)

These are exact, unmodified copies of the two scripts that produced checks IC-01 to IC-15
of `technical-foundation-audit.md` (project root). They were copied on 2026-10-23 from the
session scratchpad, and no other location was searched.

| File | Bytes | SHA-256 (source and copy are identical) | Checks |
|---|---|---|---|
| `ind_checks_a.py` | 15235 | `c5cad625019ecceb3f352c63574c51d93f928f7018709e2e7cc846a8a57fd0db` | IC-01 to IC-09 (operating points, actuator headroom on the references, Pint dimensions, SymPy linearisation, controllability and PBH, symplectic-pencil DARE, margins and frozen-speed sweep, slow-variation bound, thesis arithmetic) |
| `ind_checks_b.py` | 15705 | `5e98b430deefbf4977e8f9d594b362abc2cc8df35583c4c36c8fe61135ff2080` | IC-10 to IC-15 (primary, S-C, S-B and S-D recomputation from the raw `.npz` files, inverse-dynamics ideal-tracking energy, common quadratic Lyapunov function) |

## How they were run

```
<project>\.venv\Scripts\python.exe -I ind_checks_a.py "<project root>" "<dir>\ic_a.json"
<project>\.venv\Scripts\python.exe -I ind_checks_b.py "<project root>" "<dir>\ic_b.json"
```

- `ind_checks_b.py` must run after `ind_checks_a.py`. It reads `ic_a.json` from the
  directory of its own output path (line 248 of the script).
- Both scripts read project files only (`configs/`, `artifacts/raw/`, `artifacts/tables/`) and
  write only the JSON path they are given.
- `ind_checks_a.py` imports the project package `eureka` (`eureka.params`, `eureka.plant`,
  `eureka.controllers`) to compare against it, so they must run in the locked `.venv`, not in
  `verification\python-env`.
- Parameter values are read straight from `configs/parameters.yaml` with PyYAML. The physics,
  linearisation, DARE and margin calculations are separate implementations.

## What is not preserved here

- IC-16 (integrator mismatch, peak and RMS current, S-D torque jitter) and the γ-grid extension
  of IC-15 were run as inline commands and are not in these scripts. The audit report describes
  their results, but no script exists to rerun them exactly.
- `make_matrix.py`, which generated `technical-claim-matrix.csv`, was not in the two paths
  named for preservation and was not copied. The CSV itself is in the project root.
- The JSON outputs (`ic_a.json`, `ic_b.json`) were not preserved. Rerunning the scripts
  regenerates them. Their numbers appear in the audit report.

## Caveat

Rerunning has not been done in this phase. The copies are byte-identical to the scripts that
produced the reported results, but whether the checks still pass at a later commit has not been tested.
