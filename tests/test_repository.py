from clickpe_pim.contracts import Product
from clickpe_pim.storage.repository import Repository


def test_failed_run_does_not_replace_good_value(tmp_path, make_capture, make_observation):
    repo = Repository(tmp_path / "monitor.sqlite")
    repo.initialize()
    stamp = make_capture().retrieved_at
    repo.upsert_product(Product(product_id="p1", name="Synthetic loan", category="personal_loan", clickpe_url="https://example.org/products", active_status="active"), stamp)
    repo.upsert_source("s1", "https://example.org/products", "clickpe_catalogue", {})
    for run_id, state in [("r1", "complete"), ("r2", "failed")]:
        repo.begin_run(run_id, stamp, {"synthetic": True})
        cap = make_capture(run_id=run_id, capture_id=run_id)
        repo.save_capture(cap)
        repo.save_observations([make_observation(run_id=run_id, capture_id=run_id, observation_id=run_id)])
        repo.finish_run(run_id, state, catalogue_complete=state == "complete")
    assert repo.latest_good("p1", "s1", "loan_amount").run_id == "r1"

