"""Edge case tests for recallstorm.comms.shelf_signage_gen."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.comms.shelf_signage_gen import (
    map_placard_count_to_aisle_facings,
    schedule_fourteen_day_sign_takedown,
)


def test_shelf_signage_gen_edge():
    assert map_placard_count_to_aisle_facings(0) == 0
    with pytest.raises(DataValidationError):
        schedule_fourteen_day_sign_takedown("2027-01-01", 0)
