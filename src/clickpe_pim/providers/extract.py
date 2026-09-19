from __future__ import annotations

import re

from bs4 import BeautifulSoup

from clickpe_pim.catalogue.extract import _observation
from clickpe_pim.contracts import Capture
from clickpe_pim.normalize.money import normalize_currency
from clickpe_pim.normalize.rates import normalize_rate
from clickpe_pim.normalize.tenure import normalize_tenure

NORMALIZERS = {"money": normalize_currency, "rate": normalize_rate, "apr": lambda x: normalize_rate(x, apr=True), "tenure": normalize_tenure}


def extract_provider(html: str, capture: Capture, product_id: str, recipe: dict) -> list:
    soup = BeautifulSoup(html, "html.parser")
    for element in soup.select("script,style,nav,footer"):
        element.decompose()
    heading = next((h for h in soup.find_all(["h1", "h2", "h3"]) if h.get_text(" ", strip=True).casefold() == str(recipe.get("expected_heading", "")).casefold()), None)
    if heading is None:
        return [_observation(capture, product_id, field, "", "expected_heading", None, state="unsupported", context="unknown", confidence=0) for field in recipe.get("fields", {})]
    section_parts = []
    excludes = {str(x).casefold() for x in recipe.get("exclude_headings", [])}
    for sibling in heading.next_siblings:
        if getattr(sibling, "name", None) in {"h1", "h2", "h3"}:
            sibling_title = sibling.get_text(" ", strip=True).casefold()
            if sibling_title in excludes or sibling_title:
                break
        section_parts.append(sibling.get_text(" ", strip=True) if hasattr(sibling, "get_text") else str(sibling))
    section = " ".join(section_parts)
    facts = []
    for field, rule in recipe.get("fields", {}).items():
        matches = list(re.finditer(rule["value_pattern"], section, re.I))
        if not matches:
            facts.append(_observation(capture, product_id, field, "", f"heading:{recipe['expected_heading']}", None, state="absent", context="offer", confidence=.8))
            continue
        normalizer = NORMALIZERS[rule["normalizer"]]
        values = [(match.group(0), normalizer(match.group(0))) for match in matches]
        valid = [(raw, value) for raw, value in values if value is not None]
        if len({str(value.model_dump(mode="json")) for _, value in valid}) > 1:
            facts.extend(_observation(capture, product_id, field, raw, f"heading:{recipe['expected_heading']}", value, state="ambiguous", context="offer", confidence=.7) for raw, value in valid)
        else:
            facts.extend(_observation(capture, product_id, field, raw, f"heading:{recipe['expected_heading']}", value, context="offer", confidence=.9) for raw, value in valid)
    return facts

