"""Edge tests for recallstorm.gs1.match."""
from contract import Sku
from recallstorm.gs1.match import (
    best_match,
    match_by_name,
    match_score,
)


def test_match_edge():
    s1 = Sku("S1", "00012345678905", "Candy", "B", "candy", "SUGAR", True, False, 12, 1.0, 5.0)
    assert match_by_name("", [s1]) == []
    assert best_match({"title": "Nothing"}, []) is None
    assert match_score({}, s1) == 0.0
