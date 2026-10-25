"""Edge case tests for recallstorm.aliases.decoys."""
from recallstorm.aliases.decoys import classify_red_mention, is_dc_red_33, is_red40


def test_decoys_edge():
    assert not is_red40("FD&C RED #3")
    assert not is_dc_red_33("FD&C RED #3")
    assert classify_red_mention("RED 30") == "OTHER"
    assert classify_red_mention("") == "OTHER"
