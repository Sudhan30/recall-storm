"""Edge case tests for recallstorm.states.wa_toxic_free_kids."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.states.wa_toxic_free_kids import check_wa_phthalates_ppm, evaluate_wa_childrens_product


def test_wa_toxic_free_kids_edge():
    with pytest.raises(DataValidationError):
        check_wa_phthalates_ppm(-5.0)
    with pytest.raises(DataValidationError):
        evaluate_wa_childrens_product("toy", -1)
