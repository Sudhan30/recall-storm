"""Unit tests for recallstorm.comms.foodservice_advisories."""
from recallstorm.comms.foodservice_advisories import (
    CommissaryChefAlert,
    MenuRemovalNotice,
    alert_sushi_kiosk_franchise_operators,
    authorize_safe_ingredient_substitution,
    halt_in_store_restaurant_recipe_prep,
    log_discarded_prepared_batch_weights,
    notify_corporate_catering_event_clients,
    pull_recalled_ingredient_from_salad_bar,
    quarantine_hot_bar_steam_table_pans,
    revise_printed_grab_and_go_ingredients,
    update_digital_menu_board_allergens,
    verify_kitchen_walk_in_cooler_sweep,
)


def test_foodservice_advisories():
    assert CommissaryChefAlert().status == "ACTIVE"
    assert MenuRemovalNotice().status == "ACTIVE"
    assert halt_in_store_restaurant_recipe_prep("WM1", "REC1")["halted"] is True
    assert pull_recalled_ingredient_from_salad_bar("WM1", "Cherries")["pulled"] is True
    assert update_digital_menu_board_allergens("WM1", "M1")["updated"] is True
    assert notify_corporate_catering_event_clients(["O1", "O2"])["notified_orders"] == 2
    assert quarantine_hot_bar_steam_table_pans("WM1", 3)["pan_count"] == 3
    assert revise_printed_grab_and_go_ingredients("REC1", "SUGAR, BEET JUICE")["recipe_id"] == "REC1"
    assert alert_sushi_kiosk_franchise_operators(["K1"], "Masago")["kiosks"] == ["K1"]
    assert log_discarded_prepared_batch_weights("WM1", 25.5)["weight_lb"] == 25.5
    assert verify_kitchen_walk_in_cooler_sweep("WM1", True)["cleared"] is True
    assert authorize_safe_ingredient_substitution("REC1", "Beet Dye")["sub_ingredient"] == "Beet Dye"
