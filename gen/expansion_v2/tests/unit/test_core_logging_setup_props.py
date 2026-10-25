"""Property tests for recallstorm.core.logging_setup."""
import random
from recallstorm.core.logging_setup import configure_logging, log_timing, redact_text


def test_logging_props():
    rng = random.Random(42)
    logger = configure_logging()
    for i in range(25):
        dur = rng.uniform(0.0, 500.0)
        res = log_timing(logger, f"op_{i}", dur)
        assert res["duration_ms"] >= 0.0
        phone = f"{rng.randint(100,999)}-{rng.randint(100,999)}-{rng.randint(1000,9999)}"
        assert "[REDACTED_PHONE]" in redact_text(f"call {phone} today")
