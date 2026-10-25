"""Unit tests for recallstorm.governance.regulatory_calendar."""
from recallstorm.governance.regulatory_calendar import (
    ComplianceDeadlineCalendar,
    StatutoryPhaseInTracker,
    alert_merchandising_to_sell_through_cutoffs,
    assign_executive_owners_to_upcoming_laws,
    calculate_working_days_to_mandatory_ban,
    generate_twelve_month_regulatory_horizon_map,
    monitor_state_legislature_amendment_feeds,
    schedule_t_minus_90_day_readiness_drills,
    sync_regulatory_milestones_to_corp_calendar,
    track_ab418_ny_il_statutory_effective_dates,
    track_fda_fsma_204_traceability_deadlines,
    trigger_pre_enforcement_store_sweep_tasks,
)


def test_regulatory_calendar():
    assert ComplianceDeadlineCalendar().status == "ACTIVE"
    assert StatutoryPhaseInTracker().status == "ACTIVE"
    assert track_ab418_ny_il_statutory_effective_dates()["CA_AB418"] == "2027-01-01"
    assert schedule_t_minus_90_day_readiness_drills("2027-01-01", 90) == "2026-10-03"
    assert alert_merchandising_to_sell_through_cutoffs("CA_AB418_RED3", 30)["stop_pos_now"] is True
    assert monitor_state_legislature_amendment_feeds("CA", "AB418")["state"] == "CA"
    assert sync_regulatory_milestones_to_corp_calendar([{"id": "M1"}])["synced_count"] == 1
    assert calculate_working_days_to_mandatory_ban("2026-12-28", "2027-01-01") == 4
    assert trigger_pre_enforcement_store_sweep_tasks("CA_AB418_RED3", 24)["hours_before_ban"] == 24
    assert track_fda_fsma_204_traceability_deadlines("leafy greens")["kde_cte_required"] is True
    assert assign_executive_owners_to_upcoming_laws("AB418", "VP1")["owner_id"] == "VP1"
    assert "CA_AB418" in generate_twelve_month_regulatory_horizon_map(2027)["laws"]
