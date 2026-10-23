"""Reference speed profiles built from segment definitions (configs/cycles/profiles.yaml)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import yaml

from eureka import REPO_DIR

PROFILES_PATH = REPO_DIR / "configs" / "cycles" / "profiles.yaml"


@dataclass(frozen=True)
class Profile:
    name: str
    knots_t: np.ndarray  # s
    knots_v: np.ndarray  # m/s

    @property
    def duration(self) -> float:
        return float(self.knots_t[-1])

    def sample(self, t: np.ndarray) -> np.ndarray:
        return np.interp(t, self.knots_t, self.knots_v)

    def stats(self) -> dict:
        """Exact statistics of the piecewise-linear profile."""
        dt = np.diff(self.knots_t)
        dv = np.diff(self.knots_v)
        dist = float(np.sum(dt * (self.knots_v[1:] + self.knots_v[:-1]) / 2))
        idle = float(np.sum(dt[(self.knots_v[1:] == 0) & (self.knots_v[:-1] == 0)]))
        acc = np.divide(dv, dt, out=np.zeros_like(dv), where=dt > 0)
        stops = int(np.sum((self.knots_v[1:] == 0) & (self.knots_v[:-1] > 0)))
        return {
            "duration_s": self.duration,
            "distance_m": dist,
            "idle_s": idle,
            "max_speed_kmh": float(self.knots_v.max() * 3.6),
            "mean_speed_kmh": dist / self.duration * 3.6,
            "max_accel": float(acc.max()),
            "max_decel": float(acc.min()),
            "stops": stops,
        }


def build(name: str, segments: list[dict]) -> Profile:
    t, v = [0.0], [0.0]
    for seg in segments:
        if "idle" in seg or "cruise" in seg:
            dur = float(seg.get("idle", seg.get("cruise")))
            if "idle" in seg and v[-1] != 0.0:
                raise ValueError(f"{name}: idle segment while moving")
            t.append(t[-1] + dur)
            v.append(v[-1])
        else:
            a, target = float(seg["accel"]), seg["to_kmh"] / 3.6
            if a == 0 or np.sign(target - v[-1]) != np.sign(a):
                raise ValueError(f"{name}: acceleration sign does not reach target in {seg}")
            t.append(t[-1] + (target - v[-1]) / a)
            v.append(target)
    return Profile(name, np.asarray(t), np.asarray(v))


def load_profiles() -> dict[str, Profile]:
    raw = yaml.safe_load(PROFILES_PATH.read_text(encoding="utf-8"))
    return {name: build(name, spec["segments"]) for name, spec in raw.items()}
