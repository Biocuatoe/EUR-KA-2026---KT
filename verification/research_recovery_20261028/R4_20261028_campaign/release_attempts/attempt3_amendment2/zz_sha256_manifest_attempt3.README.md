# Release attempt 3 SHA-256 manifest: scope and self-exclusion

`zz_sha256_manifest_attempt3.csv` has the columns `path`, `bytes` and `sha256`. Paths are relative to this attempt directory, use `/` separators and are sorted. The manifest was written last in the amendment 2 preparation task (2026-10-28).

**Excluded:**

| File | Reason |
|---|---|
| `zz_sha256_manifest_attempt3.csv` | a file cannot contain its own hash. Its SHA-256 is recorded outside this directory, in `R4_20261028_pilot/logs/zz_campaign_attempt3_manifest_sha256.txt` |
| `__pycache__/`, `*.pyc` | none exist (Python ran with `-B`) |

**Included:** everything else in this directory, including this README, `ATTEMPT_NOTE_attempt3.md`, `GATE_RECORD_attempt3.json`, the code, config and inputs copies, every log and the dry run.

**Not covered:** the rest of the campaign directory. Release attempt 2 at the campaign root keeps its own manifest, `zz_sha256_manifest_release.csv`; attempt 1 is covered by that manifest.

**Rule:** no manifest is overwritten. A later state of this attempt is a new attempt directory.
