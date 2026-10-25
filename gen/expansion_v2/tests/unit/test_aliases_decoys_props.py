"""Property tests for recallstorm.aliases.decoys."""
from recallstorm.aliases.decoys import classify_red_mention, decoy_examples


def test_decoy_examples_never_classified_as_red3():
    for ex in decoy_examples():
        assert classify_red_mention(ex) != "RED3"
