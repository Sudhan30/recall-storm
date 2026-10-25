"""Edge case tests for recallstorm.vendor.import_broker_holds."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.vendor.import_broker_holds import (
    hold_deconsolidated_transload_pallets,
    track_notice_of_fda_action_detention,
)


def test_import_broker_holds_edge():
    with pytest.raises(DataValidationError):
        hold_deconsolidated_transload_pallets("C1", [])
    with pytest.raises(DataValidationError):
        track_notice_of_fda_action_detention("ENT1", "INVALID_STATUS")
