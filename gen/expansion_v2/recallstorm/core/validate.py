"""Validation of contract entities and full datapacks."""
from __future__ import annotations

from contract import Associate, DataPack, Facing, Rule, Sku, Store, StoreFormat, Truck


def validate_sku(sku: Sku) -> list[str]:
    """Validate a Sku dataclass instance."""
    issues: list[str] = []
    if not isinstance(sku, Sku):
        return ["Not a Sku instance"]
    if not sku.sku_id.strip():
        issues.append("sku_id is empty")
    if not sku.gtin.strip() or not sku.gtin.isdigit():
        issues.append(f"Invalid gtin for {sku.sku_id}: {sku.gtin!r}")
    if sku.case_units <= 0:
        issues.append(f"case_units must be > 0 for {sku.sku_id}")
    if sku.case_cube_ft3 <= 0:
        issues.append(f"case_cube_ft3 must be > 0 for {sku.sku_id}")
    if sku.case_weight_lb <= 0:
        issues.append(f"case_weight_lb must be > 0 for {sku.sku_id}")
    return issues


def validate_store(store: Store) -> list[str]:
    """Validate a Store dataclass instance."""
    issues: list[str] = []
    if not isinstance(store, Store):
        return ["Not a Store instance"]
    if not store.store_id.strip():
        issues.append("store_id is empty")
    if not isinstance(store.format, StoreFormat):
        issues.append(f"Invalid store format: {store.format!r}")
    if not (-90.0 <= store.lat <= 90.0) or not (-180.0 <= store.lon <= 180.0):
        issues.append(f"Invalid coordinates for {store.store_id}")
    if not store.dc_id.strip():
        issues.append(f"dc_id is empty for {store.store_id}")
    if not store.tz.strip():
        issues.append(f"tz is empty for {store.store_id}")
    return issues


def validate_facing(facing: Facing) -> list[str]:
    """Validate a Facing dataclass instance."""
    issues: list[str] = []
    if not isinstance(facing, Facing):
        return ["Not a Facing instance"]
    if not facing.store_id.strip():
        issues.append("facing.store_id is empty")
    if not facing.sku_id.strip():
        issues.append("facing.sku_id is empty")
    if facing.units < 0:
        issues.append(f"facing.units < 0 for {facing.store_id}/{facing.sku_id}")
    if not facing.loc.aisle.strip() or facing.loc.bay < 0:
        issues.append(f"Invalid location for {facing.store_id}/{facing.sku_id}")
    return issues


def validate_associate(assoc: Associate) -> list[str]:
    """Validate an Associate dataclass instance."""
    issues: list[str] = []
    if not isinstance(assoc, Associate):
        return ["Not an Associate instance"]
    if not assoc.associate_id.strip():
        issues.append("associate_id is empty")
    if not assoc.is_floater and not assoc.store_id:
        issues.append(f"Non-floater {assoc.associate_id} missing store_id")
    if assoc.shift_end <= assoc.shift_start:
        issues.append(f"shift_end <= shift_start for {assoc.associate_id}")
    return issues


def validate_truck(truck: Truck) -> list[str]:
    """Validate a Truck dataclass instance."""
    issues: list[str] = []
    if not isinstance(truck, Truck):
        return ["Not a Truck instance"]
    if not truck.truck_id.strip():
        issues.append("truck_id is empty")
    if not truck.dc_id.strip():
        issues.append(f"dc_id is empty for {truck.truck_id}")
    if truck.cube_ft3 <= 0 or truck.weight_lb <= 0:
        issues.append(f"Non-positive capacity for {truck.truck_id}")
    return issues


def validate_rule(rule: Rule) -> list[str]:
    """Validate a Rule dataclass instance."""
    issues: list[str] = []
    if not isinstance(rule, Rule):
        return ["Not a Rule instance"]
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
    """Collect validation issues across all collections in a DataPack."""
    out: dict[str, list[str]] = {
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
        out["skus"].extend(validate_sku(s))
    for st in pack.stores:
        out["stores"].extend(validate_store(st))
    for f in pack.facings:
        out["facings"].extend(validate_facing(f))
        if f.store_id not in store_ids:
            out["refs"].append(f"Facing references unknown store {f.store_id}")
        if f.sku_id not in sku_ids:
            out["refs"].append(f"Facing references unknown sku {f.sku_id}")
    for a in pack.associates:
        out["associates"].extend(validate_associate(a))
    for t in pack.trucks:
        out["trucks"].extend(validate_truck(t))
    for r in pack.rules:
        out["rules"].extend(validate_rule(r))
    return out


def validate_datapack(pack: DataPack) -> list[str]:
    """Return a flat list of all validation issues in a DataPack."""
    grouped = collect_issues(pack)
    flat: list[str] = []
    for k in ("skus", "stores", "facings", "associates", "trucks", "rules", "refs"):
        flat.extend(grouped[k])
    return flat


def issues_summary(issues: dict[str, list[str]]) -> dict[str, int]:
    """Return counts of issues per category plus total."""
    counts = {k: len(v) for k, v in issues.items()}
    counts["total"] = sum(counts.values())
    return counts
