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
