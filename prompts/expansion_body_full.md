You are expanding Recall Storm into a full platform in ONE continued generation.
contract.py is frozen and already exists. Everything you write must use it unchanged.

Write these packages in this exact order (the full required file list follows below) (positions matter for our measurements):
core/ (ID scheme, errors, config, logging) -> ingest/ (USDA FDC, Open Food Facts, openFDA enforcement, CPSC,
store list parsers) -> aliases/ -> rules/ (FDA Red No. 3 food and drug, CA AB 418 four additives, BVO,
Minnesota PFAS 116.943, CARB multi-purpose lubricant VOC; jurisdiction and date engine) -> adjudicate/ ->
gs1/ (GTIN check digits, AI 01/10/17, Digital Link, recall lot and date-range matching) -> store/ -> labor/ ->
allocate/ -> plan/ -> sim/ -> gs1-based recall scenario (openFDA lot codes) -> route/ (LAST package) -> cli/ ->
tests/integration/ (cross-package and property tests) -> docs/.
Each package is followed by its unit tests. route/ must be the last package before cli/.

For every package, implement the full public API listed in the manifest you write, with docstrings,
input validation, and error handling. Integration tests must exercise modules from every earlier package.


Required public APIs carried over from contract.py (the acceptance tests import exactly these):
- recallstorm/rules/:    evaluate_sku(sku, rules, state, at, classifier=None) -> SkuDecision
- recallstorm/allocate/: allocate_substitutes(demand, stock, stores) -> list[Allocation]
- recallstorm/route/:    pack_returns(pulled_cases, skus, trucks, stores) -> list[RouteManifest]
- recallstorm/__main__.py: python -m recallstorm run --scenario ID --data DIR --out DIR
Later packages must import and call earlier packages by the exact names declared in your manifest.


REQUIRED FILES (emit every one, in this order; each module is followed immediately by its two test files).
Each module must define every listed public name (CamelCase = class, else function) with a docstring,
input validation and error handling, plus any private helpers it needs. Each test file tests every
public name of its module. You may add small helper modules; you may not drop or merge listed files.

## recallstorm/core/  (recallstorm/core/__init__.py re-exports the public names)
- recallstorm/core/ids.py: make_run_id, make_task_id, make_evidence_id, make_alloc_id, make_manifest_id, make_handoff_id, make_exc_id, parse_id, validate_id_prefix
  tests/unit/test_core_ids.py  (behaviour of every public name)
  tests/unit/test_core_ids_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/core/errors.py: RecallStormError, DataValidationError, RuleConfigError, AllocationError, RoutingError, LaborError, ScenarioError, format_error, error_to_record
  tests/unit/test_core_errors.py  (behaviour of every public name)
  tests/unit/test_core_errors_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/core/config.py: Config, load_config, default_config, merge_overrides, validate_config, config_from_env, config_to_dict, get_deadline, get_scenario_path
  tests/unit/test_core_config.py  (behaviour of every public name)
  tests/unit/test_core_config_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/core/logging_setup.py: get_logger, configure_logging, JsonlLogHandler, log_event, log_timing, with_context, redact_text, set_level, flush_all
  tests/unit/test_core_logging_setup.py  (behaviour of every public name)
  tests/unit/test_core_logging_setup_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/core/clock.py: to_local, from_local, local_wall, naive_local, is_before_deadline, minutes_between, window_overlaps, clamp_window, iso_with_offset
  tests/unit/test_core_clock.py  (behaviour of every public name)
  tests/unit/test_core_clock_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/core/jsonl.py: read_jsonl, write_jsonl, append_jsonl, iter_jsonl, validate_record, record_with_src, sort_records, dedupe_by_key, stable_dumps
  tests/unit/test_core_jsonl.py  (behaviour of every public name)
  tests/unit/test_core_jsonl_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/core/validate.py: validate_sku, validate_store, validate_facing, validate_associate, validate_truck, validate_rule, validate_datapack, collect_issues, issues_summary
  tests/unit/test_core_validate.py  (behaviour of every public name)
  tests/unit/test_core_validate_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/core/registry.py: Registry, register_module, get_module, list_modules, src_path_for, emit_with_src, module_version, registry_snapshot, reset_registry
  tests/unit/test_core_registry.py  (behaviour of every public name)
  tests/unit/test_core_registry_edge.py  (invalid inputs, boundaries, determinism)

