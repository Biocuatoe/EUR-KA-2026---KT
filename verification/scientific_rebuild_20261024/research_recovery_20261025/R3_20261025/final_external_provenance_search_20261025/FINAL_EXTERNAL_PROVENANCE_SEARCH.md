# Final external provenance search: original evidence for the 12.5 % and 15.3 % claims

**Date:** 2026-10-25, about 20:15–20:41 +07:00.
**Question:** is there a surviving, pre-existing, independently checkable computational evidence chain, *outside* `D:\EUREKA`, that could substantiate either original result?
**Cut-off:** both central estimates first appear in `D:\EUREKA\KT01_FINAL_REPORT.tex` (v1), saved by 2026-09-07 04:22 local time; both ± terms first appear on 2026-09-08 at 00:41:35. The basis is `../earliest_claim_provenance_20261025/EARLIEST_CLAIM_PROVENANCE_AUDIT.md`, which was read and not repeated here.

**Answer: no.** The bounded search found no pre-cut-off computational artifact for any of the four values.

---

## 1. Executive verdict

| Claim | Verdict for this search | Earlier verdict (unchanged) |
|---|---|---|
| **12.5 %** energy improvement | **No surviving evidence found in searched locations** | Present but unsubstantiated. v1's own typed energy table gives 10.29 % mean, 12.07 % maximum vs fixed LQR |
| **± 2.1 %** | **No surviving evidence found in searched locations** | Present but unsubstantiated. First appears 93 s after an AI audit note suggested "e.g., 12.5 ± 2.1 %" |
| **15.3 %** fade reduction over 1000 cycles | **No surviving evidence found in searched locations** | Contradicted by a reproducible calculation: v1's own typed values give 5.33 % |
| **± 2.8 %** | **No surviving evidence found in searched locations** | Present but unsubstantiated. The note had suggested ±3.2 %; the origin of 2.8 is undetermined |

No artifact found here was classed **A** (pre-cut-off computational evidence) or **B** (pre-cut-off mention) for any claim. Nothing found here changes an earlier verdict. "Not found in the searched locations" does not mean the evidence never existed.

---

## 2. Search scope

### 2.1 Searched

