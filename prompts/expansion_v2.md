You are expanding Recall Storm into a full platform in ONE continued generation.
contract.py is frozen and already exists. Everything you write must use it unchanged.

Write these packages in this exact order (the full required file list follows below) (positions matter for our measurements):
core/ (ID scheme, errors, config, logging) -> ingest/ (USDA FDC, Open Food Facts, openFDA enforcement, CPSC,
store list parsers) -> aliases/ -> rules/ (FDA Red No. 3 food and drug, CA AB 418 four additives, BVO,
Minnesota PFAS 116.943, CARB multi-purpose lubricant VOC; jurisdiction and date engine) -> adjudicate/ ->
gs1/ (GTIN check digits, AI 01/10/17, Digital Link, recall lot and date-range matching) -> store/ -> labor/ ->
allocate/ -> plan/ -> sim/ -> gs1-based recall scenario (openFDA lot codes) -> states/ -> recall_lots/ -> food_safety/ -> inventory/ -> pricing/ -> comms/ -> vendor/ -> dc_ops/ -> analytics/ -> governance/ -> route/ (LAST package) -> cli/ ->
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


REQUIRED FILES (emit every one, in this order; each module is followed immediately by its three test files).
Each module must define every listed public name (CamelCase = class, else function) with a docstring,
input validation and error handling, plus any private helpers it needs. Each test file tests every
public name of its module. You may add small helper modules; you may not drop or merge listed files.

## recallstorm/core/  (recallstorm/core/__init__.py re-exports the public names)
- recallstorm/core/ids.py: make_run_id, make_task_id, make_evidence_id, make_alloc_id, make_manifest_id, make_handoff_id, make_exc_id, parse_id, validate_id_prefix
  tests/unit/test_core_ids.py  (behaviour of every public name)
  tests/unit/test_core_ids_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_core_ids_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/core/errors.py: RecallStormError, DataValidationError, RuleConfigError, AllocationError, RoutingError, LaborError, ScenarioError, format_error, error_to_record
  tests/unit/test_core_errors.py  (behaviour of every public name)
  tests/unit/test_core_errors_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_core_errors_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/core/config.py: Config, load_config, default_config, merge_overrides, validate_config, config_from_env, config_to_dict, get_deadline, get_scenario_path
  tests/unit/test_core_config.py  (behaviour of every public name)
  tests/unit/test_core_config_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_core_config_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/core/logging_setup.py: get_logger, configure_logging, JsonlLogHandler, log_event, log_timing, with_context, redact_text, set_level, flush_all
  tests/unit/test_core_logging_setup.py  (behaviour of every public name)
  tests/unit/test_core_logging_setup_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_core_logging_setup_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/core/clock.py: to_local, from_local, local_wall, naive_local, is_before_deadline, minutes_between, window_overlaps, clamp_window, iso_with_offset
  tests/unit/test_core_clock.py  (behaviour of every public name)
  tests/unit/test_core_clock_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_core_clock_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/core/jsonl.py: read_jsonl, write_jsonl, append_jsonl, iter_jsonl, validate_record, record_with_src, sort_records, dedupe_by_key, stable_dumps
  tests/unit/test_core_jsonl.py  (behaviour of every public name)
  tests/unit/test_core_jsonl_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_core_jsonl_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/core/validate.py: validate_sku, validate_store, validate_facing, validate_associate, validate_truck, validate_rule, validate_datapack, collect_issues, issues_summary
  tests/unit/test_core_validate.py  (behaviour of every public name)
  tests/unit/test_core_validate_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_core_validate_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/core/registry.py: Registry, register_module, get_module, list_modules, src_path_for, emit_with_src, module_version, registry_snapshot, reset_registry
  tests/unit/test_core_registry.py  (behaviour of every public name)
  tests/unit/test_core_registry_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_core_registry_props.py  (property-style checks over generated inputs, fixed seed)

## recallstorm/ingest/  (recallstorm/ingest/__init__.py re-exports the public names)
- recallstorm/ingest/recall_feeds.py: parse_fsis_recall, parse_fda_rss, feed_item_to_recall, dedupe_recalls, recall_since, recall_by_state, merge_recall_sources, feed_cursor, RecallFeed
  tests/unit/test_ingest_recall_feeds.py  (behaviour of every public name)
  tests/unit/test_ingest_recall_feeds_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_ingest_recall_feeds_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/ingest/labels_ocr.py: parse_ocr_payload, ocr_text_blocks, ocr_confidence, join_ocr_lines, detect_ingredient_block, ocr_to_ingredients, flag_low_confidence, ocr_language, OcrLabel
  tests/unit/test_ingest_labels_ocr.py  (behaviour of every public name)
  tests/unit/test_ingest_labels_ocr_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_ingest_labels_ocr_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/ingest/vendor_catalog.py: parse_vendor_row, vendor_to_sku, vendor_dsd_flag, vendor_case_pack, vendor_reformulation_date, vendor_sub_suggestions, merge_vendor_catalog, vendor_contacts, VendorCatalog
  tests/unit/test_ingest_vendor_catalog.py  (behaviour of every public name)
  tests/unit/test_ingest_vendor_catalog_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_ingest_vendor_catalog_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/ingest/usda_fdc.py: parse_fdc_food, parse_fdc_search, fdc_to_sku, normalize_brand, normalize_category, fdc_ingredients, fdc_gtin, fdc_is_food, iter_fdc_pages
  tests/unit/test_ingest_usda_fdc.py  (behaviour of every public name)
  tests/unit/test_ingest_usda_fdc_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_ingest_usda_fdc_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/ingest/open_food_facts.py: parse_off_product, off_to_sku, off_ingredients_text, off_additive_tags, off_e_numbers, off_categories, off_gtin, off_language, merge_off_fdc
  tests/unit/test_ingest_open_food_facts.py  (behaviour of every public name)
  tests/unit/test_ingest_open_food_facts_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_ingest_open_food_facts_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/ingest/openfda_enforcement.py: parse_enforcement_report, enforcement_to_recall, extract_lot_codes, extract_date_ranges, extract_product_gtins, classify_recall_reason, recall_jurisdictions, recall_status, iter_enforcement_pages
  tests/unit/test_ingest_openfda_enforcement.py  (behaviour of every public name)
  tests/unit/test_ingest_openfda_enforcement_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_ingest_openfda_enforcement_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/ingest/cpsc.py: parse_cpsc_recall, cpsc_to_recall, cpsc_product_names, cpsc_upcs, cpsc_hazard_text, cpsc_remedy, cpsc_dates, cpsc_units, cpsc_is_food_contact
  tests/unit/test_ingest_cpsc.py  (behaviour of every public name)
  tests/unit/test_ingest_cpsc_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_ingest_cpsc_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/ingest/store_list.py: parse_store_csv, normalize_store_format, parse_address, geocode_zip, assign_district, assign_dc, dedupe_stores, store_from_row, validate_store_list
  tests/unit/test_ingest_store_list.py  (behaviour of every public name)
  tests/unit/test_ingest_store_list_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_ingest_store_list_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/ingest/planogram.py: parse_planogram_row, planogram_to_facings, location_from_code, bay_capacity, shelf_positions, merge_planograms, planogram_diff, facing_units_estimate, validate_planogram
  tests/unit/test_ingest_planogram.py  (behaviour of every public name)
  tests/unit/test_ingest_planogram_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_ingest_planogram_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/ingest/staffing.py: parse_roster_row, roster_to_associates, parse_shift, shift_minutes, floater_pool, overnight_shift_window, roster_by_store, roster_by_district, validate_roster
  tests/unit/test_ingest_staffing.py  (behaviour of every public name)
  tests/unit/test_ingest_staffing_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_ingest_staffing_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/ingest/manifest_io.py: load_datapack_extended, write_datapack, datapack_stats, sample_datapack, filter_by_state, filter_by_stores, subset_skus, datapack_hash, compare_datapacks
  tests/unit/test_ingest_manifest_io.py  (behaviour of every public name)
  tests/unit/test_ingest_manifest_io_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_ingest_manifest_io_props.py  (property-style checks over generated inputs, fixed seed)

## recallstorm/aliases/  (recallstorm/aliases/__init__.py re-exports the public names)
- recallstorm/aliases/translations.py: TRANSLATIONS, translate_alias, detect_language, alias_in_language, multilingual_patterns, accent_fold, translated_match, language_report, add_translation
  tests/unit/test_aliases_translations.py  (behaviour of every public name)
  tests/unit/test_aliases_translations_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_aliases_translations_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/aliases/spans.py: Span, span_from_match, merge_spans, span_text, span_overlaps, shift_span, spans_to_offsets, highlight_spans, span_to_dict
  tests/unit/test_aliases_spans.py  (behaviour of every public name)
  tests/unit/test_aliases_spans_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_aliases_spans_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/aliases/normalize.py: normalize_ingredients, strip_punctuation, collapse_whitespace, fold_unicode, ocr_fix, tokenize_ingredients, split_sub_ingredients, ingredient_offsets, denormalize_span
  tests/unit/test_aliases_normalize.py  (behaviour of every public name)
  tests/unit/test_aliases_normalize_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_aliases_normalize_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/aliases/lexicon.py: Lexicon, load_lexicon, aliases_for, additive_for_alias, add_alias, e_number_for, ci_number_for, translations_for, lexicon_from_rules
  tests/unit/test_aliases_lexicon.py  (behaviour of every public name)
  tests/unit/test_aliases_lexicon_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_aliases_lexicon_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/aliases/detect.py: find_matches, find_first_match, match_span, match_confidence, is_decoy, decoy_reason, detect_all_additives, explain_match, MatchResult
  tests/unit/test_aliases_detect.py  (behaviour of every public name)
  tests/unit/test_aliases_detect_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_aliases_detect_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/aliases/decoys.py: DECOY_PATTERNS, is_red40, is_dc_red_33, is_quantity_phrase, is_product_name_phrase, is_lake_pigment, decoy_examples, classify_red_mention, near_miss_report
  tests/unit/test_aliases_decoys.py  (behaviour of every public name)
  tests/unit/test_aliases_decoys_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_aliases_decoys_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/aliases/unclear.py: is_generic_color, is_unreadable, readability_score, generic_color_phrases, unclear_reason, needs_human_review, ocr_noise_ratio, truncated_label, redact_noise
  tests/unit/test_aliases_unclear.py  (behaviour of every public name)
  tests/unit/test_aliases_unclear_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_aliases_unclear_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/aliases/bundles.py: is_bundle, split_bundle, bundle_components, component_ingredients, bundle_contains, bundle_match_path, bundle_summary, kit_keywords, flatten_bundle
  tests/unit/test_aliases_bundles.py  (behaviour of every public name)
  tests/unit/test_aliases_bundles_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_aliases_bundles_props.py  (property-style checks over generated inputs, fixed seed)

## recallstorm/rules/  (recallstorm/rules/__init__.py re-exports the public names)
- recallstorm/rules/potassium_bromate.py: bromate_aliases, detect_bromate, bromate_rules, evaluate_bromate, bromate_scope, bromate_rationale, bromate_evidence, bromate_effective, bromate_summary
  tests/unit/test_rules_potassium_bromate.py  (behaviour of every public name)
  tests/unit/test_rules_potassium_bromate_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_rules_potassium_bromate_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/rules/propylparaben.py: paraben_aliases, detect_propylparaben, paraben_rules, evaluate_propylparaben, paraben_scope, paraben_rationale, paraben_evidence, paraben_effective, paraben_summary
  tests/unit/test_rules_propylparaben.py  (behaviour of every public name)
  tests/unit/test_rules_propylparaben_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_rules_propylparaben_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/rules/preemption.py: federal_rule_for, state_rule_for, preemption_status, stricter_rule, effective_conflict, resolve_conflicts, preemption_report, preemption_matrix, PreemptionResolver
  tests/unit/test_rules_preemption.py  (behaviour of every public name)
  tests/unit/test_rules_preemption_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_rules_preemption_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/rules/model.py: RuleSet, load_rules, rule_by_id, rules_for_state, rules_for_additive, rules_for_product_type, effective_local, rule_summary, ruleset_hash
  tests/unit/test_rules_model.py  (behaviour of every public name)
  tests/unit/test_rules_model_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_rules_model_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/rules/jurisdiction.py: jurisdictions_for_state, applies_in_state, federal_applies, state_preempts, jurisdiction_rank, jurisdiction_chain, resolve_jurisdictions, state_name, state_codes
  tests/unit/test_rules_jurisdiction.py  (behaviour of every public name)
  tests/unit/test_rules_jurisdiction_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_rules_jurisdiction_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/rules/dates.py: effective_at, is_prohibited_at, days_until_effective, first_prohibited_instant, sell_through_allowed, local_deadline, deadline_for_store, deadlines_by_tz, next_effective_rule
  tests/unit/test_rules_dates.py  (behaviour of every public name)
  tests/unit/test_rules_dates_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_rules_dates_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/rules/scope.py: product_types_for_sku, sku_in_scope, is_food_scope, is_drug_scope, is_cosmetic_scope, scope_reason, exclude_reason, scope_matrix, applies_to_sku
  tests/unit/test_rules_scope.py  (behaviour of every public name)
  tests/unit/test_rules_scope_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_rules_scope_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/rules/red3.py: RED3_RULE_IDS, red3_rules, evaluate_red3, red3_rationale, red3_evidence, red3_clause, red3_aliases, red3_scope, red3_deadline
  tests/unit/test_rules_red3.py  (behaviour of every public name)
  tests/unit/test_rules_red3_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_rules_red3_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/rules/ab418.py: AB418_ADDITIVES, ab418_rules, evaluate_bvo, evaluate_potassium_bromate, evaluate_propylparaben, evaluate_red3_ca, ab418_clause, ab418_summary, ab418_effective
  tests/unit/test_rules_ab418.py  (behaviour of every public name)
  tests/unit/test_rules_ab418_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_rules_ab418_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/rules/bvo.py: bvo_aliases, detect_bvo, bvo_rules, evaluate_bvo_federal, bvo_effective, bvo_rationale, bvo_beverage_scope, bvo_evidence, bvo_summary
  tests/unit/test_rules_bvo.py  (behaviour of every public name)
  tests/unit/test_rules_bvo_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_rules_bvo_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/rules/pfas_mn.py: pfas_rules, detect_pfas_claim, pfas_product_categories, pfas_in_scope, pfas_effective, evaluate_pfas, pfas_rationale, pfas_evidence, pfas_summary
  tests/unit/test_rules_pfas_mn.py  (behaviour of every public name)
  tests/unit/test_rules_pfas_mn_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_rules_pfas_mn_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/rules/carb_voc.py: carb_voc_rules, voc_limit_for_category, parse_voc_percent, evaluate_voc, lubricant_in_scope, voc_rationale, voc_evidence, voc_effective, voc_summary
  tests/unit/test_rules_carb_voc.py  (behaviour of every public name)
  tests/unit/test_rules_carb_voc_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_rules_carb_voc_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/rules/engine.py: evaluate_sku, evaluate_many, evaluate_pack, decision_to_record, merge_decisions, strictest_decision, decision_counts, explain_decision, RuleEngine
  tests/unit/test_rules_engine.py  (behaviour of every public name)
  tests/unit/test_rules_engine_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_rules_engine_props.py  (property-style checks over generated inputs, fixed seed)

## recallstorm/adjudicate/  (recallstorm/adjudicate/__init__.py re-exports the public names)
- recallstorm/adjudicate/overrides.py: Override, apply_override, validate_override, override_to_record, overrides_for_sku, expire_overrides, override_reason_codes, override_report, OverrideBook
  tests/unit/test_adjudicate_overrides.py  (behaviour of every public name)
  tests/unit/test_adjudicate_overrides_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_adjudicate_overrides_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/adjudicate/sampling.py: sample_for_review, stratified_sample, review_rate, estimate_error_rate, confidence_interval, sample_report, seed_sampler, resample, SampleSet
  tests/unit/test_adjudicate_sampling.py  (behaviour of every public name)
  tests/unit/test_adjudicate_sampling_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_adjudicate_sampling_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/adjudicate/queue.py: ReviewQueue, enqueue, dequeue, queue_size, items_for_store, prioritize_items, mark_reviewed, queue_to_records, queue_from_records
  tests/unit/test_adjudicate_queue.py  (behaviour of every public name)
  tests/unit/test_adjudicate_queue_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_adjudicate_queue_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/adjudicate/classifier.py: HeuristicClassifier, GeminiClassifier, classifier_prompt, parse_classifier_reply, classifier_decision, fallback_hold, confidence_threshold, batch_classify, ClassifierStats
  tests/unit/test_adjudicate_classifier.py  (behaviour of every public name)
  tests/unit/test_adjudicate_classifier_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_adjudicate_classifier_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/adjudicate/evidence.py: build_evidence, evidence_span, evidence_card, evidence_to_record, source_excerpt, highlight_match, link_evidence, evidence_index, validate_evidence
  tests/unit/test_adjudicate_evidence.py  (behaviour of every public name)
  tests/unit/test_adjudicate_evidence_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_adjudicate_evidence_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/adjudicate/audit.py: AuditTrail, record_decision, record_override, audit_to_records, decisions_by_source, overrides_by_user, audit_summary, audit_diff, verify_audit
  tests/unit/test_adjudicate_audit.py  (behaviour of every public name)
  tests/unit/test_adjudicate_audit_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_adjudicate_audit_props.py  (property-style checks over generated inputs, fixed seed)

## recallstorm/gs1/  (recallstorm/gs1/__init__.py re-exports the public names)
- recallstorm/gs1/epcis.py: parse_epcis_event, epcis_object_event, epcis_to_movements, epc_to_gtin, epcis_lot, epcis_location, filter_epcis_by_gtin, epcis_summary, EpcisDoc
  tests/unit/test_gs1_epcis.py  (behaviour of every public name)
  tests/unit/test_gs1_epcis_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_gs1_epcis_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/gs1/barcodes.py: upc_a_to_gtin, ean13_to_gtin, parse_scan_string, scan_to_gtin, is_variable_measure, strip_price_embedded, barcode_type, validate_scan, ScanResult
  tests/unit/test_gs1_barcodes.py  (behaviour of every public name)
  tests/unit/test_gs1_barcodes_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_gs1_barcodes_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/gs1/gtin.py: gtin_check_digit, is_valid_gtin, normalize_gtin, gtin8_to_14, gtin12_to_14, gtin13_to_14, gtin_company_prefix, gtin_indicator, gtin_variants
  tests/unit/test_gs1_gtin.py  (behaviour of every public name)
  tests/unit/test_gs1_gtin_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_gs1_gtin_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/gs1/ai.py: parse_element_string, ai_01, ai_10, ai_17, ai_11, ai_21, build_element_string, ai_table, validate_ai
  tests/unit/test_gs1_ai.py  (behaviour of every public name)
  tests/unit/test_gs1_ai_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_gs1_ai_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/gs1/digital_link.py: parse_digital_link, build_digital_link, digital_link_gtin, digital_link_lot, digital_link_expiry, is_digital_link, canonical_digital_link, digital_link_to_ais, ais_to_digital_link
  tests/unit/test_gs1_digital_link.py  (behaviour of every public name)
  tests/unit/test_gs1_digital_link_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_gs1_digital_link_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/gs1/lots.py: parse_lot_code, lot_in_range, lot_range_from_text, normalize_lot, lot_matches_recall, expiry_in_range, date_range_overlap, lot_pattern, recall_lot_filter
  tests/unit/test_gs1_lots.py  (behaviour of every public name)
  tests/unit/test_gs1_lots_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_gs1_lots_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/gs1/match.py: match_recall_to_skus, match_by_gtin, match_by_lot, match_by_name, match_score, best_match, unmatched_recalls, match_report, GtinIndex
  tests/unit/test_gs1_match.py  (behaviour of every public name)
  tests/unit/test_gs1_match_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_gs1_match_props.py  (property-style checks over generated inputs, fixed seed)

