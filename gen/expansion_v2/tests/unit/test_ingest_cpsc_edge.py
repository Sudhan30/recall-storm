"""Edge case tests for recallstorm.ingest.cpsc."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.ingest.cpsc import cpsc_is_food_contact, parse_cpsc_recall


def test_cpsc_edge():
    with pytest.raises(DataValidationError):
        parse_cpsc_recall({})
    assert not cpsc_is_food_contact({"Title": "Lawn Mower", "Description": "Blade hazard"})
