"""Edge case tests for recallstorm.dc_ops.carrier_tendering."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.dc_ops.carrier_tendering import (
    build_consolidated_recall_return_load,
    handle_carrier_turndown_waterfall_logic,
)


def test_carrier_tendering_edge():
    with pytest.raises(DataValidationError):
        build_consolidated_recall_return_load("DC1", 40, 50000.0)
    with pytest.raises(DataValidationError):
        handle_carrier_turndown_waterfall_logic(["SCAC1"], "SCAC1")
