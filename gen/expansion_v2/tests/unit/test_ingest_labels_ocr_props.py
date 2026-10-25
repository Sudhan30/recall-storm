"""Property tests for recallstorm.ingest.labels_ocr."""
import random
from recallstorm.ingest.labels_ocr import ocr_confidence


def test_ocr_confidence_bounds():
    rng = random.Random(42)
    for _ in range(30):
        blocks = [{"text": "A", "confidence": rng.uniform(-0.5, 1.5)} for _ in range(5)]
        c = ocr_confidence({"blocks": blocks})
        assert 0.0 <= c <= 1.0
