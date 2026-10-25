"""Commissary chef alerts, salad bar pulls, and catering client advisories."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class CommissaryChefAlert:
    """Alert for in-store deli/bakery/commissary culinary teams."""

    ref_id: str = "FDS-CHF-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class MenuRemovalNotice:
    """Notice removing recalled menu items from hot bars, salad bars, and catering."""

    ref_id: str = "FDS-MNU-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def halt_in_store_restaurant_recipe_prep(store_id: str, recipe_id: str) -> dict:
    """Lock recipe card on kitchen production tablets when an ingredient is recalled."""
    _req(store_id, "store_id")
    _req(recipe_id, "recipe_id")
    return {"op": "halt_in_store_restaurant_recipe_prep", "store_id": str(store_id), "recipe_id": str(recipe_id), "halted": True, "src": "recallstorm/comms/foodservice_advisories.py"}


def pull_recalled_ingredient_from_salad_bar(store_id: str, pan_item: str) -> dict:
    """Pull a recalled pan item and sanitize adjacent sneeze-guard tongs on self-serve salad bars."""
    _req(store_id, "store_id")
    _req(pan_item, "pan_item")
    return {"op": "pull_recalled_ingredient_from_salad_bar", "store_id": str(store_id), "pan_item": str(pan_item), "pulled": True, "src": "recallstorm/comms/foodservice_advisories.py"}


def update_digital_menu_board_allergens(store_id: str, item_id: str) -> dict:
    """Blank or update digital menu board allergen/calorie displays."""
    _req(store_id, "store_id")
    _req(item_id, "item_id")
    return {"op": "update_digital_menu_board_allergens", "store_id": str(store_id), "item_id": str(item_id), "updated": True, "src": "recallstorm/comms/foodservice_advisories.py"}


def notify_corporate_catering_event_clients(order_ids: list[str], platters: str = "Party Platter") -> dict:
    """Notify customers who picked up deli/bakery party platters containing a recalled component."""
    if not order_ids:
        raise DataValidationError("order_ids cannot be empty")
    return {"op": "notify_corporate_catering_event_clients", "notified_orders": len(order_ids), "platter": str(platters), "src": "recallstorm/comms/foodservice_advisories.py"}


def quarantine_hot_bar_steam_table_pans(store_id: str, pan_count: int = 1) -> dict:
    """Quarantine and discard hot-bar steam table pans."""
    _req(store_id, "store_id")
    if pan_count < 0:
        raise DataValidationError("pan_count cannot be negative")
    return {"op": "quarantine_hot_bar_steam_table_pans", "store_id": str(store_id), "pan_count": int(pan_count), "src": "recallstorm/comms/foodservice_advisories.py"}


def revise_printed_grab_and_go_ingredients(recipe_id: str, new_ingredients: str) -> dict:
    """Update scale ingredient deck after substituting a clean ingredient."""
    _req(recipe_id, "recipe_id")
    _req(new_ingredients, "new_ingredients")
    return {"op": "revise_printed_grab_and_go_ingredients", "recipe_id": str(recipe_id), "new_ingredients": str(new_ingredients), "src": "recallstorm/comms/foodservice_advisories.py"}


def alert_sushi_kiosk_franchise_operators(kiosk_ids: list[str], ingredient: str) -> dict:
    """Send urgent recall alert to third-party leased in-store sushi/cafe kiosk operators."""
    if not kiosk_ids:
        raise DataValidationError("kiosk_ids cannot be empty")
    _req(ingredient, "ingredient")
    return {"op": "alert_sushi_kiosk_franchise_operators", "kiosks": sorted(kiosk_ids), "ingredient": str(ingredient), "src": "recallstorm/comms/foodservice_advisories.py"}


def log_discarded_prepared_batch_weights(store_id: str, weight_lb: float) -> dict:
    """Log weight in pounds of discarded prepared food batches for shrink recovery."""
    _req(store_id, "store_id")
    if weight_lb < 0:
        raise DataValidationError("weight_lb cannot be negative")
    return {"op": "log_discarded_prepared_batch_weights", "store_id": str(store_id), "weight_lb": round(float(weight_lb), 2), "src": "recallstorm/comms/foodservice_advisories.py"}


def verify_kitchen_walk_in_cooler_sweep(store_id: str, cleared: bool = True) -> dict:
    """Verify that bulk #10 cans and foodservice cases in the deli/bakery walk-in cooler were swept."""
    _req(store_id, "store_id")
    return {"op": "verify_kitchen_walk_in_cooler_sweep", "store_id": str(store_id), "cleared": bool(cleared), "src": "recallstorm/comms/foodservice_advisories.py"}


def authorize_safe_ingredient_substitution(recipe_id: str, sub_ingredient: str) -> dict:
    """Authorize a culinary substitute ingredient verified free of new undeclared allergens."""
    _req(recipe_id, "recipe_id")
    _req(sub_ingredient, "sub_ingredient")
    return {"op": "authorize_safe_ingredient_substitution", "recipe_id": str(recipe_id), "sub_ingredient": str(sub_ingredient), "src": "recallstorm/comms/foodservice_advisories.py"}
