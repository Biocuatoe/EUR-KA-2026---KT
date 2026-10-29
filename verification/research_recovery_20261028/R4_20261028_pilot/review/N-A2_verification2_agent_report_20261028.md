# N-A2 fix verification 2: read-only reviewer report (verbatim)

**Date:** 2026-10-28.
**Reviewer:** read-only review agent a6d24bd6ca8c2b9fd, resumed with its context. It used Read, Grep and Glob only.
**State reviewed:** the rev5 pilot source and draft rev2, archived unchanged in `archive/rev5_verified_20261028_1101/`.

The reviewer's text below is unchanged. The author's handling of each item is in `14_amendment2_release_readiness_report.md` §6.

---

Second verification of the N-A2 fixes (rev4b to rev5), read-only

I used Read, Grep and Glob only; I ran nothing and wrote nothing. PIL = `D:\EURÉKA 2026 - KT\verification\research_recovery_20261028\R4_20261028_pilot`. Short names mean files under PIL: `checks.py` and `campaign.py` are in `PIL\code\r4h3\`, `T_A2` is `PIL\code\tests\test_amendment2.py`, `DRAFT2` is `PIL\03_protocol_v1_amendment_2_DRAFT.md` (rev2), and `02b` is `PIL\02b_protocol_ambiguity_register_addendum_amendment2.md`. The file hashes in `logs\zz_code_changes_rev4b_to_rev5.csv` and `rev3_to_rev5.csv` are the developer's claims; I cannot hash. The files they mark as changed are the ones whose content changed in what I read.

**Summary:** R3-7(b-d), R3-10, R3-12 and R3-13 are fixed. R3-6 is only partly fixed, because the draft's change list still names the old config file (new finding R3-14, MINOR). The block matches the code, the campaign gate is still fail-closed, and CR-A2 and CR-A6 are unaffected. The draft is not yet accurate.

## Verdicts

| ID | Verdict | Evidence |
|---|---|---|
| R3-6 | **PARTIALLY FIXED** | `DRAFT2:147-152` now lists the fixed path strings, the config-rebuild blocker, R3-9, R3-10, R3-12 and R3-13. `DRAFT2:154` points to `logs\zz_code_changes_rev3_to_rev5.csv`, which exists. New inaccuracy: see R3-14. |
| R3-7(b) | **FIXED** | `T_A2:280-284` sets `AMENDMENT_1_SHA256` to a wrong value. `IMPLEMENTED_2` was built at import, so amendment 2's block still matches and the only thing tested is the issued-amendment-1 hash check (`campaign.py:506-507`). |
| R3-7(c) | **FIXED** | `T_A2:287-300` makes `pair_qs_dynamic` raise. The test asserts the pair status `NOT_EVALUABLE_CONDITION_ERROR` with eligibility `None`, that both runs stay executed with no error rows, and that the traceback is recorded. It exercises `campaign.py:722-737`. |
| R3-7(d) | **FIXED** | `T_A2:265` now expects "no approval record ap2.json", which only amendment 2's own blocker produces (`campaign.py:509`). |
| R3-10 | **FIXED** | `DRAFT2:66` states that `P3_RULE` keeps amendment 1's AMB-24 wording, and that the QS screen now also decides whether §9 applies, and never feasibility, pair status or crediting. This matches the code: `classify_pair` is unchanged and takes no QS input. |
| R3-12 | **FIXED** | An eligible M2 pair without a usable energy is now labelled `NOT_EVALUABLE_RUN_MISSING` (`checks.py:125-130`). The M2 branch outcome is still REPORTED_ONLY, because it is returned before any counts are read (`checks.py:158-159`). `IMPLEMENTED_2` (`campaign.py:309`), `DRAFT2:42`, `DRAFT2:92` and `02b:10` agree. Tested at `T_A2:303-310`. |
| R3-13 | **FIXED** | Accounting and each branch outcome are wrapped in `try` (`campaign.py:893-908`). An exception goes into `errors.csv` before that file is written (`campaign.py:913-914`). The fallback row is INCONCLUSIVE, or REPORTED_ONLY for M2, and an unknown motor defaults to INCONCLUSIVE (`campaign.py:906`). All remaining outputs are still written (`campaign.py:909-928`). Tested at `T_A2:313-329`. |

## New defects

**R3-14 — MINOR — `DRAFT2:144` and `DRAFT2:147` still name the old config file.**
- `DRAFT2:144` says `CAMPAIGN_CONFIG` → `config/campaign_config_v4_DRAFT.json`. `DRAFT2:147` says v4 "regenerates identically".
- The code now uses `campaign_config_v5_DRAFT.json` (`campaign.py:88`). v4 no longer matches `config_content`, because the `AMB_29_eligible_run_missing` value differs (`config\campaign_config_v4_DRAFT.json:286` against `v5:286`).
- **Remedy:** name v5 in both places, and say that v4 is kept unchanged but superseded.

**R3-15 — NOTE — the M2 wording for AMB-29(c) and (d) is imprecise.**
- **Where:** `DRAFT2:93-94`, `02b:11-12` and `IMPLEMENTED_2` (`campaign.py:310-311`) all say "branch INCONCLUSIVE". For M2 the branch stays REPORTED_ONLY (`checks.py:158-159`).
- **Same pattern as R3-12:** an M2 pair with both energies but QS energy ≤ 0 is labelled REPORTED_ONLY (`checks.py:130`), not `NOT_EVALUABLE_QS_UNDEFINED`, because the M2 test runs before the undefined test (`checks.py:138-141`). AMB-29(c) is worded for any eligible pair.
- **Effect:** none on any outcome, and practically unreachable.
- **Remedy:** use the "(M0/M1 branch INCONCLUSIVE; M2 stays reported only)" form for (c) and (d), and either label M2 undefined pairs as QS_UNDEFINED or document the exception.

**Residual NOTE.** The status-denominator call `checks.denominator(...)` (`campaign.py:922`) is still outside any `try` and raises on an unknown condition status. This is outside the scope of R3-13, and every status comes from the fixed list, so it cannot trigger today.

## One-line confirmations
- **Block equals `IMPLEMENTED_2`:** yes. 21 keys, value for value (`DRAFT2:181-220` against `campaign.py:292-317`). The only change from rev1 is `AMB_29_eligible_run_missing`, which matches `campaign.py:309`.
- **Fail-closed:** **YES.**
  - All blockers are still present: no issued amendment 2 (`campaign.py:501`), amendment-1 hash (`campaign.py:507`), protocol §10.1 gate (`campaign.py:529`), authorisation (`campaign.py:532-538`), location by resolved path (`campaign.py:539`), review status (`campaign.py:544`).
  - No new write sites.
  - `R4_20261028_campaign\release` still holds only amendment 1, its approval record and the issue diff.
- **CR-A2 / CR-A6:** unaffected. The changes touch only `pair_qs_dynamic`'s M2 branch and the accounting wrapper. `classify_pair`, `run_arm`, the evaluator and the separate recomputation are unchanged (evaluator and recomputation per the developer's diff file; the rest by reading). Torque limits are still independent and equivalent.
- **Draft accurate:** **not yet**, because of R3-14 (MINOR) and R3-15 (NOTE). The rest of rev2 matches the code.

**Not verified:** a complete clean test run of the current (rev5) code. `logs\pytest_run18.txt` shows 211 passed, but that was rev4b; `pytest_run19.txt` is still in progress.
