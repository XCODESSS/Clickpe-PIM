from __future__ import annotations

import re
from decimal import Decimal

from clickpe_pim.contracts import Value


def normalize_requirement(field: str, raw: str) -> Value | None:
    if not raw or not raw.strip():
        return None
    text = raw.strip()
    conditional = bool(re.search(r"\b(?:subject to|NTC|except|only|location|segment)\b", text, re.I))
    qualifier = "conditional" if conditional else "exact"
    if field == "minimum_credit_score":
        match = re.search(r"(?:minimum|at least)?\s*(?:CIBIL|credit score)?\s*(\d{3})(\+|\s+or\s+above|\s+and\s+above)?", text, re.I)
        if not match:
            return None
        return Value(kind="number", lower=Decimal(match.group(1)), unit="score", qualifier=qualifier, text=text if conditional or "above" in text.casefold() else None)
    if field == "employment_type":
        values = []
        for pattern, name in ((r"salaried", "salaried"), (r"self[- ]?employed", "self_employed"), (r"business owner", "business_owner"), (r"professional", "professional")):
            if re.search(pattern, text, re.I):
                values.append(name)
        return Value(kind="set", options=tuple(sorted(set(values))), qualifier=qualifier, text=text if conditional else None) if values else None
    if field == "repayment_frequency":
        values = [name for name in ("daily", "weekly", "monthly", "flexible") if re.search(rf"\b{name}\b", text, re.I)]
        return Value(kind="text", text=values[0] if len(values) == 1 else ", ".join(values), qualifier=qualifier) if values else None
    if field.endswith("_required"):
        if re.search(r"\b(?:not required|optional|no need)\b", text, re.I):
            return Value(kind="boolean", boolean=False, qualifier=qualifier, text=text if conditional else None)
        if re.search(r"\b(?:required|mandatory|submit|provide)\b", text, re.I):
            return Value(kind="boolean", boolean=True, qualifier=qualifier, text=text if conditional else None)
        return None
    return Value(kind="text", text=text, qualifier=qualifier)

