"""Integration test 08: core -> gs1 -> inventory -> vendor -> dc_ops."""
from recallstorm.core.ids import make_handoff_id
from recallstorm.dc_ops.outbound_holds import pull_affected_cases_from_store_build_pallet
from recallstorm.dc_ops.receiving_holds import reject_affected_lot_at_inbound_scan
from recallstorm.gs1.lots import normalize_lot
from recallstorm.inventory.reverse_logistics_acct import generate_vendor_rma_reference_id
from recallstorm.vendor.chargeback_engine import calculate_per_store_execution_labor_fee
from recallstorm.vendor.onboarding_gates import screen_new_item_setup_for_banned_additives


def test_flow_vendor_and_dc_ops():
    lot = normalize_lot("Lot: L-2601")
    assert reject_affected_lot_at_inbound_scan(lot, {"L2601"})["rejected"] is True
    assert pull_affected_cases_from_store_build_pallet("LPN1", 20, 4)["remaining_cases"] == 16
    rma = generate_vendor_rma_reference_id("VND1", "REC1")
    assert rma == "RMA-VND1-REC1"
    fee = calculate_per_store_execution_labor_fee(10, 75.0)
    assert fee == 750.0
    screen = screen_new_item_setup_for_banned_additives("SUGAR, ERYTHROSINE")
    assert screen["blocked"] is True
    assert make_handoff_id("RETURN_CONSOLIDATION", "WM1", "DC1", 1).startswith("HND-")
