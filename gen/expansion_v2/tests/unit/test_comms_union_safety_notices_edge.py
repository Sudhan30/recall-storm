"""Edge case tests for recallstorm.comms.union_safety_notices."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.comms.union_safety_notices import (
    provide_ergonomic_heavy_lifting_guide,
    specify_caustic_leaking_product_ppe,
)


def test_union_safety_notices_edge():
    with pytest.raises(DataValidationError):
        specify_caustic_leaking_product_ppe(18.0)
    with pytest.raises(DataValidationError):
        provide_ergonomic_heavy_lifting_guide(0.0)
