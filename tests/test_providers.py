from clickpe_pim.providers.extract import extract_provider


def test_calculator_interest_is_excluded(make_capture):
    html = "<main><h2>Personal Loan</h2><p>APR 14–48% p.a.</p><h2>EMI calculator</h2><p>Interest 10–36%</p></main>"
    recipe = {"version": "1", "scope_heading": "Personal Loan", "expected_heading": "Personal Loan", "exclude_headings": ["EMI calculator"], "fields": {"apr": {"label_pattern": "APR", "value_pattern": r"14–48% p\.a\.", "normalizer": "apr"}}}
    facts = extract_provider(html, make_capture(), "incred_pl", recipe)
    assert any(f.field == "apr" and f.state == "present" for f in facts)
    assert not any(f.field == "interest_rate" and f.state == "present" for f in facts)


def test_changed_heading_is_unsupported(make_capture):
    facts = extract_provider("<h2>Different</h2>", make_capture(), "p1", {"expected_heading": "Expected", "fields": {"apr": {}}})
    assert facts[0].state == "unsupported"

