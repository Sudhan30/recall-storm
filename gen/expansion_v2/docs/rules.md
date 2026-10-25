# Regulatory Rules & Date Engine

## Local Wall-Clock Evaluation
`Rule.effective` is a naive wall-clock `datetime` interpreted in each store's local timezone (`Store.tz`). When `evaluate_sku(sku, rules, state, at, classifier=None)` is called:
- `at` is converted to naive local wall-clock time (`at.replace(tzinfo=None)` or in the target timezone).
- Sale is prohibited when `local(at) >= rule.effective`.
- `state="CA"` applies rules whose `jurisdictions` include `"CA"` or `"US"`.
- Product scope (`Rule.applies_to`) is matched against `sku.is_food` (`"food"`), `sku.is_ingested_drug` (`"ingested_drug"`), or topical/other (`"cosmetic"`).

## Supported Regulatory Regimes
- **CA AB 418 (Cal. Health & Safety Code 109025(a))**: Effective `2027-01-01T00:00:00` in `CA` for `food` containing Red Dye 3, Brominated Vegetable Oil (BVO), Potassium Bromate, or Propylparaben.
- **FDA Red No. 3 Food Revocation (21 CFR 74.303, 90 FR 4628)**: Effective `2027-01-15T00:00:00` in `US` for `food`.
- **FDA Red No. 3 Ingested Drug Revocation (21 CFR 74.1303, 90 FR 4628)**: Effective `2028-01-18T00:00:00` in `US` for `ingested_drug`.
- **FDA BVO Revocation (21 CFR 180.30, 89 FR 55040)**: Effective `2025-08-02T00:00:00` in `US` for `food`.
- **Minnesota PFAS Statute 116.943 Subd. 5**: Effective `2025-01-01T00:00:00` in `MN` for cookware, cosmetics, juvenile products, and fabric treatments.
- **CARB Multi-Purpose Lubricant VOC (17 CCR 94509(a))**: 25% VOC limit by weight in `CA`.
