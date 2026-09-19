from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime

from clickpe_pim.contracts import Change, Observation, Product


@dataclass(frozen=True)
class Snapshot:
    run_id: str
    at: datetime
    products: dict[str, Product]
    observations: list[Observation]
    healthy_sources: set[str]
    catalogue_complete: bool
    synthetic: bool
    extractor_version: str
    mapping_hash: str
    config_hash: str = ""
    source_statuses: dict[str, str] = field(default_factory=dict)
    cohort_ids: frozenset[str] = frozenset()


def _semantic(item: Observation) -> str:
    return json.dumps(item.value.model_dump(mode="json") if item.value else None, sort_keys=True, separators=(",", ":"), default=str)


def _change(current: Snapshot, product_id: str, source_id: str | None, field_name: str | None, kind: str, previous_id: str | None, current_id: str | None) -> Change:
    raw = f"{current.run_id}|{product_id}|{source_id}|{field_name}|{kind}|{previous_id}|{current_id}"
    return Change(change_id=hashlib.sha256(raw.encode()).hexdigest(), product_id=product_id, source_id=source_id, field=field_name, type=kind, previous_id=previous_id, current_id=current_id, detected_at=current.at, synthetic=current.synthetic)


def detect_changes(previous: Snapshot | None, current: Snapshot, prior_absences: dict[tuple[str, str], list[datetime]]) -> list[Change]:
    if previous is None:
        return []
    if (previous.extractor_version, previous.mapping_hash, previous.config_hash) != (current.extractor_version, current.mapping_hash, current.config_hash):
        return []
    output: list[Change] = []
    old = {(o.product_id, o.source_id, o.field, o.conditions): o for o in previous.observations if o.state == "present"}
    new = {(o.product_id, o.source_id, o.field, o.conditions): o for o in current.observations if o.state == "present"}
    for key in sorted(old.keys() & new.keys()):
        if _semantic(old[key]) != _semantic(new[key]):
            output.append(_change(current, key[0], key[1], key[2], "VALUE_CHANGED", old[key].observation_id, new[key].observation_id))
    for key in sorted(new.keys() - old.keys()):
        if key[1] in current.healthy_sources and key[0] in previous.cohort_ids:
            output.append(_change(current, key[0], key[1], key[2], "FIELD_ADDED", None, new[key].observation_id))
    for key in sorted(old.keys() - new.keys()):
        dates = prior_absences.get((f"{key[1]}:{key[2]}", key[0]), [])
        if key[1] in current.healthy_sources and len(dates) >= 2 and (max(dates) - min(dates)).total_seconds() >= 86400:
            output.append(_change(current, key[0], key[1], key[2], "FIELD_REMOVED", old[key].observation_id, None))
    if previous.catalogue_complete and current.catalogue_complete:
        for product_id in sorted(current.products.keys() - previous.products.keys()):
            if product_id not in current.cohort_ids - previous.cohort_ids:
                output.append(_change(current, product_id, None, None, "PRODUCT_ADDED", None, product_id))
        for product_id in sorted(previous.products.keys() - current.products.keys()):
            dates = prior_absences.get(("product", product_id), [])
            if len(dates) >= 2 and (max(dates) - min(dates)).total_seconds() >= 86400:
                output.append(_change(current, product_id, None, None, "PRODUCT_REMOVED", product_id, None))
    for source_id, status in current.source_statuses.items():
        dates = prior_absences.get(("source", source_id), [])
        if status in {"404", "410"} and len(dates) >= 2 and (max(dates) - min(dates)).total_seconds() >= 86400:
            product_id = next((o.product_id for o in previous.observations if o.source_id == source_id), "unknown")
            output.append(_change(current, product_id, source_id, None, "SOURCE_DISAPPEARED", source_id, None))
    return output

