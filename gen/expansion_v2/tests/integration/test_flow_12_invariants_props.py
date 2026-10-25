"""Integration test 12: Property-based cross-package invariant checks."""
from datetime import datetime
import random
from contract import DcStock, Sku, Store, StoreFormat, Truck, Verdict
from recallstorm.allocate import allocate_substitutes
from recallstorm.route import pack_returns
from recallstorm.route.capacity import capacity_check
from recallstorm.rules import evaluate_sku
from recallstorm.rules.red3 import red3_aliases, red3_rules


def test_cross_package_invariants_props():
    rng = random.Random(42)
    rules = red3_rules()
    dl = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    dep = datetime.fromisoformat("2026-12-31T08:00:00-08:00")

    stores = [
        Store(f"WM{i:03d}", StoreFormat.SUPERCENTER, "CA", "City", 34.0 + i * 0.1, -118.0, "D01", "DC_NORTH", "America/Los_Angeles")
        for i in range(8)
    ]
    trucks = [Truck(f"DC_NORTH-T{t}", "DC_NORTH", 3400.0, 40000.0, dep) for t in range(4)]

    for i, alias in enumerate(red3_aliases()):
        sku = Sku(f"S{i}", "07502264930572", "Item", "B", "baking", f"SUGAR, {alias}, WATER", True, False, 12, 2.0, 15.0)
        dec = evaluate_sku(sku, rules, "CA", dl)
        assert dec.verdict == Verdict.PULL
        assert sku.ingredients[dec.match_start : dec.match_end] == dec.match_text

        init_cases = rng.randint(5, 30)
        stock = [DcStock("DC_NORTH", "SUB1", init_cases)]
        demand = {(st.store_id, "SUB1"): rng.randint(1, 8) for st in stores}
        allocs = allocate_substitutes(demand, stock, stores)
        assert sum(a.qty_cases for a in allocs) <= init_cases

        pulled = {(st.store_id, sku.sku_id): rng.randint(1, 10) for st in stores}
        mnfs = pack_returns(pulled, [sku], trucks, stores)
        assert sum(sum(s.cases for s in m.stops) for m in mnfs) == sum(pulled.values())
        for m in mnfs:
            assert capacity_check(trucks[0], m.stops)
