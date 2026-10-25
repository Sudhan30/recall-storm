"""Edge case tests for recallstorm.dc_ops.receiving_holds."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.dc_ops.receiving_holds import (
    generate_osd_over_short_damage_refusal,
    segregate_mixed_lot_vendor_ti_hi_pallets,
)


def test_receiving_holds_edge():
    with pytest.raises(DataValidationError):
        segregate_mixed_lot_vendor_ti_hi_pallets(10, 20)
    with pytest.raises(DataValidationError):
        generate_osd_over_short_damage_refusal("PO1", 0)
