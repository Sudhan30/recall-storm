"""Property tests for recallstorm.states.pa_synthetic_dyes."""
from recallstorm.states.pa_synthetic_dyes import flag_red40_yellow5_skus


def test_all_major_fdc_dyes_flagged_in_pa():
    for dye in ("RED 40", "YELLOW 5", "YELLOW 6", "BLUE 1", "BLUE 2", "RED 3"):
        assert flag_red40_yellow5_skus(f"WATER, {dye}")["flagged"] is True
