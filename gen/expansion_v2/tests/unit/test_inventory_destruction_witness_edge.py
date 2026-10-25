"""Edge case tests for recallstorm.inventory.destruction_witness."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.inventory.destruction_witness import (
    generate_dual_signature_affidavit,
    upload_geotagged_destruction_photos,
)


def test_destruction_witness_edge():
    with pytest.raises(DataValidationError):
        generate_dual_signature_affidavit("MGR1", "MGR1", 10)
    with pytest.raises(DataValidationError):
        upload_geotagged_destruction_photos("WM1", 190.0, 0.0)
