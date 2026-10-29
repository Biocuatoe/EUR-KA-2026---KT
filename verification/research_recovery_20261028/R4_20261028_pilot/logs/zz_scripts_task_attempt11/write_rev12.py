"""Write 03_protocol_v1_amendment_2_rev12_CANDIDATE.md from the scratch text, with the machine-readable block generated
from campaign.IMPLEMENTED_2 (JSON round-trip, the same comparison read_amendment uses), and its .sha256.txt.
Refuses if either target exists. Usage: write_rev12.py <pilot_dir> <text_template>"""
import hashlib, json, sys, time
from pathlib import Path

pilot, tmpl = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(pilot / "code"))
from r4h3 import campaign  # noqa: E402

out = pilot / "03_protocol_v1_amendment_2_rev12_CANDIDATE.md"
rec = pilot / "03_protocol_v1_amendment_2_rev12_CANDIDATE.sha256.txt"
for p in (out, rec):
    if p.exists():
        sys.exit(f"refused: {p} exists")
assert campaign.DRAFT_AMENDMENT_2 == out
assert campaign.IMPLEMENTED_2["owner_decisions_open"] == []
blk = {"amendment": "R4 protocol v1 amendment 2 (N-A2, AMB-29(a)-(d), AMB-30, AMB-31, AMB-32, I-1 to I-6), candidate rev12",
       "status": "DRAFT", **json.loads(json.dumps(campaign.IMPLEMENTED_2)),
       "note": "CANDIDATE rev12 - DRAFT - NOT APPROVED FOR RELEASE. Values must equal the implementation."}
text = tmpl.read_text(encoding="utf-8")
assert text.count("{{BLOCK}}") == 1
text = text.replace("{{BLOCK}}", campaign.BLOCK_MARK + "\n```json\n" + json.dumps(blk, indent=1, ensure_ascii=False) + "\n```")
line3 = text.splitlines()[2]
assert "DRAFT — NOT APPROVED FOR RELEASE" in line3 and "NOT ISSUABLE" not in line3 and "rev12" in line3
out.write_text(text, encoding="utf-8", newline="\n")
r = campaign.read_amendment(out, campaign.IMPLEMENTED_2, {})
assert r["exists"] and not r["errors"] and r["status"] == "DRAFT", r["errors"]
h = hashlib.sha256(out.read_bytes()).hexdigest()
rec.write_text(
    f"SHA-256 of 03_protocol_v1_amendment_2_rev12_CANDIDATE.md (candidate rev12): {h}\n"
    f"Recorded {time.strftime('%Y-%m-%d %H:%M:%S %z')} as an integrity identifier of the candidate text only.\n"
    "Status: CANDIDATE - DRAFT - NOT APPROVED FOR RELEASE. Not issued, not frozen, not approved. Owner rulings I-1 to I-6 "
    "implemented; no owner decision on its content is open (section 9); one implementer reading is listed for the "
    "owner's confirmation (section 1.14). Implements the owner's decisions of 2026-10-29 (sections 1.15, 1.16); fixes "
    "review R10 (attempt 10).\n"
    "Parents: protocol v1 f9826318836f7a866bb66bbaa67305851798cac998582de2a4be182afa772dab; amendment 1 "
    "7720fed75bb678e47a229d00aff154e0aa14607c051f4a1163cc9bf67b6abee2; supersedes candidate rev11 "
    "162b688d2a1665831705bc3a1bc68273f5ede15cc87b0d226837cf4f015998e9 (unchanged; superseded before any test or "
    "review) and the reviewed candidate rev10 5479f0e81b981c7977ea5a416762972d2a332d4fdb75beee7ad8379ade399804 (unchanged).\n", encoding="utf-8", newline="\n")
print(h, len(blk), "block keys", r["errors"])
