"""Start-of-task state v10 (task 'Attempt 11'). Read-only except new v10 logs in the pilot's logs/ (refuses to overwrite).
- Project pre-hash (repo minus .git, .venv, cache, tools and the pilot dir).
- Verification of the pilot manifest v9, the attempt 3-10 manifests, the attempt-2 release manifest, the frozen hashes,
  candidates rev3-rev10, the review reports and the attempt-10 gate record.
- The baseline of attempt 11: the pilot's code/ and config/ equal attempt 10's copy, file by file.
- The line-ending convention (CRLF / LF-only line counts) of every code file in the pilot."""
import csv, hashlib, json, os, sys, time
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
RR = REPO / "verification" / "research_recovery_20261028"
P, C = RR / "R4_20261028_pilot", RR / "R4_20261028_campaign"
RA = C / "release_attempts"
LOGS = P / "logs"
outs = dict(started=LOGS / "zz_v10_pre_hash_started.txt", pre=LOGS / "zz_pre_hash_project_v10.csv",
            check=LOGS / "zz_start_state_v10.json", eol=LOGS / "zz_line_endings_rev13_baseline.csv")
for p in outs.values():
    if p.exists():
        sys.exit(f"refused: {p} exists")
outs["started"].write_text(time.strftime("%Y-%m-%d %H:%M:%S %z") + "\n", encoding="utf-8")
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def verify(manifest, root, exclude=()):
    rows = list(csv.DictReader(open(manifest, encoding="utf-8")))
    bad = [r["path"] for r in rows if not (root / r["path"]).is_file() or sha(root / r["path"]) != r["sha256"]]
    listed = {r["path"] for r in rows} | set(exclude)
    extra = sorted(q.relative_to(root).as_posix() for q in root.rglob("*") if q.is_file()
                   and q.relative_to(root).as_posix() not in listed)
    return dict(manifest=str(manifest.relative_to(RR)), sha256=sha(manifest), rows=len(rows), mismatched=bad,
                unlisted=extra[:50], n_unlisted=len(extra))


EXPECT = {"attempt3": ("attempt3_amendment2", "e33cdcb9b9ff6c9e50d34ab00acdc53a21dac4fe87c20e79c41158f84f5da9d3"),
          "attempt4": ("attempt4_owner_rulings", "0727aa086b3da7639c680a0bdd4f84ce58f7fe11133e64526727841cbcb91c89"),
          "attempt5": ("attempt5_owner_rulings", "c32601c33365dc5c06f563d0ccec01c483208809499d87f3f2d7d944a4f3ca00"),
          "attempt6": ("attempt6_review_fixes", "b19ddce7373aff8e02ae854986f3107355ea244a05e0a4b62831623b96ad4c3a"),
          "attempt7": ("attempt7_final_review", "42e8c88f35edd49e206354173a79925050eae395a52b04a5fba7675f32a1f933"),
          "attempt8": ("attempt8_final_owner_decisions", "2ea8714f3f492e8ceaa5cf345182ce243ef8dab51415f55413fc45bf5300a617"),
          "attempt9": ("attempt9_review_fixes", "0e317eef0a0a7ab54af9c2c69aee4af619693dabcf5ca441d2a7c386f5766ffc"),
          "attempt10": ("attempt10_review_fixes", "9af4b502cbc01fb1ee657ac0f509f71a59b87f8467d7e7e5a8dfc0b9aa6c84a8")}
CANDS = {"rev3": ("03_protocol_v1_amendment_2_DRAFT.md", "fdaf193de510488733f0e0899d50def86cbeafabdbecdd3bc7a144099b6f492c"),
         "rev4": ("03_protocol_v1_amendment_2_rev4_CANDIDATE.md", "c726560d1e87036cbd94fe58724cafdc1e4746647f6cfacbb320f3e14ed143ab"),
         "rev5": ("03_protocol_v1_amendment_2_rev5_CANDIDATE.md", "e7ba73c11784b3cf38f48e32b69a7a7c21b070d039118547d638bc1bf06d4f5f"),
         "rev6": ("03_protocol_v1_amendment_2_rev6_CANDIDATE.md", "0dcb767e97e19f40c00735d9efaecf8d21c396c23952b70e60ccb21a3f711e1f"),
         "rev7": ("03_protocol_v1_amendment_2_rev7_CANDIDATE.md", "0e3ef3112c979237e7079f176b21dd4f2ce682c7ab435f36f33321ffe67a5996"),
         "rev8": ("03_protocol_v1_amendment_2_rev8_CANDIDATE.md", "f6430bf5512cb56065a2465bcfda1c4c42e244b80f73fcd3e88d985ac8811f7c"),
         "rev9": ("03_protocol_v1_amendment_2_rev9_CANDIDATE.md", "cdeea032c520f408f1f300a53cf1bc8b1ec4582d80340d3df2c2c94fa5d45719"),
         "rev10": ("03_protocol_v1_amendment_2_rev10_CANDIDATE.md", "5479f0e81b981c7977ea5a416762972d2a332d4fdb75beee7ad8379ade399804")}
