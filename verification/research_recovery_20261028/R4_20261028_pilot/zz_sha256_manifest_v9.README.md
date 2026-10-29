# Pilot SHA-256 manifest v9: scope and self-exclusion policy

`zz_sha256_manifest_v9.csv` has the columns `path`, `bytes` and `sha256`. Paths are relative to this pilot directory, use `/` separators and are sorted. It was written last in the task "Apply Final Owner Decisions I-2 to I-6 and Prepare Attempt 8" (2026-10-28 to 2026-10-29).

**Excluded:**

| File | Reason |
|---|---|
| `zz_sha256_manifest_v9.csv` | a file cannot contain its own hash. Its SHA-256 is in `logs/zz_manifest_v9_sha256.txt` |
| `logs/zz_manifest_v9_sha256.txt` | written after the manifest |
| `__pycache__/`, `*.pyc` | none exist |

**Included:** everything else, including:
- the v1–v8 manifests and READMEs, unchanged;
- every test log of this task:
  - targeted runs 26a, 27a and 28a;
  - full runs 26, 27 and 28;
  - the three mutation-check logs;
- the readiness gates v12, v13 and v14;
- the archives rev0 to rev12, including `rev10_attempt7_20261028_1851`, `rev11_attempt8_20261028_2126` and `rev12_attempt9_20261028_2308`;
- the review reports R8, R9 and R10;
- the amendment 2 candidates rev8, rev9 and rev10, each with its `.sha256.txt`;
- the review-status files v9 to v11 and the campaign configurations v11 to v13;
- report 20;
- the v9 start-state, pre-hash and integrity logs.

**Not covered:** the campaign directory, which has its own manifests:

| Manifest | Covers | SHA-256 recorded in |
|---|---|---|
| `../R4_20261028_campaign/zz_sha256_manifest_release.csv` | release attempt 2 at the root, plus attempt 1 | `logs/zz_campaign_release_manifest_sha256.txt` |
| `../R4_20261028_campaign/release_attempts/attempt3_amendment2/zz_sha256_manifest_attempt3.csv` to `attempt7_final_review/zz_sha256_manifest_attempt7.csv` | release attempts 3 to 7 | `logs/zz_campaign_attempt3_manifest_sha256.txt` to `…attempt7…` |
| `../R4_20261028_campaign/release_attempts/attempt8_final_owner_decisions/zz_sha256_manifest_attempt8.csv` | release attempt 8 | `logs/zz_campaign_attempt8_manifest_sha256.txt` |
| `../R4_20261028_campaign/release_attempts/attempt9_review_fixes/zz_sha256_manifest_attempt9.csv` | release attempt 9 | `logs/zz_campaign_attempt9_manifest_sha256.txt` |
| `../R4_20261028_campaign/release_attempts/attempt10_review_fixes/zz_sha256_manifest_attempt10.csv` | release attempt 10 | `logs/zz_campaign_attempt10_manifest_sha256.txt` |

**Rule:** no manifest is overwritten. A later state gets `v10`.
