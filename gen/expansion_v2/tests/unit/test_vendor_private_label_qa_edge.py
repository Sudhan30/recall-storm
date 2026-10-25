"""Edge case tests for recallstorm.vendor.private_label_qa."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.vendor.private_label_qa import (
    score_copacker_food_safety_culture,
    trigger_unannounced_gfSI_sqf_audit,
)


def test_private_label_qa_edge():
    with pytest.raises(DataValidationError):
        trigger_unannounced_gfSI_sqf_audit("PLT1", 150)
    with pytest.raises(DataValidationError):
        score_copacker_food_safety_culture(-5.0)
