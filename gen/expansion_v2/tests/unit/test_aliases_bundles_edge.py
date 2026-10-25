"""Edge case tests for recallstorm.aliases.bundles."""
from recallstorm.aliases.bundles import bundle_match_path, is_bundle, split_bundle


def test_bundles_edge():
    assert split_bundle("") == []
    assert not is_bundle("SUGAR, WATER", "candy")
    assert bundle_match_path("ITEM A: WATER | ITEM B: SALT", ("Red 3",), "RED3") is None
