"""Property tests for recallstorm.food_safety.pest_control_holds."""
from recallstorm.food_safety.pest_control_holds import map_adjacent_pallet_buffer_zone


def test_buffer_zone_always_contains_center_bay():
    for center in range(1, 20):
        zone = map_adjacent_pallet_buffer_zone(center, 2)
        assert center in zone
