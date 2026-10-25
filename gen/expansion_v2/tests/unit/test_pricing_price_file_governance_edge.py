"""Edge case tests for recallstorm.pricing.price_file_governance."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.pricing.price_file_governance import (
    validate_emergency_item_maintenance_batch,
    verify_multi_banner_price_zone_scope,
)


def test_price_file_governance_edge():
    with pytest.raises(DataValidationError):
        validate_emergency_item_maintenance_batch("B1", 0)
    with pytest.raises(DataValidationError):
        verify_multi_banner_price_zone_scope([])