## recallstorm/ingest/  (recallstorm/ingest/__init__.py re-exports the public names)
- recallstorm/ingest/recall_feeds.py: parse_fsis_recall, parse_fda_rss, feed_item_to_recall, dedupe_recalls, recall_since, recall_by_state, merge_recall_sources, feed_cursor, RecallFeed
  tests/unit/test_ingest_recall_feeds.py  (behaviour of every public name)
  tests/unit/test_ingest_recall_feeds_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/ingest/labels_ocr.py: parse_ocr_payload, ocr_text_blocks, ocr_confidence, join_ocr_lines, detect_ingredient_block, ocr_to_ingredients, flag_low_confidence, ocr_language, OcrLabel
  tests/unit/test_ingest_labels_ocr.py  (behaviour of every public name)
  tests/unit/test_ingest_labels_ocr_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/ingest/vendor_catalog.py: parse_vendor_row, vendor_to_sku, vendor_dsd_flag, vendor_case_pack, vendor_reformulation_date, vendor_sub_suggestions, merge_vendor_catalog, vendor_contacts, VendorCatalog
  tests/unit/test_ingest_vendor_catalog.py  (behaviour of every public name)
  tests/unit/test_ingest_vendor_catalog_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/ingest/usda_fdc.py: parse_fdc_food, parse_fdc_search, fdc_to_sku, normalize_brand, normalize_category, fdc_ingredients, fdc_gtin, fdc_is_food, iter_fdc_pages
  tests/unit/test_ingest_usda_fdc.py  (behaviour of every public name)
  tests/unit/test_ingest_usda_fdc_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/ingest/open_food_facts.py: parse_off_product, off_to_sku, off_ingredients_text, off_additive_tags, off_e_numbers, off_categories, off_gtin, off_language, merge_off_fdc
  tests/unit/test_ingest_open_food_facts.py  (behaviour of every public name)
  tests/unit/test_ingest_open_food_facts_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/ingest/openfda_enforcement.py: parse_enforcement_report, enforcement_to_recall, extract_lot_codes, extract_date_ranges, extract_product_gtins, classify_recall_reason, recall_jurisdictions, recall_status, iter_enforcement_pages
  tests/unit/test_ingest_openfda_enforcement.py  (behaviour of every public name)
  tests/unit/test_ingest_openfda_enforcement_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/ingest/cpsc.py: parse_cpsc_recall, cpsc_to_recall, cpsc_product_names, cpsc_upcs, cpsc_hazard_text, cpsc_remedy, cpsc_dates, cpsc_units, cpsc_is_food_contact
  tests/unit/test_ingest_cpsc.py  (behaviour of every public name)
  tests/unit/test_ingest_cpsc_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/ingest/store_list.py: parse_store_csv, normalize_store_format, parse_address, geocode_zip, assign_district, assign_dc, dedupe_stores, store_from_row, validate_store_list
  tests/unit/test_ingest_store_list.py  (behaviour of every public name)
  tests/unit/test_ingest_store_list_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/ingest/planogram.py: parse_planogram_row, planogram_to_facings, location_from_code, bay_capacity, shelf_positions, merge_planograms, planogram_diff, facing_units_estimate, validate_planogram
  tests/unit/test_ingest_planogram.py  (behaviour of every public name)
  tests/unit/test_ingest_planogram_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/ingest/staffing.py: parse_roster_row, roster_to_associates, parse_shift, shift_minutes, floater_pool, overnight_shift_window, roster_by_store, roster_by_district, validate_roster
  tests/unit/test_ingest_staffing.py  (behaviour of every public name)
  tests/unit/test_ingest_staffing_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/ingest/manifest_io.py: load_datapack_extended, write_datapack, datapack_stats, sample_datapack, filter_by_state, filter_by_stores, subset_skus, datapack_hash, compare_datapacks
  tests/unit/test_ingest_manifest_io.py  (behaviour of every public name)
  tests/unit/test_ingest_manifest_io_edge.py  (invalid inputs, boundaries, determinism)

