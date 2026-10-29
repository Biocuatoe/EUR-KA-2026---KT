# Release attempt 10 SHA-256 manifest: scope and self-exclusion

`zz_sha256_manifest_attempt10.csv` has the columns `path`, `bytes` and `sha256`. Paths are relative to this attempt directory, use `/` separators and are sorted. The manifest was written last for this attempt, after the review report, the gate record and the attempt note.

**Excluded:**

| File | Reason |
|---|---|
| `zz_sha256_manifest_attempt10.csv` | a file cannot contain its own hash. Its SHA-256 is recorded in `R4_20261028_pilot/logs/zz_campaign_attempt10_manifest_sha256.txt` |
| `__pycache__/`, `*.pyc` | none exist (Python ran with `-B`) |

**Included:** everything else in this directory, including this README.

**Not covered:** the rest of the campaign directory. Each other release attempt has its own manifest, and attempt 2 at the campaign root has `zz_sha256_manifest_release.csv`.

**Rule:** no manifest is overwritten. Any later correction, R10-1 included, is a new attempt directory; this one stays as reviewed.
