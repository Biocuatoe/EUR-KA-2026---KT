"""Reproducible consistency checks of numbers stated in the report.

Each check recomputes a quantity from inputs the report itself states and compares it
with the value the report prints. Inputs are copied verbatim from the report; the
registry (evidence/claim_registry.yaml) gives their exact locations.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

import pint

from eureka.audit.dimensional import audit_report_a_matrix

ureg = pint.UnitRegistry()


@dataclass
class CheckResult:
    id: str
    claim_ids: list[str]
    description: str
    inputs: dict
    computed: dict
    reported: dict
    consistent: bool
    note: str = ""
    tolerance: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return asdict(self)


def chk_energy_pct() -> CheckResult:
    base, new = 95.0, 85.3  # Wh/km, lines 5468-5470
    rel = (base - new) / base * 100
    return CheckResult(
        "CHK-ENERGY-PCT",
        ["C01", "C03"],
        "Relative energy saving implied by 95 -> 85.3 Wh/km",
        {"baseline_Wh_per_km": base, "adaptive_Wh_per_km": new},
        {"absolute_Wh_per_km": round(base - new, 3), "relative_pct": round(rel, 2)},
        {"line_5472_pct": 9.7, "abstract_pct": 12.5},
        consistent=abs(rel - 9.7) < 0.05 and abs(rel - 12.5) < 0.05,
        note="9.7 is the absolute difference in Wh/km, not a percentage; neither matches 12.5%.",
        tolerance={"pct_points": 0.05},
    )


def chk_vuc_speed() -> CheckResult:
    dist = 5.8 * ureg.km
    dur = 600 * ureg.s
    avg = (dist / dur).to("km/h").magnitude
    return CheckResult(
        "CHK-VUC-SPEED",
        ["C07", "C08"],
        "VUC average speed from distance and duration",
        {"distance_km": 5.8, "duration_s": 600},
        {"avg_speed_kmh": round(avg, 2)},
        {"avg_speed_kmh": 28.5},
        consistent=abs(avg - 28.5) <= 0.5,
        tolerance={"kmh": 0.5},
    )


def chk_vuc_idle() -> CheckResult:
    stops, stop_s, dur = 17, 22.0, 600.0
    idle_pct = stops * stop_s / dur * 100
    return CheckResult(
        "CHK-VUC-IDLE",
        ["C07", "C08"],
        "VUC idle fraction from stop count and mean stop duration",
        {"stops": stops, "mean_stop_s": stop_s, "duration_s": dur},
        {"idle_s": stops * stop_s, "idle_pct": round(idle_pct, 1)},
        {"idle_pct": 20.1},
        consistent=abs(idle_pct - 20.1) <= 1.0,
        note="Idle time cannot be less than total stop time.",
        tolerance={"pct_points": 1.0},
    )


def chk_cycle_speeds() -> CheckResult:
    table = {"NEDC": (11.0, 1180, 33.6), "WLTP": (23.6, 1800, 46.5), "CLTC": (14.5, 1800, 29.0)}
    computed = {k: round(d / (t / 3600), 2) for k, (d, t, _) in table.items()}
    ok = {k: abs(computed[k] - table[k][2]) <= 0.3 for k in table}
    return CheckResult(
        "CHK-CYCLE-SPEEDS",
        ["C09"],
        "Average speed = distance / duration for Table 12 cycles",
        {k: {"distance_km": d, "duration_s": t} for k, (d, t, _) in table.items()},
        {"avg_speed_kmh": computed, "consistent_per_cycle": ok},
        {"avg_speed_kmh": {k: v[2] for k, v in table.items()}},
        consistent=all(ok.values()),
        tolerance={"kmh": 0.3},
    )


def chk_bonferroni() -> CheckResult:
    # Table 38 (Appendix E); "<0.001" entered as 0.001 (most favourable reading)
    p = {
        "energy": [0.001, 0.001, 0.002, 0.015, 0.048, 0.001],
        "tracking": [0.001, 0.001, 0.003, 0.012, 0.035, 0.001],
        "aging": [0.001, 0.002, 0.008, 0.025, 0.042, 0.003],
    }
    allp = [x for v in p.values() for x in v]
    m_all, m_metric = len(allp), 6
    thr_all, thr_metric = 0.05 / m_all, 0.05 / m_metric
    fail_all = sum(x > thr_all for x in allp)
    fail_metric = sum(x > thr_metric for x in allp)
    return CheckResult(
        "CHK-BONFERRONI",
        ["C13"],
        "Reported p-values against Bonferroni-corrected thresholds",
        {"p_values": p},
        {
            "tests": m_all,
            "threshold_all_18": round(thr_all, 5),
            "n_not_significant_all_18": fail_all,
            "threshold_per_metric_6": round(thr_metric, 5),
            "n_not_significant_per_metric": fail_metric,
        },
        {"claim": "all comparisons significant after Bonferroni"},
        consistent=fail_all == 0,
    )


def chk_mc_count() -> CheckResult:
    controllers_stated, cycles_stated, trials = 6, 4, 100
    controllers_actual = 7  # 6 benchmarks + adaptive LQR (Sec. 4.3, Appendix E mu_1..mu_7)
    cycles_table13 = 7  # NEDC, WLTP, CLTC, VUC, Random 1-3
    return CheckResult(
        "CHK-MC-COUNT",
        ["C10"],
        "Monte Carlo run counts stated in the report",
        {"stated": "6 controllers x 4 cycles x 100", "other_statement": "N = 1000 samples"},
        {
            "product_stated": controllers_stated * cycles_stated * trials,
            "product_with_7_controllers_7_cycles": controllers_actual * cycles_table13 * trials,
        },
        {"total_runs": 2400, "samples": 1000},
        consistent=False,
        note="100 trials per configuration and N = 1000 samples cannot describe the same study; "
        "the 2400 product omits the adaptive controller and the extra cycles.",
    )


def chk_mc_tables() -> CheckResult:
    t16 = {"mean": 0.42, "sd": 0.08, "p5": 0.32, "p95": 0.56}
    t18 = {"mean": 0.42, "median": 0.41, "sd": 0.08, "p5": 0.28, "p95": 0.62, "p99": 0.78}
    all_below = 0.6
    issues = []
    if t18["p95"] >= all_below or t18["p99"] >= all_below:
        issues.append("Table 18 percentiles >= 0.6 m/s contradict 'all samples below 0.6 m/s'")
    if t16["p95"] != t18["p95"] or t16["p5"] != t18["p5"]:
        issues.append("Tables 16 and 18 give different percentiles for the same N = 1000 study")
    issues.append("0.4% failures (RMSE >= 0.8 m/s) contradict 'all samples below 0.6 m/s'")
    return CheckResult(
        "CHK-MC-TABLES",
        ["C11"],
        "Monte Carlo summary statistics vs 'all samples' statement",
        {"table16": t16, "table18": t18, "failure_rate_pct": 0.4},
        {"issues": issues},
        {"statement": "all samples RMSE < 0.6 m/s"},
        consistent=not issues,
    )


def chk_rmse_pct() -> CheckResult:
    a, f = 0.42, 0.68
    rel = (f - a) / f * 100
    return CheckResult(
        "CHK-RMSE-PCT",
        ["C12"],
        "Relative RMSE reduction adaptive vs fixed",
        {"adaptive_rmse": a, "fixed_rmse": f},
        {"reduction_pct": round(rel, 1)},
        {"reduction_pct": 50},
        consistent=abs(rel - 50) <= 1,
        tolerance={"pct_points": 1},
    )


def chk_morris_dup() -> CheckResult:
    t17 = {
        "R0": (0.182, 0.024),
        "Crr": (0.145, 0.018),
        "Q": (0.132, 0.021),
        "M": (0.108, 0.015),
        "Cd": (0.095, 0.012),
        "eta_motor": (0.068, 0.009),
        "g": (0.042, 0.006),
        "rho": (0.038, 0.005),
        "eta_gear_or_dt": (0.028, 0.004),
        "r_w": (0.015, 0.003),
    }
    t19 = dict(t17)  # Table 19 rows 1-10 carry the same mu and sigma (lines 5211-5220)
    identical = sum(t17[k] == t19[k] for k in t17)
    return CheckResult(
        "CHK-MORRIS-DUP",
        ["C15"],
        "Identical Morris statistics in a 10- and a 12-parameter design",
        {"table17_vs_table19_shared_params": len(t17)},
        {"identical_mu_sigma_pairs": identical},
        {"designs": "k = 10 (Table 17) and k = 12, r = 20 (Table 19)"},
        consistent=identical < len(t17),
        note="Different designs with random trajectories cannot give identical mu and sigma.",
    )


def chk_worstcase() -> CheckResult:
    sec53 = {"WC-1": 1.34, "WC-5": 1.42}
    sec48 = {"WC-1": 1.42, "WC-5": 1.52}
    return CheckResult(
        "CHK-WORSTCASE",
        ["C16"],
        "Two worst-case result sets",
        {"section_5_3": sec53, "section_4_8": sec48},
        {"WC-5_passes_in_5_3": sec53["WC-5"] < 1.5, "WC-5_passes_in_4_8": sec48["WC-5"] < 1.5},
        {"claim": "All worst-case scenarios pass the 1.5 m/s specification"},
        consistent=False,
    )


def chk_sampling() -> CheckResult:
    return CheckResult(
        "CHK-SAMPLING",
        ["C19"],
        "Control loop period and compute time",
        {
            "sec_3_1_period_ms": 10,
            "sec_5_4_period_ms": 1,
            "sec_3_6_compute_ms": 1.2,
            "sec_5_4_compute_ms": 0.40,
        },
        {"periods_equal": False, "compute_equal": False},
        {},
        consistent=False,
    )


def chk_bryson() -> CheckResult:
    r_reported, u_max = 1.0, 85.0  # R = 1; T_max = 85 Nm
    implied_umax = (1 / r_reported) ** 0.5
    return CheckResult(
        "CHK-BRYSON",
        ["C27"],
        "Bryson's rule R = 1/u_max^2 vs the stated R",
        {"R_reported": r_reported, "torque_limit_Nm": u_max},
        {"R_bryson": round(1 / u_max**2, 7), "u_max_implied_by_R_Nm": implied_umax},
        {"method": "Bryson rule"},
        consistent=abs(implied_umax - u_max) < 1e-9,
    )


def chk_fade_pct() -> CheckResult:
    return CheckResult(
        "CHK-FADE-PCT",
        ["C02", "C04"],
        "Fade reduction stated in abstract vs Chapter 6",
        {"abstract_pct": 15.3, "chapter6_pct": 14.0, "chapter6_absolute_pct_per_1000": 2.3},
        {"implied_baseline_fade_pct_per_1000": round(2.3 / 0.14, 1)},
        {"abstract": 15.3, "chapter6": 14.0},
        consistent=False,
    )


def chk_asil_level() -> CheckResult:
    return CheckResult(
        "CHK-ASIL-LEVEL",
        ["C17", "C18"],
        "ASIL target stated in different sections",
        {
            "line_5426": "ASIL B",
            "line_5850": "ASIL-C",
            "line_5860": "ASIL B",
            "line_5912": "ASIL-C or ASIL-D",
        },
        {"distinct_targets": 3},
        {},
        consistent=False,
    )


def chk_fig_cycles() -> CheckResult:
    return CheckResult(
        "CHK-FIG-CYCLES",
        ["C02", "C36"],
        "Cycle horizon of the fade figure vs the fade claim",
        {"figure_11_cycles": 1500, "claim_cycles": 1000},
        {},
        {},
        consistent=False,
        note="A difference in horizon alone is not an error, but the figure is the only fade "
        "evidence offered and it is generated from hard-coded curves.",
    )


def chk_param_mc() -> CheckResult:
    table8 = {"M_kg": 850.0, "r_w_m": 0.28, "eta_dt": 0.88}
    mc = {
        "M_mean": "M_curb + 75 kg (M_curb = 700 kg implied -> 775 kg)",
        "r_w_mean_m": 0.265,
        "eta_dt_range": [0.92, 0.98],
    }
    return CheckResult(
        "CHK-PARAM-MC",
        ["C35"],
        "Monte Carlo nominal values vs parameter table",
        {"table8": table8, "monte_carlo": mc},
        {"r_w_differs": True, "eta_dt_outside_range": not (0.92 <= 0.88 <= 0.98)},
        {},
        consistent=False,
    )


def chk_amatrix_dim() -> CheckResult:
    res = audit_report_a_matrix()
    bad = [r for r in res if not r["consistent"]]
    return CheckResult(
        "CHK-AMATRIX-DIM",
        ["C24", "C25"],
        "Dimensional audit of report Eq. 4.3-4.4 with Pint",
        {"entries_checked": len(res)},
        {"inconsistent_entries": bad, "all_entries": res},
        {"claim": "linearised vehicle model"},
        consistent=not bad,
    )


ALL_CHECKS = [
    chk_energy_pct,
    chk_vuc_speed,
    chk_vuc_idle,
    chk_cycle_speeds,
    chk_bonferroni,
    chk_mc_count,
    chk_mc_tables,
    chk_rmse_pct,
    chk_morris_dup,
    chk_worstcase,
    chk_sampling,
    chk_bryson,
    chk_fade_pct,
    chk_asil_level,
    chk_fig_cycles,
    chk_param_mc,
    chk_amatrix_dim,
]


def run_all() -> list[CheckResult]:
    return [f() for f in ALL_CHECKS]
