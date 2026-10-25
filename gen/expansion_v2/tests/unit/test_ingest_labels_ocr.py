"""Unit tests for recallstorm.ingest.labels_ocr."""
from recallstorm.ingest.labels_ocr import (
    OcrLabel,
    detect_ingredient_block,
    flag_low_confidence,
    join_ocr_lines,
    ocr_confidence,
    ocr_language,
    ocr_text_blocks,
    ocr_to_ingredients,
    parse_ocr_payload,
)


def test_labels_ocr():
    payload = {
        "sku_id": "SKU1",
        "blocks": [
            {"text": "Nutrition Facts", "confidence": 0.9},
            {"text": "INGREDIENTS: SUGAR, ERYTHRO-", "confidence": 0.8},
            {"text": "SINE, WATER.", "confidence": 0.85},
        ],
    }
    lbl = parse_ocr_payload(payload)
    assert isinstance(lbl, OcrLabel)
    assert "ERYTHROSINE" in lbl.ingredients
    assert ocr_to_ingredients(payload) == "SUGAR, ERYTHROSINE, WATER."
    assert not flag_low_confidence(payload, 0.75)
    assert ocr_language(payload) == "en"
    assert len(ocr_text_blocks(payload)) == 3
    assert abs(ocr_confidence(payload) - 0.85) < 1e-6
    assert detect_ingredient_block("Ingredients: Corn Syrup") == "Corn Syrup"
    assert join_ocr_lines(["RED-", "3"]) == "RED3"
