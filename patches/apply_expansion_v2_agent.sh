#!/bin/sh
# OURS. Rebuilds gen/expansion_v2_agentpatched/ = gen/expansion_v2/ (unedited Argon v2) + managed-agent patches, in order.
set -e
cd "$(dirname "$0")/.."
rm -rf gen/expansion_v2_agentpatched && cp -R gen/expansion_v2 gen/expansion_v2_agentpatched
for p in patches/agent/v2_aliases_translations.patch patches/agent/v2_plan_tasks_labor.patch; do
  patch -s -p1 -d gen/expansion_v2_agentpatched < "$p"; echo "applied $p"
done
