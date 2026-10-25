"""USDA FoodData Central (FDC) branded food parser."""
from __future__ import annotations

from typing import Iterator
from contract import Sku
from recallstorm.core.errors import DataValidationError


def normalize_brand(brand: str | None) -> str:
    """Normalize an FDC brandOwner or brandName string."""
    if not brand or not isinstance(brand, str):
        return "Generic"
    return " ".join(brand.strip().split())


def normalize_category(cat: str | None) -> str:
    """Normalize an FDC brandedFoodCategory string to lowercase."""
    if not cat or not isinstance(cat, str):
        return "other food"
    return " ".join(cat.strip().lower().split())


def fdc_ingredients(raw: dict) -> str:
    """Extract the ingredients string from an FDC record."""
    if not isinstance(raw, dict):
        raise TypeError("raw must be a dict")
    return str(raw.get("ingredients", "")).strip()


def fdc_gtin(raw: dict) -> str:
    """Extract and zero-pad an FDC gtinUpc to 14 digits."""
    if not isinstance(raw, dict):
        raise TypeError("raw must be a dict")
    gtin_raw = str(raw.get("gtinUpc") or raw.get("gtin") or "").strip()
    digits = "".join(ch for ch in gtin_raw if ch.isdigit())
    if not digits:
        fdc_id = str(raw.get("fdcId", "0")).strip()
        digits = "".join(ch for ch in fdc_id if ch.isdigit()) or "0"
    return digits.zfill(14)[:14]


def fdc_is_food(raw: dict) -> bool:
    """Determine if an FDC item is a food product vs ingested drug/supplement."""
    cat = normalize_category(raw.get("brandedFoodCategory") or raw.get("category"))
    if "drug" in cat or "cough" in cat or "analgesic" in cat:
        return False
    return True


def parse_fdc_food(raw: dict) -> dict:
    """Validate and normalize a raw USDA FDC food JSON object."""
    if not isinstance(raw, dict) or ("fdcId" not in raw and "sku_id" not in raw):
        raise DataValidationError("FDC food record requires fdcId or sku_id")
    sku_id = str(raw.get("sku_id") or f"FDC{raw['fdcId']}").strip()
    return {
        "sku_id": sku_id,
        "gtin": fdc_gtin(raw),
        "name": str(raw.get("description") or raw.get("name") or sku_id).strip(),
        "brand": normalize_brand(raw.get("brandName") or raw.get("brandOwner") or raw.get("brand")),
        "category": normalize_category(raw.get("brandedFoodCategory") or raw.get("category")),
        "ingredients": fdc_ingredients(raw),
        "is_food": fdc_is_food(raw),
        "is_ingested_drug": not fdc_is_food(raw),
        "case_units": int(raw.get("case_units", 12)),
        "case_cube_ft3": float(raw.get("case_cube_ft3", 1.5)),
        "case_weight_lb": float(raw.get("case_weight_lb", 8.0)),
    }


def fdc_to_sku(raw: dict) -> Sku:
    """Convert a USDA FDC food record to a contract Sku."""
    p = parse_fdc_food(raw)
    return Sku(**p)


def parse_fdc_search(payload: dict) -> list[dict]:
    """Parse an FDC search response payload containing a 'foods' list."""
    if not isinstance(payload, dict) or not isinstance(payload.get("foods"), list):
        raise DataValidationError("FDC search payload must contain a 'foods' list")
    return [parse_fdc_food(f) for f in payload["foods"]]


def iter_fdc_pages(pages: list[dict]) -> Iterator[Sku]:
    """Yield Sku objects across multiple FDC search response pages."""
    for page in pages:
        for parsed in parse_fdc_search(page):
            yield Sku(**parsed)
