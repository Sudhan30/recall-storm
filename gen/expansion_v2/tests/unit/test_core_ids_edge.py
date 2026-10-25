"""Edge case tests for recallstorm.core.ids."""
import pytest
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


def test_invalid_inputs():
    with pytest.raises(ValueError):
        make_run_id("")
    with pytest.raises(ValueError):
        make_task_id("WM1", "SKU1", "PULL", -1)
    with pytest.raises(ValueError):
        make_manifest_id("T0", -5)
    with pytest.raises(ValueError):
        make_handoff_id("FLOATER", "A", "B", -1)
    with pytest.raises(ValueError):
        parse_id("BADPREFIX-123")
    with pytest.raises(ValueError):
        parse_id("NOHYPHEN")


def test_special_characters_cleaned():
    assert make_exc_id("WM 1563!", "N#001") == "EXC-WM_1563-N_001"
    assert make_evidence_id("SKU/1", "R:2") == "EVD-SKU_1-R_2"
    assert make_alloc_id("DC 1", "ST 2", "SUB 3") == "ALC-DC_1-ST_2-SUB_3"
    assert not validate_id_prefix("INVALID", "RUN")
    assert not validate_id_prefix(123, "RUN")  # type: ignore[arg-type]
