from __future__ import annotations

import re

from bs4 import BeautifulSoup

from clickpe_pim.catalogue.extract import _observation
from clickpe_pim.contracts import Capture, Value
from clickpe_pim.normalize.money import normalize_currency
from clickpe_pim.normalize.rates import normalize_rate
from clickpe_pim.normalize.tenure import normalize_tenure


def extract_disclosures(html: str, capture: Capture) -> dict[str, list]:
    soup = BeautifulSoup(html, "html.parser")
    output: dict[str, list] = {}
    headings = soup.find_all(["h2", "h3"])
    for index, heading in enumerate(headings):
        label = heading.get_text(" ", strip=True)
        chunks = []
        for sibling in heading.next_siblings:
            if getattr(sibling, "name", None) in {"h2", "h3"}:
                break
            text = sibling.get_text(" ", strip=True) if hasattr(sibling, "get_text") else str(sibling).strip()
            if text:
                chunks.append(text)
        section = " ".join(chunks)
        if not section:
            continue
        facts = []
        for field, pattern, normalizer in (
            ("loan_amount", r"Loan Amount\s*[:\-]?\s*([^|;]+)", normalize_currency),
            ("tenure", r"Tenure\s*[:\-]?\s*([^|;]+)", normalize_tenure),
            ("interest_rate", r"Interest Rate\s*[:\-]?\s*([^|;]+)", normalize_rate),
        ):
            match = re.search(pattern, section, re.I)
            if match and (value := normalizer(match.group(1).strip())):
                facts.append(_observation(capture, label.casefold().replace(" ", "_"), field, match.group(0), f"heading:{index}:{label}", value, confidence=.8))
        for role_label in ("LSP", "Lending NBFC"):
            match = re.search(rf"{role_label}\s*[:\-]?\s*([^|;]+)", section, re.I)
            if match:
                facts.append(_observation(capture, label.casefold().replace(" ", "_"), "provider_identity", match.group(0), f"heading:{index}:{label}", Value(kind="text", text=match.group(1).strip()), confidence=.8))
        output[label] = facts
    return output

