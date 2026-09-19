from clickpe_pim.catalogue.disclosures import extract_disclosures


def test_scoped_partner_sections(make_capture):
    html = "<h2>Prefr</h2><p>Loan Amount: up to ₹3 lakh; Tenure: 12 months; LSP: Infocredit</p><h2>Other</h2><p>Loan Amount: ₹9 lakh</p>"
    out = extract_disclosures(html, make_capture())
    assert {f.field for f in out["Prefr"]} >= {"loan_amount", "tenure", "provider_identity"}
    amount = next(f for f in out["Prefr"] if f.field == "loan_amount")
    assert str(amount.value.upper) == "300000"

