"""Build run specifications from configs/experiments.yaml, execute batches, save raw outputs."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
import yaml

from eureka import REPO_DIR, ROOT_DIR
from eureka.controllers import gain
from eureka.cycles import load_profiles
from eureka.lineage import config_hash, run_context
from eureka.params import Params, load_params, uncertainty_ranges
from eureka.simulate import simulate

EXPERIMENTS_PATH = REPO_DIR / "configs" / "experiments.yaml"
RAW_DIR = ROOT_DIR / "artifacts" / "raw"
SAVED = (
    "v",
    "T",
    "t_ref",
    "t_lim",
    "sat",
    "z",
    "i",
    "SoC",
    "E_chem",
    "dist",
    "nonfinite",
    "infeasible",
)


@dataclass
class RunSpec:
    experiment: str
    profile: str
    controller: str  # fixed | scheduled
    soh: float
    gamma_v: float | None = None
    gamma_u: float | None = None
    r_scale: float = 1.0
    draw: int | None = None
    seed: int | None = None
    overrides: dict = field(default_factory=dict)

    @property
    def run_id(self) -> str:
        parts = [self.experiment, self.profile, self.controller, f"soh{self.soh:.2f}"]
        if self.gamma_u is not None:
            parts.append(f"gu{self.gamma_u:g}-gv{self.gamma_v:g}")
        if self.r_scale != 1.0:
            parts.append(f"r{self.r_scale:.4g}")
        if self.draw is not None:
            parts.append(f"d{self.draw:04d}")
        return "-".join(parts)


def load_experiments() -> dict:
    return yaml.safe_load(EXPERIMENTS_PATH.read_text(encoding="utf-8"))


def _values(spec):
    if isinstance(spec, dict) and "logspace" in spec:
        a, b, n = spec["logspace"]
        return [float(x) for x in np.logspace(a, b, int(n))]
    return list(spec)


def specs_for(name: str, cfg: dict, draws: range | None = None) -> list[RunSpec]:
    c = cfg[name]
    out: list[RunSpec] = []
    if name == "primary":
        for prof in c["profiles"]:
            for s in c["soh"]:
                for ctl in c["controllers"]:
                    out.append(RunSpec(name, prof, ctl, s))
    elif name == "gamma_sweep":
        for prof in c["profiles"]:
            for s in c["soh"]:
                if c.get("include_fixed"):
                    out.append(RunSpec(name, prof, "fixed", s))
                for gu in c["gamma_u"]:
                    for gv in c["gamma_v"]:
                        out.append(RunSpec(name, prof, "scheduled", s, gamma_v=gv, gamma_u=gu))
    elif name == "fixed_family":
        for prof in c["profiles"]:
            for s in c["soh"]:
                for rs in _values(c["r_scale"]):
                    out.append(RunSpec(name, prof, "fixed", s, r_scale=rs))
    elif name == "robustness":
        ranges = uncertainty_ranges()
        missing = set(c["perturbed"]) - set(ranges)
        if missing:
            raise ValueError(f"no uncertainty range for {missing}")
        for d in draws or range(c["pilot_draws"]):
            seed = int(c["base_seed"]) + d
            rng = np.random.default_rng(seed)
            ov = {k: float(rng.uniform(*ranges[k])) for k in c["perturbed"]}
            for ctl in ("fixed", "scheduled"):
                out.append(
                    RunSpec(
                        name, c["profile"], ctl, c["soh"], draw=d, seed=seed, overrides=dict(ov)
                    )
                )
    else:
        raise ValueError(name)
    return out


def _noise(spec: RunSpec, p: Params, steps: int) -> np.ndarray:
    rng = np.random.default_rng(spec.seed)
    _ = [rng.uniform() for _ in spec.overrides]  # same stream position as specs_for
    return rng.normal(0.0, p.noise_std, steps + 1)


def run_batch(
    name: str,
    batch: str,
    specs: list[RunSpec],
    dtype: str,
    noise: bool = False,
    allow_dirty: bool = False,
) -> Path:
    ctx = run_context()
    if not allow_dirty:
        gate = json.loads(
            (ROOT_DIR / "artifacts" / "reports" / "verification-gate.json").read_text(
                encoding="utf-8"
            )
        )
        if not gate["passed"] or gate["context"]["git"]["commit"] != ctx["git"]["commit"]:
            raise RuntimeError("verification gate has not passed for the current commit")
        if ctx["git"]["dirty"]:
            raise RuntimeError("working tree is dirty; commit before an evaluation run")

    nominal = load_params()
    profiles = load_profiles()
    prof = profiles[specs[0].profile]
    if any(s.profile != prof.name for s in specs):
        raise ValueError("one profile per batch")
    plants = [nominal.with_overrides(**s.overrides) for s in specs]
    # Controllers are always designed on NOMINAL parameters (prereg deviation log item 2).
    gains = np.vstack(
        [gain(nominal, s.controller, s.soh, s.r_scale, s.gamma_v, s.gamma_u) for s in specs]
    )
    steps = round(prof.duration / nominal.Ts)
    nz = np.vstack([_noise(s, nominal, steps) for s in specs]) if noise else None

    t0 = time.time()
    out = simulate(prof, plants, gains, np.array([s.soh for s in specs]), noise=nz)
    runtime = time.time() - t0

    dest = RAW_DIR / name / batch
    dest.mkdir(parents=True, exist_ok=True)
    arrays = {k: out[k].astype(dtype) for k in SAVED}
    arrays.update(
        t=out["t"][:, 0],
        v_ref=out["v_ref"][:, 0],
        y0=out["y0"],
        y_end=out["y_end"],
        soh=out["soh"],
        gains=out["gains"],
    )
    if nz is not None:
        arrays["noise"] = nz.astype(dtype)
    np.savez_compressed(dest / "timeseries.npz", **arrays)

    exp_cfg = load_experiments().get(name, {})
    manifest = {
        "experiment": name,
        "batch": batch,
        "context": ctx,
        "runtime_s": round(runtime, 1),
        "experiment_config": exp_cfg,
        "experiment_config_hash": config_hash(exp_cfg),
        "nominal_parameters": nominal.as_dict(),
        "parameters_hash": config_hash(nominal.as_dict()),
        "profile": {
            "name": prof.name,
            "stats": prof.stats(),
            "knots_t": prof.knots_t.tolist(),
            "knots_v": prof.knots_v.tolist(),
        },
        "dtype": dtype,
        "noise": bool(noise),
        "runs": [
            {**asdict(s), "run_id": s.run_id, "column": j, "gain": gains[j].tolist()}
            for j, s in enumerate(specs)
        ],
        "attempted": len(specs),
    }
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return dest
