# Pilot SHA-256 manifest v2: scope and self-exclusion policy

**Files.**
- `zz_sha256_manifest_v2.csv` has columns `path`, `bytes` and `sha256`, with paths relative to this pilot directory and `/` separators.
- It was written last, after every other readiness file, by the command in `logs/zz_manifest_v2_command.txt`.

**Scope.** It covers every file under `R4_20261028_pilot/`, with these exclusions:

| Excluded | Reason |
|---|---|
| `zz_sha256_manifest_v2.csv` itself | A file cannot contain its own hash. Its SHA-256 is reported in the final readiness message and in `logs/zz_manifest_v2_sha256.txt`, which is written after it and so is outside it too |
| `logs/zz_manifest_v2_sha256.txt` | written after the manifest, for the reason above |
| `__pycache__/` and `*.pyc` | none exist; bytecode is disabled everywhere (`-B`) |

**Everything else is included**, in particular:
- `zz_sha256_manifest.csv`, the **v1 manifest**, unchanged since 01:35. Checked after all readiness writes:
  - 39 of its 51 entries still verify in place, including all 13 smoke-test output files (D4).
  - The other 12 were superseded by the readiness work: `02_protocol_ambiguity_register.md`, `03_protocol_v1_amendment_1_DRAFT.md`, `code/r4h3/{__init__,closedloop,evaluator,frozen,slice,traces,validator}.py`, and `code/tests/{test_closedloop,test_evaluator,test_scope}.py`.
  - Each of those 12 has an archived copy in `archive/rev0_20261028_0135/` that carries exactly the v1 hash (`ARCHIVE_INDEX.csv`). Per-file before and after hashes: `logs/zz_code_changes_rev0_to_rev1.csv`.
- the smoke-test outputs, which are unchanged (D4);
- the readiness development outputs, the dry run, logs, configuration, code, tests and inputs;
- this README.

**Versioning rule.** No manifest is overwritten. A later state of this directory gets `zz_sha256_manifest_v3.csv` with its own README.

**Verification.** From this directory, recompute the SHA-256 of each listed `path`, reading the file in binary mode, and compare it with the `sha256` column. `sha256sum -c` cannot read this CSV format directly. Any difference means the file changed after the manifest was written.
