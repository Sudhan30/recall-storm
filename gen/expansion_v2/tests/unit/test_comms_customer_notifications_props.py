"""Property tests for recallstorm.comms.customer_notifications."""
import random
from recallstorm.comms.customer_notifications import track_email_bounce_and_open_metrics


def test_email_open_rate_bounds():
    rng = random.Random(42)
    for _ in range(25):
        sent = rng.randint(10, 200)
        bounced = rng.randint(0, sent - 1)
        opened = rng.randint(0, sent - bounced)
        res = track_email_bounce_and_open_metrics(sent, bounced, opened)
        assert 0.0 <= res["open_rate"] <= 1.0
