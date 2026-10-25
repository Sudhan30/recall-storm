"""Edge and boundary tests for recallstorm.core.ids."""
import pytest
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


def test_determinism():
    assert make_run_id("s1", "2026-01-01T00:00:00Z") == make_run_id("s1", "2026-01-01T00:00:00Z")
    assert make_task_id("S1", "K1", Action.PULL, 0) == make_task_id("S1", "K1", "PULL", 0)
    assert make_evidence_id("K1", "R1") == make_evidence_id("K1", "R1")
    assert make_alloc_id("D1", "K2", "S1") == make_alloc_id("D1", "K2", "S1")
    assert make_manifest_id("T1", "D1") == make_manifest_id("T1", "D1")
    assert make_handoff_id(HandoffKind.FLOATER, "A1", "S1", 0) == make_handoff_id("FLOATER", "A1", "S1", 0)
    assert make_exc_id("S1", "N1", ExceptionKind.TOPSTOCK) == make_exc_id("S1", "N1", "TOPSTOCK")


def test_invalid_inputs():
    with pytest.raises(ValueError):
        make_run_id("", "2026-01-01")
    with pytest.raises(ValueError):
        make_run_id("s1", "")
    with pytest.raises(ValueError):
        make_task_id("S1", "K1", "INVALID_ACT", 0)
    with pytest.raises(ValueError):
        make_task_id("S1", "K1", Action.PULL, -1)
    with pytest.raises(ValueError):
        make_task_id("S1", "K1", Action.PULL, True)
    with pytest.raises(ValueError):
        make_evidence_id("", "R1")
    with pytest.raises(ValueError):
        make_alloc_id("DC", "", "ST")
    with pytest.raises(ValueError):
        make_manifest_id("", "DC")
    with pytest.raises(ValueError):
        make_handoff_id("BAD_KIND", "A", "B")
    with pytest.raises(ValueError):
        make_exc_id("S1", "N1", "BAD_KIND")
    with pytest.raises(ValueError):
        parse_id("NOHYPHEN")
    with pytest.raises(ValueError):
        parse_id("BAD-123")


def test_validate_id_prefix_edge():
    assert validate_id_prefix("", "RUN") is False
    assert validate_id_prefix(None, "RUN") is False  # type: ignore[arg-type]
    assert validate_id_prefix("RUN-", "RUN") is False
