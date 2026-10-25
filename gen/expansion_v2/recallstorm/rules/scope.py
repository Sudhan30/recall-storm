"""Product scope evaluation (food, ingested_drug, cosmetic)."""
from __future__ import annotations

from datetime import datetime

from contract import Rule, Sku
from recallstorm.rules.dates import is_prohibited_at
from recallstorm.rules.jurisdiction import applies_in_state


def is_food_scope(sku: Sku) -> bool:
    """Return True if sku.is_food is True."""
    return bool(sku.is_food)


def is_drug_scope(sku: Sku) -> bool:
    """Return True if sku.is_ingested_drug is True."""
    return bool(sku.is_ingested_drug)


def is_cosmetic_scope(sku: Sku) -> bool:
    """Return True if sku is neither food nor ingested_drug (e.g. topical cosmetic)."""
    if sku.is_food or sku.is_ingested_drug:
        return False
    cat = (sku.category or "").lower()
    return any(k in cat for k in ("cosmetic", "lipstick", "makeup", "lotion", "shampoo", "soap", "personal care")) or (
        not sku.is_food and not sku.is_ingested_drug
    )


def product_types_for_sku(sku: Sku) -> tuple[str, ...]:
    """Return the applicable product scope tags ('food', 'ingested_drug', 'cosmetic') for sku."""
    types: list[str] = []
    if is_food_scope(sku):
        types.append("food")
    if is_drug_scope(sku):
        types.append("ingested_drug")
    if is_cosmetic_scope(sku):
        types.append("cosmetic")
    return tuple(types)


def sku_in_scope(sku: Sku, rule: Rule) -> bool:
    """Return True if sku's product types intersect rule.applies_to."""
    sku_types = set(product_types_for_sku(sku))
    rule_types = {t.lower().strip() for t in rule.applies_to}
    return bool(sku_types & rule_types)


def exclude_reason(sku: Sku, rule: Rule) -> str | None:
    """Return reason why sku is excluded from rule's product scope, or None if in scope."""
    if sku_in_scope(sku, rule):
        return None
    return f"SKU {sku.sku_id} product types {product_types_for_sku(sku)} do not match rule {rule.rule_id} scope {rule.applies_to}"


def scope_reason(sku: Sku, rule: Rule) -> str:
    """Return human-readable explanation of scope evaluation for sku and rule."""
    excl = exclude_reason(sku, rule)
    if excl:
        return excl
    return f"SKU {sku.sku_id} is in scope ({product_types_for_sku(sku)}) for rule {rule.rule_id}"


def applies_to_sku(rule: Rule, sku: Sku, state: str, at: datetime) -> bool:
    """Return True if rule applies to sku in state at time 'at'."""
    return applies_in_state(rule, state) and is_prohibited_at(rule, at) and sku_in_scope(sku, rule)


def scope_matrix(skus: list[Sku], rules: list[Rule]) -> dict:
    """Return mapping of sku_id -> list of rule_ids whose product scope matches the SKU."""
    return {s.sku_id: [r.rule_id for r in rules if sku_in_scope(s, r)] for s in skus}
