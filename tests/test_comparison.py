from datetime import datetime, timezone

from clickpe_pim.compare.engine import compare_pair
from clickpe_pim.contracts import Mapping, Value


def approved_mapping(**overrides):
    data = dict(mapping_id="m", product_id="p1", source_id="s1", role="lender", scope="same_programme", review_state="approved", confidence=1, rationale="reviewed programme evidence", reviewed_by="tester", reviewed_at=datetime(2026, 9, 19, tzinfo=timezone.utc), evidence_capture_id="c1", evidence_locator="/evidence")
    data.update(overrides)
    return Mapping(**data)


def test_unconfirmed_programme_is_ambiguous(make_observation, settings):
    a = make_observation()
    b = make_observation(observation_id="other", value=Value(kind="money", upper="300000", unit="INR", qualifier="up_to"))
    mapping = Mapping(mapping_id="m", product_id="p1", source_id="s1", role="lender", scope="unknown", review_state="candidate", confidence=.5, rationale="programme not established")
    result = compare_pair(a, b, mapping, kind="internal", settings=settings)
    assert result.status == "AMBIGUOUS"
    assert result.reason_code == "programme_unconfirmed"


def test_amount_match_and_difference(make_observation, settings):
    left = make_observation()
    right = make_observation(observation_id="right")
    assert compare_pair(left, right, approved_mapping(), kind="external", settings=settings).status == "MATCH"
    changed = make_observation(observation_id="changed", value=Value(kind="money", upper="300000", unit="INR", qualifier="up_to"))
    assert compare_pair(left, changed, approved_mapping(), kind="external", settings=settings).status == "DIFFERENT"


def test_rate_period_mismatch_is_uncomparable(make_observation, settings):
    left = make_observation(field="interest_rate", value=Value(kind="rate", lower="1", upper="1", unit="%", period="monthly"))
    right = make_observation(observation_id="right", field="interest_rate", value=Value(kind="rate", lower="12", upper="12", unit="%", period="annual"))
    assert compare_pair(left, right, approved_mapping(), kind="external", settings=settings).status == "UNCOMPARABLE"


def test_supported_absence_is_missing_not_failure(make_observation, settings):
    left = make_observation(state="absent", value=None, raw_text="", locator="/scope")
    right = make_observation(observation_id="right")
    assert compare_pair(left, right, approved_mapping(), kind="external", settings=settings).status == "MISSING_CLICKPE"

