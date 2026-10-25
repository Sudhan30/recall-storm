"""Edge case tests for recallstorm.states.la_seafood_labeling."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.states.la_seafood_labeling import evaluate_la_fluoroquinolone_ban, verify_la_placard_font_size


def test_la_seafood_labeling_edge():
    with pytest.raises(DataValidationError):
        verify_la_placard_font_size(0)
    with pytest.raises(DataValidationError):
        evaluate_la_fluoroquinolone_ban(-1.0)
