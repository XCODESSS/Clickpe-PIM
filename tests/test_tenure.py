from decimal import Decimal

from clickpe_pim.normalize.tenure import normalize_tenure


def test_tenure_preserves_approximation_and_options():
    assert normalize_tenure("24 months").upper == Decimal("730")
    assert normalize_tenure("24 months").approximate
    assert normalize_tenure("104–300 days").lower == Decimal("104")
    assert not normalize_tenure("104–300 days").approximate
    assert normalize_tenure("104, 156, 234 and 313 days").options == ("104 days", "156 days", "234 days", "313 days")


def test_tenure_rejects_unknown_or_mixed_units():
    assert normalize_tenure("24") is None
    assert normalize_tenure("2 months or 60 days") is None

