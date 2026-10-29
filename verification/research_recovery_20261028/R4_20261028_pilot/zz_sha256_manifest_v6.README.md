# Pilot SHA-256 manifest v6: scope and self-exclusion policy

`zz_sha256_manifest_v6.csv` has the columns `path`, `bytes` and `sha256`. Paths are relative to this pilot directory, use `/` separators and are sorted. It was written last in the AMB-29(a) / AMB-31 owner-rulings task (2026-10-28).

**Excluded:**

| File | Reason |
|---|---|
| `zz_sha256_manifest_v6.csv` | a file cannot contain its own hash. Its SHA-256 is in `logs/zz_manifest_v6_sha256.txt` |
| `logs/zz_manifest_v6_sha256.txt` | written after the manifest |
| `__pycache__/`, `*.pyc` | none exist |

**Included:** everything else, including:
- the v1–v5 manifests and READMEs, unchanged;
- every test log (runs 1–22) and every readiness gate (v2–v8);
- the archives rev0, rev1, rev2, rev3, rev4a, rev4b, rev5 and rev6;
- every review report, including the four N-A2 reports;
- the amendment 2 draft rev3 and candidate rev4, each with its `.sha256.txt`;
- reports 14 and 16, document 15, and the v5 and v6 integrity logs.

**Not covered:** the campaign directory, which has its own manifests:

| Manifest | Covers | SHA-256 recorded in |
|---|---|---|
| `../R4_20261028_campaign/zz_sha256_manifest_release.csv` | release attempt 2 at the root, plus attempt 1 | `logs/zz_campaign_release_manifest_sha256.txt` |
| `../R4_20261028_campaign/release_attempts/attempt3_amendment2/zz_sha256_manifest_attempt3.csv` | release attempt 3 | `logs/zz_campaign_attempt3_manifest_sha256.txt` |
| `../R4_20261028_campaign/release_attempts/attempt4_owner_rulings/zz_sha256_manifest_attempt4.csv` | release attempt 4 | `logs/zz_campaign_attempt4_manifest_sha256.txt` |

**Rule:** no manifest is overwritten. A later state gets `v7`.