## recallstorm/store/  (recallstorm/store/__init__.py re-exports the public names)
- recallstorm/store/backroom.py: backroom_locations, backroom_stock, topstock_for_sku, backroom_pull_task, backroom_capacity_left, stage_returns, staging_area, backroom_summary, Backroom
  tests/unit/test_store_backroom.py  (behaviour of every public name)
  tests/unit/test_store_backroom_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_store_backroom_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/store/signage.py: tag_flash_text, shelf_tag_for_sku, sign_template, sign_language, printer_queue, tags_for_store, tag_to_record, sign_summary, SignPrinter
  tests/unit/test_store_signage.py  (behaviour of every public name)
  tests/unit/test_store_signage_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_store_signage_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/store/layout.py: StoreLayout, build_layout, aisle_order, bay_coordinates, location_xy, walking_distance, nearest_location, layout_bounds, layout_to_json
  tests/unit/test_store_layout.py  (behaviour of every public name)
  tests/unit/test_store_layout_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_store_layout_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/store/facings.py: facings_for_store, facings_for_sku, affected_facings, units_on_shelf, facings_by_aisle, facing_key, locate_sku, facings_summary, group_facings
  tests/unit/test_store_facings.py  (behaviour of every public name)
  tests/unit/test_store_facings_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_store_facings_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/store/exceptions.py: parse_note, note_to_exception, exception_kind_for_text, dsd_vendor_pull, endcap_display, topstock, pickup_totes, resolve_exception, exceptions_for_store
  tests/unit/test_store_exceptions.py  (behaviour of every public name)
  tests/unit/test_store_exceptions_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_store_exceptions_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/store/formats.py: format_profile, carries_category, format_labor_minutes, format_tag_rule, format_backroom_capacity, format_summary, formats_in_pack, format_priority, is_club_format
  tests/unit/test_store_formats.py  (behaviour of every public name)
  tests/unit/test_store_formats_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_store_formats_props.py  (property-style checks over generated inputs, fixed seed)

## recallstorm/labor/  (recallstorm/labor/__init__.py re-exports the public names)
- recallstorm/labor/compliance.py: max_shift_minutes, break_required, meal_break_window, overtime_minutes, check_labor_rules, labor_violations, violation_to_record, labor_report, LaborRules
  tests/unit/test_labor_compliance.py  (behaviour of every public name)
  tests/unit/test_labor_compliance_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_labor_compliance_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/labor/skills.py: associate_skills, can_handle_action, skill_for_task, certify_associate, skill_gaps, skill_matrix, train_plan, skills_summary, SkillBook
  tests/unit/test_labor_skills.py  (behaviour of every public name)
  tests/unit/test_labor_skills_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_labor_skills_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/labor/shifts.py: shift_window, shift_minutes_left, available_associates, associates_for_store, floaters_for_district, shift_overlaps, clamp_to_shift, shift_utilization, ShiftCalendar
  tests/unit/test_labor_shifts.py  (behaviour of every public name)
  tests/unit/test_labor_shifts_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_labor_shifts_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/labor/estimates.py: pull_minutes, place_minutes, tag_minutes, walk_minutes, task_minutes, store_minutes, estimate_playbook, minutes_by_action, EstimateModel
  tests/unit/test_labor_estimates.py  (behaviour of every public name)
  tests/unit/test_labor_estimates_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_labor_estimates_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/labor/assign.py: assign_tasks, greedy_assign, balance_load, assign_floaters, reassign_overflow, assignment_conflicts, assignment_summary, assignment_to_records, LaborPlan
  tests/unit/test_labor_assign.py  (behaviour of every public name)
  tests/unit/test_labor_assign_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_labor_assign_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/labor/floaters.py: floater_need, dispatch_floater, floater_windows, floater_handoffs, one_store_per_window, floater_travel_minutes, floater_plan_summary, validate_floaters, FloaterPool
  tests/unit/test_labor_floaters.py  (behaviour of every public name)
  tests/unit/test_labor_floaters_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_labor_floaters_props.py  (property-style checks over generated inputs, fixed seed)

## recallstorm/allocate/  (recallstorm/allocate/__init__.py re-exports the public names)
- recallstorm/allocate/stock.py: stock_for_dc, stock_for_sku, reserve_stock, release_stock, stock_after, stock_ledger, ledger_to_records, conservation_check, StockLedger
  tests/unit/test_allocate_stock.py  (behaviour of every public name)
  tests/unit/test_allocate_stock_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_allocate_stock_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/allocate/priority.py: store_priority, format_weight, distance_weight, deadline_weight, priority_score, rank_stores, priority_report, tie_break_key, PriorityModel
  tests/unit/test_allocate_priority.py  (behaviour of every public name)
  tests/unit/test_allocate_priority_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_allocate_priority_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/allocate/demand.py: demand_from_facings, demand_by_dc, demand_by_store, substitute_for_sku, demand_cases, total_demand, demand_to_records, unmet_demand, DemandTable
  tests/unit/test_allocate_demand.py  (behaviour of every public name)
  tests/unit/test_allocate_demand_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_allocate_demand_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/allocate/allocator.py: allocate_substitutes, allocate_proportional, allocate_priority, allocation_balance, never_exceeds_stock, round_cases, tie_break, allocation_records, AllocationResult
  tests/unit/test_allocate_allocator.py  (behaviour of every public name)
  tests/unit/test_allocate_allocator_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_allocate_allocator_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/allocate/transfers.py: sub_transfers, transfer_handoff, dc_to_store_windows, transfer_cube, transfer_weight, transfers_by_truck, transfer_summary, validate_transfers, TransferPlan
  tests/unit/test_allocate_transfers.py  (behaviour of every public name)
  tests/unit/test_allocate_transfers_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_allocate_transfers_props.py  (property-style checks over generated inputs, fixed seed)

## recallstorm/plan/  (recallstorm/plan/__init__.py re-exports the public names)
- recallstorm/plan/exceptions_plan.py: exception_tasks, dsd_exception_task, endcap_exception_task, topstock_exception_task, totes_exception_task, planogram_exception_task, unclear_label_task, exception_records, ExceptionPlanner
  tests/unit/test_plan_exceptions_plan.py  (behaviour of every public name)
  tests/unit/test_plan_exceptions_plan_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_plan_exceptions_plan_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/plan/deadline.py: deadline_for_plan, window_before_deadline, shrink_window, late_risk, deadline_slack_minutes, enforce_deadline, deadline_report, deadline_violations, DeadlineGuard
  tests/unit/test_plan_deadline.py  (behaviour of every public name)
  tests/unit/test_plan_deadline_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_plan_deadline_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/plan/explain.py: explain_task, explain_store, explain_sku, explain_allocation, explain_route, plan_narrative, why_hold, why_keep, Explainer
  tests/unit/test_plan_explain.py  (behaviour of every public name)
  tests/unit/test_plan_explain_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_plan_explain_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/plan/tasks.py: build_shelf_tasks, pull_task, place_sub_task, tag_flash_task, hold_verify_task, task_sequence, task_window, task_to_record, TaskBuilder
  tests/unit/test_plan_tasks.py  (behaviour of every public name)
  tests/unit/test_plan_tasks_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_plan_tasks_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/plan/playbook.py: build_playbook, playbook_counts, playbook_windows, playbook_to_record, playbook_deadline, playbook_exceptions, playbook_manifests, playbook_summary, PlaybookBuilder
  tests/unit/test_plan_playbook.py  (behaviour of every public name)
  tests/unit/test_plan_playbook_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_plan_playbook_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/plan/handoffs.py: build_handoffs, floater_handoff, return_consolidation, sub_transfer_handoff, handoff_to_record, pair_handoffs, handoff_windows, handoff_summary, HandoffBuilder
  tests/unit/test_plan_handoffs.py  (behaviour of every public name)
  tests/unit/test_plan_handoffs_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_plan_handoffs_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/plan/assemble.py: assemble_plan, plan_records, plan_to_jsonl, validate_plan_refs, plan_stats, run_record, plan_hash, merge_plans, PlanAssembler
  tests/unit/test_plan_assemble.py  (behaviour of every public name)
  tests/unit/test_plan_assemble_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_plan_assemble_props.py  (property-style checks over generated inputs, fixed seed)

## recallstorm/sim/  (recallstorm/sim/__init__.py re-exports the public names)
- recallstorm/sim/walking.py: walk_path, walk_seconds, aisle_graph, shortest_path, path_to_moves, congestion_penalty, walking_summary, speed_for_associate, WalkModel
  tests/unit/test_sim_walking.py  (behaviour of every public name)
  tests/unit/test_sim_walking_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_sim_walking_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/sim/disruptions.py: Disruption, inject_disruption, absent_associate, truck_delay, stockout_event, replan_after_disruption, disruption_report, seed_disruptions, DisruptionSet
  tests/unit/test_sim_disruptions.py  (behaviour of every public name)
  tests/unit/test_sim_disruptions_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_sim_disruptions_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/sim/events.py: MoveEvent, PullEvent, PlaceEvent, DoneEvent, event_to_record, events_to_jsonl, sort_events, events_for_store, events_for_associate
  tests/unit/test_sim_events.py  (behaviour of every public name)
  tests/unit/test_sim_events_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_sim_events_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/sim/replay.py: replay_tasks, replay_store, replay_associate, walking_time, event_times, simulate_plan, replay_summary, detect_late_events, Replayer
  tests/unit/test_sim_replay.py  (behaviour of every public name)
  tests/unit/test_sim_replay_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_sim_replay_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/sim/metrics.py: completion_curve, tasks_done_by, pulled_units_by, placed_units_by, store_completion, district_completion, late_tasks, idle_minutes, MetricsReport
  tests/unit/test_sim_metrics.py  (behaviour of every public name)
  tests/unit/test_sim_metrics_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_sim_metrics_props.py  (property-style checks over generated inputs, fixed seed)

## recallstorm/scenario_gs1/  (recallstorm/scenario_gs1/__init__.py re-exports the public names)
- recallstorm/scenario_gs1/scenario.py: load_gs1_scenario, recall_from_openfda, recall_skus, recall_lots, recall_window, recall_rule, recall_plan, gs1_scenario_summary, Gs1Scenario
  tests/unit/test_scenario_gs1_scenario.py  (behaviour of every public name)
  tests/unit/test_scenario_gs1_scenario_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_scenario_gs1_scenario_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/scenario_gs1/lot_pull.py: lot_pull_tasks, lot_verify_task, lots_on_shelf, lot_quarantine, lot_pull_counts, lot_task_window, lot_evidence, lot_report, LotPuller
  tests/unit/test_scenario_gs1_lot_pull.py  (behaviour of every public name)
  tests/unit/test_scenario_gs1_lot_pull_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_scenario_gs1_lot_pull_props.py  (property-style checks over generated inputs, fixed seed)

## recallstorm/states/  (recallstorm/states/__init__.py re-exports the public names)
- recallstorm/states/ny_food_additives.py: NyAdditiveRule, TitaniumDioxideCheck, check_ny_ban_date, evaluate_tio2_exemption, parse_ny_senate_bill, build_ny_violation_record, filter_ny_store_zips, map_ny_ingredient_aliases, calculate_ny_civil_penalty, exempt_ny_in_transit_stock, generate_ny_compliance_memo, validate_ny_label_claim
  tests/unit/test_states_ny_food_additives.py  (behaviour of every public name)
  tests/unit/test_states_ny_food_additives_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_states_ny_food_additives_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/states/ny_dietary_supplements.py: NySupplementAgeGate, WeightLossClaimMatcher, is_restricted_ny_supplement, verify_ny_pos_id_prompt, scan_muscle_building_claims, flag_creatine_products, check_ny_delivery_age_gate, audit_ny_self_checkout_block, classify_ny_thermogenic_sku, generate_ny_ag_notice, map_ny_supplement_aisles, validate_ny_courier_handoff
  tests/unit/test_states_ny_dietary_supplements.py  (behaviour of every public name)
  tests/unit/test_states_ny_dietary_supplements_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_states_ny_dietary_supplements_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/states/il_food_safety_act.py: IlAdditiveBanRule, IlGracePeriodTracker, check_il_sb2637_scope, evaluate_il_bakery_exemption, calculate_il_sell_through_days, filter_il_jurisdiction_stores, parse_il_idph_guidance, build_il_shelf_pull_order, verify_il_reformulated_lot, assess_il_distributor_liability, format_il_inspection_sheet, track_il_phase_out_schedule
  tests/unit/test_states_il_food_safety_act.py  (behaviour of every public name)
  tests/unit/test_states_il_food_safety_act_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_states_il_food_safety_act_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/states/pa_synthetic_dyes.py: PaSchoolDyeRule, PaSyntheticDyeList, check_pa_dye_concentration, flag_red40_yellow5_skus, evaluate_pa_school_zone_store, verify_pa_warning_label_text, map_pa_affected_categories, calculate_pa_pack_exposure, generate_pa_parent_advisory, filter_pa_vending_inventory, validate_pa_catering_menu, audit_pa_confectionery_endcaps
  tests/unit/test_states_pa_synthetic_dyes.py  (behaviour of every public name)
  tests/unit/test_states_pa_synthetic_dyes_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_states_pa_synthetic_dyes_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/states/wa_toxic_free_kids.py: WaTfkcaRule, HighPriorityChemicalList, check_wa_phthalates_ppm, evaluate_wa_childrens_product, verify_wa_ecology_reporting, calculate_wa_de_minimis_threshold, flag_wa_bisphenol_packaging, parse_wa_cspa_notice_list, build_wa_Ecology_declaration, filter_wa_baby_aisle_skus, validate_wa_supplier_assay, generate_wa_recall_directive
  tests/unit/test_states_wa_toxic_free_kids.py  (behaviour of every public name)
  tests/unit/test_states_wa_toxic_free_kids_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_states_wa_toxic_free_kids_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/states/wa_pfas_packaging.py: WaPfasPackagingBan, PlantFiberWrapperCheck, test_wa_fluorine_ppm_limit, evaluate_wa_compostable_claim, check_wa_deli_paper_lots, flag_wa_greaseproof_containers, verify_wa_alternative_assessment, map_wa_fresh_dept_packaging, calculate_wa_packaging_fines, audit_wa_bakery_clam_shells, generate_wa_pfas_certificate, filter_wa_in_store_prep_wraps
  tests/unit/test_states_wa_pfas_packaging.py  (behaviour of every public name)
  tests/unit/test_states_wa_pfas_packaging_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_states_wa_pfas_packaging_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/states/nj_lead_cadmium.py: NjHeavyMetalRule, NjActionLevelTable, check_nj_candy_lead_ppb, evaluate_nj_spice_cadmium_limit, parse_nj_doh_embargo_order, flag_nj_imported_turmeric, verify_nj_lot_coa_metals, calculate_nj_daily_intake_exposure, build_nj_quarantine_tag, filter_nj_ethnic_aisle_skus, generate_nj_lab_retest_request, validate_nj_embargo_release
  tests/unit/test_states_nj_lead_cadmium.py  (behaviour of every public name)
  tests/unit/test_states_nj_lead_cadmium_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_states_nj_lead_cadmium_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/states/mn_toxic_free_kids.py: MnPriorityChemicalRule, MnLeadCadmiumBan, check_mn_toy_jewelry_ppm, evaluate_mn_child_mouthable_item, verify_mn_mdh_waiver_status, flag_mn_seasonal_novelty_skus, calculate_mn_surface_coating_limit, parse_mn_statute_325f_177, build_mn_merchant_stop_sale, filter_mn_checklane_impulses, audit_mn_vendor_test_reports, generate_mn_disposal_manifest
  tests/unit/test_states_mn_toxic_free_kids.py  (behaviour of every public name)
  tests/unit/test_states_mn_toxic_free_kids_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_states_mn_toxic_free_kids_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/states/tx_consumable_hemp.py: TxHempRetailRule, DshsHempRegistration, check_tx_delta9_thc_pct, verify_tx_qr_code_link, validate_tx_batch_coa_date, evaluate_tx_smokeable_ban, flag_tx_unregistered_brands, check_tx_child_resistant_cap, filter_tx_beverage_endcaps, generate_tx_dshs_audit_log, calculate_tx_hemp_tax_hold, audit_tx_license_expiration
  tests/unit/test_states_tx_consumable_hemp.py  (behaviour of every public name)
  tests/unit/test_states_tx_consumable_hemp_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_states_tx_consumable_hemp_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/states/la_seafood_labeling.py: LaCountryOfOriginRule, LaImportedShrimpCheck, verify_la_placard_font_size, check_la_crawfish_origin_claim, evaluate_la_fluoroquinolone_ban, flag_la_unlabeled_bulk_bins, parse_la_ldaf_stop_order, build_la_seafood_case_signage, calculate_la_misbranding_fine, audit_la_service_counter_tags, filter_la_frozen_bunker_skus, validate_la_processor_permit
  tests/unit/test_states_la_seafood_labeling.py  (behaviour of every public name)
  tests/unit/test_states_la_seafood_labeling_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_states_la_seafood_labeling_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/states/wv_kratom_hemp_act.py: WvSelectPlantRule, WvAgeVerificationMandate, check_wv_mitragynine_limit, evaluate_wv_synthetic_alkaloids, verify_wv_wvda_product_permit, flag_wv_adulterated_tinctures, check_wv_warning_statement_box, filter_wv_c_store_formats, build_wv_seizure_readiness_pack, calculate_wv_unregistered_penalty, validate_wv_lab_accreditation, audit_wv_display_case_locks
  tests/unit/test_states_wv_kratom_hemp_act.py  (behaviour of every public name)
  tests/unit/test_states_wv_kratom_hemp_act_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_states_wv_kratom_hemp_act_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/states/ut_cotinine_nicotine.py: UtElectronicCigaretteRule, UtSpecialtyPermitCheck, check_ut_nicotine_volume_cap, evaluate_ut_flavor_restriction, verify_ut_tax_stamp_presence, flag_ut_unauthorized_vape_skus, parse_ut_dhhs_banned_list, build_ut_cage_removal_task, filter_ut_front_end_fixtures, calculate_ut_revocation_risk, validate_ut_wholesaler_invoice, audit_ut_age_scanner_logs
  tests/unit/test_states_ut_cotinine_nicotine.py  (behaviour of every public name)
  tests/unit/test_states_ut_cotinine_nicotine_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_states_ut_cotinine_nicotine_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/states/az_kratom_consumer_act.py: AzKratomStandardRule, AzAlkaloidRatioCheck, verify_az_7_oh_fraction_limit, check_az_dosage_instructions, evaluate_az_synthetic_adulterants, flag_az_confectionery_forms, validate_az_label_disclaimer_text, filter_az_wellness_aisle_skus, build_az_vendor_indemnity_check, calculate_az_civil_forfeiture, audit_az_batch_alkaloid_panel, generate_az_stop_sale_notice
  tests/unit/test_states_az_kratom_consumer_act.py  (behaviour of every public name)
  tests/unit/test_states_az_kratom_consumer_act_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_states_az_kratom_consumer_act_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/states/ca_prop65_warnings.py: Prop65SafeHarborRule, AcrylamideExposureCheck, verify_prop65_shelf_sign_placement, check_prop65_bpa_canned_goods, evaluate_prop65_short_form_label, parse_oehha_chemical_list_update, flag_prop65_private_enforcer_notice, calculate_prop65_daily_madl_ug, map_prop65_pos_receipt_warnings, filter_prop65_unwarned_imports, build_prop65_consent_judgment_rule, audit_prop65_bakery_sign_hooks
  tests/unit/test_states_ca_prop65_warnings.py  (behaviour of every public name)
  tests/unit/test_states_ca_prop65_warnings_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_states_ca_prop65_warnings_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/states/me_pfas_products.py: MePfasReportingRule, MeCuuExemptionCheck, verify_me_dep_notification_id, check_me_intentionally_added_pfas, evaluate_me_cookware_coating_skus, flag_me_unreported_fabric_sprays, calculate_me_reporting_fee_tier, parse_me_title_38_section_1614, build_me_vendor_disclosure_request, filter_me_housewares_planogram, validate_me_cas_registry_match, generate_me_sales_prohibition_list
  tests/unit/test_states_me_pfas_products.py  (behaviour of every public name)
  tests/unit/test_states_me_pfas_products_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_states_me_pfas_products_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/states/vt_mercury_battery.py: VtExtendedProducerRule, VtButtonCellBanCheck, verify_vt_stewardship_plan_membership, check_vt_alkaline_mercury_ppm, evaluate_vt_embedded_battery_skus, flag_vt_non_compliant_greeting_cards, parse_vt_anr_brand_directory, build_vt_endcap_battery_pull, filter_vt_electronics_blister_packs, calculate_vt_recycling_surcharge, validate_vt_packaging_symbol_mark, audit_vt_seasonal_toy_shipments
  tests/unit/test_states_vt_mercury_battery.py  (behaviour of every public name)
  tests/unit/test_states_vt_mercury_battery_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_states_vt_mercury_battery_props.py  (property-style checks over generated inputs, fixed seed)

