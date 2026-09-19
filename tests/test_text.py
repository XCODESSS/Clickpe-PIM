from decimal import Decimal

from clickpe_pim.normalize.text import normalize_requirement


def test_conditional_credit_requirement_survives():
    value = normalize_requirement("minimum_credit_score", "Minimum CIBIL 650; NTC applicants accepted subject to banking surrogate")
    assert value.lower == Decimal("650")
    assert value.qualifier == "conditional"
    assert "NTC" in value.text


def test_silence_is_not_false_document_requirement():
    assert normalize_requirement("gst_required", "minimal paperwork") is None
    assert normalize_requirement("gst_required", "GST is optional").boolean is False

