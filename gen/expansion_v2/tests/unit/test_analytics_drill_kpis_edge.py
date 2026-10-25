"""Edge case tests for recallstorm.analytics.drill_kpis."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.analytics.drill_kpis import (
    compute_lot_capture_accuracy_precision,
    generate_executive_drill_grade_letter,
)


def test_drill_kpis_edge():
    with pytest.raises(DataValidationError):
        compute_lot_capture_accuracy_precision(0, 0)
    with pytest.raises(DataValidationError):
        generate_executive_drill_grade_letter(120.0)