## recallstorm/recall_lots/  (recallstorm/recall_lots/__init__.py re-exports the public names)
- recallstorm/recall_lots/fda_notice_parser.py: FdaEnforcementNotice, ExtractedRecallMetadata, parse_fda_press_release_html, extract_recalling_firm_feis, identify_fda_recall_class, parse_fda_reason_for_recall, extract_upc_list_from_text, normalize_fda_code_info_block, split_multi_brand_table, detect_undeclared_allergen_type, link_fda_res_event_number, validate_parsed_notice_schema
  tests/unit/test_recall_lots_fda_notice_parser.py  (behaviour of every public name)
  tests/unit/test_recall_lots_fda_notice_parser_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_recall_lots_fda_notice_parser_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/recall_lots/fsis_notice_parser.py: FsisRecallRelease, EstNumberExtractor, parse_fsis_establishment_code, extract_usda_inspection_mark, classify_fsis_health_hazard_level, parse_fsis_production_date_span, extract_fsis_case_code_strings, identify_fsis_import_country, match_fsis_retail_consignee_pdf, normalize_usda_product_title, parse_fsis_poultry_serial_range, validate_fsis_notice_completeness
  tests/unit/test_recall_lots_fsis_notice_parser.py  (behaviour of every public name)
  tests/unit/test_recall_lots_fsis_notice_parser_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_recall_lots_fsis_notice_parser_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/recall_lots/lot_pattern_matcher.py: LotPatternSpec, WildcardLotMatcher, compile_lot_glob_expression, match_alphanumeric_lot_range, strip_lot_prefix_noise, evaluate_julian_date_lot, parse_plant_line_shift_code, match_embossed_can_code, handle_ocr_confused_characters, score_lot_string_similarity, expand_hyphenated_lot_span, validate_lot_against_regex_bank
  tests/unit/test_recall_lots_lot_pattern_matcher.py  (behaviour of every public name)
  tests/unit/test_recall_lots_lot_pattern_matcher_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_recall_lots_lot_pattern_matcher_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/recall_lots/best_by_window.py: DateWindowSpec, ExpirationFormatParser, parse_stamped_date_string, normalize_two_digit_year, evaluate_inclusive_date_range, convert_julian_to_calendar_date, check_freeze_by_extension, flag_unreadable_inkjet_dates, calculate_shelf_life_backdate_lot, match_pack_date_to_best_by, handle_month_year_only_stamps, validate_window_chronology
  tests/unit/test_recall_lots_best_by_window.py  (behaviour of every public name)
  tests/unit/test_recall_lots_best_by_window_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_recall_lots_best_by_window_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/recall_lots/distribution_list.py: ConsigneeListParser, DistributionFootprint, parse_fda_state_distribution_text, map_nationwide_exclusions, resolve_dba_retailer_names, match_banner_to_parent_corp, geo_filter_affected_divisions, reconcile_broker_ship_to_list, flag_unlisted_transshipment_risk, intersect_states_with_store_master, rank_stores_by_shipment_volume, export_affected_store_roster
  tests/unit/test_recall_lots_distribution_list.py  (behaviour of every public name)
  tests/unit/test_recall_lots_distribution_list_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_recall_lots_distribution_list_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/recall_lots/depth_of_recall.py: RecallDepthLevel, DepthPolicyEngine, determine_consumer_vs_retail_depth, evaluate_wholesale_only_quarantine, trigger_point_of_sale_lockout, assign_public_placard_requirement, configure_customer_outreach_tier, check_institutional_foodservice_scope, escalate_class_i_depth_rules, map_depth_to_labor_urgency, validate_depth_against_fda_class, generate_depth_execution_matrix
  tests/unit/test_recall_lots_depth_of_recall.py  (behaviour of every public name)
  tests/unit/test_recall_lots_depth_of_recall_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_recall_lots_depth_of_recall_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/recall_lots/effectiveness_checks.py: EffectivenessCheckQuestionnaire, EdcResponseCompiler, select_fda_level_a_through_e_sample, generate_store_verification_survey, calculate_effectiveness_completion_pct, flag_non_responding_locations, compile_affidavit_return_counts, verify_physical_destruction_photos, audit_sub_account_notification_logs, score_check_timeliness_sla, build_fda_district_status_report, trigger_recheck_for_discrepancies
  tests/unit/test_recall_lots_effectiveness_checks.py  (behaviour of every public name)
  tests/unit/test_recall_lots_effectiveness_checks_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_recall_lots_effectiveness_checks_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/recall_lots/serial_traceability.py: SerialShippingContainerCode, CaseSerialTracker, match_sscc18_pallet_labels, trace_serialized_case_to_aisle, resolve_mixed_pallet_parent_child, verify_epcis_commissioning_event, flag_orphan_serial_scans, query_serialized_receiving_logs, build_serial_custody_chain, detect_duplicate_counterfeit_serials, calculate_serial_recovery_rate, export_unaccounted_serial_list
  tests/unit/test_recall_lots_serial_traceability.py  (behaviour of every public name)
  tests/unit/test_recall_lots_serial_traceability_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_recall_lots_serial_traceability_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/recall_lots/catch_weight_lots.py: CatchWeightLotRecord, VariableWeightBarcodeParser, extract_embedded_price_weight_upc, link_scale_plu_to_primal_lot, calculate_meat_chub_yield_loss, reconcile_case_weight_to_packages, trace_in_store_grind_logs, match_deli_slicing_batch_sheet, flag_commingled_trim_batches, estimate_unweighed_case_count, validate_tare_weight_deductions, generate_scale_purge_directive
  tests/unit/test_recall_lots_catch_weight_lots.py  (behaviour of every public name)
  tests/unit/test_recall_lots_catch_weight_lots_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_recall_lots_catch_weight_lots_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/recall_lots/sub_recall_cascade.py: IngredientCascadeGraph, DownstreamSkuResolver, map_raw_lot_to_finished_goods, trace_commissary_recipe_boms, identify_in_store_bakery_mixes, flag_prepared_foods_salads, calculate_generational_dilution_factor, resolve_co_packer_cross_supply, propagate_recall_to_meal_kits, build_cascade_impact_tree, audit_central_kitchen_batch_logs, generate_derivative_sku_pull_list
  tests/unit/test_recall_lots_sub_recall_cascade.py  (behaviour of every public name)
  tests/unit/test_recall_lots_sub_recall_cascade_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_recall_lots_sub_recall_cascade_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/recall_lots/consignee_reconciliation.py: ConsigneeShipmentLedger, ShipToMatcher, match_asn_bol_to_recall_lots, reconcile_billed_vs_received_cases, identify_drop_ship_store_deliveries, flag_diverted_wholesaler_loads, calculate_net_shipped_exposure, resolve_dc_cross_dock_splits, audit_unmatched_po_receipts, track_in_transit_carrier_trailers, generate_consignee_variance_table, verify_zero_shipment_attestation
  tests/unit/test_recall_lots_consignee_reconciliation.py  (behaviour of every public name)
  tests/unit/test_recall_lots_consignee_reconciliation_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_recall_lots_consignee_reconciliation_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/recall_lots/mock_recall_generator.py: SyntheticRecallScenario, MockLotInjector, synthesize_class_i_listeria_notice, inject_seeded_lots_into_wms, generate_realistic_lot_typos, create_multi_dc_split_scenario, configure_blind_drill_parameters, plant_decoy_unaffected_lots, scale_scenario_store_count, generate_mock_press_release_pdf, build_expected_ground_truth_key, validate_scenario_solvability
  tests/unit/test_recall_lots_mock_recall_generator.py  (behaviour of every public name)
  tests/unit/test_recall_lots_mock_recall_generator_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_recall_lots_mock_recall_generator_props.py  (property-style checks over generated inputs, fixed seed)

## recallstorm/food_safety/  (recallstorm/food_safety/__init__.py re-exports the public names)
- recallstorm/food_safety/temperature_holds.py: ColdChainExcursionLog, TimeTempAbuseEvaluator, parse_reefer_data_logger_csv, calculate_cumulative_degree_minutes, evaluate_fda_tcs_four_hour_rule, flag_defrost_cycle_anomalies, trigger_cooler_failure_quarantine, assess_frozen_thaw_refreeze_risk, map_multi_deck_case_zones, generate_temp_hold_pallet_tags, validate_probe_calibration_status, authorize_disposition_after_review
  tests/unit/test_food_safety_temperature_holds.py  (behaviour of every public name)
  tests/unit/test_food_safety_temperature_holds_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_food_safety_temperature_holds_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/food_safety/allergen_cross_contact.py: AllergenMatrix, LineChangeoverValidator, detect_shared_fryer_exposure, evaluate_bakery_rack_drip_risk, check_deli_slicer_cleaning_gap, flag_bulk_bin_scoop_migration, verify_allergen_segregation_planogram, audit_in_store_repack_labels, trace_sesame_flour_dust_zones, build_allergen_sanitation_task, validate_may_contain_advisory_override, score_cross_contact_severity
  tests/unit/test_food_safety_allergen_cross_contact.py  (behaviour of every public name)
  tests/unit/test_food_safety_allergen_cross_contact_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_food_safety_allergen_cross_contact_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/food_safety/sanitation_logs.py: SsopExecutionRecord, SwabVerificationTracker, schedule_listeria_zone_1_swabs, verify_quaternary_ammonia_ppm, log_food_contact_atp_rlu_scores, trigger_post_recall_deep_clean, validate_drain_sanitation_signoff, track_chemical_dispensing_titration, flag_overdue_slicer_teardown, link_sanitation_crew_to_aisle, audit_third_party_pest_reports, generate_ssop_remediation_ticket
  tests/unit/test_food_safety_sanitation_logs.py  (behaviour of every public name)
  tests/unit/test_food_safety_sanitation_logs_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_food_safety_sanitation_logs_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/food_safety/consumer_complaints.py: IllnessComplaintTicket, ClusterSignalDetector, ingest_call_center_symptom_log, calculate_incubation_period_match, detect_geographic_complaint_cluster, link_loyalty_card_purchase_lot, escalate_hospitalization_report, check_foreign_material_photo_hash, cross_reference_iwaspoisoned_feed, trigger_precautionary_lot_hold, generate_fda_medwatch_draft, track_sample_retrieval_courier
  tests/unit/test_food_safety_consumer_complaints.py  (behaviour of every public name)
  tests/unit/test_food_safety_consumer_complaints_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_food_safety_consumer_complaints_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/food_safety/sampling_plans.py: MicrobiologicalSamplingPlan, IcmsfAcceptanceCriteria, calculate_icmsf_case_class_plan, assign_composite_sub_sample_units, generate_aseptic_collection_protocol, track_chain_of_custody_seal, parse_pcr_presumptive_positive, evaluate_wgs_snp_distance_match, manage_hold_and_test_release, flag_lab_turnaround_sla_breach, build_cpsc_destructive_test_lot, archive_certificate_of_analysis
  tests/unit/test_food_safety_sampling_plans.py  (behaviour of every public name)
  tests/unit/test_food_safety_sampling_plans_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_food_safety_sampling_plans_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/food_safety/haccp_deviations.py: CcpDeviationEvent, CorrectiveActionPlan, evaluate_cooking_lethality_log, flag_metal_detector_reject_spike, verify_cooling_curve_compliance, trigger_haccp_reassessment_hold, document_root_cause_disposition, validate_test_piece_challenge_log, link_deviation_to_batch_id, lock_affected_production_window, require_qa_manager_countersign, generate_fsis_noncompliance_response
  tests/unit/test_food_safety_haccp_deviations.py  (behaviour of every public name)
  tests/unit/test_food_safety_haccp_deviations_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_food_safety_haccp_deviations_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/food_safety/foreign_material.py: ForeignMaterialIncident, XrayInspectionAudit, classify_fragment_material_type, check_fda_hard_sharp_7mm_rule, trace_broken_belt_maintenance_log, match_sieve_screen_mesh_failure, evaluate_glass_brittle_plastic_breakage, isolate_upstream_dumper_lots, verify_magnet_pull_test_records, calculate_complaint_per_million_units, build_supplier_foreign_object_claim, generate_sensory_inspection_protocol
  tests/unit/test_food_safety_foreign_material.py  (behaviour of every public name)
  tests/unit/test_food_safety_foreign_material_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_food_safety_foreign_material_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/food_safety/water_ice_safety.py: BoilWaterAdvisoryResponse, IceMachineSanitation, map_utility_boil_water_polygons, disable_produce_misting_systems, quarantine_packaged_store_ice, lock_fountain_beverage_dispensers, schedule_carbon_filter_replacement, verify_potable_water_tanker_coa, track_post_advisory_line_flushing, audit_seafood_ice_flaker_swabs, generate_food_prep_shutdown_checklist, authorize_water_system_reopen
  tests/unit/test_food_safety_water_ice_safety.py  (behaviour of every public name)
  tests/unit/test_food_safety_water_ice_safety_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_food_safety_water_ice_safety_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/food_safety/produce_wash_logs.py: ProduceCrispingRecord, AntimicrobialWashMonitor, verify_peracetic_acid_ppm_range, log_wash_tank_water_temp_diff, flag_cut_fruit_immersion_timeout, track_leafy_green_lot_commingling, validate_test_strip_lot_expiry, audit_single_pass_rinse_flow, link_cut_room_batch_to_trays, trigger_wash_solution_dump_alert, calculate_cut_produce_display_hours, generate_fresh_cut_pull_sheet
  tests/unit/test_food_safety_produce_wash_logs.py  (behaviour of every public name)
  tests/unit/test_food_safety_produce_wash_logs_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_food_safety_produce_wash_logs_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/food_safety/date_code_audits.py: RotationComplianceAudit, ExpiredStockSweep, generate_random_aisle_date_walk, calculate_close_dated_shrink_risk, flag_fifo_rotation_violations, verify_infant_formula_hard_pull, check_otc_drug_expiration_window, score_department_freshness_index, identify_chronic_overstock_skus, schedule_markdown_before_expiry, track_associate_rotation_velocity, export_expired_pull_log
  tests/unit/test_food_safety_date_code_audits.py  (behaviour of every public name)
  tests/unit/test_food_safety_date_code_audits_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_food_safety_date_code_audits_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/food_safety/pest_control_holds.py: PestSightingQuarantine, GnawDamageEvaluator, log_rodent_evidence_location, map_adjacent_pallet_buffer_zone, verify_uv_blacklight_urine_scan, quarantine_compromised_dry_goods, schedule_licensed_fumigation_visit, track_pheromone_trap_catch_counts, audit_dock_door_brush_seals, authorize_sealed_can_salvage_wash, generate_pest_destruction_affidavit, link_sighting_to_3pl_trailer
  tests/unit/test_food_safety_pest_control_holds.py  (behaviour of every public name)
  tests/unit/test_food_safety_pest_control_holds_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_food_safety_pest_control_holds_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/food_safety/salvage_reconditioning.py: ReconditioningProtocol, SalvageEligibilityEngine, evaluate_dented_can_seam_integrity, check_smoke_water_damage_exposure, apply_fda_reconditioning_guidelines, calculate_rework_labor_viability, track_relabeling_allergen_stickers, verify_state_inspector_supervision, segregate_non_salvageable_leakers, audit_salvage_broker_credentials, generate_reconditioned_lot_code, record_rework_yield_shrinkage
  tests/unit/test_food_safety_salvage_reconditioning.py  (behaviour of every public name)
  tests/unit/test_food_safety_salvage_reconditioning_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_food_safety_salvage_reconditioning_props.py  (property-style checks over generated inputs, fixed seed)

## recallstorm/inventory/  (recallstorm/inventory/__init__.py re-exports the public names)
- recallstorm/inventory/on_hand_reconciliation.py: PerpetualInventoryLedger, RecallVarianceReconciler, snapshot_pre_recall_book_inventory, compare_physical_pull_to_on_hand, resolve_in_transit_asn_quantities, adjust_phantom_inventory_balances, account_for_unscanned_pos_cart_items, reconcile_click_and_collect_stagings, flag_negative_on_hand_anomalies, calculate_unexplained_lot_discrepancy, post_erp_inventory_adjustment_journal, lock_sku_from_auto_replenishment
  tests/unit/test_inventory_on_hand_reconciliation.py  (behaviour of every public name)
  tests/unit/test_inventory_on_hand_reconciliation_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_inventory_on_hand_reconciliation_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/inventory/shrink_accounting.py: RecallShrinkJournal, FinancialWriteOffEngine, classify_vendor_funded_vs_retail_loss, calculate_landed_cost_extended_value, post_general_ledger_shrink_entries, allocate_destruction_hauling_fees, value_in_store_production_wip_loss, track_insurance_deductible_accumulation, reconcile_swell_allowance_offsets, generate_tax_deduction_destruction_cert, audit_high_value_shrink_approvals, export_period_end_recall_accrual
  tests/unit/test_inventory_shrink_accounting.py  (behaviour of every public name)
  tests/unit/test_inventory_shrink_accounting_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_inventory_shrink_accounting_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/inventory/cycle_count_triggers.py: EmergencyCycleCountTask, BlindCountVerifier, dispatch_zero_confirm_aisle_counts, require_dual_associate_blind_count, verify_empty_peg_hook_status, audit_top_stock_riser_locations, reconcile_display_endcap_secondary_locs, flag_unexpected_found_lot_stock, prioritize_high_velocity_store_counts, track_rf_scanner_count_timestamps, validate_case_pack_unit_conversion, close_cycle_count_investigation
  tests/unit/test_inventory_cycle_count_triggers.py  (behaviour of every public name)
  tests/unit/test_inventory_cycle_count_triggers_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_inventory_cycle_count_triggers_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/inventory/quarantine_bins.py: QuarantineCageManager, DigitalHoldLocation, assign_locked_backroom_cage_bin, generate_red_hold_pallet_license_plate, enforce_wms_directed_putaway_block, verify_physical_padlock_seal_number, track_quarantine_bin_capacity_cube, prevent_pick_from_quarantine_loc, log_authorized_quarantine_access, audit_aged_quarantine_dwell_time, consolidate_partial_hold_cases, release_cleared_bin_to_active
  tests/unit/test_inventory_quarantine_bins.py  (behaviour of every public name)
  tests/unit/test_inventory_quarantine_bins_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_inventory_quarantine_bins_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/inventory/reverse_logistics_acct.py: ReturnMerchandiseAuth, ReverseFreightLedger, generate_vendor_rma_reference_id, match_bill_of_lading_to_rma, value_return_center_staging_stock, track_3pl_reclamation_center_scans, reconcile_crushed_bale_weights, audit_hazmat_disposal_surcharges, calculate_restocking_fee_exemptions, post_pending_vendor_credit_memo, age_unsettled_return_receivables, close_completed_reverse_loop
  tests/unit/test_inventory_reverse_logistics_acct.py  (behaviour of every public name)
  tests/unit/test_inventory_reverse_logistics_acct_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_inventory_reverse_logistics_acct_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/inventory/lot_level_perpetual.py: LotSubLedgerEngine, FefoDepletionModel, estimate_lot_on_hand_by_receipt_date, model_fefo_customer_depletion_curve, ingest_epcis_case_depletion_events, bound_lot_presence_probability, reconcile_mixed_lot_shelf_bins, update_lot_balance_from_pull_scan, track_backroom_case_lot_tags, identify_stale_unrotated_lot_layers, export_store_lot_exposure_range, validate_lot_subledger_integrity
  tests/unit/test_inventory_lot_level_perpetual.py  (behaviour of every public name)
  tests/unit/test_inventory_lot_level_perpetual_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_inventory_lot_level_perpetual_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/inventory/in_transit_interception.py: InTransitShipmentHold, ASNInterceptor, scan_open_purchase_orders_for_lot, flag_inbound_dsd_delivery_manifests, alert_store_receiving_dock_handhelds, divert_en_route_dc_trailers, generate_refusal_at_dock_instruction, track_refused_freight_return_bol, update_expected_receipt_ledger, notify_carrier_dispatcher_of_hold, verify_seal_intact_on_refusal, reconcile_short_ship_from_intercept
  tests/unit/test_inventory_in_transit_interception.py  (behaviour of every public name)
  tests/unit/test_inventory_in_transit_interception_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_inventory_in_transit_interception_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/inventory/ecommerce_dark_stores.py: MicroFulfillmentHold, OrderPickInterceptor, purge_recalled_sku_from_web_search, cancel_unfulfilled_bopis_line_items, intercept_staged_curbside_totes, halt_autostore_bin_presentation, reroute_instacart_shopper_pick_path, flag_in_flight_last_mile_couriers, process_automatic_digital_refunds, quarantine_dark_store_decant_totes, audit_locker_pickup_compartments, sync_virtual_inventory_availability
  tests/unit/test_inventory_ecommerce_dark_stores.py  (behaviour of every public name)
  tests/unit/test_inventory_ecommerce_dark_stores_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_inventory_ecommerce_dark_stores_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/inventory/consignment_stock.py: ScanBasedTradingLedger, ConsignmentHoldTracker, identify_sbt_vendor_owned_skus, exclude_consignment_from_shrink_gl, notify_sbt_route_representative, record_zero_cost_quarantine_units, verify_dsd_driver_buyback_scan, reconcile_consignment_pad_counts, block_sbt_daily_pos_settlement, audit_unremoved_vendor_racks, generate_consignment_removal_receipt, validate_sbt_contract_recall_terms
  tests/unit/test_inventory_consignment_stock.py  (behaviour of every public name)
  tests/unit/test_inventory_consignment_stock_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_inventory_consignment_stock_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/inventory/sample_demo_stock.py: DemoStationQuarantine, ClubStoreSampleHold, halt_active_in_store_sampling_events, quarantine_demo_prep_cart_inventory, reconcile_expensed_demo_unit_transfers, alert_third_party_demo_agency_lead, verify_trash_compactor_sample_disposal, audit_bakery_free_cookie_bins, check_pharmacy_immunization_promos, log_open_package_demo_destruction, calculate_unbilled_sample_exposure, clear_demo_station_sanitation_hold
  tests/unit/test_inventory_sample_demo_stock.py  (behaviour of every public name)
  tests/unit/test_inventory_sample_demo_stock_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_inventory_sample_demo_stock_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/inventory/cross_dock_allocation.py: CrossDockHoldInterceptor, FlowThroughSplitter, identify_pre_allocated_cross_dock_pallets, break_store_assigned_pallet_ties, divert_flow_through_to_dc_hold, recalculation_store_allocation_shorts, update_wms_put_to_store_lights, cancel_outbound_shipping_labels, record_cross_dock_interception_scan, balance_multi_store_master_cartons, notify_merchandising_of_cut_allocations, release_uncontaminated_sibling_cases
  tests/unit/test_inventory_cross_dock_allocation.py  (behaviour of every public name)
  tests/unit/test_inventory_cross_dock_allocation_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_inventory_cross_dock_allocation_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/inventory/destruction_witness.py: WitnessedDestructionRecord, CompactorLogTracker, schedule_regulatory_witness_appointment, capture_compactor_cycle_video_hash, record_denaturing_chemical_application, weigh_pre_destruction_pallet_gross, generate_dual_signature_affidavit, verify_landfill_manifest_ticket_id, upload_geotagged_destruction_photos, audit_unwitnessed_disposal_exceptions, lock_destroyed_lpn_in_wms, archive_epa_rcra_waste_profile
  tests/unit/test_inventory_destruction_witness.py  (behaviour of every public name)
  tests/unit/test_inventory_destruction_witness_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_inventory_destruction_witness_props.py  (property-style checks over generated inputs, fixed seed)

