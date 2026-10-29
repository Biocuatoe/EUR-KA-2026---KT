# Pilot SHA-256 manifest v7: scope and self-exclusion policy

`zz_sha256_manifest_v7.csv` has the columns `path`, `bytes` and `sha256`. Paths are relative to this pilot directory, use `/` separators and are sorted. It was written last in the task that implemented the remaining owner rulings and prepared release attempts 5 and 6 (2026-10-28).

**Excluded:**

| File | Reason |
|---|---|
| `zz_sha256_manifest_v7.csv` | a file cannot contain its own hash. Its SHA-256 is in `logs/zz_manifest_v7_sha256.txt` |
| `logs/zz_manifest_v7_sha256.txt` | written after the manifest |
| `__pycache__/`, `*.pyc` | none exist |

**Included:** everything else, including:
- the v1–v6 manifests and READMEs, unchanged;
- every test log, failed and targeted runs included (runs 1–24, 23a, 23b, 24a), and every readiness gate (v2–v10);
- the archives rev0 to rev8, including `rev7_attempt4_20261028_1405` and `rev8_attempt5_20261028_1540`;
- every review report, including the attempt-5 review (`review/R5_…`), its erratum, and the attempt-6 verification (`review/V6_…`);
- the amendment 2 draft rev3 and candidates rev4, rev5 and rev6, each with its `.sha256.txt`;
- reports 14, 16 and 17, document 15, and the v5, v6 and v7 start-state and integrity logs.

**Not covered:** the campaign directory, which has its own manifests:

| Manifest | Covers | SHA-256 recorded in |
|---|---|---|
| `../R4_20261028_campaign/zz_sha256_manifest_release.csv` | release attempt 2 at the root, plus attempt 1 | `logs/zz_campaign_release_manifest_sha256.txt` |
| `../R4_20261028_campaign/release_attempts/attempt3_amendment2/zz_sha256_manifest_attempt3.csv` | release attempt 3 | `logs/zz_campaign_attempt3_manifest_sha256.txt` |
| `../R4_20261028_campaign/release_attempts/attempt4_owner_rulings/zz_sha256_manifest_attempt4.csv` | release attempt 4 | `logs/zz_campaign_attempt4_manifest_sha256.txt` |
| `../R4_20261028_campaign/release_attempts/attempt5_owner_rulings/zz_sha256_manifest_attempt5.csv` | release attempt 5 | `logs/zz_campaign_attempt5_manifest_sha256.txt` |
| `../R4_20261028_campaign/release_attempts/attempt6_review_fixes/zz_sha256_manifest_attempt6.csv` | release attempt 6 | `logs/zz_campaign_attempt6_manifest_sha256.txt` |

**Rule:** no manifest is overwritten. A later state gets `v8`.
