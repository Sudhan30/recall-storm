"""Validation functions for contract dataclasses and DataPack."""
from __future__ import annotations

from contract import (
    Associate,
    DataPack,
    Facing,
    Rule,
    Sku,
    Store,
    StoreFormat,
    Truck,
)


def validate_sku(sku: Sku) -> list[str]:
    """Validate a Sku instance."""
    if not isinstance(sku, Sku):
        return ["Not a Sku instance"]
    issues: list[str] = []
    if not sku.sku_id.strip():
        issues.append("sku_id is empty")
    if not sku.gtin.strip() or not sku.gtin.isdigit():
        issues.append(f"invalid gtin for {sku.sku_id}: {sku.gtin}")
    if sku.case_units <= 0:
        issues.append(f"case_units must be > 0 for {sku.sku_id}")
    if sku.case_cube_ft3 <= 0:
        issues.append(f"case_cube_ft3 must be > 0 for {sku.sku_id}")
    if sku.case_weight_lb <= 0:
        issues.append(f"case_weight_lb must be > 0 for {sku.sku_id}")
    return issues


def validate_store(store: Store) -> list[str]:
    """Validate a Store instance."""
    if not isinstance(store, Store):
        return ["Not a Store instance"]
    issues: list[str] = []
    if not store.store_id.strip():
        issues.append("store_id is empty")
    if not isinstance(store.format, StoreFormat) and store.format not in {f.value for f in StoreFormat}:
        issues.append(f"invalid format for {store.store_id}: {store.format}")
    if not (-90.0 <= store.lat <= 90.0) or not (-180.0 <= store.lon <= 180.0):
        issues.append(f"invalid coordinates for {store.store_id}")
    if not store.dc_id.strip():
        issues.append(f"empty dc_id for {store.store_id}")
    if not store.tz.strip():
        issues.append(f"empty tz for {store.store_id}")
    return issues


def validate_facing(facing: Facing) -> list[str]:
    """Validate a Facing instance."""
    if not isinstance(facing, Facing):
        return ["Not a Facing instance"]
    issues: list[str] = []
    if not facing.store_id.strip():
        issues.append("facing store_id is empty")
    if not facing.sku_id.strip():
        issues.append("facing sku_id is empty")
    if facing.units <= 0:
        issues.append(f"facing units must be > 0 at {facing.store_id}/{facing.sku_id}")
    if not facing.loc.aisle.strip() or facing.loc.bay <= 0 or facing.loc.shelf <= 0 or facing.loc.pos <= 0:
        issues.append(f"invalid location at {facing.store_id}/{facing.sku_id}")
    return issues


def validate_associate(assoc: Associate) -> list[str]:
    """Validate an Associate instance."""
    if not isinstance(assoc, Associate):
        return ["Not an Associate instance"]
    issues: list[str] = []
    if not assoc.associate_id.strip():
        issues.append("associate_id is empty")
    if not assoc.is_floater and not assoc.store_id:
        issues.append(f"non-floater {assoc.associate_id} missing store_id")
    if assoc.shift_end <= assoc.shift_start:
        issues.append(f"shift_end <= shift_start for {assoc.associate_id}")
    return issues


def validate_truck(truck: Truck) -> list[str]:
    """Validate a Truck instance."""
    if not isinstance(truck, Truck):
        return ["Not a Truck instance"]
    issues: list[str] = []
    if not truck.truck_id.strip():
        issues.append("truck_id is empty")
    if not truck.dc_id.strip():
        issues.append(f"dc_id is empty for {truck.truck_id}")
    if truck.cube_ft3 <= 0 or truck.weight_lb <= 0:
        issues.append(f"non-positive capacity for {truck.truck_id}")
    return issues


def validate_rule(rule: Rule) -> list[str]:
    """Validate a Rule instance."""
    if not isinstance(rule, Rule):
        return ["Not a Rule instance"]
    issues: list[str] = []
    if not rule.rule_id.strip():
        issues.append("rule_id is empty")
    if not rule.additive.strip():
        issues.append(f"additive is empty for {rule.rule_id}")
    if not rule.aliases:
        issues.append(f"aliases empty for {rule.rule_id}")
    if not rule.jurisdictions:
        issues.append(f"jurisdictions empty for {rule.rule_id}")
    if not rule.applies_to:
        issues.append(f"applies_to empty for {rule.rule_id}")
    return issues


def collect_issues(pack: DataPack) -> dict[str, list[str]]:
    """Collect validation issues grouped by entity category."""
    if not isinstance(pack, DataPack):
        return {"pack": ["Not a DataPack instance"]}
    issues: dict[str, list[str]] = {
        "skus": [],
        "stores": [],
        "facings": [],
        "associates": [],
        "trucks": [],
        "rules": [],
        "refs": [],
    }
    sku_ids = {s.sku_id for s in pack.skus}
    store_ids = {s.store_id for s in pack.stores}
    for s in pack.skus:
        issues["skus"].extend(validate_sku(s))
    for st in pack.stores:
        issues["stores"].extend(validate_store(st))
    for f in pack.facings:
        issues["facings"].extend(validate_facing(f))
        if f.store_id not in store_ids:
            issues["refs"].append(f"facing references unknown store {f.store_id}")
        if f.sku_id not in sku_ids:
            issues["refs"].append(f"facing references unknown sku {f.sku_id}")
    for a in pack.associates:
        issues["associates"].extend(validate_associate(a))
    for t in pack.trucks:
        issues["trucks"].extend(validate_truck(t))
    for r in pack.rules:
        issues["rules"].extend(validate_rule(r))
    return issues


def validate_datapack(pack: DataPack) -> list[str]:
    """Validate an entire DataPack and return a flat list of issues."""
    grouped = collect_issues(pack)
    flat: list[str] = []
    for group_list in grouped.values():
        flat.extend(group_list)
    return flat


def issues_summary(issues: dict[str, list[str]]) -> dict[str, int]:
    """Summarize issue counts per category plus total."""
    out = {k: len(v) for k, v in issues.items()}
    out["total"] = sum(out.values())
    return out
