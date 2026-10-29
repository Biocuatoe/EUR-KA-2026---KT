# Pilot SHA-256 manifest v10: scope and self-exclusion policy

`zz_sha256_manifest_v10.csv` has the columns `path`, `bytes` and `sha256`. Paths are relative to this pilot directory, use `/` separators and are sorted. It was written last in the task "R4 H3 — Attempt 11: Final Release-Candidate Correction and Independent Review" (2026-10-29).

**Excluded:**

| File | Reason |
|---|---|
| `zz_sha256_manifest_v10.csv` | a file cannot contain its own hash. Its SHA-256 is in `logs/zz_manifest_v10_sha256.txt` |
| `logs/zz_manifest_v10_sha256.txt` | written after the manifest |
| `__pycache__/`, `*.pyc` | none exist |

**Included:** everything else, including:
- the v1–v9 manifests and READMEs, unchanged;
- every test log of this task:
  - runs 29a, 29b, 29, 30a and 30;
  - every mutation-check log, the four failed first invocations included;
- the readiness gates v15 and v16;
- the archives up to `rev13_attempt10_20261029_0629` and `rev14_attempt11_20261029_0807`;
- the review reports R11 and R12;
- the amendment 2 candidates rev11 (superseded unused), rev12 and rev13, each with its `.sha256.txt`;
- the review-status files v12 (superseded unused), v13 and v14, and the campaign configurations v14 and v15;
- reports 21 and 21a;
- the v10 start-state, pre-hash, line-ending and integrity logs;
- the copies of this task's helper scripts in `logs/zz_scripts_task_attempt11/`.

**Not covered:** the campaign directory, which has its own manifests. Their hashes are in `logs/zz_campaign_release_manifest_sha256.txt` and `logs/zz_campaign_attempt3_manifest_sha256.txt` to `logs/zz_campaign_attempt12_manifest_sha256.txt`.

**Rule:** no manifest is overwritten. A later state gets `v11`.