## recallstorm/pricing/  (recallstorm/pricing/__init__.py re-exports the public names)
- recallstorm/pricing/pos_sale_blocks.py: PosHardLockRule, RegisterBlockInjector, compile_pos_stop_sale_xml_payload, push_emergency_plu_lock_to_lanes, verify_lane_sync_heartbeat_status, block_manual_department_key_entry, intercept_weight_embedded_barcodes, test_self_checkout_override_denial, log_blocked_scan_attempt_events, handle_offline_register_resync, generate_cashier_halt_screen_text, audit_pos_lock_coverage_by_store
  tests/unit/test_pricing_pos_sale_blocks.py  (behaviour of every public name)
  tests/unit/test_pricing_pos_sale_blocks_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_pricing_pos_sale_blocks_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/pricing/price_lookup_blocks.py: PluScaleDeactivator, TareAndPluSync, purge_recalled_plu_from_deli_scales, disable_bakery_self_serve_plu_buttons, push_scale_network_lockout_file, verify_hobart_toledo_scale_ack, block_produce_cashier_look_up_menu, prevent_in_store_bar_code_printing, archive_deactivated_plu_recipe_text, monitor_scale_firmware_sync_errors, restore_cleared_plu_price_tables, audit_unnetworked_standalone_scales
  tests/unit/test_pricing_price_lookup_blocks.py  (behaviour of every public name)
  tests/unit/test_pricing_price_lookup_blocks_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_pricing_price_lookup_blocks_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/pricing/register_prompts.py: CashierPromptConfig, LotCheckDialogBuilder, configure_date_code_entry_prompt, build_lot_prefix_validation_screen, require_supervisor_key_flick_override, display_safe_lot_visual_guide, capture_cashier_entered_lot_string, throttle_prompt_for_unaffected_upcs, track_prompt_bypass_rate_by_cashier, localize_register_prompt_translations, A_B_test_prompt_clarity_speed, disable_expired_lot_check_prompts
  tests/unit/test_pricing_register_prompts.py  (behaviour of every public name)
  tests/unit/test_pricing_register_prompts_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_pricing_register_prompts_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/pricing/promotion_conflicts.py: PromoConflictScanner, CircularAdPuller, scan_upcoming_weekly_print_circulars, flag_recalled_items_in_digital_coupons, cancel_active_bogo_deal_triggers, remove_sku_from_endcap_theme_kits, calculate_raincheck_liability_suspension, coordinate_ad_correction_apology_sign, reallocate_feature_space_to_sub, halt_automated_social_media_ads, adjust_vendor_coop_ad_funding_claim, audit_loyalty_app_personalized_offers
  tests/unit/test_pricing_promotion_conflicts.py  (behaviour of every public name)
  tests/unit/test_pricing_promotion_conflicts_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_pricing_promotion_conflicts_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/pricing/markdown_controls.py: MarkdownLockoutEngine, ClearanceTagBlocker, freeze_automated_cadence_markdowns, block_handheld_cvp_yellow_sticker_print, invalidate_existing_clearance_barcodes, recall_discounted_bakery_day_old_racks, prevent_manager_special_price_override, audit_recent_markdown_scan_history, reverse_pending_price_change_batches, flag_suspicious_pre_recall_markdowns, reconcile_markdown_journal_reversals, enforce_zero_salvage_price_floor
  tests/unit/test_pricing_markdown_controls.py  (behaviour of every public name)
  tests/unit/test_pricing_markdown_controls_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_pricing_markdown_controls_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/pricing/substitute_pricing.py: PriceMatchOverrideRule, SubPriceParityEngine, authorize_equal_or_lesser_sub_price, configure_bopis_substitution_discount, cap_margin_erosion_on_national_sub, sync_electronic_shelf_label_sub_price, waive_delivery_fee_for_recalled_sub, calculate_promotional_price_carryover, prevent_price_gouging_on_alternatives, track_sub_price_override_redemptions, reconcile_vendor_funded_sub_subsidy, restore_base_retail_after_restock
  tests/unit/test_pricing_substitute_pricing.py  (behaviour of every public name)
  tests/unit/test_pricing_substitute_pricing_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_pricing_substitute_pricing_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/pricing/electronic_shelf_labels.py: EslFlashController, DigitalTagBlanker, flash_esl_led_for_associate_pull, overwrite_esl_screen_with_recall_notice, verify_esl_gateway_transmission_ack, detect_unresponsive_low_battery_tags, batch_update_aisle_esl_templates, lock_esl_from_planogram_price_push, map_esl_mac_address_to_shelf_position, trigger_high_contrast_out_of_stock_view, audit_esl_update_latency_sla, restore_normal_price_display_layout
  tests/unit/test_pricing_electronic_shelf_labels.py  (behaviour of every public name)
  tests/unit/test_pricing_electronic_shelf_labels_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_pricing_electronic_shelf_labels_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/pricing/refund_policies.py: RecallRefundPolicy, NoReceiptReturnEngine, enable_no_receipt_full_retail_refund, bypass_return_window_day_limits, calculate_state_bottle_deposit_refund, issue_extra_goodwill_loyalty_points, process_opened_consumed_package_return, link_refund_scan_to_quarantine_bin, prevent_returned_item_restock_to_shelf, flag_serial_return_fraud_velocity, generate_customer_refund_receipt_disclaimer, reconcile_recall_refund_tender_totals
  tests/unit/test_pricing_refund_policies.py  (behaviour of every public name)
  tests/unit/test_pricing_refund_policies_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_pricing_refund_policies_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/pricing/wic_ebt_blocks.py: WicAplHotfixEngine, EbtEligibilityBlocker, remove_recalled_upc_from_state_wic_apl, coordinate_emergency_wic_substitute_approval, handle_infant_formula_wic_voucher_swap, block_snap_ebt_tender_for_banned_item, update_self_checkout_wic_validation_table, generate_wic_participant_shelf_talker, log_declined_wic_benefit_attempts, notify_state_wic_agency_liaison, validate_cereal_size_ounce_substitute, audit_wic_reimbursement_adjustments
  tests/unit/test_pricing_wic_ebt_blocks.py  (behaviour of every public name)
  tests/unit/test_pricing_wic_ebt_blocks_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_pricing_wic_ebt_blocks_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/pricing/price_file_governance.py: EmergencyPriceFilePush, PosSyncAuditor, validate_emergency_item_maintenance_batch, sign_cryptographic_price_file_hash, monitor_store_controller_apply_status, trigger_fallback_dialup_price_push, compare_host_vs_lane_item_record, quarantine_corrupt_plu_delta_files, escalate_stalled_store_pos_controllers, log_price_file_override_authorizations, verify_multi_banner_price_zone_scope, archive_point_in_time_pos_table
  tests/unit/test_pricing_price_file_governance.py  (behaviour of every public name)
  tests/unit/test_pricing_price_file_governance_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_pricing_price_file_governance_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/pricing/bottle_deposit_credits.py: ContainerDepositReconciler, CrvRedemptionBlocker, calculate_unredeemed_crv_tax_credit, block_reverse_vending_machine_barcodes, reconcile_distributor_deposit_chargebacks, adjust_crushed_beverage_can_counts, handle_multi_state_deposit_rate_diffs, generate_calrecycle_destruction_notice, audit_bottle_room_quarantine_bags, credit_customer_deposit_on_recall_return, waive_handling_fee_on_recalled_flats, export_state_beverage_container_report
  tests/unit/test_pricing_bottle_deposit_credits.py  (behaviour of every public name)
  tests/unit/test_pricing_bottle_deposit_credits_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_pricing_bottle_deposit_credits_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/pricing/coupon_clearinghouse.py: CouponRedemptionHalt, ClearinghouseNotifier, suspend_gs1_8112_universal_digital_coupons, notify_inmar_nch_of_recalled_family_code, block_paper_coupon_family_prefix_scan, void_clipped_loyalty_wallet_offers, reconcile_pre_recall_coupon_submissions, prevent_Catalina_register_printer_triggers, adjust_manufacturer_redemption_invoices, flag_raincheck_coupon_combinations, audit_override_coupon_key_entries, archive_suspended_promotion_campaigns
  tests/unit/test_pricing_coupon_clearinghouse.py  (behaviour of every public name)
  tests/unit/test_pricing_coupon_clearinghouse_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_pricing_coupon_clearinghouse_props.py  (property-style checks over generated inputs, fixed seed)

## recallstorm/comms/  (recallstorm/comms/__init__.py re-exports the public names)
- recallstorm/comms/store_notices.py: StoreActionBulletin, UrgentRecallFlash, compile_single_page_store_action_sheet, highlight_affected_lot_visual_callouts, embed_product_package_reference_photos, translate_bulletin_for_multilingual_crews, route_notice_by_store_department_scope, track_store_manager_read_receipt_ack, version_control_amended_recall_notices, generate_printable_backroom_poster_pdf, push_urgent_banner_to_zebra_handhelds, archive_superseded_bulletin_versions
  tests/unit/test_comms_store_notices.py  (behaviour of every public name)
  tests/unit/test_comms_store_notices_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_comms_store_notices_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/comms/associate_briefings.py: ShiftHuddleScript, AssociateBriefingTracker, generate_five_minute_huddle_talking_points, customize_script_for_front_end_cashiers, build_deli_bakery_prep_safety_brief, quiz_associate_on_lot_code_location, record_huddle_attendance_badge_scans, provide_customer_de_escalation_phrases, highlight_gloves_ppe_handling_rules, update_breakroom_digital_signage_feed, track_unbriefed_scheduled_associates, export_training_compliance_log
  tests/unit/test_comms_associate_briefings.py  (behaviour of every public name)
  tests/unit/test_comms_associate_briefings_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_comms_associate_briefings_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/comms/customer_notifications.py: LoyaltyRecallOutreach, AutomatedCustomerAlert, query_loyalty_households_by_upc_window, filter_online_delivery_order_histories, send_personalized_email_sms_recall_alert, trigger_automated_robocall_for_class_i, provide_self_service_lot_checker_url, track_email_bounce_and_open_metrics, log_opt_out_safety_override_justification, generate_app_push_notification_payload, handle_inbound_customer_reply_routing, generate_outreach_effectiveness_summary
  tests/unit/test_comms_customer_notifications.py  (behaviour of every public name)
  tests/unit/test_comms_customer_notifications_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_comms_customer_notifications_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/comms/vendor_notices.py: SupplierRecallDirective, VendorComplianceDemand, issue_formal_notice_of_quarantine, request_immediate_coa_and_root_cause, demand_lot_distribution_manifest_csv, notify_vendor_of_pos_lock_activation, transmit_estimated_chargeback_schedule, require_indemnification_hold_harmless, escalate_unresponsive_vendor_contacts, track_vendor_portal_document_uploads, schedule_joint_crisis_bridge_call, log_vendor_disposition_instructions
  tests/unit/test_comms_vendor_notices.py  (behaviour of every public name)
  tests/unit/test_comms_vendor_notices_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_comms_vendor_notices_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/comms/regulator_reports.py: RegulatoryStatusFiling, InspectorVisitPacket, compile_fda_district_recall_status_report, format_state_dept_of_ag_store_list, prepare_store_manager_inspector_binder, log_regulatory_in_store_sample_receipts, track_fda_form_482_483_uploads, verify_zero_stock_attestation_accuracy, redact_pii_from_submission_packages, validate_report_against_agency_schema, manage_regulatory_inquiry_response_sla, archive_final_recall_closure_letter
  tests/unit/test_comms_regulator_reports.py  (behaviour of every public name)
  tests/unit/test_comms_regulator_reports_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_comms_regulator_reports_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/comms/shelf_signage_gen.py: RecallShelfTalker, PublicNoticePlacard, render_fda_compliant_shelf_placard_pdf, check_state_mandated_signage_font_size, generate_qr_code_to_fda_press_release, map_placard_count_to_aisle_facings, schedule_fourteen_day_sign_takedown, print_bilingual_consumer_warning_cards, verify_sign_placement_via_photo_upload, flag_missing_checklane_recall_mat, format_service_counter_allergen_notice, audit_expired_placard_removal
  tests/unit/test_comms_shelf_signage_gen.py  (behaviour of every public name)
  tests/unit/test_comms_shelf_signage_gen_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_comms_shelf_signage_gen_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/comms/call_center_scripts.py: ContactCenterKnowledgeBase, EscalationTriageTree, publish_agent_recall_faq_article, build_symptom_intake_decision_tree, route_adverse_event_to_nurse_line, provide_instant_e_gift_card_issuance, validate_caller_reported_lot_string, log_media_press_inquiry_diversion, update_ivr_phone_tree_announcement, track_call_volume_spike_by_recall, sync_crm_case_tags_with_recall_id, generate_daily_sentiment_digest
  tests/unit/test_comms_call_center_scripts.py  (behaviour of every public name)
  tests/unit/test_comms_call_center_scripts_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_comms_call_center_scripts_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/comms/media_holding_statements.py: PrCrisisStatement, SocialMediaMonitor, draft_reactive_media_holding_statement, monitor_local_news_social_mentions, flag_viral_tiktok_product_complaints, coordinate_trade_association_alignment, approve_corporate_website_recall_page, track_journalist_inquiry_deadlines, align_statement_with_fda_release_time, brief_executive_spokesperson_q_and_a, verify_store_no_comment_policy_reminder, archive_public_relations_timeline
  tests/unit/test_comms_media_holding_statements.py  (behaviour of every public name)
  tests/unit/test_comms_media_holding_statements_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_comms_media_holding_statements_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/comms/pharmacy_alerts.py: PharmacyPatientOutreach, NDCQuarantineNotice, match_recalled_ndc_to_dispensing_log, generate_patient_prescription_recall_letter, alert_prescribing_physician_via_efax, quarantine_will_call_waiting_bin_bags, flag_automated_pill_counter_cassettes, check_compounding_bulk_ingredient_lots, log_pharmacist_patient_counseling_calls, coordinate_medwatch_adverse_event_filing, process_central_fill_intercept_requests, audit_controlled_substance_recall_dea
  tests/unit/test_comms_pharmacy_alerts.py  (behaviour of every public name)
  tests/unit/test_comms_pharmacy_alerts_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_comms_pharmacy_alerts_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/comms/foodservice_advisories.py: CommissaryChefAlert, MenuRemovalNotice, halt_in_store_restaurant_recipe_prep, pull_recalled_ingredient_from_salad_bar, update_digital_menu_board_allergens, notify_corporate_catering_event_clients, quarantine_hot_bar_steam_table_pans, revise_printed_grab_and_go_ingredients, alert_sushi_kiosk_franchise_operators, log_discarded_prepared_batch_weights, verify_kitchen_walk_in_cooler_sweep, authorize_safe_ingredient_substitution
  tests/unit/test_comms_foodservice_advisories.py  (behaviour of every public name)
  tests/unit/test_comms_foodservice_advisories_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_comms_foodservice_advisories_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/comms/union_safety_notices.py: LaborUnionSafetyBrief, HazmatHandlingNotice, notify_ufcw_steward_of_hazmat_recall, specify_caustic_leaking_product_ppe, communicate_mandatory_overtime_rules, log_associate_chemical_exposure_incident, provide_ergonomic_heavy_lifting_guide, verify_spill_kit_availability_in_aisles, address_immunocompromised_staff_opt_out, document_joint_safety_committee_review, distribute_sds_safety_data_sheets, archive_union_grievance_communications
  tests/unit/test_comms_union_safety_notices.py  (behaviour of every public name)
  tests/unit/test_comms_union_safety_notices_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_comms_union_safety_notices_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/comms/translation_localization.py: MultilingualNoticeEngine, CulturalAdaptationCheck, translate_recall_warning_to_spanish_chinese, verify_medical_symptom_term_accuracy, adapt_ethnic_product_alias_descriptions, validate_right_to_left_arabic_layout, check_reading_grade_level_simplicity, review_machine_translation_with_glossary, generate_audio_tts_for_visually_impaired, map_store_demographic_language_needs, sync_translations_across_pos_and_signs, audit_translation_turnaround_sla
  tests/unit/test_comms_translation_localization.py  (behaviour of every public name)
  tests/unit/test_comms_translation_localization_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_comms_translation_localization_props.py  (property-style checks over generated inputs, fixed seed)

