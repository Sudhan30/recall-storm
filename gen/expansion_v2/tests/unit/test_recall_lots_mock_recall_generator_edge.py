"""Edge case tests for recallstorm.recall_lots.mock_recall_generator."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.recall_lots.mock_recall_generator import (
    configure_blind_drill_parameters,
    inject_seeded_lots_into_wms,
)


def test_mock_recall_generator_edge():
    with pytest.raises(DataValidationError):
        inject_seeded_lots_into_wms("DC1", [])
    with pytest.raises(DataValidationError):
        configure_blind_drill_parameters("DR1", 0)
