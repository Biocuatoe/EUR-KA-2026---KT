"""Post-task integrity checks (v10, task 'Attempt 11'). Read-only except the new v10 log files in the pilot's logs/ (refuses to overwrite).
1. Evidence snapshot: manifest SHA-256 and every row (snapshot copy exists, size, hash, manifest consistency).
   Reads the snapshot copies only; never D:\\EUREKA.
2. Preflight: zz_R4_file_manifest.csv rows; no file added or removed vs the v10 pre-hash.
3. Frozen protocol, issued amendment 1, its approval record.
4. Project post-hash with the v10 pre-hash scope (repo minus .git, .venv, cache, tools and the pilot directory); comparison."""
import csv, hashlib, json, os, sys, time
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
RR = REPO / "verification" / "research_recovery_20261028"
LOGS = RR / "R4_20261028_pilot" / "logs"
outs = {k: LOGS / v for k, v in dict(rows="zz_snapshot_rows_v10_post.csv", snap="zz_snapshot_summary_v10_post.json",
                                     post="zz_post_hash_project_v10.csv", cmp="zz_pre_post_comparison_v10.txt",
                                     summ="zz_integrity_v10_post.json").items()}
for p in outs.values():
    if p.exists():
        sys.exit(f"refused: {p} exists")
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
res = {"written": time.strftime("%Y-%m-%dT%H:%M:%S%z")}

# 1. snapshot
SNAP = Path(r"C:\Users\HLC\EUREKA_EVIDENCE\GATE1_20261028\MANIFEST.sha256.csv")
msha = sha(SNAP).upper()
rows = list(csv.DictReader(open(SNAP, encoding="utf-8-sig")))
srows, ok = [], 0
for r in rows:
    sp = Path(r["snapshot_path"])
    s1 = sp.is_file()
    s2 = s1 and sp.stat().st_size == int(r["source_size_bytes"])
    s3 = s1 and sha(sp).upper() == r["snapshot_sha256"].upper()
    s4 = (r["source_sha256"].upper() == r["source_sha256_end"].upper() == r["snapshot_sha256"].upper()
          and r["verified"] == "True" and not r["error"])
    flag = s1 and s2 and s3 and s4
    ok += flag
    srows.append(dict(source_path=r["source_path"], snapshot_path=r["snapshot_path"], S1_exists=s1, S2_size=s2,
                      S3_snapshot_hash=s3, S4_manifest_consistent=s4, S5_flag=flag))
