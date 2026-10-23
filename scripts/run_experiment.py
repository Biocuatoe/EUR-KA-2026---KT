"""Execute a pre-registered experiment and save raw outputs to artifacts/raw/<experiment>/.

    python scripts/run_experiment.py primary
    python scripts/run_experiment.py gamma_sweep
    python scripts/run_experiment.py fixed_family
    python scripts/run_experiment.py robustness --stage pilot
    python scripts/run_experiment.py robustness --stage main   # N from the pilot analysis

Refuses to run unless scripts/run_gate.py passed at the current commit on a clean tree.
"""

import argparse
import json
from itertools import groupby

from eureka import ROOT_DIR
from eureka.experiment import load_experiments, run_batch, specs_for


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("experiment", choices=["primary", "gamma_sweep", "fixed_family", "robustness"])
    ap.add_argument("--stage", choices=["pilot", "main"], default="pilot")
    ap.add_argument("--batch-draws", type=int, default=150)
    args = ap.parse_args()
    cfg = load_experiments()
    c = cfg[args.experiment]

    if args.experiment != "robustness":
        specs = specs_for(args.experiment, cfg)
        for prof, group in groupby(specs, key=lambda s: s.profile):
            dest = run_batch(args.experiment, prof, list(group), c["dtype"])
            print(f"saved {dest}")
        return

    if args.stage == "pilot":
        draws = [range(c["pilot_draws"])]
    else:
        n = json.loads(
            (ROOT_DIR / "artifacts" / "reports" / "robustness-sample-size.json").read_text(
                encoding="utf-8"
            )
        )["N"]
        rest = range(c["pilot_draws"], n)
        draws = [rest[i : i + args.batch_draws] for i in range(0, len(rest), args.batch_draws)]
    for dr in draws:
        if len(dr) == 0:
            continue
        specs = specs_for("robustness", cfg, draws=dr)
        batch = f"draws-{dr.start:04d}-{dr.stop - 1:04d}"
        dest = run_batch("robustness", batch, specs, c["dtype"], noise=c["velocity_noise"])
        print(f"saved {dest}")


if __name__ == "__main__":
    main()
