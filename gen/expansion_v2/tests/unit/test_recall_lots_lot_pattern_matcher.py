"""Unit tests for recallstorm.recall_lots.lot_pattern_matcher."""
from recallstorm.recall_lots.lot_pattern_matcher import (
    LotPatternSpec,
    WildcardLotMatcher,
    compile_lot_glob_expression,
    evaluate_julian_date_lot,
    expand_hyphenated_lot_span,
    handle_ocr_confused_characters,
    match_alphanumeric_lot_range,
    match_embossed_can_code,
    parse_plant_line_shift_code,
    score_lot_string_similarity,
    strip_lot_prefix_noise,
    validate_lot_against_regex_bank,
)


def test_lot_pattern_matcher():
    assert LotPatternSpec().status == "ACTIVE"
    assert WildcardLotMatcher().status == "ACTIVE"
    assert compile_lot_glob_expression("L26*").match("L2609") is not None
    assert match_alphanumeric_lot_range("L2605", "L2601", "L2610") is True
    assert strip_lot_prefix_noise("Lot: L-2601") == "L2601"
    assert evaluate_julian_date_lot("26120", 100, 150)["in_range"] is True
    assert parse_plant_line_shift_code("P02-L4-S1")["line"] == "L4"
    assert match_embossed_can_code("CAN-99A", "CAN99") is True
    assert handle_ocr_confused_characters("L0T-O1I") == "L0T-011"
    assert score_lot_string_similarity("L2601", "L2601") == 1.0
    assert expand_hyphenated_lot_span("L", 1, 3) == ["L1", "L2", "L3"]
    assert validate_lot_against_regex_bank("L2601", [r"^L26\d+"]) is True
