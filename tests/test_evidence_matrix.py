"""The evidence matrix must cover every registered claim with a defined status."""

from eureka.evidence import STATUS_DEFINITIONS, Status, load_matrix, load_registry

ROWS = load_matrix()


def test_every_registered_claim_has_exactly_one_row():
    ids = [r.claim_id for r in ROWS]
    claims = [c.id for c in load_registry().claims]
    assert sorted(i for i in ids if i.startswith("C")) == sorted(claims)
    assert len(ids) == len(set(ids))


def test_every_status_has_a_definition():
    assert set(STATUS_DEFINITIONS) == set(Status)


def test_supported_rows_cite_artifacts_and_limitations():
    for r in ROWS:
        if r.verification_status == Status.SIMULATION_SUPPORTED:
            assert r.supporting_artifacts, r.claim_id
            assert r.contradictory_or_negative_evidence.strip(), r.claim_id
