# Evidence preservation report (2026-10-24)

Written for the project owner. Scope: preserve the controller cross-verification evidence and make the essential part traceable in Git. No simulation was run, no model, tolerance, result, preregistration or thesis file was changed, nothing was deleted or moved, nothing was committed or pushed. How to use the result: `evidence-storage-guide.md`.

## 1. Actual repository state (at the start)

- Git root `D:\EURÉKA 2026 - KT`, branch `master`, HEAD `f264eca354d67dcdf786063ca36ae246466217d2`, no remote, no other branch. History: 8 commits (`126750a` ... `f264eca`). Loose objects 142 (365 KiB).
- Working tree: ` M .gitignore`, `?? audit/`, `?? technical-claim-matrix.csv`, `?? technical-foundation-audit.md`, `?? verification/`. Nothing staged. `verification/` was entirely untracked.
- Disk D: 323 GB free of 477 GB.
- `.gitattributes`: `* text=auto`, `*.ps1 text eol=crlf`, `*.png binary`; `core.autocrlf=true`. Git LFS 3.7.1 is installed.

## 2. Check of the existing record before any change

| Check | Result |
|---|---|
| `controller-crosscheck-artifact-manifest.csv` re-hashed (536 files, 2,116,561,104 B) | 536 match; 0 missing, 0 size differences, 0 hash differences. Checked again at the end: still 536/536 |
| 40 `raw/*.csv.gz` decompressed | all 40 reproduce the SHA-256 of a listed uncompressed result CSV |
| 56 hashes in `evidence/artifact_hashes.json` (Python baseline) | 56 match, none missing |
| Protected files (thesis DOCX mtime 2026-09-21; `protocol/preregistration.md`; `git ls-files -m`) | unchanged; no tracked file is modified |

Section 2 of the integrity review was used as the starting point. Four points in it needed adjusting for conditions it did not cover:

1. `* text=auto` with `core.autocrlf=true` would rewrite line endings of every committed text file, breaking the frozen-protocol hash chain and every inventory hash on a fresh checkout. Fixed with `-text` attributes (section 5).
2. It proposed Git LFS or an external archive for the bulk data. No remote exists, so LFS would hold objects only in `.git/lfs` and change hooks and attributes repository-wide. LFS was not used; the bulk data stays outside Git history.
3. It listed 293 status-log files (0.38 GB). The logs folder holds 316 files; 309 are small and are tracked, 7 are CVODE logs of 52 to 55 MB each, which are archived compressed.
4. It covered only the controller phase. The plant-verification phase has its own evidence in the same ignored folder (63 result CSVs, 108 executable logs, the first defective runs), which would have stayed unrecorded; it is now inventoried and archived.

## 3. Inventory and classification

`evidence-preservation-inventory.csv`: 909 rows, 901 individual files (2,385,267,440 B) with size and SHA-256, plus 8 group rows for 23,231 regenerable build/cache files (636,782,302 B). Columns: path, size, sha256, git_state_before, ignore_rule (as at the start), tier, action, category, run_id, supports (table and report section), archive path/size/hash, reason.

| Action | Files | Bytes | Meaning |
|---|---|---|---|
| track (Tier A) | 475 | 3,771,148 | staged by explicit path; 309 status logs, 143 sources/records, 15 build-folder records, 8 audit files |
| tracked-unchanged | 8 | 154,149 | already in Git (`configs/*`, `evidence/*`, `protocol/preregistration.md`) |
| retain-in-place (Tier B) | 225 | 1,881,540,112 | 40 raw `.gz`, 45 Python reference series, 40 redundant uncompressed CSVs (identical to the `.gz`), Python baseline (`artifacts/` 53, `data/` 21, `logs/` 25), thesis copy 1 |
| archive-copy (Tier B) | 189 | 497,698,735 (41,700,243 compressed) | evidence existing only in ignored build folders; originals stay where they are |
| defer-review | 4 | 2,103,296 | `fastsim-smoke/*.csv` (2), `logs/om-baseline-*.txt` (2, user PATH and profile-folder snapshot); left untracked, owner to decide |
| Tier C, regenerable | 23,231 | 636,782,302 | compiler output, `omc` cache, `python-env`, bytecode; stays ignored |

Counts by state at the start: tracked 8 (+ the 2 modified config files), untracked 151 + 4 deferred + 85 Tier-B, ignored 324 + 189 + 140 + 8 groups. Total evidence files hashed, 901 against the 536 of the earlier manifest.

