"""Edge case tests for recallstorm.vendor.certificates_of_analysis."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.vendor.certificates_of_analysis import check_heavy_metal_pfas_pass_fail_limits


def test_certificates_of_analysis_edge():
    with pytest.raises(DataValidationError):
        check_heavy_metal_pfas_pass_fail_limits(-1.0, 50.0)
