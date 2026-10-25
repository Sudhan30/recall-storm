"""Edge case tests for recallstorm.dc_ops.pick_face_blocks."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.dc_ops.pick_face_blocks import (
    audit_partial_case_pick_remnants,
    trigger_immediate_slot_purge_to_cage,
)


def test_pick_face_blocks_edge():
    with pytest.raises(DataValidationError):
        trigger_immediate_slot_purge_to_cage("DC1", "S1", -1)
    with pytest.raises(DataValidationError):
        audit_partial_case_pick_remnants("S1", -5)