FROZEN = {"protocol_v1": (RR / "R4_20261028_preflight/03_R4_protocol_v1.md",
                          "f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab"),
          "amendment_1": (C / "release/03_R4_protocol_v1_amendment_1.md",
                          "7720fed75bb678e47a229d00aff154e0aa14607c051f4a1163cc9bf67b6abee2"),
          "amendment_1_approval": (C / "release/amendment_1_approval.json",
                                   "03f835e9311410095e4447840ecb2b02d95c50279527df5fdf2f6d334e15eecd")}
res = dict(started=outs["started"].read_text().strip(),
           pilot_v9=verify(P / "zz_sha256_manifest_v9.csv", P, ["zz_sha256_manifest_v9.csv", "logs/zz_manifest_v9_sha256.txt",
                                                                "logs/zz_v10_pre_hash_started.txt"]),
           pilot_v9_recorded=(LOGS / "zz_manifest_v9_sha256.txt").read_text(encoding="utf-8").split()[2],
           **{n: dict(verify(RA / d / f"zz_sha256_manifest_{n}.csv", RA / d, [f"zz_sha256_manifest_{n}.csv"]), expected=h)
              for n, (d, h) in EXPECT.items()},
           attempt2_root=verify(C / "zz_sha256_manifest_release.csv", C, ["zz_sha256_manifest_release.csv"]),
           frozen={k: dict(sha256=sha(p), expected=h, equal=sha(p) == h) for k, (p, h) in FROZEN.items()},
           candidates={k: dict(sha256=sha(P / f), expected=h, equal=sha(P / f) == h) for k, (f, h) in CANDS.items()},
           review_reports={q.name: sha(q) for q in sorted((P / "review").glob("*.md"))},
           attempt10_gate_record=sha(RA / "attempt10_review_fixes/GATE_RECORD_attempt10.json"),
           attempt11_exists=(RA / "attempt11_final_owner_decisions").exists(),
           campaign_authorization_exists=(C / "release/campaign_authorization.json").exists(),
           issued_amendment_2_exists=(C / "release/03_R4_protocol_v1_amendment_2.md").exists(),
           amendment_2_approval_exists=(C / "release/amendment_2_approval.json").exists(),
           campaign_outputs_exists=(C / "outputs").exists())
A10 = RA / "attempt10_review_fixes"
pf = {q.relative_to(P).as_posix(): sha(q) for d in ("code", "config") for q in sorted((P / d).rglob("*")) if q.is_file()}
af = {q.relative_to(A10).as_posix(): sha(q) for d in ("code", "config") for q in sorted((A10 / d).rglob("*")) if q.is_file()}
res["baseline_pilot_equals_attempt10"] = dict(pilot_files=len(pf), attempt10_files=len(af), equal=pf == af,
                                              differing=sorted(k for k in set(pf) | set(af) if pf.get(k) != af.get(k)))
eol = []
for q in sorted((P / "code").rglob("*.py")):
    b = q.read_bytes()
    crlf = b.count(b"\r\n")
    eol.append(dict(path=q.relative_to(P).as_posix(), crlf=crlf, lf_only=b.count(b"\n") - crlf,
                    convention="CRLF" if crlf and b.count(b"\n") == crlf else "LF" if not crlf else "MIXED"))
with open(outs["eol"], "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(eol[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(eol)
res["line_endings"] = {c: sum(1 for e in eol if e["convention"] == c) for c in ("CRLF", "LF", "MIXED")}
SKIP_TOP = {".git", ".venv", "cache", "tools"}
post = {}
for dp, dns, fns in os.walk(REPO):
    d = Path(dp)
    if d == REPO:
        dns[:] = [x for x in dns if x not in SKIP_TOP]
    dns[:] = [x for x in dns if d / x != P]
    for fn in fns:
        q = d / fn
        st = q.stat()
        post[str(q.relative_to(REPO))] = (st.st_size, st.st_mtime_ns, sha(q))
with open(outs["pre"], "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["path", "bytes", "mtime_ns", "sha256"])
    for k in sorted(post):
        w.writerow([k, *post[k]])
res["project_files"] = len(post)
outs["check"].write_text(json.dumps(res, indent=1), encoding="utf-8")
ok = (all(v["equal"] for v in res["frozen"].values()) and all(v["equal"] for v in res["candidates"].values())
      and all(not res[n]["mismatched"] and res[n]["sha256"] == res[n]["expected"] for n in EXPECT)
      and not res["pilot_v9"]["mismatched"] and res["pilot_v9"]["sha256"] == res["pilot_v9_recorded"]
      and not res["attempt2_root"]["mismatched"] and res["baseline_pilot_equals_attempt10"]["equal"]
      and not res["attempt11_exists"] and not res["campaign_authorization_exists"] and not res["issued_amendment_2_exists"]
      and res["line_endings"]["MIXED"] == 0)
print(json.dumps(dict(all_ok=ok, project_files=len(post), line_endings=res["line_endings"],
                      unlisted={k: res[k]["n_unlisted"] for k in ("pilot_v9", *EXPECT, "attempt2_root")},
                      baseline=res["baseline_pilot_equals_attempt10"]), indent=1))
