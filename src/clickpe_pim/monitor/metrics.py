from clickpe_pim.contracts import Mapping, Observation, Product


def weighted_completeness(group_fractions: dict[str, float], weights: dict[str, float]) -> float:
    if not weights or any(not 0 <= value <= 1 for value in group_fractions.values()) or any(value < 0 for value in weights.values()):
        raise ValueError("fractions and weights must be valid")
    denominator = sum(weights.values())
    if denominator <= 0:
        raise ValueError("weight sum must be positive")
    return 100 * sum(weights[group] * group_fractions.get(group, 0) for group in weights) / denominator


def ratio(numerator: int, denominator: int) -> float | None:
    if numerator < 0 or denominator < 0 or numerator > denominator:
        raise ValueError("invalid ratio")
    return numerator / denominator if denominator else None


def _endpoint_fraction(items: list[Observation], *, require_rate_period: bool = False) -> float:
    eligible = [
        item
        for item in items
        if item.state == "present"
        and item.value is not None
        and (not require_rate_period or item.value.period != "unknown")
        and item.context == "offer"
    ]
    if not eligible:
        return 0
    return max(
        (int(item.value.lower is not None) + int(item.value.upper is not None)) / 2
        for item in eligible
    )


def product_group_fractions(
    product: Product,
    observations: list[Observation],
    mappings: list[Mapping],
) -> dict[str, float]:
    """Compute the documented completeness slots without redistributing weights."""
    present = [item for item in observations if item.product_id == product.product_id]
    by_field: dict[str, list[Observation]] = {}
    for item in present:
        by_field.setdefault(item.field, []).append(item)

    lender = float(
        any(
            item.product_id == product.product_id
            and item.role == "lender"
            and item.review_state == "approved"
            and item.scope == "same_programme"
            for item in mappings
        )
    )
    interest = max(
        _endpoint_fraction(by_field.get("interest_rate", []), require_rate_period=True),
        _endpoint_fraction(by_field.get("apr", []), require_rate_period=True),
    )
    amount = _endpoint_fraction(by_field.get("loan_amount", []))
    tenure = _endpoint_fraction(by_field.get("tenure", []))

    def explicit(field_name: str) -> float:
        return float(
            any(
                item.state == "present" and item.context == "offer"
                for item in by_field.get(field_name, [])
            )
        )

    processing = explicit("processing_fee")
    other_fee = max(
        (explicit(name) for name in (
            "foreclosure_fee", "prepayment_fee", "late_payment_fee", "stamp_duty", "other_charges"
        )),
        default=0,
    )
    raw_fee = .5 if explicit("fees_raw_text") else 0
    fees = (processing + max(other_fee, raw_fee)) / 2

    age = (
        explicit("minimum_age") + explicit("maximum_age")
    ) / 2
    if product.category == "business_loan":
        eligibility_slots = [
            explicit("minimum_business_vintage"),
            explicit("business_type"),
            explicit("minimum_turnover"),
        ]
    elif product.category == "loan_against_property":
        eligibility_slots = [age, explicit("minimum_income"), explicit("location_restrictions")]
    else:
        eligibility_slots = [age, explicit("employment_type"), explicit("minimum_income")]
    eligibility = sum(eligibility_slots) / len(eligibility_slots)
    repayment = max(
        explicit("repayment_frequency"), explicit("emi_type"),
        explicit("auto_pay_available"), explicit("enach_available"),
    )
    documents = explicit("documents_raw")
    return {
        "lender": min(1, lender), "interest": min(1, interest),
        "amount": min(1, amount), "fees": min(1, fees), "tenure": min(1, tenure),
        "eligibility": min(1, eligibility), "repayment": min(1, repayment),
        "documents": min(1, documents),
    }
