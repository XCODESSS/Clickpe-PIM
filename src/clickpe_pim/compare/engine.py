from __future__ import annotations

import hashlib
from decimal import Decimal

from clickpe_pim.contracts import Comparison, Mapping, Observation
from clickpe_pim.settings import Settings


def _result(left: Observation, right: Observation, mapping: Mapping, kind: str, status: str, code: str, reason: str, endpoints: tuple[str, ...] = ()) -> Comparison:
    identity = f"{left.run_id}|{left.product_id}|{left.field}|{left.observation_id}|{right.observation_id}|{mapping.mapping_id}|{code}"
    return Comparison(
        comparison_id=hashlib.sha256(identity.encode()).hexdigest(), run_id=left.run_id,
        product_id=left.product_id, field=left.field, left_id=left.observation_id,
        right_id=right.observation_id, mapping_id=mapping.mapping_id, kind=kind,
        status=status, reason=reason, reason_code=code,
        confidence=min(left.confidence, right.confidence, mapping.confidence), compared_endpoints=endpoints,
    )


def compare_pair(left: Observation, right: Observation, mapping: Mapping, *, kind: str, settings: Settings) -> Comparison:
    if kind not in {"internal", "external"}:
        raise ValueError("kind must be internal or external")
    if left.product_id != right.product_id or mapping.product_id != left.product_id or mapping.source_id not in {left.source_id, right.source_id}:
        raise ValueError("product/source identity mismatch")
    if left.field != right.field:
        return _result(left, right, mapping, kind, "UNCOMPARABLE", "different_field", "Fields differ.")
    if any(item.state in {"failed", "unsupported"} for item in (left, right)):
        return _result(left, right, mapping, kind, "UNCOMPARABLE", "extraction_unavailable", "At least one source could not be extracted.")
    if mapping.review_state != "approved" or mapping.scope != "same_programme" or mapping.confidence < settings.comparison.minimum_mapping_confidence:
        return _result(left, right, mapping, kind, "AMBIGUOUS", "programme_unconfirmed", "Programme applicability has not been confirmed.")
    if any(item.state == "ambiguous" for item in (left, right)) or left.conditions != right.conditions:
        return _result(left, right, mapping, kind, "AMBIGUOUS", "conditional_or_multiple_claims", "Conditions or multiple claims differ.")
    if left.state == right.state == "absent":
        return _result(left, right, mapping, kind, "UNCOMPARABLE", "both_absent", "Both scoped sources omit the field.")
    if left.state == "absent":
        return _result(left, right, mapping, kind, "MISSING_CLICKPE", "supported_absence_left", "ClickPe source has a supported absence.")
    if right.state == "absent":
        return _result(left, right, mapping, kind, "MISSING_PROVIDER", "supported_absence_right", "Comparison source has a supported absence.")
    assert left.value is not None and right.value is not None
    a, b = left.value, right.value
    if left.context != "offer" or right.context != "offer":
        return _result(left, right, mapping, kind, "UNCOMPARABLE", "non_offer_context", "At least one claim is not a general offer term.")
    if (a.kind, a.unit) != (b.kind, b.unit):
        return _result(left, right, mapping, kind, "UNCOMPARABLE", "unit_or_kind_mismatch", "Value kind or unit differs.")
    if a.kind == "rate" and (a.period == "unknown" or b.period == "unknown" or a.period != b.period or a.basis != b.basis):
        return _result(left, right, mapping, kind, "UNCOMPARABLE", "rate_semantics_mismatch", "Rate period or basis is unknown or differs.")
    if a.qualifier == "policy" or b.qualifier == "policy" or a.options != b.options and (a.options or b.options):
        return _result(left, right, mapping, kind, "UNCOMPARABLE", "bound_semantics_mismatch", "Policy or discrete-option semantics cannot be compared directly.")
    endpoints = tuple(name for name in ("lower", "upper") if getattr(a, name) is not None and getattr(b, name) is not None)
    if not endpoints:
        return _result(left, right, mapping, kind, "UNCOMPARABLE", "no_shared_endpoint", "No comparable endpoint exists.")
    tolerance = Decimal(str(settings.comparison.amount_tolerance_inr if a.kind == "money" else settings.comparison.rate_tolerance_percentage_points if a.kind == "rate" else settings.comparison.approximate_tenure_tolerance_days if a.kind == "tenure" and (a.approximate or b.approximate) else 0))
    same = all(abs(getattr(a, name) - getattr(b, name)) <= tolerance for name in endpoints)
    status = "MATCH" if same else "DIFFERENT"
    code = "within_tolerance" if same else "endpoint_difference"
    reason = "Comparable endpoints match within configured tolerance." if same else f"Possible {left.field} difference; review programme applicability and the cited source terms."
    return _result(left, right, mapping, kind, status, code, reason, endpoints)

