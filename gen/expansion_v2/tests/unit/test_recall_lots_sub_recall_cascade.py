"""Unit tests for recallstorm.recall_lots.sub_recall_cascade."""
from recallstorm.recall_lots.sub_recall_cascade import (
    DownstreamSkuResolver,
    IngredientCascadeGraph,
    audit_central_kitchen_batch_logs,
    build_cascade_impact_tree,
    calculate_generational_dilution_factor,
    flag_prepared_foods_salads,
    generate_derivative_sku_pull_list,
    identify_in_store_bakery_mixes,
    map_raw_lot_to_finished_goods,
    propagate_recall_to_meal_kits,
    resolve_co_packer_cross_supply,
    trace_commissary_recipe_boms,
)


def test_sub_recall_cascade():
    assert IngredientCascadeGraph().status == "ACTIVE"
    assert DownstreamSkuResolver().status == "ACTIVE"
    assert map_raw_lot_to_finished_goods("L1", {"L1": ["FG2", "FG1"]}) == ["FG1", "FG2"]
    assert trace_commissary_recipe_boms("ING1", {"REC1": ["ING1"]}) == ["REC1"]
    assert identify_in_store_bakery_mixes("FDC1034191", [{"sku_id": "CUP1", "components": ["FDC1034191"]}]) == ["CUP1"]
    assert flag_prepared_foods_salads("romaine", [{"sku_id": "SAL1", "ingredients": "Romaine lettuce, dressing"}]) == ["SAL1"]
    assert calculate_generational_dilution_factor(5.0, 100.0) == 0.05
    assert resolve_co_packer_cross_supply("L1", ["CP1"])["copackers"] == ["CP1"]
    assert propagate_recall_to_meal_kits("S1", {"KIT1": ["S1", "S2"]}) == ["KIT1"]
    assert build_cascade_impact_tree("L1", ["A"], ["B"])["total_nodes"] == 3
    assert audit_central_kitchen_batch_logs("K1", 4)["batches_checked"] == 4
    assert generate_derivative_sku_pull_list("S1", ["D1"])["count"] == 2
