"""Edge case tests for recallstorm.vendor.dsd_coordination."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.vendor.dsd_coordination import (
    audit_driver_pulled_case_counts_at_exit,
    notify_dsd_bottler_bakery_dispatcher,
)


def test_dsd_coordination_edge():
    with pytest.raises(DataValidationError):
        notify_dsd_bottler_bakery_dispatcher("FL1", [])
    assert audit_driver_pulled_case_counts_at_exit(10, 7)["shortage"] == 3
