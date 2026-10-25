"""Edge tests for recallstorm.ingest.labels_ocr."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.ingest.labels_ocr import (
    flag_low_confidence,
    ocr_language,
    parse_ocr_payload,
)


def test_ocr_edge_cases():
    es_lbl = parse_ocr_payload({"sku_id": "S1", "blocks": ["Ingredientes: Azucar, E127"], "confidence": 0.5})
    assert ocr_language(es_lbl) == "es"
    assert flag_low_confidence(es_lbl, 0.75) is True

    with pytest.raises(DataValidationError):
        parse_ocr_payload({})
    with pytest.raises(DataValidationError):
        parse_ocr_payload({"sku_id": "S1", "confidence": 1.5})
    with pytest.raises(ValueError):
        flag_low_confidence(es_lbl, 2.0)