## recallstorm/aliases/  (recallstorm/aliases/__init__.py re-exports the public names)
- recallstorm/aliases/translations.py: TRANSLATIONS, translate_alias, detect_language, alias_in_language, multilingual_patterns, accent_fold, translated_match, language_report, add_translation
  tests/unit/test_aliases_translations.py  (behaviour of every public name)
  tests/unit/test_aliases_translations_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/aliases/spans.py: Span, span_from_match, merge_spans, span_text, span_overlaps, shift_span, spans_to_offsets, highlight_spans, span_to_dict
  tests/unit/test_aliases_spans.py  (behaviour of every public name)
  tests/unit/test_aliases_spans_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/aliases/normalize.py: normalize_ingredients, strip_punctuation, collapse_whitespace, fold_unicode, ocr_fix, tokenize_ingredients, split_sub_ingredients, ingredient_offsets, denormalize_span
  tests/unit/test_aliases_normalize.py  (behaviour of every public name)
  tests/unit/test_aliases_normalize_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/aliases/lexicon.py: Lexicon, load_lexicon, aliases_for, additive_for_alias, add_alias, e_number_for, ci_number_for, translations_for, lexicon_from_rules
  tests/unit/test_aliases_lexicon.py  (behaviour of every public name)
  tests/unit/test_aliases_lexicon_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/aliases/detect.py: find_matches, find_first_match, match_span, match_confidence, is_decoy, decoy_reason, detect_all_additives, explain_match, MatchResult
  tests/unit/test_aliases_detect.py  (behaviour of every public name)
  tests/unit/test_aliases_detect_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/aliases/decoys.py: DECOY_PATTERNS, is_red40, is_dc_red_33, is_quantity_phrase, is_product_name_phrase, is_lake_pigment, decoy_examples, classify_red_mention, near_miss_report
  tests/unit/test_aliases_decoys.py  (behaviour of every public name)
  tests/unit/test_aliases_decoys_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/aliases/unclear.py: is_generic_color, is_unreadable, readability_score, generic_color_phrases, unclear_reason, needs_human_review, ocr_noise_ratio, truncated_label, redact_noise
  tests/unit/test_aliases_unclear.py  (behaviour of every public name)
  tests/unit/test_aliases_unclear_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/aliases/bundles.py: is_bundle, split_bundle, bundle_components, component_ingredients, bundle_contains, bundle_match_path, bundle_summary, kit_keywords, flatten_bundle
  tests/unit/test_aliases_bundles.py  (behaviour of every public name)
  tests/unit/test_aliases_bundles_edge.py  (invalid inputs, boundaries, determinism)

