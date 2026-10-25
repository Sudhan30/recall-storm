"""Property tests for recallstorm.report.dashboard."""
from recallstorm.report.dashboard import store_status_colors


def test_store_status_colors_valid_palette():
    pbs = [{"store_id": f"WM{i}", "counts": {"tasks": i % 2}} for i in range(15)]
    colors = store_status_colors(pbs)
    assert set(colors.values()).issubset({"RED", "GREEN"})
