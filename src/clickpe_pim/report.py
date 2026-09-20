from __future__ import annotations

import json
from pathlib import Path

from clickpe_pim.queries import load_overview, load_queue


def _metric(value) -> str:
    return "not measured" if value is None else str(value)


def build_report(db_path: Path, evaluation: dict, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    overview = load_overview(db_path, include_synthetic=True)
    queue = load_queue(db_path, {}, include_synthetic=True)
    metrics = {**overview, "evaluation": evaluation}
    metrics_path = output_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    evidence = {str(row["comparison_id"]): {"product_id": row.get("product_id"), "field": row.get("field")} for _, row in queue.iterrows()}
    (output_dir / "evidence-index.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    labels = evaluation.get("labels", {})
    flags = evaluation.get("flags", {})
    lines = [
        "# ClickPe Product Intelligence Monitor — analytical report", "",
        "## Business question", "",
        "This report asks whether public ClickPe loan information is complete, internally consistent, current, and aligned with reviewed applicable provider sources. Review items are not findings of wrongdoing.", "",
        "## Catalogue and monitored cohort", "",
        f"The finalized run contains {overview.get('inventory_products', 0)} inventory records and {overview.get('cohort_products', 0)} monitored products.", "",
        "## Method and evidence", "",
        "The pipeline stores immutable source bytes, hashes, exact excerpts, locators, normalized values, mapping rationale, and comparison decisions. Unknown, unsupported, ambiguous, and absent states remain distinct.", "",
        "## Coverage and review queue", "",
        f"Applicable official-source coverage: {_metric(overview.get('coverage_ratio'))}. Open review items: {overview.get('review_items', 0)}.", "",
        "## Evaluation", "",
        f"Held split: {labels.get('split', 'not measured')}. Numeric correctness: {labels.get('present_numeric_correct', 0)}/{labels.get('present_numeric_total', 0)} ({_metric(labels.get('present_numeric_accuracy'))}).", "",
        f"Reviewed useful-flag precision: {flags.get('useful_flags', 0)}/{flags.get('reviewed_flags', 0)} ({_metric(flags.get('precision'))}). Unreviewed flags: {flags.get('unreviewed_flags', 0)}.", "",
        "## History", "",
        "One baseline only" if overview.get("runs", 0) < 2 else f"{overview.get('recent_changes', 0)} stored change events are recorded. The acceptance ledger determines whether the elapsed-time history gate is satisfied.", "",
        "## Limitations and actions", "",
        "Candidate mappings do not establish programme applicability. Synthetic replay results validate software behavior only and are excluded from real monitoring totals by default. Competitor coverage is outside this release.", "",
    ]
    path = output_dir / "report.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