Ignore rules at the start (exact): `/verification/modelica-build/` hid all 7,395 files in that folder (logs, failure records, result CSVs, build output); `/artifacts/`, `/data/`, `/logs/` hid the Python baseline (project policy, kept); `/verification/omc-userdata/` and `/verification/openmodelica-smoke/out/` hid cache and smoke output; `verification/python-env/.gitignore` (`*`) hid the verification Python environment; `__pycache__/` hid bytecode.

## 4. Staging plan checks

Before staging, the list of 475 files was tested for: `.venv`, `python-env`, `omc-userdata`, `__pycache__`, compiler outputs (`.exe .o .c` under case folders), `.npz`, `.gz`, `.docx`, `.bin`, `.dll` (none; one false hit: `verification/modelica/scripts/cases.json`, a source), files above 500 kB (one: `dop853_S2_soh1.0_dense.csv`, 0.82 MB), and content patterns for passwords, keys, tokens, e-mail addresses and `C:\Users\` paths. One hit: `verification/independent-model-report.md` contains one Windows user-profile temp path (`C:\Users\HLC\AppData\Local\Temp`) in a historical sentence. It is tracked unchanged, because editing a verification report would alter evidence; remove the path before publishing the repository if that matters. No secrets found. The two machine-state logs were deferred for the same reason.

## 5. Exact Git changes (staged, not committed)

| File | Change |
|---|---|
| `.gitignore` | the blanket `/verification/modelica-build/` rule replaced by exact paths: `cases/`, `cases_ctl/`, `cases_v0.1.0_when_pre/`, `launcher-smoke/`, `tmp/`, `python_reference/`, `logs/*_single_PT_*_cvode_*.out.txt`; new exact rules for `controller-crosscheck-runs/raw/`, `controller-crosscheck-runs/python_reference/`, `evidence-archive/`. +19 lines, nothing else changed. A first, wider glob (`*cvode*.out.txt`) also hid seven small `-version.out.txt` records; it was narrowed and every planned file was re-tested as not ignored |
| `.gitattributes` | +5 lines: `-text` for `verification/**`, `audit/**`, `/technical-claim-matrix.csv`, `/technical-foundation-audit.md`. Existing lines unchanged. As a consequence `verification/Invoke-OpenModelica.ps1` is stored byte-exact instead of CRLF-converted |
| 475 evidence files | added (explicit pathspec list, never `git add .`) |
| `verification/evidence-preservation-inventory.csv`, `evidence-storage-guide.md`, `evidence-preservation-report.md` | added |
| `verification/scripts/evidence_preservation.py` | added (in the 475); `archive`, `inventory`, `verify` |

Result: 480 files staged (2 modified, 478 added), 53,447+ added lines. Nothing unstaged except the 4 deferred files. Every staged blob was re-read from the index and its SHA-256 equals the inventory value (475/475; two audit CSVs initially differed because `text=auto` normalized them, fixed by the attribute and `git add --renormalize`).

Totals proposed for Git: 3,771,148 B of evidence files, 389,925 B inventory, plus guide, report and config.

## 6. Data movement

- Moved: none. Deleted: none. Overwritten: none. Existing manifest, report, protocol, results, raw data: untouched.
- Copied: 189 files into `verification/evidence-archive/` as deterministic `.gz` (mtime 0). For each copy the original was hashed before, the copy was decompressed and compared, and the original hashed again after; 0 mismatches. 40 result CSVs were not copied because a `raw/*.csv.gz` already reproduces them exactly. Archive size 41.7 MB (storage cost accepted: 497.7 MB of originals compress about 12:1 and cannot be rebuilt without rerunning simulations).
- Created: the archive folder, the three documents above, the script. The temporary `.partial` mechanism left no file.

## 7. Evidence that is still outside Git but important

All of it is hashed in the tracked inventory and checked by `verify`.

- `verification/controller-crosscheck-runs/raw/` (40 `.csv.gz`, 240.9 MB): the data behind every table row. Ignored by exact rule.
- `verification/controller-crosscheck-runs/python_reference/` (45 `.npz`, 47.8 MB).
- `verification/evidence-archive/` (189 `.gz`, 41.7 MB): CVODE logs, plant-phase CSVs and logs, diagnostic CSVs.
- `verification/modelica-build/cases_ctl/*/*_res.csv` (40 redundant plus 5 archived) and the other case folders: originals kept.
- Python baseline: `artifacts/` (165 MB, 56 hashes in `evidence/artifact_hashes.json`), `data/`, `logs/`, `EURÉKA 2026 - KT.docx` (434,945 B, `01363a069eeb005851f6d62ac4b9da9e3fd13a742bebbfdfc14c802f0eddff8c`).
- Risk: all of this is on one disk and untracked by Git. A `git clean -fdx` would delete the ignored parts. Copy `raw/`, `python_reference/` and `evidence-archive/` (about 330 MB) and `artifacts/`, `data/` to a second medium.

## 8. Missing or mismatched evidence

- None missing, none mismatched among the 901 listed files, the 536 manifest files, the 40 raw archives and the 56 baseline hashes.
- Never saved as files (unchanged from integrity review section 2): the first failing controller-logic run, the first 16-failure evaluation CSV and pair-table bug output, the original IDA-choosing selection output (replayed in the review).
- Deleted earlier under amendment A1 and not recoverable: the two CVODE result files of 10 GB and 0.5 GB; only header/tail/size/hash excerpts exist in `failed_runs/`.
- The `git_state` column of the 536-file manifest now describes 2026-10-24 before this work. It was left as is.

## 9. Headline artifacts (tracked, working-tree SHA-256)

| Path | Bytes | SHA-256 |
|---|---|---|
| `verification/controller-crosscheck-protocol.md` (frozen text + amendments A1-A4) | 37,144 | `367f0c8364f4b7f68524cdff4ce38625c6d8a4f26becf18aa465afdff5f6a8f0` |
| `verification/controller-crosscheck-runlog.md` | 25,630 | `98d44c32a4b8e756d388f25e71f8c227db6a83f30211212b7c719afbae09527e` |
| `verification/controller-crosscheck-report.md` | 21,393 | `e6738a99017ece96e7ee6c755c8a18ee53a5064979ed4bdd66c18c6413a24f31` |
| `verification/controller-crosscheck-results.csv` | 339,505 | `5cc670b0e9e52ccf979a8824326af5ee60b4383b869736e6a944b571db884226` |
| `verification/controller-crosscheck-integrity-review.md` | 29,797 | `a4e010087c8e1e2b96cb24acc5115e0a150dd4a64f373431894d69a0898741ca` |
| `verification/controller-crosscheck-runs/evaluation_summary.json` | 9,755 | `b1de6dba685e13c017c5c8f2aa4e8ac88c474eb45f866c9ef0a15176bb291614` |
| `verification/references/controller_solver_selection.json` | 11,333 | `5d46973e1fe5c23fdece84c4e773e28c5fff49eba7f0a13181644d26e1c4fb01` |
| `verification/references/controller_gains.json` | 9,869 | `29c4df2048aaea177f0e7876af4138b7ac1a917665dcc54f536400cda495a310` |
| `verification/controller-crosscheck-artifact-manifest.csv` | 130,945 | `c629168c70413b4c1d804f7fcd2620fdb2028cf9d51bc8e69791dfac882c1e1c` |
| `verification/modelica-build/check_results_FIRST_RUN_with_B2_failure.csv` | 37,302 | `276003924da4c1f865a04c12c1369c8edd902c43eaf9be51ee32ff04eb9f3a45` |
| `protocol/preregistration.md` (unchanged) | 11,369 | `d3e6271e6f3f225d30449a7ba5c5a17e9da2ab85a5a3b9beb4c414bf209bc10b` |
| `verification/evidence-preservation-inventory.csv` | 389,925 | `f37fed30c457d5cde5b975a2b91fe18d34dd9e39c0f0e3a352b1194bbdbacc83` |
| `verification/evidence-storage-guide.md` | see Git | `22846ba541750bf18099144b16e55f29f140635c2655f676e85aa88fb4795d84` |
| `.gitignore` | see Git | `34e93beaa7b93ccbce2a5e83a5bdc1e9e576d38fb0f5bab692390febb6a38401` |
| `.gitattributes` | see Git | `37df9208d7df4680e95b09e66f4dff1dad08ea7cad8fca4f8c52005a24688602` |

The protocol hash above covers the amended file. The frozen v1.0 hash (`c7951936eb162ab5...`) is reproduced by cutting at section 14 and re-adding `(none)`, as shown in the integrity review.

## 10. Proposed checkpoint commit (not made)

Contents: the 480 staged files above; the 4 deferred files stay untracked. All checks passed (hashes, no forbidden paths, no secrets, blobs equal inventory). Proposed command:

```
git commit -m "Preserve the controller cross-verification evidence: track sources, records and inventory; keep raw data outside history" -m "Narrows the verification ignore rules, stores verification evidence byte-exact, tracks 475 small evidence files (3.8 MB), and adds an evidence inventory with SHA-256 and a verify script. Raw data stays in place and in verification/evidence-archive; no data moved or deleted." -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

I did not run it; it is a decision for the owner. Undo before committing: `git restore --staged .` (leaves files untouched).

## 11. Future updates

See `evidence-storage-guide.md` section 4: run `verify`, never edit listed files, add new small records by explicit path, keep raw series outside Git and extend the archive, regenerate the inventory, copy Tier B to a second medium before any cleanup.
