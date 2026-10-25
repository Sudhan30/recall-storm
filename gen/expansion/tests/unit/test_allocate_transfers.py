"""Unit tests for recallstorm.allocate.transfers."""
from datetime import datetime, timezone
from contract import Allocation, Sku, Truck
from recallstorm.allocate.transfers import (
    TransferPlan,
    dc_to_store_windows,
    sub_transfers,
    transfer_cube,
    transfer_handoff,
    transfer_summary,
    transfer_weight,
    transfers_by_truck,
    validate_transfers,
)


def test_transfers_functions():
    w = dc_to_store_windows("2026-12-30T18:00:00-08:00", "2027-01-01T00:00:00-08:00")
    alloc = Allocation("ALC-1", "DC_NORTH", "SUB1", "WM1", 3, 2)
    h = transfer_handoff(alloc, w, 0)
    assert h["kind"] == "SUB_TRANSFER"
    hlist = sub_transfers([alloc], w)
    assert validate_transfers(hlist, [alloc]) == []
    sku = Sku("SUB1", "00012345678905", "Sub", "B", "c", "SUGAR", True, False, 12, 2.0, 10.0)
    assert transfer_cube([alloc], {"SUB1": sku}) == 6.0
    assert transfer_weight([alloc], {"SUB1": sku}) == 30.0
    t = Truck("DC_NORTH-T0", "DC_NORTH", 3400.0, 40000.0, datetime(2026, 12, 31, 8, 0, tzinfo=timezone.utc))
    assert "DC_NORTH-T0" in transfers_by_truck([alloc], [t])
    assert transfer_summary([alloc])["total_cases"] == 3
    tp = TransferPlan(tuple(hlist), 3)
    assert tp.total_cases == 3
