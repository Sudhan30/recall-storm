"""Parse USDA FoodData Central records into Recall Storm SKUs."""
from __future__ import annotations

from contract import Sku
from recallstorm.core.errors import DataValidationError


def normalize_brand(brand: str) -> str:
    """Normalize a USDA FDC brandOwner or brandName string."""
    if not isinstance(brand, str):
        return "Generic"
    cleaned = " ".join(brand.strip().split())
    return cleaned.title() if cleaned.isupper() else (cleaned or "Generic")


def normalize_category(cat: str) -> str:
    """Normalize a USDA FDC brandedFoodCategory string to lowercase."""
    if not isinstance(cat, str):
        return "general"
    cleaned = " ".join(cat.strip().lower().split())
    return cleaned or "general"


def fdc_ingredients(item: dict) -> str:
    """Extract the ingredients string from an FDC item."""
    if not isinstance(item, dict):
        raise DataValidationError("FDC item must be a dict")
    return str(item.get("ingredients", "")).strip()


def fdc_gtin(item: dict) -> str:
    """Extract and zero-pad the GTIN-14 from an FDC item's gtinUpc field."""
    raw = str(item.get("gtinUpc") or item.get("gtin") or "").strip()
    digits = "".join(ch for ch in raw if ch.isdigit())
    if not digits:
        fdc_id = str(item.get("fdcId", "0"))
        digits = "".join(ch for ch in fdc_id if ch.isdigit()) or "0"
    return digits[:14].zfill(14)


def fdc_is_food(item: dict) -> bool:
    """Return True if the FDC item is a food product rather than an ingested drug."""
    cat = normalize_category(str(item.get("brandedFoodCategory", item.get("category", ""))))
    if "drug" in cat or "cough" in cat or "analgesic" in cat:
        return False
    return bool(item.get("is_food", True))


def parse_fdc_food(item: dict) -> dict:
    """Parse a raw USDA FDC branded food item dictionary."""
    if not isinstance(item, dict) or ("fdcId" not in item and "sku_id" not in item):
        raise DataValidationError("FDC item requires fdcId or sku_id")
    sku_id = str(item.get("sku_id") or f"FDC{item['fdcId']}").strip()
    is_food = fdc_is_food(item)
    return {
        "sku_id": sku_id,
        "gtin": fdc_gtin(item),
        "name": str(item.get("description") or item.get("name") or sku_id).strip(),
        "brand": normalize_brand(str(item.get("brandOwner") or item.get("brand") or "Generic")),
        "category": normalize_category(str(item.get("brandedFoodCategory") or item.get("category") or "food")),
        "ingredients": fdc_ingredients(item),
        "is_food": is_food,
        "is_ingested_drug": bool(item.get("is_ingested_drug", not is_food)),
        "case_units": int(item.get("case_units", 12)),
        "case_cube_ft3": float(item.get("case_cube_ft3", 1.5)),
        "case_weight_lb": float(item.get("case_weight_lb", 8.0)),
    }


def fdc_to_sku(item: dict) -> Sku:
    """Convert a USDA FDC food item to a contract Sku."""
    d = parse_fdc_food(item)
    return Sku(**d)


def parse_fdc_search(payload: dict) -> list[dict]:
    """Parse a USDA FDC search response containing a 'foods' array."""
    if not isinstance(payload, dict):
        raise DataValidationError("FDC search payload must be a dict")
    foods = payload.get("foods", [])
    return [parse_fdc_food(f) for f in foods]


def iter_fdc_pages(pages: list[dict]) -> list[Sku]:
    """Convert multiple FDC search response pages into a list of Sku objects."""
    out: list[Sku] = []
    for p in pages:
        for f in p.get("foods", []):
            out.append(fdc_to_sku(f))
    return out
