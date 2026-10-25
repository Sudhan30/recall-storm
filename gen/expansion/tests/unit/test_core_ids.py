"""Unit tests for recallstorm.core.ids."""
from datetime import datetime, timezone
from contract import Action, ExceptionKind, HandoffKind
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


def test_make_run_id():
    dt = datetime(2026, 12, 30, 18, 0, tzinfo=timezone.utc)
    rid = make_run_id("ca_red3", dt)
    assert rid.startswith("RUN-ca_red3-")
    assert validate_id_prefix(rid, "RUN")


def test_make_task_id():
    tid = make_task_id("WM1563", "FDC1034191", Action.PULL, 1)
    assert tid.startswith("TSK-WM1563-FDC1034191-001-")
    assert validate_id_prefix(tid, "TSK")


def test_make_evidence_id():
    eid = make_evidence_id("FDC1034191", "CA_AB418_RED3")
    assert eid.startswith("EVD-FDC1034191-CA_AB418_RED3-")
    assert validate_id_prefix(eid, "EVD")


def test_make_alloc_id():
    aid = make_alloc_id("DC_NORTH", "VAR0172", "WM1575")
    assert aid.startswith("ALC-DC_NORTH-VAR0172-WM1575-")
    assert validate_id_prefix(aid, "ALC")


def test_make_manifest_id():
    mid = make_manifest_id("DC_NORTH-T0", "DC_NORTH")
    assert mid.startswith("MNF-DC_NORTH-DC_NORTH-T0-")
    assert validate_id_prefix(mid, "MNF")


def test_make_handoff_id():
    hid = make_handoff_id(HandoffKind.SUB_TRANSFER, "DC_NORTH", "WM1575", 2)
    assert hid.startswith("HND-SUB_TRANSFER-DC_NORTH-WM1575-02-")
    assert validate_id_prefix(hid, "HND")


def test_make_exc_id():
    xid = make_exc_id("SAMS4735", "N0000", ExceptionKind.ENDCAP_DISPLAY)
    assert xid.startswith("EXC-SAMS4735-N0000-")
    assert validate_id_prefix(xid, "EXC")


def test_parse_id_and_validate():
    eid = make_evidence_id("SKU1", "R1")
    prefix, body = parse_id(eid)
    assert prefix == "EVD"
    assert body.startswith("SKU1-R1-")
    assert validate_id_prefix(eid, "EVD") is True
    assert validate_id_prefix(eid, "TSK") is False
