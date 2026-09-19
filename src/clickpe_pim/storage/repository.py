from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from importlib.resources import files
from pathlib import Path

from clickpe_pim.contracts import Capture, Change, Comparison, Mapping, Observation, Product


def _json(model_or_dict: object) -> str:
    if hasattr(model_or_dict, "model_dump_json"):
        return model_or_dict.model_dump_json()
    return json.dumps(model_or_dict, sort_keys=True, separators=(",", ":"), default=str)


class Repository:
    def __init__(self, path: Path):
        self.path = Path(path)

    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(self.path)
        con.execute("PRAGMA foreign_keys=ON")
        con.execute("PRAGMA busy_timeout=5000")
        con.row_factory = sqlite3.Row
        return con

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        con = self.connect()
        try:
            with con:
                yield con
        finally:
            con.close()

    def initialize(self) -> None:
        schema = files("clickpe_pim.storage").joinpath("schema.sql").read_text(encoding="utf-8")
        with self.connect() as con:
            con.executescript(schema)

    @staticmethod
    def _insert_immutable(con: sqlite3.Connection, table: str, key: str, key_value: str, columns: dict[str, object]) -> None:
        existing = con.execute(f"SELECT * FROM {table} WHERE {key}=?", (key_value,)).fetchone()
        if existing:
            for name, value in columns.items():
                if str(existing[name]) != str(value):
                    raise ValueError(f"immutable {table} identity collision: {key_value}")
            return
        names = [key, *columns]
        placeholders = ",".join("?" for _ in names)
        con.execute(f"INSERT INTO {table} ({','.join(names)}) VALUES ({placeholders})", [key_value, *columns.values()])

    def begin_run(self, run_id: str, started_at: datetime, manifest: dict) -> None:
        manifest_json = _json(manifest)
        with self.transaction() as con:
            self._insert_immutable(con, "scrape_runs", "run_id", run_id, {
                "started_at": started_at.isoformat(), "finished_at": None, "status": "running",
                "catalogue_complete": 0, "synthetic": int(bool(manifest.get("synthetic"))), "manifest_json": manifest_json,
            })

    def update_manifest(self, run_id: str, manifest: dict) -> None:
        with self.transaction() as con:
            row = con.execute("SELECT status FROM scrape_runs WHERE run_id=?", (run_id,)).fetchone()
            if not row or row[0] != "running":
                raise ValueError("only a running run manifest can be updated")
            con.execute("UPDATE scrape_runs SET manifest_json=? WHERE run_id=?", (_json(manifest), run_id))

    def finish_run(self, run_id: str, status: str, catalogue_complete: bool) -> None:
        if status not in {"complete", "partial", "failed"}:
            raise ValueError("invalid final run status")
        with self.transaction() as con:
            row = con.execute("SELECT started_at,status FROM scrape_runs WHERE run_id=?", (run_id,)).fetchone()
            if not row:
                raise ValueError("unknown run")
            if row[1] != "running" and row[1] != status:
                raise ValueError("finalized run cannot be changed")
            con.execute(
                "UPDATE scrape_runs SET finished_at=?, status=?, catalogue_complete=? WHERE run_id=?",
                (datetime.now().astimezone().isoformat(), status, int(catalogue_complete), run_id),
            )

    def upsert_product(self, product: Product, at: datetime) -> None:
        with self.transaction() as con:
            row = con.execute("SELECT first_seen FROM products WHERE product_id=?", (product.product_id,)).fetchone()
            if row:
                con.execute("UPDATE products SET record_json=?,last_seen=?,active_status=? WHERE product_id=?", (_json(product), at.isoformat(), product.active_status, product.product_id))
            else:
                con.execute("INSERT INTO products VALUES (?,?,?,?,?)", (product.product_id, _json(product), at.isoformat(), at.isoformat(), product.active_status))

    def save_product_snapshot(self, run_id: str, product: Product) -> None:
        with self.transaction() as con:
            con.execute("INSERT OR IGNORE INTO product_snapshots VALUES (?,?,?)", (run_id, product.product_id, _json(product)))

    def upsert_source(self, source_id: str, url: str, source_type: str, record: dict) -> None:
        with self.transaction() as con:
            row = con.execute("SELECT url,source_type,record_json FROM sources WHERE source_id=?", (source_id,)).fetchone()
            serialized = _json(record)
            if row and (row[0] != url or row[1] != source_type):
                raise ValueError(f"source identity collision: {source_id}")
            con.execute(
                "INSERT INTO sources VALUES (?,?,?,?) ON CONFLICT(source_id) DO UPDATE SET record_json=excluded.record_json",
                (source_id, url, source_type, serialized),
            )

    def save_capture(self, capture: Capture) -> None:
        with self.transaction() as con:
            self._insert_immutable(con, "captures", "capture_id", capture.capture_id, {
                "run_id": capture.run_id, "source_id": capture.source_id, "retrieved_at": capture.retrieved_at.isoformat(),
                "status": capture.status, "sha256": capture.sha256, "raw_path": capture.raw_path, "record_json": _json(capture),
            })

    def save_observations(self, items: list[Observation]) -> None:
        with self.transaction() as con:
            for item in items:
                self._insert_immutable(con, "product_attributes", "observation_id", item.observation_id, {
                    "run_id": item.run_id, "product_id": item.product_id, "source_id": item.source_id,
                    "capture_id": item.capture_id, "field": item.field, "state": item.state, "record_json": _json(item),
                })

    def save_mapping(self, mapping: Mapping) -> None:
        with self.transaction() as con:
            self._insert_immutable(con, "mappings", "mapping_id", mapping.mapping_id, {
                "product_id": mapping.product_id, "source_id": mapping.source_id, "record_json": _json(mapping),
            })

    def save_comparisons(self, items: list[Comparison]) -> None:
        with self.transaction() as con:
            for item in items:
                self._insert_immutable(con, "comparisons", "comparison_id", item.comparison_id, {
                    "run_id": item.run_id, "product_id": item.product_id, "record_json": _json(item),
                })

    def save_changes(self, items: list[Change]) -> None:
        with self.transaction() as con:
            for item in items:
                self._insert_immutable(con, "changes", "change_id", item.change_id, {
                    "product_id": item.product_id, "detected_at": item.detected_at.isoformat(), "record_json": _json(item),
                })

    def save_conflict(self, comparison: Comparison, *, priority: int, severity: str, at: datetime) -> str:
        fingerprint = hashlib.sha256(
            f"{comparison.product_id}|{comparison.field}|{comparison.left_id}|{comparison.right_id}|{comparison.reason_code}".encode()
        ).hexdigest()
        record = {"fingerprint": fingerprint, "comparison_id": comparison.comparison_id, "priority": priority, "severity": severity, "state": "open"}
        with self.transaction() as con:
            row = con.execute("SELECT record_json FROM conflicts WHERE fingerprint=?", (fingerprint,)).fetchone()
            if row:
                con.execute("UPDATE conflicts SET last_seen=?,comparison_id=?,priority=?,severity=? WHERE fingerprint=?", (at.isoformat(), comparison.comparison_id, priority, severity, fingerprint))
            else:
                con.execute("INSERT INTO conflicts VALUES (?,?,?,?,?,?,?)", (fingerprint, comparison.comparison_id, priority, severity, "open", at.isoformat(), _json(record)))
        return fingerprint

    def latest_good(self, product_id: str, source_id: str, field: str) -> Observation | None:
        with self.connect() as con:
            row = con.execute(
                """SELECT a.record_json FROM product_attributes a
                JOIN scrape_runs r ON r.run_id=a.run_id JOIN captures c ON c.capture_id=a.capture_id
                WHERE a.product_id=? AND a.source_id=? AND a.field=?
                  AND r.status IN ('complete','partial') AND c.status IN ('ok','not_modified')
                  AND a.state IN ('present','absent') AND (c.sha256 IS NOT NULL OR c.status='not_modified')
                ORDER BY c.retrieved_at DESC, a.observation_id DESC LIMIT 1""",
                (product_id, source_id, field),
            ).fetchone()
        return Observation.model_validate_json(row[0]) if row else None

    def record_review(self, fingerprint: str, reviewer: str, disposition: str, note: str, at: datetime) -> None:
        if not all(x.strip() for x in (reviewer, disposition, note)):
            raise ValueError("reviewer, disposition and note are required")
        event_id = hashlib.sha256(f"{fingerprint}|{reviewer}|{disposition}|{note}|{at.isoformat()}".encode()).hexdigest()
        with self.transaction() as con:
            con.execute("INSERT OR IGNORE INTO review_events VALUES (?,?,?,?,?,?)", (event_id, fingerprint, at.isoformat(), reviewer, disposition, note))
