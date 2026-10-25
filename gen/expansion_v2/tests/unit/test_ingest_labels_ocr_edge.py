"""Edge case tests for recallstorm.ingest.labels_ocr."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.ingest.labels_ocr import flag_low_confidence, ocr_language, parse_ocr_payload


def test_labels_ocr_edge():
    with pytest.raises(DataValidationError):
        parse_ocr_payload({})
    assert flag_low_confidence({"confidence": 0.4}, 0.75)
    assert ocr_language({"text": "INGREDIENTES: AZUCAR, ROJO 3"}) == "es"
