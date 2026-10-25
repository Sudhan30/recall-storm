"""Unit tests for recallstorm.ingest.open_food_facts."""
from recallstorm.ingest.open_food_facts import (
    merge_off_fdc,
    off_additive_tags,
    off_categories,
    off_e_numbers,
    off_gtin,
    off_ingredients_text,
    off_language,
    off_to_sku,
    parse_off_product,
)
from recallstorm.ingest.usda_fdc import fdc_to_sku


def test_off_parsing_and_merge():
    raw = {
        "code": "7502264930572",
        "product_name": "Rainbow Sprinkles",
        "brands": "Chocolatera",
        "categories": "Candies, Sprinkles",
        "ingredients_text_en": "Sugar, Corn Syrup",
        "additives_tags": ["en:e127", "en:e129"],
        "lang": "en",
    }
    assert off_gtin(raw) == "07502264930572"
    assert off_ingredients_text(raw) == "Sugar, Corn Syrup"
    assert off_additive_tags(raw) == ["en:e127", "en:e129"]
    assert off_e_numbers(raw) == ["E127", "E129"]
    assert off_categories(raw) == "candies"
    assert off_language(raw) == "en"
    parsed = parse_off_product({"product": raw})
    assert "E127" in parsed["ingredients"]
    off_s = off_to_sku(raw)
    fdc_s = fdc_to_sku({"fdcId": 1034191, "gtinUpc": "7502264930572", "ingredients": "SHORT"})
    merged = merge_off_fdc(off_s, fdc_s)
    assert merged.sku_id == "FDC1034191"
    assert "E127" in merged.ingredients
