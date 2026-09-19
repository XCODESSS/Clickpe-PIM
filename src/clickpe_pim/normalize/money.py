from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from clickpe_pim.contracts import Value

MULTIPLIERS = {
    "k": Decimal(1000),
    "l": Decimal(100000),
    "lac": Decimal(100000),
    "lacs": Decimal(100000),
    "lakh": Decimal(100000),
    "lakhs": Decimal(100000),
    "cr": Decimal(10000000),
    "crore": Decimal(10000000),
    "crores": Decimal(10000000),
}
TOKEN = re.compile(r"(?P<num>\d[\d,]*(?:\.\d+)?)\s*(?P<scale>crores?|cr|lakhs?|lacs?|lac|[kKlL])?", re.I)
MONEY_MARKER = re.compile(r"(?:₹|Rs\.?|INR)", re.I)


def bounds(numbers: list[Decimal], qualifier: str) -> tuple[Decimal | None, Decimal | None, str]:
    if len(numbers) == 2:
        return numbers[0], numbers[1], "range"
    if qualifier == "from":
        return numbers[0], None, "from"
    if qualifier == "up_to":
        return None, numbers[0], "up_to"
    return numbers[0], numbers[0], "exact"


def _decimal(token: str, scale: str | None) -> Decimal:
    value = Decimal(token.replace(",", ""))
    return value * MULTIPLIERS.get((scale or "").casefold(), Decimal(1))


def normalize_currency(raw: str) -> Value | None:
    if not raw or re.search(r"[$€£]|\b(?:USD|EUR|GBP)\b|(?:^|\s)-\s*\d", raw, re.I):
        return None
    text = raw.strip().replace("–", "-").replace("—", "-")
    qualifier = "up_to" if re.search(r"\b(?:up\s*to|upto|maximum|max)\b", text, re.I) else "from" if re.search(r"\b(?:from|starting\s+from|minimum|min)\b", text, re.I) else "exact"
    cleaned = MONEY_MARKER.sub(" ", text)
    cleaned = re.sub(r"\b(?:loan(?: amount)?|borrow|loans?|amount|of|is|between|up\s*to|upto|maximum|max|from|starting\s+from|minimum|min)\b", " ", cleaned, flags=re.I)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" :")
    matches = list(TOKEN.finditer(cleaned))
    if not matches or len(matches) > 2:
        return None
    residue = TOKEN.sub("", cleaned)
    if re.sub(r"[\s,:-]+", "", residue):
        return None
    try:
        values = [_decimal(m.group("num"), m.group("scale")) for m in matches]
    except InvalidOperation:
        return None
    if len(matches) == 2:
        left, right = matches
        right_scale = right.group("scale")
        left_scale = left.group("scale")
        if right_scale and not left_scale:
            raw_left = left.group("num")
            if "," not in raw_left and Decimal(raw_left) < 1000:
                values[0] *= MULTIPLIERS[right_scale.casefold()]
        elif left_scale and not right_scale:
            raw_right = right.group("num")
            if "," not in raw_right and Decimal(raw_right) < 1000:
                values[1] *= MULTIPLIERS[left_scale.casefold()]
        if values[0] > values[1]:
            return None
    lower, upper, normalized_qualifier = bounds(values, qualifier)
    return Value(kind="money", lower=lower, upper=upper, unit="INR", qualifier=normalized_qualifier)