## recallstorm/rules/  (recallstorm/rules/__init__.py re-exports the public names)
- recallstorm/rules/potassium_bromate.py: bromate_aliases, detect_bromate, bromate_rules, evaluate_bromate, bromate_scope, bromate_rationale, bromate_evidence, bromate_effective, bromate_summary
  tests/unit/test_rules_potassium_bromate.py  (behaviour of every public name)
  tests/unit/test_rules_potassium_bromate_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/rules/propylparaben.py: paraben_aliases, detect_propylparaben, paraben_rules, evaluate_propylparaben, paraben_scope, paraben_rationale, paraben_evidence, paraben_effective, paraben_summary
  tests/unit/test_rules_propylparaben.py  (behaviour of every public name)
  tests/unit/test_rules_propylparaben_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/rules/preemption.py: federal_rule_for, state_rule_for, preemption_status, stricter_rule, effective_conflict, resolve_conflicts, preemption_report, preemption_matrix, PreemptionResolver
  tests/unit/test_rules_preemption.py  (behaviour of every public name)
  tests/unit/test_rules_preemption_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/rules/model.py: RuleSet, load_rules, rule_by_id, rules_for_state, rules_for_additive, rules_for_product_type, effective_local, rule_summary, ruleset_hash
  tests/unit/test_rules_model.py  (behaviour of every public name)
  tests/unit/test_rules_model_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/rules/jurisdiction.py: jurisdictions_for_state, applies_in_state, federal_applies, state_preempts, jurisdiction_rank, jurisdiction_chain, resolve_jurisdictions, state_name, state_codes
  tests/unit/test_rules_jurisdiction.py  (behaviour of every public name)
  tests/unit/test_rules_jurisdiction_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/rules/dates.py: effective_at, is_prohibited_at, days_until_effective, first_prohibited_instant, sell_through_allowed, local_deadline, deadline_for_store, deadlines_by_tz, next_effective_rule
  tests/unit/test_rules_dates.py  (behaviour of every public name)
  tests/unit/test_rules_dates_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/rules/scope.py: product_types_for_sku, sku_in_scope, is_food_scope, is_drug_scope, is_cosmetic_scope, scope_reason, exclude_reason, scope_matrix, applies_to_sku
  tests/unit/test_rules_scope.py  (behaviour of every public name)
  tests/unit/test_rules_scope_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/rules/red3.py: RED3_RULE_IDS, red3_rules, evaluate_red3, red3_rationale, red3_evidence, red3_clause, red3_aliases, red3_scope, red3_deadline
  tests/unit/test_rules_red3.py  (behaviour of every public name)
  tests/unit/test_rules_red3_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/rules/ab418.py: AB418_ADDITIVES, ab418_rules, evaluate_bvo, evaluate_potassium_bromate, evaluate_propylparaben, evaluate_red3_ca, ab418_clause, ab418_summary, ab418_effective
  tests/unit/test_rules_ab418.py  (behaviour of every public name)
  tests/unit/test_rules_ab418_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/rules/bvo.py: bvo_aliases, detect_bvo, bvo_rules, evaluate_bvo_federal, bvo_effective, bvo_rationale, bvo_beverage_scope, bvo_evidence, bvo_summary
  tests/unit/test_rules_bvo.py  (behaviour of every public name)
  tests/unit/test_rules_bvo_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/rules/pfas_mn.py: pfas_rules, detect_pfas_claim, pfas_product_categories, pfas_in_scope, pfas_effective, evaluate_pfas, pfas_rationale, pfas_evidence, pfas_summary
  tests/unit/test_rules_pfas_mn.py  (behaviour of every public name)
  tests/unit/test_rules_pfas_mn_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/rules/carb_voc.py: carb_voc_rules, voc_limit_for_category, parse_voc_percent, evaluate_voc, lubricant_in_scope, voc_rationale, voc_evidence, voc_effective, voc_summary
  tests/unit/test_rules_carb_voc.py  (behaviour of every public name)
  tests/unit/test_rules_carb_voc_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/rules/engine.py: evaluate_sku, evaluate_many, evaluate_pack, decision_to_record, merge_decisions, strictest_decision, decision_counts, explain_decision, RuleEngine
  tests/unit/test_rules_engine.py  (behaviour of every public name)
  tests/unit/test_rules_engine_edge.py  (invalid inputs, boundaries, determinism)

## recallstorm/adjudicate/  (recallstorm/adjudicate/__init__.py re-exports the public names)
- recallstorm/adjudicate/overrides.py: Override, apply_override, validate_override, override_to_record, overrides_for_sku, expire_overrides, override_reason_codes, override_report, OverrideBook
  tests/unit/test_adjudicate_overrides.py  (behaviour of every public name)
  tests/unit/test_adjudicate_overrides_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/adjudicate/sampling.py: sample_for_review, stratified_sample, review_rate, estimate_error_rate, confidence_interval, sample_report, seed_sampler, resample, SampleSet
  tests/unit/test_adjudicate_sampling.py  (behaviour of every public name)
  tests/unit/test_adjudicate_sampling_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/adjudicate/queue.py: ReviewQueue, enqueue, dequeue, queue_size, items_for_store, prioritize_items, mark_reviewed, queue_to_records, queue_from_records
  tests/unit/test_adjudicate_queue.py  (behaviour of every public name)
  tests/unit/test_adjudicate_queue_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/adjudicate/classifier.py: HeuristicClassifier, GeminiClassifier, classifier_prompt, parse_classifier_reply, classifier_decision, fallback_hold, confidence_threshold, batch_classify, ClassifierStats
  tests/unit/test_adjudicate_classifier.py  (behaviour of every public name)
  tests/unit/test_adjudicate_classifier_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/adjudicate/evidence.py: build_evidence, evidence_span, evidence_card, evidence_to_record, source_excerpt, highlight_match, link_evidence, evidence_index, validate_evidence
  tests/unit/test_adjudicate_evidence.py  (behaviour of every public name)
  tests/unit/test_adjudicate_evidence_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/adjudicate/audit.py: AuditTrail, record_decision, record_override, audit_to_records, decisions_by_source, overrides_by_user, audit_summary, audit_diff, verify_audit
  tests/unit/test_adjudicate_audit.py  (behaviour of every public name)
  tests/unit/test_adjudicate_audit_edge.py  (invalid inputs, boundaries, determinism)

