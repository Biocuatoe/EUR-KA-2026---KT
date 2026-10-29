# Pilot SHA-256 manifest v3: scope and self-exclusion policy

`zz_sha256_manifest_v3.csv` has columns `path`, `bytes` and `sha256`. Paths are relative to this pilot directory, with `/` separators, sorted. It was written last in the rev2 task (2026-10-28).

**Excluded:**

| File | Reason |
|---|---|
| `zz_sha256_manifest_v3.csv` | a file cannot contain its own hash. Its SHA-256 is in `logs/zz_manifest_v3_sha256.txt` |
| `logs/zz_manifest_v3_sha256.txt` | written after the manifest |
| `__pycache__/`, `*.pyc` | none exist (bytecode disabled with `-B` everywhere) |

**Included:** everything else. That covers the v1 and v2 manifests and their READMEs (kept unchanged), every test log (runs 1–10, including failing runs 1, 4 and 6 and the run-9 note), the smoke test, all development outputs, both dry runs of this task, the archives rev0 and rev1, the code, config, inputs, and every report and draft.

**Not covered:** the campaign directory `../R4_20261028_campaign/`. It has its own manifest, `../R4_20261028_campaign/zz_sha256_manifest.csv`, which also excludes itself; its SHA-256 is in `logs/zz_campaign_dir_manifest_sha256.txt`.

**Rules:**
- No manifest is overwritten. A later state gets `zz_sha256_manifest_v4.csv`.
- **Verification:** recompute each listed file's SHA-256 in binary mode and compare it with the `sha256` column.
