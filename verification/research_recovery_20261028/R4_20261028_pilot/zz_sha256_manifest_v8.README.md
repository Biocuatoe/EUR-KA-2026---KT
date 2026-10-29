# Pilot SHA-256 manifest v8: scope and self-exclusion policy

`zz_sha256_manifest_v8.csv` has the columns `path`, `bytes` and `sha256`. Paths are relative to this pilot directory, use `/` separators and are sorted. It was written last in the task "Final Amendment 2 Decisions and Release Attempt 7" (2026-10-28).

**Excluded:**

| File | Reason |
|---|---|
| `zz_sha256_manifest_v8.csv` | a file cannot contain its own hash. Its SHA-256 is in `logs/zz_manifest_v8_sha256.txt` |
| `logs/zz_manifest_v8_sha256.txt` | written after the manifest |
| `__pycache__/`, `*.pyc` | none exist |

**Included:** everything else, including:
- the v1–v7 manifests and READMEs, unchanged;
- every test log, failed and targeted runs included (up to runs 25, 25a and 25b), and every readiness gate (v2–v11);
- the archives rev0 to rev9, including `rev9_attempt6_20261028_1727`;
- every review report, including `review/R7_attempt7_review_agent_report_20261028.md`;
- the amendment 2 draft rev3 and candidates rev4 to rev7, each with its `.sha256.txt`;
- reports 14, 16, 17, 18 and 19, document 15, and the v5 to v8 start-state and integrity logs.

**Not covered:** the campaign directory, which has its own manifests:

| Manifest | Covers | SHA-256 recorded in |
|---|---|---|
| `../R4_20261028_campaign/zz_sha256_manifest_release.csv` | release attempt 2 at the root, plus attempt 1 | `logs/zz_campaign_release_manifest_sha256.txt` |
| `../R4_20261028_campaign/release_attempts/attempt3_amendment2/zz_sha256_manifest_attempt3.csv` | release attempt 3 | `logs/zz_campaign_attempt3_manifest_sha256.txt` |
| `../R4_20261028_campaign/release_attempts/attempt4_owner_rulings/zz_sha256_manifest_attempt4.csv` | release attempt 4 | `logs/zz_campaign_attempt4_manifest_sha256.txt` |
| `../R4_20261028_campaign/release_attempts/attempt5_owner_rulings/zz_sha256_manifest_attempt5.csv` | release attempt 5 | `logs/zz_campaign_attempt5_manifest_sha256.txt` |
| `../R4_20261028_campaign/release_attempts/attempt6_review_fixes/zz_sha256_manifest_attempt6.csv` | release attempt 6 | `logs/zz_campaign_attempt6_manifest_sha256.txt` |
| `../R4_20261028_campaign/release_attempts/attempt7_final_review/zz_sha256_manifest_attempt7.csv` | release attempt 7 | `logs/zz_campaign_attempt7_manifest_sha256.txt` |

**Rule:** no manifest is overwritten. A later state gets `v9`.
