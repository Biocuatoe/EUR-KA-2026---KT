# Pilot SHA-256 manifest v4: scope and self-exclusion policy

`zz_sha256_manifest_v4.csv` has columns `path`, `bytes` and `sha256`. Paths are relative to this pilot directory, with `/` separators, sorted. It was written last in the owner-approval and release task (2026-10-28).

**Excluded:**

| File | Reason |
|---|---|
| `zz_sha256_manifest_v4.csv` | a file cannot contain its own hash. Its SHA-256 is in `logs/zz_manifest_v4_sha256.txt` |
| `logs/zz_manifest_v4_sha256.txt` | written after the manifest |
| `__pycache__/`, `*.pyc` | none exist |

**Included:** everything else, including the v1, v2 and v3 manifests and READMEs (unchanged), every test log (runs 1–14), every readiness gate (v2–v6), the archives rev0, rev1 and rev2, and every report.

**Not covered:** the campaign directory. It has its own manifests: `../R4_20261028_campaign/zz_sha256_manifest.csv` (pre-release, 2 files) and `zz_sha256_manifest_release.csv` (122 files). Their SHA-256s are in `logs/zz_campaign_dir_manifest_sha256.txt` and `logs/zz_campaign_release_manifest_sha256.txt`.

**Rule:** no manifest is overwritten. A later state gets `v5`.