| Location | What was inspected | Result |
|---|---|---|
| `D:\` root | Directory and file names | 46 entries. Two candidates by name and date: `D:\drive-download-20260906T174904Z-1-001` (Drive export at 09-07 00:49 local) and `D:\Khánh 7-9` (09-07 06:06). The rest are named for other projects (CareLens, hackathons, course labs, the CNTT thesis) or are system or game folders |
| `D:\drive-download-20260906T174904Z-1-001` | File listing (12 files) | Group-photo images, a ChatGPT-generated image and photo-composition scripts. Unrelated; contents not opened |
| `D:\Khánh 7-9` | File listing (20 files) | `CONTEXT_ASTRA_MO_HINH_ESG (1).docx` plus its unzipped XML, an image and `xaml.md`. Unrelated (ESG model); contents not opened |
| All other `D:\` project folders, about 97,000 files | **File names and timestamps only.** Pruned: `node_modules`, `.git`, `.venv`, `venv`, `site-packages`, `__pycache__`, `cache`, `tools`, `.next`, `dist`; then cache, package, vendor and build paths filtered out (49,851 files left). No access errors | No KT01, LQR, micro-EV, SoH, capacity, fade, ageing, drive-cycle, NEDC/WLTP, Colab-research or Tawfik file names related to this thesis. Name hits were coincidental: a `…bfade…` hash in an image name, a 2026-10 course-lab Colab folder, a 2026-10 VinFast web crawler in `P-073` |
| Pre-cut-off text-type files outside the KT project (10,335 files: `.ipynb .py .m .mlx .csv .tsv .jl .tex .md .txt .json`, dated ≤ 2026-09-08) | **Content** grep for `LQR`, `state of health`, `capacity fade`, `micro-EV`, `Riccati`, `regenerative brak`, `12.5 %`, `15.3 %` | **0 files matched** |
| `C:\Users\HLC\Documents`, `Desktop`, `OneDrive` | Top-level listing | No research folders. Documents holds game, Arduino, GitHub and compiler-wrapper items; OneDrive holds one teaching-material folder and a Personal Vault link (not opened) |
| `C:\Users\HLC\Downloads` (505 files to depth 3) | Names filtered by research file types and keywords; archive member lists | **Spreadsheets:** `Book1.xlsx` is a list of film titles (created 2026-08-19); `Dulieu_SinhDuoc.xlsx` is a biostatistics dataset (created 2026-04-16). Both unrelated (cell text and sheet names read). **Archives:** four `drive-download-2026090[5-6,10]*.zip` (listing only) hold videos, a startup-competition poster and video, and personal ID photos; unrelated. **Other:** `Kế hoạch - Thể lệ Euréka 2026.pdf` is the competition rules, not evidence |
| Editor local history: VS Code (48 entries), Cursor (208), Windsurf (1) | `entries.json` resource paths, then the saved versions of matching files | Cursor holds versions of six `D:\EUREKA` files, two of them KT01: `KT01_MicroEV\DATA_AND_COLAB_PROMPTS.md` and `BaoCao_Poster\KT01_poster_outline.md`. **Earliest snapshot: 2026-09-08 15:33:13, after the cut-off.** Every snapshot is byte-identical to the live file (§3). VS Code and Windsurf hold nothing relevant |
| Cursor workspace record for `D:\EUREKA` (`…\Cursor\User\workspaceStorage\2ff2b3ac55381b266f5abc6fd06dcc7e\`) | Folder listing and `workspace.json` only | `workspace.json` was created **2026-09-07 02:09:01**, before any KT01 file. It holds 60 images pasted into the workspace's chat (09-07 04:20 → 09-10) and `state.vscdb` (not opened; §7) |
| Word AutoRecover / Office UnsavedFiles | File names and dates | Only `AutoRecovery save of report_copy.asd` (saved 2026-10-25 08:39, post-cut-off) and pre-2026 files. Not opened |
| Jupyter (`AppData\Roaming\jupyter`, `.jupyter`, `.ipython`) and MATLAB (`Documents\MATLAB`, `AppData\Roaming\MathWorks`) | Presence check | Absent, or `.ipython` empty |
| `AppData\Roaming\Microsoft\Windows\Recent` | Shortcut **names** filtered by fingerprints | One match: `EUREKA_Adaptive_LQR_Research_Repo_Starter.lnk`, created **2026-10-23 12:31**. Its target, `C:\Users\HLC\Downloads\EUREKA_Adaptive_LQR_Research_Repo_Starter\…`, **no longer exists**. Post-cut-off; it matches the start of the current rebuild project |
| `D:\EURÉKA 2026 - KT` (current project) | Names and timestamps | The only files dated before 2026-10-01 are the submitted thesis DOCX and its copy (2026-09-21, post-cut-off) |
| `D:\EURÉKA 2026 - CNTT` (unrelated CNTT thesis) | Names only | 111 files, none dated ≤ 2026-09-08; no fingerprint names |

### 2.2 Skipped on purpose

- **`D:\EUREKA`:** already fully audited. It was re-hashed only as an integrity check (§9).
- Windows system folders, `Program Files`, `WindowsApps`, `WpSystem`, `System Volume Information`, `$RECYCLE.BIN`, `pagefile.sys`.
- Game and media folders: `Riot Games`, `.minecraft`, `OBS`, `Capcut`.
- Dependency caches and environments: `D:\AI\Cache`, all `.venv`, `node_modules`, `site-packages`.
- The rest of `AppData`.
- Browser profiles, credential stores, messaging apps (e.g. `Zalo Received Files`), the OneDrive Personal Vault.
- A Google OAuth `client_secret_*.json` in Downloads. It is a credential and was not opened.
- **Cursor chat and agent databases:** the workspace and global `state.vscdb`, and the images pasted into that chat. These are conversation records; see §7 for why they matter.
- All cloud accounts (Google Drive, Colab, ChatGPT, Cursor cloud). There was no network access and no sign-in.

The whole machine was **not** searched. Pictures, Videos, Music and the C:\ root outside the user profile were not inspected.

---

## 3. Strongest candidates, in time order

| # | Time (+07:00) | Artifact | Category | Why it matters / what it shows |
|---|---|---|---|---|
| 1 | 2026-09-07 02:09:01 | Cursor workspace record `workspaceStorage\2ff2b3ac…\workspace.json` → `{"folder": "file:///d%3A/EUREKA"}` | Context | The early KT01 work was done in a Cursor workspace opened on `D:\EUREKA` 14 minutes before the first planning note |
| 2 | **2026-09-07 04:20:05** | `…\2ff2b3ac…\images\image-7ce5a2cb-3e69-494c-b633-501606f5237d.png` (12,331 bytes; created = modified) | **D: chronology credible, content unknown** | An image pasted into the workspace's chat **2 minutes before v1 was saved**. Not viewed (conversation attachment). Its size is small for a results plot but suits a screenshot of text or a table. It is the only surviving pre-cut-off artifact outside `D:\EUREKA` that could bear on how v1 was written |
| 3 | 2026-09-08 15:33:13 → 2026-10-25 20:23:50 | Cursor local history of `KT01_MicroEV\DATA_AND_COLAB_PROMPTS.md` (`…\History\5ded9712\`, 10 snapshots) | **C: post-cut-off** | All snapshots are byte-identical to the live file (SHA-256 `ef058e46…c2ec8`): 0 × "12.5", 0 × "15.3", 44 × "LQR", no ageing terms. No version older than 09-08 15:33 is retained, so the pre-v1 content of this note remains unknown |
| 4 | same | Cursor history of `BaoCao_Poster\KT01_poster_outline.md` (`…\History\-6c786acc\`, 10 snapshots) | C | Identical to the live file (`bc95aab0…6a6`); no target values |
| 5 | 2026-10-23 12:31 | `Recent\EUREKA_Adaptive_LQR_Research_Repo_Starter.lnk` | C | Target folder missing. Post-cut-off; it can't hold original 2026-09 computation |
| 6 | 2026-10-25 08:39 | `Word\AutoRecovery save of report_copy.asd` | C | Post-cut-off autosave; not opened |

**No candidate in category A or B was found.**

---

## 4. File-level evidence table

| Path | Size | Timestamp basis | SHA-256 | Attribution | Verdict |
|---|---|---|---|---|---|
| `C:\Users\HLC\AppData\Roaming\Cursor\User\workspaceStorage\2ff2b3ac55381b266f5abc6fd06dcc7e\workspace.json` | 37 | NTFS created/modified 2026-09-07 02:09:01 | not hashed (metadata only) | KT01/CNTT02 workspace (`D:\EUREKA` held both) | Context only |
| `…\2ff2b3ac…\images\image-7ce5a2cb-3e69-494c-b633-501606f5237d.png` | 12331 | NTFS created = modified 2026-09-07 04:20:05.56. No internal date read | `6d94fd471d1150224646b021b45d2f4d8c64ec990faf0f32f1497566facfde02` | Ambiguous (shared workspace; content not viewed) | **Attribution or chronology ambiguous**; owner review needed |
| `…\2ff2b3ac…\state.vscdb` | 69632 | Last written 2026-10-25 20:28:43 (by a Cursor session, §9) | not read | Workspace state | Not inspected (conversation data) |
| `C:\Users\HLC\AppData\Roaming\Cursor\User\History\5ded9712\*` (10 versions) | 27796 each | `entries.json` timestamps 09-08 15:33:13 … 10-25 20:23:50 | all `ef058e46781e0c535f36a1a9fea9f8b3aabf703590c8cf55d58ede0f331b2ec8` | KT01 | Post-cut-off; mention only (no targets) |
| `C:\Users\HLC\AppData\Roaming\Cursor\User\History\-6c786acc\*` (10 versions) | 4663 each | same | all `bc95aab003c2fb8493cbe7481e4277ae62795d2f66de7f748add3c9315b636a6` | KT01 | Post-cut-off; no targets |
| `C:\Users\HLC\Downloads\Book1.xlsx` | 11475 | docProps created 2026-08-19T08:19Z | `b299e0bd519e509c…` (prefix) | Unrelated (film titles) | Not relevant |
| `C:\Users\HLC\Downloads\Dulieu_SinhDuoc.xlsx` | 33243 | docProps created 2026-04-16T17:06Z | `98d6f9070c747765…` (prefix) | Unrelated (biostatistics) | Not relevant |
| `C:\Users\HLC\Downloads\drive-download-20260905T152039Z-1-001.zip` | 1921192082 | Zip member dates 2026-08-17 | `11b323e5d18d410193e87f32ca25382d94eb95dedc2efbc447ae9348f54bf8aa` | Unrelated (2 videos) | Not relevant |
| `…\drive-download-20260906T184026Z-1-001.zip` | 174474795 | members 2026-06-25 | `b38d05b15b2aa8807419d56f9201a736bf828701d330c91643c49708871cf168` | Unrelated (startup poster/video) | Not relevant |
| `…\drive-download-20260906T184130Z-1-001.zip` | 143036917 | members 2026-06-25 | `56952477f666603be341be6cee8e0362da507431abaadc9d0de20e65f3623b13` | Unrelated | Not relevant |
| `…\drive-download-20260910T072945Z-1-001.zip` | 3653069 | members 2026-09-08/09 | `602ff4456500c6efe3f8bb9b2658185000ccd662c1ac8334a302ec310ca14935` | Unrelated (personal ID photos) | Not relevant |
| `C:\Users\HLC\AppData\Roaming\Microsoft\Windows\Recent\EUREKA_Adaptive_LQR_Research_Repo_Starter.lnk` | 1303 | created 2026-10-23 12:31:16 | not hashed | EURÉKA rebuild (post-cut-off) | Post-cut-off; target absent |

---

## 5. Computational chains found

**None.** No file outside `D:\EUREKA`, in the searched locations, contains any of:
- a controller definition, drive-cycle input or energy-accounting routine;
- an ageing model with parameters, or 1000-cycle outputs;
- repeated runs from which 12.5 %, 15.3 %, ±2.1 % or ±2.8 % could be recomputed.

There was nothing to recalculate. **Energy** (§6 of the brief): no same-task fixed-LQR vs SoH-aware comparison exists in the searched locations. **Fade** (§7): no cell model, parameter set, current/SoC trajectory or cycle procedure exists. **Uncertainty terms** (§8): no observations, sample size or statistic exists for either ± value.

---

## 6. Pre-cut-off original evidence vs later corroboration

- **Pre-cut-off original computational evidence (A):** none found.
- **Pre-cut-off mention (B):** none outside `D:\EUREKA`. The planning-note targets inside it ("15–20 %", "15 %", "~8–15 % vs P-control") were covered in the earlier audit. Their pre-v1 wording is still unknown, because the oldest Cursor snapshot is from 09-08 15:33.
- **Later corroboration:** none for the original percentages. The project's own R3 study (2026-10-25) is a new, independent calculation. It found SoH scheduling worth ≤ 0.04 % on the same task (`../R3_claim_implications.md`). That is evidence *against* a material SoH-scheduling benefit on this plant class, not corroboration.

---

## 7. Strongest remaining legitimate recovery paths

These could still hold original evidence. Each needs the owner's own action; none was taken here.

1. **Cursor chat and agent history for the `D:\EUREKA` workspace.** Review it in the Cursor application yourself:
   - `…\workspaceStorage\2ff2b3ac55381b266f5abc6fd06dcc7e\state.vscdb`;
   - the global `…\Cursor\User\globalStorage\state.vscdb` (3.96 GB);
   - the pasted image of **2026-09-07 04:20:05** (§3 #2).

   The workspace was opened at 02:09, before every KT01 file, and v1 was saved at 04:22. If the claim sentence came from a computation shown to the assistant, or was proposed by it, this is where that would be recorded. *This is conversation data, so it was not opened under this brief's restrictions.* Before reviewing, **copy** the files rather than opening Cursor on the live folder (see §9 for why).
2. **Google Colab and Google Drive** (cloud; not accessed). `KT01_MicroEV\DATA_AND_COLAB_PROMPTS.md` designs Colab runs whose declared outputs (`KT01_energy_results.csv`, `KT01_benchmark.csv`) never reached any local folder. A Colab notebook with saved outputs and a revision history dated before 2026-09-07 04:22 would be category A evidence. Any notebook derived from that note compares **P-control with a plain LQR**, so at most it could support a different claim, not the fixed-LQR vs SoH-aware LQR claim.
3. **Other AI-assistant accounts the owner used** (cloud; not accessed). A ChatGPT-generated image dated 09-07 00:58 sits in a nearby unrelated folder, which shows such tools were in use that night. Any exported conversation dated before 04:22 would show whether the numbers were computed or composed.

No local recovery path remains for the **±2.1 % / ±2.8 %** terms beyond these. Their closest documented antecedent is still the AI audit note of 09-08 00:40.

---

## 8. Missing evidence and limitations

- **Cloud sources** (Colab, Drive, assistant histories) were not searched: no network, no sign-in.
- **Cursor conversation databases** and pasted images were deliberately not opened (privacy restriction). They are the main unexamined local source.
- **Editor history retention** reaches back only to 2026-09-08 15:33 for the `D:\EUREKA` files. Cursor's own session logs survive only from 2026-09-28. Nothing older can be recovered from editor history.
- **Coverage:**
  - most of the D:\ file population was searched by **name** only;
  - content was checked only for the 10,335 pre-cut-off text-type files outside the KT project;
  - binary formats (`.mat`, `.npy`, `.xlsx` other than the two above, PDFs, images) were not content-searched outside `D:\EUREKA`;
  - none with a fingerprint name or a plausible location was found.
- **Not inspected:** Pictures, Videos, Music, the C:\ root outside the profile, and the rest of `AppData`.
- **Timestamps:** NTFS dates can be rewritten. Proof: §9. The 04:20:05 image date is a file-system date only; no internal metadata was read.

---

## 9. Integrity confirmation and side effects

**What this investigation wrote:** only this report, in this new folder (confirmed absent before writing). Working files are in the session scratchpad:
- `dscan.tsv`, SHA-256 prefix `5affb6337f15…`;
- `eureka_recheck.csv`, `9db8e50fa87b…`;
- `history.py`, `af7c2bd258d0…`;
- `ziplist.py`, `75b09d97bb2d…`.

**What it did not do:**
- no edit, rename, move, delete, extraction, execution of project or research code, Git command, network access, install or sign-in;
- the thesis files, sources, protocols, audits and R1/R2/R3 outputs were not touched;
- files were read in binary mode, through `zipfile` member listing, or with `strings` (one `.lnk` file).

**An outside modification of `D:\EUREKA`, observed during this investigation and not caused by it:**
- `D:\EUREKA` was re-hashed at 20:30:28 and compared with the post-audit snapshot of 20:06:41.
- Content (SHA-256) and size are unchanged for all 439 files.
- But **the modification time of 6 files was rewritten to 2026-10-25 20:23:50**: `QUICKSTART_30PH.md`, `BaoCao_Poster\CNTT02_report.tex`, `BaoCao_Poster\KT01_poster_outline.md`, `CNTT02_STGNN\DATA_AND_COLAB_PROMPTS.md`, `CNTT02_STGNN\PROMPTS_CNTT02.md`, `KT01_MicroEV\DATA_AND_COLAB_PROMPTS.md`.
- At the same second, Cursor wrote an "Undo Create Diff" history entry for each of these files.
- A Cursor session started at **20:23:24** (log folder `Cursor\logs\20261025T202324`) and last wrote `state.vscdb` at 20:28:43. Cursor was no longer running at 20:30.
- This investigation's last write before then was at 20:10:15, and none of its commands target those paths or launch Cursor.
- The rewrite therefore came from a Cursor session opened on `D:\EUREKA` outside this investigation. It was **not** reversed, because that would itself be a write.

**Consequence for the earlier audit.** These are exactly the files whose modification times had shown the identical "batch" value 2026-09-13 17:03:27. Their Cursor snapshots are byte-identical across every recorded session from 09-08 15:33 onward. The batch timestamps are therefore **consistent with editor rewrites of unchanged content**, not with content edits. That explanation is not proven for the 09-08 03:48:40 batch, which has no matching snapshot.

**Last-access times:** reads update last-access times on both D: and C: on this machine. This investigation updated them on every file it opened or hashed:
- the 439 `D:\EUREKA` files (re-hash);
- the Cursor history snapshots;
- the pasted image (hash);
- the spreadsheets and archives listed in §4;
- the 10,335 content-checked files.

They were not reset.

---

## 10. Final determination

- A surviving, pre-existing, independently checkable computational chain for **12.5 %**, **15.3 %**, **±2.1 %** or **±2.8 %**: **not found in the searched locations.**
- The earlier verdicts stand unchanged.
- The only unexamined local lead with credible pre-cut-off timing is the Cursor conversation record for the `D:\EUREKA` workspace, including the image pasted at 2026-09-07 04:20:05. Only the owner can legitimately review it.