## recallstorm/vendor/  (recallstorm/vendor/__init__.py re-exports the public names)
- recallstorm/vendor/chargeback_engine.py: RecallChargebackInvoice, FeeScheduleCalculator, calculate_per_store_execution_labor_fee, apply_per_unit_handling_and_hauling_rate, bill_pos_programming_and_signage_flat_fee, compute_lost_gross_margin_recovery, attach_store_scan_audit_backup_csv, deduct_chargeback_from_ap_remittance, handle_vendor_chargeback_dispute_claim, enforce_master_vendor_agreement_caps, escalate_unpaid_private_label_claims, export_erp_accounts_receivable_debit
  tests/unit/test_vendor_chargeback_engine.py  (behaviour of every public name)
  tests/unit/test_vendor_chargeback_engine_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_vendor_chargeback_engine_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/vendor/reformulation_tracker.py: ReformulationMilestone, AdditivePhaseOutPlan, track_bromate_red3_replacement_timeline, ingest_updated_supplier_spec_sheets, compare_old_vs_new_ingredient_decks, verify_new_upc_gtin_assignment_rules, manage_packaging_artwork_proof_signoff, monitor_clean_lot_first_ship_date, prevent_old_formulation_po_reordering, validate_transition_lot_cutover_code, flag_delayed_vendor_r_and_d_milestones, report_category_compliance_readiness_pct
  tests/unit/test_vendor_reformulation_tracker.py  (behaviour of every public name)
  tests/unit/test_vendor_reformulation_tracker_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_vendor_reformulation_tracker_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/vendor/certificates_of_analysis.py: CoaRepository, LabResultValidator, ingest_pdf_edifact_coa_documents, verify_iso_17025_lab_accreditation_scope, match_coa_batch_id_to_asn_lot, check_heavy_metal_pfas_pass_fail_limits, flag_expired_annual_testing_certificates, detect_altered_fraudulent_coa_pdfs, block_receiving_on_missing_coa_gate, alert_qa_to_marginal_spec_results, link_coa_to_gs1_epcis_lot_master, archive_regulatory_audit_coa_bundle
  tests/unit/test_vendor_certificates_of_analysis.py  (behaviour of every public name)
  tests/unit/test_vendor_certificates_of_analysis_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_vendor_certificates_of_analysis_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/vendor/dsd_coordination.py: DsdRecallExecution, RouteDriverSignOff, notify_dsd_bottler_bakery_dispatcher, schedule_driver_in_store_credit_pickup, verify_backdoor_dex_return_invoice_scan, audit_driver_pulled_case_counts_at_exit, prevent_unauthorized_dsd_shelf_restock, lock_dsd_item_in_receiving_handheld, reconcile_driver_handwritten_credit_slips, track_unserviced_rural_store_dsd_holds, escalate_missed_dsd_pickup_sla_window, close_dsd_route_reconciliation_loop
  tests/unit/test_vendor_dsd_coordination.py  (behaviour of every public name)
  tests/unit/test_vendor_dsd_coordination_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_vendor_dsd_coordination_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/vendor/credit_reconciliation.py: VendorCreditLedger, DeductionMatcher, match_vendor_credit_memo_to_rma_id, reconcile_unit_cost_discrepancies_on_credit, track_swell_allowance_vs_recall_eligibility, clear_aged_open_deduction_balances, audit_3pl_reclamation_settlement_files, calculate_cash_discount_reversal_impact, resolve_short_paid_invoice_disputes, generate_vendor_statement_of_account_pdf, escalate_insolvent_vendor_write_offs, close_financial_recall_event_ledger
  tests/unit/test_vendor_credit_reconciliation.py  (behaviour of every public name)
  tests/unit/test_vendor_credit_reconciliation_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_vendor_credit_reconciliation_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/vendor/indemnification_claims.py: LegalIndemnityClaim, InsuranceTenderTracker, verify_vendor_product_liability_coi_limits, check_additional_insured_endorsement_status, tender_consumer_injury_claim_to_vendor, track_defense_cost_reimbursement_ledger, link_master_supply_agreement_indemnity_clause, flag_lapsed_supplier_insurance_policies, calculate_total_incident_tort_exposure, coordinate_outside_counsel_litigation_hold, manage_subrogation_recovery_workflows, archive_executed_settlement_releases
  tests/unit/test_vendor_indemnification_claims.py  (behaviour of every public name)
  tests/unit/test_vendor_indemnification_claims_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_vendor_indemnification_claims_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/vendor/private_label_qa.py: OwnBrandRecallManager, CoPackerAuditTracker, map_private_label_sku_to_copacker_plant, access_tracegains_supplier_spec_portal, trigger_unannounced_gfSI_sqf_audit, quarantine_shared_line_national_brand_runs, review_copacker_environmental_swab_trends, enforce_own_brand_zero_tolerance_policy, coordinate_private_label_press_release, manage_packaging_film_write_off_liability, track_capa_corrective_action_closure, score_copacker_food_safety_culture
  tests/unit/test_vendor_private_label_qa.py  (behaviour of every public name)
  tests/unit/test_vendor_private_label_qa_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_vendor_private_label_qa_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/vendor/supplier_scorecards.py: VendorComplianceScorecard, RecallPenaltyWeighting, calculate_recall_frequency_severity_index, penalize_late_recall_notification_lag, score_lot_traceability_data_completeness, evaluate_chargeback_dispute_friction_rate, rank_category_suppliers_by_safety_risk, trigger_probationary_business_review, feed_scorecard_to_merchandising_line_review, benchmark_dsd_vs_warehouse_compliance, track_reformulation_deadline_adherence, export_executive_vendor_risk_matrix
  tests/unit/test_vendor_supplier_scorecards.py  (behaviour of every public name)
  tests/unit/test_vendor_supplier_scorecards_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_vendor_supplier_scorecards_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/vendor/onboarding_gates.py: NewItemComplianceGate, IngredientScreenBlock, screen_new_item_setup_for_banned_additives, require_state_specific_regulatory_attestation, validate_gs1_gtin_lot_coding_capability, verify_24_7_emergency_recall_contact_info, reject_unsubstantiated_free_from_claims, check_fda_import_alert_red_list_status, enforce_mandatory_epcis_asn_readiness, assign_initial_food_safety_risk_tier, audit_broker_submitted_onboarding_data, lock_unapproved_sku_from_po_creation
  tests/unit/test_vendor_onboarding_gates.py  (behaviour of every public name)
  tests/unit/test_vendor_onboarding_gates_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_vendor_onboarding_gates_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/vendor/import_broker_holds.py: ImportHoldCoordinator, CustomsEntryQuarantine, match_fda_predict_import_hold_notice, trace_ocean_container_bol_to_drayage, verify_customs_bond_redelivery_demand, coordinate_fda_private_lab_sampling_packet, hold_deconsolidated_transload_pallets, track_notice_of_fda_action_detention, calculate_port_demurrage_detention_fees, manage_export_or_destruction_under_customs, audit_foreign_supplier_fsvp_dossiers, release_may_proceed_entries_to_dc
  tests/unit/test_vendor_import_broker_holds.py  (behaviour of every public name)
  tests/unit/test_vendor_import_broker_holds_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_vendor_import_broker_holds_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/vendor/co_packer_traceability.py: MultiCoPackerResolver, PlantCodeRouter, decode_julian_plant_suffix_on_packaging, isolate_affected_co_packer_facility, clear_unaffected_sister_plant_inventory, map_regional_co_packer_dc_assignments, verify_co_packer_sub_ingredient_suppliers, audit_unauthorized_subcontracting_events, reconcile_packaging_roll_stock_transfers, update_gtin_to_plant_routing_tables, generate_plant_specific_shelf_pull_rules, validate_dual_sourced_sku_segregation
  tests/unit/test_vendor_co_packer_traceability.py  (behaviour of every public name)
  tests/unit/test_vendor_co_packer_traceability_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_vendor_co_packer_traceability_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/vendor/dispute_resolution.py: ChargebackDisputeQueue, EvidenceArbitrator, ingest_vendor_dispute_portal_submission, attach_timestamped_store_pull_scan_logs, verify_photo_proof_of_affected_lot_code, recalculate_disputed_unit_cost_basis, evaluate_force_majeure_contract_claims, route_high_dollar_dispute_to_merch_vp, apply_partial_settlement_credit_adjustment, track_dispute_resolution_cycle_time_days, lock_settled_claims_from_re_submission, generate_arbitration_evidence_dossier
  tests/unit/test_vendor_dispute_resolution.py  (behaviour of every public name)
  tests/unit/test_vendor_dispute_resolution_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_vendor_dispute_resolution_props.py  (property-style checks over generated inputs, fixed seed)

## recallstorm/dc_ops/  (recallstorm/dc_ops/__init__.py re-exports the public names)
- recallstorm/dc_ops/receiving_holds.py: InboundReceivingBlock, DockDoorQuarantine, flag_recalled_po_line_on_receiving_rf, reject_affected_lot_at_inbound_scan, print_immediate_red_quarantine_pallet_lpn, segregate_mixed_lot_vendor_ti_hi_pallets, block_auto_putaway_to_reserve_racking, log_driver_detention_for_lot_sorting, capture_inbound_bol_and_lumper_notes, alert_dc_qa_inspector_to_receiving_dock, generate_osd_over_short_damage_refusal, release_clean_lots_on_split_delivery
  tests/unit/test_dc_ops_receiving_holds.py  (behaviour of every public name)
  tests/unit/test_dc_ops_receiving_holds_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_dc_ops_receiving_holds_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/dc_ops/pick_face_blocks.py: ActivePickSlotHold, ReplenishmentStopper, freeze_primary_forward_pick_location, cancel_pending_letdown_replenishment_tasks, redirect_voice_pick_operator_around_slot, trigger_immediate_slot_purge_to_cage, lock_case_flow_rack_lane_gravity_feed, verify_empty_pick_slot_via_barcode_scan, re_slot_substitute_sku_into_pick_face, block_automated_crane_asrs_retrieval, audit_partial_case_pick_remnants, restore_pick_face_after_sanitation
  tests/unit/test_dc_ops_pick_face_blocks.py  (behaviour of every public name)
  tests/unit/test_dc_ops_pick_face_blocks_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_dc_ops_pick_face_blocks_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/dc_ops/outbound_holds.py: OutboundWaveInterceptor, ShippingDockPurge, scan_active_pick_waves_for_recalled_lpn, intercept_pallet_at_stretch_wrap_station, pull_affected_cases_from_store_build_pallet, halt_loading_of_contaminated_trailer_door, reprint_adjusted_store_shipping_manifest, scan_staged_shipping_lanes_with_rfid, prevent_bol_print_until_hold_cleared, log_late_truck_departure_delay_reason, re_cube_shorted_store_delivery_trailer, confirm_clean_outbound_seal_application
  tests/unit/test_dc_ops_outbound_holds.py  (behaviour of every public name)
  tests/unit/test_dc_ops_outbound_holds_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_dc_ops_outbound_holds_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/dc_ops/yard_management.py: YardTrailerQuarantine, ReeferHoldMonitor, locate_affected_drop_trailer_in_yard_slot, apply_digital_glad_hand_lock_in_yms, monitor_quarantined_reefer_fuel_and_temp, prioritize_hot_recall_return_trailer_docking, track_3pl_destruction_shuttle_trailers, prevent_yard_jockey_move_to_outbound_door, log_security_gate_seal_verification_on_exit, manage_detention_clock_on_held_equipment, assign_isolated_hazmat_parking_stall, audit_daily_yard_check_inventory_sync
  tests/unit/test_dc_ops_yard_management.py  (behaviour of every public name)
  tests/unit/test_dc_ops_yard_management_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_dc_ops_yard_management_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/dc_ops/carrier_tendering.py: ReverseLoadTendering, HazmatCarrierSelector, build_consolidated_recall_return_load, tender_dedicated_truckload_via_edi_204, verify_carrier_hazmat_rcra_endorsements, track_edi_990_load_acceptance_sla, negotiate_spot_market_backhaul_rates, enforce_sealed_exclusive_use_trailer_rule, monitor_in_transit_gps_breadcrumb_ping, handle_carrier_turndown_waterfall_logic, validate_proof_of_delivery_at_reclamation, audit_reverse_freight_accessorial_bills
  tests/unit/test_dc_ops_carrier_tendering.py  (behaviour of every public name)
  tests/unit/test_dc_ops_carrier_tendering_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_dc_ops_carrier_tendering_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/dc_ops/reclamation_center.py: ReclamationSortEngine, CrushedBaleTracker, configure_reclamation_scanner_sort_chutes, route_scanned_returns_to_vendor_gaylords, separate_hazmat_aerosols_and_lithium_ion, weigh_and_tag_completed_vendor_pallets, record_zero_value_trash_compactor_throws, verify_item_eligibility_for_food_bank_donate, prevent_recalled_item_from_salvage_auction, audit_store_return_tote_manifest_accuracy, calculate_reclamation_processing_cost_per_unit, generate_vendor_pickup_ready_notification
  tests/unit/test_dc_ops_reclamation_center.py  (behaviour of every public name)
  tests/unit/test_dc_ops_reclamation_center_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_dc_ops_reclamation_center_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/dc_ops/pallet_license_plates.py: LpnGenealogyTracker, MixedPalletSplitter, trace_parent_receiving_lpn_to_child_picks, identify_rainbow_pallets_with_recalled_layers, generate_split_pallet_rework_work_order, invalidate_consumed_or_destroyed_lpns, block_lpn_consolidation_across_hold_codes, verify_gs1_128_sscc_check_digit_integrity, track_lpn_location_move_history_in_wms, flag_ghost_lpns_in_lost_and_found_zone, print_replacement_hold_lpn_thermal_labels, audit_quarantine_zone_lpn_physical_count
  tests/unit/test_dc_ops_pallet_license_plates.py  (behaviour of every public name)
  tests/unit/test_dc_ops_pallet_license_plates_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_dc_ops_pallet_license_plates_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/dc_ops/slotting_adjustments.py: QuarantineSlottingPlanner, SurgeCapacityAllocator, calculate_cubic_feet_needed_for_recall_hold, convert_bulk_floor_stack_to_quarantine_zone, re_slot_seasonal_aisle_for_return_staging, isolate_allergen_or_chemical_leaker_racks, optimize_forklift_travel_to_compactor_bay, reserve_dock_doors_for_reverse_consolidation, balance_freezer_vs_ambient_hold_capacity, update_wms_zone_velocity_restrictions, track_temporary_rack_reconfiguration_cost, restore_baseline_slotting_post_disposition
  tests/unit/test_dc_ops_slotting_adjustments.py  (behaviour of every public name)
  tests/unit/test_dc_ops_slotting_adjustments_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_dc_ops_slotting_adjustments_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/dc_ops/cold_storage_holds.py: FreezerBlastHold, ColdRoomSegregation, verify_minus_ten_f_freezer_quarantine_zone, monitor_ammonia_leak_exposure_in_cold_room, track_ice_cream_shrink_from_dock_staging, allocate_insulated_pallet_covers_for_returns, prevent_blast_cell_cross_airflow_risk, schedule_defrost_window_for_held_coils, log_cold_suit_labor_rotation_limits, validate_frozen_destruction_rendering_chain, audit_multi_temp_trailer_bulkhead_position, release_tempered_product_with_qa_signoff
  tests/unit/test_dc_ops_cold_storage_holds.py  (behaviour of every public name)
  tests/unit/test_dc_ops_cold_storage_holds_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_dc_ops_cold_storage_holds_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/dc_ops/automation_inhibits.py: AsrsCraneLockout, SymboticBotQuarantine, lock_autostore_or_symbotic_storage_bins, inhibit_depalletizer_robot_layer_pick, divert_recalled_tote_on_high_speed_sorter, purge_unit_sorter_chute_accumulations, prevent_agv_forklift_autonomous_putaway, isolate_faulted_broken_case_in_shuttle_aisle, sync_wcs_warehouse_control_with_wms_hold, schedule_maintenance_retrieval_of_locked_tote, audit_automated_storage_quarantine_inventory, restore_mechatronics_cell_to_production
  tests/unit/test_dc_ops_automation_inhibits.py  (behaviour of every public name)
  tests/unit/test_dc_ops_automation_inhibits_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_dc_ops_automation_inhibits_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/dc_ops/hazmat_segregation.py: HazmatQuarantineProtocol, RcraWasteClassifier, classify_recalled_sku_by_dot_hazard_class, segregate_flammable_aerosols_in_wire_cage, check_oxidizer_vs_corrosive_incompatibility, assign_un_number_and_packing_group_labels, monitor_lithium_battery_thermal_runaway_risk, verify_spill_containment_berm_capacity, generate_epa_hazardous_waste_manifest, coordinate_clean_harbors_lab_pack_pickup, track_acute_hazardous_waste_p_list_limits, audit_dc_tier_ii_epcra_reporting_thresholds
  tests/unit/test_dc_ops_hazmat_segregation.py  (behaviour of every public name)
  tests/unit/test_dc_ops_hazmat_segregation_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_dc_ops_hazmat_segregation_props.py  (property-style checks over generated inputs, fixed seed)

## recallstorm/analytics/  (recallstorm/analytics/__init__.py re-exports the public names)
- recallstorm/analytics/drill_kpis.py: DrillScorecardEngine, SlaPerformanceTracker, calculate_time_to_first_store_scan_mins, measure_four_hour_completion_rate_pct, compute_lot_capture_accuracy_precision, score_pos_block_deployment_latency_secs, benchmark_division_vs_company_avg_speed, track_false_positive_unaffected_pull_rate, evaluate_backroom_vs_salesfloor_miss_rate, calculate_labor_hours_variance_to_plan, generate_executive_drill_grade_letter, export_board_level_compliance_kpi_deck
  tests/unit/test_analytics_drill_kpis.py  (behaviour of every public name)
  tests/unit/test_analytics_drill_kpis_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_analytics_drill_kpis_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/analytics/risk_scoring.py: StoreRiskProfile, CategoryExposureModel, score_store_by_historical_audit_failures, weight_category_by_fda_recall_frequency, calculate_demographic_vulnerable_pop_index, assess_high_shrink_store_phantom_stock_risk, rank_suppliers_by_import_detention_history, model_regulatory_fine_multiplier_by_state, predict_understaffed_shift_execution_lag, combine_factors_into_composite_risk_tier, prioritize_high_risk_stores_for_floaters, update_risk_weights_from_post_mortem
  tests/unit/test_analytics_risk_scoring.py  (behaviour of every public name)
  tests/unit/test_analytics_risk_scoring_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_analytics_risk_scoring_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/analytics/forecasting_exposure.py: RecallExposureForecaster, DepletionCurvePredictor, forecast_remaining_shelf_units_at_hour_t, model_time_of_day_pos_basket_velocity, estimate_customer_pantry_consumption_risk, predict_quarantine_cage_overflow_by_store, project_total_financial_write_off_range, simulate_delayed_notice_exposure_penalty, calculate_substitute_stockout_runout_date, bound_confidence_interval_on_untracked_lots, adjust_forecast_for_holiday_promotional_lift, feed_exposure_estimate_to_reserve_accrual
  tests/unit/test_analytics_forecasting_exposure.py  (behaviour of every public name)
  tests/unit/test_analytics_forecasting_exposure_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_analytics_forecasting_exposure_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/analytics/anomaly_detection.py: PullScanAnomalyDetector, FraudAndErrorFlag, detect_impossible_speed_pencil_whipping, flag_zero_unit_found_in_high_on_hand_store, identify_unusual_post_lock_pos_override_scans, spot_outlier_destruction_weight_variances, detect_coordinated_multi_store_scan_gaps, alert_on_after_hours_quarantine_bin_access, compare_sister_store_pull_ratios_by_cluster, isolate_handheld_scanner_clock_drift_errors, score_store_submission_credibility_index, route_flagged_anomalies_to_audit_queue
  tests/unit/test_analytics_anomaly_detection.py  (behaviour of every public name)
  tests/unit/test_analytics_anomaly_detection_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_analytics_anomaly_detection_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/analytics/trend_reports.py: HistoricalRecallTrends, LongitudinalComplianceView, plot_monthly_recall_volume_by_fda_class, analyze_additive_ban_readiness_burn_down, track_repeat_offender_vendor_trajectories, compare_q_over_q_time_to_100_pct_closure, identify_chronic_bottleneck_store_formats, correlate_staff_turnover_with_drill_scores, chart_allergen_vs_micro_recall_proportions, measure_year_over_year_shrink_recovery_pct, generate_annual_food_safety_review_charts, export_longitudinal_dataset_to_parquet
  tests/unit/test_analytics_trend_reports.py  (behaviour of every public name)
  tests/unit/test_analytics_trend_reports_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_analytics_trend_reports_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/analytics/root_cause_mining.py: FailureModeClassifier, PostMortemTextMiner, cluster_store_exception_reason_codes, extract_themes_from_manager_delay_notes, attribute_misses_to_planogram_unmapped_locs, quantify_dsd_endcap_blind_spot_frequency, measure_impact_of_unreadable_lot_stamps, correlate_missed_pulls_with_night_crew_gaps, identify_pos_sync_failures_by_isp_carrier, rank_top_ten_systemic_execution_barriers, generate_capa_preventive_action_tickets, validate_fix_efficacy_in_subsequent_drills
  tests/unit/test_analytics_root_cause_mining.py  (behaviour of every public name)
  tests/unit/test_analytics_root_cause_mining_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_analytics_root_cause_mining_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/analytics/labor_efficiency.py: PullProductivityAnalyzer, MotionWasteEvaluator, calculate_units_pulled_per_labor_minute, compare_actual_walk_path_to_optimal_tour, measure_lot_inspection_dwell_time_by_pkg, evaluate_batch_multi_recall_walk_synergy, quantify_backroom_search_time_penalty, benchmark_floater_vs_store_associate_speed, identify_ergonomic_fatigue_drop_off_curves, optimize_two_person_team_cage_transport, calibrate_task_time_standards_by_category, export_engineered_labor_standard_updates
  tests/unit/test_analytics_labor_efficiency.py  (behaviour of every public name)
  tests/unit/test_analytics_labor_efficiency_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_analytics_labor_efficiency_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/analytics/financial_impact.py: RecallCostAggregator, TotalCostOfRecallModel, sum_direct_product_write_off_at_cost, calculate_store_and_dc_execution_labor_cost, quantify_lost_margin_from_out_of_stocks, add_reverse_freight_and_destruction_fees, deduct_recovered_vendor_chargebacks_and_rma, incorporate_regulatory_fines_and_legal_fees, estimate_brand_equity_halo_basket_erosion, compute_net_unrecovered_recall_p_and_l_hit, attribute_cost_by_merchandising_buying_desk, generate_cfo_recall_financial_bridge
  tests/unit/test_analytics_financial_impact.py  (behaviour of every public name)
  tests/unit/test_analytics_financial_impact_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_analytics_financial_impact_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/analytics/shelf_void_impact.py: OutOfStockDurationTracker, SubstituteCaptureRate, measure_days_of_empty_facing_post_pull, calculate_substitute_sku_sales_halo_lift, quantify_category_switching_walk_away_rate, track_time_to_replenish_with_clean_lot, evaluate_emergency_re_planogram_compliance, identify_orphaned_shelf_tags_without_stock, correlate_void_duration_with_nps_drop, score_dc_emergency_allocation_fill_rate, recommend_safety_stock_buffer_adjustments, export_merchandising_recovery_scorecard
  tests/unit/test_analytics_shelf_void_impact.py  (behaviour of every public name)
  tests/unit/test_analytics_shelf_void_impact_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_analytics_shelf_void_impact_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/analytics/supplier_benchmarking.py: PeerSupplierComparator, CategorySafetyRanker, normalize_recalls_per_million_cases_shipped, compare_private_label_vs_national_brand_rate, benchmark_traceability_epcis_adoption_rate, score_vendor_responsiveness_during_drills, analyze_coa_rejection_rate_by_country_origin, cluster_vendors_by_shared_co_packer_risk, identify_single_source_vulnerable_categories, calculate_cost_of_poor_quality_by_supplier, generate_quarterly_qbr_safety_slide_data, rank_vendors_for_preferred_partner_status
  tests/unit/test_analytics_supplier_benchmarking.py  (behaviour of every public name)
  tests/unit/test_analytics_supplier_benchmarking_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_analytics_supplier_benchmarking_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/analytics/simulation_calibration.py: DigitalTwinCalibrator, SimToRealGapAnalyzer, compare_simulated_walk_times_to_rf_scans, fit_lot_inspection_time_distributions, calibrate_customer_basket_pick_interference, tune_backroom_clutter_delay_multipliers, validate_truck_loading_cube_utilization_sim, measure_disruption_model_prediction_error, update_monte_carlo_prior_probabilities, backtest_simulator_against_historical_recalls, detect_store_layout_drift_from_cad_files, publish_calibrated_sim_parameter_bundle
  tests/unit/test_analytics_simulation_calibration.py  (behaviour of every public name)
  tests/unit/test_analytics_simulation_calibration_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_analytics_simulation_calibration_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/analytics/executive_briefings.py: CSuiteDigestGenerator, CrisisWarRoomFeed, synthesize_hourly_war_room_situation_report, highlight_red_flag_non_compliant_districts, project_estimated_time_to_full_containment, summarize_media_and_regulator_touchpoints, track_class_i_hospitalization_escalations, compare_current_event_to_historical_baseline, format_mobile_friendly_ceo_flash_email, generate_general_counsel_privilege_summary, update_live_geojson_store_completion_map, archive_war_room_decision_log_snapshots
  tests/unit/test_analytics_executive_briefings.py  (behaviour of every public name)
  tests/unit/test_analytics_executive_briefings_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_analytics_executive_briefings_props.py  (property-style checks over generated inputs, fixed seed)

