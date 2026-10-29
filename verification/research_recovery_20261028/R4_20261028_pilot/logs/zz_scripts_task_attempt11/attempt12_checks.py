"""From a release-attempt copy: dry run (schedule validation, no run executed) and both precondition checks.
Never calls run_campaign() or execute_schedule(); writes only inside the attempt directory.
Usage (cwd = attempt dir): python -I -B attempt12_checks.py <attempt_dir>"""
import json
import sys
import time
from pathlib import Path

att = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(att / "code"))
from r4h3 import campaign, frozen  # noqa: E402

assert frozen.PILOT.resolve() == att, (frozen.PILOT, att)
out = att / f"dry_run_{time.strftime('%Y%m%d_%H%M%S')}"
res = campaign.dry_run(out)
pre = dict(written=time.strftime("%Y-%m-%dT%H:%M:%S%z"), running_from=str(frozen.PILOT),
           campaign_dir=str(campaign.CAMPAIGN_DIR), readiness_gate=str(campaign.READINESS_GATE),
           readiness_blockers=campaign.preconditions("readiness"), campaign_blockers=campaign.preconditions("campaign"),
           campaign_authorization_exists=campaign.CAMPAIGN_AUTHORIZATION.exists(),
           issued_amendment_2_exists=campaign.ISSUED_AMENDMENT_2.exists(),
           note="preconditions() only; run_campaign() was not called (campaign mode not invoked)")
target = att / "logs" / "preconditions_attempt12.json"
if target.exists():
    sys.exit(f"refused: {target} exists")
target.write_text(json.dumps(pre, indent=1), encoding="utf-8")
print(json.dumps(dict(dry_run_dir=str(out), schedule_passed=res["schedule"]["passed"],
                      counts=res["schedule"]["counts_per_set"], config=res["campaign_config"],
                      sensitivity=res["sensitivity"], draft_amendment_2_status=res["draft_amendment_2"].get("status"),
                      draft_amendment_2_errors=res["draft_amendment_2"].get("errors"),
                      draft_amendment_2_sha256=res["draft_amendment_2"].get("sha256"),
                      campaign_may_start=res["campaign_may_start"], **{k: pre[k] for k in
                      ("readiness_blockers", "campaign_blockers", "campaign_authorization_exists",
                       "issued_amendment_2_exists")}), indent=1, default=str))