## recallstorm/gs1/  (recallstorm/gs1/__init__.py re-exports the public names)
- recallstorm/gs1/epcis.py: parse_epcis_event, epcis_object_event, epcis_to_movements, epc_to_gtin, epcis_lot, epcis_location, filter_epcis_by_gtin, epcis_summary, EpcisDoc
  tests/unit/test_gs1_epcis.py  (behaviour of every public name)
  tests/unit/test_gs1_epcis_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/gs1/barcodes.py: upc_a_to_gtin, ean13_to_gtin, parse_scan_string, scan_to_gtin, is_variable_measure, strip_price_embedded, barcode_type, validate_scan, ScanResult
  tests/unit/test_gs1_barcodes.py  (behaviour of every public name)
  tests/unit/test_gs1_barcodes_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/gs1/gtin.py: gtin_check_digit, is_valid_gtin, normalize_gtin, gtin8_to_14, gtin12_to_14, gtin13_to_14, gtin_company_prefix, gtin_indicator, gtin_variants
  tests/unit/test_gs1_gtin.py  (behaviour of every public name)
  tests/unit/test_gs1_gtin_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/gs1/ai.py: parse_element_string, ai_01, ai_10, ai_17, ai_11, ai_21, build_element_string, ai_table, validate_ai
  tests/unit/test_gs1_ai.py  (behaviour of every public name)
  tests/unit/test_gs1_ai_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/gs1/digital_link.py: parse_digital_link, build_digital_link, digital_link_gtin, digital_link_lot, digital_link_expiry, is_digital_link, canonical_digital_link, digital_link_to_ais, ais_to_digital_link
  tests/unit/test_gs1_digital_link.py  (behaviour of every public name)
  tests/unit/test_gs1_digital_link_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/gs1/lots.py: parse_lot_code, lot_in_range, lot_range_from_text, normalize_lot, lot_matches_recall, expiry_in_range, date_range_overlap, lot_pattern, recall_lot_filter
  tests/unit/test_gs1_lots.py  (behaviour of every public name)
  tests/unit/test_gs1_lots_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/gs1/match.py: match_recall_to_skus, match_by_gtin, match_by_lot, match_by_name, match_score, best_match, unmatched_recalls, match_report, GtinIndex
  tests/unit/test_gs1_match.py  (behaviour of every public name)
  tests/unit/test_gs1_match_edge.py  (invalid inputs, boundaries, determinism)

## recallstorm/store/  (recallstorm/store/__init__.py re-exports the public names)
- recallstorm/store/backroom.py: backroom_locations, backroom_stock, topstock_for_sku, backroom_pull_task, backroom_capacity_left, stage_returns, staging_area, backroom_summary, Backroom
  tests/unit/test_store_backroom.py  (behaviour of every public name)
  tests/unit/test_store_backroom_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/store/signage.py: tag_flash_text, shelf_tag_for_sku, sign_template, sign_language, printer_queue, tags_for_store, tag_to_record, sign_summary, SignPrinter
  tests/unit/test_store_signage.py  (behaviour of every public name)
  tests/unit/test_store_signage_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/store/layout.py: StoreLayout, build_layout, aisle_order, bay_coordinates, location_xy, walking_distance, nearest_location, layout_bounds, layout_to_json
  tests/unit/test_store_layout.py  (behaviour of every public name)
  tests/unit/test_store_layout_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/store/facings.py: facings_for_store, facings_for_sku, affected_facings, units_on_shelf, facings_by_aisle, facing_key, locate_sku, facings_summary, group_facings
  tests/unit/test_store_facings.py  (behaviour of every public name)
  tests/unit/test_store_facings_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/store/exceptions.py: parse_note, note_to_exception, exception_kind_for_text, dsd_vendor_pull, endcap_display, topstock, pickup_totes, resolve_exception, exceptions_for_store
  tests/unit/test_store_exceptions.py  (behaviour of every public name)
  tests/unit/test_store_exceptions_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/store/formats.py: format_profile, carries_category, format_labor_minutes, format_tag_rule, format_backroom_capacity, format_summary, formats_in_pack, format_priority, is_club_format
  tests/unit/test_store_formats.py  (behaviour of every public name)
  tests/unit/test_store_formats_edge.py  (invalid inputs, boundaries, determinism)

