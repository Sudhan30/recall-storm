"""Unit tests for recallstorm.analytics.financial_impact."""
from recallstorm.analytics.financial_impact import (
    RecallCostAggregator,
    TotalCostOfRecallModel,
    add_reverse_freight_and_destruction_fees,
    attribute_cost_by_merchandising_buying_desk,
    calculate_store_and_dc_execution_labor_cost,
    compute_net_unrecovered_recall_p_and_l_hit,
    deduct_recovered_vendor_chargebacks_and_rma,
    estimate_brand_equity_halo_basket_erosion,
    generate_cfo_recall_financial_bridge,
    incorporate_regulatory_fines_and_legal_fees,
    quantify_lost_margin_from_out_of_stocks,
    sum_direct_product_write_off_at_cost,
)


def test_financial_impact():
    assert RecallCostAggregator().status == "ACTIVE"
    assert TotalCostOfRecallModel().status == "ACTIVE"
    assert sum_direct_product_write_off_at_cost([1000.0, 2500.0]) == 3500.0
    assert calculate_store_and_dc_execution_labor_cost(80.0, 20.0, 22.0) == 2200.0
    assert quantify_lost_margin_from_out_of_stocks(200, 1.25) == 250.0
    assert add_reverse_freight_and_destruction_fees(800.0, 400.0) == 1200.0
    assert deduct_recovered_vendor_chargebacks_and_rma(5000.0, 4200.0) == 800.0
    assert incorporate_regulatory_fines_and_legal_fees(0.0, 1500.0) == 1500.0
    assert estimate_brand_equity_halo_basket_erosion(50, 18.0) == 900.0
    assert compute_net_unrecovered_recall_p_and_l_hit(10000.0, 7000.0, 1000.0) == 2000.0
    assert attribute_cost_by_merchandising_buying_desk({"BAKING": 1200.0})["BAKING"] == 1200.0
    assert generate_cfo_recall_financial_bridge(10000.0, 8000.0)["net_usd"] == 2000.0
