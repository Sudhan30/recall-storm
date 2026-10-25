"""Edge case tests for recallstorm.pricing.pos_sale_blocks."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.pricing.pos_sale_blocks import (
    audit_pos_lock_coverage_by_store,
    verify_lane_sync_heartbeat_status,
)


def test_pos_sale_blocks_edge():
    with pytest.raises(DataValidationError):
        verify_lane_sync_heartbeat_status(25, 20)
    with pytest.raises(DataValidationError):
        audit_pos_lock_coverage_by_store(-1, 10)
