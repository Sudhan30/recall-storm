"""Downstream BOM cascade from raw ingredient lots to commissary/bakery items."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class IngredientCascadeGraph:
    """DAG mapping upstream ingredient lots to downstream finished SKUs."""

    ref_id: str = "CAS-DAG-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class DownstreamSkuResolver:
    """Resolver for secondary/derivative recalls."""

    ref_id: str = "CAS-RES-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def map_raw_lot_to_finished_goods(raw_lot: str, bom_map: dict[str, list[str]]) -> list[str]:
    """Return finished good SKU IDs produced using raw_lot."""
    _req(raw_lot, "raw_lot")
    if bom_map is None:
        raise DataValidationError("bom_map cannot be None")
    return sorted(bom_map.get(str(raw_lot), []))


def trace_commissary_recipe_boms(ingredient_sku: str, recipes: dict[str, list[str]]) -> list[str]:
    """Return commissary recipe IDs that include ingredient_sku."""
    _req(ingredient_sku, "ingredient_sku")
    if recipes is None:
        raise DataValidationError("recipes cannot be None")
    return sorted(r_id for r_id, ings in recipes.items() if ingredient_sku in ings)


def identify_in_store_bakery_mixes(recalled_sprinkle_sku: str, bakery_skus: list[dict]) -> list[str]:
    """Identify in-store bakery cupcake/cookie SKUs topped with recalled_sprinkle_sku."""
    _req(recalled_sprinkle_sku, "recalled_sprinkle_sku")
    if bakery_skus is None:
        raise DataValidationError("bakery_skus cannot be None")
    return [str(b["sku_id"]) for b in bakery_skus if recalled_sprinkle_sku in b.get("components", [])]


def flag_prepared_foods_salads(ingredient_name: str, menu_items: list[dict]) -> list[str]:
    """Flag deli grab-and-go salads containing recalled ingredient_name."""
    _req(ingredient_name, "ingredient_name")
    if menu_items is None:
        raise DataValidationError("menu_items cannot be None")
    low = str(ingredient_name).lower()
    return [str(m["sku_id"]) for m in menu_items if low in str(m.get("ingredients", "")).lower()]


def calculate_generational_dilution_factor(raw_kg: float, batch_kg: float) -> float:
    """Calculate mass fraction of recalled raw ingredient in finished batch."""
    if raw_kg < 0 or batch_kg <= 0 or raw_kg > batch_kg:
        raise DataValidationError("Invalid raw_kg or batch_kg")
    return round(raw_kg / batch_kg, 4)


def resolve_co_packer_cross_supply(supplier_lot: str, copackers: list[str]) -> dict:
    """Map an upstream ingredient lot shipped to multiple co-packers."""
    _req(supplier_lot, "supplier_lot")
    return {"op": "resolve_co_packer_cross_supply", "supplier_lot": str(supplier_lot), "copackers": sorted(copackers), "src": "recallstorm/recall_lots/sub_recall_cascade.py"}


def propagate_recall_to_meal_kits(component_sku: str, kits: dict[str, list[str]]) -> list[str]:
    """Return meal kit SKU IDs containing component_sku."""
    _req(component_sku, "component_sku")
    if kits is None:
        raise DataValidationError("kits cannot be None")
    return sorted(k for k, comps in kits.items() if component_sku in comps)


def build_cascade_impact_tree(root_lot: str, tier1: list[str], tier2: list[str]) -> dict:
    """Build a multi-tier sub-recall impact tree."""
    _req(root_lot, "root_lot")
    return {"op": "build_cascade_impact_tree", "root_lot": str(root_lot), "tier1": list(tier1), "tier2": list(tier2), "total_nodes": 1 + len(tier1) + len(tier2), "src": "recallstorm/recall_lots/sub_recall_cascade.py"}


def audit_central_kitchen_batch_logs(kitchen_id: str, batches_checked: int = 5) -> dict:
    """Audit central commissary batch production logs."""
    _req(kitchen_id, "kitchen_id")
    if batches_checked < 0:
        raise DataValidationError("batches_checked cannot be negative")
    return {"op": "audit_central_kitchen_batch_logs", "kitchen_id": str(kitchen_id), "batches_checked": int(batches_checked), "src": "recallstorm/recall_lots/sub_recall_cascade.py"}


def generate_derivative_sku_pull_list(primary_sku: str, derivative_skus: list[str]) -> dict:
    """Generate a pull list combining primary_sku and all downstream derivative_skus."""
    _req(primary_sku, "primary_sku")
    if derivative_skus is None:
        raise DataValidationError("derivative_skus cannot be None")
    all_skus = sorted({str(primary_sku)} | set(derivative_skus))
    return {"op": "generate_derivative_sku_pull_list", "all_skus": all_skus, "count": len(all_skus), "src": "recallstorm/recall_lots/sub_recall_cascade.py"}
