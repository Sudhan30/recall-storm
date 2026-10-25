"""Property tests for recallstorm.pricing.electronic_shelf_labels."""
import random
from recallstorm.pricing.electronic_shelf_labels import audit_esl_update_latency_sla


def test_esl_latency_sla_props():
    rng = random.Random(42)
    for _ in range(25):
        lat = rng.uniform(1.0, 120.0)
        assert audit_esl_update_latency_sla(lat, 60.0)["within_sla"] == (lat <= 60.0)
