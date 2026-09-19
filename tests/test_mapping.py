from clickpe_pim.providers.entities import suggest_alias


def test_fuzzy_match_is_only_a_suggestion():
    matches = suggest_alias("Muthoot Finance", {"Muthoot FinCorp": "muthoot_fincorp"})
    assert isinstance(matches, list)
    assert matches[0][0] == "muthoot_fincorp"

