from dataclasses import dataclass


@dataclass(frozen=True)
class FieldSpec:
    kind: str
    group: str
    importance: float
    unit: str | None = None
    numeric: bool = False


def _s(kind: str, group: str, importance: float, unit: str | None = None, numeric: bool = False) -> FieldSpec:
    return FieldSpec(kind, group, importance, unit, numeric)


FIELD_SPECS: dict[str, FieldSpec] = {
    "loan_amount": _s("money", "amount", .8, "INR", True),
    "interest_rate": _s("rate", "interest", 1, "%", True),
    "apr": _s("rate", "interest", 1, "%", True),
    "tenure": _s("tenure", "tenure", .8, "days", True),
    "regulated_lender": _s("text", "lender", 1),
    "repayment_frequency": _s("text", "repayment", .4),
    "emi_type": _s("text", "repayment", .4),
    "auto_pay_available": _s("boolean", "repayment", .4),
    "enach_available": _s("boolean", "repayment", .4),
    "processing_fee": _s("money", "fees", .8, "INR", True),
    "foreclosure_fee": _s("money", "fees", .8, "INR", True),
    "prepayment_fee": _s("money", "fees", .8, "INR", True),
    "late_payment_fee": _s("money", "fees", .8, "INR", True),
    "stamp_duty": _s("money", "fees", .8, "INR", True),
    "other_charges": _s("money", "fees", .8, "INR", True),
    "minimum_age": _s("number", "eligibility", .6, "years", True),
    "maximum_age": _s("number", "eligibility", .6, "years", True),
    "minimum_income": _s("money", "eligibility", .6, "INR", True),
    "minimum_turnover": _s("money", "eligibility", .6, "INR", True),
    "minimum_business_vintage": _s("tenure", "eligibility", .6, "days", True),
    "minimum_credit_score": _s("number", "eligibility", .6, "score", True),
    "employment_type": _s("set", "eligibility", .6),
    "business_type": _s("set", "eligibility", .6),
    "citizenship": _s("text", "eligibility", .6),
    "residency": _s("text", "eligibility", .6),
    "location_restrictions": _s("text", "eligibility", .6),
    "pan_required": _s("boolean", "documents", .4),
    "aadhaar_required": _s("boolean", "documents", .4),
    "bank_statement_months": _s("number", "documents", .4, "months", True),
    "gst_required": _s("boolean", "documents", .4),
    "income_proof_required": _s("boolean", "documents", .4),
    "salary_slip_required": _s("boolean", "documents", .4),
    "business_proof_required": _s("boolean", "documents", .4),
    "address_proof_required": _s("boolean", "documents", .4),
    "documents_raw": _s("text", "documents", .4),
    "fees_raw_text": _s("text", "fees", .8),
    "approval_time": _s("tenure", "wording", .2, "days", True),
    "disbursal_time": _s("tenure", "wording", .2, "days", True),
    "application_mode": _s("text", "wording", .2),
    "paperless": _s("boolean", "wording", .2),
    "instant_disbursal": _s("boolean", "wording", .2),
    "marketing_claim": _s("text", "wording", .2),
    "category_content": _s("text", "wording", .2),
    "provider_identity": _s("text", "lender", 1),
}

