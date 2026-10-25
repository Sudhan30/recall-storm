"""Property tests for recallstorm.food_safety.allergen_cross_contact."""
from recallstorm.food_safety.allergen_cross_contact import score_cross_contact_severity


def test_shared_surface_increases_severity():
    for alg in ("PEANUT", "MILK", "SOY", "WHEAT"):
        assert score_cross_contact_severity(alg, True) > score_cross_contact_severity(alg, False)
