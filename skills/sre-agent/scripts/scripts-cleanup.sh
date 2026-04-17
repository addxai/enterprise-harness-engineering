#!/bin/bash
# Clean up temporary script directory under .scripts/
# Generic tool for all sre-agent modes (Patrol, Diagnosis, etc.)
#
# Usage:
#   bash scripts/scripts-cleanup.sh <directory-name>
#
# Examples:
#   bash scripts/scripts-cleanup.sh Patrol-main
#   bash scripts/scripts-cleanup.sh Patrol-prod
#   bash scripts/scripts-cleanup.sh Diagnosis-k8s-443167
#
# Safety:
#   - Name must match: alphanumeric + hyphen + underscore
#   - Must start with a known prefix (Patrol- or Diagnosis-)
#   - Rejects path traversal (.. / \ ~)
#   - Rejects symlinks
#   - Only operates under .scripts/
#   - Idempotent: no error if directory does not exist

set -euo pipefail

NAME="${1:-}"

if [ -z "$NAME" ]; then
    echo "Error: directory name required"
    echo "Usage: $0 <directory-name>"
    echo "Example: $0 Patrol-main"
    exit 1
fi

# Must start with known prefix
if [[ "$NAME" != Patrol-* ]] && [[ "$NAME" != Diagnosis-* ]]; then
    echo "Error: name must start with Patrol- or Diagnosis-"
    exit 1
fi

# Reject path traversal and special characters
if [[ "$NAME" == *..* ]] || [[ "$NAME" == */* ]] || [[ "$NAME" == *\\* ]] || [[ "$NAME" == *~* ]]; then
    echo "Error: invalid characters in name"
    exit 1
fi

# Only allow alphanumeric, dash, underscore
if [[ ! "$NAME" =~ ^[A-Za-z0-9_-]+$ ]]; then
    echo "Error: name contains invalid characters"
    exit 1
fi

SCRIPTS_DIR=".scripts"
TARGET="${SCRIPTS_DIR}/${NAME}"

# Verify target is under .scripts/ with known prefix
case "$TARGET" in
    .scripts/Patrol-*) ;;
    .scripts/Diagnosis-*) ;;
    *) echo "Error: target $TARGET is not a valid directory under .scripts/"; exit 1 ;;
esac

# Reject symlinks
if [ -L "$TARGET" ]; then
    echo "Error: $TARGET is a symlink, refusing to clean"
    exit 1
fi

# Idempotent: no error if not exists
if [ ! -d "$TARGET" ]; then
    exit 0
fi

# Remove contents then directory
find "$TARGET" -mindepth 1 -delete 2>/dev/null
rmdir "$TARGET" 2>/dev/null

echo "Cleaned $TARGET"
