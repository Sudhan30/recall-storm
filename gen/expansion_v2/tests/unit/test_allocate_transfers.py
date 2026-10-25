"""Unit tests for recallstorm.allocate.transfers."""
from datetime import datetime
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
from recallstorm.core.jsonl import validate_record


def test_allocate_transfers():
    as_of = datetime.fromisoformat("2026-12-30T18:00:00-08:00")
    deadline = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    win = dc_to_store_windows(as_of, deadline)
    alloc = Allocation("ALC-1", "DC_NORTH", "SUB1", "WM1", 3, 2)
    h = transfer_handoff(alloc, win)
    assert validate_record(h, "handoff") == []
    h_list = sub_transfers([alloc], win)
    assert validate_transfers(h_list) == []

    sku = Sku("SUB1", "00012345678905", "Sub", "B", "c", "I", True, False, 12, 2.0, 10.0)
    assert transfer_cube([alloc], {"SUB1": sku}) == 6.0
    assert transfer_weight([alloc], {"SUB1": sku}) == 30.0
    trk = Truck("DC_NORTH-T0", "DC_NORTH", 3400.0, 40000.0, deadline)
    assert "DC_NORTH-T0" in transfers_by_truck([alloc], [trk])
    assert transfer_summary([alloc])["total_cases"] == 3
    assert len(TransferPlan(h_list).handoffs) == 1
