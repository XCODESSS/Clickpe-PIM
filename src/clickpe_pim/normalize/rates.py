from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from clickpe_pim.contracts import Value
from clickpe_pim.normalize.money import bounds


def normalize_rate(raw: str, *, apr: bool = False) -> Value | None:
    if not raw:
        return None
    text = raw.strip()
    if re.search(r"(?:as per|subject to).*(?:policy|assessment)|partner policy", text, re.I):
        return Value(kind="rate", text=text, unit="%", qualifier="policy")
    if "%" not in text or re.search(r"\b(?:digital|approval|paperless)\b", text, re.I):
        return None
    period_hits: list[str] = []
    for period, pattern in {
        "annual": r"(?:\bp\.?\s*a\.?(?=\s|$)|\bper annum\b|\bannual(?:ly)?\b|\byearly\b)",
        "monthly": r"(?:\bp\.?\s*m\.?(?=\s|$)|\bper month\b|\bmonthly\b)",
        "daily": r"\b(?:per day|daily)\b",
    }.items():
        if re.search(pattern, text, re.I):
            period_hits.append(period)
    if len(period_hits) > 1 or (apr and period_hits and period_hits[0] != "annual"):
        return None
    period = "annual" if apr else period_hits[0] if period_hits else "unknown"
    basis_hits = [name for name in ("flat", "reducing") if re.search(rf"\b{name}\b", text, re.I)]
    if len(basis_hits) > 1:
        return None
    basis = basis_hits[0] if basis_hits else "unknown"
    number_part = re.sub(r"\b(?:APR|interest(?: rate)?|rate of interest|starting from|from|up\s*to|upto)\b", " ", text, flags=re.I)
    number_part = re.sub(r"(?:\bp\.?\s*a\.?(?=\s|$)|\bper annum\b|\bannual(?:ly)?\b|\byearly\b|\bp\.?\s*m\.?(?=\s|$)|\bper month\b|\bmonthly\b|\bper day\b|\bdaily\b|\bflat\b|\breducing\b)", " ", number_part, flags=re.I)
    number_part = number_part.replace("–", "-").replace("—", "-")
    matches = re.findall(r"(?<![\d.])(\d+(?:\.\d+)?)\s*%?", number_part)
    if not matches or len(matches) > 2:
        return None
    residue = re.sub(r"(?<![\d.])\d+(?:\.\d+)?\s*%?", "", number_part)
    if re.sub(r"[\s,:;-]+", "", residue):
        return None
    try:
        values = [Decimal(x) for x in matches]
    except InvalidOperation:
        return None
    if any(x < 0 for x in values) or (len(values) == 2 and values[0] > values[1]):
        return None
    qualifier = "up_to" if re.search(r"\b(?:up\s*to|upto)\b", text, re.I) else "from" if re.search(r"\b(?:from|starting from)\b", text, re.I) else "exact"
    lower, upper, normalized = bounds(values, qualifier)
    return Value(kind="rate", lower=lower, upper=upper, unit="%", period=period, basis=basis, qualifier=normalized)
