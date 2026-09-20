from pathlib import Path

from clickpe_pim.pipeline import run_monitor


def test_replay_is_deterministic_and_network_free(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("replay attempted network")

    monkeypatch.setattr("requests.sessions.Session.request", forbidden)
    manifest = Path("tests/fixtures/catalogue/replay-manifest.json")
    first = run_monitor(Path("config.yaml"), mode="replay", replay_manifest=manifest, output_root=tmp_path, run_id="fixture_r1")
    second = run_monitor(Path("config.yaml"), mode="replay", replay_manifest=manifest, output_root=tmp_path, run_id="fixture_r1")
    assert first == second
    assert first.status == "complete"
    assert first.products_discovered == 2
    assert first.products_monitored == 2
    assert first.comparisons == 2
    assert (tmp_path / "data/processed/products.parquet").exists()

    frozen_manifest = tmp_path / "data/snapshots/fixture_r1/manifest.json"
    reproduced = run_monitor(
        Path("config.yaml"), mode="replay", replay_manifest=frozen_manifest,
        output_root=tmp_path / "reproduced", run_id="fixture_r1_reproduced",
    )
    assert reproduced.products_discovered == first.products_discovered
    assert reproduced.products_monitored == first.products_monitored
    assert reproduced.observations == first.observations
    assert reproduced.comparisons == first.comparisons


def test_replay_rejects_tampered_hash(tmp_path):
    import json

    source = Path("tests/fixtures/catalogue/replay-manifest.json")
    payload = json.loads(source.read_text(encoding="utf-8"))
    payload["captures"][0]["sha256"] = "0" * 64
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    # Rebase fixture paths because the manifest contract resolves them beside the manifest.
    payload["captures"][0]["fixture"] = str(Path("tests/fixtures/catalogue/feed.json").resolve())
    payload["captures"][1]["fixture"] = str(Path("tests/fixtures/provider/match.html").resolve())
    payload["captures"][2]["fixture"] = str(Path("tests/fixtures/provider/difference.html").resolve())
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    import pytest
    with pytest.raises(ValueError, match="hash mismatch"):
        run_monitor(Path("config.yaml"), mode="replay", replay_manifest=manifest, output_root=tmp_path / "out", run_id="bad")
