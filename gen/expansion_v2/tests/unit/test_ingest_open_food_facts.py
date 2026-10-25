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


def test_open_food_facts():
    prod = {
        "code": "3017620422003",
        "product_name": "Cherry Candies",
        "brands": "SweetCo, Other",
        "categories": "Candies, Snacks",
        "ingredients_text": "Sugar, Glucose",
        "additives_tags": ["en:e127", "en:e330"],
        "lang": "en",
    }
    assert off_gtin(prod) == "03017620422003"
    assert off_ingredients_text(prod) == "Sugar, Glucose"
    assert off_additive_tags(prod) == ["en:e127", "en:e330"]
    assert off_e_numbers(prod) == ["E127", "E330"]
    assert off_categories(prod) == ["candies", "snacks"]
    assert off_language(prod) == "en"
    parsed = parse_off_product(prod)
    assert "E127" in parsed["ingredients"]
    s1 = off_to_sku(prod)
    s2 = off_to_sku({**prod, "sku_id": "FDC1", "ingredients_text": "Sugar, Glucose, E127, Water"})
    merged = merge_off_fdc(s1, s2)
    assert merged.sku_id == "FDC1"
