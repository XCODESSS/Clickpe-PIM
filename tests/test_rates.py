from decimal import Decimal

from clickpe_pim.normalize.rates import normalize_rate


def test_rate_period_and_policy():
    assert normalize_rate("1% monthly").period == "monthly"
    assert normalize_rate("12% p.a.").period == "annual"
    assert normalize_rate("Starting from 11%").period == "unknown"
    assert normalize_rate("As per partner policy").lower is None
    assert normalize_rate("11%-24% p.a.").upper == Decimal("24")


def test_non_rate_percentage_is_rejected():
    assert normalize_rate("100% digital approval") is None
    assert normalize_rate("APR 2% monthly", apr=True) is None

