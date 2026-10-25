"""Unit tests for recallstorm.pricing.markdown_controls."""
from recallstorm.pricing.markdown_controls import (
    ClearanceTagBlocker,
    MarkdownLockoutEngine,
    audit_recent_markdown_scan_history,
    block_handheld_cvp_yellow_sticker_print,
    enforce_zero_salvage_price_floor,
    flag_suspicious_pre_recall_markdowns,
    freeze_automated_cadence_markdowns,
    invalidate_existing_clearance_barcodes,
    prevent_manager_special_price_override,
    recall_discounted_bakery_day_old_racks,
    reconcile_markdown_journal_reversals,
    reverse_pending_price_change_batches,
)


def test_markdown_controls():
    assert MarkdownLockoutEngine().status == "ACTIVE"
    assert ClearanceTagBlocker().status == "ACTIVE"
    assert freeze_automated_cadence_markdowns("S1")["frozen"] is True
    assert block_handheld_cvp_yellow_sticker_print("S1", "WM1")["print_blocked"] is True
    assert invalidate_existing_clearance_barcodes("CVP123")["invalidated"] is True
    assert recall_discounted_bakery_day_old_racks("WM1")["sweep_dispatched"] is True
    assert prevent_manager_special_price_override("S1")["blocked"] is True
    assert audit_recent_markdown_scan_history([{"store_id": "WM1", "sku_id": "S1"}], "S1") == ["WM1"]
    assert reverse_pending_price_change_batches(["B2", "B1"]) == ["B1", "B2"]
    assert flag_suspicious_pre_recall_markdowns("WM1", 75.0)["flagged"] is True
    assert reconcile_markdown_journal_reversals(10, 1.5) == 15.0
    assert enforce_zero_salvage_price_floor("S1")["liquidation_prohibited"] is True
