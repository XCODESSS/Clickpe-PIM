import json
import zipfile
from pathlib import Path

import pytest

from clickpe_pim.pipeline import run_monitor
from scripts.backup import create_backup
from scripts.restore import restore_backup


def test_backup_restore_round_trip(tmp_path):
    root = tmp_path / "source"
    run_monitor(Path("config.yaml"), mode="replay", replay_manifest=Path("tests/fixtures/catalogue/replay-manifest.json"), output_root=root, run_id="backup_fixture")
    archive = create_backup(root / "data/db/monitor.sqlite", root / "data", root / "state.zip")
    restored = restore_backup(archive, tmp_path / "restored")
    assert (restored / "database/monitor.sqlite").exists()
    assert (restored / "data/raw/backup_fixture/clickpe_catalogue.json").exists()


def test_restore_rejects_traversal(tmp_path):
    archive = tmp_path / "bad.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("../escape", b"bad")
        bundle.writestr("backup-manifest.json", json.dumps({"_schema_version": 1, "../escape": "x"}))
    with pytest.raises(ValueError, match="unsafe"):
        restore_backup(archive, tmp_path / "destination")

