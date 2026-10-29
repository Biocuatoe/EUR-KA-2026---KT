"""Build source_candidate_manifest_20261025.csv from the pre/post hash snapshots and the inspection notes.

    python -I tools/eureka_candidate_manifest.py

Rows: every KT01-related file that was opened or text-scanned, plus one summary row per class of
file that was deliberately not opened. Hashes come from outputs/eureka_hashes_{pre,post}.csv.
"""

import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "outputs"

# relpath -> (category, inspection, relevant content, establishes provenance of 12.5 % / 15.3 %?)
NOTES = {
    "KT01_FINAL_REPORT.tex": ("LaTeX source v1", "regex context + lineage scan",
        "First appearance of 12.5 % and 15.3 % (line 162, Abstract, no ±). Already contains the Figure 11 formulas, the Figure 9 table and the Git claim. No calculation, no data input",
        "No - states the values"),
    "KT01_FINAL_REPORT.pdf": ("LaTeX build v1", "copied to scratchpad; pdftotext of the copy",
        "MiKTeX build 2026-09-07 04:23, 92 pages; abstract line has 12.5 %/15.3 % without ±", "No"),
    "KT01_FINAL_REPORT_v2.tex": ("LaTeX source v2", "regex context + lineage scan",
        "± 2.1 / ± 2.8 present after the edit saved 2026-09-08 00:41:35, 93 s after AUDIT_REPORT.md; also restates 15.3 % as '15.3 % extension' of battery lifetime (objectives table line 5828)",
        "No"),
    "KT01_FINAL_REPORT_v2_clean.tex": ("LaTeX source v2 (copy)", "regex context + lineage scan",
        "Saved 2026-09-07 05:40; headline numbers without ±", "No"),
    "KT01_FINAL_REPORT_v2.pdf": ("LaTeX build v2", "copied to scratchpad; pdftotext of the copy",
        "Build 2026-09-07 05:38, 177 pages; no ±", "No"),
    "KT01_FINAL_REPORT_v8.tex": ("LaTeX source of the submitted thesis", "read (Fig. 9 lines 1843-1885, Fig. 11 lines 2678-2706) + regex + lineage scan",
        "Fig. 11 = three typed pgfplots expressions (lines 2690-2694); Fig. 9 = typed 12-row table + chord + 2 markers (lines 1854-1876); Tables 16/18 typed literals (e.g. line 4658); k_c and k_cal named but never valued (line 2520-2524); seed only as typeset equation (line 3774); Git and 'available upon request' statements (lines 3778, 5246)",
        "No - presentation values only"),
    "KT01_FINAL_REPORT_v8.pdf": ("LaTeX build of the submitted thesis", "copied to scratchpad; pdftotext of the copy; paragraph match against the DOCX",
        "Build 2026-09-10 14:22, 155 pages; LoF/LoT page numbers equal the DOCX; 881/909 (96.9 %) DOCX body paragraphs found verbatim", "No"),
    "scripts\\render_kt01_figures.py": ("figure script (matplotlib)", "read in full as text; not executed",
        "13 figure functions; hard-coded arrays and seeded np.random noise (lines 245-248, 314-321, 458, 546-566); energy bars vs P-Control hard-coded (lines 283-285); single analytic SoH curve (line 143). Not the source of the submitted pgfplots Figures 9/11; its output folder figures_kt01 is empty",
        "No"),
    "KT01_MicroEV\\DATA_AND_COLAB_PROMPTS.md": ("planning note / Colab prompts", "read in full",
        "Line 3: use published numbers as 'ground truth' and simulate with 'reasonable noise' so results are 'indistinguishable from experiment'. Colab code: P-control vs non-adaptive LQR only; no SoH scheduling, no fade model; expected 'LQR ~8-15 % better than P-control' (line 709); outputs to KT01_MicroEV\\results (absent)",
        "No - no 12.5/15.3; no outputs present"),
    "KT01_MicroEV\\BLUEPRINT_200TRANG.md": ("planning note", "regex context",
        "Line 24: target stated in advance - SoH-adapted K to raise battery life by 15-20 %; line 25: to be shown by Monte Carlo of 100 cycles fixed vs adaptive K", "No"),
    "KT01_MicroEV\\PROMPTS_KT01.md": ("planning note", "regex context", "SoH via Coulomb counting + capacity fade (line 192); no numbers", "No"),
    "final_blueprint_KT01.md": ("planning note", "regex context",
        "Placeholders for a 1000-cycle fixed-vs-adaptive fade figure (lines 277-279, 360-365); no values", "No"),
    "AUDIT_REPORT.md": ("AI-generated audit note", "read in full",
        "Generated 2026-09-08 00:40 on KT01_FINAL_REPORT_v2.tex; C2 'Fabricated-Perfect Numbers'; recommends 'Add realistic uncertainty ranges (e.g. 12.5 ± 2.1%)' (line 28) and '±2.1 %' / '±3.2 %' (lines 195-196)",
        "No - documents the ± as a recommendation"),
    "CHANGELOG_v4.md": ("changelog", "regex context", "'Already had uncertainty bounds (12.5% ± 2.1%) - no change needed' (line 20)", "No"),
    "FIX_SUMMARY_v4.md": ("changelog", "regex context", "'Verified (uncertainty bounds present)' (line 32)", "No"),
    "OPUS5_STRESS_TEST_REPORT.md": ("AI-generated review note", "regex context",
        "Compares 12.5 % / 15.3 % with literature ranges by web search ('Verified 12.5% claim', line 311); plausibility only", "No"),
    "V8_CHANGELOG.md": ("changelog", "read lines 1-30, 100-130",
        "v8 adds content 'to reach 160-200 pages'; lists LHS Monte Carlo table, TCO, payback 3.86 y", "No"),
    "V8_FINAL_REPORT.md": ("summary note", "read lines 1-20, 105-125",
        "Key results 85.3 Wh/km (9.7 %), SoH fade 14.2 %/1000 cycles (14 %), Monte Carlo success 98.2 % - no calculation", "No"),
    "readme.md": ("assistant instructions", "read lines 205-240",
        "Integrity note on simulation-only results; support line 'Số liệu không khớp: tôi sẽ tinh chỉnh noise/scaling' (line 226)", "No"),
    "PHIEU_DANG_KY_EUREKA_2026.md": ("registration form draft", "regex context", "Vietnamese summary repeats 12,5 % and 15,3 % (line 27)", "No"),
    "refs.bib": ("bibliography", "regex count", "0 matches for Tawfik/Asfoor/71711", "No"),
    "refs_BACKUP_v9.bib": ("bibliography backup", "regex count", "0 matches for Tawfik/Asfoor/71711", "No"),
}