with open(outs["rows"], "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(srows[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(srows)
res["snapshot"] = dict(manifest=str(SNAP), manifest_sha256=msha,
                       manifest_sha256_expected="A93EB44FC128DAC30E754C6EA996D67AB381B78A708A999C8BE1DE7600D4F279",
                       manifest_sha256_matches=msha == "A93EB44FC128DAC30E754C6EA996D67AB381B78A708A999C8BE1DE7600D4F279",
                       rows=len(rows), rows_all_checks_pass=ok)
outs["snap"].write_text(json.dumps(res["snapshot"], indent=1), encoding="utf-8")

# 2. preflight
PF = RR / "R4_20261028_preflight"
pm = list(csv.DictReader(open(PF / "zz_R4_file_manifest.csv", encoding="utf-8")))
pf_ok = sum(1 for r in pm if (PF / r["path"]).is_file() and sha(PF / r["path"]) == r["sha256"])
pre = {r["path"]: r for r in csv.DictReader(open(LOGS / "zz_pre_hash_project_v10.csv", encoding="utf-8"))}
pfx = "verification\\research_recovery_20261028\\R4_20261028_preflight\\"
pf_now = {str(p.relative_to(REPO)): p for p in PF.rglob("*") if p.is_file()}
pf_pre = {k for k in pre if k.startswith(pfx)}
pf_changed = [k for k in pf_pre & set(pf_now) if sha(pf_now[k]) != pre[k]["sha256"]]
res["preflight"] = dict(manifest_rows=len(pm), manifest_rows_verified=pf_ok, files_now=len(pf_now), files_at_start=len(pf_pre),
                        added=sorted(set(pf_now) - pf_pre), removed=sorted(pf_pre - set(pf_now)), changed=pf_changed)

# 3. frozen hashes
res["frozen"] = {
    "protocol_v1": sha(PF / "03_R4_protocol_v1.md"),
    "amendment_1_issued": sha(RR / "R4_20261028_campaign/release/03_R4_protocol_v1_amendment_1.md"),
    "amendment_1_approval": sha(RR / "R4_20261028_campaign/release/amendment_1_approval.json"),
    "campaign_authorization_exists": (RR / "R4_20261028_campaign/release/campaign_authorization.json").exists(),
    "issued_amendment_2_exists": (RR / "R4_20261028_campaign/release/03_R4_protocol_v1_amendment_2.md").exists(),
    "amendment_2_approval_exists": (RR / "R4_20261028_campaign/release/amendment_2_approval.json").exists(),
    "amendment_2_candidate_rev4": sha(RR / "R4_20261028_pilot/03_protocol_v1_amendment_2_rev4_CANDIDATE.md"),
    "amendment_2_draft_rev3": sha(RR / "R4_20261028_pilot/03_protocol_v1_amendment_2_DRAFT.md"),
    "amendment_2_candidate_rev5": sha(RR / "R4_20261028_pilot/03_protocol_v1_amendment_2_rev5_CANDIDATE.md"),
    "amendment_2_candidate_rev6": sha(RR / "R4_20261028_pilot/03_protocol_v1_amendment_2_rev6_CANDIDATE.md"),
    "amendment_2_candidate_rev7": sha(RR / "R4_20261028_pilot/03_protocol_v1_amendment_2_rev7_CANDIDATE.md"),
    "amendment_2_candidate_rev8": sha(RR / "R4_20261028_pilot/03_protocol_v1_amendment_2_rev8_CANDIDATE.md"),
    "amendment_2_candidate_rev9": sha(RR / "R4_20261028_pilot/03_protocol_v1_amendment_2_rev9_CANDIDATE.md"),
    "amendment_2_candidate_rev10": sha(RR / "R4_20261028_pilot/03_protocol_v1_amendment_2_rev10_CANDIDATE.md"),
    "amendment_2_candidate_rev11": sha(RR / "R4_20261028_pilot/03_protocol_v1_amendment_2_rev11_CANDIDATE.md"),
    "amendment_2_candidate_rev12": sha(RR / "R4_20261028_pilot/03_protocol_v1_amendment_2_rev12_CANDIDATE.md"),
    "amendment_2_candidate_rev13": sha(RR / "R4_20261028_pilot/03_protocol_v1_amendment_2_rev13_CANDIDATE.md"),
    "campaign_outputs_dir_exists": (RR / "R4_20261028_campaign/outputs").exists()}

# 4. project post-hash, v5 pre-hash scope
SKIP_TOP = {".git", ".venv", "cache", "tools"}
PILOT = RR / "R4_20261028_pilot"
post = {}
for dp, dns, fns in os.walk(REPO):
    d = Path(dp)
    if d == REPO:
        dns[:] = [x for x in dns if x not in SKIP_TOP]
    dns[:] = [x for x in dns if d / x != PILOT]
    for fn in fns:
        p = d / fn
        st = p.stat()
        post[str(p.relative_to(REPO))] = dict(bytes=st.st_size, mtime_ns=st.st_mtime_ns, sha256=sha(p))
with open(outs["post"], "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["path", "bytes", "mtime_ns", "sha256"])
    for k in sorted(post):
        w.writerow([k, post[k]["bytes"], post[k]["mtime_ns"], post[k]["sha256"]])
added = sorted(set(post) - set(pre))
removed = sorted(set(pre) - set(post))
changed = sorted(k for k in set(pre) & set(post) if pre[k]["sha256"] != post[k]["sha256"])
att = ("verification\\research_recovery_20261028\\R4_20261028_campaign\\release_attempts\\attempt11_final_owner_decisions\\",
       "verification\\research_recovery_20261028\\R4_20261028_campaign\\release_attempts\\attempt12_final_owner_decisions\\")
res["project"] = dict(before=len(pre), after=len(post), added=len(added), removed=len(removed), changed=len(changed),
                      added_outside_attempts_11_and_12=[a for a in added if not a.startswith(att)], removed_list=removed,
                      changed_list=changed)
lines = [f"before {len(pre)} after {len(post)} added {len(added)} removed {len(removed)} changed {len(changed)}",
         f"scope: repository minus {sorted(SKIP_TOP)} and the pilot directory (same as zz_pre_hash_project_v10.csv)"]
lines += [f"ADDED {a}" for a in added] + [f"REMOVED {a}" for a in removed] + [f"CHANGED {a}" for a in changed]
outs["cmp"].write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
outs["summ"].write_text(json.dumps(res, indent=1), encoding="utf-8")
print(json.dumps(res, indent=1))

# 5. every amendment-2 draft revision (rev0-rev4) is still present unchanged somewhere in the pilot (live or archived)
EXPECT_DRAFTS = {"rev0": "c3e1ddfce7dca7909bb1cd2a6186f4d5044b5dfe81eeed43df0b9fcf215957d4",
                 "rev1": "a936023af0a772ee2b81c720c76f9c462aba89afe1a8e1de38a286872a8744bf",
                 "rev2": "e0dc68827c57704b49b13886c455b281e4e3c10ce377a1f174742ff5529247cc",
                 "rev3": "fdaf193de510488733f0e0899d50def86cbeafabdbecdd3bc7a144099b6f492c",
                 "rev4": "c726560d1e87036cbd94fe58724cafdc1e4746647f6cfacbb320f3e14ed143ab",
                 "rev5": "e7ba73c11784b3cf38f48e32b69a7a7c21b070d039118547d638bc1bf06d4f5f",
                 "rev6": "0dcb767e97e19f40c00735d9efaecf8d21c396c23952b70e60ccb21a3f711e1f",
                 "rev7": "0e3ef3112c979237e7079f176b21dd4f2ce682c7ab435f36f33321ffe67a5996",
                 "rev8": "f6430bf5512cb56065a2465bcfda1c4c42e244b80f73fcd3e88d985ac8811f7c",
                 "rev9": "cdeea032c520f408f1f300a53cf1bc8b1ec4582d80340d3df2c2c94fa5d45719",
                 "rev10": "5479f0e81b981c7977ea5a416762972d2a332d4fdb75beee7ad8379ade399804",
                 "rev11": "162b688d2a1665831705bc3a1bc68273f5ede15cc87b0d226837cf4f015998e9",
                 "rev12": "ac376c0b362c2e99a9d3777fa849205844487e0be50a41dd1c5f1b2410b5ae1b"}
found = {}
for p in PILOT.rglob("03_protocol_v1_amendment_2*.md"):
    found.setdefault(sha(p), []).append(p.relative_to(PILOT).as_posix())
res["amendment_2_drafts"] = {k: dict(sha256=h, present_at=sorted(found.get(h, []))) for k, h in EXPECT_DRAFTS.items()}
res["amendment_2_drafts_all_present"] = all(found.get(h) for h in EXPECT_DRAFTS.values())

# 6. every release manifest (attempt 2 at the campaign root, attempts 3-9): its own SHA-256 equals the recorded value,
# and every listed file is present with the listed size and hash
C = RR / "R4_20261028_campaign"
MANIFESTS = {"attempt2_root": (C / "zz_sha256_manifest_release.csv", "eae902275b363357674be7aed8a8b37162b687cd72ced0033dbfb84dfaff32e4"),
             "attempt3": (C / "release_attempts/attempt3_amendment2/zz_sha256_manifest_attempt3.csv",
                          "e33cdcb9b9ff6c9e50d34ab00acdc53a21dac4fe87c20e79c41158f84f5da9d3"),
             "attempt4": (C / "release_attempts/attempt4_owner_rulings/zz_sha256_manifest_attempt4.csv",
                          "0727aa086b3da7639c680a0bdd4f84ce58f7fe11133e64526727841cbcb91c89"),
             "attempt5": (C / "release_attempts/attempt5_owner_rulings/zz_sha256_manifest_attempt5.csv",
                          "c32601c33365dc5c06f563d0ccec01c483208809499d87f3f2d7d944a4f3ca00"),
             "attempt6": (C / "release_attempts/attempt6_review_fixes/zz_sha256_manifest_attempt6.csv",
                          "b19ddce7373aff8e02ae854986f3107355ea244a05e0a4b62831623b96ad4c3a"),
             "attempt7": (C / "release_attempts/attempt7_final_review/zz_sha256_manifest_attempt7.csv",
                          "42e8c88f35edd49e206354173a79925050eae395a52b04a5fba7675f32a1f933"),
             "attempt8": (C / "release_attempts/attempt8_final_owner_decisions/zz_sha256_manifest_attempt8.csv",
                          "2ea8714f3f492e8ceaa5cf345182ce243ef8dab51415f55413fc45bf5300a617"),
             "attempt9": (C / "release_attempts/attempt9_review_fixes/zz_sha256_manifest_attempt9.csv",
                          "0e317eef0a0a7ab54af9c2c69aee4af619693dabcf5ca441d2a7c386f5766ffc"),
             "attempt10": (C / "release_attempts/attempt10_review_fixes/zz_sha256_manifest_attempt10.csv",
                           "9af4b502cbc01fb1ee657ac0f509f71a59b87f8467d7e7e5a8dfc0b9aa6c84a8"),
             "attempt11": (C / "release_attempts/attempt11_final_owner_decisions/zz_sha256_manifest_attempt11.csv",
                           "b62952650d79381ebb3c309dfe17049e03f08cbf7b3e8b929b6f83d3e5ef5768"),
             "attempt12": (C / "release_attempts/attempt12_final_owner_decisions/zz_sha256_manifest_attempt12.csv",
                           (LOGS / "zz_campaign_attempt12_manifest_sha256.txt").read_text(encoding="utf-8").split()[2])}
res["release_manifests"] = {}
for k, (m, want) in MANIFESTS.items():
    mrows = list(csv.DictReader(open(m, encoding="utf-8")))
    bad = [r["path"] for r in mrows if not (m.parent / r["path"]).is_file()
           or (m.parent / r["path"]).stat().st_size != int(r["bytes"]) or sha(m.parent / r["path"]) != r["sha256"]]
    res["release_manifests"][k] = dict(manifest_sha256=sha(m), recorded=want, manifest_matches=sha(m) == want,
                                       rows=len(mrows), rows_mismatched=bad)
res["release_manifests_all_ok"] = all(v["manifest_matches"] and not v["rows_mismatched"]
                                      for v in res["release_manifests"].values())
outs["summ"].write_text(json.dumps(res, indent=1), encoding="utf-8")
print(json.dumps({k: res[k] for k in ("amendment_2_drafts_all_present", "release_manifests_all_ok")}, indent=1))
print(json.dumps({k: (v["manifest_matches"], v["rows"], v["rows_mismatched"]) for k, v in res["release_manifests"].items()}))
