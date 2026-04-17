#!/usr/bin/env bash
set -euo pipefail

# Pre-commit hook wrapper for stable local secret scanning.
# - If HEAD~1 exists, scan the incremental git range.
# - Otherwise (e.g. first commit), fall back to filesystem scan.
if git rev-parse --verify HEAD~1 >/dev/null 2>&1; then
  exec trufflehog git "file://." \
    --since-commit HEAD~1 \
    --branch HEAD \
    --results=verified \
    --fail \
    --no-update
fi

exec trufflehog filesystem . \
  --results=verified \
  --fail \
  --no-update
