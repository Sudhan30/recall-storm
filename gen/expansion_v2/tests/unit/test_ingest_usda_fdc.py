"""Unit tests for recallstorm.ingest.usda_fdc."""
from recallstorm.ingest.usda_fdc import (
    fdc_gtin,
    fdc_ingredients,
    fdc_is_food,
    fdc_to_sku,
    iter_fdc_pages,
    normalize_brand,
    normalize_category,
    parse_fdc_food,
    parse_fdc_search,
)


def test_usda_fdc_parsing():
    raw = {
        "fdcId": 1034191,
        "gtinUpc": "07502264930572",
        "description": "Rainbow Sprinkles",
        "brandOwner": "CHOCOLATERA DE NAYARIT",
        "brandedFoodCategory": "Baking Decorations & Dessert Toppings",
        "ingredients": "SUGAR, FD&C RED #3.",
    }
    parsed = parse_fdc_food(raw)
    assert parsed["sku_id"] == "FDC1034191"
    assert fdc_gtin(raw) == "07502264930572"
    assert fdc_ingredients(raw) == "SUGAR, FD&C RED #3."
    assert fdc_is_food(raw) is True
    assert normalize_brand("GREAT VALUE") == "Great Value"
    assert normalize_category("  Candy  ") == "candy"
    sku = fdc_to_sku(raw)
    assert sku.sku_id == "FDC1034191"
    search_res = parse_fdc_search({"foods": [raw]})
    assert len(search_res) == 1
    skus = iter_fdc_pages([{"foods": [raw]}])
    assert len(skus) == 1
