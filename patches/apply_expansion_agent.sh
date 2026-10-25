#!/bin/sh
# OURS. Rebuilds gen/expansion_agentpatched/ = gen/expansion/ (unedited Argon v1) + managed-agent patches, in order.
set -e
cd "$(dirname "$0")/.."
rm -rf gen/expansion_agentpatched && cp -R gen/expansion gen/expansion_agentpatched
for p in patches/agent/exp_plan_tasks_labor.patch patches/agent/exp_aliases_detect_coverage.patch patches/agent/exp_route_packing.patch; do
  patch -s -p1 -d gen/expansion_agentpatched < "$p"; echo "applied $p"
done
