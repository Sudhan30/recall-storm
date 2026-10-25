"""Integration test 03: openFDA enforcement -> GS1 GTIN/Lot/AI/DigitalLink -> Scenario GS1 lot pull."""
from contract import load_datapack
from recallstorm.core import validate_id_prefix
from recallstorm.gs1 import (
    build_digital_link,
    digital_link_gtin,
    digital_link_lot,
    is_valid_gtin,
    lot_matches_recall,
    match_recall_to_skus,
)
from recallstorm.ingest import enforcement_to_recall, sample_datapack
from recallstorm.scenario_gs1 import recall_from_openfda, recall_plan


def test_flow_03_gs1_lot_recall():
    pack = sample_datapack(load_datapack("data"), max_stores=3, seed=42)
    report = {
        "recall_number": "F-2026-991",
        "status": "Ongoing",
        "product_description": "Rainbow Sprinkles GTIN 07502264930572",
        "code_info": "Lot: L2601A, Batch B9920; 2026-10-01 to 2026-12-31",
        "reason_for_recall": "Undeclared FD&C Red No. 3",
        "distribution_pattern": "CA, OR",
    }
    rec = enforcement_to_recall(report)
    assert is_valid_gtin(rec["gtins"][0]) is True

    uri = build_digital_link(rec["gtins"][0], lot=rec["lot_codes"][0], expiry="261231")
    assert digital_link_gtin(uri) == "07502264930572"
    dl_lot = digital_link_lot(uri)
    assert dl_lot is not None and lot_matches_recall(dl_lot, rec["lot_codes"]) is True

    matched = match_recall_to_skus(rec, pack.skus)
    assert len(matched) >= 1

    scen = recall_from_openfda(report)
    plan_recs = recall_plan(scen, pack)
    ev_recs = [r for r in plan_recs if r["type"] == "evidence"]
    assert len(ev_recs) >= 1
    assert validate_id_prefix(ev_recs[0]["evidence_id"], "EVD")
