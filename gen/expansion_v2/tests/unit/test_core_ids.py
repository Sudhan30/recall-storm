"""Unit tests for recallstorm.core.ids."""
from recallstorm.core.ids import (
    make_alloc_id,
    make_evidence_id,
    make_exc_id,
    make_handoff_id,
    make_manifest_id,
    make_run_id,
    make_task_id,
    parse_id,
    validate_id_prefix,
)


def test_make_ids_basic():
    run_id = make_run_id("ca_red3", "2026-12-30T18:00:00-08:00")
    assert validate_id_prefix(run_id, "RUN")
    tsk_id = make_task_id("WM1563", "FDC1034191", "PULL", 1)
    assert tsk_id == "TSK-WM1563-FDC1034191-PULL-0001"
    evd_id = make_evidence_id("FDC1034191", "CA_AB418_RED3")
    assert evd_id == "EVD-FDC1034191-CA_AB418_RED3"
    alc_id = make_alloc_id("DC_NORTH", "WM1575", "VAR0172")
    assert alc_id == "ALC-DC_NORTH-WM1575-VAR0172"
    mnf_id = make_manifest_id("DC_NORTH-T0", 0)
    assert mnf_id == "MNF-DC_NORTH-T0-000"
    hnd_id = make_handoff_id("FLOATER", "D01", "WM1575", 2)
    assert hnd_id == "HND-FLOATER-D01-WM1575-002"
    exc_id = make_exc_id("SAMS4735", "N0000")
    assert exc_id == "EXC-SAMS4735-N0000"


def test_parse_id():
    parsed = parse_id("EVD-SKU1-RULE1")
    assert parsed["prefix"] == "EVD"
    assert parsed["parts"] == ["SKU1", "RULE1"]
