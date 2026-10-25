"""Edge case tests for recallstorm.dc_ops.outbound_holds."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.dc_ops.outbound_holds import (
    pull_affected_cases_from_store_build_pallet,
    re_cube_shorted_store_delivery_trailer,
)


def test_outbound_holds_edge():
    with pytest.raises(DataValidationError):
        pull_affected_cases_from_store_build_pallet("LPN1", 10, 15)
    with pytest.raises(DataValidationError):
        re_cube_shorted_store_delivery_trailer(100.0, 200.0)
