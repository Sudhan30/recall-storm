"""Property tests for recallstorm.recall_lots.fda_notice_parser."""
from recallstorm.recall_lots.fda_notice_parser import detect_undeclared_allergen_type


def test_detect_all_big9_allergens():
    for alg in ("peanut", "milk", "egg", "wheat", "soy", "sesame"):
        assert detect_undeclared_allergen_type(f"Product has undeclared {alg} protein") == alg.upper()
