from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
from pathlib import Path

import pandas as pd

from clickpe_pim.storage.repository import Repository


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_rows(con: sqlite3.Connection, sql: str, params: tuple = ()) -> list[dict]:
    return [json.loads(row[0]) for row in con.execute(sql, params)]


def _write_parquet(path: Path, rows: list[dict], columns: list[str] | None = None) -> None:
    frame = pd.json_normalize(rows, sep="_") if rows else pd.DataFrame(columns=columns or ["run_id"])
    frame.to_parquet(path, index=False)


def _wide_products(products: list[dict], observations: list[dict]) -> list[dict]:
    fields = {"loan_amount": "loan_amount", "interest_rate": "interest_rate", "apr": "APR", "tenure": "tenure_days"}
    by_key: dict[tuple[str, str], list[dict]] = {}
    for item in observations:
        if item.get("state") == "present" and item.get("field") in fields:
            by_key.setdefault((item["product_id"], item["field"]), []).append(item)
    output = []
    for product in products:
        row = dict(product)
        for field, prefix in fields.items():
            items = by_key.get((product["product_id"], field), [])
            state_key = f"{prefix}_state"
            if len(items) == 1:
                value = items[0].get("value") or {}
                row[f"min_{prefix}"] = value.get("lower")
                row[f"max_{prefix}"] = value.get("upper")
                row[f"{prefix}_unit"] = value.get("unit")
                row[f"{prefix}_period"] = value.get("period")
                row[f"{prefix}_basis"] = value.get("basis")
                row[f"{prefix}_evidence_id"] = items[0].get("observation_id")
                row[state_key] = "present"
            elif len(items) > 1:
                row[state_key] = "ambiguous"
                row[f"{prefix}_evidence_id"] = ",".join(x["observation_id"] for x in items)
            else:
                row[state_key] = "unknown"
        output.append(row)
    return output


def export_run(repo: Repository, run_id: str, output_root: Path) -> dict[str, str]:
    target = output_root
    target.mkdir(parents=True, exist_ok=True)
    with repo.connect() as con:
        products = _read_rows(con, "SELECT record_json FROM product_snapshots WHERE run_id=? ORDER BY product_id", (run_id,))
        observations = _read_rows(con, "SELECT record_json FROM product_attributes WHERE run_id=? ORDER BY observation_id", (run_id,))
        comparisons = _read_rows(con, "SELECT record_json FROM comparisons WHERE run_id=? ORDER BY comparison_id", (run_id,))
        changes = _read_rows(con, "SELECT record_json FROM changes WHERE product_id IN (SELECT product_id FROM product_snapshots WHERE run_id=?) ORDER BY change_id", (run_id,))
        source_rows = [dict(row) for row in con.execute("SELECT source_id,url,source_type,record_json FROM sources ORDER BY source_id")]
    wide = _wide_products(products, observations)
    pd.DataFrame(products).to_csv(target / "clickpe_products.csv", index=False, encoding="utf-8", lineterminator="\n")
    _write_parquet(target / "products.parquet", wide, ["product_id", "name", "category"])
    _write_parquet(target / "observations.parquet", observations, ["observation_id", "run_id", "product_id", "field", "state"])
    _write_parquet(target / "comparisons.parquet", comparisons, ["comparison_id", "run_id", "product_id", "field", "status"])
    _write_parquet(target / "changes.parquet", changes, ["change_id", "product_id", "type"])
    _write_parquet(target / "clickpe_normalized.parquet", [x for x in observations if x.get("source_id") == "clickpe_catalogue"])
    _write_parquet(target / "provider_normalized.parquet", [x for x in observations if x.get("source_id") != "clickpe_catalogue"])
    pd.DataFrame(source_rows, columns=["source_id", "url", "source_type", "record_json"]).to_csv(target / "source_mapping.csv", index=False, encoding="utf-8", lineterminator="\n")
    metrics = {
        "run_id": run_id,
        "inventory_products": len(products),
        "observations": len(observations),
        "comparisons": len(comparisons),
        "review_items": sum(item.get("status") != "MATCH" for item in comparisons),
        "changes": len(changes),
    }
    (target / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    evidence = {item["observation_id"]: {"capture_id": item["capture_id"], "locator": item["locator"], "raw_text": item["raw_text"]} for item in observations}
    (target / "evidence-index.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {path.name: _hash(path) for path in sorted(target.iterdir()) if path.is_file()}


def publish_latest(snapshot: Path, processed: Path, hashes: dict[str, str]) -> None:
    processed.mkdir(parents=True, exist_ok=True)
    for source in snapshot.iterdir():
        if not source.is_file() or source.name in {"result.json", "manifest.json"}:
            continue
        temporary = processed / f".{source.name}.tmp"
        shutil.copyfile(source, temporary)
        os.replace(temporary, processed / source.name)
    receipt = {"snapshot": str(snapshot), "artifacts": hashes}
    temporary = processed / ".latest.json.tmp"
    temporary.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, processed / "latest.json")

