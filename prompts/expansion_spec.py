"""OURS. The expansion's required file list (G1a scope). Order is the generation order.

Sized from the probe run: ~510 visible tokens per required public function plus ~80% for two test files, so
~920 tokens per function. Edit by adding or removing whole packages, never by asking for length.

Usage: python prompts/expansion_spec.py > prompts/expansion_files.md
"""

SPEC = {
    "core": {
        "ids": "make_run_id make_task_id make_evidence_id make_alloc_id make_manifest_id make_handoff_id make_exc_id parse_id validate_id_prefix",
        "errors": "RecallStormError DataValidationError RuleConfigError AllocationError RoutingError LaborError ScenarioError format_error error_to_record",
        "config": "Config load_config default_config merge_overrides validate_config config_from_env config_to_dict get_deadline get_scenario_path",
        "logging_setup": "get_logger configure_logging JsonlLogHandler log_event log_timing with_context redact_text set_level flush_all",
        "clock": "to_local from_local local_wall naive_local is_before_deadline minutes_between window_overlaps clamp_window iso_with_offset",
        "jsonl": "read_jsonl write_jsonl append_jsonl iter_jsonl validate_record record_with_src sort_records dedupe_by_key stable_dumps",
        "validate": "validate_sku validate_store validate_facing validate_associate validate_truck validate_rule validate_datapack collect_issues issues_summary",
        "registry": "Registry register_module get_module list_modules src_path_for emit_with_src module_version registry_snapshot reset_registry",
    },
    "ingest": {
        "recall_feeds": "parse_fsis_recall parse_fda_rss feed_item_to_recall dedupe_recalls recall_since recall_by_state merge_recall_sources feed_cursor RecallFeed",
        "labels_ocr": "parse_ocr_payload ocr_text_blocks ocr_confidence join_ocr_lines detect_ingredient_block ocr_to_ingredients flag_low_confidence ocr_language OcrLabel",
        "vendor_catalog": "parse_vendor_row vendor_to_sku vendor_dsd_flag vendor_case_pack vendor_reformulation_date vendor_sub_suggestions merge_vendor_catalog vendor_contacts VendorCatalog",
        "usda_fdc": "parse_fdc_food parse_fdc_search fdc_to_sku normalize_brand normalize_category fdc_ingredients fdc_gtin fdc_is_food iter_fdc_pages",
        "open_food_facts": "parse_off_product off_to_sku off_ingredients_text off_additive_tags off_e_numbers off_categories off_gtin off_language merge_off_fdc",
        "openfda_enforcement": "parse_enforcement_report enforcement_to_recall extract_lot_codes extract_date_ranges extract_product_gtins classify_recall_reason recall_jurisdictions recall_status iter_enforcement_pages",
        "cpsc": "parse_cpsc_recall cpsc_to_recall cpsc_product_names cpsc_upcs cpsc_hazard_text cpsc_remedy cpsc_dates cpsc_units cpsc_is_food_contact",
        "store_list": "parse_store_csv normalize_store_format parse_address geocode_zip assign_district assign_dc dedupe_stores store_from_row validate_store_list",
        "planogram": "parse_planogram_row planogram_to_facings location_from_code bay_capacity shelf_positions merge_planograms planogram_diff facing_units_estimate validate_planogram",
        "staffing": "parse_roster_row roster_to_associates parse_shift shift_minutes floater_pool overnight_shift_window roster_by_store roster_by_district validate_roster",
        "manifest_io": "load_datapack_extended write_datapack datapack_stats sample_datapack filter_by_state filter_by_stores subset_skus datapack_hash compare_datapacks",
    },
    "aliases": {
        "translations": "TRANSLATIONS translate_alias detect_language alias_in_language multilingual_patterns accent_fold translated_match language_report add_translation",
        "spans": "Span span_from_match merge_spans span_text span_overlaps shift_span spans_to_offsets highlight_spans span_to_dict",
        "normalize": "normalize_ingredients strip_punctuation collapse_whitespace fold_unicode ocr_fix tokenize_ingredients split_sub_ingredients ingredient_offsets denormalize_span",
        "lexicon": "Lexicon load_lexicon aliases_for additive_for_alias add_alias e_number_for ci_number_for translations_for lexicon_from_rules",
        "detect": "find_matches find_first_match match_span match_confidence is_decoy decoy_reason detect_all_additives explain_match MatchResult",
        "decoys": "DECOY_PATTERNS is_red40 is_dc_red_33 is_quantity_phrase is_product_name_phrase is_lake_pigment decoy_examples classify_red_mention near_miss_report",
        "unclear": "is_generic_color is_unreadable readability_score generic_color_phrases unclear_reason needs_human_review ocr_noise_ratio truncated_label redact_noise",
        "bundles": "is_bundle split_bundle bundle_components component_ingredients bundle_contains bundle_match_path bundle_summary kit_keywords flatten_bundle",
    },
    "rules": {
        "potassium_bromate": "bromate_aliases detect_bromate bromate_rules evaluate_bromate bromate_scope bromate_rationale bromate_evidence bromate_effective bromate_summary",
        "propylparaben": "paraben_aliases detect_propylparaben paraben_rules evaluate_propylparaben paraben_scope paraben_rationale paraben_evidence paraben_effective paraben_summary",
        "preemption": "federal_rule_for state_rule_for preemption_status stricter_rule effective_conflict resolve_conflicts preemption_report preemption_matrix PreemptionResolver",
        "model": "RuleSet load_rules rule_by_id rules_for_state rules_for_additive rules_for_product_type effective_local rule_summary ruleset_hash",
        "jurisdiction": "jurisdictions_for_state applies_in_state federal_applies state_preempts jurisdiction_rank jurisdiction_chain resolve_jurisdictions state_name state_codes",
        "dates": "effective_at is_prohibited_at days_until_effective first_prohibited_instant sell_through_allowed local_deadline deadline_for_store deadlines_by_tz next_effective_rule",
        "scope": "product_types_for_sku sku_in_scope is_food_scope is_drug_scope is_cosmetic_scope scope_reason exclude_reason scope_matrix applies_to_sku",
        "red3": "RED3_RULE_IDS red3_rules evaluate_red3 red3_rationale red3_evidence red3_clause red3_aliases red3_scope red3_deadline",
        "ab418": "AB418_ADDITIVES ab418_rules evaluate_bvo evaluate_potassium_bromate evaluate_propylparaben evaluate_red3_ca ab418_clause ab418_summary ab418_effective",
        "bvo": "bvo_aliases detect_bvo bvo_rules evaluate_bvo_federal bvo_effective bvo_rationale bvo_beverage_scope bvo_evidence bvo_summary",
        "pfas_mn": "pfas_rules detect_pfas_claim pfas_product_categories pfas_in_scope pfas_effective evaluate_pfas pfas_rationale pfas_evidence pfas_summary",
        "carb_voc": "carb_voc_rules voc_limit_for_category parse_voc_percent evaluate_voc lubricant_in_scope voc_rationale voc_evidence voc_effective voc_summary",
        "engine": "evaluate_sku evaluate_many evaluate_pack decision_to_record merge_decisions strictest_decision decision_counts explain_decision RuleEngine",
    },
    "adjudicate": {
        "overrides": "Override apply_override validate_override override_to_record overrides_for_sku expire_overrides override_reason_codes override_report OverrideBook",
        "sampling": "sample_for_review stratified_sample review_rate estimate_error_rate confidence_interval sample_report seed_sampler resample SampleSet",
        "queue": "ReviewQueue enqueue dequeue queue_size items_for_store prioritize_items mark_reviewed queue_to_records queue_from_records",
        "classifier": "HeuristicClassifier GeminiClassifier classifier_prompt parse_classifier_reply classifier_decision fallback_hold confidence_threshold batch_classify ClassifierStats",
        "evidence": "build_evidence evidence_span evidence_card evidence_to_record source_excerpt highlight_match link_evidence evidence_index validate_evidence",
        "audit": "AuditTrail record_decision record_override audit_to_records decisions_by_source overrides_by_user audit_summary audit_diff verify_audit",
    },
    "gs1": {
        "epcis": "parse_epcis_event epcis_object_event epcis_to_movements epc_to_gtin epcis_lot epcis_location filter_epcis_by_gtin epcis_summary EpcisDoc",
        "barcodes": "upc_a_to_gtin ean13_to_gtin parse_scan_string scan_to_gtin is_variable_measure strip_price_embedded barcode_type validate_scan ScanResult",
        "gtin": "gtin_check_digit is_valid_gtin normalize_gtin gtin8_to_14 gtin12_to_14 gtin13_to_14 gtin_company_prefix gtin_indicator gtin_variants",
        "ai": "parse_element_string ai_01 ai_10 ai_17 ai_11 ai_21 build_element_string ai_table validate_ai",
        "digital_link": "parse_digital_link build_digital_link digital_link_gtin digital_link_lot digital_link_expiry is_digital_link canonical_digital_link digital_link_to_ais ais_to_digital_link",
        "lots": "parse_lot_code lot_in_range lot_range_from_text normalize_lot lot_matches_recall expiry_in_range date_range_overlap lot_pattern recall_lot_filter",
        "match": "match_recall_to_skus match_by_gtin match_by_lot match_by_name match_score best_match unmatched_recalls match_report GtinIndex",
    },
    "store": {
        "backroom": "backroom_locations backroom_stock topstock_for_sku backroom_pull_task backroom_capacity_left stage_returns staging_area backroom_summary Backroom",
        "signage": "tag_flash_text shelf_tag_for_sku sign_template sign_language printer_queue tags_for_store tag_to_record sign_summary SignPrinter",
        "layout": "StoreLayout build_layout aisle_order bay_coordinates location_xy walking_distance nearest_location layout_bounds layout_to_json",
        "facings": "facings_for_store facings_for_sku affected_facings units_on_shelf facings_by_aisle facing_key locate_sku facings_summary group_facings",
        "exceptions": "parse_note note_to_exception exception_kind_for_text dsd_vendor_pull endcap_display topstock pickup_totes resolve_exception exceptions_for_store",
        "formats": "format_profile carries_category format_labor_minutes format_tag_rule format_backroom_capacity format_summary formats_in_pack format_priority is_club_format",
    },
    "labor": {
        "compliance": "max_shift_minutes break_required meal_break_window overtime_minutes check_labor_rules labor_violations violation_to_record labor_report LaborRules",
        "skills": "associate_skills can_handle_action skill_for_task certify_associate skill_gaps skill_matrix train_plan skills_summary SkillBook",
        "shifts": "shift_window shift_minutes_left available_associates associates_for_store floaters_for_district shift_overlaps clamp_to_shift shift_utilization ShiftCalendar",
        "estimates": "pull_minutes place_minutes tag_minutes walk_minutes task_minutes store_minutes estimate_playbook minutes_by_action EstimateModel",
        "assign": "assign_tasks greedy_assign balance_load assign_floaters reassign_overflow assignment_conflicts assignment_summary assignment_to_records LaborPlan",
        "floaters": "floater_need dispatch_floater floater_windows floater_handoffs one_store_per_window floater_travel_minutes floater_plan_summary validate_floaters FloaterPool",
    },
    "allocate": {
        "stock": "stock_for_dc stock_for_sku reserve_stock release_stock stock_after stock_ledger ledger_to_records conservation_check StockLedger",
        "priority": "store_priority format_weight distance_weight deadline_weight priority_score rank_stores priority_report tie_break_key PriorityModel",
        "demand": "demand_from_facings demand_by_dc demand_by_store substitute_for_sku demand_cases total_demand demand_to_records unmet_demand DemandTable",
        "allocator": "allocate_substitutes allocate_proportional allocate_priority allocation_balance never_exceeds_stock round_cases tie_break allocation_records AllocationResult",
        "transfers": "sub_transfers transfer_handoff dc_to_store_windows transfer_cube transfer_weight transfers_by_truck transfer_summary validate_transfers TransferPlan",
    },
    "plan": {
        "exceptions_plan": "exception_tasks dsd_exception_task endcap_exception_task topstock_exception_task totes_exception_task planogram_exception_task unclear_label_task exception_records ExceptionPlanner",
        "deadline": "deadline_for_plan window_before_deadline shrink_window late_risk deadline_slack_minutes enforce_deadline deadline_report deadline_violations DeadlineGuard",
        "explain": "explain_task explain_store explain_sku explain_allocation explain_route plan_narrative why_hold why_keep Explainer",
        "tasks": "build_shelf_tasks pull_task place_sub_task tag_flash_task hold_verify_task task_sequence task_window task_to_record TaskBuilder",
        "playbook": "build_playbook playbook_counts playbook_windows playbook_to_record playbook_deadline playbook_exceptions playbook_manifests playbook_summary PlaybookBuilder",
        "handoffs": "build_handoffs floater_handoff return_consolidation sub_transfer_handoff handoff_to_record pair_handoffs handoff_windows handoff_summary HandoffBuilder",
        "assemble": "assemble_plan plan_records plan_to_jsonl validate_plan_refs plan_stats run_record plan_hash merge_plans PlanAssembler",
    },
    "sim": {
        "walking": "walk_path walk_seconds aisle_graph shortest_path path_to_moves congestion_penalty walking_summary speed_for_associate WalkModel",
        "disruptions": "Disruption inject_disruption absent_associate truck_delay stockout_event replan_after_disruption disruption_report seed_disruptions DisruptionSet",
        "events": "MoveEvent PullEvent PlaceEvent DoneEvent event_to_record events_to_jsonl sort_events events_for_store events_for_associate",
        "replay": "replay_tasks replay_store replay_associate walking_time event_times simulate_plan replay_summary detect_late_events Replayer",
        "metrics": "completion_curve tasks_done_by pulled_units_by placed_units_by store_completion district_completion late_tasks idle_minutes MetricsReport",
    },
    "scenario_gs1": {
        "scenario": "load_gs1_scenario recall_from_openfda recall_skus recall_lots recall_window recall_rule recall_plan gs1_scenario_summary Gs1Scenario",
        "lot_pull": "lot_pull_tasks lot_verify_task lots_on_shelf lot_quarantine lot_pull_counts lot_task_window lot_evidence lot_report LotPuller",
    },
    "route": {
        "capacity": "truck_capacity remaining_cube remaining_weight capacity_check overload_report utilization_by_dc capacity_to_record capacity_summary CapacityModel",
        "dispatch": "dispatch_plan depart_time arrival_eta driver_hours dispatch_to_records late_departures dispatch_summary validate_dispatch Dispatcher",
        "returns": "returned_cases cases_by_store cases_by_dc case_cube case_weight returns_summary returns_to_stops validate_returns ReturnLoad",
        "packing": "pack_returns first_fit_decreasing pack_truck fits_truck truck_utilization split_stop manifest_to_record packing_summary PackingResult",
        "stops": "order_stops nearest_neighbor_order route_distance stop_eta stops_for_truck merge_stops stop_to_record stops_summary RoutePlanner",
    },
    "report": {
        "summary": "drill_summary store_table sku_table counts_by_verdict counts_by_action summary_to_markdown summary_to_json compare_runs SummaryReport",
        "checks": "check_refs check_conservation check_capacity check_labor check_deadline check_contradictions run_all_checks checks_to_json CheckReport",
        "export": "export_csv export_markdown export_store_packets export_dc_packets export_evidence export_manifests export_zip export_index Exporter",
        "dashboard": "dashboard_data map_points store_status_colors timeline_series kpi_tiles dashboard_to_json dashboard_html DashboardModel DashboardBuilder",
    },
    "cli": {
        "main": "main build_parser cmd_run cmd_validate cmd_stats cmd_explain cmd_replay cmd_scenarios exit_code_for",
    },
}

