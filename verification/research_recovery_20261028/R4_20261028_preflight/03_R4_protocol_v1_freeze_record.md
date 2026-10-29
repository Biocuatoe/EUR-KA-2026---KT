# Freeze record: R4 protocol v1

| Field | Value |
|---|---|
| File | `03_R4_protocol_v1.md` (same directory) |
| SHA-256 | `f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab` |
| Size | 22,632 bytes |
| File modification time | 2026-10-28 00:54:48 +07:00 |
| Hash computed | 2026-10-28 00:54:59 +07:00, by two tools: `sha256sum` (Git Bash) and `certutil -hashfile … SHA256` (Windows). Both gave the same value |
| Read-only attribute | set on the protocol file immediately after hashing |
| Outcomes existing at freeze | none. No R4 code, run or planner output exists |
| Frozen scope | H3 on branch RP-E (executable); H1 on RP-E (defined, not scheduled); H2, H4, H5 blocked |
| Gates at freeze | G0 PASS; G1 PASS (classification); G2 PASS for RP-E only (FAIL for K, RP-S, AGE); G3 PASS for the executable scope (`04_gate_status_summary.md`) |
| Pre-freeze edits | Four edits were made before hashing, all on 2026-10-28 between 00:50 and 00:55: (1) the `r3_lib.py` and M1-curve hash references were written out in full; (2) a disclosure of prior knowledge was added to §8.3; (3)–(4) the trace sampling was set to 1 ms for all runs, so the recomputation tolerances are uniform. No edit was made after hashing |
| Prepared by | AI assistant (Claude); no human review |

**Verifying the protocol later:**
- Bash: `sha256sum 03_R4_protocol_v1.md`
- PowerShell: `Get-FileHash 03_R4_protocol_v1.md -Algorithm SHA256`

The result must equal the SHA-256 above. Any difference means the frozen text was altered. In that case the original is the one with this hash, and no result may be reported under v1 until the discrepancy is explained in a dated amendment.
