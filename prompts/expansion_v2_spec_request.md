You are helping scope a software project. Recall Storm is a retailer compliance-drill platform (Python) that finds banned or recalled products in stores, plans shelf pulls, substitutes, labor, returns trucks and reporting. It already has these packages/modules (do NOT repeat them):
core/ids, core/errors, core/config, core/logging_setup, core/clock, core/jsonl, core/validate, core/registry, ingest/recall_feeds, ingest/labels_ocr, ingest/vendor_catalog, ingest/usda_fdc, ingest/open_food_facts, ingest/openfda_enforcement, ingest/cpsc, ingest/store_list, ingest/planogram, ingest/staffing, ingest/manifest_io, aliases/translations, aliases/spans, aliases/normalize, aliases/lexicon, aliases/detect, aliases/decoys, aliases/unclear, aliases/bundles, rules/potassium_bromate, rules/propylparaben, rules/preemption, rules/model, rules/jurisdiction, rules/dates, rules/scope, rules/red3, rules/ab418, rules/bvo, rules/pfas_mn, rules/carb_voc, rules/engine, adjudicate/overrides, adjudicate/sampling, adjudicate/queue, adjudicate/classifier, adjudicate/evidence, adjudicate/audit, gs1/epcis, gs1/barcodes, gs1/gtin, gs1/ai, gs1/digital_link, gs1/lots, gs1/match, store/backroom, store/signage, store/layout, store/facings, store/exceptions, store/formats, labor/compliance, labor/skills, labor/shifts, labor/estimates, labor/assign, labor/floaters, allocate/stock, allocate/priority, allocate/demand, allocate/allocator, allocate/transfers, plan/exceptions_plan, plan/deadline, plan/explain, plan/tasks, plan/playbook, plan/handoffs, plan/assemble, sim/walking, sim/disruptions, sim/events, sim/replay, sim/metrics, scenario_gs1/scenario, scenario_gs1/lot_pull, route/capacity, route/dispatch, route/returns, route/packing, route/stops, report/summary, report/checks, report/export, report/dashboard, cli/main

Propose exactly 160 NEW modules, each a distinct, realistic responsibility, spread across these NEW packages (about 12-18 modules each):
- states/        additive and product laws in other states (NY, IL, PA, WA, NJ, MN, TX, LA, WV, UT, AZ), one module per law, each different in substance
- recall_lots/   FDA/USDA-FSIS lot-and-date recall scenario: notice parsing, lot ranges, best-by windows, distribution lists, depth of recall, effectiveness checks
- food_safety/   temperature holds, allergen cross-contact, sanitation logs, consumer complaints, sampling plans
- inventory/     on-hand reconciliation, shrink, cycle counts, quarantine bins, reverse logistics accounting
- pricing/       markdowns, price-lookup blocks, POS sale blocks, register prompts, promotion conflicts
- comms/         store notices, associate briefings, customer notifications, vendor notices, regulator reports
- vendor/        chargebacks, reformulation tracking, certificates, DSD coordination, credits
- dc_ops/        DC receiving holds, pick-face blocks, outbound holds, yard management, carrier tendering
- analytics/     drill KPIs, risk scoring, forecasting exposure, anomaly detection, trend reports
- governance/    audit evidence packs, approvals, sign-offs, retention, access logs
Each module gets exactly 12 public names (CamelCase = class, otherwise snake_case function), concrete and specific to that module.

Output ONLY lines in this exact format, nothing else:
pkg/module_name: name1 name2 name3 name4 name5 name6 name7 name8 name9 name10 name11 name12
