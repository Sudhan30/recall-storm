"""Product scope evaluation ('food', 'ingested_drug', 'cosmetic') for SKUs and Rules."""
from __future__ import annotations

from contract import Rule, Sku


def is_food_scope(sku: Sku) -> bool:
    """Return True if SKU is a food product."""
    if not isinstance(sku, Sku):
        raise TypeError("sku must be a Sku")
    return bool(sku.is_food)


def is_drug_scope(sku: Sku) -> bool:
    """Return True if SKU is an ingested drug."""
    if not isinstance(sku, Sku):
        raise TypeError("sku must be a Sku")
    return bool(sku.is_ingested_drug)


def is_cosmetic_scope(sku: Sku) -> bool:
    """Return True if SKU is a topical/cosmetic or non-food/non-ingested-drug item."""
    if not isinstance(sku, Sku):
        raise TypeError("sku must be a Sku")
    if not sku.is_food and not sku.is_ingested_drug:
        return True
    cat = sku.category.lower()
    return "cosmetic" in cat or "topical" in cat or "lipstick" in cat


def product_types_for_sku(sku: Sku) -> tuple[str, ...]:
    """Return the tuple of contract product scope strings applicable to sku."""
    if not isinstance(sku, Sku):
        raise TypeError("sku must be a Sku")
    types: list[str] = []
    if is_food_scope(sku):
        types.append("food")
    if is_drug_scope(sku):
        types.append("ingested_drug")
    if is_cosmetic_scope(sku):
        types.append("cosmetic")
    return tuple(types)


def sku_in_scope(sku: Sku, rule: Rule) -> bool:
    """Return True if any of sku's product types match rule.applies_to."""
    if not isinstance(sku, Sku) or not isinstance(rule, Rule):
        raise TypeError("Expected Sku and Rule instances")
    sku_types = set(product_types_for_sku(sku))
    rule_types = {t.lower() for t in rule.applies_to}
    return bool(sku_types & rule_types)


def applies_to_sku(rule: Rule, sku: Sku) -> bool:
    """Return True if rule applies to sku's product type."""
    return sku_in_scope(sku, rule)


def scope_reason(sku: Sku, rule: Rule) -> str:
    """Explain why sku is in or out of scope for rule."""
    sku_types = product_types_for_sku(sku)
    if sku_in_scope(sku, rule):
        return f"SKU {sku.sku_id} product types {sku_types} match rule {rule.rule_id} scope {rule.applies_to}"
    return f"SKU {sku.sku_id} product types {sku_types} outside rule {rule.rule_id} scope {rule.applies_to}"


def exclude_reason(sku: Sku, rule: Rule) -> str | None:
    """Return an exclusion reason string if sku is outside rule's scope, else None."""
    if sku_in_scope(sku, rule):
        return None
    return scope_reason(sku, rule)


def scope_matrix(skus: list[Sku], rules: list[Rule]) -> dict[str, list[str]]:
    """Map each sku_id to the list of rule_ids whose product scope covers that SKU."""
    out: dict[str, list[str]] = {}
    for s in skus:
        out[s.sku_id] = [r.rule_id for r in rules if sku_in_scope(s, r)]
    return out
