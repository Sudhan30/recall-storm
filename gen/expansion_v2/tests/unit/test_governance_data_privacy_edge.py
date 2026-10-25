"""Edge case tests for recallstorm.governance.data_privacy."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.governance.data_privacy import (
    enforce_purpose_limitation_on_recall_contact,
    validate_k_anonymity_in_published_analytics,
)


def test_data_privacy_edge():
    assert enforce_purpose_limitation_on_recall_contact("Recall alert! Buy one get one free")["compliant"] is False
    assert validate_k_anonymity_in_published_analytics([2, 10], 5) is False
    with pytest.raises(DataValidationError):
        validate_k_anonymity_in_published_analytics([5], 0)
