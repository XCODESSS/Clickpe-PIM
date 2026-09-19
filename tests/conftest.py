from datetime import datetime, timezone
from pathlib import Path

import pytest

from clickpe_pim.contracts import Capture, Observation, Value
from clickpe_pim.settings import load_settings


def pytest_configure():
    Path(".artifacts").mkdir(exist_ok=True)


@pytest.fixture
def make_capture():
    def factory(**overrides):
        data = {
            "capture_id": "c1", "run_id": "r1", "source_id": "s1",
            "source_type": "clickpe_catalogue", "url": "https://example.org/products",
            "final_url": "https://example.org/products", "retrieved_at": datetime(2026, 9, 19, tzinfo=timezone.utc),
            "status": "ok", "http_status": 200, "sha256": "a" * 64,
            "raw_path": "r1/s1.json", "media_type": "application/json", "error_code": None,
        }
        data.update(overrides)
        return Capture(**data)
    return factory


@pytest.fixture
def make_observation():
    def factory(**overrides):
        data = {
            "observation_id": "o1", "run_id": "r1", "product_id": "p1", "source_id": "s1",
            "capture_id": "c1", "field": "loan_amount", "state": "present",
            "value": Value(kind="money", upper="500000", unit="INR", qualifier="up_to"),
            "raw_text": "up to INR 500000", "locator": "/response/0/content/headline",
            "context": "offer", "extracted_at": datetime(2026, 9, 19, tzinfo=timezone.utc),
            "extractor_version": "1", "confidence": 1, "conditions": (),
        }
        data.update(overrides)
        return Observation(**data)
    return factory


@pytest.fixture
def settings():
    from pathlib import Path
    return load_settings(Path("config.yaml"))
