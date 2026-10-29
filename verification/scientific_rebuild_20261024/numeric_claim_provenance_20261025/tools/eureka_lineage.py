"""Feature matrix of the KT01 LaTeX versions in D:\\EUREKA (read-only text scan).

    python -I tools/eureka_lineage.py   -> outputs/eureka_kt01_lineage.csv

For every KT01 .tex file (and the KT01 planning notes) it records creation/modification time and
whether specific strings are present: the headline numbers with and without ±, the body values
behind them, the Figure 9 table and Figure 11 formulas, and any sign of a computation (file
inputs such as \\input of data, pgfplots tables read from files, csvread, load(...)).
Files are only opened in binary read mode; nothing in D:\\EUREKA is executed or written.
"""

import csv
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

SRC = Path(r"D:\EUREKA")
OUT = Path(__file__).resolve().parent.parent / "outputs"
TZ = timezone(timedelta(hours=7))

FEATURES = {
    "headline_12.5": r"12[.,]5\s?\\?%",
    "headline_15.3": r"15[.,]3\s?\\?%",
    "pm_2.1": r"12[.,]5\\?%\s*(\$\\pm\$|±)\s*2[.,]1",
    "pm_2.8": r"15[.,]3\\?%\s*(\$\\pm\$|±)\s*2[.,]8",
    "pm_3.2": r"(\$\\pm\$|±)\s*3[.,]2\\?%",
    "body_95_to_85.3": r"95\s*Wh/km.{0,200}85[.,]3|85[.,]3.{0,200}95\s*Wh/km",
    "body_9.7pct": r"9[.,]7\s*Wh/km\s*=\s*9[.,]7",
    "body_16.5_14.2": r"16[.,]5\\?%.{0,300}14[.,]2\\?%",
    "body_14pct_fade": r"=\s*14\\?%\s*(improvement|reduction)",
    "fig11_formula_fixed": r"100\s*-\s*0\.002\*x\s*-\s*0\.000001\*x\^2",
    "fig11_formula_adaptive": r"100\s*-\s*0\.0017\*x\s*-\s*0\.0000008\*x\^2",
    "fig9_table_120_4.2": r"120\s+4\.2\s*\n\s*125\s+3\.8",
    "pgfplots_rand_noise": r"\\addplot[^\n]*\brand\b",
    "external_data_read": r"\\addplot[^\n]*table[^\n{]*\{[^}\n]*\.(csv|dat|txt)\}|\\pgfplotstableread|\\csvreader|\\input\{[^}]*\.(csv|dat)\}|csvread|load\(",
    "k_c_value": r"k_c\s*=\s*[0-9]|k_\{c\}\s*=\s*[0-9]",
    "k_cal_value": r"k_\{?cal\}?\s*=\s*[0-9]",
    "matlab_seed_42": r"randn\(.?seed.?,\s*42\)",
    "git_claim": r"version-controlled using Git",
    "tawfik": r"Tawfik|Asfoor|71711",
}


def iso(ts):
    return datetime.fromtimestamp(ts, TZ).isoformat(timespec="seconds")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    files = sorted([p for p in SRC.glob("*.tex") if p.name.upper().startswith("KT01")]
                   + list(SRC.glob("chapters_v7/KT01*.tex")) + list(SRC.glob("BaoCao_Poster/KT01*"))
                   + list(SRC.glob("KT01_MicroEV/*.md")) + [SRC / "chapter6_deployment.tex"],
                   key=lambda p: p.stat().st_ctime)
    rows = []
    for p in files:
        st = p.stat()
        text = open(p, "rb").read().decode("utf-8", errors="replace")
        row = {"relpath": str(p.relative_to(SRC)), "created": iso(st.st_ctime), "modified": iso(st.st_mtime),
               "size": st.st_size}
        for k, rx in FEATURES.items():
            row[k] = len(re.findall(rx, text, flags=re.S if "." in rx else 0))
        rows.append(row)
    OUT.mkdir(exist_ok=True)
    with open(OUT / "eureka_kt01_lineage.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    keys = list(FEATURES)
    print("created              " + " ".join(k[:9].rjust(9) for k in keys) + "  file")
    for r in rows:
        print(r["created"][:16], " ".join(str(r[k]).rjust(9) for k in keys), " ", r["relpath"])


if __name__ == "__main__":
    main()
