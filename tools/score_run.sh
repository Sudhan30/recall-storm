#!/bin/sh
# OURS. Scores one finished Argon generation end to end: split, seams, code checks, drill, hidden tests, lot scenario.
# Usage: tools/score_run.sh NAME            (reads runs/NAME/, writes gen/NAME/, out/NAME/, reports/NAME_*)
set -u
cd "$(dirname "$0")/.."
N="$1"
PY=.venv/bin/python
echo "== split";      $PY tools/split_stream.py runs/$N/stream.txt --log runs/$N/stream_log.jsonl --out gen/$N/ | tail -3
echo "== seams";      $PY tools/seam_check.py runs/$N/ --report reports/${N}_seams.json | tail -1
echo "== code";       $PY tools/verify_code.py gen/$N/ --offsets gen/$N/offsets.jsonl --report reports/${N}_code.json --jobs 6 --timeout 60 | tail -12
echo "== drill";      PYTHONPATH=gen/$N:. $PY -m recallstorm run --scenario ca_red3 --data data/ --out out/$N/ > reports/${N}_drill_log.txt 2>&1 \
                        && $PY tools/verify_plan.py out/$N/plan.jsonl --labels data/labels.csv --data data/ \
                             --report reports/${N}_plan.json --offsets gen/$N/offsets.jsonl | sed -n 1,6p \
                        || { echo "drill crashed:"; tail -15 reports/${N}_drill_log.txt; }
echo "== hidden tests"
PYTHONPATH=gen/$N:. $PY -m pytest acceptance -q --no-header -p no:cacheprovider --junitxml reports/accept_$N.xml 2>&1 | tail -1
for p in rules allocate route; do printf "  %-9s" $p; PYTHONPATH=gen/$N:. $PY -m pytest acceptance/test_$p.py -q --no-header -p no:cacheprovider 2>&1 | tail -1; done
echo "== lot scenario (fda_lots, via adapter)"
for m in gs1 gs1_lotinv cli; do
  printf "  %-11s" $m
  RECALLSTORM_GEN=gen/$N $PY scenarios/fda_lots/adapter.py --mode $m --out out/${N}_fda_lots_$m/ > reports/${N}_fda_lots_${m}_log.txt 2>&1 \
    && $PY tools/verify_lots.py out/${N}_fda_lots_$m/plan.jsonl --name ${N}_fda_lots_$m 2>&1 | sed -n 2,3p | tr -s " " | paste -sd" " - \
    || echo "adapter failed (see reports/${N}_fda_lots_${m}_log.txt)"
done
echo "== hops"
$PY -c "
import json; h=[json.loads(l) for l in open('runs/$N/hops.jsonl') if '\"finish\"' in l]
inp=sum(x['prompt_hop'] or 0 for x in h); out=h[-1]['visible_total']
print(f'{len(h)} hops, {out:,} visible tokens, {h[-1][\"t\"]/60:.1f} min, finish {h[-1][\"finish\"]}, input {inp:,}, est \${inp*2e-6+out*10e-6:.2f}')"
