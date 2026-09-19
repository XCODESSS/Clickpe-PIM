from clickpe_pim.catalogue.extract import extract_product


def test_headline_upper_bound_is_not_exact_amount(make_capture):
    row = {"id": "prefr_pl", "name": "Prefr Personal Loan", "category": "Personal Loan", "content": {"headline": "Instant Personal Loan up to ₹5 Lakhs", "keyBenefits": []}}
    facts = extract_product(row, make_capture())
    amount = next(f for f in facts if f.field == "loan_amount" and f.state == "present")
    assert str(amount.value.upper) == "500000"
    assert amount.value.lower is None
    assert amount.locator.endswith("/content/headline")


def test_deposit_copy_does_not_become_loan_interest(make_capture):
    row = {"id": "vivifi_pl", "name": "Vivifi Personal Loan", "category": "Personal Loan", "content": {"headline": "Zero Balance Digital Savings Account", "keyBenefits": ["Earn up to 4% interest p.a."]}}
    facts = extract_product(row, make_capture())
    assert not any(f.field == "interest_rate" and f.state == "present" for f in facts)
    assert any(f.field == "category_content" and f.state == "ambiguous" for f in facts)


def test_no_hidden_charges_is_only_marketing(make_capture):
    row = {"id": "p1", "name": "Loan", "category": "Personal Loan", "content": {"headline": "No hidden charges", "keyBenefits": []}}
    facts = extract_product(row, make_capture())
    assert any(f.field == "marketing_claim" for f in facts)
    assert not any(f.field == "processing_fee" for f in facts)