if __name__ == "__main__":
    n_mod = n_fn = 0
    lines = ["REQUIRED FILES (emit every one, in this order; each module is followed immediately by its two test files).",
             "Each module must define every listed public name (CamelCase = class, else function) with a docstring,",
             "input validation and error handling, plus any private helpers it needs. Each test file tests every",
             "public name of its module. You may add small helper modules; you may not drop or merge listed files.", ""]
    for pkg, mods in SPEC.items():
        lines.append(f"## recallstorm/{pkg}/  (recallstorm/{pkg}/__init__.py re-exports the public names)")
        for mod, names in mods.items():
            fns = names.split()
            n_mod += 1; n_fn += len(fns)
            lines.append(f"- recallstorm/{pkg}/{mod}.py: {', '.join(fns)}")
            lines.append(f"  tests/unit/test_{pkg}_{mod}.py  (behaviour of every public name)")
            lines.append(f"  tests/unit/test_{pkg}_{mod}_edge.py  (invalid inputs, boundaries, determinism)")
        lines.append("")
    lines += ["## recallstorm/__main__.py  (calls recallstorm.cli.main.main)",
              "## tests/integration/  (12 files, test_flow_*.py, each exercising modules from at least 5 earlier packages)",
              "## docs/  (architecture.md, data_model.md, rules.md, operations.md)"]
    print("\n".join(lines))
    import sys
    print(f"modules={n_mod} functions={n_fn} est_tokens={n_fn * 920:,}", file=sys.stderr)
