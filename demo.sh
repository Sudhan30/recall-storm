#!/bin/sh
# OURS. Live demo: run Argon's working core on 20 stores, verify it, open the map.
# Usage: ./demo.sh            (core with the 3 logged fixes; ./demo.sh raw for Argon's unedited core)
set -e
cd "$(dirname "$0")"
B=${1:-patched}
if [ "$B" = raw ]; then GEN=gen/core; OUT=out/core; else ./patches/apply_core.sh >/dev/null; GEN=gen/core_patched; OUT=out/core_patched; fi
lsof -i :8000 >/dev/null 2>&1 || (python3 -m http.server -d . 8000 >/dev/null 2>&1 &)
echo "\$ python -m recallstorm run --scenario ca_red3 --data data/ --out $OUT/"
PYTHONPATH=$GEN:. .venv/bin/python -m recallstorm run --scenario ca_red3 --data data/ --out $OUT/
echo "\$ python tools/verify_plan.py $OUT/plan.jsonl"
.venv/bin/python tools/verify_plan.py $OUT/plan.jsonl --labels data/labels.csv --data data/ --report reports/demo_plan.json | sed -n 1,4p
.venv/bin/python viewer/build_data.py >/dev/null
[ -f out/expansion/plan.jsonl ] && [ -f out/expansion_agentpatched/plan.jsonl ] && .venv/bin/python viewer/build_compare.py >/dev/null
open "http://localhost:8000/viewer/#map"
