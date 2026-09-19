from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import yaml

from clickpe_pim.catalogue.discover import discover, select_cohort
from clickpe_pim.catalogue.extract import extract_product
from clickpe_pim.collect.http import HttpCollector
from clickpe_pim.collect.policy import check_policy
from clickpe_pim.compare.checks import check_product
from clickpe_pim.compare.engine import compare_pair
from clickpe_pim.compare.scoring import priority
from clickpe_pim.contracts import Capture, Mapping
from clickpe_pim.fields import FIELD_SPECS
from clickpe_pim.providers.extract import extract_provider
from clickpe_pim.settings import load_settings
from clickpe_pim.storage.captures import save_bytes
from clickpe_pim.storage.exports import export_run, publish_latest
from clickpe_pim.storage.repository import Repository


@dataclass(frozen=True)
class RunResult:
    run_id: str
    status: str
    products_discovered: int
    products_monitored: int
    observations: int
    comparisons: int
    changes: int
    errors: tuple[str, ...]


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _file_sha(path: Path) -> str:
    return _sha(path.read_bytes())


def _git_state() -> tuple[str | None, bool | None]:
    try:
        revision = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True).stdout.strip())
        return revision, dirty
    except (OSError, subprocess.CalledProcessError):
        return None, None


def _capture_from_bytes(repo: Repository, raw_root: Path, run_id: str, spec: dict, payload: bytes, at: datetime) -> Capture:
    expected = spec.get("sha256")
    if expected and _sha(payload) != expected:
        raise ValueError(f"capture hash mismatch: {spec['source_id']}")
    suffix = spec.get("suffix") or (".json" if "json" in spec.get("media_type", "") else ".html")
    relative, digest = save_bytes(raw_root, run_id, spec["source_id"], payload, suffix)
    capture = Capture(
        capture_id=spec.get("capture_id", f"{run_id}-{spec['source_id']}"), run_id=run_id,
        source_id=spec["source_id"], source_type=spec["source_type"], url=spec["url"], final_url=spec.get("final_url", spec["url"]),
        retrieved_at=at, status="ok", http_status=200, sha256=digest, raw_path=str(relative).replace("\\", "/"), media_type=spec.get("media_type"),
    )
    repo.upsert_source(spec["source_id"], spec["url"], spec["source_type"], spec)
    repo.save_capture(capture)
    return capture


