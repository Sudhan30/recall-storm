"""Edge case tests for recallstorm.analytics.supplier_benchmarking."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.analytics.supplier_benchmarking import (
    benchmark_traceability_epcis_adoption_rate,
    normalize_recalls_per_million_cases_shipped,
)


def test_supplier_benchmarking_edge():
    with pytest.raises(DataValidationError):
        normalize_recalls_per_million_cases_shipped(1, 0)
    with pytest.raises(DataValidationError):
        benchmark_traceability_epcis_adoption_rate(110, 100)
