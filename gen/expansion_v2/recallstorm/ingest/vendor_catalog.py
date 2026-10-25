"""Parse vendor catalog rows into SKUs and metadata."""
from __future__ import annotations

from dataclasses import dataclass, field

from contract import Sku
from recallstorm.core.errors import DataValidationError


@dataclass
class VendorCatalog:
    """Merged vendor catalog with SKUs, DSD flags, and substitute suggestions."""

    skus: dict[str, Sku] = field(default_factory=dict)
    dsd_flags: dict[str, bool] = field(default_factory=dict)
    substitutes: dict[str, list[str]] = field(default_factory=dict)
    contacts: dict[str, dict] = field(default_factory=dict)


def parse_vendor_row(row: dict) -> dict:
    """Validate and normalize a raw vendor catalog dictionary."""
    if not isinstance(row, dict) or not row.get("sku_id") or not row.get("gtin"):
        raise DataValidationError("Vendor row requires sku_id and gtin")
    return {
        "sku_id": str(row["sku_id"]).strip(),
        "gtin": str(row["gtin"]).strip().zfill(14),
        "name": str(row.get("name", "Unknown")).strip(),
        "brand": str(row.get("brand", "Generic")).strip(),
        "category": str(row.get("category", "general")).strip().lower(),
        "ingredients": str(row.get("ingredients", "")).strip(),
        "is_food": bool(row.get("is_food", True)),
        "is_ingested_drug": bool(row.get("is_ingested_drug", False)),
        "dsd": vendor_dsd_flag(row),
        "case_pack": vendor_case_pack(row),
        "reformulation_date": vendor_reformulation_date(row),
        "substitutes": vendor_sub_suggestions(row),
        "contacts": vendor_contacts(row),
    }


def vendor_case_pack(row: dict) -> tuple[int, float, float]:
    """Extract (case_units, case_cube_ft3, case_weight_lb) from a vendor row."""
    units = int(row.get("case_units", 12))
    cube = float(row.get("case_cube_ft3", 1.5))
    weight = float(row.get("case_weight_lb", 10.0))
    if units <= 0 or cube <= 0 or weight <= 0:
        raise DataValidationError("Case pack dimensions must be positive")
    return (units, cube, weight)


def vendor_to_sku(row: dict) -> Sku:
    """Convert a vendor catalog row to a contract Sku."""
    parsed = parse_vendor_row(row)
    units, cube, weight = parsed["case_pack"]
    return Sku(
        sku_id=parsed["sku_id"],
        gtin=parsed["gtin"],
        name=parsed["name"],
        brand=parsed["brand"],
        category=parsed["category"],
        ingredients=parsed["ingredients"],
        is_food=parsed["is_food"],
        is_ingested_drug=parsed["is_ingested_drug"],
        case_units=units,
        case_cube_ft3=cube,
        case_weight_lb=weight,
    )


def vendor_dsd_flag(row: dict) -> bool:
    """Return True if the vendor item is Direct Store Delivery (DSD)."""
    return bool(row.get("is_dsd") or row.get("dsd"))


def vendor_reformulation_date(row: dict) -> str | None:
    """Return the planned reformulation ISO date string if present."""
    dt = row.get("reformulation_date")
    return str(dt).strip() if dt else None


def vendor_sub_suggestions(row: dict) -> list[str]:
    """Extract substitute SKU IDs suggested by the vendor."""
    subs = row.get("substitutes") or []
    if isinstance(subs, str):
        return [s.strip() for s in subs.split(",") if s.strip()]
    return [str(s).strip() for s in subs if str(s).strip()]


def vendor_contacts(row: dict) -> dict:
    """Extract vendor recall contact info."""
    return {
        "vendor_name": str(row.get("vendor_name", row.get("brand", "Vendor"))).strip(),
        "email": str(row.get("contact_email", "qa@vendor.example")).strip(),
    }


def merge_vendor_catalog(rows: list[dict]) -> VendorCatalog:
    """Merge multiple vendor rows into a VendorCatalog."""
    cat = VendorCatalog()
    for r in rows:
        sku = vendor_to_sku(r)
        cat.skus[sku.sku_id] = sku
        cat.dsd_flags[sku.sku_id] = vendor_dsd_flag(r)
        cat.substitutes[sku.sku_id] = vendor_sub_suggestions(r)
        cat.contacts[sku.sku_id] = vendor_contacts(r)
    return cat
