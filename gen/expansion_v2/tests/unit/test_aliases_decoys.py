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


def test_decoys():
    assert len(DECOY_PATTERNS) >= 5
    assert is_red40("WATER, FD&C RED #40, SUGAR")
    assert is_dc_red_33("D&C RED NO. 33")
    assert is_quantity_phrase("3 PEPPER JALAPENO BEEF JERKY")
    assert is_product_name_phrase("SPICES (RED PEPPER)")
    assert is_lake_pigment("RED 40 LAKE")
    assert len(decoy_examples()) == 6
    assert classify_red_mention("FD&C RED #3") == "RED3"
    assert classify_red_mention("FD&C RED #40") == "RED40"
    assert classify_red_mention("D&C RED 33") == "DC_RED"
    assert classify_red_mention("RED PEPPER") == "NATURAL_FOOD"
    rep = near_miss_report("RED 40 LAKE, RED PEPPER")
    assert rep["red40"] and rep["product_phrase"] and rep["lake_pigment"]