def _read_replay(manifest_path: Path) -> tuple[dict, list[tuple[dict, bytes]]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    captures = []
    for spec in manifest.get("captures", []):
        fixture = (manifest_path.parent / spec["fixture"]).resolve()
        payload = fixture.read_bytes()
        if _sha(payload) != spec.get("sha256"):
            raise ValueError(f"capture hash mismatch: {spec['source_id']}")
        captures.append((spec, payload))
    return manifest, captures


def run_monitor(config_path: Path, *, mode: Literal["live", "replay"], replay_manifest: Path | None, output_root: Path, run_id: str | None = None) -> RunResult:
    if mode == "replay" and replay_manifest is None:
        raise ValueError("replay mode requires a manifest")
    if mode == "live" and replay_manifest is not None:
        raise ValueError("live mode does not accept a replay manifest")
    settings = load_settings(config_path)
    output_root = output_root.resolve()
    run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    snapshot = output_root / settings.paths.snapshots / run_id
    receipt = snapshot / "result.json"
    if receipt.exists():
        saved = json.loads(receipt.read_text(encoding="utf-8"))
        saved["errors"] = tuple(saved.get("errors", ()))
        return RunResult(**saved)
    repo = Repository(output_root / settings.paths.database)
    repo.initialize()
    started = datetime.now(timezone.utc)
    revision, dirty = _git_state()
    errors: list[str] = []
    manifest_record = {
        "schema_version": 1, "run_id": run_id, "mode": mode, "synthetic": mode == "replay",
        "started_at": started.isoformat(), "config_hash": _file_sha(config_path), "git_revision": revision,
        "git_dirty": dirty, "python": sys.version, "source_parse_status": {}, "captures": [],
    }
    repo.begin_run(run_id, started, manifest_record)
    try:
        if mode == "replay":
            assert replay_manifest is not None
            replay, payloads = _read_replay(replay_manifest)
            capture_time = datetime.fromisoformat(replay["retrieved_at"].replace("Z", "+00:00"))
        else:
            feed_url = "https://clickpe.ai/api/proxy/products?channel=landing"
            collector = HttpCollector(settings)
            robots = collector.fetch("https://clickpe.ai/robots.txt", allowed_hosts={"clickpe.ai"})
            if robots.status != "ok" or not check_policy(feed_url, settings.scraping.user_agent, (robots.body or b"").decode(errors="ignore"), robots.http_status or 0):
                raise RuntimeError("ClickPe robots policy could not be confirmed")
            fetched = collector.fetch(feed_url, allowed_hosts={"clickpe.ai"})
            if fetched.status != "ok" or fetched.body is None:
                raise RuntimeError(f"catalogue collection failed: {fetched.error_code}")
            capture_time = fetched.retrieved_at
            payloads = [({"source_id": "clickpe_catalogue", "source_type": "clickpe_catalogue", "url": feed_url, "media_type": fetched.media_type or "application/json", "suffix": ".json"}, fetched.body)]
            replay = {"product_ids": [], "mappings": [], "provider_recipes": {}}
        captures: dict[str, Capture] = {}
        bodies: dict[str, bytes] = {}
        raw_root = output_root / settings.paths.raw
        for spec, payload in payloads:
            captures[spec["source_id"]] = _capture_from_bytes(repo, raw_root, run_id, spec, payload, capture_time)
            bodies[spec["source_id"]] = payload
            manifest_record["captures"].append({"capture_id": captures[spec["source_id"]].capture_id, "source_id": spec["source_id"], "sha256": captures[spec["source_id"]].sha256, "raw_path": captures[spec["source_id"]].raw_path})
            manifest_record["source_parse_status"][spec["source_id"]] = "captured"
        catalogue_capture = captures["clickpe_catalogue"]
        feed = json.loads(bodies["clickpe_catalogue"])
        discovery = discover(feed, catalogue_capture.url)
        if not discovery.complete:
            errors.extend(discovery.reasons)
        rows = feed["response"]
        by_id = {item["id"]: item for item in rows if isinstance(item, dict) and "id" in item}
        cohort_ids = replay.get("product_ids") or []
        if not cohort_ids:
            cohort_cfg = yaml.safe_load((config_path.parent / "config/cohort.yaml").read_text(encoding="utf-8"))
            cohort_ids = cohort_cfg.get("product_ids") or select_cohort(discovery.products, rows, cohort_cfg["target"], cohort_cfg["seed_ids"])
        cohort = [product for product in discovery.products if product.product_id in set(cohort_ids)]
        observations = []
        for product in discovery.products:
            repo.upsert_product(product, capture_time)
            repo.save_product_snapshot(run_id, product)
            if product.product_id in set(cohort_ids):
                observations.extend(extract_product(by_id[product.product_id], catalogue_capture))
        mappings = [Mapping.model_validate(item) for item in replay.get("mappings", [])]
        provider_recipes = replay.get("provider_recipes", {})
        for mapping in mappings:
            repo.save_mapping(mapping)
            if mapping.source_id in captures and mapping.source_id in provider_recipes:
                observations.extend(extract_provider(bodies[mapping.source_id].decode("utf-8"), captures[mapping.source_id], mapping.product_id, provider_recipes[mapping.source_id]))
        repo.save_observations(observations)
        comparisons = []
        for mapping in mappings:
            left_items = [o for o in observations if o.product_id == mapping.product_id and o.source_id == "clickpe_catalogue"]
            right_items = [o for o in observations if o.product_id == mapping.product_id and o.source_id == mapping.source_id]
            for left in left_items:
                for right in right_items:
                    if left.field == right.field:
                        comparisons.append(compare_pair(left, right, mapping, kind="external", settings=settings))
        for product in cohort:
            comparisons.extend(check_product(product, [item for item in observations if item.product_id == product.product_id]))
        repo.save_comparisons(comparisons)
        for comparison in comparisons:
            if comparison.status != "MATCH":
                importance = FIELD_SPECS[comparison.field].importance
                severity = "critical" if comparison.field == "provider_identity" else "high" if importance >= .8 else "medium"
                repo.save_conflict(comparison, priority=priority(severity, importance, comparison.confidence, 0), severity=severity, at=capture_time)
        manifest_record["source_parse_status"] = {source_id: "ok" for source_id in captures}
        manifest_record["cohort_ids"] = cohort_ids
        pending = snapshot.with_name(snapshot.name + ".pending")
        if pending.exists():
            shutil.rmtree(pending)
        hashes = export_run(repo, run_id, pending)
        manifest_record["artifact_hashes"] = hashes
        manifest_record["finished_at"] = datetime.now(timezone.utc).isoformat()
        (pending / "manifest.json").write_text(json.dumps(manifest_record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        pending.rename(snapshot)
        status = "complete" if discovery.complete and not errors else "partial"
        repo.update_manifest(run_id, manifest_record)
        repo.finish_run(run_id, status, discovery.complete)
        result = RunResult(run_id, status, len(discovery.products), len(cohort), len(observations), len(comparisons), 0, tuple(errors))
        receipt.write_text(json.dumps(asdict(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        publish_latest(snapshot, output_root / "data/processed", hashes)
        return result
    except Exception:
        try:
            repo.finish_run(run_id, "failed", False)
        except Exception:
            pass
        raise
