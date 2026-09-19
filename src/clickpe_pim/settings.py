from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ScrapingSettings(StrictModel):
    request_delay: float = Field(ge=0)
    max_retries: int = Field(ge=0, le=10)
    connect_timeout: float = Field(gt=0)
    read_timeout: float = Field(gt=0)
    max_bytes: int = Field(gt=0)
    max_pages_per_host: int = Field(gt=0)
    user_agent: str = "ClickPePIM/0.1"


class MonitoringSettings(StrictModel):
    stale_days: int = Field(ge=0)
    confirm_absence_hours: int = Field(gt=0)
    required_absence_observations: int = Field(ge=2)
    maximum_comparison_age_days: int = Field(gt=0)
    maximum_pair_skew_days: int = Field(ge=0)


class CompletenessSettings(StrictModel):
    weights: dict[str, float]

    @field_validator("weights")
    @classmethod
    def valid_weights(cls, value: dict[str, float]) -> dict[str, float]:
        if any(weight < 0 for weight in value.values()) or abs(sum(value.values()) - 1) > 1e-9:
            raise ValueError("completeness weights must be non-negative and sum to one")
        return value


class ComparisonSettings(StrictModel):
    amount_tolerance_inr: float = Field(ge=0)
    rate_tolerance_percentage_points: float = Field(ge=0)
    approximate_tenure_tolerance_days: float = Field(ge=0)
    minimum_mapping_confidence: float = Field(ge=0, le=1)
    high_priority_threshold: int = Field(ge=0, le=100)


class PathSettings(StrictModel):
    database: Path
    raw: Path
    snapshots: Path


class Settings(StrictModel):
    scraping: ScrapingSettings
    monitoring: MonitoringSettings
    completeness: CompletenessSettings
    comparison: ComparisonSettings
    paths: PathSettings


def load_settings(path: Path) -> Settings:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return Settings.model_validate(payload)

