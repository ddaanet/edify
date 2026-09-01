#!/usr/bin/env bash
exec 2>&1
set -xeuo pipefail

# Clean tree; ` M memory` is the submodule's resting state, not dirt.
status=$(git status --porcelain | grep -vx ' M memory' || true)
if [[ -n "$status" ]]; then
    echo "DIRTY: uncommitted changes"
    echo "$status"
    exit 1
fi

just precommit || {
    echo "PRECOMMIT: validation failed"
    exit 1
}

echo "CLEAN"
exit 0
