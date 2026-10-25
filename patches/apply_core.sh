#!/bin/sh
# OURS. Rebuilds gen/core_patched/ = gen/core/ (unedited Argon output) + patches/core/*.patch, in order.
set -e
cd "$(dirname "$0")/.."
rm -rf gen/core_patched && cp -R gen/core gen/core_patched
for p in patches/core/*.patch; do patch -s -p1 -d gen/core_patched < "$p"; echo "applied $p"; done
