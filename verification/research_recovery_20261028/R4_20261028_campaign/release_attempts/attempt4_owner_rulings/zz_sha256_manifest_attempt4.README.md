# Release attempt 4 SHA-256 manifest: scope and self-exclusion

`zz_sha256_manifest_attempt4.csv` has the columns `path`, `bytes` and `sha256`. Paths are relative to this attempt directory, use `/` separators and are sorted. The manifest was written last in the AMB-29(a) / AMB-31 owner-rulings task (2026-10-28).

**Excluded:**

| File | Reason |
|---|---|
| `zz_sha256_manifest_attempt4.csv` | a file cannot contain its own hash. Its SHA-256 is recorded in `R4_20261028_pilot/logs/zz_campaign_attempt4_manifest_sha256.txt` |
| `__pycache__/`, `*.pyc` | none exist (Python ran with `-B`) |

**Included:** everything else in this directory.

**Not covered:** the rest of the campaign directory. Release attempt 2, at the campaign root, has `zz_sha256_manifest_release.csv`; release attempt 3 has `release_attempts/attempt3_amendment2/zz_sha256_manifest_attempt3.csv`.

**Rule:** no manifest is overwritten. A later state is a new attempt directory.
