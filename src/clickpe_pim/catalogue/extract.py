from __future__ import annotations

import hashlib
import re

from clickpe_pim.contracts import Capture, Observation, Value
from clickpe_pim.normalize.money import normalize_currency
from clickpe_pim.normalize.rates import normalize_rate
from clickpe_pim.normalize.tenure import normalize_tenure
from clickpe_pim.normalize.text import normalize_requirement

EXTRACTOR_VERSION = "1"
FIELD_PATTERNS = {
    "loan_amount": re.compile(r"(?:loan(?: amount)?|borrow|loans?)\s*(?:from|of|up to|upto|starting from)?\s*(?:₹|Rs\.?|INR)?\s*[\d,.]+(?:\s*(?:to|[-–])\s*(?:₹|Rs\.?|INR)?\s*[\d,.]+)?\s*(?:lakhs?|lacs?|crores?|[KL])?", re.I),
    "interest_rate": re.compile(r"(?:interest(?: rate)?|rate of interest)[^;\n]{0,70}%[^;\n]{0,25}", re.I),
    "minimum_credit_score": re.compile(r"(?:minimum\s+)?(?:CIBIL|credit score)[^;\n]{0,80}", re.I),
    "tenure": re.compile(r"(?:tenure|repay(?:ment)?(?: period)?)\s*(?:of|from|up to|upto|:)?\s*[\d,.]+(?:\s*(?:to|[-–,]|and)\s*[\d,.]+)*\s*(?:days?|weeks?|months?|years?)", re.I),
}


def field_spans(text: str) -> list[tuple[str, str]]:
    return [(field, match.group(0)) for field, pattern in FIELD_PATTERNS.items() for match in pattern.finditer(text)]


def _observation(capture: Capture, product_id: str, field: str, raw: str, locator: str, value: Value | None, *, state: str = "present", context: str = "offer", confidence: float = .9, conditions: tuple[str, ...] = ()) -> Observation:
    identity = "|".join((capture.run_id, product_id, capture.source_id, field, locator, raw, EXTRACTOR_VERSION))
    return Observation(
        observation_id=hashlib.sha256(identity.encode()).hexdigest(), run_id=capture.run_id,
        product_id=product_id, source_id=capture.source_id, capture_id=capture.capture_id,
        field=field, state=state, value=value, raw_text=raw, locator=locator, context=context,
        extracted_at=capture.retrieved_at, extractor_version=EXTRACTOR_VERSION, confidence=confidence,
        conditions=conditions,
    )


def _strip_label(field: str, text: str) -> str:
    patterns = {
        "loan_amount": r"^(?:(?:instant|personal|business)\s+)*(?:loan(?: amount)?|borrow|loans?)\s*",
        "interest_rate": r"^(?:interest(?: rate)?|rate of interest)\s*(?:of|:|from|starting from)?\s*",
        "minimum_credit_score": r"^(?:minimum\s+)?(?:CIBIL|credit score)\s*(?:of|:)?\s*",
        "tenure": r"^(?:tenure|repay(?:ment)?(?: period)?)\s*(?:of|from|:)?\s*",
    }
    return re.sub(patterns[field], "", text, flags=re.I).strip()


def extract_product(record: dict, capture: Capture) -> list[Observation]:
    product_id = str(record.get("id", ""))
    content = record.get("content") if isinstance(record.get("content"), dict) else {}
    blocks: list[tuple[str, str]] = []
    if isinstance(content.get("headline"), str):
        blocks.append(("/content/headline", content["headline"]))
    for key in ("keyBenefits", "requiredDocuments"):
        if isinstance(content.get(key), list):
            blocks.extend((f"/content/{key}/{index}", item) for index, item in enumerate(content[key]) if isinstance(item, str))
    text_all = " ".join(text for _, text in blocks)
    contaminated = str(record.get("category")) in {"Personal Loan", "Business Loan", "Loan Against Property"} and bool(re.search(r"savings account|fixed deposit|demat|credit card", text_all, re.I))
    facts: list[Observation] = []
    if contaminated:
        facts.append(_observation(capture, product_id, "category_content", text_all, "/content", Value(kind="text", text=text_all), state="ambiguous", context="unknown", confidence=1))
    for locator, block in blocks:
        for field, span in field_spans(block):
            if contaminated and field in {"loan_amount", "interest_rate", "apr"}:
                continue
            raw_value = _strip_label(field, span)
            value = normalize_currency(raw_value) if field == "loan_amount" else normalize_rate(raw_value) if field == "interest_rate" else normalize_tenure(raw_value) if field == "tenure" else normalize_requirement(field, span)
            if value is not None:
                facts.append(_observation(capture, product_id, field, span, locator, value))
        if re.search(r"no hidden charges", block, re.I):
            facts.append(_observation(capture, product_id, "marketing_claim", block, locator, Value(kind="text", text=block), context="marketing", confidence=.8))
        if locator.startswith("/content/requiredDocuments"):
            facts.append(_observation(capture, product_id, "documents_raw", block, locator, Value(kind="text", text=block), confidence=.8))
    return facts
