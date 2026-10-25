# Regulatory Rules & Jurisdiction Engine

## Supported Regulations

1. **California Food Safety Act (AB 418) - Cal. Health & Safety Code 109025(a)**
   - **Jurisdiction**: `CA`
   - **Scope**: `food`
   - **Effective**: `2027-01-01T00:00:00` (local store wall-clock)
   - **Prohibited Substances**:
     - `RED3`: FD&C Red No. 3, Red Dye 3, Red 3, Erythrosine, E127, CI 45430 (`CA_AB418_RED3`)
     - `BVO`: Brominated vegetable oil, E443 (`CA_AB418_BVO`)
     - `POTASSIUM_BROMATE`: Potassium bromate, bromated flour, E924 (`CA_AB418_BROMATE`)
     - `PROPYLPARABEN`: Propylparaben, E216 (`CA_AB418_PROPYLPARABEN`)

2. **FDA Revocation of FD&C Red No. 3 (90 FR 4628)**
   - `FDA_RED3_FOOD` (21 CFR 74.303): `US`, `food`, effective `2027-01-15T00:00:00`
   - `FDA_RED3_DRUG` (21 CFR 74.1303): `US`, `ingested_drug`, effective `2028-01-18T00:00:00`

3. **FDA Revocation of Brominated Vegetable Oil (89 FR 55040)**
   - `FDA_BVO_FOOD` (21 CFR 180.30): `US`, `food`, effective `2025-08-02T00:00:00`

4. **Minnesota Amara's Law (Minn. Stat. 116.943 Subd. 5)**
   - `MN_PFAS_116_943`: `MN`, intentionally added PFAS (`PTFE`, `PFOA`, `PFOS`) in 11 product categories including cookware, cosmetics, cleaning products, dental floss, ski wax, and juvenile products, effective `2025-01-01T00:00:00`.

5. **CARB Consumer Products Regulation (17 CCR 94509)**
   - `CARB_LUBRICANT_VOC`: `CA`, multi-purpose lubricants exceeding `10%` VOC by weight, effective `2026-01-01T00:00:00`.

## Timezone & Preemption Semantics

- `Rule.effective` is a naive wall-clock datetime interpreted in each store's local timezone (`Store.tz`).
- When evaluating a SKU for a state (e.g. `state="CA"`), rules whose `jurisdictions` include `"CA"` or `"US"` are candidates.
- Sale is prohibited when `local(at) >= rule.effective`.
