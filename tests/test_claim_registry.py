"""The claim registry must quote the report exactly and reference only existing checks."""

import hashlib

import pytest

from eureka import REPORT_MD, ROOT_DIR
from eureka.audit.report_checks import ALL_CHECKS, run_all
from eureka.evidence import load_registry

REG = load_registry()
LINES = REPORT_MD.read_text(encoding="utf-8").splitlines()


def test_registry_points_at_preserved_original():
    raw = ROOT_DIR / REG.report_file
    assert hashlib.sha256(raw.read_bytes()).hexdigest().upper() == REG.report_sha256


@pytest.mark.parametrize(
    ("cid", "loc"),
    [(c.id, loc) for c in REG.claims for loc in c.locations],
    ids=lambda v: v if isinstance(v, str) else f"L{v.line}",
)
def test_quote_is_verbatim_at_stated_line(cid, loc):
    assert loc.quote in LINES[loc.line - 1], f"{cid}: quote not found on line {loc.line}"


def test_named_claims_required_by_protocol_are_registered():
    text = {c.id: (c.title + c.statement).lower() for c in REG.claims}
    joined = " ".join(text.values())
    for needle in ("12.5%", "15.3%", "vuc", "monte carlo", "asil", "hardware", "validated"):
        assert needle in joined, needle


def test_consistency_check_ids_exist():
    known = {r.id for r in run_all()}
    referenced = {k for c in REG.claims for k in c.consistency_checks}
    assert referenced <= known, referenced - known
    assert len(known) == len(ALL_CHECKS)
