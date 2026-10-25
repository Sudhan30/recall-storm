"""Parse Open Food Facts products and merge with USDA FDC."""
from __future__ import annotations

from contract import Sku
from recallstorm.core.errors import DataValidationError


def off_gtin(prod: dict) -> str:
    """Extract and zero-pad the GTIN-14 from an Open Food Facts product."""
    code = str(prod.get("code") or prod.get("gtin") or "").strip()
    digits = "".join(c for c in code if c.isdigit())
    if not digits:
        raise DataValidationError("Open Food Facts product missing numeric code")
    return digits[:14].zfill(14)


def off_ingredients_text(prod: dict) -> str:
    """Extract the best available ingredients_text from an OFF product."""
    for key in ("ingredients_text_en", "ingredients_text", "ingredients"):
        val = prod.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def off_additive_tags(prod: dict) -> list[str]:
    """Extract additive tags (e.g., 'en:e127') from an OFF product."""
    tags = prod.get("additives_tags") or []
    return [str(t).lower().strip() for t in tags if str(t).strip()]


def off_e_numbers(prod: dict) -> list[str]:
    """Convert OFF additive tags to uppercase E-numbers (e.g., 'E127')."""
    out: list[str] = []
    for tag in off_additive_tags(prod):
        part = tag.split(":")[-1].upper()
        if part.startswith("E") and part[1:].isalnum():
            out.append(part)
    return out


def off_categories(prod: dict) -> list[str]:
    """Extract normalized categories from an OFF product."""
    cats = prod.get("categories") or ""
    if isinstance(cats, list):
        return [str(c).strip().lower() for c in cats if str(c).strip()]
    return [c.strip().lower() for c in str(cats).split(",") if c.strip()]


def off_language(prod: dict) -> str:
    """Return the primary language code of an OFF product."""
    return str(prod.get("lang") or "en").lower().strip()


def parse_off_product(prod: dict) -> dict:
    """Parse an Open Food Facts product dictionary."""
    if not isinstance(prod, dict):
        raise DataValidationError("OFF product must be a dict")
    gtin = off_gtin(prod)
    sku_id = str(prod.get("sku_id") or f"OFF{gtin[-8:]}")
    cats = off_categories(prod)
    ings = off_ingredients_text(prod)
    enums = off_e_numbers(prod)
    if enums and not any(e in ings.upper() for e in enums):
        ings = f"{ings} ({', '.join(enums)})".strip()
    return {
        "sku_id": sku_id,
        "gtin": gtin,
        "name": str(prod.get("product_name") or sku_id).strip(),
        "brand": str(prod.get("brands") or "Generic").split(",")[0].strip(),
        "category": cats[0] if cats else "food",
        "ingredients": ings,
        "is_food": True,
        "is_ingested_drug": False,
        "case_units": int(prod.get("case_units", 12)),
        "case_cube_ft3": float(prod.get("case_cube_ft3", 1.4)),
        "case_weight_lb": float(prod.get("case_weight_lb", 6.0)),
    }


def off_to_sku(prod: dict) -> Sku:
    """Convert an Open Food Facts product dict into a contract Sku."""
    return Sku(**parse_off_product(prod))


def merge_off_fdc(off_sku: Sku, fdc_sku: Sku) -> Sku:
    """Merge an OFF Sku and FDC Sku preferring FDC identity and richer ingredients."""
    ings = fdc_sku.ingredients if len(fdc_sku.ingredients) >= len(off_sku.ingredients) else off_sku.ingredients
    return Sku(
        sku_id=fdc_sku.sku_id,
        gtin=fdc_sku.gtin,
        name=fdc_sku.name or off_sku.name,
        brand=fdc_sku.brand or off_sku.brand,
        category=fdc_sku.category or off_sku.category,
        ingredients=ings,
        is_food=fdc_sku.is_food,
        is_ingested_drug=fdc_sku.is_ingested_drug,
        case_units=fdc_sku.case_units,
        case_cube_ft3=fdc_sku.case_cube_ft3,
        case_weight_lb=fdc_sku.case_weight_lb,
    )
