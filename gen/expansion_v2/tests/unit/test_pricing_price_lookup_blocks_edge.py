"""Edge case tests for recallstorm.pricing.price_lookup_blocks."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.pricing.price_lookup_blocks import (
    disable_bakery_self_serve_plu_buttons,
    push_scale_network_lockout_file,
)


def test_price_lookup_blocks_edge():
    with pytest.raises(DataValidationError):
        disable_bakery_self_serve_plu_buttons("WM1", [])
    with pytest.raises(DataValidationError):
        push_scale_network_lockout_file("WM1", 0)
