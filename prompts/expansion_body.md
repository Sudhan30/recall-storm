You are expanding Recall Storm into a full platform in ONE continued generation.
contract.py is frozen and already exists. Everything you write must use it unchanged.

Write these packages in this exact order (positions matter for our measurements):
core/ (ID scheme, errors, config, logging) -> ingest/ (USDA FDC, Open Food Facts, openFDA enforcement, CPSC,
store list parsers) -> aliases/ -> rules/ (FDA Red No. 3 food and drug, CA AB 418 four additives, BVO,
Minnesota PFAS 116.943, CARB multi-purpose lubricant VOC; jurisdiction and date engine) -> adjudicate/ ->
gs1/ (GTIN check digits, AI 01/10/17, Digital Link, recall lot and date-range matching) -> store/ -> labor/ ->
allocate/ -> plan/ -> sim/ -> gs1-based recall scenario (openFDA lot codes) -> route/ (LAST package) -> cli/ ->
tests/integration/ (cross-package and property tests) -> docs/.
Each package is followed by its unit tests. route/ must be the last package before cli/.

For every package, implement the full public API listed in the manifest you write, with docstrings,
input validation, and error handling. Integration tests must exercise modules from every earlier package.