## recallstorm/labor/  (recallstorm/labor/__init__.py re-exports the public names)
- recallstorm/labor/compliance.py: max_shift_minutes, break_required, meal_break_window, overtime_minutes, check_labor_rules, labor_violations, violation_to_record, labor_report, LaborRules
  tests/unit/test_labor_compliance.py  (behaviour of every public name)
  tests/unit/test_labor_compliance_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/labor/skills.py: associate_skills, can_handle_action, skill_for_task, certify_associate, skill_gaps, skill_matrix, train_plan, skills_summary, SkillBook
  tests/unit/test_labor_skills.py  (behaviour of every public name)
  tests/unit/test_labor_skills_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/labor/shifts.py: shift_window, shift_minutes_left, available_associates, associates_for_store, floaters_for_district, shift_overlaps, clamp_to_shift, shift_utilization, ShiftCalendar
  tests/unit/test_labor_shifts.py  (behaviour of every public name)
  tests/unit/test_labor_shifts_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/labor/estimates.py: pull_minutes, place_minutes, tag_minutes, walk_minutes, task_minutes, store_minutes, estimate_playbook, minutes_by_action, EstimateModel
  tests/unit/test_labor_estimates.py  (behaviour of every public name)
  tests/unit/test_labor_estimates_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/labor/assign.py: assign_tasks, greedy_assign, balance_load, assign_floaters, reassign_overflow, assignment_conflicts, assignment_summary, assignment_to_records, LaborPlan
  tests/unit/test_labor_assign.py  (behaviour of every public name)
  tests/unit/test_labor_assign_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/labor/floaters.py: floater_need, dispatch_floater, floater_windows, floater_handoffs, one_store_per_window, floater_travel_minutes, floater_plan_summary, validate_floaters, FloaterPool
  tests/unit/test_labor_floaters.py  (behaviour of every public name)
  tests/unit/test_labor_floaters_edge.py  (invalid inputs, boundaries, determinism)

## recallstorm/allocate/  (recallstorm/allocate/__init__.py re-exports the public names)
- recallstorm/allocate/stock.py: stock_for_dc, stock_for_sku, reserve_stock, release_stock, stock_after, stock_ledger, ledger_to_records, conservation_check, StockLedger
  tests/unit/test_allocate_stock.py  (behaviour of every public name)
  tests/unit/test_allocate_stock_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/allocate/priority.py: store_priority, format_weight, distance_weight, deadline_weight, priority_score, rank_stores, priority_report, tie_break_key, PriorityModel
  tests/unit/test_allocate_priority.py  (behaviour of every public name)
  tests/unit/test_allocate_priority_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/allocate/demand.py: demand_from_facings, demand_by_dc, demand_by_store, substitute_for_sku, demand_cases, total_demand, demand_to_records, unmet_demand, DemandTable
  tests/unit/test_allocate_demand.py  (behaviour of every public name)
  tests/unit/test_allocate_demand_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/allocate/allocator.py: allocate_substitutes, allocate_proportional, allocate_priority, allocation_balance, never_exceeds_stock, round_cases, tie_break, allocation_records, AllocationResult
  tests/unit/test_allocate_allocator.py  (behaviour of every public name)
  tests/unit/test_allocate_allocator_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/allocate/transfers.py: sub_transfers, transfer_handoff, dc_to_store_windows, transfer_cube, transfer_weight, transfers_by_truck, transfer_summary, validate_transfers, TransferPlan
  tests/unit/test_allocate_transfers.py  (behaviour of every public name)
  tests/unit/test_allocate_transfers_edge.py  (invalid inputs, boundaries, determinism)

