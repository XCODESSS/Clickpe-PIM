from datetime import datetime, timedelta, timezone

import pytest

from clickpe_pim.compare.scoring import priority
from clickpe_pim.contracts import Mapping, Product, Value
from clickpe_pim.monitor.freshness import age_days, freshness_band
from clickpe_pim.monitor.metrics import product_group_fractions, ratio, weighted_completeness


def test_unknown_denominator_and_freshness():
    assert ratio(0, 0) is None
    assert freshness_band(None) == "Unknown"
    assert [freshness_band(x) for x in [7, 8, 30, 31, 90, 91]] == ["Fresh", "Monitor", "Monitor", "Stale", "Stale", "High priority"]


def test_weighted_score_and_priority():
    assert weighted_completeness({"lender": 1, "interest": 0}, {"lender": .5, "interest": .5}) == 50
    assert priority("high", 1, 1, 8) == 80
    assert priority("critical", 1, 1, 100) == 100


def test_future_timestamp_rejected():
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError):
        age_days(now + timedelta(days=1), now)


def test_product_completeness_keeps_unknown_groups_at_zero(make_observation):
    product = Product(
        product_id="p1", name="Loan", category="personal_loan",
        clickpe_url="https://example.org", active_status="active",
    )
    groups = product_group_fractions(product, [make_observation()], [])
    assert groups["amount"] == .5
    assert groups["lender"] == 0
    assert groups["interest"] == 0


def test_product_completeness_uses_reviewed_mapping_and_rate_semantics(make_observation):
    product = Product(
        product_id="p1", name="Loan", category="personal_loan",
        clickpe_url="https://example.org", active_status="active",
    )
    mapping = Mapping(
        mapping_id="m1", product_id="p1", source_id="official", entity_id="lender-1",
        role="lender", scope="same_programme", review_state="approved", confidence=.95,
        evidence_capture_id="c1", evidence_locator="#programme", rationale="Reviewed programme evidence.",
        reviewed_by="reviewer", reviewed_at=datetime(2026, 9, 19, tzinfo=timezone.utc),
    )
    policy_rate = make_observation(
        observation_id="rate-policy", field="interest_rate",
        value=Value(kind="rate", text="subject to policy", qualifier="policy"),
        raw_text="subject to policy",
    )
    annual_apr = make_observation(
        observation_id="apr", field="apr",
        value=Value(kind="rate", lower="12", upper="18", unit="percent", period="annual", qualifier="range"),
        raw_text="APR 12%-18% p.a.",
    )
    groups = product_group_fractions(product, [policy_rate, annual_apr], [mapping])
    assert groups["lender"] == 1
    assert groups["interest"] == 1


def test_product_completeness_preserves_partial_fee_and_category_slots(make_observation):
    product = Product(
        product_id="p1", name="Business loan", category="business_loan",
        clickpe_url="https://example.org", active_status="active",
    )
    observations = [
        make_observation(
            observation_id="fee-raw", field="fees_raw_text",
            value=Value(kind="text", text="Charges depend on the schedule", qualifier="policy"),
            raw_text="Charges depend on the schedule",
        ),
        make_observation(
            observation_id="vintage", field="minimum_business_vintage",
            value=Value(kind="tenure", lower="730", upper="730", unit="days"),
            raw_text="2 years in business",
        ),
        make_observation(
            observation_id="business-type", field="business_type",
            value=Value(kind="set", options=("proprietorship",)),
            raw_text="Proprietorship",
        ),
    ]
    groups = product_group_fractions(product, observations, [])
    assert groups["fees"] == .25
    assert groups["eligibility"] == pytest.approx(2 / 3)
