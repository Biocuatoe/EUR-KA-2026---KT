# Release attempt 8 SHA-256 manifest: scope and self-exclusion

`zz_sha256_manifest_attempt8.csv` has the columns `path`, `bytes` and `sha256`. Paths are relative to this attempt directory, use `/` separators and are sorted. The manifest was written last for this attempt, after the review report, the gate record and the attempt note.

**Excluded:**

| File | Reason |
|---|---|
| `zz_sha256_manifest_attempt8.csv` | a file cannot contain its own hash. Its SHA-256 is recorded in `R4_20261028_pilot/logs/zz_campaign_attempt8_manifest_sha256.txt` |
| `__pycache__/`, `*.pyc` | none exist (Python ran with `-B`) |

**Included:** everything else in this directory, including this README.

**Not covered:** the rest of the campaign directory. Each other release attempt has its own manifest, and attempt 2 at the campaign root has `zz_sha256_manifest_release.csv`.

**Rule:** no manifest is overwritten. This attempt has 3 MAJOR review findings open, so the corrections are a new attempt directory (`../attempt9_review_fixes/`), and this one stays as reviewed.
