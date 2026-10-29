# N-A2 fix verification 3: read-only reviewer report (verbatim)

**Date:** 2026-10-28.
**Reviewer:** read-only review agent a6d24bd6ca8c2b9fd, resumed with its context. It used Read, Grep and Glob only.
**State reviewed:** the rev6 pilot source with draft rev3, SHA-256 `fdaf193de510488733f0e0899d50def86cbeafabdbecdd3bc7a144099b6f492c`.

The reviewer's text below is unchanged.

---

Third verification of the N-A2 fixes (rev5 to rev6), read-only

I used Read, Grep and Glob only; I ran nothing and wrote nothing. PIL = `D:\EURÉKA 2026 - KT\verification\research_recovery_20261028\R4_20261028_pilot`. Short names mean files under PIL: `checks.py` and `campaign.py` are in `PIL\code\r4h3\`, `T_A2` is `PIL\code\tests\test_amendment2.py`, `DRAFT2` is `PIL\03_protocol_v1_amendment_2_DRAFT.md` (rev3), and `02b` is `PIL\02b_protocol_ambiguity_register_addendum_amendment2.md`. The file hashes in `logs\zz_code_changes_rev5_to_rev6.csv` are the developer's claims; I cannot hash. The changes it lists (`checks.py`, `campaign.py`, `test_amendment2.py`, plus `config\campaign_config_v6_DRAFT.json` added) match what I read.

**Summary:** all three items are fixed, I found no new defect, and no CRITICAL or MAJOR finding is open. One verification gap remains: there is no complete test run of the current (rev6) code yet.

## Verdicts

| Item | Verdict | Evidence |
|---|---|---|
| R3-14 | **FIXED** | `CAMPAIGN_CONFIG` is now `config/campaign_config_v6_DRAFT.json` (`campaign.py:88`). v6 holds the current values for all three changed AMB-29 keys (`v6:286-288`). `DRAFT2:144` names v6 and says v3, v4 and v5 are kept unchanged but superseded. `DRAFT2:147` names v6. Whether v6 regenerates byte-identically is not verified, because that needs execution. |
| R3-15 | **FIXED** | For M2, an arm with an undefined ratio now gives `NOT_EVALUABLE_QS_UNDEFINED`, after the no-energy test (`checks.py:130-133`). The M2 branch outcome is still REPORTED_ONLY, returned before any counts are read (`checks.py:162-163`). `IMPLEMENTED_2` uses the "M0/M1 branch INCONCLUSIVE; M2 stays reported only" form for all three keys (`campaign.py:309-312`), and so do `DRAFT2:42`, `DRAFT2:92-94`, `DRAFT2:198-200` and `02b:10-12`. Tested at `T_A2:335-344`. The existing R3-12 test still holds, because "FAIL…" does not start with "undefined". |
| Residual note (D5 status denominator) | **FIXED** | `checks.denominator` now runs inside a `try` before `errors.csv` is written. An exception is recorded as `STATUS-DENOMINATOR`, and the manifest gets `denominator = {"error": …}` (`campaign.py:910-915`, `920-921`, `929`). Tested at `T_A2:321`, `328`, `332`. |

**New defects:** none found.

## One-line confirmations
- **Block equals `IMPLEMENTED_2` (all keys):** yes. All 21 keys match value for value (`DRAFT2:181-220` against `campaign.py:292-318`); the reader skips `amendment`, `status` and `note`. The two changed AMB-29 values match exactly (`DRAFT2:199-200` against `campaign.py:310-312`).
- **Fail-closed:** **YES.**
  - All blockers are still present: no issued amendment 2 (`campaign.py:502`), amendment-1 hash (`campaign.py:508`), protocol §10.1 gate (`campaign.py:530`), authorisation and scope (`campaign.py:70`, `533`), location by resolved path (`campaign.py:540`), review status (`campaign.py:545`).
  - No new write sites.
  - `R4_20261028_campaign\release` still holds only amendment 1, its approval record and the issue diff.
- **CR-A2 / CR-A6 / torque limits:** unaffected. The only code changes are in `pair_qs_dynamic`'s M2 branch and the output wrappers in `execute_schedule`. `classify_pair` takes no QS input. `evaluator.py`, `recompute_from_traces.py`, `closedloop.py` and `frozen.py` are unchanged according to the developer's diff file.
- **Draft rev3 accurate against the code:** yes, as far as can be checked by reading.
  - `DRAFT2:10` cites `archive\rev5_verified_20261028_1101\ARCHIVE_INDEX.csv`, which exists and holds the rev2 hash.
  - `DRAFT2:154` cites `logs\zz_code_changes_rev3_to_rev6.csv`, which exists.
  - `DRAFT2:11` still describes the integrity files as to be written later; they do not exist yet.
- **Open CRITICAL or MAJOR findings:** none. The only MAJOR finding across these reviews, R3-1 (location check by name only), is fixed at `campaign.py:540` and tested at `T_A2:239-244`. No CRITICAL finding was raised.

**Still open, not as defects:**
- AMB-29(a), AMB-30 and AMB-31 are owner decisions; the draft discloses each one's direction.
- `config\code_review_status_v4.json` is absent, so campaign mode blocks; this is expected before review sign-off.
- **Not verified:** a complete test run of the current (rev6) code. `logs\pytest_run19.txt` shows 215 passed, but that was rev5, and `pytest_run20.txt` has not finished.
