"""Edge case tests for recallstorm.states.mn_toxic_free_kids."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.states.mn_toxic_free_kids import check_mn_toy_jewelry_ppm, evaluate_mn_child_mouthable_item


def test_mn_toxic_free_kids_edge():
    with pytest.raises(DataValidationError):
        check_mn_toy_jewelry_ppm(-1.0, 0.0)
    with pytest.raises(DataValidationError):
        evaluate_mn_child_mouthable_item(0.0)
