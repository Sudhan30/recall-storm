"""Property tests for recallstorm.aliases.bundles."""
from recallstorm.aliases.bundles import bundle_match_path


def test_bundle_match_offset_accuracy():
    for i in range(15):
        prefix = "X" * i
        text = f"KIT CONTAINS: Safe_{prefix}: WATER, SALT | Affected: SUGAR, FD&C RED #3, CORN SYRUP"
        res = bundle_match_path(text, ("FD&C Red No. 3",), "RED3")
        assert res is not None
        comp, m = res
        assert comp == "Affected"
        assert text[m.start : m.end] == m.match_text
