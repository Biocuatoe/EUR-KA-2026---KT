# Pre-commit safety review (2026-10-24)

Read-only review of the staged changes. Nothing was staged, unstaged, committed, pushed, reset, cleaned or rerun while writing it. This file is **untracked on purpose**; it is not part of the 480 staged files and not in the evidence inventory (the inventory's `verify` is unaffected).

**Verdict: NOT READY — BLOCKERS LISTED** (one blocker, a documentation fix; no safety, secrecy or integrity blocker).

## 1. Repository state

| Item | Result |
|---|---|
| `git rev-parse --show-toplevel` | `D:/EURÉKA 2026 - KT` |
| `git rev-parse HEAD` | `f264eca354d67dcdf786063ca36ae246466217d2`, branch `master` |
| `git status --short` | 480 staged entries (`M` 2, `A` 478) and 4 untracked deferred files; no unstaged modification (`git ls-files -m` empty) |
| Staged count / bytes | **480 files, 4,183,541 bytes** (blob sizes from the index; largest `dop853_S2_soh1.0_dense.csv`, 821,829 B) |
| Staged vs plan | 475 planned files + `.gitignore`, `.gitattributes`, inventory, guide, report = 480. Planned-not-staged: none. Staged-not-planned: none. Deferred staged: none. Tier B/C staged: none. Tracked files that match an ignore rule (`git ls-files -i -c --exclude-standard`): none |
| `git diff --cached --check` | exit 2, see section 3 (line-ending noise, not a defect) |
| Hooks | none active, `core.hooksPath` unset |
| **Remote** | **`origin` = `https://github.com/Biocuatoe/EUR-KA-2026---KT.git` exists; `refs/remotes/origin/master` = `f264eca` = HEAD.** `.git/config` was modified 2026-10-24 05:49, i.e. after the preservation work reported "no remote". Visibility of the GitHub repository is not known to me and was not queried |

## 2. Sensitive-content scan (staged blobs only, 480 files)

Patterns: passwords/API keys/tokens/private keys, key shapes (AWS, GitHub, Slack, `sk-`), e-mail addresses, user and host names, user-profile and other `C:` paths, `D:` paths outside the project, IPv4 addresses, `.env`/binary/cache file names.

| Finding | Path | Assessment |
|---|---|---|
| No credential, key, token, `.env`, IPv4 address, hostname | whole staged set | none found |
| No compiler output, cache, executable, `.npz/.gz/.docx`, `python-env`, `omc-userdata`, `modelica-build/cases*` | whole staged set (name test) | none staged |
| OS user name in a path: `C:\Users\HLC\AppData\Local\Temp` | `verification/independent-model-report.md` line 106 | housekeeping remark, not needed for provenance. Historical evidence document, left unedited. Redact before publication if the user name matters; that is an owner decision |
| Same path quoted | `verification/evidence-preservation-report.md` (item 4) | my own text; could say `C:\Users\<user>\...` instead |
| Standard OS path without user name: `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\OpenModelica` (x3) | `audit/toolchain-installation-report.md` | installer-residue provenance; keep |
| Legacy workspace path `D:\EUREKA-2026\.venv` | `technical-claim-matrix.csv`, `technical-foundation-audit.md` | states historic interpreter path, "provenance only"; keep. It is the project's own former location, not another project |
| Project path `D:\EURÉKA 2026 - KT` (239 occurrences, 73 files) | launcher logs, smoke JSON, audit documents | machine-specific but necessary to interpret the run records; no user name; keep |
| Drive alias `Y:` | launcher JSON/logs, `.mos` records | harmless |
| `noreply@anthropic.com` | `verification/evidence-preservation-report.md` (proposed commit trailer) | not personal data |
| No path to any other research project | | none found; the only `D:` roots are the project and its legacy location |

Context: the user name and machine name already exist in files committed in HEAD (`docs/environment-inventory.md`, `docs/installation-verification.md`, `evidence/artifact_hashes.json`). Because `origin/master` equals HEAD, they are already on the remote. This commit adds the user name to 2 files only (above); it does not create the exposure.

The two machine-state logs that hold the user PATH (`verification/logs/om-baseline-before.txt`, `om-baseline-after-install.txt`) are not staged.

## 3. Line endings and attributes

Staged `.gitattributes` adds exactly:

```
verification/** -text
audit/** -text
/technical-claim-matrix.csv -text
/technical-foundation-audit.md -text
```

- `git check-attr` on all 480 staged paths: 478 `text: unset` (all under `verification/`, `audit/` or the two named files) and 2 `text: auto` (`.gitignore`, `.gitattributes`). Over all tracked files, none outside the four patterns has `text` unset. Files outside the scope are unaffected: `src/eureka/plant.py`, `tests`, `scripts/analyze.py`, `docs/model.md`, `configs/parameters.yaml`, `protocol/preregistration.md` stay `text: auto`; `scripts/setup.ps1` stays `text` + `eol=crlf`.
- Side effect: `verification/Invoke-OpenModelica.ps1` is stored byte-exact (LF, as it exists and has been run) rather than converted to CRLF by the `*.ps1 text eol=crlf` rule.
- Source code under `verification/` (`.py`, `.mo`, `.mos`) is also stored byte-exact; that is the intent, because the freeze hashes cover those bytes. Cost: no automatic line-ending normalization for those files.
- Hash retention (checked on the **staged blobs**, not the working files): all 475 inventory files have blob SHA-256 equal to the inventory value. The frozen protocol text reconstructs from the staged `controller-crosscheck-protocol.md` to `c7951936eb162ab5326711d537fe7f8438f76a2ac25df4a80126267237e9725d`, the value recorded at the freeze. The final snapshot of every file/hash pair in the run log matches its staged blob (38 matches). The 4 differences are earlier snapshots in the same log that a later snapshot supersedes: protocol `c7951936...` (freeze) and `b4ed35eb...` (after A1/A2) versus `367f0c83...` (final), and `generate_controller_case_scripts.py` `d01e4dfa...` (freeze) versus `77625e17...` (final); the log itself records them in order.
- Is the scope broader than necessary? `verification/**` is needed (freeze hash chain). `audit/**` is broader than the two CSVs that actually changed (the six audit `.md/.py` files would be unchanged by Git but would turn CRLF on a Windows checkout). I judge it acceptable and consistent with the inventory hashes; if you prefer the minimum, replace `audit/**` by `audit/external-data-provenance.csv`. No correction applied.
- `git diff --cached --check` reports 29,049 "trailing whitespace" and 4 "new blank line at EOF" in 156 files. 148 of those files have only the carriage return of CRLF line endings; 8 have genuine trailing blanks or a blank last line (`verification/logs/om-smoke.log`, `phase2-env.log`, `phase3-fastsim.log`, `modelica-build/logs/20261023-220545-diagtol-diag_openloop_tol1e-12.out.txt`, `20261023-220629-v011-diag_openloop_tol1e-12.out.txt`, `20261024-003750-diag_maxstep-diag_dist_maxstep.err.txt`, `verification/scripts/controller_step_tests.py`, `guarded_run.py`). The first six are verbatim tool output and the others are existing scripts; they are not edited. No conflict markers.
- `.gitignore` staged diff: +19 lines, nothing removed except the former one-rule block; exact paths only; no rule hides a staged file.

## 4. Evidence completeness

Run today without simulations: `python verification/scripts/evidence_preservation.py verify` -> 901 files, 56 baseline hashes, 0 problems. Old 536-file manifest re-hashed -> 536 match, 0 missing, 0 changed. The 40 `raw/*.csv.gz` all decompress to the hashes of their listed result CSVs. The 189 archive files on disk equal the 189 `archive-copy` rows and decompress to their original hashes. No file exists under `verification/`, `audit/`, `artifacts/`, `data/`, `logs/`, `protocol/` or `evidence/` that the inventory does not account for. The 7 ignored CVODE logs and the raw folders are present. Nothing was deleted.

Represented in the staged index: frozen protocol with amendments, run log, report, integrity review, results table (1 each), solver selection, gains, preliminary and step-test JSON, 8 failed-run records, the first defective plant runs (`check_results_FIRST_RUN_with_B2_failure.csv`, `..._DEFECTIVE.json`), 309 solver-status logs, 45 Modelica sources/generated inputs, 43 scripts. In the archive/in place: raw series, Python references, CVODE logs, plant-phase CSVs. Deferred and not staged: `verification/fastsim-smoke/zoe_hwfet_timeseries.csv`, `zoe_udds_timeseries.csv`, `verification/logs/om-baseline-before.txt`, `om-baseline-after-install.txt`. No missing historical run was reconstructed.

## 5. Backup readiness

No verified second storage medium has been used. All evidence sits on **D:** (NTFS, fixed, "GAME", NVMe Samsung 512 GB, 322.6 GB free). The machine has a second internal NVMe disk behind **C:** (Micron 256 GB, 8.6 GB free); no copy exists there either. After a push, GitHub would hold only the 4 MB of Tier A. **The raw series, Python references, archive, baseline and thesis copy are still vulnerable to failure of the single D: drive, and to `git clean -fdx`, loss of the machine, or deletion.** Not run: any copy, `git clean`.

Checklist (about 497 MB; copy to an external drive or cloud storage, then hash-compare against the inventory; a copy on C: only protects against failure of the D: drive):

| Item | Path | Files | Size |
|---|---|---|---|
| Raw Modelica results | `verification/controller-crosscheck-runs/raw/` | 40 | 240.9 MB |
| Python reference series | `verification/controller-crosscheck-runs/python_reference/` | 45 | 47.8 MB |
| Evidence archive | `verification/evidence-archive/` | 189 | 41.7 MB |
| Python baseline | `artifacts/` | 53 | 165.2 MB |
| Baseline inputs | `data/` (21), `logs/` (25) | 46 | 1.7 MB |
| Thesis copy | `EURÉKA 2026 - KT.docx` | 1 | 0.43 MB |
| CVODE logs (originals, ignored) | `verification/modelica-build/logs/*_single_PT_*_cvode_*.out.txt` | 7 | 376 MB (archived at 1.1 MB; copy optional) |
| Repository | `.git/` after the commit | | few MB |

Not needed: the 40 uncompressed CSVs (1.44 GB, identical to the `.gz`), build output, `python-env`, `omc-userdata`. After copying, compare each file's SHA-256 with `verification/evidence-preservation-inventory.csv` (columns `path`, `sha256`) and keep the second copy untouched.

## 6. Blocker

**B1. Staged texts say there is no remote, and a GitHub remote now exists.**
- `.gitignore` lines 39-40 (comment, two lines): "too large for plain Git, no LFS remote".
- `verification/evidence-storage-guide.md`: table row 3 ("there is no LFS remote") and last bullet of section 5 ("with no remote, LFS objects would sit only in `.git/lfs`").
- `verification/evidence-preservation-report.md`: section 1 ("no remote"), section 2 item 2 ("No remote exists").
These were true when written. They would be wrong in a commit that cannot be rewritten later. They also change the decision basis: with a GitHub remote, Git LFS and a push are possible, so Tier B placement outside Git is now a choice (history permanence, GitHub storage quota, publication of evidence) and not a constraint.

Proposed minimal correction (**not applied; needs your approval because it edits and restages three staged files**):
1. `.gitignore`: "too large for plain Git, no LFS remote" -> "kept out of Git history; Git LFS is not enabled".
2. Guide: replace "and there is no LFS remote" with "and Git LFS is not enabled"; replace the last bullet by "Git LFS 3.7.1 is installed but not enabled. A GitHub remote (`origin`) was added on 2026-10-24 after this work started, so LFS is now possible subject to its storage quota; enabling it rewrites hooks and attributes repository-wide and is an owner decision. Until then Tier B stays outside Git."
3. Report: add a line "Note: `origin` (GitHub) was configured at 05:49 on 2026-10-24, after this report was first written; statements about 'no remote' describe the state at that time" and make the two references time-stamped.
Alternative: the owner may accept the commit as is; the report then stays accurate only as a dated statement.

Not a blocker, owner decisions: (a) whether to redact `C:\Users\HLC\...` in `verification/independent-model-report.md` before any push; (b) whether the GitHub repository is public (unknown), since the commit adds evidence logs and absolute paths and the history already holds the user and machine name; (c) `audit/**` scope; (d) a second-medium backup before or soon after the commit.

## 7. Stop

No commit, push or staging change was made. Waiting for explicit owner approval: either "apply the B1 correction and restage those three files" or "commit as staged".
