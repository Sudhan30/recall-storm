"""DataPack loading, writing, subsetting, sampling, and deterministic hashing."""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import asdict
from pathlib import Path
from contract import DataPack, load_datapack
from recallstorm.core.errors import DataValidationError
from recallstorm.core.jsonl import write_jsonl


def load_datapack_extended(data_dir: str | Path) -> DataPack:
    """Load a DataPack from data_dir using contract.load_datapack."""
    p = Path(data_dir)
    if not p.exists():
        raise DataValidationError(f"Data directory not found: {p}")
    return load_datapack(str(p))


def write_datapack(pack: DataPack, out_dir: str | Path) -> dict[str, int]:
    """Write a DataPack out to JSONL/JSON files in out_dir."""
    if not isinstance(pack, DataPack):
        raise TypeError("pack must be a DataPack")
    base = Path(out_dir)
    base.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    counts["skus"] = write_jsonl(base / "skus.jsonl", [asdict(s) for s in pack.skus])
    counts["stores"] = write_jsonl(
        base / "stores.jsonl",
        [{**asdict(s), "format": s.format.value} for s in pack.stores],
    )
    counts["facings"] = write_jsonl(base / "facings.jsonl", [asdict(f) for f in pack.facings])
    counts["associates"] = write_jsonl(
        base / "associates.jsonl",
        [
            {
                **asdict(a),
                "shift_start": a.shift_start.isoformat(),
                "shift_end": a.shift_end.isoformat(),
            }
            for a in pack.associates
        ],
    )
    counts["trucks"] = write_jsonl(
        base / "trucks.jsonl",
        [{**asdict(t), "depart": t.depart.isoformat()} for t in pack.trucks],
    )
    counts["dc_stock"] = write_jsonl(base / "dc_stock.jsonl", [asdict(d) for d in pack.dc_stock])
    counts["notes"] = write_jsonl(base / "notes.jsonl", [asdict(n) for n in pack.notes])
    counts["rules"] = write_jsonl(
        base / "rules.jsonl",
        [
            {
                **asdict(r),
                "aliases": list(r.aliases),
                "jurisdictions": list(r.jurisdictions),
                "applies_to": list(r.applies_to),
                "effective": r.effective.isoformat(),
            }
            for r in pack.rules
        ],
    )
    (base / "substitutes.json").write_text(json.dumps(pack.substitutes, sort_keys=True), encoding="utf-8")
    return counts


def datapack_stats(pack: DataPack) -> dict[str, int]:
    """Return entity counts for a DataPack."""
    if not isinstance(pack, DataPack):
        raise TypeError("pack must be a DataPack")
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


def filter_by_stores(pack: DataPack, store_ids: set[str] | list[str]) -> DataPack:
    """Subset a DataPack to the specified store_ids."""
    st_set = set(store_ids)
    stores = [s for s in pack.stores if s.store_id in st_set]
    districts = {s.district for s in stores}
    dcs = {s.dc_id for s in stores}
    facings = [f for f in pack.facings if f.store_id in st_set]
    associates = [
        a for a in pack.associates if a.store_id in st_set or (a.is_floater and a.district in districts)
    ]
    trucks = [t for t in pack.trucks if t.dc_id in dcs]
    dc_stock = [d for d in pack.dc_stock if d.dc_id in dcs]
    notes = [n for n in pack.notes if n.store_id in st_set]
    return DataPack(
        skus=list(pack.skus),
        stores=stores,
        facings=facings,
        associates=associates,
        trucks=trucks,
        dc_stock=dc_stock,
        substitutes=dict(pack.substitutes),
        notes=notes,
        rules=list(pack.rules),
        as_of=pack.as_of,
    )


def filter_by_state(pack: DataPack, state: str) -> DataPack:
    """Subset a DataPack to stores in a 2-letter state."""
    st = state.strip().upper()
    ids = {s.store_id for s in pack.stores if s.state.upper() == st}
    return filter_by_stores(pack, ids)


def sample_datapack(pack: DataPack, max_stores: int = 5, seed: int = 42) -> DataPack:
    """Deterministically sample up to max_stores from a DataPack."""
    if max_stores <= 0:
        raise ValueError("max_stores must be positive")
    rng = random.Random(seed)
    sorted_ids = sorted(s.store_id for s in pack.stores)
    chosen = rng.sample(sorted_ids, min(max_stores, len(sorted_ids)))
    return filter_by_stores(pack, chosen)


def subset_skus(pack: DataPack, sku_ids: set[str] | list[str]) -> DataPack:
    """Subset a DataPack to the given sku_ids."""
    sk_set = set(sku_ids)
    return DataPack(
        skus=[s for s in pack.skus if s.sku_id in sk_set],
        stores=list(pack.stores),
        facings=[f for f in pack.facings if f.sku_id in sk_set],
        associates=list(pack.associates),
        trucks=list(pack.trucks),
        dc_stock=[d for d in pack.dc_stock if d.sku_id in sk_set],
        substitutes={k: v for k, v in pack.substitutes.items() if k in sk_set},
        notes=list(pack.notes),
        rules=list(pack.rules),
        as_of=pack.as_of,
    )


def datapack_hash(pack: DataPack) -> str:
    """Compute a deterministic SHA-256 hex digest of a DataPack's stats and IDs."""
    stats = datapack_stats(pack)
    sku_ids = sorted(s.sku_id for s in pack.skus)
    store_ids = sorted(s.store_id for s in pack.stores)
    payload = json.dumps({"stats": stats, "skus": sku_ids, "stores": store_ids}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def compare_datapacks(p1: DataPack, p2: DataPack) -> dict[str, int]:
    """Return entity count differences (p2 - p1) across two DataPacks."""
    s1 = datapack_stats(p1)
    s2 = datapack_stats(p2)
    return {k: s2[k] - s1[k] for k in s1}
