"""Integration test 02: Ingest USDA FDC & Open Food Facts -> Aliases -> Rules -> Adjudication evidence."""
from datetime import datetime, timezone
from contract import Verdict
from recallstorm.adjudicate import build_evidence, validate_evidence
from recallstorm.aliases import lexicon_from_rules, normalize_ingredients
from recallstorm.core import validate_sku
from recallstorm.ingest import fdc_to_sku, merge_off_fdc, off_to_sku
from recallstorm.rules import evaluate_sku, red3_rules


def test_flow_02_ingest_to_adjudicate():
    fdc_raw = {
        "fdcId": 99001,
        "description": "Cherry Frosting",
        "brandOwner": "BakeCorp",
        "brandedFoodCategory": "Baking Decorations",
        "gtinUpc": "00750226493057",
        "ingredients": "SUGAR, WATER",
    }
    off_raw = {
        "code": "00750226493057",
        "product_name": "Cherry Frosting",
        "brands": "BakeCorp",
        "categories": "Baking",
        "ingredients_text_en": "SUGAR, WATER, ERYTHROSINE (E127), SALT",
        "additives_tags": ["en:e127"],
    }
    fdc_sku = fdc_to_sku(fdc_raw)
    off_sku = off_to_sku(off_raw)
    merged = merge_off_fdc(off_sku, fdc_sku)
    assert validate_sku(merged) == []
    assert "ERYTHROSINE" in normalize_ingredients(merged.ingredients)

    rules = red3_rules()
    lex = lexicon_from_rules(rules)
    assert "E127" in lex.entries["RED3"]

    dec = evaluate_sku(merged, rules, "CA", datetime(2027, 1, 2, tzinfo=timezone.utc))
    assert dec.verdict == Verdict.PULL
    ev = build_evidence(merged, dec, rules[0])
    assert validate_evidence(ev) == []
