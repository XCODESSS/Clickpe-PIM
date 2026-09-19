from decimal import Decimal

import pytest

from clickpe_pim.normalize.money import normalize_currency


@pytest.mark.parametrize("raw,expected", [("₹5 lakh", "500000"), ("Rs 500000", "500000"), ("INR 5,00,000", "500000"), ("5L", "500000"), ("25K", "25000"), ("₹1 crore", "10000000")])
def test_money(raw, expected):
    value = normalize_currency(raw)
    assert value.lower == value.upper == Decimal(expected)


def test_qualifiers_and_shared_units():
    assert normalize_currency("up to ₹5 lakh").lower is None
    assert normalize_currency("₹20,000–3 lakh").upper == Decimal("300000")
    assert normalize_currency("1–5 lakh").lower == Decimal("100000")
    assert normalize_currency("₹5–3 lakh") is None


@pytest.mark.parametrize("raw", ["USD 500", "₹5 lakh for salaried people", "amount -2 lakh"])
def test_unsupported_money_is_not_guessed(raw):
    assert normalize_currency(raw) is None

