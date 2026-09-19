from __future__ import annotations

from dataclasses import dataclass

from clickpe_pim.contracts import Product

CATEGORY_MAP = {
    "Personal Loan": "personal_loan", "Business Loan": "business_loan",
    "Loan Against Property": "loan_against_property", "Creditline": "credit_line", "Credit Line": "credit_line",
}


@dataclass(frozen=True)
class DiscoveryResult:
    products: list[Product]
    complete: bool
    excluded: list[dict]
    reasons: tuple[str, ...]


def discover(payload: dict, catalogue_url: str) -> DiscoveryResult:
    reasons: list[str] = []
    rows = payload.get("response") if payload.get("status") == "Success" else None
    if not isinstance(rows, list) or not rows:
        return DiscoveryResult([], False, [], ("invalid_or_empty_envelope",))
    seen: set[str] = set()
    products: list[Product] = []
    excluded: list[dict] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or not all(isinstance(row.get(k), str) and row[k].strip() for k in ("id", "name", "category")):
            reasons.append(f"malformed_row:{index}")
            excluded.append({"index": index, "reason": "malformed"})
            continue
        if row["id"] in seen:
            reasons.append(f"duplicate_id:{row['id']}")
            continue
        seen.add(row["id"])
        category = CATEGORY_MAP.get(row["category"])
        if category is None:
            excluded.append({"id": row["id"], "category": row["category"], "reason": "out_of_scope"})
            continue
        products.append(Product(
            product_id=row["id"], name=row["name"], category=category,
            provider_name_raw=row.get("lender") if isinstance(row.get("lender"), str) else None,
            clickpe_url=catalogue_url,
            active_status={"ACTIVE": "active", "INACTIVE": "inactive"}.get(str(row.get("status", "")).upper(), "unknown"),
        ))
    return DiscoveryResult(products, not reasons and bool(products), excluded, tuple(reasons))


def select_cohort(products: list[Product], native_records: list[dict], target: int, seed_ids: list[str]) -> list[str]:
    by_id = {p.product_id: p for p in products if p.active_status == "active"}
    missing = [item for item in seed_ids if item not in by_id]
    if missing:
        raise ValueError(f"seed products not found or inactive: {', '.join(missing)}")
    ranking = {str(row.get("id")): (row.get("ranking") if isinstance(row.get("ranking"), (int, float)) else 10**9) for row in native_records}
    selected = list(dict.fromkeys(seed_ids))
    for category in ("business_loan", "loan_against_property", "credit_line"):
        for product in sorted((p for p in by_id.values() if p.category == category), key=lambda p: (ranking.get(p.product_id, 10**9), p.product_id)):
            if product.product_id not in selected:
                selected.append(product.product_id)
    for product in sorted(by_id.values(), key=lambda p: (ranking.get(p.product_id, 10**9), p.product_id)):
        if len(selected) >= target:
            break
        if product.product_id not in selected:
            selected.append(product.product_id)
    return selected[:target]

