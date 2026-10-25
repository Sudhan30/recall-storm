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


def test_ocr_pipeline():
    payload = {
        "sku_id": "SKU100",
        "blocks": ["NUTRITION FACTS", "INGREDIENTS: SUGAR, ERYTHRO-", "SINE, WATER."],
        "confidence": 0.92,
    }
    lbl = parse_ocr_payload(payload)
    assert isinstance(lbl, OcrLabel)
    assert len(ocr_text_blocks(lbl)) == 3
    assert ocr_confidence(lbl) == 0.92
    joined = join_ocr_lines(lbl.blocks)
    assert "ERYTHROSINE" in joined
    assert detect_ingredient_block(joined) == "SUGAR, ERYTHROSINE, WATER."
    assert ocr_to_ingredients(lbl) == "SUGAR, ERYTHROSINE, WATER."
    assert flag_low_confidence(lbl, 0.8) is False
    assert ocr_language(lbl) == "en"
