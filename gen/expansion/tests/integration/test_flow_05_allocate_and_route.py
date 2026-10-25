"""Integration test 05: Rules -> Store exceptions -> Allocate demand & transfers -> Route returns & packing."""
from datetime import datetime
from contract import ExceptionKind, load_datapack
from recallstorm.allocate import (
    allocate_substitutes,
    demand_from_facings,
    never_exceeds_stock,
    sub_transfers,
    validate_transfers,
)
from recallstorm.core import validate_id_prefix
from recallstorm.ingest import sample_datapack
from recallstorm.route import (
    overload_report,
    pack_returns,
    returned_cases,
    validate_returns,
)
from recallstorm.rules import evaluate_pack
from recallstorm.store import exception_kind_for_text


def test_flow_05_allocate_and_route():
    pack = sample_datapack(load_datapack("data"), max_stores=5, seed=42)
    dl = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    decisions = evaluate_pack(pack, "CA", dl)
    skus_by_id = {s.sku_id: s for s in pack.skus}
    stores_by_id = {s.store_id: s for s in pack.stores}
    trucks_by_id = {t.truck_id: t for t in pack.trucks}

    # Allocate substitutes
    demand = demand_from_facings(pack.facings, decisions, pack.substitutes, skus_by_id, pack.dc_stock, stores_by_id)
    allocs = allocate_substitutes(demand, pack.dc_stock, pack.stores)
    assert never_exceeds_stock(pack.dc_stock, allocs) is True
    for a in allocs:
        assert validate_id_prefix(a.alloc_id, "ALC")

    handoffs = sub_transfers(allocs, ("2026-12-31T06:00:00-08:00", "2026-12-31T12:00:00-08:00"))
    assert validate_transfers(handoffs, allocs) == []

    # Route returns
    dsd_stores = {n.store_id for n in pack.notes if exception_kind_for_text(n.text) == ExceptionKind.DSD_VENDOR_PULL}
    pulled = returned_cases(pack.facings, decisions, skus_by_id, dsd_stores)
    manifests = pack_returns(pulled, pack.skus, pack.trucks, pack.stores)
    assert overload_report(manifests, trucks_by_id) == []
    assert validate_returns(pulled, manifests) == []
