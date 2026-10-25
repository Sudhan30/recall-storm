"""Edge case tests for recallstorm.analytics.anomaly_detection."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.analytics.anomaly_detection import (
    compare_sister_store_pull_ratios_by_cluster,
    detect_impossible_speed_pencil_whipping,
)


def test_anomaly_detection_edge():
    with pytest.raises(DataValidationError):
        detect_impossible_speed_pencil_whipping(0, 10.0)
    with pytest.raises(DataValidationError):
        compare_sister_store_pull_ratios_by_cluster(1.5, 0.5)
