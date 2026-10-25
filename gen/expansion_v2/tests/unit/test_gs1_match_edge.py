"""Edge case tests for recallstorm.gs1.match."""
from recallstorm.gs1.match import best_match, match_by_name


def test_gs1_match_edge():
    assert match_by_name("", []) == []
    assert best_match({"gtins": []}, []) is None
