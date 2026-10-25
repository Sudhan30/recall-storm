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


def test_fdc_parsing():
    raw = {
        "fdcId": 1034191,
        "description": "Rainbow Sprinkles",
        "brandOwner": "Chocolatera De Nayarit",
        "brandedFoodCategory": "Baking Decorations & Dessert Toppings",
        "gtinUpc": "7502264930572",
        "ingredients": "SUGAR, FD&C RED #3.",
    }
    parsed = parse_fdc_food(raw)
    assert parsed["sku_id"] == "FDC1034191"
    assert fdc_gtin(raw) == "07502264930572"
    assert fdc_ingredients(raw) == "SUGAR, FD&C RED #3."
    assert fdc_is_food(raw) is True
    assert normalize_brand("  Brand   X ") == "Brand X"
    assert normalize_category("  Candy  ") == "candy"
    sku = fdc_to_sku(raw)
    assert sku.sku_id == "FDC1034191"

    page = {"foods": [raw]}
    assert len(parse_fdc_search(page)) == 1
    assert list(iter_fdc_pages([page])) == [sku]
