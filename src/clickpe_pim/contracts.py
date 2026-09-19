from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .fields import FIELD_SPECS


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def _aware(value: datetime | None, name: str) -> None:
    if value is not None and (value.tzinfo is None or value.utcoffset() is None):
        raise ValueError(f"{name} must be timezone-aware")


class Value(Record):
    kind: Literal["money", "rate", "tenure", "number", "text", "boolean", "set"]
    lower: Decimal | None = None
    upper: Decimal | None = None
    text: str | None = None
    boolean: bool | None = None
    options: tuple[str, ...] = ()
    unit: str | None = None
    period: Literal["annual", "monthly", "daily", "unknown"] = "unknown"
    basis: Literal["flat", "reducing", "unknown"] = "unknown"
    qualifier: Literal["exact", "range", "from", "up_to", "policy", "conditional"] = "exact"
    approximate: bool = False

    @model_validator(mode="after")
    def validate_bounds(self) -> Value:
        for name, value in (("lower", self.lower), ("upper", self.upper)):
            if value is not None and (not value.is_finite() or value < 0):
                raise ValueError(f"{name} must be finite and non-negative")
        if self.lower is not None and self.upper is not None and self.lower > self.upper:
            raise ValueError("lower must be less than or equal to upper")
        if self.qualifier == "policy" and self.lower is not None:
            raise ValueError("policy values cannot have numeric bounds")
        return self


class Product(Record):
    product_id: str
    name: str
    category: str
    provider_name_raw: str | None = None
    provider_id: str | None = None
    clickpe_url: str
    active_status: Literal["active", "inactive", "unknown"]


class Capture(Record):
    capture_id: str
    run_id: str
    source_id: str
    source_type: str
    url: str
    final_url: str
    retrieved_at: datetime
    status: Literal["ok", "not_modified", "blocked", "failed", "not_found"]
    http_status: int | None = None
    sha256: str | None = None
    raw_path: str | None = None
    media_type: str | None = None
    error_code: str | None = None

    @model_validator(mode="after")
    def validate_timestamp(self) -> Capture:
        _aware(self.retrieved_at, "retrieved_at")
        return self


class Observation(Record):
    observation_id: str
    run_id: str
    product_id: str
    source_id: str
    capture_id: str
    field: str
    state: Literal["present", "absent", "ambiguous", "unsupported", "failed"]
    value: Value | None = None
    raw_text: str
    locator: str
    context: Literal["offer", "marketing", "calculator", "example", "form_config", "unknown"]
    extracted_at: datetime
    extractor_version: str
    confidence: float = Field(ge=0, le=1)
    conditions: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_evidence(self) -> Observation:
        _aware(self.extracted_at, "extracted_at")
        if self.field not in FIELD_SPECS:
            raise ValueError(f"unknown field: {self.field}")
        if self.state == "present":
            if self.value is None:
                raise ValueError("present observation requires a value")
            if not self.raw_text.strip() or not self.locator.strip():
                raise ValueError("present observation requires quote and locator")
        if self.state == "absent":
            if self.value is not None:
                raise ValueError("absent observation cannot have a value")
            if not self.locator.strip():
                raise ValueError("absent observation requires inspected-scope locator")
        return self


class Mapping(Record):
    mapping_id: str
    product_id: str
    source_id: str
    entity_id: str | None = None
    role: Literal["brand", "lsp", "lender", "marketplace", "parent", "unknown"]
    programme: str | None = None
    segment: str | None = None
    geography: str | None = None
    scope: Literal["same_programme", "related_programme", "unknown", "different_programme"]
    review_state: Literal["candidate", "approved", "rejected"]
    confidence: float = Field(ge=0, le=1)
    evidence_capture_id: str | None = None
    evidence_locator: str | None = None
    rationale: str
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    effective_from: datetime | None = None
    effective_to: datetime | None = None

    @model_validator(mode="after")
    def validate_review(self) -> Mapping:
        for name in ("reviewed_at", "effective_from", "effective_to"):
            _aware(getattr(self, name), name)
        if self.review_state == "approved":
            required = (
                self.reviewed_by,
                self.reviewed_at,
                self.evidence_capture_id,
                self.evidence_locator,
                self.rationale.strip(),
            )
            if not all(required):
                raise ValueError("approved mapping requires reviewer, date, evidence, and rationale")
        return self


class Comparison(Record):
    comparison_id: str
    run_id: str
    product_id: str
    field: str
    left_id: str | None
    right_id: str | None
    mapping_id: str | None
    kind: Literal["internal", "external", "single_source"]
    status: Literal[
        "MATCH", "DIFFERENT", "MISSING_CLICKPE", "MISSING_PROVIDER", "UNCOMPARABLE", "AMBIGUOUS"
    ]
    reason: str
    reason_code: str
    confidence: float = Field(ge=0, le=1)
    compared_endpoints: tuple[str, ...] = ()


class Change(Record):
    change_id: str
    product_id: str
    source_id: str | None
    field: str | None
    type: Literal[
        "VALUE_CHANGED", "PRODUCT_ADDED", "PRODUCT_REMOVED", "SOURCE_DISAPPEARED", "FIELD_ADDED", "FIELD_REMOVED"
    ]
    previous_id: str | None
    current_id: str | None
    detected_at: datetime
    synthetic: bool = False

    @model_validator(mode="after")
    def validate_timestamp(self) -> Change:
        _aware(self.detected_at, "detected_at")
        return self

