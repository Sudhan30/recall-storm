"""Load, write, filter, and hash DataPacks."""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
from pathlib import Path

from contract import DataPack, load_datapack
from recallstorm.core.jsonl import write_jsonl


def load_datapack_extended(data_dir: str) -> DataPack:
    """Load a DataPack from data_dir using contract.load_datapack."""
    return load_datapack(data_dir)


def write_datapack(pack: DataPack, out_dir: str) -> dict:
    """Write a DataPack out to JSONL/JSON files in out_dir."""
    p = Path(out_dir)
    p.mkdir(parents=True, exist_ok=True)
    counts = {
        "skus": write_jsonl(str(p / "skus.jsonl"), [asdict(s) for s in pack.skus]),
        "stores": write_jsonl(
            str(p / "stores.jsonl"),
            [{**asdict(st), "format": st.format.value} for st in pack.stores],
        ),
        "facings": write_jsonl(str(p / "facings.jsonl"), [asdict(f) for f in pack.facings]),
    }
    (p / "substitutes.json").write_text(json.dumps(pack.substitutes, sort_keys=True), encoding="utf-8")
    return counts


def datapack_stats(pack: DataPack) -> dict:
    """Compute counts of all collections in a DataPack."""
    return {
        "skus": len(pack.skus),
        "stores": len(pack.stores),
        "facings": len(pack.facings),
        "associates": len(pack.associates),
        "trucks": len(pack.trucks),
        "dc_stock": len(pack.dc_stock),
        "notes": len(pack.notes),
        "rules": len(pack.rules),
    }


def filter_by_state(pack: DataPack, state: str) -> DataPack:
    """Filter a DataPack to stores (and their facings/associates/notes) in state."""
    st_code = state.upper().strip()
    store_ids = {s.store_id for s in pack.stores if s.state.upper() == st_code}
    return filter_by_stores(pack, store_ids)


def filter_by_stores(pack: DataPack, store_ids: set[str]) -> DataPack:
    """Filter a DataPack to a specific set of store_ids."""
    stores = [s for s in pack.stores if s.store_id in store_ids]
    districts = {s.district for s in stores}
    dcs = {s.dc_id for s in stores}
    return DataPack(
        skus=list(pack.skus),
        stores=stores,
        facings=[f for f in pack.facings if f.store_id in store_ids],
        associates=[
            a for a in pack.associates if (a.store_id in store_ids) or (a.is_floater and a.district in districts)
        ],
        trucks=[t for t in pack.trucks if t.dc_id in dcs],
        dc_stock=[d for d in pack.dc_stock if d.dc_id in dcs],
        substitutes=dict(pack.substitutes),
        notes=[n for n in pack.notes if n.store_id in store_ids],
        rules=list(pack.rules),
        as_of=pack.as_of,
    )


def subset_skus(pack: DataPack, sku_ids: set[str]) -> DataPack:
    """Filter a DataPack to a specific set of sku_ids."""
    return DataPack(
        skus=[s for s in pack.skus if s.sku_id in sku_ids],
        stores=list(pack.stores),
        facings=[f for f in pack.facings if f.sku_id in sku_ids],
        associates=list(pack.associates),
        trucks=list(pack.trucks),
        dc_stock=[d for d in pack.dc_stock if d.sku_id in sku_ids],
        substitutes={k: v for k, v in pack.substitutes.items() if k in sku_ids},
        notes=list(pack.notes),
        rules=list(pack.rules),
        as_of=pack.as_of,
    )


def sample_datapack(pack: DataPack, max_stores: int = 5, max_skus: int = 10) -> DataPack:
    """Return a deterministic sample of a DataPack."""
    store_ids = {s.store_id for s in sorted(pack.stores, key=lambda x: x.store_id)[:max_stores]}
    sku_ids = {s.sku_id for s in sorted(pack.skus, key=lambda x: x.sku_id)[:max_skus]}
    return subset_skus(filter_by_stores(pack, store_ids), sku_ids)


def datapack_hash(pack: DataPack) -> str:
    """Compute a deterministic SHA-256 hash of a DataPack's core stats and IDs."""
    payload = {
        "skus": sorted(s.sku_id for s in pack.skus),
        "stores": sorted(s.store_id for s in pack.stores),
        "facings": len(pack.facings),
        "rules": sorted(r.rule_id for r in pack.rules),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def compare_datapacks(p1: DataPack, p2: DataPack) -> dict:
    """Return differences in counts between two DataPacks."""
    s1, s2 = datapack_stats(p1), datapack_stats(p2)
    return {k: s2[k] - s1[k] for k in s1}
