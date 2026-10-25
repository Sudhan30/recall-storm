"""Property tests for recallstorm.vendor.onboarding_gates."""
from recallstorm.rules.red3 import red3_aliases
from recallstorm.vendor.onboarding_gates import screen_new_item_setup_for_banned_additives


def test_all_red3_aliases_blocked_at_onboarding():
    for al in red3_aliases():
        res = screen_new_item_setup_for_banned_additives(f"SUGAR, {al}, CORN SYRUP")
        assert res["blocked"] is True
