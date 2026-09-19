from datetime import datetime

import pytest
from pydantic import ValidationError

from clickpe_pim.contracts import Capture, Mapping, Value
from clickpe_pim.settings import load_settings


def test_unknown_is_not_zero():
    assert Value(kind="money", unit="INR").lower is None


def test_inverted_range_is_rejected():
    with pytest.raises(ValidationError):
        Value(kind="money", lower="500000", upper="300000", unit="INR")


@pytest.mark.parametrize("value", ["-1", "NaN", "Infinity"])
def test_invalid_finance_quantities(value):
    with pytest.raises(ValidationError):
        Value(kind="money", lower=value, unit="INR")


def test_completeness_weights_sum_to_one():
    cfg = load_settings(__import__("pathlib").Path("config.yaml"))
    assert sum(cfg.completeness.weights.values()) == pytest.approx(1)


def test_naive_capture_timestamp_rejected():
    with pytest.raises(ValidationError):
        Capture(capture_id="c", run_id="r", source_id="s", source_type="x", url="https://example.org", final_url="https://example.org", retrieved_at=datetime(2026, 1, 1), status="failed")


def test_approved_mapping_needs_review_evidence():
    with pytest.raises(ValidationError):
        Mapping(mapping_id="m", product_id="p", source_id="s", role="lender", scope="same_programme", review_state="approved", confidence=1, rationale="")

