"""Shelf flash tags and customer recall notices."""
from __future__ import annotations

from dataclasses import dataclass
from contract import Action, Facing, Location, Sku, StoreFormat


@dataclass(frozen=True)
class SignPrinter:
    """Store sign printer queue configuration."""

    store_id: str
    template: str = "STANDARD_FLASH_TAG"


def tag_flash_text(sku: Sku, rule_ids: list[str] | tuple[str, ...]) -> str:
    """Format customer-facing TAG_FLASH text for a pulled SKU."""
    if not isinstance(sku, Sku):
        raise TypeError("sku must be a Sku")
    rules_str = ", ".join(rule_ids) if rule_ids else "Regulatory Compliance"
    return f"ITEM TEMPORARILY UNAVAILABLE: {sku.brand} {sku.name} ({sku.gtin}) - {rules_str}"


def sign_template(fmt: StoreFormat | str) -> str:
    """Return the shelf tag template name for a store format."""
    f = fmt.value if isinstance(fmt, StoreFormat) else str(fmt).upper()
    return "PALLET_PLACARD" if f == "SAMS" else "SHELF_CHANNEL_FLASH"


def sign_language(state: str) -> str:
    """Return primary/secondary signage language code for a state."""
    return "en/es" if state.strip().upper() in ("CA", "TX", "FL", "NM", "AZ") else "en"


def shelf_tag_for_sku(store_id: str, sku: Sku, loc: Location) -> dict:
    """Build a shelf flash tag dictionary for a specific location."""
    return {
        "store_id": store_id,
        "sku_id": sku.sku_id,
        "action": Action.TAG_FLASH.value,
        "loc": {"aisle": loc.aisle, "bay": loc.bay, "shelf": loc.shelf, "pos": loc.pos},
        "text": tag_flash_text(sku, ()),
    }


def tags_for_store(
    store_id: str,
    facings: list[Facing],
    skus_by_id: dict[str, Sku],
    pulled_sku_ids: set[str],
) -> list[dict]:
    """Generate shelf tag dicts for all pulled facings in a store."""
    out: list[dict] = []
    for f in facings:
        if f.store_id == store_id and f.sku_id in pulled_sku_ids and f.sku_id in skus_by_id:
            out.append(shelf_tag_for_sku(store_id, skus_by_id[f.sku_id], f.loc))
    return out


def printer_queue(tags: list[dict]) -> list[dict]:
    """Order shelf tags by aisle, bay, shelf, and pos for efficient printing and placement."""
    return sorted(
        tags,
        key=lambda t: (
            t.get("store_id", ""),
            t["loc"]["aisle"],
            t["loc"]["bay"],
            t["loc"]["shelf"],
            t["loc"]["pos"],
        ),
    )


def tag_to_record(tag: dict) -> dict:
    """Normalize a tag dictionary for serialization."""
    return dict(tag)


def sign_summary(tags: list[dict]) -> dict:
    """Summarize generated shelf tags."""
    stores = sorted({t["store_id"] for t in tags})
    return {"total_tags": len(tags), "stores": stores}