## recallstorm/plan/  (recallstorm/plan/__init__.py re-exports the public names)
- recallstorm/plan/exceptions_plan.py: exception_tasks, dsd_exception_task, endcap_exception_task, topstock_exception_task, totes_exception_task, planogram_exception_task, unclear_label_task, exception_records, ExceptionPlanner
  tests/unit/test_plan_exceptions_plan.py  (behaviour of every public name)
  tests/unit/test_plan_exceptions_plan_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/plan/deadline.py: deadline_for_plan, window_before_deadline, shrink_window, late_risk, deadline_slack_minutes, enforce_deadline, deadline_report, deadline_violations, DeadlineGuard
  tests/unit/test_plan_deadline.py  (behaviour of every public name)
  tests/unit/test_plan_deadline_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/plan/explain.py: explain_task, explain_store, explain_sku, explain_allocation, explain_route, plan_narrative, why_hold, why_keep, Explainer
  tests/unit/test_plan_explain.py  (behaviour of every public name)
  tests/unit/test_plan_explain_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/plan/tasks.py: build_shelf_tasks, pull_task, place_sub_task, tag_flash_task, hold_verify_task, task_sequence, task_window, task_to_record, TaskBuilder
  tests/unit/test_plan_tasks.py  (behaviour of every public name)
  tests/unit/test_plan_tasks_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/plan/playbook.py: build_playbook, playbook_counts, playbook_windows, playbook_to_record, playbook_deadline, playbook_exceptions, playbook_manifests, playbook_summary, PlaybookBuilder
  tests/unit/test_plan_playbook.py  (behaviour of every public name)
  tests/unit/test_plan_playbook_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/plan/handoffs.py: build_handoffs, floater_handoff, return_consolidation, sub_transfer_handoff, handoff_to_record, pair_handoffs, handoff_windows, handoff_summary, HandoffBuilder
  tests/unit/test_plan_handoffs.py  (behaviour of every public name)
  tests/unit/test_plan_handoffs_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/plan/assemble.py: assemble_plan, plan_records, plan_to_jsonl, validate_plan_refs, plan_stats, run_record, plan_hash, merge_plans, PlanAssembler
  tests/unit/test_plan_assemble.py  (behaviour of every public name)
  tests/unit/test_plan_assemble_edge.py  (invalid inputs, boundaries, determinism)

## recallstorm/sim/  (recallstorm/sim/__init__.py re-exports the public names)
- recallstorm/sim/walking.py: walk_path, walk_seconds, aisle_graph, shortest_path, path_to_moves, congestion_penalty, walking_summary, speed_for_associate, WalkModel
  tests/unit/test_sim_walking.py  (behaviour of every public name)
  tests/unit/test_sim_walking_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/sim/disruptions.py: Disruption, inject_disruption, absent_associate, truck_delay, stockout_event, replan_after_disruption, disruption_report, seed_disruptions, DisruptionSet
  tests/unit/test_sim_disruptions.py  (behaviour of every public name)
  tests/unit/test_sim_disruptions_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/sim/events.py: MoveEvent, PullEvent, PlaceEvent, DoneEvent, event_to_record, events_to_jsonl, sort_events, events_for_store, events_for_associate
  tests/unit/test_sim_events.py  (behaviour of every public name)
  tests/unit/test_sim_events_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/sim/replay.py: replay_tasks, replay_store, replay_associate, walking_time, event_times, simulate_plan, replay_summary, detect_late_events, Replayer
  tests/unit/test_sim_replay.py  (behaviour of every public name)
  tests/unit/test_sim_replay_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/sim/metrics.py: completion_curve, tasks_done_by, pulled_units_by, placed_units_by, store_completion, district_completion, late_tasks, idle_minutes, MetricsReport
  tests/unit/test_sim_metrics.py  (behaviour of every public name)
  tests/unit/test_sim_metrics_edge.py  (invalid inputs, boundaries, determinism)