## recallstorm/governance/  (recallstorm/governance/__init__.py re-exports the public names)
- recallstorm/governance/audit_evidence_packs.py: AuditBinderCompiler, TamperEvidentPackager, assemble_store_by_store_execution_dossier, bundle_timestamped_pos_lock_confirmations, attach_geotagged_quarantine_cage_photos, include_signed_destruction_witness_certs, compute_sha256_merkle_root_for_evidence, generate_pdf_a_archival_compliance_binder, cross_reference_fda_effectiveness_checks, verify_completeness_of_mandatory_artifacts, watermark_confidential_regulatory_exhibits, export_encrypted_regulator_handoff_zip
  tests/unit/test_governance_audit_evidence_packs.py  (behaviour of every public name)
  tests/unit/test_governance_audit_evidence_packs_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_governance_audit_evidence_packs_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/governance/approvals_workflow.py: MultiStageApprovalGate, CrisisSignOffRouter, route_class_i_pos_lock_for_vp_approval, enforce_dual_control_on_chainwide_pulls, capture_cryptographic_digital_signatures, escalate_unapproved_holds_past_15_mins, log_verbal_war_room_authorization_overrides, verify_qa_director_clearance_for_release, manage_delegation_of_authority_on_weekends, block_premature_quarantine_bin_unlocking, track_approval_turnaround_bottlenecks, generate_sox_compliant_approval_trail
  tests/unit/test_governance_approvals_workflow.py  (behaviour of every public name)
  tests/unit/test_governance_approvals_workflow_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_governance_approvals_workflow_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/governance/store_sign_offs.py: StoreManagerAttestation, SwornAffidavitCollector, require_store_manager_pin_and_signature, validate_100_percent_aisle_task_completion, block_sign_off_when_lot_variance_exceeds_cap, capture_closing_manager_shift_handover_ack, generate_legally_binding_affidavit_text, flag_proxy_sign_offs_by_unauthorized_staff, record_gps_and_device_mac_at_attestation, trigger_district_manager_escalation_on_miss, archive_immutable_store_completion_receipts, export_unattested_store_exception_list
  tests/unit/test_governance_store_sign_offs.py  (behaviour of every public name)
  tests/unit/test_governance_store_sign_offs_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_governance_store_sign_offs_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/governance/retention_policies.py: LegalHoldManager, RecordRetentionEnforcer, apply_seven_year_fda_fsma_retention_rule, place_litigation_hold_on_injury_linked_lots, prevent_auto_purge_of_recall_epcis_events, archive_cold_storage_jsonl_to_glacier_worm, manage_gdpr_ccpa_pii_redaction_schedules, verify_immutable_s3_object_lock_status, track_retention_expiration_disposition_dates, audit_unauthorized_deletion_attempts, link_related_vendor_correspondence_to_hold, generate_records_management_compliance_cert
  tests/unit/test_governance_retention_policies.py  (behaviour of every public name)
  tests/unit/test_governance_retention_policies_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_governance_retention_policies_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/governance/access_logs.py: PrivilegedAccessLogger, RbacPolicyEnforcer, log_every_view_of_unredacted_recall_drafts, enforce_role_based_access_to_pos_kill_switch, detect_anomalous_bulk_export_of_vendor_lists, require_mfa_step_up_for_hold_release_action, audit_third_party_auditor_portal_sessions, track_impersonation_support_session_actions, revoke_terminated_associate_drill_credentials, generate_siem_compatible_cef_security_logs, alert_infosec_on_permission_escalation_try, archive_quarterly_access_entitlement_review
  tests/unit/test_governance_access_logs.py  (behaviour of every public name)
  tests/unit/test_governance_access_logs_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_governance_access_logs_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/governance/policy_versioning.py: StandardOperatingProcedureGit, PolicyDiffTracker, version_control_recall_playbook_markdown, require_legal_review_on_jurisdiction_rules, track_effective_dates_of_state_ban_modules, diff_rule_engine_thresholds_between_drills, bind_drill_execution_to_immutable_policy_sha, manage_annual_sop_recertification_cycles, publish_redlined_policy_updates_to_field, roll_back_erroneous_rule_configuration_push, audit_policy_exception_waiver_expirations, generate_regulatory_change_management_log
  tests/unit/test_governance_policy_versioning.py  (behaviour of every public name)
  tests/unit/test_governance_policy_versioning_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_governance_policy_versioning_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/governance/regulatory_calendar.py: ComplianceDeadlineCalendar, StatutoryPhaseInTracker, track_ab418_ny_il_statutory_effective_dates, schedule_t_minus_90_day_readiness_drills, alert_merchandising_to_sell_through_cutoffs, monitor_state_legislature_amendment_feeds, sync_regulatory_milestones_to_corp_calendar, calculate_working_days_to_mandatory_ban, trigger_pre_enforcement_store_sweep_tasks, track_fda_fsma_204_traceability_deadlines, assign_executive_owners_to_upcoming_laws, generate_twelve_month_regulatory_horizon_map
  tests/unit/test_governance_regulatory_calendar.py  (behaviour of every public name)
  tests/unit/test_governance_regulatory_calendar_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_governance_regulatory_calendar_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/governance/whistleblower_intake.py: EthicsHotlineIntake, AnonymousSafetyReport, ingest_anonymous_backroom_bypass_tips, protect_reporter_identity_via_zero_knowledge, route_deliberate_relabeling_allegations_to_lp, triage_pest_or_temperature_cover_up_claims, enforce_non_retaliation_monitoring_flags, link_tip_to_specific_store_and_lot_audit, track_internal_investigation_sla_milestones, require_independent_qa_verification_visit, document_substantiated_finding_remediation, generate_audit_committee_ethics_summary
  tests/unit/test_governance_whistleblower_intake.py  (behaviour of every public name)
  tests/unit/test_governance_whistleblower_intake_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_governance_whistleblower_intake_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/governance/third_party_audits.py: ExternalAuditorPortal, StoreWalkVerification, schedule_unannounced_steritech_ecolab_checks, grant_time_boxed_auditor_read_only_access, ingest_third_party_mystery_shopper_scans, verify_pulled_sku_absence_on_store_shelves, reconcile_external_audit_findings_with_self_report, trigger_immediate_re_pull_on_auditor_find, score_banner_integrity_gap_percentage, track_corrective_coaching_for_failed_stores, benchmark_internal_vs_external_pass_rates, archive_independent_verification_certificates
  tests/unit/test_governance_third_party_audits.py  (behaviour of every public name)
  tests/unit/test_governance_third_party_audits_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_governance_third_party_audits_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/governance/training_certification.py: ComplianceLmsTracker, RoleCertificationGate, assign_mandatory_recall_drill_microlearning, verify_annual_fsma_204_handler_certification, block_untrained_associate_from_quarantine_tasks, track_forklift_hazmat_spill_training_expiry, score_simulated_drill_assessment_quizzes, trigger_remedial_training_after_failed_pull, sync_lms_completion_with_labor_skill_matrix, audit_new_hire_onboarding_safety_modules, generate_osha_fda_training_inspection_log, notify_store_manager_of_lapsed_certifications
  tests/unit/test_governance_training_certification.py  (behaviour of every public name)
  tests/unit/test_governance_training_certification_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_governance_training_certification_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/governance/data_privacy.py: CustomerPiiVault, OutreachPrivacyGuard, encrypt_loyalty_customer_phone_and_email, enforce_purpose_limitation_on_recall_contact, verify_hipaa_compliance_for_pharmacy_recalls, scrub_credit_card_pans_from_pos_scan_logs, manage_tokenized_household_purchase_links, log_lawful_vital_interest_gdpr_basis_use, purge_temporary_call_center_contact_lists, audit_sms_vendor_subprocessor_dpa_status, handle_consumer_data_subject_access_requests, validate_k_anonymity_in_published_analytics
  tests/unit/test_governance_data_privacy.py  (behaviour of every public name)
  tests/unit/test_governance_data_privacy_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_governance_data_privacy_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/governance/board_reporting.py: RiskCommitteePackage, FiduciaryOversightBrief, compile_quarterly_enterprise_recall_summary, quantify_unmitigated_state_ban_exposures, report_material_fda_warning_letter_risks, summarize_whistleblower_and_audit_exceptions, benchmark_compliance_maturity_against_peers, track_capex_investment_in_esl_and_epcis, highlight_supply_chain_single_point_failures, document_crisis_simulation_readiness_scores, provide_directors_and_officers_liability_view, archive_signed_board_resolution_minutes
  tests/unit/test_governance_board_reporting.py  (behaviour of every public name)
  tests/unit/test_governance_board_reporting_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_governance_board_reporting_props.py  (property-style checks over generated inputs, fixed seed)

## recallstorm/route/  (recallstorm/route/__init__.py re-exports the public names)
- recallstorm/route/capacity.py: truck_capacity, remaining_cube, remaining_weight, capacity_check, overload_report, utilization_by_dc, capacity_to_record, capacity_summary, CapacityModel
  tests/unit/test_route_capacity.py  (behaviour of every public name)
  tests/unit/test_route_capacity_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_route_capacity_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/route/dispatch.py: dispatch_plan, depart_time, arrival_eta, driver_hours, dispatch_to_records, late_departures, dispatch_summary, validate_dispatch, Dispatcher
  tests/unit/test_route_dispatch.py  (behaviour of every public name)
  tests/unit/test_route_dispatch_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_route_dispatch_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/route/returns.py: returned_cases, cases_by_store, cases_by_dc, case_cube, case_weight, returns_summary, returns_to_stops, validate_returns, ReturnLoad
  tests/unit/test_route_returns.py  (behaviour of every public name)
  tests/unit/test_route_returns_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_route_returns_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/route/packing.py: pack_returns, first_fit_decreasing, pack_truck, fits_truck, truck_utilization, split_stop, manifest_to_record, packing_summary, PackingResult
  tests/unit/test_route_packing.py  (behaviour of every public name)
  tests/unit/test_route_packing_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_route_packing_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/route/stops.py: order_stops, nearest_neighbor_order, route_distance, stop_eta, stops_for_truck, merge_stops, stop_to_record, stops_summary, RoutePlanner
  tests/unit/test_route_stops.py  (behaviour of every public name)
  tests/unit/test_route_stops_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_route_stops_props.py  (property-style checks over generated inputs, fixed seed)

## recallstorm/report/  (recallstorm/report/__init__.py re-exports the public names)
- recallstorm/report/summary.py: drill_summary, store_table, sku_table, counts_by_verdict, counts_by_action, summary_to_markdown, summary_to_json, compare_runs, SummaryReport
  tests/unit/test_report_summary.py  (behaviour of every public name)
  tests/unit/test_report_summary_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_report_summary_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/report/checks.py: check_refs, check_conservation, check_capacity, check_labor, check_deadline, check_contradictions, run_all_checks, checks_to_json, CheckReport
  tests/unit/test_report_checks.py  (behaviour of every public name)
  tests/unit/test_report_checks_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_report_checks_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/report/export.py: export_csv, export_markdown, export_store_packets, export_dc_packets, export_evidence, export_manifests, export_zip, export_index, Exporter
  tests/unit/test_report_export.py  (behaviour of every public name)
  tests/unit/test_report_export_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_report_export_props.py  (property-style checks over generated inputs, fixed seed)
- recallstorm/report/dashboard.py: dashboard_data, map_points, store_status_colors, timeline_series, kpi_tiles, dashboard_to_json, dashboard_html, DashboardModel, DashboardBuilder
  tests/unit/test_report_dashboard.py  (behaviour of every public name)
  tests/unit/test_report_dashboard_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_report_dashboard_props.py  (property-style checks over generated inputs, fixed seed)

## recallstorm/cli/  (recallstorm/cli/__init__.py re-exports the public names)
- recallstorm/cli/main.py: main, build_parser, cmd_run, cmd_validate, cmd_stats, cmd_explain, cmd_replay, cmd_scenarios, exit_code_for
  tests/unit/test_cli_main.py  (behaviour of every public name)
  tests/unit/test_cli_main_edge.py  (invalid inputs, boundaries, determinism)
  tests/unit/test_cli_main_props.py  (property-style checks over generated inputs, fixed seed)

## recallstorm/__main__.py  (calls recallstorm.cli.main.main)
## tests/integration/  (12 files, test_flow_*.py, each exercising modules from at least 5 earlier packages)
## docs/  (architecture.md, data_model.md, rules.md, operations.md)

CONVENTIONS (facts about the environment you are writing into)
- contract.py and contract_io.py exist at the repo root. Import with `from contract import ...`.
  Load data with `from contract import load_datapack; pack = load_datapack(data_dir)`.
- Rule.effective is a NAIVE wall-clock datetime, interpreted in each store's local tz (Store.tz).
  `at` passed to evaluate_sku is tz-aware; compare at.astimezone(ZoneInfo(store_tz)).replace(tzinfo=None)
  against rule.effective when you know the tz, else at.replace(tzinfo=None). Sale is prohibited when
  local(at) >= effective. evaluate_sku with state="CA" applies rules whose jurisdictions include "CA" or "US".
- Datetimes in plan.jsonl and events.jsonl are ISO 8601 with offset.
- The scenario file is data/scenario_<id>.json (fields: scenario_id, state, rule_ids, as_of, deadline).
- The deadline for every task window is the scenario deadline; windows must end strictly before it.
- data/labels.csv is ground truth and you will NOT see it. Do not read it from code.


