"""Open Food Facts (OFF) product parser and FDC merger."""
from __future__ import annotations

from contract import Sku
from recallstorm.core.errors import DataValidationError
from recallstorm.ingest.usda_fdc import normalize_brand, normalize_category


def off_gtin(raw: dict) -> str:
    """Extract and zero-pad the OFF product barcode ('code') to 14 digits."""
    code = str(raw.get("code") or raw.get("gtin") or "").strip()
    digits = "".join(ch for ch in code if ch.isdigit())
    if not digits:
        raise DataValidationError("Open Food Facts product requires numeric 'code'")
    return digits.zfill(14)[:14]


def off_ingredients_text(raw: dict) -> str:
    """Extract the best available ingredient text from an OFF product."""
    for key in ("ingredients_text_en", "ingredients_text", "ingredients"):
        val = raw.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def off_additive_tags(raw: dict) -> list[str]:
    """Return normalized additive tags (e.g., 'en:e127') from OFF product."""
    tags = raw.get("additives_tags", [])
    if not isinstance(tags, list):
        return []
    return [str(t).strip().lower() for t in tags if str(t).strip()]


def off_e_numbers(raw: dict) -> list[str]:
    """Extract uppercase E-numbers (e.g., 'E127') from OFF additive tags."""
    out: list[str] = []
    for tag in off_additive_tags(raw):
        code = tag.split(":")[-1].upper()
        if code.startswith("E") and any(ch.isdigit() for ch in code):
            out.append(code)
    return out


def off_categories(raw: dict) -> str:
    """Extract the primary category from an OFF product."""
    cats = raw.get("categories") or raw.get("categories_en") or "other food"
    if isinstance(cats, list):
        cats = cats[0] if cats else "other food"
    first = str(cats).split(",")[0]
    return normalize_category(first)


def off_language(raw: dict) -> str:
    """Return the 2-letter language code of an OFF product."""
    return str(raw.get("lang", "en")).strip().lower() or "en"


def parse_off_product(raw: dict) -> dict:
    """Parse a raw OFF product dictionary (or wrapper with 'product' key)."""
    if not isinstance(raw, dict):
        raise DataValidationError("OFF product must be a dict")
    prod = raw.get("product", raw)
    if not isinstance(prod, dict):
        raise DataValidationError("OFF product field must be a dict")
    gtin = off_gtin(prod)
    sku_id = str(prod.get("sku_id") or f"OFF{gtin[-8:]}").strip()
    ing = off_ingredients_text(prod)
    enums = off_e_numbers(prod)
    if enums and not any(e in ing.upper() for e in enums):
        ing = f"{ing} ({', '.join(enums)})".strip()
    return {
        "sku_id": sku_id,
        "gtin": gtin,
        "name": str(prod.get("product_name") or prod.get("name") or sku_id).strip(),
        "brand": normalize_brand(prod.get("brands") or prod.get("brand")),
        "category": off_categories(prod),
        "ingredients": ing,
        "is_food": True,
        "is_ingested_drug": False,
        "case_units": int(prod.get("case_units", 12)),
        "case_cube_ft3": float(prod.get("case_cube_ft3", 1.5)),
        "case_weight_lb": float(prod.get("case_weight_lb", 8.0)),
    }


def off_to_sku(raw: dict) -> Sku:
    """Convert an Open Food Facts product dictionary to a contract Sku."""
    return Sku(**parse_off_product(raw))


def merge_off_fdc(off_sku: Sku, fdc_sku: Sku) -> Sku:
    """Merge an OFF Sku with an FDC Sku, preferring FDC identity and richer ingredients."""
    if not isinstance(off_sku, Sku) or not isinstance(fdc_sku, Sku):
        raise TypeError("Both arguments must be Sku instances")
    ing = fdc_sku.ingredients if len(fdc_sku.ingredients) >= len(off_sku.ingredients) else off_sku.ingredients
    return Sku(
        sku_id=fdc_sku.sku_id,
        gtin=fdc_sku.gtin,
        name=fdc_sku.name or off_sku.name,
        brand=fdc_sku.brand if fdc_sku.brand != "Generic" else off_sku.brand,
        category=fdc_sku.category,
        ingredients=ing,
        is_food=fdc_sku.is_food,
        is_ingested_drug=fdc_sku.is_ingested_drug,
        case_units=fdc_sku.case_units,
        case_cube_ft3=fdc_sku.case_cube_ft3,
        case_weight_lb=fdc_sku.case_weight_lb,
    )
