from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from clickpe_pim.contracts import Value
from clickpe_pim.normalize.money import bounds

UNITS = {"day": False, "week": False, "month": True, "year": True}


def _days(value: Decimal, unit: str) -> Decimal:
    if unit == "day":
        return value
    if unit == "week":
        return value * Decimal(7)
    if unit == "month":
        return value * Decimal(365) / Decimal(12)
    return value * Decimal(365)


def normalize_tenure(raw: str) -> Value | None:
    if not raw or re.search(r"business\s+days?|calendar\s+days?", raw, re.I):
        return None
    text = raw.strip().replace("–", "-").replace("—", "-")
    found_units = {u.casefold().rstrip("s") for u in re.findall(r"\b(days?|weeks?|months?|years?)\b", text, re.I)}
    if len(found_units) != 1:
        return None
    unit_name = next(iter(found_units))
    approximate = UNITS[unit_name]
    numbers = re.findall(r"(?<![\d.])(\d+(?:\.\d+)?)", text)
    if not numbers or len(numbers) > 20:
        return None
    try:
        raw_numbers = [Decimal(item) for item in numbers]
    except InvalidOperation:
        return None
    converted = [_days(value, unit_name) for value in raw_numbers]
    is_list = len(converted) > 2 or (len(converted) > 1 and bool(re.search(r",|\band\b", text, re.I)) and "-" not in text)
    options = tuple(f"{value} {unit_name}{'' if value == 1 else 's'}" for value in raw_numbers) if is_list else ()
    qualifier = "up_to" if re.search(r"\b(?:up\s*to|upto|maximum|max)\b", text, re.I) else "from" if re.search(r"\b(?:from|minimum|min)\b", text, re.I) else "exact"
    if is_list:
        lower, upper, normalized = min(converted), max(converted), "range"
    elif len(converted) == 2:
        lower, upper, normalized = converted[0], converted[1], "range"
        if lower > upper:
            return None
    else:
        lower, upper, normalized = bounds(converted, qualifier)
    return Value(kind="tenure", lower=lower, upper=upper, unit="days", qualifier=normalized, approximate=approximate, options=options)
