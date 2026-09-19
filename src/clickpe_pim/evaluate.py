from __future__ import annotations

import json
import math
import sqlite3
from pathlib import Path

from clickpe_pim.contracts import Comparison, Observation


def _wilson(correct: int, total: int, z: float = 1.959963984540054) -> list[float] | None:
    if total == 0:
        return None
    proportion = correct / total
    denominator = 1 + z * z / total
    centre = (proportion + z * z / (2 * total)) / denominator
    margin = z * math.sqrt(proportion * (1 - proportion) / total + z * z / (4 * total * total)) / denominator
    return [max(0, centre - margin), min(1, centre + margin)]


def _value_equal(actual: dict | None, expected: dict | None) -> bool:
    if actual is None or expected is None:
        return actual is expected
    keys = {"kind", "lower", "upper", "unit", "period", "basis", "qualifier", "approximate", "options"}
    return all(actual.get(key) == expected.get(key) for key in keys if key in expected)


def evaluate_labels(observations: list[Observation], labels: list[dict], *, split: str) -> dict:
    selected = [label for label in labels if label.get("split") == split]
    by_key: dict[tuple[str, str, str, str], list[Observation]] = {}
    for item in observations:
        by_key.setdefault((item.product_id, item.source_id, item.capture_id, item.field), []).append(item)
    numeric_total = numeric_correct = state_correct = missing_total = missing_correct = abstentions = 0
    per_field: dict[str, dict[str, int]] = {}
    for label in selected:
        key = (label["product_id"], label["source_id"], label["capture_id"], label["field"])
        predictions = by_key.get(key, [])
        state = label["state"]
        field_counts = per_field.setdefault(label["field"], {"correct": 0, "total": 0})
        field_counts["total"] += 1
        state_ok = len(predictions) == 1 and predictions[0].state == state
        state_correct += int(state_ok)
        if state == "absent":
            missing_total += 1
            missing_correct += int(state_ok)
        if state == "present" and label.get("expected") and label["expected"].get("kind") in {"money", "rate", "tenure", "number"}:
            numeric_total += 1
            good = len(predictions) == 1 and predictions[0].state == "present" and _value_equal(predictions[0].value.model_dump(mode="json") if predictions[0].value else None, label["expected"])
            numeric_correct += int(good)
            field_counts["correct"] += int(good)
        else:
            field_counts["correct"] += int(state_ok)
        if not predictions or any(item.state in {"unsupported", "failed"} for item in predictions):
            abstentions += 1
    return {
        "split": split, "labels_total": len(selected), "present_numeric_correct": numeric_correct,
        "present_numeric_total": numeric_total, "present_numeric_accuracy": numeric_correct / numeric_total if numeric_total else None,
        "present_numeric_wilson_95": _wilson(numeric_correct, numeric_total),
        "state_correct": state_correct, "state_total": len(selected), "state_accuracy": state_correct / len(selected) if selected else None,
        "missing_correct": missing_correct, "missing_total": missing_total, "missing_field_recall": missing_correct / missing_total if missing_total else None,
        "abstentions": abstentions, "abstention_rate": abstentions / len(selected) if selected else None,
        "per_field": per_field,
    }


def evaluate_flags(comparisons: list[Comparison], reviews: list[dict]) -> dict:
    useful = {review["comparison_id"] for review in reviews if review.get("disposition") == "confirmed_useful"}
    reviewed = {review["comparison_id"] for review in reviews if review.get("disposition")}
    candidates = {item.comparison_id for item in comparisons if item.status != "MATCH"}
    denominator = len(reviewed & candidates)
    numerator = len(useful & candidates)
    return {"useful_flags": numerator, "reviewed_flags": denominator, "unreviewed_flags": len(candidates - reviewed), "precision": numerator / denominator if denominator else None}


def evaluate_database(db_path: Path, labels_path: Path, split: str) -> dict:
    if not db_path.exists():
        raise ValueError("database does not exist")
    labels = [json.loads(line) for line in labels_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    with sqlite3.connect(db_path) as con:
        row = con.execute("SELECT run_id FROM scrape_runs WHERE status IN ('complete','partial') ORDER BY finished_at DESC LIMIT 1").fetchone()
        observations = [Observation.model_validate_json(item[0]) for item in con.execute("SELECT record_json FROM product_attributes WHERE run_id=?", (row[0],))] if row else []
        comparisons = [Comparison.model_validate_json(item[0]) for item in con.execute("SELECT record_json FROM comparisons WHERE run_id=?", (row[0],))] if row else []
        reviews = [
            dict(zip(("comparison_id", "disposition"), item, strict=True))
            for item in con.execute(
                "SELECT c.comparison_id,e.disposition FROM review_events e "
                "JOIN conflicts c ON c.fingerprint=e.fingerprint"
            )
        ] if row else []
    return {"labels": evaluate_labels(observations, labels, split=split), "flags": evaluate_flags(comparisons, reviews)}
