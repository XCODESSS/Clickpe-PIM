from __future__ import annotations

import hashlib

from clickpe_pim.contracts import Comparison, Observation, Product


def check_product(product: Product, observations: list[Observation]) -> list[Comparison]:
    output = []
    for item in observations:
        if item.product_id == product.product_id and item.field in {"category_content", "provider_identity"} and item.state == "ambiguous":
            identity = f"{item.run_id}|{product.product_id}|{item.field}|{item.observation_id}|single"
            output.append(Comparison(
                comparison_id=hashlib.sha256(identity.encode()).hexdigest(), run_id=item.run_id,
                product_id=product.product_id, field=item.field, left_id=item.observation_id, right_id=None,
                mapping_id=None, kind="single_source", status="AMBIGUOUS",
                reason="The product category or provider identity requires review.", reason_code="internal_content_check",
                confidence=item.confidence,
            ))
    return output

