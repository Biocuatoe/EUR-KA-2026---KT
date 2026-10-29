# Erratum: provenance header of `R5_attempt5_review_agent_report_20261028.md`

**Date:** 2026-10-28. **Written by:** the developer (not the reviewer).

The provenance header of `R5_attempt5_review_agent_report_20261028.md` says that the agent "delivered this report at about 15:55". **That time is wrong.** I wrote the header and estimated the time instead of reading it.

The recorded times are:

| Event | Time (+0700) | Source |
|---|---|---|
| review started | 14:49:00 | `review_scope_attempt5.json` (`review_started`) |
| attempt-5 precondition record and release validation written; the agent was resumed after these | 15:21:03 and 15:21:10 | `logs/preconditions_attempt5.json`, `logs/release_validation_attempt5.json` |
| report saved to file | 15:35:03 | file modification time of the saved report |
| attempt-5 gate record | 15:36:05 | `GATE_RECORD_attempt5.json` (`written`) |

So the report was delivered at about **15:34**.

The report text below the header's line is unaffected. The two copies, here and in `R4_20261028_campaign/release_attempts/attempt5_owner_rulings/review/`, are identical (SHA-256 `f77bc6818554b10fea53555436c3b3c4684de61c0117ac9ee0efa14e8a35448b`). Neither copy has been edited: the attempt-5 copy is hashed in that attempt's gate record and manifest, and changing either copy would break those records.
