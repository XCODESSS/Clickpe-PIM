from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd

from clickpe_pim.storage.repository import Repository


def _connect(path: Path) -> sqlite3.Connection | None:
    if not path.exists():
        return None
    con = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def _latest(con: sqlite3.Connection, include_synthetic: bool) -> sqlite3.Row | None:
    condition = "" if include_synthetic else "AND synthetic=0"
    return con.execute(f"SELECT * FROM scrape_runs WHERE status IN ('complete','partial') {condition} ORDER BY finished_at DESC LIMIT 1").fetchone()


def load_overview(db_path: Path, *, include_synthetic: bool = False) -> dict:
    con = _connect(db_path)
    if con is None:
        return {}
    try:
        run = _latest(con, include_synthetic)
        if run is None:
            return {}
        run_id = run["run_id"]
        inventory = con.execute("SELECT COUNT(*) FROM product_snapshots WHERE run_id=?", (run_id,)).fetchone()[0]
        cohort = len(json.loads(run["manifest_json"]).get("cohort_ids", []))
        comparisons = con.execute("SELECT record_json FROM comparisons WHERE run_id=?", (run_id,)).fetchall()
        parsed = [json.loads(row[0]) for row in comparisons]
        sources = json.loads(run["manifest_json"]).get("source_parse_status", {})
        runs = con.execute("SELECT COUNT(*) FROM scrape_runs WHERE status IN ('complete','partial')" + ("" if include_synthetic else " AND synthetic=0")).fetchone()[0]
        approved_products = con.execute("SELECT COUNT(DISTINCT product_id) FROM mappings WHERE json_extract(record_json,'$.review_state')='approved' AND json_extract(record_json,'$.scope')='same_programme'").fetchone()[0]
        changes = con.execute("SELECT COUNT(*) FROM changes WHERE synthetic=?", (1 if include_synthetic else 0,)).fetchone()[0] if not include_synthetic else con.execute("SELECT COUNT(*) FROM changes").fetchone()[0]
        return {
            "run_id": run_id, "status": run["status"], "inventory_products": inventory, "cohort_products": cohort,
            "review_items": sum(item["status"] != "MATCH" for item in parsed),
            "high_priority_items": con.execute("SELECT COUNT(*) FROM conflicts WHERE priority>=70 AND state='open'").fetchone()[0],
            "failed_sources": sum(status != "ok" for status in sources.values()),
            "coverage_numerator": approved_products, "coverage_denominator": cohort,
            "coverage_ratio": approved_products / cohort if cohort else None,
            "recent_changes": changes, "runs": runs, "synthetic": bool(run["synthetic"]),
        }
    finally:
        con.close()


def load_queue(db_path: Path, filters: dict[str, list[str]], *, include_synthetic: bool = False) -> pd.DataFrame:
    columns = [
        "product_id", "field", "status", "priority", "severity", "confidence",
        "kind", "state", "reason", "comparison_id", "fingerprint",
    ]
    con = _connect(db_path)
    if con is None:
        return pd.DataFrame(columns=columns)
    try:
        run = _latest(con, include_synthetic)
        if run is None:
            return pd.DataFrame(columns=columns)
        rows = []
        for row in con.execute(
            "SELECT f.fingerprint,f.comparison_id,f.priority,f.severity,f.state,"
            "c.record_json AS comparison_json FROM conflicts f "
            "JOIN comparisons c ON c.comparison_id=f.comparison_id WHERE c.run_id=?",
            (run["run_id"],),
        ):
            comparison = json.loads(row["comparison_json"])
            item = {key: row[key] for key in ("fingerprint", "comparison_id", "priority", "severity", "state")}
            item.update({key: comparison.get(key) for key in ("product_id", "field", "status", "kind", "reason", "confidence")})
            rows.append(item)
        frame = pd.DataFrame(rows, columns=columns)
        for key, values in filters.items():
            if values and key in frame.columns:
                frame = frame[frame[key].isin(values)]
        return frame.sort_values(["priority", "product_id"], ascending=[False, True]).reset_index(drop=True) if not frame.empty else frame
    finally:
        con.close()


