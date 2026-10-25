"""Property tests for recallstorm.governance.whistleblower_intake."""
from recallstorm.governance.whistleblower_intake import protect_reporter_identity_via_zero_knowledge


def test_zero_knowledge_token_determinism():
    for i in range(15):
        p = f"pass_{i}"
        assert protect_reporter_identity_via_zero_knowledge(p) == protect_reporter_identity_via_zero_knowledge(p)
