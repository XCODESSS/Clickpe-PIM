from pathlib import Path

from clickpe_pim.pipeline import run_monitor
from clickpe_pim.queries import (
    load_evidence,
    load_overview,
    load_product,
    load_providers,
    load_queue,
)


def test_queries_use_a_coherent_finalized_run(tmp_path):
    run_monitor(Path("config.yaml"), mode="replay", replay_manifest=Path("tests/fixtures/catalogue/replay-manifest.json"), output_root=tmp_path, run_id="query_fixture")
    db = tmp_path / "data/db/monitor.sqlite"
    assert load_overview(db) == {}
    overview = load_overview(db, include_synthetic=True)
    assert overview["inventory_products"] == 2
    assert overview["review_items"] == 1
    queue = load_queue(db, {}, include_synthetic=True)
    assert len(queue) == 1
    assert queue.iloc[0]["product_id"] == "fixture_difference"
    assert queue.iloc[0]["field"] == "loan_amount"
    evidence = load_evidence(db, queue.iloc[0]["comparison_id"])
    assert len(evidence["evidence"]) == 2
    assert load_product(db, "fixture_difference")["product"]["name"] == "Fixture Difference Loan"
    assert load_providers(db)["products"].sum() == 2
