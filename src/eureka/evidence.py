"""Schemas for the claim registry and the scientific evidence matrix.

The registry records what the report claims (never edited to fit results); the
evidence matrix records what this repository has actually tested.
"""

from __future__ import annotations

import csv
import json
from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from eureka import REPO_DIR

REGISTRY_PATH = REPO_DIR / "evidence" / "claim_registry.yaml"
MATRIX_PATH = REPO_DIR / "evidence" / "evidence_matrix.yaml"


class EvidenceCategory(StrEnum):
    claimed_simulation_result = "claimed_simulation_result"
    claimed_measurement = "claimed_measurement"
    claimed_experimental_validation = "claimed_experimental_validation"
    claimed_statistical_result = "claimed_statistical_result"
    claimed_standard_compliance = "claimed_standard_compliance"
    claimed_hardware_result = "claimed_hardware_result"
    model_statement = "model_statement"
    methodological_statement = "methodological_statement"
    software_provenance = "software_provenance"
    parameter_provenance = "parameter_provenance"
    out_of_scope_analysis = "out_of_scope_analysis"


class Reproducibility(StrEnum):
    not_reproducible_no_data_or_code = "not_reproducible_no_data_or_code"
    underspecified = "underspecified"
    internally_inconsistent = "internally_inconsistent"
    arithmetic_check_fails = "arithmetic_check_fails"
    arithmetic_check_passes = "arithmetic_check_passes"
    dimensionally_inconsistent = "dimensionally_inconsistent"
    not_applicable = "not_applicable"


class Disposition(StrEnum):
    WITHDRAW = "WITHDRAW"
    WITHDRAW_PENDING_RETEST = "WITHDRAW_PENDING_RETEST"
    REVISE = "REVISE"
    RELABEL_AS_ASSUMED = "RELABEL_AS_ASSUMED"
    RELABEL_AS_FUTURE_WORK = "RELABEL_AS_FUTURE_WORK"
    KEEP_WITH_CITATION_CHECK = "KEEP_WITH_CITATION_CHECK"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"


class Location(BaseModel):
    model_config = ConfigDict(extra="forbid")
    line: int = Field(gt=0, description="1-based line in data/processed/report/report.md")
    section: str
    quote: str = Field(min_length=8, description="verbatim substring of that line")


class Claim(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(pattern=r"^C\d{2}$")
    title: str
    category: str
    statement: str
    locations: list[Location] = Field(min_length=1)
    units: str
    definition: str
    evidence_category: EvidenceCategory
    source_data: str
    calculation: str
    reproducibility: Reproducibility
    consistency_checks: list[str] = Field(default_factory=list)
    provenance_notes: str = ""
    disposition: Disposition
    disposition_note: str


class Registry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    report_file: str
    report_sha256: str
    derived_markdown: str
    claims: list[Claim]

    @model_validator(mode="after")
    def unique_ids(self) -> Registry:
        ids = [c.id for c in self.claims]
        dupes = {i for i in ids if ids.count(i) > 1}
        if dupes:
            raise ValueError(f"duplicate claim ids: {sorted(dupes)}")
        return self


class Status(StrEnum):
    """Verification statuses; the exact conditions are in STATUS_DEFINITIONS."""

    NOT_TESTED = "NOT_TESTED"
    IMPLEMENTED_NOT_VALIDATED = "IMPLEMENTED_NOT_VALIDATED"
    SIMULATION_SUPPORTED = "SIMULATION_SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    REQUIRES_PHYSICAL_VALIDATION = "REQUIRES_PHYSICAL_VALIDATION"
    CONSISTENT_WITH_RECORD = "CONSISTENT_WITH_RECORD"


STATUS_DEFINITIONS = {
    Status.NOT_TESTED: (
        "No experiment or check in this repository addresses the claim, because it is out of the "
        "approved scope or a prerequisite (data, model, parameter provenance) is missing."
    ),
    Status.IMPLEMENTED_NOT_VALIDATED: (
        "Code that addresses the claim exists and runs, but at least one required condition for "
        "SIMULATION_SUPPORTED is not met (a verification test fails, the model or a parameter "
        "lacks provenance for the claimed use, or the claim's conditions are not fully specified)."
    ),
    Status.SIMULATION_SUPPORTED: (
        "All of: (1) the claim is restated with its model, operating domain and metric; (2) the "
        "pre-registered experiment reproduces it (same sign and, if a value is claimed, within the "
        "claimed interval); (3) all verification tests pass; (4) every number is regenerated from "
        "saved raw outputs by a documented command at a recorded Git commit. It says nothing "
        "about physical reality."
    ),
    Status.CONTRADICTED: (
        "A reproducible check or the pre-registered experiment gives a result inconsistent with "
        "the claim (opposite sign, outside the claimed interval, or the report's own numbers or "
        "equations are mutually inconsistent or dimensionally invalid)."
    ),
    Status.CONSISTENT_WITH_RECORD: (
        "A non-quantitative statement about how the work was done (declaration, limitation) "
        "that agrees with every artefact found. It is not evidence for any result."
    ),
    Status.REQUIRES_PHYSICAL_VALIDATION: (
        "The claim concerns physical hardware, real batteries, real traffic data, vehicles or "
        "certification; no simulation in this repository can establish it."
    ),
}


PRECEDENCE = (
    "When several statuses apply, CONTRADICTED takes precedence, then "
    "REQUIRES_PHYSICAL_VALIDATION, then IMPLEMENTED_NOT_VALIDATED, then NOT_TESTED. "
    "Rows N## are restated claims proposed for a revised report; rows C## are the original claims."
)


class MatrixRow(BaseModel):
    model_config = ConfigDict(extra="forbid")
    claim_id: str = Field(pattern=r"^[CN]\d{2}$")
    original_statement: str
    required_evidence: str
    implemented_experiment: str
    supporting_artifacts: list[str] = Field(default_factory=list)
    verification_status: Status
    contradictory_or_negative_evidence: str
    final_reporting_recommendation: str


def load_registry(path: Path = REGISTRY_PATH) -> Registry:
    return Registry.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def load_matrix(path: Path = MATRIX_PATH) -> list[MatrixRow]:
    rows = yaml.safe_load(path.read_text(encoding="utf-8"))["rows"]
    return [MatrixRow.model_validate(r) for r in rows]


def write_matrix_exports(rows: list[MatrixRow], out_dir: Path) -> list[Path]:
    """Write the evidence matrix as CSV and JSON (machine-readable exports)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    data = [r.model_dump(mode="json") for r in rows]
    json_path = out_dir / "evidence_matrix.json"
    json_path.write_text(
        json.dumps(
            {
                "status_definitions": {k.value: v for k, v in STATUS_DEFINITIONS.items()},
                "rows": data,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    csv_path = out_dir / "evidence_matrix.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(data[0]))
        w.writeheader()
        for row in data:
            w.writerow({**row, "supporting_artifacts": "; ".join(row["supporting_artifacts"])})
    return [json_path, csv_path]
