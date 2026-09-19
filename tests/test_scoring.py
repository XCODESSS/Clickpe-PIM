from datetime import datetime, timedelta, timezone

import pytest

from clickpe_pim.compare.scoring import priority
from clickpe_pim.monitor.freshness import age_days, freshness_band
from clickpe_pim.monitor.metrics import ratio, weighted_completeness


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

