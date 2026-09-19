from clickpe_pim.evaluate import evaluate_flags, evaluate_labels


def test_abstention_is_not_ignored(make_observation):
    observation = make_observation()
    labels = [
        {"label_id": "a", "product_id": "p1", "source_id": "s1", "capture_id": "c1", "field": "loan_amount", "state": "present", "expected": {"kind": "money", "upper": "500000", "lower": None, "unit": "INR", "qualifier": "up_to"}, "split": "test"},
        {"label_id": "b", "product_id": "p2", "source_id": "s1", "capture_id": "c1", "field": "loan_amount", "state": "present", "expected": {"kind": "money", "upper": "300000", "lower": None, "unit": "INR", "qualifier": "up_to"}, "split": "test"},
        {"label_id": "c", "product_id": "p3", "source_id": "s1", "capture_id": "c1", "field": "loan_amount", "state": "absent", "expected": None, "split": "test"},
    ]
    output = evaluate_labels([observation], labels, split="test")
    assert output["present_numeric_correct"] == 1
    assert output["present_numeric_total"] == 2
    assert output["present_numeric_accuracy"] == .5
    assert output["labels_total"] == 3
    assert output["abstentions"] == 2
    assert evaluate_flags([], [])["precision"] is None