=== contract.py ===
"""Recall Storm contract. Frozen before the core run. Do not edit after the expansion launches."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Protocol

# ---------- vocabulary (D3 checks every uppercase code against these) ----------
class Verdict(str, Enum):
    PULL = "PULL"; HOLD_VERIFY = "HOLD_VERIFY"; KEEP = "KEEP"

class Action(str, Enum):
    PULL = "PULL"; HOLD_VERIFY = "HOLD_VERIFY"; PLACE_SUB = "PLACE_SUB"; TAG_FLASH = "TAG_FLASH"

class StoreFormat(str, Enum):
    SUPERCENTER = "SUPERCENTER"; DISCOUNT = "DISCOUNT"; NEIGHBORHOOD = "NEIGHBORHOOD"; SAMS = "SAMS"

class ExceptionKind(str, Enum):
    DSD_VENDOR_PULL = "DSD_VENDOR_PULL"; ENDCAP_DISPLAY = "ENDCAP_DISPLAY"; TOPSTOCK = "TOPSTOCK"
    PICKUP_TOTES = "PICKUP_TOTES"; NOT_ON_PLANOGRAM = "NOT_ON_PLANOGRAM"; UNCLEAR_LABEL = "UNCLEAR_LABEL"

class HandoffKind(str, Enum):
    FLOATER = "FLOATER"; SUB_TRANSFER = "SUB_TRANSFER"; RETURN_CONSOLIDATION = "RETURN_CONSOLIDATION"

class DecidedBy(str, Enum):
    RULE = "RULE"; MODEL = "MODEL"

# ---------- input data ----------
@dataclass(frozen=True)
class Sku:
    sku_id: str; gtin: str; name: str; brand: str; category: str; ingredients: str
    is_food: bool; is_ingested_drug: bool; case_units: int; case_cube_ft3: float; case_weight_lb: float

@dataclass(frozen=True)
class Store:
    store_id: str; format: StoreFormat; state: str; city: str; lat: float; lon: float
    district: str; dc_id: str; tz: str            # tz like "America/Los_Angeles"

@dataclass(frozen=True)
class Location:
    aisle: str; bay: int; shelf: int; pos: int

@dataclass(frozen=True)
class Facing:
    store_id: str; sku_id: str; loc: Location; units: int

@dataclass(frozen=True)
class Associate:
    associate_id: str; store_id: str | None; district: str; is_floater: bool
    shift_start: datetime; shift_end: datetime     # local time, tz-aware

@dataclass(frozen=True)
class Truck:
    truck_id: str; dc_id: str; cube_ft3: float; weight_lb: float; depart: datetime

@dataclass(frozen=True)
class DcStock:
    dc_id: str; sku_id: str; cases: int

@dataclass(frozen=True)
class StoreNote:
    note_id: str; store_id: str; text: str          # free text; exceptions come from here

@dataclass(frozen=True)
class Rule:
    rule_id: str; additive: str; aliases: tuple[str, ...]; jurisdictions: tuple[str, ...]
    applies_to: tuple[str, ...]                     # "food", "ingested_drug", "cosmetic"
    effective: datetime                             # sale prohibited at or after this instant, local
    clause_ref: str; source_text: str

@dataclass
class DataPack:
    skus: list[Sku]; stores: list[Store]; facings: list[Facing]; associates: list[Associate]
    trucks: list[Truck]; dc_stock: list[DcStock]; substitutes: dict[str, list[str]]
    notes: list[StoreNote]; rules: list[Rule]; as_of: datetime

def load_datapack(data_dir: str) -> DataPack:
    """Loads data/*.jsonl into a DataPack. Implemented by us in contract_io.py (not generated)."""
    from contract_io import load  # ours
    return load(data_dir)

# ---------- outputs of the matched packages (acceptance tests target these) ----------
@dataclass(frozen=True)
class SkuDecision:
    sku_id: str; verdict: Verdict; additive: str | None; match_text: str | None
    match_start: int | None; match_end: int | None; rule_ids: tuple[str, ...]
    decided_by: DecidedBy; rationale: str

@dataclass(frozen=True)
class Allocation:
    alloc_id: str; dc_id: str; sub_sku_id: str; store_id: str; qty_cases: int; dc_balance_after: int

@dataclass(frozen=True)
class Stop:
    store_id: str; cases: int; cube_ft3: float; weight_lb: float

@dataclass(frozen=True)
class RouteManifest:
    manifest_id: str; truck_id: str; dc_id: str; stops: tuple[Stop, ...]; depart: datetime

class Classifier(Protocol):
    """Gemini hook for items rules cannot decide. Returns HOLD_VERIFY when unsure."""
    def __call__(self, sku: Sku, candidates: list[Rule]) -> SkuDecision: ...

# rules package MUST expose:
def evaluate_sku(sku: Sku, rules: list[Rule], state: str, at: datetime,
                 classifier: Classifier | None = None) -> SkuDecision: ...
# allocate package MUST expose (never exceed stock; integer cases; deterministic tie-breaks by store_id):
def allocate_substitutes(demand: dict[tuple[str, str], int],      # (store_id, sub_sku_id) -> cases wanted
                         stock: list[DcStock], stores: list[Store]) -> list[Allocation]: ...
# route package MUST expose (cube and weight within truck limits; every pulled case on exactly one stop):
def pack_returns(pulled_cases: dict[tuple[str, str], int],         # (store_id, sku_id) -> cases
                 skus: list[Sku], trucks: list[Truck], stores: list[Store]) -> list[RouteManifest]: ...

# ---------- plan.jsonl record types and required fields ----------
PLAN_TYPES: dict[str, tuple[str, ...]] = {
    "run":            ("run_id", "scenario_id", "generator", "as_of", "rule_ids", "src"),
    "sku_verdict":    ("sku_id", "gtin", "verdict", "additive", "match", "rule_ids", "jurisdictions",
                       "decided_by", "evidence_id", "src"),
    "evidence":       ("evidence_id", "sku_id", "rule_id", "clause_ref", "source_span", "rationale", "src"),
    "store_playbook": ("store_id", "format", "deadline", "windows", "counts", "associate_ids",
                       "exception_ids", "manifest_ids", "src"),
    "shelf_task":     ("task_id", "store_id", "sku_id", "action", "loc", "qty_units", "associate_id",
                       "window", "seq", "evidence_id", "sub_sku_id", "alloc_id", "src"),
    "exception":      ("exc_id", "store_id", "kind", "note_id", "resolution", "task_ids", "src"),
    "allocation":     ("alloc_id", "dc_id", "sub_sku_id", "store_id", "qty_cases", "dc_balance_after", "src"),
    "handoff":        ("handoff_id", "kind", "from_id", "to_id", "window", "qty", "ref_ids", "src"),
    "route_manifest": ("manifest_id", "truck_id", "dc_id", "stops", "limits", "depart", "src"),
}
# src = repo-relative path of the module that emitted the record. Windows are ISO local times [start, end].
# CLI contract: python -m recallstorm run --scenario <id> --data data/ --out out/<name>/
#   writes out/<name>/plan.jsonl and out/<name>/events.jsonl
# events.jsonl: {"t": iso, "store_id", "associate_id", "kind": "MOVE"|"PULL"|"PLACE"|"DONE", "loc", "task_id"}


=== data/rules.jsonl ===
{"rule_id": "CA_AB418_RED3", "additive": "RED3", "aliases": ["FD&C Red No. 3", "Red No. 3", "Red 3", "Red Dye 3", "erythrosine", "E127"], "jurisdictions": ["CA"], "applies_to": ["food"], "effective": "2027-01-01T00:00:00", "clause_ref": "Cal. Health & Safety Code 109025(a)", "source_text": "Commencing January 1, 2027, a person or entity shall not manufacture, sell, deliver, distribute, hold, or offer for sale, in commerce a food product for human consumption that contains any of the following substances: (1) Brominated vegetable oil. (2) Potassium bromate. (3) Propylparaben. (4) Red dye 3."}
{"rule_id": "FDA_RED3_FOOD", "additive": "RED3", "aliases": ["FD&C Red No. 3", "Red No. 3", "Red 3", "Red Dye 3", "erythrosine", "E127"], "jurisdictions": ["US"], "applies_to": ["food"], "effective": "2027-01-15T00:00:00", "clause_ref": "21 CFR 74.303 (revoked for food, 90 FR 4628)", "source_text": "FDA is revoking the authorization for the use of FD&C Red No. 3 in food and ingested drugs. Manufacturers who use FD&C Red No. 3 in food have until January 15, 2027 to reformulate their products."}
{"rule_id": "FDA_RED3_DRUG", "additive": "RED3", "aliases": ["FD&C Red No. 3", "Red No. 3", "Red 3", "Red Dye 3", "erythrosine", "E127"], "jurisdictions": ["US"], "applies_to": ["ingested_drug"], "effective": "2028-01-18T00:00:00", "clause_ref": "21 CFR 74.1303 (revoked for ingested drugs, 90 FR 4628)", "source_text": "Manufacturers of ingested drugs have until January 18, 2028 to reformulate."}


=== data/scenario_ca_red3.json ===
{
  "scenario_id": "ca_red3",
  "state": "CA",
  "rule_ids": [
    "CA_AB418_RED3"
  ],
  "as_of": "2026-12-30T18:00:00-08:00",
  "deadline": "2027-01-01T00:00:00-08:00",
  "note": "every window must end before 2027-01-01T00:00 local"
}


=== data/skus.jsonl (20 sample rows) ===
{"sku_id": "FDC1034191", "gtin": "07502264930572", "name": "Rainbow Sprinkles", "brand": "Chocolatera De Nayarit, S.A. De C.V.", "category": "baking decorations & dessert toppings", "ingredients": "SUGAR, CORN SYRUP, HYDROGENATED PALM KERNEL OIL, SOY LECITHIN, FD&C BLUE #1, FD&C YELLOW #5, FD&C YELLOW #6, FD&C RED #3, FD&C RED #40, SALT, HBT (BUTYLHYDROXYTOLUENE), CARNAUBA WAX.", "is_food": true, "is_ingested_drug": false, "case_units": 6, "case_cube_ft3": 2.05, "case_weight_lb": 23.2, "_real": true, "_src": "fdc:1034191"}
{"sku_id": "FDC1878485", "gtin": "00073621007017", "name": "Candy", "brand": "Angry Birds", "category": "candy", "ingredients": "SUGAR, CORN SYRUP, ADIPIC ACID, HYDROG. PALM KERNEL & PALM OILS AND SOYBEAN OIL MONO & DIGLYCERIDES, NATURAL & ARTIFICIAL FLAVORS, ARTIFICIAL COLORS FD&C RED 3, YELLOW 5, YELLOW 6, BLUE 2.", "is_food": true, "is_ingested_drug": false, "case_units": 12, "case_cube_ft3": 1.51, "case_weight_lb": 6.3, "_real": true, "_src": "fdc:1878485"}
{"sku_id": "FDC1913788", "gtin": "00811033712026", "name": "Maraschino Cherries Without Stem", "brand": "Bell Foods International", "category": "baking decorations & dessert toppings", "ingredients": "CHERRIES, HIGH FRUCTOSE CORN SYRUP, WATER, POTASSIUM SORBATE (A PRESERVATIVE), SODIUM BENZOATE (A PRESERVATIVE), CITRIC ACID, NATURAL AND ARTIFICIAL FLAVOR, FD&C RED #40, SULFUR DIOXIDE (A PRESERVATIVE).", "is_food": true, "is_ingested_drug": false, "case_units": 12, "case_cube_ft3": 1.43, "case_weight_lb": 4.6, "_real": true, "_src": "fdc:1913788"}
{"sku_id": "FDC1983505", "gtin": "00070572244003", "name": "Syrup, Bacon", "brand": "Tropical", "category": "syrups & molasses", "ingredients": "CORN SYRUP, HIGH FRUCTOSE CORN SYRUP, WATER, NATURAL AND ARTIFICIAL FLAVOR, SALT, POTASSIUM SORBATE (A PRESERVATIVE) AND CARAMEL COLOR.", "is_food": true, "is_ingested_drug": false, "case_units": 24, "case_cube_ft3": 1.51, "case_weight_lb": 5.1, "_real": true, "_src": "fdc:1983505"}
{"sku_id": "FDC2032505", "gtin": "00077290773105", "name": "Candy", "brand": "Bit-O-Honey", "category": "candy", "ingredients": "CORN SYRUP, SUGAR, NONFAT MILK, HYDROGENATED COCONUT OIL, ALMONDS, AND LESS THAN 2% OF HONEY, SALT, EGG WHITES, CANOLA AND/OR SAFFLOWER AND/OR PALM OIL, MODIFIED SOY PROTEIN, NATURAL FLAVOR, TBHQ AND CITRIC ACID (TO PRESERVE FRESHNESS).", "is_food": true, "is_ingested_drug": false, "case_units": 12, "case_cube_ft3": 2.12, "case_weight_lb": 5.2, "_real": true, "_src": "fdc:2032505"}
{"sku_id": "FDC2072562", "gtin": "00096619783953", "name": "Animal Crackers", "brand": "Kirkland Signature", "category": "cookies & biscuits", "ingredients": "ORGANIC WHEAT FLOUR, ORGANIC CANE SUGAR, ORGANIC PALM OIL, ORGANIC CANE INVERT SYRUP, ORGANIC DEGERMED CORN FLOUR, ORGANIC SUNFLOWER OIL, BAKING SODA, ORGANIC VANILLA EXTRACT, SALT, SOY LECITHIN, CREAM OF TARTAR, NATURAL FLAVOR, ORGANIC SPICE.", "is_food": true, "is_ingested_drug": false, "case_units": 8, "case_cube_ft3": 1.21, "case_weight_lb": 14.0, "_real": true, "_src": "fdc:2072562"}
{"sku_id": "FDC2099147", "gtin": "00007078446200", "name": "Graham Cracker", "brand": "Tops", "category": "crusts & dough", "ingredients": "GRAHAM CRACKER MEAL (ENRICHED FLOUR [WHEAT FLOUR, NIACIN, REDUCED IRON, THIAMIN MONONITRATE, RIBOFLAVIN, FOLIC ACID], SUGAR, WHOLE WHEAT FLOUR, PALM OIL, HIGH FRUCTOSE CORN SYRUP BROWN SUGAR, HONEY, SODIUM BICARBONATE, MOLASSES, SALT, MALT SYRUP [MALTED BARLEY, CORN], ARTIFICIAL FLAVOR), VEGETABLE SHORTENING (CONTAINS HYDROGENATED PALM KERNEL, PALM OIL, CANOLA OIL), SUGAR, CORNSTARCH.", "is_food": true, "is_ingested_drug": false, "case_units": 36, "case_cube_ft3": 0.82, "case_weight_lb": 6.8, "_real": true, "_src": "fdc:2099147"}
{"sku_id": "FDC2133371", "gtin": "00741643048683", "name": "Butter Syrup", "brand": "Lowes Foods", "category": "syrups & molasses", "ingredients": "CORN SYRUP, HIGH FRUCTOSE CORN SYRUP, WATER, SUGAR, NATURAL AND ARTIFICIAL FLAVOR, SALT, CARAMEL COLOR, POTASSIUM SORBATE (PRESERVATIVE), CELLULOSE GUM, SODIUM HEXAMETAPHOSPHATE.", "is_food": true, "is_ingested_drug": false, "case_units": 24, "case_cube_ft3": 1.09, "case_weight_lb": 6.4, "_real": true, "_src": "fdc:2133371"}
{"sku_id": "FDC2195999", "gtin": "00073621012912", "name": "Candy", "brand": "Pez", "category": "candy", "ingredients": "SUGAR, CORN SYRUP, ADIPIC ACID, HYDROGENATED PALM KERNEL & PALM OILS, MONO & DIGLYCERIDES, NATURAL & ARTIFICIAL FLAVORS.", "is_food": true, "is_ingested_drug": false, "case_units": 36, "case_cube_ft3": 1.02, "case_weight_lb": 5.0, "_real": true, "_src": "fdc:2195999"}
{"sku_id": "FDC2308934", "gtin": "00021333071390", "name": "Gummi Bears Candies, Gummi Bears", "brand": "Fareway", "category": "candy", "ingredients": "CORN SYRUP, SUGAR, WHITE GRAPE JUICE FROM CONCENTRATE, GELATIN, CITRIC ACID, SORBITOL, NATURAL AND ARTIFICIAL FLAVORS, CARNAUBA WAX, ARTIFICIAL COLORS (RED 40, YELLOW 5, YELLOW 6, BLUE 1).", "is_food": true, "is_ingested_drug": false, "case_units": 36, "case_cube_ft3": 1.75, "case_weight_lb": 21.2, "_real": true, "_src": "fdc:2308934"}
{"sku_id": "FDC2429227", "gtin": "00007789046152", "name": "Fruit Cocktail In 100% Juice, Fruit Cocktail", "brand": "Wegmans", "category": "canned fruit", "ingredients": "DICED PEACHES, DICED PEARS, WATER, GRAPES, PEACH PULP AND JUICE, PINEAPPLE SECTORS, PEAR JUICE CONCENTRATE, HALVED CHERRIES (COLORED RED WITH CARMINE), ASCORBIC ACID (VITAMIN C) TO PROTECT COLOR.", "is_food": true, "is_ingested_drug": false, "case_units": 12, "case_cube_ft3": 1.87, "case_weight_lb": 3.2, "_real": true, "_src": "fdc:2429227"}
{"sku_id": "FDC2493510", "gtin": "00011822446921", "name": "3 Pepper Jalapeno Beef Jerky, 3 Pepper Jalapeno", "brand": "Big Win", "category": "other snacks", "ingredients": "BEEF, SUGAR, WATER, SEA SALT, GARLIC POWDER, YEAST EXTRACT, NATURAL FLAVORS (JALAPENO, BLACK PEPPER, RED PEPPER), ONION POWDER, SPICES (OREGANO), CITRIC ACID, ROSEMARY EXTRACT WITH GREEN TEA EXTRACT, CELERY POWDER.", "is_food": true, "is_ingested_drug": false, "case_units": 12, "case_cube_ft3": 1.18, "case_weight_lb": 5.6, "_real": true, "_src": "fdc:2493510"}
{"sku_id": "FDC2524922", "gtin": "00078742374871", "name": "Sprinkle Mix", "brand": "Great Value", "category": "baking decorations & dessert toppings", "ingredients": "DEXTROSE, SUGAR, CORN STARCH, DEXTRIN, GLUCOSE SYRUP MAGNESIUM STEARATE, ARTIFICIAL VANILLA FAVOR, CONFECTIONER'S GLAZE, GUM ARABIC, CARNAUBA WAX, RED 40, RED 3, BLUE 1, YELLOW 5, YELLOW 6, BLUE2.", "is_food": true, "is_ingested_drug": false, "case_units": 12, "case_cube_ft3": 0.56, "case_weight_lb": 18.7, "_real": true, "_src": "fdc:2524922"}
{"sku_id": "FDC2567743", "gtin": "00070506072412", "name": "Rainbow Sprinkles", "brand": "Spice Farms", "category": "baking decorations & dessert toppings", "ingredients": "SUGAR, CORN STARCH, PALM OIL & PALM KERNEL OIL, DEXTRIN, SOY LECITHIN, SUNFLOWER LECITHIN, CARNAUBA WAX, CONFECTIONER'S GLAZE, FD&C YELLOW #5 LAKE, FD&C YELLOW #6 LAKE, FD&C BLUE #1 LAKE, FD&C RED #40 LAKE, FD&C RED #3, FD&C BLUE #2, FD&C RED #40, FD&C BLUE #1", "is_food": true, "is_ingested_drug": false, "case_units": 36, "case_cube_ft3": 1.22, "case_weight_lb": 7.9, "_real": true, "_src": "fdc:2567743"}
{"sku_id": "FDC2612060", "gtin": "00049646006823", "name": "Candied Jalapenos, Candied", "brand": "Preserved Harvest", "category": "pickles, olives, peppers & relishes", "ingredients": "JALAPENOS, (SALT, VINEGAR & CALCIUM CHLORIDE) SUGAR, WATER, VINEGAR, SALT, SPICES.", "is_food": true, "is_ingested_drug": false, "case_units": 24, "case_cube_ft3": 1.13, "case_weight_lb": 19.9, "_real": true, "_src": "fdc:2612060"}
{"sku_id": "FDC2655277", "gtin": "00079200079291", "name": "Gummy Clusters Candy, Gummy Clusters", "brand": "Nerds", "category": "candy", "ingredients": "CORN SYRUP, SUGAR, DEXTROSE, GELATIN, MODIFIED CORN STARCH, WATER, CONTAINS 2% OR LESS OF MALIC ACID (DL-MALIC ACID), CITRIC ACID, SODIUM CITRATE, APPLE JUICE CONCENTRATE, NATURAL AND ARTIFICIAL FLAVORS, GUM ARABIC, CARNAUBA WAX, RED 40 LAKE, RED 40, COLOR ADDED.", "is_food": true, "is_ingested_drug": false, "case_units": 36, "case_cube_ft3": 1.66, "case_weight_lb": 11.4, "_real": true, "_src": "fdc:2655277"}
{"sku_id": "FDC2677948", "gtin": "00085239015223", "name": "Mini Brownies With Frosting, Frosting", "brand": "Market Pantry", "category": "cakes, cupcakes, snack cakes", "ingredients": "BROWNIE: SUGAR, ENRICHED WHEAT FLOUR (WHEAT FLOUR, NIACIN, REDUCED IRON, THIAMINE MONONITRATE, RIBOFLAVIN, FOLIC ACID), SOYBEAN OIL, EGG WHITE, CORN SYRUP, WATER, SHORTENING (PALM, CANOLA, AND MODIFIED PALM OIL), CHOCOLATE (SUGAR, CHOCOLATE LIQUOR, COCOA BUTTER, SOY LECITHIN, VANILLA EXTRACT), COCOA POWDER (PROCESSED WITH ALKALI), SALT, NATURAL AND ARTIFICIAL FLAVOR, WHEY POWDER, MODIFIED CORN STARCH, LEAVENING (SODIUM ACID PYROPHOSPHATE, SODIUM BICARBONATE, CORN STARCH, MONOCALCIUM PHOSPHATE, CALCIUM SULFATE), SOY LECITHIN. ICING: ICING SUGAR, SHORTENING (CANOLA, PALM, MODIFIED PALM AND PALM KERNEL OIL), INVERT SUGAR, MARGARINE [SOYBEAN AND MODIFIED PALM OIL, WATER, SALT, WHEY POWDER, SOY LECITHIN, MONOGLYCERIDES, NATURAL FLAVOR, VITAMIN A PALMITATE, VITAMIN D3, COLOR (ANNATTO)], GLUCOSE, WATER, MODIFIED CORN STARCH, SKIM MILK POWDER, MONO AND DIGLYCERIDES, YELLOW 5, BLUE 1), ARTIFICIAL FLAVOR, SALT, POLYSORBATE 60. SPRINKLES: SUGAR, MODIFIED CORN STARCH, PALM KERNEL OIL, CORN STARCH, GUM ARABIC, SOY LECITHIN, ARTIFICIAL FLAVOR, POLYSORBATE 60.", "is_food": true, "is_ingested_drug": false, "case_units": 36, "case_cube_ft3": 0.82, "case_weight_lb": 15.7, "_real": true, "_src": "fdc:2677948"}
{"sku_id": "VAR0021", "gtin": "02000000000213", "name": "Dipped & Sprinkled Pretzels, Dipped & Sprinkled", "brand": "Favorite Day", "category": "popcorn, peanuts, seeds & related snacks", "ingredients": "CONFECTIONERY COATING (SUGAR, PALM KERNEL OIL, NONFAT DRY MILK, LACTOSE, TITANIUM DIOXIDE [COLOR], SOY LECITHIN [AN EMULSIFIER], DISTILLED MONOGLYCERIDES, VANILLA, FRACTIONATED COCONUT OIL, BLUE 1 LAKE, RED 40 LAKE), PRETZELS (ENRICHED WHEAT FLOUR [WHEAT FLOUR, NIACIN, REDUCED IRON, THIAMINE MONONITRATE, RIBOFLAVIN, FOLIC ACID], CORN SYRUP, SALT, VEGETABLE OIL [MAY CONTAIN ONE OR MORE OF THE FOLLOWING: CANOLA, CORN, SOYBEAN], VITAL WHEAT GLUTEN, SODIUM BICARBONATE, YEAST), NONPAREILS (SUGAR, CORNSTARCH, E127, RED 40, CARNAUBA WAX, CONFECTIONER'S GLAZE, BLUE 1).", "is_food": true, "is_ingested_drug": false, "case_units": 12, "case_cube_ft3": 1.81, "case_weight_lb": 4.2, "_real": false, "_kind": "alias:E127", "_base": "FDC2605087"}
{"sku_id": "VAR0081", "gtin": "02000000000817", "name": "Fruit Cocktail In Heavy Syrup", "brand": "Island Sun", "category": "canned fruit", "ingredients": "DICED PEACHES, DICED PEARS, GRAPES, PINEAPPLE SEGMENTS, CHERRIES (Red Dye 3), WATER, SUGAR, CITRIC ACID.", "is_food": true, "is_ingested_drug": false, "case_units": 12, "case_cube_ft3": 1.85, "case_weight_lb": 8.9, "_real": false, "_kind": "alias:Red Dye 3", "_base": "FDC2066569"}
{"sku_id": "VAR0141", "gtin": "02000000001418", "name": "Easter Basket Candy Pack #7", "brand": "The Candy Shoppe", "category": "seasonal kits", "ingredients": "KIT CONTAINS: Frosted Heart Pretzels, Frosted Heart: WHITE CONFECTIONERY COATING (SUGAR, PALM KERNEL OIL, NONFAT MILK POWDER, LACTOSE, TITANIUM DIOXIDE [COLOR], SOY LECITHIN (AN EMULSIFIERT, DISTILLED MONOGLYCERIDES, VANILLA), HEART SHAPED PRETZELS (ENRICHED WHEAT FLOUR (WHEAT FLOUR, NIACIN, REDUCED IRON, THIAMINE MONONITRATE, RIBOFLAVIN, FOLIC ACID), SALT, VEGETABLE OIL (MAY CONTAIN ONE OR MORE OF THE FOLLOWING: CANOLA, CORN, SOYBEAN], CORN SYRUP, SODIUM BICARBONATE, YEAST), PINK, LIGHT PINK, RED NONPAREILS (SUGAR, CORNSTARCH, RED 3 POWDER, RED 40 POWDER, CONFECTIONER'S GLAZE, CARNAUBA WAX). | Maraschino Cherries With Stems, Maraschino: CHERRIES, WATER, CORN SYRUP, HIGH FRUCTOSE CORN SYRUP, CITRIC ACID, NATURAL AND ARTIFICIAL FLAVOR, POTASSIUM SORBATE AND SODIUM BENZOATE (PRESERVATIVES), RED 40, SULFUR DIOXIDE (PRESERVATIVE).", "is_food": true, "is_ingested_drug": false, "case_units": 12, "case_cube_ft3": 2.03, "case_weight_lb": 4.9, "_real": false, "_kind": "bundle_kit", "_base": "FDC2504071"}

=== data/stores.jsonl (20 sample rows) ===
{"store_id": "SAMS4735", "format": "SAMS", "state": "CA", "city": "La Habra", "lat": 33.91287, "lon": -117.97008, "district": "D09", "dc_id": "DC_SOUTH", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:way/563170433", "_name": "Sam's Club", "_addr": "1400 South Beach Boulevard"}
{"store_id": "SAMS4767", "format": "SAMS", "state": "CA", "city": "Palmdale", "lat": 34.60838, "lon": -118.14441, "district": "D06", "dc_id": "DC_CENTRAL", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:way/472905677", "_name": "Sam's Club", "_addr": "39940 10th Street West"}
{"store_id": "SAMS6405", "format": "SAMS", "state": "CA", "city": "Yuba City", "lat": 39.13926, "lon": -121.64549, "district": "D01", "dc_id": "DC_NORTH", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:node/11993193507", "_name": "Sam's Club", "_addr": "900 North Walton Avenue"}
{"store_id": "SAMS6621", "format": "SAMS", "state": "CA", "city": "Roseville", "lat": 38.78642, "lon": -121.28773, "district": "D01", "dc_id": "DC_NORTH", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:way/45368716", "_name": "Sam's Club", "_addr": "904 Pleasant Grove Boulevard"}
{"store_id": "WM1563", "format": "SUPERCENTER", "state": "CA", "city": "Lancaster", "lat": 34.6938, "lon": -118.17406, "district": "D06", "dc_id": "DC_CENTRAL", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:relation/6955798", "_name": "Walmart Supercenter", "_addr": "44665 Valley Central Way"}
{"store_id": "WM1574", "format": "SUPERCENTER", "state": "CA", "city": "Bakersfield", "lat": 35.29875, "lon": -119.02938, "district": "D06", "dc_id": "DC_CENTRAL", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:way/59822569", "_name": "Walmart Supercenter", "_addr": "6225 Colony Street"}
{"store_id": "WM1575", "format": "SUPERCENTER", "state": "CA", "city": "Oroville", "lat": 39.49063, "lon": -121.57145, "district": "D01", "dc_id": "DC_NORTH", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:way/474456102", "_name": "Walmart Supercenter", "_addr": "465 Cal Oak Road"}
{"store_id": "WM1588", "format": "SUPERCENTER", "state": "CA", "city": "Victorville", "lat": 34.46512, "lon": -117.35443, "district": "D06", "dc_id": "DC_CENTRAL", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:way/1008760751", "_name": "Walmart Supercenter", "_addr": "11896 Amargosa Road"}
{"store_id": "WM1608", "format": "SUPERCENTER", "state": "CA", "city": "Red Bluff", "lat": 40.16293, "lon": -122.23437, "district": "D01", "dc_id": "DC_NORTH", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:way/546732624", "_name": "Walmart Supercenter", "_addr": "608 Luther Road"}
{"store_id": "WM1616", "format": "DISCOUNT", "state": "CA", "city": "Susanville", "lat": 40.40892, "lon": -120.63758, "district": "D01", "dc_id": "DC_NORTH", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:way/436352557", "_name": "Walmart", "_addr": "2900 Main Street"}
{"store_id": "WM1630", "format": "SUPERCENTER", "state": "CA", "city": "Yreka", "lat": 41.69865, "lon": -122.64457, "district": "D01", "dc_id": "DC_NORTH", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:way/360427744", "_name": "Walmart Supercenter", "_addr": "1906 Fort Jones Road"}
{"store_id": "WM1899", "format": "SUPERCENTER", "state": "CA", "city": "Riverside", "lat": 33.93853, "lon": -117.28613, "district": "D09", "dc_id": "DC_SOUTH", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:way/444490322", "_name": "Walmart Supercenter", "_addr": "6250 Valley Springs Parkway"}
{"store_id": "WM1912", "format": "SUPERCENTER", "state": "CA", "city": "Corona", "lat": 33.89079, "lon": -117.51729, "district": "D09", "dc_id": "DC_SOUTH", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:way/201454867", "_name": "Walmart Supercenter", "_addr": "479 North McKinley Street"}
{"store_id": "WM2028", "format": "SUPERCENTER", "state": "CA", "city": "Riverside", "lat": 33.93712, "lon": -117.45539, "district": "D09", "dc_id": "DC_SOUTH", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:node/928693137", "_name": "Walmart Supercenter", "_addr": "5200 Van Buren Boulevard"}
{"store_id": "WM2333", "format": "DISCOUNT", "state": "CA", "city": "Apple Valley", "lat": 34.52554, "lon": -117.22309, "district": "D06", "dc_id": "DC_CENTRAL", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:way/460848367", "_name": "Walmart", "_addr": "20251 Happy Trails Highway"}
{"store_id": "WM2523", "format": "DISCOUNT", "state": "CA", "city": "Brea", "lat": 33.91346, "lon": -117.86523, "district": "D09", "dc_id": "DC_SOUTH", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:way/142606474", "_name": "Walmart", "_addr": "2595 East Imperial Highway"}
{"store_id": "WM3139", "format": "NEIGHBORHOOD", "state": "CA", "city": "Bakersfield", "lat": 35.37013, "lon": -119.14746, "district": "D06", "dc_id": "DC_CENTRAL", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:node/5315598907", "_name": "Walmart Neighborhood Market", "_addr": "1249 Allen Road"}
{"store_id": "WM3141", "format": "NEIGHBORHOOD", "state": "CA", "city": "Bakersfield", "lat": 35.35339, "lon": -118.94765, "district": "D06", "dc_id": "DC_CENTRAL", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:node/4093403024", "_name": "Walmart Neighborhood Market", "_addr": "5037 East Brundage Lane"}
{"store_id": "WM4127", "format": "NEIGHBORHOOD", "state": "CA", "city": "Woodland", "lat": 38.68087, "lon": -121.78792, "district": "D01", "dc_id": "DC_NORTH", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:node/5315598128", "_name": "Walmart Neighborhood Market", "_addr": "215 California Street"}
{"store_id": "WM5603", "format": "NEIGHBORHOOD", "state": "CA", "city": "Downey", "lat": 33.92814, "lon": -118.14774, "district": "D09", "dc_id": "DC_SOUTH", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:way/351803045", "_name": "Walmart Neighborhood Market", "_addr": "12270 Paramount Boulevard"}

=== data/facings.jsonl (20 sample rows) ===
{"store_id": "SAMS4735", "sku_id": "FDC1034191", "loc": {"aisle": "A01", "bay": 1, "shelf": 1, "pos": 1}, "units": 11}
{"store_id": "SAMS6405", "sku_id": "FDC1458937", "loc": {"aisle": "A01", "bay": 1, "shelf": 1, "pos": 3}, "units": 10}
{"store_id": "WM1563", "sku_id": "FDC1460285", "loc": {"aisle": "A01", "bay": 1, "shelf": 4, "pos": 3}, "units": 7}
{"store_id": "WM1563", "sku_id": "FDC2651690", "loc": {"aisle": "A06", "bay": 5, "shelf": 4, "pos": 2}, "units": 9}
{"store_id": "WM1574", "sku_id": "FDC2314254", "loc": {"aisle": "A04", "bay": 4, "shelf": 2, "pos": 1}, "units": 32}
{"store_id": "WM1575", "sku_id": "FDC2016322", "loc": {"aisle": "A02", "bay": 2, "shelf": 4, "pos": 6}, "units": 35}
{"store_id": "WM1575", "sku_id": "VAR0073", "loc": {"aisle": "A08", "bay": 1, "shelf": 4, "pos": 5}, "units": 16}
{"store_id": "WM1588", "sku_id": "FDC2535728", "loc": {"aisle": "A05", "bay": 5, "shelf": 2, "pos": 4}, "units": 7}
{"store_id": "WM1608", "sku_id": "FDC2110231", "loc": {"aisle": "A03", "bay": 3, "shelf": 5, "pos": 3}, "units": 17}
{"store_id": "WM1616", "sku_id": "FDC1893879", "loc": {"aisle": "A01", "bay": 2, "shelf": 3, "pos": 2}, "units": 33}
{"store_id": "WM1630", "sku_id": "FDC2066567", "loc": {"aisle": "A02", "bay": 5, "shelf": 4, "pos": 4}, "units": 20}
{"store_id": "WM1630", "sku_id": "VAR0161", "loc": {"aisle": "A08", "bay": 4, "shelf": 4, "pos": 3}, "units": 8}
{"store_id": "WM1899", "sku_id": "FDC2606004", "loc": {"aisle": "A06", "bay": 3, "shelf": 2, "pos": 2}, "units": 8}
{"store_id": "WM1912", "sku_id": "FDC2172550", "loc": {"aisle": "A04", "bay": 1, "shelf": 5, "pos": 1}, "units": 30}
{"store_id": "WM2028", "sku_id": "FDC1924887", "loc": {"aisle": "A01", "bay": 5, "shelf": 2, "pos": 6}, "units": 32}
{"store_id": "WM2028", "sku_id": "VAR0001", "loc": {"aisle": "A07", "bay": 4, "shelf": 2, "pos": 5}, "units": 21}
{"store_id": "WM2523", "sku_id": "FDC2009631", "loc": {"aisle": "A01", "bay": 4, "shelf": 1, "pos": 1}, "units": 23}
{"store_id": "WM3139", "sku_id": "FDC2415607", "loc": {"aisle": "A03", "bay": 2, "shelf": 5, "pos": 2}, "units": 10}
{"store_id": "WM3141", "sku_id": "FDC2578244", "loc": {"aisle": "A04", "bay": 2, "shelf": 2, "pos": 5}, "units": 9}
{"store_id": "WM4127", "sku_id": "FDC2752913", "loc": {"aisle": "A05", "bay": 1, "shelf": 3, "pos": 6}, "units": 29}

=== data/associates.jsonl (20 sample rows) ===
{"associate_id": "SAMS4735-A00", "store_id": "SAMS4735", "district": "D09", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "SAMS4767-A01", "store_id": "SAMS4767", "district": "D06", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "SAMS6405-A02", "store_id": "SAMS6405", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "SAMS6621-A03", "store_id": "SAMS6621", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM1563-A04", "store_id": "WM1563", "district": "D06", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM1574-A01", "store_id": "WM1574", "district": "D06", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM1574-A12", "store_id": "WM1574", "district": "D06", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM1575-A09", "store_id": "WM1575", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM1588-A06", "store_id": "WM1588", "district": "D06", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM1608-A03", "store_id": "WM1608", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM1616-A00", "store_id": "WM1616", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM1630-A05", "store_id": "WM1630", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM1899-A02", "store_id": "WM1899", "district": "D09", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM1899-A13", "store_id": "WM1899", "district": "D09", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM1912-A10", "store_id": "WM1912", "district": "D09", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM2028-A07", "store_id": "WM2028", "district": "D09", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM2333-A04", "store_id": "WM2333", "district": "D06", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM3139-A03", "store_id": "WM3139", "district": "D06", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM3141-A06", "store_id": "WM3141", "district": "D06", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM5603-A01", "store_id": "WM5603", "district": "D09", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}

=== data/trucks.jsonl (20 sample rows) ===
{"truck_id": "DC_CENTRAL-T0", "dc_id": "DC_CENTRAL", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_CENTRAL-T1", "dc_id": "DC_CENTRAL", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_CENTRAL-T2", "dc_id": "DC_CENTRAL", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_CENTRAL-T3", "dc_id": "DC_CENTRAL", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_CENTRAL-T4", "dc_id": "DC_CENTRAL", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_CENTRAL-T5", "dc_id": "DC_CENTRAL", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_NORTH-T0", "dc_id": "DC_NORTH", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_NORTH-T1", "dc_id": "DC_NORTH", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_NORTH-T2", "dc_id": "DC_NORTH", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_NORTH-T3", "dc_id": "DC_NORTH", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_NORTH-T4", "dc_id": "DC_NORTH", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_NORTH-T5", "dc_id": "DC_NORTH", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_SOUTH-T0", "dc_id": "DC_SOUTH", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_SOUTH-T1", "dc_id": "DC_SOUTH", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_SOUTH-T2", "dc_id": "DC_SOUTH", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_SOUTH-T3", "dc_id": "DC_SOUTH", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_SOUTH-T4", "dc_id": "DC_SOUTH", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_SOUTH-T5", "dc_id": "DC_SOUTH", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}

=== data/dc_stock.jsonl (20 sample rows) ===
{"dc_id": "DC_CENTRAL", "sku_id": "FDC1141715", "cases": 12}
{"dc_id": "DC_CENTRAL", "sku_id": "FDC2013052", "cases": 5}
{"dc_id": "DC_CENTRAL", "sku_id": "FDC2093122", "cases": 5}
{"dc_id": "DC_CENTRAL", "sku_id": "FDC2178255", "cases": 9}
{"dc_id": "DC_CENTRAL", "sku_id": "FDC2427753", "cases": 5}
{"dc_id": "DC_CENTRAL", "sku_id": "FDC2544428", "cases": 4}
{"dc_id": "DC_CENTRAL", "sku_id": "FDC2660333", "cases": 4}
{"dc_id": "DC_NORTH", "sku_id": "FDC1877171", "cases": 4}
{"dc_id": "DC_NORTH", "sku_id": "FDC2026573", "cases": 3}
{"dc_id": "DC_NORTH", "sku_id": "FDC2102896", "cases": 2}
{"dc_id": "DC_NORTH", "sku_id": "FDC2284520", "cases": 6}
{"dc_id": "DC_NORTH", "sku_id": "FDC2454962", "cases": 11}
{"dc_id": "DC_NORTH", "sku_id": "FDC2594947", "cases": 3}
{"dc_id": "DC_NORTH", "sku_id": "FDC421530", "cases": 3}
{"dc_id": "DC_SOUTH", "sku_id": "FDC1913788", "cases": 6}
{"dc_id": "DC_SOUTH", "sku_id": "FDC2051416", "cases": 7}
{"dc_id": "DC_SOUTH", "sku_id": "FDC2122309", "cases": 4}
{"dc_id": "DC_SOUTH", "sku_id": "FDC2338061", "cases": 2}
{"dc_id": "DC_SOUTH", "sku_id": "FDC2499832", "cases": 3}
{"dc_id": "DC_SOUTH", "sku_id": "FDC2612440", "cases": 3}

=== data/notes.jsonl (20 sample rows) ===
{"note_id": "N0000", "store_id": "SAMS4735", "text": "Endcap 16 holds a vendor Halloween display; candy there is not on the planogram."}
{"note_id": "N0003", "store_id": "SAMS4767", "text": "Frito-Lay DSD rep restocks Tuesdays; DSD items are vendor-pulled, do not pack for DC return."}
{"note_id": "N0006", "store_id": "SAMS6405", "text": "Topstock above aisle 12 has overflow cases of baking decorations."}
{"note_id": "N0009", "store_id": "SAMS6621", "text": "Online pickup totes staged in backroom bay 4 may contain affected items."}
{"note_id": "N0012", "store_id": "WM1563", "text": "Aisle 5 moved to garden center during remodel; locations are not on planogram."}
{"note_id": "N0015", "store_id": "WM1574", "text": "Store-brand frosting labels are smudged from a printer fault; check ingredients by hand."}
{"note_id": "N0018", "store_id": "WM1575", "text": "Endcap 14 holds a vendor Halloween display; candy there is not on the planogram."}
{"note_id": "N0021", "store_id": "WM1588", "text": "Frito-Lay DSD rep restocks Tuesdays; DSD items are vendor-pulled, do not pack for DC return."}
{"note_id": "N0024", "store_id": "WM1608", "text": "Topstock above aisle 2 has overflow cases of baking decorations."}
{"note_id": "N0027", "store_id": "WM1616", "text": "Online pickup totes staged in backroom bay 1 may contain affected items."}
{"note_id": "N0030", "store_id": "WM1630", "text": "Aisle 7 moved to garden center during remodel; locations are not on planogram."}
{"note_id": "N0033", "store_id": "WM1899", "text": "Store-brand frosting labels are smudged from a printer fault; check ingredients by hand."}
{"note_id": "N0036", "store_id": "WM1912", "text": "Endcap 20 holds a vendor Halloween display; candy there is not on the planogram."}
{"note_id": "N0039", "store_id": "WM2028", "text": "Frito-Lay DSD rep restocks Tuesdays; DSD items are vendor-pulled, do not pack for DC return."}
{"note_id": "N0042", "store_id": "WM2333", "text": "Topstock above aisle 6 has overflow cases of baking decorations."}
{"note_id": "N0045", "store_id": "WM2523", "text": "Online pickup totes staged in backroom bay 10 may contain affected items."}
{"note_id": "N0048", "store_id": "WM3139", "text": "Aisle 2 moved to garden center during remodel; locations are not on planogram."}
{"note_id": "N0051", "store_id": "WM3141", "text": "Store-brand frosting labels are smudged from a printer fault; check ingredients by hand."}
{"note_id": "N0054", "store_id": "WM4127", "text": "Endcap 2 holds a vendor Halloween display; candy there is not on the planogram."}
{"note_id": "N0057", "store_id": "WM5603", "text": "Frito-Lay DSD rep restocks Tuesdays; DSD items are vendor-pulled, do not pack for DC return."}

=== data/substitutes.json (sample) ===
{"FDC1034191": ["VAR0172"], "FDC1039055": ["FDC2009631", "FDC2030891"], "FDC1096385": ["FDC2594947", "VAR0182"], "FDC1138169": ["FDC2028308", "FDC2278504"], "FDC1152536": ["VAR0172"], "FDC1152555": ["FDC1863608"], "FDC1850898": ["FDC2101396", "VAR0182"], "FDC1851197": ["FDC2099158", "FDC2099175"], "FDC1861265": ["FDC1858097", "FDC2016691"], "FDC1863607": ["FDC2067256", "FDC2656035"], "FDC1864116": ["FDC1889618"], "FDC1873319": ["FDC2540675", "FDC2606211"], "FDC1874472": ["FDC2525111"], "FDC1878485": ["FDC2415865"], "FDC1878835": ["FDC2541940"], "FDC1885241": ["FDC2630123"], "FDC1885264": ["FDC2375329"], "FDC1885345": ["FDC2016691"], "FDC1885462": ["FDC1889890", "FDC2415607"], "FDC1886623": ["FDC2454957", "VAR0159"]}

OUTPUT PROTOCOL (follow exactly)
1. First emit the manifest between the lines <<<MANIFEST>>> and <<<END MANIFEST>>>.
   One JSON object per line: {"path": "...", "purpose": "...", "public": ["name(arg, arg) -> type", ...],
   "depends_on": ["path", ...]}
2. Then emit every manifest file, in manifest order, each as:
   <<<FILE path=relative/path.py>>>
   ...complete file contents...
   <<<END FILE>>>
3. Never emit text outside these blocks. No markdown fences inside files.
4. Every file is complete and runnable. Forbidden: pass as a body, TODO, NotImplementedError, "...",
   "rest omitted", placeholder comments.
5. Import shared types only from contract.py (already exists; do not re-emit it). Use its enums for every code value.
6. Every plan.jsonl record must include "src": the path of the module that emitted it.
7. Python 3.11, standard library plus pytest and duckdb only. Deterministic: no randomness without a fixed seed.
8. Unit tests for package X go in tests/unit/test_X_*.py immediately after package X.
9. Stop only after the last manifest file is complete.

