"""Integration test 03: core -> rules -> store -> labor -> allocate."""
from datetime import datetime
from contract import DcStock, Facing, Location, Sku, Store, StoreFormat
from recallstorm.allocate import allocate_substitutes
from recallstorm.allocate.demand import demand_from_facings
from recallstorm.core.clock import is_before_deadline
from recallstorm.ingest.staffing import parse_roster_row
from recallstorm.labor.assign import assign_tasks
from recallstorm.rules import evaluate_sku
from recallstorm.rules.red3 import red3_rules
from recallstorm.store.facings import affected_facings


def test_flow_labor_and_allocate():
    s1 = Sku("FDC1034191", "07502264930572", "Sprinkles", "B", "baking", "SUGAR, FD&C RED #3.", True, False, 6, 2.0, 10.0)
    sub = Sku("VAR0172", "00012345678905", "Sub", "B", "baking", "SUGAR.", True, False, 6, 2.0, 10.0)
    st = Store("WM1563", StoreFormat.SUPERCENTER, "CA", "Lancaster", 34.6, -118.1, "D06", "DC_CENTRAL", "America/Los_Angeles")
    f = Facing("WM1563", "FDC1034191", Location("A01", 1, 1, 1), 12)
    dl = datetime.fromisoformat("2027-01-01T00:00:00-08:00")

    dec = evaluate_sku(s1, red3_rules(), "CA", dl)
    decs = {"FDC1034191": dec}
    assert affected_facings([f], decs) == [f]

    demand = demand_from_facings([f], decs, {"FDC1034191": ["VAR0172"]}, {"VAR0172": sub}, [DcStock("DC_CENTRAL", "VAR0172", 5)])
    allocs = allocate_substitutes(demand, [DcStock("DC_CENTRAL", "VAR0172", 5)], [st])
    assert len(allocs) == 1 and allocs[0].qty_cases == 2

    assoc = parse_roster_row(
        {
            "associate_id": "WM1563-A04",
            "store_id": "WM1563",
            "district": "D06",
            "is_floater": False,
            "shift_start": "2026-12-30T22:00:00-08:00",
            "shift_end": "2026-12-31T06:00:00-08:00",
        }
    )
    assigned = assign_tasks([{"task_id": "T1", "store_id": "WM1563", "action": "PULL", "qty_units": 12}], [assoc], deadline=dl)
    assert is_before_deadline(datetime.fromisoformat(assigned[0]["window"][1]), dl)
