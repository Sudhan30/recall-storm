"""Unit tests for recallstorm.food_safety.salvage_reconditioning."""
from recallstorm.food_safety.salvage_reconditioning import (
    ReconditioningProtocol,
    SalvageEligibilityEngine,
    apply_fda_reconditioning_guidelines,
    audit_salvage_broker_credentials,
    calculate_rework_labor_viability,
    check_smoke_water_damage_exposure,
    evaluate_dented_can_seam_integrity,
    generate_reconditioned_lot_code,
    record_rework_yield_shrinkage,
    segregate_non_salvageable_leakers,
    track_relabeling_allergen_stickers,
    verify_state_inspector_supervision,
)


def test_salvage_reconditioning():
    assert ReconditioningProtocol().status == "ACTIVE"
    assert SalvageEligibilityEngine().status == "ACTIVE"
    assert evaluate_dented_can_seam_integrity(True, False)["reject"] is True
    assert check_smoke_water_damage_exposure("can", True)["destroy_mandatory"] is True
    assert apply_fda_reconditioning_guidelines("MISBRANDING")["eligible"] is True
    assert calculate_rework_labor_viability(200.0, 1000.0)["viable"] is True
    assert track_relabeling_allergen_stickers("B1", 500)["stickers_applied"] == 500
    assert verify_state_inspector_supervision("RW1", True)["supervised"] is True
    assert segregate_non_salvageable_leakers(20, 3)["intact_cases"] == 17
    assert audit_salvage_broker_credentials("BRK1", True)["approved"] is True
    assert generate_reconditioned_lot_code("L2601") == "L2601-RECOND"
    assert record_rework_yield_shrinkage(100, 95)["lost_units"] == 5
