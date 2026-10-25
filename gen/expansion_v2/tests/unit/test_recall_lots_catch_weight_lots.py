"""Unit tests for recallstorm.recall_lots.catch_weight_lots."""
from recallstorm.recall_lots.catch_weight_lots import (
    CatchWeightLotRecord,
    VariableWeightBarcodeParser,
    calculate_meat_chub_yield_loss,
    estimate_unweighed_case_count,
    extract_embedded_price_weight_upc,
    flag_commingled_trim_batches,
    generate_scale_purge_directive,
    link_scale_plu_to_primal_lot,
    match_deli_slicing_batch_sheet,
    reconcile_case_weight_to_packages,
    trace_in_store_grind_logs,
    validate_tare_weight_deductions,
)


def test_catch_weight_lots():
    assert CatchWeightLotRecord().status == "ACTIVE"
    assert VariableWeightBarcodeParser().status == "ACTIVE"
    res = extract_embedded_price_weight_upc("201234005995")
    assert res["item_code"] == "01234" and res["price_usd"] == 5.99
    assert link_scale_plu_to_primal_lot("4011", "LOT1")["plu"] == "4011"
    assert calculate_meat_chub_yield_loss(50.0, 45.0) == 5.0
    assert reconcile_case_weight_to_packages(40.0, [20.0, 19.5])["variance_lb"] == 0.5
    assert trace_in_store_grind_logs("G1", ["L1"])["source_lots"] == ["L1"]
    assert match_deli_slicing_batch_sheet("SL1", "L1")["chub_lot"] == "L1"
    assert flag_commingled_trim_batches([{"batch_id": "B1", "lots": ["L1", "L2"]}], "L1") == ["B1"]
    assert estimate_unweighed_case_count(120.0, 40.0) == 3
    assert validate_tare_weight_deductions(2.05, 0.05) == 2.0
    assert generate_scale_purge_directive("WM1", ["PLU1"])["plus"] == ["PLU1"]
