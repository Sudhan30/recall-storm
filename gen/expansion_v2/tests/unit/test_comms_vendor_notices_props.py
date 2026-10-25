"""Property tests for recallstorm.comms.vendor_notices."""
import random
from recallstorm.comms.vendor_notices import escalate_unresponsive_vendor_contacts


def test_vendor_escalation_threshold_props():
    rng = random.Random(42)
    for _ in range(25):
        h = rng.uniform(0.0, 6.0)
        assert escalate_unresponsive_vendor_contacts("V1", h)["escalated"] == (h > 2.0)
