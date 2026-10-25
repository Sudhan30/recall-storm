"""Unit tests for recallstorm.aliases.decoys."""
from recallstorm.aliases.decoys import (
    DECOY_PATTERNS,
    classify_red_mention,
    decoy_examples,
    is_dc_red_33,
    is_lake_pigment,
    is_product_name_phrase,
    is_quantity_phrase,
    is_red40,
    near_miss_report,
)


def test_decoy_detection():
    assert len(DECOY_PATTERNS) >= 5
    assert len(decoy_examples()) >= 4
    assert is_red40("SUGAR, FD&C RED #40, WATER", 7) is True
    assert is_dc_red_33("D&C RED #33", 0) is True
    assert is_quantity_phrase("SPICES (3 RED BELL PEPPERS)", 8, 13) is True
    assert is_product_name_phrase("RED 3 BEAN SALAD", 0, 5) is True
    assert is_lake_pigment("FD&C RED #40 LAKE", 0, 12) is True
    assert classify_red_mention("FD&C RED #3") == "RED3"
    assert classify_red_mention("FD&C RED #40") == "RED40"
    assert classify_red_mention("D&C RED #33") == "DC_RED"
    assert classify_red_mention("COLORED WITH CARMINE") == "NATURAL_RED"
    assert classify_red_mention("WATER, SALT") == "NONE"
    nm = near_miss_report("SUGAR, RED 40 LAKE, CARMINE")
    assert len(nm) == 2
