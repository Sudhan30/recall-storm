"""Shelf tag flashing and store signage generation."""
from __future__ import annotations

from dataclasses import dataclass, field

from contract import Action, Facing, Location, Sku, SkuDecision, Store, Verdict


@dataclass
class SignPrinter:
    """In-store signage print queue."""

    store_id: str
    jobs: list[dict] = field(default_factory=list)


def sign_language(store: Store) -> str:
    """Return signage language mode ('en-es' bilingual for CA/TX/FL/AZ/NM, else 'en')."""
    if store.state.upper() in {"CA", "TX", "FL", "AZ", "NM", "NY"}:
        return "en-es"
    return "en"


def sign_template(verdict: Verdict, lang: str = "en") -> str:
    """Return the shelf sign template string for verdict and lang."""
    if verdict == Verdict.PULL:
        if "es" in lang:
            return "ITEM RECALLED / ARTICULO RETIRADO - DO NOT SELL"
        return "ITEM RECALLED - DO NOT SELL"
    if verdict == Verdict.HOLD_VERIFY:
        return "HOLD FOR QA VERIFICATION - DO NOT STOCK"
    return "AVAILABLE FOR SALE"


def tag_flash_text(sku: Sku, verdict: Verdict) -> str:
    """Generate ESL / shelf tag text for a SKU and Verdict."""
    return f"{sku.sku_id} ({sku.name}): {sign_template(verdict)}"


def shelf_tag_for_sku(sku: Sku, loc: Location, verdict: Verdict) -> dict:
    """Create a shelf tag dictionary for a specific location."""
    return {
        "sku_id": sku.sku_id,
        "gtin": sku.gtin,
        "action": Action.TAG_FLASH.value,
        "verdict": verdict.value,
        "loc": {"aisle": loc.aisle, "bay": loc.bay, "shelf": loc.shelf, "pos": loc.pos},
        "text": tag_flash_text(sku, verdict),
    }


def tags_for_store(
    store: Store,
    facings: list[Facing],
    skus: dict[str, Sku],
    decisions: dict[str, SkuDecision],
) -> list[dict]:
    """Build TAG_FLASH shelf tags for all pulled or held facings in store."""
    out: list[dict] = []
    for f in facings:
        if f.store_id != store.store_id:
            continue
        dec = decisions.get(f.sku_id)
        sku = skus.get(f.sku_id)
        if dec and sku and dec.verdict in {Verdict.PULL, Verdict.HOLD_VERIFY}:
            out.append({**shelf_tag_for_sku(sku, f.loc, dec.verdict), "store_id": store.store_id})
    return out


def printer_queue(tags: list[dict]) -> list[dict]:
    """Order shelf tags by aisle, bay, shelf, and position for efficient printing/placement."""
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
    """Attach source provenance to a shelf tag record."""
    return {**tag, "src": "recallstorm/store/signage.py"}


def sign_summary(tags: list[dict]) -> dict:
    """Summarize generated shelf tags."""
    return {"total_tags": len(tags), "stores": sorted({t.get("store_id", "") for t in tags if t.get("store_id")})}