def read(name):
    with open(OUT / name, encoding="utf-8") as f:
        next(f)
        return {r["relpath"]: r for r in csv.DictReader(f)}


def main():
    pre, post = read("eureka_hashes_pre.csv"), read("eureka_hashes_post.csv")
    lineage = {r["relpath"] for r in csv.DictReader(open(OUT / "eureka_kt01_lineage.csv", encoding="utf-8"))}
    rows = []
    for rel in sorted(set(NOTES) | lineage, key=str.lower):
        a, b = pre[rel], post[rel]
        cat, how, content, prov = NOTES.get(rel, ("KT01 LaTeX version / fragment", "lineage scan (eureka_lineage.py)",
                                                   "feature counts in outputs/eureka_kt01_lineage.csv", "No"))
        if rel in NOTES and rel in lineage and "lineage" not in how:
            how += " + lineage scan"
        rows.append({"relpath": "D:\\EUREKA\\" + rel, "size": a["size"], "created": a["ctime"], "modified": a["mtime"],
                     "sha256_pre": a["sha256"], "sha256_post": b["sha256"],
                     "unchanged": a["sha256"] == b["sha256"] and a["mtime"] == b["mtime"] and a["size"] == b["size"],
                     "category": cat, "inspection": how, "relevant_content": content,
                     "establishes_provenance": prov})
    untouched = [r for r in pre if r not in NOTES and r not in lineage]
    groups = {
        "CNTT02 thesis files (separate thesis; out of scope)": lambda r: "cntt02" in r.lower(),
        "page-render / layout-check PNG and PPM images (classified by name only)": lambda r: r.lower().endswith((".png", ".ppm")),
        "LaTeX build by-products (.aux .bcf .lof .lot .out .toc .log .run.xml .bbl .blg .thm)": lambda r: r.lower().endswith(
            (".aux", ".bcf", ".lof", ".lot", ".out", ".toc", ".log", ".xml", ".bbl", ".blg", ".thm")),
        "pandoc distribution and pandoc.zip (third-party binary)": lambda r: r.lower().startswith("pandoc"),
    }
    for label, test in groups.items():
        members = [r for r in untouched if test(r)]
        untouched = [r for r in untouched if not test(r)]
        rows.append({"relpath": f"[{len(members)} files] " + label, "size": sum(int(pre[m]["size"]) for m in members),
                     "created": "", "modified": "", "sha256_pre": "see outputs/eureka_hashes_pre.csv",
                     "sha256_post": "see outputs/eureka_hashes_post.csv",
                     "unchanged": all(pre[m]["sha256"] == post[m]["sha256"] for m in members),
                     "category": "not opened", "inspection": "metadata and hash only", "relevant_content": "",
                     "establishes_provenance": "not assessed"})
    rows.append({"relpath": f"[{len(untouched)} files] other notes, templates, fix scripts, posters, test files",
                 "size": sum(int(pre[m]["size"]) for m in untouched), "created": "", "modified": "",
                 "sha256_pre": "see outputs/eureka_hashes_pre.csv", "sha256_post": "see outputs/eureka_hashes_post.csv",
                 "unchanged": all(pre[m]["sha256"] == post[m]["sha256"] for m in untouched),
                 "category": "not opened beyond the repository-wide regex search for 12.5 %/15.3 %/±",
                 "inspection": "metadata, hash, Grep count", "relevant_content": "; ".join(sorted(untouched))[:3000],
                 "establishes_provenance": "not assessed"})
    with open(HERE / "source_candidate_manifest_20261025.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(len(rows), "rows;", sum(1 for r in rows if not str(r["relpath"]).startswith("[")), "individual files;",
          "all unchanged:", all(r["unchanged"] for r in rows))


if __name__ == "__main__":
    main()
