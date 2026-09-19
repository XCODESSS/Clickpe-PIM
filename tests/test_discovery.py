import pytest

from clickpe_pim.catalogue.discover import discover, select_cohort


def test_native_ids_distinguish_muthoot_variants():
    rows = [{"id": x, "name": x, "category": "Business Loan", "lender": "Muthoot Finance", "status": "ACTIVE"} for x in ["muthoot_emi_bl", "muthoot_daily_bl"]]
    result = discover({"status": "Success", "response": rows}, "https://clickpe.ai/product")
    assert len(result.products) == 2
    assert result.complete


def test_shell_empty_and_duplicate_ids_are_not_complete():
    assert not discover({"status": "Success", "response": []}, "https://clickpe.ai/product").complete
    row = {"id": "p", "name": "Loan", "category": "Personal Loan", "status": "ACTIVE"}
    assert not discover({"status": "Success", "response": [row, row]}, "https://clickpe.ai/product").complete


def test_selection_requires_seed_and_preserves_minority_category():
    rows = [
        {"id": "p1", "name": "A", "category": "Personal Loan", "status": "ACTIVE", "ranking": 1},
        {"id": "b1", "name": "B", "category": "Business Loan", "status": "ACTIVE", "ranking": 5},
    ]
    products = discover({"status": "Success", "response": rows}, "https://clickpe.ai/product").products
    assert select_cohort(products, rows, 2, ["p1"]) == ["p1", "b1"]
    with pytest.raises(ValueError):
        select_cohort(products, rows, 2, ["missing"])

