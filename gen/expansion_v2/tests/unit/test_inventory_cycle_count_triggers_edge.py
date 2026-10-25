"""Edge case tests for recallstorm.inventory.cycle_count_triggers."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.inventory.cycle_count_triggers import (
    require_dual_associate_blind_count,
    validate_case_pack_unit_conversion,
)


def test_cycle_count_triggers_edge():
    assert require_dual_associate_blind_count(10, 12)["matched"] is False
    with pytest.raises(DataValidationError):
        validate_case_pack_unit_conversion(-1, 0, 12)
