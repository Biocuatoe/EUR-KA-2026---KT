"""H3 campaign command line (protocol v1 10; readiness task: only --build-config and --dry-run were used).

    python -I -B code/run_campaign.py --build-config   config/campaign_config_v1_DRAFT.json + draw table (no overwrite)
    python -I -B code/run_campaign.py --dry-run        schedule and input validation; executes no run
    python -I -B code/run_campaign.py --execute        campaign mode: refuses while any precondition is unmet
"""

import json
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout.reconfigure(encoding="utf-8")

from r4h3 import campaign, frozen  # noqa: E402

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "--dry-run"
    if arg == "--build-config":
        print(json.dumps(campaign.build_config(), indent=1))
    elif arg == "--dry-run":
        out = frozen.PILOT / "outputs" / f"dry_run_{time.strftime('%Y%m%d_%H%M%S')}"
        res = campaign.dry_run(out)
        print(json.dumps({"outdir": str(out), "schedule_passed": res["schedule"]["passed"],
                          "counts": res["schedule"]["counts_per_set"], "blockers": res["blockers"],
                          "campaign_may_start": res["campaign_may_start"]}, indent=1))
    elif arg == "--execute":
        try:
            campaign.run_campaign()
        except campaign.CampaignBlocked as e:
            print("REFUSED: campaign preconditions not met:")
            for b in e.args[0]:
                print("  -", b)
            sys.exit(2)
    else:
        sys.exit(__doc__)
