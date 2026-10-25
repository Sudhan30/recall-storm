"""Edge case tests for recallstorm.recall_lots.distribution_list."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.recall_lots.distribution_list import (
    parse_fda_state_distribution_text,
    rank_stores_by_shipment_volume,
)


def test_distribution_list_edge():
    assert parse_fda_state_distribution_text("Nationwide distribution") == ["US"]
    with pytest.raises(DataValidationError):
        parse_fda_state_distribution_text("")
    with pytest.raises(DataValidationError):
        rank_stores_by_shipment_volume(None)  # type: ignore[arg-type]
