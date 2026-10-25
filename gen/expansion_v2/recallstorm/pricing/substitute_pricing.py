"""Substitute price parity overrides and anti-gouging controls."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class PriceMatchOverrideRule:
    """Rule honoring recalled item's lower retail price on substitute SKUs."""

    ref_id: str = "SUB-PRC-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class SubPriceParityEngine:
    """Engine managing substitute price parity and vendor subsidies."""

    ref_id: str = "SUB-PAR-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def authorize_equal_or_lesser_sub_price(recalled_price: float, sub_price: float) -> float:
    """Return min(recalled_price, sub_price) so customers are never upcharged on a substitute."""
    if recalled_price <= 0 or sub_price <= 0:
        raise DataValidationError("Prices must be positive")
    return round(min(float(recalled_price), float(sub_price)), 2)


def configure_bopis_substitution_discount(order_id: str, recalled_price: float, sub_price: float) -> dict:
    """Calculate automatic BOPIS substitution discount."""
    _req(order_id, "order_id")
    charged = authorize_equal_or_lesser_sub_price(recalled_price, sub_price)
    discount = round(max(0.0, float(sub_price) - charged), 2)
    return {"op": "configure_bopis_substitution_discount", "order_id": str(order_id), "charged": charged, "discount": discount, "src": "recallstorm/pricing/substitute_pricing.py"}


def cap_margin_erosion_on_national_sub(recalled_price: float, sub_cost: float, max_loss_per_unit: float = 2.0) -> dict:
    """Check whether substituting a national brand for private label exceeds max_loss_per_unit."""
    if recalled_price <= 0 or sub_cost <= 0 or max_loss_per_unit < 0:
        raise DataValidationError("Invalid price/cost inputs")
    loss = max(0.0, sub_cost - recalled_price)
    return {"op": "cap_margin_erosion_on_national_sub", "within_cap": loss <= max_loss_per_unit, "loss": round(loss, 2), "src": "recallstorm/pricing/substitute_pricing.py"}


def sync_electronic_shelf_label_sub_price(store_id: str, sub_sku_id: str, price: float) -> dict:
    """Push substitute retail price to the ESL tag at the shelf facing."""
    _req(store_id, "store_id")
    _req(sub_sku_id, "sub_sku_id")
    if price <= 0:
        raise DataValidationError("price must be positive")
    return {"op": "sync_electronic_shelf_label_sub_price", "store_id": str(store_id), "sub_sku_id": str(sub_sku_id), "price": round(float(price), 2), "src": "recallstorm/pricing/substitute_pricing.py"}


def waive_delivery_fee_for_recalled_sub(order_id: str, fee_usd: float = 7.95) -> dict:
    """Waive replacement delivery fee when a customer's previous order contained a recalled item."""
    _req(order_id, "order_id")
    if fee_usd < 0:
        raise DataValidationError("fee_usd cannot be negative")
    return {"op": "waive_delivery_fee_for_recalled_sub", "order_id": str(order_id), "waived_usd": round(float(fee_usd), 2), "src": "recallstorm/pricing/substitute_pricing.py"}


def calculate_promotional_price_carryover(promo_price: float, base_sub_price: float) -> float:
    """Carry over active promotional price from recalled SKU to its substitute."""
    return authorize_equal_or_lesser_sub_price(promo_price, base_sub_price)


def prevent_price_gouging_on_alternatives(old_price: float, new_price: float, max_increase_pct: float = 0.10) -> dict:
    """Enforce state emergency anti-price-gouging cap (<= 10% increase) on scarce alternatives (e.g. infant formula)."""
    if old_price <= 0 or new_price <= 0 or max_increase_pct < 0:
        raise DataValidationError("Invalid price inputs")
    inc = (new_price - old_price) / old_price
    return {"op": "prevent_price_gouging_on_alternatives", "compliant": inc <= max_increase_pct + 1e-6, "increase_pct": round(inc, 4), "src": "recallstorm/pricing/substitute_pricing.py"}


def track_sub_price_override_redemptions(redemptions: int, avg_subsidy_usd: float) -> float:
    """Calculate total price-parity subsidy across redemptions."""
    if redemptions < 0 or avg_subsidy_usd < 0:
        raise DataValidationError("Negative redemption inputs")
    return round(float(redemptions) * float(avg_subsidy_usd), 2)


def reconcile_vendor_funded_sub_subsidy(vendor_id: str, subsidy_usd: float) -> dict:
    """Bill the recalling manufacturer for the price-parity subsidy on substitute national brands."""
    _req(vendor_id, "vendor_id")
    if subsidy_usd < 0:
        raise DataValidationError("subsidy_usd cannot be negative")
    return {"op": "reconcile_vendor_funded_sub_subsidy", "vendor_id": str(vendor_id), "subsidy_usd": round(float(subsidy_usd), 2), "src": "recallstorm/pricing/substitute_pricing.py"}


def restore_base_retail_after_restock(sub_sku_id: str, base_price: float) -> dict:
    """Restore substitute SKU to its standard retail price once recall parity window ends."""
    _req(sub_sku_id, "sub_sku_id")
    if base_price <= 0:
        raise DataValidationError("base_price must be positive")
    return {"op": "restore_base_retail_after_restock", "sub_sku_id": str(sub_sku_id), "base_price": round(float(base_price), 2), "src": "recallstorm/pricing/substitute_pricing.py"}