def load_evidence(db_path: Path, comparison_id: str) -> dict:
    con = _connect(db_path)
    if con is None:
        return {}
    try:
        row = con.execute("SELECT record_json FROM comparisons WHERE comparison_id=?", (comparison_id,)).fetchone()
        if not row:
            return {}
        comparison = json.loads(row[0])
        evidence = []
        for observation_id in (comparison.get("left_id"), comparison.get("right_id")):
            if not observation_id:
                continue
            item = con.execute("SELECT a.record_json,c.record_json,s.url,s.source_type FROM product_attributes a JOIN captures c ON c.capture_id=a.capture_id JOIN sources s ON s.source_id=a.source_id WHERE a.observation_id=?", (observation_id,)).fetchone()
            if item:
                observation, capture = json.loads(item[0]), json.loads(item[1])
                evidence.append({"observation": observation, "capture": capture, "url": item[2], "source_type": item[3]})
        mapping = None
        if comparison.get("mapping_id"):
            item = con.execute("SELECT record_json FROM mappings WHERE mapping_id=?", (comparison["mapping_id"],)).fetchone()
            mapping = json.loads(item[0]) if item else None
        return {"comparison": comparison, "evidence": evidence, "mapping": mapping}
    finally:
        con.close()


def record_review(db_path: Path, fingerprint: str, reviewer: str, disposition: str, note: str, at: datetime) -> None:
    Repository(db_path).record_review(fingerprint, reviewer, disposition, note, at)


def load_product(db_path: Path, product_id: str) -> dict:
    con = _connect(db_path)
    if con is None:
        return {}
    try:
        run = _latest(con, True)
        if not run:
            return {}
        product_row = con.execute("SELECT record_json FROM product_snapshots WHERE run_id=? AND product_id=?", (run["run_id"], product_id)).fetchone()
        if not product_row:
            return {}
        observations = [json.loads(row[0]) for row in con.execute("SELECT record_json FROM product_attributes WHERE run_id=? AND product_id=? ORDER BY field,observation_id", (run["run_id"], product_id))]
        mappings = [json.loads(row[0]) for row in con.execute("SELECT record_json FROM mappings WHERE product_id=? ORDER BY mapping_id", (product_id,))]
        return {"product": json.loads(product_row[0]), "observations": observations, "mappings": mappings}
    finally:
        con.close()


def load_changes(db_path: Path, filters: dict[str, list[str]]) -> pd.DataFrame:
    con = _connect(db_path)
    columns = ["change_id", "product_id", "source_id", "field", "type", "previous_id", "current_id", "detected_at", "synthetic"]
    if con is None:
        return pd.DataFrame(columns=columns)
    try:
        frame = pd.DataFrame([json.loads(row[0]) for row in con.execute("SELECT record_json FROM changes ORDER BY detected_at DESC")], columns=columns)
        for key, values in filters.items():
            if values and key in frame.columns:
                frame = frame[frame[key].isin(values)]
        return frame.reset_index(drop=True)
    finally:
        con.close()


def load_providers(db_path: Path) -> pd.DataFrame:
    con = _connect(db_path)
    columns = ["entity_id", "role", "programmes", "products", "approved_sources", "open_reviews"]
    if con is None:
        return pd.DataFrame(columns=columns)
    try:
        mappings = [json.loads(row[0]) for row in con.execute("SELECT record_json FROM mappings")]
        grouped: dict[tuple[str, str], dict] = {}
        for item in mappings:
            key = (item.get("entity_id") or "unresolved", item["role"])
            record = grouped.setdefault(key, {"entity_id": key[0], "role": key[1], "programmes": set(), "products": set(), "approved_sources": 0, "open_reviews": 0})
            if item.get("programme"):
                record["programmes"].add(item["programme"])
            record["products"].add(item["product_id"])
            record["approved_sources"] += int(item["review_state"] == "approved" and item["scope"] == "same_programme")
        rows = [{**item, "programmes": len(item["programmes"]), "products": len(item["products"])} for item in grouped.values()]
        return pd.DataFrame(rows, columns=columns)
    finally:
        con.close()
