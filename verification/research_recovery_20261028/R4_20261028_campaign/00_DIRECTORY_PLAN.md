# R4_20261028_campaign: directory plan (H3 campaign release package)

**Status: NOT RELEASED. No official run exists here. The 170-run campaign has not started.**

- **Created:** 2026-10-28 07:17:11 +07:00. It was verified absent first (log: `../R4_20261028_pilot/logs/campaign_dir_created.txt`).
- **Decided by:** owner decision AMB-15 (`../R4_20261028_pilot/09_owner_decision_record.md`).
- **Governing texts:**
  - the frozen protocol `../R4_20261028_preflight/03_R4_protocol_v1.md`, SHA-256 `f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab`;
  - the amendment candidate `../R4_20261028_pilot/03_protocol_v1_amendment_1_rev2_CANDIDATE.md`, which is READY FOR OWNER APPROVAL and not approved.

## What this directory is for

- the release package (a copy of the pilot's code, configuration and inputs, at release);
- the issued amendment and its approval record;
- the protocol §10.1 gate record;
- the official run outputs.

## What this directory is not for

Development logs, smoke tests, readiness checks and any non-official output. Those stay in `../R4_20261028_pilot/`.

## Layout

| Path | When | Content |
|---|---|---|
| `00_DIRECTORY_PLAN.md` | now | this file |
| `GATE_RECORD_not_released.json` | now | independent pre-release gate record: hashes, blockers, status NOT RELEASED |
| `zz_sha256_manifest.csv` | now | manifest of this directory (self-excluding; policy below) |
| `release/03_R4_protocol_v1_amendment_1.md` | owner, at approval | issued amendment: the reviewed candidate text with `"status": "APPROVED"` |
| `release/amendment_1_approval.json` | owner, at approval | `approved_by`, `date`, `amendment_sha256`, `accepted_review_items: ["CR-A6 residual"]`, `approved_tolerances` |
| `code/`, `config/`, `inputs/` | release | hash-identical copies from the pilot. Hashes must equal `../R4_20261028_pilot/logs/readiness_gate_v4.json` and `zz_sha256_manifest_v3.csv` |
| `logs/pytest_release.txt` / `.xml` | release | clean test run executed in this directory |
| `logs/pre_run_hashes.txt` | release | the protocol §10.1 gate (`code/record_gate.py`), written before the first official run |
| `outputs/campaign/` | campaign | the only place official runs are written (`run_campaign.py --execute`) |

Every step is listed in `../R4_20261028_pilot/11_campaign_release_checklist.md`.

## Manifest policy for this directory

- `zz_sha256_manifest.csv` lists every file here except itself.
- Its own SHA-256 is recorded in `../R4_20261028_pilot/logs/zz_campaign_dir_manifest_sha256.txt`.
- It is never overwritten: a release-time manifest is written as `zz_sha256_manifest_release.csv`.
