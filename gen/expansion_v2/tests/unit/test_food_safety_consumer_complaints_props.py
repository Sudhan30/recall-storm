"""Property tests for recallstorm.food_safety.consumer_complaints."""
from recallstorm.food_safety.consumer_complaints import check_foreign_material_photo_hash


def test_photo_hash_determinism():
    for i in range(20):
        payload = f"photo_bytes_{i}"
        assert check_foreign_material_photo_hash(payload) == check_foreign_material_photo_hash(payload)
