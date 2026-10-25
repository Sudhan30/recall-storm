"""Edge case tests for recallstorm.store.signage."""
from contract import Store, StoreFormat, Verdict
from recallstorm.store.signage import sign_language, sign_template, tags_for_store


def test_store_signage_edge():
    st = Store("WM1", StoreFormat.SUPERCENTER, "ME", "Portland", 43.6, -70.2, "D01", "DC1", "America/New_York")
    assert sign_language(st) == "en"
    assert "AVAILABLE" in sign_template(Verdict.KEEP)
    assert tags_for_store(st, [], {}, {}) == []