## recallstorm/scenario_gs1/  (recallstorm/scenario_gs1/__init__.py re-exports the public names)
- recallstorm/scenario_gs1/scenario.py: load_gs1_scenario, recall_from_openfda, recall_skus, recall_lots, recall_window, recall_rule, recall_plan, gs1_scenario_summary, Gs1Scenario
  tests/unit/test_scenario_gs1_scenario.py  (behaviour of every public name)
  tests/unit/test_scenario_gs1_scenario_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/scenario_gs1/lot_pull.py: lot_pull_tasks, lot_verify_task, lots_on_shelf, lot_quarantine, lot_pull_counts, lot_task_window, lot_evidence, lot_report, LotPuller
  tests/unit/test_scenario_gs1_lot_pull.py  (behaviour of every public name)
  tests/unit/test_scenario_gs1_lot_pull_edge.py  (invalid inputs, boundaries, determinism)

## recallstorm/route/  (recallstorm/route/__init__.py re-exports the public names)
- recallstorm/route/capacity.py: truck_capacity, remaining_cube, remaining_weight, capacity_check, overload_report, utilization_by_dc, capacity_to_record, capacity_summary, CapacityModel
  tests/unit/test_route_capacity.py  (behaviour of every public name)
  tests/unit/test_route_capacity_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/route/dispatch.py: dispatch_plan, depart_time, arrival_eta, driver_hours, dispatch_to_records, late_departures, dispatch_summary, validate_dispatch, Dispatcher
  tests/unit/test_route_dispatch.py  (behaviour of every public name)
  tests/unit/test_route_dispatch_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/route/returns.py: returned_cases, cases_by_store, cases_by_dc, case_cube, case_weight, returns_summary, returns_to_stops, validate_returns, ReturnLoad
  tests/unit/test_route_returns.py  (behaviour of every public name)
  tests/unit/test_route_returns_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/route/packing.py: pack_returns, first_fit_decreasing, pack_truck, fits_truck, truck_utilization, split_stop, manifest_to_record, packing_summary, PackingResult
  tests/unit/test_route_packing.py  (behaviour of every public name)
  tests/unit/test_route_packing_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/route/stops.py: order_stops, nearest_neighbor_order, route_distance, stop_eta, stops_for_truck, merge_stops, stop_to_record, stops_summary, RoutePlanner
  tests/unit/test_route_stops.py  (behaviour of every public name)
  tests/unit/test_route_stops_edge.py  (invalid inputs, boundaries, determinism)

## recallstorm/report/  (recallstorm/report/__init__.py re-exports the public names)
- recallstorm/report/summary.py: drill_summary, store_table, sku_table, counts_by_verdict, counts_by_action, summary_to_markdown, summary_to_json, compare_runs, SummaryReport
  tests/unit/test_report_summary.py  (behaviour of every public name)
  tests/unit/test_report_summary_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/report/checks.py: check_refs, check_conservation, check_capacity, check_labor, check_deadline, check_contradictions, run_all_checks, checks_to_json, CheckReport
  tests/unit/test_report_checks.py  (behaviour of every public name)
  tests/unit/test_report_checks_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/report/export.py: export_csv, export_markdown, export_store_packets, export_dc_packets, export_evidence, export_manifests, export_zip, export_index, Exporter
  tests/unit/test_report_export.py  (behaviour of every public name)
  tests/unit/test_report_export_edge.py  (invalid inputs, boundaries, determinism)
- recallstorm/report/dashboard.py: dashboard_data, map_points, store_status_colors, timeline_series, kpi_tiles, dashboard_to_json, dashboard_html, DashboardModel, DashboardBuilder
  tests/unit/test_report_dashboard.py  (behaviour of every public name)
  tests/unit/test_report_dashboard_edge.py  (invalid inputs, boundaries, determinism)

## recallstorm/cli/  (recallstorm/cli/__init__.py re-exports the public names)
- recallstorm/cli/main.py: main, build_parser, cmd_run, cmd_validate, cmd_stats, cmd_explain, cmd_replay, cmd_scenarios, exit_code_for
  tests/unit/test_cli_main.py  (behaviour of every public name)
  tests/unit/test_cli_main_edge.py  (invalid inputs, boundaries, determinism)

## recallstorm/__main__.py  (calls recallstorm.cli.main.main)
## tests/integration/  (12 files, test_flow_*.py, each exercising modules from at least 5 earlier packages)
## docs/  (architecture.md, data_model.md, rules.md, operations.md)
