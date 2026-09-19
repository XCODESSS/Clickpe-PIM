import json
from pathlib import Path

from clickpe_pim.pipeline import run_monitor
from clickpe_pim.report import build_report


def test_report_marks_unmeasured_results(tmp_path):
    run_monitor(Path("config.yaml"), mode="replay", replay_manifest=Path("tests/fixtures/catalogue/replay-manifest.json"), output_root=tmp_path, run_id="report_fixture")
    output = build_report(tmp_path / "data/db/monitor.sqlite", {"labels": {}, "flags": {}}, tmp_path / "report")
    text = output.read_text(encoding="utf-8")
    assert "not measured" in text
    assert "Synthetic replay" in text
    assert json.loads((tmp_path / "report/metrics.json").read_text(encoding="utf-8"))["inventory_products"] == 2

